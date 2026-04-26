"""
Test that all engine functions produce identical results for the same input.

All engines must produce bitwise-identical outputs for the same initial state.
"""
import numpy as np
import pytest

from life.domain.rules import apply_rules
from life.domain.types import Grid as State
from life.engines import convolution, loop, window, fast, ultra_fast, vectorized


ALL_ENGINES = {
    "convolution": convolution,
    "loop": loop,
    "window": window,
    "fast": fast,
    "ultra_fast": ultra_fast,
    "vectorized": vectorized,
}


@pytest.fixture
def vertical_line_pattern() -> tuple[State, State]:
    """Vertical line on 7x7 grid; expected next state is a 3-column band."""
    input_state = np.zeros((7, 7), dtype=np.int8)
    input_state[:, 3] = 1
    expected = np.zeros((7, 7), dtype=np.int8)
    expected[:, 2:5] = 1
    return input_state, expected


@pytest.fixture
def horizontal_line_pattern() -> tuple[State, State]:
    """Horizontal line on 7x7 grid; expected next state is a 3-row band."""
    input_state = np.zeros((7, 7), dtype=np.int8)
    input_state[3, :] = 1
    expected = np.zeros((7, 7), dtype=np.int8)
    expected[2:5, :] = 1
    return input_state, expected


@pytest.fixture
def block_pattern() -> tuple[State, State]:
    """2×2 block still life — stable across all generations."""
    input_state = np.array([
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0],
    ], dtype=np.int8)
    return input_state, input_state.copy()


@pytest.fixture
def glider_pattern() -> tuple[State, State]:
    """Glider on 5x5 grid and its expected next state."""
    input_state = np.zeros((5, 5), dtype=np.int8)
    input_state[0:3, 0:3] = np.array([
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ], dtype=np.int8)
    expected = np.zeros((5, 5), dtype=np.int8)
    expected[0:4, 0:4] = np.array([
        [0, 0, 0, 0],
        [1, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 0],
    ], dtype=np.int8)
    return input_state, expected


@pytest.fixture
def random_state_small() -> State:
    np.random.seed(42)
    return np.random.randint(0, 2, size=(5, 5), dtype=np.int8)


@pytest.fixture
def random_state_medium() -> State:
    np.random.seed(42)
    return np.random.randint(0, 2, size=(10, 10), dtype=np.int8)


