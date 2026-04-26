from typing import Any

from life.domain.protocols import PatternRepository
from life.domain.types import BUILT_IN_SEEDS

MINSIZE = 10
MAXSIZE = 1000

SIZE_ERROR_MSG = f"The size parameter must be between {MINSIZE} and {MAXSIZE}."
TYPE_ERROR_MSG = "The size parameter must be an integer."


class LifeParamsError(Exception):
    def __init__(self, msg: str = "") -> None:
        super().__init__(msg)


class SizeTypeError(LifeParamsError):
    def __init__(self, size: Any) -> None:
        super().__init__(f"{TYPE_ERROR_MSG} Got {size}.")


class SizeValueError(LifeParamsError):
    def __init__(self, size: int) -> None:
        super().__init__(f"{SIZE_ERROR_MSG} Got {size}.")


class SeedValueError(LifeParamsError):
    def __init__(self, seed: str, available: list[str]) -> None:
        options = sorted(BUILT_IN_SEEDS) + sorted(available)
        super().__init__(
            f"The seed parameter must be one of: {options}. Got '{seed}'."
        )


def validate_args(size: Any, seed: Any, repository: PatternRepository) -> None:
    if not isinstance(size, int):
        raise SizeTypeError(size)
    if size < MINSIZE or size > MAXSIZE:
        raise SizeValueError(size)
    if seed not in BUILT_IN_SEEDS and not repository.contains(seed):
        raise SeedValueError(seed, repository.list_names())
