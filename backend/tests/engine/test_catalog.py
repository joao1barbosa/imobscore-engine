"""Testes do catálogo simulado, das personas e dos itens de vistoria."""

from pathlib import Path

import pytest
import yaml

from app.engine import FEATURE_KEYS
from app.seed import ListingRow, generate_catalog
from app.seed.catalog import NEIGHBORHOODS

SEED_DIR = Path(__file__).resolve().parents[2] / "app" / "seed"


@pytest.fixture(scope="module")
def catalog() -> list[ListingRow]:
    return generate_catalog(42)


@pytest.fixture(scope="module")
def personas() -> list[dict]:
    return yaml.safe_load((SEED_DIR / "personas.yaml").read_text(encoding="utf-8"))


def test_same_seed_same_catalog(catalog: list[ListingRow]) -> None:
    assert generate_catalog(42) == catalog


def test_different_seed_different_catalog(catalog: list[ListingRow]) -> None:
    assert generate_catalog(43) != catalog


def test_all_300_listings_are_for_sale_in_goiania(catalog: list[ListingRow]) -> None:
    assert len(catalog) == 300
    assert {row.city for row in catalog} == {"Goiânia"}
    assert {row.purpose for row in catalog} == {"sale"}


def test_codes_are_unique_and_sequential(catalog: list[ListingRow]) -> None:
    assert [row.code for row in catalog] == [f"GYN-V-{i:04d}" for i in range(1, 301)]


def test_price_range_covers_at_least_95_percent(catalog: list[ListingRow]) -> None:
    inside = [150_000 <= row.price_brl <= 2_500_000 for row in catalog]

    assert sum(inside) / len(inside) >= 0.95


def test_prices_are_rounded_to_a_thousand(catalog: list[ListingRow]) -> None:
    assert all(row.price_brl % 1000 == 0 for row in catalog)


def test_values_respect_the_database_checks(catalog: list[ListingRow]) -> None:
    for row in catalog:
        assert row.kind in ("apartment", "house")
        assert row.price_brl > 0
        assert row.area_m2 > 0
        assert 1 <= row.bedrooms <= 6
        assert 1 <= row.bathrooms <= max(1, min(row.bedrooms, int(row.area_m2 // 25)))
        assert 0 <= row.parking <= 4
        assert row.dist_center_km >= 0.3
        assert 0 <= row.age_years <= 40
        assert 0 <= row.leisure_count <= 3


def test_bedrooms_and_leisure_follow_the_kind(catalog: list[ListingRow]) -> None:
    for row in catalog:
        if row.kind == "house":
            assert 2 <= row.bedrooms <= 5
            assert row.leisure_count <= 2
        else:
            assert 1 <= row.bedrooms <= 4


def test_titles_and_illustrations(catalog: list[ListingRow]) -> None:
    for row in catalog:
        noun = "Casa" if row.kind == "house" else "Apartamento"
        rooms = "quarto" if row.bedrooms == 1 else "quartos"
        assert row.title == f"{noun} de {row.bedrooms} {rooms} no {row.neighborhood}"
        assert row.illustration in {f"{row.kind}-{i}" for i in (1, 2, 3)}


def test_all_neighborhoods_are_used_near_their_distance(catalog: list[ListingRow]) -> None:
    distances = dict(NEIGHBORHOODS)

    assert {row.neighborhood for row in catalog} == set(distances)
    for row in catalog:
        assert abs(row.dist_center_km - distances[row.neighborhood]) <= 0.5 + 1e-9


def test_personas_have_all_twelve_keys(personas: list[dict]) -> None:
    assert [persona["slug"] for persona in personas] == ["familia", "investidor", "estudante"]
    for persona in personas:
        assert tuple(persona["prior_mean"]) == FEATURE_KEYS
        assert tuple(persona["prior_sd"]) == FEATURE_KEYS
        assert set(persona["prior_sd"].values()) == {1.0}
        assert persona["description"]


def test_demo_defaults_stay_in_the_catalog_segment(
    personas: list[dict], catalog: list[ListingRow]
) -> None:
    for persona in personas:
        defaults = persona["demo_defaults"]
        assert defaults["city"] == "Goiânia"
        assert defaults["purpose"] == "sale"
        low, high = defaults["price_min"], defaults["price_max"]
        assert low < high
        candidates = [row for row in catalog if 0.85 * low <= row.price_brl <= 1.15 * high]
        assert len(candidates) >= 20, persona["slug"]


def test_inspection_items() -> None:
    items = yaml.safe_load((SEED_DIR / "inspection_items.yaml").read_text(encoding="utf-8"))

    assert {item["key"]: item["delta"] for item in items} == {
        "noisy_street": -10,
        "humidity": -8,
        "needs_renovation": -7,
        "low_light": -5,
        "good_light": 5,
        "quiet_neighborhood": 6,
        "walkable_shops": 5,
        "nice_view": 4,
    }
    assert all(item["label"] for item in items)
