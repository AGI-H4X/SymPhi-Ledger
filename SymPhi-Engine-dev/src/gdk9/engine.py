from dataclasses import dataclass
import hashlib
from typing import List, Optional, Sequence, Union

import numpy as np

from .framework import classify_word, symmetry_counts, word_energy, vectorize
from .transformations import available_transformations, get_transformation
from .ledger import JsonLineLedger, LedgerEntry, LedgerStep, new_entry


@dataclass
class SymmetryReading:
    word: str
    energy: float
    classes: List[Optional[str]]
    vector_sum: np.ndarray
    symmetry_counts: dict


@dataclass
class ConservationReport:
    initial_energy: float
    transformed_energy: float
    delta: float
    conserved: bool
    signature: str


@dataclass
class TransformationResult:
    strategy: str
    transformed_word: str
    reading_before: SymmetryReading
    reading_after: SymmetryReading
    conservation: ConservationReport


class ImplicationEngine:
    def __init__(self, tolerance: float = 1e-6, ledger: Optional[JsonLineLedger] = None):
        self.tolerance = tolerance
        self.ledger = ledger

    def read(self, word: str) -> SymmetryReading:
        """Decode the word into its symmetry profile."""
        clean_word = word or ''
        vectors = [vectorize(c) for c in clean_word]
        vector_sum = np.sum(vectors, axis=0) if vectors else np.zeros(4)
        classes = classify_word(clean_word)
        counts = symmetry_counts(clean_word)
        energy_total = word_energy(clean_word)
        return SymmetryReading(
            word=clean_word,
            energy=energy_total,
            classes=classes,
            vector_sum=vector_sum,
            symmetry_counts=counts,
        )

    def validate_conservation(
        self,
        reference: Union[str, SymmetryReading],
        candidate: Optional[Union[str, SymmetryReading]] = None,
    ) -> bool:
        """Check whether energy stays within tolerance between readings."""
        before = self._ensure_reading(reference)
        after = self._ensure_reading(candidate) if candidate is not None else before
        return abs(before.energy - after.energy) <= self.tolerance

    def transform(self, word: str, strategy: str = 'mirror') -> TransformationResult:
        """Apply a stable transformation and return detailed ledger information."""
        transform_fn = get_transformation(strategy)
        reading_before = self.read(word)
        transformed_word = transform_fn(word)
        reading_after = self.read(transformed_word)
        conserved = self.validate_conservation(reading_before, reading_after)
        report = ConservationReport(
            initial_energy=reading_before.energy,
            transformed_energy=reading_after.energy,
            delta=reading_after.energy - reading_before.energy,
            conserved=conserved,
            signature=self._build_signature(reading_before, reading_after),
        )
        return TransformationResult(
            strategy=strategy,
            transformed_word=transformed_word,
            reading_before=reading_before,
            reading_after=reading_after,
            conservation=report,
        )

    def transform_sequence(
        self,
        word: str,
        strategies: Sequence[str],
        log: bool = True,
    ) -> LedgerEntry:
        """Apply a sequence of stable transforms and optionally persist to the ledger.

        This models a discrete time-evolution of the symbol configuration under
        purely permutational dynamics. Because each step is an index permutation,
        the total energy (a sum over characters) is conserved up to numerical
        tolerance, analogous to conserved Hamiltonians in classical or quantum
        systems.
        """
        entry = new_entry(word)
        current_word = word
        for idx, name in enumerate(strategies):
            step_result = self.transform(current_word, strategy=name)
            step = LedgerStep(
                index=idx,
                strategy=name,
                before=step_result.reading_before,
                after=step_result.reading_after,
                conservation=step_result.conservation,
            )
            entry.steps.append(step)
            current_word = step_result.transformed_word

        # Final signature ties whole sequence together using last conservation signature.
        if entry.steps:
            entry.final_signature = entry.steps[-1].conservation.signature

        if log and self.ledger is not None:
            self.ledger.append(entry)

        return entry

    def available_strategies(self):
        return available_transformations()

    def _ensure_reading(self, value: Union[str, SymmetryReading]) -> SymmetryReading:
        if isinstance(value, SymmetryReading):
            return value
        if isinstance(value, str):
            return self.read(value)
        raise TypeError("Value must be a string or SymmetryReading.")

    @staticmethod
    def _build_signature(before: SymmetryReading, after: SymmetryReading) -> str:
        payload = (
            f"{before.word}|{before.energy:.8f}|"
            f"{after.word}|{after.energy:.8f}|"
            f"{after.vector_sum.tolist()}"
        )
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()
