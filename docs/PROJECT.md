# PROJECT.md — Conway's Game of Life

Project-specific technical guidance for the Life codebase.

## Quick Start

```bash
uv sync
uv run python -m life
uv run python -m life --size 100 --seed noise --engine pad_slice --frontend pygame
uv run python tests/test_timeit.py   # benchmark table
./scripts/run.sh --size 100 --seed noise
```

## Project Overview

A NumPy-oriented implementation of [Conway's Game of Life](https://conwaylife.com/)
with six interchangeable computation engines and two visualization frontends. The
codebase follows Domain-Driven Design with clean architectural layers.

## Architecture

### Layer Structure

```
domain          — types, protocols, Game of Life rules (no I/O)
engines         — six GridUpdater strategies (bitpack, convolution, loop,
                  pad_slice, ix_index, roll)
infrastructure  — RlePatternRepository: lazy .rle file loader
seeds           — initial state generators (noise, symmetric, scattered, pattern)
simulation      — LifeSimulation: main iterator, depends only on protocols
validation      — validate_args(), exception hierarchy
presentation    — MatplotlibAnimator, PygameVisualizer
```

**Dependency rule:** `domain` is the innermost layer — nothing inside it may import
from any other layer.

### Core Components

1. **`LifeSimulation`** (`src/life/simulation/life_simulation.py`):
   - Main iterator; implements `__iter__` / `__next__`
   - Constructor: `__init__(size, seed, engine, repository)`
   - `state: Grid` — current NDArray[int8] grid
   - Depends only on `domain` protocols (`GridUpdater`, `PatternRepository`)

2. **Engine functions** (`src/life/engines/`):
   - Six pluggable `GridUpdater` implementations, all using toroidal wrap
   - Selected via `--engine` at the CLI
   - `ENGINE_REGISTRY: dict[str, GridUpdater]` in `engines/__init__.py`
   - Performance ranking (100×100, 1 000 generations):

   | Engine | Technique | Mean (s) |
   |---|---|---|
   | pad_slice | `np.pad` + 8 slice sums | 0.1279 |
   | roll | `np.roll` via `itertools.product` | 0.3997 |
   | ix_index | `np.ix_` advanced indexing | 0.5883 |
   | bitpack | `np.packbits` + CSA neighbor sum | 0.5155 |
   | convolution | `scipy.signal.convolve2d` | 0.6158 |
   | loop | pure Python double loop | 37.9015 |

3. **Presentation** (`src/life/presentation/`):
   - `PygameVisualizer` — interactive pygame frontend (default)
   - `MatplotlibAnimator` — matplotlib FuncAnimation
   - Both depend on the `Simulation` protocol, not on `LifeSimulation` directly

4. **Seed generators** (`src/life/seeds/`):
   - `new_seed_generator(size, seed, repository) -> Grid` factory
   - `NoiseGenerator`: random binary grid
   - `SymmetricGenerator`: tiled symmetric patterns
   - `ScatteredGenerator`: multiple randomly-placed patterns OR-ed together
   - `PatternSeedGenerator`: named patterns from `RlePatternRepository`
   - `place_pattern(grid, pattern, row, col)`: shared placement helper

5. **Domain types** (`src/life/domain/`):
   - `Grid = NDArray[int8]`
   - `GridUpdater = Callable[[Grid], Grid]`
   - `PatternRepository`, `Simulation` protocols
   - `apply_rules(neighbors, state) -> Grid` — single source of GoL truth

### Execution Flow

```
__main__.py (argparse)
    ↓
RlePatternRepository()  — lazy-load .rle patterns
ENGINE_REGISTRY[args.engine]
    ↓
LifeSimulation(size, seed, engine, repository)
    ├─ validate_args()       — size ∈ [10, 1000], seed valid
    └─ new_seed_generator()  — builds initial Grid
    ↓
PygameVisualizer(sim)()   or   MatplotlibAnimator(sim)()
```

## Key Design Decisions

- **Protocol-based coupling:** all cross-layer dependencies use `typing.Protocol`;
  no layer imports a concrete class from another layer.
- **Pluggable engines:** `ENGINE_REGISTRY` maps names to functions; the CLI and tests
  both use it as the single source of engine truth.
- **Lazy pattern loading:** `RlePatternRepository` loads `.rle` files only on first
  access, keeping import time fast.
- **Validation at the boundary:** `validate_args()` runs in `LifeSimulation.__init__`;
  internal code trusts its invariants.
- **Iterator pattern:** `LifeSimulation` is an iterator; both frontends consume it the
  same way — one `next()` per frame.

## Testing & Benchmarking

| File | Purpose |
|---|---|
| `tests/test_life.py` | `LifeSimulation` — init, iterator, state progression, all engines/seeds |
| `tests/test_engine_equivalence.py` | bitwise identity across all 6 engines |
| `tests/test_pattern_repository.py` | `RlePatternRepository` — load, list, lazy-load, errors |
| `tests/test_timeit.py` | benchmark suite (dual-mode: pytest + standalone) |

Run all tests: `uv run pytest tests/ -v`
Run benchmarks: `uv run python tests/test_timeit.py`

## Dependencies

- **numpy**: grid state and array operations
- **scipy**: `convolve2d` for the convolution engine
- **matplotlib**: `MatplotlibAnimator` frontend
- **pygame**: `PygameVisualizer` frontend (interactive)
- **python-dotenv**: `.env` file loading at import time

## Important Notes

- **Toroidal wrap is mandatory** — all engines must wrap at boundaries. The equivalence
  test suite enforces this.
- **Benchmarks are machine-specific** — re-run `uv run python tests/test_timeit.py`
  after any engine change.
