"""Metropolis-Hastings vetorizado para a posteriori dos pesos (seção 5.4)."""

import logging
from collections.abc import Callable
from dataclasses import dataclass, replace
from math import exp, sqrt
from time import perf_counter

import numpy as np

from app.engine.diagnostics import Diagnostics, effective_sample_size, is_ok, split_rhat
from app.engine.model import log_posterior

logger = logging.getLogger(__name__)

INITIAL_STEP = 2.38 / sqrt(12)
ADAPT_WINDOW = 50
STEP_MIN = 0.01
STEP_MAX = 5.0

LogTarget = Callable[[np.ndarray], np.ndarray]


@dataclass(frozen=True)
class MCMCConfig:
    chains: int = 16
    warmup: int = 1000
    draws: int = 2000
    thin: int = 8
    target_accept: float = 0.30


DEFAULT_CONFIG = MCMCConfig()


@dataclass(frozen=True)
class MCMCResult:
    """`samples` (S, 12), em ordem por cadeia: as linhas [k*K:(k+1)*K] são a cadeia k."""

    samples: np.ndarray
    n_chains: int
    seed: int
    diagnostics: Diagnostics


@dataclass(frozen=True)
class ChainRun:
    """`samples` (C, K, d), com K = draws // thin."""

    samples: np.ndarray
    accept_rate: float
    step_size: float


def run_chains(
    log_target: LogTarget,
    mu: np.ndarray,
    sd: np.ndarray,
    rng: np.random.Generator,
    cfg: MCMCConfig,
) -> ChainRun:
    """Passeio aleatório com as C cadeias avançando juntas. `log_target`: (C, d) -> (C,)."""
    n_dims = mu.shape[0]
    n_kept = cfg.draws // cfg.thin
    samples = np.empty((cfg.chains, n_kept, n_dims))

    # As cadeias começam espalhadas, o que é necessário para o R-hat funcionar.
    W = mu + sd * rng.standard_normal((cfg.chains, n_dims))
    lp = log_target(W)
    step = INITIAL_STEP

    window_accepted = 0
    draws_accepted = 0
    kept = 0
    for t in range(1, cfg.warmup + cfg.draws + 1):
        W_prop = W + step * sd * rng.standard_normal((cfg.chains, n_dims))
        lp_prop = log_target(W_prop)

        # A proposta é simétrica: q(W'|W) = q(W|W'). A razão de Hastings se cancela
        # e por isso não aparece aqui; sobra só a diferença das log-posterioris.
        accept = np.log(rng.random(cfg.chains)) < lp_prop - lp
        W[accept] = W_prop[accept]
        lp[accept] = lp_prop[accept]
        n_accepted = int(accept.sum())

        if t <= cfg.warmup:
            window_accepted += n_accepted
            if t % ADAPT_WINDOW == 0:
                rate = window_accepted / (ADAPT_WINDOW * cfg.chains)
                step = min(max(step * exp(rate - cfg.target_accept), STEP_MIN), STEP_MAX)
                window_accepted = 0
        else:
            # Depois do aquecimento o passo fica fixo, o que mantém a cadeia válida.
            draws_accepted += n_accepted
            if (t - cfg.warmup) % cfg.thin == 0:
                samples[:, kept] = W
                kept += 1

    return ChainRun(
        samples=samples,
        accept_rate=draws_accepted / (cfg.draws * cfg.chains),
        step_size=step,
    )


def fit_posterior(
    D: np.ndarray,
    mu: np.ndarray,
    sd: np.ndarray,
    seed: int,
    cfg: MCMCConfig = DEFAULT_CONFIG,
) -> MCMCResult:
    """D (m, 12): cada linha é z(vencedor) - z(perdedor). Com m = 0, sorteia da priori."""
    start = perf_counter()
    rng = np.random.default_rng(seed)
    total = cfg.chains * (cfg.draws // cfg.thin)

    if D.shape[0] == 0:
        return MCMCResult(
            samples=mu + sd * rng.standard_normal((total, mu.shape[0])),
            n_chains=cfg.chains,
            seed=seed,
            diagnostics=Diagnostics(
                accept_rate=1.0,
                rhat_max=1.0,
                ess_min=float(total),
                step_size=0.0,
                elapsed_ms=_elapsed_ms(start),
                ok=True,
            ),
        )

    def log_target(W: np.ndarray) -> np.ndarray:
        return log_posterior(W, D, mu, sd)

    run = run_chains(log_target, mu, sd, rng, cfg)
    rhat_max, ess_min = _convergence(run)
    if not is_ok(run.accept_rate, rhat_max, ess_min):
        # Nova tentativa com aquecimento e amostras dobrados (seção 5.5). O desbaste
        # também dobra, para S continuar igual ao que a API e o banco esperam.
        retry = replace(cfg, warmup=2 * cfg.warmup, draws=2 * cfg.draws, thin=2 * cfg.thin)
        run = run_chains(log_target, mu, sd, rng, retry)
        rhat_max, ess_min = _convergence(run)

    ok = is_ok(run.accept_rate, rhat_max, ess_min)
    if not ok:
        logger.warning(
            "MCMC não convergiu: seed=%d aceitação=%.3f rhat_max=%.3f ess_min=%.0f",
            seed,
            run.accept_rate,
            rhat_max,
            ess_min,
        )

    return MCMCResult(
        samples=run.samples.reshape(total, mu.shape[0]),
        n_chains=cfg.chains,
        seed=seed,
        diagnostics=Diagnostics(
            accept_rate=run.accept_rate,
            rhat_max=rhat_max,
            ess_min=ess_min,
            step_size=run.step_size,
            elapsed_ms=_elapsed_ms(start),
            ok=ok,
        ),
    )


def _convergence(run: ChainRun) -> tuple[float, float]:
    return float(split_rhat(run.samples).max()), float(effective_sample_size(run.samples).min())


def _elapsed_ms(start: float) -> int:
    return round((perf_counter() - start) * 1000)
