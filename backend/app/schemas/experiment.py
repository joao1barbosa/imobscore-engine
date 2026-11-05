"""Schemas do experimento: as métricas agregadas de uma rodada."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel

Method = Literal["equal", "persona", "mle", "bayes"]


class ExperimentRow(BaseModel):
    """A média e o desvio de um método, com um número de pares de treino."""

    method: Method
    n_train: int
    acc_mean: float
    acc_sd: float
    ll_mean: float
    ll_sd: float
    n_participants: int


class ParticipantRow(BaseModel):
    """A acurácia média de um participante, com um método."""

    participant_code: str
    method: str
    acc_mean: float


class ExperimentSummary(BaseModel):
    """O resumo de uma rodada do experimento."""

    run_id: UUID | None
    simulated: bool
    participants: int
    rows: list[ExperimentRow]
    per_participant: list[ParticipantRow]
