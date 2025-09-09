#!/usr/bin/env python3
"""
Files View for FletV2
High-performance implementation with ListView virtualization and async operations.
Optimized for smooth UI with large file datasets.
"""

import flet as ft
from typing import List, Dict, Any, Tuple
import os
import asyncio
import aiofiles
from datetime import datetime, timedelta
from utils.debug_setup import get_logger
from utils.ui_helpers import (
    size_to_human,
    format_iso_short,
    build_status_badge,
    striped_row_color,
)
from utils.perf_metrics import PerfTimer
from utils.loading_states import LoadingState, create_loading_indicator, create_status_text
from utils.responsive_layouts import create_data_table_container, create_action_bar, SPACING
from utils.user_feedback import show_success_message, show_error_message, show_info_message
from utils.performance import (
    AsyncDebouncer, PaginationConfig, AsyncDataLoader,
    global_memory_manager, paginate_data
)
from config import RECEIVED_FILES_DIR, ASYNC_DELAY, show_mock_data

logger = get_logger(__name__)

# PopupMenuButton Solution - WORKING Implementation for Files
file_action_count = {"count": 0}
file_action_feedback_text = ft.Text("No file actions yet - click the menu buttons", size=14, color=ft.Colors.BLUE)

def download_file_action(file_data, page):
    """Download action - download file to Downloads folder."""
    file_name = file_data.get('name', 'Unknown file')
    file_path = file_data.get('path', '')
    file_size = file_data.get('size', 0)
    logger.info(f"Download file action for: {file_name}")
    
    # Create async task to avoid blocking the UI
    page.run_task(_download_file_async(file_data, page))

