#!/usr/bin/env python3
"""
Dialog Builder - SIMPLIFIED with proven patterns from working views.

This module provides dialog helpers extracted from the EXACT patterns
used in clients.py, files.py, database_pro.py. These are the patterns
that actually work in production, not theoretical abstractions.

Original file: 449 lines of complex form builders (0% adoption)
New file: ~150 lines of proven patterns from views
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

import flet as ft
from FletV2.utils.debug_setup import get_logger

logger = get_logger(__name__)


def create_text_input_dialog(
    page: ft.Page,
    title: str,
    field_label: str,
    on_save_async: Callable[[str], Awaitable[bool]],
    field_value: str = "",
    validate: Callable[[str], str | None] | None = None,
    field_hint: str = "",
) -> None:
    """
    Create a text input dialog matching the proven pattern from clients.py.

    This is EXACTLY what clients.py:384-439 does inline (30 lines).
    Now it's 1 line: create_text_input_dialog(page, "Add Client", "Name", save_fn)

    Args:
        page: Flet page instance
        title: Dialog title
        field_label: Label for the input field
        on_save_async: Async function that receives input value, returns True on success
        field_value: Initial value for the field
        validate: Optional validator that returns error message or None
        field_hint: Hint text for the field

    Example:
        async def save_client_async(name: str) -> bool:
            result = await run_sync_in_executor(safe_server_call, bridge, 'add_client', {'name': name})
            if result.get('success'):
                show_success_message(page, f"Client {name} added")
                return True
            else:
                show_error_message(page, f"Failed: {result.get('error')}")
                return False

        create_text_input_dialog(page, "Add Client", "Client Name", save_client_async)
    """
    from FletV2.utils.user_feedback import show_error_message

    input_field = ft.TextField(
        label=field_label,
        value=field_value,
        hint_text=field_hint,
        autofocus=True,
    )

    async def handle_save_async(_e: ft.ControlEvent) -> None:
        value = input_field.value
        if not value or not value.strip():
            show_error_message(page, f"{field_label} is required")
            return

        if validate:
            error = validate(value.strip())
            if error:
                show_error_message(page, error)
                return

        success = await on_save_async(value.strip())
        if success:
            page.close(dialog)

    def handle_save(event: ft.ControlEvent) -> None:
        if hasattr(page, "run_task"):
            page.run_task(handle_save_async, event)
        else:
            asyncio.create_task(handle_save_async(event))

    dialog = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Column([input_field], tight=True, height=120),
        actions=[
            ft.TextButton("Cancel", on_click=lambda _: page.close(dialog)),
            ft.FilledButton("Save", on_click=handle_save),
        ],
    )
    page.open(dialog)


def create_multi_field_dialog(
    page: ft.Page,
    title: str,
    fields: list[tuple[str, str, str]],  # (label, key, hint)
    on_save_async: Callable[[dict[str, str]], Awaitable[bool]],
    initial_values: dict[str, str] | None = None,
) -> None:
    """
    Create a multi-field dialog matching the proven pattern from clients.py.

    This is the pattern from clients.py:384-439 for add/edit forms with multiple fields.

    Args:
        page: Flet page instance
        title: Dialog title
        fields: List of (label, key, hint_text) tuples for each field
        on_save_async: Async function that receives dict of values, returns True on success
        initial_values: Optional dict of initial values for fields

    Example:
        fields = [
            ("Client Name", "name", "Enter client name"),
            ("IP Address", "ip_address", "Enter IP address"),
        ]

        async def save_client_async(data: dict[str, str]) -> bool:
            result = await run_sync_in_executor(safe_server_call, bridge, 'add_client', data)
            # ... handle result
            return result.get('success', False)

        create_multi_field_dialog(page, "Add Client", fields, save_client_async)
    """
    from FletV2.utils.user_feedback import show_error_message

    initial_values = initial_values or {}
    field_controls: dict[str, ft.TextField] = {}

    # Create fields
    controls_list = []
    for label, key, hint in fields:
        field = ft.TextField(
            label=label,
            value=initial_values.get(key, ""),
            hint_text=hint,
        )
        field_controls[key] = field
        controls_list.append(field)

    async def handle_save_async(_e: ft.ControlEvent) -> None:
        # Collect values
        data = {}
        for key, field in field_controls.items():
            data[key] = field.value.strip() if field.value else ""

        # Basic validation
        for label, key, _ in fields:
            if not data.get(key):
                show_error_message(page, f"{label} is required")
                return

        success = await on_save_async(data)
        if success:
            page.close(dialog)

    def handle_save(event: ft.ControlEvent) -> None:
        if hasattr(page, "run_task"):
            page.run_task(handle_save_async, event)
        else:
            asyncio.create_task(handle_save_async(event))

    dialog = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Column(controls_list, height=min(200, len(fields) * 80), scroll=ft.ScrollMode.AUTO),
        actions=[
            ft.TextButton("Cancel", on_click=lambda _: page.close(dialog)),
            ft.FilledButton("Save", on_click=handle_save),
        ],
    )
    page.open(dialog)


def create_confirmation_dialog(
    page: ft.Page,
    title: str,
    message: str,
    on_confirm_async: Callable[[], Awaitable[bool]],
    confirm_text: str = "Confirm",
    confirm_color: str | None = None,
    is_destructive: bool = False,
) -> None:
    """
    Create a confirmation dialog matching the proven pattern from clients.py.

    This is EXACTLY what clients.py:302-341 (disconnect) and 343-382 (delete) do inline.

    Args:
        page: Flet page instance
        title: Dialog title
        message: Confirmation message
        on_confirm_async: Async function to call on confirm, returns True on success
        confirm_text: Text for confirm button
        confirm_color: Optional color for confirm button
        is_destructive: If True, uses red button (for delete operations)

    Example:
        async def delete_client_async() -> bool:
            result = await run_sync_in_executor(safe_server_call, bridge, 'delete_client', client_id)
            if result.get('success'):
                show_success_message(page, "Client deleted")
                load_clients_data()
                return True
            else:
                show_error_message(page, f"Failed: {result.get('error')}")
                return False

        create_confirmation_dialog(
            page,
            "Delete Client",
            f"Are you sure you want to delete {client_name}?\\n\\nThis action cannot be undone.",
            delete_client_async,
            confirm_text="Delete",
            is_destructive=True
        )
    """
    async def handle_confirm_async(_e: ft.ControlEvent) -> None:
        success = await on_confirm_async()
        if success:
            page.close(dialog)

    def handle_confirm(event: ft.ControlEvent) -> None:
        if hasattr(page, "run_task"):
            page.run_task(handle_confirm_async, event)
        else:
            asyncio.create_task(handle_confirm_async(event))

    # Determine button color
    if is_destructive:
        button_style = ft.ButtonStyle(bgcolor=ft.Colors.RED)
    elif confirm_color:
        button_style = ft.ButtonStyle(bgcolor=confirm_color)
    else:
        button_style = None

    dialog = ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Cancel", on_click=lambda _: page.close(dialog)),
            ft.FilledButton(confirm_text, on_click=handle_confirm, style=button_style),
        ],
    )
    page.open(dialog)


def create_info_dialog(
    page: ft.Page,
    title: str,
    content: str | ft.Control,
    width: int | None = None,
    height: int | None = None,
) -> None:
    """
    Create an information dialog for displaying details.

    This is the pattern from clients.py for showing client details.

    Args:
        page: Flet page instance
        title: Dialog title
        content: Content to display (text or Flet control)
        width: Optional dialog width
        height: Optional dialog height

    Example:
        details = ft.Column([
            ft.Text(f"Name: {client['name']}"),
            ft.Text(f"IP: {client['ip_address']}"),
            ft.Text(f"Status: {client['status']}"),
        ])

        create_info_dialog(page, "Client Details", details, width=400)
    """
    if isinstance(content, str):
        content_control = ft.Text(content, selectable=True)
    else:
        content_control = content

    container = ft.Container(
        content=content_control,
        width=width,
        height=height,
        padding=10 if width or height else None,
    )

    dialog = ft.AlertDialog(
        title=ft.Text(title),
        content=container,
        actions=[
            ft.FilledButton("OK", on_click=lambda _: page.close(dialog)),
        ],
    )
    page.open(dialog)
