"""Rota do feed da sessão."""

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import get_db, get_session_or_404
from app.models import SessionModel
from app.schemas.feed import FeedPage
from app.services import feed_service

router = APIRouter()


@router.get("/sessions/{session_id}/feed", response_model=FeedPage)
def feed(
    session_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[SessionModel, Depends(get_session_or_404)],
    method: Annotated[Literal["bayes", "persona"], Query()] = "bayes",
    at: Annotated[int | None, Query(ge=0)] = None,
    limit: Annotated[int, Query(ge=1, le=50)] = 30,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> FeedPage:
    """O feed de imóveis, com a afinidade da sessão.

    Com `at=N`, o feed é calculado com os N primeiros pares respondidos; sem
    ele, com todos os pares respondidos até agora.
    """
    page = feed_service.feed_page(db, session, method=method, at=at, limit=limit, offset=offset)
    db.commit()
    return page
