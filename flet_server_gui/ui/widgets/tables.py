#!/usr/bin/env python3
"""
UI Widgets - Tables

Purpose: Advanced data table component with filtering, sorting, actions
Logic: Data processing, filtering algorithms, sort operations
UI: Table rendering, Material Design 3 styling, responsive layout
"""

import flet as ft
import json
import re
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SortDirection(Enum):
    ASC = "asc"
    DESC = "desc"

class FilterOperator(Enum):
    EQUALS = "equals"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    REGEX = "regex"
    DATE_RANGE = "date_range"

@dataclass
class ColumnFilter:
    """Filter configuration for a column"""
    operator: FilterOperator
    value: Any
    enabled: bool = True
    case_sensitive: bool = False

@dataclass
class ColumnSort:
    """Sort configuration for a column"""
    direction: SortDirection
    priority: int = 0  # For multi-column sorting

@dataclass
class TableColumn:
    """Enhanced table column definition"""
    key: str
    title: str
    width: Optional[int] = None
    sortable: bool = True
    filterable: bool = True
    data_type: str = "text"  # text, number, date, bool
    format_function: Optional[Callable] = None
    alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START

@dataclass
class TableAction:
    """Context menu action definition"""
    name: str
    icon: str
    callback: Callable
    enabled: bool = True
    separator_after: bool = False


