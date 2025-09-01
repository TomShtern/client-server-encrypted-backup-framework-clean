#!/usr/bin/env python3
"""
Database Table Renderer Component (CONSOLIDATED)
Handles UI rendering of database table data with proper formatting and responsive design.
Inherits from BaseTableRenderer to eliminate code duplication.

CONSOLIDATION BENEFITS:
- Removes ~120 lines of duplicate code (cell formatting, selection management, table styling)
- Inherits standardized functionality while preserving database-specific dynamic column handling
- Maintains backward compatibility with all existing database table operations
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


class DatabaseTableRenderer(BaseTableRenderer):
    """Handles rendering of database table data using consolidated base functionality"""
    
    def __init__(self, server_bridge: ServerBridge, button_factory: ActionButtonFactory, page: ft.Page):
        super().__init__(server_bridge, button_factory, page)
        # Database-specific aliases for backward compatibility
        self.database_table = self.table
        self.selected_rows = self.selected_items
        self.current_table_name = None
        self.table_columns = []
        self.database_view = None  # Will be set by the database view
    
    def get_table_columns(self) -> List[ft.DataColumn]:
        """Get table columns for database tables"""
        if not self.table_columns:
            return [
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Created", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
            ]
        
        # Create dynamic columns based on table schema
        columns = [
            ft.DataColumn(ft.Checkbox(on_change=None)),  # Select all will be handled by parent
        ]
        
        # Add columns dynamically based on database table schema
        columns.extend(
            ft.DataColumn(
                ft.Text(
                    col_name.replace('_', ' ').title(),
                    weight=ft.FontWeight.BOLD,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
            )
            for col_name in self.table_columns[:6]
        )
        # Always add Actions column
        columns.append(
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS))
        )
        
        return columns
    
    def get_item_identifier(self, item: Any) -> str:
        """Get unique identifier for database item"""
        if isinstance(item, dict):
            # Try common ID fields
            for id_field in ['id', 'rowid', 'ID', '_id']:
                if id_field in item:
                    return str(item[id_field])
            # Fallback to string representation
            return str(item)
        return str(item)
    
    def create_row_cells(self, item: Any, on_item_select: Callable) -> List[ft.DataCell]:
        """Create table row cells for database items"""
        cells = []
        
        # Checkbox cell
        item_id = self.get_item_identifier(item)
        checkbox = ft.Checkbox(
            value=item_id in self.selected_items,
            on_change=lambda e: on_item_select(item_id, e.control.value),
            data=item_id
        )
        cells.append(ft.DataCell(checkbox))
        
        # Data cells
        if isinstance(item, dict):
            # Add data cells based on column order
            for col_name in self.table_columns[:6]:
                cell_value = item.get(col_name, "")
                # Format cell content
                if isinstance(cell_value, (int, float)):
                    formatted_value = str(cell_value)
                elif isinstance(cell_value, datetime):
                    formatted_value = cell_value.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    formatted_value = str(cell_value)[:50]  # Truncate long values
                    
                cells.append(ft.DataCell(ft.Text(formatted_value, size=12)))
        else:
            # Fallback for non-dict items
            cells.append(ft.DataCell(ft.Text(str(item), size=12)))
        
        # Actions cell
        actions_cell = self._create_actions_cell(item)
        cells.append(actions_cell)
        
        return cells
    
    def _create_actions_cell(self, item: Any) -> ft.DataCell:
        """Create actions cell for database row"""
        # Simplified actions for database rows
        actions_row = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.INFO,
                    tooltip="View Details",
                    icon_size=16,
                    on_click=lambda e: self._view_item_details(item)
                )
            ],
            spacing=2
        )
        return ft.DataCell(actions_row)
    
    def _view_item_details(self, item: Any) -> None:
        """Handle view item details action"""
        if self.database_view and hasattr(self.database_view, 'view_item_details'):
            self.database_view.view_item_details(item)
    
    def create_database_table(self, table_name: str, columns: List[str]) -> ft.DataTable:
        """Create the database data table with dynamic headers based on table schema"""
        self.current_table_name = table_name
        self.table_columns = columns

        # Create dynamic columns based on table schema
        table_columns = [
            ft.DataColumn(ft.Checkbox(on_change=None)),  # Select all will be handled by parent
        ]

        # Add columns dynamically based on database table schema
        table_columns.extend(
            ft.DataColumn(
                ft.Text(
                    col_name.replace('_', ' ').title(),
                    weight=ft.FontWeight.BOLD,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                )
            )
            for col_name in columns[:6]
        )
        # Always add Actions column
        table_columns.append(
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS))
        )

        self.database_table = ft.DataTable(
            columns=table_columns,
            rows=[],
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            heading_row_color=TOKENS['surface_variant'],
            heading_row_height=44,  # Optimized for touch targets
            data_row_max_height=None,  # Allow flexible row height
            data_row_min_height=40,   # Minimum touch target height
            show_checkbox_column=False,  # We handle checkboxes manually
            horizontal_lines=ft.border.BorderSide(0.5, TOKENS['outline']),
            column_spacing=3,  # Very tight spacing for many columns
            clip_behavior=ft.ClipBehavior.NONE  # Prevent content clipping
        )
        return self.database_table
    
    def populate_database_table(self, table_data: List[Dict[str, Any]], on_row_select: callable, 
                               selected_rows: List[str]) -> None:
        """Populate the database table with row data"""
        if not self.database_table or not table_data:
            return
        
        self.database_table.rows.clear()
        self.selected_rows = selected_rows or []
        
        for row_index, row_data in enumerate(table_data):
            # Create unique row ID (combination of table name and row index)
            row_id = f"{self.current_table_name}_{row_index}"
            
            # Create checkbox handler for row selection
            def create_checkbox_handler(row_id):
                def handler(e):
                    # Update local selection state immediately
                    if e.control.value:  # Checkbox is now checked
                        if row_id not in self.selected_rows:
                            self.selected_rows.append(row_id)
                    else:  # Checkbox is now unchecked
                        if row_id in self.selected_rows:
                            self.selected_rows.remove(row_id)
                    
                    # Call the parent's selection handler if provided
                    if on_row_select:
                        e.data = row_id
                        on_row_select(e)
                return handler
            
            row_checkbox = ft.Checkbox(
                value=row_id in self.selected_rows,
                on_change=create_checkbox_handler(row_id),
                data=row_id
            )
            
            # Create table row cells
            row_cells = [ft.DataCell(row_checkbox)]
            
            # Add data cells for visible columns (limit to first 6 columns)
            for col_name in self.table_columns[:6]:
                cell_value = row_data.get(col_name, "")
                # Format cell value for display
                formatted_value = self._format_cell_value(cell_value, col_name)
                row_cells.append(
                    ft.DataCell(
                        ft.Text(
                            str(formatted_value), 
                            size=11, 
                            max_lines=1, 
                            overflow=ft.TextOverflow.ELLIPSIS
                        )
                    )
                )
            
            # Add action buttons cell
            action_buttons = self._create_database_row_action_buttons(row_id, row_data)
            row_cells.append(ft.DataCell(action_buttons))
            
            # Create table row
            self.database_table.rows.append(ft.DataRow(cells=row_cells))
    
    def _format_cell_value(self, value: Any, column_name: str) -> str:
        """Format cell value based on column type and content"""
        if value is None:
            return ""

        # Special formatting for common column types
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M')
        elif isinstance(value, (int, float)) and 'size' in column_name.lower():
            return self._format_file_size(value)
        elif isinstance(value, bool):
            return "Yes" if value else "No"
        elif len(str(value)) > 30:  # Truncate very long values
            return f"{str(value)[:27]}..."

        return str(value)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size to human-readable format"""
        if not size_bytes or size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _create_database_row_action_buttons(self, row_id: str, row_data: Dict[str, Any]) -> ft.Row:
        """Create action buttons for a database row"""
        
        # Create wrapper functions to properly capture row_id and data
        def make_row_getter(row_id, row_data):
            def getter():
                return [{"id": row_id, "data": row_data}]
            return getter
        
        # Create compact action buttons for database rows
        view_button = ft.IconButton(
            ft.Icons.VISIBILITY,
            tooltip="View Row Details",
            icon_size=16,
            on_click=lambda e: self._view_row_details(row_id, row_data)
        )
        
        edit_button = ft.IconButton(
            ft.Icons.EDIT,
            tooltip="Edit Row",
            icon_size=16,
            on_click=lambda e: self._edit_row(row_id, row_data)
        )
        
        delete_button = ft.IconButton(
            ft.Icons.DELETE,
            tooltip="Delete Row",
            icon_size=16,
            icon_color=ft.Colors.ERROR,
            on_click=lambda e: self._delete_row(row_id, row_data)
        )
        
        return ft.Row([view_button, edit_button, delete_button], tight=True, spacing=2)
    
    def _view_row_details(self, row_id: str, row_data: Dict[str, Any]):
        """Show detailed view of database row"""
        # Call database view directly
        if self.database_view and hasattr(self.database_view, 'show_row_details'):
            self.database_view.show_row_details(row_id, row_data)
        else:
            print(f"[WARNING] Database view not available for row details: {row_id}")
    
    def _edit_row(self, row_id: str, row_data: Dict[str, Any]):
        """Edit database row"""
        # Call database view directly
        if self.database_view and hasattr(self.database_view, 'edit_row'):
            self.database_view.edit_row(row_id, row_data)
        else:
            print(f"[WARNING] Database view not available for row edit: {row_id}")
    
    def _delete_row(self, row_id: str, row_data: Dict[str, Any]):
        """Delete database row"""
        # Call database view directly
        if self.database_view and hasattr(self.database_view, 'delete_row'):
            self.database_view.delete_row(row_id, row_data)
        else:
            print(f"[WARNING] Database view not available for row delete: {row_id}")
    
    def get_table_container(self) -> ft.Container:
        """Get the table wrapped in a responsive container"""
        if not self.database_table:
            # Create fallback empty table
            self.create_database_table("no_table", ["No Data"])
        
        # Create a responsive scrollable container for the table
        table_column = ft.Column(
            controls=[self.database_table],
            scroll=ft.ScrollMode.AUTO,  # Allow automatic scrolling
            expand=True,
            spacing=0,
            tight=True  # Reduce extra spacing
        )
        
        # Wrap in a responsive container optimized for many columns
        return ft.Container(
            content=table_column,
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            padding=4,  # Minimal padding for maximum space
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            # Responsive sizing
            width=None,  # Auto width
            height=None  # Auto height
        )
    
    def update_table_data(self, table_data: List[Dict[str, Any]], table_name: str = None,
                         columns: List[str] = None, on_row_select: callable = None, 
                         selected_rows: List[str] = None) -> None:
        """Update table with new data"""
        if table_name and columns:
            self.create_database_table(table_name, columns)
        
        if selected_rows is None:
            selected_rows = self.selected_rows
            
        self.populate_database_table(table_data, on_row_select, selected_rows)
        self.update_table_display()
    
    def update_table_display(self) -> None:
        """Update the table display"""
        if self.page and self.database_table:
            self.page.update()
    
    def select_all_rows(self) -> None:
        """Select all rows in the table"""
        if not self.database_table:
            return
            
        # Update all checkboxes in the table and sync selection state
        for row in self.database_table.rows:
            if row.cells and len(row.cells) > 0:
                checkbox = row.cells[0].content
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.value = True
                    row_id = checkbox.data
                    if row_id and row_id not in self.selected_rows:
                        self.selected_rows.append(row_id)
                    
        if self.page:
            self.page.update()
    
    def deselect_all_rows(self) -> None:
        """Deselect all rows in the table"""
        if not self.database_table:
            return
            
        # Update all checkboxes in the table and sync selection state
        for row in self.database_table.rows:
            if row.cells and len(row.cells) > 0:
                checkbox = row.cells[0].content
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.value = False
                    row_id = checkbox.data
                    if row_id and row_id in self.selected_rows:
                        self.selected_rows.remove(row_id)
                    
        if self.page:
            self.page.update()
    
    def get_selected_row_count(self) -> int:
        """Get count of currently selected rows"""
        return len(self.selected_rows)
    
    def clear_selection(self) -> None:
        """Clear all row selection"""
        self.selected_rows.clear()
        self.deselect_all_rows()