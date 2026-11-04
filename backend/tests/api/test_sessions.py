"""Testes das sessões: criação, consentimento, código do participante e estado."""

from decimal import Decimal
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import SessionModel
from app.services.seed_service import seed_database


@pytest.fixture
def seeded(db: Session) -> Session:
    """Semeia o catálogo de demonstração no banco do teste."""
    seed_database(db, get_settings())
    return db


def onboarding(**changes: Any) -> dict[str, Any]:
    """O corpo do onboarding, com os campos trocados quando preciso."""
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


def test_cria_sessao_de_coleta_com_consentimento(client: TestClient, seeded: Session) -> None:
    response = client.post("/api/v1/sessions", json=onboarding())

    assert response.status_code == 201
    body = response.json()
    assert body["mode"] == "collection"
    assert body["city"] == "Goiânia"
    assert body["purpose"] == "sale"
    assert body["persona_slug"] == "familia"
    assert body["target_pairs"] == 25
    assert body["answered"] == 0
    assert body["status"] == "comparing"
    assert Decimal(body["price_min"]) == Decimal("300000")
    assert Decimal(body["price_max"]) == Decimal("900000")


def test_sessao_nao_devolve_o_codigo_do_participante(client: TestClient, seeded: Session) -> None:
    response = client.post("/api/v1/sessions", json=onboarding())

    assert response.status_code == 201
    assert "participant_code" not in response.json()


def test_coleta_sem_consentimento_da_422(client: TestClient, seeded: Session) -> None:
    response = client.post("/api/v1/sessions", json=onboarding(consent=False))

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_codigo_do_participante_vai_em_sequencia(client: TestClient, seeded: Session) -> None:
    first = client.post("/api/v1/sessions", json=onboarding())
    second = client.post("/api/v1/sessions", json=onboarding())

    assert first.status_code == 201
    assert second.status_code == 201

    codes = sorted(seeded.scalars(select(SessionModel.participant_code)).all())
    assert codes == ["P01", "P02"]

    sessions = seeded.scalars(select(SessionModel)).all()
    assert all(session.consent_at is not None for session in sessions)


def test_fora_de_goiania_da_422(client: TestClient, seeded: Session) -> None:
    response = client.post("/api/v1/sessions", json=onboarding(city="São Paulo"))

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_para_aluguel_da_422(client: TestClient, seeded: Session) -> None:
    response = client.post("/api/v1/sessions", json=onboarding(purpose="rent"))

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_faixa_de_preco_invertida_da_422(client: TestClient, seeded: Session) -> None:
    response = client.post("/api/v1/sessions", json=onboarding(price_min=900000, price_max=300000))

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_precos_iguais_da_422(client: TestClient, seeded: Session) -> None:
    response = client.post("/api/v1/sessions", json=onboarding(price_min=500000, price_max=500000))

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_error"


def test_modos_demo_e_product_usa_o_numero_de_pares_do_plano(
    client: TestClient, seeded: Session
) -> None:
    demo = client.post("/api/v1/sessions", json=onboarding(mode="demo", consent=False))
    product = client.post("/api/v1/sessions", json=onboarding(mode="product", consent=False))

    assert demo.status_code == 201
    assert demo.json()["target_pairs"] == 3
    assert product.status_code == 201
    assert product.json()["target_pairs"] == 8


def test_pega_o_estado_da_sessao(client: TestClient, seeded: Session) -> None:
    created = client.post("/api/v1/sessions", json=onboarding()).json()

    response = client.get(f"/api/v1/sessions/{created['id']}")

    assert response.status_code == 200
    state = response.json()
    assert state["id"] == created["id"]
    assert state["mode"] == created["mode"]
    assert state["city"] == created["city"]
    assert state["purpose"] == created["purpose"]
    assert state["persona_slug"] == created["persona_slug"]
    assert state["target_pairs"] == created["target_pairs"]
    assert state["answered"] == created["answered"]
    assert state["status"] == created["status"]
    assert Decimal(state["price_min"]) == Decimal(created["price_min"])
    assert Decimal(state["price_max"]) == Decimal(created["price_max"])


def test_sessao_inexistente_da_404(client: TestClient, seeded: Session) -> None:
    response = client.get(f"/api/v1/sessions/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "session_not_found"
