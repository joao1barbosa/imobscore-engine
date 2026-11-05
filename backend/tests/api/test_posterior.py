"""Testes da posteriori: os doze pesos e o traço das cadeias."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.engine import FEATURE_KEYS
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
        assert answer(client, session_id, position, "A" if position % 2 else "B").status_code == 200


def test_posterior_tem_doze_pesos(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    run_pairs(client, session_id, 3)

    response = client.get(f"/api/v1/sessions/{session_id}/posterior")

    assert response.status_code == 200
    body = response.json()
    assert body["n_comparisons"] == 3
    assert len(body["weights"]) == 12
    assert [weight["feature_key"] for weight in body["weights"]] == list(FEATURE_KEYS)
    for weight in body["weights"]:
        assert weight["label"]
        assert weight["post_sd"] >= 0
        assert weight["ci_low"] <= weight["post_mean"] <= weight["ci_high"]
    assert body["diagnostics"]["ok"] in (True, False)
    assert body["diagnostics"]["accept_rate"] >= 0


def test_posterior_mostra_a_priori_da_persona(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client, persona_slug="investidor")

    body = client.get(f"/api/v1/sessions/{session_id}/posterior").json()

    by_key = {weight["feature_key"]: weight for weight in body["weights"]}
    assert by_key["log_price"]["prior_mean"] == pytest.approx(-1.5)
    assert by_key["log_price"]["prior_sd"] == pytest.approx(1.0)


def test_posterior_com_n_invalido_da_422(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    run_pairs(client, session_id, 3)

    response = client.get(f"/api/v1/sessions/{session_id}/posterior", params={"n": 5})

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_trace_tem_quatro_cadeias_de_duzentos_e_cinquenta_pontos(
    client: TestClient, seeded: Session
) -> None:
    session_id = start_session(client)
    run_pairs(client, session_id, 3)

    response = client.get(
        f"/api/v1/sessions/{session_id}/posterior/trace", params={"feature": "log_price"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["feature_key"] == "log_price"
    assert len(body["chains"]) == 4
    assert all(len(chain) == 250 for chain in body["chains"])
    assert all(isinstance(value, float) for chain in body["chains"] for value in chain)


def test_trace_com_caracteristica_desconhecida_da_422(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)

    response = client.get(
        f"/api/v1/sessions/{session_id}/posterior/trace", params={"feature": "inexistente"}
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_resposta_da_demo_devolve_os_diagnosticos(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    client.get(f"/api/v1/sessions/{session_id}/next-pair")

    response = answer(client, session_id, 1)

    assert response.status_code == 200
    body = response.json()
    assert body["answered"] == 1
    assert body["diagnostics"] is not None
    assert body["diagnostics"]["rhat_max"] >= 1.0
    assert body["diagnostics"]["ess_min"] > 0


def test_coleta_nao_roda_o_mcmc(client: TestClient, seeded: Session) -> None:
    created = client.post(
        "/api/v1/sessions", json=onboarding(mode="collection", consent=True)
    ).json()
    session_id = str(created["id"])
    client.get(f"/api/v1/sessions/{session_id}/next-pair")

    response = answer(client, session_id, 1)

    assert response.status_code == 200
    assert response.json()["diagnostics"] is None


def test_posterior_sem_pares_continua_ok_na_segunda_leitura(
    client: TestClient, seeded: Session
) -> None:
    session_id = start_session(client)

    primeira = client.get(f"/api/v1/sessions/{session_id}/posterior", params={"n": 0})
    segunda = client.get(f"/api/v1/sessions/{session_id}/posterior", params={"n": 0})

    assert primeira.status_code == 200
    assert segunda.status_code == 200
    assert primeira.json()["diagnostics"]["ok"] is True
    assert segunda.json()["diagnostics"]["ok"] is True
