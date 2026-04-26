import logging
from logging.config import fileConfig
from pathlib import Path

from dotenv import dotenv_values

ConfigFile = dict[str, str | None]

config: ConfigFile = {**dotenv_values(dotenv_path=".env")}

_project_root = Path(__file__).resolve().parent.parent.parent
_logging_conf = _project_root / "logging.conf"
if _logging_conf.exists():
    fileConfig(fname=str(_logging_conf))
else:
    logging.basicConfig(level=logging.INFO)

logger: logging.Logger = logging.getLogger(name=__name__)

if config.get("DEBUG"):
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler.setLevel(logging.DEBUG)
