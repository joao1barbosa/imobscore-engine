"""Testes dos metadados: os segmentos do catálogo e as personas."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Listing
from app.services.seed_service import seed_database


@pytest.fixture
def seeded(db: Session) -> Session:
    """Semeia o catálogo de demonstração no banco do teste."""
    seed_database(db, get_settings())
    return db


def test_meta_options_devolve_a_faixa_de_preco(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/v1/meta/options")

    assert response.status_code == 200
    segments = response.json()["segments"]
    assert len(segments) == 1

    prices = seeded.scalars(select(Listing.price_brl)).all()
    segment = segments[0]
    assert segment["city"] == "Goiânia"
    assert segment["purpose"] == "sale"
    assert segment["price_floor"] == float(min(prices))
    assert segment["price_ceiling"] == float(max(prices))


def test_meta_personas_devolve_as_tres_personas(client: TestClient, seeded: Session) -> None:
    response = client.get("/api/v1/meta/personas")

    assert response.status_code == 200
    personas = response.json()
    assert [persona["slug"] for persona in personas] == ["familia", "investidor", "estudante"]

    for persona in personas:
        assert set(persona) == {"slug", "name", "description", "demo_defaults"}
        assert persona["name"]
        assert persona["description"]
        defaults = persona["demo_defaults"]
        assert set(defaults) == {"city", "purpose", "price_min", "price_max"}
        assert defaults["city"] == "Goiânia"
        assert defaults["purpose"] == "sale"
        assert defaults["price_min"] < defaults["price_max"]


def test_meta_sem_catalogo_devolve_lista_vazia(client: TestClient) -> None:
    response = client.get("/api/v1/meta/options")

    assert response.status_code == 200
    assert response.json() == {"segments": []}
