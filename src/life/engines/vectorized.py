import numpy as np

from life.domain.rules import apply_rules
from life.domain.types import Grid


def vectorized(state: Grid) -> Grid:
    """
    Next state via np.roll on both axes with toroidal wrap boundary.

    Examples
    --------
        >>> import numpy as np
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=np.int8)
        >>> vectorized(state)
        array([[0, 0, 0],
               [1, 1, 1],
               [0, 0, 0]], dtype=int8)
    """
    neighbors = (
        np.roll(np.roll(state, -1, axis=0), -1, axis=1)  # top-left
        + np.roll(state, -1, axis=0)                      # top
        + np.roll(np.roll(state, -1, axis=0), 1, axis=1)  # top-right
        + np.roll(state, -1, axis=1)                      # left
        + np.roll(state, 1, axis=1)                       # right
        + np.roll(np.roll(state, 1, axis=0), -1, axis=1)  # bottom-left
        + np.roll(state, 1, axis=0)                       # bottom
        + np.roll(np.roll(state, 1, axis=0), 1, axis=1)   # bottom-right
    )
    return apply_rules(neighbors, state)
