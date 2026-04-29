# SPEC: Finalize the DDD Migration

## 1. Objective

Complete the Domain-Driven Design restructure of Conway's Game of Life. The code has
been reorganized into clean architectural layers (`domain`, `engines`, `infrastructure`,
`presentation`, `simulation`, `seeds`, `validation`) but the project documentation and
`pyproject.toml` still describe the old flat-module structure. The spec covers two tracks:

- **Track A — Verification:** confirm the restructured code is correct, fully tested,
  and the CLI entry point works end-to-end.
- **Track B — Documentation:** update `CLAUDE.md`, `README.md`, and `PROJECT.md` (if
  it exists) to accurately describe the new structure.

**Target users:** the project maintainer (Itay Feldman) and any Claude Code agent
working on this repo in the future.

---

## 2. Acceptance Criteria

### Track A — Verification

- [ ] `uv run pytest tests/ -v` passes with zero failures and zero errors.
- [ ] `uv run python -m life --help` prints usage without error.
- [ ] `uv run life --help` (console script) works without error.
- [ ] `uv run mypy src/` reports zero errors.
- [ ] Engine equivalence invariant holds: all six engines produce bitwise-identical
      output (enforced by `tests/test_engine_equivalence.py`).
- [ ] Benchmark table in `README.md` is up-to-date (re-run `python tests/test_timeit.py`
      and replace stale numbers if results differ by >10%).

### Track B — Documentation

- [ ] `CLAUDE.md` Architecture section describes the new layer structure (not the old
      flat modules).
- [ ] `CLAUDE.md` data-flow diagram reflects `LifeSimulation`, `CellsPatternRepository`,
      `MatplotlibAnimator`, and `PygameVisualizer`.
- [ ] `CLAUDE.md` Gotchas section removes stale references (`pattern_factory.py`,
      "console script is broken") and adds any new gotchas.
- [ ] `CLAUDE.md` Commands section reflects the current `--engine` / `--frontend` flags.
- [ ] `README.md` is already accurate (updated during restructure); confirm no stale
      references to old modules remain.
- [ ] `PROJECT.md` (if present) is updated or replaced to describe the new architecture.

---

## 3. Architecture (post-migration)

```
src/life/
├── __init__.py          # loads .env + logging.conf at import; exposes logger
├── __main__.py          # argparse CLI; assembles and runs the simulation
├── domain/              # types, protocols, Game of Life rules — no I/O
│   ├── types.py         # Grid, CellState, GridUpdater, GridIterator, BUILT_IN_SEEDS
│   ├── protocols.py     # PatternRepository, Simulation, Visualizer, GridUpdater
│   └── rules.py         # apply_rules() — the single source of Game of Life truth
├── engines/             # six interchangeable GridUpdater strategies
│   ├── __init__.py      # ENGINE_REGISTRY: dict[str, GridUpdater]
│   ├── convolution.py
│   ├── fast.py
│   ├── loop.py
│   ├── ultra_fast.py
│   ├── vectorized.py
│   └── window.py
├── infrastructure/      # I/O: pattern file loading
│   ├── __init__.py
│   └── cells_pattern_repository.py  # lazy-loading .cells reader
├── presentation/        # visualization frontends
│   ├── __init__.py
│   ├── matplotlib_animator.py
│   └── pygame_visualizer.py
├── seeds/               # initial-state generators
│   ├── __init__.py      # new_seed_generator() factory + BUILT_IN_SEEDS
│   ├── _placement.py    # place_pattern() shared helper
│   ├── noise.py
│   ├── pattern_seed.py
│   ├── scattered.py
│   └── symmetric.py
├── simulation/          # main iterator — depends only on domain protocols
│   ├── __init__.py
│   └── life_simulation.py
├── validation/          # input validation and exception hierarchy
│   ├── __init__.py
│   └── exceptions.py
└── patterns/            # .cells data files (not Python)
```

**Dependency rule:** inner layers must not import from outer layers.

```
domain ← engines, simulation, seeds, validation, infrastructure, presentation
```

**Data flow:**

```
__main__.py (argparse)
  → CellsPatternRepository()          # infrastructure
  → ENGINE_REGISTRY[args.engine]      # engines
  → LifeSimulation(size, seed,        # simulation
                   engine, repository)
      ├─ validate_args()              # validation
      └─ new_seed_generator()         # seeds → Grid (NDArray[int8])
  → PygameVisualizer(sim, ...) ()     # presentation
    or MatplotlibAnimator(sim, ...) ()
```

---

## 4. Code Style

Follow conventions already established in `~/.claude/rules/coding-principles.md`:

- PEP 8, lines ≤ 80 characters.
- Comments explain *why*, not *what*; prefer self-explanatory names.
- No `conftest.py`; fixtures duplicated per test file (existing pattern).
- Type annotations on all public functions and methods.
- Protocols over concrete types for cross-layer dependencies.

---

## 5. Testing Strategy

All changes must follow TDD (Red → Green → Refactor).

| Test file | Coverage |
|---|---|
| `tests/test_life.py` | `LifeSimulation` — init, iterator protocol, state progression, all engines, all seeds |
| `tests/test_engine_equivalence.py` | bitwise identity across all 6 engines |
| `tests/test_pattern_repository.py` | `CellsPatternRepository` — load, list, contains, lazy load, error cases |
| `tests/test_timeit.py` | benchmark suite (dual-mode: pytest + standalone) |

**Skipping rule:** the `symmetric` seed may fail for sizes whose `size // 2` has no
suitable tile divisors. Tests parametrized over sizes must skip those cases — follow
the existing skip pattern in `test_life.py`.

**Verification steps (Track A):**
1. `uv run pytest tests/ -v` — all green.
2. `uv run mypy src/` — zero errors.
3. `uv run python -m life --help` — no import errors.
4. `uv run life --help` — console script resolves.

---

## 6. Boundaries

### Always do
- Run `pytest tests/ -v` after every change.
- Preserve the engine equivalence invariant (toroidal wrap, bitwise-identical output).
- Keep domain layer free of I/O and infrastructure imports.
- Use `uv run` for all Python commands (no bare `python`).

### Ask first about
- Changing the public API of any domain protocol (may break callers).
- Adding new dependencies to `requirements.txt` or `pyproject.toml`.
- Renaming or moving `.cells` pattern files.
- Changing benchmark numbers in `README.md` by more than 10%.

### Never do
- Import from `presentation` or `infrastructure` inside `domain/`, `engines/`,
  `simulation/`, or `seeds/`.
- Skip or suppress failing tests instead of fixing root causes.
- Use bare `python` commands — always use `uv run python` or `uv run pytest`.
- Delete or alter `.cells` pattern files without confirming with the user.
