import unittest


class TestBasicFunctionality(unittest.TestCase):
    """Basic tests that don't require external dependencies."""

    def test_python_basics(self):
        """Test basic Python functionality."""
        self.assertEqual(2 + 2, 4)
        self.assertTrue(True)
        self.assertFalse(False)

    def test_list_operations(self):
        """Test basic list operations."""
        test_list = [1, 2, 3]
        self.assertEqual(len(test_list), 3)
        self.assertIn(2, test_list)
        self.assertNotIn(4, test_list)

    def test_string_operations(self):
        """Test basic string operations."""
        test_string = "Conway's Game of Life"
        self.assertIn("Conway", test_string)
        self.assertIn("Life", test_string)
        self.assertEqual(test_string.lower().count("life"), 1)

    def test_dictionary_operations(self):
        """Test basic dictionary operations."""
        test_dict = {"theme": "matrix", "size": 100}
        self.assertEqual(test_dict["theme"], "matrix")
        self.assertEqual(test_dict["size"], 100)
        self.assertIn("theme", test_dict)

    def test_exception_handling(self):
        """Test exception handling."""
        with self.assertRaises(ValueError):
            int("not_a_number")
        
        with self.assertRaises(KeyError):
            {}["nonexistent_key"]

    def test_function_definition(self):
        """Test that we can define and call functions."""
        def add_numbers(a, b):
            return a + b
        
        result = add_numbers(3, 4)
        self.assertEqual(result, 7)

    def test_class_definition(self):
        """Test that we can define and use classes."""
        class TestClass:
            def __init__(self, value):
                self.value = value
            
            def get_value(self):
                return self.value
        
        obj = TestClass(42)
        self.assertEqual(obj.get_value(), 42)

    def test_import_system(self):
        """Test that Python import system works."""
        import os
        import sys
        
        self.assertTrue(hasattr(os, 'path'))
        self.assertTrue(hasattr(sys, 'path'))

    def test_file_path_operations(self):
        """Test file path operations without actually creating files."""
        import os
        
        # Test path joining
        path = os.path.join("tests", "test_file.py")
        self.assertIn("tests", path)
        self.assertIn("test_file.py", path)

    def test_mock_patterns(self):
        """Test basic mock patterns for later use."""
        # Simple mock-like behavior
        class MockObject:
            def __init__(self):
                self.called = False
                self.call_count = 0
            
            def mock_method(self):
                self.called = True
                self.call_count += 1
                return "mocked_result"
        
        mock = MockObject()
        result = mock.mock_method()
        
        self.assertTrue(mock.called)
        self.assertEqual(mock.call_count, 1)
        self.assertEqual(result, "mocked_result")


if __name__ == '__main__':
    unittest.main()