class EnhancedDataTable:
    """
    Advanced data table with sophisticated filtering, sorting, and context menu functionality.
    Professional table management with responsive design and Material Design 3 styling.
    """
    
    def __init__(self, 
                 columns: List[TableColumn],
                 data_source: Callable[[], List[Dict[str, Any]]],
                 row_actions: Optional[List[TableAction]] = None,
                 bulk_actions: Optional[List[TableAction]] = None):
        """Initialize enhanced table with column definitions and data source"""
        
        self.columns = {col.key: col for col in columns}
        self.column_order = [col.key for col in columns]
        self.data_source = data_source
        self.row_actions = row_actions or []
        self.bulk_actions = bulk_actions or []
        
        # Table state
        self.raw_data: List[Dict[str, Any]] = []
        self.filtered_data: List[Dict[str, Any]] = []
        self.selected_rows: set = set()
        self.current_page = 0
        self.rows_per_page = 50
        
        # Filter and sort state
        self.column_filters: Dict[str, ColumnFilter] = {}
        self.column_sorts: Dict[str, ColumnSort] = {}
        self.global_search = ""
        
        # UI components with responsive design
        self.table_container = ft.Container(expand=True)
        self.search_bar = ft.TextField(expand=True)
        self.filter_panel = ft.Container()
        self.sort_indicator_row = ft.Row()
        self.pagination_controls = ft.Row()
        self.selection_info = ft.Text()
        self.bulk_action_bar = ft.Row(visible=False)
        
        # Settings persistence
        self.table_id = f"table_{id(self)}"
        
        logger.info("✅ Enhanced data table initialized")
    
    def create_enhanced_table(self) -> ft.Container:
        """Create the main enhanced table view with responsive design"""
        
        # Header with search and controls
        header = self._create_table_header()
        
        # Filter panel (collapsible)
        filter_panel = self._create_filter_panel()
        
        # Sort indicators
        sort_panel = self._create_sort_panel()
        
        # Selection info and bulk actions
        selection_panel = self._create_selection_panel()
        
        # Main data table
        data_table = self._create_data_table()
        
        # Pagination controls
        pagination = self._create_pagination_controls()
        
        self.table_container = ft.Container(
            content=ft.Column([
                header,
                filter_panel,
                sort_panel,
                selection_panel,
                data_table,
                pagination
            ], spacing=10, expand=True),
            expand=True
        )
        
        # Load initial data
        self._refresh_data()
        
        return self.table_container
    
    def _create_table_header(self) -> ft.Container:
        """Create responsive table header with search and controls"""
        
        self.search_bar = ft.TextField(
            label="Global Search",
            prefix_icon=ft.Icons.SEARCH,
            suffix=ft.IconButton(
                icon=ft.Icons.CLEAR,
                tooltip="Clear Search",
                on_click=self._clear_search
            ),
            on_change=self._on_search_changed,
            expand=True
        )
        
        control_buttons = ft.ResponsiveRow([
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.FILTER_LIST,
                    tooltip="Toggle Filters",
                    on_click=self._toggle_filter_panel
                ),
                col={"sm": 6, "md": 3},
            ),
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.SORT,
                    tooltip="Clear Sorting", 
                    on_click=self._clear_sorting
                ),
                col={"sm": 6, "md": 3},
            ),
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh Data",
                    on_click=self._refresh_data
                ),
                col={"sm": 6, "md": 3},
            ),
            ft.Container(
                content=ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text="Export Visible Data",
                            icon=ft.Icons.FILE_DOWNLOAD,
                            on_click=self._export_visible_data
                        ),
                        ft.PopupMenuItem(
                            text="Export All Data",
                            icon=ft.Icons.DOWNLOAD,
                            on_click=self._export_all_data
                        ),
                        ft.PopupMenuItem(
                            text="Reset Table",
                            icon=ft.Icons.RESTORE,
                            on_click=self._reset_table
                        )
                    ]
                ),
                col={"sm": 6, "md": 3},
            )
        ], expand=True)
        
        return ft.Container(
            content=ft.ResponsiveRow([
                ft.Container(
                    content=self.search_bar,
                    col={"sm": 12, "md": 8},
                    expand=True
                ),
                ft.Container(
                    content=control_buttons,
                    col={"sm": 12, "md": 4},
                    expand=True
                )
            ], expand=True),
            padding=ft.padding.all(10),
            expand=True
        )
    
    def _create_filter_panel(self) -> ft.Container:
        """Create collapsible filter panel with responsive design"""
        
        filter_controls = []
        
        for col_key, column in self.columns.items():
            if not column.filterable:
                continue
                
            if column.data_type == "text":
                filter_control = ft.TextField(
                    label=f"Filter {column.title}",
                    on_change=lambda e, key=col_key: self._on_filter_changed(key, e.control.value),
                    expand=True
                )
            elif column.data_type == "number":
                filter_control = ft.Row([
                    ft.TextField(
                        label=f"Min {column.title}",
                        on_change=lambda e, key=col_key: self._on_numeric_filter_changed(key, "min", e.control.value),
                        expand=True
                    ),
                    ft.TextField(
                        label=f"Max {column.title}",
                        on_change=lambda e, key=col_key: self._on_numeric_filter_changed(key, "max", e.control.value),
                        expand=True
                    )
                ], expand=True)
            elif column.data_type == "date":
                filter_control = ft.Row([
                    ft.TextField(
                        label=f"From Date {column.title}",
                        on_change=lambda e, key=col_key: self._on_date_filter_changed(key, "from", e.control.value),
                        expand=True
                    ),
                    ft.TextField(
                        label=f"To Date {column.title}",
                        on_change=lambda e, key=col_key: self._on_date_filter_changed(key, "to", e.control.value),
                        expand=True
                    )
                ], expand=True)
            else:
                filter_control = ft.Dropdown(
                    label=f"Filter {column.title}",
                    options=[
                        ft.dropdown.Option("all", "All"),
                        ft.dropdown.Option("true", "True"),
                        ft.dropdown.Option("false", "False")
                    ],
                    on_change=lambda e, key=col_key: self._on_dropdown_filter_changed(key, e.control.value),
                    expand=True
                )
                
            filter_controls.append(
                ft.Container(
                    content=filter_control,
                    padding=ft.padding.symmetric(horizontal=5),
                    expand=True
                )
            )
        
        # Create responsive filter grid
        filter_grid = ft.ResponsiveRow([
            ft.Container(
                content=control,
                col={"sm": 12, "md": 6, "lg": 4},
                expand=True
            ) for control in filter_controls
        ], expand=True)
        
        self.filter_panel = ft.Container(
            content=ft.Column([
                ft.Text("Filters", style=ft.TextThemeStyle.TITLE_MEDIUM),
                filter_grid
            ], spacing=10),
            padding=ft.padding.all(10),
            visible=False,
            expand=True
        )
        
        return self.filter_panel
    
    def _create_sort_panel(self) -> ft.Container:
        """Create sort indicators panel with responsive design"""
        
        self.sort_indicator_row = ft.ResponsiveRow(
            controls=[],
            spacing=10,
            visible=False,
            expand=True
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Active Sorting", style=ft.TextThemeStyle.TITLE_SMALL),
                self.sort_indicator_row
            ], spacing=5),
            padding=ft.padding.all(10),
            expand=True
        )
    
    def _create_selection_panel(self) -> ft.Container:
        """Create selection info and bulk actions panel"""
        
        self.selection_info = ft.Text("No items selected", expand=True)
        
        self.bulk_action_bar = ft.ResponsiveRow([
            ft.Container(
                content=ft.ElevatedButton(
                    text=action.name,
                    icon=action.icon,
                    on_click=lambda e, a=action: self._execute_bulk_action(a)
                ),
                col={"sm": 12, "md": 6, "lg": 4},
                expand=True
            ) for action in self.bulk_actions
        ], visible=False, spacing=8, expand=True)
        
        return ft.Container(
            content=ft.Column([
                self.selection_info,
                self.bulk_action_bar
            ], spacing=10),
            padding=ft.padding.all(10),
            expand=True
        )
    
    def _create_data_table(self) -> ft.Container:
        """Create the main data table with responsive design"""
        
        # Create column headers with sort capability
        headers = []
        for col_key in self.column_order:
            column = self.columns[col_key]
            
            header_content = ft.Row([
                ft.Text(column.title, expand=True),
                ft.Icon(ft.Icons.UNFOLD_MORE, size=16) if column.sortable else None
            ], spacing=5)
            
            if column.sortable:
                header = ft.TextButton(
                    content=header_content,
                    on_click=lambda e, key=col_key: self._toggle_column_sort(key),
                    style=ft.ButtonStyle(
                        padding=ft.padding.all(8),
                        shape=ft.RoundedRectangleBorder(radius=4)
                    )
                )
            else:
                header = ft.Container(
                    content=header_content,
                    padding=ft.padding.all(8)
                )
            
            headers.append(ft.DataColumn(header))
        
        # Add action column if row actions exist
        if self.row_actions:
            headers.append(ft.DataColumn(ft.Text("Actions")))
        
        # Create data rows
        rows = self._create_data_rows()
        
        data_table = ft.DataTable(
            columns=headers,
            rows=rows,
            show_checkbox_column=True,
            expand=True
        )
        
        return ft.Container(
            content=ft.Column([
                data_table
            ], scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True
        )
    
    def _create_data_rows(self) -> List[ft.DataRow]:
        """Create data rows for the current page"""
        
        rows = []
        start_idx = self.current_page * self.rows_per_page
        end_idx = start_idx + self.rows_per_page
        page_data = self.filtered_data[start_idx:end_idx]
        
        for row_idx, row_data in enumerate(page_data):
            cells = []
            
            # Create data cells
            for col_key in self.column_order:
                column = self.columns[col_key]
                value = row_data.get(col_key, "")
                
                # Format value if format function provided
                if column.format_function and value is not None:
                    try:
                        formatted_value = column.format_function(value)
                    except:
                        formatted_value = str(value)
                else:
                    formatted_value = str(value) if value is not None else ""
                
                cells.append(ft.DataCell(ft.Text(formatted_value)))
            
            # Add action cell if row actions exist
            if self.row_actions:
                action_buttons = ft.Row([
                    ft.IconButton(
                        icon=action.icon,
                        tooltip=action.name,
                        on_click=lambda e, a=action, data=row_data: self._execute_row_action(a, data)
                    ) for action in self.row_actions
                ], spacing=2)
                
                cells.append(ft.DataCell(action_buttons))
            
            # Create row with selection capability
            row_id = str(start_idx + row_idx)
            is_selected = row_id in self.selected_rows
            
            row = ft.DataRow(
                cells=cells,
                selected=is_selected,
                on_select_changed=lambda e, rid=row_id: self._on_row_selected(rid, e.control.selected)
            )
            
            rows.append(row)
        
        return rows
    
    def _create_pagination_controls(self) -> ft.Container:
        """Create responsive pagination controls"""
        
        total_pages = (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page
        
        pagination_info = ft.Text(
            f"Page {self.current_page + 1} of {total_pages} ({len(self.filtered_data)} items)",
            expand=True
        )
        
        pagination_controls = ft.ResponsiveRow([
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.FIRST_PAGE,
                    on_click=lambda e: self._go_to_page(0),
                    disabled=self.current_page == 0
                ),
                col={"sm": 3, "md": 2},
            ),
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    on_click=lambda e: self._go_to_page(self.current_page - 1),
                    disabled=self.current_page == 0
                ),
                col={"sm": 3, "md": 2},
            ),
            ft.Container(
                content=pagination_info,
                col={"sm": 6, "md": 4},
                alignment=ft.alignment.center,
                expand=True
            ),
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    on_click=lambda e: self._go_to_page(self.current_page + 1),
                    disabled=self.current_page >= total_pages - 1
                ),
                col={"sm": 3, "md": 2},
            ),
            ft.Container(
                content=ft.IconButton(
                    icon=ft.Icons.LAST_PAGE,
                    on_click=lambda e: self._go_to_page(total_pages - 1),
                    disabled=self.current_page >= total_pages - 1
                ),
                col={"sm": 3, "md": 2},
            ),
            ft.Container(
                content=ft.Dropdown(
                    label="Rows per page",
                    options=[
                        ft.dropdown.Option(str(x), str(x)) for x in [25, 50, 100, 200]
                    ],
                    value=str(self.rows_per_page),
                    on_change=self._on_rows_per_page_changed
                ),
                col={"sm": 12, "md": 2},
            )
        ], expand=True)
        
        return ft.Container(
            content=pagination_controls,
            padding=ft.padding.all(10),
            expand=True
        )
    
    # Event handlers and utility methods
    
    def _refresh_data(self, e=None):
        """Refresh table data from data source"""
        try:
            self.raw_data = self.data_source()
            self._apply_filters()
            self._apply_sorting()
            self._update_table_display()
            logger.info(f"✅ Table refreshed with {len(self.raw_data)} rows")
        except Exception as ex:
            logger.error(f"❌ Error refreshing table data: {ex}")
    
    def _apply_filters(self):
        """Apply all active filters to the data"""
        self.filtered_data = self.raw_data.copy()
        
        # Apply global search
        if self.global_search.strip():
            search_term = self.global_search.lower()
            self.filtered_data = [
                row for row in self.filtered_data
                if any(search_term in str(row.get(col_key, "")).lower() 
                      for col_key in self.column_order)
            ]
        
        # Apply column filters
        for col_key, filter_config in self.column_filters.items():
            if not filter_config.enabled:
                continue
                
            self.filtered_data = [
                row for row in self.filtered_data
                if self._row_matches_filter(row, col_key, filter_config)
            ]
    
    def _apply_sorting(self):
        """Apply sorting to filtered data"""
        if not self.column_sorts:
            return
            
        # Sort by priority (multi-column sorting)
        sorted_items = sorted(
            self.column_sorts.items(),
            key=lambda x: x[1].priority
        )
        
        for col_key, sort_config in reversed(sorted_items):
            reverse = sort_config.direction == SortDirection.DESC
            self.filtered_data.sort(
                key=lambda row: self._get_sort_key(row, col_key),
                reverse=reverse
            )
    
    def _update_table_display(self):
        """Update the table display after data changes"""
        # Reset to first page if current page is out of bounds
        total_pages = (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page
        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)
        
        # Update selection info
        selected_count = len(self.selected_rows)
        self.selection_info.value = (
            f"{selected_count} of {len(self.filtered_data)} items selected" 
            if selected_count > 0 else "No items selected"
        )
        
        # Show/hide bulk actions
        self.bulk_action_bar.visible = selected_count > 0
        
        # Recreate table content
        self.table_container.content = self.create_enhanced_table().content
    
    # Additional event handlers (abbreviated for space)
    
    def _clear_search(self, e=None):
        """Clear global search"""
        self.global_search = ""
        self.search_bar.value = ""
        self._refresh_data()
    
    def _on_search_changed(self, e):
        """Handle search input changes"""
        self.global_search = e.control.value
        self._apply_filters()
        self._apply_sorting()
        self._update_table_display()
    
    def _toggle_filter_panel(self, e):
        """Toggle filter panel visibility"""
        self.filter_panel.visible = not self.filter_panel.visible
        self.table_container.update()
    
    def _clear_sorting(self, e):
        """Clear all sorting"""
        self.column_sorts.clear()
        self._apply_sorting()
        self._update_table_display()
    
    def _reset_table(self, e):
        """Reset table to default state"""
        self.column_filters.clear()
        self.column_sorts.clear()
        self.global_search = ""
        self.search_bar.value = ""
        self.current_page = 0
        self.selected_rows.clear()
        self._refresh_data()
    
    def _export_visible_data(self, e):
        """Export currently visible data"""
        # Placeholder for export functionality
        pass
    
    def _export_all_data(self, e):
        """Export all filtered data"""
        # Placeholder for export functionality
        pass
    
    def _toggle_column_sort(self, col_key: str):
        """Toggle sorting for a column"""
        if col_key in self.column_sorts:
            current_sort = self.column_sorts[col_key]
            if current_sort.direction == SortDirection.ASC:
                self.column_sorts[col_key].direction = SortDirection.DESC
            else:
                del self.column_sorts[col_key]
        else:
            self.column_sorts[col_key] = ColumnSort(SortDirection.ASC, len(self.column_sorts))
        
        self._apply_sorting()
        self._update_table_display()
    
    def _go_to_page(self, page: int):
        """Navigate to specific page"""
        total_pages = (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page
        if 0 <= page < total_pages:
            self.current_page = page
            self._update_table_display()
    
    def _on_rows_per_page_changed(self, e):
        """Handle rows per page change"""
        self.rows_per_page = int(e.control.value)
        self.current_page = 0
        self._update_table_display()
    
    def _on_row_selected(self, row_id: str, selected: bool):
        """Handle row selection changes"""
        if selected:
            self.selected_rows.add(row_id)
        else:
            self.selected_rows.discard(row_id)
        self._update_table_display()
    
    def _row_matches_filter(self, row: Dict[str, Any], col_key: str, filter_config: ColumnFilter) -> bool:
        """Check if row matches filter criteria"""
        value = row.get(col_key, "")
        filter_value = filter_config.value
        
        if not filter_value:
            return True
        
        # Convert to string for text operations
        value_str = str(value).lower() if not filter_config.case_sensitive else str(value)
        filter_str = str(filter_value).lower() if not filter_config.case_sensitive else str(filter_value)
        
        if filter_config.operator == FilterOperator.CONTAINS:
            return filter_str in value_str
        elif filter_config.operator == FilterOperator.EQUALS:
            return value_str == filter_str
        elif filter_config.operator == FilterOperator.STARTS_WITH:
            return value_str.startswith(filter_str)
        elif filter_config.operator == FilterOperator.ENDS_WITH:
            return value_str.endswith(filter_str)
        # Add more operators as needed
        
        return True
    
    def _get_sort_key(self, row: Dict[str, Any], col_key: str):
        """Get sort key for a row and column"""
        value = row.get(col_key, "")
        column = self.columns[col_key]
        
        if column.data_type == "number":
            try:
                return float(value) if value else 0
            except (ValueError, TypeError):
                return 0
        elif column.data_type == "date":
            try:
                return datetime.fromisoformat(str(value))
            except (ValueError, TypeError):
                return datetime.min
        else:
            return str(value).lower()
    
    def _execute_row_action(self, action: TableAction, row_data: Dict[str, Any]):
        """Execute row action"""
        if action.enabled and action.callback:
            try:
                action.callback(row_data)
            except Exception as e:
                logger.error(f"❌ Error executing row action {action.name}: {e}")
    
    def _execute_bulk_action(self, action: TableAction):
        """Execute bulk action on selected rows"""
        if action.enabled and action.callback and self.selected_rows:
            try:
                selected_data = []
                start_idx = self.current_page * self.rows_per_page
                for row_idx_str in self.selected_rows:
                    row_idx = int(row_idx_str) - start_idx
                    if 0 <= row_idx < len(self.filtered_data[start_idx:start_idx + self.rows_per_page]):
                        selected_data.append(self.filtered_data[start_idx + row_idx])
                
                action.callback(selected_data)
            except Exception as e:
                logger.error(f"❌ Error executing bulk action {action.name}: {e}")
    
    def _on_filter_changed(self, col_key: str, value: str):
        """Handle text filter changes"""
        if value.strip():
            self.column_filters[col_key] = ColumnFilter(FilterOperator.CONTAINS, value)
        else:
            self.column_filters.pop(col_key, None)
        
        self._apply_filters()
        self._apply_sorting()
        self._update_table_display()
    
    def _on_numeric_filter_changed(self, col_key: str, filter_type: str, value: str):
        """Handle numeric filter changes"""
        # Placeholder for numeric filtering implementation
        pass
    
    def _on_date_filter_changed(self, col_key: str, filter_type: str, value: str):
        """Handle date filter changes"""
        # Placeholder for date filtering implementation
        pass
    
    def _on_dropdown_filter_changed(self, col_key: str, value: str):
        """Handle dropdown filter changes"""
        if value and value != "all":
            bool_value = value == "true"
            self.column_filters[col_key] = ColumnFilter(FilterOperator.EQUALS, bool_value)
        else:
            self.column_filters.pop(col_key, None)
        
        self._apply_filters()
        self._apply_sorting()
        self._update_table_display()


# Factory function for easy table creation
def create_enhanced_data_table(
    columns: List[TableColumn],
    data_source: Callable[[], List[Dict[str, Any]]],
    row_actions: Optional[List[TableAction]] = None,
    bulk_actions: Optional[List[TableAction]] = None
) -> EnhancedDataTable:
    """Create an enhanced data table with the specified configuration"""
    return EnhancedDataTable(columns, data_source, row_actions, bulk_actions)