from life.domain.types import GridUpdater
from life.engines.convolution import convolution
from life.engines.fast import fast
from life.engines.loop import loop
from life.engines.ultra_fast import ultra_fast
from life.engines.vectorized import vectorized
from life.engines.window import window

ENGINE_REGISTRY: dict[str, GridUpdater] = {
    "convolution": convolution,
    "fast": fast,
    "loop": loop,
    "ultra_fast": ultra_fast,
    "vectorized": vectorized,
    "window": window,
}

__all__ = [
    "convolution",
    "fast",
    "loop",
    "ultra_fast",
    "vectorized",
    "window",
    "ENGINE_REGISTRY",
]
