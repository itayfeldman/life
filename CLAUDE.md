# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Conway's Game of Life implemented in Python with six interchangeable next-state computation engines (`convolution`, `loop`, `window`, `fast`, `ultra_fast`, `vectorized`) that are benchmarked against each other. Visualization is via matplotlib animation. See `README.md` for usage and benchmark results; `PROJECT.md` for architecture and design decisions.

## Commands

**Install:**
```bash
uv sync           # preferred — uv.lock is checked in
pip install -e .  # alternative
```

**Run:**
```bash
python -m life [--size N] [--seed noise|symmetric|<pattern>] \
               [--interval MS] [--cmap NAME] [--figsize N] \
               [--func convolution|loop|window|fast|ultra_fast|vectorized]

./scripts/run.sh --size 100 --seed noise  # wrapper (assumes ~/.virtualenvs/life)
./scripts/debug.sh ...                    # debugpy on localhost:5678
```

**Test:**
```bash
pytest tests/ -v
pytest tests/test_life.py -v
pytest tests/test_life.py::TestLifeInitialization::test_init_with_noise_seed
pytest tests/test_timeit.py -v    # benchmark suite (pytest mode)
python tests/test_timeit.py       # benchmark suite (prints formatted table)
```

**Type-check** (no project config, ad-hoc):
```bash
mypy src/
```

> No linter or formatter is configured. The `life` console script declared in `pyproject.toml` is broken (`__main__.py` has no `main()` function) — always use `python -m life`.

## Architecture

**Data flow:**
```
__main__.py (argparse)
  → ENGINES[args.func]           # selects one of six strategies
  → Life(size, seed, func)       # validates args, builds initial state
      ├─ exceptions.validate_args()
      └─ seeds.new_seed_generator() → State (NDArray[int8])
  → Animator(life, cmap, interval, figsize)
      └─ matplotlib FuncAnimation pulls frames from the Life iterator
```

**Module roles in `src/life/`:**

| Module | Role |
|---|---|
| `life.py` | `Life` iterator — `__next__` applies `func(state)` and returns the new state |
| `engine.py` | Six next-state strategies + shared `_apply_rules()`. All use toroidal wrap boundaries |
| `animator.py` | Wraps `matplotlib.FuncAnimation`; consumes the `Life` iterator |
| `seeds.py` / `tiles.py` | Initial-state generators: `noise`, `symmetric` (tile-based), named patterns |
| `pattern_factory.py` | Loads `.cells` files from `src/life/patterns/{Guns,Metuselah,Orphans,Oscillators,Spaceships}/` into a `patterns` dict **at import time** |
| `exceptions.py` | `validate_args(size, seed)` — size bounded 10–1000; seed must be `noise`, `symmetric`, or a loaded pattern name |
| `__init__.py` | Loads `.env` (via python-dotenv) and `logging.conf` **at import time**; exposes `logger` |

**Key invariant:** all six engines must produce **bitwise-identical output** for any given input. This is enforced by `tests/test_engine_equivalence.py`. Toroidal wrap is mandatory — any engine change must preserve this.

## Testing

- No `conftest.py`; fixtures are duplicated per file.
- `tests/test_life.py` parametrizes heavily over `ALL_ENGINES`, valid seeds, and grid sizes.
- `tests/test_timeit.py` is dual-mode: runs as a pytest suite or standalone (`python tests/test_timeit.py`) to print a benchmark table.
- The `symmetric` seed can fail for sizes whose half lacks suitable tile divisors. `test_life.py` skips those cases — match this pattern when adding new parametrizations.

## Gotchas

- `src/life/__init__.py` loads `.env` and `logging.conf` at import time. Setting `DEBUG=true` in `.env` switches the file handler to DEBUG level.
- `pattern_factory.py` `rglob`s `*.cells` at import; a malformed file logs an error but does not raise.
- The `life = "life.__main__:main"` console script in `pyproject.toml` is non-functional — use `python -m life`.

## Coding conventions (from `~/.claude/rules/`)

- TDD for any logic change or bug fix; use the Prove-It pattern (write a failing test that reproduces the bug first).
- SOLID principles, DDD where applicable.
- PEP 8, ≤80-char lines, comments explain *why* not *what*.
- When asking the user a question: one question at a time, numbered options, include a recommendation.
