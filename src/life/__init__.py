import logging
from logging.config import dictConfig
from typing import Callable, Iterator, Dict

from dotenv import dotenv_values
import yaml
from numpy import int8
from numpy.typing import NDArray

# Relevant type aliases
ConfigDict = Dict[str, str | None]
State = NDArray[int8]
StateIterator = Iterator[State]
StateUpdater = Callable[[State], State]
Patterns = Dict[str, State]

# Load config
with open("config.yaml") as f:
    config: ConfigDict = yaml.safe_load(f)

# Load development variables
env_file: str = "dev.env" if config["develop"] else ".env"
env_variables: ConfigDict = {**dotenv_values(dotenv_path=env_file)}

# Load logging config
with open("logging.yaml", "r") as f:
    logging_config: ConfigDict = yaml.safe_load(f)
dictConfig(logging_config)
logger: logging.Logger = logging.getLogger(name=__name__)

# Set logging level from env variables
root_logger = logging.getLogger()
for handler in root_logger.handlers:
    if isinstance(handler, logging.FileHandler):
        handler.setLevel(logging.DEBUG)
