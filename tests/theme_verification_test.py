#!/usr/bin/env python3
"""
Theme Verification Test
Simple test to verify that the custom theme is working correctly with enhanced components.
"""

import sys

# Add project root to path
sys.path.insert(0, '.')

try:
    # Import the custom theme
    import flet as ft
    from flet_server_gui.ui.theme_m3 import TOKENS, create_theme

    def main(page: ft.Page):
        page.title = "Theme Verification Test"
        page.padding = 20

        # Apply the custom theme
        theme = create_theme(use_material3=True, dark=False)
        page.theme = theme
        page.dark_theme = create_theme(use_material3=True, dark=True)
        page.theme_mode = ft.ThemeMode.SYSTEM

        # Display the theme tokens
        token_items = []
        for key, value in TOKENS.items():
            # Create color swatch for color tokens
            if isinstance(value, str) and value.startswith('#'):
                color_swatch = ft.Container(
                    width=24,
                    height=24,
                    bgcolor=value,
                    border_radius=4,
                    border=ft.border.all(1, ft.Colors.OUTLINE)
                )
                token_item = ft.Row([
                    ft.Text(f"{key}:", weight=ft.FontWeight.BOLD, width=150),
                    ft.Text(str(value)),
                    color_swatch
                ], spacing=10)
            else:
                token_item = ft.Row([
                    ft.Text(f"{key}:", weight=ft.FontWeight.BOLD, width=150),
                    ft.Text(str(value))
                ], spacing=10)
            token_items.append(token_item)

        # Create a sample button using the theme
        sample_button = ft.FilledButton(
            text="Sample Button",
            icon=ft.Icons.CHECK,
            on_click=lambda e: print("Button clicked!")
        )

        # Create a sample card using the theme
        sample_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Sample Card", style=ft.TextThemeStyle.TITLE_LARGE),
                    ft.Text("This card uses the custom theme colors."),
                    sample_button
                ], spacing=16),
                padding=20
            ),
            elevation=2
        )

        # Add all elements to the page
        page.add(
            ft.Text("Theme Verification Test", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("Custom Theme Tokens:", size=18, weight=ft.FontWeight.W_500),
            ft.Column(token_items, spacing=8),
            ft.Divider(),
            ft.Text("Sample Components:", size=18, weight=ft.FontWeight.W_500),
            sample_card
        )

    ft.app(target=main)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
