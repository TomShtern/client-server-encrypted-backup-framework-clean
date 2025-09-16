#!/usr/bin/env python3
"""
Dialog Consolidation Utilities for FletV2
Standardized dialog patterns and user feedback to eliminate the 15+ repeated AlertDialog implementations.
"""

import flet as ft
from typing import Optional, Callable, List, Union
from utils.debug_setup import get_logger

logger = get_logger(__name__)

# Mock mode prefixes
MOCK_PREFIX = "🧪 DEMO: "
REAL_PREFIX = "✅ "


class DialogManager:
    """
    Centralized dialog management with automatic cleanup and standardized patterns.
    Replaces the repeated AlertDialog creation patterns found across view files.
    """
    
    @staticmethod
    def create_confirmation_dialog(
        page: ft.Page,
        title: str,
        content: str,
        on_confirm: Callable,
        on_cancel: Optional[Callable] = None,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        confirm_color: str = ft.Colors.PRIMARY,
        is_destructive: bool = False
    ) -> ft.AlertDialog:
        """
        Create standardized confirmation dialog.
        
        Args:
            page: Flet page instance
            title: Dialog title
            content: Dialog content/message
            on_confirm: Callback for confirm button
            on_cancel: Optional callback for cancel button
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button
            confirm_color: Color for confirm button
            is_destructive: If True, uses error styling for confirm button
        """
        def close_dialog():
            dialog.open = False
            page.update()  # Use page.update() for consistency
        
        def handle_confirm(e):
            try:
                if on_confirm:
                    # Check if callback is async and run it appropriately
                    import asyncio
                    import inspect
                    
                    if inspect.iscoroutinefunction(on_confirm):
                        # Run async callback using page.run_task()
                        page.run_task(lambda: on_confirm(e))
                    else:
                        # Run sync callback normally
                        on_confirm(e)
                close_dialog()
            except Exception as ex:
                logger.error(f"Dialog confirm action failed: {ex}")
                close_dialog()
        
        def handle_cancel(e):
            try:
                if on_cancel:
                    on_cancel(e)
                close_dialog()
            except Exception as ex:
                logger.error(f"Dialog cancel action failed: {ex}")
                close_dialog()
        
        # Use destructive styling for dangerous actions
        if is_destructive:
            confirm_color = ft.Colors.ERROR
        
        actions = [
            ft.TextButton(cancel_text, on_click=handle_cancel),
            ft.FilledButton(
                confirm_text, 
                on_click=handle_confirm,
                style=ft.ButtonStyle(bgcolor=confirm_color)
            )
        ]
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Text(content, size=14),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        # Auto-manage dialog lifecycle
        page.overlay.append(dialog)
        dialog.open = True
        page.update()  # Use page.update() instead of dialog.update() to avoid page attachment issues
        
        return dialog
    
    @staticmethod 
    def create_info_dialog(
        page: ft.Page,
        title: str,
        content: Union[str, ft.Control],
        ok_text: str = "OK",
        width: Optional[float] = None,
        height: Optional[float] = None
    ) -> ft.AlertDialog:
        """
        Create standardized information dialog.
        
        Args:
            page: Flet page instance
            title: Dialog title
            content: Dialog content (text or control)
            ok_text: Text for OK button
            width: Optional dialog width
            height: Optional dialog height
        """
        def close_dialog():
            dialog.open = False
            page.update()  # Use page.update() for consistency
        
        def handle_ok(e):
            close_dialog()
        
        # Handle both string and control content
        if isinstance(content, str):
            content_control = ft.Text(content, size=14, selectable=True)
        else:
            content_control = content
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=content_control,
                width=width,
                height=height,
                padding=ft.Padding(10, 10, 10, 10) if width or height else None
            ),
            actions=[ft.FilledButton(ok_text, on_click=handle_ok)],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()  # Use page.update() instead of dialog.update()
        
        return dialog
    
    @staticmethod
    def create_input_dialog(
        page: ft.Page,
        title: str,
        content: str,
        input_label: str,
        on_submit: Callable[[str], None],
        on_cancel: Optional[Callable] = None,
        submit_text: str = "Submit",
        cancel_text: str = "Cancel",
        initial_value: str = "",
        input_type: str = "text",
        multiline: bool = False
    ) -> ft.AlertDialog:
        """
        Create standardized input dialog with text field.
        
        Args:
            page: Flet page instance
            title: Dialog title
            content: Dialog description text
            input_label: Label for input field
            on_submit: Callback with input value
            on_cancel: Optional cancel callback
            submit_text: Text for submit button
            cancel_text: Text for cancel button
            initial_value: Initial input value
            input_type: Input type ('text', 'password', 'number')
            multiline: Whether input should be multiline
        """
        def close_dialog():
            dialog.open = False
            page.update()  # Use page.update() for consistency
        
        def handle_submit(e):
            try:
                value = input_field.value or ""
                if on_submit:
                    on_submit(value)
                close_dialog()
            except Exception as ex:
                logger.error(f"Dialog submit action failed: {ex}")
                close_dialog()
        
        def handle_cancel(e):
            try:
                if on_cancel:
                    on_cancel()
                close_dialog()
            except Exception as ex:
                logger.error(f"Dialog cancel action failed: {ex}")
                close_dialog()
        
        # Create appropriate input field
        input_kwargs = {
            "label": input_label,
            "value": initial_value,
            "multiline": multiline,
            "on_submit": handle_submit  # Enter key submits
        }
        
        if input_type == "password":
            input_kwargs["password"] = True
        elif input_type == "number":
            input_kwargs["keyboard_type"] = ft.KeyboardType.NUMBER
        
        input_field = ft.TextField(**input_kwargs)
        
        dialog_content = ft.Column([
            ft.Text(content, size=14),
            input_field
        ], spacing=16, tight=True)
        
        actions = [
            ft.TextButton(cancel_text, on_click=handle_cancel),
            ft.FilledButton(submit_text, on_click=handle_submit)
        ]
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title, weight=ft.FontWeight.BOLD),
            content=dialog_content,
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        page.overlay.append(dialog)
        dialog.open = True
        page.update()  # Use page.update() instead of dialog.update()
        
        # Auto-focus input field
        input_field.focus()
        # Remove input_field.update() as it might cause issues - focus() handles display
        
        return dialog


