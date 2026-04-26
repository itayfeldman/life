import numpy as np

from life.domain.rules import apply_rules
from life.domain.types import Grid


def loop(state: Grid) -> Grid:
    """
    Next state via pure-Python double loop with toroidal wrap boundary.

    Examples
    --------
        >>> import numpy as np
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=np.int8)
        >>> loop(state)
        array([[0, 0, 0],
               [1, 1, 1],
               [0, 0, 0]], dtype=int8)
    """
    rows, cols = state.shape
    neighbors = np.zeros_like(state, dtype=np.int8)

    for r in range(rows):
        for c in range(cols):
            count = 0
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    if di == 0 and dj == 0:
                        continue
                    ni = (r + di + rows) % rows
                    nj = (c + dj + cols) % cols
                    count += state[ni, nj]
            neighbors[r, c] = count

    return apply_rules(neighbors, state)
