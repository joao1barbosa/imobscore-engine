"""Testes do feed: a ordem, o método, o `at` e o reaproveitamento da posteriori."""

from typing import Any
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.services import feed_service, posterior_service
from app.services.seed_service import seed_database


@pytest.fixture
def seeded(db: Session) -> Session:
    """Semeia o catálogo de demonstração no banco do teste."""
    seed_database(db, get_settings())
    return db


def onboarding(**changes: Any) -> dict[str, Any]:
    """O corpo do onboarding da demo."""
    payload: dict[str, Any] = {
        "mode": "demo",
        "city": "Goiânia",
        "purpose": "sale",
        "price_min": 300000,
        "price_max": 900000,
        "persona_slug": "familia",
        "consent": False,
    }
    payload.update(changes)
    return payload


def start_session(client: TestClient, **changes: Any) -> str:
    """Cria uma sessão de demo e devolve o id."""
    response = client.post("/api/v1/sessions", json=onboarding(**changes))
    assert response.status_code == 201
    return str(response.json()["id"])


def answer(client: TestClient, session_id: str, position: int, chosen: str = "A") -> Any:
    """Responde um par."""
    return client.post(
        f"/api/v1/sessions/{session_id}/comparisons/{position}",
        json={"chosen": chosen, "response_ms": 1200},
    )


def run_pairs(client: TestClient, session_id: str, total: int) -> None:
    """Mostra e responde `total` pares."""
    for position in range(1, total + 1):
        assert client.get(f"/api/v1/sessions/{session_id}/next-pair").status_code == 200
        response = answer(client, session_id, position, "A" if position % 2 else "B")
        assert response.status_code == 200


def test_feed_com_zero_pares_usa_a_priori(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)

    response = client.get(f"/api/v1/sessions/{session_id}/feed")

    assert response.status_code == 200
    page = response.json()
    assert page["method"] == "bayes"
    assert page["n_comparisons"] == 0
    assert len(page["items"]) == 30
    assert page["items"][0]["rank"] == 1
    assert all(0 <= item["score"] <= 100 for item in page["items"])


def test_feed_com_tres_pares(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    run_pairs(client, session_id, 3)

    response = client.get(f"/api/v1/sessions/{session_id}/feed")

    assert response.status_code == 200
    page = response.json()
    assert page["n_comparisons"] == 3
    assert len(page["items"]) == 30
    assert all(item["inspection_delta"] == 0 for item in page["items"])


def test_feed_ordena_pela_afinidade(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    run_pairs(client, session_id, 3)

    page = client.get(f"/api/v1/sessions/{session_id}/feed").json()

    affinities = [item["affinity_pct"] for item in page["items"]]
    assert affinities == sorted(affinities, reverse=True)
    assert len({item["listing"]["code"] for item in page["items"]}) == len(page["items"])


def test_feed_com_metodo_persona_nao_tem_motivos(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    run_pairs(client, session_id, 3)

    response = client.get(f"/api/v1/sessions/{session_id}/feed", params={"method": "persona"})

    assert response.status_code == 200
    page = response.json()
    assert page["method"] == "persona"
    assert page["n_comparisons"] == 3
    assert all(item["reasons"] == [] for item in page["items"])
    assert all(0 <= item["score"] <= 100 for item in page["items"])


def test_at_zero_diferente_de_at_tres(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    run_pairs(client, session_id, 3)

    before = client.get(f"/api/v1/sessions/{session_id}/feed", params={"at": 0}).json()
    after = client.get(f"/api/v1/sessions/{session_id}/feed", params={"at": 3}).json()

    assert before["n_comparisons"] == 0
    assert after["n_comparisons"] == 3
    before_scores = [(item["listing"]["code"], item["affinity_pct"]) for item in before["items"]]
    after_scores = [(item["listing"]["code"], item["affinity_pct"]) for item in after["items"]]
    assert before_scores != after_scores


def test_at_invalido_da_422(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    run_pairs(client, session_id, 3)

    high = client.get(f"/api/v1/sessions/{session_id}/feed", params={"at": 5})
    low = client.get(f"/api/v1/sessions/{session_id}/feed", params={"at": -1})

    assert high.status_code == 422
    assert high.json()["detail"]["code"] == "validation_error"
    assert low.status_code == 422
    assert low.json()["detail"]["code"] == "validation_error"


def test_limit_e_offset(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)

    first = client.get(f"/api/v1/sessions/{session_id}/feed", params={"limit": 10}).json()
    second = client.get(
        f"/api/v1/sessions/{session_id}/feed", params={"limit": 10, "offset": 10}
    ).json()

    assert len(first["items"]) == 10
    assert first["next_offset"] == 10
    assert second["items"][0]["rank"] == 11
    codes = {item["listing"]["code"] for item in first["items"]}
    assert codes.isdisjoint({item["listing"]["code"] for item in second["items"]})


def test_limit_fora_do_intervalo_da_422(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)

    low = client.get(f"/api/v1/sessions/{session_id}/feed", params={"limit": 0})
    high = client.get(f"/api/v1/sessions/{session_id}/feed", params={"limit": 51})

    assert low.status_code == 422
    assert high.status_code == 422


def test_segunda_chamada_do_feed_nao_roda_o_mcmc_de_novo(
    client: TestClient, seeded: Session
) -> None:
    """A segunda chamada do feed usa a posteriori já gravada."""
    session_id = start_session(client)

    with mock.patch(
        "app.services.posterior_service.fit_posterior",
        wraps=posterior_service.fit_posterior,
    ) as fitted:
        first = client.get(f"/api/v1/sessions/{session_id}/feed")
        assert first.status_code == 200
        assert fitted.call_count == 1

        # O cache do ranking é esvaziado, para a segunda chamada ter de ler a linha.
        feed_service.clear_cache()
        second = client.get(f"/api/v1/sessions/{session_id}/feed")

    assert second.status_code == 200
    assert fitted.call_count == 1
    # A ordem do ranking é a mesma; as amostras guardadas em float32 arredondam
    # um pouco a afinidade, e o arredondamento chega aos centésimos.
    assert [item["listing"]["code"] for item in first.json()["items"]] == [
        item["listing"]["code"] for item in second.json()["items"]
    ]


def test_sessao_inexistente_da_404(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/v1/sessions/11111111-1111-1111-1111-111111111111/feed")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "session_not_found"