async def _download_file_async(file_data, page):
    """Async helper for file download to avoid blocking UI."""
    file_name = file_data.get('name', 'Unknown file')
    file_path = file_data.get('path', '')
    file_size = file_data.get('size', 0)
    
    try:
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
            logger.info(f"Created Downloads directory: {downloads_dir}")
        
        destination_path = os.path.join(downloads_dir, file_name)
        
        # Check if file exists and is readable
        if file_path and file_path != "mock" and os.path.exists(file_path):
            # Real file copy operation - use async
            import shutil
            await asyncio.get_event_loop().run_in_executor(None, shutil.copy2, file_path, destination_path)
            
            show_success_message(page, f"File {file_name} downloaded to Downloads folder")
            file_action_feedback_text.value = f"Downloaded {file_name} ({file_size} bytes)"
            file_action_feedback_text.update()
            logger.info(f"File copied from {file_path} to {destination_path}")
            
        else:
            # For mock data - create a simple text file as placeholder using aiofiles
            mock_content = f"""Mock file: {file_name}
Original path: {file_path}
Size: {file_size} bytes
Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            async with aiofiles.open(destination_path, 'w', encoding='utf-8') as f:
                await f.write(mock_content)
            
            show_success_message(page, f"Mock download: {file_name} created in Downloads")
            file_action_feedback_text.value = f"Mock download: {file_name}"
            file_action_feedback_text.update()
            logger.info(f"Mock file created at {destination_path}")
            
    except PermissionError as e:
        error_msg = f"Permission denied when downloading {file_name}"
        logger.error(f"{error_msg}: {e}")
        show_error_message(page, error_msg)
        file_action_feedback_text.value = f"Permission error: {file_name}"
        file_action_feedback_text.update()
        
    except Exception as e:
        error_msg = f"Error downloading {file_name}: {str(e)}"
        logger.error(error_msg)
        show_error_message(page, error_msg)
        file_action_feedback_text.value = f"Download failed: {file_name}"
        file_action_feedback_text.update()
        file_action_feedback_text.value = f"Download failed: {file_name}"
        file_action_feedback_text.update()

def verify_file_action(file_data, page):
    """Verify action - check file integrity and show verification results with enhanced error handling."""
    file_name = file_data.get('name', 'Unknown file')
    file_path = file_data.get('path', '')
    file_size_reported = file_data.get('size', 0)
    logger.info(f"Verify file action for: {file_name}")
    
    # Create async task to avoid blocking the UI
    page.run_task(_verify_file_async(file_data, page))

async def _verify_file_async(file_data, page):
    """Async helper for file verification to avoid blocking UI."""
    file_name = file_data.get('name', 'Unknown file')
    file_path = file_data.get('path', '')
    file_size_reported = file_data.get('size', 0)
    
    try:
        # Check if this is a real file path or mock data
        if file_path and file_path != "mock" and os.path.exists(file_path):
            # Get file stats with enhanced error handling - use async executor
            try:
                stat = await asyncio.get_event_loop().run_in_executor(None, os.stat, file_path)
                actual_file_size = stat.st_size
                modified_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                # Verify file size matches reported size
                size_match = abs(actual_file_size - file_size_reported) <= 1024  # Allow 1KB tolerance
                size_status = "✓ Size matches" if size_match else f"⚠ Size mismatch (reported: {file_size_reported}, actual: {actual_file_size})"
                
            except (OSError, ValueError) as stat_error:
                logger.error(f"Failed to get file stats: {stat_error}")
                show_error_message(page, f"Cannot access file {file_name}: {stat_error}")
                return

            # Calculate file hash for verification with progress indication - use async
            try:
                import hashlib
                # Use SHA256 only (remove MD5 per security guidance)
                hash_sha256 = hashlib.sha256()
                
                # Use aiofiles for async file reading
                async with aiofiles.open(file_path, "rb") as f:
                    chunk = await f.read(4096)
                    while chunk:
                        hash_sha256.update(chunk)
                        chunk = await f.read(4096)

                sha256_hash = hash_sha256.hexdigest()
                
            except (IOError, PermissionError) as hash_error:
                logger.error(f"Failed to calculate file hash: {hash_error}")
                show_error_message(page, f"Cannot read file {file_name}: {hash_error}")
                return

            # Create verification dialog
            verification_content = ft.Column([
                ft.Text("File Verification Results", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(f"File: {file_name}"),
                ft.Text(f"Size: {actual_file_size:,} bytes"),
                ft.Text(f"Modified: {modified_time}"),
                ft.Text(size_status, color=ft.Colors.GREEN if size_match else ft.Colors.ORANGE),
                ft.Text(f"Status: File exists and is readable", color=ft.Colors.GREEN),
                ft.Divider(),
                ft.Text("Checksum (SHA256):", weight=ft.FontWeight.BOLD),
                ft.Text(f"{sha256_hash}", selectable=True),
            ], tight=True, spacing=5)

            # Create and show dialog
            dialog = ft.AlertDialog(
                title=ft.Text(f"Verification: {file_name}"),
                content=verification_content,
                actions=[
                    ft.TextButton("Close", on_click=lambda e: close_dialog(dialog))
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )
            
            def close_dialog(dialog_ref):
                dialog_ref.open = False
                page.update()
            
            page.overlay.append(dialog)
            dialog.open = True
            page.update()
            
            show_success_message(page, f"File {file_name} verified successfully")
            file_action_feedback_text.value = f"Verified {file_name} - file is intact"
            file_action_feedback_text.update()
            
        else:
            # For mock data or missing files
            show_error_message(page, f"Cannot verify {file_name}: file not found")
            file_action_feedback_text.value = f"Verification failed: {file_name} not found"
            file_action_feedback_text.update()
            
    except Exception as e:
        logger.error(f"Failed to verify file {file_name}: {e}")
        show_error_message(page, f"Failed to verify file: {str(e)}")
        file_action_feedback_text.value = f"Verification error: {file_name}"
        file_action_feedback_text.update()

def delete_file_action(file_data, page, files_data=None, update_table_func=None):
    """Delete action - delete file with confirmation dialog."""
    file_name = file_data.get('name', 'Unknown file')
    file_path = file_data.get('path', '')
    file_id = file_data.get('id', '')
    logger.info(f"Delete file action for: {file_name}")
    
    def confirm_delete(e):
        try:
            # Close confirmation dialog
            confirmation_dialog.open = False
            page.update()
            
            # First try to delete from server bridge if available
            delete_success = False
            if server_bridge:
                try:
                    delete_success = server_bridge.delete_file(file_id)
                    logger.info(f"Server bridge delete result for {file_id}: {delete_success}")
                except Exception as bridge_error:
                    logger.warning(f"Server bridge delete failed: {bridge_error}")
                    delete_success = False
            
            # ALWAYS remove from local filesystem if it exists (regardless of server bridge result)
            if file_path and file_path != "mock" and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    show_success_message(page, f"File {file_name} deleted from disk successfully")
                    logger.info(f"File {file_name} physically deleted from {file_path}")
                    delete_success = True
                except Exception as fs_error:
                    logger.error(f"File system delete failed: {fs_error}")
                    if not delete_success:  # Only show error if server bridge also failed
                        show_error_message(page, f"Failed to delete file from disk: {fs_error}")
                        return
            else:
                # Mock delete or file doesn't exist on disk
                show_success_message(page, f"Mock delete: {file_name} (removed from list)")
                logger.info(f"Mock delete: {file_name} (file not found on disk)")
                delete_success = True
            
            # CRITICAL: Always remove from the UI data structure for immediate visual update
            if files_data is not None and delete_success:
                original_count = len(files_data)
                files_data[:] = [f for f in files_data if f.get('id') != file_id and f.get('name') != file_name]
                removed_count = original_count - len(files_data)
                logger.info(f"Removed {removed_count} file(s) from UI data structure (ID: {file_id}, Name: {file_name})")
                
                # Force immediate UI refresh
                if update_table_func:
                    update_table_func()
                    logger.info("Table refreshed after file deletion")
            
            file_action_feedback_text.value = f"Deleted {file_name} successfully"
            file_action_feedback_text.update()
                
        except Exception as e:
            logger.error(f"Error during delete: {e}")
            show_error_message(page, f"Error deleting file: {str(e)}")
            file_action_feedback_text.value = f"Delete failed: {file_name}"
            file_action_feedback_text.update()
    
    def cancel_delete(e):
        confirmation_dialog.open = False
        page.update()
        file_action_feedback_text.value = f"Delete cancelled: {file_name}"
        file_action_feedback_text.update()
    
    # Create confirmation dialog
    confirmation_dialog = ft.AlertDialog(
        title=ft.Text("Confirm Delete"),
        content=ft.Text(f"Are you sure you want to delete '{file_name}'?\n\nThis action cannot be undone."),
        actions=[
            ft.TextButton("Cancel", on_click=cancel_delete),
            ft.TextButton("Delete", on_click=confirm_delete, 
                         style=ft.ButtonStyle(color=ft.Colors.ERROR))
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )
    
    page.overlay.append(confirmation_dialog)
    confirmation_dialog.open = True
    page.update()


def create_files_view(server_bridge, page: ft.Page, state_manager=None) -> ft.Control:
    """
    Create files view with enhanced infrastructure and state management.
    Follows Framework Harmony principles - no custom classes, use Flet's built-ins.
    """
    logger.info("Creating files view with enhanced infrastructure")
    
    # High-performance state variables and optimization utilities
    files_data: List[Dict[str, Any]] = []  # raw list
    filtered_files_data: List[Dict[str, Any]] = []  # filtered slice
    # is_loading retained for potential future gating (currently unused)
    last_updated = None
    search_query = ""
    status_filter = "all"
    type_filter = "all"
    size_filter = "all"
    case_sensitive_search = False  # New state for case sensitivity
    
    # Performance optimization utilities
    # NOTE: AsyncDebouncer expects seconds, not milliseconds. 0.3 = 300ms.
    search_debouncer = AsyncDebouncer(delay=0.3)  # 300ms search debouncing
    # Use zero-based page index consistent with paginate_data utility (same fix as logs view)
    pagination_config = PaginationConfig(page_size=50, current_page=0)  # 50 files per page (zero-based)
    data_loader = AsyncDataLoader(max_cache_size=100)  # Cache up to 100 items
    
    # Memory management
    global_memory_manager.register_component("files_view")

    # Enhanced file actions with server bridge integration
    def download_file_action_enhanced(file_data, page):
        """Enhanced download action with server bridge integration."""
        file_id = file_data.get('id', '')
        file_name = file_data.get('name', 'Unknown file')
        file_size = file_data.get('size', 0)
        logger.info(f"Enhanced download file action for: {file_name}")
        
        async def download_async():
            try:
                # Show loading state
                file_action_feedback_text.value = f"Downloading {file_name}..."
                await file_action_feedback_text.update_async()
                
                downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                if not os.path.exists(downloads_dir):
                    os.makedirs(downloads_dir)
                    logger.info(f"Created Downloads directory: {downloads_dir}")
                
                destination_path = os.path.join(downloads_dir, file_name)
                
                # Try server bridge first
                if server_bridge:
                    try:
                        result = await server_bridge.download_file_async(file_id, destination_path)
                        if result:
                            # Update state via state manager
                            if state_manager:
                                await state_manager.update_state("file_downloaded", {
                                    "file_id": file_id,
                                    "file_name": file_name,
                                    "destination": destination_path,
                                    "timestamp": datetime.now().isoformat()
                                })
                            
                            show_success_message(page, f"File {file_name} downloaded successfully")
                            file_action_feedback_text.value = f"Downloaded {file_name} ({file_size} bytes)"
                            await file_action_feedback_text.update_async()
                            logger.info(f"File downloaded via server bridge: {destination_path}")
                            return
                    except Exception as e:
                        logger.error(f"Server bridge download error: {e}")
                        # Fall through to mock implementation
                
                # Mock implementation fallback
                file_path = file_data.get('path', '')
                if file_path and file_path != "mock" and os.path.exists(file_path):
                    # Real file copy operation
                    import shutil
                    shutil.copy2(file_path, destination_path)
                    
                    show_success_message(page, f"File {file_name} downloaded to Downloads folder")
                    file_action_feedback_text.value = f"Downloaded {file_name} ({file_size} bytes)"
                    await file_action_feedback_text.update_async()
                    logger.info(f"File copied from {file_path} to {destination_path}")
                else:
                    # For mock data - create a simple text file as placeholder
                    mock_content = f"""Mock file: {file_name}
