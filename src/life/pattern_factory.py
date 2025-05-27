import os
from typing import Callable, Dict
from pathlib import Path

import numpy as np

from life import logger, LifeState

Patterns = Dict[str, LifeState]


def load_pattern_from_cells(file_path: Path) -> LifeState:
    """
    Load a pattern from a .cells file.

    .cells format:
    - Lines starting with '!' are comments
    - 'O' represents live cells
    - '.' represents dead cells
    - Each line represents a row
    """
    lines: list[str] = []
    with open(file_path, "r") as f:
        for line in f:
            if line and not line.startswith("!"):
                line = line.rstrip()
                lines.append(line)

    if not lines:
        raise ValueError(f"No pattern data found in {file_path}")

    # Determine dimensions
    max_width = max(len(line) for line in lines)
    height = len(lines)

    # Create pattern array
    pattern = np.zeros((height, max_width), dtype=np.int8)

    for i, line in enumerate(lines):
        for j, char in enumerate(line):
            if char == "O":
                pattern[i, j] = 1
            # Everything else (including '.') is treated as 0 (dead cell)

    return pattern


def load_objects_from_pattern_dir(
    pattern_dir: str, filter: Callable[[object], bool] | None = None
) -> Patterns:
    """
    Load patterns from .cells files in a pattern_dir and all subdirectories
    """
    result: Patterns = {}
    pattern_dir_path = Path(pattern_dir)

    # Use rglob to recursively find all .cells files
    for file_path in pattern_dir_path.rglob("*.cells"):
        try:
            pattern_name = str(file_path.name[:-6])
            pattern = load_pattern_from_cells(file_path)
            if filter is None or filter(pattern):
                result[pattern_name] = pattern
                logger.debug(f"Loaded pattern '{pattern_name}' from {file_path}")
        except Exception as e:
            logger.error(f"Error loading pattern from {file_path}: {e}")

    return result


def get_patterns() -> Patterns:
    pattern_dir = os.path.join(os.path.dirname(__file__), "patterns")
    return load_objects_from_pattern_dir(
        pattern_dir,
        lambda obj: isinstance(obj, np.ndarray),
    )


patterns = get_patterns()
