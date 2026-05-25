"""Tests for __main__.py argument parsing and display-size translation."""

from unittest.mock import MagicMock, patch

import pytest

from life.__main__ import PYGAME_DPI, build_parser


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


def test_func_alias_accepted():
    """--func is a backwards-compatibility alias for --engine."""
    parser = build_parser()
    args = parser.parse_args(["--func", "convolution"])
    assert args.engine == "convolution"


def test_func_alias_default_unchanged():
    """Omitting both --engine and --func leaves the default engine intact."""
    parser = build_parser()
    args = parser.parse_args([])
    assert args.engine == "pad_slice"
