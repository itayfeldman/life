import matplotlib.animation as animation
import matplotlib.pyplot as plt
from typing import Optional

from life.life import Life


class Animator:
    """
    Animator for Conway's Game of Life.

    Parameters
    ----------
    life : Life
        An instance of the Life class that provides the state of the game of life.
    cmap : str
        The matplotlib color map name to use for the game of life board.
    interval : int
        The interval between frames in milliseconds.
    figsize : int
        The size of the figure for the game of life board.
    show_axis : bool, optional
        Whether to display axis ticks and labels (default: False).

    Methods
    -------
    __call__() -> animation.FuncAnimation
        Returns the animation object.
    """

    def __init__(self, life: Life, cmap: str, interval: int, figsize: int) -> None:
        self.life = life
        self.cmap = cmap
        self.interval = interval
        self.figsize = figsize
        self._anim: Optional[animation.FuncAnimation] = None

    def __call__(self) -> animation.FuncAnimation:
        """
        Create and return the animation.
        Additional kwargs are passed to FuncAnimation.
        """
        fig, ax = plt.subplots(figsize=(self.figsize, self.figsize))
        im = ax.imshow(self.life.state, cmap=self.cmap, interpolation="nearest")
        plt.axis("off")

        def update():
            im.set_data(self.life.state)
            return [im]

        self._anim = animation.FuncAnimation(
            fig=fig,
            func=update,
            frames=self.life,
            interval=self.interval,
            cache_frame_data=False,
        )
        return self._anim
