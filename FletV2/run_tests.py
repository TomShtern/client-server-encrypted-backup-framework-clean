#!/usr/bin/env python3
"""
Script to run tests from the project root directory.
This script ensures the correct Python path is set up to find all modules.
"""

import os
import sys
import unittest

def setup_test_environment():
    """Set up the testing environment with proper paths."""
    # Get the directory containing this script (FletV2 directory)
    fletv2_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add FletV2 to Python path
    if fletv2_dir not in sys.path:
        sys.path.insert(0, fletv2_dir)
        print(f"Added FletV2 directory to path: {fletv2_dir}")
    
    # Add project root to Python path
    project_root = os.path.dirname(fletv2_dir)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        print(f"Added project root to path: {project_root}")

# Set up the environment
setup_test_environment()

# Import and run tests
if __name__ == '__main__':
    try:
        # Discover and run tests
        loader = unittest.TestLoader()
        fletv2_dir = os.path.dirname(os.path.abspath(__file__))
        start_dir = os.path.join(fletv2_dir, 'tests')
        print(f"Discovering tests in: {start_dir}")
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Exit with error code if tests failed
        sys.exit(0 if result.wasSuccessful() else 1)
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)