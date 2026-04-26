from __future__ import annotations

from typing import Iterator, Protocol, runtime_checkable

from life.domain.types import Grid


@runtime_checkable
class GridUpdater(Protocol):
    def __call__(self, state: Grid) -> Grid: ...


@runtime_checkable
class PatternRepository(Protocol):
    def list_names(self) -> list[str]: ...
    def load(self, name: str) -> Grid: ...
    def contains(self, name: str) -> bool: ...


@runtime_checkable
class Simulation(Protocol):
    state: Grid

    def __iter__(self) -> Iterator[Grid]: ...
    def __next__(self) -> Grid: ...


@runtime_checkable
class Visualizer(Protocol):
    def __call__(self) -> object: ...
