import numpy as np
from scipy.signal import convolve2d  # type: ignore[import-untyped]

from life.domain import Grid, apply_rules


def convolution(state: Grid) -> Grid:
    """
    Next state via scipy convolution with toroidal wrap boundary.

    Examples
    --------
        >>> import numpy as np
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=np.int8)
        >>> convolution(state)
        array([[0, 0, 0],
               [1, 1, 1],
               [0, 0, 0]], dtype=int8)
    """
    neighbors = (
        convolve2d(state, np.ones((3, 3)), mode="same", boundary="wrap") - state
    )
    return apply_rules(neighbors, state)
