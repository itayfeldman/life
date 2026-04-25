# Plan: Create CLAUDE.md and remove the deprecated SDLC pipeline

## Context

This repository is Itay Feldman's NumPy-oriented Conway's Game of Life implementation, whose distinguishing feature is a set of six pluggable next-state engines (`convolution`, `loop`, `window`, `fast`, `ultra_fast`, `vectorized`) that must all produce bitwise-identical outputs and are benchmarked against each other. There is no `CLAUDE.md` today.

The repo also currently contains an SDLC/Experiment-Architect pipeline (`sdlc_trigger/`, `experiment_briefs/`, `.github/workflows/sdlc_trigger.yml`) that scanned `#TODO:` comments and called the Anthropic API to auto-generate experiment briefs. **The user has declared this process deprecated.** We will delete every artifact related to it and ensure the new `CLAUDE.md` does not mention it.

## Approach

Two coordinated changes in a single task:

1. **Delete** all SDLC pipeline artifacts (directories, generated briefs, workflow file).
2. **Create** `/home/itayfeldman/Code/Projects/life/CLAUDE.md` describing only the surviving codebase.

## Files & directories to delete

Verified by `ls` and a repo-wide grep for `sdlc|experiment.brief|experiment.architect`:

| Path | What it is |
|---|---|
| `/home/itayfeldman/Code/Projects/life/sdlc_trigger/` (entire dir) | `run.py`, `experiment_architect.py`, `todo_scanner.py` (mode `0600`) |
| `/home/itayfeldman/Code/Projects/life/experiment_briefs/` (entire dir) | Two auto-generated briefs (`20260304T215629_*.md`, `20260304T215657_*.md`) |
| `/home/itayfeldman/Code/Projects/life/.github/workflows/sdlc_trigger.yml` | The GitHub Actions workflow that drove the pipeline |

**Removal command** (single `rm -rf` of three paths):

```bash
rm -rf \
  /home/itayfeldman/Code/Projects/life/sdlc_trigger \
  /home/itayfeldman/Code/Projects/life/experiment_briefs \
  /home/itayfeldman/Code/Projects/life/.github/workflows/sdlc_trigger.yml
```

After deletion, `.github/workflows/` will be empty; that's fine — leave the directory in place (no other workflows reference it, and an empty workflows dir is valid).

**No other references** exist to scrub: `.gitignore` is clean, `pyproject.toml` is clean, `tasks/` is clean, `README.md`/`PROJECT.md` are clean. A repo-wide grep confirmed all hits live inside the three paths above.

## File to create

`/home/itayfeldman/Code/Projects/life/CLAUDE.md`

## CLAUDE.md outline

1. **Required prefix** — exactly the two boilerplate lines from the prompt.
2. **Project** — one paragraph: Conway's Game of Life with six interchangeable engines benchmarked against each other; matplotlib visualization. Point at `README.md` and `PROJECT.md` for deep dives.
3. **Commands**
   - Install: `uv sync` (preferred — `uv.lock` is checked in) or `pip install -e .`
   - Run: `python -m life [--size N --seed noise|symmetric|<pattern> --interval MS --cmap NAME --figsize N --func convolution|loop|window|fast|ultra_fast|vectorized]`
   - Run via wrapper: `./scripts/run.sh ...` (assumes `~/.virtualenvs/life`)
   - Debug: `./scripts/debug.sh ...` (debugpy on `localhost:5678`)
   - Tests: `pytest tests/ -v`
   - Single test file: `pytest tests/test_life.py -v`
   - Single test: `pytest tests/test_life.py::TestLifeInitialization::test_init_with_noise_seed`
   - Benchmarks (pytest): `pytest tests/test_timeit.py -v`
   - Benchmarks (standalone, prints table): `python tests/test_timeit.py`
   - Type-check (ad-hoc, no project config): `mypy src/`
   - **Note**: no linter/formatter is configured; the `life` console script declared in `pyproject.toml` is **broken** (`__main__.py` has no `main()` — use `python -m life`).
4. **Architecture (big picture)**
   - Data flow: `__main__` → `ENGINES[args.func]` → `Life(size, seed, func)` (validates via `exceptions.validate_args`, builds initial state via `seeds.new_seed_generator`) → `Animator` → `matplotlib.FuncAnimation` pulls frames from the `Life` iterator.
   - Module roles in `src/life/`: `life.py` (iterator), `engine.py` (six strategies + shared `_apply_rules`, all toroidal-wrap), `animator.py` (matplotlib wrapper), `seeds.py`/`tiles.py` (initial-state generators including symmetric tilings), `pattern_factory.py` (loads `.cells` files from `src/life/patterns/{Guns,Metuselah,Orphans,Oscillators,Spaceships}/` at import time into a `patterns` dict), `exceptions.py` (size 10–1000, valid seed names), `__init__.py` (loads `.env` and configures `logging.conf` eagerly).
   - Key invariant: **all six engines must produce bitwise-identical output**, enforced by `tests/test_engine_equivalence.py`. Toroidal wrap boundary is mandatory.
5. **Testing notes**
   - No `conftest.py`; fixtures are duplicated per file. No coverage/hypothesis config.
   - `tests/test_life.py` parametrizes heavily over `ALL_ENGINES`, valid seeds, and grid sizes; `tests/test_timeit.py` is a dual-mode benchmark (pytest + `__main__`).
   - The `symmetric` seed fails for sizes whose half lacks suitable tile divisors; `test_life.py` skips that case — match this if you add new engine/seed parametrizations.
6. **Gotchas**
   - `src/life/__init__.py` loads `.env` and `logging.conf` at import time; `DEBUG=true` in `.env` switches the file handler to DEBUG.
   - `pattern_factory.py` `rglob`s `*.cells` at import; a malformed file logs an error but does not raise.
   - The `life = "life.__main__:main"` console script in `pyproject.toml` does not work — always use `python -m life`.
7. **User coding rules (from `~/.claude/rules/`)** — pointer note: TDD for any logic/bug-fix (Prove-It pattern for bugs), SOLID, DDD where applicable, ≤80-char lines, PEP 8, comments explain *why* not *what*, and one-question-at-a-time with numbered options when asking the user.

Explicitly **omitted**: any mention of SDLC, experiment briefs, the Experiment-Architect agent, or the `sdlc_trigger.yml` workflow.

## Execution order

1. `rm -rf` the three SDLC paths.
2. Verify removal: `ls .github/workflows/` (empty), `ls | grep -E "sdlc|experiment"` at repo root (empty).
3. Repo-wide sanity grep: `grep -rn -iE "sdlc|experiment.brief|experiment.architect" --exclude-dir={.git,.venv,.mypy_cache,.claude}` should return nothing.
4. Write `CLAUDE.md`.

## Verification

1. `cat CLAUDE.md` — confirm prefix is exact and content renders cleanly.
2. `ls /home/itayfeldman/Code/Projects/life/` — `sdlc_trigger/` and `experiment_briefs/` are gone.
3. `ls /home/itayfeldman/Code/Projects/life/.github/workflows/` — empty (or removed if user prefers).
4. `grep -rn -iE "sdlc|experiment.brief|experiment.architect" /home/itayfeldman/Code/Projects/life/ --exclude-dir={.git,.venv,.mypy_cache,.claude}` — zero hits.
5. Smoke-test that the app still runs: `python -m life --size 50 --func fast --seed noise` (the SDLC pipeline was orthogonal — nothing in `src/life/` imports from `sdlc_trigger/`).
6. `pytest tests/ -v` passes (no test references the deleted code).
