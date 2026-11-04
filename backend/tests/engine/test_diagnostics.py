"""Testes do R-hat dividido, do ESS e do critério de aprovação."""

import numpy as np
import pytest

from app.engine.diagnostics import effective_sample_size, is_ok, split_rhat


def ar1(rho: float, shape: tuple[int, int, int], seed: int) -> np.ndarray:
    """Cadeias autorregressivas de variância 1: o ESS teórico é S (1 - rho) / (1 + rho)."""
    rng = np.random.default_rng(seed)
    chains = np.empty(shape)
    chains[:, 0] = rng.standard_normal((shape[0], shape[2]))
    noise = rng.standard_normal(shape) * np.sqrt(1 - rho**2)
    for t in range(1, shape[1]):
        chains[:, t] = rho * chains[:, t - 1] + noise[:, t]
    return chains


def test_rhat_segue_a_formula_da_secao_5_5() -> None:
    # Duas cadeias com 4 pontos viram 4 meias-cadeias com n = 2.
    samples = np.array([[1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0]])[:, :, None]
    # Médias 1,5; 3,5; 3; 7. Variâncias 0,5; 0,5; 2; 2.
    within = 1.25
    between = 2 * np.var([1.5, 3.5, 3.0, 7.0], ddof=1)
    expected = np.sqrt((0.5 * within + between / 2) / within)

    assert split_rhat(samples)[0] == pytest.approx(expected)


def test_rhat_fica_perto_de_1_quando_as_cadeias_concordam() -> None:
    samples = np.random.default_rng(1).standard_normal((16, 250, 3))

    assert np.all(np.abs(split_rhat(samples) - 1.0) < 0.02)


def test_rhat_acusa_cadeias_em_lugares_diferentes() -> None:
    samples = np.random.default_rng(2).standard_normal((16, 250, 1))
    samples[8:] += 3.0

    assert split_rhat(samples)[0] > 1.3


def test_rhat_acusa_uma_cadeia_que_ainda_esta_descendo() -> None:
    samples = np.random.default_rng(3).standard_normal((16, 250, 1))
    samples += np.linspace(6.0, 0.0, 250)[None, :, None]

    assert split_rhat(samples)[0] > 1.05


def test_rhat_com_cadeias_paradas_nao_quebra() -> None:
    same = np.zeros((4, 10, 1))
    apart = np.arange(4.0)[:, None, None] * np.ones((4, 10, 1))

    assert split_rhat(same)[0] == 1.0
    assert split_rhat(apart)[0] == np.inf


def test_ess_de_amostras_independentes_fica_perto_de_s() -> None:
    samples = np.random.default_rng(4).standard_normal((16, 250, 3))

    assert np.all(effective_sample_size(samples) > 0.8 * 4000)
    assert np.all(effective_sample_size(samples) <= 4000)


@pytest.mark.parametrize("rho", [0.5, 0.9])
def test_ess_recupera_o_valor_teorico(rho: float) -> None:
    samples = ar1(rho, (16, 2000, 1), seed=5)
    expected = 32_000 * (1 - rho) / (1 + rho)

    assert effective_sample_size(samples)[0] == pytest.approx(expected, rel=0.2)


def test_ess_de_cadeias_paradas_fica_abaixo_do_numero_de_cadeias() -> None:
    assert effective_sample_size(np.zeros((16, 250, 1)))[0] < 16


@pytest.mark.parametrize(
    ("accept", "rhat", "ess", "expected"),
    [
        (0.30, 1.01, 500.0, True),
        (0.15, 1.01, 500.0, True),
        (0.50, 1.01, 500.0, True),
        (0.14, 1.01, 500.0, False),
        (0.51, 1.01, 500.0, False),
        (0.30, 1.05, 500.0, False),
        (0.30, 1.01, 400.0, False),
    ],
)
def test_criterio_da_secao_5_5(accept: float, rhat: float, ess: float, expected: bool) -> None:
    assert is_ok(accept, rhat, ess) is expected
