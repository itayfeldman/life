# Whole-library code review — `life` (Conway's Game of Life)

## Context

The library has just landed a new `scattered` seed plus a shared `place_pattern`
helper. That change is small and clean (already approved separately). The user
now asks for a full-library review across all five axes **and** a verdict on the
architecture, patterns, and naming.

This document is the review. It is grouped by severity, then by axis. It also
includes a short list of things that are genuinely good — the library has more
right than wrong, and a review that only lists problems would mislead.

The library is small (~25 source files, ~1k LOC), single-author, well-tested
(141 passing tests), and structurally clean (DDD layering, six interchangeable
engines, two interchangeable frontends). The findings below are mostly polish
and consistency, not redesign.

---

## What's good (don't change these)

- **Layered package structure** (`domain / engines / simulation / seeds /
  validation / infrastructure / presentation`) with a clear inward-pointing
  dependency rule. Easy to read.
- **`apply_rules` in `domain/rules.py` is the single source of truth** for
  Conway's B3/S23 logic, and **all six engines call it.** Eliminates the most
  dangerous duplication.
- **Engine equivalence is enforced by tests** (`test_engine_equivalence.py`)
  against `convolution` as the reference. This is the right invariant in the
  right place.
- **`Simulation` and `PatternRepository` protocols are real abstractions** —
  both are substituted at runtime (presentation classes accept any
  `Simulation`; `LifeSimulation` accepts any `PatternRepository`).
- **`PygameVisualizer` and `MatplotlibAnimator` depend only on the
  `Simulation` protocol**, not on `LifeSimulation`. Clean boundary.
- **`__main__.py` is the only composition root** that pulls concrete
  infrastructure + presentation. Correct.
- **Test parametrization over `ALL_ENGINES`** for shape/dtype/oscillation
  invariants is the right pattern.
- **No `print()` in library code, no swallowed bare `except:` in business
  logic, no TODO/HACK markers** anywhere in `src/`.

---

## Findings — by severity

### 1. Required (real correctness or design defects)

#### 1.1 `GridUpdater` is defined twice in the domain
- `src/life/domain/types.py:6` defines `GridUpdater = Callable[[Grid], Grid]`.
- `src/life/domain/protocols.py:9` defines `GridUpdater` again as a
  `runtime_checkable` Protocol.
- The alias is what's actually imported (`engines/__init__.py`,
  `simulation/life_simulation.py`). The Protocol form is never substituted.
- **Action**: keep one. The alias is sufficient for current use; delete the
  Protocol. (Or vice-versa, but pick one and remove the other.)

#### 1.2 `BUILT_IN_SEEDS` lives in the wrong layer
- `src/life/domain/types.py:11` enumerates `{"noise", "symmetric",
  "scattered"}` — concrete strategy names owned by `seeds/`.
- `seeds/__init__.py` then re-exports it back from domain — a tell that the
  data flow is inverted.
- The dispatch in `seeds/__init__.py` does **not** derive its `if seed == ...`
  branches from `BUILT_IN_SEEDS`. The two will drift the next time someone
  adds a seed.
- **Action**: move `BUILT_IN_SEEDS` to `seeds/__init__.py` and have
  `validation/exceptions.py` import it from there. Consider deriving the
  dispatch table from a `dict[str, Callable[..., Grid]]` so the literal-string
  branches and the constant share one source of truth.

#### 1.3 `SymmetricGenerator` violates the size contract
- `src/life/seeds/symmetric.py:72-78` returns a grid of shape
  `(num_tiles*tile_size*2, num_tiles*tile_size*2)`, which generally does
  **not** equal `(size, size)`. Every other generator returns exactly
  `(size, size)`.
