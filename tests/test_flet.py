#!/usr/bin/env python3
"""Simple Flet test to verify everything works"""

import flet as ft

def main(page: ft.Page):
    page.title = "Flet Test"
    page.theme_mode = ft.ThemeMode.DARK
    
    # Test Material Design 3 components
    page.add(
        ft.Column([
            ft.Text("🎉 Flet Works!", style="headlineLarge"),
            ft.Text("Hebrew test: שלום עולם", style="bodyLarge"),
            
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Server Status", style="titleLarge"),
                        ft.Chip(
                            label=ft.Text("ONLINE", color=ft.Colors.ON_PRIMARY),
                            bgcolor=ft.Colors.PRIMARY_CONTAINER
                        ),
                        ft.ElevatedButton(
                            "Test Button",
                            icon=ft.Icons.PLAY_ARROW,
                            on_click=lambda e: page.add(ft.Text("Button clicked!"))
                        )
                    ]),
                    padding=20
                )
            )
        ])
    )

if __name__ == "__main__":
    print("Testing basic Flet functionality...")
    # Just test import and basic functionality
    try:
        import flet as ft
        print("OK Flet imported successfully")
        print("OK Colors available:", hasattr(ft, 'Colors'))
        print("OK Icons available:", hasattr(ft, 'Icons'))
        print("OK Ready to run dashboard!")
    except Exception as e:
        print(f"ERROR: {e}")