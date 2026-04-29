"""Tests for seed generators and the _place_pattern helper."""
import numpy as np
import pytest

from life.infrastructure import CellsPatternRepository
from life.seeds._placement import place_pattern
from life.seeds.pattern_seed import PatternSeedGenerator
from life.seeds.scattered import ScatteredGenerator, scattered_count


@pytest.fixture(scope="module")
def repo() -> CellsPatternRepository:
    return CellsPatternRepository()


# ---------------------------------------------------------------------------
# place_pattern
# ---------------------------------------------------------------------------

class TestPlacePattern:
    def test_places_at_origin(self):
        grid = np.zeros((10, 10), dtype=np.int8)
        pattern = np.ones((2, 3), dtype=np.int8)
        place_pattern(grid, pattern, 0, 0)
        assert np.array_equal(grid[:2, :3], pattern)
        assert grid[2:, :].sum() == 0

    def test_places_at_offset(self):
        grid = np.zeros((10, 10), dtype=np.int8)
        pattern = np.ones((2, 2), dtype=np.int8)
        place_pattern(grid, pattern, 5, 6)
        assert np.array_equal(grid[5:7, 6:8], pattern)
        assert grid[:5, :].sum() == 0

    def test_clips_pattern_at_grid_boundary(self):
        grid = np.zeros((10, 10), dtype=np.int8)
        pattern = np.ones((4, 4), dtype=np.int8)
        # Placed so 2 rows and 2 cols fall outside the grid.
        place_pattern(grid, pattern, 8, 8)
        assert grid[8:, 8:].sum() == 4   # only 2×2 fits

    def test_does_not_clear_existing_cells(self):
        grid = np.ones((10, 10), dtype=np.int8)
        pattern = np.zeros((3, 3), dtype=np.int8)
        place_pattern(grid, pattern, 0, 0)
        # OR semantics: pattern zeros must not overwrite existing ones.
        assert grid.sum() == 100

    def test_returns_none(self):
        grid = np.zeros((5, 5), dtype=np.int8)
        result = place_pattern(grid, np.ones((2, 2), dtype=np.int8), 0, 0)
        assert result is None


# ---------------------------------------------------------------------------
# PatternSeedGenerator (uses place_pattern internally)
# ---------------------------------------------------------------------------

class TestPatternSeedGenerator:
    def test_top_left_placement(self, repo):
        gen = PatternSeedGenerator(repo)
        grid = gen(20, "blinker")
        assert grid[:1, :3].sum() == 3
        assert grid[1:, :].sum() == 0

    def test_grid_shape(self, repo):
        gen = PatternSeedGenerator(repo)
        grid = gen(50, "glider")
        assert grid.shape == (50, 50)

    def test_dtype(self, repo):
        gen = PatternSeedGenerator(repo)
        assert gen(20, "block").dtype == np.int8


# ---------------------------------------------------------------------------
# scattered_count
# ---------------------------------------------------------------------------

class TestScatteredCount:
    @pytest.mark.parametrize("size,expected", [
        (50, 1),
        (100, 5),
        (200, 20),
        (500, 125),
    ])
    def test_formula(self, size, expected):
        assert scattered_count(size) == expected

    def test_minimum_is_one(self):
        assert scattered_count(10) >= 1


# ---------------------------------------------------------------------------
# ScatteredGenerator
# ---------------------------------------------------------------------------

class TestScatteredGenerator:
    def test_output_shape(self, repo):
        gen = ScatteredGenerator(repo)
        grid = gen(100)
        assert grid.shape == (100, 100)

    def test_output_dtype(self, repo):
        gen = ScatteredGenerator(repo)
        assert gen(100).dtype == np.int8

    def test_has_alive_cells(self, repo):
        gen = ScatteredGenerator(repo)
        assert gen(100).sum() > 0

    def test_only_zero_and_one(self, repo):
        gen = ScatteredGenerator(repo)
        grid = gen(100)
        assert np.all((grid == 0) | (grid == 1))

    def test_reproducible_with_seed(self, repo):
        gen = ScatteredGenerator(repo)
        np.random.seed(42)
        g1 = gen(100)
        np.random.seed(42)
        g2 = gen(100)
        assert np.array_equal(g1, g2)

    def test_small_grid(self, repo):
        gen = ScatteredGenerator(repo)
        grid = gen(10)
        assert grid.shape == (10, 10)

    def test_large_grid(self, repo):
        gen = ScatteredGenerator(repo)
        grid = gen(500)
        assert grid.shape == (500, 500)

    def test_custom_count(self, repo):
        """count parameter overrides the default formula."""
        gen = ScatteredGenerator(repo)
        # With count=1 and a fixed seed, we know exactly one pattern is placed.
        np.random.seed(0)
        grid = gen(100, count=1)
        assert grid.sum() > 0

    def test_empty_repository_raises(self):
        class EmptyRepo:
            def list_names(self) -> list[str]: return []
            def load(self, name: str): raise KeyError(name)
            def contains(self, name: str) -> bool: return False

        gen = ScatteredGenerator(EmptyRepo())
        with pytest.raises(ValueError, match="non-empty"):
            gen(100)


# ---------------------------------------------------------------------------
# Integration: scattered appears in new_seed_generator
# ---------------------------------------------------------------------------

def test_scattered_available_via_factory(repo):
    from life.seeds import new_seed_generator
    grid = new_seed_generator(100, "scattered", repo)
    assert grid.shape == (100, 100)
    assert grid.dtype == np.int8
