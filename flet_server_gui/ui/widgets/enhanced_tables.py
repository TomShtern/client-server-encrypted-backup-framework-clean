#!/usr/bin/env python3
"""
Enhanced Table Components - Complete table system with ALL table functionality absorbed

Absorption Method Applied - ALL table functionality consolidated into ONE file:
- Enhanced table implementation (original base)
- Table data structures (absorbed from unified_table_base.py)
- Specialized table presets (absorbed from specialized_tables.py)
- Domain-specific factory methods

Purpose: Single comprehensive table solution for all table needs
Logic: Table creation, data handling, sorting, filtering, pagination, and specialized presets
UI: Material Design 3 styled tables with domain-specific configurations

One import, all table functionality - same pattern as successful chart consolidation!
"""

import flet as ft
import json
import re
import os
import asyncio
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

# Import from theme compatibility
from flet_server_gui.managers.theme_manager import TOKENS

# Try to import optional dependencies for specialized features
try:
    from flet_server_gui.core.semantic_colors import get_status_color
except ImportError:
    # Fallback color function if semantic colors not available
    def get_status_color(status: str) -> str:
        color_map = {
            "success": "#4CAF50",
            "info": "#2196F3", 
            "warning": "#FF9800",
            "error": "#F44336",
            "neutral": "#9E9E9E"
        }
        return color_map.get(status, "#9E9E9E")

# Add project root to path for additional imports if needed
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Optional imports for specialized functionality
try:
    from flet_server_gui.utils.server_bridge import ServerBridge
    from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
except ImportError:
    # Fallback for direct execution or missing dependencies
    ServerBridge = object
    ActionButtonFactory = object


# ============================================================================
# ABSORBED DATA STRUCTURES (from unified_table_base.py)
# ============================================================================

class TableSize(Enum):
    """Table sizes"""
    SMALL = "small"    # Compact rows
    MEDIUM = "medium"  # Default row height
    LARGE = "large"    # Spacious rows


class SortDirection(Enum):
    """Sort directions"""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(Enum):
    """Filter operators for advanced filtering"""
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
class EnhancedTableColumn:
    """Enhanced table column definition"""
    key: str
    title: str
    width: Optional[int] = None
    sortable: bool = True
    filterable: bool = True
    data_type: str = "text"  # text, number, date, bool
    format_function: Optional[Callable] = None
    alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START
    text_align: ft.TextAlign = ft.TextAlign.LEFT
    numeric: bool = False


@dataclass
class TableAction:
    """Context menu action definition"""
    name: str
    icon: str
    callback: Callable
    enabled: bool = True
    separator_after: bool = False


@dataclass
class TableConfig:
    """Configuration for enhanced tables"""
    columns: List[EnhancedTableColumn] = field(default_factory=list)
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
    
    # Advanced features
    data_source: Optional[Callable[[], List[Dict[str, Any]]]] = None
    row_actions: List[TableAction] = field(default_factory=list)
    bulk_actions: List[TableAction] = field(default_factory=list)


