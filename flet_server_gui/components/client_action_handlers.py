#!/usr/bin/env python3
"""
Client Action Handlers Component
Handles all client-related actions including view, disconnect, delete, and bulk operations.
"""

import flet as ft
import asyncio
from typing import List, Dict, Any, Optional, Callable
from ..utils.server_bridge import ServerBridge
from ..actions import ClientActions


class ClientActionHandlers:
    """Handles all client-related actions and operations"""
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, toast_manager, page: ft.Page):
        self.server_bridge = server_bridge
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.page = page
        
        # Initialize client actions
        self.client_actions = ClientActions(server_bridge)
        
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
    
    async def view_client_details(self, client_id: str) -> None:
        """View detailed information about a client"""
        try:
            # Get client details from server
            client_data = await self._get_client_details(client_id)
            
            if not client_data:
                self.toast_manager.show_error(f"Could not retrieve details for client: {client_id}")
                return
            
            # Create detailed view content
            details_content = self._create_client_details_content(client_data)
            
            # Show details dialog
            self.dialog_system.show_custom_dialog(
                title=f"Client Details: {client_id}",
                content=details_content,
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self._close_dialog())
                ]
            )
            
        except Exception as e:
            self.toast_manager.show_error(f"Error viewing client details: {str(e)}")
    
    async def view_client_files(self, client_id: str) -> None:
        """View files associated with a client"""
        try:
            # Get client files from server
            client_files = await self._get_client_files(client_id)
            
            if not client_files:
                self.toast_manager.show_info(f"No files found for client: {client_id}")
                return
            
            # Create files view content
            files_content = self._create_client_files_content(client_files)
            
            # Show files dialog
            self.dialog_system.show_custom_dialog(
                title=f"Files for Client: {client_id}",
                content=files_content,
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self._close_dialog())
                ]
            )
            
        except Exception as e:
            self.toast_manager.show_error(f"Error viewing client files: {str(e)}")
    
    async def disconnect_client(self, client_id: str) -> None:
        """Disconnect a client from the server"""
        def confirm_disconnect():
            self._close_dialog()
            # Use page.run_task if available, otherwise check for event loop
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_disconnect(client_id))
            else:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_disconnect(client_id))
                except RuntimeError:
                    # No event loop running, skip async task creation
                    pass
        
        # Show confirmation dialog
        await self._show_confirmation_dialog(
            title="Confirm Disconnect",
            message=f"Are you sure you want to disconnect client '{client_id}'?",
            on_confirm=confirm_disconnect,
            on_cancel=lambda: self._close_dialog()
        )
    
    async def _perform_disconnect(self, client_id: str) -> None:
        """Actually perform the client disconnection"""
        try:
            # Execute disconnect via client actions
            success = await self.client_actions.disconnect_client(client_id)
            
            if success:
                self.toast_manager.show_success(f"Client '{client_id}' disconnected successfully")
                if self.on_data_changed:
                    await self.on_data_changed()
            else:
                self.toast_manager.show_error(f"Failed to disconnect client '{client_id}'")
                
        except Exception as e:
            self.toast_manager.show_error(f"Error disconnecting client: {str(e)}")
    
    async def delete_client(self, client_id: str) -> None:
        """Delete a client and all associated data"""
        try:
            def confirm_delete():
                self._close_dialog()
                # Use consistent async task creation
                if hasattr(self.page, 'run_task'):
                    self.page.run_task(self._perform_delete(client_id))
                else:
                    try:
                        import asyncio
                        loop = asyncio.get_running_loop()
                        loop.create_task(self._perform_delete(client_id))
                    except RuntimeError:
                        pass  # No event loop available
            
            def cancel_delete():
                self._close_dialog()
            
            # Show confirmation dialog with warning
            await self._show_confirmation_dialog(
                title="⚠️ Confirm Delete",
                message=f"Are you sure you want to permanently delete client '{client_id}' and all associated data? This action cannot be undone.",
                on_confirm=confirm_delete,
                on_cancel=cancel_delete
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.toast_manager.show_error(f"Error deleting client: {str(e)}")
    
    async def _perform_delete(self, client_id: str) -> None:
        """Actually perform the client deletion"""
        try:
            # Execute delete via client actions
            success = await self.client_actions.delete_client(client_id)
            
            if success:
                self.toast_manager.show_success(f"Client '{client_id}' deleted successfully")
                # Instead of relying on callback, directly refresh the UI
                if hasattr(self, 'page') and self.page:
                    # Find the parent clients view and refresh it
                    # Create a task to refresh the UI
                    async def refresh_ui():
                        try:
                            # Wait a moment for the delete to complete
                            await asyncio.sleep(0.1)
                            # Trigger a manual refresh
                            if hasattr(self.page, 'views') and self.page.views:
                                # Find the clients view and refresh it
                                for view in self.page.views:
                                    if hasattr(view, '__class__') and 'ClientsView' in view.__class__.__name__:
                                        if hasattr(view, '_refresh_clients'):
                                            await view._refresh_clients()
                                            break
                        except Exception as e:
                            pass  # Ignore refresh errors
                    
                    # Schedule the refresh
                    if hasattr(self.page, 'run_task'):
                        self.page.run_task(refresh_ui())
                    else:
                        try:
                            loop = asyncio.get_running_loop()
                            if loop.is_running():
                                asyncio.create_task(refresh_ui())
                        except RuntimeError:
                            pass
            else:
                self.toast_manager.show_error(f"Failed to delete client '{client_id}'")
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.toast_manager.show_error(f"Error deleting client: {str(e)}")
    
    async def show_client_statistics(self, client_id: str) -> None:
        """Show detailed statistics for a client"""
        try:
            # Get client statistics
            stats = await self._get_client_statistics(client_id)
            
            if not stats:
                self.toast_manager.show_error(f"Could not retrieve statistics for client: {client_id}")
                return
            
            # Create statistics content
            stats_content = self._create_client_stats_content(stats)
            
            # Show statistics dialog
            self.dialog_system.show_custom_dialog(
                title=f"Statistics for Client: {client_id}",
                content=stats_content,
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self._close_dialog())
                ]
            )
            
        except Exception as e:
            self.toast_manager.show_error(f"Error showing client statistics: {str(e)}")
    
    async def perform_bulk_action(self, action: str, client_ids: List[str]) -> None:
        """Perform bulk action on multiple clients"""
        if not client_ids:
            self.toast_manager.show_warning("No clients selected")
            return
        
        action_map = {
            "disconnect": self._bulk_disconnect,
            "delete": self._bulk_delete,
        }
        
        if action in action_map:
            await action_map[action](client_ids)
        else:
            self.toast_manager.show_error(f"Unknown bulk action: {action}")
    
    async def bulk_disconnect_clients(self, client_ids: List[str]) -> None:
        """Disconnect multiple clients from the server"""
        if not client_ids:
            self.toast_manager.show_warning("No clients selected")
            return
            
        success_count = 0
        for client_id in client_ids:
            try:
                if await self.client_actions.disconnect_client(client_id):
                    success_count += 1
            except Exception:
                continue
        
        self.toast_manager.show_success(f"Disconnected {success_count}/{len(client_ids)} clients")
        if self.on_data_changed:
            await self.on_data_changed()
    
    async def bulk_delete_clients(self, client_ids: List[str]) -> None:
        """Delete multiple clients from the server"""
        if not client_ids:
            self.toast_manager.show_warning("No clients selected")
            return
            
        def confirm_bulk_delete():
            self._close_dialog()
            # Use page.run_task if available, otherwise check for event loop
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_bulk_delete(client_ids))
            else:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_bulk_delete(client_ids))
                except RuntimeError:
                    # No event loop running, skip async task creation
                    pass
        
        await self._show_confirmation_dialog(
            title="⚠️ Confirm Bulk Delete",
            message=f"Are you sure you want to permanently delete {len(client_ids)} clients and all associated data? This action cannot be undone.",
            on_confirm=confirm_bulk_delete,
            on_cancel=lambda: self._close_dialog()
        )
    
    async def _bulk_disconnect(self, client_ids: List[str]) -> None:
        """Disconnect multiple clients"""
        def confirm_bulk_disconnect():
            self._close_dialog()
            # Use page.run_task if available, otherwise check for event loop
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_bulk_disconnect(client_ids))
            else:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_bulk_disconnect(client_ids))
                except RuntimeError:
                    # No event loop running, skip async task creation
                    pass
        
        await self._show_confirmation_dialog(
            title="Confirm Bulk Disconnect",
            message=f"Are you sure you want to disconnect {len(client_ids)} clients?",
            on_confirm=confirm_bulk_disconnect,
            on_cancel=lambda: self._close_dialog()
        )
    
    
    async def _bulk_delete(self, client_ids: List[str]) -> None:
        """Delete multiple clients"""
        def confirm_bulk_delete():
            self._close_dialog()
            # Use page.run_task if available, otherwise check for event loop
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_bulk_delete(client_ids))
            else:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_bulk_delete(client_ids))
                except RuntimeError:
                    # No event loop running, skip async task creation
                    pass
        
        await self._show_confirmation_dialog(
            title="⚠️ Confirm Bulk Delete",
            message=f"Are you sure you want to permanently delete {len(client_ids)} clients and all associated data? This action cannot be undone.",
            on_confirm=confirm_bulk_delete,
            on_cancel=lambda: self._close_dialog()
        )
    
    async def _perform_bulk_delete(self, client_ids: List[str]) -> None:
        """Actually perform bulk deletion"""
        success_count = 0
        for client_id in client_ids:
            try:
                if await self.client_actions.delete_client(client_id):
                    success_count += 1
            except Exception:
                continue
        
        self.toast_manager.show_success(f"Deleted {success_count}/{len(client_ids)} clients")
        if self.on_data_changed:
            await self.on_data_changed()
    
    # Helper methods for data retrieval and UI creation
    
    async def _get_client_details(self, client_id: str) -> Optional[Dict]:
        """Get detailed client information"""
        try:
            return await self.client_actions.get_client_details(client_id)
        except Exception:
            return None
    
    async def _get_client_files(self, client_id: str) -> Optional[List]:
        """Get files associated with client"""
        try:
            return await self.client_actions.get_client_files(client_id)
        except Exception:
            return None
    
    async def _get_client_statistics(self, client_id: str) -> Optional[Dict]:
        """Get client statistics"""
        try:
            return await self.client_actions.get_client_statistics(client_id)
        except Exception:
            return None
    
    def _create_client_details_content(self, client_data: Dict) -> ft.Control:
        """Create client details display content"""
        details_text = []
        for key, value in client_data.items():
            details_text.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return ft.Column([
            ft.Text("\n".join(details_text), size=12)
        ], scroll=ft.ScrollMode.AUTO)
    
    def _create_client_files_content(self, files_data: List) -> ft.Control:
        """Create client files display content"""
        files_list = []
        for file_info in files_data:
            files_list.append(
                ft.ListTile(
                    title=ft.Text(file_info.get('filename', 'Unknown')),
                    subtitle=ft.Text(f"Size: {file_info.get('size', 0)} bytes"),
                    leading=ft.Icon(ft.Icons.FILE_PRESENT)
                )
            )
        
        return ft.Column(files_list, scroll=ft.ScrollMode.AUTO)
    
    def _create_client_stats_content(self, stats_data: Dict) -> ft.Control:
        """Create client statistics display content"""
        stats_text = []
        for key, value in stats_data.items():
            stats_text.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return ft.Column([
            ft.Text("\n".join(stats_text), size=12)
        ], scroll=ft.ScrollMode.AUTO)
    
    def _close_dialog(self):
        """Close the current dialog"""
        if self.dialog_system and hasattr(self.dialog_system, 'current_dialog'):
            if self.dialog_system.current_dialog:
                self.dialog_system.current_dialog.open = False
                self.page.update()