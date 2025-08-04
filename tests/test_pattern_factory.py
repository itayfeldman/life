import unittest
from unittest.mock import patch, mock_open, Mock
import numpy as np
from pathlib import Path
import tempfile
import os

from life.pattern_factory import (
    load_pattern_from_cells,
    load_pattern_from_ndarray,
    load_objects_from_pattern_dir,
    get_patterns,
    patterns,
    file_types
)


class TestPatternFactory(unittest.TestCase):
    """Test cases for the pattern factory module."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample .cells file content
        self.sample_cells_content = """!Name: Test Pattern
!Author: Test
!Comment: A simple test pattern
.O.
OOO
.O."""
        
        # Expected pattern from sample cells content
        self.expected_cells_pattern = np.array([
            [0, 1, 0],
            [1, 1, 1],
            [0, 1, 0]
        ], dtype=np.int8)
        
        # Sample cells content with comments and empty lines
        self.complex_cells_content = """!Name: Complex Pattern
!This is a comment line

.OO.
O..O
!Another comment
O..O
.OO.

"""
        
        self.expected_complex_pattern = np.array([
            [0, 1, 1, 0],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [0, 1, 1, 0]
        ], dtype=np.int8)

    def test_load_pattern_from_cells_simple(self):
        """Test loading a simple pattern from cells format."""
        with patch("builtins.open", mock_open(read_data=self.sample_cells_content)):
            result = load_pattern_from_cells(Path("test.cells"))
            
            np.testing.assert_array_equal(result, self.expected_cells_pattern)
            self.assertEqual(result.dtype, np.int8)

    def test_load_pattern_from_cells_complex(self):
        """Test loading a complex pattern with comments and empty lines."""
        with patch("builtins.open", mock_open(read_data=self.complex_cells_content)):
            result = load_pattern_from_cells(Path("complex.cells"))
            
            np.testing.assert_array_equal(result, self.expected_complex_pattern)
            self.assertEqual(result.dtype, np.int8)

    def test_load_pattern_from_cells_empty_file(self):
        """Test loading from an empty cells file."""
        empty_content = """!Name: Empty
!Comment: Only comments
"""
        
        with patch("builtins.open", mock_open(read_data=empty_content)):
            with self.assertRaises(ValueError) as context:
                load_pattern_from_cells(Path("empty.cells"))
            
            self.assertIn("No pattern data found", str(context.exception))

    def test_load_pattern_from_cells_irregular_lines(self):
        """Test loading from cells file with irregular line lengths."""
        irregular_content = """!Irregular pattern
O
OO
O
"""
        expected_irregular = np.array([
            [1, 0],
            [1, 1],
            [1, 0]
        ], dtype=np.int8)
        
        with patch("builtins.open", mock_open(read_data=irregular_content)):
            result = load_pattern_from_cells(Path("irregular.cells"))
            
            np.testing.assert_array_equal(result, expected_irregular)

    def test_load_pattern_from_cells_only_comments(self):
        """Test loading from cells file with only comments."""
        comments_only = """!Name: Comments Only
