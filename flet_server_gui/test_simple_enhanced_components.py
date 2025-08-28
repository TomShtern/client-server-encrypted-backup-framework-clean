#!/usr/bin/env python3
"""
Simple test script for enhanced UI components
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import flet as ft
from flet_server_gui.ui.widgets import (
    EnhancedButton,
    EnhancedCard,
    EnhancedButtonConfig,
    EnhancedCardConfig,
    ButtonVariant,
    CardVariant
)


def main(page: ft.Page):
    # Configure the page
    page.title = "Enhanced Components Test"
    page.scroll = ft.ScrollMode.AUTO
    
    # Test Enhanced Button
    button_config = EnhancedButtonConfig(
        text="Click Me",
        variant=ButtonVariant.FILLED,
        on_click=lambda e: print("Button clicked!")
    )
    enhanced_button = EnhancedButton(page, button_config)
    
    # Test Enhanced Card
    card_config = EnhancedCardConfig(
        title="Test Card",
        content="This is a test card content",
        variant=CardVariant.ELEVATED
    )
    enhanced_card = EnhancedCard(page, card_config)
    
    # Create layout
    layout = ft.Column([
        ft.Text("Enhanced Components Test", size=32, weight=ft.FontWeight.BOLD),
        ft.Divider(),
        ft.Text("Enhanced Button:", size=20, weight=ft.FontWeight.W_500),
        enhanced_button.get_control(),
        ft.Divider(),
        ft.Text("Enhanced Card:", size=20, weight=ft.FontWeight.W_500),
        enhanced_card.get_control(),
    ], spacing=20)
    
    page.add(layout)


if __name__ == "__main__":
    ft.app(target=main)