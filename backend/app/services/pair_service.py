"""Serviço de pares: sorteio da coleta e registro das respostas."""

from datetime import UTC, datetime

import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engine import random_pairs, seed_for
from app.errors import ApiError
from app.models import Comparison, Listing, SessionModel
from app.schemas.pair import AnswerIn, AnswerOut, PairOut
from app.services.listing_service import candidate_listings, listing_card
from app.services.session_service import answered_count

COLLECTION_SELECTION = "random"


def collection_pairs(db: Session, session: SessionModel) -> list[tuple[Listing, Listing]]:
    """A lista de pares da coleta, sempre a mesma para a mesma sessão.

    O sorteio usa `random_pairs` com a semente `seed_for(session.id, 0)`, então
    a lista é recalculada a cada chamada sem mudar.
    """
    candidates = candidate_listings(db, session)
    pairs = random_pairs(
        len(candidates),
        session.target_pairs,
        np.random.default_rng(seed_for(session.id, 0)),
    )
    return [(candidates[first], candidates[second]) for first, second in pairs]


def pending_comparison(db: Session, session: SessionModel) -> Comparison | None:
    """O par mostrado e ainda não respondido, se houver."""
    return db.scalar(
        select(Comparison)
        .where(Comparison.session_id == session.id, Comparison.chosen.is_(None))
        .order_by(Comparison.position)
        .limit(1)
    )


def create_next_comparison(db: Session, session: SessionModel) -> Comparison:
    """Grava o próximo par da coleta, na posição que falta."""
    position = answered_count(db, session) + 1
    listing_a, listing_b = collection_pairs(db, session)[position - 1]
    comparison = Comparison(
        session_id=session.id,
        position=position,
        listing_a_id=listing_a.id,
        listing_b_id=listing_b.id,
        selection=COLLECTION_SELECTION,
    )
    db.add(comparison)
    db.flush()
    return comparison


def pair_out(db: Session, comparison: Comparison, session: SessionModel) -> PairOut:
    """Monta o par para a resposta da API."""
    listing_a = db.get(Listing, comparison.listing_a_id)
    listing_b = db.get(Listing, comparison.listing_b_id)
    if listing_a is None or listing_b is None:  # pragma: no cover - o banco não deixa isso
        raise ApiError(404, "listing_not_found", "Imóvel do par não encontrado.")
    return PairOut(
        position=comparison.position,
        total=session.target_pairs,
        listing_a=listing_card(listing_a),
        listing_b=listing_card(listing_b),
    )


def record_answer(db: Session, session: SessionModel, position: int, answer: AnswerIn) -> AnswerOut:
    """Registra a escolha da pessoa e devolve o estado da coleta."""
    if session.status == "done":
        raise ApiError(409, "session_done", "Esta sessão de coleta já terminou.")

    comparison = db.scalar(
        select(Comparison).where(
            Comparison.session_id == session.id,
            Comparison.position == position,
        )
    )
    if comparison is None:
        raise ApiError(409, "pair_out_of_order", "Este par ainda não foi mostrado.")
    if comparison.chosen is not None:
        raise ApiError(409, "pair_already_answered", "Este par já foi respondido.")

    comparison.chosen = answer.chosen
    comparison.answered_at = datetime.now(UTC)
    comparison.response_ms = answer.response_ms
    db.flush()

    answered = answered_count(db, session)
    total = session.target_pairs
    done = answered >= total
    if done:
        session.status = "done"
        db.flush()

    return AnswerOut(answered=answered, total=total, done=done, diagnostics=None)
