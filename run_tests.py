#!/usr/bin/env python3
"""
Test runner for Conway's Game of Life unit tests.

This script runs all unit tests and provides a comprehensive test report.
"""

import unittest
import sys
import os
from io import StringIO

# Add src directory to path so we can import life modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def run_tests():
    """Run all unit tests and return results."""
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.join(os.path.dirname(__file__), 'tests')
    
    # Discover all test files
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Create a test runner with detailed output
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        failfast=False,
        buffer=True
    )
    
    # Run the tests
    print("🧪 Running Conway's Game of Life Unit Tests\n")
    print("=" * 60)
    
    # Also run with console output
    console_runner = unittest.TextTestRunner(verbosity=2)
    result = console_runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    
    print(f"Total Tests Run: {total_tests}")
    print(f"✅ Passed: {total_tests - failures - errors - skipped}")
    print(f"❌ Failed: {failures}")
    print(f"🔥 Errors: {errors}")
    print(f"⏭️  Skipped: {skipped}")
    
    if failures == 0 and errors == 0:
        print("\n🎉 ALL TESTS PASSED!")
        success = True
    else:
        print(f"\n⚠️  {failures + errors} TESTS FAILED")
        success = False
    
    # Print detailed failure information
    if result.failures:
        print("\n" + "=" * 60)
        print("❌ FAILURE DETAILS")
        print("=" * 60)
        for test, traceback in result.failures:
            print(f"\nFAILED: {test}")
            print("-" * 40)
            print(traceback)
    
    if result.errors:
        print("\n" + "=" * 60)
        print("🔥 ERROR DETAILS")
        print("=" * 60)
        for test, traceback in result.errors:
            print(f"\nERROR: {test}")
            print("-" * 40)
            print(traceback)
    
    return success

def run_specific_test_module(module_name):
    """Run tests for a specific module."""
    print(f"🔍 Running tests for {module_name}")
    
    # Import the specific test module
    try:
        test_module = __import__(f'tests.{module_name}', fromlist=[module_name])
        
        # Create test suite from the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # Run the tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except ImportError as e:
        print(f"❌ Could not import test module {module_name}: {e}")
        return False

def main():
    """Main test runner function."""
    if len(sys.argv) > 1:
        # Run specific test module
        module_name = sys.argv[1]
        if not module_name.startswith('test_'):
            module_name = f'test_{module_name}'
        
        success = run_specific_test_module(module_name)
    else:
        # Run all tests
        success = run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()