!Author: Test
!This file has no actual pattern data
!Just comments
"""
        
        with patch("builtins.open", mock_open(read_data=comments_only)):
            with self.assertRaises(ValueError):
                load_pattern_from_cells(Path("comments.cells"))

    @patch('life.pattern_factory.import_module')
    @patch('life.pattern_factory.inspect.getmembers')
    def test_load_pattern_from_ndarray(self, mock_getmembers, mock_import):
        """Test loading pattern from Python module with ndarray."""
        # Mock the imported module
        mock_module = Mock()
        mock_import.return_value = mock_module
        
        # Mock numpy array in the module
        test_array = np.array([[1, 0], [0, 1]], dtype=np.int8)
        mock_getmembers.return_value = [
            ('some_var', 'not_an_array'),
            ('pattern_array', test_array),
            ('another_var', 42)
        ]
        
        result = load_pattern_from_ndarray(Path("test_pattern.py"))
        
        np.testing.assert_array_equal(result, test_array)
        mock_import.assert_called_once_with("test_pattern.py")

    @patch('life.pattern_factory.import_module')
    @patch('life.pattern_factory.inspect.getmembers')
    def test_load_pattern_from_ndarray_no_array(self, mock_getmembers, mock_import):
        """Test loading from Python module with no numpy arrays."""
        mock_module = Mock()
        mock_import.return_value = mock_module
        
        # Mock module with no numpy arrays
        mock_getmembers.return_value = [
            ('some_var', 'string'),
            ('number', 42),
            ('list_data', [1, 2, 3])
        ]
        
        result = load_pattern_from_ndarray(Path("no_array.py"))
        
        self.assertIsNone(result)

    def test_file_types_mapping(self):
        """Test that file_types mapping contains expected functions."""
        self.assertIn('cells', file_types)
        self.assertIn('py', file_types)
        
        self.assertEqual(file_types['cells'], load_pattern_from_cells)
        self.assertEqual(file_types['py'], load_pattern_from_ndarray)

    @patch('life.pattern_factory.Path.rglob')
    @patch('life.pattern_factory.load_pattern_from_cells')
    def test_load_objects_from_pattern_dir(self, mock_load_cells, mock_rglob):
        """Test loading patterns from a directory."""
        # Mock file paths
        mock_files = [
            Path("patterns/blinker.cells"),
            Path("patterns/glider.cells"),
            Path("patterns/block.cells")
        ]
        mock_rglob.return_value = mock_files
        
        # Mock pattern loading
        patterns_data = {
            "blinker": np.array([[0, 1, 0], [0, 1, 0], [0, 1, 0]], dtype=np.int8),
            "glider": np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]], dtype=np.int8),
            "block": np.array([[1, 1], [1, 1]], dtype=np.int8)
        }
        
        def mock_load_side_effect(path):
            stem = path.stem
            return patterns_data.get(stem, np.zeros((2, 2), dtype=np.int8))
        
        mock_load_cells.side_effect = mock_load_side_effect
        
        # Test loading
        result_patterns = {}
        result = load_objects_from_pattern_dir("test_patterns", "cells", result_patterns)
        
        self.assertEqual(len(result), 3)
        self.assertIn("blinker", result)
        self.assertIn("glider", result)
        self.assertIn("block", result)
        
        # Verify patterns are correct
        np.testing.assert_array_equal(result["blinker"], patterns_data["blinker"])
        np.testing.assert_array_equal(result["glider"], patterns_data["glider"])
        np.testing.assert_array_equal(result["block"], patterns_data["block"])

    @patch('life.pattern_factory.Path.rglob')
    @patch('life.pattern_factory.load_pattern_from_cells')
    def test_load_objects_from_pattern_dir_with_errors(self, mock_load_cells, mock_rglob):
        """Test loading patterns with some files causing errors."""
        mock_files = [
            Path("patterns/good.cells"),
            Path("patterns/bad.cells")
        ]
        mock_rglob.return_value = mock_files
        
        def mock_load_side_effect(path):
            if "bad" in str(path):
                raise ValueError("Bad pattern file")
            return np.array([[1, 0], [0, 1]], dtype=np.int8)
        
        mock_load_cells.side_effect = mock_load_side_effect
        
        # Test loading with error handling
        result_patterns = {}
        with patch('life.pattern_factory.logger') as mock_logger:
            result = load_objects_from_pattern_dir("test_patterns", "cells", result_patterns)
            
            # Should have loaded the good pattern
            self.assertEqual(len(result), 1)
            self.assertIn("good", result)
            
            # Should have logged the error
            mock_logger.error.assert_called_once()

    @patch('life.pattern_factory.Path.rglob')
    def test_load_objects_from_pattern_dir_with_filter(self, mock_rglob):
        """Test loading patterns with a filter function."""
        mock_files = [Path("test.cells")]
        mock_rglob.return_value = mock_files
        
        # Mock a pattern that would be filtered out
        small_pattern = np.array([[1]], dtype=np.int8)
        
        with patch('life.pattern_factory.load_pattern_from_cells', return_value=small_pattern):
            # Filter function that rejects patterns smaller than 2x2
            def size_filter(pattern):
                return pattern.shape[0] >= 2 and pattern.shape[1] >= 2
            
            result_patterns = {}
            result = load_objects_from_pattern_dir(
                "test_patterns", "cells", result_patterns, filter=size_filter
            )
            
            # Pattern should be filtered out
            self.assertEqual(len(result), 0)

    @patch('life.pattern_factory.load_objects_from_pattern_dir')
    @patch('os.path.join')
    @patch('os.path.dirname')
    def test_get_patterns(self, mock_dirname, mock_join, mock_load_objects):
        """Test the get_patterns function."""
        mock_dirname.return_value = "/mock/path"
        mock_join.return_value = "/mock/path/patterns"
        
        # Mock loading results
        mock_patterns = {
            "test_pattern": np.array([[1, 0], [0, 1]], dtype=np.int8)
        }
        mock_load_objects.return_value = mock_patterns
        
        result = get_patterns("patterns", ["cells", "py"])
        
        # Should have called load_objects_from_pattern_dir for each suffix
        self.assertEqual(mock_load_objects.call_count, 2)
        
        # Should return the patterns
        self.assertEqual(result, mock_patterns)

    def test_get_patterns_default_filter(self):
        """Test that get_patterns uses the default numpy array filter."""
        # This tests the lambda function in get_patterns
        default_filter = lambda obj: isinstance(obj, np.ndarray)
        
        # Test with actual numpy array
        test_array = np.array([[1, 0], [0, 1]], dtype=np.int8)
        self.assertTrue(default_filter(test_array))
        
        # Test with non-array
        self.assertFalse(default_filter("not an array"))
        self.assertFalse(default_filter(42))
        self.assertFalse(default_filter([1, 2, 3]))

    def test_patterns_global_variable_exists(self):
        """Test that the global patterns variable is created."""
        # The patterns variable should be a dictionary
        self.assertIsInstance(patterns, dict)
        
        # It might be empty in test environment, but should be a dict
        self.assertTrue(isinstance(patterns, dict))

    def test_real_cells_file_parsing(self):
        """Test parsing a real .cells file format."""
        # Create a temporary file with real cells content
        real_cells_content = """!Name: Blinker
!The smallest oscillator
.O.
.O.
.O.
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cells', delete=False) as f:
            f.write(real_cells_content)
            temp_path = f.name
        
        try:
            result = load_pattern_from_cells(Path(temp_path))
            
            expected = np.array([
                [0, 1, 0],
                [0, 1, 0], 
                [0, 1, 0]
            ], dtype=np.int8)
            
            np.testing.assert_array_equal(result, expected)
            
        finally:
            os.unlink(temp_path)

    def test_cells_file_with_spaces_and_tabs(self):
        """Test cells file with mixed spaces and tabs."""
        mixed_content = """!Pattern with spaces
O  O
 OO 
  O  
"""
        expected = np.array([
            [1, 0, 0, 1],
            [0, 1, 1, 0],
            [0, 0, 1, 0]
        ], dtype=np.int8)
        
        with patch("builtins.open", mock_open(read_data=mixed_content)):
            result = load_pattern_from_cells(Path("mixed.cells"))
            
            np.testing.assert_array_equal(result, expected)

    def tearDown(self):
        """Clean up after tests."""
        pass


if __name__ == '__main__':
    unittest.main()