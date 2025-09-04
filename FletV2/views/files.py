#!/usr/bin/env python3
"""
Files View for FletV2
An improved implementation using ft.UserControl for better state management.
"""

import flet as ft
from typing import List, Dict, Any
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from utils.debug_setup import get_logger
from config import RECEIVED_FILES_DIR, ASYNC_DELAY, show_mock_data

logger = get_logger(__name__)


class FilesView(ft.UserControl):
    """
    Files view using ft.UserControl for better state management.
    """
    
    def __init__(self, server_bridge, page: ft.Page):
        super().__init__()
        self.server_bridge = server_bridge
        self.page = page
        self.files_data: List[Dict[str, Any]] = []
        self.is_loading = False
        self.last_updated = None
        
        # UI References using ft.Ref for robust access
        self.files_table_ref = ft.Ref[ft.DataTable]()
        self.status_text_ref = ft.Ref[ft.Text]()
        self.search_field_ref = ft.Ref[ft.TextField]()
        self.last_updated_text_ref = ft.Ref[ft.Text]()
        
    def build(self):
        """Build the files view UI."""
        # Create UI components with ft.Ref
        self.files_table_ref = ft.Ref[ft.DataTable]()
        self.status_text_ref = ft.Ref[ft.Text]()
        self.search_field_ref = ft.Ref[ft.TextField]()
        self.last_updated_text_ref = ft.Ref[ft.Text]()
        
        return ft.Column([
            # Header with title and refresh button
            ft.Container(
                content=ft.Row([
                    ft.Text("File Management", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),  # Spacer
                    ft.Row([
                        ft.TextField(
                            label="Search files...",
                            prefix_icon=ft.Icons.SEARCH,
                            width=300,
                            on_change=self._on_search_change,
                            ref=self.search_field_ref
                        ),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Refresh Files",
                            on_click=self._on_refresh_click
                        )
                    ], spacing=10)
                ]),
                padding=ft.Padding(20, 20, 20, 10)
            ),
            
            # Status info
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        value="Loading files...",
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        ref=self.status_text_ref
                    ),
                    ft.Container(expand=True),
                    ft.Text(
                        value="Last updated: Never",
                        color=ft.Colors.ON_SURFACE,
                        size=12,
                        ref=self.last_updated_text_ref
                    )
                ]),
                padding=ft.Padding(20, 0, 20, 10)
            ),
            
            # Files table in a scrollable container
            ft.Container(
                content=ft.Column([
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)), 
                            ft.DataColumn(ft.Text("Modified", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
                        ],
                        rows=[],
                        heading_row_color=ft.Colors.SURFACE,
                        border=ft.border.all(1, ft.Colors.OUTLINE),
                        border_radius=8,
                        data_row_min_height=45,
                        ref=self.files_table_ref
                    )
                ], scroll=ft.ScrollMode.AUTO),
                expand=True,
                padding=ft.Padding(20, 0, 20, 20)
            )
        ], expand=True)
    
    async def _load_files_data_async(self):
        """Asynchronously load files data."""
        if self.is_loading:
            return
            
        self.is_loading = True
        try:
            # Show loading state
            self.status_text_ref.current.value = "Loading files..."
            self.status_text_ref.current.update()
            
            # Load data asynchronously
            if self.server_bridge:
                self.files_data = await self.page.run_thread(self.server_bridge.get_files)
            else:
                # Fallback: scan received_files directory
                self.files_data = await self.page.run_thread(self._scan_files_directory)
            
            # Update last updated timestamp
            self.last_updated = datetime.now()
            self.last_updated_text_ref.current.value = f"Last updated: {self.last_updated.strftime('%H:%M:%S')}"
            
            # Update UI
            self._update_table()
            self.status_text_ref.current.value = f"Showing {len(self.files_data)} files"
            
        except Exception as e:
            logger.error(f"Error loading files data: {e}")
            self.status_text_ref.current.value = "Error loading files data"
        finally:
            self.is_loading = False
            self.update()
    
    def _scan_files_directory(self):
        """Scan received_files directory for files."""
        files_data = []
        
        try:
            if RECEIVED_FILES_DIR.exists():
                for file_path in RECEIVED_FILES_DIR.iterdir():
                    if file_path.is_file():
                        try:
                            stat = file_path.stat()
                            files_data.append({
                                "id": str(hash(file_path.name)) % 10000,
                                "name": file_path.name,
                                "size": stat.st_size,
                                "type": file_path.suffix.lstrip('.') or 'unknown',
                                "owner": "system",
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                "status": "Received",
                                "path": str(file_path)
                            })
                        except Exception as e:
                            logger.warning(f"Error reading file {str(file_path)}: {str(e)}")
                            continue
            # Only show mock data in debug mode
            elif show_mock_data():
                # Create mock data if no received_files directory
                base_time = datetime.now()
                files_data = [
                    {"id": "1", "name": "report_final_v2.docx", "size": 1572864, "type": "docx", "owner": "user1", "modified": (base_time - timedelta(days=1)).isoformat(), "status": "Verified", "path": "mock"},
                    {"id": "2", "name": "project_data.xlsx", "size": 4823449, "type": "xlsx", "owner": "user2", "modified": (base_time - timedelta(hours=5)).isoformat(), "status": "Pending", "path": "mock"},
                    {"id": "3", "name": "logo_draft.png", "size": 891234, "type": "png", "owner": "user1", "modified": (base_time - timedelta(days=3)).isoformat(), "status": "Verified", "path": "mock"},
                    {"id": "4", "name": "main_script.py", "size": 12345, "type": "py", "owner": "user3", "modified": (base_time - timedelta(minutes=30)).isoformat(), "status": "Unverified", "path": "mock"},
                    {"id": "5", "name": "backup_archive.zip", "size": 254857600, "type": "zip", "owner": "user2", "modified": (base_time - timedelta(days=10)).isoformat(), "status": "Verified", "path": "mock"},
                    {"id": "6", "name": "notes.txt", "size": 512, "type": "txt", "owner": "user1", "modified": (base_time - timedelta(hours=1)).isoformat(), "status": "Verified", "path": "mock"}
                ]
        except Exception as e:
            logger.error(f"Failed to scan files: {e}")
            files_data = []
        
        return files_data
    
    # Helper function for size formatting  
    def _format_size(self, size_bytes):
        """Formats size in bytes to a human-readable string."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/1024**2:.1f} MB"
        else:
            return f"{size_bytes/1024**3:.1f} GB"
    
    def _update_table(self):
        """Update the files table with data using ft.Ref."""
        # Create new table rows
        new_rows = []
        for file_data in self.files_data:
            # Status color based on file status
            status_color_name = {
                "Verified": "GREEN",
                "Pending": "ORANGE",
                "Received": "BLUE",
                "Unverified": "RED",
                "Unknown": "ON_SURFACE"
            }.get(file_data.get("status", "Unknown"), "ON_SURFACE")
            
            status_color = getattr(ft.Colors, status_color_name, ft.Colors.ON_SURFACE)
            
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(file_data.get("name", "Unknown")))),
                    ft.DataCell(ft.Text(self._format_size(file_data.get("size", 0)))),
                    ft.DataCell(ft.Text(str(file_data.get("type", "unknown")).upper())),
                    ft.DataCell(ft.Text(
                        datetime.fromisoformat(file_data["modified"]).strftime("%Y-%m-%d %H:%M")
                        if file_data.get("modified") else "Unknown"
                    )),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                str(file_data.get("status", "Unknown")),
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD
                            ),
                            padding=ft.Padding(8, 4, 8, 4),
                            border_radius=12,
                            bgcolor=status_color
                        )
                    ),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                icon_color=ft.Colors.BLUE,
                                tooltip="Download",
                                on_click=self._create_download_handler(file_data)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.VERIFIED,
                                icon_color=ft.Colors.GREEN,
                                tooltip="Verify",
                                on_click=self._create_verify_handler(file_data)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Delete",
                                on_click=self._create_delete_handler(file_data)
                            )
                        ], spacing=0)
                    )
                ]
            )
            new_rows.append(row)
        
        # Update table using ft.Ref
        self.files_table_ref.current.rows = new_rows
        self.files_table_ref.current.update()
    
    def _create_download_handler(self, file_data):
        def handler(e):
            file_name = file_data.get('name', 'Unknown file')
            logger.info(f"Download file: {file_name}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Downloading {file_name}..."),
                bgcolor=ft.Colors.BLUE
            )
            self.page.snack_bar.open = True
            self.page.update()
        return handler
    
    def _create_verify_handler(self, file_data):
        def handler(e):
            file_name = file_data.get('name', 'Unknown file')
            logger.info(f"Verify file: {file_name}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Verified {file_name}"),
                bgcolor=ft.Colors.GREEN
            )
            self.page.snack_bar.open = True
            self.page.update()
        return handler
    
    async def _delete_file_async(self, file_data):
        """Async function to delete a file."""
        try:
            # Simulate async operation
            await asyncio.sleep(ASYNC_DELAY)
            file_name = file_data.get('name', 'Unknown file')
            logger.info(f"Deleted file: {file_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def _create_delete_handler(self, file_data):
        def handler(e):
            file_name = file_data.get('name', 'Unknown file')
            logger.info(f"Delete file: {file_name}")
            # Simple confirmation dialog using Flet's built-in AlertDialog
            dialog = ft.AlertDialog(
                title=ft.Text("Confirm Delete"),
                content=ft.Text(f"Are you sure you want to delete '{file_name}'?"),
                actions=[
                    ft.TextButton("Cancel", on_click=self._close_dialog),
                    ft.TextButton("Delete", on_click=self._confirm_delete(file_data))
                ]
            )
            
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
        return handler
    
    def _confirm_delete(self, file_data):
        def handler(e):
            async def async_delete():
                try:
                    success = await self._delete_file_async(file_data)
                    if success:
                        logger.info(f"Confirmed delete: {file_data.get('name', 'Unknown file')}")
                        # Remove file from data and update table
                        self.files_data = [f for f in self.files_data if f.get('id') != file_data.get('id')]
                        self._update_table()
                        self.status_text_ref.current.value = f"Showing {len(self.files_data)} files"
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Deleted {file_data.get('name', 'Unknown file')}"),
                            bgcolor=ft.Colors.RED
                        )
                    else:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Failed to delete {file_data.get('name', 'Unknown file')}"),
                            bgcolor=ft.Colors.RED
                        )
                    self.page.snack_bar.open = True
                    self._close_dialog(None)
                except Exception as e:
                    logger.error(f"Error in delete handler: {e}")
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Error deleting {file_data.get('name', 'Unknown file')}"),
                        bgcolor=ft.Colors.RED
                    )
                    self.page.snack_bar.open = True
                    self._close_dialog(None)
            
            # Run async operation
            self.page.run_task(async_delete)
        return handler
    
    def _close_dialog(self, e):
        if hasattr(self.page, 'dialog') and self.page.dialog:
            self.page.dialog.open = False
        self.page.update()
    
    def _on_search_change(self, e):
        search_query = e.control.value
        logger.info(f"Search query changed to: '{search_query}'")
        # In a real implementation, this would filter the displayed files
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Searching for: {search_query}"),
            bgcolor=ft.Colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def _on_refresh_click(self, e):
        logger.info("Refresh files list")
        self.page.run_task(self._load_files_data_async)
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Refreshing files list..."),
            bgcolor=ft.Colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def did_mount(self):
        """Called when the control is added to the page."""
        self.page.run_task(self._load_files_data_async)


def create_files_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create files view using ft.UserControl.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The files view
    """
    return FilesView(server_bridge, page)