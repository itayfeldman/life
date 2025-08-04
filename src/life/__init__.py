import logging
from logging.config import dictConfig
from typing import Callable, Iterator, Dict, Tuple

from dotenv import dotenv_values
import yaml
from numpy import int8
from numpy.typing import NDArray

# Relevant type aliases
type Config = Dict[str, str | None]
type ArrayShape = Tuple[int, int]
type State = NDArray[int8]
type StateIterator = Iterator[State]
type StateUpdater = Callable[[State], State]
type Patterns = Dict[str, State]

# Load project config
with open("config.yaml") as cfg:
    config: Config = yaml.safe_load(cfg)

# Load environment variables
env_file: str = "dev.env" if config["develop"] else ".env"
env_variables: Config = {**dotenv_values(dotenv_path=env_file)}

# Load logging config
with open("logging.yaml", "r") as cfg:
    logging_config: Config = yaml.safe_load(cfg)
dictConfig(logging_config)
logger: logging.Logger = logging.getLogger(name=__name__)

# Set logging level from env variables
root_logger = logging.getLogger()
for handler in root_logger.handlers:
    if isinstance(handler, logging.FileHandler):
        handler.setLevel(logging.DEBUG)
