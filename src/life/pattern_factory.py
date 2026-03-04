import os
from typing import Callable, Dict
from pathlib import Path

import numpy as np
from importlib import import_module
import inspect

from life import logger, State


Patterns = Dict[str, State]


def load_pattern_from_cells(file_path: Path) -> State:
    """
    Load a pattern from a cells file.

    cells format:
    - Lines starting with '!' are comments
    - 'O' represents live cells
    - '.' represents dead cells
    - Each line represents a row
    """
    lines: list[str] = []
    with open(file_path, "r") as f:
        for line in f:
            if line and not line.startswith("!"):
                lines.append(line.rstrip())

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
    return pattern


def load_pattern_from_ndarray(file_path: Path) -> State | None:
    module = import_module(str(file_path))
    for name, value in inspect.getmembers(module):
        if isinstance(value, np.ndarray):
            return value
    return None


def load_objects_from_pattern_dir(
    pattern_dir: str,
    suffix: str,
    patterns: Patterns,
    predicate: Callable[[object], bool] | None = None,
) -> Patterns:
    pattern_dir_path = Path(pattern_dir)

    for file_path in pattern_dir_path.rglob("*." + suffix):
        try:
            pattern = file_types[suffix](file_path)
            if predicate is None or predicate(pattern):
                patterns[str(file_path.stem)] = pattern
                logger.debug(f"Loaded pattern from {file_path}")
        except Exception as e:
            logger.error(f"Error loading pattern from {file_path}: {e}")
    return patterns


def get_patterns(
    pattern_dir_name: str,
    suffixes: list[str],
    predicate: Callable[[object], bool] = lambda obj: isinstance(obj, np.ndarray),
) -> Patterns:
    patterns: Patterns = {}
    pattern_dir: str = os.path.join(os.path.dirname(__file__), pattern_dir_name)
    for suffix in suffixes:
        patterns = load_objects_from_pattern_dir(
            pattern_dir, suffix, patterns, predicate
        )
    return patterns


file_types = {
    "cells": load_pattern_from_cells,
    "py": load_pattern_from_ndarray,
}


patterns = get_patterns(pattern_dir_name="patterns", suffixes=["cells"])
