#!/usr/bin/env python3
"""
Table Consolidation Utilities for FletV2
Standardized table creation and update patterns to eliminate repeated DataTable implementations.
"""

import flet as ft
from typing import List, Dict, Any, Optional, Callable, Union
from utils.debug_setup import get_logger

logger = get_logger(__name__)


class TableManager:
    """
    Centralized table management with standardized patterns.
    Replaces the repeated DataTable creation and update patterns found across view files.
    """
    
    @staticmethod
    def create_data_table(
        columns: List[Dict[str, Any]],
        rows: Optional[List[Dict[str, Any]]] = None,
        column_spacing: Optional[float] = 56.0,
        horizontal_lines: bool = True,
        show_checkbox_column: bool = False,
        show_bottom_border: bool = True
    ) -> ft.DataTable:
        """
        Create standardized DataTable with consistent styling.
        
        Args:
            columns: List of column definitions [{"key": "name", "label": "Name", "width": 150}]
            rows: List of row data [{"name": "John", "status": "Active"}]
            column_spacing: Spacing between columns
            horizontal_lines: Show horizontal grid lines
            show_checkbox_column: Show selection checkboxes
            show_bottom_border: Show border at bottom
        """
        # Create DataColumn objects from column definitions
        data_columns = []
        for col in columns:
            column_label = col.get("label", col.get("key", ""))
            column_width = col.get("width")
            
            data_columns.append(
                ft.DataColumn(
                    label=ft.Text(
                        column_label,
                        weight=ft.FontWeight.BOLD,
                        size=14
                    ),
                    tooltip=col.get("tooltip")
                )
            )
        
        # Create initial empty table
        table = ft.DataTable(
            columns=data_columns,
            rows=[],
            column_spacing=column_spacing,
            horizontal_lines=horizontal_lines,
            show_checkbox_column=show_checkbox_column,
            show_bottom_border=show_bottom_border,
            expand=True
        )
        
        # Populate rows if provided
        if rows:
            TableManager.update_table_data(table, rows, columns)
        
        return table
    
    @staticmethod
    def update_table_data(
        table: ft.DataTable,
        rows: List[Dict[str, Any]],
        columns: List[Dict[str, Any]],
        auto_update: bool = True
    ):
        """
        Update table data while preserving table structure.
        
        Args:
            table: DataTable to update
            rows: New row data
            columns: Column definitions (for key mapping)
            auto_update: Whether to call table.update() automatically
        """
        try:
            # Clear existing rows
            table.rows.clear()
            
            # Add new rows
            for row_data in rows:
                cells = []
                for col in columns:
                    key = col.get("key", "")
                    value = row_data.get(key, "")
                    
                    # Handle different value types
                    if isinstance(value, str):
                        cell_content = ft.Text(value, size=13)
                    elif isinstance(value, (int, float)):
                        cell_content = ft.Text(str(value), size=13)
                    elif isinstance(value, ft.Control):
                        cell_content = value
                    else:
                        cell_content = ft.Text(str(value), size=13)
                    
                    cells.append(ft.DataCell(cell_content))
                
                table.rows.append(ft.DataRow(cells=cells))
            
            if auto_update:
                table.update()
                
        except Exception as e:
            logger.error(f"Failed to update table data: {e}")
    
    @staticmethod
    def create_action_button(
        text: str,
        on_click: Callable,
        style: str = "primary",
        size: str = "small",
        icon: Optional[str] = None
    ) -> ft.Control:
        """
        Create standardized action button for table cells.
        
        Args:
            text: Button text
            on_click: Click handler
            style: Button style ('primary', 'secondary', 'danger', 'success')
            size: Button size ('small', 'medium', 'large')
            icon: Optional icon name
        """
        # Style mapping
        style_map = {
            'primary': ft.Colors.BLUE,
            'secondary': ft.Colors.GREY,
            'danger': ft.Colors.RED,
            'success': ft.Colors.GREEN
        }
        
        # Size mapping
        size_map = {
            'small': 12,
            'medium': 14,
            'large': 16
        }
        
        button_kwargs = {
            "text": text,
            "on_click": on_click,
            "style": ft.ButtonStyle(
                bgcolor=style_map.get(style, ft.Colors.BLUE),
                color=ft.Colors.WHITE
            )
        }
        
        if icon:
            button_kwargs["icon"] = icon
        
        if size in size_map:
            button_kwargs["style"].text_style = ft.TextStyle(
                size=size_map[size]
            )
        
        return ft.ElevatedButton(**button_kwargs)
    
    @staticmethod
    def create_status_chip(
        status: str,
        color_mapping: Optional[Dict[str, str]] = None
    ) -> ft.Container:
        """
        Create standardized status chip for table cells.
        
        Args:
            status: Status text
            color_mapping: Custom color mapping for status values
        """
        # Default color mapping
        default_colors = {
            "active": ft.Colors.GREEN,
            "inactive": ft.Colors.RED,
            "pending": ft.Colors.ORANGE,
            "connected": ft.Colors.GREEN,
            "disconnected": ft.Colors.RED,
            "online": ft.Colors.GREEN,
            "offline": ft.Colors.RED,
            "success": ft.Colors.GREEN,
            "error": ft.Colors.RED,
            "warning": ft.Colors.ORANGE,
            "info": ft.Colors.BLUE
        }
        
        colors = color_mapping or default_colors
        status_lower = status.lower()
        color = colors.get(status_lower, ft.Colors.GREY)
        
        return ft.Container(
            content=ft.Text(
                status,
                color=ft.Colors.WHITE,
                size=11,
                weight=ft.FontWeight.BOLD
            ),
            bgcolor=color,
            border_radius=12,
            padding=ft.Padding(8, 4, 8, 4)
        )


