"""Escolha de pares (seção 5.7): aleatórios na coleta, por informação (BALD) na demo."""

from hashlib import sha256
from uuid import UUID

import numpy as np

from app.engine.model import sigmoid

_TRIES_PER_PAIR = 50
_MAX_RESTARTS = 100


def seed_for(session_id: UUID | str, n: int) -> int:
    """Deriva a semente de uma sessão e do número de pares respondidos."""
    return int.from_bytes(sha256(f"{session_id}:{n}".encode()).digest()[:8], "big")


def _draw_new_pair(
    available: list[int], used: set[frozenset[int]], rng: np.random.Generator
) -> tuple[int, int] | None:
    """Sorteia um par ainda não usado entre os índices disponíveis, ou None se não houver."""
    size = len(available)
    if size < 2:
        return None
    for _ in range(_TRIES_PER_PAIR):
        first, second = (int(k) for k in rng.integers(size, size=2))
        if first != second and frozenset((available[first], available[second])) not in used:
            return available[first], available[second]
    remaining = [
        (a, b)
        for pos, a in enumerate(available)
        for b in available[pos + 1 :]
        if frozenset((a, b)) not in used
    ]
    if not remaining:
        return None
    return remaining[int(rng.integers(len(remaining)))]


def _attempt(
    n_items: int, n_pairs: int, rng: np.random.Generator, max_appearances: int
) -> list[tuple[int, int]] | None:
    """Tenta montar a lista inteira. Devolve None se o sorteio ficar sem saída."""
    available = list(range(n_items))
    appearances = [0] * n_items
    used: set[frozenset[int]] = set()
    pairs: list[tuple[int, int]] = []
    for _ in range(n_pairs):
        pair = _draw_new_pair(available, used, rng)
        if pair is None:
            return None
        used.add(frozenset(pair))
        for item in pair:
            appearances[item] += 1
            if appearances[item] == max_appearances:
                available.remove(item)
        # O lado é sorteado à parte, para não haver viés de posição.
        pairs.append(pair if rng.random() < 0.5 else (pair[1], pair[0]))
    return pairs


def random_pairs(
    n_items: int, n_pairs: int, rng: np.random.Generator, max_appearances: int = 3
) -> list[tuple[int, int]]:
    """Devolve (esquerda, direita) em 0..n_items-1, sem repetir par.

    Cada índice aparece no máximo `max_appearances` vezes. Levanta ValueError se for impossível.
    """
    limit = min(n_items * (n_items - 1) // 2, n_items * max_appearances // 2)
    if n_pairs > limit or n_pairs < 0:
        raise ValueError(
            f"Impossível sortear {n_pairs} pares com {n_items} itens "
            f"e até {max_appearances} aparições."
        )
    for _ in range(_MAX_RESTARTS):
        pairs = _attempt(n_items, n_pairs, rng, max_appearances)
        if pairs is not None:
            return pairs
    raise ValueError(
        f"Não foi possível sortear {n_pairs} pares com {n_items} itens "
        f"e até {max_appearances} aparições."
    )


def _entropy(p: np.ndarray) -> np.ndarray:
    """Entropia de uma escolha com probabilidade p, em nats. No limite, 0 log 0 = 0."""
    clipped = np.clip(p, 1e-12, 1.0 - 1e-12)
    entropy: np.ndarray = -clipped * np.log(clipped) - (1.0 - clipped) * np.log1p(-clipped)
    return entropy


def bald_scores(D: np.ndarray, samples: np.ndarray) -> np.ndarray:
    """D (k, 12), samples (S, 12) -> (k,). Quanto a resposta de cada par ensina sobre os pesos.

    É a incerteza total menos a incerteza que sobraria mesmo conhecendo os pesos. Sobra
    mais onde as amostras discordam entre si, e não onde cada uma só está em dúvida.
    """
    p_s = sigmoid(D @ samples.T)  # (k, S)
    scores: np.ndarray = _entropy(p_s.mean(axis=1)) - _entropy(p_s).mean(axis=1)
    # Pela desigualdade de Jensen, nunca é negativo; o piso só retira erro de arredondamento.
    floored: np.ndarray = np.maximum(scores, 0.0)
    return floored


def next_pair_bald(
    Z: np.ndarray,
    samples: np.ndarray,
    shown: set[frozenset[int]],
    rng: np.random.Generator,
    k: int = 300,
) -> tuple[int, int]:
    """Sorteia até k pares não mostrados e devolve (esquerda, direita) do mais informativo."""
    n_items = Z.shape[0]
    first, second = np.triu_indices(n_items, k=1)

    if shown:
        shown_codes = [min(pair) * n_items + max(pair) for pair in shown]
        keep = np.isin(first * n_items + second, shown_codes, invert=True)
        first, second = first[keep], second[keep]
    if first.size == 0:
        raise ValueError("Não há par que ainda não tenha sido mostrado.")

    drawn = rng.choice(first.size, size=min(k, first.size), replace=False)
    first, second = first[drawn], second[drawn]
    best = int(np.argmax(bald_scores(Z[first] - Z[second], samples)))

    # O lado é sorteado para não haver viés de posição.
    left, right = int(first[best]), int(second[best])
    return (left, right) if rng.random() < 0.5 else (right, left)
