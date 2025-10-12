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
            ft.Text(message, size=14, color=ft.colors.ON_SURFACE_VARIANT)
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
            ft.Icon(ft.icons.ERROR_OUTLINE, color=ft.colors.ERROR, size=48),
            ft.Text("Error", size=20, weight=ft.FontWeight.BOLD, color=ft.colors.ERROR),
            ft.Text(error_message, size=14, color=ft.colors.ON_SURFACE_VARIANT, text_align=ft.TextAlign.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        alignment=ft.alignment.center,
        padding=20
    )


def create_empty_state(title, message, icon=ft.icons.INBOX_OUTLINED):
    """
    Create standardized empty state display.
    
    Args:
        title: Title for the empty state
        message: Message for the empty state
        icon: Icon to display (default: INBOX_OUTLINED)
        
    Returns:
        Container with icon, title, and message for empty state
    """
    return ft.Container(
        content=ft.Column([
            ft.Icon(icon, color=ft.colors.ON_SURFACE_VARIANT, size=64),
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            ft.Text(message, size=14, color=ft.colors.ON_SURFACE_VARIANT, text_align=ft.TextAlign.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        alignment=ft.alignment.center,
        padding=40
    )


def show_snackbar(page, message, bgcolor=None):
    """
    Show standardized snackbar notification.
    
    Args:
        page: Flet page to show the snackbar on
        message: Message to display
        bgcolor: Background color for the snackbar (optional)
    """
    page.snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=bgcolor or ft.colors.SURFACE_VARIANT
    )
    page.snack_bar.open = True
    page.update()


def show_error_snackbar(page, error_message):
    """
    Show error snackbar.
    
    Args:
        page: Flet page to show the snackbar on
        error_message: Error message to display
    """
    show_snackbar(page, error_message, bgcolor=ft.colors.ERROR_CONTAINER)


def show_success_snackbar(page, message):
    """
    Show success snackbar.
    
    Args:
        page: Flet page to show the snackbar on
        message: Success message to display
    """
    show_snackbar(page, message, bgcolor=ft.colors.PRIMARY_CONTAINER)