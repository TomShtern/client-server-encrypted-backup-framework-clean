#!/usr/bin/env python3
"""
Absolutely minimal test to verify Flet is working at all.
"""

import flet as ft

def minimal_test(page: ft.Page):
    """Minimal test with just basic text."""
    print("Creating minimal test page...")

    page.title = "Minimal Test"
    page.theme_mode = ft.ThemeMode.SYSTEM

    # Add very simple, visible content
    page.add(
        ft.Column([
            ft.Text("🔴 HELLO WORLD - RED TEXT", size=32, color=ft.Colors.RED, weight=ft.FontWeight.BOLD),
            ft.Text("🟢 This is GREEN text", size=24, color=ft.Colors.GREEN),
            ft.Text("🔵 This is BLUE text", size=16, color=ft.Colors.BLUE),
            ft.ElevatedButton("TEST BUTTON", bgcolor=ft.Colors.YELLOW),
            ft.Container(
                content=ft.Text("WHITE TEXT ON BLACK", color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLACK,
                padding=20,
                border=ft.border.all(3, ft.Colors.RED)
            )
        ], spacing=20)
    )

    print("Minimal test content added to page")

if __name__ == "__main__":
    import os
    print("Starting absolutely minimal Flet test (WEB_BROWSER mode)...")
    print("Env Flags:")
    for k in ["CYBERBACKUP_DISABLE_INTEGRATED_GUI", "CYBERBACKUP_DISABLE_GUI", "FLET_DASHBOARD_DEBUG"]:
        print(f"  {k}={os.environ.get(k)}")
    ft.app(target=minimal_test, view=ft.AppView.WEB_BROWSER, port=8560)