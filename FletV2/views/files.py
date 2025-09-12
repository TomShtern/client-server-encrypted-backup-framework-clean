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
from utils.user_feedback import show_success_message, show_error_message
from utils.dialog_consolidation_helper import show_confirmation, show_info

logger = get_logger(__name__)

def create_files_view(
    server_bridge: Optional[ServerBridge], 
    page: ft.Page, 
    state_manager: Optional[StateManager] = None
) -> ft.Control:
    """
    Create files view with clean, maintainable implementation.
    Follows successful patterns from clients.py and analytics.py.
    """
    logger.info("Creating files view")
    
    # State Management - Simple and Direct
    files_data: List[Dict[str, Any]] = []
    filtered_files: List[Dict[str, Any]] = []
    search_query = ""
    status_filter = "all"
    type_filter = "all"
    is_loading = False
    
    # UI Control References
    search_field = ft.TextField(
        label="Search files...",
        prefix_icon=ft.Icons.SEARCH,
        on_change=lambda e: apply_search(e.control.value),
        width=300
    )
    
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
        on_change=lambda e: apply_filter("status", e.control.value),
        width=150
    )
    
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
        on_change=lambda e: apply_filter("type", e.control.value),
        width=150
    )
    
    files_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Modified", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
        ],
        rows=[],
        show_bottom_border=True,
        expand=True
    )
    
    status_text = ft.Text("Ready", size=12, color=ft.Colors.BLUE)
    
    # Core Data Functions
    async def load_files_data():
        """Load files data from server bridge with fallback to mock data."""
        nonlocal files_data, is_loading
        
        if is_loading:
            return
            
        is_loading = True
        status_text.value = "Loading files..."
        status_text.color = ft.Colors.ORANGE
        # Use page.update() instead of status_text.update() to avoid page attachment issues
        page.update()
        
        try:
            if server_bridge:
                try:
                    files_data = await server_bridge.get_files_async()
                    logger.info(f"Loaded {len(files_data)} files from server bridge")
                except Exception as e:
                    logger.warning(f"Server bridge failed, using mock data: {e}")
                    files_data = generate_mock_files()
            else:
                files_data = generate_mock_files()
                
            # Update state manager
            if state_manager:
                state_manager.update("files_data", files_data)
                
            apply_filters()
            status_text.value = f"Loaded {len(files_data)} files"
            status_text.color = ft.Colors.GREEN
            
        except Exception as e:
            logger.error(f"Failed to load files: {e}")
            show_error_message(page, f"Failed to load files: {str(e)}")
            status_text.value = f"Error: {str(e)}"
            status_text.color = ft.Colors.RED
        finally:
            is_loading = False
            # Use page.update() instead of status_text.update() to avoid page attachment issues
            page.update()

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
        nonlocal search_query
        search_query = query.lower().strip()
        apply_filters()

    def apply_filter(filter_type: str, value: str):
        """Apply status or type filter and update display."""
        nonlocal status_filter, type_filter
        
        if filter_type == "status":
            status_filter = value
        elif filter_type == "type":
            type_filter = value
            
        apply_filters()

    def apply_filters():
        """Apply all active filters and update table display."""
        nonlocal filtered_files
        
        filtered_files = files_data.copy()
        
        # Apply search filter
        if search_query:
            filtered_files = [
                file for file in filtered_files
                if search_query in file.get("name", "").lower() or
                   search_query in file.get("type", "").lower()
            ]
        
        # Apply status filter
        if status_filter != "all":
            filtered_files = [
                file for file in filtered_files
                if file.get("status", "").lower() == status_filter
            ]
        
        # Apply type filter
        if type_filter != "all":
            filtered_files = [
                file for file in filtered_files
                if file.get("type", "").lower() == type_filter
            ]
        
        update_table_display()

    def update_table_display():
        """Update the files table with filtered data."""
        files_table.rows.clear()
        
        for file_data in filtered_files[:50]:  # Limit to 50 for performance
            # File type icon
            file_type = file_data.get("type", "unknown")
            if file_type == "document":
                type_icon = ft.Icons.DESCRIPTION
            elif file_type == "image":
                type_icon = ft.Icons.IMAGE
            elif file_type == "video":
                type_icon = ft.Icons.VIDEO_FILE
            elif file_type == "code":
                type_icon = ft.Icons.CODE
            else:
                type_icon = ft.Icons.INSERT_DRIVE_FILE
            
            # Enhanced status chip with colors matching clients page
            status = file_data.get("status", "unknown")
            
            # Enhanced status coloring matching actual mock data values (case-insensitive)
            status_lower = status.lower()
            if status_lower in ["complete", "completed"]:
                status_color = ft.Colors.GREEN_600
                status_icon = ft.Icons.CHECK_CIRCLE
            elif status_lower in ["uploading", "upload"]:
                status_color = ft.Colors.BLUE_600  
                status_icon = ft.Icons.UPLOAD
            elif status_lower in ["queued", "pending", "queue"]:
                status_color = ft.Colors.ORANGE_600
                status_icon = ft.Icons.PENDING
            elif status_lower in ["processing", "verified", "verify"]:
                status_color = ft.Colors.PURPLE_600
                status_icon = ft.Icons.VERIFIED
            elif status_lower in ["failed", "error", "fail"]:
                status_color = ft.Colors.RED_600
                status_icon = ft.Icons.ERROR
            else:
                status_color = ft.Colors.GREY_600
                status_icon = ft.Icons.HELP
            
            # Modern status chip with icon, shadow and animations
            status_chip = ft.Container(
                content=ft.Row([
                    ft.Icon(
                        status_icon,
                        size=14,
                        color=ft.Colors.WHITE
                    ),
                    ft.Text(
                        status.title(),
                        size=12,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD
                    )
                ], spacing=6, tight=True),
                bgcolor=status_color,
                border_radius=16,
                padding=ft.Padding(10, 6, 10, 6),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    offset=ft.Offset(0, 2),
                    color=ft.Colors.with_opacity(0.3, status_color)
                ),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
            )
            
            # Format file size
            size_bytes = file_data.get("size", 0)
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024*1024:
                size_str = f"{size_bytes/1024:.1f} KB"
            else:
                size_str = f"{size_bytes/(1024*1024):.1f} MB"
            
            # Enhanced action buttons with modern hover states
            actions_row = ft.Row([
                ft.IconButton(
                    icon=ft.Icons.DOWNLOAD,
                    tooltip="Download File",
                    icon_color=ft.Colors.BLUE_600,
                    icon_size=20,
                    on_click=lambda e, f=file_data: download_file(f),
                    style=ft.ButtonStyle(
                        bgcolor={
                            ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
                            ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT
                        },
                        shape=ft.CircleBorder(),
                        padding=8,
                        animation_duration=200
                    )
                ),
                ft.IconButton(
                    icon=ft.Icons.VERIFIED,
                    tooltip="Verify Integrity",
                    icon_color=ft.Colors.GREEN_600,
                    icon_size=20,
                    on_click=lambda e, f=file_data: verify_file(f),
                    style=ft.ButtonStyle(
                        bgcolor={
                            ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
                            ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT
                        },
                        shape=ft.CircleBorder(),
                        padding=8,
                        animation_duration=200
                    )
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="Delete File",
                    icon_color=ft.Colors.RED_600,
                    icon_size=20,
                    on_click=lambda e, f=file_data: delete_file(f),
                    style=ft.ButtonStyle(
                        bgcolor={
                            ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.RED),
                            ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT
                        },
                        shape=ft.CircleBorder(),
                        padding=8,
                        animation_duration=200
                    )
                )
            ], spacing=4, tight=True)
            
            files_table.rows.append(
                ft.DataRow([
                    ft.DataCell(
                        ft.Row([
                            ft.Icon(type_icon, size=16, color=ft.Colors.BLUE_600),
                            ft.Text(file_data.get("name", ""), size=13)
                        ], spacing=8, tight=True)
                    ),
                    ft.DataCell(ft.Text(size_str, size=13)),
                    ft.DataCell(ft.Text(file_type.title(), size=13)),
                    ft.DataCell(status_chip),
                    ft.DataCell(ft.Text(file_data.get("modified", ""), size=13)),
                    ft.DataCell(actions_row)
                ])
            )
        
        files_table.update()

    # File Action Functions
    def download_file(file_data: Dict[str, Any]):
        """Download file to Downloads folder."""
        file_name = file_data.get("name", "unknown")
        file_path = file_data.get("path", "")
        
        try:
            # Create Downloads directory
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            os.makedirs(downloads_dir, exist_ok=True)
            
            destination = os.path.join(downloads_dir, file_name)
            
            if os.path.exists(file_path):
                # Real file copy
                shutil.copy2(file_path, destination)
                show_success_message(page, f"Downloaded {file_name} to Downloads")
            else:
                # Mock download - create placeholder
                mock_content = f"""Mock file: {file_name}
Size: {file_data.get('size', 0)} bytes  
Status: {file_data.get('status', 'unknown')}
Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
                
                with open(destination, 'w', encoding='utf-8') as f:
                    f.write(mock_content)
                    
                show_success_message(page, f"Mock downloaded {file_name} (demo mode)")
            
            logger.info(f"File downloaded: {destination}")
            
        except Exception as e:
            logger.error(f"Download failed for {file_name}: {e}")
            show_error_message(page, f"Download failed: {str(e)}")

    def verify_file(file_data: Dict[str, Any]):
        """Verify file integrity and show results."""
        file_name = file_data.get("name", "unknown")
        file_path = file_data.get("path", "")
        
        try:
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
                
        except Exception as e:
            logger.error(f"Verification failed for {file_name}: {e}")
            show_error_message(page, f"Verification failed: {str(e)}")

    def delete_file(file_data: Dict[str, Any]):
        """Delete file with confirmation."""
        file_name = file_data.get("name", "unknown")
        
        async def confirm_delete_async(e):
            """Actually delete the file like client disconnect does."""
            try:
                file_id = file_data.get("id", "")
                
                # Server bridge operation
                if server_bridge:
                    try:
                        result = await server_bridge.delete_file_async(file_id)
                        if result:
                            # Update local state via state manager
                            if state_manager:
                                state_manager.update("file_deleted", {
                                    "file_id": file_id,
                                    "filename": file_name,
                                    "timestamp": datetime.now().isoformat()
                                })
                            
                            show_success_message(page, f"File {file_name} deleted successfully")
                            # Refresh files list to show updated data
                            page.run_task(load_files_data)
                        else:
                            show_error_message(page, f"Failed to delete file {file_name}")
                    except Exception as e:
                        logger.error(f"Server bridge delete error: {e}")
                        show_error_message(page, f"Error deleting file: {str(e)}")
                else:
                    # Mock delete - ACTUALLY remove from files_data like clients page does
                    logger.info(f"Performing REAL delete for file {file_id}")
                    
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
                        # Update local state via state manager
                        if state_manager:
                            state_manager.update("file_deleted", {
                                "file_id": file_id,
                                "filename": file_name,
                                "timestamp": datetime.now().isoformat()
                            })
                        
                        # Refresh the table to show updated data
                        apply_filters()
                        show_success_message(page, f"File {file_name} deleted successfully")
                        logger.info(f"File {file_id} successfully deleted and UI updated")
                    else:
                        show_error_message(page, f"File {file_name} not found in data")
                        logger.error(f"File {file_id} not found in files_data during delete")
                
            except Exception as e:
                logger.error(f"Error during delete: {e}")
                show_error_message(page, f"Error deleting file: {str(e)}")
        
        def confirm_delete(e):
            """Wrapper to run async delete in a task like clients page"""
            async def run_delete():
                await confirm_delete_async(e)
            
            page.run_task(run_delete)
        
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
    
    filters_row = ft.ResponsiveRow([
        ft.Column([search_field], col={"sm": 12, "md": 6}),
        ft.Column([status_dropdown], col={"sm": 6, "md": 3}),
        ft.Column([type_dropdown], col={"sm": 6, "md": 3})
    ], spacing=16)
    
    table_container = ft.Container(
        content=files_table,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8,
        padding=16,
        expand=True
    )
    
    status_row = ft.Row([
        ft.Icon(ft.Icons.INFO_OUTLINE, size=16, color=ft.Colors.BLUE),
        status_text
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
    
    # Initialize data loading
    page.run_task(load_files_data)
    
    return main_view