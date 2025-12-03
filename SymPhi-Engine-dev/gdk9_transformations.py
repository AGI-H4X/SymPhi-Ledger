"""Deterministic transformation primitives that preserve symbol energies."""

from typing import Callable, Dict

from gdk9_framework import classify_word


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


TRANSFORMATIONS: Dict[str, Callable[[str], str]] = {
    'mirror': mirror,
    'pairwise_rotate': pairwise_rotate,
    'interleave': interleave,
    'symmetry_stabilize': symmetry_stabilize,
}


def get_transformation(name: str) -> Callable[[str], str]:
    if name not in TRANSFORMATIONS:
        raise KeyError(f"Unknown transformation '{name}'")
    return TRANSFORMATIONS[name]


def available_transformations():
    return tuple(TRANSFORMATIONS.keys())

