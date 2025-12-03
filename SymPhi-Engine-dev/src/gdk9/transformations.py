"""Deterministic transformation primitives that preserve symbol energies."""

from typing import Callable, Dict, Iterable, List

from .framework import classify_word


def mirror(word: str) -> str:
    """Reverse order to model involutive flips."""
    return word[::-1]


def pairwise_rotate(word: str) -> str:
    """Rotate each adjacent pair (ab -> ba) to simulate phase lag."""
    chars = list(word)
    for idx in range(0, len(chars) - 1, 2):
        chars[idx], chars[idx + 1] = chars[idx + 1], chars[idx]
    return ''.join(chars)


def interleave(word: str) -> str:
    """Split even/odd channels and interleave for stable braids."""
    even = word[::2]
    odd = word[1::2]
    return odd + even


def symmetry_stabilize(word: str) -> str:
    """Sort symbols by symmetry class then original order to minimize drift."""
    classes = classify_word(word)
    sortable = list(zip(classes, range(len(word)), word))
    sortable.sort(key=lambda item: ((item[0] or 'zz'), item[1]))
    return ''.join(ch for _, _, ch in sortable)


def cycle(word: str, k: int = 1) -> str:
    """Cyclic rotation; models periodic boundary conditions.

    Pure permutation of indices, so energy is conserved.
    """
    if not word:
        return word
    k = k % len(word)
    return word[-k:] + word[:-k]


def compose_sequence(word: str, strategies: Iterable[Callable[[str], str]]) -> str:
    """Apply a sequence of pure index permutations.

    As long as each strategy is a bijection on positions, the
    overall map preserves total energy (mathematically a permutation
    of the basis, analogous to unitary evolution without phase).
    """
    current = word
    for transform in strategies:
        current = transform(current)
    return current


TRANSFORMATIONS: Dict[str, Callable[[str], str]] = {
    'mirror': mirror,
    'pairwise_rotate': pairwise_rotate,
    'interleave': interleave,
    'symmetry_stabilize': symmetry_stabilize,
    'cycle': cycle,
}


def get_transformation(name: str) -> Callable[[str], str]:
    if name not in TRANSFORMATIONS:
        raise KeyError(f"Unknown transformation '{name}'")
    return TRANSFORMATIONS[name]


def available_transformations():
    return tuple(TRANSFORMATIONS.keys())

