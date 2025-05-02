"""Exception objects for error handling."""

from typing import Any

from oscillators_factory import oscillators

MINSIZE = 10
MAXSIZE = 1000

SIZE_ERROR_MSG = f"""
The size parameter must between {MINSIZE} and {MAXSIZE}.
"""

TYPE_ERROR_MSG = f"""
The size parameter must be an integer.
"""

SEED_ERROR_MSG = f"""
The seed parameter must be one of the following: {[k for k in oscillators.keys()]}.
"""


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
    def __init__(self, seed: str) -> None:
        super().__init__(f"{SEED_ERROR_MSG} Got {seed}.")


def validate_args(size: Any, seed: Any) -> None:
    if not isinstance(size, int):
        raise SizeTypeError(size)
    if size < MINSIZE or size > MAXSIZE:
        raise SizeValueError(size)
    if seed not in [
        "noise",
        "symmetric",
        "Glider",
        "Cross",
        "Pulsar",
        "Bracketpulsar",
        "Pentadecathlon",
    ]:
        raise SeedValueError(seed)
