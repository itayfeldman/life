"""Tests for CellsPatternRepository."""
import numpy as np
import pytest

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


def test_lazy_loading_does_not_load_at_import():
    """A fresh instance must not load patterns until first accessed."""
    fresh = CellsPatternRepository()
    assert not fresh._loaded
    fresh.list_names()
    assert fresh._loaded


def test_list_names_stable_across_calls(repo):
    assert repo.list_names() == repo.list_names()


def test_load_pattern_has_correct_shape(repo):
    """Loaded grids must be 2-dimensional."""
    for name in repo.list_names():
        pattern = repo.load(name)
        assert pattern.ndim == 2, f"Pattern '{name}' is not 2D"
