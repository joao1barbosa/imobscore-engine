"""Interface pública do motor (seção 5.10). Só traz os nomes já implementados."""

from app.engine.features import (
    FEATURE_KEYS,
    FEATURES,
    FeatureSpec,
    ListingLike,
    fit_stats,
    raw_matrix,
    standardize,
)
from app.engine.pairs import random_pairs, seed_for

__all__ = [
    "FEATURES",
    "FEATURE_KEYS",
    "FeatureSpec",
    "ListingLike",
    "fit_stats",
    "random_pairs",
    "raw_matrix",
    "seed_for",
    "standardize",
]
