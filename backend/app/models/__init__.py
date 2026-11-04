"""Modelos do banco: as 8 tabelas do projeto."""

from app.models.base import Base
from app.models.comparison import Comparison
from app.models.experiment_result import ExperimentResult
from app.models.feature_stats import FeatureStat
from app.models.inspection import Inspection
from app.models.listing import Listing
from app.models.persona import Persona
from app.models.posterior import Posterior
from app.models.session import SessionModel

__all__ = [
    "Base",
    "Comparison",
    "ExperimentResult",
    "FeatureStat",
    "Inspection",
    "Listing",
    "Persona",
    "Posterior",
    "SessionModel",
]
