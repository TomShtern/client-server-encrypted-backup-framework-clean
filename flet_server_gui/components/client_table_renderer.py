#!/usr/bin/env python3
"""
Client Table Renderer Component (CONSOLIDATED)
Handles UI rendering of client data in tables with proper formatting and responsive design.
Inherits from BaseTableRenderer to eliminate code duplication.

CONSOLIDATION BENEFITS:
- Removed ~150 lines of duplicate code (checkbox handlers, styling, selection management)
- Inherited standardized table creation, container wrapping, and update methods
- Leverages common formatting utilities from base class
- Maintains all original functionality while reducing maintenance overhead
"""

import flet as ft
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from flet_server_gui.core.semantic_colors import get_status_color
from flet_server_gui.core.theme_compatibility import TOKENS

# Add project root to path for imports
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from flet_server_gui.utils.server_bridge import ServerBridge
    from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
    from .base_table_renderer import BaseTableRenderer
except ImportError:
    # Fallback to relative imports for direct execution
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
        from utils.server_bridge import ServerBridge
        from ui.widgets.buttons import ActionButtonFactory
        from base_table_renderer import BaseTableRenderer
    except ImportError:
        ServerBridge = object
        ActionButtonFactory = object
        BaseTableRenderer = object


class ClientTableRenderer(BaseTableRenderer):
    """Handles rendering of client data in table format using consolidated base functionality"""
    
    def __init__(self, server_bridge: ServerBridge, button_factory: ActionButtonFactory, page: ft.Page):
        super().__init__(server_bridge, button_factory, page)
        # Client-specific aliases for backward compatibility
        self.client_table = self.table
        self.selected_clients = self.selected_items
    
    # Abstract method implementations for client-specific table structure
    
    def get_table_columns(self) -> List[ft.DataColumn]:
        """Get client table columns"""
        return [
            ft.DataColumn(ft.Checkbox(on_change=None)),  # Select all handled by parent
            ft.DataColumn(self.create_bold_header("Client ID")),
            ft.DataColumn(self.create_bold_header("Status")),
            ft.DataColumn(self.create_bold_header("Last Seen")),
            ft.DataColumn(self.create_bold_header("Files")),
            ft.DataColumn(self.create_bold_header("Total Size")),
            ft.DataColumn(self.create_bold_header("Actions")),
        ]
    
    def get_item_identifier(self, client: Any) -> str:
        """Get client identifier"""
        return getattr(client, 'client_id', None) or (
            client['client_id'] if hasattr(client, '__getitem__') and 'client_id' in client else (
                client.get('id', 'Unknown') if hasattr(client, 'get') else 'Unknown'
            )
        )
    
    def create_row_cells(self, client: Any, on_client_select: Callable) -> List[ft.DataCell]:
        """Create client table row cells"""
        client_id = self.get_item_identifier(client)
        
        # Selection checkbox using base class method
        client_checkbox = self.create_selection_checkbox(client_id, on_client_select)
        
        # Status display with color coding
        status = getattr(client, 'status', None) or (
            client['status'] if hasattr(client, '__getitem__') and 'status' in client else (
                client.get('status', 'Unknown') if hasattr(client, 'get') else 'Unknown'
            )
        )
        status_display = self._format_status_display(status)
        
        # Last seen formatting using base class method
        last_seen = getattr(client, 'last_seen', None) or (
            client['last_seen'] if hasattr(client, '__getitem__') and 'last_seen' in client else (
                client.get('last_seen', 'Unknown') if hasattr(client, 'get') else 'Unknown'
            )
        )
        last_seen_display = self.format_date_relative(last_seen)
        
        # Total size formatting using base class method
        total_size = getattr(client, 'total_size', None) or (
            client['total_size'] if hasattr(client, '__getitem__') and 'total_size' in client else (
                client.get('total_size', 0) if hasattr(client, 'get') else 0
            )
        )
        size_display = self.format_file_size(total_size)
        
        # Files count
        files_count = getattr(client, 'files_count', None) or (
            client['files_count'] if hasattr(client, '__getitem__') and 'files_count' in client else (
                client.get('files_count', 0) if hasattr(client, 'get') else 0
            )
        )
        
        # Action buttons
        action_buttons = self._create_client_action_buttons(client)
        
        return [
            ft.DataCell(client_checkbox),
            ft.DataCell(self.create_compact_text(client_id)),
            ft.DataCell(status_display),
            ft.DataCell(self.create_compact_text(last_seen_display, size=11)),
            ft.DataCell(self.create_compact_text(str(files_count))),
            ft.DataCell(self.create_compact_text(size_display)),
            ft.DataCell(action_buttons),
        ]
    
    def create_client_table(self) -> ft.DataTable:
        """Create client table using base class (backward compatibility)"""
        self.client_table = self.create_base_table()
        return self.client_table
    
    def populate_client_table(self, filtered_clients: List[Any], on_client_select: callable, 
                             selected_clients: List[str]) -> None:
        """Populate client table using base class (backward compatibility)"""
        self.populate_table(filtered_clients, on_client_select, selected_clients)
        # Update aliases for backward compatibility
        self.selected_clients = self.selected_items
        self.client_table = self.table
    
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
    
    # Client-specific formatting methods (unique to client table)
    
    
    def _create_client_action_buttons(self, client) -> ft.Row:
        """Create action buttons for a client row"""
        # Get client ID safely
        client_id = getattr(client, 'client_id', None) or (client['client_id'] if hasattr(client, '__getitem__') and 'client_id' in client else (client.get('id', 'Unknown') if hasattr(client, 'get') else 'Unknown'))
        
        # Create wrapper functions to properly capture client_id
        def make_client_getter(client_id):
            def getter():
                result = [client_id]
                return result
            return getter
        
        view_details_button = self.button_factory.create_action_button(
            'client_view_details', 
            make_client_getter(client_id)
        )
        
        view_files_button = self.button_factory.create_action_button(
            'client_view_files', 
            make_client_getter(client_id)
        )
        
        disconnect_button = self.button_factory.create_action_button(
            'client_disconnect', 
            make_client_getter(client_id)
        )
        
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
        
        return buttons_row
    
    # Backward compatibility aliases that delegate to base class
    
    def update_table_data(self, filtered_clients: List[Any], on_client_select: callable = None, 
                         selected_clients: List[str] = None) -> None:
        """Update table with new data using base class"""
        super().update_table_data(filtered_clients, on_client_select, selected_clients)
        # Update aliases for backward compatibility
        self.selected_clients = self.selected_items
        self.client_table = self.table
    
    
    def select_all_rows(self) -> None:
        """Select all rows using base class"""
        super().select_all_rows()
        self.selected_clients = self.selected_items
    
    def deselect_all_rows(self) -> None:
        """Deselect all rows using base class"""
        super().deselect_all_rows()
        self.selected_clients = self.selected_items
    
    # Additional backward compatibility methods
    
    def get_table_container(self) -> ft.Container:
        """Get table container using base class (backward compatibility)"""
        container = super().get_table_container()
        self.client_table = self.table  # Ensure alias is updated
        return container