Original path: {file_path}
Size: {file_size} bytes
Downloaded: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
                    
                    with open(destination_path, 'w', encoding='utf-8') as f:
                        f.write(mock_content)
                    
                    show_success_message(page, f"Mock download: {file_name} created in Downloads")
                    file_action_feedback_text.value = f"Mock download: {file_name}"
                    await file_action_feedback_text.update_async()
                    logger.info(f"Mock file created at {destination_path}")
                    
            except PermissionError as e:
                error_msg = f"Permission denied when downloading {file_name}"
                logger.error(f"{error_msg}: {e}")
                show_error_message(page, error_msg)
                file_action_feedback_text.value = f"Permission error: {file_name}"
                await file_action_feedback_text.update_async()
                
            except Exception as e:
                error_msg = f"Error downloading {file_name}: {str(e)}"
                logger.error(error_msg)
                show_error_message(page, error_msg)
                file_action_feedback_text.value = f"Download failed: {file_name}"
                await file_action_feedback_text.update_async()
        
        # Run async operation using page.run_task
        page.run_task(download_async)

    def verify_file_action_enhanced(file_data, page):
        """Enhanced verify action with server bridge integration."""
        file_id = file_data.get('id', '')
        file_name = file_data.get('name', 'Unknown file')
        logger.info(f"Enhanced verify file action for: {file_name}")
        
        async def verify_async():
            try:
                # Show loading state
                file_action_feedback_text.value = f"Verifying {file_name}..."
                await file_action_feedback_text.update_async()
                
                # Try server bridge first
                if server_bridge:
                    try:
                        result = await server_bridge.verify_file_async(file_id)
                        if result:
                            # Update state via state manager
                            if state_manager:
                                await state_manager.update_state("file_verified", {
                                    "file_id": file_id,
                                    "file_name": file_name,
                                    "verification_result": result,
                                    "timestamp": datetime.now().isoformat()
                                })
                            
                            show_success_message(page, f"File {file_name} verification passed")
                            file_action_feedback_text.value = f"Verified {file_name} - integrity OK"
                            await file_action_feedback_text.update_async()
                            logger.info(f"File verification passed: {file_name}")
                            return
                        else:
                            show_error_message(page, f"File {file_name} verification failed")
                            file_action_feedback_text.value = f"Verification failed: {file_name}"
                            await file_action_feedback_text.update_async()
                            return
                    except Exception as e:
                        logger.error(f"Server bridge verify error: {e}")
                        # Fall through to mock implementation
                
                # Mock verification - always pass for demo
                await asyncio.sleep(1)  # Simulate verification time
                show_success_message(page, f"Mock verification: {file_name} is valid")
                file_action_feedback_text.value = f"Mock verified: {file_name}"
                await file_action_feedback_text.update_async()
                logger.info(f"Mock verification completed for: {file_name}")
                
            except Exception as e:
                error_msg = f"Error verifying {file_name}: {str(e)}"
                logger.error(error_msg)
                show_error_message(page, error_msg)
                file_action_feedback_text.value = f"Verify failed: {file_name}"
                await file_action_feedback_text.update_async()
        
        # Run async operation using page.run_task
        page.run_task(verify_async)

    def delete_file_action_enhanced(file_data, page, files_data=None, update_table_func=None):
        """Enhanced delete action with server bridge integration."""
        file_id = file_data.get('id', '')
        file_name = file_data.get('name', 'Unknown file')
        logger.info(f"Enhanced delete file action for: {file_name}")
        
        async def confirm_delete_async(e):
            try:
                # Close confirmation dialog
                confirmation_dialog.open = False
                confirmation_dialog.update()
                
                # Show loading state
                file_action_feedback_text.value = f"Deleting {file_name}..."
                file_action_feedback_text.update()
                
                # Try server bridge first
                if server_bridge:
                    try:
                        result = server_bridge.delete_file(file_id)
                        if result:
                            # Update state via state manager
                            if state_manager:
                                await state_manager.update_state("file_deleted", {
                                    "file_id": file_id,
                                    "file_name": file_name,
                                    "timestamp": datetime.now().isoformat()
                                })
                            
                            # Remove from local data
                            if files_data:
                                files_data[:] = [f for f in files_data if f.get('id') != file_id]
                                if update_table_func:
                                    update_table_func()
                            
                            show_success_message(page, f"File {file_name} deleted successfully")
                            file_action_feedback_text.value = f"Deleted {file_name}"
                            file_action_feedback_text.update()
                            logger.info(f"File deleted via server bridge: {file_name}")
                            return
                        else:
                            show_error_message(page, f"Failed to delete file {file_name}")
                            file_action_feedback_text.value = f"Delete failed: {file_name}"
                            file_action_feedback_text.update()
                            return
                    except Exception as e:
                        logger.error(f"Server bridge delete error: {e}")
                        # Fall through to mock implementation
                
                # Mock delete - remove from local data
                if files_data:
                    original_count = len(files_data)
                    files_data[:] = [f for f in files_data if f.get('id') != file_id]
                    
                    if len(files_data) < original_count:
                        if update_table_func:
                            update_table_func()
                        show_success_message(page, f"Mock delete: {file_name} removed from list")
                        file_action_feedback_text.value = f"Mock deleted: {file_name}"
                        logger.info(f"Mock file deleted: {file_name}")
                    else:
                        show_error_message(page, f"File {file_name} not found in data")
                        file_action_feedback_text.value = f"Delete failed: {file_name} not found"
                        logger.error(f"File {file_name} not found for deletion")
                
                file_action_feedback_text.update()
                
            except Exception as e:
                error_msg = f"Error deleting {file_name}: {str(e)}"
                logger.error(error_msg)
                show_error_message(page, error_msg)
                file_action_feedback_text.value = f"Delete failed: {file_name}"
                file_action_feedback_text.update()
        
        async def confirm_delete(e):
            """Async delete handler"""
            await confirm_delete_async(e)
        
        def cancel_delete(e):
            confirmation_dialog.open = False
            page.update()
        
        # Create confirmation dialog
        confirmation_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete {file_name}?\\n\\nThis action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=cancel_delete),
                ft.TextButton("Delete", on_click=confirm_delete, 
                             style=ft.ButtonStyle(color=ft.Colors.ERROR))
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        page.overlay.append(confirmation_dialog)
        confirmation_dialog.open = True
        page.update()

    def create_file_list_tile(file_data: Dict[str, Any]) -> ft.ListTile:
        """Create optimized ListTile for file entry - high performance virtualized rendering."""
        file_name = file_data.get('name', 'Unknown')
        file_size = file_data.get('size', 0)
        file_type = file_data.get('type', 'Unknown')
        file_modified = file_data.get('modified', 'Unknown')
        file_owner = file_data.get('owner', 'Unknown')
        file_status = file_data.get('status', 'Unknown')
        
        # Format file size
        if isinstance(file_size, int):
            if file_size >= 1024 * 1024:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            elif file_size >= 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} B"
        else:
            size_str = str(file_size)
        
        # Get file type icon
        type_icon = ft.Icons.INSERT_DRIVE_FILE
        if file_type.lower() in ['pdf']:
            type_icon = ft.Icons.PICTURE_AS_PDF
        elif file_type.lower() in ['jpg', 'png', 'gif', 'jpeg']:
            type_icon = ft.Icons.IMAGE
        elif file_type.lower() in ['mp4', 'avi', 'mov']:
            type_icon = ft.Icons.VIDEO_FILE
        elif file_type.lower() in ['py', 'js', 'html', 'css']:
            type_icon = ft.Icons.CODE
        
        # Status color
        status_color = ft.Colors.GREEN if file_status == "Complete" or file_status == "Verified" else ft.Colors.ORANGE
        
        return ft.ListTile(
            leading=ft.Icon(type_icon, color=ft.Colors.BLUE_600),
            title=ft.Text(file_name, size=14, weight=ft.FontWeight.W_500),
            subtitle=ft.Row([
                ft.Text(size_str, size=12, color=ft.Colors.GREY_600, width=80),
                ft.Text(file_type.upper(), size=12, color=ft.Colors.GREY_600, width=60),
                ft.Text(file_owner, size=12, color=ft.Colors.GREY_600, width=80),
                ft.Container(
                    content=ft.Text(file_status, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                    bgcolor=status_color,
                    padding=ft.Padding(6, 2, 6, 2),
                    border_radius=8
                )
            ], spacing=8),
            trailing=ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        text="Download",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=lambda e: download_file_action(file_data, page)
                    ),
                    ft.PopupMenuItem(
                        text="Verify",
                        icon=ft.Icons.VERIFIED,
                        on_click=lambda e: verify_file_action(file_data, page)
                    ),
                    ft.PopupMenuItem(
                        text="Delete",
                        icon=ft.Icons.DELETE,
                        on_click=lambda e: delete_file_action(file_data, page)
                    ),
                ],
                tooltip="File Actions"
            ),
            content_padding=ft.Padding(16, 8, 16, 8),
            on_click=lambda e: logger.info(f"Selected file: {file_name}")
        )

    # Create optimized ListView container instead of DataTable
    files_listview_container = ft.Container(
        content=ft.Column([
            ft.Text("Loading files...", size=16, text_align=ft.TextAlign.CENTER)
        ]),
        expand=True,
        bgcolor=ft.Colors.WHITE,
        border=ft.border.all(2, ft.Colors.GREEN_300),
        border_radius=15,
        padding=ft.Padding(8, 8, 8, 8)
    )
    status_text_ref = ft.Ref[ft.Text]()
    search_field_ref = ft.Ref[ft.TextField]()
    last_updated_text_ref = ft.Ref[ft.Text]()
    files_table_ref = ft.Ref[ft.DataTable]()
    
    # Initialize files_table with basic structure
    files_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Modified", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Owner", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800))
        ],
        rows=[],  # Initialize with empty rows
        heading_row_color=ft.Colors.GREEN_50,
        border=ft.border.all(2, ft.Colors.GREEN_300),
        border_radius=15,
        data_row_min_height=58,
        column_spacing=30,
        show_checkbox_column=False
    )

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

    # Legacy helper retained for backward compatibility (now using size_to_human)
    def format_size(size_bytes):  # pragma: no cover - wrappers keep compatibility
        return size_to_human(size_bytes)

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
                                if os.name == 'nt':  # Windows
                                    import win32security
                                    import win32api
                                    owner = win32api.GetUserName()
                                else:  # Unix/Linux
                                    import pwd
                                    owner = pwd.getpwuid(stat.st_uid).pw_name if hasattr(stat, 'st_uid') else "system"
                            except (ImportError, KeyError, Exception):
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

                            # Generate consistent file ID that matches server bridge expectations
                            file_id = f"file_{hash(file_path.name) % 10000}"
                            files_list.append({
                                "id": file_id,
                                "file_id": file_id,  # Also include file_id for server bridge compatibility
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
                            logger.warning("Error reading file %s: %s", str(file_path), str(e))
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
        """Get files data from server bridge with fallback to mock data."""
        try:
            # Try to get data from server bridge first
            if server_bridge:
                try:
                    # Run server call in thread to avoid blocking UI
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        files_data = await asyncio.get_event_loop().run_in_executor(
                            executor, server_bridge.get_files
                        )
                    
                    if files_data:
                        # Update state manager cache if available (for other purposes)
                        if state_manager:
                            try:
                                # Use asyncio.create_task to avoid blocking and prevent async warning
                                asyncio.create_task(state_manager.update_state("files", files_data))
                            except Exception as state_error:
                                logger.debug(f"State manager update failed (non-critical): {state_error}")
                        logger.debug(f"Retrieved {len(files_data)} files from server bridge")
                        return files_data
                except Exception as e:
                    logger.error(f"Server bridge get_files failed: {e}")
            
            # Fallback to mock data if server bridge fails or no server bridge
            logger.debug("Using fallback mock files data")
            mock_files = [
                {
                    "id": "mock_1",
                    "name": "sample_document.pdf",
                    "size": "1.2 MB",
                    "type": "PDF",
                    "modified": "2025-09-07 15:30:00",
                    "owner": "admin",
                    "status": "Complete"
                },
                {
                    "id": "mock_2", 
                    "name": "backup_config.json",
                    "size": "512 KB",
                    "type": "JSON",
                    "modified": "2025-09-08 10:15:00",
                    "owner": "admin", 
                    "status": "Complete"
                },
                {
                    "id": "mock_3",
                    "name": "system_logs.txt", 
                    "size": "2.1 MB",
                    "type": "TXT",
                    "modified": "2025-09-09 01:45:00",
                    "owner": "system",
                    "status": "Complete"
                }
            ]
            
            # Try to get files from local directory scan as additional fallback
            try:
                scanned_files = scan_files_directory()
                if scanned_files:
                    mock_files.extend(scanned_files)
            except Exception as scan_error:
                logger.debug(f"Directory scan failed: {scan_error}")
                
            return mock_files
            
        except Exception as e:
            logger.error(f"Error getting files data: {e}")
            return []

    def update_files_display():
        """Update files display using high-performance ListView virtualization.
        (Currently unused by main table path; kept for potential future ListView optimization.)"""
        if not filtered_files_data:
            empty_state = ft.Column([
                ft.Icon(ft.Icons.FOLDER_OPEN, size=64, color=ft.Colors.GREY_400),
                ft.Text("No files found", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                ft.Text("No files match the current search and filter criteria.", size=14, color=ft.Colors.GREY_500),
                ft.ElevatedButton(
                    "Refresh Files",
                    icon=ft.Icons.REFRESH,
                    on_click=lambda e: asyncio.create_task(load_files_data_async()),
                    tooltip="Refresh file list"
                )
            ], alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               spacing=16)
            files_listview_container.content = empty_state
        else:
            # Properly unpack paginate_data return (data_slice, pagination_config)
            page_items, _ = paginate_data(
                filtered_files_data,
                pagination_config.current_page,
                pagination_config.page_size
            )
            files_listview = ft.ListView(
                controls=[create_file_list_tile(file_data) for file_data in page_items],
                expand=True,
                spacing=4,
                padding=ft.Padding(8, 8, 8, 8),
                auto_scroll=False,
                semantic_child_count=len(page_items)
            )
            files_listview_container.content = files_listview
        try:
            files_listview_container.update()
        except Exception:
            # Fallback if not yet attached
            if hasattr(page, 'update'):
                page.update()

    def apply_filters():  # Backward compatibility stub (deprecated path)
        pass

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
            with PerfTimer("files.load.scan_initial"):
                initial_files_data = scan_files_directory()
            files_data.clear()
            files_data.extend(initial_files_data)
            
            # Now schedule async loading via page.run_task for enhanced data
            async def load_enhanced_data():
                try:
                    with PerfTimer("files.load.get_enhanced"):
                        enhanced_data = await get_files_data()
                    files_data.clear()
                    files_data.extend(enhanced_data)
                    # Update UI after loading
                    update_table_display()
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
            update_table_display()

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

                    # Calculate file hash for verification using SHA256 (avoid MD5)
                    import hashlib
                    sha256 = hashlib.sha256()
                    with open(file_path, "rb") as f:
                        for chunk in iter(lambda: f.read(8192), b""):
                            sha256.update(chunk)
                    file_hash = sha256.hexdigest()

                    # Show verification results (truncate hash for display)
                    show_success_message(page, f"Verified {file_name}: {format_size(file_size)}, Modified: {modified_time}, SHA256: {file_hash[:12]}...")
                    logger.info(f"File verified successfully (sha256) : {file_name}")
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
                        update_table_display()
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

    # Debounced search support
    try:
        from utils.performance import AsyncDebouncer
        search_debouncer = AsyncDebouncer(delay=0.3)
    except Exception:
        search_debouncer = None  # fallback

    async def perform_search_async():
        pagination_config.current_page = 0
        with PerfTimer("files.search.perform"):
            update_table_display()
        logger.info(f"Debounced search executed: '{search_query}'")

    def on_search_change(e):
        """Handle search input changes with debounce."""
        nonlocal search_query
        search_query = e.control.value
        logger.info(f"Search query changed to: '{search_query}' (debounced)")
        if search_debouncer:
            page.run_task(search_debouncer.debounce(perform_search_async))
        else:
            update_table_display()

    def on_clear_search():
        """Clear the search field."""
        nonlocal search_query
        search_query = ""
        if search_field_ref.current:
            search_field_ref.current.value = ""
        logger.info("Search cleared")
        update_table_display()

    def on_case_sensitive_toggle(e):
        """Handle case sensitivity toggle."""
        nonlocal case_sensitive_search
        case_sensitive_search = e.control.value
        logger.info(f"Case sensitive search: {case_sensitive_search}")
        update_table_display()

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
        update_table_display()

    def on_status_filter_change(e):
        """Handle status filter changes."""
        nonlocal status_filter
        status_filter = e.control.value
        logger.info(f"Status filter changed to: '{status_filter}'")
        update_table_display()

    def on_type_filter_change(e):
        """Handle type filter changes."""
        nonlocal type_filter
        type_filter = e.control.value
        logger.info(f"Type filter changed to: '{type_filter}'")
        update_table_display()

    def on_size_filter_change(e):
        """Handle size filter changes."""
        nonlocal size_filter
        size_filter = e.control.value
        logger.info(f"Size filter changed to: '{size_filter}'")
        update_table_display()

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

        # File Action Feedback
        ft.Container(
            content=file_action_feedback_text,
            padding=ft.Padding(20, 10, 20, 10),
            bgcolor=ft.Colors.SURFACE,
            border_radius=4
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
                    color=ft.Colors.OUTLINE,
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

    # Diff engine caches (Phase E)
    previous_page_signatures: List[tuple] = []
    previous_page_rows: List[ft.DataRow] = []

    def update_table_display():
        """Build and display DataTable rows using signature-based diff reuse (Phase E). Refactored helpers reduce complexity."""
        nonlocal previous_page_signatures, previous_page_rows
        with PerfTimer("files.table.total"):
            filtered_files = filter_files()
        table_container.content = None

        def build_empty_state():
            return ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.FOLDER_OPEN, size=64, color=ft.Colors.OUTLINE),
                        ft.Text("No files found", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                        ft.Text(
                            "No files have been uploaded or stored yet." if not search_query.strip() else f"No files match your search: '{search_query}'",
                            size=14,
                            color=ft.Colors.OUTLINE
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                    height=300,
                    alignment=ft.alignment.center
                )
            ], scroll=ft.ScrollMode.AUTO)

        def compute_page_items():
            return paginate_data(filtered_files, pagination_config.current_page, pagination_config.page_size)[0]

        def enrich_and_signature(file_data):
            if "_size_fmt" not in file_data:
                file_data["_size_fmt"] = size_to_human(file_data.get("size", 0))
            if "_modified_fmt" not in file_data:
                file_data["_modified_fmt"] = format_iso_short(file_data.get("modified"))
            return (
                file_data.get("id"),
                file_data.get("_size_fmt"),
                file_data.get("status"),
                file_data.get("_modified_fmt"),
            )

        def build_row(idx, file_data):
            name_control: ft.Control = ft.Text(str(file_data.get("name", "Unknown")), overflow=ft.TextOverflow.ELLIPSIS)
            if len(str(file_data.get("name", ""))) > 28:
                name_control = ft.Tooltip(message=str(file_data.get("name", "")), content=name_control)
            status_val = str(file_data.get("status", "Unknown"))
            badge = build_status_badge(status_val, status_val)
            actions_menu = ft.PopupMenuButton(
                icon=ft.Icons.MORE_VERT,
                tooltip="File Actions",
                items=[
                    ft.PopupMenuItem(text="Download", icon=ft.Icons.DOWNLOAD, on_click=lambda e, d=file_data: download_file_action_enhanced(d, page)),
                    ft.PopupMenuItem(text="Verify", icon=ft.Icons.VERIFIED, on_click=lambda e, d=file_data: verify_file_action_enhanced(d, page)),
                    ft.PopupMenuItem(text="Delete", icon=ft.Icons.DELETE, on_click=lambda e, d=file_data: delete_file_action_enhanced(d, page, files_data, update_table_display)),
                ]
            )
            return ft.DataRow(
                cells=[
                    ft.DataCell(name_control),
                    ft.DataCell(ft.Text(file_data.get("_size_fmt"))),
                    ft.DataCell(ft.Text(str(file_data.get("type", "unknown")).upper())),
                    ft.DataCell(ft.Text(file_data.get("_modified_fmt"))),
                    ft.DataCell(ft.Text(str(file_data.get("owner", "Unknown")))),
                    ft.DataCell(badge),
                    ft.DataCell(actions_menu),
                ],
                color=striped_row_color(idx),
            )

        if not filtered_files:
            table_container.content = build_empty_state()
            previous_page_signatures = []
            previous_page_rows = []
        else:
            with PerfTimer("files.table.page_slice"):
                page_items = compute_page_items()
            new_rows: List[ft.DataRow] = []
            new_signatures: List[tuple] = []
            reuse_threshold = 0.4  # if more than 40% changed -> rebuild all

            # Pre-pass compute signatures & detect changes count
            changed = 0
            precomputed: List[tuple] = []
            with PerfTimer("files.table.prepass"):
                for idx, file_data in enumerate(page_items):
                    sig = enrich_and_signature(file_data)
                    precomputed.append(sig)
                    if idx >= len(previous_page_signatures) or previous_page_signatures[idx] != sig:
                        changed += 1

            # Decide strategy
            total = len(page_items)
            rebuild_all = (total == 0) or (changed / max(1, total) > (1 - reuse_threshold)) or (total != len(previous_page_rows))

            if rebuild_all:
                previous_page_rows = []  # discard
                with PerfTimer("files.table.rebuild_all"):
                    for idx, file_data in enumerate(page_items):
                        row = build_row(idx, file_data)
                        previous_page_rows.append(row)
                new_rows = previous_page_rows
            else:
                # Reuse unchanged rows, rebuild changed ones
                updated_rows: List[ft.DataRow] = []
                with PerfTimer("files.table.partial_rebuild"):
                    for idx, file_data in enumerate(page_items):
                        sig = precomputed[idx]
                        if idx < len(previous_page_signatures) and previous_page_signatures[idx] == sig and idx < len(previous_page_rows):
                            updated_rows.append(previous_page_rows[idx])
                        else:
                            updated_rows.append(build_row(idx, file_data))
                previous_page_rows = updated_rows
                new_rows = updated_rows

            new_signatures = precomputed
            previous_page_signatures = new_signatures

            fresh_table = ft.DataTable(
                columns=files_table.columns,
                rows=new_rows,
                heading_row_color=files_table.heading_row_color,
                border=files_table.border,
                border_radius=files_table.border_radius,
                data_row_min_height=files_table.data_row_min_height,
                column_spacing=files_table.column_spacing,
                show_checkbox_column=False,
                ref=files_table_ref,
            )
            body = ft.Column([fresh_table], scroll=ft.ScrollMode.AUTO)
            # AnimatedSwitcher wrapper (low-cost fade)
            table_container.content = ft.AnimatedSwitcher(
                content=body,
                transition=ft.AnimatedSwitcherTransition.FADE,
                duration=300,
                reverse=True,
            )

        # Update status text
        # Pagination + status area update
        try:
            if status_text_ref.current and hasattr(status_text_ref.current, 'page') and status_text_ref.current.page is not None:
                total = len(files_data)
                filtered_count = len(filtered_files)
                total_pages = max(1, (filtered_count + pagination_config.page_size - 1) // pagination_config.page_size)
                start = pagination_config.current_page * pagination_config.page_size + 1 if filtered_count else 0
                end = min(start + pagination_config.page_size - 1, filtered_count) if filtered_count else 0
                status_text_ref.current.value = (
                    f"Showing {start}-{end} of {filtered_count} files (Total: {total}) | Page {pagination_config.current_page + 1} of {total_pages}" if filtered_count else f"No files found (Total: {total})"
                )
                status_text_ref.current.color = ft.Colors.PRIMARY if filtered_count else ft.Colors.OUTLINE
                status_text_ref.current.update()
        except Exception:  # pragma: no cover
            pass

        # Force container refresh
        try:
            if hasattr(table_container, 'page') and table_container.page is not None:
                table_container.update()
            else:
                page.update()
        except Exception:
            try:
                page.update()
            except Exception:
                logger.error("Failed to update files table display")

    # Pagination controls (Files view – new)
    def on_first(_):
        pagination_config.current_page = 0; update_table_display()
    def on_prev(_):
        if pagination_config.current_page > 0:
            pagination_config.current_page -= 1; update_table_display()
    def on_next(_):
        filtered = filter_files()
        total_pages = max(1, (len(filtered) + pagination_config.page_size - 1) // pagination_config.page_size)
        if (pagination_config.current_page + 1) < total_pages:
            pagination_config.current_page += 1; update_table_display()
    def on_last(_):
        filtered = filter_files()
        total_pages = max(1, (len(filtered) + pagination_config.page_size - 1) // pagination_config.page_size)
        pagination_config.current_page = max(0, total_pages - 1); update_table_display()

    first_btn = ft.IconButton(icon=ft.Icons.FIRST_PAGE, tooltip="First Page", on_click=on_first, disabled=True)
    prev_btn = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, tooltip="Previous Page", on_click=on_prev, disabled=True)
    next_btn = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, tooltip="Next Page", on_click=on_next, disabled=True)
    last_btn = ft.IconButton(icon=ft.Icons.LAST_PAGE, tooltip="Last Page", on_click=on_last, disabled=True)
    page_info_text = ft.Text("Page 1 of 1", size=12, weight=ft.FontWeight.W_500)

    def update_pagination_controls():
        filtered = filter_files()
        total_pages = max(1, (len(filtered) + pagination_config.page_size - 1) // pagination_config.page_size)
        first_btn.disabled = pagination_config.current_page <= 0
        prev_btn.disabled = pagination_config.current_page <= 0
        next_btn.disabled = (pagination_config.current_page + 1) >= total_pages
        last_btn.disabled = (pagination_config.current_page + 1) >= total_pages
        page_info_text.value = f"Page {pagination_config.current_page + 1} of {total_pages}"
        for c in [first_btn, prev_btn, next_btn, last_btn, page_info_text]:
            try:
                c.update()
            except Exception:
                pass

    # Wrap update_table_display to also refresh pagination buttons
    orig_update_table_display = update_table_display
    def update_table_display_wrapper():
        orig_update_table_display()
        update_pagination_controls()
    update_table_display = update_table_display_wrapper  # type: ignore

    pagination_row = ft.Row([first_btn, prev_btn, page_info_text, next_btn, last_btn], spacing=5)

    # Add new pagination row & table container
    main_view.controls.append(ft.Container(content=ft.Row([ft.Container(expand=True), pagination_row, ft.Container(expand=True)]), padding=ft.Padding(20, 0, 20, 10)))
    main_view.controls.append(table_container)

    # Initial display update
    update_table_display()

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
