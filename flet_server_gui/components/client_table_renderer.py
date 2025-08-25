#!/usr/bin/env python3
"""
Client Table Renderer Component
Handles UI rendering of client data in tables with proper formatting and responsive design.
"""

import flet as ft
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..utils.server_bridge import ServerBridge
from .button_factory import ActionButtonFactory


class ClientTableRenderer:
    """Handles rendering of client data in table format"""
    
    def __init__(self, server_bridge: ServerBridge, button_factory: ActionButtonFactory, page: ft.Page):
        self.server_bridge = server_bridge
        self.button_factory = button_factory
        self.page = page
        
        # Table components
        self.client_table = None
        self.selected_clients = []
    
    def create_client_table(self) -> ft.DataTable:
        """Create the client data table with headers"""
        self.client_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Checkbox(on_change=None)),  # Select all will be handled by parent
                ft.DataColumn(ft.Text("Client ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Last Seen", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Files", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Total Size", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            heading_row_color=ft.Colors.ON_SURFACE_VARIANT,
            heading_row_height=50,
            data_row_max_height=60,
            show_checkbox_column=False,  # We handle checkboxes manually
        )
        return self.client_table
    
    def populate_client_table(self, filtered_clients: List[Any], on_client_select: callable, 
                             selected_clients: List[str]) -> None:
        """Populate the client table with filtered client data"""
        if not self.client_table:
            return
        
        self.client_table.rows.clear()
        self.selected_clients = selected_clients
        
        for client in filtered_clients:
            # Client selection checkbox
            client_checkbox = ft.Checkbox(
                value=client.client_id in selected_clients,
                on_change=on_client_select,
                data=client.client_id
            )
            
            # Status display with color coding
            status_display = self._format_status_display(client.status)
            
            # Last seen formatting
            last_seen_display = self._format_last_seen(client.last_seen)
            
            # Total size formatting
            size_display = self._format_total_size(getattr(client, 'total_size', 0))
            
            # Action buttons
            action_buttons = self._create_client_action_buttons(client)
            
            # Create table row
            self.client_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(client_checkbox),
                        ft.DataCell(ft.Text(client.client_id, size=12)),
                        ft.DataCell(status_display),
                        ft.DataCell(ft.Text(last_seen_display, size=11)),
                        ft.DataCell(ft.Text(str(getattr(client, 'files_count', 0)))),
                        ft.DataCell(ft.Text(size_display)),
                        ft.DataCell(action_buttons),
                    ]
                )
            )
    
    def _format_status_display(self, status: str) -> ft.Control:
        """Format status with appropriate color coding"""
        status_colors = {
            "connected": ft.Colors.GREEN_600,
            "registered": ft.Colors.BLUE_600,
            "offline": ft.Colors.ORANGE_600,
        }
        
        color = status_colors.get(status.lower(), ft.Colors.GREY_600)
        
        return ft.Container(
            content=ft.Text(
                status.title(),
                size=11,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE
            ),
            bgcolor=color,
            padding=ft.Padding(4, 2, 4, 2),
            border_radius=4
        )
    
    def _format_last_seen(self, last_seen: str) -> str:
        """Format last seen time to human-readable format with relative time display"""
        try:
            if not last_seen or last_seen == "Unknown":
                return "Unknown"
            
            # Parse the datetime string
            last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
            now = datetime.now()
            
            # Calculate time difference
            diff = now - last_seen_dt.replace(tzinfo=None)
            
            # Use the more sophisticated relative time formatting from real_data_clients.py
            if diff.total_seconds() < 300:  # 5 minutes
                return "Just now"
            elif diff.total_seconds() < 3600:  # 1 hour
                minutes = int(diff.total_seconds() / 60)
                return f"{minutes}m ago"
            elif diff.days > 0:
                return last_seen_dt.strftime('%Y-%m-%d %H:%M')
            else:
                hours = int(diff.total_seconds() / 3600)
                return f"{hours}h ago"
                
        except (ValueError, AttributeError) as e:
            return "Unknown"
    
    def _format_total_size(self, total_size: int) -> str:
        """Format total size to human-readable format"""
        if not total_size or total_size == 0:
            return "0 B"
        
        # Convert bytes to appropriate unit
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if total_size < 1024.0:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024.0
        return f"{total_size:.1f} PB"
    
    def _create_client_action_buttons(self, client) -> ft.Row:
        """Create action buttons for a client row"""
        return ft.Row([
            self.button_factory.create_action_button(
                'client_view_details', 
                lambda c=client: [c.client_id]
            ),
            self.button_factory.create_action_button(
                'client_view_files', 
                lambda c=client: [c.client_id]
            ),
            self.button_factory.create_action_button(
                'client_disconnect', 
                lambda c=client: [c.client_id]
            ),
            self.button_factory.create_action_button(
                'client_delete', 
                lambda c=client: [c.client_id]
            ),
        ], tight=True, spacing=5)
    
    def get_table_container(self) -> ft.Container:
        """Get the table wrapped in a responsive container"""
        if not self.client_table:
            self.create_client_table()
        
        return ft.Container(
            content=ft.Column([
                self.client_table
            ], scroll=ft.ScrollMode.AUTO),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
            expand=True
        )
    
    def update_table_display(self) -> None:
        """Update table display after changes"""
        if self.page:
            self.page.update()