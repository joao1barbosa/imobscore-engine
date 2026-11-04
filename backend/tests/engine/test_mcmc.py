"""Testes do Metropolis-Hastings (seção 5.4 e tarefa A05)."""

import logging
from pathlib import Path
from time import perf_counter

import numpy as np
import pytest
import yaml
from scipy.optimize import minimize
from scipy.special import logsumexp

from app.engine import FEATURE_KEYS, MCMCConfig, fit_posterior, fit_stats, raw_matrix, standardize
from app.engine.diagnostics import effective_sample_size, split_rhat
from app.engine.mcmc import STEP_MAX, STEP_MIN, run_chains
from app.engine.model import log_posterior, sigmoid
from app.seed import generate_catalog

SEED_DIR = Path(__file__).resolve().parents[2] / "app" / "seed"
N_DIMS = len(FEATURE_KEYS)
# O padrão foi calibrado para até 40 pares. Com 300 pares a posteriori fica estreita e os
# pesos do catálogo são correlacionados, então estes testes rodam cadeias mais longas.
LONG = MCMCConfig(warmup=4000, draws=16_000, thin=16)
LONGER = MCMCConfig(warmup=8000, draws=32_000, thin=32)


@pytest.fixture(scope="module")
def Z() -> np.ndarray:
    T = raw_matrix(generate_catalog(42))
    center, scale = fit_stats(T)
    return standardize(T, center, scale)


def simulate(Z: np.ndarray, w: np.ndarray, n: int, seed: int) -> np.ndarray:
    """Usuário sintético com pesos `w`: devolve D (n, 12), do vencedor para o perdedor."""
    rng = np.random.default_rng(seed)
    first = rng.integers(0, len(Z), n)
    second = (first + rng.integers(1, len(Z), n)) % len(Z)
    d = Z[first] - Z[second]
    first_wins = rng.random(n) < sigmoid(d @ w)
    return np.where(first_wins[:, None], d, -d)


def persona_prior(index: int = 0) -> tuple[np.ndarray, np.ndarray]:
    persona = yaml.safe_load((SEED_DIR / "personas.yaml").read_text(encoding="utf-8"))[index]
    mu = np.array([persona["prior_mean"][key] for key in FEATURE_KEYS])
    sd = np.array([persona["prior_sd"][key] for key in FEATURE_KEYS])
    return mu, sd


def true_weights(scale: float = 1.0, seed: int = 9) -> np.ndarray:
    return scale * np.random.default_rng(seed).normal(0.0, 1.0, N_DIMS)


def find_map(D: np.ndarray, prior_sd: float) -> np.ndarray:
    """O ponto de maior densidade da posteriori, com priori N(0, prior_sd^2)."""

    def neg_log_posterior(w: np.ndarray) -> float:
        return float(np.logaddexp(0.0, -(D @ w)).sum() + 0.5 * ((w / prior_sd) ** 2).sum())

    def gradient(w: np.ndarray) -> np.ndarray:
        grad: np.ndarray = -(D * sigmoid(-(D @ w))[:, None]).sum(axis=0) + w / prior_sd**2
        return grad

    found = minimize(neg_log_posterior, np.zeros(N_DIMS), jac=gradient, method="BFGS")
    map_w: np.ndarray = found.x
    return map_w


def importance_mean(D: np.ndarray, map_w: np.ndarray, prior_sd: float, seed: int) -> np.ndarray:
    """Média da posteriori por amostragem por importância, sem nada de MCMC.

    A proposta é uma t de Student centrada no MAP, com a curvatura da posteriori.
    """
    rng = np.random.default_rng(seed)
    n_draws, df = 100_000, 6
    p = sigmoid(D @ map_w)
    hessian = (D * (p * (1 - p))[:, None]).T @ D + np.eye(N_DIMS) / prior_sd**2
    chol = np.linalg.cholesky(1.3 * np.linalg.inv(hessian))

    z = rng.standard_normal((n_draws, N_DIMS))
    radius = np.sqrt(rng.chisquare(df, n_draws) / df)[:, None]
    draws = map_w + (z / radius) @ chol.T

    log_q = -(df + N_DIMS) / 2 * np.log1p(((z / radius) ** 2).sum(axis=1) / df)
    log_p = log_posterior(draws, D, np.zeros(N_DIMS), prior_sd * np.ones(N_DIMS))
    log_weights = log_p - log_q
    weights = np.exp(log_weights - logsumexp(log_weights))
    mean: np.ndarray = weights @ draws
    return mean


# (a) alvo conhecido


