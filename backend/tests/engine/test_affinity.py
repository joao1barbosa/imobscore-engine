"""Testes da afinidade, do score e da explicação (seção 5.6)."""

import numpy as np
import pytest

from app.engine import FEATURE_KEYS, compute_affinity, explain, to_score
from app.engine.model import sigmoid

N = len(FEATURE_KEYS)


def index(key: str) -> int:
    return FEATURE_KEYS.index(key)


def vector(**values: float) -> np.ndarray:
    v = np.zeros(N)
    for key, value in values.items():
        v[index(key)] = value
    return v


def test_afinidade_fica_sempre_entre_0_e_1() -> None:
    rng = np.random.default_rng(1)
    Z = rng.normal(0.0, 30.0, (50, N))
    samples = rng.normal(0.0, 5.0, (400, N))

    result = compute_affinity(Z, samples)

    for values in (result.mean, result.p5, result.p95):
        assert values.shape == (50,)
        assert np.all((values >= 0.0) & (values <= 1.0))


def test_o_imovel_tipico_tem_afinidade_meio() -> None:
    samples = np.random.default_rng(2).normal(0.0, 3.0, (400, N))

    result = compute_affinity(np.zeros((1, N)), samples)

    assert result.mean[0] == pytest.approx(0.5)
    assert result.p5[0] == pytest.approx(0.5)
    assert result.p95[0] == pytest.approx(0.5)


def test_afinidade_e_a_media_das_sigmoides_e_nao_a_sigmoide_da_media() -> None:
    # Pesos 3 e -1 com z = 1: média das sigmoides 0,611; sigmoide da média 0,731.
    z = vector(log_area=1.0)[None, :]
    samples = np.vstack((vector(log_area=3.0), vector(log_area=-1.0)))

    affinity = compute_affinity(z, samples).mean[0]

    assert affinity == pytest.approx((sigmoid(np.array(3.0)) + sigmoid(np.array(-1.0))) / 2)
    assert affinity == pytest.approx(0.611, abs=0.001)
    assert affinity != pytest.approx(float(sigmoid(np.array(1.0))), abs=0.05)


def test_o_intervalo_contem_a_media_e_some_com_uma_amostra_so() -> None:
    rng = np.random.default_rng(3)
    Z = rng.standard_normal((20, N))

    many = compute_affinity(Z, rng.normal(0.0, 1.0, (4000, N)))
    one = compute_affinity(Z, rng.normal(0.0, 1.0, (1, N)))

    assert np.all((many.p5 <= many.mean) & (many.mean <= many.p95))
    assert np.array_equal(one.p5, one.mean)
    assert np.array_equal(one.p95, one.mean)


@pytest.mark.parametrize(
    ("affinity", "delta", "expected"),
    [
        (0.5, 0, 50),
        (0.874, 0, 87),
        (0.0, 0, 0),
        (1.0, 0, 100),
        (0.5, 10, 60),
        (0.5, -80, 0),
        (0.5, 80, 100),
        (0.0, -80, 0),
        (1.0, 80, 100),
    ],
)
def test_to_score_fica_sempre_entre_0_e_100(affinity: float, delta: int, expected: int) -> None:
    score = to_score(affinity, delta)

    assert score == expected
    assert isinstance(score, int)


def test_explain_traz_as_3_maiores_positivas_e_a_mais_negativa() -> None:
    w = vector(log_area=2.0, parking=1.0, leisure=0.5, pet=0.3, log_price=-1.0, age=-0.5)
    z = np.ones(N)

    reasons = explain(z, w)

    assert [r.feature_key for r in reasons] == ["log_area", "parking", "leisure", "log_price"]
    assert [r.contribution for r in reasons] == [2.0, 1.0, 0.5, -1.0]


def test_explain_usa_o_texto_conforme_o_sinal_de_z() -> None:
    # Morar longe do centro pesa contra; ser mais barato conta a favor pelo peso negativo.
    w = vector(log_price=-1.0, dist_center=-1.0)
    z = vector(log_price=-1.0, dist_center=1.0)

    reasons = {r.feature_key: r for r in explain(z, w)}

    assert reasons["log_price"].text == "mais barato que o típico"
    assert reasons["log_price"].contribution == 1.0
    assert reasons["dist_center"].text == "longe do centro"
    assert reasons["dist_center"].contribution == -1.0


def test_explain_ignora_contribuicoes_pequenas() -> None:
    w = vector(log_area=1.0, parking=1.0, leisure=1.0)
    z = vector(log_area=0.09, parking=-0.09, leisure=0.1)

    reasons = explain(z, w)

    assert [r.feature_key for r in reasons] == ["leisure"]


def test_explain_do_imovel_tipico_nao_tem_motivo() -> None:
    assert explain(np.zeros(N), np.ones(N)) == []


def test_explain_devolve_no_maximo_4_motivos() -> None:
    rng = np.random.default_rng(4)

    for _ in range(200):
        reasons = explain(rng.normal(0.0, 2.0, N), rng.normal(0.0, 2.0, N))
        assert len(reasons) <= 4
        assert sum(r.contribution < 0 for r in reasons) <= 1


def test_explain_sem_negativas_nao_passa_de_3_motivos() -> None:
    reasons = explain(np.ones(N), np.ones(N))

    assert len(reasons) == 3
    assert all(r.contribution > 0 for r in reasons)


def test_explain_respeita_um_limite_menor() -> None:
    w = vector(log_area=2.0, parking=1.0, leisure=0.5, log_price=-1.0)

    reasons = explain(np.ones(N), w, max_reasons=2)

    assert [r.feature_key for r in reasons] == ["log_area", "log_price"]
