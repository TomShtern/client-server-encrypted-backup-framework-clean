#!/usr/bin/env python3
"""
Minimal dashboard test to check if anything displays.
"""

import os
import sys

# Add the FletV2 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set debug mode
os.environ['FLET_DASHBOARD_DEBUG'] = '1'

def create_minimal_dashboard():
    """Create a minimal dashboard with just visible text."""
    import flet as ft

    # Create a simple visible dashboard
    minimal_content = ft.Container(
        content=ft.Column([
            ft.Text("🚀 DASHBOARD LOADED SUCCESSFULLY", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
            ft.Text("If you can see this, the dashboard system works", size=18, color=ft.Colors.BLUE),
            ft.Text("Hero metrics should appear below:", size=16, color=ft.Colors.GREEN),
            # Add some test hero metrics
            ft.Container(
                content=ft.Text("Total Clients: 5", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
                padding=20,
                border_radius=12,
                margin=ft.margin.symmetric(vertical=10)
            ),
            ft.Container(
                content=ft.Text("Active Transfers: 2", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
                padding=20,
                border_radius=12,
                margin=ft.margin.symmetric(vertical=10)
            ),
            ft.Container(
                content=ft.Text("Server Uptime: 1h 30m", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PURPLE),
                padding=20,
                border_radius=12,
                margin=ft.margin.symmetric(vertical=10)
            )
        ], spacing=20),
        padding=40,
        expand=True
    )

    def dispose():
        pass

    def setup():
        pass

    return minimal_content, dispose, setup

def test_minimal_dashboard():
    """Test the minimal dashboard."""
    try:
        result = create_minimal_dashboard()
        print("✅ Minimal dashboard created successfully")
        print(f"Result type: {type(result)}")
        if isinstance(result, tuple) and len(result) >= 1:
            container = result[0]
            print(f"Container type: {type(container)}")
            print("✅ Minimal dashboard test passed")
        else:
            print("❌ Unexpected result format")
    except Exception as e:
        print(f"❌ Error creating minimal dashboard: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_minimal_dashboard()