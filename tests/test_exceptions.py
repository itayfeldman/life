import unittest
from unittest.mock import patch

from life.exceptions import (
    LifeParamsError,
    SizeTypeError,
    SizeValueError,
    SeedValueError,
    validate_args,
    MINSIZE,
    MAXSIZE
)


class TestExceptions(unittest.TestCase):
    """Test cases for the exceptions module."""

    def test_life_params_error_base_class(self):
        """Test LifeParamsError base exception class."""
        # Test with custom message
        error = LifeParamsError("Custom error message")
        self.assertEqual(str(error), "Custom error message")
        self.assertIsInstance(error, Exception)
        
        # Test with default message
        error_default = LifeParamsError()
        self.assertEqual(str(error_default), "")

    def test_size_type_error(self):
        """Test SizeTypeError for invalid size types."""
        # Test with string
        error = SizeTypeError("50")
        self.assertIn("integer", str(error))
        self.assertIn("50", str(error))
        self.assertIsInstance(error, LifeParamsError)
        
        # Test with float
        error_float = SizeTypeError(50.5)
        self.assertIn("integer", str(error_float))
        self.assertIn("50.5", str(error_float))
        
        # Test with None
        error_none = SizeTypeError(None)
        self.assertIn("integer", str(error_none))
        self.assertIn("None", str(error_none))

    def test_size_value_error(self):
        """Test SizeValueError for invalid size values."""
        # Test with too small value
        error_small = SizeValueError(5)
        self.assertIn(str(MINSIZE), str(error_small))
        self.assertIn(str(MAXSIZE), str(error_small))
        self.assertIn("5", str(error_small))
        self.assertIsInstance(error_small, LifeParamsError)
        
        # Test with too large value
        error_large = SizeValueError(2000)
        self.assertIn(str(MINSIZE), str(error_large))
        self.assertIn(str(MAXSIZE), str(error_large))
        self.assertIn("2000", str(error_large))

    def test_seed_value_error(self):
        """Test SeedValueError for invalid seed values."""
        error = SeedValueError("invalid_seed")
        self.assertIn("invalid_seed", str(error))
        self.assertIsInstance(error, LifeParamsError)
        
        # Should mention available patterns
        error_msg = str(error)
        self.assertTrue(any(word in error_msg.lower() for word in ["seed", "pattern"]))

    def test_minsize_maxsize_constants(self):
        """Test that MINSIZE and MAXSIZE constants are properly defined."""
        self.assertIsInstance(MINSIZE, int)
        self.assertIsInstance(MAXSIZE, int)
        self.assertGreater(MINSIZE, 0)
        self.assertGreater(MAXSIZE, MINSIZE)
        
        # Test expected values
        self.assertEqual(MINSIZE, 10)
        self.assertEqual(MAXSIZE, 1000)

    def test_validate_args_valid_inputs(self):
        """Test validate_args with valid inputs."""
        # Test valid size and seed
        try:
            validate_args(50, "noise")
            validate_args(MINSIZE, "symmetric")
            validate_args(MAXSIZE, "any_seed")
        except Exception as e:
            self.fail(f"validate_args raised {type(e).__name__} unexpectedly: {e}")

    def test_validate_args_invalid_size_type(self):
        """Test validate_args with invalid size types."""
        # String size
        with self.assertRaises(SizeTypeError):
            validate_args("50", "noise")
        
        # Float size
        with self.assertRaises(SizeTypeError):
            validate_args(50.5, "noise")
        
        # None size
        with self.assertRaises(SizeTypeError):
            validate_args(None, "noise")
        
        # List size
        with self.assertRaises(SizeTypeError):
            validate_args([50], "noise")

    def test_validate_args_invalid_size_value(self):
        """Test validate_args with invalid size values."""
        # Too small
        with self.assertRaises(SizeValueError):
            validate_args(5, "noise")
        
        with self.assertRaises(SizeValueError):
            validate_args(MINSIZE - 1, "noise")
        
        # Too large
        with self.assertRaises(SizeValueError):
            validate_args(MAXSIZE + 1, "noise")
        
        with self.assertRaises(SizeValueError):
            validate_args(2000, "noise")
        
        # Negative
        with self.assertRaises(SizeValueError):
            validate_args(-10, "noise")

    def test_validate_args_boundary_values(self):
        """Test validate_args with boundary values."""
        # Minimum valid size
        try:
            validate_args(MINSIZE, "noise")
        except Exception as e:
            self.fail(f"MINSIZE should be valid but raised: {e}")
        
        # Maximum valid size
        try:
            validate_args(MAXSIZE, "noise")
        except Exception as e:
            self.fail(f"MAXSIZE should be valid but raised: {e}")

    def test_validate_args_seed_validation_commented_out(self):
        """Test that seed validation is currently commented out."""
        # The seed validation is commented out in the current code
        # So any seed should be accepted
        try:
            validate_args(50, "invalid_seed_that_should_fail")
            validate_args(50, "")
            validate_args(50, None)
        except SeedValueError:
            self.fail("Seed validation should be commented out")
        except Exception as e:
            # Other exceptions might be raised, but not SeedValueError
            if isinstance(e, SeedValueError):
                self.fail("SeedValueError should not be raised when validation is commented out")

    def test_error_message_formatting(self):
        """Test that error messages are properly formatted."""
        # Test SizeTypeError message
        error = SizeTypeError(42.5)
        msg = str(error)
        self.assertIn("integer", msg)
        self.assertIn("42.5", msg)
        
        # Test SizeValueError message  
        error = SizeValueError(5)
        msg = str(error)
        self.assertIn(str(MINSIZE), msg)
        self.assertIn(str(MAXSIZE), msg)
        self.assertIn("5", msg)
        
        # Test SeedValueError message
        error = SeedValueError("bad_seed")
        msg = str(error)
        self.assertIn("bad_seed", msg)

    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from LifeParamsError."""
        self.assertTrue(issubclass(SizeTypeError, LifeParamsError))
        self.assertTrue(issubclass(SizeValueError, LifeParamsError))
        self.assertTrue(issubclass(SeedValueError, LifeParamsError))
        
        # And LifeParamsError inherits from Exception
        self.assertTrue(issubclass(LifeParamsError, Exception))

    def test_validate_args_type_checking_order(self):
        """Test that type checking happens before value checking."""
        # Type error should be raised before value error
        with self.assertRaises(SizeTypeError):
            validate_args("5", "noise")  # String "5" is invalid type, even though 5 would be invalid value

    def test_error_constants_used_in_messages(self):
        """Test that error messages use the defined constants."""
        error = SizeValueError(5)
        msg = str(error)
        
        # Should contain the actual constant values
        self.assertIn("10", msg)  # MINSIZE
        self.assertIn("1000", msg)  # MAXSIZE

    @patch('life.exceptions.patterns', {'blinker': 'mock_pattern', 'glider': 'mock_pattern'})
    def test_seed_error_message_with_patterns(self, ):
        """Test SeedValueError message includes available patterns."""
        error = SeedValueError("invalid")
        msg = str(error)
        
        # Should mention available patterns
        self.assertIn("blinker", msg)
        self.assertIn("glider", msg)

    def test_validate_args_comprehensive(self):
        """Test validate_args with comprehensive input combinations."""
        # Valid combinations
        valid_combinations = [
            (10, "noise"),
            (50, "symmetric"), 
            (100, "pattern_name"),
            (1000, ""),
            (500, None)  # None seed might be valid
        ]
        
        for size, seed in valid_combinations:
            try:
                validate_args(size, seed)
            except (SizeTypeError, SizeValueError):
                self.fail(f"Valid combination ({size}, {seed}) should not raise exception")
            except SeedValueError:
                # Seed validation is commented out, so this shouldn't happen
                pass

    def tearDown(self):
        """Clean up after tests."""
        pass


if __name__ == '__main__':
    unittest.main()