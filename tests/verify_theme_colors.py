#!/usr/bin/env python3
"""
Final verification script to show all custom theme colors
"""
import sys

# Add project root to path
sys.path.insert(0, '.')

try:
    import flet as ft
    from flet_server_gui.ui.theme_m3 import TOKENS, create_theme

    def main(page: ft.Page):
        # Apply the custom theme
        theme = create_theme(use_material3=True, dark=False)
        page.theme = theme
        page.title = "Custom Theme Colors Verification"

        # Create color swatches for all custom tokens
        swatches = []
        for name, color in TOKENS.items():
            swatch = ft.Container(
                content=ft.Column([
                    ft.Container(
                        width=100,
                        height=100,
                        bgcolor=color,
                        border=ft.border.all(1, ft.Colors.BLACK12),
                        border_radius=8
                    ),
                    ft.Text(name, size=12, weight=ft.FontWeight.BOLD),
                    ft.Text(color, size=10, color=ft.Colors.GREY)
                ], spacing=5, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10,
                width=120
            )
            swatches.append(swatch)

        # Create a grid of color swatches
        swatch_grid = ft.GridView(
            controls=swatches,
            runs_count=4,
            max_extent=150,
            spacing=10,
            run_spacing=10,
            padding=20
        )

        # Add a gradient example
        try:
            from flet_server_gui.ui.theme_m3 import gradient_button
            gradient_example = gradient_button(
                ft.Text("Gradient Button"),
                width=200,
                height=50,
                on_click=lambda e: print("Gradient button clicked!")
            )
        except:
            gradient_example = ft.Container(
                content=ft.Text("Gradient Unavailable"),
                width=200,
                height=50,
                alignment=ft.alignment.center,
                gradient=ft.LinearGradient(
                    colors=["#A8CBF3", "#7C5CD9"],
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right
                ),
                border_radius=8
            )

        page.add(
            ft.AppBar(
                title=ft.Text("Custom Theme Colors Verification"),
                bgcolor=ft.Colors.SURFACE_VARIANT if hasattr(ft.Colors, 'SURFACE_VARIANT') else ft.Colors.GREY_300
            ),
            ft.Column([
                ft.Text("Custom Theme Color Swatches", size=20, weight=ft.FontWeight.BOLD),
                swatch_grid,
                ft.Divider(),
                ft.Text("Gradient Example", size=16, weight=ft.FontWeight.BOLD),
                gradient_example,
                ft.Divider(),
                ft.Text(
                    "This view shows all custom colors from the theme_m3.py file.\n"
                    "Primary: Blue to Purple Gradient (#A8CBF3 → #7C5CD9)\n"
                    "Secondary: Orange (#FCA651)\n"
                    "Tertiary: Pinkish-Red (#AB6DA4)\n"
                    "Container: Teal/Turquoise (#38A298)\n"
                    "Surface: Light Natural (#F6F8FB)",
                    size=12
                )
            ], scroll=ft.ScrollMode.AUTO, expand=True)
        )

    ft.app(target=main)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
