import matplotlib.animation as animation
import matplotlib.pyplot as plt

from life.life import Life


# TODO: Refactor this class to be more modular and testable. Consider separating the animation logic from the data handling logic. Consider using pygame library.
class Animator:
    """
    The animator class is a callable that returns an animation of the game of life.

    Parameters
    ----------
    life: Life
        An instance of the Life class that provides the state of the game of life.
    cmap: str
        The color map to use for the game of life board.
    interval: int
        The interval between frames in milliseconds.
    figsize: int
        The size of the figure for the game of life board.

    Returns
    -------
    animation.FuncAnimation
        The animation of the game of life.
    """

    def __init__(self, life: Life, cmap: str, interval: int, figsize: int) -> None:
        self.life: Life = life
        self.cmap: str = cmap
        self.interval: int = interval
        self.figsize: int = figsize

    def __call__(self) -> animation.FuncAnimation:
        fig, ax = plt.subplots(figsize=(self.figsize, self.figsize))
        # Display the initial state of the game.
        # self.life is an iterator. Calling next() on it advances the state.
        # We need the state *before* the first animation step for the initial display.
        im = ax.imshow(self.life.state, cmap=self.cmap, interpolation="nearest")
        plt.axis("off")

        return animation.FuncAnimation(
            fig=fig,
            func=lambda _: [im.set_data(self.life.state)],
            frames=self.life,
            interval=self.interval,
            cache_frame_data=False,
        )
