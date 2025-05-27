import logging
from logging import Logger
from logging.config import fileConfig
from typing import Iterator

from numpy import int8
from numpy.typing import NDArray

from dotenv import dotenv_values

LifeState = NDArray[int8]
LifeIterator = Iterator[LifeState]

DEVELOP = False


# load development variables
envfile = "dev.env" if DEVELOP else ".env"
config: dict[str, str | None] = {**dotenv_values(dotenv_path=envfile)}

# load logging configuration
fileConfig(fname="logging.conf")
logger: Logger = logging.getLogger(name=__name__)

# Set logging level from config
if config.get("DEBUG"):
    logger.setLevel(logging.DEBUG)
    # Also set the root logger level for all modules
    logging.getLogger().setLevel(logging.DEBUG)
