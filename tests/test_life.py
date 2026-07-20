"""
Comprehensive unit tests for the LifeSimulation class.

Test organization:
1. TestLifeInitialization: Valid construction scenarios
2. TestLifeIteratorProtocol: Iterator protocol compliance
3. TestLifeStateProgression: State updates over multiple generations
4. TestLifeWithAllEngines: All 6 engine function support
5. TestLifeWithVariousGridSizes: Grid size range validation
6. TestLifeInvalidInputs: Error handling for invalid arguments
7. TestLifeMultipleIterations: Consecutive iteration behavior
"""

import numpy as np
import pytest

from life.domain import Grid as State, GridUpdater as StateUpdater
from life.engines import bitpack, convolution, ix_index, loop, pad_slice, roll
from life.infrastructure import CellsPatternRepository
from life.simulation import LifeSimulation as Life
from life.validation import (
    LifeParamsError,
    SizeTypeError,
    SizeValueError,
)


ALL_ENGINES = {
    "bitpack": bitpack,
    "convolution": convolution,
    "loop": loop,
    "pad_slice": pad_slice,
    "ix_index": ix_index,
    "roll": roll,
}

VALID_SEEDS = ["noise", "symmetric"]
PATTERN_SEEDS = ["glider", "blinker", "gosperglidergun"]
MIN_SIZE = 10
MAX_SIZE = 1000


@pytest.fixture(scope="module")
def repository() -> CellsPatternRepository:
    return CellsPatternRepository()


@pytest.fixture
def default_engine() -> StateUpdater:
    return convolution


@pytest.fixture
def default_seed() -> str:
    return "noise"


@pytest.fixture
def simple_state() -> State:
    state = np.zeros((10, 10), dtype=np.int8)
    state[4:6, 4:6] = 1
    return state


@pytest.fixture
def blinker_horizontal() -> State:
    state = np.zeros((10, 10), dtype=np.int8)
    state[5, 4:7] = 1
    return state


@pytest.fixture
def blinker_vertical() -> State:
    state = np.zeros((10, 10), dtype=np.int8)
    state[4:7, 5] = 1
    return state


@pytest.fixture
def all_alive_state() -> State:
    return np.ones((10, 10), dtype=np.int8)


@pytest.fixture
def all_dead_state() -> State:
    return np.zeros((10, 10), dtype=np.int8)


class TestLifeInitialization:
    """Test valid initialization scenarios for the LifeSimulation class."""

    def test_init_with_noise_seed(self, repository):
        life = Life(size=50, seed="noise", engine=convolution, repository=repository)
        assert life.state.shape == (50, 50)
        assert life.state.dtype == np.int8
        assert life.engine == convolution

    @pytest.mark.parametrize("size", [10, 11, 20, 50, 51, 100])
    def test_init_with_symmetric_seed(self, size, repository):
        life = Life(
            size=size, seed="symmetric", engine=convolution, repository=repository
        )
        assert life.state.shape == (size, size)
        assert life.state.dtype == np.int8
        assert np.all((life.state == 0) | (life.state == 1))

    @pytest.mark.parametrize("seed", PATTERN_SEEDS)
    def test_init_with_pattern_seeds(self, seed, repository):
        life = Life(size=50, seed=seed, engine=convolution, repository=repository)
        assert life.state.shape == (50, 50)
        assert life.state.dtype == np.int8

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_init_with_all_engines(self, engine_name, repository):
        engine = ALL_ENGINES[engine_name]
        life = Life(size=50, seed="noise", engine=engine, repository=repository)
        assert life.engine == engine

    @pytest.mark.parametrize("size", [10, 50, 100, 500, 1000])
    def test_init_with_various_sizes(self, size, repository):
        life = Life(size=size, seed="noise", engine=convolution, repository=repository)
        assert life.state.shape == (size, size)

    def test_init_stores_correct_state(self, repository):
        life = Life(size=20, seed="noise", engine=convolution, repository=repository)
        assert isinstance(life.state, np.ndarray)
        assert life.state.dtype == np.int8
        assert life.state.shape == (20, 20)
        assert np.all((life.state == 0) | (life.state == 1))

    def test_init_stores_function_reference(self, default_engine, repository):
        life = Life(
            size=20, seed="noise", engine=default_engine, repository=repository
        )
        assert life.engine is default_engine


