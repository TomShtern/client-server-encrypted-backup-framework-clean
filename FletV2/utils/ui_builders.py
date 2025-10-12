"""
UI Builders for FletV2 - Common UI patterns and components.

This module provides standardized building blocks for:
- Search bars
- Filter dropdowns
- Action buttons
- Confirmation dialogs
"""

from __future__ import annotations

import flet as ft


def create_search_bar(
    on_change,
    *,
    placeholder: str = "Search…",
    expand: bool = True,
    width: int | None = None,
    prefix_icon: str = ft.Icons.SEARCH,
):
    """Create a standardized search bar aligned with Flet 0.28.3 styling."""

    field = ft.TextField(
        label=placeholder,
        prefix_icon=prefix_icon,
        border=ft.InputBorder.OUTLINE,
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.SURFACE,
        focused_border_color=ft.Colors.PRIMARY,
        on_change=on_change,
        expand=expand if width is None else False,
        width=width,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        text_style=ft.TextStyle(size=14),
    )
    return field


def create_filter_dropdown(
    label: str,
    options,
    on_change,
    *,
    value=None,
    width: int | None = 200,
    expand: bool = False,
):
    """Create a standardized dropdown styled for filter toolbars."""

    dropdown_options: list[ft.dropdown.Option] = []
    for option in options:
        if isinstance(option, ft.dropdown.Option):
            dropdown_options.append(option)
        elif isinstance(option, tuple):
            if len(option) == 2:
                dropdown_options.append(ft.dropdown.Option(option[0], option[1]))
            else:
                dropdown_options.append(ft.dropdown.Option(option[0]))
        else:
            dropdown_options.append(ft.dropdown.Option(option))

    return ft.Dropdown(
        label=label,
        value=value,
        options=dropdown_options,
        on_change=on_change,
        border=ft.InputBorder.OUTLINE,
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.SURFACE,
        focused_border_color=ft.Colors.PRIMARY,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        width=None if expand else width,
        expand=expand,
    )


def create_action_button(text, on_click, icon=None, primary=True):
    """Create a consistent action button that respects the active theme."""

    button_cls = ft.FilledButton if primary else ft.OutlinedButton

    return button_cls(
        text=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(16, 10, 16, 10),
        ),
    )


def create_view_header(
    title: str,
    *,
    icon: str | None = None,
    description: str | None = None,
    actions: list[ft.Control] | None = None,
) -> ft.Control:
    """Compose a compact, responsive header for top-of-view toolbars."""

    leading_controls: list[ft.Control] = []
    if icon:
        leading_controls.append(
            ft.Icon(icon, size=26, color=ft.Colors.PRIMARY)
        )
    leading_controls.append(
        ft.Text(title, size=26, weight=ft.FontWeight.BOLD)
    )

    title_row = ft.Row(
        [
            ft.Row(
                leading_controls,
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(expand=True),
            *(actions or []),
        ],
        spacing=16,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        wrap=False,
    )

    header_controls: list[ft.Control] = [title_row]
    if description:
        header_controls.append(
            ft.Text(
                description,
                size=14,
                color=ft.Colors.ON_SURFACE_VARIANT,
            )
        )

    return ft.Container(
        content=ft.Column(header_controls, spacing=4),
        padding=ft.padding.only(bottom=12),
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