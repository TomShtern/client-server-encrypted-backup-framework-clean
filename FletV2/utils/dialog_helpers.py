#!/usr/bin/env python3
"""
Dialog Creation Utilities for FletV2
Standardized dialog patterns for consistent user interaction.
"""

import flet as ft
from typing import Optional, Callable, List
from utils.debug_setup import get_logger

logger = get_logger(__name__)


def create_confirmation_dialog(
    title: str,
    content: str,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    confirm_handler: Optional[Callable[[ft.ControlEvent], None]] = None,
    cancel_handler: Optional[Callable[[ft.ControlEvent], None]] = None,
    confirm_color: Optional[str] = None,
    modal: bool = True
) -> ft.AlertDialog:
    """
    Create a standardized confirmation dialog with consistent styling.
    
    Args:
        title: Dialog title
        content: Dialog content text
        confirm_text: Text for confirmation button
        cancel_text: Text for cancel button
        confirm_handler: Function to call on confirmation
        cancel_handler: Function to call on cancel
        confirm_color: Color for confirm button (optional)
        modal: Whether dialog is modal
    
    Returns:
        Configured AlertDialog
        
    Example:
        dialog = create_confirmation_dialog(
            "Delete File",
            "Are you sure you want to delete this file?",
            "Delete",
            "Cancel",
            on_confirm_delete,
            on_cancel_delete,
            ft.Colors.RED
        )
    """
    def default_cancel(e):
        if cancel_handler:
            cancel_handler(e)
        else:
            # Default behavior: close dialog
            e.control.page.dialog.open = False
            e.control.page.dialog.update()
    
    def default_confirm(e):
        if confirm_handler:
            confirm_handler(e)
        # Dialog closing should be handled by the confirm_handler
        
    actions = [
        ft.TextButton(
            cancel_text,
            on_click=default_cancel
        ),
        ft.TextButton(
            confirm_text,
            on_click=default_confirm,
            style=ft.ButtonStyle(
                color=confirm_color if confirm_color else None
            )
        )
    ]
    
    return ft.AlertDialog(
        modal=modal,
        title=ft.Text(title, weight=ft.FontWeight.BOLD),
        content=ft.Text(content, size=16),
        actions=actions,
        actions_alignment=ft.MainAxisAlignment.END
    )


def create_info_dialog(
    title: str,
    content: str,
    button_text: str = "OK",
    button_handler: Optional[Callable] = None,
    modal: bool = True
) -> ft.AlertDialog:
    """
    Create a standardized information dialog.
    
    Args:
        title: Dialog title
        content: Dialog content text
        button_text: Text for the OK button
        button_handler: Function to call when OK is clicked
        modal: Whether dialog is modal
    
    Returns:
        Configured AlertDialog
        
    Example:
        dialog = create_info_dialog(
            "Operation Complete",
            "The file has been successfully processed."
        )
    """
    def default_ok(e):
        if button_handler:
            button_handler(e)
        else:
            # Default behavior: close dialog
            e.control.page.dialog.open = False
            e.control.page.dialog.update()
    
    return ft.AlertDialog(
        modal=modal,
        title=ft.Text(title, weight=ft.FontWeight.BOLD),
        content=ft.Text(content, size=16),
        actions=[
            ft.TextButton(button_text, on_click=default_ok)
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )


def create_input_dialog(
    title: str,
    label: str,
    placeholder: str = "",
    initial_value: str = "",
    confirm_text: str = "OK",
    cancel_text: str = "Cancel",
    confirm_handler: Optional[Callable[[str], None]] = None,
    cancel_handler: Optional[Callable] = None,
    multiline: bool = False,
    modal: bool = True
) -> ft.AlertDialog:
    """
    Create a standardized input dialog for text collection.
    
    Args:
        title: Dialog title
        label: Label for input field
        placeholder: Placeholder text
        initial_value: Initial value for input
        confirm_text: Text for confirmation button
        cancel_text: Text for cancel button
        confirm_handler: Function to call with input value on confirmation
        cancel_handler: Function to call on cancel
        multiline: Whether input should be multiline
        modal: Whether dialog is modal
    
    Returns:
        Configured AlertDialog with input field
        
    Example:
        dialog = create_input_dialog(
            "Enter Name",
            "Client Name:",
            "Enter client name...",
            "",
            "Save",
            "Cancel",
            lambda value: save_client_name(value)
        )
    """
    input_field = ft.TextField(
        label=label,
        placeholder=placeholder,
        value=initial_value,
        multiline=multiline,
        max_lines=5 if multiline else 1,
        width=300
    )
    
    def default_cancel(e):
        if cancel_handler:
            cancel_handler(e)
        else:
            e.control.page.dialog.open = False
            e.control.page.dialog.update()
    
    def default_confirm(e):
        if confirm_handler:
            confirm_handler(input_field.value or "")
        # Dialog closing should be handled by the confirm_handler
    
    return ft.AlertDialog(
        modal=modal,
        title=ft.Text(title, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=input_field,
            width=320,
            padding=ft.Padding(0, 10, 0, 0)
        ),
        actions=[
            ft.TextButton(cancel_text, on_click=default_cancel),
            ft.TextButton(confirm_text, on_click=default_confirm)
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )