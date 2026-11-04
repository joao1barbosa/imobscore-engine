"""Interface pública do motor (seção 5.10)."""

from app.engine.affinity import AffinityResult, Reason, compute_affinity, explain, to_score
from app.engine.baselines import Method, fit_mle, predict_proba
from app.engine.diagnostics import Diagnostics, is_ok
from app.engine.evaluation import ResultRow, evaluate_participant, simulate_choices
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
from app.engine.pairs import next_pair_bald, random_pairs, seed_for

__all__ = [
    "AffinityResult",
    "Diagnostics",
    "FEATURES",
    "FEATURE_KEYS",
    "FeatureSpec",
    "ListingLike",
    "MCMCConfig",
    "MCMCResult",
    "Method",
    "Reason",
    "ResultRow",
    "compute_affinity",
    "evaluate_participant",
    "explain",
    "fit_mle",
    "fit_posterior",
    "fit_stats",
    "is_ok",
    "next_pair_bald",
    "predict_proba",
    "random_pairs",
    "raw_matrix",
    "seed_for",
    "simulate_choices",
    "standardize",
    "to_score",
]