def test_a_recupera_um_alvo_gaussiano_conhecido() -> None:
    rng = np.random.default_rng(11)
    target_mean = rng.normal(0.0, 1.0, N_DIMS)
    target_sd = rng.uniform(0.5, 1.5, N_DIMS)

    def log_target(W: np.ndarray) -> np.ndarray:
        return -0.5 * (((W - target_mean) / target_sd) ** 2).sum(axis=1)

    run = run_chains(log_target, np.zeros(N_DIMS), np.ones(N_DIMS), rng, LONGER)
    flat = run.samples.reshape(-1, N_DIMS)

    assert np.all(np.abs(flat.mean(axis=0) - target_mean) < 0.1)
    assert np.all(np.abs(flat.var(axis=0) / target_sd**2 - 1.0) < 0.10)
    # (f) nesse caso
    assert split_rhat(run.samples).max() < 1.05
    assert effective_sample_size(run.samples).min() > 400


# (b) sem pares


def test_b_sem_pares_as_amostras_reproduzem_a_priori() -> None:
    mu, sd = persona_prior()

    result = fit_posterior(np.empty((0, N_DIMS)), mu, sd, seed=1)

    assert result.samples.shape == (4000, N_DIMS)
    assert np.all(np.abs(result.samples.mean(axis=0) - mu) < 4 * sd / np.sqrt(4000))
    assert np.all(np.abs(result.samples.std(axis=0) / sd - 1.0) < 0.05)


def test_b_sem_pares_os_diagnosticos_sao_os_da_interface() -> None:
    mu, sd = persona_prior()

    d = fit_posterior(np.empty((0, N_DIMS)), mu, sd, seed=1).diagnostics

    assert (d.accept_rate, d.rhat_max, d.ess_min, d.step_size) == (1.0, 1.0, 4000.0, 0.0)
    assert d.ok


def test_b_as_cadeias_tambem_reproduzem_a_priori_sem_dados() -> None:
    # Confere a própria cadeia, porque com m = 0 `fit_posterior` não a usa.
    mu, sd = persona_prior()

    def log_target(W: np.ndarray) -> np.ndarray:
        return log_posterior(W, np.empty((0, N_DIMS)), mu, sd)

    run = run_chains(log_target, mu, sd, np.random.default_rng(2), LONG)
    flat = run.samples.reshape(-1, N_DIMS)

    assert np.all(np.abs(flat.mean(axis=0) - mu) < 0.15 * sd)
    assert np.all(np.abs(flat.std(axis=0) / sd - 1.0) < 0.10)


# (c) usuário sintético


def test_c_recupera_os_pesos_de_um_usuario_sintetico(Z: np.ndarray) -> None:
    w = true_weights()
    D = simulate(Z, w, 300, seed=5)

    result = fit_posterior(D, np.zeros(N_DIMS), np.ones(N_DIMS), seed=3, cfg=LONG)

    assert np.corrcoef(result.samples.mean(axis=0), w)[0, 1] > 0.9
    # (f) nesse caso
    assert result.diagnostics.rhat_max < 1.05
    assert result.diagnostics.ess_min > 400


# (d) priori fraca


def test_d_com_priori_fraca_a_media_fica_perto_do_map(Z: np.ndarray) -> None:
    # Pesos moderados: com os escolhidos quase sempre acertados, a posteriori fica assimétrica
    # e a média se afasta do MAP de verdade (ver o teste seguinte).
    D = simulate(Z, true_weights(scale=0.5), 300, seed=5)
    prior_sd = 10.0

    result = fit_posterior(D, np.zeros(N_DIMS), prior_sd * np.ones(N_DIMS), seed=3, cfg=LONGER)

    assert np.all(np.abs(result.samples.mean(axis=0) - find_map(D, prior_sd)) < 0.15)
    # (f) nesse caso
    assert result.diagnostics.rhat_max < 1.05
    assert result.diagnostics.ess_min > 400


def test_d_posteriori_assimetrica_bate_com_um_calculo_independente(Z: np.ndarray) -> None:
    # Neste caso a média fica a cerca de 0,5 do MAP: quem explica é a posteriori, não a
    # cadeia, porque a amostragem por importância chega à mesma média sem usar MCMC.
    D = simulate(Z, true_weights(), 300, seed=5)
    prior_sd = 10.0
    map_w = find_map(D, prior_sd)

    result = fit_posterior(D, np.zeros(N_DIMS), prior_sd * np.ones(N_DIMS), seed=3, cfg=LONGER)
    mean = result.samples.mean(axis=0)

    assert np.abs(mean - map_w).max() > 0.15
    assert np.all(np.abs(mean - importance_mean(D, map_w, prior_sd, seed=4)) < 0.1)


# (e) reprodutibilidade


def test_e_mesma_semente_mesmas_amostras(Z: np.ndarray) -> None:
    mu, sd = persona_prior()
    D = simulate(Z, mu, 8, seed=6)

    first = fit_posterior(D, mu, sd, seed=42)
    second = fit_posterior(D, mu, sd, seed=42)
    other = fit_posterior(D, mu, sd, seed=43)

    assert np.array_equal(first.samples, second.samples)
    assert not np.array_equal(first.samples, other.samples)


