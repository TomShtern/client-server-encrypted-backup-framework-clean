#!/usr/bin/env python3
"""
Simplified Files View - The Flet Way
~400 lines instead of 931 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, AlertDialog, and FilePicker.
Clean file management with server integration and graceful fallbacks.
"""

# Standard library imports
import asyncio
import contextlib
import hashlib
import os
import sys
from datetime import datetime
from typing import Any

# Ensure repository and package roots are on sys.path for runtime resolution
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Third-party imports
import aiofiles
import flet as ft

# ALWAYS import this in any Python file that deals with subprocess or console I/O
import Shared.utils.utf8_solution as _  # noqa: F401

try:
    from FletV2.utils.debug_setup import get_logger
except ImportError:  # pragma: no cover - fallback logging
    import logging

    from FletV2 import config

    def get_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name or __name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if getattr(config, "DEBUG_MODE", False) else logging.WARNING)
        return logger

from FletV2.utils.async_helpers import run_sync_in_executor, safe_server_call
from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.state_manager import StateManager
from FletV2.utils.ui_components import AppCard, create_status_pill
from FletV2.utils.user_feedback import show_error_message, show_success_message
from FletV2.utils.ui_builders import (
    create_action_button,
    create_filter_dropdown,
    create_search_bar,
    create_view_header,
)

logger = get_logger(__name__)


def _build_metric_card(title: str, value_control: ft.Control, icon: str) -> ft.Card:
    """Create a reusable metric card for the files overview."""

    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, size=24), ft.Text(title, size=14)]),
                value_control,
            ], spacing=8),
            padding=20,
        ),
        elevation=2,
    )


