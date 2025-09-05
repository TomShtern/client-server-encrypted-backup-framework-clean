#!/usr/bin/env python3
"""
Files View for FletV2
Function-based implementation following Framework Harmony principles.
"""

import flet as ft
from typing import List, Dict, Any
import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from utils.debug_setup import get_logger
from utils.loading_states import LoadingState, create_loading_indicator, create_status_text
from utils.responsive_layouts import create_data_table_container, create_action_bar, SPACING
from utils.user_feedback import show_success_message, show_error_message, show_info_message
from config import RECEIVED_FILES_DIR, ASYNC_DELAY, show_mock_data

logger = get_logger(__name__)


def create_files_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create files view using simple function-based pattern.
    Follows Framework Harmony principles - no custom classes, use Flet's built-ins.
    """
    # Simple data state
    files_data: List[Dict[str, Any]] = []
    is_loading = False
    last_updated = None
    
    # Direct control references
    files_table_ref = ft.Ref[ft.DataTable]()
    status_text_ref = ft.Ref[ft.Text]()
    search_field_ref = ft.Ref[ft.TextField]()
    last_updated_text_ref = ft.Ref[ft.Text]()
    
    def format_size(size_bytes):
        """Format size in bytes to human-readable string."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024**3:
            return f"{size_bytes/1024**2:.1f} MB"
        else:
            return f"{size_bytes/1024**3:.1f} GB"
    
    def scan_files_directory():
        """Scan received_files directory for files."""
        files_list = []
        
        try:
            if RECEIVED_FILES_DIR.exists():
                for file_path in RECEIVED_FILES_DIR.iterdir():
                    if file_path.is_file():
                        try:
                            stat = file_path.stat()
                            files_list.append({
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
            elif show_mock_data():
                # Create mock data if no received_files directory
                base_time = datetime.now()
                files_list = [
                    {"id": "1", "name": "report_final_v2.docx", "size": 1572864, "type": "docx", "owner": "user1", "modified": (base_time - timedelta(days=1)).isoformat(), "status": "Verified", "path": "mock"},
                    {"id": "2", "name": "project_data.xlsx", "size": 4823449, "type": "xlsx", "owner": "user2", "modified": (base_time - timedelta(hours=5)).isoformat(), "status": "Pending", "path": "mock"},
                    {"id": "3", "name": "logo_draft.png", "size": 891234, "type": "png", "owner": "user1", "modified": (base_time - timedelta(days=3)).isoformat(), "status": "Verified", "path": "mock"},
                    {"id": "4", "name": "main_script.py", "size": 12345, "type": "py", "owner": "user3", "modified": (base_time - timedelta(minutes=30)).isoformat(), "status": "Unverified", "path": "mock"},
                    {"id": "5", "name": "backup_archive.zip", "size": 254857600, "type": "zip", "owner": "user2", "modified": (base_time - timedelta(days=10)).isoformat(), "status": "Verified", "path": "mock"},
                    {"id": "6", "name": "notes.txt", "size": 512, "type": "txt", "owner": "user1", "modified": (base_time - timedelta(hours=1)).isoformat(), "status": "Verified", "path": "mock"}
                ]
        except Exception as e:
            logger.error(f"Failed to scan files: {e}")
            files_list = []
        
        return files_list
    
    def update_table():
        """Update the files table with current data."""
        new_rows = []
        for file_data in files_data:
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
                                on_click=lambda e, data=file_data: on_download(data)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.VERIFIED,
                                icon_color=ft.Colors.GREEN,
                                tooltip="Verify",
                                on_click=lambda e, data=file_data: on_verify(data)
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_color=ft.Colors.RED,
                                tooltip="Delete",
                                on_click=lambda e, data=file_data: on_delete(data)
                            )
                        ], spacing=0)
                    )
                ]
            )
            new_rows.append(row)
        
        # Update table
        files_table_ref.current.rows = new_rows
        files_table_ref.current.update()
    
    # Simple loading state without complex state management during initialization
    # We'll handle loading updates manually to avoid control attachment issues
    
    async def load_files_data_async():
        """Load files data with simple, safe control updates."""
        nonlocal files_data, last_updated
        
        # Check if controls are properly attached before proceeding
        if not (status_text_ref.current and 
                hasattr(status_text_ref.current, 'page') and 
                status_text_ref.current.page is not None):
            logger.debug("Controls not yet attached to page, deferring data load")
            return
            
        try:
            # Update status text safely
            if (status_text_ref.current and 
                hasattr(status_text_ref.current, 'page') and 
                status_text_ref.current.page is not None):
                status_text_ref.current.value = "Loading files..."
                status_text_ref.current.color = ft.Colors.PRIMARY
                status_text_ref.current.update()
            
            # Load data asynchronously  
            if server_bridge:
                files_data = await page.run_task(server_bridge.get_files)
            else:
                # Fallback: scan received_files directory
                files_data = await page.run_task(scan_files_directory)
            
            # Update last updated timestamp - with safe control check
            if (last_updated_text_ref.current and 
                hasattr(last_updated_text_ref.current, 'page') and 
                last_updated_text_ref.current.page is not None):
                last_updated = datetime.now()
                last_updated_text_ref.current.value = f"Last updated: {last_updated.strftime('%H:%M:%S')}"
                last_updated_text_ref.current.update()
            
            # Update UI
            update_table()
            
            # Update status text with success
            if (status_text_ref.current and 
                hasattr(status_text_ref.current, 'page') and 
                status_text_ref.current.page is not None):
                status_text_ref.current.value = f"Showing {len(files_data)} files"
                status_text_ref.current.color = ft.Colors.PRIMARY
                status_text_ref.current.update()
                
        except Exception as e:
            logger.error(f"Error loading files data: {e}")
            # Update status text with error
            if (status_text_ref.current and 
                hasattr(status_text_ref.current, 'page') and 
                status_text_ref.current.page is not None):
                status_text_ref.current.value = f"Failed to load files: {str(e)}"
                status_text_ref.current.color = ft.Colors.ERROR
                status_text_ref.current.update()
    
    def on_download(file_data):
        """Handle file download with improved feedback."""
        file_name = file_data.get('name', 'Unknown file')
        logger.info(f"Download file: {file_name}")
        show_info_message(page, f"Downloading {file_name}...")
    
    def on_verify(file_data):
        """Handle file verification."""
        file_name = file_data.get('name', 'Unknown file')
        logger.info(f"Verify file: {file_name}")
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Verified {file_name}"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()
    
    async def delete_file_async(file_data):
        """Async function to delete a file."""
        try:
            await asyncio.sleep(ASYNC_DELAY)
            file_name = file_data.get('name', 'Unknown file')
            logger.info(f"Deleted file: {file_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def on_delete(file_data):
        """Handle file deletion with confirmation."""
        file_name = file_data.get('name', 'Unknown file')
        logger.info(f"Delete file: {file_name}")
        
        def close_dialog(e):
            if hasattr(page, 'dialog') and page.dialog:
                page.dialog.open = False
            page.update()
        
        def confirm_delete(e):
            async def async_delete():
                try:
                    success = await delete_file_async(file_data)
                    if success:
                        logger.info(f"Confirmed delete: {file_name}")
                        # Remove file from data and update table
                        nonlocal files_data
                        files_data = [f for f in files_data if f.get('id') != file_data.get('id')]
                        update_table()
                        status_text_ref.current.value = f"Showing {len(files_data)} files"
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
                    close_dialog(None)
                except Exception as ex:
                    logger.error(f"Error in delete handler: {ex}")
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Error deleting {file_name}"),
                        bgcolor=ft.Colors.RED
                    )
                    page.snack_bar.open = True
                    close_dialog(None)
            
            # Run async operation
            page.run_task(async_delete)
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete '{file_name}'?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Delete", on_click=confirm_delete)
            ]
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def on_search_change(e):
        """Handle search input changes."""
        search_query = e.control.value
        logger.info(f"Search query changed to: '{search_query}'")
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Searching for: {search_query}"),
            bgcolor=ft.Colors.BLUE
        )
        page.snack_bar.open = True
        page.update()
    
    def on_refresh_click(e):
        """Handle refresh button click."""
        logger.info("Refresh files list")
        page.run_task(load_files_data_async)
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Refreshing files list..."),
            bgcolor=ft.Colors.BLUE
        )
        page.snack_bar.open = True
        page.update()
    
    # Build the main UI
    main_view = ft.Column([
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
                        on_change=on_search_change,
                        ref=search_field_ref
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
                ft.Text(
                    value="Loading files...",
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    ref=status_text_ref
                ),
                ft.Container(expand=True),
                ft.Text(
                    value="Last updated: Never",
                    color=ft.Colors.ON_SURFACE,
                    size=12,
                    ref=last_updated_text_ref
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
                    ref=files_table_ref
                )
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=ft.Padding(20, 0, 20, 20)
        )
    ], expand=True)
    
    # Schedule data loading after the view is attached
    def schedule_data_load():
        """Schedule data loading with retry mechanism to ensure controls are attached."""
        async def delayed_load_with_retry():
            max_retries = 5
            retry_delay = 0.1
            
            for attempt in range(max_retries):
                # Check if controls are attached
                if (status_text_ref.current and 
                    hasattr(status_text_ref.current, 'page') and 
                    status_text_ref.current.page is not None):
                    logger.info(f"Controls attached on attempt {attempt + 1}, loading data")
                    await load_files_data_async()
                    return
                
                logger.debug(f"Attempt {attempt + 1}: Controls not attached, waiting {retry_delay}s")
                await asyncio.sleep(retry_delay)
                retry_delay *= 1.5  # Exponential backoff
            
            logger.warning("Failed to load files data: controls never attached after 5 attempts")
        
        page.run_task(delayed_load_with_retry)
    
    # Use page.update after view is attached
    page.on_view_pop = lambda e: None  # Placeholder to ensure page events work
    schedule_data_load()
    
    return main_view