def test_e_sem_pares_mesma_semente_mesmas_amostras() -> None:
    mu, sd = persona_prior()
    empty = np.empty((0, N_DIMS))

    assert np.array_equal(
        fit_posterior(empty, mu, sd, seed=7).samples, fit_posterior(empty, mu, sd, seed=7).samples
    )


# (f) no uso real: o que a demo, o produto e a avaliação rodam


@pytest.mark.parametrize("n_pairs", [3, 8, 15])
@pytest.mark.parametrize("persona", [0, 1, 2])
def test_f_converge_no_uso_real_com_a_configuracao_padrao(
    Z: np.ndarray, n_pairs: int, persona: int
) -> None:
    mu, sd = persona_prior(persona)
    D = simulate(Z, mu + sd * np.random.default_rng(persona).standard_normal(N_DIMS), n_pairs, 7)

    d = fit_posterior(D, mu, sd, seed=n_pairs).diagnostics

    assert d.ok
    assert d.rhat_max < 1.05
    assert d.ess_min > 400
    assert 0.15 <= d.accept_rate <= 0.50


# Forma, passo e nova tentativa


def test_as_amostras_ficam_em_ordem_por_cadeia(Z: np.ndarray) -> None:
    mu, sd = persona_prior()
    D = simulate(Z, mu, 3, seed=8)
    seed = 21

    result = fit_posterior(D, mu, sd, seed=seed)

    def log_target(W: np.ndarray) -> np.ndarray:
        return log_posterior(W, D, mu, sd)

    run = run_chains(log_target, mu, sd, np.random.default_rng(seed), MCMCConfig())
    assert result.n_chains == 16
    assert np.array_equal(result.samples[:250], run.samples[0])
    assert np.array_equal(result.samples[250:500], run.samples[1])


def test_o_passo_sobe_ate_o_limite_quando_tudo_e_aceito() -> None:
    def flat(W: np.ndarray) -> np.ndarray:
        return np.zeros(W.shape[0])

    run = run_chains(
        flat, np.zeros(2), np.ones(2), np.random.default_rng(1), MCMCConfig(4, 1000, 100, 1)
    )

    assert run.step_size == STEP_MAX
    assert run.accept_rate == 1.0


def test_o_passo_desce_ate_o_limite_quando_nada_e_aceito() -> None:
    def spike(W: np.ndarray) -> np.ndarray:
        return -0.5 * ((W / 1e-6) ** 2).sum(axis=1)

    run = run_chains(
        spike, np.zeros(2), np.ones(2), np.random.default_rng(1), MCMCConfig(4, 1000, 100, 1)
    )

    assert run.step_size == STEP_MIN


def test_o_passo_nao_muda_depois_do_aquecimento() -> None:
    def flat(W: np.ndarray) -> np.ndarray:
        return np.zeros(W.shape[0])

    no_draws = run_chains(
        flat, np.zeros(2), np.ones(2), np.random.default_rng(1), MCMCConfig(4, 200, 8, 1)
    )
    with_draws = run_chains(
        flat, np.zeros(2), np.ones(2), np.random.default_rng(1), MCMCConfig(4, 200, 2000, 1)
    )

    assert no_draws.step_size == with_draws.step_size


def test_sem_convergir_avisa_no_log_e_ainda_devolve_as_amostras(
    Z: np.ndarray, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # O `fileConfig` do Alembic, que a fixture da migração roda neste mesmo processo,
    # desliga os loggers já existentes. A API não roda migração no mesmo processo.
    monkeypatch.setattr(logging.getLogger("app.engine.mcmc"), "disabled", False)
    mu, sd = persona_prior()
    D = simulate(Z, mu, 8, seed=10)
    short = MCMCConfig(warmup=50, draws=100, thin=1)

    with caplog.at_level(logging.WARNING, logger="app.engine.mcmc"):
        result = fit_posterior(D, mu, sd, seed=1, cfg=short)

    assert not result.diagnostics.ok
    assert "MCMC não convergiu" in caplog.text
    # A nova tentativa dobra as amostras e o desbaste: S não muda.
    assert result.samples.shape == (16 * 100, N_DIMS)


# (g) desempenho


@pytest.mark.perf
def test_g_uma_passada_com_40_pares_leva_menos_de_250_ms(Z: np.ndarray) -> None:
    mu, sd = persona_prior()
    D = simulate(Z, mu, 40, seed=12)

    # Uma passada do algoritmo com o cálculo dos diagnósticos. A nova tentativa, comum com
    # 40 pares, leva cerca de 3 vezes esse tempo; os testes (f) cobrem o uso real.
    def log_target(W: np.ndarray) -> np.ndarray:
        return log_posterior(W, D, mu, sd)

    times = []
    for seed in range(5):
        start = perf_counter()
        run = run_chains(log_target, mu, sd, np.random.default_rng(seed), MCMCConfig())
        split_rhat(run.samples)
        effective_sample_size(run.samples)
        times.append(perf_counter() - start)

    assert np.median(times) < 0.250
