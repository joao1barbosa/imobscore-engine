"""Interface pública do motor (seção 5.10). Só traz os nomes já implementados."""

from app.engine.diagnostics import Diagnostics
from app.engine.features import (
    FEATURE_KEYS,
    FEATURES,
    FeatureSpec,
    ListingLike,
    fit_stats,
    raw_matrix,
    standardize,
)
from app.engine.mcmc import MCMCConfig, MCMCResult, fit_posterior
from app.engine.pairs import random_pairs, seed_for

__all__ = [
    "Diagnostics",
    "FEATURES",
    "FEATURE_KEYS",
    "FeatureSpec",
    "ListingLike",
    "MCMCConfig",
    "MCMCResult",
    "fit_posterior",
    "fit_stats",
    "random_pairs",
    "raw_matrix",
    "seed_for",
    "standardize",
]
