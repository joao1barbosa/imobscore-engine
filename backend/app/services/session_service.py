"""Serviço de sessões: criação, código do participante e estado da coleta."""

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.errors import ApiError
from app.models import Comparison, Persona, SessionModel
from app.schemas.session import SessionCreate, SessionOut

PARTICIPANT_CODE_LOCK = 728_364_119
PRICE_QUANTUM = Decimal("0.01")


def target_pairs_for(mode: str) -> int:
    """Quantos pares a sessão vai ter, conforme o modo."""
    settings = get_settings()
    if mode == "collection":
        return settings.pairs_collection
    if mode == "demo":
        return settings.pairs_demo
    return settings.pairs_product


def next_participant_code(db: Session) -> str:
    """Gera o código do participante (P01, P02...), travando a transação.

    O `pg_advisory_xact_lock` segura a transação até o fim, para que duas
    pessoas ao mesmo tempo não recebam o mesmo código.
    """
    db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": PARTICIPANT_CODE_LOCK})
    codes = db.scalars(
        select(SessionModel.participant_code).where(SessionModel.participant_code.is_not(None))
    ).all()
    numbers = [int(code[1:]) for code in codes if code and code[1:].isdigit()]
    return f"P{max(numbers, default=0) + 1:02d}"


def create_session(db: Session, payload: SessionCreate) -> SessionModel:
    """Cria a sessão, com consentimento e código do participante na coleta."""
    if db.get(Persona, payload.persona_slug) is None:
        raise ApiError(422, "validation_error", "Persona desconhecida.")

    consent_at = datetime.now(UTC) if payload.mode == "collection" else None
    participant_code = next_participant_code(db) if payload.mode == "collection" else None

    session = SessionModel(
        mode=payload.mode,
        city=payload.city,
        purpose=payload.purpose,
        price_min=payload.price_min.quantize(PRICE_QUANTUM),
        price_max=payload.price_max.quantize(PRICE_QUANTUM),
        persona_slug=payload.persona_slug,
        target_pairs=target_pairs_for(payload.mode),
        participant_code=participant_code,
        consent_at=consent_at,
    )
    db.add(session)
    db.flush()
    return session


def answered_count(db: Session, session: SessionModel) -> int:
    """Quantos pares da sessão já foram respondidos."""
    return int(
        db.scalar(
            select(func.count())
            .select_from(Comparison)
            .where(Comparison.session_id == session.id, Comparison.chosen.is_not(None))
        )
        or 0
    )


def session_out(db: Session, session: SessionModel) -> SessionOut:
    """Monta o estado da sessão para a resposta da API."""
    return SessionOut(
        id=session.id,
        mode=session.mode,
        city=session.city,
        purpose=session.purpose,
        price_min=session.price_min,
        price_max=session.price_max,
        persona_slug=session.persona_slug,
        target_pairs=session.target_pairs,
        answered=answered_count(db, session),
        status=session.status,
    )
