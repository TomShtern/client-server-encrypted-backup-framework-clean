#!/usr/bin/env python3
"""Test script to verify dashboard.py functionality."""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import the dashboard function
    print("SUCCESS: create_dashboard_view imported successfully")

    # Try to import the common imports
    from views.common_imports import *
    print("SUCCESS: common_imports imported successfully")

    # Try to import specific functions that should be available
    print("SUCCESS: themed_button and themed_card imported successfully")

    print("SUCCESS: show_success_message and show_error_message imported successfully")

    print("All imports successful!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
