#!/usr/bin/env python3
"""
Centralized User Feedback Utilities for FletV2
Provides consistent user feedback patterns across the application.
"""

import flet as ft
from utils.debug_setup import get_logger

logger = get_logger(__name__)


def show_user_feedback(page: ft.Page, message: str, is_error: bool = False, action_label: str = None) -> None:
    """
    Show centralized user feedback using Flet's SnackBar.
    
    This is the ONLY acceptable use of page.update() in the application -
    for system-level feedback like SnackBar, which requires page-level updates.
    
    Args:
        page: Flet page instance
        message: Message to display to user
        is_error: Whether this is an error message (changes color)
        action_label: Optional action button label
    """
    try:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.ERROR if is_error else ft.Colors.PRIMARY,
            action=action_label if action_label else "DISMISS",
            duration=4000  # 4 seconds
        )
        page.snack_bar.open = True
        page.update()  # ONLY acceptable page.update() use case
        
        logger.info(f"User feedback shown: {'ERROR' if is_error else 'INFO'} - {message}")
        
    except Exception as e:
        logger.error(f"Failed to show user feedback: {e}")


def show_success_message(page: ft.Page, message: str, action_label: str = None) -> None:
    """Show success message to user."""
    show_user_feedback(page, message, is_error=False, action_label=action_label)


def show_error_message(page: ft.Page, message: str, action_label: str = None) -> None:
    """Show error message to user."""
    show_user_feedback(page, message, is_error=True, action_label=action_label)


def show_info_message(page: ft.Page, message: str, action_label: str = None) -> None:
    """Show info message to user."""
    show_user_feedback(page, message, is_error=False, action_label=action_label)


async def show_loading_dialog(page: ft.Page, title: str, message: str) -> ft.AlertDialog:
    """
    Show loading dialog for long operations.
    
    Returns:
        AlertDialog: The dialog instance for manual closing
    """
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Row([
            ft.ProgressRing(width=20, height=20),
            ft.Text(message, size=14)
        ], alignment=ft.MainAxisAlignment.START),
    )
    
    page.dialog = dialog
    dialog.open = True
    page.update()  # ONLY acceptable page.update() for dialogs
    
    return dialog


async def close_loading_dialog(page: ft.Page, dialog: ft.AlertDialog) -> None:
    """Close loading dialog."""
    if page.dialog == dialog:
        dialog.open = False
        page.dialog = None
        page.update()  # ONLY acceptable page.update() for dialogs


def create_confirmation_dialog(
    page: ft.Page,
    title: str,
    message: str,
    on_confirm: callable,
    on_cancel: callable = None,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel"
) -> ft.AlertDialog:
    """
    Create confirmation dialog for destructive actions.
    
    Args:
        page: Flet page instance
        title: Dialog title
        message: Dialog message
        on_confirm: Callback for confirm action
        on_cancel: Optional callback for cancel action
        confirm_text: Confirm button text
        cancel_text: Cancel button text
    
    Returns:
        AlertDialog: The dialog instance
    """
    def handle_confirm(e):
        page.dialog.open = False
        page.update()  # ONLY acceptable page.update() for dialogs
        if on_confirm:
            on_confirm(e)
    
    def handle_cancel(e):
        page.dialog.open = False
        page.update()  # ONLY acceptable page.update() for dialogs
        if on_cancel:
            on_cancel(e)
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[
            ft.TextButton(cancel_text, on_click=handle_cancel),
            ft.FilledButton(confirm_text, on_click=handle_confirm),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    return dialog


def show_confirmation_dialog(
    page: ft.Page,
    title: str,
    message: str,
    on_confirm: callable,
    on_cancel: callable = None,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel"
) -> None:
    """Show confirmation dialog immediately."""
    dialog = create_confirmation_dialog(
        page, title, message, on_confirm, on_cancel, confirm_text, cancel_text
    )
    
    page.dialog = dialog
    dialog.open = True
    page.update()  # ONLY acceptable page.update() for dialogs