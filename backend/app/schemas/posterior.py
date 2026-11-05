"""Schemas da posteriori: os pesos, o diagnóstico e o traço das cadeias."""

from pydantic import BaseModel

from app.schemas.pair import Diagnostics


class WeightOut(BaseModel):
    """Um peso da posteriori: a priori da persona e o que os pares responderam."""

    feature_key: str
    label: str
    prior_mean: float
    prior_sd: float
    post_mean: float
    post_sd: float
    ci_low: float
    ci_high: float


class PosteriorOut(BaseModel):
    """A posteriori da sessão, com os doze pesos e o diagnóstico do MCMC."""

    n_comparisons: int
    weights: list[WeightOut]
    diagnostics: Diagnostics


class TraceOut(BaseModel):
    """O traço das primeiras cadeias de um peso."""

    feature_key: str
    chains: list[list[float]]
