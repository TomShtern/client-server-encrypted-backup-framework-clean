"""
Simple placeholder mode indicator for FletV2 GUI.
Shows a visual banner when the application is using placeholder/lorem ipsum data.
"""

import flet as ft
from typing import Optional


def create_placeholder_mode_banner(server_bridge) -> ft.Control:
    """
    Create a simple banner indicating when placeholder data is being used.

    Args:
        server_bridge: The server bridge instance to check for placeholder mode

    Returns:
        ft.Control: A banner container or empty container if not in placeholder mode
    """
    # Check if we're in placeholder mode by looking for the _placeholder_generator attribute
    is_placeholder_mode = hasattr(server_bridge, '_placeholder_generator') and server_bridge._placeholder_generator is not None

    if not is_placeholder_mode:
        # Return empty container with zero height when not in placeholder mode
        return ft.Container(height=0)

    # Create the placeholder mode banner
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(
                    name=ft.Icons.INFO_OUTLINE,
                    color=ft.Colors.AMBER_700,
                    size=16
                ),
                ft.Text(
                    "Using Lorem Ipsum Placeholder Data",
                    size=12,
                    color=ft.Colors.AMBER_700,
                    weight=ft.FontWeight.W_500
                ),
                ft.Text(
                    "• Development Mode",
                    size=11,
                    color=ft.Colors.AMBER_600,
                    italic=True
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8
        ),
        bgcolor=ft.Colors.AMBER_50,
        border=ft.Border(
            bottom=ft.BorderSide(width=1, color=ft.Colors.AMBER_200)
        ),
        padding=ft.Padding(left=16, right=16, top=8, bottom=8),
        margin=ft.Margin(left=0, right=0, top=0, bottom=0),
        animate=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_IN_OUT)
    )