"""As 12 características do motor: especificação, transformação e padronização (seção 5.1)."""

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from math import log
from typing import Protocol

import numpy as np

# Converte o intervalo interquartil em uma escala comparável ao desvio padrão de uma normal.
IQR_TO_SCALE = 1.349


@dataclass(frozen=True)
class FeatureSpec:
    key: str
    label: str  # rótulo em pt-BR para a interface
    direction: int  # -1, 0 ou +1 (só baseline de pesos iguais)
    text_high: str
    text_low: str


FEATURES: tuple[FeatureSpec, ...] = (
    FeatureSpec("log_price", "Preço", -1, "mais caro que o típico", "mais barato que o típico"),
    FeatureSpec("log_area", "Área", 1, "mais espaçoso", "mais compacto"),
    FeatureSpec("bedrooms", "Quartos", 1, "mais quartos", "menos quartos"),
    FeatureSpec(
        "bedrooms_sq", "Distância de 3 quartos", -1, "longe de 3 quartos", "perto de 3 quartos"
    ),
    FeatureSpec("bathrooms", "Banheiros", 1, "mais banheiros", "menos banheiros"),
    FeatureSpec("parking", "Vagas", 1, "mais vagas", "menos vagas"),
    FeatureSpec("dist_center", "Distância do centro", -1, "longe do centro", "perto do centro"),
    FeatureSpec("age", "Idade", -1, "mais antigo", "mais novo"),
    FeatureSpec("is_house", "Casa", 0, "é casa", "é apartamento"),
    FeatureSpec("leisure", "Lazer", 1, "mais lazer", "menos lazer"),
    FeatureSpec("pet", "Aceita pet", 1, "aceita pet", "não aceita pet"),
    FeatureSpec("doorman", "Portaria 24 h", 1, "tem portaria 24 h", "sem portaria"),
)
FEATURE_KEYS: tuple[str, ...] = tuple(feature.key for feature in FEATURES)


class ListingLike(Protocol):
    """Serve para a linha do ORM e para o `ListingRow` do catálogo."""

    price_brl: Decimal | float
    area_m2: Decimal | float
    bedrooms: int
    bathrooms: int
    parking: int
    dist_center_km: Decimal | float
    age_years: int
    kind: str
    leisure_count: int
    pet_friendly: bool
    doorman_24h: bool


def _transform(row: ListingLike) -> list[float]:
    """Calcula t(x), na ordem de `FEATURE_KEYS`."""
    return [
        log(float(row.price_brl)),
        log(float(row.area_m2)),
        float(row.bedrooms),
        float((row.bedrooms - 3) ** 2),
        float(row.bathrooms),
        float(row.parking),
        float(row.dist_center_km),
        float(row.age_years),
        1.0 if row.kind == "house" else 0.0,
        float(row.leisure_count),
        1.0 if row.pet_friendly else 0.0,
        1.0 if row.doorman_24h else 0.0,
    ]


def raw_matrix(rows: Sequence[ListingLike]) -> np.ndarray:
    """Devolve (n, 12) = t(x), antes da padronização."""
    return np.array([_transform(row) for row in rows], dtype=np.float64).reshape(-1, len(FEATURES))


def fit_stats(T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Devolve (center, scale): mediana e IQR / 1,349 de cada coluna.

    Se o IQR de uma coluna for zero, usa o desvio padrão. Se ele também for zero, usa 1.
    """
    center = np.median(T, axis=0)
    q25, q75 = np.percentile(T, [25, 75], axis=0)
    scale = (q75 - q25) / IQR_TO_SCALE
    scale = np.where(scale > 0, scale, np.std(T, axis=0))
    scale = np.where(scale > 0, scale, 1.0)
    return center, scale


def standardize(T: np.ndarray, center: np.ndarray, scale: np.ndarray) -> np.ndarray:
    """Devolve (n, 12) = z. O imóvel típico do segmento vira o vetor zero."""
    z: np.ndarray = (T - center) / scale
    return z
