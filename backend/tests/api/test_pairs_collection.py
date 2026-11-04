"""Testes dos pares da coleta: sorteio, retomada, respostas e fim da sessão."""

from collections import Counter
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Comparison
from app.services.seed_service import seed_database


@pytest.fixture
def seeded(db: Session) -> Session:
    """Semeia o catálogo de demonstração no banco do teste."""
    seed_database(db, get_settings())
    return db


def onboarding(**changes: Any) -> dict[str, Any]:
    """O corpo do onboarding da coleta."""
    payload: dict[str, Any] = {
        "mode": "collection",
        "city": "Goiânia",
        "purpose": "sale",
        "price_min": 300000,
        "price_max": 900000,
        "persona_slug": "familia",
        "consent": True,
    }
    payload.update(changes)
    return payload


def start_session(client: TestClient) -> str:
    """Cria uma sessão de coleta e devolve o id."""
    response = client.post("/api/v1/sessions", json=onboarding())
    assert response.status_code == 201
    return str(response.json()["id"])


def answer(client: TestClient, session_id: str, position: int, chosen: str = "A") -> Any:
    """Responde um par."""
    return client.post(
        f"/api/v1/sessions/{session_id}/comparisons/{position}",
        json={"chosen": chosen, "response_ms": 1500},
    )


def test_next_pair_devolve_o_primeiro_par(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)

    response = client.get(f"/api/v1/sessions/{session_id}/next-pair")

    assert response.status_code == 200
    pair = response.json()
    assert pair["position"] == 1
    assert pair["total"] == 25
    assert pair["listing_a"]["id"] != pair["listing_b"]["id"]
    assert pair["listing_a"]["code"].startswith("GYN-V-")
    assert pair["listing_b"]["code"].startswith("GYN-V-")


def test_recarregar_devolve_o_mesmo_par_pendente(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)

    first = client.get(f"/api/v1/sessions/{session_id}/next-pair").json()
    second = client.get(f"/api/v1/sessions/{session_id}/next-pair").json()

    assert first == second


def test_vinte_e_cinco_pares_sem_repetir(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)

    seen: list[frozenset[str]] = []
    appearances: Counter[str] = Counter()
    for position in range(1, 26):
        pair = client.get(f"/api/v1/sessions/{session_id}/next-pair").json()
        assert pair["position"] == position

        codes = [pair["listing_a"]["code"], pair["listing_b"]["code"]]
        seen.append(frozenset(codes))
        appearances.update(codes)

        response = answer(client, session_id, position)
        assert response.status_code == 200

    assert len(set(seen)) == 25
    assert max(appearances.values()) <= 3

    comparisons = seeded.scalars(select(Comparison)).all()
    assert len(comparisons) == 25
    assert all(comparison.selection == "random" for comparison in comparisons)
    assert all(comparison.chosen is not None for comparison in comparisons)


def test_resposta_repetida_da_409(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    client.get(f"/api/v1/sessions/{session_id}/next-pair")

    first = answer(client, session_id, 1)
    second = answer(client, session_id, 1)

    assert first.status_code == 200
    assert second.status_code == 409
    assert second.json()["detail"]["code"] == "pair_already_answered"


def test_resposta_fora_de_ordem_da_409(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    client.get(f"/api/v1/sessions/{session_id}/next-pair")

    response = answer(client, session_id, 2)

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "pair_out_of_order"


def test_apos_o_ultimo_par_a_sessao_termina(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)

    last = None
    for position in range(1, 26):
        client.get(f"/api/v1/sessions/{session_id}/next-pair")
        last = answer(client, session_id, position)

    assert last is not None
    assert last.status_code == 200
    assert last.json() == {"answered": 25, "total": 25, "done": True, "diagnostics": None}

    state = client.get(f"/api/v1/sessions/{session_id}").json()
    assert state["status"] == "done"
    assert state["answered"] == 25

    next_pair = client.get(f"/api/v1/sessions/{session_id}/next-pair")
    assert next_pair.status_code == 204
    assert next_pair.content == b""


def test_sessao_terminada_recusa_nova_resposta(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    for position in range(1, 26):
        client.get(f"/api/v1/sessions/{session_id}/next-pair")
        answer(client, session_id, position)

    response = answer(client, session_id, 25)

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "session_done"


def test_modo_demo_nao_tem_par_ainda(client: TestClient, seeded: Session) -> None:
    created = client.post("/api/v1/sessions", json=onboarding(mode="demo", consent=False)).json()

    response = client.get(f"/api/v1/sessions/{created['id']}/next-pair")

    assert response.status_code == 501
    assert response.json()["detail"]["code"] == "not_available"


def test_sessao_inexistente_da_404(client: TestClient, seeded: Session) -> None:
    session_id = str(uuid4())

    state = client.get(f"/api/v1/sessions/{session_id}")
    next_pair = client.get(f"/api/v1/sessions/{session_id}/next-pair")
    comparison = answer(client, session_id, 1)

    assert state.status_code == 404
    assert state.json()["detail"]["code"] == "session_not_found"
    assert next_pair.status_code == 404
    assert next_pair.json()["detail"]["code"] == "session_not_found"
    assert comparison.status_code == 404
    assert comparison.json()["detail"]["code"] == "session_not_found"


def test_resposta_sem_o_par_sido_mostrado_da_409(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)

    response = answer(client, session_id, 1)

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "pair_out_of_order"
