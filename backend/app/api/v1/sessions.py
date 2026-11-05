"""Rotas de sessões e de pares da coleta."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Response, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_session_or_404
from app.models import SessionModel
from app.schemas.pair import AnswerIn, AnswerOut, PairOut
from app.schemas.session import SessionCreate, SessionOut
from app.services import pair_service, posterior_service, session_service

router = APIRouter()


@router.post("/sessions", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: SessionCreate,
    db: Annotated[Session, Depends(get_db)],
) -> SessionOut:
    """Cria a sessão a partir do onboarding."""
    session = session_service.create_session(db, payload)
    db.commit()
    return session_service.session_out(db, session)


@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[SessionModel, Depends(get_session_or_404)],
) -> SessionOut:
    """O estado da sessão e o progresso da coleta."""
    return session_service.session_out(db, session)


@router.get("/sessions/{session_id}/next-pair", response_model=PairOut)
def next_pair(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[SessionModel, Depends(get_session_or_404)],
) -> PairOut | Response:
    """O par pendente da sessão, ou 204 quando a sessão acabou.

    Recarregar a página devolve o mesmo par: o par pendente é devolvido em vez
    de criar outro. Na coleta o par é sorteado ao acaso; nos outros modos, é
    escolhido por informação, com a posteriori atual.
    """
    db.refresh(session, with_for_update=True)

    if session.status == "done":
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    comparison = pair_service.pending_comparison(db, session)
    if comparison is None:
        if session_service.answered_count(db, session) >= session.target_pairs:
            session.status = "done"
            db.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        comparison = pair_service.create_next_comparison(db, session)
        db.commit()

    return pair_service.pair_out(db, comparison, session)


@router.post("/sessions/{session_id}/comparisons/{position}", response_model=AnswerOut)
def answer_pair(
    session_id: UUID,
    position: Annotated[int, Path(ge=1, le=32767)],
    payload: AnswerIn,
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[SessionModel, Depends(get_session_or_404)],
) -> AnswerOut:
    """Registra a escolha da pessoa.

    Fora do modo coleta, a posteriori é recalculada e os diagnósticos do MCMC
    voltam na resposta.
    """
    db.refresh(session, with_for_update=True)
    result = pair_service.record_answer(db, session, position, payload)

    if session.mode != "collection":
        fit = posterior_service.get_or_fit(db, session, result.answered)
        result.diagnostics = posterior_service.diagnostics_out(fit.diagnostics)

    db.commit()
    return result
