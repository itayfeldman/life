from typing import Callable, Iterator

import numpy as np

from life.exceptions import validate_args
from life.seeds import new_seed_generator

LifeState = np.ndarray
LifeIterator = Iterator[LifeState]


class Life:
    """
    The life class is an iterator that returns the next state of the game of life.

    Parameters
    ----------
    size: int
        The size of the game of life board.
        Value must be greater than 10 and less than 1000 (1 million cells).
    seed: str {'noise', 'symmetric', 'glider', 'pulsar', 'cross', 'bracketpulser', 'pentadecathlon'}
        The seed to use for the game of life board.
        * "noise" - Randomly generated board.
        * "symmetric" - symmetric board.
        Patterns:
        * "glider" - Empty board with a glider.
        * "cross" - Board with a single cross (size=10).
        * "pulsar" - Board with a single pulsar (size=15).
        * "bracketpulser" - Board with a single bracket pulser (size=15).
        * "pentadecathlon" - Period-15 Pattern (size=16).
    func: Callable
        The function to use to calculate the next state of the game of life board.
    """

    def __init__(self, size: int, seed: str, func: Callable) -> None:
        validate_args(size, seed)
        self.state: LifeState = new_seed_generator(size=size, seed=seed)
        self.func: Callable = func

    def __iter__(self) -> LifeIterator:
        return self

    def __next__(self) -> LifeState:
        """
        Advances the simulation by one step and returns the new state.

        Returns
        -------
        LifeState
            The updated state after applying the life rules.
        """
        self.state = self.func(self.state)
        return self.state
