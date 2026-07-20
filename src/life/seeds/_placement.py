import numpy as np

from life.domain import Grid


def place_pattern(grid: Grid, pattern: Grid, row: int, col: int) -> None:
    """OR a pattern into grid at (row, col), clipping at grid boundaries."""
    n, m = pattern.shape
    r_end = min(row + n, grid.shape[0])
    c_end = min(col + m, grid.shape[1])
    p_rows = r_end - row
    p_cols = c_end - col
    grid[row:r_end, col:c_end] = np.bitwise_or(
        grid[row:r_end, col:c_end], pattern[:p_rows, :p_cols]
    )
