from life import State, StateIterator, StateUpdater, logger
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

    def __init__(self, size: int, seed: str, func: StateUpdater) -> None:
        logger.debug(
            f"Initializing Life with size={size}, seed={seed}, func={func.__name__}"
        )
        validate_args(size, seed)
        self.state: State = new_seed_generator(size=size, seed=seed)
        logger.debug("Seed generated for %s pattern", seed)
        self.func: StateUpdater = func
        logger.debug("Life initialization complete")

    def __iter__(self) -> StateIterator:
        return self

    def __next__(self) -> State:
        """
        Advances the simulation by one step and returns the new state.

        Returns
        -------
        State
            The updated state after applying the life rules.
        """
        self.state = self.func(self.state)
        return self.state
