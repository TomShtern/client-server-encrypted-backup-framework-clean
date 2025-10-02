#!/usr/bin/env python3
"""
Quick test to verify dashboard display functionality.
"""

import os
import sys

# Set environment for GUI-only mode
os.environ['FLET_GUI_ONLY_MODE'] = '1'
os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'
os.environ['CYBERBACKUP_DISABLE_GUI'] = '1'

# Add path for imports
sys.path.insert(0, '.')
sys.path.insert(0, '..')

# Import UTF8 solution first
import Shared.utils.utf8_solution

import flet as ft
from views.dashboard import create_dashboard_view

def test_dashboard(page: ft.Page):
    """Test dashboard creation and display."""
    print("Testing dashboard creation...")

    page.title = "Dashboard Test"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0

    try:
        # Create dashboard with no server bridge (triggers Lorem ipsum mode)
        # Updated signature expects 'state_manager' (not _state_manager)
        dashboard_control = create_dashboard_view(
            server_bridge=None,
            page=page,
            state_manager=None
        )

        print(f"Dashboard created successfully: {type(dashboard_control)}")

        # Check if it's a tuple (control, dispose_func, setup_func)
        if isinstance(dashboard_control, tuple):
            control, dispose_func, setup_func = dashboard_control
            print(f"Dashboard control type: {type(control)}")
            print(f"Has dispose function: {dispose_func is not None}")
            print(f"Has setup function: {setup_func is not None}")

            # Add the control to the page
            page.add(control)
            print("Dashboard added to page successfully")

            # Call setup if available
            if callable(setup_func):
                try:
                    setup_func()
                    print("Dashboard setup completed")
                except Exception as setup_err:
                    print(f"Setup error (non-critical): {setup_err}")
        else:
            # Single control returned
            page.add(dashboard_control)
            print("Dashboard added to page successfully")

    except Exception as e:
        print(f"Dashboard creation failed: {e}")
        import traceback
        print(traceback.format_exc())

        # Show error message
        page.add(ft.Text(f"Dashboard Error: {e}", color=ft.Colors.RED))

if __name__ == "__main__":
    print("Starting dashboard display test...")
    ft.app(target=test_dashboard, view=ft.AppView.FLET_APP)