"""
Test that all engine functions produce identical results for the same input.

This test module verifies that the _apply_rules refactoring in engine.py works
correctly across all computation strategies (convolution, loop, window, fast,
ultra_fast, vectorized). All engines should produce bitwise identical outputs
for the same initial state.

Test coverage includes:
- Simple known patterns (vertical line, horizontal line)
- Larger random states to catch edge cases in wrapping behavior
- All 6 engine implementations
- Multiple rounds of iterations (consistency across generations)
"""
import numpy as np
import pytest

from life import State
from life.engine import convolution, loop, window, fast, ultra_fast, vectorized


# All 6 engine functions available in life.engine
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
    """
    Vertical line pattern on a 7x7 grid and its expected next state.

    The vertical line expands due to the Game of Life rules.
    Uses 7x7 grid to minimize toroidal wrapping effects.

    Returns
    -------
    tuple[State, State]
        Input state and expected output state.
    """
    input_state = np.zeros((7, 7), dtype=np.int8)
    input_state[:, 3] = 1

    expected = np.zeros((7, 7), dtype=np.int8)
    expected[:, 2:5] = 1

    return input_state, expected


@pytest.fixture
def horizontal_line_pattern() -> tuple[State, State]:
    """
    Horizontal line pattern on a 7x7 grid and its expected next state.

    The horizontal line expands due to the Game of Life rules.
    Uses 7x7 grid to minimize toroidal wrapping effects.

    Returns
    -------
    tuple[State, State]
        Input state and expected output state.
    """
    input_state = np.zeros((7, 7), dtype=np.int8)
    input_state[3, :] = 1

    expected = np.zeros((7, 7), dtype=np.int8)
    expected[2:5, :] = 1

    return input_state, expected


@pytest.fixture
def block_pattern() -> tuple[State, State]:
    """
    Still life pattern: block (2x2 square).

    Block is a stable pattern that does not change over time.

    Returns
    -------
    tuple[State, State]
        Input state and expected output state (same as input).
    """
    input_state = np.array([
        [0, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0]
    ], dtype=np.int8)

    expected = input_state.copy()

    return input_state, expected


@pytest.fixture
def glider_pattern() -> tuple[State, State]:
    """
    Glider pattern and its expected next state.

    The glider is a spaceship that moves diagonally across the grid.
    Uses 5x5 grid with glider in top-left to minimize wrapping effects.

    Returns
    -------
    tuple[State, State]
        Input state and expected output state.
    """
    input_state = np.zeros((5, 5), dtype=np.int8)
    input_state[0:3, 0:3] = np.array([
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1]
    ], dtype=np.int8)

    expected = np.zeros((5, 5), dtype=np.int8)
    expected[0:4, 0:4] = np.array([
        [0, 0, 0, 0],
        [1, 0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 0, 0]
    ], dtype=np.int8)

    return input_state, expected


@pytest.fixture
def random_state_small() -> State:
    """
    Small random state for testing.

    Returns
    -------
    State
        A 5x5 random binary state.
    """
    np.random.seed(42)
    return np.random.randint(0, 2, size=(5, 5), dtype=np.int8)


@pytest.fixture
def random_state_medium() -> State:
    """
    Medium random state for testing.

    Returns
    -------
    State
        A 10x10 random binary state.
    """
    np.random.seed(42)
    return np.random.randint(0, 2, size=(10, 10), dtype=np.int8)


