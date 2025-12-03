# SymPhi-Engine

Physics-aware symbolic implication kernel for modular, self-improving AI. Applies conserved-energy grammar to alphabet symmetries for stable transformations in reasoning and cryptography.

## Features
- **Symmetry Classification**: Categorizes letters (A-Z/a-z) as idempotent, biphasic, involutive, or asymmetric.
- **Energy Computation**: Assigns/validates energies preserving totals (e.g., \(E(\text{FWEM}) \approx 42.04\)).
- **Vectorization**: Encodes symbols into 4D vectors for implication flows.
- **Implication Engine**: Reads words, transforms via morphisms, checks conservation.
- **Stable Transformations**: Mirror, pair-rotate, interleave, and symmetry-stabilise strings without energy drift.
- **Conservation Ledger**: Deterministic SHA-256 signatures prove whether energy remained within tolerance.

## Installation
```bash
git clone https://github.com/AGI-H4X/SymPhi-Engine.git
cd SymPhi-Engine
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Optional: tooling for tests
pip install -r requirements-dev.txt
```

## CLI Usage

Read a word profile:
```bash
python main.py SYMPHI
```

Apply a stable transformation and observe the conservation report:
```bash
python main.py SYMPHI --strategy pairwise_rotate
```

List available strategies:
```bash
python main.py --list-strategies
```

## Testing

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

