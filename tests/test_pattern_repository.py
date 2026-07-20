"""Tests for RlePatternRepository (RLE format)."""
import logging
import numpy as np
import pytest
from pathlib import Path

from life.infrastructure import RlePatternRepository


@pytest.fixture(scope="module")
def repo() -> RlePatternRepository:
    return RlePatternRepository()


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
        fresh = RlePatternRepository(tmp_path)
        assert accessed == [], "rglob called before any public method"
        fresh.list_names()
        assert accessed != [], "rglob not called after list_names()"


def test_malformed_cells_file_does_not_raise(tmp_path, caplog):
    """A file that fails to parse is skipped; no exception escapes."""
    bad = tmp_path / "bad.rle"
    bad.write_text("not valid rle content\n", encoding="utf-8")
    with caplog.at_level(logging.ERROR, logger="life"):
        repo = RlePatternRepository(tmp_path)
        names = repo.list_names()
    assert "bad" not in names


def test_stem_collision_logs_warning(tmp_path, caplog):
    """Two .rle files with the same stem in different subdirs produce a warning."""
    sub1 = tmp_path / "a"
    sub2 = tmp_path / "b"
    sub1.mkdir()
    sub2.mkdir()
    rle = "x = 3, y = 1, rule = B3/S23\n3o!\n"
    (sub1 / "glider.rle").write_text(rle, encoding="utf-8")
    (sub2 / "glider.rle").write_text(rle, encoding="utf-8")
    with caplog.at_level(logging.WARNING, logger="life"):
        repo = RlePatternRepository(tmp_path)
        repo.list_names()
    assert any("glider" in r.message for r in caplog.records)


def test_list_names_stable_across_calls(repo):
    assert repo.list_names() == repo.list_names()


def test_load_pattern_has_correct_shape(repo):
    """Loaded grids must be 2-dimensional."""
    for name in repo.list_names():
        pattern = repo.load(name)
        assert pattern.ndim == 2, f"Pattern '{name}' is not 2D"


def test_rle_glider_shape_and_cells(repo):
    """Glider RLE must decode to the canonical 3x3 live-cell arrangement."""
    g = repo.load("glider")
    assert g.shape == (3, 3)
    expected = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]], dtype=np.int8)
    assert np.array_equal(g, expected), f"Glider decoded incorrectly:\n{g}"


def test_rle_blinker_shape_and_cells(repo):
    """Blinker RLE must decode to 1x3."""
    b = repo.load("blinker")
    assert b.shape == (1, 3)
    assert np.array_equal(b, np.ones((1, 3), dtype=np.int8))


def test_rle_malformed_does_not_raise(tmp_path, caplog):
    """An .rle file that fails to parse is skipped; no exception escapes."""
    bad = tmp_path / "bad.rle"
    bad.write_text("not valid rle content\n", encoding="utf-8")
    with caplog.at_level(logging.ERROR, logger="life"):
        r = RlePatternRepository(tmp_path)
        names = r.list_names()
    assert "bad" not in names


def test_rle_stem_collision_logs_warning(tmp_path, caplog):
    """Two .rle files with the same stem in different subdirs produce a warning."""
    sub1 = tmp_path / "a"
    sub2 = tmp_path / "b"
    sub1.mkdir()
    sub2.mkdir()
    rle_body = "#N glider\nx = 3, y = 3, rule = B3/S23\nb2o$2bo$3o!\n"
    (sub1 / "glider.rle").write_text(rle_body, encoding="utf-8")
    (sub2 / "glider.rle").write_text(rle_body, encoding="utf-8")
    with caplog.at_level(logging.WARNING, logger="life"):
        r = RlePatternRepository(tmp_path)
        r.list_names()
    assert any("glider" in rec.message for rec in caplog.records)
