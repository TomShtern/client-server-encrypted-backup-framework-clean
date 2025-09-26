#!/usr/bin/env python3
"""
Simple Test for Enhanced Components
Verifies that enhanced components are working correctly.
"""

import sys

# Add project root to path
sys.path.insert(0, '.')

import flet as ft
from flet_server_gui.components.enhanced_components import (
    create_enhanced_button,
    create_enhanced_card,
    create_enhanced_chip,
    create_enhanced_icon_button,
    create_enhanced_text_field,
)


def main(page: ft.Page):
    page.title = "Enhanced Components Test"
    page.padding = 20

    # Test enhanced button
    def on_button_click(e):
        print("Enhanced button clicked!")
        page.snack_bar = ft.SnackBar(ft.Text("Enhanced button works!"))
        page.snack_bar.open = True
        page.update()

    button = create_enhanced_button(
        text="Test Enhanced Button",
        icon=ft.Icons.CHECK,
        on_click=on_button_click
    )

    # Test enhanced icon button
    def on_icon_button_click(e):
        print("Enhanced icon button clicked!")
        page.snack_bar = ft.SnackBar(ft.Text("Enhanced icon button works!"))
        page.snack_bar.open = True
        page.update()

    icon_button = create_enhanced_icon_button(
        icon=ft.Icons.STAR,
        tooltip="Test Button",
        on_click=on_icon_button_click
    )

    # Test enhanced chip
    def on_chip_click(e):
        print("Enhanced chip clicked!")
        page.snack_bar = ft.SnackBar(ft.Text("Enhanced chip works!"))
        page.snack_bar.open = True
        page.update()

    chip = create_enhanced_chip(
        label="Test Chip",
        on_click=on_chip_click
    )

    # Test enhanced text field
    def on_text_change(e):
        print(f"Text changed to: {e.data}")

    text_field = create_enhanced_text_field(
        label="Test Text Field",
        icon=ft.Icons.TEXT_FIELDS,
        on_change=on_text_change
    )

    # Test enhanced card
    card_content = ft.Column([
        ft.Text("Test Card", style=ft.TextThemeStyle.TITLE_LARGE),
        ft.Text("This is an enhanced card with hover effects.", size=14),
        ft.Row([button, icon_button], spacing=12)
    ], spacing=16)

    card = create_enhanced_card(
        content=ft.Container(
            content=card_content,
            padding=20
        )
    )

    # Add all components to page
    page.add(
        ft.Text("Enhanced Components Test", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Column([
            ft.Text("Click components to test functionality:", size=16),
            ft.Row([chip], spacing=12),
            text_field,
            card
        ], spacing=20)
    )


if __name__ == "__main__":
    ft.app(target=main)
