from typing import Callable

from life.domain.protocols import Simulation, Visualizer
from life.presentation.matplotlib_animator import MatplotlibAnimator
from life.presentation.pygame_visualizer import PygameVisualizer

# Converts display-size inches to pygame window pixels (100 px per inch).
PYGAME_DPI = 100

FrontendFactory = Callable[[Simulation, int, int, str], Visualizer]


def _build_pygame(
    simulation: Simulation, interval: int, display_size: int, cmap: str
) -> Visualizer:
    return PygameVisualizer(
        simulation=simulation,
        interval=interval,
        window_size=display_size * PYGAME_DPI,
    )


def _build_matplotlib(
    simulation: Simulation, interval: int, display_size: int, cmap: str
) -> Visualizer:
    return MatplotlibAnimator(
        simulation=simulation,
        cmap=cmap,
        interval=interval,
        figsize=display_size,
    )


FRONTEND_REGISTRY: dict[str, FrontendFactory] = {
    "pygame": _build_pygame,
    "matplotlib": _build_matplotlib,
}

__all__ = [
    "MatplotlibAnimator",
    "PygameVisualizer",
    "FRONTEND_REGISTRY",
    "PYGAME_DPI",
]
