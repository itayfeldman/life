from typing import Callable

from life import LifeState, LifeIterator
from life.exceptions import validate_args
from life.seeds import new_seed_generator


class Life:
    """
    The life class is an iterator that returns the next state of the game of life.

    Parameters
    ----------
    size: int
        The size of the game of life board.
        Value must be greater than 10 and less than 1000 (1 million cells).
    seed:
        The seed to use for the game of life board.
        * "noise" - Randomly generated board.
        * "symmetric" - symmetric board.
        * <pattern name>
    func: Callable
        The function to use to calculate the next state of the game of life board.
    """

    def __init__(
        self, size: int, seed: str, func: Callable[[LifeState], LifeState]
    ) -> None:
        validate_args(size, seed)
        self.state: LifeState = new_seed_generator(size=size, seed=seed)
        self.func: Callable[[LifeState], LifeState] = func

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
