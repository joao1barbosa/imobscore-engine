"""Diagnósticos do MCMC: R-hat dividido, ESS e o critério de aprovação (seção 5.5)."""

from dataclasses import dataclass

import numpy as np

RHAT_LIMIT = 1.05
ESS_LIMIT = 400.0
ACCEPT_MIN = 0.15
ACCEPT_MAX = 0.50


@dataclass(frozen=True)
class Diagnostics:
    """Mesmos nomes do schema `Diagnostics` da API (seção 6)."""

    accept_rate: float
    rhat_max: float
    ess_min: float
    step_size: float
    elapsed_ms: int
    ok: bool


def split_rhat(samples: np.ndarray) -> np.ndarray:
    """samples (C, K, d) -> (d,). Perto de 1: as meias-cadeias concordam entre si."""
    n = samples.shape[1] // 2
    halves = np.concatenate((samples[:, :n], samples[:, n : 2 * n]), axis=0)

    within = halves.var(axis=1, ddof=1).mean(axis=0)
    between = n * halves.mean(axis=1).var(axis=0, ddof=1)
    pooled = (n - 1) / n * within + between / n

    # Cadeias paradas não têm variância: só concordam se estiverem todas no mesmo ponto.
    ratio = np.full_like(within, np.inf)
    ratio[(within == 0.0) & (between == 0.0)] = 1.0
    moving = within > 0.0
    ratio[moving] = pooled[moving] / within[moving]
    rhat: np.ndarray = np.sqrt(ratio)
    return rhat


def _mean_autocorrelation(samples: np.ndarray) -> np.ndarray:
    """samples (C, K, d) -> (K, d): autocorrelação por defasagem, em média entre as cadeias."""
    n_kept = samples.shape[1]
    centered = samples - samples.mean(axis=1, keepdims=True)

    # O dobro de pontos evita que a FFT misture o fim da cadeia com o começo.
    n_fft = 2 * n_kept
    spectrum = np.fft.rfft(centered, n=n_fft, axis=1)
    autocov = np.fft.irfft(spectrum * np.conj(spectrum), n=n_fft, axis=1)[:, :n_kept]

    # Cadeia parada: nada muda de uma amostra para a outra, então a correlação é 1.
    variance = autocov[:, :1, :]
    rho = np.divide(autocov, variance, out=np.ones_like(autocov), where=variance > 1e-20)

    mean_rho: np.ndarray = rho.mean(axis=0)
    return mean_rho


def effective_sample_size(samples: np.ndarray) -> np.ndarray:
    """samples (C, K, d) -> (d,). Amostras independentes que estas S equivalem (Geyer)."""
    n_chains, n_kept, n_dims = samples.shape
    total = n_chains * n_kept
    rho = _mean_autocorrelation(samples)

    ess = np.empty(n_dims)
    for dim in range(n_dims):
        # Pares consecutivos (rho_0 + rho_1), (rho_2 + rho_3)...: para no primeiro negativo.
        n_pairs = n_kept // 2
        pairs = rho[: 2 * n_pairs, dim].reshape(n_pairs, 2).sum(axis=1)
        negative = np.flatnonzero(pairs < 0.0)
        stop = int(negative[0]) if negative.size else n_pairs
        # -1 + 2 * soma dos pares é o mesmo que 1 + 2 * (rho_1 + rho_2 + ...).
        # O piso de 1 impede que uma correlação negativa prometa mais que S amostras.
        tau = max(-1.0 + 2.0 * float(pairs[:stop].sum()), 1.0)
        ess[dim] = total / tau
    return ess


def is_ok(accept_rate: float, rhat_max: float, ess_min: float) -> bool:
    """O critério da seção 5.5."""
    return rhat_max < RHAT_LIMIT and ess_min > ESS_LIMIT and ACCEPT_MIN <= accept_rate <= ACCEPT_MAX
