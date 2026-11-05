"""Serviço do feed: o ranking de imóveis com a afinidade da sessão."""

from collections import OrderedDict
from typing import Literal

from sqlalchemy.orm import Session

from app.engine import compute_affinity, explain, to_score
from app.errors import ApiError
from app.models import SessionModel
from app.schemas.feed import FeedItem, FeedPage, Reason
from app.services.listing_service import candidate_listings, listing_card
from app.services.posterior_service import get_or_fit, prior, standardized
from app.services.session_service import answered_count

Method = Literal["bayes", "persona"]

# O ranking fica em memória por (sessão, número de pares, método), até 128 entradas.
CACHE_LIMIT = 128

_cache: OrderedDict[tuple[str, int, str], list[FeedItem]] = OrderedDict()


def feed_page(
    db: Session,
    session: SessionModel,
    method: Method = "bayes",
    at: int | None = None,
    limit: int = 30,
    offset: int = 0,
) -> FeedPage:
    """Uma página do feed da sessão, com o ranking pela afinidade."""
    answered = answered_count(db, session)
    n = answered if at is None else at
    if n < 0 or n > answered:
        raise ApiError(
            422,
            "validation_error",
            f"O número de pares tem de estar entre 0 e {answered}.",
        )

    ranked = _ranking(db, session, n, method)
    total = len(ranked)
    window = ranked[offset : offset + limit]
    items = [
        item.model_copy(update={"rank": offset + index + 1}) for index, item in enumerate(window)
    ]
    consumed = offset + len(items)
    return FeedPage(
        items=items,
        next_offset=consumed if consumed < total else None,
        method=method,
        n_comparisons=n,
    )


def clear_cache() -> None:
    """Esvazia o cache do ranking (usado nos testes)."""
    _cache.clear()


def _ranking(db: Session, session: SessionModel, n: int, method: Method) -> list[FeedItem]:
    """O ranking inteiro da sessão, com o cache em memória."""
    key = (str(session.id), n, method)
    cached = _cache.get(key)
    if cached is not None:
        _cache.move_to_end(key)
        return cached

    candidates = candidate_listings(db, session)
    z = standardized(db, session, candidates)
    if method == "bayes":
        samples = get_or_fit(db, session, n).samples
    else:
        mu, _ = prior(db, session)
        samples = mu[None, :]

    affinity = compute_affinity(z, samples)
    w_mean = samples.mean(axis=0)

    items: list[FeedItem] = []
    for index, listing in enumerate(candidates):
        reasons = explain(z[index], w_mean) if method == "bayes" else []
        items.append(
            FeedItem(
                listing=listing_card(listing),
                score=to_score(float(affinity.mean[index]), 0),
                affinity_pct=round(100 * float(affinity.mean[index]), 1),
                interval=(
                    round(100 * float(affinity.p5[index]), 1),
                    round(100 * float(affinity.p95[index]), 1),
                ),
                inspection_delta=0,
                reasons=[
                    Reason(
                        feature_key=reason.feature_key,
                        text=reason.text,
                        contribution=reason.contribution,
                    )
                    for reason in reasons
                ],
                rank=0,
            )
        )

    order = sorted(
        range(len(items)),
        key=lambda index: (-float(affinity.mean[index]), items[index].listing.code),
    )
    ranked = [items[index] for index in order]

    _cache[key] = ranked
    while len(_cache) > CACHE_LIMIT:
        _cache.popitem(last=False)
    return ranked