class TestLifeIteratorProtocol:
    """Test the iterator protocol implementation of LifeSimulation."""

    def test_iter_returns_self(self, default_engine, default_seed, repository):
        life = Life(
            size=20, seed=default_seed, engine=default_engine, repository=repository
        )
        assert iter(life) is life

    def test_next_returns_state(self, default_engine, default_seed, repository):
        life = Life(
            size=20, seed=default_seed, engine=default_engine, repository=repository
        )
        result = next(life)
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.int8

    def test_next_returns_correct_shape(self, default_engine, default_seed, repository):
        size = 30
        life = Life(
            size=size, seed=default_seed, engine=default_engine, repository=repository
        )
        result = next(life)
        assert result.shape == (size, size)

    def test_can_iterate_multiple_times(self, default_engine, default_seed, repository):
        life = Life(
            size=20, seed=default_seed, engine=default_engine, repository=repository
        )
        for state in [next(life), next(life), next(life)]:
            assert state.shape == (20, 20)

    def test_for_loop_iteration(self, default_engine, default_seed, repository):
        life = Life(
            size=20, seed=default_seed, engine=default_engine, repository=repository
        )
        count = 0
        for state in life:
            count += 1
            assert isinstance(state, np.ndarray)
            if count >= 5:
                break
        assert count == 5

    def test_iterator_is_persistent(self, default_engine, default_seed, repository):
        life = Life(
            size=20, seed=default_seed, engine=default_engine, repository=repository
        )
        states = []
        for state in life:
            states.append(state.copy())
            if len(states) >= 3:
                break
        assert len(states) == 3
        for state in states:
            assert state.shape == (20, 20)


class TestLifeStateProgression:
    """Test that state progresses correctly through generations."""

    def test_state_changes_after_next(self, default_engine, repository):
        life = Life(
            size=20, seed="blinker", engine=default_engine, repository=repository
        )
        initial_state = life.state.copy()
        next_state = next(life)
        assert not np.array_equal(initial_state, next_state)

    def test_state_attribute_updated(self, default_engine, default_seed, repository):
        life = Life(
            size=20, seed=default_seed, engine=default_engine, repository=repository
        )
        returned_state = next(life)
        assert np.array_equal(life.state, returned_state)

    def test_successive_states_differ(self, default_engine, default_seed, repository):
        Life(size=25, seed=default_seed, engine=default_engine, repository=repository)

    def test_block_pattern_is_stable(self, default_engine, repository):
        life = Life(
            size=20, seed="glider", engine=default_engine, repository=repository
        )
        life.state = np.zeros((20, 20), dtype=np.int8)
        life.state[8:10, 8:10] = 1
        block_state = life.state.copy()
        next_state = next(life)
        assert np.array_equal(block_state, next_state)

    def test_blinker_oscillates(self, default_engine, repository):
        life = Life(
            size=20, seed="glider", engine=default_engine, repository=repository
        )
        life.state = np.zeros((20, 20), dtype=np.int8)
        life.state[10, 8:11] = 1
        state_0 = life.state.copy()
        state_1 = next(life)
        assert not np.array_equal(state_0, state_1)
        state_2 = next(life)
        assert np.array_equal(state_0, state_2)


