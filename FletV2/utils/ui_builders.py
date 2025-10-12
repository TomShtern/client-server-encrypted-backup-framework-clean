"""
UI Builders for FletV2 - Common UI patterns and components.

This module provides standardized building blocks for:
- Search bars
- Filter dropdowns
- Action buttons
- Confirmation dialogs
"""

import flet as ft


def create_search_bar(on_change, placeholder="Search...", width=300):
    """
    Create standardized search bar.
    
    Args:
        on_change: Function to call when search text changes
        placeholder: Placeholder text for the search bar
        width: Width of the search bar
        
    Returns:
        TextField configured as a search bar
    """
    return ft.TextField(
        hint_text=placeholder,
        prefix_icon=ft.icons.SEARCH,
        border_radius=20,
        width=width,
        on_change=on_change,
        dense=True
    )


def create_filter_dropdown(label, options, on_change, width=200):
    """
    Create standardized filter dropdown.
    
    Args:
        label: Label for the dropdown
        options: List of options for the dropdown
        on_change: Function to call when selection changes
        width: Width of the dropdown
        
    Returns:
        Dropdown control configured as a filter
    """
    return ft.Dropdown(
        label=label,
        options=[ft.dropdown.Option(opt) for opt in options],
        on_change=on_change,
        width=width,
        dense=True
    )


def create_action_button(text, on_click, icon=None, primary=True):
    """
    Create standardized action button.
    
    Args:
        text: Text to display on the button
        on_click: Function to call when the button is clicked
        icon: Icon to display on the button (optional)
        primary: Whether to use primary color (True) or surface variant (False)
        
    Returns:
        ElevatedButton configured as an action button
    """
    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=ft.colors.PRIMARY if primary else ft.colors.SURFACE_VARIANT,
            color=ft.colors.ON_PRIMARY if primary else ft.colors.ON_SURFACE_VARIANT
        )
    )


def create_confirmation_dialog(title, message, on_confirm, on_cancel):
    """
    Create standardized confirmation dialog.
    
    Args:
        title: Title of the dialog
        message: Message to display in the dialog
        on_confirm: Function to call if user confirms
        on_cancel: Function to call if user cancels
        
    Returns:
        AlertDialog configured as a confirmation dialog
    """
    return ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Cancel", on_click=on_cancel),
            ft.TextButton("Confirm", on_click=on_confirm)
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )