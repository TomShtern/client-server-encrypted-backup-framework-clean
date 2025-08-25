#!/usr/bin/env python3
"""
Launch script for Flet Server GUI
Runs the Material Design 3 desktop application.
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import utf8_solution to fix encoding issues
try:
    import Shared.utils.utf8_solution
    print("[INFO] UTF-8 solution imported successfully")
except ImportError as e:
    # Try alternative path
    utf8_path = os.path.join(os.path.dirname(__file__), "Shared", "utils")
    if utf8_path not in sys.path:
        sys.path.insert(0, utf8_path)
    try:
        import utf8_solution
        print("[INFO] UTF-8 solution imported via alternative path")
    except ImportError:
        print("[WARNING] utf8_solution import failed, continuing without it")
        print(f"[DEBUG] Import error: {e}")

try:
    # Import and run the Flet GUI
    from flet_server_gui.main import main
    import flet as ft
    
    print("=" * 60)
    print("Starting Flet Material Design 3 Server GUI")
    print("=" * 60)
    print("Framework: Flet (Flutter-powered)")
    print("Design: Material Design 3")
    print("Platform: Desktop Application")
    print("Theme: Dark mode with dynamic switching")
    print("Navigation: Multi-screen navigation rail")
    print("=" * 60)
    
    if len(sys.argv) > 1 and "--web" in sys.argv:
        print("Running as web application...")
        ft.app(target=main, view=ft.WEB_BROWSER, port=8550)
    else:
        print("Running as desktop application...")
        ft.app(target=main)

except ImportError as e:
    print(f"Import Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure you're in the correct virtual environment:")
    print("   .\\flet_venv\\Scripts\\activate")
    print("2. Install Flet if not installed:")
    print("   pip install flet")
    print("3. Check if all required files exist in flet_server_gui/")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nCheck the error details above and ensure all components are properly installed.")