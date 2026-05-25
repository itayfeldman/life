import re
from pathlib import Path

import numpy as np

from life import logger
from life.domain.types import Grid

_RLE_TOKEN = re.compile(r"(\d*)(b|o|\$|!)")


class CellsPatternRepository:
    """
    Lazy-loading repository for .rle format pattern files.

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
        for file_path in self._pattern_dir.rglob("*.rle"):
            try:
                stem = file_path.stem
                if stem in self._cache:
                    logger.warning(
                        "Pattern name collision: '%s' already loaded; skipping %s",
                        stem, file_path,
                    )
                    continue
                self._cache[stem] = self._parse_rle(file_path)
                logger.debug("Loaded pattern %s from %s", stem, file_path)
            except Exception as e:
                logger.error("Error loading pattern from %s: %s", file_path, e)
        self._loaded = True

    def _parse_rle(self, file_path: Path) -> Grid:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Strip comment lines (#) and find the header line (x = ..., y = ...)
        lines = text.splitlines()
        data_lines: list[str] = []
        width = height = None
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if width is None and stripped.startswith("x"):
                m = re.search(r"x\s*=\s*(\d+)", stripped)
                n = re.search(r"y\s*=\s*(\d+)", stripped)
                if not m or not n:
                    raise ValueError(f"Missing x/y in header: {stripped!r}")
                width, height = int(m.group(1)), int(n.group(1))
                continue
            data_lines.append(stripped)

        if width is None or height is None:
            raise ValueError(f"No header found in {file_path}")

        body = "".join(data_lines)
        pattern = np.zeros((height, width), dtype=np.int8)
        row = col = 0
        for m in _RLE_TOKEN.finditer(body):
            count = int(m.group(1)) if m.group(1) else 1
            tag = m.group(2)
            if tag == "o":
                pattern[row, col : col + count] = 1
                col += count
            elif tag == "b":
                col += count
            elif tag == "$":
                row += count
                col = 0
            elif tag == "!":
                break

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
