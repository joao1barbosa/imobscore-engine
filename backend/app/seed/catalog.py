"""Catálogo simulado e determinístico: 300 imóveis à venda em Goiânia (tarefa A02)."""

from dataclasses import dataclass
from math import exp, log

import numpy as np

CATALOG_SIZE = 300
CITY = "Goiânia"
PURPOSE = "sale"

# Bairro e distância aproximada ao centro, em km.
NEIGHBORHOODS: tuple[tuple[str, float], ...] = (
    ("Setor Central", 1.0),
    ("Setor Oeste", 2.0),
    ("Setor Universitário", 2.0),
    ("Setor Marista", 3.0),
    ("Setor Bueno", 4.0),
    ("Jardim Goiás", 5.0),
    ("Setor Pedro Ludovico", 5.0),
    ("Jardim América", 6.0),
    ("Parque Amazônia", 8.0),
)

PRICE_INTERCEPT = 8.5


@dataclass(frozen=True)
class ListingRow:
    """Campos da tabela `listings`, exceto `id` e `created_at`."""

    code: str
    city: str
    purpose: str
    kind: str
    title: str
    neighborhood: str
    price_brl: float
    area_m2: float
    bedrooms: int
    bathrooms: int
    parking: int
    dist_center_km: float
    age_years: int
    leisure_count: int
    pet_friendly: bool
    doorman_24h: bool
    illustration: str


def _title(kind: str, bedrooms: int, neighborhood: str) -> str:
    noun = "Casa" if kind == "house" else "Apartamento"
    rooms = "quarto" if bedrooms == 1 else "quartos"
    return f"{noun} de {bedrooms} {rooms} no {neighborhood}"


def _generate_row(index: int, rng: np.random.Generator) -> ListingRow:
    """Gera um imóvel. A ordem dos sorteios faz parte do contrato de reprodutibilidade."""
    neighborhood, base_distance = NEIGHBORHOODS[int(rng.integers(len(NEIGHBORHOODS)))]
    dist_center_km = round(max(base_distance + float(rng.uniform(-0.5, 0.5)), 0.3), 2)

    is_house = bool(rng.random() < 0.35)
    kind = "house" if is_house else "apartment"
    if is_house:
        bedrooms = int(rng.choice([2, 3, 4, 5], p=[0.15, 0.40, 0.30, 0.15]))
    else:
        bedrooms = int(rng.choice([1, 2, 3, 4], p=[0.15, 0.40, 0.35, 0.10]))

    log_area = log(28 + 22 * bedrooms) + (0.15 if is_house else 0.0)
    area_m2 = round(exp(float(rng.normal(log_area, 0.18))), 1)

    max_bathrooms = max(1, min(bedrooms, int(area_m2 // 25)))
    bathrooms = int(rng.integers(1, max_bathrooms + 1))
    parking = int(np.clip(round(area_m2 / 45 + float(rng.normal(0.0, 0.6))), 0, 4))
    age_years = int(rng.integers(0, 41))

    leisure_p = [0.6, 0.3, 0.1, 0.0] if is_house else [0.2, 0.3, 0.3, 0.2]
    leisure_count = int(rng.choice([0, 1, 2, 3], p=leisure_p))
    doorman_24h = bool(rng.random() < (0.10 if is_house else 0.70))
    pet_friendly = bool(rng.random() < 0.60)

    log_price = (
        PRICE_INTERCEPT
        + log(area_m2)
        + 0.08 * parking
        - 0.03 * dist_center_km
        - 0.006 * age_years
        + 0.05 * leisure_count
        + 0.04 * doorman_24h
        + float(rng.normal(0.0, 0.12))
    )
    price_brl = float(round(exp(log_price) / 1000) * 1000)

    illustration = f"{kind}-{int(rng.integers(1, 4))}"

    return ListingRow(
        code=f"GYN-V-{index:04d}",
        city=CITY,
        purpose=PURPOSE,
        kind=kind,
        title=_title(kind, bedrooms, neighborhood),
        neighborhood=neighborhood,
        price_brl=price_brl,
        area_m2=area_m2,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        parking=parking,
        dist_center_km=dist_center_km,
        age_years=age_years,
        leisure_count=leisure_count,
        pet_friendly=pet_friendly,
        doorman_24h=doorman_24h,
        illustration=illustration,
    )


def generate_catalog(seed: int) -> list[ListingRow]:
    """Gera o catálogo. A mesma semente sempre gera os mesmos imóveis."""
    rng = np.random.default_rng(seed)
    return [_generate_row(index, rng) for index in range(1, CATALOG_SIZE + 1)]
