"""
Dialog Builder - Reusable dialog templates for CRUD operations.

Provides a consistent, neumorphic-styled dialog system for:
- Add/Edit forms
- Delete confirmations
- Information displays
- Custom dialogs

Usage:
    from utils.dialog_builder import show_add_client_dialog, show_delete_confirmation

    # Show add dialog
    result = await show_add_client_dialog(page, state_manager, server_bridge)
    if result.get('success'):
        print(f"Client added: {result.get('data')}")
"""

import flet as ft
from typing import Any, Callable, Dict, Optional
from theme import MODERATE_NEUMORPHIC_SHADOWS, GLASS_STRONG


# =============================================================================
# GENERIC DIALOG BUILDERS
# =============================================================================

def create_form_dialog(
    title: str,
    fields: list[Dict[str, Any]],
    on_submit: Callable,
    on_cancel: Callable,
    submit_text: str = "Submit",
    cancel_text: str = "Cancel"
) -> ft.AlertDialog:
    """
    Create a form dialog with neumorphic styling.

    Args:
        title: Dialog title
        fields: List of field configs:
            {
                'key': 'field_name',
                'label': 'Display Label',
                'type': 'text'|'number'|'password'|'dropdown'|'checkbox'|'textarea',
                'value': 'default_value',
                'required': True|False,
                'options': ['opt1', 'opt2']  # For dropdown
                'hint': 'Helper text'
            }
        on_submit: Callback(data: dict) when form submitted
        on_cancel: Callback() when cancelled
        submit_text: Submit button text
        cancel_text: Cancel button text

    Returns:
        ft.AlertDialog configured with form
    """
    # Create refs for all fields
    field_refs = {}
    form_controls = []

    for field_config in fields:
        key = field_config['key']
        label = field_config['label']
        field_type = field_config.get('type', 'text')
        value = field_config.get('value', '')
        required = field_config.get('required', False)
        hint = field_config.get('hint', '')
        options = field_config.get('options', [])

        # Create appropriate control based on type
        if field_type == 'text':
            control = ft.TextField(
                label=label,
                value=str(value) if value else '',
                hint_text=hint,
                filled=True,
                border_radius=8,
            )
        elif field_type == 'number':
            control = ft.TextField(
                label=label,
                value=str(value) if value else '',
                hint_text=hint,
                filled=True,
                border_radius=8,
                keyboard_type=ft.KeyboardType.NUMBER,
            )
        elif field_type == 'password':
            control = ft.TextField(
                label=label,
                value=str(value) if value else '',
                hint_text=hint,
                filled=True,
                border_radius=8,
                password=True,
                can_reveal_password=True,
            )
        elif field_type == 'dropdown':
            control = ft.Dropdown(
                label=label,
                value=str(value) if value else (options[0] if options else ''),
                hint_text=hint,
                options=[ft.dropdown.Option(opt) for opt in options],
                filled=True,
                border_radius=8,
            )
        elif field_type == 'checkbox':
            control = ft.Checkbox(
                label=label,
                value=bool(value),
            )
        elif field_type == 'textarea':
            control = ft.TextField(
                label=label,
                value=str(value) if value else '',
                hint_text=hint,
                filled=True,
                border_radius=8,
                multiline=True,
                min_lines=3,
                max_lines=10,
            )
        else:
            control = ft.TextField(label=label, value=str(value), filled=True, border_radius=8)

        field_refs[key] = control

        # Add required indicator
        if required:
            form_controls.append(
                ft.Row([
                    control,
                    ft.Text("*", color=ft.Colors.ERROR, size=20)
                ], spacing=5)
            )
        else:
            form_controls.append(control)

    # Submit handler
    def handle_submit(e):
        # Collect form data
        data = {}
        for key, control in field_refs.items():
            if isinstance(control, ft.Checkbox):
                data[key] = control.value
            elif isinstance(control, ft.Dropdown):
                data[key] = control.value
            else:
                data[key] = control.value

        # Validate required fields
        for field_config in fields:
            if field_config.get('required', False):
                value = data.get(field_config['key'])
                if not value or (isinstance(value, str) and not value.strip()):
                    # Show error - field required
                    return

        on_submit(data)

    # Create dialog
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, size=24, weight=ft.FontWeight.BOLD),
        content=ft.Container(
            content=ft.Column(
                controls=form_controls,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=500,
            padding=ft.Padding(20, 20, 20, 20),
        ),
        actions=[
            ft.TextButton(cancel_text, on_click=lambda e: on_cancel()),
            ft.FilledButton(submit_text, on_click=handle_submit),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return dialog


def create_confirmation_dialog(
    title: str,
    message: str,
    on_confirm: Callable,
    on_cancel: Callable,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    danger: bool = False
) -> ft.AlertDialog:
    """
    Create a confirmation dialog (e.g., for delete operations).

    Args:
        title: Dialog title
        message: Confirmation message
        on_confirm: Callback() when confirmed
        on_cancel: Callback() when cancelled
        confirm_text: Confirm button text
        cancel_text: Cancel button text
        danger: If True, uses error/warning colors

    Returns:
        ft.AlertDialog configured for confirmation
    """
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(
                ft.Icons.WARNING if danger else ft.Icons.INFO,
                color=ft.Colors.ERROR if danger else ft.Colors.PRIMARY,
                size=30
            ),
            ft.Text(title, size=22, weight=ft.FontWeight.BOLD),
        ], spacing=10),
        content=ft.Container(
            content=ft.Text(message, size=16),
            padding=ft.Padding(20, 10, 20, 10),
        ),
        actions=[
            ft.TextButton(cancel_text, on_click=lambda e: on_cancel()),
            ft.FilledButton(
                confirm_text,
                on_click=lambda e: on_confirm(),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.ERROR if danger else ft.Colors.PRIMARY
                )
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    return dialog


# =============================================================================
# CLIENT-SPECIFIC DIALOGS
# =============================================================================

async def show_add_client_dialog(
    page: ft.Page,
    state_manager: Any,
    server_bridge: Any
) -> Dict[str, Any]:
    """
    Show dialog to add a new client.

    Returns:
        {'success': True, 'data': client_data} on success
        {'success': False, 'error': 'message'} on cancel/error
    """
    result = {'success': False}

    def on_submit(data):
        nonlocal result
        result = {'success': True, 'data': data}
        page.close(dialog)

    def on_cancel():
        nonlocal result
        result = {'success': False, 'error': 'Cancelled'}
        page.close(dialog)

    dialog = create_form_dialog(
        title="Add New Client",
        fields=[
            {'key': 'name', 'label': 'Client Name', 'type': 'text', 'required': True, 'hint': 'e.g., Production Server'},
            {'key': 'host', 'label': 'Host', 'type': 'text', 'required': True, 'hint': 'IP address or hostname'},
            {'key': 'port', 'label': 'Port', 'type': 'number', 'required': True, 'value': '5500'},
            {'key': 'encryption', 'label': 'Encryption', 'type': 'dropdown', 'options': ['AES-256', 'AES-128', 'None'], 'value': 'AES-256'},
            {'key': 'auto_backup', 'label': 'Enable Auto Backup', 'type': 'checkbox', 'value': True},
        ],
        on_submit=on_submit,
        on_cancel=on_cancel,
        submit_text="Add Client",
        cancel_text="Cancel"
    )

    page.open(dialog)

    # Wait for dialog to close
    while dialog.open:
        await page.update_async()

    return result


async def show_edit_client_dialog(
    page: ft.Page,
    state_manager: Any,
    server_bridge: Any,
    client_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Show dialog to edit an existing client.

    Args:
        client_data: Current client data to pre-populate form

    Returns:
        {'success': True, 'data': updated_client_data} on success
        {'success': False, 'error': 'message'} on cancel/error
    """
    result = {'success': False}

    def on_submit(data):
        nonlocal result
        result = {'success': True, 'data': {**client_data, **data}}
        page.close(dialog)

    def on_cancel():
        nonlocal result
        result = {'success': False, 'error': 'Cancelled'}
        page.close(dialog)

    dialog = create_form_dialog(
        title=f"Edit Client: {client_data.get('name', 'Unknown')}",
        fields=[
            {'key': 'name', 'label': 'Client Name', 'type': 'text', 'required': True, 'value': client_data.get('name', '')},
            {'key': 'host', 'label': 'Host', 'type': 'text', 'required': True, 'value': client_data.get('host', '')},
            {'key': 'port', 'label': 'Port', 'type': 'number', 'required': True, 'value': client_data.get('port', 5500)},
            {'key': 'encryption', 'label': 'Encryption', 'type': 'dropdown', 'options': ['AES-256', 'AES-128', 'None'], 'value': client_data.get('encryption', 'AES-256')},
            {'key': 'auto_backup', 'label': 'Enable Auto Backup', 'type': 'checkbox', 'value': client_data.get('auto_backup', True)},
        ],
        on_submit=on_submit,
        on_cancel=on_cancel,
        submit_text="Save Changes",
        cancel_text="Cancel"
    )

    page.open(dialog)

    # Wait for dialog to close
    while dialog.open:
        await page.update_async()

    return result


async def show_delete_client_confirmation(
    page: ft.Page,
    client_name: str
) -> bool:
    """
    Show confirmation dialog for deleting a client.

    Args:
        client_name: Name of client to delete

    Returns:
        True if confirmed, False if cancelled
    """
    confirmed = False

    def on_confirm():
        nonlocal confirmed
        confirmed = True
        page.close(dialog)

    def on_cancel():
        nonlocal confirmed
        confirmed = False
        page.close(dialog)

    dialog = create_confirmation_dialog(
        title="Delete Client",
        message=f"Are you sure you want to delete '{client_name}'?\n\nThis action cannot be undone. All backup history for this client will be permanently removed.",
        on_confirm=on_confirm,
        on_cancel=on_cancel,
        confirm_text="Delete",
        cancel_text="Cancel",
        danger=True
    )

    page.open(dialog)

    # Wait for dialog to close
    while dialog.open:
        await page.update_async()

    return confirmed


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def show_info_dialog(page: ft.Page, title: str, message: str):
    """
    Show a simple information dialog.

    Args:
        page: Flet page
        title: Dialog title
        message: Message to display
    """
    def close_dialog(e):
        page.close(dialog)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title, size=22, weight=ft.FontWeight.BOLD),
        content=ft.Text(message, size=16),
        actions=[
            ft.FilledButton("OK", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.open(dialog)


def show_error_dialog(page: ft.Page, title: str, error: str):
    """
    Show an error dialog with red styling.

    Args:
        page: Flet page
        title: Dialog title
        error: Error message
    """
    def close_dialog(e):
        page.close(dialog)

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.ERROR, color=ft.Colors.ERROR, size=30),
            ft.Text(title, size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.ERROR),
        ], spacing=10),
        content=ft.Container(
            content=ft.Text(error, size=16),
            padding=ft.Padding(20, 10, 20, 10),
        ),
        actions=[
            ft.FilledButton(
                "OK",
                on_click=close_dialog,
                style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR)
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.open(dialog)
