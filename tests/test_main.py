import unittest
from unittest.mock import patch, Mock, MagicMock
import sys
from io import StringIO

# We need to be careful testing __main__ since it executes code on import
# We'll test the components that can be tested safely


class TestMainModule(unittest.TestCase):
    """Test cases for the main module functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.original_argv = sys.argv.copy()

    def tearDown(self):
        """Clean up after tests."""
        sys.argv = self.original_argv

    @patch('life.__main__.plt.show')
    @patch('life.__main__.Animator')
    @patch('life.__main__.Life')
    def test_function_map_exists(self, mock_life, mock_animator, mock_show):
        """Test that FUNCTION_MAP contains all expected functions."""
        # Import the module to get access to FUNCTION_MAP
        import life.__main__ as main_module
        
        expected_functions = [
            'convolution', 'window', 'loop', 
            'fast', 'ultra_fast', 'vectorized'
        ]
        
        for func_name in expected_functions:
            self.assertIn(func_name, main_module.FUNCTION_MAP)
            self.assertTrue(callable(main_module.FUNCTION_MAP[func_name]))

    @patch('life.__main__.plt.show')
    @patch('life.__main__.Animator')
    @patch('life.__main__.Life')
    @patch('sys.argv', ['life', '--help'])
    def test_argument_parser_help(self, mock_life, mock_animator, mock_show):
        """Test that argument parser has help functionality."""
        # This test is tricky because --help causes sys.exit()
        # We'll test that the parser exists and has the expected arguments
        import life.__main__ as main_module
        
        # Check that parser exists
        self.assertTrue(hasattr(main_module, 'parser'))
        
        # Check that parser has the expected arguments
        parser = main_module.parser
        
        # Get all action destinations
        action_dests = [action.dest for action in parser._actions if action.dest != 'help']
        
        expected_args = [
            'size', 'seed', 'interval', 'cmap', 'figsize', 
            'func', 'theme', 'show_stats', 'fullscreen'
        ]
        
        for expected_arg in expected_args:
            self.assertIn(expected_arg, action_dests)

    @patch('life.__main__.plt.show')
    @patch('life.__main__.Animator')
    @patch('life.__main__.Life')
    def test_function_map_no_eval(self, mock_life, mock_animator, mock_show):
        """Test that FUNCTION_MAP replaces eval() usage safely."""
        import life.__main__ as main_module
        
        # Ensure all functions in the map are actual function objects
        for func_name, func in main_module.FUNCTION_MAP.items():
            self.assertTrue(callable(func))
            # Should have a __name__ attribute
            self.assertTrue(hasattr(func, '__name__'))

    @patch('life.__main__.plt.show')  
    @patch('life.__main__.Animator')
    @patch('life.__main__.Life')
    @patch('sys.argv', ['life', '--size', '50', '--theme', 'matrix'])
    def test_safe_function_selection(self, mock_life, mock_animator, mock_show):
        """Test that function selection uses safe mapping instead of eval."""
        # Mock the components
        mock_life_instance = Mock()
        mock_life.return_value = mock_life_instance
        
        mock_animator_instance = Mock()
        mock_animator.return_value = mock_animator_instance
        
        # Import and let it run (with mocked components)
        try:
            import life.__main__ as main_module
        except SystemExit:
            pass  # May exit due to argument parsing
        
        # The important thing is that FUNCTION_MAP exists and is safe
        self.assertIsInstance(main_module.FUNCTION_MAP, dict)

    @patch('life.__main__.plt.show')
    @patch('life.__main__.Animator') 
    @patch('life.__main__.Life')
    def test_theme_choices(self, mock_life, mock_animator, mock_show):
        """Test that theme argument has correct choices."""
        import life.__main__ as main_module
        
        parser = main_module.parser
        
        # Find the theme argument action
        theme_action = None
        for action in parser._actions:
            if action.dest == 'theme':
                theme_action = action
                break
        
        self.assertIsNotNone(theme_action)
        
        expected_themes = ["default", "neon", "matrix", "ocean", "fire", "cyber"]
        self.assertEqual(set(theme_action.choices), set(expected_themes))

    @patch('life.__main__.plt.show')
    @patch('life.__main__.Animator')
    @patch('life.__main__.Life')
    def test_boolean_arguments(self, mock_life, mock_animator, mock_show):
        """Test that boolean arguments are configured correctly."""
        import life.__main__ as main_module
        
        parser = main_module.parser
        
        boolean_args = ['show_stats', 'fullscreen']
        
        for arg_name in boolean_args:
            action = None
            for a in parser._actions:
                if a.dest == arg_name:
                    action = a
                    break
            
            self.assertIsNotNone(action, f"Boolean argument {arg_name} not found")
            self.assertEqual(action.action, 'store_true')

    @patch('life.__main__.plt.show')
    @patch('life.__main__.Animator')
    @patch('life.__main__.Life')
    def test_default_values(self, mock_life, mock_animator, mock_show):
        """Test that default values are set correctly."""
        import life.__main__ as main_module
        
        parser = main_module.parser
        
        # Parse empty args to get defaults
        with patch('sys.argv', ['life']):
            try:
                args = parser.parse_args([])  # Parse empty argument list
                
                # Test default values
                self.assertEqual(args.size, 100)
                self.assertEqual(args.seed, "noise")
                self.assertEqual(args.interval, 350)
                self.assertEqual(args.cmap, "binary")
                self.assertEqual(args.figsize, 8)
                self.assertEqual(args.func, "fast")
                self.assertEqual(args.theme, "default")
                self.assertFalse(args.show_stats)
                self.assertFalse(args.fullscreen)
                
            except SystemExit:
                # Parser might exit, that's okay for this test
                pass

    @patch('builtins.print')
    @patch('life.__main__.plt.show')
    @patch('life.__main__.Animator')
    @patch('life.__main__.Life')
    @patch('sys.argv', ['life', '--size', '50'])
    def test_console_output(self, mock_life, mock_animator, mock_show, mock_print):
        """Test that the enhanced console output is generated."""
        mock_life_instance = Mock()
        mock_life.return_value = mock_life_instance
        
        mock_animator_instance = Mock()
        mock_animator.return_value = mock_animator_instance
        
        try:
            # Re-import to trigger execution
            import importlib
            import life.__main__ as main_module
            importlib.reload(main_module)
        except SystemExit:
            pass
        
        # Should have printed the enhanced console messages
        self.assertTrue(mock_print.called)
        
        # Check that some expected strings were printed
        printed_calls = [str(call) for call in mock_print.call_args_list]
        printed_text = ' '.join(printed_calls)
        
        # Should contain emoji and enhanced information
        expected_strings = ["Conway's Game of Life", "Enhanced Edition"]
        for expected in expected_strings:
            self.assertTrue(any(expected in call for call in printed_calls),
                          f"Expected '{expected}' in printed output")

    @patch('life.__main__.plt.show')
    @patch('life.__main__.plt.get_current_fig_manager')
    @patch('life.__main__.Animator')
    @patch('life.__main__.Life')
    @patch('sys.argv', ['life', '--fullscreen'])
    def test_fullscreen_functionality(self, mock_life, mock_animator, mock_fig_manager, mock_show):
        """Test fullscreen functionality."""
        mock_life_instance = Mock()
        mock_life.return_value = mock_life_instance
        
        mock_animator_instance = Mock()
        mock_animator.return_value = mock_animator_instance
        
        mock_manager = Mock()
        mock_fig_manager.return_value = mock_manager
        
        try:
            import importlib
            import life.__main__ as main_module
            importlib.reload(main_module)
        except SystemExit:
            pass
        
        # Should have attempted to get figure manager for fullscreen
        mock_fig_manager.assert_called_once()

    def test_import_safety(self):
        """Test that importing the main module doesn't cause issues."""
        # This test ensures that the main module can be imported without 
        # immediately executing and causing problems in the test environment
        try:
            import life.__main__
            # If we get here, the import was successful
            self.assertTrue(True)
        except Exception as e:
            # If there's an import error, we want to know about it
            self.fail(f"Failed to import life.__main__: {e}")

    @patch('life.__main__.plt.style.use')
    @patch('life.__main__.plt.show')
    @patch('life.__main__.Animator')
    @patch('life.__main__.Life')
    @patch('sys.argv', ['life', '--theme', 'matrix'])
    def test_matplotlib_style_usage(self, mock_life, mock_animator, mock_show, mock_style_use):
        """Test that matplotlib style is set for non-default themes."""
        mock_life_instance = Mock()
        mock_life.return_value = mock_life_instance
        
        mock_animator_instance = Mock()
        mock_animator.return_value = mock_animator_instance
        
        try:
            import importlib
            import life.__main__ as main_module
            importlib.reload(main_module)
        except SystemExit:
            pass
        
        # Should have called plt.style.use for non-default theme
        mock_style_use.assert_called_with('dark_background')

    def test_security_no_eval_usage(self):
        """Test that the main module doesn't use eval() anywhere."""
        import life.__main__ as main_module
        import inspect
        
        # Get the source code of the main module
        try:
            source = inspect.getsource(main_module)
            
            # Should not contain 'eval(' 
            self.assertNotIn('eval(', source, "Main module should not use eval()")
            
        except OSError:
            # If we can't get source (e.g., in some test environments), 
            # at least verify FUNCTION_MAP exists as alternative
            self.assertTrue(hasattr(main_module, 'FUNCTION_MAP'))


if __name__ == '__main__':
    unittest.main()