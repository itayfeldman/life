import logging
from logging.config import fileConfig
from typing import Callable, Iterator
from pathlib import Path

from numpy import int8
from numpy.typing import NDArray
from dotenv import dotenv_values

# Relevant type aliases
ConfigFile = dict[str, str | None]
State = NDArray[int8]
StateIterator = Iterator[State]
StateUpdater = Callable[[State], State]

# Load development variables
DEVELOP = False
envfile = "dev.env" if DEVELOP else ".env"
config: ConfigFile = {**dotenv_values(dotenv_path=envfile)}

# Load logging configuration
_project_root = Path(__file__).resolve().parent.parent.parent
_logging_conf = _project_root / "logging.conf"
if _logging_conf.exists():
    fileConfig(fname=str(_logging_conf))
else:
    logging.basicConfig(level=logging.INFO)

logger: logging.Logger = logging.getLogger(name=__name__)

# Set logging level from config
if config.get("DEBUG"):
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.setLevel(logging.DEBUG)
