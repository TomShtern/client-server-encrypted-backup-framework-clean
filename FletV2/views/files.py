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


def create_files_view(server_bridge, page: ft.Page, state_manager=None) -> ft.Control:
    """
    Create files view using simple function-based pattern.
    Follows Framework Harmony principles - no custom classes, use Flet's built-ins.
    """
    # Simple data state
    files_data: List[Dict[str, Any]] = []
    is_loading = False
    last_updated = None
    search_query = ""
    status_filter = "all"
    type_filter = "all"
    size_filter = "all"
    case_sensitive_search = False  # New state for case sensitivity

    # Direct control references
    files_table_ref = ft.Ref[ft.DataTable]()
    
    # Pre-create the DataTable to avoid lifecycle issues
    files_table = ft.DataTable(
        ref=files_table_ref,
        columns=[
            ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Modified", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Owner", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
        ],
        rows=[],  # Will be populated by update_table()
        heading_row_color=ft.Colors.SURFACE,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8,
        data_row_min_height=45,
        column_spacing=20
    )
    status_text_ref = ft.Ref[ft.Text]()
    search_field_ref = ft.Ref[ft.TextField]()
    last_updated_text_ref = ft.Ref[ft.Text]()

    def filter_files():
        """Filter files based on search query and filters."""
        filtered = files_data

        # Apply search filter
        if search_query.strip():
            query = search_query.strip()
            if not case_sensitive_search:
                query = query.lower()
            filtered = [f for f in filtered if
                       query in (str(f.get("name", "")) if case_sensitive_search else str(f.get("name", "")).lower()) or
                       query in (str(f.get("owner", "")) if case_sensitive_search else str(f.get("owner", "")).lower())]

        # Apply status filter
        if status_filter != "all":
            filtered = [f for f in filtered if str(f.get("status", "")).lower() == status_filter.lower()]

        # Apply type filter
        if type_filter != "all":
            filtered = [f for f in filtered if str(f.get("type", "")).lower() == type_filter.lower()]

        # Apply size filter
        if size_filter != "all":
            def is_matching_size(file_data):
                size = file_data.get("size", 0)
                if size_filter == "small":
                    return size < 1024 * 1024  # Less than 1 MB
                elif size_filter == "medium":
                    return 1024 * 1024 <= size < 100 * 1024 * 1024  # 1 MB to 100 MB
                elif size_filter == "large":
                    return size >= 100 * 1024 * 1024  # 100 MB or more
                return True

            filtered = [f for f in filtered if is_matching_size(f)]

        return filtered

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

                            # Get file owner (platform-specific)
                            try:
                                import pwd
                                owner = pwd.getpwuid(stat.st_uid).pw_name if hasattr(stat, 'st_uid') else "system"
                            except (ImportError, KeyError):
                                owner = "system"

                            # Determine file status based on modification time
                            mod_time = datetime.fromtimestamp(stat.st_mtime)
                            now = datetime.now()
                            age = now - mod_time

                            # Set status based on file age and size
                            if age.days > 30:
                                status = "Archived"
                            elif stat.st_size == 0:
                                status = "Empty"
                            elif age.days > 7:
                                status = "Stored"
                            else:
                                status = "Received"

                            files_list.append({
                                "id": str(hash(file_path.name)) % 10000,
                                "name": file_path.name,
                                "size": stat.st_size,
                                "type": file_path.suffix.lstrip('.') or 'unknown',
                                "owner": owner,
                                "modified": mod_time.isoformat(),
                                "status": status,
                                "path": str(file_path),
                                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                                "permissions": oct(stat.st_mode)[-3:] if hasattr(stat, 'st_mode') else "unknown"
                            })
                        except Exception as e:
                            logger.warning(f"Error reading file {str(file_path)}: {str(e)}")
                            continue
            elif show_mock_data():
                # Create mock data if no received_files directory
                base_time = datetime.now()
                files_list = [
                    {"id": "1", "name": "report_final_v2.docx", "size": 1572864, "type": "docx", "owner": "user1", "modified": (base_time - timedelta(days=1)).isoformat(), "status": "Verified", "path": "mock", "created": (base_time - timedelta(days=2)).isoformat(), "permissions": "644"},
                    {"id": "2", "name": "project_data.xlsx", "size": 4823449, "type": "xlsx", "owner": "user2", "modified": (base_time - timedelta(hours=5)).isoformat(), "status": "Pending", "path": "mock", "created": (base_time - timedelta(hours=6)).isoformat(), "permissions": "644"},
                    {"id": "3", "name": "logo_draft.png", "size": 891234, "type": "png", "owner": "user1", "modified": (base_time - timedelta(days=3)).isoformat(), "status": "Verified", "path": "mock", "created": (base_time - timedelta(days=5)).isoformat(), "permissions": "644"},
                    {"id": "4", "name": "main_script.py", "size": 12345, "type": "py", "owner": "user3", "modified": (base_time - timedelta(minutes=30)).isoformat(), "status": "Unverified", "path": "mock", "created": (base_time - timedelta(minutes=45)).isoformat(), "permissions": "755"},
                    {"id": "5", "name": "backup_archive.zip", "size": 254857600, "type": "zip", "owner": "user2", "modified": (base_time - timedelta(days=10)).isoformat(), "status": "Verified", "path": "mock", "created": (base_time - timedelta(days=15)).isoformat(), "permissions": "600"},
                    {"id": "6", "name": "notes.txt", "size": 512, "type": "txt", "owner": "user1", "modified": (base_time - timedelta(hours=1)).isoformat(), "status": "Verified", "path": "mock", "created": (base_time - timedelta(hours=2)).isoformat(), "permissions": "644"}
                ]
        except Exception as e:
            logger.error(f"Failed to scan files: {e}")
            files_list = []

        return files_list

    async def get_files_data():
        """Get files data from enhanced server bridge with smart caching."""
        try:
            # Check state manager cache first if available
            if state_manager:
                cached_files = state_manager.get_cached("files", max_age_seconds=30)
                if cached_files:
                    logger.debug("Using cached files data")
                    return cached_files
            
            # Try to get files from enhanced server bridge first
            if server_bridge:
                try:
                    files_data = await server_bridge.get_files()
                    if files_data:
                        # Update state manager cache if available
                        if state_manager:
                            await state_manager.update_state("files", files_data)
                        return files_data
                except Exception as e:
                    logger.warning(f"Failed to get files from server bridge: {e}")

            # Fallback to scanning local directory
            files_data = scan_files_directory()
            # Update cache with fallback data if available
            if state_manager and files_data:
                await state_manager.update_state("files", files_data)
            return files_data
        except Exception as e:
            logger.error(f"Error getting files data: {e}")
            return []

    def update_table():
        """Update the files table with current data."""
        filtered_files = filter_files()
        new_rows = []
        for file_data in filtered_files:
            # Status color based on file status
            status_color_name = {
                "Verified": "GREEN",
                "Pending": "ORANGE",
                "Received": "BLUE",
                "Unverified": "RED",
                "Stored": "PURPLE",
                "Archived": "BROWN",
                "Empty": "GREY",
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
                    ft.DataCell(ft.Text(str(file_data.get("owner", "Unknown")))),
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

        # Always update the pre-created table object first
        files_table.rows = new_rows
        
        # Update table ref if it exists and is properly attached
        if (files_table_ref.current and 
            hasattr(files_table_ref.current, 'page') and 
            files_table_ref.current.page is not None):
            files_table_ref.current.rows = new_rows
            try:
                files_table_ref.current.update()
            except Exception as update_error:
                logger.debug(f"Files DataTable update failed, will retry on next update: {update_error}")
        else:
            logger.debug("Files DataTable ref not ready yet, table will be updated when displayed")
            
        # Always update the display
        update_table_display()

        # Update status text with search result count
        if (status_text_ref.current and
            hasattr(status_text_ref.current, 'page') and
            status_text_ref.current.page is not None):
            total = len(files_data)
            filtered_count = len(filtered_files)
            search_active = bool(search_query.strip())

            if search_active:
                status_text_ref.current.value = f"Search results: {filtered_count} of {total} files"
            else:
                status_text_ref.current.value = f"Showing {filtered_count} of {total} files"
            status_text_ref.current.color = ft.Colors.PRIMARY
            status_text_ref.current.update()

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

            # Load data - start with scan_files_directory (sync) for immediate data
            # The async loading will happen separately via page.run_task
            initial_files_data = scan_files_directory()
            files_data.clear()
            files_data.extend(initial_files_data)
            
            # Now schedule async loading via page.run_task for enhanced data
            async def load_enhanced_data():
                try:
                    enhanced_data = await get_files_data()
                    files_data.clear()
                    files_data.extend(enhanced_data)
                    # Update UI after loading
                    update_table()
                    if status_text_ref.current:
                        status_text_ref.current.value = f"Showing {len(files_data)} files"
                        status_text_ref.current.update()
                except Exception as e:
                    logger.error(f"Failed to load enhanced files data: {e}")
            
            # Schedule the async task
            page.run_task(load_enhanced_data)

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
        """Handle file download with real file operations."""
        logger.info(f"BUTTON CLICK: Download button clicked for file data: {file_data}")
        file_name = file_data.get('name', 'Unknown file')
        file_path = file_data.get('path', '')

        logger.info(f"Download file: {file_name}")

        # Check if this is a real file path or mock data
        if file_path and file_path != "mock":
            try:
                # Check if file exists
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    # Create a downloads directory if it doesn't exist
                    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                    if not os.path.exists(downloads_dir):
                        os.makedirs(downloads_dir)

                    # Create destination path
                    dest_path = os.path.join(downloads_dir, file_name)

                    # Copy file to downloads directory
                    import shutil
                    shutil.copy2(file_path, dest_path)

                    show_success_message(page, f"File downloaded to {dest_path}")
                    logger.info(f"File downloaded successfully: {dest_path}")
                else:
                    show_error_message(page, f"File not found: {file_name}")
                    logger.error(f"File not found for download: {file_path}")
            except Exception as e:
                logger.error(f"Failed to download file {file_name}: {e}")
                show_error_message(page, f"Failed to download file: {str(e)}")
        else:
            # For mock data, just show a message
            show_info_message(page, f"Downloading {file_name}... (mock data)")

    def on_verify(file_data):
        """Handle file verification with real file operations."""
        logger.info(f"BUTTON CLICK: Verify button clicked for file data: {file_data}")
        file_name = file_data.get('name', 'Unknown file')
        file_path = file_data.get('path', '')

        logger.info(f"Verify file: {file_name}")

        # Check if this is a real file path or mock data
        if file_path and file_path != "mock":
            try:
                # Check if file exists
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    # Get file stats
                    stat = os.stat(file_path)
                    file_size = stat.st_size
                    modified_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                    # Calculate file hash for verification (simple checksum)
                    import hashlib
                    hash_md5 = hashlib.md5()
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_md5.update(chunk)
                    file_hash = hash_md5.hexdigest()

                    # Show verification results
                    show_success_message(page, f"Verified {file_name}: {format_size(file_size)}, Modified: {modified_time}, Hash: {file_hash[:8]}...")
                    logger.info(f"File verified successfully: {file_name}")
                else:
                    show_error_message(page, f"File not found: {file_name}")
                    logger.error(f"File not found for verification: {file_path}")
            except Exception as e:
                logger.error(f"Failed to verify file {file_name}: {e}")
                show_error_message(page, f"Failed to verify file: {str(e)}")
        else:
            # For mock data, just show a message
            show_success_message(page, f"Verified {file_name}")

    async def delete_file_async(file_data):
        """Async function to delete a file."""
        try:
            file_name = file_data.get('name', 'Unknown file')
            file_path = file_data.get('path', '')

            # Check if this is a real file path or mock data
            if file_path and file_path != "mock":
                # Check if file exists and delete it
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.info(f"Deleted file: {file_name}")
                    return True
                else:
                    logger.error(f"File not found for deletion: {file_path}")
                    return False
            else:
                # For mock data, simulate deletion
                await asyncio.sleep(ASYNC_DELAY)
                logger.info(f"Deleted file: {file_name}")
                return True
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def on_delete(file_data):
        """Handle file deletion with confirmation."""
        logger.info(f"BUTTON CLICK: Delete button clicked for file data: {file_data}")
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
                        if status_text_ref.current:
                            status_text_ref.current.value = f"Showing {len(files_data)} files"
                            status_text_ref.current.update()
                        show_success_message(page, f"Deleted {file_name}")
                    else:
                        show_error_message(page, f"Failed to delete {file_name}")
                    close_dialog(None)
                except Exception as ex:
                    logger.error(f"Error in delete handler: {ex}")
                    show_error_message(page, f"Error deleting {file_name}")
                    close_dialog(None)

            # Run async operation
            page.run_task(async_delete)

        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text(f"Are you sure you want to delete '{file_name}'?"),
            actions=[
                ft.TextButton("Cancel", icon=ft.Icons.CANCEL, on_click=close_dialog, tooltip="Cancel deletion"),
                ft.TextButton("Delete", icon=ft.Icons.DELETE, on_click=confirm_delete, tooltip="Confirm file deletion")
            ]
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def on_search_change(e):
        """Handle search input changes."""
        nonlocal search_query
        search_query = e.control.value
        logger.info(f"Search query changed to: '{search_query}'")
        update_table()

    def on_clear_search():
        """Clear the search field."""
        nonlocal search_query
        search_query = ""
        if search_field_ref.current:
            search_field_ref.current.value = ""
        logger.info("Search cleared")
        update_table()

    def on_case_sensitive_toggle(e):
        """Handle case sensitivity toggle."""
        nonlocal case_sensitive_search
        case_sensitive_search = e.control.value
        logger.info(f"Case sensitive search: {case_sensitive_search}")
        update_table()

    def on_reset_filters(e):
        """Reset all search and filter fields."""
        nonlocal search_query, status_filter, type_filter, size_filter
        search_query = ""
        status_filter = "all"
        type_filter = "all"
        size_filter = "all"
        if search_field_ref.current:
            search_field_ref.current.value = ""
        logger.info("Filters reset")
        update_table()

    def on_status_filter_change(e):
        """Handle status filter changes."""
        nonlocal status_filter
        status_filter = e.control.value
        logger.info(f"Status filter changed to: '{status_filter}'")
        update_table()

    def on_type_filter_change(e):
        """Handle type filter changes."""
        nonlocal type_filter
        type_filter = e.control.value
        logger.info(f"Type filter changed to: '{type_filter}'")
        update_table()

    def on_size_filter_change(e):
        """Handle size filter changes."""
        nonlocal size_filter
        size_filter = e.control.value
        logger.info(f"Size filter changed to: '{size_filter}'")
        update_table()

    def on_refresh_click(e):
        """Handle refresh button click."""
        logger.info("Refresh files list")
        page.run_task(load_files_data_async)
        show_info_message(page, "Refreshing files list...")

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
                        hint_text="Search by filename, owner, or type...",
                        prefix_icon=ft.Icons.SEARCH,
                        suffix=ft.IconButton(
                            icon=ft.Icons.CLEAR,
                            tooltip="Clear search",
                            icon_size=16,
                            on_click=lambda e: on_clear_search()
                        ),
                        width=300,
                        on_change=on_search_change,
                        ref=search_field_ref
                    ),
                    ft.Container(
                        content=ft.Switch(
                            label="Case sensitive",
                            value=False,
                            on_change=on_case_sensitive_toggle
                        ),
                        padding=ft.Padding(10, 0, 10, 0)
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLEAR,
                        tooltip="Reset all filters",
                        on_click=on_reset_filters
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

        # Filter controls
        ft.Container(
            content=ft.Row([
                ft.Dropdown(
                    label="Filter by Status",
                    value="all",
                    options=[
                        ft.dropdown.Option("all", "All Statuses"),
                        ft.dropdown.Option("Received", "Received"),
                        ft.dropdown.Option("Verified", "Verified"),
                        ft.dropdown.Option("Pending", "Pending"),
                        ft.dropdown.Option("Unverified", "Unverified"),
                        ft.dropdown.Option("Stored", "Stored"),
                        ft.dropdown.Option("Archived", "Archived"),
                        ft.dropdown.Option("Empty", "Empty")
                    ],
                    width=150,
                    on_change=on_status_filter_change
                ),
                ft.Dropdown(
                    label="Filter by Type",
                    value="all",
                    options=[
                        ft.dropdown.Option("all", "All Types"),
                        ft.dropdown.Option("docx", "Word Document"),
                        ft.dropdown.Option("xlsx", "Excel Spreadsheet"),
                        ft.dropdown.Option("pdf", "PDF Document"),
                        ft.dropdown.Option("jpg", "JPEG Image"),
                        ft.dropdown.Option("png", "PNG Image"),
                        ft.dropdown.Option("txt", "Text File"),
                        ft.dropdown.Option("py", "Python Script"),
                        ft.dropdown.Option("zip", "ZIP Archive")
                    ],
                    width=150,
                    on_change=on_type_filter_change
                ),
                ft.Dropdown(
                    label="Filter by Size",
                    value="all",
                    options=[
                        ft.dropdown.Option("all", "All Sizes"),
                        ft.dropdown.Option("small", "Small (< 1 MB)"),
                        ft.dropdown.Option("medium", "Medium (1 MB - 100 MB)"),
                        ft.dropdown.Option("large", "Large (> 100 MB)")
                    ],
                    width=200,
                    on_change=on_size_filter_change
                )
            ], spacing=20, wrap=True),
            padding=ft.Padding(20, 0, 20, 10)
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
        )
    ])

    # Files table container with empty state
    table_container = ft.Container(
        expand=True,
        padding=ft.Padding(20, 0, 20, 20)
    )

    def update_table_display():
        """Update table display with empty state handling."""
        filtered_files = filter_files()
        if not filtered_files:
            # Show empty state
            table_container.content = ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.FOLDER_OPEN,
                            size=64,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        ),
                        ft.Text(
                            "No files found",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE
                        ),
                        ft.Text(
                            "No files have been uploaded or stored yet.",
                            size=14,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        )
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=16
                    ),
                    height=300,
                    alignment=ft.alignment.center
                )
            ], scroll=ft.ScrollMode.AUTO)
        else:
            # Show table - use the pre-created table
            table_container.content = ft.Column([
                files_table
            ], scroll=ft.ScrollMode.AUTO)
        
        # Defensive update - only update if table_container is attached
        try:
            if (hasattr(table_container, 'page') and table_container.page is not None):
                table_container.update()
        except Exception as e:
            logger.debug(f"Table container update failed, will retry: {e}")

    # Add the table container to the main view
    main_view.controls.append(table_container)

    # Initial display update
    update_table_display()
    # Update table with actual data
    update_table()

    # Also provide a trigger for manual loading if needed
    def trigger_initial_load():
        """Trigger initial data load manually."""
        page.run_task(schedule_data_load)

    # Export the trigger function so it can be called externally
    main_view.trigger_initial_load = trigger_initial_load

    # Schedule data loading after the view is attached
    async def schedule_data_load():
        """Schedule data loading with retry mechanism to ensure controls are attached."""
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

    # Use page.update after view is attached
    page.on_view_pop = lambda e: None  # Placeholder to ensure page events work
    
    # Schedule initial data load
    def initial_schedule():
        schedule_data_load()
    
    # Set up the initial load to happen after the view is attached
    page.on_connect = lambda e: initial_schedule()

    # Also trigger initial load when view is added to page
    page.run_task(schedule_data_load)

    return main_view
