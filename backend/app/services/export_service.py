"""Serviço de export: os pares respondidos da coleta em JSON, para a análise (A07)."""

from __future__ import annotations

import json
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engine import FEATURE_KEYS, raw_matrix
from app.models import Comparison, FeatureStat, Listing, SessionModel

COLLECTION_MODE = "collection"

# Só entram no export as sessões da coleta com pelo menos 20 pares respondidos.
MIN_ANSWERED_PAIRS = 20

# Mediana abaixo disso indica escolhas feitas sem ler os cartões (decisão de 09/11).
MIN_MEDIAN_RESPONSE_MS = 1000

# São Paulo não tem horário de verão desde 2019, então o deslocamento é fixo.
SAO_PAULO_TZ = timezone(timedelta(hours=-3))


class ExportError(RuntimeError):
    """Erro de export, com mensagem para quem está no terminal."""


def exported_at() -> str:
    """O momento da exportação, no fuso de São Paulo (`-03:00`)."""
    return datetime.now(SAO_PAULO_TZ).isoformat(timespec="seconds")


def segment_center_scale(db: Session, city: str, purpose: str) -> tuple[list[float], list[float]]:
    """O centro e a escala do segmento, na ordem das 12 características."""
    rows = db.scalars(
        select(FeatureStat).where(
            FeatureStat.city == city,
            FeatureStat.purpose == purpose,
        )
    ).all()
    stats = {row.feature_key: row for row in rows}
    missing = [key for key in FEATURE_KEYS if key not in stats]
    if missing:
        raise ExportError(
            f"Faltam as estatísticas de {', '.join(missing)} do segmento {city}/{purpose}. "
            "Rode o seed para recriá-las."
        )
    return (
        [float(stats[key].center) for key in FEATURE_KEYS],
        [float(stats[key].scale) for key in FEATURE_KEYS],
    )


def answered_comparisons(db: Session, session: SessionModel) -> list[Comparison]:
    """Os pares respondidos da sessão, em ordem de posição."""
    return list(
        db.scalars(
            select(Comparison)
            .where(
                Comparison.session_id == session.id,
                Comparison.chosen.is_not(None),
            )
            .order_by(Comparison.position)
        ).all()
    )


def pair_export(db: Session, comparison: Comparison) -> dict[str, Any]:
    """Um par respondido, com os imóveis e as linhas brutas das características."""
    left = db.get(Listing, comparison.listing_a_id)
    right = db.get(Listing, comparison.listing_b_id)
    if left is None or right is None:  # pragma: no cover - o banco não deixa isso
        raise ExportError(f"Imóvel do par {comparison.position} não encontrado.")

    matrix = raw_matrix([left, right])
    return {
        "position": comparison.position,
        "left_code": left.code,
        "right_code": right.code,
        "t_left": [float(value) for value in matrix[0]],
        "t_right": [float(value) for value in matrix[1]],
        "chosen": comparison.chosen,
        "response_ms": comparison.response_ms,
    }


def median_response_ms(comparisons: list[Comparison]) -> float | None:
    """A mediana do tempo de resposta dos pares, sem os que não têm tempo; None se não há nenhum."""
    times = [
        comparison.response_ms for comparison in comparisons if comparison.response_ms is not None
    ]
    if not times:
        return None
    return statistics.median(times)


def participant_export(
    db: Session, session: SessionModel, comparisons: list[Comparison]
) -> dict[str, Any]:
    """Um participante da coleta, com os pares respondidos e o padrão do segmento."""
    center, scale = segment_center_scale(db, session.city, session.purpose)
    return {
        "participant_code": session.participant_code,
        "session_id": str(session.id),
        "persona_slug": session.persona_slug,
        "city": session.city,
        "purpose": session.purpose,
        "center": center,
        "scale": scale,
        "pairs": [pair_export(db, comparison) for comparison in comparisons],
    }


def export_participants(db: Session) -> list[dict[str, Any]]:
    """Os participantes da coleta com pelo menos 20 pares respondidos e mediana do tempo de
    resposta de pelo menos 1.000 ms. Sem nenhum tempo registrado, não há mediana e a sessão
    fica de fora.
    """
    sessions = db.scalars(
        select(SessionModel)
        .where(SessionModel.mode == COLLECTION_MODE)
        .order_by(SessionModel.created_at, SessionModel.participant_code)
    ).all()

    participants: list[dict[str, Any]] = []
    for session in sessions:
        comparisons = answered_comparisons(db, session)
        if len(comparisons) < MIN_ANSWERED_PAIRS:
            continue
        median = median_response_ms(comparisons)
        if median is None or median < MIN_MEDIAN_RESPONSE_MS:
            continue
        participants.append(participant_export(db, session, comparisons))
    return participants


def build_export(db: Session) -> dict[str, Any]:
    """O JSON do export, no formato lido pela análise (A07)."""
    return {
        "exported_at": exported_at(),
        "feature_keys": list(FEATURE_KEYS),
        "participants": export_participants(db),
    }


def write_export(db: Session, path: Path) -> int:
    """Grava o JSON do export em `path` e devolve quantos participantes saíram."""
    payload = build_export(db)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(payload["participants"])
