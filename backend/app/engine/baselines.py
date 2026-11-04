"""Métodos de comparação com o motor bayesiano (seção 5.8)."""

from typing import Literal

import numpy as np
from sklearn.linear_model import LogisticRegression  # type: ignore[import-untyped]

from app.engine.features import FEATURES
from app.engine.model import sigmoid

Method = Literal["equal", "persona", "mle", "bayes"]

EQUAL_WEIGHTS = np.array([float(feature.direction) for feature in FEATURES])


def fit_mle(D: np.ndarray) -> np.ndarray:
    """D (m, 12) -> (12,). Regressão logística com a regularização L2 padrão (C = 1).

    Cada par entra duas vezes, (d, 1) e (-d, 0): com só um rótulo, o scikit-learn recusa
    o treino. Sem a regularização, com 3 pares os pesos iriam para o infinito.
    """
    X = np.vstack((D, -D))
    y = np.concatenate((np.ones(D.shape[0]), np.zeros(D.shape[0])))
    model = LogisticRegression(fit_intercept=False, C=1.0)
    model.fit(X, y)
    weights: np.ndarray = model.coef_[0]
    return weights


def predict_proba(
    method: Method,
    D: np.ndarray,
    *,
    mu: np.ndarray | None = None,
    samples: np.ndarray | None = None,
    w_mle: np.ndarray | None = None,
) -> np.ndarray:
    """D (m, 12) -> (m,): a probabilidade de o primeiro imóvel de cada linha vencer."""
    if method == "equal":
        return sigmoid(D @ EQUAL_WEIGHTS)
    if method == "persona":
        if mu is None:
            raise ValueError('O método "persona" precisa de mu.')
        return sigmoid(D @ mu)
    if method == "mle":
        if w_mle is None:
            raise ValueError('O método "mle" precisa de w_mle.')
        return sigmoid(D @ w_mle)
    if samples is None:
        raise ValueError('O método "bayes" precisa de samples.')
    probabilities: np.ndarray = sigmoid(D @ samples.T).mean(axis=1)
    return probabilities
