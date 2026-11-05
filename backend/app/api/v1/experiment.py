"""Rota do experimento: o resumo de uma rodada."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_db
from app.schemas.experiment import ExperimentSummary
from app.services import experiment_service

router = APIRouter()


@router.get("/experiment/summary", response_model=ExperimentSummary)
def experiment_summary(
    db: Annotated[Session, Depends(get_db)],
    run_id: Annotated[UUID | None, Query(description="Rodada pedida.")] = None,
) -> ExperimentSummary:
    """As métricas agregadas da última rodada, ou da rodada pedida."""
    return experiment_service.summary(db, run_id)
