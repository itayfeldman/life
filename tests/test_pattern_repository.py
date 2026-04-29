"""Tests for CellsPatternRepository."""
import logging
import numpy as np
import pytest
from pathlib import Path

from life.infrastructure import CellsPatternRepository


@pytest.fixture(scope="module")
def repo() -> CellsPatternRepository:
    return CellsPatternRepository()


def test_list_names_returns_known_patterns(repo):
    names = repo.list_names()
    assert isinstance(names, list)
    assert len(names) > 0
    assert "glider" in names
    assert "blinker" in names


def test_load_returns_valid_grid(repo):
    pattern = repo.load("glider")
    assert isinstance(pattern, np.ndarray)
    assert pattern.dtype == np.int8
    assert np.all((pattern == 0) | (pattern == 1))


def test_contains_known_pattern(repo):
    assert repo.contains("glider") is True
    assert repo.contains("blinker") is True


def test_contains_unknown_pattern(repo):
    assert repo.contains("__nonexistent_pattern__") is False


def test_load_raises_on_unknown_name(repo):
    with pytest.raises(KeyError, match="not found"):
        repo.load("__nonexistent_pattern__")


def test_lazy_loading_does_not_load_at_import(tmp_path):
    """Patterns dir is not read until the first public method call."""
    accessed = []
    original_rglob = Path.rglob

    def tracking_rglob(self, pattern):
        accessed.append(self)
        return original_rglob(self, pattern)

    import unittest.mock as mock
    with mock.patch.object(Path, "rglob", tracking_rglob):
        fresh = CellsPatternRepository(tmp_path)
        assert accessed == [], "rglob called before any public method"
        fresh.list_names()
        assert accessed != [], "rglob not called after list_names()"


def test_malformed_cells_file_does_not_raise(tmp_path, caplog):
    """A file that fails to parse is skipped; no exception escapes."""
    bad = tmp_path / "bad.cells"
    bad.write_text("! comment\n\x00\xff\n", encoding="latin-1")
    with caplog.at_level(logging.ERROR, logger="life"):
        repo = CellsPatternRepository(tmp_path)
        names = repo.list_names()
    assert "bad" not in names


def test_stem_collision_logs_warning(tmp_path, caplog):
    """Two .cells files with the same stem in different subdirs produce a warning."""
    sub1 = tmp_path / "a"
    sub2 = tmp_path / "b"
    sub1.mkdir()
    sub2.mkdir()
    (sub1 / "glider.cells").write_text("OOO\n", encoding="utf-8")
    (sub2 / "glider.cells").write_text("O\nO\n", encoding="utf-8")
    with caplog.at_level(logging.WARNING, logger="life"):
        repo = CellsPatternRepository(tmp_path)
        repo.list_names()
    assert any("glider" in r.message for r in caplog.records)


def test_list_names_stable_across_calls(repo):
    assert repo.list_names() == repo.list_names()


def test_load_pattern_has_correct_shape(repo):
    """Loaded grids must be 2-dimensional."""
    for name in repo.list_names():
        pattern = repo.load(name)
        assert pattern.ndim == 2, f"Pattern '{name}' is not 2D"
