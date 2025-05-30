import logging
from logging.config import fileConfig
from typing import Callable, Iterator

from numpy import int8
from numpy.typing import NDArray
from dotenv import dotenv_values

# Relevant type aliases
State = NDArray[int8]
StateIterator = Iterator[State]
StateUpdater = Callable[[State], State]

DEVELOP = False

# load development variables
envfile = "dev.env" if DEVELOP else ".env"
config: dict[str, str | None] = {**dotenv_values(dotenv_path=envfile)}

# load logging configuration
fileConfig(fname="logging.conf")
logger: logging.Logger = logging.getLogger(name=__name__)

# Set logging level from config
if config.get("DEBUG"):
    logger.setLevel(logging.DEBUG)
    # Also set the root logger level for all modules
    logging.getLogger().setLevel(logging.DEBUG)