def show_confirmation(
    page: ft.Page,
    title: str,
    message: str,
    on_confirm: Callable,
    confirm_text: str = "Confirm",
    is_destructive: bool = False
) -> ft.AlertDialog:
    """
    Quick confirmation dialog factory function.
    
    Example:
        def delete_item():
            print("Item deleted")
        
        show_confirmation(
            page, 
            "Delete Item", 
            "Are you sure you want to delete this item?",
            delete_item,
            confirm_text="Delete",
            is_destructive=True
        )
    """
    return DialogManager.create_confirmation_dialog(
        page, title, message, on_confirm, 
        confirm_text=confirm_text, is_destructive=is_destructive
    )


def show_info(
    page: ft.Page,
    title: str,
    message: Union[str, ft.Control],
    width: Optional[float] = None
) -> ft.AlertDialog:
    """
    Quick info dialog factory function.
    
    Example:
        show_info(page, "File Details", file_details_text, width=400)
    """
    return DialogManager.create_info_dialog(page, title, message, width=width)


def show_input(
    page: ft.Page,
    title: str,
    message: str,
    input_label: str,
    on_submit: Callable[[str], None],
    initial_value: str = ""
) -> ft.AlertDialog:
    """
    Quick input dialog factory function.
    
    Example:
        def handle_rename(new_name):
            print(f"Renamed to: {new_name}")
        
        show_input(
            page,
            "Rename File",
            "Enter the new filename:",
            "New name",
            handle_rename,
            initial_value="current_name.txt"
        )
    """
    return DialogManager.create_input_dialog(
        page, title, message, input_label, on_submit, initial_value=initial_value
    )


# User Feedback Functions (migrated from user_feedback.py)
def show_user_feedback(page: ft.Page, message: str, is_error: bool = False, action_label: Optional[str] = None) -> None:
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
            bgcolor=ft.Colors.ERROR if is_error else ft.Colors.BLUE,
            action=action_label if action_label else "DISMISS",
            duration=4000  # 4 seconds
        )
        page.snack_bar.open = True
        page.update()  # ONLY acceptable page.update() use case
        
        logger.info(f"User feedback shown: {'ERROR' if is_error else 'INFO'} - {message}")
        
    except Exception as e:
        logger.error(f"Failed to show user feedback: {e}")


def show_success_message(page: ft.Page, message: str, action_label: Optional[str] = None, mode: Optional[str] = None) -> None:
    """Show success message to user with optional mode indicator."""
    try:
        # Add mode prefix if specified
        display_message = message
        if mode == 'mock':
            display_message = f"{MOCK_PREFIX}{message}"
        elif mode == 'real':
            display_message = f"{REAL_PREFIX}{message}"
        
        page.snack_bar = ft.SnackBar(
            content=ft.Text(display_message),
            bgcolor=ft.Colors.ORANGE if mode == 'mock' else ft.Colors.GREEN,
            action=action_label if action_label else "DISMISS",
            duration=5000 if mode == 'mock' else 4000  # Longer for mock messages
        )
        page.snack_bar.open = True
        page.update()  # ONLY acceptable page.update() use case
        
        logger.info(f"User feedback shown: SUCCESS - {message}")
        
    except Exception as e:
        logger.error(f"Failed to show user feedback: {e}")


def show_error_message(page: ft.Page, message: str, action_label: Optional[str] = None) -> None:
    """Show error message to user."""
    show_user_feedback(page, message, is_error=True, action_label=action_label)


def show_info_message(page: ft.Page, message: str, action_label: Optional[str] = None, mode: Optional[str] = None) -> None:
    """Show info message to user with optional mode indicator."""
    # Add mode prefix if specified
    display_message = message
    if mode == 'mock':
        display_message = f"{MOCK_PREFIX}{message}"
    elif mode == 'real':
        display_message = f"{REAL_PREFIX}{message}"
    
    try:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(display_message),
            bgcolor=ft.Colors.ORANGE if mode == 'mock' else ft.Colors.BLUE,
            action=action_label if action_label else "DISMISS",
            duration=5000 if mode == 'mock' else 4000  # Longer for mock messages
        )
        page.snack_bar.open = True
        page.update()
        
        logger.info(f"Info message shown ({mode or 'standard'} mode): {display_message}")
        
    except Exception as e:
        logger.error(f"Failed to show info message: {e}")


def show_warning_message(page: ft.Page, message: str, action_label: Optional[str] = None) -> None:
    """Show warning message to user."""
    try:
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.BLUE,
            action=action_label if action_label else "DISMISS",
            duration=4000  # 4 seconds
        )
        page.snack_bar.open = True
        page.update()  # ONLY acceptable page.update() use case
        
        logger.info(f"User feedback shown: WARNING - {message}")
        
    except Exception as e:
        logger.error(f"Failed to show user feedback: {e}")