import numpy as np

from life.domain import Grid


class NoiseGenerator:
    def __call__(self, size: int) -> Grid:
        return np.random.randint(2, size=(size, size), dtype=np.int8)
