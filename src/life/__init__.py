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

# Load development variables
envfile = "dev.env" if DEVELOP else ".env"
config: dict[str, str | None] = {**dotenv_values(dotenv_path=envfile)}

# Load logging configuration
fileConfig(fname="logging.conf")
logger: logging.Logger = logging.getLogger(name=__name__)

# Set logging level from config
if config.get("DEBUG"):
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.setLevel(logging.DEBUG)