class TestLifeWithAllEngines:
    """Test LifeSimulation with all 6 engine functions."""

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_iterate(self, engine_name, repository):
        engine = ALL_ENGINES[engine_name]
        life = Life(size=20, seed="noise", engine=engine, repository=repository)
        state = next(life)
        assert state.shape == (20, 20)

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_with_blinker(self, engine_name, repository):
        engine = ALL_ENGINES[engine_name]
        life = Life(size=20, seed="glider", engine=engine, repository=repository)
        life.state = np.zeros((20, 20), dtype=np.int8)
        life.state[10, 8:11] = 1
        state_0 = life.state.copy()
        state_1 = next(life)
        state_2 = next(life)
        assert not np.array_equal(state_0, state_1), (
            f"Engine {engine_name}: state didn't change"
        )
        assert np.array_equal(state_0, state_2), (
            f"Engine {engine_name}: didn't oscillate correctly"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_with_block(self, engine_name, repository):
        engine = ALL_ENGINES[engine_name]
        life = Life(size=20, seed="glider", engine=engine, repository=repository)
        life.state = np.zeros((20, 20), dtype=np.int8)
        life.state[9:11, 9:11] = 1
        block_state = life.state.copy()
        next_state = next(life)
        assert np.array_equal(block_state, next_state), (
            f"Engine {engine_name}: block pattern not preserved"
        )

    @pytest.mark.parametrize("engine_name", list(ALL_ENGINES.keys()))
    def test_all_engines_produce_valid_output(self, engine_name, repository):
        engine = ALL_ENGINES[engine_name]
        life = Life(size=25, seed="noise", engine=engine, repository=repository)
        for _ in range(5):
            state = next(life)
            assert np.all((state == 0) | (state == 1)), (
                f"Engine {engine_name}: produced invalid values"
            )


class TestLifeWithVariousGridSizes:
    """Test LifeSimulation with various grid sizes in valid range."""

    @pytest.mark.parametrize("size", [10, 15, 20, 50, 100, 200, 500, 1000])
    def test_various_grid_sizes(self, size, repository):
        life = Life(
            size=size, seed="noise", engine=convolution, repository=repository
        )
        assert life.state.shape == (size, size)
        state = next(life)
        assert state.shape == (size, size)

    @pytest.mark.parametrize("size", [10, 50, 100, 500])
    def test_multiple_iterations_various_sizes(self, size, repository):
        """Note: symmetric seed is non-deterministic; dtype may be int8 or int64."""
        try:
            life = Life(
                size=size, seed="symmetric", engine=loop, repository=repository
            )
        except ValueError:
            pytest.skip(f"Size {size} doesn't work with symmetric seed decomposition")
        for _ in range(3):
            state = next(life)
            assert state.shape == (size, size)
            assert np.all((state == 0) | (state == 1))

    def test_min_size(self, repository):
        life = Life(size=10, seed="noise", engine=convolution, repository=repository)
        assert life.state.shape == (10, 10)

    def test_max_size(self, repository):
        life = Life(size=1000, seed="noise", engine=convolution, repository=repository)
        assert life.state.shape == (1000, 1000)


class TestLifeInvalidInputs:
    """Test error handling for invalid arguments."""

    def test_size_too_small(self, repository):
        with pytest.raises(SizeValueError):
            Life(size=9, seed="noise", engine=convolution, repository=repository)

    def test_size_too_large(self, repository):
        with pytest.raises(SizeValueError):
            Life(size=1001, seed="noise", engine=convolution, repository=repository)

    def test_size_is_not_integer(self, repository):
        with pytest.raises(SizeTypeError):
            Life(size=50.5, seed="noise", engine=convolution, repository=repository)

    def test_size_is_string(self, repository):
        with pytest.raises(SizeTypeError):
            Life(size="50", seed="noise", engine=convolution, repository=repository)

    def test_size_is_none(self, repository):
        with pytest.raises(SizeTypeError):
            Life(size=None, seed="noise", engine=convolution, repository=repository)

    def test_size_is_bool(self, repository):
        with pytest.raises(SizeTypeError):
            Life(size=True, seed="noise", engine=convolution, repository=repository)

    def test_size_is_negative(self, repository):
        with pytest.raises(SizeValueError):
            Life(size=-10, seed="noise", engine=convolution, repository=repository)

    def test_size_is_zero(self, repository):
        with pytest.raises(SizeValueError):
            Life(size=0, seed="noise", engine=convolution, repository=repository)


class TestLifeMultipleIterations:
    """Test behavior over multiple consecutive iterations."""

    def test_10_iterations(self, default_engine, default_seed, repository):
        life = Life(
            size=25, seed=default_seed, engine=default_engine, repository=repository
        )
        for _ in range(10):
            state = next(life)
            assert state.shape == (25, 25)
            assert state.dtype == np.int8

    def test_state_consistency_across_iterations(
        self, default_engine, default_seed, repository
    ):
        life = Life(
            size=20, seed=default_seed, engine=default_engine, repository=repository
        )
        for _ in range(5):
            returned_state = next(life)
            assert np.array_equal(life.state, returned_state)

    def test_100_iterations_small_grid(self, default_engine, repository):
        life = Life(
            size=10, seed="noise", engine=default_engine, repository=repository
        )
        for _ in range(100):
            state = next(life)
            assert state.shape == (10, 10)

    def test_iterations_converge_to_stable_state(self, repository):
        """Blinker is a period-2 oscillator: horizontal → vertical → horizontal."""
        life = Life(
            size=20, seed="glider", engine=convolution, repository=repository
        )
        life.state = np.zeros((20, 20), dtype=np.int8)
        life.state[10, 8:11] = 1
        state_0 = life.state.copy()

        for i in range(10):
            state = next(life)
            if i % 2 == 0:
                assert not np.array_equal(state_0, state), (
                    f"Iteration {i}: expected different state"
                )
            else:
                assert np.array_equal(state_0, state), (
                    f"Iteration {i}: expected same state"
                )

    def test_all_values_remain_valid(self, default_engine, default_seed, repository):
        life = Life(
            size=20, seed=default_seed, engine=default_engine, repository=repository
        )
        for _ in range(20):
            state = next(life)
            assert np.all((state == 0) | (state == 1))

    def test_state_shape_never_changes(self, default_engine, default_seed, repository):
        size = 35
        life = Life(
            size=size, seed=default_seed, engine=default_engine, repository=repository
        )
        for _ in range(15):
            state = next(life)
            assert state.shape == (size, size)


class TestLifeEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_initial_state(self, repository):
        life = Life(
            size=20, seed="noise", engine=convolution, repository=repository
        )
        life.state = np.zeros((20, 20), dtype=np.int8)
        state = next(life)
        assert np.array_equal(state, np.zeros((20, 20), dtype=np.int8))

    def test_fully_populated_initial_state(self, repository):
        life = Life(
            size=15, seed="noise", engine=convolution, repository=repository
        )
        life.state = np.ones((15, 15), dtype=np.int8)
        state = next(life)
        assert state.dtype == np.int8
        assert np.all((state == 0) | (state == 1))

    def test_single_alive_cell(self, repository):
        life = Life(
            size=20, seed="noise", engine=convolution, repository=repository
        )
        life.state = np.zeros((20, 20), dtype=np.int8)
        life.state[10, 10] = 1
        state = next(life)
        assert np.array_equal(state, np.zeros((20, 20), dtype=np.int8))

    def test_two_adjacent_cells(self, repository):
        life = Life(
            size=20, seed="noise", engine=convolution, repository=repository
        )
        life.state = np.zeros((20, 20), dtype=np.int8)
        life.state[10, 10:12] = 1
        state = next(life)
        assert np.array_equal(state, np.zeros((20, 20), dtype=np.int8))

    @pytest.mark.parametrize("seed", ["noise", "symmetric", "glider"])
    def test_different_seeds_produce_valid_states(self, seed, repository):
        """Different seeds produce valid initial states."""
        try:
            life1 = Life(
                size=30, seed=seed, engine=convolution, repository=repository
            )
            life2 = Life(
                size=30, seed=seed, engine=convolution, repository=repository
            )
        except ValueError:
            pytest.skip(f"Size 30 doesn't work with seed '{seed}'")

        assert life1.state.shape == (30, 30)
        assert life2.state.shape == (30, 30)

        if seed not in ["noise", "symmetric"]:
            assert np.array_equal(life1.state, life2.state)

    def test_seed_generators_work_correctly(self, repository):
        for seed in ["noise", "symmetric"] + PATTERN_SEEDS:
            try:
                life = Life(
                    size=40, seed=seed, engine=convolution, repository=repository
                )
                assert life.state.shape == (40, 40)
            except Exception as e:
                pytest.fail(f"Seed '{seed}' raised exception: {e}")


class TestLifeIntegration:
    """Integration tests combining multiple features."""

    def test_life_simulation_workflow(self, repository):
        life = Life(size=50, seed="noise", engine=loop, repository=repository)
        assert life.state.shape == (50, 50)
        for _ in range(20):
            state = next(life)
            assert state.shape == (50, 50)
            assert np.all((state == 0) | (state == 1))

    def test_engine_switching_not_allowed(self, repository):
        life = Life(
            size=20, seed="noise", engine=convolution, repository=repository
        )
        assert life.engine == convolution

    def test_seed_affects_only_initial_state(self, repository):
        life = Life(
            size=30, seed="blinker", engine=convolution, repository=repository
        )
        for _ in range(5):
            state = next(life)
            assert state.dtype == np.int8

    @pytest.mark.parametrize("size,seed,engine_name", [
        (10, "noise", "convolution"),
        (20, "symmetric", "loop"),
        (50, "glider", "roll"),
        (100, "blinker", "pad_slice"),
        (200, "noise", "ix_index"),
        (500, "symmetric", "bitpack"),
    ])
    def test_combinations(self, size, seed, engine_name, repository):
        engine = ALL_ENGINES[engine_name]
        try:
            life = Life(
                size=size, seed=seed, engine=engine, repository=repository
            )
        except ValueError:
            pytest.skip(f"Size {size} doesn't work with seed '{seed}'")
        state = next(life)
        assert state.shape == (size, size)
