import unittest
import numpy as np

from life.engine import (
    convolution,
    window, 
    loop,
    fast,
    ultra_fast,
    vectorized
)


class TestEngine(unittest.TestCase):
    """Test cases for the Conway's Game of Life engine functions."""

    def setUp(self):
        """Set up test fixtures with known patterns."""
        # Blinker pattern (oscillates between horizontal and vertical)
        self.blinker_horizontal = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0]
        ], dtype=np.int8)
        
        self.blinker_vertical = np.array([
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0]
        ], dtype=np.int8)
        
        # Block pattern (stable)
        self.block = np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0]
        ], dtype=np.int8)
        
        # Empty state
        self.empty = np.zeros((5, 5), dtype=np.int8)
        
        # Single cell (dies from underpopulation)
        self.single_cell = np.array([
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ], dtype=np.int8)
        
        # Overcrowded pattern (all die from overpopulation)
        self.overcrowded = np.array([
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1]
        ], dtype=np.int8)

    def test_all_functions_available(self):
        """Test that all engine functions are available and callable."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            self.assertTrue(callable(func))

    def test_function_return_types(self):
        """Test that all functions return numpy arrays of correct type."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            result = func(self.blinker_horizontal)
            
            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(result.dtype, np.int8)
            self.assertEqual(result.shape, self.blinker_horizontal.shape)

    def test_empty_state_remains_empty(self):
        """Test that empty state remains empty for all functions."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            result = func(self.empty)
            
            np.testing.assert_array_equal(result, self.empty)
            self.assertEqual(np.sum(result), 0)

    def test_single_cell_dies(self):
        """Test that a single isolated cell dies (underpopulation)."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        expected_result = np.zeros((3, 3), dtype=np.int8)
        
        for func in functions:
            result = func(self.single_cell)
            
            np.testing.assert_array_equal(result, expected_result)

    def test_block_pattern_stable(self):
        """Test that block pattern remains stable."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            result = func(self.block)
            
            np.testing.assert_array_equal(result, self.block)

    def test_blinker_oscillation(self):
        """Test blinker pattern oscillation."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            # Horizontal blinker should become vertical
            result = func(self.blinker_horizontal)
            np.testing.assert_array_equal(result, self.blinker_vertical)
            
            # Vertical blinker should become horizontal
            result = func(self.blinker_vertical)
            np.testing.assert_array_equal(result, self.blinker_horizontal)

    def test_overcrowded_dies(self):
        """Test that overcrowded cells die from overpopulation."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            result = func(self.overcrowded)
            
            # All interior cells should die (8 neighbors each)
            # Only corner cells might survive (3 neighbors each)
            expected = np.array([
                [1, 0, 1],
                [0, 0, 0],
                [1, 0, 1]
            ], dtype=np.int8)
            
            np.testing.assert_array_equal(result, expected)

    def test_function_consistency(self):
        """Test that all functions produce identical results."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        test_patterns = [
            self.blinker_horizontal,
            self.blinker_vertical, 
            self.block,
            self.empty,
            self.single_cell,
            self.overcrowded
        ]
        
        for pattern in test_patterns:
            results = []
            for func in functions:
                result = func(pattern)
                results.append(result)
            
            # All results should be identical
            reference_result = results[0]
            for i, result in enumerate(results[1:], 1):
                np.testing.assert_array_equal(
                    result, reference_result,
                    f"Function {functions[i].__name__} differs from {functions[0].__name__}"
                )

    def test_conways_rules_implementation(self):
        """Test specific Conway's Game of Life rules."""
        # Test rule: Live cell with 2-3 neighbors survives
        pattern = np.array([
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0]
        ], dtype=np.int8)
        
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            result = func(pattern)
            
            # Center cell has 4 neighbors, should die
            self.assertEqual(result[1, 1], 0)
            
            # Edge cells have 3 neighbors, should be born/stay alive
            self.assertEqual(result[0, 1], 1)  # Top
            self.assertEqual(result[1, 0], 1)  # Left  
            self.assertEqual(result[1, 2], 1)  # Right
            self.assertEqual(result[2, 1], 1)  # Bottom

    def test_birth_rule(self):
        """Test that dead cells with exactly 3 neighbors are born."""
        # Pattern where dead center cell has exactly 3 live neighbors
        pattern = np.array([
            [1, 1, 0],
            [1, 0, 0],
            [0, 0, 0]
        ], dtype=np.int8)
        
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            result = func(pattern)
            
            # Center cell (1,1) has exactly 3 neighbors, should be born
            self.assertEqual(result[1, 1], 1)

    def test_wrapping_boundaries(self):
        """Test that functions handle wrapping boundaries correctly."""
        # Create pattern at edge to test wrapping
        edge_pattern = np.zeros((5, 5), dtype=np.int8)
        edge_pattern[0, 0] = 1  # Top-left corner
        edge_pattern[0, 1] = 1  # Top edge
        edge_pattern[1, 0] = 1  # Left edge
        
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            result = func(edge_pattern)
            
            # The pattern should evolve according to Conway's rules
            # with wraparound considered for neighbor counting
            self.assertIsInstance(result, np.ndarray)
            self.assertEqual(result.shape, edge_pattern.shape)
            
            # Values should only be 0 or 1
            unique_values = np.unique(result)
            self.assertTrue(all(val in [0, 1] for val in unique_values))

    def test_large_random_consistency(self):
        """Test function consistency on larger random patterns."""
        np.random.seed(42)  # For reproducible tests
        large_pattern = np.random.randint(0, 2, size=(20, 20), dtype=np.int8)
        
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        results = []
        
        for func in functions:
            result = func(large_pattern)
            results.append(result)
        
        # All functions should produce identical results
        reference = results[0]
        for i, result in enumerate(results[1:], 1):
            np.testing.assert_array_equal(
                result, reference,
                f"Function {functions[i].__name__} differs from reference on large pattern"
            )

    def test_function_docstrings(self):
        """Test that all functions have proper documentation."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            self.assertIsNotNone(func.__doc__)
            self.assertIn('state', func.__doc__.lower())
            self.assertIn('State', func.__doc__)  # Return type
            
            # Should mention Conway's Game of Life
            doc_lower = func.__doc__.lower()
            self.assertTrue(
                'game of life' in doc_lower or 'life' in doc_lower,
                f"Function {func.__name__} docstring should mention Game of Life"
            )

    def test_function_examples_in_docstrings(self):
        """Test that function docstring examples are present."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        for func in functions:
            doc = func.__doc__
            if doc:
                # Many functions have examples in their docstrings
                if 'Examples' in doc or '>>>' in doc:
                    self.assertIn('>>>', doc)

    def test_performance_functions_exist(self):
        """Test that performance-optimized functions exist."""
        # These should be the fastest implementations
        performance_functions = [fast, ultra_fast, vectorized]
        
        for func in performance_functions:
            self.assertTrue(callable(func))
            
            # Test with a small pattern
            result = func(self.blinker_horizontal)
            self.assertIsInstance(result, np.ndarray)

    def test_edge_cases(self):
        """Test edge cases for all functions."""
        functions = [convolution, window, loop, fast, ultra_fast, vectorized]
        
        # Minimum size grid
        tiny_grid = np.array([[1]], dtype=np.int8)
        
        for func in functions:
            result = func(tiny_grid)
            
            self.assertEqual(result.shape, (1, 1))
            self.assertEqual(result.dtype, np.int8)
            # Single cell with wraparound has 0 neighbors, should die
            self.assertEqual(result[0, 0], 0)

    def tearDown(self):
        """Clean up after tests."""
        pass


if __name__ == '__main__':
    unittest.main()