#!/usr/bin/env python3
"""
Test the dashboard in isolation to verify it works correctly
"""

import sys
import os

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

import flet as ft
import Shared.utils.utf8_solution as _  # noqa: F401

def main(page: ft.Page):
    page.title = "Dashboard Test"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.GREEN, use_material3=True)

    print("Starting dashboard test...")

    try:
        from views.dashboard import create_dashboard_view
        print("✅ Dashboard import successful")

        # Create dashboard
        dashboard, dispose, setup = create_dashboard_view(None, page, None)
        print(f"✅ Dashboard created: {type(dashboard)}")

        # Add to page
        page.add(dashboard)
        print("✅ Dashboard added to page")

        # Setup dashboard
        setup()
        print("✅ Dashboard setup complete")

        # Test data update
        print("Dashboard test completed successfully!")

    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        import traceback
        traceback.print_exc()

        # Show error on page
        page.add(
            ft.Container(
                content=ft.Column([
                    ft.Text("Dashboard Test Failed", size=24, color=ft.Colors.RED),
                    ft.Text(f"Error: {str(e)}", size=14),
                    ft.Text("See console for details", size=12)
                ]),
                padding=20
            )
        )

if __name__ == "__main__":
    print("Running dashboard test...")
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8553)