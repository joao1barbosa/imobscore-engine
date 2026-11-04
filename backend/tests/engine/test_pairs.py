"""Testes dos pares aleatórios, do BALD e da semente por sessão (seção 5.7)."""

from collections import Counter
from hashlib import sha256
from uuid import UUID

import numpy as np
import pytest

from app.engine import next_pair_bald, random_pairs, seed_for
from app.engine.pairs import bald_scores


def test_no_repeated_pair_and_at_most_three_appearances() -> None:
    pairs = random_pairs(50, 40, np.random.default_rng(0))
    unordered = {frozenset(pair) for pair in pairs}
    appearances = Counter(item for pair in pairs for item in pair)

    assert len(pairs) == 40
    assert len(unordered) == 40
    assert max(appearances.values()) <= 3
    assert all(0 <= item < 50 for pair in pairs for item in pair)
    assert all(left != right for left, right in pairs)


def test_collection_size_with_the_smallest_candidate_set() -> None:
    pairs = random_pairs(20, 25, np.random.default_rng(3))

    assert len({frozenset(pair) for pair in pairs}) == 25
    assert max(Counter(item for pair in pairs for item in pair).values()) <= 3


def test_same_seed_same_list() -> None:
    first = random_pairs(50, 40, np.random.default_rng(7))
    second = random_pairs(50, 40, np.random.default_rng(7))

    assert first == second
    assert first != random_pairs(50, 40, np.random.default_rng(8))


def test_left_side_has_no_position_bias() -> None:
    pairs = random_pairs(2000, 2000, np.random.default_rng(11))

    share = sum(left < right for left, right in pairs) / len(pairs)

    assert 0.45 <= share <= 0.55


@pytest.mark.parametrize(
    ("n_items", "n_pairs", "max_appearances"),
    [(4, 7, 3), (10, 16, 3), (1, 1, 3), (0, 1, 3)],
)
def test_impossible_requests_raise(n_items: int, n_pairs: int, max_appearances: int) -> None:
    with pytest.raises(ValueError):
        random_pairs(n_items, n_pairs, np.random.default_rng(0), max_appearances)


@pytest.mark.parametrize(("n_items", "n_pairs"), [(4, 6), (10, 15), (5, 5)])
def test_tight_but_possible_requests_succeed(n_items: int, n_pairs: int) -> None:
    max_appearances = 3 if n_items != 5 else 2

    pairs = random_pairs(n_items, n_pairs, np.random.default_rng(1), max_appearances)

    assert len({frozenset(pair) for pair in pairs}) == n_pairs
    assert max(Counter(item for pair in pairs for item in pair).values()) <= max_appearances


def test_zero_pairs_is_an_empty_list() -> None:
    assert random_pairs(5, 0, np.random.default_rng(0)) == []


def test_seed_for_follows_the_interface() -> None:
    session = UUID("12345678-1234-5678-1234-567812345678")

    assert seed_for(session, 0) == seed_for(str(session), 0)
    assert seed_for(session, 0) != seed_for(session, 1)
    assert 0 <= seed_for(session, 0) < 2**64
    assert seed_for("abc", 0) == int.from_bytes(sha256(b"abc:0").digest()[:8], "big")


# BALD


N_FEATURES = 12


def test_bald_nunca_e_negativo_em_nenhum_par() -> None:
    rng = np.random.default_rng(1)
    D = rng.normal(0.0, 3.0, (500, N_FEATURES))
    samples = rng.normal(0.0, 2.0, (800, N_FEATURES))

    assert np.all(bald_scores(D, samples) >= 0.0)


def test_bald_com_amostras_quase_iguais_fica_perto_de_zero() -> None:
    rng = np.random.default_rng(2)
    w = rng.normal(0.0, 1.0, N_FEATURES)
    samples = w + 1e-6 * rng.standard_normal((800, N_FEATURES))
    D = rng.standard_normal((300, N_FEATURES))

    assert bald_scores(D, samples).max() < 1e-6


def test_bald_prefere_o_par_em_que_as_amostras_discordam() -> None:
    # Só o peso 0 é incerto. O par 0 mexe nesse peso; o par 1, em outro, de peso fixo em 0.
    samples = np.zeros((1000, N_FEATURES))
    samples[:, 0] = np.random.default_rng(3).normal(0.0, 2.0, 1000)
    D = np.zeros((2, N_FEATURES))
    D[0, 0] = 1.0
    D[1, 1] = 1.0

    scores = bald_scores(D, samples)

    # O par 1 dá p = 0,5 em toda amostra: dúvida total, mas nada a aprender.
    assert scores[1] == pytest.approx(0.0, abs=1e-12)
    assert scores[0] > 0.05


def test_bald_bate_com_a_conta_a_mao() -> None:
    # p_s = 0,9 e 0,1: H(0,5) = 0,6931; H(0,9) = H(0,1) = 0,3251; BALD = 0,3681.
    logit = float(np.log(9.0))
    samples = np.zeros((2, N_FEATURES))
    samples[:, 0] = [logit, -logit]
    D = np.zeros((1, N_FEATURES))
    D[0, 0] = 1.0

    assert bald_scores(D, samples)[0] == pytest.approx(0.3681, abs=1e-4)


def test_next_pair_bald_nunca_repete_um_par_mostrado() -> None:
    rng = np.random.default_rng(4)
    Z = rng.standard_normal((6, N_FEATURES))
    samples = rng.normal(0.0, 1.0, (200, N_FEATURES))
    shown: set[frozenset[int]] = set()

    # Com 6 imóveis há 15 pares possíveis: todos saem, cada um uma vez.
    for _ in range(15):
        left, right = next_pair_bald(Z, samples, shown, rng)
        assert left != right
        assert frozenset((left, right)) not in shown
        shown.add(frozenset((left, right)))

    assert len(shown) == 15
    with pytest.raises(ValueError):
        next_pair_bald(Z, samples, shown, rng)


def test_next_pair_bald_escolhe_o_melhor_entre_os_sorteados() -> None:
    rng = np.random.default_rng(5)
    Z = rng.standard_normal((10, N_FEATURES))
    samples = rng.normal(0.0, 1.0, (500, N_FEATURES))

    # k maior que os 45 pares possíveis: todos entram, e sai o de maior BALD.
    left, right = next_pair_bald(Z, samples, set(), rng)

    first, second = np.triu_indices(10, k=1)
    scores = bald_scores(Z[first] - Z[second], samples)
    best = int(np.argmax(scores))
    assert {left, right} == {int(first[best]), int(second[best])}


def test_next_pair_bald_sorteia_o_lado() -> None:
    rng = np.random.default_rng(6)
    Z = rng.standard_normal((5, N_FEATURES))
    samples = rng.normal(0.0, 1.0, (100, N_FEATURES))

    pairs = [next_pair_bald(Z, samples, set(), rng) for _ in range(200)]

    first_lower = sum(left < right for left, right in pairs)
    assert 60 < first_lower < 140


def test_next_pair_bald_usa_a_semente() -> None:
    rng = np.random.default_rng(7)
    Z = rng.standard_normal((300, N_FEATURES))
    samples = rng.normal(0.0, 1.0, (400, N_FEATURES))

    first = next_pair_bald(Z, samples, set(), np.random.default_rng(1))
    second = next_pair_bald(Z, samples, set(), np.random.default_rng(1))

    assert first == second
