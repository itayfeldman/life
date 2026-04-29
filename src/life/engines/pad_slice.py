import numpy as np

from life.domain.rules import apply_rules
from life.domain.types import Grid


def pad_slice(state: Grid) -> Grid:
    """
    Next state via NumPy padding and slicing with toroidal wrap boundary.

    Cache-friendly neighbor counting without convolution or roll operations.

    Examples
    --------
        >>> import numpy as np
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=np.int8)
        >>> pad_slice(state)
        array([[0, 0, 0],
               [1, 1, 1],
               [0, 0, 0]], dtype=int8)
    """
    padded = np.pad(state, pad_width=1, mode="wrap")
    neighbors = (
        padded[:-2, :-2]   # top-left
        + padded[:-2, 1:-1]  # top
        + padded[:-2, 2:]    # top-right
        + padded[1:-1, :-2]  # left
        + padded[1:-1, 2:]   # right
        + padded[2:, :-2]    # bottom-left
        + padded[2:, 1:-1]   # bottom
        + padded[2:, 2:]     # bottom-right
    )
    return apply_rules(neighbors, state)
