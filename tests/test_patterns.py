"""
Unit tests for pattern loading and validation.
"""
import numpy as np
import pytest
from pathlib import Path

from life.pattern_factory import (
    load_pattern_from_cells,
    patterns,
)


class TestPatternLoading:
    """Test pattern loading functionality."""
    
    def test_load_glider_pattern(self):
        """Test loading the glider pattern."""
        assert 'glider' in patterns, "Glider pattern should be available"
        glider = patterns['glider']
        
        # Glider should be a 3x3 pattern
        assert glider.shape == (3, 3), f"Expected (3, 3), got {glider.shape}"
        
        # Check the glider pattern structure
        expected = np.array([
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ], dtype=np.int8)
        
        np.testing.assert_array_equal(glider, expected)
    
    def test_load_blinker_pattern(self):
        """Test loading the blinker pattern."""
        assert 'blinker' in patterns, "Blinker pattern should be available"
        blinker = patterns['blinker']
        
        # Blinker should be a 3x1 pattern
        assert blinker.shape == (1, 3), f"Expected (1, 3), got {blinker.shape}"
        
        # Check the blinker pattern structure
        expected = np.array([[1, 1, 1]], dtype=np.int8)
        np.testing.assert_array_equal(blinker, expected)
    
    def test_pattern_data_types(self):
        """Test that all patterns are numpy arrays with correct dtype."""
        for name, pattern in patterns.items():
            assert isinstance(pattern, np.ndarray), f"Pattern {name} should be numpy array"
            assert pattern.dtype == np.int8, f"Pattern {name} should have dtype int8"
            assert np.all((pattern == 0) | (pattern == 1)), f"Pattern {name} should only contain 0s and 1s"
    
    def test_pattern_names_are_strings(self):
        """Test that all pattern names are strings."""
        for name in patterns.keys():
            assert isinstance(name, str), f"Pattern name {name} should be a string"
    
    def test_patterns_not_empty(self):
        """Test that we have loaded some patterns."""
        assert len(patterns) > 0, "Should have loaded at least one pattern"
    
    def test_new_patterns_loaded(self):
        """Test that our newly added patterns are loaded."""
        expected_patterns = [
            'lightweight_spaceship',
            'middleweight_spaceship', 
            'heavyweight_spaceship',
            'toad',
            'beacon',
            'clock',
            'block',
            'beehive',
            'loaf',
            'boat',
            'acorn',
            'diehard',
            'rpentomino'
        ]
        
        for pattern_name in expected_patterns:
            assert pattern_name in patterns, f"Pattern {pattern_name} should be loaded"


class TestCellsFileFormat:
    """Test the .cells file format parsing."""
    
    def test_cells_format_parsing(self):
        """Test parsing of a simple cells format string."""
        # Create a temporary cells content
        cells_content = """!Name: Test Pattern
!This is a test
.O.
O.O
.O."""
        
        # Write to a temporary file and test loading
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cells', delete=False) as f:
            f.write(cells_content)
            f.flush()
            
            pattern = load_pattern_from_cells(Path(f.name))
            
            expected = np.array([
                [0, 1, 0],
                [1, 0, 1],
                [0, 1, 0]
            ], dtype=np.int8)
            
            np.testing.assert_array_equal(pattern, expected)
        
        # Clean up
        Path(f.name).unlink()
    
    def test_cells_format_with_comments(self):
        """Test that comments are properly ignored."""
        cells_content = """!This is a comment
!Another comment
OO
!Comment in the middle
OO"""
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cells', delete=False) as f:
            f.write(cells_content)
            f.flush()
            
            pattern = load_pattern_from_cells(Path(f.name))
            
            expected = np.array([
                [1, 1],
                [1, 1]
            ], dtype=np.int8)
            
            np.testing.assert_array_equal(pattern, expected)
        
        # Clean up
        Path(f.name).unlink()
    
    def test_cells_format_irregular_width(self):
        """Test handling of irregular line widths."""
        cells_content = """O
OOO
O"""
        
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cells', delete=False) as f:
            f.write(cells_content)
            f.flush()
            
            pattern = load_pattern_from_cells(Path(f.name))
            
            # Should pad shorter lines with zeros
            expected = np.array([
                [1, 0, 0],
                [1, 1, 1],
                [1, 0, 0]
            ], dtype=np.int8)
            
            np.testing.assert_array_equal(pattern, expected)
        
        # Clean up
        Path(f.name).unlink()


if __name__ == "__main__":
    pytest.main([__file__])

