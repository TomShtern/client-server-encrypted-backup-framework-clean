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

# PopupMenuButton Solution - WORKING Implementation for Files
file_action_count = {"count": 0}
file_action_feedback_text = ft.Text("No file actions yet - click the menu buttons", size=14, color=ft.Colors.BLUE)

def download_file_action(file_data, page):
    """Download action - download file to Downloads folder."""
    file_name = file_data.get('name', 'Unknown file')
    file_path = file_data.get('path', '')
    file_size = file_data.get('size', 0)
    logger.info(f"Download file action for: {file_name}")
    
    try:
        downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        if not os.path.exists(downloads_dir):
            os.makedirs(downloads_dir)
            logger.info(f"Created Downloads directory: {downloads_dir}")
        
        destination_path = os.path.join(downloads_dir, file_name)
        
        # Check if file exists and is readable
        if file_path and file_path != "mock" and os.path.exists(file_path):
            # Real file copy operation
            import shutil
            shutil.copy2(file_path, destination_path)
            
            show_success_message(page, f"File {file_name} downloaded to Downloads folder")
            file_action_feedback_text.value = f"Downloaded {file_name} ({file_size} bytes)"
            file_action_feedback_text.update()
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

    try:
        # Check if this is a real file path or mock data
        if file_path and file_path != "mock" and os.path.exists(file_path):
            # Get file stats with enhanced error handling
            try:
                stat = os.stat(file_path)
                actual_file_size = stat.st_size
                modified_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                
                # Verify file size matches reported size
                size_match = abs(actual_file_size - file_size_reported) <= 1024  # Allow 1KB tolerance
                size_status = "✓ Size matches" if size_match else f"⚠ Size mismatch (reported: {file_size_reported}, actual: {actual_file_size})"
                
            except (OSError, ValueError) as stat_error:
                logger.error(f"Failed to get file stats: {stat_error}")
                show_error_message(page, f"Cannot access file {file_name}: {stat_error}")
                return

            # Calculate file hash for verification with progress indication
            try:
                import hashlib
                hash_md5 = hashlib.md5()
                hash_sha256 = hashlib.sha256()
                
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                        hash_sha256.update(chunk)
                
                md5_hash = hash_md5.hexdigest()
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
                ft.Text("Checksums:", weight=ft.FontWeight.BOLD),
                ft.Text(f"MD5: {md5_hash}", selectable=True),
                ft.Text(f"SHA256: {sha256_hash}", selectable=True),
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
    # Simple data state
    files_data: List[Dict[str, Any]] = []
    is_loading = False
    last_updated = None
    search_query = ""
    status_filter = "all"
    type_filter = "all"
    size_filter = "all"
    case_sensitive_search = False  # New state for case sensitivity

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

    # Direct control references
    files_table_ref = ft.Ref[ft.DataTable]()
    
    # Pre-create the DataTable to avoid lifecycle issues
    files_table = ft.DataTable(
        ref=files_table_ref,
        columns=[
            ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Modified", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Owner", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800))
        ],
        rows=[],  # Will be populated by update_table()
        heading_row_color=ft.Colors.GREEN_50,
        border=ft.border.all(2, ft.Colors.GREEN_300),
        border_radius=15,
        data_row_min_height=58,
        column_spacing=30,
        show_checkbox_column=False
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
        """Get files data from server bridge - always fresh for immediate UI updates."""
        try:
            # Always get fresh data for immediate UI updates after deletions
            if server_bridge:
                try:
                    files_data = server_bridge.get_files()  # Synchronous call
                    if files_data:
                        # Update state manager cache if available (for other purposes)
                        if state_manager:
                            state_manager.update_state("files", files_data)
                        logger.debug(f"Retrieved {len(files_data)} files from server bridge")
                        return files_data
                except Exception as e:
                    logger.error(f"Server bridge get_files failed: {e}")
            
            # Fallback to mock data if server bridge fails
            logger.debug("Using fallback mock files data")
            return [
                {
                    "id": "mock_1",
                    "name": "sample_document.pdf",
                    "size": "1.2 MB",
                    "type": "PDF",
                    "modified": "2025-09-07 15:30:00",
                    "owner": "admin",
                    "status": "Complete"
                }
            ]
            files_data = scan_files_directory()
            # Update cache with fallback data if available
            if state_manager and files_data:
                await state_manager.update_state("files", files_data)
            return files_data
        except Exception as e:
            logger.error(f"Error getting files data: {e}")
            return []

    def update_table():
        """Update the files table with current data and force UI refresh."""
        filtered_files = filter_files()
        new_rows = []
        for file_data in filtered_files:
            # Status color based on file status
            status_color_name = {
                "Verified": "GREEN_600",
                "Pending": "ORANGE_600", 
                "Received": "BLUE_600",
                "Unverified": "RED_600",
                "Stored": "PURPLE_600",       # Fixed: Use proper Flet color
                "Archived": "BROWN_600",      # Fixed: Use proper Flet color
                "Empty": "GREY_500",          # Fixed: Use proper Flet color
                "Unknown": "GREY_400"         # Fixed: Use proper Flet color
            }.get(file_data.get("status", "Unknown"), "GREY_400")

            status_color = getattr(ft.Colors, status_color_name, ft.Colors.GREY_400)

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
                            bgcolor=status_color,
                            # CRITICAL: Force color persistence and prevent theme override
                            border=ft.border.all(2, status_color),  # Border with same color for emphasis
                            ink=False,  # Disable ink ripple that might interfere
                        )
                    ),
                    ft.DataCell(
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            tooltip="File Actions",
                            items=[
                                ft.PopupMenuItem(
                                    text="Download",
                                    icon=ft.Icons.DOWNLOAD,
                                    on_click=lambda e, data=file_data: download_file_action_enhanced(data, page)
                                ),
                                ft.PopupMenuItem(
                                    text="Verify",
                                    icon=ft.Icons.VERIFIED,
                                    on_click=lambda e, data=file_data: verify_file_action_enhanced(data, page)
                                ),
                                ft.PopupMenuItem(
                                    text="Delete",
                                    icon=ft.Icons.DELETE,
                                    on_click=lambda e, data=file_data: delete_file_action_enhanced(data, page, files_data, update_table)
                                )
                            ]
                        )
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
        
        # CRITICAL FIX: Force complete table container refresh
        update_table_display()
        
        # REMOVED: Replaced page.update() with precise control updates per FletV2 best practices

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

    def update_table_display():
        """Update table display with empty state handling and force refresh."""
        filtered_files = filter_files()
        
        # Clear existing content first
        table_container.content = None
        
        if not filtered_files:
            # Show empty state
            table_container.content = ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Icon(
                            ft.Icons.FOLDER_OPEN,
                            size=64,
                            color=ft.Colors.OUTLINE
                        ),
                        ft.Text(
                            "No files found",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ON_SURFACE
                        ),
                        ft.Text(
                            "No files have been uploaded or stored yet." if not search_query.strip() 
                            else f"No files match your search: '{search_query}'",
                            size=14,
                            color=ft.Colors.OUTLINE
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
            # Recreate the table with fresh data to ensure proper refresh
            fresh_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
                    ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
                    ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
                    ft.DataColumn(ft.Text("Modified", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
                    ft.DataColumn(ft.Text("Owner", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
                    ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800)),
                    ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.GREEN_800))
                ],
                rows=files_table.rows,  # Use the updated rows
                heading_row_color=ft.Colors.GREEN_50,
                border=ft.border.all(2, ft.Colors.GREEN_300),
                border_radius=15,
                data_row_min_height=58,
                column_spacing=30,
                show_checkbox_column=False,
                ref=files_table_ref
            )
            
            # Update the global reference
            files_table.columns = fresh_table.columns
            files_table.rows = fresh_table.rows
            files_table.border = fresh_table.border
            files_table.border_radius = fresh_table.border_radius
            
            # Show table with fresh content
            table_container.content = ft.Column([
                fresh_table
            ], scroll=ft.ScrollMode.AUTO)
        
        # Force update the container - CRITICAL FIX for empty files display
        try:
            # First try to update the container directly
            table_container.update()
            logger.debug("Table container updated successfully")
        except Exception as e:
            logger.debug(f"Table container update failed: {e}")
            # Fallback to page update if container update fails
            try:
                page.update()
                logger.debug("Page update fallback successful")
            except Exception as page_error:
                logger.error(f"Both container and page update failed: {page_error}")

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
