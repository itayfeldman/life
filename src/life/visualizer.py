"""
Enhanced visualization module for Conway's Game of Life.
"""
from typing import Optional, Tuple, List
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from life.life import Life
from life import State


class EnhancedVisualizer:
    """
    Enhanced visualizer with statistics, controls, and better graphics.
    
    Features:
    - Generation counter
    - Population statistics
    - Grid lines option
    - Better color schemes
    - Pause/resume functionality
    - Export capabilities
    """
    
    def __init__(
        self,
        life: Life,
        cmap: str = "binary",
        interval: int = 350,
        figsize: Tuple[int, int] = (10, 8),
        show_grid: bool = False,
        show_stats: bool = True,
        title: Optional[str] = None
    ) -> None:
        self.life = life
        self.cmap = cmap
        self.interval = interval
        self.figsize = figsize
        self.show_grid = show_grid
        self.show_stats = show_stats
        self.title = title or "Conway's Game of Life"
        
        # Statistics tracking
        self.generation = 0
        self.population_history: List[int] = []
        self.is_paused = False
        
        # Animation objects
        self.fig = None
        self.ax_main = None
        self.ax_stats = None
        self.im = None
        self.text_gen = None
        self.text_pop = None
        self.line_pop = None
        
    def setup_figure(self) -> None:
        """Set up the figure with main display and statistics panel."""
        if self.show_stats:
            self.fig, (self.ax_main, self.ax_stats) = plt.subplots(
                1, 2, figsize=self.figsize, gridspec_kw={'width_ratios': [3, 1]}
            )
        else:
            self.fig, self.ax_main = plt.subplots(figsize=self.figsize)
        
        # Main game display
        self.im = self.ax_main.imshow(
            self.life.state, 
            cmap=self.cmap, 
            interpolation="nearest"
        )
        self.ax_main.set_title(self.title, fontsize=14, fontweight='bold')
        self.ax_main.axis("off")
        
        # Add grid if requested
        if self.show_grid:
            self._add_grid()
        
        # Statistics panel
        if self.show_stats:
            self._setup_stats_panel()
        
        # Add keyboard controls
        self.fig.canvas.mpl_connect('key_press_event', self._on_key_press)
        
        plt.tight_layout()
    
    def _add_grid(self) -> None:
        """Add grid lines to the main display."""
        rows, cols = self.life.state.shape
        
        # Add grid lines
        for i in range(rows + 1):
            self.ax_main.axhline(i - 0.5, color='gray', linewidth=0.5, alpha=0.3)
        for j in range(cols + 1):
            self.ax_main.axvline(j - 0.5, color='gray', linewidth=0.5, alpha=0.3)
    
    def _setup_stats_panel(self) -> None:
        """Set up the statistics panel."""
        self.ax_stats.set_title("Statistics", fontweight='bold')
        
        # Text displays for current stats
        self.text_gen = self.ax_stats.text(
            0.1, 0.9, f"Generation: {self.generation}", 
            transform=self.ax_stats.transAxes, fontsize=12
        )
        
        current_pop = np.sum(self.life.state)
        self.population_history.append(current_pop)
        self.text_pop = self.ax_stats.text(
            0.1, 0.8, f"Population: {current_pop}", 
            transform=self.ax_stats.transAxes, fontsize=12
        )
        
        # Population history plot
        self.line_pop, = self.ax_stats.plot(
            self.population_history, 'b-', linewidth=2, alpha=0.7
        )
        self.ax_stats.set_xlabel("Generation")
        self.ax_stats.set_ylabel("Population")
        self.ax_stats.grid(True, alpha=0.3)
        
        # Controls text
        controls_text = "Controls:\\nSPACE: Pause/Resume\\nS: Save frame\\nQ: Quit"
        self.ax_stats.text(
            0.1, 0.3, controls_text, 
            transform=self.ax_stats.transAxes, fontsize=10,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.5)
        )
    
    def _on_key_press(self, event) -> None:
        """Handle keyboard events."""
        if event.key == ' ':  # Space bar to pause/resume
            self.is_paused = not self.is_paused
            status = "PAUSED" if self.is_paused else "RUNNING"
            print(f"Animation {status}")
        elif event.key == 's':  # Save current frame
            self.save_frame()
        elif event.key == 'q':  # Quit
            plt.close(self.fig)
    
    def update_frame(self, frame_num) -> List:
        """Update function for animation."""
        if self.is_paused:
            return [self.im]
        
        # Get next state
        try:
            next_state = next(self.life)
            self.generation += 1
            current_pop = np.sum(next_state)
            self.population_history.append(current_pop)
            
            # Update main display
            self.im.set_data(next_state)
            
            # Update statistics
            if self.show_stats:
                self.text_gen.set_text(f"Generation: {self.generation}")
                self.text_pop.set_text(f"Population: {current_pop}")
                
                # Update population plot
                self.line_pop.set_data(range(len(self.population_history)), self.population_history)
                self.ax_stats.relim()
                self.ax_stats.autoscale_view()
            
            return [self.im, self.text_gen, self.text_pop, self.line_pop] if self.show_stats else [self.im]
            
        except StopIteration:
            # Animation finished
            return [self.im]
    
    def animate(self, frames: Optional[int] = None) -> animation.FuncAnimation:
        """Create and return the animation."""
        self.setup_figure()
        
        anim = animation.FuncAnimation(
            fig=self.fig,
            func=self.update_frame,
            frames=frames,
            interval=self.interval,
            blit=False,  # Disable blitting for better compatibility with stats
            cache_frame_data=False,
            repeat=False
        )
        
        return anim
    
    def save_frame(self, filename: Optional[str] = None) -> None:
        """Save the current frame as an image."""
        if filename is None:
            filename = f"life_generation_{self.generation:04d}.png"
        
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"Saved frame to {filename}")
    
    def export_animation(self, filename: str, frames: int = 100, fps: int = 10) -> None:
        """Export animation as a video file."""
        anim = self.animate(frames=frames)
        
        # Save as MP4 (requires ffmpeg)
        try:
            anim.save(filename, writer='ffmpeg', fps=fps, bitrate=1800)
            print(f"Animation saved to {filename}")
        except Exception as e:
            print(f"Error saving animation: {e}")
            print("Make sure ffmpeg is installed for video export")
    
    def get_statistics(self) -> dict:
        """Get current statistics."""
        return {
            'generation': self.generation,
            'current_population': np.sum(self.life.state),
            'population_history': self.population_history.copy(),
            'max_population': max(self.population_history) if self.population_history else 0,
            'min_population': min(self.population_history) if self.population_history else 0,
            'avg_population': np.mean(self.population_history) if self.population_history else 0
        }


