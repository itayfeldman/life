# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in
this repository.

## Project

Conway's Game of Life implemented in Python with six interchangeable next-state
computation engines (`convolution`, `loop`, `window`, `fast`, `ultra_fast`,
`vectorized`) and two visualization frontends (`pygame`, `matplotlib`). See `README.md`
for usage and benchmark results; `PROJECT.md` for architecture and design decisions.

## Commands

**Install:**
```bash
uv sync           # preferred — uv.lock is checked in
pip install -e .  # alternative
```

**Run:**
```bash
python -m life [--size N] [--seed noise|symmetric|<pattern>] \
               [--interval MS] [--frontend pygame|matplotlib] \
               [--engine convolution|loop|window|fast|ultra_fast|vectorized] \
               [--display-size N] [--cmap NAME]

# --func is accepted as an alias for --engine (backwards compatibility)

./scripts/run.sh --size 100 --seed noise  # wrapper (assumes ~/.virtualenvs/life)
./scripts/debug.sh ...                    # debugpy on localhost:5678
```

**Test:**
```bash
uv run pytest tests/ -v
uv run pytest tests/test_life.py -v
uv run pytest tests/test_life.py::TestLifeInitialization::test_init_with_noise_seed
uv run pytest tests/test_timeit.py -v    # benchmark suite (pytest mode)
uv run python tests/test_timeit.py       # benchmark suite (prints formatted table)
```

**Type-check:**
```bash
uv run --with mypy mypy src/
```

## Architecture

```
src/life/
├── __init__.py          # loads .env + logging.conf at import; exposes logger
├── __main__.py          # argparse CLI; assembles and runs the simulation
├── domain/              # types, protocols, Game of Life rules — no I/O
│   ├── types.py         # Grid, CellState, GridUpdater, GridIterator, BUILT_IN_SEEDS
│   ├── protocols.py     # PatternRepository, Simulation, Visualizer, GridUpdater
│   └── rules.py         # apply_rules() — single source of Game of Life truth
├── engines/             # six interchangeable GridUpdater strategies
│   └── __init__.py      # ENGINE_REGISTRY: dict[str, GridUpdater]
├── infrastructure/      # I/O: lazy-loading .cells pattern file reader
├── presentation/        # MatplotlibAnimator and PygameVisualizer
├── seeds/               # initial-state generators + new_seed_generator() factory
├── simulation/          # LifeSimulation iterator — depends only on protocols
├── validation/          # validate_args() + exception hierarchy
└── patterns/            # .cells data files (not Python)
```

**Dependency rule:** inner layers must not import from outer layers.

```
domain ← engines, simulation, seeds, validation, infrastructure, presentation
```

**Data flow:**
```
__main__.py (argparse)
  → CellsPatternRepository()           # infrastructure — lazy .cells loader
  → ENGINE_REGISTRY[args.engine]       # engines — selects one of six strategies
  → LifeSimulation(size, seed,         # simulation
                   engine, repository)
      ├─ validate_args()               # validation
      └─ new_seed_generator()          # seeds → Grid (NDArray[int8])
  → PygameVisualizer(sim, ...) ()      # presentation (default)
    or MatplotlibAnimator(sim, ...) ()
```

**Key invariant:** all six engines must produce **bitwise-identical output** for any
given input. Enforced by `tests/test_engine_equivalence.py`. Toroidal wrap is
mandatory — any engine change must preserve this.

## Testing

- No `conftest.py`; fixtures are duplicated per file.
- `tests/test_life.py` parametrizes heavily over `ALL_ENGINES`, valid seeds, and grid
  sizes.
- `tests/test_timeit.py` is dual-mode: runs as a pytest suite or standalone
  (`uv run python tests/test_timeit.py`) to print a benchmark table.
- The `symmetric` seed can fail for sizes whose half lacks suitable tile divisors.
  `test_life.py` skips those cases — match this pattern when adding new
  parametrizations.

## Gotchas

- `src/life/__init__.py` loads `.env` and `logging.conf` at import time. Setting
  `DEBUG=true` in `.env` switches the file handler to DEBUG level.
- `CellsPatternRepository` loads `.cells` files lazily on first access (not at import).
  A malformed file logs an error but does not raise.
- `mypy` is not in dev dependencies — run it via `uv run --with mypy mypy src/`.
- Always use `uv run` rather than bare `python` or `pytest`.

## Coding conventions (from `~/.claude/rules/`)

- TDD for any logic change or bug fix; use the Prove-It pattern (write a failing test
  that reproduces the bug first).
- SOLID principles, DDD where applicable.
- PEP 8, ≤80-char lines, comments explain *why* not *what*.
- When asking the user a question: one question at a time, numbered options, include a
  recommendation.
