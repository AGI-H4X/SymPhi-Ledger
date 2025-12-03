import math
from collections import Counter
from typing import Dict, List, Optional

import numpy as np

# Symmetry sets (from handbook)
idemp_upper = set('AHIMOTUV WXY'.replace(' ', ''))
idemp_lower = set('amotuv wxy'.replace(' ', ''))
biphasic_upper = set('BCDEK')
biphasic_lower = set('bcdek')
invol_upper = set('NSZ')
invol_lower = set('nsz')
asym_upper = set('FGJLPQR')
asym_lower = set('fgjl pqr'.replace(' ', ''))

SYMMETRY_ORDER = ('idempotent', 'biphasic', 'involutive', 'asymmetric')


def normalize_word(word: str) -> str:
    """Keep alphabetic characters only and strip whitespace noise."""
    return ''.join(ch for ch in word if ch.isalpha())


def get_symmetry_type(char: str) -> Optional[str]:
    """Return the symmetry class for a character, if defined."""
    if not char or not char.isalpha():
        return None
    upper = char.upper()
    if upper in idemp_upper:
        return 'idempotent'
    if upper in biphasic_upper:
        return 'biphasic'
    if upper in invol_upper:
        return 'involutive'
    if upper in asym_upper:
        return 'asymmetric'
    if upper in idemp_lower:
        return 'idempotent'
    if upper in biphasic_lower:
        return 'biphasic'
    if upper in invol_lower:
        return 'involutive'
    if upper in asym_lower:
        return 'asymmetric'
    return None


def energy(char: str) -> float:
    """Energy heuristic derived from symmetry classification."""
    if not char.isalpha():
        return 0.0
    upper = char.upper()
    pos = ord(upper) - ord('A') + 1
    sym = get_symmetry_type(char)
    if sym == 'idempotent':
        return float(pos)
    if sym == 'biphasic':
        return math.sin(pos)
    if sym == 'involutive':
        return 1.0 / pos
    if sym == 'asymmetric':
        return pos + 1
    return 0.0


def word_energy(word: str) -> float:
    """Aggregate the energy of a word."""
    return sum(energy(c) for c in word)


def vectorize(char: str) -> np.ndarray:
    """Projected vector representation for downstream implication math."""
    if not char.isalpha():
        return np.zeros(4)
    upper = char.upper()
    pos = ord(upper) - ord('A') + 1
    sym = get_symmetry_type(char)
    type_id = {s: i + 1 for i, s in enumerate(SYMMETRY_ORDER)}.get(sym, 0)
    e = energy(char)
    theta = pos * math.pi / 26  # Approximate angular embedding.
    return np.array([pos, type_id, math.sqrt(abs(e)), math.sin(theta)], dtype=float)


def classify_word(word: str) -> List[Optional[str]]:
    """Return the symmetry class per character."""
    return [get_symmetry_type(c) for c in word]


def symmetry_counts(word: str) -> Dict[str, int]:
    """Count how many characters fall into each symmetry class."""
    counts = Counter(classify_word(word))
    if None in counts:
        counts['unknown'] = counts.pop(None)
    ordered = {cls: counts.get(cls, 0) for cls in SYMMETRY_ORDER}
    ordered['unknown'] = counts.get('unknown', 0)
    return ordered