class PatternAnalyzer:
    """
    Analyze patterns in the Game of Life for interesting behaviors.
    """
    
    @staticmethod
    def detect_oscillation(states: List[State], max_period: int = 50) -> Optional[int]:
        """
        Detect if the pattern is oscillating and return the period.
        
        Args:
            states: List of consecutive states
            max_period: Maximum period to check for
            
        Returns:
            Period of oscillation, or None if no oscillation detected
        """
        if len(states) < 2 * max_period:
            return None
        
        # Check for periods from 1 to max_period
        for period in range(1, max_period + 1):
            if len(states) < 2 * period:
                continue
                
            # Check if pattern repeats with this period
            is_periodic = True
            for i in range(period):
                state1 = states[-(period + i)]
                state2 = states[-(i + 1)]
                if not np.array_equal(state1, state2):
                    is_periodic = False
                    break
            
            if is_periodic:
                return period
        
        return None
    
    @staticmethod
    def detect_stability(states: List[State], min_stable_gens: int = 10) -> bool:
        """
        Detect if the pattern has reached a stable state.
        
        Args:
            states: List of consecutive states
            min_stable_gens: Minimum generations to consider stable
            
        Returns:
            True if pattern is stable
        """
        if len(states) < min_stable_gens:
            return False
        
        # Check if last min_stable_gens states are identical
        reference_state = states[-1]
        for i in range(1, min_stable_gens + 1):
            if not np.array_equal(states[-i], reference_state):
                return False
        
        return True
    
    @staticmethod
    def calculate_center_of_mass(state: State) -> Tuple[float, float]:
        """Calculate the center of mass of living cells."""
        rows, cols = np.where(state == 1)
        if len(rows) == 0:
            return (0.0, 0.0)
        
        center_row = np.mean(rows)
        center_col = np.mean(cols)
        return (center_row, center_col)
    
    @staticmethod
    def detect_movement(states: List[State]) -> Optional[Tuple[float, float]]:
        """
        Detect if pattern is moving and return velocity.
        
        Returns:
            (velocity_row, velocity_col) or None if not moving
        """
        if len(states) < 10:
            return None
        
        centers = [PatternAnalyzer.calculate_center_of_mass(state) for state in states[-10:]]
        
        # Calculate average velocity over last 10 generations
        velocities_row = []
        velocities_col = []
        
        for i in range(1, len(centers)):
            dr = centers[i][0] - centers[i-1][0]
            dc = centers[i][1] - centers[i-1][1]
            velocities_row.append(dr)
            velocities_col.append(dc)
        
        avg_vel_row = np.mean(velocities_row)
        avg_vel_col = np.mean(velocities_col)
        
        # Consider it moving if average velocity is significant
        if abs(avg_vel_row) > 0.1 or abs(avg_vel_col) > 0.1:
            return (avg_vel_row, avg_vel_col)
        
        return None

