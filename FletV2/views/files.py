#!/usr/bin/env python3
"""
Simplified Files View - The Flet Way
~400 lines instead of 931 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, AlertDialog, and FilePicker.
Clean file management with server integration and graceful fallbacks.
"""

# Standard library imports
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

from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.state_manager import StateManager
from FletV2.utils.ui_components import create_status_pill, themed_button, themed_card, themed_metric_card
from FletV2.utils.user_feedback import show_error_message, show_success_message

logger = get_logger(__name__)


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
    async def _fetch_files_async():
        """Fetch files from server asynchronously."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _fetch_files_sync)

    def _fetch_files_sync():
        """Synchronous files fetch (called in executor)."""
        if not server_bridge:
            return []
        try:
            result = server_bridge.get_files()
            return result if isinstance(result, list) else []
        except Exception as ex:
            logger.error(f"Failed to fetch files from server: {ex}")
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
            # Fallback for environments without run_task
            files_data = _fetch_files_sync()
            update_table()

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

        # Update the stat card values
        if stats_row.controls and len(stats_row.controls) >= 4:
            # Update Total Files
            if stats_row.controls[0].controls[0].content:
                stats_row.controls[0].controls[0].content.content.controls[1].value = str(total_files)

            # Update Complete Files
            if stats_row.controls[1].controls[0].content:
                stats_row.controls[1].controls[0].content.content.controls[1].value = str(complete_files)

            # Update Total Size
            if stats_row.controls[2].controls[0].content:
                stats_row.controls[2].controls[0].content.content.controls[1].value = format_file_size(total_size)

            # Update Failed Files
            if stats_row.controls[3].controls[0].content:
                stats_row.controls[3].controls[0].content.content.controls[1].value = str(failed_files)

            stats_row.update()

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
                    result = server_bridge.download_file(file_id, e.path)
                    if result.get('success'):
                        show_success_message(page, f"Downloaded {file.get('name')} to {e.path}")
                    else:
                        show_error_message(page, f"Download failed: {result.get('error', 'Unknown error')}")
                else:
                    show_error_message(page, "Server not connected. Please start the backup server.")
                    return
            except Exception as ex:
                show_error_message(page, f"Download error: {ex}")

        file_picker = ft.FilePicker(on_result=save_file)
        page.overlay.append(file_picker)
        file_picker.update()  # Ensure FilePicker is properly attached before use
        file_picker.save_file(
            dialog_title="Save File",
            file_name=file.get('name', 'file.txt')
        )

    def verify_file(file: dict[str, Any]) -> None:
        """Verify file integrity."""
        file_name = file.get('name', 'Unknown')
        file_path = file.get('path', '')

        if server_bridge:
            file_id = file.get('id')
            if not file_id or not isinstance(file_id, str):
                show_error_message(page, "Invalid file ID")
                return
            try:
                result = server_bridge.verify_file(file_id)

                # Handle both normalized dict format and raw boolean return
                if isinstance(result, bool):
                    # Direct boolean return from mock
                    if result:
                        verification_data = {
                            'size': file.get('size', 0),
                            'modified': file.get('modified', 'Unknown'),
                            'status': 'verified'
                        }
                        show_verification_dialog(file_name, verification_data, "Server")
                    else:
                        show_error_message(page, "File verification failed")
                elif isinstance(result, dict):
                    # Normalized return format
                    if result.get('success'):
                        verification_data = result.get('data', {})
                        show_verification_dialog(file_name, verification_data, "Server")
                    else:
                        show_error_message(page, f"Verification failed: {result.get('error', 'Unknown error')}")
                else:
                    show_error_message(page, f"Unexpected verification result type: {type(result)}")
            except Exception as ex:
                show_error_message(page, f"Verification error: {ex}")
        else:
            if not server_bridge:
                show_error_message(page, "Server not connected. Please start the backup server.")
                return

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
        def confirm_delete(_e: ft.ControlEvent) -> None:
            if server_bridge:
                file_id = file.get('id')
                if not file_id or not isinstance(file_id, str):
                    show_error_message(page, "Invalid file ID")
                    return
                try:
                    result = server_bridge.delete_file(file_id)
                    if result.get('success'):
                        show_success_message(page, f"File {file.get('name')} deleted")
                        load_files_data()
                    else:
                        show_error_message(page, f"Delete failed: {result.get('error', 'Unknown error')}")
                except Exception as ex:
                    show_error_message(page, f"Error: {ex}")
            else:
                show_error_message(page, "Server not connected. Please start the backup server.")
                return

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
    search_field = ft.TextField(
        label="Search files",
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_search_change,
        width=300
    )

    status_filter_dropdown = ft.Dropdown(
        label="Status",
        value="all",
        options=[
            ft.dropdown.Option("all", "All"),
            ft.dropdown.Option("complete", "Complete"),
            ft.dropdown.Option("verified", "Verified"),
            ft.dropdown.Option("uploading", "Uploading"),
            ft.dropdown.Option("queued", "Queued"),
            ft.dropdown.Option("failed", "Failed"),
        ],
        on_change=on_status_filter_change,
        width=120
    )

    type_filter_dropdown = ft.Dropdown(
        label="Type",
        value="all",
        options=[
            ft.dropdown.Option("all", "All"),
            ft.dropdown.Option("document", "Documents"),
            ft.dropdown.Option("image", "Images"),
            ft.dropdown.Option("video", "Videos"),
            ft.dropdown.Option("code", "Code"),
            ft.dropdown.Option("archive", "Archives"),
        ],
        on_change=on_type_filter_change,
        width=120
    )

    # Actions row
    actions_row = ft.Row([
        search_field,
        status_filter_dropdown,
        type_filter_dropdown,
        ft.Container(expand=True),  # Spacer
        themed_button("Refresh", refresh_files, "outlined", ft.Icons.REFRESH),
    ], spacing=10)

    # File stats are now handled by update_stats_display() function

    # Enhanced table with layered card design
    table_card = themed_card(files_table, "Files", page)

    # Initialize stats container for updates
    stats_row = ft.ResponsiveRow([
        ft.Column([themed_metric_card("Total Files", "0", ft.Icons.FOLDER)],
                 col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([themed_metric_card("Complete", "0", ft.Icons.CHECK_CIRCLE)],
                 col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([themed_metric_card("Total Size", "0 B", ft.Icons.STORAGE)],
                 col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([themed_metric_card("Failed", "0", ft.Icons.ERROR)],
                 col={"sm": 12, "md": 6, "lg": 3}),
    ])

    # Main layout with responsive design and scrollbar
    main_content = ft.Column([
        ft.Text("Files Management", size=28, weight=ft.FontWeight.BOLD),
        stats_row,
        actions_row,
        table_card
    ], expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)

    # Create the main container with theme support
    files_container = themed_card(main_content, None, page)  # No title since we have one in content

    def setup_subscriptions() -> None:
        """Setup subscriptions and initial data loading after view is added to page."""
        load_files_data()

    def dispose() -> None:
        """Clean up subscriptions and resources."""
        logger.debug("Disposing files view")
        # No subscriptions to clean up currently

    return files_container, dispose, setup_subscriptions
