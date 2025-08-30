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
from ..utils.action_result import ActionResult
from ..utils.trace_center import get_trace_center
from ..services.confirmation_service import ConfirmationService


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
    
    async def download_file(self, filename: str, destination_path: str = None) -> ActionResult:
        """Download a single file (with progress dialog if available)."""
        trace = get_trace_center()
        cid = trace.new_correlation_id()
        try:
            if not destination_path:
                destination_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)
            if not self.dialog_system:
                success = await self.file_actions.download_file(filename, destination_path)
                if success:
                    if self.toast_manager:
                        self.toast_manager.show_success(f"Downloaded '{filename}'")
                    return ActionResult.make_success(
                        code="FILE_DOWNLOAD_OK",
                        message="File downloaded",
                        correlation_id=cid,
                        data={"filename": filename, "path": destination_path},
                        selection=[filename],
                    )
                if self.toast_manager:
                    self.toast_manager.show_error(f"Failed to download '{filename}'")
                return ActionResult.make_error(
                    code="FILE_DOWNLOAD_FAILED",
                    message="Download failed",
                    correlation_id=cid,
                    error_code="FAILED",
                    data={"filename": filename},
                    selection=[filename],
                )
            progress_dialog = self._create_progress_dialog("Downloading File", f"Downloading {filename}...")
            self.dialog_system.show_custom_dialog(
                title="Download Progress",
                content=progress_dialog,
                actions=[],
            )
            success = await self.file_actions.download_file(filename, destination_path)
            self._close_dialog()
            if success:
                if self.toast_manager:
                    self.toast_manager.show_success(f"File '{filename}' downloaded to {destination_path}")
                return ActionResult.make_success(
                    code="FILE_DOWNLOAD_OK",
                    message="File downloaded",
                    correlation_id=cid,
                    data={"filename": filename, "path": destination_path},
                    selection=[filename],
                )
            if self.toast_manager:
                self.toast_manager.show_error(f"Failed to download file '{filename}'")
            return ActionResult.make_error(
                code="FILE_DOWNLOAD_FAILED",
                message="Download failed",
                correlation_id=cid,
                error_code="FAILED",
                data={"filename": filename},
                selection=[filename],
            )
        except Exception as e:  # noqa: BLE001
            self._close_dialog()
            if self.toast_manager:
                self.toast_manager.show_error(f"Error downloading file: {e}")
            return ActionResult.make_error(
                code="FILE_DOWNLOAD_ERROR",
                message=str(e),
                correlation_id=cid,
                error_code="EXCEPTION",
                data={"filename": filename},
                selection=[filename],
            )
    
    async def verify_file(self, filename: str) -> ActionResult:
        """Verify file integrity."""
        trace = get_trace_center()
        cid = trace.new_correlation_id()
        try:
            if self.dialog_system:
                self.dialog_system.show_info_dialog(
                    title="Verifying File",
                    message=f"Verifying integrity of '{filename}'...",
                )
            verification_result = await self.file_actions.verify_file(filename)
            if self.dialog_system:
                self._close_dialog()
            valid = verification_result.get("valid", False)
            if valid:
                if self.toast_manager:
                    self.toast_manager.show_success(f"File '{filename}' verified")
                return ActionResult.make_success(
                    code="FILE_VERIFY_OK",
                    message="File verified",
                    correlation_id=cid,
                    data={"filename": filename, "details": verification_result},
                    selection=[filename],
                )
            error_msg = verification_result.get("error", "Verification failed")
            if self.toast_manager:
                self.toast_manager.show_error(f"File '{filename}' verification failed: {error_msg}")
            return ActionResult.make_error(
                code="FILE_VERIFY_FAILED",
                message=error_msg,
                correlation_id=cid,
                error_code="FAILED",
                data={"filename": filename, "details": verification_result},
                selection=[filename],
            )
        except Exception as e:  # noqa: BLE001
            if self.dialog_system:
                self._close_dialog()
            if self.toast_manager:
                self.toast_manager.show_error(f"Error verifying file: {e}")
            return ActionResult.make_error(
                code="FILE_VERIFY_ERROR",
                message=str(e),
                correlation_id=cid,
                error_code="EXCEPTION",
                data={"filename": filename},
                selection=[filename],
            )
    
    async def preview_file(self, filename: str = None, file_id: str = None) -> ActionResult:
        """Preview file content using FilePreviewManager."""
        trace = get_trace_center()
        cid = trace.new_correlation_id()
        target_file = filename or file_id
        if not target_file:
            return ActionResult.make_error(
                    code="FILE_PREVIEW_NO_TARGET",
                    message="No filename provided",
                    correlation_id=cid,
                    error_code="INVALID_INPUT",
                )
        if not self.dialog_system:
            return ActionResult.make_error(
                code="FILE_PREVIEW_NO_DIALOG",
                message="Dialog system required for preview",
                correlation_id=cid,
                error_code="UNAVAILABLE",
                selection=[target_file],
            )
        try:
            self.dialog_system.show_info_dialog(
                title="Loading Preview",
                message=f"Loading preview for '{target_file}'...",
            )
            result = await self.file_actions.get_file_content(target_file)
            self._close_dialog()
            if getattr(result, "success", False):
                content_displayed = False
                if hasattr(self, "parent_view") and hasattr(self.parent_view, "preview_manager"):
                    await self.parent_view.preview_manager.show_file_preview(target_file)
                    content_displayed = True
                elif hasattr(self, "preview_manager"):
                    await self.preview_manager.show_file_preview(target_file)
                    content_displayed = True
                else:
                    file_content = result.data
                    self.dialog_system.show_info_dialog(
                        title=f"Preview: {target_file}",
                        message=(file_content[:1000] + "..." if isinstance(file_content, str) and len(file_content) > 1000 else file_content),
                    )
                    content_displayed = True
                if self.toast_manager:
                    self.toast_manager.show_success(f"Preview loaded for '{target_file}'")
                return ActionResult.make_success(
                    code="FILE_PREVIEW_OK",
                    message="Preview shown" if content_displayed else "Preview fetched",
                    correlation_id=cid,
                    data={"filename": target_file},
                    selection=[target_file],
                )
            if self.toast_manager:
                self.toast_manager.show_error(f"Failed to load preview for '{target_file}'")
            return ActionResult.make_error(
                    code="FILE_PREVIEW_FAILED",
                    message="Preview load failed",
                    correlation_id=cid,
                    error_code="FAILED",
                    selection=[target_file],
                )
        except Exception as e:  # noqa: BLE001
            if self.dialog_system:
                self._close_dialog()
            if self.toast_manager:
                self.toast_manager.show_error(f"Error previewing file: {e}")
            return ActionResult.make_error(
                code="FILE_PREVIEW_ERROR",
                message=str(e),
                correlation_id=cid,
                error_code="EXCEPTION",
                selection=[target_file],
            )
    
    async def delete_file(self, filename: str) -> ActionResult:
        """Delete a file with confirmation."""
        trace = get_trace_center()
        cid = trace.new_correlation_id()
        confirmed = True
        if self.dialog_system:
            confirmed = await self.dialog_system.show_confirmation_async(
                title="⚠️ Confirm Delete",
                message=f"Delete '{filename}'? This cannot be undone.",
            )
        if not confirmed:
            return ActionResult.make_cancelled(
                code="FILE_DELETE_CANCELLED",
                message="User cancelled delete",
                correlation_id=cid,
                selection=[filename],
            )
        return await self._perform_delete(filename, correlation_id=cid)
    
    async def _perform_delete(self, filename: str, correlation_id: Optional[str] = None) -> ActionResult:
        """Actually perform the file deletion"""
        cid = correlation_id or get_trace_center().new_correlation_id()
        try:
            success = await self.file_actions.delete_file(filename)
            if success:
                if self.toast_manager:
                    self.toast_manager.show_success(f"File '{filename}' deleted")
                if self.on_data_changed:
                    await self.on_data_changed()
                return ActionResult.make_success(
                    code="FILE_DELETE_OK",
                    message="File deleted",
                    correlation_id=cid,
                    selection=[filename],
                )
            if self.toast_manager:
                self.toast_manager.show_error(f"Failed to delete file '{filename}'")
            return ActionResult.make_error(
                code="FILE_DELETE_FAILED",
                message="Delete failed",
                correlation_id=cid,
                error_code="FAILED",
                selection=[filename],
            )
        except Exception as e:  # noqa: BLE001
            if self.toast_manager:
                self.toast_manager.show_error(f"Error deleting file: {e}")
            return ActionResult.make_error(
                code="FILE_DELETE_ERROR",
                message=str(e),
                correlation_id=cid,
                error_code="EXCEPTION",
                selection=[filename],
            )
    
    async def view_file_details(self, filename: str = None, file_id: str = None) -> ActionResult:
        """View detailed information about a file."""
        trace = get_trace_center()
        cid = trace.new_correlation_id()
        target_file = filename or file_id
        if not target_file:
            return ActionResult.make_error(
                code="FILE_DETAILS_NO_TARGET",
                message="No filename provided",
                correlation_id=cid,
                error_code="INVALID_INPUT",
            )
        if not self.dialog_system:
            details = await self._get_file_details(target_file)
            if not details:
                if self.toast_manager:
                    self.toast_manager.show_error(f"No details for {target_file}")
                return ActionResult.make_error(
                    code="FILE_DETAILS_NOT_FOUND",
                    message="Details not found",
                    correlation_id=cid,
                    error_code="NOT_FOUND",
                    selection=[target_file],
                )
            if self.toast_manager:
                self.toast_manager.show_success(f"Details (console) for {target_file}")
            return ActionResult.make_info(
                code="FILE_DETAILS_FALLBACK",
                message="Details fetched (no dialog system)",
                correlation_id=cid,
                data={"details": details},
                selection=[target_file],
            )
        try:
            details = await self._get_file_details(target_file)
            if not details:
                if self.toast_manager:
                    self.toast_manager.show_error(f"No details for {target_file}")
                return ActionResult.make_error(
                    code="FILE_DETAILS_NOT_FOUND",
                    message="Details not found",
                    correlation_id=cid,
                    error_code="NOT_FOUND",
                    selection=[target_file],
                )
            details_content = self._create_file_details_content(details)
            self.dialog_system.show_custom_dialog(
                title=f"File Details: {target_file}",
                content=details_content,
                actions=[
                    ft.TextButton(
                        "Download",
                        on_click=lambda e: self._safe_async_task(self._download_from_dialog(target_file)),
                    ),
                    ft.TextButton("Close", on_click=lambda e: self._close_dialog()),
                ],
            )
            return ActionResult.make_success(
                code="FILE_DETAILS_OK",
                message="Details shown",
                correlation_id=cid,
                data={"details": details},
                selection=[target_file],
            )
        except Exception as e:  # noqa: BLE001
            if self.toast_manager:
                self.toast_manager.show_error(f"Error viewing file details: {e}")
            return ActionResult.make_error(
                code="FILE_DETAILS_ERROR",
                message=str(e),
                correlation_id=cid,
                error_code="EXCEPTION",
                selection=[target_file],
            )
    
    async def _download_from_dialog(self, filename: str) -> None:
        """Download file from details dialog"""
        self._close_dialog()
        await self.download_file(filename)
    
    async def show_file_statistics(self, filename: str) -> ActionResult:
        """Show detailed statistics for a file."""
        trace = get_trace_center()
        cid = trace.new_correlation_id()
        try:
            stats = await self._get_file_statistics(filename)
            if not stats:
                if self.toast_manager:
                    self.toast_manager.show_error(f"No statistics for {filename}")
                return ActionResult.make_error(
                    code="FILE_STATS_NOT_FOUND",
                    message="Statistics not found",
                    correlation_id=cid,
                    error_code="NOT_FOUND",
                    selection=[filename],
                )
            if self.dialog_system:
                stats_content = self._create_file_stats_content(stats)
                self.dialog_system.show_custom_dialog(
                    title=f"Statistics for File: {filename}",
                    content=stats_content,
                    actions=[ft.TextButton("Close", on_click=lambda e: self._close_dialog())],
                )
                return ActionResult.make_success(
                    code="FILE_STATS_OK",
                    message="Statistics shown",
                    correlation_id=cid,
                    data={"stats": stats},
                    selection=[filename],
                )
            if self.toast_manager:
                self.toast_manager.show_info(f"Statistics (fallback) for {filename}")
            return ActionResult.make_info(
                code="FILE_STATS_FALLBACK",
                message="Stats fetched (no dialog system)",
                correlation_id=cid,
                data={"stats": stats},
                selection=[filename],
            )
        except Exception as e:  # noqa: BLE001
            if self.toast_manager:
                self.toast_manager.show_error(f"Error showing file statistics: {e}")
            return ActionResult.make_error(
                code="FILE_STATS_ERROR",
                message=str(e),
                correlation_id=cid,
                error_code="EXCEPTION",
                selection=[filename],
            )
    
    async def perform_bulk_action(self, action: str, filenames: List[str]) -> ActionResult:
        """Perform bulk action on multiple files."""
        if not filenames:
            if self.toast_manager:
                self.toast_manager.show_warning("No files selected")
            return ActionResult.make_error(
                code="FILE_BULK_EMPTY",
                message="No files selected",
                error_code="NO_SELECTION",
            )
        action_map = {"download": self._bulk_download, "verify": self._bulk_verify, "delete": self._bulk_delete}
        if action not in action_map:
            if self.toast_manager:
                self.toast_manager.show_error(f"Unknown bulk action: {action}")
            return ActionResult.make_error(
                code="FILE_BULK_UNKNOWN",
                message="Unknown bulk action",
                error_code="UNKNOWN_ACTION",
                data={"action": action},
            )
        return await action_map[action](filenames)
    
    async def _bulk_download(self, filenames: List[str]) -> ActionResult:
        """Download multiple files (with confirmation)."""
        trace = get_trace_center()
        cid = trace.new_correlation_id()
        if not filenames:
            return ActionResult.make_error(
                code="FILE_BULK_DOWNLOAD_EMPTY",
                message="No files selected",
                error_code="NO_SELECTION",
            )
        confirmed = True
        if self.dialog_system:
            confirmed = await self.dialog_system.show_confirmation_async(
                title="Confirm Bulk Download",
                message=f"Download {len(filenames)} files to Downloads?",
            )
        if not confirmed:
            return ActionResult.make_cancelled(
                code="FILE_BULK_DOWNLOAD_CANCELLED",
                message="User cancelled bulk download",
                correlation_id=cid,
                selection=filenames,
            )
        return await self._perform_bulk_download(filenames, correlation_id=cid)
    
    async def _perform_bulk_download(self, filenames: List[str], correlation_id: Optional[str] = None) -> ActionResult:
        """Actually perform bulk download"""
        cid = correlation_id or get_trace_center().new_correlation_id()
        success_count = 0
        download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        if self.dialog_system:
            progress_content = ft.Column([
                ft.Text(f"Downloading {len(filenames)} files..."),
                ft.ProgressBar(),
                ft.Text("", key="progress_text"),
            ])
            self.dialog_system.show_custom_dialog(
                title="Bulk Download Progress",
                content=progress_content,
                actions=[],
            )
        for i, fname in enumerate(filenames):
            try:
                if self.dialog_system:
                    progress_text = progress_content.controls[2]
                    progress_text.value = f"Downloading {fname} ({i+1}/{len(filenames)})"
                    self.page.update()
                dest = os.path.join(download_path, fname)
                if await self.file_actions.download_file(fname, dest):
                    success_count += 1
            except Exception:  # noqa: BLE001
                continue
        if self.dialog_system:
            self._close_dialog()
        if self.toast_manager:
            self.toast_manager.show_success(f"Downloaded {success_count}/{len(filenames)} files")
        code = "FILE_BULK_DOWNLOAD_OK" if success_count == len(filenames) else "FILE_BULK_DOWNLOAD_PARTIAL"
        if success_count == len(filenames):
            return ActionResult.make_success(
                code=code,
                message="All files downloaded",
                correlation_id=cid,
                selection=filenames,
                data={"success": success_count, "total": len(filenames), "path": download_path},
            )
        return ActionResult.make_partial(
            code=code,
            message=f"{success_count}/{len(filenames)} downloaded",
            correlation_id=cid,
            selection=filenames,
            failed=[],
            data={"success": success_count, "total": len(filenames)}
        )
    
    async def _bulk_verify(self, filenames: List[str]) -> ActionResult:
        """Verify multiple files with confirmation and ActionResult."""
        trace = get_trace_center()
        cid = trace.new_correlation_id()
        if not filenames:
            return ActionResult.make_error(code="FILE_BULK_VERIFY_EMPTY", message="No files selected", error_code="NO_SELECTION")
        confirmed = True
        if self.dialog_system:
            cs = ConfirmationService(self.dialog_system)
            cresult = await cs.confirm(
                title="Confirm Bulk Verification",
                message=f"Verify integrity of {len(filenames)} files?",
                proceed_code="FILE_BULK_VERIFY_STARTED",
                proceed_message="Bulk verification started",
                cancel_message="Bulk verification cancelled"
            )
            if cresult.code == "CANCELLED":
                return ActionResult.make_cancelled(code="FILE_BULK_VERIFY_CANCELLED", message=cresult.message, correlation_id=cid, selection=filenames)
        success_count = 0
        if self.dialog_system:
            progress_content = ft.Column([
                ft.Text(f"Verifying {len(filenames)} files..."),
                ft.ProgressBar(),
                ft.Text("", key="progress_text")
            ])
            self.dialog_system.show_custom_dialog(title="Bulk Verification Progress", content=progress_content, actions=[])
        for i, filename in enumerate(filenames):
            try:
                if self.dialog_system:
                    progress_text = progress_content.controls[2]
                    progress_text.value = f"Verifying {filename} ({i+1}/{len(filenames)})"
                    self.page.update()
                result = await self.file_actions.verify_file(filename)
                if result.get('valid', False):
                    success_count += 1
            except Exception:
                continue
        if self.dialog_system:
            self._close_dialog()
        if self.toast_manager:
            self.toast_manager.show_success(f"Verified {success_count}/{len(filenames)} files")
        code = "FILE_BULK_VERIFY_OK" if success_count == len(filenames) else "FILE_BULK_VERIFY_PARTIAL"
        if success_count == len(filenames):
            return ActionResult.make_success(code=code, message="All files verified", correlation_id=cid, selection=filenames, data={"success": success_count, "total": len(filenames)})
        return ActionResult.make_partial(code=code, message=f"{success_count}/{len(filenames)} verified", correlation_id=cid, selection=filenames, failed=[], data={"success": success_count, "total": len(filenames)})
    
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
    
    async def _bulk_delete(self, filenames: List[str]) -> ActionResult:
        """Delete multiple files with confirmation and ActionResult."""
        trace = get_trace_center()
        cid = trace.new_correlation_id()
        if not filenames:
            return ActionResult.make_error(code="FILE_BULK_DELETE_EMPTY", message="No files selected", error_code="NO_SELECTION")
        if self.dialog_system:
            cs = ConfirmationService(self.dialog_system)
            cresult = await cs.confirm(
                title="⚠️ Confirm Bulk Delete",
                message=f"Permanently delete {len(filenames)} files? This cannot be undone.",
                proceed_code="FILE_BULK_DELETE_STARTED",
                proceed_message="Bulk deletion started",
                cancel_message="Bulk deletion cancelled"
            )
            if cresult.code == "CANCELLED":
                return ActionResult.make_cancelled(code="FILE_BULK_DELETE_CANCELLED", message=cresult.message, correlation_id=cid, selection=filenames)
        success_count = 0
        for filename in filenames:
            try:
                if await self.file_actions.delete_file(filename):
                    success_count += 1
            except Exception:
                continue
        if self.toast_manager:
            self.toast_manager.show_success(f"Deleted {success_count}/{len(filenames)} files")
        if self.on_data_changed:
            await self.on_data_changed()
        code = "FILE_BULK_DELETE_OK" if success_count == len(filenames) else "FILE_BULK_DELETE_PARTIAL"
        if success_count == len(filenames):
            return ActionResult.make_success(code=code, message="All files deleted", correlation_id=cid, selection=filenames, data={"success": success_count, "total": len(filenames)})
        return ActionResult.make_partial(code=code, message=f"{success_count}/{len(filenames)} deleted", correlation_id=cid, selection=filenames, failed=[], data={"success": success_count, "total": len(filenames)})
    
    # Removed _perform_bulk_delete (logic merged into _bulk_delete returning ActionResult)
    
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
    
    def _create_file_details_content(self, file_data) -> ft.Control:
        """Create file details display content"""
        # Handle case where file_data is an ActionResult instead of a dict
        if hasattr(file_data, 'data') and file_data.data:
            # Extract the actual data from ActionResult
            data_dict = file_data.data
        else:
            data_dict = file_data
            
        details_text = []
        if isinstance(data_dict, dict):
            for key, value in data_dict.items():
                details_text.append(f"{key.replace('_', ' ').title()}: {value}")
        else:
            details_text.append(f"Details: {data_dict}")
        
        return ft.Column([
            ft.Text("\n".join(details_text), size=12)
        ], scroll=ft.ScrollMode.AUTO)
    
    def _create_file_stats_content(self, stats_data) -> ft.Control:
        """Create file statistics display content"""
        # Handle case where stats_data is an ActionResult instead of a dict
        if hasattr(stats_data, 'data') and stats_data.data:
            # Extract the actual data from ActionResult
            data_dict = stats_data.data
        else:
            data_dict = stats_data
            
        stats_text = []
        if isinstance(data_dict, dict):
            for key, value in data_dict.items():
                stats_text.append(f"{key.replace('_', ' ').title()}: {value}")
        else:
            stats_text.append(f"Statistics: {data_dict}")
        
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
        if self.dialog_system and hasattr(self.dialog_system, 'current_dialog') and self.dialog_system.current_dialog:
            self.dialog_system.current_dialog.open = False
            self.page.update()
    
    def _safe_async_task(self, coro):
        """Safely create an async task with proper error handling"""
        # Use page.run_task if available, otherwise check for event loop
        if hasattr(self.page, 'run_task'):
            self.page.run_task(coro)
        else:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    asyncio.create_task(coro)
            except RuntimeError:
                # No event loop running, skip async task creation
                pass