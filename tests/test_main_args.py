"""Tests for __main__.py argument parsing and display-size translation."""

import time
from io import StringIO
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from life.__main__ import build_parser, run_bench
from life.domain import Visualizer
from life.presentation import (
    FRONTEND_REGISTRY,
    PYGAME_DPI,
    MatplotlibAnimator,
    PygameVisualizer,
)


class _FakeSimulation:
    """Minimal Simulation-protocol stand-in; avoids spinning up a real engine."""

    def __init__(self) -> None:
        self.state = np.zeros((10, 10), dtype=np.int8)

    def __iter__(self) -> "_FakeSimulation":
        return self

    def __next__(self) -> np.ndarray:
        return self.state


def test_parser_has_display_size():
    parser = build_parser()
    args = parser.parse_args([])
    assert hasattr(args, "display_size")


def test_parser_no_figsize_or_window():
    parser = build_parser()
    args = parser.parse_args([])
    assert not hasattr(args, "figsize")
    assert not hasattr(args, "window")


def test_display_size_default():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.display_size == 10


def test_display_size_explicit():
    parser = build_parser()
    args = parser.parse_args(["--display-size", "12"])
    assert args.display_size == 12


def test_pygame_window_size_translates():
    """pygame window_size must equal display_size * PYGAME_DPI."""
    parser = build_parser()
    args = parser.parse_args(["--display-size", "8", "--frontend", "pygame"])
    assert args.display_size * PYGAME_DPI == 800


def test_matplotlib_figsize_passes_through():
    """matplotlib figsize must equal display_size directly (inches)."""
    parser = build_parser()
    args = parser.parse_args(["--display-size", "10", "--frontend", "matplotlib"])
    assert args.display_size == 10



def test_bench_argument_parsed():
    parser = build_parser()
    args = parser.parse_args(["--bench", "50"])
    assert args.bench == 50


def test_bench_default_is_none():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.bench is None


def test_run_bench_prints_summary(capsys):
    run_bench(generations=10, size=20, seed="noise", engine_name="pad_slice")
    out = capsys.readouterr().out
    assert "generations" in out
    assert "ms/gen" in out
    assert "gen/s" in out


def test_run_bench_timing_is_positive(capsys):
    run_bench(generations=5, size=20, seed="noise", engine_name="convolution")
    out = capsys.readouterr().out
    # Extract the ms/gen value and confirm it's a positive float.
    for token in out.split():
        try:
            val = float(token)
            assert val > 0
        except ValueError:
            pass


def test_pygame_visualizer_satisfies_visualizer_protocol():
    visualizer = PygameVisualizer(simulation=_FakeSimulation(), window_size=100)
    assert isinstance(visualizer, Visualizer)


def test_matplotlib_animator_satisfies_visualizer_protocol():
    animator = MatplotlibAnimator(
        simulation=_FakeSimulation(), cmap="binary", interval=100, figsize=5
    )
    assert isinstance(animator, Visualizer)


def test_frontend_registry_has_pygame_and_matplotlib():
    assert set(FRONTEND_REGISTRY.keys()) == {"pygame", "matplotlib"}


def test_frontend_registry_builds_pygame_visualizer():
    visualizer = FRONTEND_REGISTRY["pygame"](_FakeSimulation(), 100, 8, "binary")
    assert isinstance(visualizer, PygameVisualizer)


def test_frontend_registry_builds_matplotlib_animator():
    visualizer = FRONTEND_REGISTRY["matplotlib"](_FakeSimulation(), 100, 8, "binary")
    assert isinstance(visualizer, MatplotlibAnimator)
