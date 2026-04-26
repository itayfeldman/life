import numpy as np

from life.domain.types import Grid


def apply_rules(neighbors: Grid, state: Grid) -> Grid:
    """
    Conway's Game of Life rules.

    Birth: a dead cell with exactly 3 live neighbors becomes alive.
    Survival: a live cell with 2 or 3 live neighbors survives.
    Death: all other cells die or remain dead.
    """
    return np.asarray(
        (neighbors == 3) | ((state == 1) & (neighbors == 2)), dtype=np.int8
    )
