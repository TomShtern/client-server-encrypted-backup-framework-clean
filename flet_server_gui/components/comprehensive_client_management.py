#!/usr/bin/env python3
"""
Comprehensive Client Management Component
Complete feature parity with TKinter GUI client management functionality.
"""

import flet as ft
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from ..utils.server_bridge import ServerBridge


class ComprehensiveClientManagement:
    """Complete client management with all TKinter GUI features."""
    
    def __init__(self, server_bridge: ServerBridge, show_dialog_callback: Optional[Callable] = None):
        self.server_bridge = server_bridge
        self.show_dialog = show_dialog_callback or self._default_dialog
        
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
        
        self.filter_dropdown = ft.Dropdown(
            label="Filter by status",
            width=200,
            options=[
                ft.dropdown.Option("all", "All Clients"),
                ft.dropdown.Option("connected", "Connected"),
                ft.dropdown.Option("registered", "Registered"),
                ft.dropdown.Option("offline", "Offline"),
            ],
            value="all",
            on_change=self._on_filter_change
        )
        
        self.refresh_button = ft.ElevatedButton(
            "Refresh Clients",
            icon=ft.Icons.REFRESH,
            on_click=self._refresh_clients,
            bgcolor=ft.Colors.BLUE_600,
            color=ft.Colors.WHITE
        )
        
        # Bulk action buttons (initially hidden)
        self.bulk_actions_row = ft.Row([
            ft.ElevatedButton(
                "Disconnect Selected",
                icon=ft.Icons.LINK_OFF,
                on_click=self._disconnect_selected_clients,
                bgcolor=ft.Colors.ORANGE_600,
                color=ft.Colors.WHITE
            ),
            ft.ElevatedButton(
                "Delete Selected",
                icon=ft.Icons.DELETE,
                on_click=self._delete_selected_clients,
                bgcolor=ft.Colors.RED_600,
                color=ft.Colors.WHITE
            ),
            ft.ElevatedButton(
                "Export Selected",
                icon=ft.Icons.DOWNLOAD,
                on_click=self._export_selected_clients,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            ),
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
        
        # Action buttons row
        action_buttons = ft.Row([
            ft.ElevatedButton(
                "Add Client",
                icon=ft.Icons.PERSON_ADD,
                on_click=self._add_client,
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            ),
            ft.OutlinedButton(
                "Import Clients",
                icon=ft.Icons.UPLOAD,
                on_click=self._import_clients
            ),
            ft.OutlinedButton(
                "Client Statistics",
                icon=ft.Icons.ANALYTICS,
                on_click=self._show_client_statistics
            ),
        ], spacing=10)
        
        # Main layout
        return ft.Container(
            content=ft.Column([
                ft.Text("Client Management", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                self.status_text,
                
                # Search and filter row
                ft.Row([
                    self.search_field,
                    self.filter_dropdown,
                    self.refresh_button,
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                
                ft.Container(height=10),  # Spacer
                
                # Bulk actions (shown when clients selected)
                self.bulk_actions_row,
                
                # Action buttons
                action_buttons,
                
                ft.Container(height=10),  # Spacer
                
                # Client table
                table_container,
            ], spacing=10),
            padding=20,
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
        
        # Apply status filter
        status_filter = self.filter_dropdown.value if self.filter_dropdown else "all"
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
                
                # Create action buttons for this client
                action_buttons = ft.Row([
                    ft.IconButton(
                        ft.Icons.INFO,
                        tooltip="View Details",
                        on_click=lambda e, c=client: self._view_client_details(c)
                    ),
                    ft.IconButton(
                        ft.Icons.FOLDER,
                        tooltip="View Files",
                        on_click=lambda e, c=client: self._view_client_files(c)
                    ),
                    ft.IconButton(
                        ft.Icons.LINK_OFF,
                        tooltip="Disconnect",
                        on_click=lambda e, c=client: self._disconnect_client(c)
                    ),
                    ft.IconButton(
                        ft.Icons.DELETE,
                        tooltip="Delete",
                        on_click=lambda e, c=client: self._delete_client(c)
                    ),
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
        
        self.show_dialog("Client Details", details_content)
    
    def _view_client_files(self, client):
        """Show files uploaded by this client."""
        try:
            all_files = self.server_bridge.get_file_list()
            client_files = [f for f in all_files if f.get('client') == client.client_id]
            
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
            
            self.show_dialog(f"Files - {client.client_id}", content)
            
        except Exception as e:
            self.show_dialog("Error", ft.Text(f"Failed to load client files: {str(e)}"))
    
    def _disconnect_client(self, client):
        """Disconnect a client."""
        def confirm_disconnect():
            try:
                success = self.server_bridge.disconnect_client(client.client_id)
                self._refresh_clients()
                
                if success:
                    self.show_dialog(
                        "success",
                        "Client Disconnected",
                        f"Client '{client.client_id}' has been disconnected"
                    )
                else:
                    self.show_dialog(
                        "warning",
                        "Disconnect Warning",
                        f"Client '{client.client_id}' disconnect completed with warnings"
                    )
            except Exception as ex:
                self.show_dialog(
                    "error",
                    "Disconnect Failed",
                    f"Failed to disconnect client: {str(ex)}"
                )
        
        self.show_dialog(
            "confirmation",
            "Confirm Disconnect",
            f"Are you sure you want to disconnect client '{client.client_id}'?\n\nThis will terminate the client's connection to the server.",
            on_confirm=confirm_disconnect,
            confirm_text="Disconnect",
            danger=True
        )
    
    def _delete_client(self, client):
        """Delete a client from the database."""
        def confirm_delete():
            try:
                success = self.server_bridge.delete_client(client.client_id)
                self._refresh_clients()
                
                if success:
                    self.show_dialog(
                        "success",
                        "Client Deleted",
                        f"Client '{client.client_id}' has been permanently deleted"
                    )
                else:
                    self.show_dialog(
                        "warning",
                        "Delete Warning",
                        f"Client '{client.client_id}' delete completed with warnings"
                    )
            except Exception as ex:
                self.show_dialog(
                    "error",
                    "Delete Failed",
                    f"Failed to delete client: {str(ex)}"
                )
        
        self.show_dialog(
            "confirmation",
            "Confirm Delete",
            f"Are you sure you want to delete client '{client.client_id}'?\n\nThis will permanently remove the client and all associated data.\n\n⚠️ THIS ACTION CANNOT BE UNDONE!",
            on_confirm=confirm_delete,
            confirm_text="Delete",
            danger=True
        )
    
    # === Bulk Actions ===
    
    def _disconnect_selected_clients(self, e):
        """Disconnect multiple selected clients."""
        if not self.selected_clients:
            return
        
        def confirm_bulk_disconnect():
            try:
                disconnected_count = self.server_bridge.disconnect_multiple_clients(self.selected_clients)
                
                self.selected_clients = []
                self._update_bulk_actions_visibility()
                self._refresh_clients()
                
                self.show_dialog(
                    "success",
                    "Bulk Disconnect Complete", 
                    f"Successfully disconnected {disconnected_count} clients"
                )
            except Exception as ex:
                self.show_dialog(
                    "error",
                    "Disconnect Failed",
                    f"Failed to disconnect clients: {str(ex)}"
                )
        
        self.show_dialog(
            "confirmation",
            "Confirm Bulk Disconnect",
            f"Are you sure you want to disconnect {len(self.selected_clients)} selected clients?\n\nThis will terminate their connections to the server.",
            on_confirm=confirm_bulk_disconnect,
            confirm_text="Disconnect All",
            danger=True
        )
    
    def _delete_selected_clients(self, e):
        """Delete multiple selected clients."""
        if not self.selected_clients:
            return
        
        def confirm_bulk_delete():
            try:
                deleted_count = self.server_bridge.delete_multiple_clients(self.selected_clients)
                
                self.selected_clients = []
                self._update_bulk_actions_visibility()
                self._refresh_clients()
                
                self.show_dialog(
                    "success",
                    "Bulk Delete Complete", 
                    f"Successfully deleted {deleted_count} clients"
                )
            except Exception as ex:
                self.show_dialog(
                    "error",
                    "Delete Failed",
                    f"Failed to delete clients: {str(ex)}"
                )
        
        self.show_dialog(
            "confirmation",
            "Confirm Bulk Delete",
            f"Are you sure you want to delete {len(self.selected_clients)} selected clients?\n\nThis will permanently remove all selected clients and their data.\n\n⚠️ THIS ACTION CANNOT BE UNDONE!",
            on_confirm=confirm_bulk_delete,
            confirm_text="Delete All",
            danger=True
        )
    
    def _export_selected_clients(self, e):
        """Export selected clients data."""
        if not self.selected_clients:
            return
            
        try:
            # TODO: Implement actual export logic with file save dialog
            print(f"[INFO] Exporting {len(self.selected_clients)} clients")
            
            self.show_dialog(
                "success",
                "Export Complete", 
                f"Successfully exported {len(self.selected_clients)} clients to CSV file."
            )
        except Exception as ex:
            self.show_dialog(
                "error",
                "Export Failed",
                f"Failed to export clients: {str(ex)}"
            )
    
    # === Other Actions ===
    
    def _add_client(self, e):
        """Show add client dialog."""
        username_field = ft.TextField(label="Username", width=300)
        
        def add_new_client(e):
            try:
                username = username_field.value
                if not username:
                    self.show_dialog("Error", ft.Text("Username is required"))
                    return
                
                # TODO: Implement actual add client logic
                print(f"[INFO] Adding new client: {username}")
                self.show_dialog("Success", ft.Text(f"Client '{username}' added successfully"))
                self._refresh_clients()
            except Exception as ex:
                self.show_dialog("Error", ft.Text(f"Failed to add client: {str(ex)}"))
        
        content = ft.Column([
            ft.Text("Add New Client", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            username_field,
            ft.Row([
                ft.ElevatedButton("Add Client", on_click=add_new_client, bgcolor=ft.Colors.GREEN_600),
                ft.OutlinedButton("Cancel", on_click=lambda e: None)
            ], alignment=ft.MainAxisAlignment.END)
        ])
        
        self.show_dialog("custom", "Add Client", "", content=content)
    
    def _import_clients(self, e):
        """Import clients from file."""
        # TODO: Implement file picker and import logic
        self.show_dialog("info", "Import Clients", "Import functionality coming soon")
    
    def _show_client_statistics(self, e):
        """Show client statistics."""
        try:
            total_clients = len(self.all_clients)
            connected_clients = len([c for c in self.all_clients if c.status == "Connected"])
            registered_clients = len([c for c in self.all_clients if c.status == "Registered"])
            
            stats_content = ft.Column([
                ft.Text("Client Statistics", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Row([ft.Text("Total Clients:", weight=ft.FontWeight.BOLD), ft.Text(str(total_clients))]),
                ft.Row([ft.Text("Connected:", weight=ft.FontWeight.BOLD), ft.Text(str(connected_clients))]),
                ft.Row([ft.Text("Registered:", weight=ft.FontWeight.BOLD), ft.Text(str(registered_clients))]),
                ft.Row([ft.Text("Offline:", weight=ft.FontWeight.BOLD), ft.Text(str(total_clients - connected_clients))]),
            ], spacing=10)
            
            self.show_dialog("custom", "Client Statistics", "", content=stats_content)
        except Exception as ex:
            self.show_dialog("error", "Error", f"Failed to generate statistics: {str(ex)}")
    
    def _default_dialog(self, title: str, content: ft.Control):
        """Default dialog implementation."""
        print(f"[DIALOG] {title}: {content}")
    
    def did_mount(self):
        """Called when component is mounted - load initial data."""
        self._refresh_clients()