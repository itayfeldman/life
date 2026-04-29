import itertools

import numpy as np

from life.domain.rules import apply_rules
from life.domain.types import Grid


def roll(state: Grid) -> Grid:
    """
    Next state via np.roll sliding window with toroidal wrap boundary.

    Examples
    --------
        >>> import numpy as np
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=np.int8)
        >>> roll(state)
        array([[0, 0, 0],
               [1, 1, 1],
               [0, 0, 0]], dtype=int8)
    """
    neighbors = np.add.reduce(
        [
            np.roll(np.roll(state, i, 0), j, 1)
            for i, j in itertools.product([-1, 0, 1], repeat=2)
            if (i, j) != (0, 0)
        ]
    )
    return apply_rules(neighbors, state)
