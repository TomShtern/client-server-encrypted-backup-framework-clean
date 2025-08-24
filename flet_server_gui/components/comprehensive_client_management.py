#!/usr/bin/env python3
"""
Comprehensive Client Management Component
Complete feature parity with TKinter GUI client management functionality.
"""

import flet as ft
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from ..utils.server_bridge import ServerBridge
from .base_component import BaseComponent
from .button_factory import ActionButtonFactory
from ..actions import ClientActions
from ..layouts import ResponsiveBuilder, BreakpointManager


class ComprehensiveClientManagement(BaseComponent):
    """Complete client management with all TKinter GUI features."""
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, toast_manager, page):
        super().__init__(page, dialog_system, toast_manager)
        self.server_bridge = server_bridge
        # Initialize button factory
        self.button_factory = ActionButtonFactory(self, server_bridge, page)
        # Initialize client actions
        self.client_actions = ClientActions(server_bridge)
        
        # UI Components
        self.client_table = None
        self.selected_clients = []
        self.status_text = None
        self.refresh_button = None
        self.search_field = None
        self.filter_dropdown = None
        self.bulk_actions_row = None
        
        # Data
        self.all_clients = []
        self.filtered_clients = []
        
    def build(self) -> ft.Control:
        """Build the comprehensive client management view."""
        
        # Header with title and status
        self.status_text = ft.Text(
            "Loading client data...",
            size=14,
            color=ft.Colors.BLUE_600
        )
        
        # Search and filter controls
        self.search_field = ft.TextField(
            label="Search clients...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            width=300,
        )
        
        # Status filter chips (enhanced UX from enhanced_client_management)
        self.status_chips = ft.Row([
            ft.Chip(
                label=ft.Text("All"),
                selected=True,
                on_select=lambda e: self._on_chip_select("all", e),
                bgcolor=ft.Colors.PRIMARY_CONTAINER,
            ),
            ft.Chip(
                label=ft.Text("Connected"),
                on_select=lambda e: self._on_chip_select("connected", e),
                bgcolor=ft.Colors.GREEN_100,
            ),
            ft.Chip(
                label=ft.Text("Registered"),
                on_select=lambda e: self._on_chip_select("registered", e),
                bgcolor=ft.Colors.BLUE_100,
            ),
            ft.Chip(
                label=ft.Text("Offline"),
                on_select=lambda e: self._on_chip_select("offline", e),
                bgcolor=ft.Colors.ORANGE_100,
            )
        ], spacing=8, wrap=True)
        
        self.current_filter = "all"
        
        self.refresh_button = ft.ElevatedButton(
            "Refresh Clients",
            icon=ft.Icons.REFRESH,
            on_click=self._refresh_clients,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE
        )
        
        # Bulk action buttons using button factory (initially hidden)
        self.bulk_actions_row = ResponsiveBuilder.create_responsive_row([
            self.button_factory.create_action_button('client_disconnect_bulk', self._get_selected_clients),
            self.button_factory.create_action_button('client_delete_bulk', self._get_selected_clients),
            self.button_factory.create_action_button('client_export', self._get_selected_clients),
        ], visible=False, spacing=10)
        
        # Client data table with selection
        self.client_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Checkbox(on_change=self._on_select_all)),  # Select all checkbox
                ft.DataColumn(ft.Text("Username", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Last Seen", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Files", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Total Size", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        )
        
        # Table container with scrolling
        table_container = ft.Container(
            content=ft.Column([
                self.client_table
            ], scroll=ft.ScrollMode.AUTO),
            height=500,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
        )
        
        # Action buttons row using responsive layout
        action_buttons = ResponsiveBuilder.create_responsive_row([
            self.button_factory.create_action_button('client_import', lambda: []),
            ft.OutlinedButton(
                "Client Statistics",
                icon=ft.Icons.ANALYTICS,
                on_click=self._show_client_statistics
            ),
        ], spacing=10)
        
        # Main layout with responsive design
        screen_width = self.page.window_width or 1024
        responsive_padding = BreakpointManager.get_adaptive_padding(screen_width)
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Client Management", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.status_text,
                
                # Search and filter controls with responsive layout
                ResponsiveBuilder.create_responsive_row([
                    self.search_field,
                    self.refresh_button,
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                
                # Status filter chips for better UX
                ft.Container(
                    content=ft.Column([
                        ft.Text("Filter by Status:", size=12, weight=ft.FontWeight.BOLD),
                        self.status_chips
                    ], spacing=5),
                    padding=ft.padding.symmetric(vertical=5)
                ),
                
                ft.Container(height=10),  # Spacer
                
                # Bulk actions (shown when clients selected)
                self.bulk_actions_row,
                
                # Action buttons
                action_buttons,
                
                ft.Container(height=10),  # Spacer
                
                # Client table
                table_container,
            ], spacing=10),
            padding=responsive_padding,
        )
    
    def _refresh_clients(self, e=None):
        """Refresh client data from server."""
        try:
            self.status_text.value = "Refreshing client data..."
            self.status_text.color = ft.Colors.BLUE_600
            
            # Get real client data
            clients = self.server_bridge.get_client_list()
            self.all_clients = clients
            
            # Get file counts for each client
            files = self.server_bridge.get_file_list()
            client_file_counts = {}
            client_file_sizes = {}
            
            for file_info in files:
                client_name = file_info.get('client', 'Unknown')
                client_file_counts[client_name] = client_file_counts.get(client_name, 0) + 1
                
                size = file_info.get('size', 0) or 0
                client_file_sizes[client_name] = client_file_sizes.get(client_name, 0) + size
            
            # Add file info to clients
            for client in clients:
                client_name = client.client_id
                client.files_count = client_file_counts.get(client_name, 0)
                client.total_size = client_file_sizes.get(client_name, 0)
            
            self._apply_filters()
            
            if not clients:
                self.status_text.value = "No registered clients found"
                self.status_text.color = ft.Colors.ORANGE_600
            else:
                mode_text = "Mock Data" if getattr(self.server_bridge, 'mock_mode', False) else "Real Database"
                self.status_text.value = f"Found {len(clients)} clients ({mode_text})"
                self.status_text.color = ft.Colors.GREEN_600
                
        except Exception as e:
            self.status_text.value = f"Error loading clients: {str(e)}"
            self.status_text.color = ft.Colors.RED_600
            print(f"[ERROR] Failed to refresh clients: {e}")
    
    def _apply_filters(self):
        """Apply search and status filters to clients."""
        filtered = self.all_clients.copy()
        
        # Apply search filter
        search_term = self.search_field.value.lower() if self.search_field.value else ""
        if search_term:
            filtered = [c for c in filtered if search_term in c.client_id.lower()]
        
        # Apply status filter (enhanced with chip system)
        status_filter = getattr(self, 'current_filter', 'all')
        if status_filter != "all":
            filtered = [c for c in filtered if c.status.lower() == status_filter.lower()]
        
        self.filtered_clients = filtered
        self._populate_client_table()
    
    def _populate_client_table(self):
        """Populate the client table with filtered data."""
        self.client_table.rows.clear()
        self.selected_clients.clear()
        
        if not self.filtered_clients:
            # No clients to show
            self.client_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("No clients match the current filters", italic=True)),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                    ft.DataCell(ft.Text("")),
                ])
            )
        else:
            for client in self.filtered_clients:
                # Format last activity
                try:
                    if hasattr(client, 'last_activity'):
                        time_diff = datetime.now() - client.last_activity
                        if time_diff.total_seconds() < 300:
                            last_seen = "Just now"
                        elif time_diff.total_seconds() < 3600:
                            mins = int(time_diff.total_seconds() / 60)
                            last_seen = f"{mins}m ago"
                        else:
                            last_seen = client.last_activity.strftime('%Y-%m-%d %H:%M')
                    else:
                        last_seen = "Unknown"
                except Exception:
                    last_seen = "Unknown"
                
                # Format file size
                total_size_mb = getattr(client, 'total_size', 0) / (1024 * 1024) if getattr(client, 'total_size', 0) > 0 else 0
                size_display = f"{total_size_mb:.1f} MB" if total_size_mb > 0 else "0 MB"
                
                # Status display with icon
                status_icon = "🟢" if client.status == "Connected" else "🟡"
                status_display = f"{status_icon} {client.status}"
                
                # Create action buttons for this client using button factory
                action_buttons = ft.Row([
                    self.button_factory.create_action_button('client_view_details', lambda c=client: [client.client_id]),
                    self.button_factory.create_action_button('client_view_files', lambda c=client: [client.client_id]),
                    self.button_factory.create_action_button('client_disconnect', lambda c=client: [client.client_id]),
                    self.button_factory.create_action_button('client_delete', lambda c=client: [client.client_id]),
                ], tight=True)
                
                # Add client row
                self.client_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Checkbox(
                                value=False,
                                data=client.client_id,
                                on_change=self._on_client_select
                            )),
                            ft.DataCell(ft.Text(
                                client.client_id,
                                weight=ft.FontWeight.BOLD,
                                selectable=True
                            )),
                            ft.DataCell(ft.Text(status_display)),
                            ft.DataCell(ft.Text(last_seen, size=12)),
                            ft.DataCell(ft.Text(str(getattr(client, 'files_count', 0)))),
                            ft.DataCell(ft.Text(size_display)),
                            ft.DataCell(action_buttons),
                        ]
                    )
                )
        
        self._update_bulk_actions_visibility()
    
    def _on_search_change(self, e):
        """Handle search field changes."""
        self._apply_filters()
    
    def _on_filter_change(self, e):
        """Handle filter dropdown changes."""
        self._apply_filters()
    
    def _on_chip_select(self, filter_value: str, e):
        """Handle status chip selection (enhanced UX from enhanced_client_management)."""
        # Update current filter
        self.current_filter = filter_value
        
        # Update chip selection states
        for chip in self.status_chips.controls:
            if isinstance(chip, ft.Chip):
                chip.selected = False
        
        # Set selected chip
        e.control.selected = True
        
        # Apply filters and update UI
        self._apply_filters()
        
        # Show toast notification for user feedback
        if hasattr(self, 'page') and self.page:
            self._show_toast(f"Filtered by: {filter_value.title()}", ft.Colors.PRIMARY_CONTAINER)
    
    def _on_select_all(self, e):
        """Handle select all checkbox."""
        select_all = e.control.value
        self.selected_clients.clear()
        
        for row in self.client_table.rows:
            if len(row.cells) > 0 and isinstance(row.cells[0].content, ft.Checkbox):
                checkbox = row.cells[0].content
                checkbox.value = select_all
                if select_all and hasattr(checkbox, 'data'):
                    self.selected_clients.append(checkbox.data)
        
        self._update_bulk_actions_visibility()
    
    def _on_client_select(self, e):
        """Handle individual client selection."""
        client_id = e.control.data
        if e.control.value:
            if client_id not in self.selected_clients:
                self.selected_clients.append(client_id)
        else:
            if client_id in self.selected_clients:
                self.selected_clients.remove(client_id)
        
        self._update_bulk_actions_visibility()
    
    def _update_bulk_actions_visibility(self):
        """Show/hide bulk actions based on selection."""
        self.bulk_actions_row.visible = len(self.selected_clients) > 0
    
    # === Individual Client Actions ===
    
    def _view_client_details(self, client):
        """Show detailed client information."""
        async def show_details():
            try:
                # Use action system to get client details
                result = await self.client_actions.get_client_details(client.client_id)
                if result.success:
                    client_data = result.data
                    details_content = ft.Column([
                        ft.Text(f"Client Details: {client.client_id}", size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Row([ft.Text("Username:", weight=ft.FontWeight.BOLD), ft.Text(client.client_id)]),
                        ft.Row([ft.Text("Status:", weight=ft.FontWeight.BOLD), ft.Text(client.status)]),
                        ft.Row([ft.Text("Address:", weight=ft.FontWeight.BOLD), ft.Text(getattr(client, 'address', 'N/A'))]),
                        ft.Row([ft.Text("Connected At:", weight=ft.FontWeight.BOLD), 
                               ft.Text(client.connected_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(client, 'connected_at') else 'N/A')]),
                        ft.Row([ft.Text("Last Activity:", weight=ft.FontWeight.BOLD), 
                               ft.Text(client.last_activity.strftime('%Y-%m-%d %H:%M:%S') if hasattr(client, 'last_activity') else 'N/A')]),
                        ft.Row([ft.Text("Files Count:", weight=ft.FontWeight.BOLD), ft.Text(str(getattr(client, 'files_count', 0)))]),
                        ft.Row([ft.Text("Total Size:", weight=ft.FontWeight.BOLD), 
                               ft.Text(f"{getattr(client, 'total_size', 0) / (1024*1024):.1f} MB")]),
                    ], spacing=10)
                    
                    if self.dialog_system:
                        self.dialog_system.show_custom("Client Details", details_content)
                else:
                    if self.dialog_system:
                        self.dialog_system.show_error("Error", f"Failed to get client details: {result.error_message}")
            except Exception as e:
                if self.dialog_system:
                    self.dialog_system.show_error("Error", f"Failed to load client details: {str(e)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(show_details())
    
    def _view_client_files(self, client):
        """Show files uploaded by this client."""
        async def show_files():
            try:
                # Use action system to get client files
                result = await self.client_actions.get_client_files(client.client_id)
                if result.success:
                    client_files = result.data
                    
                    if not client_files:
                        content = ft.Text(f"No files found for client '{client.client_id}'")
                    else:
                        # Create file list
                        file_rows = []
                        for file_info in client_files:
                            size_mb = (file_info.get('size', 0) or 0) / (1024 * 1024)
                            file_rows.append(
                                ft.Row([
                                    ft.Text(file_info.get('filename', 'Unknown'), expand=True),
                                    ft.Text(f"{size_mb:.2f} MB"),
                                    ft.Text("Verified" if file_info.get('verified') else "Unverified"),
                                ])
                            )
                        
                        content = ft.Column([
                            ft.Text(f"Files from {client.client_id} ({len(client_files)} files):", 
                                   weight=ft.FontWeight.BOLD),
                            ft.Divider(),
                            *file_rows[:20],  # Limit to first 20 files
                            ft.Text(f"... and {len(client_files) - 20} more files" if len(client_files) > 20 else "")
                        ], height=400, scroll=ft.ScrollMode.AUTO)
                    
                    if self.dialog_system:
                        self.dialog_system.show_custom(f"Files - {client.client_id}", content)
                else:
                    if self.dialog_system:
                        self.dialog_system.show_error("Error", f"Failed to get client files: {result.error_message}")
            except Exception as e:
                if self.dialog_system:
                    self.dialog_system.show_error("Error", f"Failed to load client files: {str(e)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(show_files())
    
    def _disconnect_client(self, client):
        """Disconnect a client."""
        async def disconnect_action():
            try:
                # Use action system to disconnect client
                result = await self.client_actions.disconnect_client(client.client_id)
                
                if result.success:
                    if self.dialog_system:
                        self.dialog_system.show_success(
                            "Client Disconnected",
                            f"Client '{client.client_id}' has been disconnected"
                        )
                    self._refresh_clients()
                else:
                    if self.dialog_system:
                        if "already" in result.error_message.lower():
                            self.dialog_system.show_warning(
                                "Disconnect Warning",
                                f"Client '{client.client_id}' is already disconnected"
                            )
                        else:
                            self.dialog_system.show_warning(
                                "Disconnect Warning",
                                f"Client '{client.client_id}' disconnect completed with warnings: {result.error_message}"
                            )
                    self._refresh_clients()
            except Exception as ex:
                if self.dialog_system:
                    self.dialog_system.show_error(
                        "Disconnect Failed",
                        f"Failed to disconnect client: {str(ex)}"
                    )
        
        if self.dialog_system:
            self.dialog_system.show_confirmation(
                "Confirm Disconnect",
                f"Are you sure you want to disconnect client '{client.client_id}'?\n\nThis will terminate the client's connection to the server.",
                on_confirm=lambda: asyncio.create_task(disconnect_action()),
                confirm_text="Disconnect",
                danger=True
            )
    
    def _delete_client(self, client):
        """Delete a client from the database."""
        async def delete_action():
            try:
                # Use action system to delete client
                result = await self.client_actions.delete_client(client.client_id)
                
                if result.success:
                    if self.dialog_system:
                        self.dialog_system.show_success(
                            "Client Deleted",
                            f"Client '{client.client_id}' has been permanently deleted"
                        )
                    self._refresh_clients()
                else:
                    if self.dialog_system:
                        self.dialog_system.show_warning(
                            "Delete Warning",
                            f"Client '{client.client_id}' delete completed with warnings: {result.error_message}"
                        )
                    self._refresh_clients()
            except Exception as ex:
                if self.dialog_system:
                    self.dialog_system.show_error(
                        "Delete Failed",
                        f"Failed to delete client: {str(ex)}"
                    )
        
        if self.dialog_system:
            self.dialog_system.show_confirmation(
                "Confirm Delete",
                f"Are you sure you want to delete client '{client.client_id}'?\n\nThis will permanently remove the client and all associated data.\n\n⚠️ THIS ACTION CANNOT BE UNDONE!",
                on_confirm=lambda: asyncio.create_task(delete_action()),
                confirm_text="Delete",
                danger=True
            )
    
    def _get_selected_clients(self) -> List[str]:
        """Get list of currently selected client IDs."""
        return self.selected_clients.copy()
    
    # Bulk actions are now handled by button factory and BaseComponent
    
    # Client import is now handled by button factory
    
    def _show_client_statistics(self, e):
        """Show client statistics."""
        async def show_stats():
            try:
                # Use action system to get client stats
                result = await self.client_actions.get_client_stats()
                if result.success:
                    stats = result.data
                    total_clients = stats.get('total_clients', 0)
                    active_clients = stats.get('active_clients', 0)
                    inactive_clients = stats.get('inactive_clients', 0)
                    
                    stats_content = ft.Column([
                        ft.Text("Client Statistics", size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Row([ft.Text("Total Clients:", weight=ft.FontWeight.BOLD), ft.Text(str(total_clients))]),
                        ft.Row([ft.Text("Connected:", weight=ft.FontWeight.BOLD), ft.Text(str(active_clients))]),
                        ft.Row([ft.Text("Registered:", weight=ft.FontWeight.BOLD), ft.Text(str(inactive_clients))]),
                        ft.Row([ft.Text("Offline:", weight=ft.FontWeight.BOLD), ft.Text(str(total_clients - active_clients))]),
                    ], spacing=10)
                    
                    if self.dialog_system:
                        self.dialog_system.show_custom("Client Statistics", stats_content)
                else:
                    if self.dialog_system:
                        self.dialog_system.show_error("Error", f"Failed to generate statistics: {result.error_message}")
            except Exception as ex:
                if self.dialog_system:
                    self.dialog_system.show_error("Error", f"Failed to generate statistics: {str(ex)}")
        
        # Run the async function
        import asyncio
        asyncio.create_task(show_stats())
    
    def _show_toast(self, message: str, bgcolor: str = None):
        """Show toast notification (enhanced UX from enhanced_client_management)."""
        try:
            if hasattr(self, 'toast_manager') and self.toast_manager:
                # Use the integrated toast manager
                self.toast_manager.show_info(message)
            elif hasattr(self, 'page') and self.page:
                # Fallback to snack bar
                snack_bar = ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=bgcolor or ft.Colors.PRIMARY_CONTAINER,
                    duration=2000
                )
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()
        except Exception as e:
            print(f"[TOAST ERROR] {e}: {message}")
    
    def did_mount(self):
        """Called when component is mounted - load initial data."""
        self._refresh_clients()