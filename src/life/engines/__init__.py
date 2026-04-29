from life.domain.types import GridUpdater
from life.engines.bitpack import bitpack
from life.engines.convolution import convolution
from life.engines.ix_index import ix_index
from life.engines.loop import loop
from life.engines.pad_slice import pad_slice
from life.engines.roll import roll

ENGINE_REGISTRY: dict[str, GridUpdater] = {
    "bitpack": bitpack,
    "convolution": convolution,
    "loop": loop,
    "pad_slice": pad_slice,
    "ix_index": ix_index,
    "roll": roll,
}

__all__ = [
    "bitpack",
    "convolution",
    "ix_index",
    "loop",
    "pad_slice",
    "roll",
    "ENGINE_REGISTRY",
]
