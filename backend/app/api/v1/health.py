"""Rota de saúde da API."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.deps import get_db

router = APIRouter()


@router.get("/health")
def health(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    """Diz se a API responde e se o banco está acessível."""
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "ok"}
