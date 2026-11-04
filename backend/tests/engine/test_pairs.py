"""Testes dos pares aleatórios da coleta e da semente por sessão (seção 5.7)."""

from collections import Counter
from hashlib import sha256
from uuid import UUID

import numpy as np
import pytest

from app.engine import random_pairs, seed_for


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
