from life import logger
from life.domain.protocols import PatternRepository
from life.domain.types import Grid, GridIterator, GridUpdater
from life.seeds import new_seed_generator
from life.validation.exceptions import validate_args


class LifeSimulation:
    """
    Stateful Game of Life iterator.

    Depends only on domain protocols — no direct infrastructure imports.

    Parameters
    ----------
    size : int
        Grid dimension (size × size). Must be between 10 and 1000.
    seed : str
        Initial state strategy: "noise", "symmetric", or a named pattern.
    engine : GridUpdater
        Function that computes the next grid state from the current one.
    repository : PatternRepository
        Source of named patterns for seed generation and validation.
    """

    def __init__(
        self,
        size: int,
        seed: str,
        engine: GridUpdater,
        repository: PatternRepository,
    ) -> None:
        logger.debug(
            "Initializing LifeSimulation: size=%s, seed=%s", size, seed
        )
        validate_args(size=size, seed=seed, repository=repository)
        self.state: Grid = new_seed_generator(
            size=size, seed=seed, repository=repository
        )
        self.engine: GridUpdater = engine
        logger.debug("LifeSimulation initialised")

    def __iter__(self) -> GridIterator:
        return self

    def __next__(self) -> Grid:
        self.state = self.engine(self.state)
        return self.state
