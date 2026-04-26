import numpy as np

from life.domain.protocols import PatternRepository
from life.domain.types import Grid


class PatternSeedGenerator:
    """Places a named pattern at the top-left corner of a zeroed grid."""

    def __init__(self, repository: PatternRepository) -> None:
        self._repo = repository

    def __call__(self, size: int, name: str) -> Grid:
        state = np.zeros((size, size), dtype=np.int8)
        pattern = self._repo.load(name)
        n, m = pattern.shape
        state[:n, :m] = pattern
        return state