class EnhancedTable:
    """
    Complete table solution - ALL table functionality in ONE class.
    
    Absorption Method Applied:
    - Original EnhancedTable functionality (base)
    - Utility methods absorbed from UnifiedTableBase 
    - Specialized table support through configuration presets
    - Domain-specific formatting and action patterns
    
    Advanced data table with sophisticated filtering, sorting, context menu functionality,
    and professional table management with responsive design and Material Design 3 styling.
    """
    
    def __init__(self, page: ft.Page, config: TableConfig, server_bridge=None, button_factory=None):
        """Initialize enhanced table with configuration and optional specialized features"""
        
        self.page = page
        self.config = config
        
        # Optional specialized functionality (absorbed from UnifiedTableBase pattern)
        self.server_bridge = server_bridge
        self.button_factory = button_factory
        
        # Initialize data - unified approach
        if self.config.data_source:
            self.raw_data: List[Dict[str, Any]] = self.config.data_source()
        else:
            self.raw_data: List[Dict[str, Any]] = self.config.data.copy()
            
        self.filtered_data: List[Dict[str, Any]] = self.raw_data.copy()
        self.selected_rows: set = set()
        self.selected_items = []  # Compatibility alias absorbed from UnifiedTableBase
        self.current_page = 0
        self.rows_per_page = self.config.page_size
        
        # Unified filter and sort state
        self.column_filters: Dict[str, ColumnFilter] = {}
        self.column_sorts: Dict[str, ColumnSort] = {}
        self.global_search = self.config.filter_text
        
        # Advanced features (absorbed from UnifiedTableBase)
        self.sort_column = None
        self.sort_ascending = True
        self.total_items = 0
        self.items_per_page = self.config.page_size
        
        # Specialized table state (for domain-specific functionality)
        self.table_type = getattr(config, 'table_type', 'generic')  # client, file, database, generic
        self.current_table_name = None  # For database tables
        self.table_columns = []  # For dynamic database columns
        
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
        
        logger.info(f"✅ Enhanced data table initialized (type: {self.table_type})")
    
    def build(self) -> ft.Container:
        """Create the main enhanced table view with responsive design"""
        
        # Header with title and status
        self.status_text = ft.Text(
            "Loading table data...",
            size=14,
            color=TOKENS['primary']
        )
        
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
        
        # Convert config columns to dictionary for easier access
        columns_dict = {col.key: col for col in self.config.columns}
        column_order = [col.key for col in self.config.columns]
        
        for col_key, column in columns_dict.items():
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
            ) for action in self.config.bulk_actions
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
        
        # Convert config columns to dictionary for easier access
        columns_dict = {col.key: col for col in self.config.columns}
        column_order = [col.key for col in self.config.columns]
        
        # Create column headers with sort capability
        headers = []
        for col_key in column_order:
            column = columns_dict[col_key]
            
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
        if self.config.row_actions:
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

        # Convert config columns to dictionary for easier access
        columns_dict = {col.key: col for col in self.config.columns}
        column_order = [col.key for col in self.config.columns]

        for row_idx, row_data in enumerate(page_data):
            cells = []

            # Create data cells
            for col_key in column_order:
                column = columns_dict[col_key]
                value = row_data.get(col_key, "")

                # Format value if format function provided
                if column.format_function and value is not None:
                    try:
                        formatted_value = column.format_function(value)
                    except Exception:
                        formatted_value = str(value)
                else:
                    formatted_value = str(value) if value is not None else ""

                cells.append(ft.DataCell(ft.Text(formatted_value)))

            # Add action cell if row actions exist
            if self.config.row_actions:
                action_buttons = ft.Row([
                    ft.IconButton(
                        icon=action.icon,
                        tooltip=action.name,
                        on_click=lambda e, a=action, data=row_data: self._execute_row_action(a, data)
                    ) for action in self.config.row_actions
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
            if self.config.data_source:
                self.raw_data = self.config.data_source()
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
            # Convert config columns to dictionary for easier access
            column_order = [col.key for col in self.config.columns]
            self.filtered_data = [
                row for row in self.filtered_data
                if any(search_term in str(row.get(col_key, "")).lower() 
                      for col_key in column_order)
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
        self.table_container.content = self.build().content
    
    # Additional event handlers
    
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
        value_str = str(value) if filter_config.case_sensitive else str(value).lower()
        filter_str = str(filter_value) if filter_config.case_sensitive else str(filter_value).lower()
        
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
        # Find the column in config
        column = next((col for col in self.config.columns if col.key == col_key), None)
        
        if column and column.data_type == "number":
            try:
                return float(value) if value else 0
            except (ValueError, TypeError):
                return 0
        elif column and column.data_type == "date":
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

    def _show_table_settings(self, e):
        """Show table configuration dialog"""
        logger.info("📋 Table settings dialog requested")
        # TODO: Implement table settings dialog
    
    def _load_table_settings(self):
        """Load saved table settings"""
        try:
            settings_file = f"{self.table_id}_settings.json"
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                self.rows_per_page = settings.get('rows_per_page', 50)
                # Load other settings as needed
                
                logger.info("✅ Table settings loaded")
        except Exception as e:
            logger.warning(f"⚠️ Could not load table settings: {e}")
    
    def _save_table_settings(self):
        """Save current table settings"""
        try:
            settings = {
                'rows_per_page': self.rows_per_page,
                'column_widths': {},  # TODO: Save column widths
                'last_saved': datetime.now().isoformat()
            }
            
            settings_file = f"{self.table_id}_settings.json"
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error saving table settings: {e}")

    def add_row_action(self, action: TableAction):
        """Dynamically add a row action"""
        self.config.row_actions.append(action)
        logger.info(f"✅ Added row action: {action.name}")

    def add_bulk_action(self, action: TableAction):
        """Dynamically add a bulk action"""
        self.config.bulk_actions.append(action)
        logger.info(f"✅ Added bulk action: {action.name}")

    def get_selected_data(self) -> List[Dict[str, Any]]:
        """Get data for currently selected rows - enhanced with absorbed functionality"""
        selected_data = []
        for item_id in self.selected_items:
            try:
                # Try to get by index first
                idx = int(item_id) if item_id.isdigit() else -1
                if 0 <= idx < len(self.filtered_data):
                    selected_data.append(self.filtered_data[idx])
                else:
                    # Try to find by identifier in the data
                    for row in self.filtered_data:
                        if str(row.get('id', '')) == item_id or str(row.get('filename', '')) == item_id:
                            selected_data.append(row)
                            break
            except (ValueError, TypeError):
                continue
        return selected_data

    def clear_selection(self):
        """Clear all row selections - enhanced with absorbed functionality"""
        self.selected_rows.clear()
        self.selected_items.clear()  # Compatibility alias
        self._update_table_display()
    
    def select_all_specialized(self) -> None:
        """
        Select all rows using standardized logic - absorbed from UnifiedTableBase.
        Enhanced selection management from specialized tables.
        """
        if not self.table_container:
            return
            
        # Find all checkboxes and select them
        # This would need to be implemented based on current table structure
        # For now, select all items in current view
        for i in range(len(self.filtered_data)):
            item_id = str(i)
            if item_id not in self.selected_items:
                self.selected_items.append(item_id)
                self.selected_rows.add(item_id)
                        
        if self.page:
            self._update_table_display()
    
    def deselect_all_specialized(self) -> None:
        """
        Deselect all rows using standardized logic - absorbed from UnifiedTableBase.
        Enhanced deselection management from specialized tables.
        """
        self.clear_selection()
    
    def get_selected_count(self) -> int:
        """Get count of currently selected items - absorbed from UnifiedTableBase"""
        return len(self.selected_items)

    # ========================================================================
    # ABSORBED UTILITY METHODS (from UnifiedTableBase)
    # ========================================================================
    
    def format_file_size(self, size: int) -> str:
        """
        Format file size to human-readable format.
        Absorbed from UnifiedTableBase - consolidates identical formatting logic.
        """
        if not size or size == 0:
            return "0 B"
        
        # Convert bytes to appropriate unit
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def format_date_relative(self, date_str: str) -> str:
        """
        Format date to human-readable relative format.
        Absorbed from UnifiedTableBase - consolidates date formatting logic.
        """
        try:
            if not date_str or date_str == "Unknown":
                return "Unknown"
            
            # Parse the datetime string
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now()
            
            # Calculate time difference
            diff = now - date_obj.replace(tzinfo=None)
            
            # Relative time formatting
            if diff.total_seconds() < 300:  # 5 minutes
                return "Just now"
            elif diff.total_seconds() < 3600:  # 1 hour
                minutes = int(diff.total_seconds() / 60)
                return f"{minutes}m ago"
            elif diff.days > 7:
                return date_obj.strftime('%Y-%m-%d')
            elif diff.days > 0:
                return f"{diff.days}d ago"
            else:
                hours = int(diff.total_seconds() / 3600)
                return f"{hours}h ago"
                
        except (ValueError, AttributeError):
            return "Unknown"
    
    def format_cell_value(self, value: Any, column_name: str) -> str:
        """
        Format cell value based on type and column context.
        Absorbed from UnifiedTableBase - consolidates cell formatting logic.
        """
        if value is None:
            return ""

        # Special formatting for common column types
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M')
        elif isinstance(value, (int, float)) and 'size' in column_name.lower():
            return self.format_file_size(value)
        elif isinstance(value, bool):
            return "Yes" if value else "No"
        elif len(str(value)) > 30:  # Truncate very long values
            return f"{str(value)[:27]}..."

        return str(value)
    
    def create_compact_text(self, text: str, size: int = 12, max_lines: int = 1) -> ft.Text:
        """Create standardized text component for table cells - absorbed from UnifiedTableBase"""
        return ft.Text(
            text,
            size=size,
            max_lines=max_lines,
            overflow=ft.TextOverflow.ELLIPSIS
        )
    
    def create_bold_header(self, text: str) -> ft.Text:
        """Create standardized header text for table columns - absorbed from UnifiedTableBase"""
        return ft.Text(
            text,
            weight=ft.FontWeight.BOLD,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS
        )
    
    def create_selection_checkbox(self, item_id: str, on_item_select: Callable = None) -> ft.Checkbox:
        """
        Create selection checkbox with standardized behavior.
        Absorbed from UnifiedTableBase - consolidates identical checkbox creation patterns.
        """
        def handler(e):
            # Update local selection state immediately
            if e.control.value:  # Checkbox is now checked
                if item_id not in self.selected_items:
                    self.selected_items.append(item_id)
                    self.selected_rows.add(item_id)
            else:  # Checkbox is now unchecked
                if item_id in self.selected_items:
                    self.selected_items.remove(item_id)
                    self.selected_rows.discard(item_id)
            
            # Call the parent's selection handler if provided
            if on_item_select:
                e.data = item_id
                on_item_select(e)
        return ft.Checkbox(value=item_id in self.selected_items, on_change=handler, data=item_id)
    
    def get_table_stats(self) -> Dict[str, Any]:
        """Get table statistics - enhanced with absorbed functionality"""
        return {
            'total_rows': len(self.raw_data),
            'filtered_rows': len(self.filtered_data),
            'selected_rows': len(self.selected_rows),
            'selected_items': len(self.selected_items),  # Compatibility
            'current_page': self.current_page + 1,
            'total_pages': max(1, (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page),
            'active_filters': len(self.column_filters),
            'active_sorts': len(self.column_sorts),
            'table_type': self.table_type
        }

    # Convenience methods for backward compatibility
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Set table data - enhanced with absorbed functionality"""
        self.config.data = data
        self.raw_data = data.copy()
        self.filtered_data = data.copy()
        self.current_page = 0
        self.selected_rows.clear()
        self.selected_items.clear()  # Compatibility alias
        self.total_items = len(data)
        self._refresh_data()
    
    def set_filter(self, filter_text: str, column: Optional[str] = None):
        """Set filter text and column"""
        self.global_search = filter_text
        self.config.filter_column = column
        self.current_page = 0
        self.selected_rows.clear()
        self._refresh_data()
        
        # Call filter callback if provided
        if self.config.on_filter:
            self.config.on_filter(filter_text, column)
    
    def get_control(self) -> ft.Control:
        """Get the Flet control"""
        return self.build()

# Factory function for easy table creation
def create_enhanced_data_table(
    columns: List[EnhancedTableColumn],
    data_source: Callable[[], List[Dict[str, Any]]],
    row_actions: Optional[List[TableAction]] = None,
    bulk_actions: Optional[List[TableAction]] = None
) -> EnhancedTable:
    """Create an enhanced data table with the specified configuration"""
    config = TableConfig(
        columns=columns,
        data_source=data_source,
        row_actions=row_actions or [],
        bulk_actions=bulk_actions or []
    )
    # We need a page object, so we'll create a minimal config-based table
    # In practice, this would be created within a page context
    return EnhancedTable(page=None, config=config)

# ============================================================================
# SPECIALIZED FACTORY FUNCTIONS (converted from specialized_tables.py)
# ============================================================================
def create_simple_table(
    page: ft.Page,
    data: List[Dict[str, Any]],
    columns: Optional[List[str]] = None,
    **kwargs
) -> EnhancedTable:
    """Create a simple table with automatic column detection"""
    # Determine columns
    if not columns:
        columns = list(data[0].keys()) if data else []
    # Create column definitions
    column_defs = []
    for col in columns:
        # Try to determine if column is numeric
        is_numeric = False
        if data:
            sample_value = data[0].get(col)
            is_numeric = isinstance(sample_value, (int, float))

        column_defs.append(
            EnhancedTableColumn(
                key=col,
                title=col.replace("_", " ").title(),
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
        EnhancedTableColumn(key="id", title="ID", numeric=True, width=60),
        EnhancedTableColumn(key="name", title="Name"),
        EnhancedTableColumn(key="ip_address", title="IP Address"),
        EnhancedTableColumn(key="status", title="Status"),
        EnhancedTableColumn(key="last_seen", title="Last Seen"),
        EnhancedTableColumn(key="files_count", title="Files", numeric=True)
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
        EnhancedTableColumn(key="name", title="File Name"),
        EnhancedTableColumn(key="size", title="Size", numeric=True),
        EnhancedTableColumn(key="type", title="Type"),
        EnhancedTableColumn(key="owner", title="Owner"),
        EnhancedTableColumn(key="modified", title="Modified"),
        EnhancedTableColumn(key="status", title="Status")
    ]
    
    # File-specific actions absorbed from FileTable
    row_actions = []
    if button_factory:
        row_actions = [
            TableAction("View Details", ft.Icons.INFO, lambda data: _handle_file_view_details(data, server_bridge)),
            TableAction("Preview", ft.Icons.PREVIEW, lambda data: _handle_file_preview(data, server_bridge)),
            TableAction("Download", ft.Icons.DOWNLOAD, lambda data: _handle_file_download(data, server_bridge)),
            TableAction("Verify", ft.Icons.VERIFIED, lambda data: _handle_file_verify(data, server_bridge)),
            TableAction("Delete", ft.Icons.DELETE, lambda data: _handle_file_delete(data, server_bridge))
        ]
    
    config = TableConfig(
        columns=columns,
        data=files,
        show_checkboxes=True,
        show_pagination=True,
        page_size=10,
        table_type='file',
        row_actions=row_actions,
        **kwargs
    )
    
    table = EnhancedTable(page, config, server_bridge, button_factory)
    table._enhance_file_table()  # Apply file-specific enhancements
    return table


def create_database_table(
    page: ft.Page,
    table_data: List[Dict[str, Any]],
    table_name: str = "data_table",
    columns: Optional[List[str]] = None,
    server_bridge=None,
    button_factory=None,
    **kwargs
) -> EnhancedTable:
    """
    Create a specialized database table with dynamic columns and database-specific actions.
    Absorbed and enhanced from specialized_tables.py DatabaseTable implementation.
    """
    # Auto-detect columns if not provided
    if not columns and table_data:
        columns = list(table_data[0].keys())
    
    # Create column definitions dynamically
    column_defs = []
    for col_name in (columns or []):
        # Try to determine data type from sample data
        data_type = "text"
        if table_data:
            sample_value = table_data[0].get(col_name)
            if isinstance(sample_value, (int, float)):
                data_type = "number"
            elif isinstance(sample_value, datetime):
                data_type = "date"
            elif isinstance(sample_value, bool):
                data_type = "bool"
        
        column_defs.append(
            EnhancedTableColumn(
                key=col_name,
                title=col_name.replace('_', ' ').title(),
                width=120,
                data_type=data_type
            )
        )
    
    # Database-specific actions absorbed from DatabaseTable
    row_actions = [
        TableAction("View Details", ft.Icons.VISIBILITY, lambda data: _handle_database_view_details(data, server_bridge)),
        TableAction("Edit Row", ft.Icons.EDIT, lambda data: _handle_database_edit_row(data, server_bridge)),
        TableAction("Delete Row", ft.Icons.DELETE, lambda data: _handle_database_delete_row(data, server_bridge))
    ]
    
    config = TableConfig(
        columns=column_defs,
        data=table_data,
        show_checkboxes=True,
        show_pagination=True,
        page_size=25,  # Database tables often have more rows
        table_type='database',
        row_actions=row_actions,
        **kwargs
    )
    
    table = EnhancedTable(page, config, server_bridge, button_factory)
    table.current_table_name = table_name
    table.table_columns = columns or []
    table._enhance_database_table()  # Apply database-specific enhancements
    return table


# Legacy compatibility functions for existing code
def create_enhanced_data_table(
    columns: List[EnhancedTableColumn],
    data_source: Callable[[], List[Dict[str, Any]]],
    row_actions: Optional[List[TableAction]] = None,
    bulk_actions: Optional[List[TableAction]] = None
) -> EnhancedTable:
    """Create an enhanced data table with the specified configuration - legacy compatibility"""
    config = TableConfig(
        columns=columns,
        data_source=data_source,
        row_actions=row_actions or [],
        bulk_actions=bulk_actions or []
    )
    # Note: This creates a table without a page, which may cause issues
    # In practice, this should be created within a page context
    logger.warning("Creating table without page context - may cause issues")
    return EnhancedTable(page=None, config=config)

# Test function
async def test_enhanced_tables(page: ft.Page):
    """Test enhanced tables functionality"""
    print("Testing enhanced tables...")

    clients = [
        {
            "id": i + 1,
            "name": f"Client {i + 1}",
            "ip_address": f"192.168.1.{i + 1}",
            "status": random.choice(["Online", "Offline", "Away"]),
            "last_seen": (
                datetime.now() - timedelta(minutes=random.randint(0, 1440))
            ).strftime("%Y-%m-%d %H:%M"),
            "files_count": random.randint(0, 1000),
        }
        for i in range(25)
    ]
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


# ============================================================================
# ABSORBED SPECIALIZED TABLE ENHANCEMENTS (from specialized_tables.py)
# ============================================================================

def _format_status_display(status: str, table_instance) -> ft.Control:
    """Format status with appropriate color coding - absorbed from ClientTable"""
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

def _get_file_type_display(filename: str, table_instance) -> ft.Control:
    """Get file type display with icon and label - absorbed from FileTable"""
    file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
    
    # File type mappings
    type_mappings = {
        'txt': ('📄', 'Text', TOKENS['surface']),
        'pdf': ('📕', 'PDF', TOKENS['error']),
        'doc': ('📘', 'Word', TOKENS['primary']),
        'docx': ('📘', 'Word', TOKENS['primary']),
        'xls': ('📗', 'Excel', TOKENS['tertiary']),
        'xlsx': ('📗', 'Excel', TOKENS['tertiary']),
        'ppt': ('📙', 'PowerPoint', TOKENS['secondary']),
        'pptx': ('📙', 'PowerPoint', TOKENS['secondary']),
        'jpg': ('🖼️', 'Image', TOKENS['container']),
        'jpeg': ('🖼️', 'Image', TOKENS['container']),
        'png': ('🖼️', 'Image', TOKENS['container']),
        'gif': ('🖼️', 'Image', TOKENS['container']),
        'mp4': ('🎬', 'Video', TOKENS['surface_variant']),
        'avi': ('🎬', 'Video', TOKENS['surface_variant']),
        'mp3': ('🎵', 'Audio', TOKENS['tertiary']),
        'wav': ('🎵', 'Audio', TOKENS['tertiary']),
        'zip': ('🗜️', 'Archive', TOKENS['outline']),
        'rar': ('🗜️', 'Archive', TOKENS['outline']),
        '7z': ('🗜️', 'Archive', TOKENS['outline']),
    }
    
    icon, type_name, bg_color = type_mappings.get(file_extension, ('📄', 'File', TOKENS['surface_variant']))
    
    return ft.Container(
        content=ft.Row([
            ft.Text(icon, size=16),
            ft.Text(type_name, size=10, weight=ft.FontWeight.BOLD)
        ], spacing=4, tight=True),
        bgcolor=bg_color,
        padding=ft.Padding(4, 2, 4, 2),
        border_radius=4
    )

# Action handlers for specialized tables
def _handle_client_view_details(data, server_bridge):
    """Handle client view details action"""
    if server_bridge and hasattr(server_bridge, 'get_client_details'):
        return server_bridge.get_client_details(data.get('client_id'))
    print(f"View client details: {data.get('client_id')}")

def _handle_client_view_files(data, server_bridge):
    """Handle client view files action"""
    if server_bridge and hasattr(server_bridge, 'get_client_files'):
        return server_bridge.get_client_files(data.get('client_id'))
    print(f"View client files: {data.get('client_id')}")

def _handle_client_disconnect(data, server_bridge):
    """Handle client disconnect action"""
    if server_bridge and hasattr(server_bridge, 'disconnect_client'):
        return server_bridge.disconnect_client(data.get('client_id'))
    print(f"Disconnect client: {data.get('client_id')}")

def _handle_client_delete(data, server_bridge):
    """Handle client delete action"""
    if server_bridge and hasattr(server_bridge, 'delete_client'):
        return server_bridge.delete_client(data.get('client_id'))
    print(f"Delete client: {data.get('client_id')}")

def _handle_file_view_details(data, server_bridge):
    """Handle file view details action"""
    if server_bridge and hasattr(server_bridge, 'get_file_details'):
        return server_bridge.get_file_details(data.get('filename'))
    print(f"View file details: {data.get('filename')}")

def _handle_file_preview(data, server_bridge):
    """Handle file preview action"""
    if server_bridge and hasattr(server_bridge, 'preview_file'):
        return server_bridge.preview_file(data.get('filename'))
    print(f"Preview file: {data.get('filename')}")

def _handle_file_download(data, server_bridge):
    """Handle file download action"""
    if server_bridge and hasattr(server_bridge, 'download_file'):
        return server_bridge.download_file(data.get('filename'))
    print(f"Download file: {data.get('filename')}")

def _handle_file_verify(data, server_bridge):
    """Handle file verify action"""
    if server_bridge and hasattr(server_bridge, 'verify_file'):
        return server_bridge.verify_file(data.get('filename'))
    print(f"Verify file: {data.get('filename')}")

def _handle_file_delete(data, server_bridge):
    """Handle file delete action"""
    if server_bridge and hasattr(server_bridge, 'delete_file'):
        return server_bridge.delete_file(data.get('filename'))
    print(f"Delete file: {data.get('filename')}")

def _handle_database_view_details(data, server_bridge):
    """Handle database view details action"""
    if server_bridge and hasattr(server_bridge, 'view_row_details'):
        return server_bridge.view_row_details(data)
    print(f"View database row details: {data}")

def _handle_database_edit_row(data, server_bridge):
    """Handle database edit row action"""
    if server_bridge and hasattr(server_bridge, 'edit_database_row'):
        return server_bridge.edit_database_row(data)
    print(f"Edit database row: {data}")

def _handle_database_delete_row(data, server_bridge):
    """Handle database delete row action"""
    if server_bridge and hasattr(server_bridge, 'delete_database_row'):
        return server_bridge.delete_database_row(data)
    print(f"Delete database row: {data}")

# Enhanced table methods for specialized functionality
def _apply_client_enhancements(self):
    """Apply client-specific enhancements to the table"""
    # Override cell formatting for client-specific columns
    original_create_data_rows = self._create_data_rows
    
    def enhanced_create_data_rows():
        rows = original_create_data_rows()
        for row in rows:
            # Apply client-specific formatting to status cells
            if len(row.cells) > 2:  # Status column
                status_cell = row.cells[2]
                if hasattr(status_cell, 'content') and hasattr(status_cell.content, 'value'):
                    status_value = status_cell.content.value
                    row.cells[2] = ft.DataCell(_format_status_display(status_value, self))
        return rows
    
    self._create_data_rows = enhanced_create_data_rows

def _apply_file_enhancements(self):
    """Apply file-specific enhancements to the table"""
    # Override cell formatting for file-specific columns
    original_create_data_rows = self._create_data_rows
    
    def enhanced_create_data_rows():
        rows = original_create_data_rows()
        for row in rows:
            # Apply file-specific formatting to type cells
            if len(row.cells) > 2:  # Type column
                filename_cell = row.cells[1]  # Filename column
                if hasattr(filename_cell, 'content') and hasattr(filename_cell.content, 'value'):
                    filename = filename_cell.content.value
                    row.cells[2] = ft.DataCell(_get_file_type_display(filename, self))
        return rows
    
    self._create_data_rows = enhanced_create_data_rows

def _apply_database_enhancements(self):
    """Apply database-specific enhancements to the table"""
    # Database tables use dynamic columns, so enhancements are minimal
    # Focus on cell value formatting
    pass

# Bind the enhancement methods to the class
EnhancedTable._apply_client_enhancements = _apply_client_enhancements
EnhancedTable._apply_file_enhancements = _apply_file_enhancements
EnhancedTable._apply_database_enhancements = _apply_database_enhancements

# Add placeholders for enhancement methods
EnhancedTable._enhance_client_table = lambda self: self._apply_client_enhancements()
EnhancedTable._enhance_file_table = lambda self: self._apply_file_enhancements()
EnhancedTable._enhance_database_table = lambda self: self._apply_database_enhancements()

# Utility function for file statistics (absorbed from FileTable)
def get_file_statistics(files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get statistics about a file list - absorbed from FileTable"""
    if not files:
        return {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'avg_size': 0
        }
    
    # Create a temporary table instance for format_file_size method
    temp_table = type('TempTable', (), {
        'format_file_size': lambda self, size: EnhancedTable.format_file_size(self, size)
    })()
    
    total_size = sum(f.get('size', 0) for f in files)
    file_types = {}
    
    for file_obj in files:
        filename = file_obj.get('filename', file_obj.get('name', 'Unknown'))
        extension = filename.split('.')[-1].lower() if '.' in filename else 'no_ext'
        file_types[extension] = file_types.get(extension, 0) + 1
    
    return {
        'total_files': len(files),
        'total_size': total_size,
        'total_size_formatted': temp_table.format_file_size(total_size),
        'file_types': file_types,
        'avg_size': total_size // len(files) if files else 0,
        'avg_size_formatted': temp_table.format_file_size(total_size // len(files)) if files else "0 B"
    }

if __name__ == "__main__":
    print("✨ Enhanced Table Components Module - ABSORPTION METHOD APPLIED ✨")
    print("This module provides ALL table functionality in ONE consolidated file:")
    print("- Enhanced table implementation (original base)")
    print("- Table data structures (absorbed from unified_table_base.py)")
    print("- Specialized table presets (absorbed from specialized_tables.py)")
    print("- Domain-specific factory methods")
    print("\n✅ One import, all table functionality!")
    print("\nUsage:")
    print("from flet_server_gui.ui.widgets.enhanced_tables import (")
    print("    EnhancedTable, create_client_table, create_file_table, create_database_table")
    print(")")
