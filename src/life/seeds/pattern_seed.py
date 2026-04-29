import numpy as np

from life.domain.protocols import PatternRepository
from life.domain.types import Grid
from life.seeds._placement import place_pattern


class PatternSeedGenerator:
    """Places a named pattern at the top-left corner of a zeroed grid."""

    def __init__(self, repository: PatternRepository) -> None:
        self._repo = repository

    def __call__(self, size: int, name: str) -> Grid:
        state = np.zeros((size, size), dtype=np.int8)
        place_pattern(state, self._repo.load(name), 0, 0)
        return state
