"""Serviço do experimento: o resumo das métricas de uma rodada."""

from uuid import UUID

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ExperimentResult
from app.schemas.experiment import ExperimentRow, ExperimentSummary, ParticipantRow

# Os mesmos métodos, na mesma ordem do relatório do experimento (seção 5.9).
METHODS: tuple[str, ...] = ("bayes", "mle", "persona", "equal")
BY_PARTICIPANT_N_TRAIN = 5
SIMULATED_PREFIX = "S"


def summary(db: Session, run_id: UUID | None = None) -> ExperimentSummary:
    """O resumo de uma rodada: sem `run_id`, usa a mais recente."""
    if run_id is None:
        latest = db.scalar(
            select(ExperimentResult)
            .order_by(ExperimentResult.created_at.desc(), ExperimentResult.id.desc())
            .limit(1)
        )
        run_id = latest.run_id if latest is not None else None

    if run_id is None:
        return ExperimentSummary(
            run_id=None,
            simulated=False,
            participants=0,
            rows=[],
            per_participant=[],
        )

    results = db.scalars(
        select(ExperimentResult)
        .where(ExperimentResult.run_id == run_id)
        .order_by(ExperimentResult.participant_code, ExperimentResult.method)
    ).all()

    participants = sorted({result.participant_code for result in results})
    return ExperimentSummary(
        run_id=run_id,
        simulated=any(code.startswith(SIMULATED_PREFIX) for code in participants),
        participants=len(participants),
        rows=_rows(results),
        per_participant=_per_participant(results),
    )


def _rows(results: list[ExperimentResult]) -> list[ExperimentRow]:
    """A média e o desvio amostral de cada método, por número de pares de treino."""
    grouped: dict[tuple[str, int], list[ExperimentResult]] = {}
    for result in results:
        grouped.setdefault((result.method, result.n_train), []).append(result)

    rows: list[ExperimentRow] = []
    for n_train in sorted({key[1] for key in grouped}):
        for method in METHODS:
            selected = grouped.get((method, n_train))
            if not selected:
                continue
            accuracy = np.array([result.accuracy for result in selected])
            log_loss = np.array([result.log_loss for result in selected])
            rows.append(
                ExperimentRow(
                    method=method,
                    n_train=n_train,
                    acc_mean=float(accuracy.mean()),
                    acc_sd=float(accuracy.std(ddof=1)) if accuracy.size > 1 else 0.0,
                    ll_mean=float(log_loss.mean()),
                    ll_sd=float(log_loss.std(ddof=1)) if log_loss.size > 1 else 0.0,
                    n_participants=len({result.participant_code for result in selected}),
                )
            )
    return rows


def _per_participant(results: list[ExperimentResult]) -> list[ParticipantRow]:
    """A acurácia média de cada participante, com um número fixo de pares de treino."""
    selected = [result for result in results if result.n_train == BY_PARTICIPANT_N_TRAIN]
    codes = sorted({result.participant_code for result in selected})

    rows: list[ParticipantRow] = []
    for code in codes:
        for method in METHODS:
            chosen = [
                result
                for result in selected
                if result.participant_code == code and result.method == method
            ]
            if not chosen:
                continue
            accuracy = np.array([result.accuracy for result in chosen])
            rows.append(
                ParticipantRow(
                    participant_code=code,
                    method=method,
                    acc_mean=float(accuracy.mean()),
                )
            )
    return rows
