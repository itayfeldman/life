from typing import Callable, Iterator

from numpy import int8
from numpy.typing import NDArray

CellState = int8
Grid = NDArray[CellState]
GridUpdater = Callable[[Grid], Grid]
GridIterator = Iterator[Grid]

BUILT_IN_SEEDS: frozenset[str] = frozenset({"noise", "symmetric", "scattered"})
