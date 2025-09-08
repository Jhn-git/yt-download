#!/usr/bin/env python3
"""
Test runner script for yt-download project.

This script provides a convenient way to run tests with various options.
It uses Python's built-in unittest framework.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py -v               # Run with verbose output
    python run_tests.py test_config       # Run specific test module
    python run_tests.py --help            # Show help
"""

import sys
import unittest
import argparse
from pathlib import Path

# Add the project root and src to Python path so we can import modules
project_root = Path(__file__).parent.parent  # Go up one level from tools/ to project root
src_path = project_root / "src"
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))


def discover_and_run_tests(test_pattern=None, verbosity=1, failfast=False):
    """
    Discover and run tests using unittest's discovery mechanism.
    
    Args:
        test_pattern: Specific test pattern to run (e.g., 'test_config')
        verbosity: Verbosity level (0=quiet, 1=normal, 2=verbose)
        failfast: Stop on first failure
    
    Returns:
        Test result object
    """
    # Configure test discovery
    loader = unittest.TestLoader()
    
    if test_pattern:
        # Load specific test module
        try:
            if test_pattern.startswith('test_'):
                module_name = f"tests.{test_pattern}"
            else:
                module_name = f"tests.test_{test_pattern}"
            
            suite = loader.loadTestsFromName(module_name)
        except (ImportError, AttributeError) as e:
            print(f"Error loading test module '{test_pattern}': {e}")
            print(f"Available test modules:")
            list_available_tests()
            return False
    else:
        # Discover all tests in the tests directory
        test_dir = project_root / 'tests'
        suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    # Configure test runner
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        failfast=failfast,
        buffer=True  # Capture stdout/stderr during tests
    )
    
    # Run tests
    result = runner.run(suite)
    
    return result.wasSuccessful()


def list_available_tests():
    """List all available test modules."""
    tests_dir = project_root / 'tests'
    test_files = list(tests_dir.glob('test_*.py'))
    
    print("Available test modules:")
    for test_file in sorted(test_files):
        module_name = test_file.stem
        print(f"  - {module_name}")
        
        # Try to get test class names
        try:
            module_path = f"tests.{module_name}"
            module = __import__(module_path, fromlist=[''])
            
            test_classes = [
                name for name in dir(module)
                if name.startswith('Test') and hasattr(getattr(module, name), '__bases__')
            ]
            
            if test_classes:
                for test_class in test_classes:
                    print(f"    - {test_class}")
        except ImportError:
            pass
    
    print("\nExample usage:")
    print("  python run_tests.py                    # Run all tests")
    print("  python run_tests.py config             # Run tests/test_config.py")
    print("  python run_tests.py test_downloader    # Run tests/test_downloader.py")
    print("  python run_tests.py -v                 # Run all tests with verbose output")


def check_test_environment():
    """Check that the test environment is properly set up."""
    issues = []
    
    # Check that core modules can be imported
    try:
        from ytdl.core.config import ConfigService
        from ytdl.core.logger import LoggerService
        from ytdl.core.downloader import DownloaderService
        from ytdl.core.cli import CLIService
    except ImportError as e:
        issues.append(f"Cannot import core modules: {e}")
    
    # Check that tests directory exists
    tests_dir = project_root / 'tests'
    if not tests_dir.exists():
        issues.append(f"Tests directory not found: {tests_dir}")
    
    # Check for test files
    test_files = list(tests_dir.glob('test_*.py'))
    if not test_files:
        issues.append("No test files found in tests directory")
    
    return issues


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Test runner for yt-download project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py -v                 # Run all tests with verbose output
  python run_tests.py config             # Run ConfigService tests
  python run_tests.py test_downloader    # Run DownloaderService tests
  python run_tests.py --list             # List available test modules
  python run_tests.py --failfast         # Stop on first failure
        """
    )
    
    parser.add_argument(
        'test_pattern',
        nargs='?',
        help='Specific test module to run (e.g., config, downloader, test_cli)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose test output'
    )
    
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet test output (minimal)'
    )
    
    parser.add_argument(
        '--failfast',
        action='store_true',
        help='Stop on first test failure'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available test modules and exit'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check test environment and exit'
    )
    
    args = parser.parse_args()
    
    # Handle special flags
    if args.list:
        list_available_tests()
        return 0
    
    if args.check:
        print("Checking test environment...")
        issues = check_test_environment()
        if issues:
            print("Issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return 1
        else:
            print("Test environment looks good!")
            return 0
    
    # Determine verbosity level
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1
    
    # Check environment before running tests
    issues = check_test_environment()
    if issues:
        print("Test environment issues found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nUse --check flag for more details.")
        return 1
    
    # Run tests
    print("Running yt-download tests...")
    if args.test_pattern:
        print(f"Test pattern: {args.test_pattern}")
    
    try:
        success = discover_and_run_tests(
            test_pattern=args.test_pattern,
            verbosity=verbosity,
            failfast=args.failfast
        )
        
        if success:
            print("\n✅ All tests passed!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
            
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        return 130
    except Exception as e:
        print(f"\nUnexpected error running tests: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())