class TableBuilder:
    """
    Builder pattern for creating complex tables with actions.
    Simplifies the repeated patterns of table creation with action columns.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.columns = []
        self.rows = []
        self.action_handlers = {}
    
    def add_column(
        self,
        key: str,
        label: str,
        width: Optional[float] = None,
        tooltip: Optional[str] = None
    ) -> 'TableBuilder':
        """Add a data column to the table."""
        self.columns.append({
            "key": key,
            "label": label,
            "width": width,
            "tooltip": tooltip
        })
        return self
    
    def add_action_column(
        self,
        label: str = "Actions",
        actions: Optional[List[Dict[str, Any]]] = None
    ) -> 'TableBuilder':
        """
        Add an actions column with standardized buttons.
        
        Args:
            label: Column label
            actions: List of action definitions [{"text": "Edit", "handler": "edit", "style": "primary"}]
        """
        self.columns.append({
            "key": "_actions",
            "label": label,
            "width": 150
        })
        
        if actions:
            for action in actions:
                handler_key = action.get("handler", action.get("text", "").lower())
                self.action_handlers[handler_key] = action
        
        return self
    
    def set_data(self, rows: List[Dict[str, Any]]) -> 'TableBuilder':
        """Set table row data."""
        self.rows = rows
        return self
    
    def build(self) -> ft.DataTable:
        """Build the final DataTable with all configurations."""
        # Process rows to add action buttons
        processed_rows = []
        for row_data in self.rows:
            processed_row = row_data.copy()
            
            # Add action buttons if action column exists
            if any(col.get("key") == "_actions" for col in self.columns):
                actions_row = ft.Row(spacing=4)
                
                for handler_key, action_config in self.action_handlers.items():
                    button = TableManager.create_action_button(
                        text=action_config.get("text", handler_key.title()),
                        on_click=lambda e, row=row_data, handler=handler_key: self._handle_action(row, handler),
                        style=action_config.get("style", "primary"),
                        size="small",
                        icon=action_config.get("icon")
                    )
                    actions_row.controls.append(button)
                
                processed_row["_actions"] = actions_row
            
            processed_rows.append(processed_row)
        
        return TableManager.create_data_table(
            columns=self.columns,
            rows=processed_rows
        )
    
    def _handle_action(self, row_data: Dict[str, Any], handler_key: str):
        """Handle action button clicks."""
        try:
            if handler_key in self.action_handlers:
                handler_config = self.action_handlers[handler_key]
                callback = handler_config.get("callback")
                if callback:
                    callback(row_data)
        except Exception as e:
            logger.error(f"Action handler failed for {handler_key}: {e}")


def create_simple_table(
    columns: List[str],
    rows: List[List[str]],
    show_headers: bool = True
) -> ft.DataTable:
    """
    Quick factory for simple string-based tables.
    
    Example:
        table = create_simple_table(
            columns=["Name", "Status", "Size"],
            rows=[
                ["file1.txt", "Active", "1.2 MB"],
                ["file2.txt", "Inactive", "2.1 MB"]
            ]
        )
    """
    column_defs = [{"key": f"col_{i}", "label": col} for i, col in enumerate(columns)]
    
    row_dicts = []
    for row in rows:
        row_dict = {}
        for i, value in enumerate(row):
            row_dict[f"col_{i}"] = value
        row_dicts.append(row_dict)
    
    return TableManager.create_data_table(column_defs, row_dicts)


def update_table_with_loading(
    table: ft.DataTable,
    data_loader: Callable,
    columns: List[Dict[str, Any]],
    loading_message: str = "Loading...",
    error_message: str = "Failed to load data"
) -> None:
    """
    Update table with loading state and error handling.
    Standardizes the repeated pattern of async table updates.
    
    Example:
        def load_clients():
            return server_bridge.get_clients()
        
        update_table_with_loading(
            clients_table,
            load_clients,
            client_columns,
            "Loading clients...",
            "Failed to load client data"
        )
    """
    try:
        # Show loading state
        table.rows.clear()
        table.rows.append(
            ft.DataRow([
                ft.DataCell(ft.Row([
                    ft.ProgressRing(width=16, height=16),
                    ft.Text(loading_message, size=12)
                ], spacing=8))
            ])
        )
        table.update()
        
        # Load data
        data = data_loader()
        
        # Update with real data
        TableManager.update_table_data(table, data, columns)
        
    except Exception as e:
        logger.error(f"Table loading failed: {e}")
        
        # Show error state
        table.rows.clear()
        table.rows.append(
            ft.DataRow([
                ft.DataCell(ft.Row([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=16, color=ft.Colors.RED),
                    ft.Text(f"{error_message}: {str(e)}", size=12, color=ft.Colors.RED)
                ], spacing=8))
            ])
        )
        table.update()