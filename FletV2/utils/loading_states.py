"""
Loading States for FletV2 - Standardized loading, error, and empty state displays.

This module provides consistent UI components for:
- Loading indicators
- Error displays
- Empty states
- Snackbar notifications
"""

import flet as ft


def create_loading_indicator(message="Loading..."):
    """
    Create standardized loading indicator.

    Args:
        message: Message to display with the loading indicator

    Returns:
        Container with loading indicator and message
    """
    return ft.Container(
        content=ft.Column([
            ft.ProgressRing(),
            ft.Text(message, size=14, color=ft.Colors.ON_SURFACE_VARIANT)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        padding=20
    )


def create_error_display(error_message):
    """
    Create standardized error display.

    Args:
        error_message: Error message to display

    Returns:
        Container with error icon and message
    """
    return ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.ERROR, size=48),
            ft.Text("Error", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ERROR),
            ft.Text(error_message, size=14, color=ft.Colors.ON_SURFACE_VARIANT, text_align=ft.TextAlign.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        alignment=ft.alignment.center,
        padding=20
    )


def create_empty_state(title, message, icon=None):
    """
    Create standardized empty state display.

    Args:
        title: Title for the empty state
        message: Message for the empty state
        icon: Icon to display (default: INBOX_OUTLINED)

    Returns:
        Container with icon, title, and message for empty state
    """
    resolved_icon = icon or ft.Icons.INBOX_OUTLINED

    return ft.Container(
        content=ft.Column([
            ft.Icon(resolved_icon, color=ft.Colors.ON_SURFACE_VARIANT, size=64),
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            ft.Text(message, size=14, color=ft.Colors.ON_SURFACE_VARIANT, text_align=ft.TextAlign.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        alignment=ft.alignment.center,
        padding=40
    )


# Snackbar functions removed - use user_feedback.py instead
# - show_success_message(page, message)
# - show_error_message(page, message)
# - show_info_message(page, message)
# - show_warning_message(page, message)