import itertools

import numpy as np
from scipy.signal import convolve2d

from life import LifeState


def convolution(state: LifeState) -> LifeState:
    """
    Calculates the next state of the Game of Life based on the current state using convolution.

    Parameters
    ----------
    state : LifeState
        The current state of the Game of Life.

    Returns
    -------
    LifeState
        The next state of the Game of Life.

    Examples
    --------
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]])
        >>> convolution(state)
        array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])
    """
    neighbor_count = (
        convolve2d(state, np.ones((3, 3)), mode="same", boundary="wrap") - state
    )
    return np.asarray(
        (neighbor_count == 3) | ((state == 1) & (neighbor_count == 2)), dtype=np.int8
    )


def loop(state: LifeState) -> LifeState:
    """
    Calculates the next state of the Game of Life based on the current state using a loop.
    This version correctly implements wrapping boundary conditions.

    Parameters
    ----------
    state : LifeState
        The current state of the Game of Life.

    Returns
    -------
    LifeState
        The next state of the Game of Life.

    Examples
    --------
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]])
        >>> loop(state)
        array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])
    """
    rows, cols = state.shape
    next_state = np.zeros_like(state)

    for r in range(rows):
        for c in range(cols):
            neighbor_count = 0
            # Iterate over all 8 neighbors
            for i_offset in range(-1, 2):
                for j_offset in range(-1, 2):
                    if i_offset == 0 and j_offset == 0:
                        continue  # Skip the cell itself

                    # Apply wrapping for neighbors
                    # (r + i_offset + rows) % rows ensures positive result before modulo
                    ni, nj = (r + i_offset + rows) % rows, (c + j_offset + cols) % cols
                    neighbor_count += state[ni, nj]

            # Apply Game of Life rules
            if state[r, c] == 1:  # If cell is alive
                if neighbor_count == 2 or neighbor_count == 3:
                    next_state[r, c] = 1
                # else: it dies (already 0 in next_state)
            else:  # If cell is dead
                if neighbor_count == 3:
                    next_state[r, c] = 1
                # else: it stays dead (already 0 in next_state)
    return next_state


def window(state: LifeState) -> LifeState:
    """
    Calculates the next state of the Game of Life based on the current state.

    Parameters
    ----------
    state: LifeState
        The current state of the Game of Life.

    Returns
    -------
    LifeState
        The next state of the Game of Life.

    Examples
    --------
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]])
        >>> window(state)
        array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])
    """
    neighbor_count = sum(
        np.roll(np.roll(state, i, 0), j, 1)
        for i, j in itertools.product([-1, 0, 1], repeat=2)
        if (i, j) != (0, 0)
    )
    return np.asarray(
        (neighbor_count == 3) | ((state == 1) & (neighbor_count == 2)), dtype=np.int8
    )


def fast_neighbors(state: LifeState) -> LifeState:
    """
    Ultra-fast neighbor counting using NumPy slicing and padding.

    This method uses array slicing to count neighbors without convolution
    or rolling operations, making it very cache-friendly and fast.

    Parameters
    ----------
    state : LifeState
        The current state of the Game of Life.

    Returns
    -------
    LifeState
        The next state of the Game of Life.

    Examples
    --------
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]])
        >>> fast_neighbors(state)
        array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])
    """
    # Pad the array with zeros to handle edge cases
    padded = np.pad(state, pad_width=1, mode="wrap")

    # Count neighbors using slicing - much faster than loops or convolution
    neighbors = (
        padded[:-2, :-2]  # top-left
        + padded[:-2, 1:-1]  # top
        + padded[:-2, 2:]  # top-right
        + padded[1:-1, :-2]  # left
        # Skip center cell
        + padded[1:-1, 2:]  # right
        + padded[2:, :-2]  # bottom-left
        + padded[2:, 1:-1]  # bottom
        + padded[2:, 2:]  # bottom-right
    )

    # Apply Conway's Game of Life rules
    return np.asarray(
        (neighbors == 3) | ((state == 1) & (neighbors == 2)), dtype=np.int8
    )


def ultra_fast_neighbors(state: LifeState) -> LifeState:
    """
    Even faster version using pre-allocated arrays and in-place operations.

    This minimizes memory allocation and copying for maximum performance.

    Parameters
    ----------
    state : LifeState
        The current state of the Game of Life.

    Returns
    -------
    LifeState
        The next state of the Game of Life.

    Examples
    --------
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]])
        >>> ultra_fast_neighbors(state)
        array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])
    """
    rows, cols = state.shape

    # Use wrapping indices for boundary conditions
    up = np.arange(-1, rows - 1) % rows
    down = np.arange(1, rows + 1) % rows
    left = np.arange(-1, cols - 1) % cols
    right = np.arange(1, cols + 1) % cols

    # Count neighbors using advanced indexing
    neighbors = (
        state[np.ix_(up, left)]  # top-left
        + state[np.ix_(up, np.arange(cols))]  # top
        + state[np.ix_(up, right)]  # top-right
        + state[np.ix_(np.arange(rows), left)]  # left
        + state[np.ix_(np.arange(rows), right)]  # right
        + state[np.ix_(down, left)]  # bottom-left
        + state[np.ix_(down, np.arange(cols))]  # bottom
        + state[np.ix_(down, right)]  # bottom-right
    )

    # Apply rules
    return np.asarray(
        (neighbors == 3) | ((state == 1) & (neighbors == 2)), dtype=np.int8
    )


def vectorized_neighbors(state: LifeState) -> LifeState:
    """
    Vectorized approach using np.roll for wrapping boundaries.
    Often the fastest for most grid sizes.

    Parameters
    ----------
    state : LifeState
        The current state of the Game of Life.

    Returns
    -------
    LifeState
        The next state of the Game of Life.

    Examples
    --------
        >>> state = np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]])
        >>> vectorized_neighbors(state)
        array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])
    """
    # Pre-compute all 8 neighbor shifts
    neighbors = (
        np.roll(np.roll(state, -1, axis=0), -1, axis=1)  # top-left
        + np.roll(state, -1, axis=0)  # top
        + np.roll(np.roll(state, -1, axis=0), 1, axis=1)  # top-right
        + np.roll(state, -1, axis=1)  # left
        + np.roll(state, 1, axis=1)  # right
        + np.roll(np.roll(state, 1, axis=0), -1, axis=1)  # bottom-left
        + np.roll(state, 1, axis=0)  # bottom
        + np.roll(np.roll(state, 1, axis=0), 1, axis=1)  # bottom-right
    )

    # Apply Conway's rules
    return np.asarray(
        (neighbors == 3) | ((state == 1) & (neighbors == 2)), dtype=np.int8
    )
