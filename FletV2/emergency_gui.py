#!/usr/bin/env python3
"""
Emergency GUI launcher that shows the dashboard immediately without complex initialization.
This bypasses all server bridge creation and heavy startup processes.
"""

import os
import sys

# Set up environment for safe operations
os.environ['FLET_GUI_ONLY_MODE'] = '1'
os.environ['FLET_EMERGENCY_SIMPLE_DASHBOARD'] = '1'
os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'
os.environ['CYBERBACKUP_DISABLE_GUI'] = '1'

# Fix for blank content area - bypass AnimatedSwitcher
os.environ['FLET_BYPASS_SWITCHER'] = '1'

# Add path for imports
sys.path.insert(0, '.')
sys.path.insert(0, '..')

# Import UTF8 solution first to avoid issues
import Shared.utils.utf8_solution

import flet as ft

# Direct import to avoid server bridge imports
try:
    from views.dashboard import _create_emergency_simple_dashboard
    dashboard_available = True
except ImportError:
    dashboard_available = False
    print("Warning: Emergency dashboard not available")

def main(page: ft.Page):
    """Minimal main function that shows dashboard immediately."""
    print("Emergency GUI starting...")

    # Basic page setup
    page.title = "FletV2 Dashboard (Demo Mode)"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0

    if dashboard_available:
        try:
            # Use the emergency simple dashboard directly
            dashboard_control, dispose_func, setup_func = _create_emergency_simple_dashboard(page)

            print("Emergency dashboard created successfully")

            # Add to page immediately
            page.add(dashboard_control)

            print("Emergency dashboard added to page")

            # Optional setup (non-blocking)
            if callable(setup_func):
                try:
                    setup_func()
                    print("Dashboard setup completed")
                except Exception as e:
                    print(f"Setup failed (non-critical): {e}")

        except Exception as e:
            print(f"Emergency dashboard failed: {e}")
            # Show simple error message
            page.add(ft.Text(f"Emergency Dashboard Error: {e}", color=ft.Colors.RED))
    else:
        # Ultra-minimal fallback
        page.add(ft.Column([
            ft.Text("FletV2 Dashboard", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("Emergency mode - Dashboard components not available", color=ft.Colors.AMBER),
            ft.ElevatedButton("Refresh", icon=ft.Icons.REFRESH)
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER))

if __name__ == "__main__":
    print("Starting emergency GUI...")
    try:
        # Use the correct Flet 0.28.3 syntax
        ft.app(target=main, view=ft.AppView.FLET_APP)
    except Exception as e:
        print(f"Failed to start emergency GUI: {e}")
        try:
            # Fallback for different Flet versions
            ft.app(main)
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            sys.exit(1)