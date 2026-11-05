"""Rotas da posteriori: os pesos e o traço das cadeias."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_db, get_session_or_404
from app.errors import ApiError
from app.models import SessionModel
from app.schemas.posterior import PosteriorOut, TraceOut
from app.services import posterior_service
from app.services.session_service import answered_count

router = APIRouter()


@router.get("/sessions/{session_id}/posterior", response_model=PosteriorOut)
def posterior(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[SessionModel, Depends(get_session_or_404)],
    n: Annotated[int | None, Query(ge=0)] = None,
) -> PosteriorOut:
    """Os doze pesos da posteriori, com a priori da persona e os diagnósticos."""
    answered = answered_count(db, session)
    count = answered if n is None else n
    if count > answered:
        raise ApiError(
            422,
            "validation_error",
            f"O número de pares tem de estar entre 0 e {answered}.",
        )

    result = posterior_service.posterior_out(db, session, count)
    db.commit()
    return result


@router.get("/sessions/{session_id}/posterior/trace", response_model=TraceOut)
def posterior_trace(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[SessionModel, Depends(get_session_or_404)],
    feature: Annotated[str, Query(description="Chave da característica.")],
    n: Annotated[int | None, Query(ge=0)] = None,
) -> TraceOut:
    """O traço das quatro primeiras cadeias de um peso."""
    answered = answered_count(db, session)
    count = answered if n is None else n
    if count > answered:
        raise ApiError(
            422,
            "validation_error",
            f"O número de pares tem de estar entre 0 e {answered}.",
        )

    result = posterior_service.trace_out(db, session, feature, count)
    db.commit()
    return result
