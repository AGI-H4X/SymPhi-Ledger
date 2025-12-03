import argparse
import json
from pathlib import Path

from .engine import ImplicationEngine
from .ledger import JsonLineLedger


def _serialize_vector(vector):
    return [float(f"{value:.6f}") for value in vector.tolist()]


def main():
    parser = argparse.ArgumentParser(
        description="SymPhi-Engine: symmetry-aware transformation kernel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  gdk9 SYMPHI\n"
            "  gdk9 SYMPHI --strategy mirror\n"
            "  gdk9 SYMPHI --sequence mirror,interleave,symmetry_stabilize\n"
            "  gdk9 --list-strategies\n"
        ),
    )

    default_ledger_path = Path("symphi_ledger.jsonl")

    parser.add_argument("word", nargs="?", help="Word to analyse/transform.")
    parser.add_argument(
        "--strategy",
        help="Apply a single stable transformation strategy.",
    )
    parser.add_argument(
        "--sequence",
        help=(
            "Comma-separated list of strategies to apply sequentially "
            "(e.g. mirror,interleave,symmetry_stabilize)."
        ),
    )
    parser.add_argument(
        "--list-strategies",
        action="store_true",
        help="List available transformation strategies and exit.",
    )
    parser.add_argument(
        "--ledger-path",
        default=str(default_ledger_path),
        help=f"Path to JSONL ledger file (default: {default_ledger_path}).",
    )

    args = parser.parse_args()

    engine = ImplicationEngine(ledger=JsonLineLedger(args.ledger_path))

    if args.list_strategies:
        print(json.dumps({"strategies": engine.available_strategies()}, indent=2))
        return

    if not args.word:
        parser.print_help()
        return

    reading = engine.read(args.word)
    payload = {
        "word": reading.word,
        "energy": round(reading.energy, 6),
        "classes": reading.classes,
        "symmetry_counts": reading.symmetry_counts,
        "vector_sum": _serialize_vector(reading.vector_sum),
    }

    if args.sequence:
        strategy_names = [s.strip() for s in args.sequence.split(",") if s.strip()]
        entry = engine.transform_sequence(args.word, strategy_names, log=True)
        payload["sequence"] = {
            "strategies": strategy_names,
            "steps": [
                {
                    "index": step.index,
                    "strategy": step.strategy,
                    "before_energy": round(step.before.energy, 6),
                    "after_energy": round(step.after.energy, 6),
                    "delta": round(step.conservation.delta, 6),
                    "conserved": step.conservation.conserved,
                }
                for step in entry.steps
            ],
            "final_signature": entry.final_signature,
            "ledger_path": args.ledger_path,
        }
    elif args.strategy:
        result = engine.transform(args.word, args.strategy)
        payload["transformation"] = {
            "strategy": args.strategy,
            "transformed_word": result.transformed_word,
            "conservation": {
                "initial_energy": round(result.conservation.initial_energy, 6),
                "transformed_energy": round(result.conservation.transformed_energy, 6),
                "delta": round(result.conservation.delta, 6),
                "conserved": result.conservation.conserved,
                "signature": result.conservation.signature,
            },
        }

    print(json.dumps(payload, indent=2))

