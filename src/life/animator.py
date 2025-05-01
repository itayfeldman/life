import matplotlib.animation as animation
import matplotlib.pyplot as plt

from life import Life


class Animator:
    """
    The animator class is a callable that returns an animation of the game of life.

    Parameters
    ----------
    frames : Life
        An instance of the Life class that provides the state of the game of life.
    cmap : str
        The color map to use for the game of life board.
    interval : int
        The interval between frames in milliseconds.
    figsize : int
        The size of the figure for the game of life board.

    Returns
    -------
    animation.FuncAnimation
        The animation of the game of life.
    """

    def __init__(self, frames: Life, cmap: str, interval: int, figsize: int):
        self.frames: Life = frames
        self.cmap: str = cmap
        self.interval: int = interval
        self.figsize: int = figsize

    def __call__(self) -> animation.FuncAnimation:
        fig, ax = plt.subplots(figsize=(self.figsize, self.figsize))
        im = ax.imshow(self.frames.state, cmap=self.cmap, interpolation="nearest")
        plt.axis("off")

        return animation.FuncAnimation(
            fig=fig,
            func=lambda _: [im.set_data(self.frames.state)],
            frames=self.frames,
            interval=self.interval,
            cache_frame_data=False,
        )
