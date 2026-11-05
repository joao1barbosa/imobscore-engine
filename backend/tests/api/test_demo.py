"""Testes da demo: os três pares adaptativos, sem repetir."""

from collections import Counter
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Comparison, Posterior
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


def test_demo_com_tres_pares_sem_repetir(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)

    seen: list[frozenset[str]] = []
    appearances: Counter[str] = Counter()
    for position in range(1, 4):
        pair = client.get(f"/api/v1/sessions/{session_id}/next-pair")
        assert pair.status_code == 200
        body = pair.json()
        assert body["position"] == position
        assert body["total"] == 3

        codes = [body["listing_a"]["code"], body["listing_b"]["code"]]
        seen.append(frozenset(codes))
        appearances.update(codes)

        response = answer(client, session_id, position, "A" if position % 2 else "B")
        assert response.status_code == 200
        assert response.json()["diagnostics"] is not None

    assert len(set(seen)) == 3
    assert max(appearances.values()) <= 3

    comparisons = seeded.scalars(
        select(Comparison).where(Comparison.session_id == session_id)
    ).all()
    assert len(comparisons) == 3
    assert all(comparison.selection == "adaptive" for comparison in comparisons)
    assert all(comparison.chosen is not None for comparison in comparisons)


def test_demo_termina_apos_tres_pares(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    for position in range(1, 4):
        client.get(f"/api/v1/sessions/{session_id}/next-pair")
        assert answer(client, session_id, position).status_code == 200

    state = client.get(f"/api/v1/sessions/{session_id}").json()
    assert state["status"] == "done"
    assert state["answered"] == 3

    next_pair = client.get(f"/api/v1/sessions/{session_id}/next-pair")
    assert next_pair.status_code == 204
    assert next_pair.content == b""


def test_demo_grava_a_posteriori_de_cada_par(client: TestClient, seeded: Session) -> None:
    session_id = start_session(client)
    for position in range(1, 4):
        client.get(f"/api/v1/sessions/{session_id}/next-pair")
        answer(client, session_id, position)

    posteriors = seeded.scalars(select(Posterior).where(Posterior.session_id == session_id)).all()

    assert sorted(posterior.n_comparisons for posterior in posteriors) == [0, 1, 2, 3]
    assert all(posterior.seed != 0 for posterior in posteriors)
    assert all(len(posterior.samples) > 0 for posterior in posteriors)


def test_recarregar_devolve_o_mesmo_par_pendente_na_demo(
    client: TestClient, seeded: Session
) -> None:
    session_id = start_session(client)

    first = client.get(f"/api/v1/sessions/{session_id}/next-pair").json()
    second = client.get(f"/api/v1/sessions/{session_id}/next-pair").json()

    assert first == second
