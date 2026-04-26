from pathlib import Path

import numpy as np

from life import logger
from life.domain.types import Grid


class CellsPatternRepository:
    """
    Lazy-loading repository for .cells format pattern files.

    Patterns are loaded from disk on first access, not at import time.
    The default pattern directory is src/life/patterns/.
    """

    def __init__(self, pattern_dir: Path | None = None) -> None:
        if pattern_dir is None:
            pattern_dir = Path(__file__).resolve().parent.parent / "patterns"
        self._pattern_dir = pattern_dir
        self._cache: dict[str, Grid] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        for file_path in self._pattern_dir.rglob("*.cells"):
            try:
                self._cache[file_path.stem] = self._parse_cells(file_path)
                logger.debug("Loaded pattern %s from %s", file_path.stem, file_path)
            except Exception as e:
                logger.error("Error loading pattern from %s: %s", file_path, e)

    def _parse_cells(self, file_path: Path) -> Grid:
        lines: list[str] = []
        with open(file_path, "r") as f:
            for line in f:
                if line and not line.startswith("!"):
                    lines.append(line.rstrip())
        if not lines:
            raise ValueError(f"No pattern data found in {file_path}")
        max_width = max(len(line) for line in lines)
        pattern = np.zeros((len(lines), max_width), dtype=np.int8)
        for i, line in enumerate(lines):
            row = np.frombuffer(line.encode(), dtype=np.uint8)
            pattern[i, : len(row)] = row == ord("O")
        return pattern

    def list_names(self) -> list[str]:
        self._ensure_loaded()
        return list(self._cache.keys())

    def load(self, name: str) -> Grid:
        self._ensure_loaded()
        if name not in self._cache:
            raise KeyError(
                f"Pattern '{name}' not found. Available: {self.list_names()}"
            )
        return self._cache[name]

    def contains(self, name: str) -> bool:
        self._ensure_loaded()
        return name in self._cache
