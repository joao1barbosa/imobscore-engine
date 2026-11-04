"""Testes do modelo: estabilidade numérica e conferência com o scikit-learn (seção 5.2)."""

import warnings

import numpy as np
from sklearn.metrics import log_loss

from app.engine.model import log_likelihood, log_posterior, log_prior, sigmoid


def test_sigmoid_is_stable_for_large_values() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        p = sigmoid(np.array([-1000.0, 0.0, 1000.0]))

    assert not np.isnan(p).any()
    np.testing.assert_allclose(p, [0.0, 0.5, 1.0])


def test_sigmoid_symmetry() -> None:
    u = np.linspace(-20, 20, 81)

    np.testing.assert_allclose(sigmoid(u) + sigmoid(-u), np.ones_like(u))


def test_log_likelihood_matches_sklearn() -> None:
    rng = np.random.default_rng(0)
    m = 40
    w = rng.normal(size=12)
    D = rng.normal(size=(m, 12))
    p = sigmoid(D @ w)

    expected = -log_loss(np.ones(m), p, labels=[0, 1]) * m

    np.testing.assert_allclose(log_likelihood(w[None, :], D), [expected])


def test_log_likelihood_is_finite_for_large_values() -> None:
    D = np.full((3, 12), 100.0)

    assert np.isfinite(log_likelihood(np.full((2, 12), -10.0), D)).all()


def test_functions_evaluate_every_chain_at_once() -> None:
    rng = np.random.default_rng(1)
    W = rng.normal(size=(16, 12))
    D = rng.normal(size=(5, 12))
    mu, sd = rng.normal(size=12), np.ones(12)

    together = log_posterior(W, D, mu, sd)
    one_by_one = [log_posterior(w[None, :], D, mu, sd)[0] for w in W]

    assert together.shape == (16,)
    np.testing.assert_allclose(together, one_by_one)


def test_without_pairs_posterior_equals_prior() -> None:
    rng = np.random.default_rng(2)
    W = rng.normal(size=(4, 12))
    mu, sd = rng.normal(size=12), np.full(12, 1.5)

    np.testing.assert_array_equal(log_posterior(W, np.empty((0, 12)), mu, sd), log_prior(W, mu, sd))


def test_log_prior_is_highest_at_the_mean() -> None:
    mu = np.arange(12.0)
    sd = np.ones(12)

    values = log_prior(np.stack([mu, mu + 1.0]), mu, sd)

    assert values[0] == 0.0
    assert values[1] == -6.0
