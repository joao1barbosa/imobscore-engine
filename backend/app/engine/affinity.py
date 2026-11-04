"""Afinidade, score e explicação de cada imóvel (seção 5.6)."""

from dataclasses import dataclass

import numpy as np

from app.engine.features import FEATURES
from app.engine.model import sigmoid

MIN_CONTRIBUTION = 0.1
MAX_POSITIVE = 3


@dataclass(frozen=True)
class AffinityResult:
    """`mean`, `p5` e `p95` têm forma (n,), com valores em [0, 1]."""

    mean: np.ndarray
    p5: np.ndarray
    p95: np.ndarray


@dataclass(frozen=True)
class Reason:
    feature_key: str
    text: str
    contribution: float


def compute_affinity(Z: np.ndarray, samples: np.ndarray) -> AffinityResult:
    """Z (n, 12), samples (S, 12). Para o método "persona": samples = mu[None, :]."""
    affinity = sigmoid(Z @ samples.T)  # (n, S)
    # A média das sigmoides, e não a sigmoide da média: é assim que a incerteza dos
    # pesos entra no score.
    p5, p95 = np.percentile(affinity, [5, 95], axis=1)
    return AffinityResult(mean=affinity.mean(axis=1), p5=p5, p95=p95)


def to_score(affinity: float, inspection_delta: int = 0) -> int:
    """clip(round(100 * afinidade) + delta, 0, 100)."""
    return min(max(round(100 * affinity) + inspection_delta, 0), 100)


def explain(z: np.ndarray, w_mean: np.ndarray, max_reasons: int = 4) -> list[Reason]:
    """As maiores contribuições positivas e a mais negativa, ignorando |c| < 0,1."""
    contributions = w_mean * z
    order = np.argsort(-contributions, kind="stable")
    positives = [int(j) for j in order if contributions[j] >= MIN_CONTRIBUTION]
    negatives = [int(j) for j in order[::-1] if contributions[j] <= -MIN_CONTRIBUTION]

    # A mais negativa sempre aparece, para o motivo não mostrar só o lado bom do imóvel.
    negative = negatives[:1]
    positive = positives[: min(MAX_POSITIVE, max_reasons - len(negative))]

    return [
        Reason(
            feature_key=FEATURES[j].key,
            text=FEATURES[j].text_high if z[j] > 0 else FEATURES[j].text_low,
            contribution=float(contributions[j]),
        )
        for j in positive + negative
    ]
