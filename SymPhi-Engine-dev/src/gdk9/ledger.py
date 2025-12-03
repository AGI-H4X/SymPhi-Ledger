"""On-disk ledger for symmetry-preserving transformation sequences.

Each record is a JSON line encoding:
- input word and per-step outputs
- strategies applied in order
- per-step and overall conservation deltas
- a final integrity signature.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    # Imported only for type checking to avoid runtime circular imports.
    from .engine import ConservationReport, SymmetryReading


@dataclass  # type: ignore[misc]  # Forward refs resolved at runtime
class LedgerStep:  # pragma: no cover - simple data container
    """Single transformation step."""

    index: int
    strategy: str
    before: "SymmetryReading"
    after: "SymmetryReading"
    conservation: "ConservationReport"


@dataclass  # type: ignore[misc]
class LedgerEntry:  # pragma: no cover - serialisation exercised via tests
    """Multi-step transformation run for auditing."""

    word: str
    created_at: float
    steps: List[LedgerStep] = field(default_factory=list)
    final_signature: str | None = None

    def to_json(self) -> str:
        """Serialise to a JSON string suitable for line-oriented logs."""
        serialisable = {
            "word": self.word,
            "created_at": self.created_at,
            "steps": [
                {
                    "index": step.index,
                    "strategy": step.strategy,
                    "before": {
                        "word": step.before.word,
                        "energy": step.before.energy,
                        "classes": step.before.classes,
                        "symmetry_counts": step.before.symmetry_counts,
                        "vector_sum": step.before.vector_sum.tolist(),
                    },
                    "after": {
                        "word": step.after.word,
                        "energy": step.after.energy,
                        "classes": step.after.classes,
                        "symmetry_counts": step.after.symmetry_counts,
                        "vector_sum": step.after.vector_sum.tolist(),
                    },
                    "conservation": asdict(step.conservation),
                }
                for step in self.steps
            ],
            "final_signature": self.final_signature,
        }
        return json.dumps(serialisable)


class JsonLineLedger:
    """Append-only JSONL log for transformation runs."""

    def __init__(self, path: str = "symphi_ledger.jsonl"):
        self.path = path

    def append(self, entry: LedgerEntry) -> None:
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(entry.to_json())
            f.write("\n")


def new_entry(word: str) -> LedgerEntry:
    return LedgerEntry(word=word, created_at=time.time())



