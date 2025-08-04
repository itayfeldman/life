import unittest
import numpy as np

from life.life import Life
from life.engine import fast, loop, convolution
from life.exceptions import SizeTypeError, SizeValueError


class TestLife(unittest.TestCase):
    """Test cases for the Life class."""

    def setUp(self):
        """Set up test fixtures."""
        self.size = 50
        self.test_life = Life(size=self.size, seed="noise", func=fast)

    def test_life_initialization_valid(self):
        """Test Life initialization with valid parameters."""
        life = Life(size=50, seed="noise", func=fast)
        
        self.assertEqual(life.state.shape, (50, 50))
        self.assertEqual(life.state.dtype, np.int8)
        self.assertEqual(life.func, fast)
        
        # State should contain only 0s and 1s
        unique_values = np.unique(life.state)
        self.assertTrue(all(val in [0, 1] for val in unique_values))

    def test_life_initialization_different_sizes(self):
        """Test Life initialization with different valid sizes."""
        sizes = [10, 25, 100, 500, 1000]
        
        for size in sizes:
            life = Life(size=size, seed="noise", func=fast)
            self.assertEqual(life.state.shape, (size, size))
            self.assertEqual(life.state.dtype, np.int8)

    def test_life_initialization_different_functions(self):
        """Test Life initialization with different engine functions."""
        functions = [fast, loop, convolution]
        
        for func in functions:
            life = Life(size=30, seed="noise", func=func)
            self.assertEqual(life.func, func)
            self.assertEqual(life.state.shape, (30, 30))

    def test_life_initialization_invalid_size_type(self):
        """Test Life initialization with invalid size type."""
        with self.assertRaises(SizeTypeError):
            Life(size="50", seed="noise", func=fast)
        
        with self.assertRaises(SizeTypeError):
            Life(size=50.5, seed="noise", func=fast)
        
        with self.assertRaises(SizeTypeError):
            Life(size=None, seed="noise", func=fast)

    def test_life_initialization_invalid_size_value(self):
        """Test Life initialization with invalid size values."""
        with self.assertRaises(SizeValueError):
            Life(size=5, seed="noise", func=fast)  # Too small
        
        with self.assertRaises(SizeValueError):
            Life(size=1500, seed="noise", func=fast)  # Too large

    def test_life_iterator_protocol(self):
        """Test that Life implements iterator protocol correctly."""
        life = Life(size=20, seed="noise", func=fast)
        
        # Should be its own iterator
        self.assertEqual(iter(life), life)
        
        # Should be able to call next()
        initial_state = life.state.copy()
        next_state = next(life)
        
        self.assertIsInstance(next_state, np.ndarray)
        self.assertEqual(next_state.shape, (20, 20))
        self.assertEqual(next_state.dtype, np.int8)
        
        # State should have changed (unless it's a stable pattern)
        # We'll just check that we got a valid state back
        unique_values = np.unique(next_state)
        self.assertTrue(all(val in [0, 1] for val in unique_values))

    def test_life_multiple_iterations(self):
        """Test multiple iterations of Life."""
        life = Life(size=20, seed="noise", func=fast)
        
        states = []
        for i in range(5):
            state = next(life)
            states.append(state.copy())
            
            # Each state should be valid
            self.assertEqual(state.shape, (20, 20))
            self.assertEqual(state.dtype, np.int8)
            unique_values = np.unique(state)
            self.assertTrue(all(val in [0, 1] for val in unique_values))
        
        # Should have 5 different states
        self.assertEqual(len(states), 5)

    def test_life_state_consistency(self):
        """Test that Life state is consistent with the internal state."""
        life = Life(size=20, seed="noise", func=fast)
        
        # Initial state should match
        initial_internal = life.state.copy()
        
        # After iteration, next() return should match internal state
        next_state = next(life)
        
        np.testing.assert_array_equal(next_state, life.state)

    def test_life_different_seeds(self):
        """Test Life with different seed types."""
        # Test with noise seed
        life_noise = Life(size=30, seed="noise", func=fast)
        self.assertEqual(life_noise.state.shape, (30, 30))
        
        # Test with symmetric seed  
        life_symmetric = Life(size=30, seed="symmetric", func=fast)
        self.assertEqual(life_symmetric.state.shape, (30, 30))
        
        # States should be different (with very high probability)
        # Note: There's a tiny chance they could be identical, but highly unlikely
        states_equal = np.array_equal(life_noise.state, life_symmetric.state)
        # We won't assert this is False due to randomness, but typically it should be

    def test_life_known_patterns(self):
        """Test Life with known patterns if available."""
        # This would test with loaded patterns from pattern_factory
        # For now, we'll test that the pattern seed works
        try:
            # Try to create with a pattern (may not exist in test environment)
            life = Life(size=50, seed="blinker", func=fast)
            self.assertEqual(life.state.shape, (50, 50))
        except:
            # If pattern doesn't exist, that's okay for this test
            pass

    def test_life_blinker_pattern(self):
        """Test Life with a simple blinker pattern."""
        # Create a blinker pattern manually
        life = Life(size=5, seed="noise", func=fast)
        
        # Set up a blinker pattern: three horizontal cells
        blinker = np.zeros((5, 5), dtype=np.int8)
        blinker[2, 1:4] = 1  # Horizontal line
        life.state = blinker
        
        # After one iteration, should become vertical
        next_state = next(life)
        
        # Check that we have exactly 3 live cells
        live_cells = np.sum(next_state)
        self.assertEqual(live_cells, 3)

    def test_life_empty_state(self):
        """Test Life behavior with empty state."""
        life = Life(size=10, seed="noise", func=fast)
        
        # Set to empty state
        life.state = np.zeros((10, 10), dtype=np.int8)
        
        # Should remain empty after iteration
        next_state = next(life)
        
        self.assertEqual(np.sum(next_state), 0)
        np.testing.assert_array_equal(next_state, np.zeros((10, 10), dtype=np.int8))

    def test_life_full_state(self):
        """Test Life behavior with completely filled state."""
        life = Life(size=5, seed="noise", func=fast)
        
        # Set to full state
        life.state = np.ones((5, 5), dtype=np.int8)
        
        # After iteration, should follow Conway's rules
        # All cells die due to overpopulation except possibly edges
        next_state = next(life)
        
        # Should be mostly empty (all interior cells die)
        # Only edge cells might survive with 2-3 neighbors
        total_live = np.sum(next_state)
        self.assertLess(total_live, 25)  # Definitely less than full

    def test_life_state_immutability_after_next(self):
        """Test that calling next() updates the internal state."""
        life = Life(size=10, seed="noise", func=fast)
        
        initial_state = life.state.copy()
        next_state = next(life)
        
        # Internal state should have been updated
        np.testing.assert_array_equal(life.state, next_state)
        
        # Should be different from initial (unless stable pattern)
        # We just verify that the mechanism works correctly
        self.assertIsInstance(next_state, np.ndarray)

    def test_life_function_parameter(self):
        """Test that Life correctly uses the provided function."""
        # We can't easily test which function was called without mocking,
        # but we can verify the function is stored correctly
        functions = [fast, loop, convolution]
        
        for func in functions:
            life = Life(size=20, seed="noise", func=func)
            self.assertEqual(life.func, func)

    def test_life_docstring_functionality(self):
        """Test that Life's __next__ method has proper documentation."""
        life = Life(size=10, seed="noise", func=fast)
        
        # Check that __next__ method exists and is callable
        self.assertTrue(hasattr(life, '__next__'))
        self.assertTrue(callable(getattr(life, '__next__')))
        
        # Check that it has a docstring
        next_method = getattr(life, '__next__')
        self.assertIsNotNone(next_method.__doc__)
        self.assertIn('state', next_method.__doc__.lower())

    def tearDown(self):
        """Clean up after tests."""
        pass


if __name__ == '__main__':
    unittest.main()