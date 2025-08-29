#!/usr/bin/env python3
"""
Client Table Renderer Component
Handles UI rendering of client data in tables with proper formatting and responsive design.
"""

import flet as ft
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from flet_server_gui.core.semantic_colors import get_status_color
# Unified theme system - consolidated theme functionality
from flet_server_gui.ui.unified_theme_system import TOKENS

# Add project root to path for imports
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from flet_server_gui.utils.server_bridge import ServerBridge
    from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
except ImportError:
    # Fallback to relative imports for direct execution
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
        from utils.server_bridge import ServerBridge
        from ui.widgets.buttons import ActionButtonFactory
    except ImportError:
        ServerBridge = object
        ActionButtonFactory = object


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
                ft.DataColumn(ft.Text("Client ID", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataColumn(ft.Text("Last Seen", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataColumn(ft.Text("Files", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataColumn(ft.Text("Total Size", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
            ],
            rows=[],
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            heading_row_color=TOKENS['surface_variant'],
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
        self.selected_clients = selected_clients or []
        
        for client in filtered_clients:
            # Client selection checkbox
            client_id = getattr(client, 'client_id', None) or (client['client_id'] if hasattr(client, '__getitem__') and 'client_id' in client else (client.get('id', 'Unknown') if hasattr(client, 'get') else 'Unknown'))
            
            # Create a wrapper function to capture the client_id
            def create_checkbox_handler(client_id):
                def handler(e):
                    # Call the parent's selection handler if provided
                    if on_client_select:
                        # Create a mock event with the client_id as data
                        class MockEvent:
                            def __init__(self, client_id, checked):
                                self.data = client_id
                                self.control = type('Control', (), {'value': checked})()
                        # Determine new state (opposite of current)
                        new_state = not (client_id in self.selected_clients)
                        mock_event = MockEvent(client_id, new_state)
                        on_client_select(mock_event)
                return handler
            
            client_checkbox = ft.Checkbox(
                value=client_id in self.selected_clients,
                on_change=create_checkbox_handler(client_id),
                data=client_id
            )
            
            # Status display with color coding
            status = getattr(client, 'status', None) or (client['status'] if hasattr(client, '__getitem__') and 'status' in client else (client.get('status', 'Unknown') if hasattr(client, 'get') else 'Unknown'))
            status_display = self._format_status_display(status)
            
            # Last seen formatting
            last_seen = getattr(client, 'last_seen', None) or (client['last_seen'] if hasattr(client, '__getitem__') and 'last_seen' in client else (client.get('last_seen', 'Unknown') if hasattr(client, 'get') else 'Unknown'))
            last_seen_display = self._format_last_seen(last_seen)
            
            # Total size formatting
            total_size = getattr(client, 'total_size', None) or (client['total_size'] if hasattr(client, '__getitem__') and 'total_size' in client else (client.get('total_size', 0) if hasattr(client, 'get') else 0))
            size_display = self._format_total_size(total_size)
            
            # Files count
            files_count = getattr(client, 'files_count', None) or (client['files_count'] if hasattr(client, '__getitem__') and 'files_count' in client else (client.get('files_count', 0) if hasattr(client, 'get') else 0))
            
            # Client ID
            client_id = getattr(client, 'client_id', None) or (client['client_id'] if hasattr(client, '__getitem__') and 'client_id' in client else (client.get('id', 'Unknown') if hasattr(client, 'get') else 'Unknown'))
            
            # Action buttons
            action_buttons = self._create_client_action_buttons(client)
            
            # Create table row
            self.client_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(client_checkbox),
                        ft.DataCell(ft.Text(client_id, size=12, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(status_display),
                        ft.DataCell(ft.Text(last_seen_display, size=11, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(str(files_count), max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(size_display, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(action_buttons),
                    ]
                )
            )
    
    def _format_status_display(self, status: str) -> ft.Control:
        """Format status with appropriate color coding"""
        # Use semantic color system for client status colors
        status_color_map = {
            "connected": "success",
            "registered": "info", 
            "offline": "warning"
        }
        semantic_status = status_color_map.get(status.lower(), "neutral")
        color = get_status_color(semantic_status)
        
        return ft.Container(
            content=ft.Text(
                status.title(),
                size=11,
                weight=ft.FontWeight.BOLD,
                color=TOKENS['on_primary']
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
        # Get client ID safely
        client_id = getattr(client, 'client_id', None) or (client['client_id'] if hasattr(client, '__getitem__') and 'client_id' in client else (client.get('id', 'Unknown') if hasattr(client, 'get') else 'Unknown'))
        print(f"[DEBUG] Creating action buttons for client: {client_id}")
        
        # Create wrapper functions to properly capture client_id
        def make_client_getter(client_id):
            def getter():
                result = [client_id]
                print(f"[DEBUG] Client getter returning: {result}")
                return result
            return getter
        
        print(f"[DEBUG] Creating client view details button for: {client_id}")
        view_details_button = self.button_factory.create_action_button(
            'client_view_details', 
            make_client_getter(client_id)
        )
        
        print(f"[DEBUG] Creating client view files button for: {client_id}")
        view_files_button = self.button_factory.create_action_button(
            'client_view_files', 
            make_client_getter(client_id)
        )
        
        print(f"[DEBUG] Creating client disconnect button for: {client_id}")
        disconnect_button = self.button_factory.create_action_button(
            'client_disconnect', 
            make_client_getter(client_id)
        )
        
        print(f"[DEBUG] Creating client delete button for: {client_id}")
        delete_button = self.button_factory.create_action_button(
            'client_delete', 
            make_client_getter(client_id)
        )
        
        buttons_row = ft.Row([
            view_details_button,
            view_files_button,
            disconnect_button,
            delete_button,
        ], tight=True, spacing=5)
        
        print(f"[DEBUG] Created action buttons row for client: {client_id}")
        return buttons_row
    
    def get_table_container(self) -> ft.Container:
        """Get the table wrapped in a responsive container"""
        if not self.client_table:
            self.create_client_table()
        
        # Ensure client_table is not None
        if not self.client_table:
            # Create a fallback table if needed
            self.client_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Client ID")),
                    ft.DataColumn(ft.Text("Status")),
                ],
                rows=[]
            )
        
        # Create a scrollable container for the table with proper responsive properties
        table_scroll_container = ft.Container(
            content=ft.Column([
                self.client_table
            ], scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE
        )
        
        # Wrap in a responsive container with proper sizing
        return ft.Container(
            content=table_scroll_container,
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            padding=10,
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            width=float("inf")  # Allow infinite width for proper scaling
        )
    
    def update_table_data(self, filtered_clients: List[Any], on_client_select: callable = None, 
                         selected_clients: List[str] = None) -> None:
        """Update table with new data"""
        if selected_clients is None:
            selected_clients = self.selected_clients
            
        self.populate_client_table(filtered_clients, on_client_select, selected_clients)
        self.update_table_display()
    
    def update_table_display(self) -> None:
        """Update the table display"""
        if self.page and self.client_table:
            self.page.update()
    
    def select_all_rows(self) -> None:
        """Select all rows in the table"""
        if not self.client_table:
            return
            
        # Update all checkboxes in the table
        for row in self.client_table.rows:
            if row.cells and len(row.cells) > 0:
                checkbox = row.cells[0].content
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.value = True
                    
        if self.page:
            self.page.update()
    
    def deselect_all_rows(self) -> None:
        """Deselect all rows in the table"""
        if not self.client_table:
            return
            
        # Update all checkboxes in the table
        for row in self.client_table.rows:
            if row.cells and len(row.cells) > 0:
                checkbox = row.cells[0].content
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.value = False
                    
        if self.page:
            self.page.update()