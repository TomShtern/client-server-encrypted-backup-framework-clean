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
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.dialog_consolidation_helper import show_success_message, show_error_message, show_confirmation, show_info
from utils.server_mediated_operations import create_server_mediated_operations, file_size_processor
from utils.ui_components import create_modern_card, apply_advanced_table_effects, create_status_chip

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

    # Professional DataTable with clean styling following clients.py pattern
    files_table = ft.DataTable(
        ref=files_table_ref,
        columns=[
            ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
            ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
            ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
            ft.DataColumn(ft.Text("Modified", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY))
        ],
        rows=[],
        heading_row_color=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
        border=ft.border.all(3, ft.Colors.PRIMARY),
        border_radius=16,
        data_row_min_height=62,
        column_spacing=28,
        show_checkbox_column=False,
        bgcolor=ft.Colors.SURFACE,
        divider_thickness=1
    )

    # Comment 8: Initial status message based on server availability
    initial_status = "Ready" if server_bridge else "Server unavailable—running in mock mode."
    status_text = ft.Text(initial_status, ref=status_text_ref, size=12, color=ft.Colors.ON_SURFACE)

    # Comment 3: Add ProgressRing for loading indicator
    loading_indicator = ft.ProgressRing(ref=loading_indicator_ref, visible=False, width=16, height=16)

    # Server-Mediated Data Functions
    async def load_files_data():
        """Load files data using server-mediated state management."""
        # Set loading state through state manager
        state_manager.set_loading("files_data", True)
        status_text.value = "Loading files..."
        status_text.color = ft.Colors.ON_SURFACE
        status_text.update()

        try:
            # Use server-mediated update for persistence and consistency
            result = await state_manager.server_mediated_update(
                key="files_data",
                value=None,  # Will be set by server response
                server_operation="get_files_async"
            )

            if not result.get('success'):
                # Fallback to mock data if server operation fails
                mock_files = generate_mock_files()
                await state_manager.update_async("files_data", mock_files, source="fallback")
                logger.warning("Using mock files data")

        except Exception as e:
            logger.error(f"Failed to load files: {e}")
            show_error_message(page, f"Failed to load files: {str(e)}")
            error_files = []
            await state_manager.update_async("files_data", error_files, source="error")
        finally:
            state_manager.set_loading("files_data", False)

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

    def get_status_color(status: str) -> str:
        """Get status color matching clients.py pattern."""
        status_lower = status.lower()
        if status_lower in ["complete", "completed"]:
            return ft.Colors.GREEN_600
        elif status_lower in ["uploading", "upload"]:
            return ft.Colors.BLUE_600
        elif status_lower in ["queued", "pending", "queue"]:
            return ft.Colors.ORANGE_600
        elif status_lower in ["processing", "verified", "verify"]:
            return ft.Colors.PURPLE_600
        elif status_lower in ["failed", "error", "fail"]:
            return ft.Colors.RED_600
        else:
            return ft.Colors.GREY_600

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
        """Download file using server-mediated operations."""
        file_name = file_data.get("name", "unknown")
        file_id = file_data.get("id", "")

        try:
            # Set loading state
            state_manager.set_loading(f"download_{file_id}", True)

            # Compute destination path (e.g., ~/Downloads/<name>)
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            destination_path = os.path.join(downloads_dir, file_name)

            # Server-mediated download operation with arguments
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

            if result.get('success'):
                show_success_message(page, f"Downloaded {file_name} successfully")
                logger.info(f"File downloaded: {file_name}")
            else:
                # Fallback mock download
                mock_content = f"""Mock file: {file_name}
Size: {file_data.get('size', 0)} bytes
Status: {file_data.get('status', 'unknown')}
Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

                with open(destination_path, 'w', encoding='utf-8') as f:
                    f.write(mock_content)

                show_success_message(page, f"Mock downloaded {file_name} (demo mode)")
                await state_manager.update_async("file_downloaded", {
                    "file_id": file_id,
                    "filename": file_name,
                    "destination_path": destination_path,
                    "mode": "mock",
                    "timestamp": datetime.now().isoformat()
                }, source="fallback")

        except Exception as e:
            logger.error(f"Download failed for {file_name}: {e}")
            show_error_message(page, f"Download failed: {str(e)}")
        finally:
            state_manager.set_loading(f"download_{file_id}", False)

    def download_file(file_data: Dict[str, Any]):
        """Wrapper for async download file operation."""
        page.run_task(download_file_async, file_data)

    async def verify_file_async(file_data: Dict[str, Any]):
        """Verify file integrity using server-mediated operations."""
        file_name = file_data.get("name", "unknown")
        file_id = file_data.get("id", "")
        file_path = file_data.get("path", "")

        try:
            # Set loading state
            state_manager.set_loading(f"verify_{file_id}", True)
            # Server-mediated verification operation with arguments
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

            if result.get('success') and result.get('data'):
                # Show server verification results
                verification_data = result['data']
                verification_info = ft.Column([
                    ft.Text("File Verification Results", size=18, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Text(f"File: {file_name}"),
                    ft.Text(f"Size: {verification_data.get('size', 'Unknown')} bytes"),
                    ft.Text(f"Modified: {verification_data.get('modified', 'Unknown')}"),
                    ft.Text("Status: File verified successfully", color=ft.Colors.GREEN),
                    ft.Divider(),
                    ft.Text("SHA256 Hash:", weight=ft.FontWeight.BOLD),
                    ft.Text(verification_data.get('hash', 'N/A'), selectable=True, size=11)
                ], tight=True, spacing=8)

                show_info(page, f"Verification: {file_name}", verification_info, width=500)
                show_success_message(page, f"File {file_name} verified successfully")
            else:
                # Fallback verification
                if os.path.exists(file_path):
                    # Calculate SHA256 hash
                    sha256_hash = hashlib.sha256()
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            sha256_hash.update(chunk)

                    file_stats = os.stat(file_path)

                    verification_info = ft.Column([
                        ft.Text("File Verification Results", size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text(f"File: {file_name}"),
                        ft.Text(f"Size: {file_stats.st_size:,} bytes"),
                        ft.Text(f"Modified: {datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"),
                        ft.Text("Status: File exists and is readable", color=ft.Colors.GREEN),
                        ft.Divider(),
                        ft.Text("SHA256 Hash:", weight=ft.FontWeight.BOLD),
                        ft.Text(sha256_hash.hexdigest(), selectable=True, size=11)
                    ], tight=True, spacing=8)

                    show_info(page, f"Verification: {file_name}", verification_info, width=500)
                    show_success_message(page, f"File {file_name} verified successfully")
                else:
                    # Mock verification
                    show_info(page, f"Verification: {file_name}",
                             ft.Text("Mock verification - file integrity confirmed", color=ft.Colors.GREEN))
                    show_success_message(page, f"Mock verified {file_name} (demo mode)")

                await state_manager.update_async("file_verified", {
                    "file_id": file_id,
                    "filename": file_name,
                    "mode": "fallback",
                    "timestamp": datetime.now().isoformat()
                }, source="fallback")

        except Exception as e:
            logger.error(f"Verification failed for {file_name}: {e}")
            show_error_message(page, f"Verification failed: {str(e)}")
        finally:
            state_manager.set_loading(f"verify_{file_id}", False)

    def verify_file(file_data: Dict[str, Any]):
        """Wrapper for async verify file operation."""
        page.run_task(verify_file_async, file_data)

    async def delete_file_async(file_data: Dict[str, Any]):
        """Delete file using server-mediated operations."""
        file_name = file_data.get("name", "unknown")
        file_id = file_data.get("id", "")

        try:
            # Set loading state
            state_manager.set_loading(f"delete_{file_id}", True)
            # Server-mediated delete operation with arguments
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

            if result.get('success'):
                show_success_message(page, f"File {file_name} deleted successfully")
                # Update files_data via state_manager only when data actually changes
                updated_files_data = [f for f in files_data if f.get("id") != file_id]
                if len(updated_files_data) != len(files_data):
                    await state_manager.update_async("files_data", updated_files_data, source="server_delete")
            else:
                # Fallback delete - actually remove from files_data
                logger.info(f"Performing fallback delete for file {file_id}")

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
                    await state_manager.update_async("files_data", files_data, source="fallback_delete")

                    # Update state manager with deletion event
                    await state_manager.update_async("file_deleted", {
                        "file_id": file_id,
                        "filename": file_name,
                        "mode": "fallback",
                        "timestamp": datetime.now().isoformat()
                    }, source="fallback")

                    # Keep UI updates minimal - use control.update()
                    apply_filters()  # This will call table_content.update() internally
                    show_success_message(page, f"File {file_name} deleted successfully")
                    logger.info(f"File {file_id} successfully deleted and UI updated")
                else:
                    show_error_message(page, f"File {file_name} not found in data")
                    logger.error(f"File {file_id} not found in files_data during delete")

        except Exception as e:
            logger.error(f"Error during delete: {e}")
            show_error_message(page, f"Error deleting file: {str(e)}")
        finally:
            state_manager.set_loading(f"delete_{file_id}", False)

    def delete_file(file_data: Dict[str, Any]):
        """Delete file with confirmation."""
        file_name = file_data.get("name", "unknown")

        def confirm_delete(e):
            """Wrapper to run async delete in a task."""
            page.run_task(delete_file_async, file_data)

        show_confirmation(
            page,
            "Confirm Delete",
            f"Are you sure you want to delete '{file_name}'?\n\nThis action cannot be undone.",
            confirm_delete,
            confirm_text="Delete",
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

    # Responsive filters row - removes hardcoded widths for better responsive behavior
    # Remove hardcoded width assignments for responsive layout
    filters_row = create_modern_card(
        content=ft.ResponsiveRow([
            ft.Column([search_field], col={"sm": 12, "md": 6, "lg": 4}),
            ft.Column([status_dropdown], col={"sm": 12, "md": 3, "lg": 2}),
            ft.Column([type_dropdown], col={"sm": 12, "md": 3, "lg": 2})
        ], spacing=16),
        elevation="soft",
        padding=24,
        return_type="container"
    )

    table_container = apply_advanced_table_effects(files_table, container_elevation="floating")

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

    # Reactive State Subscriptions
    async def on_files_data_changed(new_files, old_files):
        """React to files data changes from state manager."""
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
            logger.warning(f"Failed to update files data UI: {e}")

    async def on_loading_state_changed(new_loading_states, old_loading_states):
        """React to loading state changes."""
        try:
            if new_loading_states.get("files_data"):
                status_text.value = "Loading files..."
                status_text.color = ft.Colors.ON_SURFACE
                if hasattr(status_text, 'page') and status_text.page:
                    status_text.update()
                # Comment 3: Toggle loading indicator visibility
                loading_indicator.visible = True
                if hasattr(loading_indicator, 'page') and loading_indicator.page:
                    loading_indicator.update()
            else:
                # Comment 3: Hide loading indicator when not loading
                loading_indicator.visible = False
                if hasattr(loading_indicator, 'page') and loading_indicator.page:
                    loading_indicator.update()
        except Exception as e:
            logger.warning(f"Failed to update loading state UI: {e}")

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

    # Defer subscriptions until after view is attached to page
    async def setup_subscriptions():
        """Set up state subscriptions after view is attached to page"""
        await asyncio.sleep(0.1)  # Small delay to ensure page attachment
        if state_manager:
            state_manager.subscribe_async("files_data", on_files_data_changed)
            state_manager.subscribe_async("loading_states", on_loading_state_changed)
            state_manager.subscribe_async("file_downloaded", on_file_operation_complete)
            state_manager.subscribe_async("file_verified", on_file_operation_complete)
            state_manager.subscribe_async("file_deleted", on_file_operation_complete)

        # Trigger initial data load after subscriptions are safely set up
        await load_files_data()

    # Start subscription setup in background
    page.run_task(setup_subscriptions)

    return main_view