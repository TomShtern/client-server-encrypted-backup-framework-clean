#!/usr/bin/env python3
"""
Simple test script to verify Flet GUI can run
"""

import sys
import pytest
import os

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

# Import UTF-8 solution to fix encoding issues
try:
    import Shared.utils.utf8_solution
    print("UTF-8 solution imported successfully")
except ImportError as e:
    print("Warning: Failed to import UTF-8 solution:", e)

print("Project root:", project_root)
print("Python path:", sys.path)

# Try importing the main module
try:
    import flet as ft
    print("Flet imported successfully")
except ImportError as e:
    print("Failed to import Flet:", e)
    pytest.skip(f"Skipping legacy Flet GUI test: {e}")

# Try importing the main GUI app
try:
    from flet_server_gui.main import ServerGUIApp
    print("ServerGUIApp imported successfully")
except ImportError as e:
    print("Failed to import ServerGUIApp:", e)
    # Print more details about the error
    import traceback
    traceback.print_exc()
    pytest.fail(f"Critical import failure: {e}")

print("All imports successful!")

def main(page: ft.Page):
    page.add(ft.Text("Flet GUI Test - Imports Successful!"))
    print("Flet GUI test completed successfully")

if __name__ == "__main__":
    print("Starting Flet GUI test...")
    ft.app(target=main)