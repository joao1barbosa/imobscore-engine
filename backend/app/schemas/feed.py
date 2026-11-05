"""Schemas do feed: o cartão com score, intervalo e motivos."""

from typing import Literal

from pydantic import BaseModel

from app.schemas.listing import ListingCard


class Reason(BaseModel):
    """Um motivo do imóvel, com a característica e a contribuição."""

    feature_key: str
    text: str
    contribution: float


class FeedItem(BaseModel):
    """Um imóvel do feed, com o score e o intervalo de afinidade."""

    listing: ListingCard
    score: int
    affinity_pct: float
    interval: tuple[float, float]
    inspection_delta: int
    reasons: list[Reason]
    rank: int


class FeedPage(BaseModel):
    """Uma página do feed da sessão."""

    items: list[FeedItem]
    next_offset: int | None
    method: Literal["bayes", "persona"]
    n_comparisons: int


class FeatureOut(BaseModel):
    """Uma característica do motor, com o texto para o cartão do imóvel."""

    key: str
    label: str
    text_high: str
    text_low: str


class InspectionItemOut(BaseModel):
    """Um item da vistoria, com o ajuste sugerido no score."""

    key: str
    label: str
    delta: int
