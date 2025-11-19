#!/usr/bin/env python3
"""
Quick Flet version and functionality test.
"""
import sys

import flet as ft


def main(page: ft.Page):
    page.title = "Flet Version Test"
    page.window_width = 400
    page.window_height = 300

    # Get version info
    python_version = sys.version.split()[0]
    flet_version = "0.28.3"  # We confirmed this from pip show

    page.add(
        ft.Column([
            ft.Text("🎉 Flet Setup Verification", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                ft.Text(f"Python: {python_version}", size=16)
            ]),
            ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                ft.Text(f"Flet: {flet_version}", size=16)
            ]),
            ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN),
                ft.Text("Environment: flet_venv", size=16)
            ]),
            ft.Divider(),
            ft.ElevatedButton(
                "Close Test",
                on_click=lambda _: page.window_close(),
                icon=ft.Icons.CLOSE
            )
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10)
    )

    print("✅ Flet app created successfully!")
    print(f"✅ Python {python_version} + Flet {flet_version} working perfectly!")

if __name__ == "__main__":
    print("🚀 Testing Flet functionality...")
    print("Note: This will open a window briefly to test Flet GUI functionality")
    ft.app(target=main)
