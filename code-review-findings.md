# Code Review Findings — bitpack addition (HEAD~4..HEAD)

Date: 2026-05-24

## Finding 1 — `--func` alias crashes at runtime

**File:** `src/life/__main__.py:43`
**Severity:** High

`CLAUDE.md` documents `--func` as a backwards-compatibility alias for `--engine`, but `build_parser()` never registers it. Running `python -m life --func bitpack` exits with `error: unrecognized arguments: --func bitpack`.

**Failure scenario:** Any script or user relying on the documented `--func` flag gets a hard CLI crash.

---

## Finding 2 — CSA adder tree drops carry; wrong neighbor counts for 4 and 8

**File:** `src/life/engines/bitpack.py:96`
**Severity:** Medium (latent)

Line 96: `bit1, _ = _csa(bit1_pre, carry_mid, zero)` discards the carry output. This causes:
- 4 live neighbors → reported as 0
- 8 live neighbors → reported as 4

Currently masked because `apply_rules` only distinguishes counts 2 and 3 — both wrong values still map to "dead cell". Any future extension of `apply_rules` or direct use of `neighbor_count` would produce silently wrong results while all other engines remain correct.

**Failure scenario:** A birth-at-4 variant rule, or any code that inspects `neighbor_count` directly, would get wrong counts from `bitpack` only.

---

## Finding 3 — Odd-size symmetric seed silently breaks 4-fold symmetry

**File:** `src/life/seeds/symmetric.py:84`
**Severity:** Medium

For odd `size`, `k = size // 2` tiles a `(2k) × (2k) = (size-1) × (size-1)` subgrid into a `size × size` zero-initialized array. The last row and column are always dead, breaking the symmetry the seed is supposed to guarantee. No test asserts symmetry, so it passes silently.

**Failure scenario:** `SymmetricGenerator()(11)` returns an 11×11 grid where row 10 and column 10 are always zero; toroidal wrap then gives row 0 fewer live neighbours than a truly symmetric seed would.

---

## Finding 4 — `bitpack` absent from `test_combinations` integration test

**File:** `tests/test_life.py:521`
**Severity:** Low-Medium

The `test_combinations` parametrize list covers `convolution`, `loop`, `roll`, `pad_slice`, and `ix_index` (twice). `bitpack` is never exercised in an end-to-end simulation run. A regression across the full `LifeSimulation` iterator stack would go undetected.

**Failure scenario:** A dtype coercion bug or multi-step evolution error in `bitpack` would not be caught by the integration suite.

---

## Finding 5 — Equivalence tests only cover square grids

**File:** `tests/test_engine_equivalence.py:261`
**Severity:** Low

All parametrized sizes `[3, 4, 5, 10, 16]` are passed as `size × size`. `bitpack`'s column-packing arithmetic (`_shift_left`, `_shift_right`, carry logic, `last_bit`, `pad_mask`) is untested for non-square inputs.

**Failure scenario:** A bug in carry logic for a non-square grid (e.g. 5×9) would not be caught; `bitpack(np.random.randint(0,2,(5,9)))` diverging from `convolution` would go undetected.
