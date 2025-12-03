import pytest

from gdk9.engine import ImplicationEngine
from gdk9.framework import word_energy
from gdk9.ledger import JsonLineLedger


@pytest.fixture()
def engine():
    return ImplicationEngine()


def test_read_returns_expected_profile(engine):
    reading = engine.read("PHI")
    assert reading.word == "PHI"
    assert reading.symmetry_counts['unknown'] == 0
    assert abs(reading.energy - word_energy("PHI")) < 1e-9
    assert len(reading.classes) == len("PHI")
    assert reading.vector_sum.shape == (4,)


@pytest.mark.parametrize("strategy", ["mirror", "pairwise_rotate", "interleave", "symmetry_stabilize"])
def test_transformations_conserve_energy(engine, strategy):
    result = engine.transform("SYMPHI", strategy=strategy)
    assert result.conservation.conserved
    assert abs(result.conservation.delta) <= engine.tolerance
    assert len(result.transformed_word) == len("SYMPHI")


def test_sequence_transformation_conserves_energy_and_logs(tmp_path):
    ledger_path = tmp_path / "log.jsonl"
    engine = ImplicationEngine(ledger=JsonLineLedger(str(ledger_path)))
    word = "SYMPHI"
    sequence = ["mirror", "interleave", "symmetry_stabilize", "cycle"]

    entry = engine.transform_sequence(word, sequence, log=True)

    # Energy conservation across full sequence
    assert entry.steps
    first = entry.steps[0]
    last = entry.steps[-1]
    assert abs(first.before.energy - last.after.energy) <= engine.tolerance
    assert all(step.conservation.conserved for step in entry.steps)

    # Ledger persistence
    assert entry.final_signature is not None
    assert ledger_path.exists()
    content = ledger_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(content) == 1

