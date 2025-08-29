#!/usr/bin/env python3
"""
Enhanced Table Components - Advanced table system with animations and Material Design 3

Purpose: Provide consistent, animated table components with proper styling
Logic: Table creation, data handling, sorting, filtering, and pagination
UI: Material Design 3 styled tables with interactive features
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import logging
import random
from datetime import datetime
from flet_server_gui.ui.unified_theme_system import TOKENS

logger = logging.getLogger(__name__)


class TableSize(Enum):
    """Table sizes"""
    SMALL = "small"    # Compact rows
    MEDIUM = "medium"  # Default row height
    LARGE = "large"    # Spacious rows


class SortDirection(Enum):
    """Sort directions"""
    ASC = "asc"
    DESC = "desc"


@dataclass
class TableColumn:
    """Table column definition"""
    name: str
    label: str
    sortable: bool = True
    filterable: bool = True
    width: Optional[int] = None
    text_align: ft.TextAlign = ft.TextAlign.LEFT
    numeric: bool = False


@dataclass
class TableConfig:
    """Configuration for enhanced tables"""
    columns: List[TableColumn] = field(default_factory=list)
    data: List[Dict[str, Any]] = field(default_factory=list)
    size: TableSize = TableSize.MEDIUM
    show_header: bool = True
    show_footer: bool = True
    show_checkboxes: bool = False
    show_pagination: bool = False
    page_size: int = 10
    sort_column: Optional[str] = None
    sort_direction: SortDirection = SortDirection.ASC
    filter_text: str = ""
    filter_column: Optional[str] = None
    on_row_click: Optional[Callable] = None
    on_selection_change: Optional[Callable] = None
    on_sort: Optional[Callable] = None
    on_filter: Optional[Callable] = None
    expand: Union[bool, int] = False
    border_radius: int = 12
    elevation: int = 1


class EnhancedTable:
    """
    Enhanced table with Material Design 3 styling and animations
    """
    
    def __init__(self, page: ft.Page, config: TableConfig):
        self.page = page
        self.config = config
        self.table_ref = ft.Ref[ft.DataTable]()
        self.selected_rows = set()
        self.current_page = 0
        
        # Create the table
        self.table = self._create_table()
        
        # Create pagination controls if needed
        self.pagination_controls = self._create_pagination() if config.show_pagination else None
    
    def _create_table(self) -> ft.DataTable:
        """Create the enhanced table"""
        # Create columns
        columns = self._create_columns()
        
        # Create rows
        rows = self._create_rows()
        
        # Determine row height based on size
        if self.config.size == TableSize.SMALL:
            data_row_height = 32
        elif self.config.size == TableSize.LARGE:
            data_row_height = 56
        else:
            data_row_height = 48
        
        # Create table
        table = ft.DataTable(
            ref=self.table_ref,
            columns=columns,
            rows=rows,
            data_row_height=data_row_height,
            heading_row_color=TOKENS['surface_variant'],
            border=ft.BorderSide(1, TOKENS['outline']),
            horizontal_lines=ft.BorderSide(0.5, TOKENS['outline']),
            show_checkbox_column=self.config.show_checkboxes,
            on_select_all=self._on_select_all if self.config.show_checkboxes else None,
            sort_ascending=self.config.sort_direction == SortDirection.ASC,
            sort_column_index=self._get_column_index(self.config.sort_column) if self.config.sort_column else None
        )
        
        return table
    
    def _create_columns(self) -> List[ft.DataColumn]:
        """Create table columns"""
        columns = []
        
        for column in self.config.columns:
            # Create column header
            header_content = ft.Text(
                column.label,
                text_align=column.text_align,
                weight=ft.FontWeight.W_500
            )
            
            # Add sort indicator if sortable and currently sorted
            if column.sortable and self.config.sort_column == column.name:
                sort_icon = ft.Icons.ARROW_UPWARD if self.config.sort_direction == SortDirection.ASC else ft.Icons.ARROW_DOWNWARD
                header_content = ft.Row([
                    header_content,
                    ft.Icon(sort_icon, size=16)
                ], spacing=4)
            
            # Create data column
            data_column = ft.DataColumn(
                header_content,
                on_sort=lambda e, col_name=column.name: self._on_column_sort(col_name) if column.sortable else None,
                numeric=column.numeric
            )
            
            columns.append(data_column)
        
        return columns
    
    def _create_rows(self) -> List[ft.DataRow]:
        """Create table rows"""
        rows = []
        
        # Apply filtering
        filtered_data = self._apply_filter(self.config.data)
        
        # Apply sorting
        sorted_data = self._apply_sort(filtered_data)
        
        # Apply pagination
        paged_data = self._apply_pagination(sorted_data)
        
        # Create rows
        for i, item in enumerate(paged_data):
            cells = []
            
            for column in self.config.columns:
                value = item.get(column.name, "")
                # Format value based on type
                if isinstance(value, datetime):
                    formatted_value = value.strftime("%Y-%m-%d %H:%M")
                elif isinstance(value, (int, float)):
                    if column.numeric:
                        formatted_value = f"{value:,}"
                    else:
                        formatted_value = str(value)
                else:
                    formatted_value = str(value)
                
                cells.append(
                    ft.DataCell(
                        ft.Text(
                            formatted_value,
                            text_align=column.text_align
                        )
                    )
                )
            
            # Create data row
            row = ft.DataRow(
                cells=cells,
                on_select_changed=lambda e, idx=i: self._on_row_select(e, idx) if self.config.show_checkboxes else None,
                on_tap=lambda e, data=item: self._on_row_click(e, data) if self.config.on_row_click else None
            )
            
            rows.append(row)
        
        return rows
    
    def _create_pagination(self) -> Optional[ft.Control]:
        """Create pagination controls"""
        if not self.config.show_pagination:
            return None
        
        # Calculate total pages
        filtered_data = self._apply_filter(self.config.data)
        total_items = len(filtered_data)
        total_pages = (total_items + self.config.page_size - 1) // self.config.page_size if self.config.page_size > 0 else 1
        
        if total_pages <= 1:
            return None
        
        # Create pagination controls
        controls = [
            ft.IconButton(
                icon=ft.Icons.FIRST_PAGE,
                on_click=lambda e: self._go_to_page(0),
                disabled=self.current_page == 0
            ),
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda e: self._go_to_page(self.current_page - 1),
                disabled=self.current_page == 0
            ),
            ft.Text(f"{self.current_page + 1} of {total_pages}"),
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                on_click=lambda e: self._go_to_page(self.current_page + 1),
                disabled=self.current_page >= total_pages - 1
            ),
            ft.IconButton(
                icon=ft.Icons.LAST_PAGE,
                on_click=lambda e: self._go_to_page(total_pages - 1),
                disabled=self.current_page >= total_pages - 1
            )
        ]
        
        return ft.Row(controls, alignment=ft.MainAxisAlignment.CENTER)
    
    def _apply_filter(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply filter to data"""
        if not self.config.filter_text:
            return data
        
        filtered_data = []
        filter_text = self.config.filter_text.lower()
        
        for item in data:
            # If filtering by specific column
            if self.config.filter_column:
                value = str(item.get(self.config.filter_column, "")).lower()
                if filter_text in value:
                    filtered_data.append(item)
            else:
                # Filter across all columns
                match = False
                for column in self.config.columns:
                    value = str(item.get(column.name, "")).lower()
                    if filter_text in value:
                        match = True
                        break
                if match:
                    filtered_data.append(item)
        
        return filtered_data
    
    def _apply_sort(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply sorting to data"""
        if not self.config.sort_column:
            return data
        
        try:
            sorted_data = sorted(
                data,
                key=lambda x: x.get(self.config.sort_column, ""),
                reverse=(self.config.sort_direction == SortDirection.DESC)
            )
            return sorted_data
        except Exception as ex:
            logger.error(f"Error sorting data: {ex}")
            return data
    
    def _apply_pagination(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply pagination to data"""
        if not self.config.show_pagination or self.config.page_size <= 0:
            return data
        
        start_index = self.current_page * self.config.page_size
        end_index = start_index + self.config.page_size
        
        return data[start_index:end_index]
    
    def _get_column_index(self, column_name: str) -> Optional[int]:
        """Get column index by name"""
        for i, column in enumerate(self.config.columns):
            if column.name == column_name:
                return i
        return None
    
    def _on_column_sort(self, column_name: str):
        """Handle column sort"""
        # If same column, toggle direction
        if self.config.sort_column == column_name:
            if self.config.sort_direction == SortDirection.ASC:
                self.config.sort_direction = SortDirection.DESC
            else:
                self.config.sort_direction = SortDirection.ASC
        else:
            # New column, default to ascending
            self.config.sort_column = column_name
            self.config.sort_direction = SortDirection.ASC
        
        # Rebuild table
        self._refresh_table()
        
        # Call sort callback if provided
        if self.config.on_sort:
            self.config.on_sort(column_name, self.config.sort_direction)
    
    def _on_row_select(self, e, row_index: int):
        """Handle row selection"""
        if e.data == "true":
            self.selected_rows.add(row_index)
        else:
            self.selected_rows.discard(row_index)
        
        # Call selection callback if provided
        if self.config.on_selection_change:
            self.config.on_selection_change(list(self.selected_rows))
    
    def _on_select_all(self, e):
        """Handle select all"""
        if e.data == "true":
            # Select all visible rows
            filtered_data = self._apply_filter(self.config.data)
            paged_data = self._apply_pagination(filtered_data)
            self.selected_rows = set(range(len(paged_data)))
        else:
            self.selected_rows.clear()
        
        # Call selection callback if provided
        if self.config.on_selection_change:
            self.config.on_selection_change(list(self.selected_rows))
        
        # Rebuild table to update checkboxes
        self._refresh_table()
    
    def _on_row_click(self, e, data: Dict[str, Any]):
        """Handle row click"""
        if self.config.on_row_click:
            self.config.on_row_click(data)
    
    def _go_to_page(self, page: int):
        """Go to specific page"""
        filtered_data = self._apply_filter(self.config.data)
        total_items = len(filtered_data)
        total_pages = (total_items + self.config.page_size - 1) // self.config.page_size if self.config.page_size > 0 else 1
        
        if 0 <= page < total_pages:
            self.current_page = page
            self._refresh_table()
    
    def _refresh_table(self):
        """Refresh table content"""
        # Recreate table
        new_table = self._create_table()
        self.table.columns = new_table.columns
        self.table.rows = new_table.rows
        self.table.sort_column_index = new_table.sort_column_index
        self.table.sort_ascending = new_table.sort_ascending
        
        # Recreate pagination if needed
        if self.config.show_pagination:
            new_pagination = self._create_pagination()
            self.pagination_controls = new_pagination
        
        self.page.update()
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Set table data"""
        self.config.data = data
        self.current_page = 0
        self.selected_rows.clear()
        self._refresh_table()
    
    def set_filter(self, filter_text: str, column: Optional[str] = None):
        """Set filter text and column"""
        self.config.filter_text = filter_text
        self.config.filter_column = column
        self.current_page = 0
        self.selected_rows.clear()
        self._refresh_table()
        
        # Call filter callback if provided
        if self.config.on_filter:
            self.config.on_filter(filter_text, column)
    
    def get_selected_data(self) -> List[Dict[str, Any]]:
        """Get selected row data"""
        filtered_data = self._apply_filter(self.config.data)
        sorted_data = self._apply_sort(filtered_data)
        paged_data = self._apply_pagination(sorted_data)
        
        return [paged_data[i] for i in self.selected_rows if i < len(paged_data)]
    
    def get_control(self) -> ft.Control:
        """Get the Flet control"""
        if self.pagination_controls:
            return ft.Column([
                self.table,
                self.pagination_controls
            ], spacing=16)
        else:
            return self.table


# Convenience functions for common table types
def create_simple_table(
    page: ft.Page,
    data: List[Dict[str, Any]],
    columns: Optional[List[str]] = None,
    **kwargs
) -> EnhancedTable:
    """Create a simple table with automatic column detection"""
    # Determine columns
    if not columns and data:
        columns = list(data[0].keys())
    elif not columns:
        columns = []
    
    # Create column definitions
    column_defs = []
    for col in columns:
        # Try to determine if column is numeric
        is_numeric = False
        if data:
            sample_value = data[0].get(col)
            is_numeric = isinstance(sample_value, (int, float))
        
        column_defs.append(
            TableColumn(
                name=col,
                label=col.replace("_", " ").title(),
                numeric=is_numeric
            )
        )
    
    config = TableConfig(
        columns=column_defs,
        data=data,
        **kwargs
    )
    
    return EnhancedTable(page, config)


def create_client_table(
    page: ft.Page,
    clients: List[Dict[str, Any]],
    **kwargs
) -> EnhancedTable:
    """Create a specialized client table"""
    columns = [
        TableColumn(name="id", label="ID", numeric=True, width=60),
        TableColumn(name="name", label="Name"),
        TableColumn(name="ip_address", label="IP Address"),
        TableColumn(name="status", label="Status"),
        TableColumn(name="last_seen", label="Last Seen"),
        TableColumn(name="files_count", label="Files", numeric=True)
    ]
    
    config = TableConfig(
        columns=columns,
        data=clients,
        show_checkboxes=True,
        show_pagination=True,
        page_size=10,
        **kwargs
    )
    
    return EnhancedTable(page, config)


def create_file_table(
    page: ft.Page,
    files: List[Dict[str, Any]],
    **kwargs
) -> EnhancedTable:
    """Create a specialized file table"""
    columns = [
        TableColumn(name="name", label="File Name"),
        TableColumn(name="size", label="Size", numeric=True),
        TableColumn(name="type", label="Type"),
        TableColumn(name="owner", label="Owner"),
        TableColumn(name="modified", label="Modified"),
        TableColumn(name="status", label="Status")
    ]
    
    config = TableConfig(
        columns=columns,
        data=files,
        show_checkboxes=True,
        show_pagination=True,
        page_size=10,
        **kwargs
    )
    
    return EnhancedTable(page, config)


# Test function
async def test_enhanced_tables(page: ft.Page):
    """Test enhanced tables functionality"""
    print("Testing enhanced tables...")
    
    # Generate sample data
    clients = []
    for i in range(25):
        clients.append({
            "id": i + 1,
            "name": f"Client {i + 1}",
            "ip_address": f"192.168.1.{i + 1}",
            "status": random.choice(["Online", "Offline", "Away"]),
            "last_seen": (datetime.now() - timedelta(minutes=random.randint(0, 1440))).strftime("%Y-%m-%d %H:%M"),
            "files_count": random.randint(0, 1000)
        })
    
    # Create client table
    client_table = create_client_table(
        page,
        clients,
        on_row_click=lambda data: print(f"Clicked client: {data['name']}")
    )
    
    # Create layout
    layout = ft.Column([
        ft.Text("Enhanced Tables Test", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
        client_table.get_control()
    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
    
    # Add to page
    page.add(layout)
    page.update()
    
    # Test data updates
    await asyncio.sleep(2)
    new_clients = clients[:5]  # Show only first 5 clients
    client_table.set_data(new_clients)
    
    # Test filtering
    await asyncio.sleep(1)
    client_table.set_filter("Online", "status")
    
    print("Enhanced tables test completed")


if __name__ == "__main__":
    print("Enhanced Table Components Module")
    print("This module provides enhanced table components for the Flet Server GUI")