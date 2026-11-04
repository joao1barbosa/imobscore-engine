"""Dependências compartilhadas pelas rotas."""

from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.errors import ApiError
from app.models import SessionModel


def get_db() -> Iterator[Session]:
    """Abre uma sessão por requisição e fecha no fim."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session_or_404(
    db: Annotated[Session, Depends(get_db)],
    session_id: UUID,
) -> SessionModel:
    """Devolve a sessão pedida ou levanta 404."""
    session = db.get(SessionModel, session_id)
    if session is None:
        raise ApiError(404, "session_not_found", "Sessão não encontrada.")
    return session
