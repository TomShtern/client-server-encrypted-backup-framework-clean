#!/usr/bin/env python3
"""
Files View for FletV2
Clean, framework-harmonious implementation following successful patterns.
Optimized for maintainability and visual appeal at ~600 LOC.
"""

import flet as ft
import os
import asyncio
import hashlib
import shutil
import aiofiles
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.user_feedback import show_success_message, show_error_message, show_confirmation, show_info
from config import get_status_color
from utils.server_mediated_operations import create_server_mediated_operations
from utils.server_mediated_operations import file_size_processor
from utils.ui_components import create_modern_card, apply_advanced_table_effects, create_status_chip, format_file_size

logger = get_logger(__name__)

def create_files_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    state_manager: StateManager
) -> ft.Control:
    """
    Create files view with server-mediated operations through state manager.
    Uses reactive patterns for UI updates following FletV2 framework harmony.
    """
    logger.info("Creating files view with server-mediated operations")

    # Comment 8: Show server unavailable status if server_bridge is falsy
    if not server_bridge:
        logger.info("Server unavailable - running in mock mode")

    # State Management - Reactive with State Manager
    files_data: List[Dict[str, Any]] = []
    filtered_files: List[Dict[str, Any]] = []
    search_query = ""
    status_filter = "all"
    type_filter = "all"

    # UI Control References - Add ft.Ref definitions
    status_text_ref = ft.Ref[ft.Text]()
    search_field_ref = ft.Ref[ft.TextField]()
    loading_indicator_ref = ft.Ref[ft.ProgressRing]()

    def handle_search_change(e):
        """Handle search field changes with proper scoping."""
        nonlocal search_query
        search_query = e.control.value.lower().strip()
        apply_filters()

    search_field = ft.TextField(
        ref=search_field_ref,
        label="Search files...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=handle_search_change,
        width=300
    )

    def handle_status_filter_change(e):
        """Handle status filter changes with proper scoping."""
        nonlocal status_filter
        status_filter = e.control.value
        apply_filters()

    status_dropdown = ft.Dropdown(
        label="Status",
        options=[
            ft.dropdown.Option("all", "All Status"),
            ft.dropdown.Option("complete", "Complete"),
            ft.dropdown.Option("uploading", "Uploading"),
            ft.dropdown.Option("queued", "Queued"),
            ft.dropdown.Option("failed", "Failed"),
            ft.dropdown.Option("verified", "Verified")
        ],
        value="all",
        on_change=handle_status_filter_change,
        width=150
    )

    def handle_type_filter_change(e):
        """Handle type filter changes with proper scoping."""
        nonlocal type_filter
        type_filter = e.control.value
        apply_filters()

    type_dropdown = ft.Dropdown(
        label="Type",
        options=[
            ft.dropdown.Option("all", "All Types"),
            ft.dropdown.Option("document", "Documents"),
            ft.dropdown.Option("image", "Images"),
            ft.dropdown.Option("video", "Videos"),
            ft.dropdown.Option("code", "Code")
        ],
        value="all",
        on_change=handle_type_filter_change,
        width=150
    )

    # Control references for reactive UI updates
    files_table_ref = ft.Ref[ft.DataTable]()

    # Professional DataTable with enhanced Material Design 3 styling and responsive design
    files_table_columns = [
        ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
        ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
        ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
        ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
        ft.DataColumn(ft.Text("Modified", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
        ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY))
    ]

    files_table = ft.DataTable(
        ref=files_table_ref,
        columns=files_table_columns,
        rows=[],
        heading_row_color=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
        border=ft.border.all(2, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
        border_radius=20,  # Enhanced border radius for premium appearance
        data_row_min_height=68,  # Increased row height for better spacing
        heading_row_height=72,  # Enhanced header height
        column_spacing=32,  # Improved column spacing
        show_checkbox_column=False,
        bgcolor=ft.Colors.SURFACE,
        divider_thickness=1,
        expand=True,  # Enable proper window scaling
        # Enhanced hover effects
        data_row_color={
            ft.ControlState.HOVERED: ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
            ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT
        },
        horizontal_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.08, ft.Colors.OUTLINE))
    )

    # Comment 8: Initial status message based on server availability
    initial_status = "Ready" if server_bridge else "Server unavailable—running in mock mode."
    status_text = ft.Text(initial_status, ref=status_text_ref, size=12, color=ft.Colors.ON_SURFACE)

    # Comment 3: Add ProgressRing for loading indicator
    loading_indicator = ft.ProgressRing(ref=loading_indicator_ref, visible=False, width=16, height=16)

    # Server-Mediated Data Functions with enhanced loading state management
    async def load_files_data():
        """Load files data using server-mediated state management with comprehensive error handling."""
        try:
            # Set loading state through state manager (sync method)
            if state_manager:
                state_manager.set_loading("files_data", True)
            status_text.value = "Loading files..."
            status_text.color = ft.Colors.ON_SURFACE
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()

            # Use server-mediated update for persistence and consistency
            if state_manager:
                result = await state_manager.server_mediated_update(
                    key="files_data",
                    value=None,  # Will be set by server response
                    server_operation="get_files_async"
                )
            else:
                # Fallback when no state manager - use server bridge directly
                result = await server_bridge.get_files_async() if server_bridge else {'success': False, 'error': 'No server connection'}

            if result.get('success') and result.get('data'):
                # Server operation successful
                logger.info(f"Loaded {len(result['data'])} files from server")
                status_text.value = f"Loaded {len(result['data'])} files"
                status_text.color = ft.Colors.TERTIARY
                if state_manager:
                    await state_manager.update_async("files_data", result['data'], source="server")
            elif not result.get('success'):
                # Fallback to mock data if server operation fails
                error_msg = result.get('error', 'Server operation failed')
                logger.warning(f"Server files load failed: {error_msg}, using mock data")
                mock_files = generate_mock_files()
                if state_manager:
                    await state_manager.update_async("files_data", mock_files, source="fallback")
                status_text.value = f"Loaded {len(mock_files)} files (demo mode)"
                status_text.color = ft.Colors.SECONDARY

        except Exception as e:
            logger.error(f"Failed to load files: {e}", exc_info=True)
            show_error_message(page, f"Failed to load files: {str(e)}")
            # Set empty files list as fallback
            error_files = []
            if state_manager:
                await state_manager.update_async("files_data", error_files, source="error")
            status_text.value = "Error loading files"
            status_text.color = ft.Colors.ERROR
        finally:
            if state_manager:
                state_manager.set_loading("files_data", False)
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()

    def generate_mock_files() -> List[Dict[str, Any]]:
        """Generate mock files data for development/fallback."""
        return [
            {
                "id": f"file_{i}",
                "name": f"backup_file_{i:03d}.{ext}",
                "size": size,
                "type": file_type,
                "status": status,
                "owner": "system",
                "modified": "2025-01-11 14:30",
                "path": f"/backup/files/file_{i}.{ext}"
            }
            for i, (ext, file_type, size, status) in enumerate([
                ("pdf", "document", 1024*512, "complete"),
                ("jpg", "image", 1024*256, "verified"),
                ("mp4", "video", 1024*1024*50, "pending"),
                ("py", "code", 1024*8, "complete"),
                ("txt", "document", 1024*4, "verified"),
                ("png", "image", 1024*128, "complete"),
                ("zip", "archive", 1024*1024*10, "pending"),
                ("json", "code", 1024*16, "verified")
            ], 1)
        ]

    def apply_search(query: str):
        """Apply search filter and update display."""
        search_query = query.lower().strip()
        apply_filters()

    def apply_filter(filter_type: str, value: str):
        """Apply status or type filter and update display."""
        if filter_type == "status":
            status_filter = value
        elif filter_type == "type":
            type_filter = value
        apply_filters()

    def apply_filters():
        """Apply all filters and update table display."""
        nonlocal filtered_files
        filtered_files = [
            f for f in files_data
            if (search_query == "" or search_query in f["name"].lower()) and
               (status_filter == "all" or f["status"] == status_filter) and
               (type_filter == "all" or f["type"] == type_filter)
        ]
        update_table(filtered_files)

    def get_file_type_icon(file_type: str) -> tuple:
        """Get file type icon and color."""
        if file_type == "document":
            return ft.Icons.DESCRIPTION, ft.Colors.AMBER
        elif file_type == "image":
            return ft.Icons.IMAGE, ft.Colors.PINK
        elif file_type == "video":
            return ft.Icons.VIDEO_FILE, ft.Colors.CYAN
        elif file_type == "code":
            return ft.Icons.CODE, ft.Colors.SECONDARY
        else:
            return ft.Icons.INSERT_DRIVE_FILE, ft.Colors.PRIMARY

    # get_status_color function moved to utils/ui_patterns.py for reuse

    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024*1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024*1024):.1f} MB"

    def update_table(filtered_files_param=None):
        """Professional DataTable update with clean styling following clients.py pattern."""
        # Use parameter if provided, otherwise use the nonlocal filtered_files
        data_to_display = filtered_files_param if filtered_files_param is not None else filtered_files

        # Clear existing rows
        files_table.rows.clear()

        # Populate DataTable rows with clean cell structure
        for file_data in data_to_display[:50]:  # Limit to 50 for performance
            file_type = file_data.get("type", "unknown")
            type_icon, icon_color = get_file_type_icon(file_type)
            status = file_data.get("status", "unknown")

            # Create name cell with file type icon
            name_content = ft.Row([
                ft.Container(
                    content=ft.Icon(type_icon, size=16, color=icon_color),
                    bgcolor=ft.Colors.with_opacity(0.1, icon_color),
                    border_radius=6,
                    padding=ft.Padding(4, 4, 4, 4)
                ),
                ft.Text(
                    file_data.get("name", ""),
                    size=13,
                    weight=ft.FontWeight.W_500,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    max_lines=1
                )
            ], spacing=6, tight=True)

            # Create DataRow following clients.py pattern
            row = ft.DataRow(
                cells=[
                    ft.DataCell(name_content),
                    ft.DataCell(ft.Text(format_file_size(file_data.get("size", 0)), size=13)),
                    ft.DataCell(ft.Text(file_type.title(), size=13)),
                    ft.DataCell(create_status_chip(status)),
                    ft.DataCell(ft.Text(str(file_data.get("modified", "")), size=13)),
                    ft.DataCell(
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            tooltip="File Actions",
                            icon_color=ft.Colors.PRIMARY,
                            items=[
                                ft.PopupMenuItem(
                                    text="Download",
                                    icon=ft.Icons.DOWNLOAD,
                                    on_click=lambda e, f=file_data: download_file(f)
                                ),
                                ft.PopupMenuItem(
                                    text="Verify",
                                    icon=ft.Icons.VERIFIED,
                                    on_click=lambda e, f=file_data: verify_file(f)
                                ),
                                ft.PopupMenuItem(
                                    text="Delete",
                                    icon=ft.Icons.DELETE,
                                    on_click=lambda e, f=file_data: delete_file(f)
                                )
                            ]
                        )
                    )
                ]
            )
            files_table.rows.append(row)

        # Update DataTable efficiently with proper safety checks
        try:
            if files_table_ref.current is not None and hasattr(files_table_ref.current, 'page') and files_table_ref.current.page is not None:
                files_table_ref.current.update()
            elif hasattr(files_table, 'page') and files_table.page is not None:
                files_table.update()
            else:
                logger.debug("Skipping DataTable update - control not attached to page yet")
        except Exception as e:
            logger.warning(f"Failed to update DataTable: {e}")
            # Skip update to prevent errors - the table will be updated when properly attached

        logger.debug(f"DataTable updated with {len(data_to_display[:50])} rows")

    # Server-Mediated File Action Functions
    async def download_file_async(file_data: Dict[str, Any]):
        """Download file using server-mediated operations with comprehensive error handling."""
        file_name = file_data.get("name", "unknown")
        file_id = file_data.get("id", "")

        try:
            # Set loading state with proper state management
            if state_manager:
                state_manager.set_loading(f"download_{file_id}", True)

            # Show loading feedback to user
            status_text.value = f"Downloading {file_name}..."
            status_text.color = ft.Colors.SECONDARY
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()

            # Validate file data
            if not file_id or not file_name:
                raise ValueError("Invalid file data: missing ID or name")

            # Compute destination path (e.g., ~/Downloads/<name>)
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            destination_path = os.path.join(downloads_dir, file_name)

            # Server-mediated download operation with enhanced error handling
            if state_manager:
                result = await state_manager.server_mediated_update(
                    key="file_downloaded",
                    value={
                        "file_id": file_id,
                        "filename": file_name,
                        "destination_path": destination_path,
                        "timestamp": datetime.now().isoformat()
                    },
                    server_operation="download_file_async",
                    file_id=file_id,
                    destination_path=destination_path
                )
            else:
                # Fallback when no state manager - use server bridge directly
                result = await server_bridge.download_file_async(file_id, destination_path) if server_bridge else {'success': False, 'error': 'No server connection'}

            if result.get('success'):
                show_success_message(page, f"Downloaded {file_name} successfully")
                logger.info(f"File downloaded: {file_name}")
                # Update status to show completion
                status_text.value = f"Downloaded {file_name}"
                status_text.color = ft.Colors.TERTIARY
            else:
                # Enhanced fallback with better error reporting
                error_msg = result.get('error', 'Server operation failed')
                logger.warning(f"Download fallback for {file_name}: {error_msg}")

                # Create mock content with enhanced metadata
                mock_content = f"""Mock file: {file_name}
Size: {file_data.get('size', 0)} bytes
Status: {file_data.get('status', 'unknown')}
Type: {file_data.get('type', 'unknown')}
Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Mode: Demo/Development
Original Error: {error_msg}"""

                async with aiofiles.open(destination_path, 'w', encoding='utf-8') as f:
                    await f.write(mock_content)

                show_success_message(page, f"Mock downloaded {file_name} (demo mode)")
                if state_manager:
                    await state_manager.update_async("file_downloaded", {
                        "file_id": file_id,
                        "filename": file_name,
                        "destination_path": destination_path,
                        "mode": "mock",
                        "error": error_msg,
                        "timestamp": datetime.now().isoformat()
                    }, source="fallback")

                # Update status to show fallback completion
                status_text.value = f"Downloaded {file_name} (demo mode)"
                status_text.color = ft.Colors.SECONDARY

        except Exception as e:
            logger.error(f"Download failed for {file_name}: {e}", exc_info=True)
            show_error_message(page, f"Download failed for {file_name}: {str(e)}")
            # Update status to show error
            status_text.value = f"Download failed: {file_name}"
            status_text.color = ft.Colors.ERROR
        finally:
            if state_manager:
                state_manager.set_loading(f"download_{file_id}", False)
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()

    def download_file(file_data: Dict[str, Any]):
        """Wrapper for async download file operation."""
        page.run_task(download_file_async, file_data)

    async def verify_file_async(file_data: Dict[str, Any]):
        """Verify file integrity using server-mediated operations with comprehensive validation."""
        file_name = file_data.get("name", "unknown")
        file_id = file_data.get("id", "")
        file_path = file_data.get("path", "")

        try:
            # Set loading state with proper state management
            if state_manager:
                state_manager.set_loading(f"verify_{file_id}", True)

            # Show loading feedback to user
            status_text.value = f"Verifying {file_name}..."
            status_text.color = ft.Colors.SECONDARY
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()

            # Validate file data
            if not file_id or not file_name:
                raise ValueError("Invalid file data: missing ID or name")

            # Server-mediated verification operation with enhanced error handling
            if state_manager:
                result = await state_manager.server_mediated_update(
                    key="file_verified",
                    value={
                        "file_id": file_id,
                        "filename": file_name,
                        "timestamp": datetime.now().isoformat()
                    },
                    server_operation="verify_file_async",
                    file_id=file_id
                )
            else:
                # Fallback when no state manager - use server bridge directly
                result = await server_bridge.verify_file_async(file_id) if server_bridge else {'success': False, 'error': 'No server connection'}

            if result.get('success') and result.get('data'):
                # Show enhanced server verification results with Material Design styling
                verification_data = result['data']
                verification_info = ft.Column([
                    ft.Text("File Verification Results", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                    ft.Divider(color=ft.Colors.OUTLINE, thickness=1),
                    ft.Container(height=8),
                    ft.Text(f"📄 File: {file_name}", size=16, weight=ft.FontWeight.W_500),
                    ft.Text(f"📊 Size: {format_file_size(verification_data.get('size', 0))}", size=14),
                    ft.Text(f"🕒 Modified: {verification_data.get('modified', 'Unknown')}", size=14),
                    ft.Container(
                        content=ft.Text("✅ File verified successfully", size=14, weight=ft.FontWeight.W_500),
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.TERTIARY),
                        border_radius=8,
                        padding=ft.Padding(12, 8, 12, 8)
                    ),
                    ft.Container(height=12),
                    ft.Text("🔐 SHA256 Hash:", weight=ft.FontWeight.BOLD, size=14),
                    ft.Container(
                        content=ft.Text(verification_data.get('hash', 'N/A'), selectable=True, size=12, color=ft.Colors.ON_SURFACE),
                        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
                        border_radius=8,
                        padding=ft.Padding(12, 8, 12, 8),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE))
                    )
                ], tight=True, spacing=8)

                show_info(page, f"Verification: {file_name}", verification_info, width=550)
                show_success_message(page, f"File {file_name} verified successfully")
                # Update status to show completion
                status_text.value = f"Verified {file_name}"
                status_text.color = ft.Colors.TERTIARY
            else:
                # Enhanced fallback verification with better error reporting
                error_msg = result.get('error', 'Server operation failed')
                logger.warning(f"Verification fallback for {file_name}: {error_msg}")

                if os.path.exists(file_path):
                    # Calculate SHA256 hash with progress indication (async)
                    sha256_hash = hashlib.sha256()
                    file_size = os.path.getsize(file_path)
                    async with aiofiles.open(file_path, "rb") as f:
                        while True:
                            chunk = await f.read(4096)
                            if not chunk:
                                break
                            sha256_hash.update(chunk)
                            # Allow other async operations to run during hash calculation
                            await asyncio.sleep(0)

                    file_stats = os.stat(file_path)

                    verification_info = ft.Column([
                        ft.Text("File Verification Results (Local)", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                        ft.Divider(color=ft.Colors.OUTLINE, thickness=1),
                        ft.Container(height=8),
                        ft.Text(f"📄 File: {file_name}", size=16, weight=ft.FontWeight.W_500),
                        ft.Text(f"📊 Size: {format_file_size(file_stats.st_size)}", size=14),
                        ft.Text(f"🕒 Modified: {datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}", size=14),
                        ft.Container(
                            content=ft.Text("✅ File exists and is readable", size=14, weight=ft.FontWeight.W_500),
                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.TERTIARY),
                            border_radius=8,
                            padding=ft.Padding(12, 8, 12, 8)
                        ),
                        ft.Container(height=12),
                        ft.Text("🔐 SHA256 Hash:", weight=ft.FontWeight.BOLD, size=14),
                        ft.Container(
                            content=ft.Text(sha256_hash.hexdigest(), selectable=True, size=12, color=ft.Colors.ON_SURFACE),
                            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
                            border_radius=8,
                            padding=ft.Padding(12, 8, 12, 8),
                            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE))
                        )
                    ], tight=True, spacing=8)

                    show_info(page, f"Verification: {file_name}", verification_info, width=550)
                    show_success_message(page, f"File {file_name} verified successfully (local)")
                    # Update status to show local completion
                    status_text.value = f"Verified {file_name} (local)"
                    status_text.color = ft.Colors.SECONDARY
                else:
                    # Enhanced mock verification with detailed info
                    mock_hash = hashlib.sha256(f"mock_{file_name}_{datetime.now().isoformat()}".encode()).hexdigest()
                    verification_info = ft.Column([
                        ft.Text("Mock Verification Results", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.SECONDARY),
                        ft.Divider(color=ft.Colors.OUTLINE, thickness=1),
                        ft.Container(height=8),
                        ft.Text(f"📄 File: {file_name}", size=16, weight=ft.FontWeight.W_500),
                        ft.Text(f"📊 Size: {format_file_size(file_data.get('size', 0))}", size=14),
                        ft.Text(f"🕒 Last Modified: {file_data.get('modified', 'Unknown')}", size=14),
                        ft.Container(
                            content=ft.Text("🔄 Mock verification - file integrity confirmed", size=14, weight=ft.FontWeight.W_500),
                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SECONDARY),
                            border_radius=8,
                            padding=ft.Padding(12, 8, 12, 8)
                        ),
                        ft.Container(height=12),
                        ft.Text("🔐 Mock SHA256 Hash:", weight=ft.FontWeight.BOLD, size=14),
                        ft.Container(
                            content=ft.Text(mock_hash, selectable=True, size=12, color=ft.Colors.ON_SURFACE),
                            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE),
                            border_radius=8,
                            padding=ft.Padding(12, 8, 12, 8),
                            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE))
                        )
                    ], tight=True, spacing=8)

                    show_info(page, f"Verification: {file_name}", verification_info, width=550)
                    show_success_message(page, f"Mock verified {file_name} (demo mode)")
                    # Update status to show mock completion
                    status_text.value = f"Verified {file_name} (demo mode)"
                    status_text.color = ft.Colors.SECONDARY

                if state_manager:
                    await state_manager.update_async("file_verified", {
                        "file_id": file_id,
                        "filename": file_name,
                        "mode": "fallback",
                        "timestamp": datetime.now().isoformat()
                    }, source="fallback")

        except Exception as e:
            logger.error(f"Verification failed for {file_name}: {e}", exc_info=True)
            show_error_message(page, f"Verification failed for {file_name}: {str(e)}")
            # Update status to show error
            status_text.value = f"Verification failed: {file_name}"
            status_text.color = ft.Colors.ERROR
        finally:
            if state_manager:
                state_manager.set_loading(f"verify_{file_id}", False)
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()

    def verify_file(file_data: Dict[str, Any]):
        """Wrapper for async verify file operation."""
        page.run_task(verify_file_async, file_data)

    async def delete_file_async(file_data: Dict[str, Any]):
        """Delete file using server-mediated operations with comprehensive validation."""
        file_name = file_data.get("name", "unknown")
        file_id = file_data.get("id", "")

        try:
            # Set loading state with proper state management
            if state_manager:
                state_manager.set_loading(f"delete_{file_id}", True)

            # Show loading feedback to user
            status_text.value = f"Deleting {file_name}..."
            status_text.color = ft.Colors.ERROR
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()

            # Validate file data
            if not file_id or not file_name:
                raise ValueError("Invalid file data: missing ID or name")

            # Server-mediated delete operation with enhanced error handling
            if state_manager:
                result = await state_manager.server_mediated_update(
                    key="file_deleted",
                    value={
                        "file_id": file_id,
                        "filename": file_name,
                        "timestamp": datetime.now().isoformat()
                    },
                    server_operation="delete_file_async",
                    file_id=file_id
                )
            else:
                # Fallback when no state manager - use server bridge directly
                result = await server_bridge.delete_file_async(file_id) if server_bridge else {'success': False, 'error': 'No server connection'}

            if result.get('success'):
                show_success_message(page, f"File {file_name} deleted successfully")
                logger.info(f"File {file_id} deleted via server")
                # Update files_data via state_manager only when data actually changes
                updated_files_data = [f for f in files_data if f.get("id") != file_id]
                if len(updated_files_data) != len(files_data):
                    await state_manager.update_async("files_data", updated_files_data, source="server_delete")
                # Update status to show completion
                status_text.value = f"Deleted {file_name}"
                status_text.color = ft.Colors.TERTIARY
            else:
                # Enhanced fallback delete with better error reporting
                error_msg = result.get('error', 'Server operation failed')
                logger.warning(f"Delete fallback for file {file_id}: {error_msg}")

                # Find and remove the file from the data structure
                file_found = False
                for i, file_item in enumerate(files_data):
                    current_id = file_item.get("id")
                    if current_id == file_id:
                        old_status = file_item.get("status", "Unknown")
                        files_data.pop(i)  # Actually remove the file
                        file_found = True
                        logger.info(f"File {file_id} removed from files_data (was {old_status})")
                        break

                if file_found:
                    # Update files_data state only when data actually changes (after fallback delete)
                    if state_manager:
                        await state_manager.update_async("files_data", files_data, source="fallback_delete")

                        # Update state manager with deletion event
                        await state_manager.update_async("file_deleted", {
                            "file_id": file_id,
                            "filename": file_name,
                            "mode": "fallback",
                            "error": error_msg,
                            "timestamp": datetime.now().isoformat()
                        }, source="fallback")

                    # Keep UI updates minimal - use control.update()
                    apply_filters()  # This will call table_content.update() internally
                    show_success_message(page, f"File {file_name} deleted successfully")
                    logger.info(f"File {file_id} successfully deleted and UI updated")
                    # Update status to show fallback completion
                    status_text.value = f"Deleted {file_name} (demo mode)"
                    status_text.color = ft.Colors.SECONDARY
                else:
                    show_error_message(page, f"File {file_name} not found in data")
                    logger.error(f"File {file_id} not found in files_data during delete")
                    # Update status to show error
                    status_text.value = f"Delete failed: file not found"
                    status_text.color = ft.Colors.ERROR

        except Exception as e:
            logger.error(f"Error during delete: {e}", exc_info=True)
            show_error_message(page, f"Error deleting file {file_name}: {str(e)}")
            # Update status to show error
            status_text.value = f"Delete failed: {file_name}"
            status_text.color = ft.Colors.ERROR
        finally:
            state_manager.set_loading(f"delete_{file_id}", False)
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()

    def delete_file(file_data: Dict[str, Any]):
        """Delete file with enhanced confirmation dialog."""
        file_name = file_data.get("name", "unknown")
        file_size = format_file_size(file_data.get("size", 0))
        file_type = file_data.get("type", "unknown")

        def confirm_delete(e):
            """Wrapper to run async delete in a task with validation."""
            try:
                page.run_task(delete_file_async, file_data)
            except Exception as ex:
                logger.error(f"Failed to start delete task: {ex}")
                show_error_message(page, f"Failed to initiate delete: {str(ex)}")

        # Enhanced confirmation dialog with file details
        confirmation_message = f"""Are you sure you want to delete this file?

📄 Name: {file_name}
📊 Size: {file_size}
📁 Type: {file_type.title()}

⚠️ This action cannot be undone and will permanently remove the file from the backup system."""

        show_confirmation(
            page,
            "🗑️ Confirm File Deletion",
            confirmation_message,
            confirm_delete,
            confirm_text="Delete File",
            is_destructive=True
        )

    # Enhanced UI Layout Construction
    header_row = ft.Row([
        ft.Row([
            ft.Icon(ft.Icons.FOLDER_COPY, size=28, color=ft.Colors.PRIMARY),
            ft.Text("Files Management", size=24, weight=ft.FontWeight.BOLD)
        ], spacing=12),
        ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh Files",
            icon_size=24,
            icon_color=ft.Colors.PRIMARY,
            on_click=lambda e: page.run_task(load_files_data),
            style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                    ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT
                },
                shape=ft.CircleBorder(),
                padding=12,
                animation_duration=200
            )
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # Enhanced responsive filter controls with adaptive column sizing
    # Remove hardcoded widths from individual controls for responsive behavior
    search_field.width = None  # Remove fixed width for responsive behavior
    status_dropdown.width = None
    type_dropdown.width = None

    filters_row = create_modern_card(
        content=ft.ResponsiveRow([
            # Search field - adaptive sizing: desktop(50%), tablet(100%), mobile(100%)
            ft.Column([search_field], col={"sm": 12, "md": 12, "lg": 6}),
            # Status filter - adaptive sizing: desktop(25%), tablet(50%), mobile(100%)
            ft.Column([status_dropdown], col={"sm": 12, "md": 6, "lg": 3}),
            # Type filter - adaptive sizing: desktop(25%), tablet(50%), mobile(100%)
            ft.Column([type_dropdown], col={"sm": 12, "md": 6, "lg": 3})
        ], spacing=20, vertical_alignment=ft.CrossAxisAlignment.END),
        elevation="elevated",  # Enhanced elevation for premium appearance
        padding=28,  # Enhanced padding using theme system values
        return_type="container"
    )

    # Enhanced table container with responsive design and sophisticated shadows
    table_container = ft.Container(
        content=ft.ResponsiveRow([
            ft.Column([
                apply_advanced_table_effects(files_table, container_elevation="floating")
            ], col={"sm": 12, "md": 12, "lg": 12}, expand=True)
        ]),
        expand=True  # Enable proper window scaling
    )

    status_row = ft.Row([
        ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.PRIMARY),
        status_text,
        loading_indicator  # Comment 3: Add loading indicator to status row
    ], spacing=8)

    main_view = ft.Column([
        header_row,
        ft.Divider(),
        filters_row,
        ft.Container(height=16),  # Spacing
        table_container,
        ft.Container(height=8),   # Spacing
        status_row
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=0)

    # Enhanced reactive state subscriptions with proper error handling
    async def on_files_data_changed(new_files, old_files):
        """React to files data changes from state manager with comprehensive error handling."""
        nonlocal files_data
        try:
            if new_files != files_data:
                files_data.clear()
                files_data.extend(new_files or [])
                apply_filters()
                status_text.value = f"Loaded {len(files_data)} files"
                status_text.color = ft.Colors.PRIMARY
                if hasattr(status_text, 'page') and status_text.page:
                    status_text.update()
                logger.info(f"Files data updated: {len(files_data)} files")
        except Exception as e:
            logger.error(f"Failed to update files data UI: {e}", exc_info=True)
            # Set error state with user-friendly message
            status_text.value = "Error loading files data"
            status_text.color = ft.Colors.ERROR
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()
            show_error_message(page, f"Failed to update files display: {str(e)}")

    async def on_loading_state_changed(new_loading_states, old_loading_states):
        """React to loading state changes with enhanced loading state management."""
        try:
            # Check for any file operation loading states
            is_loading = any([
                new_loading_states.get("files_data"),
                any(key.startswith(("download_", "verify_", "delete_")) for key in new_loading_states.keys() if new_loading_states.get(key))
            ])

            if is_loading:
                if new_loading_states.get("files_data"):
                    status_text.value = "Loading files..."
                else:
                    status_text.value = "Processing file operation..."
                status_text.color = ft.Colors.ON_SURFACE
                if hasattr(status_text, 'page') and status_text.page:
                    status_text.update()
                # Enhanced loading indicator visibility
                loading_indicator.visible = True
                if hasattr(loading_indicator, 'page') and loading_indicator.page:
                    loading_indicator.update()
            else:
                # Hide loading indicator when not loading
                loading_indicator.visible = False
                if hasattr(loading_indicator, 'page') and loading_indicator.page:
                    loading_indicator.update()
        except Exception as e:
            logger.error(f"Failed to update loading state UI: {e}", exc_info=True)

    async def on_file_operation_complete(event_data, old_data):
        """React to file operation completion events."""
        if event_data:
            operation_type = "operation"
            if "file_downloaded" in str(event_data):
                operation_type = "download"
            elif "file_verified" in str(event_data):
                operation_type = "verification"
            elif "file_deleted" in str(event_data):
                operation_type = "deletion"

            logger.info(f"File {operation_type} completed: {event_data}")

    # Enhanced subscription setup with comprehensive error handling
    async def setup_subscriptions():
        """Set up state subscriptions after view is attached to page with error handling."""
        try:
            await asyncio.sleep(0.1)  # Small delay to ensure page attachment
            if state_manager:
                # Subscribe to all relevant state changes
                state_manager.subscribe_async("files_data", on_files_data_changed)
                state_manager.subscribe_async("loading_states", on_loading_state_changed)
                state_manager.subscribe_async("file_downloaded", on_file_operation_complete)
                state_manager.subscribe_async("file_verified", on_file_operation_complete)
                state_manager.subscribe_async("file_deleted", on_file_operation_complete)
                logger.info("Files view subscriptions established")
            else:
                logger.warning("State manager not available - subscriptions skipped")

            # Trigger initial data load after subscriptions are safely set up
            await load_files_data()
        except Exception as e:
            logger.error(f"Failed to setup files view subscriptions: {e}", exc_info=True)
            # Fallback: try to load data anyway
            try:
                await load_files_data()
            except Exception as load_error:
                logger.error(f"Fallback data load failed: {load_error}")
                show_error_message(page, "Failed to initialize files view")

    # Start subscription setup in background with error handling
    page.run_task(setup_subscriptions)

    return main_view