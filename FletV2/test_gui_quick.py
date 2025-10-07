#!/usr/bin/env python3
"""Quick GUI diagnostic test to check view loading and navigation."""

import os
import sys

# Add paths
_flet_v2_root = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Disable server GUI
os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'
os.environ['CYBERBACKUP_DISABLE_GUI'] = '1'

import flet as ft

def main(page: ft.Page):
    """Quick diagnostic GUI."""

    page.title = "GUI Diagnostic Test"
    page.window.width = 1200
    page.window.height = 800

    # Status text
    status_text = ft.Text("Testing GUI components...", size=16)

    # Test creating views
    test_results = []

    def test_view_imports():
        """Test if views can be imported and created."""
        results = []

        views_to_test = [
            ("dashboard", "views.dashboard", "create_dashboard_view"),
            ("clients", "views.clients", "create_clients_view"),
            ("files", "views.files", "create_files_view"),
            ("database", "views.database", "create_database_view"),
        ]

        for view_name, module_name, function_name in views_to_test:
            try:
                module = __import__(module_name, fromlist=[function_name])
                if hasattr(module, function_name):
                    results.append(f"✅ {view_name}: imports OK")
                else:
                    results.append(f"❌ {view_name}: missing function")
            except Exception as e:
                results.append(f"❌ {view_name}: {str(e)[:50]}")

        return results

    def test_navigation_rail():
        """Test navigation rail creation."""
        try:
            nav = ft.NavigationRail(
                selected_index=0,
                destinations=[
                    ft.NavigationRailDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),
                    ft.NavigationRailDestination(icon=ft.Icons.PEOPLE, label="Clients"),
                ],
                on_change=lambda e: None
            )
            return "✅ NavigationRail: creates OK"
        except Exception as e:
            return f"❌ NavigationRail: {str(e)[:50]}"

    def test_animated_switcher():
        """Test AnimatedSwitcher."""
        try:
            switcher = ft.AnimatedSwitcher(
                content=ft.Text("Test content"),
                transition=ft.AnimatedSwitcherTransition.FADE,
                duration=200
            )
            return "✅ AnimatedSwitcher: creates OK"
        except Exception as e:
            return f"❌ AnimatedSwitcher: {str(e)[:50]}"

    def run_diagnostics(e):
        """Run all diagnostic tests."""
        results = []

        results.append("=== Import Tests ===")
        results.extend(test_view_imports())

        results.append("\n=== Component Tests ===")
        results.append(test_navigation_rail())
        results.append(test_animated_switcher())

        # Update status
        status_text.value = "\n".join(results)
        page.update()

    # UI
    run_button = ft.ElevatedButton("Run Diagnostics", on_click=run_diagnostics)

    page.add(
        ft.Column([
            ft.Text("FletV2 GUI Diagnostic Test", size=24, weight=ft.FontWeight.BOLD),
            run_button,
            ft.Divider(),
            status_text
        ], spacing=20, scroll="auto")
    )

    # Auto-run on start
    run_diagnostics(None)

if __name__ == "__main__":
    ft.app(target=main)
