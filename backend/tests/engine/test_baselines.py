"""Testes dos métodos de comparação (seção 5.8)."""

import numpy as np
import pytest

from app.engine import FEATURE_KEYS, FEATURES, Method, fit_mle, predict_proba
from app.engine.model import sigmoid

N = len(FEATURE_KEYS)


@pytest.fixture
def D() -> np.ndarray:
    return np.random.default_rng(1).standard_normal((30, N))


def test_fit_mle_treina_com_um_par_so() -> None:
    d = np.random.default_rng(2).standard_normal((1, N))

    w = fit_mle(d)

    assert w.shape == (N,)
    assert np.all(np.isfinite(w))
    # O par visto como vencedor recebe mais de 50% de chance.
    assert sigmoid(d @ w)[0] > 0.5


def test_fit_mle_regularizado_nao_explode_em_dados_separaveis() -> None:
    # Três pares separáveis: sem regularização, os pesos iriam para o infinito.
    d = np.random.default_rng(3).standard_normal((3, N))

    assert np.abs(fit_mle(d)).max() < 5.0


def test_fit_mle_recupera_a_direcao_dos_pesos() -> None:
    rng = np.random.default_rng(4)
    w_true = rng.normal(0.0, 1.0, N)
    d = rng.standard_normal((500, N))
    wins = rng.random(500) < sigmoid(d @ w_true)
    oriented = np.where(wins[:, None], d, -d)

    assert np.corrcoef(fit_mle(oriented), w_true)[0, 1] > 0.9


def test_fit_mle_nao_tem_viés() -> None:
    d = np.random.default_rng(5).standard_normal((20, N))

    assert sigmoid(np.zeros((1, N)) @ fit_mle(d))[0] == 0.5


@pytest.mark.parametrize("method", ["equal", "persona", "mle", "bayes"])
def test_os_quatro_metodos_devolvem_valores_entre_0_e_1(method: Method, D: np.ndarray) -> None:
    rng = np.random.default_rng(6)
    p = predict_proba(
        method,
        D,
        mu=rng.normal(0.0, 1.0, N),
        samples=rng.normal(0.0, 1.0, (400, N)),
        w_mle=fit_mle(D),
    )

    assert p.shape == (30,)
    assert np.all((p > 0.0) & (p < 1.0))


@pytest.mark.parametrize("method", ["equal", "persona", "mle", "bayes"])
def test_inverter_o_par_inverte_a_probabilidade(method: Method, D: np.ndarray) -> None:
    rng = np.random.default_rng(7)
    args = {
        "mu": rng.normal(0.0, 1.0, N),
        "samples": rng.normal(0.0, 1.0, (400, N)),
        "w_mle": fit_mle(D),
    }

    forward = predict_proba(method, D, **args)
    backward = predict_proba(method, -D, **args)

    assert forward + backward == pytest.approx(np.ones(30))


def test_equal_usa_as_direcoes_da_tabela() -> None:
    directions = np.array([feature.direction for feature in FEATURES], dtype=float)
    d = np.eye(N)

    assert predict_proba("equal", d) == pytest.approx(sigmoid(directions))


def test_bayes_e_a_media_das_sigmoides() -> None:
    d = np.zeros((1, N))
    d[0, 0] = 1.0
    samples = np.zeros((2, N))
    samples[:, 0] = [3.0, -1.0]

    p = predict_proba("bayes", d, samples=samples)

    assert p[0] == pytest.approx((sigmoid(np.array(3.0)) + sigmoid(np.array(-1.0))) / 2)


@pytest.mark.parametrize("method", ["persona", "mle", "bayes"])
def test_metodo_sem_o_argumento_necessario_avisa(method: Method, D: np.ndarray) -> None:
    with pytest.raises(ValueError, match=method):
        predict_proba(method, D)
