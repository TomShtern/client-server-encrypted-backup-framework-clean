#!/usr/bin/env python3
"""
Dialog Consolidation Utilities for FletV2
Standardized dialog patterns to eliminate the 15+ repeated AlertDialog implementations.
"""

import flet as ft
from typing import Optional, Callable, List, Union
from utils.debug_setup import get_logger

logger = get_logger(__name__)


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
        confirm_color: ft.colors = ft.Colors.PRIMARY,
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
            dialog.update()
        
        def handle_confirm(e):
            try:
                if on_confirm:
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
        dialog.update()
        
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
            dialog.update()
        
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
        dialog.update()
        
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
            dialog.update()
        
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
        dialog.update()
        
        # Auto-focus input field
        input_field.focus()
        input_field.update()
        
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