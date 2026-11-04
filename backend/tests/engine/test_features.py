"""Testes das características: transformação e padronização (seção 5.1)."""

from dataclasses import replace
from decimal import Decimal
from math import log

import numpy as np
import pytest

from app.engine import FEATURE_KEYS, FEATURES, fit_stats, raw_matrix, standardize
from app.seed import ListingRow, generate_catalog

BASE = ListingRow(
    code="GYN-V-0001",
    city="Goiânia",
    purpose="sale",
    kind="apartment",
    title="Apartamento de 3 quartos no Setor Bueno",
    neighborhood="Setor Bueno",
    price_brl=500000.0,
    area_m2=100.0,
    bedrooms=3,
    bathrooms=2,
    parking=2,
    dist_center_km=4.0,
    age_years=8,
    leisure_count=2,
    pet_friendly=True,
    doorman_24h=False,
    illustration="apartment-1",
)


def column(key: str) -> int:
    return FEATURE_KEYS.index(key)


def test_twelve_features_in_table_order() -> None:
    assert FEATURE_KEYS == (
        "log_price",
        "log_area",
        "bedrooms",
        "bedrooms_sq",
        "bathrooms",
        "parking",
        "dist_center",
        "age",
        "is_house",
        "leisure",
        "pet",
        "doorman",
    )
    assert [feature.key for feature in FEATURES] == list(FEATURE_KEYS)
    assert all(feature.direction in (-1, 0, 1) for feature in FEATURES)


def test_raw_matrix_shape_and_dtype() -> None:
    T = raw_matrix(generate_catalog(42))

    assert T.shape == (300, 12)
    assert T.dtype == np.float64
    assert np.isfinite(T).all()


def test_raw_matrix_empty_keeps_twelve_columns() -> None:
    assert raw_matrix([]).shape == (0, 12)


def test_raw_matrix_transformations() -> None:
    row = raw_matrix([BASE])[0]

    assert row[column("log_price")] == pytest.approx(log(500000.0))
    assert row[column("log_area")] == pytest.approx(log(100.0))
    assert row[column("is_house")] == 0.0
    assert row[column("pet")] == 1.0
    assert row[column("doorman")] == 0.0


def test_raw_matrix_accepts_decimal_like_the_orm() -> None:
    orm_like = replace(BASE, price_brl=Decimal("500000.00"), area_m2=Decimal("100.0"))  # type: ignore[arg-type]

    np.testing.assert_array_equal(raw_matrix([orm_like]), raw_matrix([BASE]))


@pytest.mark.parametrize(("bedrooms", "expected"), [(1, 4.0), (2, 1.0), (3, 0.0), (5, 4.0)])
def test_bedrooms_sq_is_zero_at_three_bedrooms(bedrooms: int, expected: float) -> None:
    row = raw_matrix([replace(BASE, bedrooms=bedrooms)])[0]

    assert row[column("bedrooms_sq")] == expected


def test_median_becomes_zero_after_standardize() -> None:
    T = raw_matrix(generate_catalog(42))
    center, scale = fit_stats(T)
    Z = standardize(T, center, scale)

    np.testing.assert_allclose(np.median(Z, axis=0), np.zeros(12), atol=1e-12)
    assert (scale > 0).all()


def test_scale_is_iqr_over_1_349() -> None:
    T = np.tile(np.array([[1.0], [2.0], [3.0], [4.0], [5.0]]), (1, 12))

    _, scale = fit_stats(T)

    np.testing.assert_allclose(scale, np.full(12, 2.0 / 1.349))


def test_zero_iqr_falls_back_to_standard_deviation() -> None:
    values = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0])
    T = np.tile(values[:, None], (1, 12))

    _, scale = fit_stats(T)

    np.testing.assert_allclose(scale, np.full(12, np.std(values)))


def test_constant_column_falls_back_to_one() -> None:
    _, scale = fit_stats(np.full((5, 12), 7.0))

    np.testing.assert_array_equal(scale, np.ones(12))
