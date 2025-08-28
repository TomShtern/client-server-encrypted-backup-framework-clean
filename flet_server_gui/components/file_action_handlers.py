#!/usr/bin/env python3
"""
File Action Handlers Component
Handles all file-related actions including download, verify, delete, and bulk operations.
"""

import flet as ft
import asyncio
import os
from typing import List, Dict, Any, Optional, Callable
from ..utils.server_bridge import ServerBridge
from ..actions import FileActions


class FileActionHandlers:
    """Handles all file-related actions and operations"""
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, toast_manager, page: ft.Page):
        self.server_bridge = server_bridge
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.page = page
        
        # Initialize file actions
        self.file_actions = FileActions(server_bridge)
        
        # Callbacks for parent component
        self.on_data_changed: Optional[Callable] = None
    
    def set_data_changed_callback(self, callback: Callable):
        """Set callback for when data changes and refresh is needed"""
        self.on_data_changed = callback
    
    async def _show_confirmation_dialog(self, title: str, message: str, 
                                 on_confirm: Callable, on_cancel: Callable = None):
        """Show confirmation dialog with standard styling"""
        if self.dialog_system:
            confirmed = await self.dialog_system.show_confirmation_async(
                title=title,
                message=message
            )
            if confirmed:
                # Handle both sync and async callbacks
                if asyncio.iscoroutinefunction(on_confirm):
                    await on_confirm()
                else:
                    on_confirm()
            elif on_cancel:
                # Handle both sync and async callbacks
                if asyncio.iscoroutinefunction(on_cancel):
                    await on_cancel()
                else:
                    on_cancel()
            else:
                self._close_dialog()
        else:
            # Fallback behavior - handle both sync and async callbacks
            if asyncio.iscoroutinefunction(on_confirm):
                await on_confirm()
            else:
                on_confirm()
    
    async def download_file(self, filename: str, destination_path: str = None) -> bool:
        """Download a single file"""
        try:
            # Use default download path if none specified
            if not destination_path:
                destination_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            
            # Show progress dialog
            progress_dialog = self._create_progress_dialog("Downloading File", f"Downloading {filename}...")
            self.dialog_system.show_custom_dialog(
                title="Download Progress",
                content=progress_dialog,
                actions=[]
            )
            
            # Execute download
            success = await self.file_actions.download_file(filename, destination_path)
            
            # Close progress dialog
            self._close_dialog()
            
            if success:
                self.toast_manager.show_success(f"File '{filename}' downloaded successfully to {destination_path}")
                return True
            else:
                self.toast_manager.show_error(f"Failed to download file '{filename}'")
                return False
                
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Error downloading file: {str(e)}")
            return False
    
    async def verify_file(self, filename: str) -> bool:
        """Verify file integrity"""
        try:
            # Show verification dialog
            self.dialog_system.show_info_dialog(
                title="Verifying File",
                message=f"Verifying integrity of '{filename}'...",
            )
            
            # Execute verification
            verification_result = await self.file_actions.verify_file(filename)
            
            # Close dialog
            self._close_dialog()
            
            if verification_result.get('valid', False):
                self.toast_manager.show_success(f"File '{filename}' verification successful")
                return True
            else:
                error_msg = verification_result.get('error', 'Unknown verification error')
                self.toast_manager.show_error(f"File '{filename}' verification failed: {error_msg}")
                return False
                
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Error verifying file: {str(e)}")
            return False
    
    async def preview_file(self, filename: str) -> None:
        """Preview file content using FilePreviewManager"""
        try:
            # Show loading indicator
            self.dialog_system.show_info_dialog(
                title="Loading Preview",
                message=f"Loading preview for '{filename}'...",
            )
            
            # Get file content through FileActions
            result = await self.file_actions.get_file_content(filename)
            
            # Close loading dialog
            self._close_dialog()
            
            if result.success:
                # Show preview using FilePreviewManager
                if hasattr(self, 'parent_view') and hasattr(self.parent_view, 'preview_manager'):
                    # If we have access to the preview manager through parent view
                    await self.parent_view.preview_manager.show_file_preview(filename)
                elif hasattr(self, 'preview_manager'):
                    # If preview manager is directly available
                    await self.preview_manager.show_file_preview(filename)
                else:
                    # Fallback: show content in a simple dialog
                    file_content = result.data
                    self.dialog_system.show_info_dialog(
                        title=f"Preview: {filename}",
                        message=file_content[:1000] + "..." if len(file_content) > 1000 else file_content
                    )
            else:
                self.toast_manager.show_error(f"Failed to load preview for '{filename}': {result.error_message}")
                
        except Exception as e:
            self._close_dialog()
            self.toast_manager.show_error(f"Error previewing file: {str(e)}")
    
    async def delete_file(self, filename: str) -> None:
        """Delete a file with confirmation"""
        def confirm_delete():
            self._close_dialog()
            asyncio.create_task(self._perform_delete(filename))
        
        # Show confirmation dialog
        await self._show_confirmation_dialog(
            title="⚠️ Confirm Delete",
            message=f"Are you sure you want to permanently delete '{filename}'? This action cannot be undone.",
            on_confirm=confirm_delete,
            on_cancel=lambda: self._close_dialog()
        )
    
    async def _perform_delete(self, filename: str) -> None:
        """Actually perform the file deletion"""
        try:
            # Execute delete via file actions
            success = await self.file_actions.delete_file(filename)
            
            if success:
                self.toast_manager.show_success(f"File '{filename}' deleted successfully")
                if self.on_data_changed:
                    await self.on_data_changed()
            else:
                self.toast_manager.show_error(f"Failed to delete file '{filename}'")
                
        except Exception as e:
            self.toast_manager.show_error(f"Error deleting file: {str(e)}")
    
    async def view_file_details(self, filename: str) -> None:
        """View detailed information about a file"""
        try:
            # Get file details from server
            file_details = await self._get_file_details(filename)
            
            if not file_details:
                self.toast_manager.show_error(f"Could not retrieve details for file: {filename}")
                return
            
            # Create detailed view content
            details_content = self._create_file_details_content(file_details)
            
            # Show details dialog
            self.dialog_system.show_custom_dialog(
                title=f"File Details: {filename}",
                content=details_content,
                actions=[
                    ft.TextButton("Download", on_click=lambda e: asyncio.create_task(self._download_from_dialog(filename))),
                    ft.TextButton("Close", on_click=lambda e: self._close_dialog())
                ]
            )
            
        except Exception as e:
            self.toast_manager.show_error(f"Error viewing file details: {str(e)}")
    
    async def _download_from_dialog(self, filename: str) -> None:
        """Download file from details dialog"""
        self._close_dialog()
        await self.download_file(filename)
    
    async def show_file_statistics(self, filename: str) -> None:
        """Show detailed statistics for a file"""
        try:
            # Get file statistics
            stats = await self._get_file_statistics(filename)
            
            if not stats:
                self.toast_manager.show_error(f"Could not retrieve statistics for file: {filename}")
                return
            
            # Create statistics content
            stats_content = self._create_file_stats_content(stats)
            
            # Show statistics dialog
            self.dialog_system.show_custom_dialog(
                title=f"Statistics for File: {filename}",
                content=stats_content,
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self._close_dialog())
                ]
            )
            
        except Exception as e:
            self.toast_manager.show_error(f"Error showing file statistics: {str(e)}")
    
    async def perform_bulk_action(self, action: str, filenames: List[str]) -> None:
        """Perform bulk action on multiple files"""
        if not filenames:
            self.toast_manager.show_warning("No files selected")
            return
        
        action_map = {
            "download": self._bulk_download,
            "verify": self._bulk_verify,
            "delete": self._bulk_delete,
        }
        
        if action in action_map:
            await action_map[action](filenames)
        else:
            self.toast_manager.show_error(f"Unknown bulk action: {action}")
    
    async def _bulk_download(self, filenames: List[str]) -> None:
        """Download multiple files"""
        def confirm_bulk_download():
            self._close_dialog()
            asyncio.create_task(self._perform_bulk_download(filenames))
        
        await self._show_confirmation_dialog(
            title="Confirm Bulk Download",
            message=f"Are you sure you want to download {len(filenames)} files to your Downloads folder?",
            on_confirm=confirm_bulk_download,
            on_cancel=lambda: self._close_dialog()
        )
    
    async def _perform_bulk_download(self, filenames: List[str]) -> None:
        """Actually perform bulk download"""
        success_count = 0
        download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        
        # Create progress dialog
        progress_content = ft.Column([
            ft.Text(f"Downloading {len(filenames)} files..."),
            ft.ProgressBar(),
            ft.Text("", key="progress_text")
        ])
        
        self.dialog_system.show_custom_dialog(
            title="Bulk Download Progress",
            content=progress_content,
            actions=[]
        )
        
        for i, filename in enumerate(filenames):
            try:
                # Update progress
                progress_text = progress_content.controls[2]
                progress_text.value = f"Downloading {filename} ({i+1}/{len(filenames)})"
                self.page.update()
                
                destination = os.path.join(download_path, filename)
                if await self.file_actions.download_file(filename, destination):
                    success_count += 1
                    
            except Exception:
                continue
        
        self._close_dialog()
        self.toast_manager.show_success(f"Downloaded {success_count}/{len(filenames)} files to {download_path}")
    
    async def _bulk_verify(self, filenames: List[str]) -> None:
        """Verify multiple files"""
        def confirm_bulk_verify():
            self._close_dialog()
            asyncio.create_task(self._perform_bulk_verify(filenames))
        
        await self._show_confirmation_dialog(
            title="Confirm Bulk Verification",
            message=f"Are you sure you want to verify {len(filenames)} files?",
            on_confirm=confirm_bulk_verify,
            on_cancel=lambda: self._close_dialog()
        )
    
    async def _perform_bulk_verify(self, filenames: List[str]) -> None:
        """Actually perform bulk verification"""
        success_count = 0
        
        # Create progress dialog
        progress_content = ft.Column([
            ft.Text(f"Verifying {len(filenames)} files..."),
            ft.ProgressBar(),
            ft.Text("", key="progress_text")
        ])
        
        self.dialog_system.show_custom_dialog(
            title="Bulk Verification Progress",
            content=progress_content,
            actions=[]
        )
        
        for i, filename in enumerate(filenames):
            try:
                # Update progress
                progress_text = progress_content.controls[2]
                progress_text.value = f"Verifying {filename} ({i+1}/{len(filenames)})"
                self.page.update()
                
                result = await self.file_actions.verify_file(filename)
                if result.get('valid', False):
                    success_count += 1
                    
            except Exception:
                continue
        
        self._close_dialog()
        self.toast_manager.show_success(f"Verified {success_count}/{len(filenames)} files successfully")
    
    async def _bulk_delete(self, filenames: List[str]) -> None:
        """Delete multiple files"""
        def confirm_bulk_delete():
            self._close_dialog()
            asyncio.create_task(self._perform_bulk_delete(filenames))
        
        await self._show_confirmation_dialog(
            title="⚠️ Confirm Bulk Delete",
            message=f"Are you sure you want to permanently delete {len(filenames)} files? This action cannot be undone.",
            on_confirm=confirm_bulk_delete,
            on_cancel=lambda: self._close_dialog()
        )
    
    async def _perform_bulk_delete(self, filenames: List[str]) -> None:
        """Actually perform bulk deletion"""
        success_count = 0
        for filename in filenames:
            try:
                if await self.file_actions.delete_file(filename):
                    success_count += 1
            except Exception:
                continue
        
        self.toast_manager.show_success(f"Deleted {success_count}/{len(filenames)} files")
        if self.on_data_changed:
            await self.on_data_changed()
    
    # Helper methods for data retrieval and UI creation
    
    async def _get_file_details(self, filename: str) -> Optional[Dict]:
        """Get detailed file information"""
        try:
            return await self.file_actions.get_file_details(filename)
        except Exception:
            return None
    
    async def _get_file_statistics(self, filename: str) -> Optional[Dict]:
        """Get file statistics"""
        try:
            return await self.file_actions.get_file_statistics(filename)
        except Exception:
            return None
    
    def _create_file_details_content(self, file_data: Dict) -> ft.Control:
        """Create file details display content"""
        details_text = []
        for key, value in file_data.items():
            details_text.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return ft.Column([
            ft.Text("\n".join(details_text), size=12)
        ], scroll=ft.ScrollMode.AUTO)
    
    def _create_file_stats_content(self, stats_data: Dict) -> ft.Control:
        """Create file statistics display content"""
        stats_text = []
        for key, value in stats_data.items():
            stats_text.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return ft.Column([
            ft.Text("\n".join(stats_text), size=12)
        ], scroll=ft.ScrollMode.AUTO)
    
    def _create_progress_dialog(self, title: str, message: str) -> ft.Control:
        """Create a progress dialog content"""
        return ft.Column([
            ft.Text(message),
            ft.ProgressBar(),
            ft.Text("Please wait...")
        ], spacing=10)
    
    def _close_dialog(self):
        """Close the current dialog"""
        if self.dialog_system and hasattr(self.dialog_system, 'current_dialog'):
            if self.dialog_system.current_dialog:
                self.dialog_system.current_dialog.open = False
                self.page.update()