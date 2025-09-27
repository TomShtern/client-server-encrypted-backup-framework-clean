#!/usr/bin/env python3
"""
Standalone dashboard test - shows dashboard content without full app framework.
"""

import sys
import os

# Add FletV2 to path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Import Flet
import flet as ft

# Import dashboard
from views.dashboard import create_dashboard_view

def main(page: ft.Page):
    """Simple test app that shows dashboard content."""
    page.title = "Dashboard Test"

    try:
        # Create dashboard
        print("Creating dashboard...")
        container, dispose, setup = create_dashboard_view(None, page, None)

        print(f"Dashboard created: {type(container)}")

        # Add to page
        page.add(container)

        print("Dashboard added to page")

        # Call setup
        if setup:
            setup()
            print("Dashboard setup called")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

        # Show error on page
        page.add(ft.Text(f"Error: {e}", color=ft.Colors.RED))

if __name__ == "__main__":
    ft.app(target=main)