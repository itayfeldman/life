import numpy as np

from life.domain import Grid, PatternRepository
from life.seeds._placement import place_pattern


def scattered_count(size: int) -> int:
    """Number of patterns to scatter for a given grid size."""
    return max(1, size * size // 2000)


class ScatteredGenerator:
    """
    Seeds a grid with N randomly-chosen patterns at random positions.

    Patterns are OR-ed in so overlaps merge rather than erase.
    Count defaults to scattered_count(size) but can be overridden.
    """

    def __init__(self, repository: PatternRepository) -> None:
        self._repo = repository

    def __call__(self, size: int, count: int | None = None) -> Grid:
        if count is None:
            count = scattered_count(size)
        names = self._repo.list_names()
        if not names:
            raise ValueError("ScatteredGenerator requires a non-empty pattern repository")
        grid = np.zeros((size, size), dtype=np.int8)
        for _ in range(count):
            name = names[np.random.randint(len(names))]
            pattern = self._repo.load(name)
            n, m = pattern.shape
            row = np.random.randint(0, max(1, size - n + 1))
            col = np.random.randint(0, max(1, size - m + 1))
            place_pattern(grid, pattern, row, col)
        return grid
