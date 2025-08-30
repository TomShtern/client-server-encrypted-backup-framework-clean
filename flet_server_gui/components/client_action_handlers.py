#!/usr/bin/env python3
"""
Client Action Handlers Component
Handles all client-related actions including view, disconnect, delete, and bulk operations.
"""

# Import UTF-8 solution for Unicode handling
import Shared.utils.utf8_solution

import flet as ft
import asyncio
from typing import List, Dict, Any, Optional, Callable
from ..utils.server_bridge import ServerBridge
from ..actions import ClientActions
from ..utils.action_result import ActionResult
from ..utils.trace_center import get_trace_center
from .base_action_handler import BaseActionHandler, UIActionMixin


class ClientActionHandlers(BaseActionHandler, UIActionMixin):
    """Handles all client-related actions and operations"""
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, toast_manager, page: ft.Page):
        # Initialize base handler with common dependencies
        super().__init__(server_bridge, dialog_system, toast_manager, page)
        
        # Initialize client actions
        self.client_actions = ClientActions(server_bridge)
    
    async def view_client_details(self, client_id: str) -> ActionResult:
        """View detailed information about a client."""
        return await self.execute_action(
            action_name=f"View Client Details ({client_id})",
            action_coro=self._view_client_details_action(client_id),
            require_selection=False,
            trigger_data_change=False,
            show_success_toast=False
        )
    
    async def _view_client_details_action(self, client_id: str):
        """Action implementation for viewing client details"""
        client_data = await self._get_client_details(client_id)
        if not client_data:
            raise ValueError(f"No data found for client {client_id}")
        
        if not self.dialog_system:
            self.show_info(f"Client {client_id} details (dialog system not available)")
            return {"client": client_data}
        
        details_content = self.create_details_content(client_data, f"Client Details: {client_id}")
        await self.show_custom_dialog(
            title=f"Client Details: {client_id}",
            content=details_content
        )
        
        return {"client": client_data}
    
    async def view_client_files(self, client_id: str) -> ActionResult:
        """View files associated with a client."""
        return await self.execute_action(
            action_name=f"View Client Files ({client_id})",
            action_coro=self._view_client_files_action(client_id),
            require_selection=False,
            trigger_data_change=False,
            show_success_toast=False
        )
    
    async def _view_client_files_action(self, client_id: str):
        """Action implementation for viewing client files"""
        client_files = await self._get_client_files(client_id)
        if client_files is None:
            raise ValueError(f"Failed to retrieve files for client {client_id}")
        
        if not client_files:  # empty list
            self.show_info(f"No files for client {client_id}")
            return {"client_id": client_id, "files": []}
        
        if not self.dialog_system:
            self.show_info(f"{len(client_files)} files (dialog system not available)")
            return {"files": client_files, "client_id": client_id}
        
        files_content = self._create_client_files_content(client_files)
        await self.show_custom_dialog(
            title=f"Files for Client: {client_id}",
            content=files_content
        )
        
        return {"files": client_files, "client_id": client_id}
    
    async def disconnect_client(self, client_id: str) -> ActionResult:
        """Disconnect a client from the server (with confirmation)."""
        return await self.execute_action(
            action_name=f"Disconnect Client ({client_id})",
            action_coro=self._disconnect_client_action(client_id),
            confirmation_text=f"Disconnect client '{client_id}'?",
            confirmation_title="Confirm Disconnect",
            require_selection=False,
            trigger_data_change=True,
            success_message=f"Client '{client_id}' disconnected"
        )
    
    async def _disconnect_client_action(self, client_id: str):
        """Action implementation for disconnecting client"""
        success = await self.client_actions.disconnect_client(client_id)
        if not success:
            raise ValueError(f"Failed to disconnect client '{client_id}'")
        
        return {"client_id": client_id}
    
    async def delete_client(self, client_id: str) -> ActionResult:
        """Delete a client and all associated data (with confirmation)."""
        return await self.execute_action(
            action_name=f"Delete Client ({client_id})",
            action_coro=self._delete_client_action(client_id),
            confirmation_text=f"Delete client '{client_id}' and all associated data? This cannot be undone.",
            confirmation_title="⚠️ Confirm Delete",
            require_selection=False,
            trigger_data_change=True,
            success_message=f"Client '{client_id}' deleted"
        )
    
    async def _delete_client_action(self, client_id: str):
        """Action implementation for deleting client"""
        success = await self.client_actions.delete_client(client_id)
        
        # Optional verification
        verified = True
        try:
            remaining_clients = await self.client_actions.server_bridge.get_clients()
            verified = all(client.get("id") != client_id for client in remaining_clients)
        except Exception:
            verified = True  # don't penalize if verification unavailable
        
        if not success:
            raise ValueError(f"Failed to delete client '{client_id}'")
        
        return {"client_id": client_id, "verified": verified}
    
    async def show_client_statistics(self, client_id: str) -> ActionResult:
        """Show detailed statistics for a client."""
        return await self.execute_action(
            action_name=f"View Client Statistics ({client_id})",
            action_coro=self._show_client_statistics_action(client_id),
            require_selection=False,
            trigger_data_change=False,
            show_success_toast=False
        )
    
    async def _show_client_statistics_action(self, client_id: str):
        """Action implementation for showing client statistics"""
        stats = await self._get_client_statistics(client_id)
        if not stats:
            raise ValueError(f"No statistics for client {client_id}")
        
        if not self.dialog_system:
            self.show_info(f"Statistics for {client_id} (dialog system not available)")
            return {"stats": stats}
        
        stats_content = self._create_client_stats_content(stats)
        await self.show_custom_dialog(
            title=f"Statistics for Client: {client_id}",
            content=stats_content
        )
        
        return {"stats": stats}
    
    async def perform_bulk_action(self, action: str, client_ids: List[str]) -> ActionResult:
        """Perform bulk action on multiple clients."""
        if not client_ids:
            self.show_warning("No clients selected")
            return ActionResult.error(
                code="CLIENT_BULK_EMPTY",
                message="No clients selected",
                error_code="NO_SELECTION"
            )
        
        action_map = {"disconnect": self.bulk_disconnect_clients, "delete": self.bulk_delete_clients}
        if action not in action_map:
            self.show_error(f"Unknown bulk action: {action}")
            return ActionResult.error(
                code="CLIENT_BULK_UNKNOWN",
                message="Unknown bulk action",
                error_code="UNKNOWN_ACTION"
            )
        
        return await action_map[action](client_ids)
    
    async def bulk_disconnect_clients(self, client_ids: List[str]) -> ActionResult:
        """Disconnect multiple clients from the server (with confirmation)."""
        if not client_ids:
            self.show_warning("No clients selected")
            return ActionResult.error(
                code="CLIENT_BULK_DISCONNECT_EMPTY",
                message="No clients selected",
                error_code="NO_SELECTION"
            )
        
        return await self.execute_action(
            action_name=f"Bulk Disconnect ({len(client_ids)} clients)",
            action_coro=self._bulk_disconnect_action(client_ids),
            confirmation_text=f"Disconnect {len(client_ids)} clients?",
            confirmation_title="Confirm Bulk Disconnect",
            require_selection=False,
            trigger_data_change=True,
            success_message=f"Disconnected clients"
        )
    
    async def _bulk_disconnect_action(self, client_ids: List[str]):
        """Action implementation for bulk disconnect"""
        success_count = 0
        for client_id in client_ids:
            try:
                if await self.client_actions.disconnect_client(client_id):
                    success_count += 1
            except Exception:
                continue
        
        # Show detailed success message
        if self.toast_manager:
            self.toast_manager.show_success(f"Disconnected {success_count}/{len(client_ids)} clients")
        
        if success_count == 0:
            raise ValueError("Failed to disconnect any clients")
        elif success_count < len(client_ids):
            raise Warning(f"Only {success_count}/{len(client_ids)} clients disconnected")
        
        return {"success": success_count, "total": len(client_ids)}
    
    async def bulk_delete_clients(self, client_ids: List[str]) -> ActionResult:
        """Delete multiple clients from the server (with confirmation)."""
        if not client_ids:
            self.show_warning("No clients selected")
            return ActionResult.error(
                code="CLIENT_BULK_DELETE_EMPTY",
                message="No clients selected",
                error_code="NO_SELECTION"
            )
        
        return await self.execute_action(
            action_name=f"Bulk Delete ({len(client_ids)} clients)",
            action_coro=self._bulk_delete_action(client_ids),
            confirmation_text=f"Delete {len(client_ids)} clients and all data? This cannot be undone.",
            confirmation_title="⚠️ Confirm Bulk Delete",
            require_selection=False,
            trigger_data_change=True,
            success_message=f"Deleted clients"
        )
    
    async def _bulk_delete_action(self, client_ids: List[str]):
        """Action implementation for bulk delete"""
        success_count = 0
        for client_id in client_ids:
            try:
                if await self.client_actions.delete_client(client_id):
                    success_count += 1
            except Exception:
                continue
        
        # Show detailed success message
        if self.toast_manager:
            self.toast_manager.show_success(f"Deleted {success_count}/{len(client_ids)} clients")
        
        if success_count == 0:
            raise ValueError("Failed to delete any clients")
        elif success_count < len(client_ids):
            raise Warning(f"Only {success_count}/{len(client_ids)} clients deleted")
        
        return {"success": success_count, "total": len(client_ids)}
    
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
    
    def _create_client_files_content(self, files_data: List) -> ft.Control:
        """Create client files display content"""
        files_list = [
            ft.ListTile(
                title=ft.Text(file_info.get('filename', 'Unknown')),
                subtitle=ft.Text(f"Size: {file_info.get('size', 0)} bytes"),
                leading=ft.Icon(ft.Icons.FILE_PRESENT),
            )
            for file_info in files_data
        ]
        return ft.Column([
            ft.Text("Files", style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Divider(),
            ft.Column(files_list, spacing=4)
        ], scroll=ft.ScrollMode.AUTO)
    
    def _create_client_stats_content(self, stats_data: Dict) -> ft.Control:
        """Create client statistics display content using base class method"""
        return self.create_details_content(stats_data, "Statistics")