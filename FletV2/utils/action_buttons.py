#!/usr/bin/env python3
"""
Reusable action buttons block for the Settings view.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

import flet as ft
from utils.ui_components import create_progress_indicator

from FletV2.utils.debug_setup import get_logger


class SettingsStateProto(Protocol):
    state_manager: Any | None
    page: Any | None
    file_picker: Any | None
    current_settings: dict

    async def save_settings_async(self) -> bool: ...
    async def export_settings(self, fmt: str) -> dict[str, Any]: ...
    async def backup_settings_async(self, backup_name: str) -> dict[str, Any]: ...
    async def import_settings(self, path: str) -> dict[str, Any]: ...
    def _load_default_settings(self) -> dict: ...
    def _update_ui_from_settings(self) -> None: ...

logger = get_logger(__name__)


def create_enhanced_action_buttons(state: SettingsStateProto) -> ft.Column:
    """Create enhanced action buttons with responsive layout, modern styling and progress indicators."""

    # Progress indicators
    save_progress = create_progress_indicator("settings_save", state.state_manager)
    export_progress = create_progress_indicator("settings_export", state.state_manager)
    import_progress = create_progress_indicator("settings_import", state.state_manager)

    async def save_settings_handler(e: ft.ControlEvent) -> None:
        success = await state.save_settings_async()
        if not success and state.state_manager:
            state.state_manager.add_notification("Failed to save settings", "error")

    async def export_handler(e: ft.ControlEvent) -> None:
        result = await state.export_settings("json")
        if not result['success'] and state.state_manager:
            error_msg = result.get('error', 'Unknown error')
            state.state_manager.add_notification(
                f"Export failed: {error_msg}", "error"
            )

    async def backup_handler(e: ft.ControlEvent) -> None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"settings_backup_{timestamp}"
        result = await state.backup_settings_async(backup_name)
        if not result['success'] and state.state_manager:
            error_msg = result.get('error', 'Unknown error')
            state.state_manager.add_notification(
                f"Backup failed: {error_msg}", "error"
            )

    def reset_all_settings(e: ft.ControlEvent) -> None:
        def confirm_reset(e: ft.ControlEvent) -> None:
            state.current_settings = state._load_default_settings()
            state._update_ui_from_settings()
            if state.page:
                state.page.dialog.open = False
                state.page.dialog.update()
            if state.state_manager:
                state.state_manager.add_notification("Settings reset to defaults", "info")

        def cancel_reset(e: ft.ControlEvent) -> None:
            if state.page:
                state.page.dialog.open = False
                state.page.dialog.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Reset All Settings"),
            content=ft.Text(
                "Are you sure you want to reset all settings to their default values?\n\n"
                "This action cannot be undone and will affect:\n"
                "• Server configuration\n"
                "• User interface preferences\n"
                "• Monitoring settings\n"
                "• Security settings\n"
                "• All other configurations"
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    icon=ft.Icons.CANCEL,
                    on_click=cancel_reset,
                    style=ft.ButtonStyle(color=ft.Colors.ON_SURFACE)
                ),
                ft.FilledButton(
                    "Reset All",
                    icon=ft.Icons.RESTORE,
                    on_click=confirm_reset,
                    style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        if state.page:
            state.page.dialog = dialog
            dialog.open = True
            state.page.dialog.update()

    # FilePicker lifecycle management
    def pick_files_result(e: ft.FilePickerResultEvent) -> None:
        if e.files and state.page and hasattr(state.page, "run_task"):
            state.page.run_task(state.import_settings, e.files[0].path)
        else:
            if state.state_manager:
                state.state_manager.add_notification("Import cancelled", "info")

    # Ensure only one FilePicker per view instance
    if not hasattr(state, 'file_picker') or state.file_picker is None:
        state.file_picker = ft.FilePicker(on_result=pick_files_result)
    file_picker = state.file_picker
    if state.page and file_picker not in state.page.overlay:
        state.page.overlay.append(file_picker)

    def import_handler(e: ft.ControlEvent) -> None:
        try:
            if state.file_picker:
                state.file_picker.pick_files(
                    allowed_extensions=["json", "ini"],
                    dialog_title="Select Settings File"
                )
        except Exception as e:
            logger.error(f"Error opening file picker: {e}")
            if state.state_manager:
                state.state_manager.add_notification("Error opening file picker", "error")

    return ft.Column([
        ft.ResponsiveRow([
            ft.Column([
                ft.FilledButton(
                    "Save Settings",
                    icon=ft.Icons.SAVE,
                    on_click=lambda e: (
                        state.page.run_task(save_settings_handler, e)
                        if state.page and hasattr(state.page, "run_task")
                        else None
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY,
                        elevation=2,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    expand=True
                )
            ], col={"sm": 12, "md": 6, "lg": 2}),
            ft.Column([
                ft.OutlinedButton(
                    "Export Backup",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: (
                        state.page.run_task(export_handler, e)
                        if state.page and hasattr(state.page, "run_task")
                        else None
                    ),
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(2, ft.Colors.PRIMARY),
                        color=ft.Colors.PRIMARY,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    expand=True
                )
            ], col={"sm": 12, "md": 6, "lg": 2}),
            ft.Column([
                ft.OutlinedButton(
                    "Create Backup",
                    icon=ft.Icons.BACKUP,
                    on_click=lambda e: (
                        state.page.run_task(backup_handler, e)
                        if state.page and hasattr(state.page, "run_task")
                        else None
                    ),
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(2, ft.Colors.SECONDARY),
                        color=ft.Colors.SECONDARY,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    expand=True
                )
            ], col={"sm": 12, "md": 6, "lg": 2}),
            ft.Column([
                ft.TextButton(
                    "Import Settings",
                    icon=ft.Icons.UPLOAD,
                    on_click=import_handler,
                    style=ft.ButtonStyle(
                        color=ft.Colors.TERTIARY,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    expand=True
                )
            ], col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([
                ft.TextButton(
                    "Reset All",
                    icon=ft.Icons.RESTORE,
                    on_click=reset_all_settings,
                    style=ft.ButtonStyle(
                        color=ft.Colors.ERROR,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    expand=True
                )
            ], col={"sm": 12, "md": 12, "lg": 3}),
        ], spacing=10),
        ft.ResponsiveRow([
            ft.Column([save_progress], col={"sm": 12, "md": 4}),
            ft.Column([export_progress], col={"sm": 12, "md": 4}),
            ft.Column([import_progress], col={"sm": 12, "md": 4}),
        ], spacing=20),
    ], spacing=10)
