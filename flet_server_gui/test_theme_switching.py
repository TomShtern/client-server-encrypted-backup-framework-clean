#!/usr/bin/env python3
"""Test theme switching functionality"""

import flet as ft
from ui.unified_theme_system import UnifiedThemeManager, ThemeMode

def main(page: ft.Page):
    # Initialize theme manager
    theme_manager = UnifiedThemeManager(page)
    
    # Create test controls
    title = ft.Text("Theme Test", size=24, weight=ft.FontWeight.BOLD)
    status_text = ft.Text("Current theme: SYSTEM", size=16)
    
    # Theme toggle button
    def toggle_theme(e):
        theme_manager.toggle_theme()
        mode = page.theme_mode
        if mode == ft.ThemeMode.DARK:
            status_text.value = "Current theme: DARK"
        elif mode == ft.ThemeMode.LIGHT:
            status_text.value = "Current theme: LIGHT"
        else:
            status_text.value = "Current theme: SYSTEM"
        page.update()
    
    toggle_button = ft.ElevatedButton("Toggle Theme", on_click=toggle_theme)
    
    # Test card with theme colors
    test_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("This card should change colors with theme", size=14),
                ft.ElevatedButton("Test Button", on_click=lambda e: print("Button clicked"))
            ]),
            padding=20
        )
    )
    
    # Layout
    page.add(
        ft.Column([
            title,
            status_text,
            toggle_button,
            test_card
        ])
    )

if __name__ == "__main__":
    ft.app(target=main)