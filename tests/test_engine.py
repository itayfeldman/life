"""
Unit tests for the Game of Life engine algorithms.
"""
import numpy as np
import pytest

from life.engine import (
    convolution,
    window,
    loop,
    fast,
    ultra_fast,
    vectorized,
)


class TestEngineAlgorithms:
    """Test all engine algorithms produce consistent results."""
    
    @pytest.fixture
    def blinker_state(self):
        """A simple blinker pattern for testing."""
        state = np.zeros((5, 5), dtype=np.int8)
        state[2, 1:4] = 1  # Horizontal line
        return state
    
    @pytest.fixture
    def block_state(self):
        """A stable block pattern for testing."""
        state = np.zeros((4, 4), dtype=np.int8)
        state[1:3, 1:3] = 1  # 2x2 block
        return state
    
    @pytest.fixture
    def glider_state(self):
        """A glider pattern for testing."""
        state = np.zeros((10, 10), dtype=np.int8)
        # Glider pattern
        state[1, 2] = 1
        state[2, 3] = 1
        state[3, 1:4] = 1
        return state
    
    def test_all_algorithms_consistent_blinker(self, blinker_state):
        """Test that all algorithms produce the same result for a blinker."""
        algorithms = [convolution, window, loop, fast, ultra_fast, vectorized]
        results = [alg(blinker_state) for alg in algorithms]
        
        # All results should be identical
        for i in range(1, len(results)):
            np.testing.assert_array_equal(
                results[0], results[i],
                f"Algorithm {algorithms[i].__name__} differs from {algorithms[0].__name__}"
            )
    
    def test_all_algorithms_consistent_block(self, block_state):
        """Test that all algorithms produce the same result for a stable block."""
        algorithms = [convolution, window, loop, fast, ultra_fast, vectorized]
        results = [alg(block_state) for alg in algorithms]
        
        # All results should be identical
        for i in range(1, len(results)):
            np.testing.assert_array_equal(
                results[0], results[i],
                f"Algorithm {algorithms[i].__name__} differs from {algorithms[0].__name__}"
            )
    
    def test_all_algorithms_consistent_glider(self, glider_state):
        """Test that all algorithms produce the same result for a glider."""
        algorithms = [convolution, window, loop, fast, ultra_fast, vectorized]
        results = [alg(glider_state) for alg in algorithms]
        
        # All results should be identical
        for i in range(1, len(results)):
            np.testing.assert_array_equal(
                results[0], results[i],
                f"Algorithm {algorithms[i].__name__} differs from {algorithms[0].__name__}"
            )
    
    def test_blinker_oscillation(self, blinker_state):
        """Test that a blinker oscillates correctly."""
        # First generation should be vertical
        next_state = fast(blinker_state)
        expected = np.zeros((5, 5), dtype=np.int8)
        expected[1:4, 2] = 1  # Vertical line
        np.testing.assert_array_equal(next_state, expected)
        
        # Second generation should be back to horizontal
        next_next_state = fast(next_state)
        np.testing.assert_array_equal(next_next_state, blinker_state)
    
    def test_block_stability(self, block_state):
        """Test that a block remains stable."""
        next_state = fast(block_state)
        np.testing.assert_array_equal(next_state, block_state)
    
    def test_empty_grid(self):
        """Test that an empty grid remains empty."""
        empty = np.zeros((10, 10), dtype=np.int8)
        next_state = fast(empty)
        np.testing.assert_array_equal(next_state, empty)
    
    def test_full_grid(self):
        """Test behavior with a completely filled grid."""
        full = np.ones((5, 5), dtype=np.int8)
        next_state = fast(full)
        
        # In a full grid, only corner cells should survive (they have 3 neighbors)
        expected = np.zeros((5, 5), dtype=np.int8)
        expected[0, 0] = expected[0, 4] = expected[4, 0] = expected[4, 4] = 1
        np.testing.assert_array_equal(next_state, expected)
    
    def test_single_cell(self):
        """Test that a single cell dies (underpopulation)."""
        single = np.zeros((3, 3), dtype=np.int8)
        single[1, 1] = 1
        next_state = fast(single)
        expected = np.zeros((3, 3), dtype=np.int8)
        np.testing.assert_array_equal(next_state, expected)
    
    def test_wrapping_boundaries(self):
        """Test that boundary wrapping works correctly."""
        # Place a glider near the edge to test wrapping
        state = np.zeros((5, 5), dtype=np.int8)
        # Glider at the edge
        state[0, 3] = 1
        state[1, 4] = 1
        state[2, 2:5] = 1
        
        # All algorithms should handle wrapping consistently
        algorithms = [convolution, window, loop, fast, ultra_fast, vectorized]
        results = [alg(state) for alg in algorithms]
        
        for i in range(1, len(results)):
            np.testing.assert_array_equal(
                results[0], results[i],
                f"Wrapping differs between {algorithms[0].__name__} and {algorithms[i].__name__}"
            )


class TestGameOfLifeRules:
    """Test that the Game of Life rules are correctly implemented."""
    
    def test_underpopulation_rule(self):
        """Test that cells with fewer than 2 neighbors die."""
        state = np.zeros((3, 3), dtype=np.int8)
        state[1, 1] = 1  # Single cell
        next_state = fast(state)
        assert next_state[1, 1] == 0, "Cell should die from underpopulation"
    
    def test_survival_rule(self):
        """Test that cells with 2 or 3 neighbors survive."""
        # Create a configuration where center cell has exactly 2 neighbors
        state = np.zeros((3, 3), dtype=np.int8)
        state[1, 1] = 1  # Center cell
        state[0, 0] = 1  # Neighbor 1
        state[0, 1] = 1  # Neighbor 2
        
        next_state = fast(state)
        assert next_state[1, 1] == 1, "Cell should survive with 2 neighbors"
    
    def test_overpopulation_rule(self):
        """Test that cells with more than 3 neighbors die."""
        # Create a configuration where center cell has 4+ neighbors
        state = np.zeros((3, 3), dtype=np.int8)
        state[1, 1] = 1  # Center cell
        state[0, 0:3] = 1  # Top row
        state[1, 0] = 1  # Left neighbor
        
        next_state = fast(state)
        assert next_state[1, 1] == 0, "Cell should die from overpopulation"
    
    def test_reproduction_rule(self):
        """Test that empty cells with exactly 3 neighbors become alive."""
        # Create a configuration where center cell has exactly 3 neighbors
        state = np.zeros((3, 3), dtype=np.int8)
        state[0, 0] = 1  # Neighbor 1
        state[0, 1] = 1  # Neighbor 2
        state[1, 0] = 1  # Neighbor 3
        # Center cell is empty
        
        next_state = fast(state)
        assert next_state[1, 1] == 1, "Empty cell should become alive with 3 neighbors"


if __name__ == "__main__":
    pytest.main([__file__])

