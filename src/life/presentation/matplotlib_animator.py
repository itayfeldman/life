from typing import Any

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.artist import Artist

from life.domain.protocols import Simulation


class MatplotlibAnimator:
    """
    Renders a Game of Life simulation as a matplotlib animation.

    Depends on the Simulation protocol — not on any concrete simulation class.

    Parameters
    ----------
    simulation : Simulation
        Any object satisfying the Simulation protocol.
    cmap : str
        Matplotlib colormap name.
    interval : int
        Milliseconds between frames.
    figsize : int
        Figure width and height in inches.
    """

    def __init__(
        self,
        simulation: Simulation,
        cmap: str,
        interval: int,
        figsize: int,
    ) -> None:
        self.simulation = simulation
        self.cmap = cmap
        self.interval = interval
        self.figsize = figsize

    def __call__(self) -> animation.FuncAnimation:
        fig, ax = plt.subplots(figsize=(self.figsize, self.figsize))
        im = ax.imshow(
            self.simulation.state, cmap=self.cmap, interpolation="nearest"
        )
        plt.axis("off")

        def _update(_: Any) -> list[Artist]:
            im.set_data(self.simulation.state)
            return [im]

        return animation.FuncAnimation(
            fig=fig,
            func=_update,
            frames=self.simulation,
            interval=self.interval,
            cache_frame_data=False,
        )
