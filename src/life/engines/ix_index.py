import numpy as np

from life.domain import Grid, apply_rules


def ix_index(state: Grid) -> Grid:
    """
    Next state via advanced indexing with pre-computed wrap indices.

    Minimises memory allocation; uses np.ix_ for toroidal boundary.

    Examples
    --------
        >>> import numpy as np
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=np.int8)
        >>> ix_index(state)
        array([[0, 0, 0],
               [1, 1, 1],
               [0, 0, 0]], dtype=int8)
    """
    rows, cols = state.shape
    up = np.arange(-1, rows - 1) % rows
    down = np.arange(1, rows + 1) % rows
    left = np.arange(-1, cols - 1) % cols
    right = np.arange(1, cols + 1) % cols
    col_idx = np.arange(cols)
    row_idx = np.arange(rows)

    neighbors = (
        state[np.ix_(up, left)]
        + state[np.ix_(up, col_idx)]
        + state[np.ix_(up, right)]
        + state[np.ix_(row_idx, left)]
        + state[np.ix_(row_idx, right)]
        + state[np.ix_(down, left)]
        + state[np.ix_(down, col_idx)]
        + state[np.ix_(down, right)]
    )
    return apply_rules(neighbors, state)
