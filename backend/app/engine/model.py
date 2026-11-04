"""Modelo de Bradley-Terry: sigmoide, verossimilhança e posteriori (seção 5.2)."""

import numpy as np


def sigmoid(u: np.ndarray) -> np.ndarray:
    """Calcula 1 / (1 + e^-u) sem estourar com |u| grande."""
    p: np.ndarray = np.exp(-np.logaddexp(0.0, -u))
    return p


def log_likelihood(W: np.ndarray, D: np.ndarray) -> np.ndarray:
    """W (C, 12), D (m, 12) -> (C,). Cada linha de D é orientada do vencedor para o perdedor."""
    u = W @ D.T
    ll: np.ndarray = -np.logaddexp(0.0, -u).sum(axis=1)
    return ll


def log_prior(W: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    """W (C, 12) -> (C,). Priori normal independente, sem a constante."""
    lp: np.ndarray = -0.5 * (((W - mu) / sd) ** 2).sum(axis=1)
    return lp


def log_posterior(W: np.ndarray, D: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray:
    """Soma da log-verossimilhança com a log-priori. Com m = 0, é só a priori."""
    lp: np.ndarray = log_likelihood(W, D) + log_prior(W, mu, sd)
    return lp
