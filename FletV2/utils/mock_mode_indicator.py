#!/usr/bin/env python3
"""
Mock Mode Indicator for FletV2
Provides visual indicators when the application is running in mock/fallback mode.
"""

import flet as ft
from utils.debug_setup import get_logger

logger = get_logger(__name__)


def create_mock_mode_banner(server_bridge) -> ft.Control:
    """
    Create a banner that shows when the application is running in mock mode.
    
    Args:
        server_bridge: The server bridge instance to check for real server connection
        
    Returns:
        ft.Control: A banner control or empty container if in real mode
    """
    if server_bridge and server_bridge.is_connected():
        # Real server mode - no banner needed
        return ft.Container(height=0)
    
    # Mock/fallback mode - show banner
    banner = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.SCIENCE, color=ft.Colors.WHITE, size=20),
            ft.Text(
                "DEMO MODE: Using mock data - no real server operations",
                color=ft.Colors.WHITE,
                weight=ft.FontWeight.BOLD,
                size=14
            ),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.INFO_OUTLINE,
                icon_color=ft.Colors.WHITE,
                tooltip="This application is running in demo mode with mock data. No real files are downloaded, verified, or database changes are made.",
                icon_size=20
            )
        ], spacing=10),
        bgcolor=ft.Colors.ORANGE_600,
        padding=ft.Padding(16, 8, 16, 8),
        border_radius=ft.BorderRadius(0, 0, 8, 8),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
    )
    
    return banner


def add_mock_indicator_to_snackbar_message(message: str, mode: str = 'unknown') -> str:
    """
    Add mock mode prefix to user feedback messages.
    
    Args:
        message: Original message
        mode: Operation mode ('real', 'mock', or 'unknown')
        
    Returns:
        str: Message with appropriate prefix
    """
    if mode == 'mock':
        return f"🧪 DEMO: {message}"
    elif mode == 'real':
        return f"✅ {message}"
    else:
        return message


def create_mock_mode_tooltip(operation_name: str) -> str:
    """
    Create tooltip text that explains mock mode behavior.
    
    Args:
        operation_name: Name of the operation (e.g., "download", "verify", "edit")
        
    Returns:
        str: Tooltip text explaining mock behavior
    """
    tooltips = {
        "download": "In demo mode, this creates a sample file in your Downloads folder instead of downloading the real file.",
        "verify": "In demo mode, this performs a mock verification that always passes without checking the actual file.",
        "edit": "In demo mode, this simulates editing without making real database changes.",
        "delete": "In demo mode, this removes items from the display without deleting real files or database records."
    }
    
    return tooltips.get(operation_name, f"In demo mode, this {operation_name} operation is simulated without real changes.")


def create_status_indicator(is_connected: bool) -> ft.Control:
    """
    Create a small status indicator showing connection status.
    
    Args:
        is_connected: True if connected to real server, False for mock mode
        
    Returns:
        ft.Control: Status indicator control
    """
    if is_connected:
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CLOUD_DONE, color=ft.Colors.GREEN, size=16),
                ft.Text("Live", color=ft.Colors.GREEN, size=12, weight=ft.FontWeight.BOLD)
            ], spacing=4, tight=True),
            tooltip="Connected to real server"
        )
    else:
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SCIENCE, color=ft.Colors.ORANGE, size=16),
                ft.Text("Demo", color=ft.Colors.ORANGE, size=12, weight=ft.FontWeight.BOLD)
            ], spacing=4, tight=True),
            tooltip="Running in demo mode with mock data"
        )


def update_action_button_for_mock_mode(button: ft.Control, server_bridge, operation_name: str) -> ft.Control:
    """
    Update an action button to indicate mock mode behavior.
    
    Args:
        button: The button control to update
        server_bridge: Server bridge to check connection status
        operation_name: Name of the operation for tooltip
        
    Returns:
        ft.Control: Updated button with mock mode indicators
    """
    if not server_bridge or not server_bridge.is_connected():
        # Add mock mode styling
        if hasattr(button, 'tooltip'):
            original_tooltip = button.tooltip or ""
            button.tooltip = f"{original_tooltip}\n\n{create_mock_mode_tooltip(operation_name)}"
        
        # Add subtle mock mode styling
        if hasattr(button, 'style') and button.style:
            # Keep existing style but add subtle mock indicator
            pass
        else:
            # Add new style for mock mode
            button.style = ft.ButtonStyle(
                overlay_color={
                    ft.MaterialState.DEFAULT: ft.Colors.ORANGE_50,
                    ft.MaterialState.HOVERED: ft.Colors.ORANGE_100,
                }
            )
    
    return button