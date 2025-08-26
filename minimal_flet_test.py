#!/usr/bin/env python3
"""
Minimal Flet Test - Isolate GUI errors from logging noise
Tests basic Flet functionality and Material Design 3 compliance
"""

import flet as ft
import sys
import os

# Add project path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import UTF-8 solution
try:
    import Shared.utils.utf8_solution
    print("[UTF-8] UTF-8 solution imported successfully")
except ImportError:
    print("[WARNING] UTF-8 solution not available")

# Safe print function to handle encoding issues
def safe_print(message: str):
    """Print message with UTF-8 encoding safety"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback: remove non-ASCII characters
        clean_msg = ''.join(char if ord(char) < 128 else '?' for char in message)
        print(clean_msg)

def main(page: ft.Page):
    """Minimal test of Flet with Material Design 3"""
    
    # Configure page
    page.title = "Flet MD3 Test"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.window_width = 800
    page.window_height = 600
    
    # Test Material Design 3 colors and icons
    test_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Flet Material Design 3 Test", 
                       style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                       weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600, size=24),
                    ft.Text("Flet successfully imported and running", 
                           style=ft.TextThemeStyle.BODY_LARGE)
                ], spacing=12),
                ft.Row([
                    ft.Icon(ft.Icons.PALETTE, color=ft.Colors.PRIMARY, size=24),
                    ft.Text(f"Theme mode: {page.theme_mode}", 
                           style=ft.TextThemeStyle.BODY_MEDIUM)
                ], spacing=12),
                ft.Divider(),
                ft.ResponsiveRow([
                    ft.Container(
                        content=ft.FilledButton(
                            "Test Button",
                            icon=ft.Icons.PLAY_ARROW,
                            on_click=lambda _: safe_print("[SUCCESS] Button clicked successfully!")
                        ),
                        col={"sm": 12, "md": 6},
                        expand=True
                    ),
                    ft.Container(
                        content=ft.OutlinedButton(
                            "Secondary", 
                            icon=ft.Icons.SETTINGS,
                            on_click=lambda _: page.show_snack_bar(ft.SnackBar(ft.Text("Snackbar working!")))
                        ),
                        col={"sm": 12, "md": 6},
                        expand=True
                    )
                ], spacing=12)
            ], spacing=16),
            padding=ft.padding.all(20)
        ),
        elevation=2
    )
    
    # Add to page
    page.add(
        ft.Container(
            content=test_card,
            padding=ft.padding.all(20),
            expand=True,
            alignment=ft.alignment.center
        )
    )
    
    safe_print("[SUCCESS] Minimal Flet test initialized successfully")

if __name__ == "__main__":
    safe_print("[LAUNCH] Starting minimal Flet Material Design 3 test...")
    try:
        ft.app(target=main)
        safe_print("[SUCCESS] Flet test completed successfully")
    except Exception as e:
        safe_print(f"[ERROR] Flet test failed: {e}")
        sys.exit(1)