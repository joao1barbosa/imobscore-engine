"""Participantes sintéticos da A07, no mesmo formato JSON do export (seção 5.9)."""

from decimal import Decimal
from typing import Any

import numpy as np
from sqlalchemy.orm import Session

from app.engine import (
    FEATURE_KEYS,
    random_pairs,
    raw_matrix,
    seed_for,
    simulate_choices,
    standardize,
)
from app.models import SessionModel
from app.services.export_service import exported_at, segment_center_scale
from app.services.listing_service import candidate_listings
from app.services.seed_service import load_personas

N_PAIRS = 25
TRUE_WEIGHT_NOISE = 0.7


def simulated_participant(db: Session, index: int) -> dict[str, Any]:
    """O participante S{index}: personas em rodízio e w verdadeiro = mu + N(0; 0,7²)."""
    code = f"S{index:02d}"
    personas = load_personas()
    persona = personas[(index - 1) % len(personas)]
    defaults = persona.demo_defaults
    rng = np.random.default_rng(seed_for("simulate", index))

    # Sessão transitória, nunca gravada: só para usar a mesma regra de candidatos da API.
    session = SessionModel(
        city=defaults["city"],
        purpose=defaults["purpose"],
        price_min=Decimal(defaults["price_min"]),
        price_max=Decimal(defaults["price_max"]),
    )
    candidates = candidate_listings(db, session)
    center, scale = segment_center_scale(db, session.city, session.purpose)

    T = raw_matrix(candidates)
    Z = standardize(T, np.array(center), np.array(scale))
    mu = np.array([persona.prior_mean[key] for key in FEATURE_KEYS])
    w_true = mu + TRUE_WEIGHT_NOISE * rng.standard_normal(mu.shape[0])

    pairs = random_pairs(len(candidates), N_PAIRS, rng)
    left = [pair[0] for pair in pairs]
    right = [pair[1] for pair in pairs]
    chosen = simulate_choices(Z[left] - Z[right], w_true, rng)

    return {
        "participant_code": code,
        "session_id": None,
        "persona_slug": persona.slug,
        "city": session.city,
        "purpose": session.purpose,
        "center": center,
        "scale": scale,
        "pairs": [
            {
                "position": position,
                "left_code": candidates[i].code,
                "right_code": candidates[j].code,
                "t_left": [float(value) for value in T[i]],
                "t_right": [float(value) for value in T[j]],
                "chosen": str(chosen[position - 1]),
                "response_ms": None,
            }
            for position, (i, j) in enumerate(pairs, start=1)
        ],
    }


def build_simulated_export(db: Session, participants: int) -> dict[str, Any]:
    return {
        "exported_at": exported_at(),
        "feature_keys": list(FEATURE_KEYS),
        "participants": [simulated_participant(db, index) for index in range(1, participants + 1)],
    }
