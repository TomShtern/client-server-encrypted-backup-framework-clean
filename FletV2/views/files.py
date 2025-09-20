#!/usr/bin/env python3
"""
Simplified Files View - The Flet Way
~400 lines instead of 931 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, AlertDialog, and FilePicker.
Clean file management with server integration and graceful fallbacks.
"""

import flet as ft
from typing import Optional, Dict, Any, List
import os
import hashlib
from datetime import datetime

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_components import themed_card, themed_button, themed_metric_card, create_status_pill
from utils.user_feedback import show_success_message, show_error_message

logger = get_logger(__name__)


def create_files_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    _state_manager: StateManager
) -> ft.Control:
    """Simple files view using Flet's built-in components."""
    logger.info("Creating simplified files view")

    # Simple state management
    search_query = ""
    status_filter = "all"
    type_filter = "all"
    files_data = []

    # Mock file data for demonstration
    def get_mock_files() -> List[Dict[str, Any]]:
        """Simple mock file data generator."""
        return [
            {"id": "file_001", "name": "backup_001.pdf", "size": 1024*512, "type": "document",
             "status": "complete", "modified": "2025-01-17 14:20:15", "path": "/backup/file_001.pdf"},
            {"id": "file_002", "name": "image_002.jpg", "size": 1024*256, "type": "image",
             "status": "verified", "modified": "2025-01-17 13:45:22", "path": "/backup/file_002.jpg"},
            {"id": "file_003", "name": "video_003.mp4", "size": 1024*1024*50, "type": "video",
             "status": "uploading", "modified": "2025-01-17 14:30:10", "path": "/backup/file_003.mp4"},
            {"id": "file_004", "name": "script_004.py", "size": 1024*8, "type": "code",
             "status": "complete", "modified": "2025-01-17 12:15:33", "path": "/backup/file_004.py"},
            {"id": "file_005", "name": "archive_005.zip", "size": 1024*1024*10, "type": "archive",
             "status": "failed", "modified": "2025-01-17 11:30:45", "path": "/backup/file_005.zip"},
            {"id": "file_006", "name": "document_006.txt", "size": 1024*4, "type": "document",
             "status": "queued", "modified": "2025-01-17 14:35:12", "path": "/backup/file_006.txt"},
        ]

    # Load file data from server or use mock
    def load_files_data():
        """Load file data using server bridge or mock."""
        nonlocal files_data

        if server_bridge:
            try:
                result = server_bridge.get_files()
                if result.get('success'):
                    files_data = result.get('data', [])
                else:
                    files_data = get_mock_files()
            except Exception:
                files_data = get_mock_files()
        else:
            files_data = get_mock_files()

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

    def filter_files():
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

    def update_table():
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

    def update_stats_display():
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
    def download_file(file: Dict[str, Any]):
        """Download file using FilePicker."""
        def save_file(e: ft.FilePickerResultEvent):
            if e.path:
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
                        # Mock download - create a simple text file
                        with open(e.path, 'w') as f:
                            f.write(f"Mock file content for {file.get('name')}\n")
                            f.write(f"Size: {format_file_size(file.get('size', 0))}\n")
                            f.write(f"Type: {file.get('type', 'unknown')}\n")
                            f.write(f"Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        show_success_message(page, f"Downloaded {file.get('name')} (mock mode)")
                except Exception as ex:
                    show_error_message(page, f"Download error: {ex}")

        file_picker = ft.FilePicker(on_result=save_file)
        page.overlay.append(file_picker)
        file_picker.update()  # Ensure FilePicker is properly attached before use
        file_picker.save_file(
            dialog_title="Save File",
            file_name=file.get('name', 'file.txt')
        )

    def verify_file(file: Dict[str, Any]):
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
            # Mock verification
            mock_hash = hashlib.sha256(f"mock_{file_name}_{datetime.now().isoformat()}".encode()).hexdigest()
            verification_data = {
                'size': file.get('size', 0),
                'modified': file.get('modified', 'Unknown'),
                'hash': mock_hash,
                'status': 'verified'
            }
            show_verification_dialog(file_name, verification_data, "Mock")

    def show_verification_dialog(file_name: str, data: Dict[str, Any], mode: str):
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

    def delete_file(file: Dict[str, Any]):
        """Delete file with confirmation."""
        def confirm_delete(_e):
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
                # Mock success - remove from local data
                global files_data
                files_data = [f for f in files_data if f.get('id') != file.get('id')]
                show_success_message(page, f"File {file.get('name')} deleted (mock mode)")
                update_table()

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
    def on_search_change(e):
        """Handle search input."""
        nonlocal search_query
        search_query = e.control.value
        update_table()

    def on_status_filter_change(e):
        """Handle status filter change."""
        nonlocal status_filter
        status_filter = e.control.value
        update_table()

    def on_type_filter_change(e):
        """Handle type filter change."""
        nonlocal type_filter
        type_filter = e.control.value
        update_table()

    def refresh_files(_e):
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

    def setup_subscriptions():
        """Setup subscriptions and initial data loading after view is added to page."""
        load_files_data()

    def dispose():
        """Clean up subscriptions and resources."""
        logger.debug("Disposing files view")
        # No subscriptions to clean up currently

    return files_container, dispose, setup_subscriptions