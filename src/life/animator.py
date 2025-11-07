import time
from typing import Optional, Tuple

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

from life.life import Life


class Animator:
    """
    Enhanced animator class for Conway's Game of Life with visual improvements.

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
    show_stats: bool, optional
        Whether to display statistics overlay (default: False).

    Returns
    -------
    animation.FuncAnimation
        The enhanced animation of the game of life.
    """

    def __init__(
        self,
        life: Life,
        cmap: str,
        interval: int,
        figsize: int,
        show_stats: bool = True,
    ) -> None:
        self.life: Life = life
        self.cmap: str = cmap
        self.interval: int = interval
        self.figsize: int = figsize
        self.show_stats: bool = show_stats

        # Statistics tracking
        self.generation: int = 0
        self.start_time: float = time.time()
        self.fps_counter: list = []
        self.last_frame_time: float = time.time()

    def _get_population_stats(self) -> Tuple[int, float]:
        """Calculate population and density statistics."""
        population = int(np.sum(self.life.state))
        total_cells = self.life.state.size
        density = population / total_cells * 100
        return population, density

    def _update_fps(self) -> float:
        """Update FPS counter and return current FPS."""
        current_time = time.time()
        if len(self.fps_counter) >= 10:
            self.fps_counter.pop(0)

        frame_time = current_time - self.last_frame_time
        if frame_time > 0:
            self.fps_counter.append(1.0 / frame_time)

        self.last_frame_time = current_time
        return float(np.mean(self.fps_counter)) if self.fps_counter else 0.0


    def __call__(self) -> animation.FuncAnimation:
        """Create and return the enhanced animation."""
        # Setup figure
        fig, ax = plt.subplots(figsize=(self.figsize, self.figsize))

        # Create enhanced image display
        im = ax.imshow(
            self.life.state,
            cmap=self.cmap,
            # interpolation="bilinear",
            vmin=0,
            vmax=1,
            alpha=1.0,
        )


        # Setup display mode
        if self.show_stats:
            ax.set_xticks([])
            ax.set_yticks([])
            title_text = ax.set_title("", color="white", fontsize=12, pad=20)

            # Stats text overlay
            stats_text = ax.text(
                0.02,
                0.98,
                "",
                transform=ax.transAxes,
                verticalalignment="top",
                fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.7),
                color="white",
            )
        else:
            plt.axis("off")
            stats_text = None
            title_text = None

        def update_frame(_):
            """Enhanced update function with statistics and effects."""
            # Update the image
            im.set_data(self.life.state)

            # Update statistics
            self.generation += 1
            population, density = self._get_population_stats()
            fps = self._update_fps()
            elapsed_time = time.time() - self.start_time

            # Update stats display if enabled
            if self.show_stats and stats_text:
                stats_str = (
                    f"Generation: {self.generation}\n"
                    f"Population: {population:,}\n"
                    f"Density: {density:.1f}%\n"
                    f"FPS: {fps:.1f}\n"
                    f"Time: {elapsed_time:.1f}s"
                )
                stats_text.set_text(stats_str)
                title_text.set_text(f"Conway's Game of Life - Gen: {self.generation}")

            return [im] + ([stats_text, title_text] if stats_text else [])

        return animation.FuncAnimation(
            fig=fig,
            func=update_frame,
            frames=self.life,
            interval=self.interval,
            cache_frame_data=False,
            blit=False if self.show_stats else True,
            repeat=True,
        )