class TestEngineEquivalenceSimplePatterns:
    """Engine equivalence on known simple patterns."""

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_vertical_line_next_generation(self, engine_name, vertical_line_pattern):
        engine_func = ALL_ENGINES[engine_name]
        input_state, expected = vertical_line_pattern
        result = engine_func(input_state)
        assert np.array_equal(result, expected), (
            f"{engine_name} produced incorrect result for vertical line.\n"
            f"Expected:\n{expected}\nGot:\n{result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_horizontal_line_next_generation(
        self, engine_name, horizontal_line_pattern
    ):
        engine_func = ALL_ENGINES[engine_name]
        input_state, expected = horizontal_line_pattern
        result = engine_func(input_state)
        assert np.array_equal(result, expected), (
            f"{engine_name} produced incorrect result for horizontal line.\n"
            f"Expected:\n{expected}\nGot:\n{result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_block_pattern_stable(self, engine_name, block_pattern):
        engine_func = ALL_ENGINES[engine_name]
        input_state, expected = block_pattern
        result = engine_func(input_state)
        assert np.array_equal(result, expected), (
            f"{engine_name} failed to preserve block pattern.\n"
            f"Expected:\n{expected}\nGot:\n{result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_glider_pattern_moves(self, engine_name, glider_pattern):
        engine_func = ALL_ENGINES[engine_name]
        input_state, expected = glider_pattern
        result = engine_func(input_state)
        assert np.array_equal(result, expected), (
            f"{engine_name} produced incorrect result for glider.\n"
            f"Expected:\n{expected}\nGot:\n{result}"
        )


class TestEngineEquivalenceAllEngines:
    """All engines must produce identical output to convolution."""

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_vertical_line(
        self, engine_name, vertical_line_pattern
    ):
        input_state, _ = vertical_line_pattern
        ref = convolution(input_state)
        result = ALL_ENGINES[engine_name](input_state)
        assert np.array_equal(result, ref), (
            f"{engine_name} differs from convolution for vertical line."
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_horizontal_line(
        self, engine_name, horizontal_line_pattern
    ):
        input_state, _ = horizontal_line_pattern
        ref = convolution(input_state)
        result = ALL_ENGINES[engine_name](input_state)
        assert np.array_equal(result, ref), (
            f"{engine_name} differs from convolution for horizontal line."
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_block(self, engine_name, block_pattern):
        input_state, _ = block_pattern
        ref = convolution(input_state)
        result = ALL_ENGINES[engine_name](input_state)
        assert np.array_equal(result, ref), (
            f"{engine_name} differs from convolution for block."
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_glider(self, engine_name, glider_pattern):
        input_state, _ = glider_pattern
        ref = convolution(input_state)
        result = ALL_ENGINES[engine_name](input_state)
        assert np.array_equal(result, ref), (
            f"{engine_name} differs from convolution for glider."
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_random_small(
        self, engine_name, random_state_small
    ):
        ref = convolution(random_state_small)
        result = ALL_ENGINES[engine_name](random_state_small)
        assert np.array_equal(result, ref), (
            f"{engine_name} differs from convolution on small random state."
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_random_medium(
        self, engine_name, random_state_medium
    ):
        ref = convolution(random_state_medium)
        result = ALL_ENGINES[engine_name](random_state_medium)
        assert np.array_equal(result, ref), (
            f"{engine_name} differs from convolution on medium random state."
        )


class TestEngineConsistency:
    """Engine results stay consistent across multiple generations."""

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_engine_consistent_across_generations_blinker_oscillation(
        self, engine_name
    ):
        """Blinker (period-2) must return to original after 2 generations."""
        engine_func = ALL_ENGINES[engine_name]
        blinker = np.zeros((5, 5), dtype=np.int8)
        blinker[2, 1:4] = 1
        state_gen2 = engine_func(engine_func(blinker))
        assert np.array_equal(state_gen2, blinker), (
            f"{engine_name} failed to oscillate correctly for blinker.\n"
            f"Original:\n{blinker}\nAfter 2 gens:\n{state_gen2}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_engine_block_remains_stable_multiple_generations(
        self, engine_name, block_pattern
    ):
        engine_func = ALL_ENGINES[engine_name]
        input_state, _ = block_pattern
        state = input_state.copy()
        for _ in range(5):
            state = engine_func(state)
            assert np.array_equal(state, input_state), (
                f"{engine_name} failed to keep block stable."
            )


class TestEngineEdgeCases:
    """Edge cases and boundary conditions."""

    def test_all_engines_handle_empty_state(self):
        empty_state = np.zeros((5, 5), dtype=np.int8)
        for engine_name, engine_func in ALL_ENGINES.items():
            result = engine_func(empty_state)
            assert np.array_equal(result, empty_state), (
                f"{engine_name} produced non-zero result from empty state."
            )

    def test_all_engines_handle_full_state(self):
        full_state = np.ones((5, 5), dtype=np.int8)
        ref = convolution(full_state)
        for engine_name, engine_func in ALL_ENGINES.items():
            result = engine_func(full_state)
            assert np.array_equal(result, ref), (
                f"{engine_name} differs from convolution on full state."
            )

    def test_all_engines_handle_single_cell(self):
        single_cell = np.zeros((3, 3), dtype=np.int8)
        single_cell[1, 1] = 1
        ref = convolution(single_cell)
        for engine_name, engine_func in ALL_ENGINES.items():
            result = engine_func(single_cell)
            assert np.array_equal(result, ref), (
                f"{engine_name} differs from convolution on single cell."
            )

    @pytest.mark.parametrize("size", [3, 4, 5, 10, 16])
    def test_all_engines_handle_various_sizes(self, size):
        np.random.seed(42)
        state = np.random.randint(0, 2, size=(size, size), dtype=np.int8)
        ref = convolution(state)
        for engine_name, engine_func in ALL_ENGINES.items():
            result = engine_func(state)
            assert np.array_equal(result, ref), (
                f"{engine_name} differs from convolution for size {size}x{size}."
            )


class TestApplyRulesDirect:
    """
    Direct tests of apply_rules() — now public and independently testable.

    Previously _apply_rules was private in engine.py; these tests were not possible.
    """

    def test_birth_rule(self):
        """Dead cell with exactly 3 live neighbors is born."""
        neighbors = np.array([[0, 3, 0]], dtype=np.int8)
        state = np.array([[0, 0, 0]], dtype=np.int8)
        result = apply_rules(neighbors, state)
        assert result[0, 1] == 1

    def test_survival_with_2_neighbors(self):
        """Live cell with 2 neighbors survives."""
        neighbors = np.array([[0, 2, 0]], dtype=np.int8)
        state = np.array([[0, 1, 0]], dtype=np.int8)
        result = apply_rules(neighbors, state)
        assert result[0, 1] == 1

    def test_survival_with_3_neighbors(self):
        """Live cell with 3 neighbors survives."""
        neighbors = np.array([[0, 3, 0]], dtype=np.int8)
        state = np.array([[0, 1, 0]], dtype=np.int8)
        result = apply_rules(neighbors, state)
        assert result[0, 1] == 1

    def test_underpopulation_dies(self):
        """Live cell with fewer than 2 neighbors dies."""
        for n in (0, 1):
            neighbors = np.array([[0, n, 0]], dtype=np.int8)
            state = np.array([[0, 1, 0]], dtype=np.int8)
            result = apply_rules(neighbors, state)
            assert result[0, 1] == 0, f"Expected death with {n} neighbors"

    def test_overpopulation_dies(self):
        """Live cell with more than 3 neighbors dies."""
        for n in (4, 5, 6, 7, 8):
            neighbors = np.array([[0, n, 0]], dtype=np.int8)
            state = np.array([[0, 1, 0]], dtype=np.int8)
            result = apply_rules(neighbors, state)
            assert result[0, 1] == 0, f"Expected death with {n} neighbors"

    def test_dead_cell_no_birth_without_exactly_3(self):
        """Dead cell with neighbor count != 3 stays dead."""
        for n in (0, 1, 2, 4, 5, 6, 7, 8):
            neighbors = np.array([[0, n, 0]], dtype=np.int8)
            state = np.array([[0, 0, 0]], dtype=np.int8)
            result = apply_rules(neighbors, state)
            assert result[0, 1] == 0, f"Expected no birth with {n} neighbors"

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_engines_consistent_with_apply_rules_birth(self, engine_name):
        """Engines agree with apply_rules on a birth-rule pattern."""
        state = np.array([
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0],
        ], dtype=np.int8)
        ref = convolution(state)
        result = ALL_ENGINES[engine_name](state)
        assert np.array_equal(result, ref), (
            f"{engine_name} failed birth rule test."
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_engines_consistent_with_apply_rules_overpopulation(self, engine_name):
        state = np.array([
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0],
        ], dtype=np.int8)
        ref = convolution(state)
        result = ALL_ENGINES[engine_name](state)
        assert np.array_equal(result, ref), (
            f"{engine_name} failed overpopulation rule test."
        )
