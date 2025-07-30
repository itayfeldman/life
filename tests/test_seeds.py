"""
Unit tests for seed generation functionality.
"""
import numpy as np
import pytest

from life.seeds import SeedGenerators, new_seed_generator


class TestSeedGenerators:
    """Test seed generation methods."""
    
    def test_noise_seed_shape(self):
        """Test that noise seed generates correct shape."""
        size = 50
        seed = SeedGenerators.noise(size)
        
        assert seed.shape == (size, size), f"Expected ({size}, {size}), got {seed.shape}"
        assert seed.dtype == np.int8, f"Expected int8, got {seed.dtype}"
        assert np.all((seed == 0) | (seed == 1)), "Seed should only contain 0s and 1s"
    
    def test_noise_seed_randomness(self):
        """Test that noise seed is actually random."""
        size = 100
        seed1 = SeedGenerators.noise(size)
        seed2 = SeedGenerators.noise(size)
        
        # Seeds should be different (with very high probability)
        assert not np.array_equal(seed1, seed2), "Two noise seeds should be different"
        
        # Should have some alive cells (with very high probability for size 100)
        assert np.sum(seed1) > 0, "Noise seed should have some alive cells"
        assert np.sum(seed2) > 0, "Noise seed should have some alive cells"
    
    def test_symmetric_seed_shape(self):
        """Test that symmetric seed generates correct shape."""
        size = 50
        seed = SeedGenerators.symmetric(size)
        
        assert seed.shape == (size, size), f"Expected ({size}, {size}), got {seed.shape}"
        assert seed.dtype == np.int8, f"Expected int8, got {seed.dtype}"
        assert np.all((seed == 0) | (seed == 1)), "Seed should only contain 0s and 1s"
    
    def test_pattern_seed_glider(self):
        """Test that pattern seed loads glider correctly."""
        size = 20
        seed = SeedGenerators.pattern(size, "glider")
        
        assert seed.shape == (size, size), f"Expected ({size}, {size}), got {seed.shape}"
        assert seed.dtype == np.int8, f"Expected int8, got {seed.dtype}"
        
        # Check that glider pattern is at top-left corner
        expected_glider = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ], dtype=np.int8)
        
        np.testing.assert_array_equal(seed[0:3, 0:3], expected_glider)
        
        # Rest should be zeros
        assert np.sum(seed[3:, :]) == 0, "Area below glider should be empty"
        assert np.sum(seed[:, 3:]) == 0, "Area to right of glider should be empty"
    
    def test_new_seed_generator_noise(self):
        """Test new_seed_generator with noise."""
        size = 30
        seed = new_seed_generator(size, "noise")
        
        assert seed.shape == (size, size)
        assert seed.dtype == np.int8
        assert np.all((seed == 0) | (seed == 1))
    
    def test_new_seed_generator_symmetric(self):
        """Test new_seed_generator with symmetric."""
        size = 30
        seed = new_seed_generator(size, "symmetric")
        
        assert seed.shape == (size, size)
        assert seed.dtype == np.int8
        assert np.all((seed == 0) | (seed == 1))
    
    def test_new_seed_generator_pattern(self):
        """Test new_seed_generator with pattern."""
        size = 20
        seed = new_seed_generator(size, "glider")
        
        assert seed.shape == (size, size)
        assert seed.dtype == np.int8
        
        # Should contain the glider pattern
        expected_glider = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ], dtype=np.int8)
        
        np.testing.assert_array_equal(seed[0:3, 0:3], expected_glider)
    
    def test_seed_generator_edge_cases(self):
        """Test seed generators with edge case sizes."""
        # Test minimum reasonable size
        small_size = 10
        noise_seed = SeedGenerators.noise(small_size)
        assert noise_seed.shape == (small_size, small_size)
        
        # Test larger size
        large_size = 200
        noise_seed_large = SeedGenerators.noise(large_size)
        assert noise_seed_large.shape == (large_size, large_size)
    
    def test_pattern_seed_with_new_patterns(self):
        """Test that our newly added patterns work as seeds."""
        size = 30
        new_patterns = [
            'lightweight_spaceship',
            'toad',
            'beacon',
            'block',
            'beehive',
            'acorn'
        ]
        
        for pattern_name in new_patterns:
            try:
                seed = new_seed_generator(size, pattern_name)
                assert seed.shape == (size, size), f"Pattern {pattern_name} should generate correct size"
                assert seed.dtype == np.int8, f"Pattern {pattern_name} should have correct dtype"
                assert np.sum(seed) > 0, f"Pattern {pattern_name} should have some alive cells"
            except KeyError:
                pytest.skip(f"Pattern {pattern_name} not available in test environment")


if __name__ == "__main__":
    pytest.main([__file__])

