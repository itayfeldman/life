import itertools
from typing import List

from scipy.signal import convolve2d
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

LifeState = np.ndarray


def window(state: LifeState) -> LifeState:
    """
    Calculates the next state of the Game of Life based on the current state.

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
        >>> window(state)
        array([[0, 0, 0], [1, 1, 1], [0, 0, 0]])
    """
    neighbor_count = sum(
        np.roll(np.roll(state, i, 0), j, 1)
        for i, j in itertools.product([-1, 0, 1], repeat=2)
        if (i, j) != (0, 0)
    )
    return (neighbor_count == 3) | ((state == 1) & (neighbor_count == 2))


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
    return (neighbor_count == 3) | ((state == 1) & (neighbor_count == 2))


def loop(state: LifeState) -> LifeState:
    """
    Calculates the next state of the Game of Life based on the current state using a loop.

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
        >>> state = [[0, 1, 0], [0, 1, 0], [0, 1, 0]]
        >>> loop(state)
        [[0, 0, 0], [1, 1, 1], [0, 0, 0]]
    """
    next_state = np.zeros_like(state)

    for i, j in itertools.product(range(state.shape[0]), range(state.shape[1])):
        n1 = 0 if (i == 0 or j == 0) else state[i - 1][j - 1]
        n2 = 0 if i == 0 else state[i - 1][j]
        n3 = 0 if (i == 0 or j == (state.shape[1] - 1)) else state[i - 1][j + 1]
        n4 = 0 if j == 0 else state[i][j - 1]
        n5 = 0 if (j == (state.shape[1] - 1)) else state[i][j + 1]
        n6 = 0 if ((i == (state.shape[0] - 1)) or (j == 0)) else state[i + 1][j - 1]
        n7 = 0 if (i == (state.shape[0] - 1)) else state[i + 1][j]
        n8 = (
            0
            if ((i == (state.shape[0] - 1)) or (j == (state.shape[1] - 1)))
            else state[i + 1][j + 1]
        )
        neighbor_count = n1 + n2 + n3 + n4 + n5 + n6 + n7 + n8

        if neighbor_count < 4 and (neighbor_count + state[i][j]) > 2:
            next_state[i][j] = 1

    return next_state
