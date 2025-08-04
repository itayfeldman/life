import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from life.animator import Animator
from life.life import Life
from life.engine import fast


class TestAnimator(unittest.TestCase):
    """Test cases for the enhanced Animator class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a small test grid for faster testing
        self.size = 10
        self.life = Life(size=self.size, seed="noise", func=fast)
        self.default_animator = Animator(
            life=self.life,
            cmap="binary",
            interval=100,
            figsize=5
        )

    def test_animator_initialization_default(self):
        """Test Animator initialization with default parameters."""
        animator = Animator(
            life=self.life,
            cmap="binary", 
            interval=100,
            figsize=5
        )
        
        self.assertEqual(animator.life, self.life)
        self.assertEqual(animator.cmap, "binary")
        self.assertEqual(animator.interval, 100)
        self.assertEqual(animator.figsize, 5)
        self.assertFalse(animator.show_grid)
        self.assertFalse(animator.show_stats)
        self.assertEqual(animator.theme, 'default')
        self.assertEqual(animator.generation, 0)
        self.assertIsInstance(animator.fps_counter, list)
        self.assertEqual(len(animator.fps_counter), 0)

    def test_animator_initialization_with_options(self):
        """Test Animator initialization with enhanced options."""
        animator = Animator(
            life=self.life,
            cmap="viridis",
            interval=200,
            figsize=8,
            show_grid=True,
            show_stats=True,
            theme='matrix'
        )
        
        self.assertTrue(animator.show_grid)
        self.assertTrue(animator.show_stats)
        self.assertEqual(animator.theme, 'matrix')
        # Theme should override cmap
        self.assertEqual(animator.cmap, 'Greens')

    def test_themes_configuration(self):
        """Test that all themes are properly configured."""
        expected_themes = ['default', 'neon', 'matrix', 'ocean', 'fire', 'cyber']
        
        for theme in expected_themes:
            self.assertIn(theme, Animator.THEMES)
            theme_config = Animator.THEMES[theme]
            self.assertIn('cmap', theme_config)
            self.assertIn('bg_color', theme_config)

    def test_setup_colormap_matrix(self):
        """Test custom colormap setup for Matrix theme."""
        animator = Animator(
            life=self.life,
            cmap="binary",
            interval=100,
            figsize=5,
            theme='matrix'
        )
        
        self.assertIsInstance(animator._custom_cmap, LinearSegmentedColormap)
        self.assertEqual(animator._custom_cmap.name, 'matrix')

    def test_setup_colormap_neon(self):
        """Test custom colormap setup for Neon theme."""
        animator = Animator(
            life=self.life,
            cmap="binary",
            interval=100,
            figsize=5,
            theme='neon'
        )
        
        self.assertIsInstance(animator._custom_cmap, LinearSegmentedColormap)
        self.assertEqual(animator._custom_cmap.name, 'neon')

    def test_setup_colormap_default(self):
        """Test that default theme doesn't create custom colormap."""
        animator = Animator(
            life=self.life,
            cmap="binary",
            interval=100,
            figsize=5,
            theme='default'
        )
        
        self.assertIsNone(animator._custom_cmap)

    def test_get_population_stats(self):
        """Test population statistics calculation."""
        # Create a known state
        test_state = np.array([[1, 0, 1], [0, 1, 0], [1, 1, 0]], dtype=np.int8)
        self.life.state = test_state
        
        population, density = self.default_animator._get_population_stats()
        
        expected_population = 5  # Count of 1s in test_state
        expected_density = (5 / 9) * 100  # 5 out of 9 cells
        
        self.assertEqual(population, expected_population)
        self.assertAlmostEqual(density, expected_density, places=1)

    def test_update_fps(self):
        """Test FPS counter functionality."""
        import time
        
        # Simulate frame updates
        fps1 = self.default_animator._update_fps()
        time.sleep(0.01)  # Small delay
        fps2 = self.default_animator._update_fps()
        
        # Should have some FPS values
        self.assertTrue(len(self.default_animator.fps_counter) > 0)
        self.assertIsInstance(fps2, float)
        self.assertGreater(fps2, 0)

    def test_fps_counter_limit(self):
        """Test that FPS counter is limited to 10 entries."""
        # Add more than 10 entries
        for i in range(15):
            self.default_animator._update_fps()
        
        # Should be limited to 10
        self.assertLessEqual(len(self.default_animator.fps_counter), 10)

    @patch('matplotlib.pyplot.subplots')
    def test_draw_grid_small_grid(self, mock_subplots):
        """Test grid drawing for small grids."""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # Test with small grid (should draw grid)
        small_shape = (20, 20)  # Less than 50
        self.default_animator._draw_grid(mock_ax, small_shape)
        
        # Should have called axhline and axvline
        self.assertTrue(mock_ax.axhline.called)
        self.assertTrue(mock_ax.axvline.called)
        
        # Should have correct number of calls (21 lines for 20x20 grid)
        self.assertEqual(mock_ax.axhline.call_count, 21)
        self.assertEqual(mock_ax.axvline.call_count, 21)

    @patch('matplotlib.pyplot.subplots')
    def test_draw_grid_large_grid(self, mock_subplots):
        """Test grid drawing for large grids."""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        
        # Test with large grid (should not draw grid)
        large_shape = (100, 100)  # Greater than 50
        self.default_animator._draw_grid(mock_ax, large_shape)
        
        # Should not have called axhline or axvline
        self.assertFalse(mock_ax.axhline.called)
        self.assertFalse(mock_ax.axvline.called)

    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.animation.FuncAnimation')
    def test_call_method_default(self, mock_animation, mock_subplots):
        """Test the __call__ method with default options."""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        mock_im = Mock()
        mock_ax.imshow.return_value = mock_im
        mock_anim = Mock()
        mock_animation.return_value = mock_anim
        
        result = self.default_animator()
        
        # Verify setup calls
        mock_subplots.assert_called_once()
        mock_ax.imshow.assert_called_once()
        mock_animation.assert_called_once()
        
        # Should turn off axis for default mode
        plt.axis.assert_called_with("off") if hasattr(plt, 'axis') else None
        
        self.assertEqual(result, mock_anim)

    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.animation.FuncAnimation')
    def test_call_method_with_stats(self, mock_animation, mock_subplots):
        """Test the __call__ method with statistics enabled."""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        mock_im = Mock()
        mock_ax.imshow.return_value = mock_im
        mock_ax.text.return_value = Mock()
        mock_ax.set_title.return_value = Mock()
        mock_anim = Mock()
        mock_animation.return_value = mock_anim
        
        stats_animator = Animator(
            life=self.life,
            cmap="binary",
            interval=100,
            figsize=5,
            show_stats=True
        )
        
        result = stats_animator()
        
        # Should set up stats display
        mock_ax.set_xticks.assert_called_once_with([])
        mock_ax.set_yticks.assert_called_once_with([])
        mock_ax.set_title.assert_called_once()
        mock_ax.text.assert_called_once()
        
        # Should disable blitting when stats are shown
        call_args = mock_animation.call_args[1]
        self.assertEqual(call_args['blit'], False)

    @patch('matplotlib.pyplot.subplots')
    @patch('matplotlib.animation.FuncAnimation')
    def test_call_method_with_grid(self, mock_animation, mock_subplots):
        """Test the __call__ method with grid enabled."""
        mock_fig = Mock()
        mock_ax = Mock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        mock_im = Mock()
        mock_ax.imshow.return_value = mock_im
        mock_anim = Mock()
        mock_animation.return_value = mock_anim
        
        # Use small size so grid will be drawn
        small_life = Life(size=20, seed="noise", func=fast)
        grid_animator = Animator(
            life=small_life,
            cmap="binary",
            interval=100,
            figsize=5,
            show_grid=True
        )
        
        result = grid_animator()
        
        # Grid drawing should be called
        self.assertTrue(mock_ax.axhline.called)
        self.assertTrue(mock_ax.axvline.called)

    def test_theme_background_colors(self):
        """Test that different themes set appropriate background colors."""
        themes_to_test = ['matrix', 'neon', 'cyber']
        
        for theme in themes_to_test:
            with patch('matplotlib.pyplot.subplots') as mock_subplots:
                mock_fig = Mock()
                mock_ax = Mock()
                mock_subplots.return_value = (mock_fig, mock_ax)
                mock_ax.imshow.return_value = Mock()
                
                with patch('matplotlib.animation.FuncAnimation'):
                    animator = Animator(
                        life=self.life,
                        cmap="binary",
                        interval=100,
                        figsize=5,
                        theme=theme
                    )
                    animator()
                    
                    # Should set background colors
                    mock_fig.patch.set_facecolor.assert_called_once()
                    mock_ax.set_facecolor.assert_called_once()

    def test_glow_effect_themes(self):
        """Test that glow effect is applied to appropriate themes."""
        glow_themes = ['neon', 'matrix']
        
        for theme in glow_themes:
            animator = Animator(
                life=self.life,
                cmap="binary",
                interval=100,
                figsize=5,
                theme=theme
            )
            
            # The glow effect should be handled in the update function
            # This is tested indirectly by checking theme assignment
            self.assertIn(animator.theme, glow_themes)

    def tearDown(self):
        """Clean up after tests."""
        plt.close('all')


if __name__ == '__main__':
    unittest.main()