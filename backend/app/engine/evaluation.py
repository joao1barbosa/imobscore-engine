"""Protocolo de avaliação com pares nunca vistos e simulação de escolhas (seção 5.9)."""

from dataclasses import dataclass
from typing import get_args

import numpy as np

from app.engine.baselines import Method, fit_mle, predict_proba
from app.engine.mcmc import DEFAULT_CONFIG, MCMCConfig, fit_posterior
from app.engine.model import sigmoid
from app.engine.pairs import seed_for

LOG_LOSS_FLOOR = 1e-6


@dataclass(frozen=True)
class ResultRow:
    participant_code: str
    method: Method
    n_train: int
    split_seed: int
    n_test: int
    accuracy: float
    log_loss: float


def _score(p_winner: np.ndarray) -> tuple[float, float]:
    """p_winner (m,): a chance dada ao imóvel que venceu. Devolve acurácia e perda."""
    hits = np.where(p_winner == 0.5, 0.5, (p_winner > 0.5).astype(float))
    clipped = np.clip(p_winner, LOG_LOSS_FLOOR, 1.0 - LOG_LOSS_FLOOR)
    return float(hits.mean()), float(-np.log(clipped).mean())


def evaluate_participant(
    code: str,
    D: np.ndarray,
    mu: np.ndarray,
    sd: np.ndarray,
    *,
    n_train_list: tuple[int, ...] = (3, 5, 10, 15),
    n_splits: int = 20,
    n_test: int = 10,
    cfg: MCMCConfig = DEFAULT_CONFIG,
) -> list[ResultRow]:
    """D (m, 12): pares orientados do vencedor para o perdedor, na ordem respondida."""
    n_pairs = D.shape[0]
    if n_pairs < n_test + max(n_train_list):
        raise ValueError(
            f"{code} tem {n_pairs} pares; são precisos {n_test + max(n_train_list)} ou mais."
        )

    rows: list[ResultRow] = []
    for split_seed in range(n_splits):
        # A mesma ordem em todo n_train: com mais pares, o treino só cresce, e o teste é o mesmo.
        order = np.random.default_rng(seed_for(code, split_seed)).permutation(n_pairs)
        D_test = D[order[:n_test]]
        D_rest = D[order[n_test:]]

        for n_train in n_train_list:
            D_train = D_rest[:n_train]
            samples = fit_posterior(
                D_train, mu, sd, seed_for(f"{code}:{n_train}", split_seed), cfg
            ).samples
            w_mle = fit_mle(D_train)

            for method in get_args(Method):
                # O teste é orientado do vencedor: a probabilidade é a de acertar o par.
                p = predict_proba(method, D_test, mu=mu, samples=samples, w_mle=w_mle)
                accuracy, log_loss = _score(p)
                rows.append(
                    ResultRow(code, method, n_train, split_seed, n_test, accuracy, log_loss)
                )
    return rows


def simulate_choices(
    D_left_minus_right: np.ndarray, w_true: np.ndarray, rng: np.random.Generator
) -> np.ndarray:
    """(m,) de "A" ou "B", sorteados com P(A) = sigma(w_true . d)."""
    p_left = sigmoid(D_left_minus_right @ w_true)
    return np.where(rng.random(p_left.shape[0]) < p_left, "A", "B")
