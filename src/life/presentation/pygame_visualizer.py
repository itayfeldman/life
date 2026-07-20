import numpy as np
import pygame

from life.domain import Simulation

_DEAD = (10, 10, 10)
_ALIVE = (200, 230, 200)


class PygameVisualizer:
    """
    Interactive pygame frontend for a Life simulation.

    Controls
    --------
    Space       pause / resume
    Right arrow step one generation while paused
    +/-         speed up / slow down (interval ±25 ms, clamped to 25–2000)
    Q / Escape  quit
    """

    def __init__(
        self,
        simulation: Simulation,
        interval: int = 100,
        window_size: int = 800,
        alive_color: tuple[int, int, int] = _ALIVE,
        dead_color: tuple[int, int, int] = _DEAD,
    ) -> None:
        self._sim = simulation
        self._interval = interval
        self._window_size = window_size
        self._alive = np.array(alive_color, dtype=np.uint8)
        self._dead = np.array(dead_color, dtype=np.uint8)

    def __call__(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((self._window_size, self._window_size))
        pygame.display.set_caption("Conway's Game of Life")
        clock = pygame.time.Clock()

        grid_size = self._sim.state.shape[0]
        cell_px = max(1, self._window_size // grid_size)
        render_size = grid_size * cell_px

        # Pre-allocate a surface for the raw cell grid (1 px per cell).
        cell_surface = pygame.Surface((grid_size, grid_size))

        paused = False
        last_tick = pygame.time.get_ticks()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        pygame.quit()
                        return
                    elif event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_RIGHT and paused:
                        next(self._sim)
                        last_tick = pygame.time.get_ticks()
                    elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                        self._interval = max(25, self._interval - 25)
                    elif event.key == pygame.K_MINUS:
                        self._interval = min(2000, self._interval + 25)

            now = pygame.time.get_ticks()
            if not paused and (now - last_tick) >= self._interval:
                next(self._sim)
                last_tick = now

            self._render(screen, cell_surface, self._sim.state, cell_px, render_size)
            pygame.display.flip()
            clock.tick(60)

    def _render(
        self,
        screen: pygame.Surface,
        cell_surface: pygame.Surface,
        state: np.ndarray,
        cell_px: int,
        render_size: int,
    ) -> None:
        # surfarray uses column-major (x=col, y=row), so transpose state.
        pixels = np.where(state.T[:, :, np.newaxis], self._alive, self._dead)
        pygame.surfarray.blit_array(cell_surface, pixels)

        if cell_px > 1:
            scaled = pygame.transform.scale(cell_surface, (render_size, render_size))
            screen.blit(scaled, (0, 0))
        else:
            screen.blit(cell_surface, (0, 0))
