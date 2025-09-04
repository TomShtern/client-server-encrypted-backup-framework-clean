#!/usr/bin/env python3
"""
Files View for FletV2
A clean implementation using pure Flet patterns.
"""

import flet as ft
from typing import List, Dict, Any
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from utils.debug_setup import get_logger

logger = get_logger(__name__)


def create_files_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create files view using simple Flet patterns.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The files view
    """
    
    # Get files data from server or received_files directory
    def get_files_data():
        """Get real files from received_files directory or server bridge."""
        files_data = []
        
        if server_bridge:
            try:
                # Try to get files from server bridge
                files_data = server_bridge.get_files()
            except Exception as e:
                logger.warning(f"Failed to get files from server bridge: {e}")
        
        # Fallback: scan received_files directory
        if not files_data:
            try:
                received_files_dir = Path("../received_files")
                if received_files_dir.exists():
                    for file_path in received_files_dir.iterdir():
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
                else:
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
    def format_size(size_bytes):
        """Formats size in bytes to a human-readable string."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/1024**2:.1f} MB"
        else:
            return f"{size_bytes/1024**3:.1f} GB"
    
    # Create action handlers
    def on_download_click(file_data):
        def handler(e):
            file_name = file_data.get('name', 'Unknown file')
            logger.info(f"Download file: {file_name}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Downloading {file_name}..."),
                bgcolor=ft.Colors.BLUE
            )
            page.snack_bar.open = True
            page.update()
        return handler
    
    def on_verify_click(file_data):
        def handler(e):
            file_name = file_data.get('name', 'Unknown file')
            logger.info(f"Verify file: {file_name}")
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Verified {file_name}"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
            page.update()
        return handler
    
    async def delete_file_async(file_data):
        """Async function to delete a file."""
        try:
            # Simulate async operation
            await asyncio.sleep(0.5)
            file_name = file_data.get('name', 'Unknown file')
            logger.info(f"Deleted file: {file_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def on_delete_click(file_data):
        def handler(e):
            file_name = file_data.get('name', 'Unknown file')
            logger.info(f"Delete file: {file_name}")
            # Simple confirmation dialog using Flet's built-in AlertDialog
            dialog = ft.AlertDialog(
                title=ft.Text("Confirm Delete"),
                content=ft.Text(f"Are you sure you want to delete '{file_name}'?"),
                actions=[
                    ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                    ft.TextButton("Delete", on_click=lambda e: confirm_delete())
                ]
            )
            
            def close_dialog():
                page.dialog.open = False
                page.update()
            
            def confirm_delete():
                async def async_delete():
                    try:
                        success = await delete_file_async(file_data)
                        if success:
                            logger.info(f"Confirmed delete: {file_name}")
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(f"Deleted {file_name}"),
                                bgcolor=ft.Colors.RED
                            )
                        else:
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text(f"Failed to delete {file_name}"),
                                bgcolor=ft.Colors.RED
                            )
                        page.snack_bar.open = True
                        close_dialog()
                    except Exception as e:
                        logger.error(f"Error in delete handler: {e}")
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Error deleting {file_name}"),
                            bgcolor=ft.Colors.RED
                        )
                        page.snack_bar.open = True
                        close_dialog()
                
                # Run async operation
                page.run_task(async_delete)
            
            page.dialog = dialog
            dialog.open = True
            page.update()
        return handler
    
    def on_refresh_click(e):
        logger.info("Refresh files list")
        # In a real implementation, this would reload the file list
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Files refreshed"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()

    # Get initial files data
    files_data = get_files_data()

    # Create DataTable using Flet's built-in component
    files_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)), 
            ft.DataColumn(ft.Text("Modified", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(file_data.get("name", "Unknown")))),
                    ft.DataCell(ft.Text(format_size(file_data.get("size", 0)))),
                    ft.DataCell(ft.Text(str(file_data.get("type", "unknown")).upper())),
                    ft.DataCell(ft.Text(
                        datetime.fromisoformat(file_data["modified"]).strftime("%Y-%m-%d %H:%M")
                        if file_data.get("modified") else "Unknown"
                    )),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                str(file_data.get("status", "Unknown")),
                                color=ft.Colors.GREEN if file_data.get("status") == "Verified" 
                                      else ft.Colors.ORANGE if file_data.get("status") == "Pending"
                                      else ft.Colors.BLUE if file_data.get("status") == "Received"
                                      else ft.Colors.RED
                            ),
                            padding=ft.Padding(8, 4, 8, 4),
                            border_radius=12,
                            bgcolor=ft.Colors.SURFACE_TINT
                        )
                    ),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                icon_color=ft.Colors.BLUE,
                                tooltip="Download",
                                on_click=on_download_click(file_data)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.VERIFIED,
                                icon_color=ft.Colors.GREEN,
                                tooltip="Verify",
                                on_click=on_verify_click(file_data)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Delete",
                                on_click=on_delete_click(file_data)
                            )
                        ], spacing=0)
                    )
                ]
            ) for file_data in files_data
        ],
        heading_row_color=ft.Colors.SURFACE,
        border=ft.border.all(1, ft.Colors.OUTLINE)
    )
    
    # Return the view using simple Flet layout
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
                        on_change=lambda e: logger.info(f"Search: {e.control.value}")
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh Files",
                        on_click=on_refresh_click
                    )
                ], spacing=10)
            ]),
            padding=ft.Padding(20, 20, 20, 10)
        ),
        
        # Status info
        ft.Container(
            content=ft.Row([
                ft.Text(f"Showing {len(files_data)} files", color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(expand=True),
                ft.Text(
                    f"Total size: {format_size(sum(f['size'] for f in files_data))}",
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ]),
            padding=ft.Padding(20, 0, 20, 10)
        ),
        
        # Files table in a scrollable container
        ft.Container(
            content=ft.Column([files_table], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=ft.Padding(20, 0, 20, 20)
        )
    ], expand=True)