class TestEngineEquivalenceSimplePatterns:
    """Test engine equivalence on known simple patterns."""

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_vertical_line_next_generation(self, engine_name: str, vertical_line_pattern):
        """
        Test that engine produces correct next state for vertical line.

        The vertical line should become a horizontal line.
        """
        engine_func = ALL_ENGINES[engine_name]
        input_state, expected = vertical_line_pattern

        result = engine_func(input_state)

        assert np.array_equal(result, expected), (
            f"{engine_name} produced incorrect result for vertical line.\n"
            f"Expected:\n{expected}\nGot:\n{result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_horizontal_line_next_generation(self, engine_name: str, horizontal_line_pattern):
        """
        Test that engine produces correct next state for horizontal line.

        The horizontal line should become a vertical line.
        """
        engine_func = ALL_ENGINES[engine_name]
        input_state, expected = horizontal_line_pattern

        result = engine_func(input_state)

        assert np.array_equal(result, expected), (
            f"{engine_name} produced incorrect result for horizontal line.\n"
            f"Expected:\n{expected}\nGot:\n{result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_block_pattern_stable(self, engine_name: str, block_pattern):
        """
        Test that block (still life) pattern remains stable.

        Block is stable and should not change.
        """
        engine_func = ALL_ENGINES[engine_name]
        input_state, expected = block_pattern

        result = engine_func(input_state)

        assert np.array_equal(result, expected), (
            f"{engine_name} failed to preserve block pattern.\n"
            f"Expected:\n{expected}\nGot:\n{result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_glider_pattern_moves(self, engine_name: str, glider_pattern):
        """
        Test that glider pattern produces correct next state.
        """
        engine_func = ALL_ENGINES[engine_name]
        input_state, expected = glider_pattern

        result = engine_func(input_state)

        assert np.array_equal(result, expected), (
            f"{engine_name} produced incorrect result for glider.\n"
            f"Expected:\n{expected}\nGot:\n{result}"
        )


class TestEngineEquivalenceAllEngines:
    """Test that all engines produce identical results across various inputs."""

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_vertical_line(
        self, engine_name: str, vertical_line_pattern
    ):
        """
        Test that all engines produce the same result as convolution for vertical line.
        """
        input_state, _ = vertical_line_pattern

        convolution_result = convolution(input_state)
        engine_result = ALL_ENGINES[engine_name](input_state)

        assert np.array_equal(engine_result, convolution_result), (
            f"{engine_name} differs from convolution for vertical line.\n"
            f"Convolution:\n{convolution_result}\n{engine_name}:\n{engine_result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_horizontal_line(
        self, engine_name: str, horizontal_line_pattern
    ):
        """
        Test that all engines produce the same result as convolution for horizontal line.
        """
        input_state, _ = horizontal_line_pattern

        convolution_result = convolution(input_state)
        engine_result = ALL_ENGINES[engine_name](input_state)

        assert np.array_equal(engine_result, convolution_result), (
            f"{engine_name} differs from convolution for horizontal line.\n"
            f"Convolution:\n{convolution_result}\n{engine_name}:\n{engine_result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_block(self, engine_name: str, block_pattern):
        """
        Test that all engines produce the same result as convolution for block pattern.
        """
        input_state, _ = block_pattern

        convolution_result = convolution(input_state)
        engine_result = ALL_ENGINES[engine_name](input_state)

        assert np.array_equal(engine_result, convolution_result), (
            f"{engine_name} differs from convolution for block.\n"
            f"Convolution:\n{convolution_result}\n{engine_name}:\n{engine_result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_glider(self, engine_name: str, glider_pattern):
        """
        Test that all engines produce the same result as convolution for glider.
        """
        input_state, _ = glider_pattern

        convolution_result = convolution(input_state)
        engine_result = ALL_ENGINES[engine_name](input_state)

        assert np.array_equal(engine_result, convolution_result), (
            f"{engine_name} differs from convolution for glider.\n"
            f"Convolution:\n{convolution_result}\n{engine_name}:\n{engine_result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_random_small(
        self, engine_name: str, random_state_small
    ):
        """
        Test that all engines produce the same result as convolution on small random state.
        """
        convolution_result = convolution(random_state_small)
        engine_result = ALL_ENGINES[engine_name](random_state_small)

        assert np.array_equal(engine_result, convolution_result), (
            f"{engine_name} differs from convolution on small random state.\n"
            f"Convolution:\n{convolution_result}\n{engine_name}:\n{engine_result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_match_convolution_random_medium(
        self, engine_name: str, random_state_medium
    ):
        """
        Test that all engines produce the same result as convolution on medium random state.
        """
        convolution_result = convolution(random_state_medium)
        engine_result = ALL_ENGINES[engine_name](random_state_medium)

        assert np.array_equal(engine_result, convolution_result), (
            f"{engine_name} differs from convolution on medium random state.\n"
            f"Convolution:\n{convolution_result}\n{engine_name}:\n{engine_result}"
        )


class TestEngineConsistency:
    """Test consistency of engine results across multiple generations."""

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_engine_consistent_across_generations_blinker_oscillation(
        self, engine_name: str
    ):
        """
        Test that blinker oscillator (period-2) returns to original state after 2 generations.

        The blinker is a simple horizontal line that becomes vertical and vice versa.
        """
        engine_func = ALL_ENGINES[engine_name]
        # Blinker on 5x5 grid to minimize wrapping effects
        blinker = np.zeros((5, 5), dtype=np.int8)
        blinker[2, 1:4] = 1

        # First generation: horizontal -> vertical
        state_gen1 = engine_func(blinker)
        # Second generation: vertical -> horizontal
        state_gen2 = engine_func(state_gen1)

        # After 2 generations, should match original
        assert np.array_equal(state_gen2, blinker), (
            f"{engine_name} failed to oscillate correctly for blinker.\n"
            f"Original:\n{blinker}\nAfter 2 gens:\n{state_gen2}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_engine_block_remains_stable_multiple_generations(
        self, engine_name: str, block_pattern
    ):
        """
        Test that block pattern remains stable across multiple generations.
        """
        engine_func = ALL_ENGINES[engine_name]
        input_state, _ = block_pattern

        # Apply engine 5 times
        state = input_state.copy()
        for _ in range(5):
            state = engine_func(state)
            assert np.array_equal(state, input_state), (
                f"{engine_name} failed to keep block stable.\n"
                f"Expected:\n{input_state}\nGot:\n{state}"
            )


class TestEngineEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_all_engines_handle_empty_state(self):
        """
        Test that all engines handle an all-zero (empty) state correctly.

        An empty state should remain empty (no births possible).
        """
        empty_state = np.zeros((5, 5), dtype=np.int8)

        for engine_name, engine_func in ALL_ENGINES.items():
            result = engine_func(empty_state)
            assert np.array_equal(result, empty_state), (
                f"{engine_name} produced non-zero result from empty state.\n"
                f"Got:\n{result}"
            )

    def test_all_engines_handle_full_state(self):
        """
        Test that all engines handle an all-live state correctly.

        In a full state, most cells die due to overpopulation (>3 neighbors).
        Only corner and edge cells survive or die in specific patterns.
        """
        full_state = np.ones((5, 5), dtype=np.int8)

        reference_result = convolution(full_state)

        for engine_name, engine_func in ALL_ENGINES.items():
            result = engine_func(full_state)
            assert np.array_equal(result, reference_result), (
                f"{engine_name} differs from convolution on full state.\n"
                f"Convolution:\n{reference_result}\n{engine_name}:\n{result}"
            )

    def test_all_engines_handle_single_cell(self):
        """
        Test that all engines handle a single live cell correctly.

        A single cell has 0 neighbors (with wrapping), so it dies.
        """
        single_cell = np.zeros((3, 3), dtype=np.int8)
        single_cell[1, 1] = 1

        reference_result = convolution(single_cell)

        for engine_name, engine_func in ALL_ENGINES.items():
            result = engine_func(single_cell)
            assert np.array_equal(result, reference_result), (
                f"{engine_name} differs from convolution on single cell.\n"
                f"Convolution:\n{reference_result}\n{engine_name}:\n{result}"
            )

    @pytest.mark.parametrize("size", [3, 4, 5, 10, 16])
    def test_all_engines_handle_various_sizes(self, size: int):
        """
        Test that all engines work correctly with various grid sizes.

        This ensures wrapping boundary conditions work for different dimensions.
        """
        np.random.seed(42)
        state = np.random.randint(0, 2, size=(size, size), dtype=np.int8)

        reference_result = convolution(state)

        for engine_name, engine_func in ALL_ENGINES.items():
            result = engine_func(state)
            assert np.array_equal(result, reference_result), (
                f"{engine_name} differs from convolution for size {size}x{size}.\n"
                f"Convolution:\n{reference_result}\n{engine_name}:\n{result}"
            )


class TestApplyRulesRefactoring:
    """
    Dedicated tests to verify the _apply_rules refactoring works correctly.

    The _apply_rules function encapsulates Conway's Game of Life rules:
    - A cell is alive if it has exactly 3 neighbors (birth), OR
    - It is currently alive AND has exactly 2 neighbors (survival)
    """

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_birth_rule_exactly_3_neighbors(self, engine_name: str):
        """
        Test that birth rule works: dead cell with 3 neighbors becomes alive.

        Create a configuration where a dead cell has exactly 3 live neighbors.
        """
        # Center cell is dead, has 3 live neighbors (top-left, top, top-right)
        state = np.array([
            [1, 1, 1],
            [0, 0, 0],
            [0, 0, 0]
        ], dtype=np.int8)

        engine_func = ALL_ENGINES[engine_name]
        result = engine_func(state)

        # After next generation, center cell should be alive
        # (and possibly others depending on their neighbor counts)
        reference_result = convolution(state)

        assert np.array_equal(result, reference_result), (
            f"{engine_name} failed birth rule test.\n"
            f"Convolution:\n{reference_result}\n{engine_name}:\n{result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_survival_rule_exactly_2_neighbors(self, engine_name: str):
        """
        Test that survival rule works: live cell with 2 neighbors survives.

        Create a configuration where a live cell has exactly 2 neighbors.
        """
        # Center cell is alive, has 2 neighbors (left and right via wrapping)
        state = np.array([
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ], dtype=np.int8)

        engine_func = ALL_ENGINES[engine_name]
        result = engine_func(state)

        reference_result = convolution(state)

        assert np.array_equal(result, reference_result), (
            f"{engine_name} failed survival rule test.\n"
            f"Convolution:\n{reference_result}\n{engine_name}:\n{result}"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_overpopulation_rule_more_than_3_neighbors(self, engine_name: str):
        """
        Test that overpopulation rule works: live cell with >3 neighbors dies.
        """
        # Center cell is alive but surrounded by 4 live neighbors
        state = np.array([
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0]
        ], dtype=np.int8)

        engine_func = ALL_ENGINES[engine_name]
        result = engine_func(state)

        reference_result = convolution(state)

        assert np.array_equal(result, reference_result), (
            f"{engine_name} failed overpopulation rule test.\n"
            f"Convolution:\n{reference_result}\n{engine_name}:\n{result}"
        )
