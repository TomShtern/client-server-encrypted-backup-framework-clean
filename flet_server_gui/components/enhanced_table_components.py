"""
Enhanced Table Components for Flet Server GUI
Advanced data table with sophisticated search, filtering, sorting, and context menu functionality
Phase 7.2 Implementation: Professional-grade table management similar to TKinter ModernTable
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
    Phase 7.2: Professional table management with TKinter ModernTable feature parity.
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
        
        # UI components
        self.table_container = ft.Container()
        self.search_bar = ft.TextField()
        self.filter_panel = ft.Container()
        self.sort_indicator_row = ft.Row()
        self.pagination_controls = ft.Row()
        self.selection_info = ft.Text()
        self.bulk_action_bar = ft.Row(visible=False)
        
        # Settings persistence
        self.table_id = f"table_{id(self)}"
        self._load_table_settings()
        
        logger.info("✅ Enhanced data table initialized")
    
    def create_enhanced_table(self) -> ft.Container:
        """Create the main enhanced table view"""
        
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
        
        # Context menu (invisible until needed)
        context_menu = self._create_context_menu()
        
        self.table_container = ft.Container(
            content=ft.Column([
                header,
                filter_panel,
                sort_panel,
                selection_panel,
                data_table,
                pagination,
                context_menu
            ], spacing=10),
            expand=True
        )
        
        # Load initial data
        self._refresh_data()
        
        return self.table_container
    
    def _create_table_header(self) -> ft.Container:
        """Create table header with search and controls"""
        
        self.search_bar = ft.TextField(
            label="Global Search",
            prefix_icon=ft.icons.search,
            suffix=ft.IconButton(
                icon=ft.icons.clear,
                tooltip="Clear Search",
                on_click=self._clear_search
            ),
            on_change=self._on_search_changed,
            expand=True
        )
        
        return ft.Container(
            content=ft.Row([
                self.search_bar,
                ft.IconButton(
                    icon=ft.icons.filter_list,
                    tooltip="Toggle Filters",
                    on_click=self._toggle_filter_panel
                ),
                ft.IconButton(
                    icon=ft.icons.sort,
                    tooltip="Clear Sorting",
                    on_click=self._clear_sorting
                ),
                ft.IconButton(
                    icon=ft.icons.refresh,
                    tooltip="Refresh Data",
                    on_click=self._refresh_data
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text="Export Visible Data",
                            icon=ft.icons.file_download,
                            on_click=self._export_visible_data
                        ),
                        ft.PopupMenuItem(
                            text="Export All Data",
                            icon=ft.icons.download,
                            on_click=self._export_all_data
                        ),
                        ft.PopupMenuItem(),  # Separator
                        ft.PopupMenuItem(
                            text="Table Settings",
                            icon=ft.icons.settings,
                            on_click=self._show_table_settings
                        )
                    ],
                    tooltip="Table Options"
                )
            ], alignment=ft.MainAxisAlignment.START),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            padding=10,
            border_radius=8
        )
    
    def _create_filter_panel(self) -> ft.Container:
        """Create collapsible filter panel"""
        
        filter_controls = []
        
        for col_key, column in self.columns.items():
            if not column.filterable:
                continue
                
            # Filter control based on data type
            if column.data_type == "text":
                filter_control = self._create_text_filter(col_key, column)
            elif column.data_type == "number":
                filter_control = self._create_number_filter(col_key, column)
            elif column.data_type == "date":
                filter_control = self._create_date_filter(col_key, column)
            else:
                filter_control = self._create_text_filter(col_key, column)
            
            filter_controls.append(filter_control)
        
        self.filter_panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Column Filters", weight=ft.FontWeight.BOLD),
                    ft.Container(expand=1),
                    ft.TextButton(
                        "Clear All",
                        icon=ft.icons.clear_all,
                        on_click=self._clear_all_filters
                    )
                ]),
                ft.Divider(),
                ft.Column(filter_controls, spacing=10)
            ]),
            visible=False,
            bgcolor=ft.Colors.SURFACE,
            padding=10,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        )
        
        return self.filter_panel
    
    def _create_text_filter(self, col_key: str, column: TableColumn) -> ft.Row:
        """Create text filter controls"""
        
        operator_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("contains", "Contains"),
                ft.dropdown.Option("equals", "Equals"),
                ft.dropdown.Option("starts_with", "Starts With"),
                ft.dropdown.Option("ends_with", "Ends With"),
                ft.dropdown.Option("regex", "Regex")
            ],
            value="contains",
            width=120,
            on_change=lambda e: self._update_filter(col_key, e)
        )
        
        filter_input = ft.TextField(
            label=f"Filter {column.title}",
            on_change=lambda e: self._update_filter(col_key, e),
            expand=True
        )
        
        case_sensitive_switch = ft.Checkbox(
            label="Case Sensitive",
            value=False,
            on_change=lambda e: self._update_filter(col_key, e)
        )
        
        return ft.Row([
            ft.Text(column.title, width=100),
            operator_dropdown,
            filter_input,
            case_sensitive_switch
        ])
    
    def _create_number_filter(self, col_key: str, column: TableColumn) -> ft.Row:
        """Create numeric filter controls"""
        
        operator_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("equals", "Equals"),
                ft.dropdown.Option("gt", "Greater Than"),
                ft.dropdown.Option("lt", "Less Than")
            ],
            value="equals",
            width=120,
            on_change=lambda e: self._update_filter(col_key, e)
        )
        
        filter_input = ft.TextField(
            label=f"Filter {column.title}",
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=lambda e: self._update_filter(col_key, e),
            expand=True
        )
        
        return ft.Row([
            ft.Text(column.title, width=100),
            operator_dropdown,
            filter_input
        ])
    
    def _create_date_filter(self, col_key: str, column: TableColumn) -> ft.Row:
        """Create date filter controls"""
        
        # Simplified date filter - can be expanded
        filter_input = ft.TextField(
            label=f"Filter {column.title} (YYYY-MM-DD)",
            on_change=lambda e: self._update_filter(col_key, e),
            expand=True
        )
        
        return ft.Row([
            ft.Text(column.title, width=100),
            ft.Text("Date:", width=120),
            filter_input
        ])
    
    def _create_sort_panel(self) -> ft.Container:
        """Create sort indicators panel"""
        
        sort_chips = []
        for col_key, sort_config in sorted(self.column_sorts.items(), key=lambda x: x[1].priority):
            column = self.columns[col_key]
            
            sort_chip = ft.Chip(
                label=ft.Text(f"{column.title} {sort_config.direction.value}"),
                leading=ft.Icon(
                    ft.icons.arrow_upward if sort_config.direction == SortDirection.ASC else ft.icons.arrow_downward
                ),
                delete_icon=ft.icons.close,
                on_delete=lambda e, k=col_key: self._remove_sort(k)
            )
            sort_chips.append(sort_chip)
        
        self.sort_indicator_row = ft.Row(sort_chips, wrap=True)
        
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Active Sorting:", size=12, weight=ft.FontWeight.W500),
                    ft.Container(expand=1)
                ]),
                self.sort_indicator_row
            ]),
            visible=bool(sort_chips),
            padding=ft.padding.symmetric(horizontal=10),
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            border_radius=4
        )
    
    def _create_selection_panel(self) -> ft.Container:
        """Create selection info and bulk actions panel"""
        
        self.selection_info = ft.Text("No items selected", size=12)
        
        bulk_action_buttons = []
        for action in self.bulk_actions:
            button = ft.ElevatedButton(
                text=action.name,
                icon=getattr(ft.icons, action.icon, ft.icons.circle),
                on_click=lambda e, a=action: self._execute_bulk_action(a),
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.ON_PRIMARY
            )
            bulk_action_buttons.append(button)
        
        self.bulk_action_bar = ft.Row(
            bulk_action_buttons,
            visible=False,
            spacing=10
        )
        
        return ft.Container(
            content=ft.Row([
                self.selection_info,
                ft.Container(expand=1),
                self.bulk_action_bar
            ]),
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            border_radius=4
        )
    
    def _create_data_table(self) -> ft.DataTable:
        """Create the main data table"""
        
        # Create column headers with sort controls
        table_columns = []
        
        # Selection column
        select_all_checkbox = ft.Checkbox(on_change=self._select_all_rows)
        table_columns.append(ft.DataColumn(select_all_checkbox))
        
        # Data columns
        for col_key in self.column_order:
            column = self.columns[col_key]
            
            header_content = ft.Row([
                ft.Text(column.title, weight=ft.FontWeight.BOLD),
                ft.IconButton(
                    icon=ft.icons.sort,
                    icon_size=16,
                    on_click=lambda e, k=col_key: self._toggle_column_sort(k),
                    tooltip=f"Sort by {column.title}"
                ) if column.sortable else ft.Container()
            ], tight=True)
            
            table_columns.append(ft.DataColumn(header_content))
        
        # Actions column
        table_columns.append(ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)))
        
        # Create table with empty rows initially
        self.data_table = ft.DataTable(
            columns=table_columns,
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            vertical_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            horizontal_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
            data_row_max_height=60
        )
        
        return self.data_table
    
    def _create_context_menu(self) -> ft.Container:
        """Create context menu for right-click actions"""
        
        menu_items = []
        for action in self.row_actions:
            menu_item = ft.ListTile(
                leading=ft.Icon(getattr(ft.icons, action.icon, ft.icons.circle)),
                title=ft.Text(action.name),
                on_click=lambda e, a=action: self._execute_row_action(a)
            )
            menu_items.append(menu_item)
            
            if action.separator_after:
                menu_items.append(ft.Divider())
        
        context_menu = ft.Container(
            content=ft.Column(menu_items, tight=True),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=5,
            visible=False
        )
        
        return context_menu
    
    def _create_pagination_controls(self) -> ft.Container:
        """Create pagination controls"""
        
        page_info = ft.Text("", size=12)
        
        prev_button = ft.IconButton(
            icon=ft.icons.chevron_left,
            on_click=self._previous_page,
            tooltip="Previous Page"
        )
        
        next_button = ft.IconButton(
            icon=ft.icons.chevron_right,
            on_click=self._next_page,
            tooltip="Next Page"
        )
        
        rows_per_page_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option("25", "25 per page"),
                ft.dropdown.Option("50", "50 per page"),
                ft.dropdown.Option("100", "100 per page"),
                ft.dropdown.Option("200", "200 per page")
            ],
            value=str(self.rows_per_page),
            width=120,
            on_change=self._change_rows_per_page
        )
        
        self.pagination_controls = ft.Row([
            page_info,
            ft.Container(expand=1),
            prev_button,
            next_button,
            ft.VerticalDivider(),
            rows_per_page_dropdown
        ])
        
        return ft.Container(
            content=self.pagination_controls,
            padding=10,
            bgcolor=ft.Colors.SURFACE_VARIANT,
            border_radius=8
        )
    
    def _refresh_data(self, e=None):
        """Refresh table data from source"""
        try:
            self.raw_data = self.data_source()
            self._apply_filters_and_sorting()
            self._update_table_display()
            logger.info(f"✅ Table data refreshed: {len(self.raw_data)} total rows")
            
        except Exception as ex:
            logger.error(f"❌ Error refreshing table data: {ex}")
    
    def _apply_filters_and_sorting(self):
        """Apply all active filters and sorting to the data"""
        
        # Start with raw data
        filtered_data = list(self.raw_data)
        
        # Apply global search
        if self.global_search.strip():
            search_term = self.global_search.lower()
            filtered_data = [
                row for row in filtered_data
                if any(search_term in str(row.get(key, "")).lower() 
                      for key in self.columns.keys())
            ]
        
        # Apply column filters
        for col_key, filter_config in self.column_filters.items():
            if not filter_config.enabled or not filter_config.value:
                continue
                
            filtered_data = self._apply_column_filter(filtered_data, col_key, filter_config)
        
        # Apply sorting
        if self.column_sorts:
            # Multi-column sorting
            sort_keys = sorted(self.column_sorts.items(), key=lambda x: x[1].priority)
            
            for col_key, sort_config in reversed(sort_keys):
                reverse = (sort_config.direction == SortDirection.DESC)
                
                try:
                    filtered_data.sort(
                        key=lambda row: row.get(col_key, ""),
                        reverse=reverse
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Error sorting by {col_key}: {e}")
        
        self.filtered_data = filtered_data
    
    def _apply_column_filter(self, data: List[Dict], col_key: str, filter_config: ColumnFilter) -> List[Dict]:
        """Apply a single column filter to the data"""
        
        if not filter_config.value:
            return data
        
        filtered_data = []
        filter_value = filter_config.value
        
        if not filter_config.case_sensitive and isinstance(filter_value, str):
            filter_value = filter_value.lower()
        
        for row in data:
            row_value = row.get(col_key, "")
            
            if not filter_config.case_sensitive and isinstance(row_value, str):
                row_value = row_value.lower()
            
            try:
                if filter_config.operator == FilterOperator.EQUALS:
                    if str(row_value) == str(filter_value):
                        filtered_data.append(row)
                        
                elif filter_config.operator == FilterOperator.CONTAINS:
                    if str(filter_value) in str(row_value):
                        filtered_data.append(row)
                        
                elif filter_config.operator == FilterOperator.STARTS_WITH:
                    if str(row_value).startswith(str(filter_value)):
                        filtered_data.append(row)
                        
                elif filter_config.operator == FilterOperator.ENDS_WITH:
                    if str(row_value).endswith(str(filter_value)):
                        filtered_data.append(row)
                        
                elif filter_config.operator == FilterOperator.REGEX:
                    if re.search(str(filter_value), str(row_value)):
                        filtered_data.append(row)
                        
                elif filter_config.operator == FilterOperator.GREATER_THAN:
                    if float(row_value) > float(filter_value):
                        filtered_data.append(row)
                        
                elif filter_config.operator == FilterOperator.LESS_THAN:
                    if float(row_value) < float(filter_value):
                        filtered_data.append(row)
                        
            except Exception:
                # Skip rows with invalid data for numeric/regex operations
                continue
        
        return filtered_data
    
    def _update_table_display(self):
        """Update the table display with current page data"""
        
        # Calculate pagination
        total_rows = len(self.filtered_data)
        total_pages = max(1, (total_rows + self.rows_per_page - 1) // self.rows_per_page)
        self.current_page = min(self.current_page, total_pages - 1)
        
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, total_rows)
        page_data = self.filtered_data[start_idx:end_idx]
        
        # Create table rows
        table_rows = []
        
        for i, row_data in enumerate(page_data):
            row_index = start_idx + i
            
            # Selection checkbox
            row_checkbox = ft.Checkbox(
                value=row_index in self.selected_rows,
                on_change=lambda e, idx=row_index: self._toggle_row_selection(idx)
            )
            
            # Data cells
            data_cells = [ft.DataCell(row_checkbox)]
            
            for col_key in self.column_order:
                column = self.columns[col_key]
                raw_value = row_data.get(col_key, "")
                
                # Apply formatting function if provided
                if column.format_function:
                    formatted_value = column.format_function(raw_value)
                else:
                    formatted_value = str(raw_value)
                
                cell = ft.DataCell(
                    ft.Text(
                        formatted_value,
                        size=12,
                        text_align=column.alignment
                    )
                )
                data_cells.append(cell)
            
            # Action buttons
            action_buttons = []
            for action in self.row_actions[:3]:  # Limit to 3 visible actions
                button = ft.IconButton(
                    icon=getattr(ft.icons, action.icon, ft.icons.circle),
                    tooltip=action.name,
                    icon_size=16,
                    on_click=lambda e, a=action, r=row_data: self._execute_row_action(a, r)
                )
                action_buttons.append(button)
            
            if len(self.row_actions) > 3:
                more_menu = ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            text=action.name,
                            icon=getattr(ft.icons, action.icon, ft.icons.circle),
                            on_click=lambda e, a=action, r=row_data: self._execute_row_action(a, r)
                        )
                        for action in self.row_actions[3:]
                    ],
                    tooltip="More Actions"
                )
                action_buttons.append(more_menu)
            
            actions_cell = ft.DataCell(ft.Row(action_buttons, tight=True))
            data_cells.append(actions_cell)
            
            table_rows.append(ft.DataRow(cells=data_cells))
        
        # Update table
        self.data_table.rows = table_rows
        self.data_table.update()
        
        # Update pagination info
        page_info_text = f"Showing {start_idx + 1}-{end_idx} of {total_rows} rows (Page {self.current_page + 1} of {total_pages})"
        self.pagination_controls.controls[0].value = page_info_text
        self.pagination_controls.update()
        
        # Update selection info
        selected_count = len(self.selected_rows)
        self.selection_info.value = f"{selected_count} of {total_rows} items selected"
        self.bulk_action_bar.visible = selected_count > 0
        self.selection_info.update()
        self.bulk_action_bar.update()
    
    def _on_search_changed(self, e):
        """Handle global search input change"""
        self.global_search = e.control.value
        self._apply_filters_and_sorting()
        self.current_page = 0
        self._update_table_display()
    
    def _clear_search(self, e):
        """Clear global search"""
        self.search_bar.value = ""
        self.global_search = ""
        self._apply_filters_and_sorting()
        self.current_page = 0
        self._update_table_display()
        self.search_bar.update()
    
    def _toggle_filter_panel(self, e):
        """Toggle filter panel visibility"""
        self.filter_panel.visible = not self.filter_panel.visible
        self.filter_panel.update()
    
    def _clear_sorting(self, e):
        """Clear all sorting"""
        self.column_sorts.clear()
        self._apply_filters_and_sorting()
        self._update_table_display()
        self._update_sort_display()
    
    def _clear_all_filters(self, e):
        """Clear all column filters"""
        self.column_filters.clear()
        self._apply_filters_and_sorting()
        self.current_page = 0
        self._update_table_display()
    
    def _toggle_column_sort(self, col_key: str):
        """Toggle sorting for a column"""
        if col_key in self.column_sorts:
            current_sort = self.column_sorts[col_key]
            if current_sort.direction == SortDirection.ASC:
                current_sort.direction = SortDirection.DESC
            else:
                del self.column_sorts[col_key]
        else:
            # Add new sort with next priority
            max_priority = max([s.priority for s in self.column_sorts.values()], default=-1)
            self.column_sorts[col_key] = ColumnSort(
                direction=SortDirection.ASC,
                priority=max_priority + 1
            )
        
        self._apply_filters_and_sorting()
        self._update_table_display()
        self._update_sort_display()
    
    def _update_sort_display(self):
        """Update sort indicators display"""
        sort_chips = []
        for col_key, sort_config in sorted(self.column_sorts.items(), key=lambda x: x[1].priority):
            column = self.columns[col_key]
            
            sort_chip = ft.Chip(
                label=ft.Text(f"{column.title} {sort_config.direction.value}"),
                leading=ft.Icon(
                    ft.icons.arrow_upward if sort_config.direction == SortDirection.ASC else ft.icons.arrow_downward
                ),
                delete_icon=ft.icons.close,
                on_delete=lambda e, k=col_key: self._remove_sort(k)
            )
            sort_chips.append(sort_chip)
        
        self.sort_indicator_row.controls = sort_chips
        self.sort_indicator_row.update()
    
    def _remove_sort(self, col_key: str):
        """Remove sorting for a specific column"""
        if col_key in self.column_sorts:
            del self.column_sorts[col_key]
            self._apply_filters_and_sorting()
            self._update_table_display()
            self._update_sort_display()
    
    def _select_all_rows(self, e):
        """Select or deselect all visible rows"""
        if e.control.value:
            # Select all visible rows
            start_idx = self.current_page * self.rows_per_page
            end_idx = min(start_idx + self.rows_per_page, len(self.filtered_data))
            for i in range(start_idx, end_idx):
                self.selected_rows.add(i)
        else:
            # Clear selection
            self.selected_rows.clear()
        
        self._update_table_display()
    
    def _toggle_row_selection(self, row_index: int):
        """Toggle selection for a specific row"""
        if row_index in self.selected_rows:
            self.selected_rows.remove(row_index)
        else:
            self.selected_rows.add(row_index)
        
        self._update_table_display()
    
    def _execute_row_action(self, action: TableAction, row_data: Dict[str, Any] = None):
        """Execute a row action"""
        try:
            if action.enabled:
                action.callback(row_data)
                logger.info(f"✅ Executed row action: {action.name}")
        except Exception as e:
            logger.error(f"❌ Error executing row action {action.name}: {e}")
    
    def _execute_bulk_action(self, action: TableAction):
        """Execute a bulk action on selected rows"""
        try:
            if action.enabled and self.selected_rows:
                selected_data = [self.filtered_data[i] for i in self.selected_rows if i < len(self.filtered_data)]
                action.callback(selected_data)
                logger.info(f"✅ Executed bulk action: {action.name} on {len(selected_data)} items")
        except Exception as e:
            logger.error(f"❌ Error executing bulk action {action.name}: {e}")
    
    def _previous_page(self, e):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self._update_table_display()
    
    def _next_page(self, e):
        """Go to next page"""
        total_pages = max(1, (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._update_table_display()
    
    def _change_rows_per_page(self, e):
        """Change number of rows per page"""
        self.rows_per_page = int(e.control.value)
        self.current_page = 0
        self._update_table_display()
    
    def _update_filter(self, col_key: str, e):
        """Update column filter based on UI input"""
        # Implementation depends on the specific filter control
        # This is a simplified version
        filter_value = e.control.value if hasattr(e.control, 'value') else e.control.data
        
        if filter_value:
            if col_key not in self.column_filters:
                self.column_filters[col_key] = ColumnFilter(
                    operator=FilterOperator.CONTAINS,
                    value=filter_value
                )
            else:
                self.column_filters[col_key].value = filter_value
        else:
            self.column_filters.pop(col_key, None)
        
        self._apply_filters_and_sorting()
        self.current_page = 0
        self._update_table_display()
    
    def _export_visible_data(self, e):
        """Export currently visible/filtered data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"table_export_filtered_{timestamp}.json"
            
            export_data = {
                'metadata': {
                    'export_time': datetime.now().isoformat(),
                    'total_rows': len(self.filtered_data),
                    'filters_applied': len(self.column_filters),
                    'sorts_applied': len(self.column_sorts)
                },
                'data': self.filtered_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"✅ Exported filtered data to {filename}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting filtered data: {e}")
    
    def _export_all_data(self, e):
        """Export all data regardless of filters"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"table_export_all_{timestamp}.json"
            
            export_data = {
                'metadata': {
                    'export_time': datetime.now().isoformat(),
                    'total_rows': len(self.raw_data)
                },
                'data': self.raw_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"✅ Exported all data to {filename}")
            
        except Exception as e:
            logger.error(f"❌ Error exporting all data: {e}")
    
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
        self.row_actions.append(action)
        logger.info(f"✅ Added row action: {action.name}")
    
    def add_bulk_action(self, action: TableAction):
        """Dynamically add a bulk action"""
        self.bulk_actions.append(action)
        logger.info(f"✅ Added bulk action: {action.name}")
    
    def get_selected_data(self) -> List[Dict[str, Any]]:
        """Get data for currently selected rows"""
        return [self.filtered_data[i] for i in self.selected_rows if i < len(self.filtered_data)]
    
    def clear_selection(self):
        """Clear all row selections"""
        self.selected_rows.clear()
        self._update_table_display()
    
    def get_table_stats(self) -> Dict[str, Any]:
        """Get table statistics"""
        return {
            'total_rows': len(self.raw_data),
            'filtered_rows': len(self.filtered_data),
            'selected_rows': len(self.selected_rows),
            'current_page': self.current_page + 1,
            'total_pages': max(1, (len(self.filtered_data) + self.rows_per_page - 1) // self.rows_per_page),
            'active_filters': len(self.column_filters),
            'active_sorts': len(self.column_sorts)
        }