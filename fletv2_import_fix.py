#!/usr/bin/env python3
"""
Fix for the 'No module named utils.debug_setup' error.

This script can be imported at the beginning of any script that needs to import
FletV2 modules to ensure the Python path is set up correctly.
"""

import os
import sys

def fix_fletv2_imports():
    """
    Fix FletV2 imports by ensuring the correct paths are in sys.path.
    
    This function should be called before importing any FletV2 modules.
    """
    # Get the directory containing this script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're in the FletV2 directory
    if os.path.basename(current_dir) == 'FletV2':
        fletv2_dir = current_dir
    else:
        # Look for FletV2 directory in current directory
        fletv2_dir = os.path.join(current_dir, 'FletV2')
        if not os.path.exists(fletv2_dir):
            # Try looking in parent directory
            fletv2_dir = os.path.join(os.path.dirname(current_dir), 'FletV2')
    
    # Add FletV2 to Python path if found
    if os.path.exists(fletv2_dir) and fletv2_dir not in sys.path:
        sys.path.insert(0, fletv2_dir)
        print(f"Added FletV2 to Python path: {fletv2_dir}")
        
        # Also add FletV2/utils to path for direct imports
        utils_dir = os.path.join(fletv2_dir, 'utils')
        if os.path.exists(utils_dir) and utils_dir not in sys.path:
            sys.path.insert(0, utils_dir)
            print(f"Added FletV2/utils to Python path: {utils_dir}")

# Apply the fix automatically when this module is imported
fix_fletv2_imports()

# Example usage:
# from fletv2_import_fix import fix_fletv2_imports
# fix_fletv2_imports()  # Call this before importing FletV2 modules
# from utils.debug_setup import setup_terminal_debugging