def create_files_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    _state_manager: StateManager | None = None
) -> Any:
    """Simple files view using Flet's built-in components."""
    logger.info("Creating simplified files view")

    # Simple state management
    search_query = ""
    status_filter = "all"
    type_filter = "all"
    files_data = []

    # Load file data from server - ASYNC VERSION to prevent UI blocking
    async def _fetch_files_async() -> list[dict[str, Any]]:
        """Fetch files from server asynchronously."""
        if not server_bridge:
            return []

        result = await run_sync_in_executor(safe_server_call, server_bridge, 'get_files')
        if result.get('success'):
            data = result.get('data', [])
            if isinstance(data, list):
                return data

        logger.error(f"Failed to fetch files from server: {result.get('error', 'Unknown error')}")
        return []

    def load_files_data() -> None:
        """Load file data using async pattern to avoid blocking UI."""
        nonlocal files_data

        async def _load_and_apply() -> None:
            nonlocal files_data
            new_files = await _fetch_files_async()
            files_data = new_files
            update_table()

        if hasattr(page, "run_task"):
            page.run_task(_load_and_apply)
        else:
            asyncio.get_event_loop().create_task(_load_and_apply())

    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024*1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024*1024):.1f} MB"

    def get_file_type_icon(file_type: str) -> str:
        """Get file type icon."""
        type_icons = {
            "document": ft.Icons.DESCRIPTION,
            "image": ft.Icons.IMAGE,
            "video": ft.Icons.VIDEO_FILE,
            "code": ft.Icons.CODE,
            "archive": ft.Icons.FOLDER_ZIP,
        }
        return type_icons.get(file_type, ft.Icons.INSERT_DRIVE_FILE)

    def get_status_type(status: str) -> str:
        """Map file status to status pill type."""
        status_mapping = {
            "complete": "success",     # Green for completed files
            "verified": "info",        # Blue for verified files
            "uploading": "warning",    # Orange for files in progress
            "queued": "queued",        # Amber for queued files
            "failed": "error",         # Red for failed files
            "pending": "queued",       # Amber for pending files
            "unknown": "unknown"       # Light Blue Grey for unknown states
        }
        return status_mapping.get(status.lower(), "default")

    # Create DataTable using Flet's built-in functionality with enhanced header
    files_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Size")),
            ft.DataColumn(ft.Text("Type")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Modified")),
            ft.DataColumn(ft.Text("Actions")),
        ],
        rows=[],
        heading_row_color="#212121",  # Enhanced darker header as specified in document
        border_radius=12,
        expand=True
    )

    total_files_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
    complete_files_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
    total_size_value = ft.Text("0 B", size=24, weight=ft.FontWeight.BOLD)
    failed_files_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)

    def filter_files() -> list[dict[str, Any]]:
        """Filter files based on search and filters."""
        filtered = files_data.copy()

        # Apply search filter
        if search_query.strip():
            query = search_query.lower()
            filtered = [
                file for file in filtered
                if query in file.get("name", "").lower()
            ]

        # Apply status filter
        if status_filter != "all":
            filtered = [
                file for file in filtered
                if file.get("status", "") == status_filter
            ]

        # Apply type filter
        if type_filter != "all":
            filtered = [
                file for file in filtered
                if file.get("type", "") == type_filter
            ]

        return filtered

    def update_table() -> None:
        """Update table using Flet's simple patterns."""
        filtered_files = filter_files()
        files_table.rows.clear()

        for file in filtered_files:
            file_type = file.get("type", "unknown")
            status = file.get("status", "unknown")

            files_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row([
                                ft.Icon(get_file_type_icon(file_type), size=16),
                                ft.Text(file.get("name", ""), size=13)
                            ], spacing=8)
                        ),
                        ft.DataCell(ft.Text(format_file_size(file.get("size", 0)))),
                        ft.DataCell(ft.Text(file_type.title())),
                        ft.DataCell(create_status_pill(status, get_status_type(status))),
                        ft.DataCell(ft.Text(file.get("modified", ""))),
                        ft.DataCell(
                            ft.PopupMenuButton(
                                icon=ft.Icons.MORE_VERT,
                                items=[
                                    ft.PopupMenuItem(text="Download", icon=ft.Icons.DOWNLOAD,
                                                   on_click=lambda _e, f=file: download_file(f)),
                                    ft.PopupMenuItem(text="Verify", icon=ft.Icons.VERIFIED,
                                                   on_click=lambda _e, f=file: verify_file(f)),
                                    ft.PopupMenuItem(text="Delete", icon=ft.Icons.DELETE,
                                                   on_click=lambda _e, f=file: delete_file(f)),
                                ]
                            )
                        )
                    ]
                )
            )

        files_table.update()
        update_stats_display()

    def update_stats_display() -> None:
        """Update the stats display with current file data."""
        total_files = len(files_data)
        complete_files = len([f for f in files_data if f.get('status') == 'complete'])
        total_size = sum(f.get('size', 0) for f in files_data)
        failed_files = len([f for f in files_data if f.get('status') == 'failed'])

        total_files_value.value = str(total_files)
        complete_files_value.value = str(complete_files)
        total_size_value.value = format_file_size(total_size)
        failed_files_value.value = str(failed_files)

        for control in (
            total_files_value,
            complete_files_value,
            total_size_value,
            failed_files_value,
        ):
            with contextlib.suppress(Exception):
                control.update()

    # File action handlers
    def download_file(file: dict[str, Any]) -> None:
        """Download file using FilePicker."""
        async def save_file(e: ft.FilePickerResultEvent) -> None:
            if not e.path:
                return
            try:
                if server_bridge:
                    file_id = file.get('id')
                    if not file_id or not isinstance(file_id, str):
                        show_error_message(page, "Invalid file ID")
                        return
                    result = await run_sync_in_executor(safe_server_call, server_bridge, 'download_file', file_id, e.path)
                    if result.get('success'):
                        show_success_message(page, f"Downloaded {file.get('name')} to {e.path}")
                    else:
                        show_error_message(page, f"Download failed: {result.get('error', 'Unknown error')}")
                else:
                    show_error_message(page, "Server not connected. Please start the backup server.")
                    return
            except Exception as ex:
                show_error_message(page, f"Download error: {ex}")

        def handle_picker_result(event: ft.FilePickerResultEvent) -> None:
            if hasattr(page, "run_task"):
                page.run_task(save_file, event)
            else:
                asyncio.get_event_loop().create_task(save_file(event))

        file_picker = ft.FilePicker(on_result=handle_picker_result)
        page.overlay.append(file_picker)
        file_picker.update()  # Ensure FilePicker is properly attached before use
        file_picker.save_file(
            dialog_title="Save File",
            file_name=file.get('name', 'file.txt')
        )

    async def _verify_file_async(file_data: dict[str, Any]) -> None:
        file_name = file_data.get('name', 'Unknown')
        file_id = file_data.get('id')

        if not file_id or not isinstance(file_id, str):
            show_error_message(page, "Invalid file ID")
            return

        try:
            result = await run_sync_in_executor(safe_server_call, server_bridge, 'verify_file', file_id)
        except Exception as exc:  # pragma: no cover - UI feedback path
            show_error_message(page, f"Verification error: {exc}")
            return

        if isinstance(result, dict):
            if result.get('success'):
                verification_data = result.get('data', {})
                show_verification_dialog(file_name, verification_data, "Server")
                return

            show_error_message(page, f"Verification failed: {result.get('error', 'Unknown error')}")
            return

        if isinstance(result, bool):
            if result:
                verification_data = {
                    'size': file_data.get('size', 0),
                    'modified': file_data.get('modified', 'Unknown'),
                    'status': 'verified'
                }
                show_verification_dialog(file_name, verification_data, "Server")
            else:
                show_error_message(page, "File verification failed")
            return

        show_error_message(page, f"Unexpected verification result type: {type(result)}")

    def verify_file(file: dict[str, Any]) -> None:
        """Verify file integrity without blocking the UI."""
        if not server_bridge:
            show_error_message(page, "Server not connected. Please start the backup server.")
            return

        if hasattr(page, "run_task"):
            page.run_task(_verify_file_async, file)
        else:
            asyncio.get_event_loop().create_task(_verify_file_async(file))

    def show_verification_dialog(file_name: str, data: dict[str, Any], mode: str) -> None:
        """Show verification results dialog."""
        verification_dialog = ft.AlertDialog(
            title=ft.Text(f"Verification Results - {mode}"),
            content=ft.Column([
                ft.Text(f"File: {file_name}"),
                ft.Text(f"Size: {format_file_size(data.get('size', 0))}"),
                ft.Text(f"Modified: {data.get('modified', 'Unknown')}"),
                ft.Row([
                    ft.Text("Status: "),
                    create_status_pill(data.get('status', 'Unknown'), get_status_type(data.get('status', 'Unknown')))
                ], spacing=8),
                ft.Text("SHA256 Hash:", weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.Text(data.get('hash', 'N/A'), selectable=True, size=12),
                    bgcolor=ft.Colors.SURFACE_TINT,
                    padding=8,
                    border_radius=4
                ),
            ], spacing=10, height=250, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Close", on_click=lambda _e: page.close(verification_dialog))
            ],
        )
        page.open(verification_dialog)

    def delete_file(file: dict[str, Any]) -> None:
        """Delete file with confirmation."""
        async def confirm_delete(_e: ft.ControlEvent) -> None:
            if not server_bridge:
                show_error_message(page, "Server not connected. Please start the backup server.")
                page.close(delete_dialog)
                return

            file_id = file.get('id')
            if not file_id or not isinstance(file_id, str):
                show_error_message(page, "Invalid file ID")
                page.close(delete_dialog)
                return

            result = await run_sync_in_executor(safe_server_call, server_bridge, 'delete_file', file_id)

            if result.get('success'):
                show_success_message(page, f"File {file.get('name')} deleted")
                load_files_data()
            else:
                show_error_message(page, f"Delete failed: {result.get('error', 'Unknown error')}")

            page.close(delete_dialog)

        delete_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete {file.get('name', 'this file')}?\n\nThis action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: page.close(delete_dialog)),
                ft.FilledButton("Delete", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED)),
            ],
        )
        page.open(delete_dialog)

    # Search and filter handlers
    def on_search_change(e: ft.ControlEvent) -> None:
        """Handle search input."""
        nonlocal search_query
        search_query = e.control.value
        update_table()

    def on_status_filter_change(e: ft.ControlEvent) -> None:
        """Handle status filter change."""
        nonlocal status_filter
        status_filter = e.control.value
        update_table()

    def on_type_filter_change(e: ft.ControlEvent) -> None:
        """Handle type filter change."""
        nonlocal type_filter
        type_filter = e.control.value
        update_table()

    def refresh_files(_e: ft.ControlEvent) -> None:
        """Refresh files list."""
        load_files_data()
        show_success_message(page, "Files refreshed")

    # Create UI components
    search_field = create_search_bar(
        on_search_change,
        placeholder="Search files…",
    )

    status_filter_dropdown = create_filter_dropdown(
        "Status",
        [
            ("all", "All"),
            ("complete", "Complete"),
            ("verified", "Verified"),
            ("uploading", "Uploading"),
            ("queued", "Queued"),
            ("failed", "Failed"),
        ],
        on_status_filter_change,
        value=status_filter,
        width=200,
    )

    type_filter_dropdown = create_filter_dropdown(
        "Type",
        [
            ("all", "All"),
            ("document", "Documents"),
            ("image", "Images"),
            ("video", "Videos"),
            ("code", "Code"),
            ("archive", "Archives"),
        ],
        on_type_filter_change,
        value=type_filter,
        width=200,
    )

    filters_row = ft.ResponsiveRow(
        controls=[
            ft.Container(content=search_field, col={"xs": 12, "sm": 8, "md": 6, "lg": 5}),
            ft.Container(content=status_filter_dropdown, col={"xs": 12, "sm": 4, "md": 3, "lg": 2}),
            ft.Container(content=type_filter_dropdown, col={"xs": 12, "sm": 4, "md": 3, "lg": 2}),
            ft.Container(
                content=create_action_button("Refresh", refresh_files, icon=ft.Icons.REFRESH, primary=False),
                col={"xs": 12, "sm": 12, "md": 3, "lg": 2},
                alignment=ft.alignment.center_left,
            ),
        ],
        spacing=12,
        run_spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    stats_row = ft.ResponsiveRow([
        ft.Container(
            content=_build_metric_card("Total files", total_files_value, ft.Icons.FOLDER),
            col={"sm": 12, "md": 6, "lg": 3},
        ),
        ft.Container(
            content=_build_metric_card("Complete", complete_files_value, ft.Icons.CHECK_CIRCLE),
            col={"sm": 12, "md": 6, "lg": 3},
        ),
        ft.Container(
            content=_build_metric_card("Total size", total_size_value, ft.Icons.STORAGE),
            col={"sm": 12, "md": 6, "lg": 3},
        ),
        ft.Container(
            content=_build_metric_card("Failed", failed_files_value, ft.Icons.ERROR),
            col={"sm": 12, "md": 6, "lg": 3},
        ),
    ], spacing=16, run_spacing=16)

    stats_section = AppCard(stats_row, title="At a glance")
    filters_section = AppCard(filters_row, title="Filters")
    table_section = AppCard(files_table, title="Files")
    table_section.expand = True

    header = create_view_header(
        "Files management",
        icon=ft.Icons.FOLDER,
        description="Review backed up files and manage integrity checks.",
    )

    main_content = ft.Column(
        [
            header,
            stats_section,
            filters_section,
            table_section,
        ],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    files_container = ft.Container(
        content=main_content,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        expand=True,
    )

    def setup_subscriptions() -> None:
        """Setup subscriptions and initial data loading after view is added to page."""
        load_files_data()

    def dispose() -> None:
        """Clean up subscriptions and resources."""
        logger.debug("Disposing files view")
        # No subscriptions to clean up currently

    return files_container, dispose, setup_subscriptions