- For `size < 4`, `divisors` is empty and `random.choice(divisors)` raises
  `IndexError`. CLAUDE.md acknowledges this as a known footgun ("symmetric
  seed can fail for sizes whose half lacks suitable tile divisors") but the
  failure mode is a raw `IndexError`, not a typed error.
- **Action**: either crop/pad the result to `(size, size)`, or document the
  contract as "≤ size in each dimension." Replace the `IndexError` with
  `SeedValueError` or skip-on-incompatible-size at the dispatcher.

#### 1.4 `simulation/life_simulation.py` docstring is inaccurate
- The docstring claims "depends only on domain protocols," but the file
  imports `from life.seeds import new_seed_generator` and
  `from life import logger`. Both are non-domain.
- **Action**: either fix the docstring, or invert the dependency by accepting
  a `Callable[[int], Grid]` seed factory at construction time instead of
  importing the seed package directly. The factory approach also makes
  `LifeSimulation` testable without a full `PatternRepository`.

#### 1.5 `validate_args` admits `bool` as a valid `size`
- `src/life/validation/exceptions.py:37`: `isinstance(size, int)` is `True`
  for `bool`. `LifeSimulation(size=True, ...)` would slip past the type check
  and fail at the value check with the message `"Got True"`.
- **Action**: `if not isinstance(size, int) or isinstance(size, bool):`.

#### 1.6 `ScatteredGenerator` crashes on an empty repository
- `src/life/seeds/scattered.py:30`: if `self._repo.list_names()` is empty,
  `np.random.randint(0)` raises `ValueError`.
- The shipped repository has 27+ patterns so this never trips in practice,
  but it's an unguarded invariant.
- **Action**: raise a typed error (`SeedValueError` or a new
  `EmptyRepositoryError`) up front, or guard with an early return.

#### 1.7 `CellsPatternRepository` namespace collisions are silent
- Patterns are keyed by `file_path.stem`. `rglob` walks subdirectories. Two
  files with the same stem in different folders silently overwrite each
  other.
- `_ensure_loaded` sets `self._loaded = True` *before* the loop, so a
  partially-failed load is treated as complete. Subsequent `load(name)` calls
  for missing patterns get a `KeyError` with no link to the original parse
  error.
- **Action**: log a warning on stem collision; defer setting `_loaded = True`
  until the loop completes (or at least until the file iteration ends
  successfully).

### 2. Should fix (architecture / naming consistency)

#### 2.1 Engine names are a mix of "what it does" and "how it feels"
- Descriptive: `convolution`, `loop`, `window`.
- Comparative / vague: `fast`, `ultra_fast`, `vectorized`.
- "Vectorized" is misleading — every engine except `loop` is vectorized.
  "Fast" and "ultra_fast" are superlatives that age poorly.
- **Suggested rename** (preserve old names as aliases in the registry for one
  release if backwards compat matters):
  - `fast` → `pad_slice` (uses `np.pad` + 8 slice sums).
  - `ultra_fast` → `ix_index` (uses `np.ix_` advanced indexing).
  - `vectorized` → `roll` (uses 8 `np.roll`s).
- `window` and `vectorized` produce identical results by identical means
  (both sum 8 `np.roll` shifts). One of them should be deleted, or the
  distinction documented.

#### 2.2 Seed generator interfaces are not unified
- Signatures across `seeds/`:
  - `NoiseGenerator()(size)`
  - `SymmetricGenerator()(size)`
  - `PatternSeedGenerator(repo)(size, name)`
  - `ScatteredGenerator(repo)(size, count=None)`
- The dispatcher `new_seed_generator` knows each shape via a hand-written
  `if/elif` chain.
- **Action**: introduce a `SeedGenerator` protocol with a single
  `__call__(size: int) -> Grid` signature. Wrap repository-dependent
  generators with closures (e.g. `partial(PatternSeedGenerator(repo),
  name="glider")`). The dispatcher becomes a `dict[str, SeedGenerator]`
  lookup. Eliminates the if/elif chain and unifies `BUILT_IN_SEEDS` with the
  dispatch table.

#### 2.3 RNG state is global and uncoordinated
- `noise.py`, `scattered.py`, and `symmetric.py` all use `np.random.randint`
  (legacy global RNG). `symmetric.py` also uses Python's `random.choice`,
  mixing two independent global RNGs in one module.
- Reproducibility from a single seed is impossible without monkey-patching.
- **Action**: accept an optional `np.random.Generator` (and Python `Random`
  where applicable) at construction time. Default to a module-level instance
  if not provided. This also makes `test_reproducible_with_seed` cleaner.

#### 2.4 `Visualizer` protocol is dead
- `src/life/domain/protocols.py:29` defines a `Visualizer` Protocol that no
  one references anywhere outside the domain `__init__`'s re-export.
  `MatplotlibAnimator` and `PygameVisualizer` don't declare conformance, and
  `__main__` constructs them concretely.
- **Action**: delete the `Visualizer` Protocol — it's speculative
  generality. Add it back the day a third visualizer appears.

#### 2.5 `__main__.PYGAME_DPI` and the `--display-size` flag have split units
- `--display-size 10` means "10 inches" for matplotlib (figsize) and "1000
  pixels" for pygame (multiplied by 100). One flag, two unit systems.
- **Action**: split into `--figsize-inches` and `--window-pixels`, OR pick
  one unit and have the matplotlib branch convert. Document the choice in
  `--help`.

### 3. Test gaps

- **No `LifeSimulation` test exercises `seed="scattered"`.** The factory-level
  test in `test_seeds.py::test_scattered_available_via_factory` is fine but
  doesn't run a simulation step.
- **No malformed `.cells` file test.** CLAUDE.md says malformed files "log an
  error but do not raise" — that contract is unverified.
- **No empty-repository test.** Would catch finding 1.6.
- **`validate_args` is only exercised through `LifeSimulation.__init__`**, not
  directly. A focused unit test would catch finding 1.5.
- **No tests for `PygameVisualizer` or `MatplotlibAnimator`.** Acceptable for
  now (UI testing is expensive), but document the gap.
- **`ALL_ENGINES` constant is duplicated** in `test_life.py`,
  `test_engine_equivalence.py`, `test_timeit.py`. Three copies; one change
  touches three files. Move to a shared `tests/_shared.py` or a `conftest.py`
  fixture (CLAUDE.md prohibits the latter, but the prohibition is policy not
  law — worth revisiting).

### 4. Documentation drift

- `README.md` says `--display-size` defaults to `8`. Actual default is `10`
  (`__main__.py:31`, also asserted by `test_main_args.py`).
- `README.md` does not mention the `scattered` seed.
- `PROJECT.md` and `SPEC.md` list seed generators as
  `noise + pattern_seed + symmetric` — both miss `scattered.py` and
  `_placement.py`.
- `CLAUDE.md` test list omits `test_seeds.py` and `test_main_args.py`.
- `SPEC.md` claims `uv run mypy src/ — zero errors` but mypy isn't a dev
  dependency and there's no `[tool.mypy]` config.

### 5. Nits / FYI

- `src/life/__init__.py:20` — `if config.get("DEBUG"):` is truthy on the
  string `"false"`. Use a real boolean parse.
- `src/life/__init__.py:9` — `dotenv_values(dotenv_path=".env")` is
  cwd-relative; runs from anywhere except the project root silently load
  nothing. Compute the path from `__file__` like `_logging_conf` does.
- `logging.conf` writes to `logs/development.log` (also cwd-relative). No
  rotation; file grows unbounded.
- `pyproject.toml` has no version pins outside `uv.lock`. Acceptable given
  `uv` is the documented installer, but `pip install -e .` users get
  whatever's latest.
- `engines/window.py` and `engines/vectorized.py` are functionally identical
  (see 2.1).
- `scattered_count(size) = size*size // 2000` — magic number; promote `2000`
  to a named module constant with a docstring explaining the chosen density.
- `CellsPatternRepository._parse_cells` opens files without an explicit
  `encoding=`. ASCII-only `.cells` files mean it works, but `encoding="utf-8"`
  is one keystroke and removes a portability footgun.

---

## Architecture verdict

> **Is this the right architecture?** Yes — with two qualifications.

The DDD-style layering is appropriate for a project this size *because* it's
already paid off: six engine swaps, two frontend swaps, four seed strategies,
all without touching the simulation core. The `Grid` ↔ engines ↔ simulation
boundary is genuinely clean.

The two qualifications are:

1. **The "domain" is partially a numpy domain.** `Grid = NDArray[CellState]` in
   `domain/types.py` couples the domain to numpy. This is the right call (a
   pure-Python domain abstraction would cripple the engines), but it means the
   word "domain" is slightly aspirational. Either accept it (rename the layer
   to `core` if you want honesty), or push numpy out of the domain and into
   `engines/` — which would force `Grid` to become a `Sequence[Sequence[int]]`
   alias and slow everything down. **Recommendation: accept it**, document it
   in PROJECT.md.

2. **The protocol layer is half real.** `Simulation` and `PatternRepository`
   earn their keep. `Visualizer` and the `GridUpdater` Protocol don't.
   Speculative protocols cost readers the same time as real ones — delete the
   dead ones (see 1.1 and 2.4).

> **Are the patterns right?** Mostly.

- ✅ Strategy pattern for engines (registry of callables).
- ✅ Repository pattern for patterns (lazy-loading, protocol-backed).
- ✅ Iterator protocol for `LifeSimulation`.
- ✅ Composition root in `__main__`.
- ⚠️ Seed dispatch is hand-rolled instead of registry-driven (see 2.2).
- ⚠️ Two visualizer concrete classes share no base or protocol (Visualizer
   protocol exists but is unused — see 2.4).

> **Are the names right?** Mixed.

- ✅ Domain language: `Grid`, `CellState`, `Generation`-via-iterator,
   `apply_rules`, `Simulation`, `PatternRepository`. Good Conway vocabulary.
- ❌ Engine names mix descriptive (`convolution`, `loop`, `window`) with
   comparative (`fast`, `ultra_fast`, `vectorized`). See 2.1.
- ❌ `_TileMaker` / `_TilePattern` in `symmetric.py` are fine but their public
   methods (`quilt`, `book_match`, `hamburger`) are domain jargon that
   probably wants a docstring or a glossary in PROJECT.md.

---

## Recommended action plan (ordered)

The list below is **what I'd implement** if asked to follow up on this
review. It's ordered by leverage: each step makes the next easier or removes
ambiguity.

1. **Delete dead abstractions** (1.1, 2.4): drop the duplicate `GridUpdater`
   Protocol and the unused `Visualizer` Protocol. Pure subtraction; no risk.
2. **Move `BUILT_IN_SEEDS` to `seeds/`** and have validation import it from
   there (1.2). Pure subtraction from domain.
3. **Tighten `validate_args`** to reject `bool` (1.5) and add a direct unit
   test.
4. **Fix `SymmetricGenerator`** size contract (1.3) — crop or pad to
   `(size, size)` and replace `IndexError` with `SeedValueError`.
5. **Guard `ScatteredGenerator`** against empty repositories (1.6) with a
   regression test.
6. **Fix `CellsPatternRepository`**: warn on stem collision, defer
   `_loaded = True` (1.7). Add a malformed-`.cells` test.
7. **Update docs**: `README.md` `--display-size` default, add `scattered` to
   README/PROJECT/SPEC, fix CLAUDE.md test list. (Cheap; do alongside any of
   the above.)
8. **Defer to follow-up PRs** (each its own change):
   - Unify the seed-generator protocol (2.2).
   - Inject RNG (2.3).
   - Rename engines and remove `vectorized` if it's a duplicate of `window`
     (2.1).
   - Split `--display-size` into two flags (2.5).
   - Fix `simulation/life_simulation.py` docstring or invert seed dependency
     (1.4).

Each of items 1–7 is a ≤ 50-line change with a focused regression test. They
should land in separate commits so the history reads cleanly. Items 8 are
larger and warrant their own design discussion — none are urgent.

---

## Critical files referenced

- `src/life/domain/types.py` — duplicate `GridUpdater`, `BUILT_IN_SEEDS` leak.
- `src/life/domain/protocols.py` — dead `Visualizer` Protocol, duplicate
  `GridUpdater`.
- `src/life/domain/rules.py` — single source of Conway truth (good).
- `src/life/seeds/__init__.py` — hand-rolled dispatch, drift risk vs.
  `BUILT_IN_SEEDS`.
- `src/life/seeds/symmetric.py` — size-contract violation, `IndexError` on
  small sizes, mixed RNGs.
- `src/life/seeds/scattered.py` — empty-repo crash, magic `2000`.
- `src/life/simulation/life_simulation.py` — inaccurate docstring, imports
  non-domain modules.
- `src/life/validation/exceptions.py` — `bool`-as-`int` admission.
- `src/life/infrastructure/cells_pattern_repository.py` — silent stem
  collisions, `_loaded` set too early, no encoding.
- `src/life/__init__.py` — cwd-relative `.env`/log paths, stringly-typed
  `DEBUG`.
- `src/life/__main__.py` — `--display-size` unit ambiguity.
- `src/life/engines/{fast,ultra_fast,vectorized,window}.py` — naming and
  near-duplication.
- `tests/test_life.py` — `scattered` not in parametrized seeds.
- `tests/test_pattern_repository.py` — no malformed-file test, asserts
  private `_loaded`.
- `README.md`, `PROJECT.md`, `SPEC.md`, `CLAUDE.md` — drift on `scattered`,
  default sizes, mypy claim.

---

## Verification

This is a review, not a code change, so verification is reading-shaped:

- Open each "Critical files referenced" file and confirm the cited line
  numbers / behaviors match the report.
- For any item the user wants implemented, the matching tests are listed
  beside the finding (e.g. add a `test_validate_args_rejects_bool`,
  `test_scattered_empty_repository_raises`,
  `test_pattern_repository_logs_on_malformed_file`).
- Re-run `uv run pytest tests/ -q` after any fix to confirm the existing
  141 tests still pass.
- Re-run `uv run --with mypy mypy src/` after any fix to keep the
  zero-errors claim true.

## Verdict

**Approve the codebase as-is.** Health is good. The findings above are
incremental improvements, not blockers. The biggest single win is item 2
(seed-generator protocol unification) — it would shrink the seed dispatcher
from a typed if/elif into a dict lookup and remove the drift risk between
`BUILT_IN_SEEDS` and the literal-string branches.
