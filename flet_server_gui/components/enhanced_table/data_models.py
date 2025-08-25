#!/usr/bin/env python3
"""
Enhanced Table Data Models
Dataclasses, enums, and type definitions for enhanced table functionality.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Any, List, Dict
import flet as ft


class SortDirection(Enum):
    """Enumeration for sort directions"""
    ASC = "asc"
    DESC = "desc"


class FilterOperator(Enum):
    """Enumeration for filter operations"""
    CONTAINS = "contains"
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_EQUAL = "greater_equal"
    LESS_EQUAL = "less_equal"
    REGEX = "regex"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"


@dataclass
class ColumnFilter:
    """Configuration for column filtering"""
    column_key: str
    operator: FilterOperator
    value: Any = None
    case_sensitive: bool = False
    
    def __post_init__(self):
        """Validate filter configuration after initialization"""
        if self.operator in [FilterOperator.IS_EMPTY, FilterOperator.IS_NOT_EMPTY]:
            self.value = None  # These operators don't need a value


@dataclass
class ColumnSort:
    """Configuration for column sorting"""
    column_key: str
    direction: SortDirection
    priority: int = 0  # For multi-column sorting
    
    def __post_init__(self):
        """Validate sort configuration"""
        if self.priority < 0:
            self.priority = 0


@dataclass
class TableColumn:
    """Configuration for table column display and behavior"""
    key: str
    title: str
    width: Optional[int] = None
    sortable: bool = True
    filterable: bool = True
    visible: bool = True
    data_type: str = "string"  # string, number, date, boolean
    format_function: Optional[Callable] = None
    alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.START
    
    def __post_init__(self):
        """Validate column configuration"""
        if not self.key or not self.title:
            raise ValueError("Column key and title are required")
        
        if self.width is not None and self.width <= 0:
            raise ValueError("Column width must be positive")
        
        # Validate data_type
        valid_types = ["string", "number", "date", "boolean"]
        if self.data_type not in valid_types:
            raise ValueError(f"Invalid data_type. Must be one of: {valid_types}")


@dataclass
class TableAction:
    """Configuration for table actions (row and bulk operations)"""
    key: str
    title: str
    icon: str = ft.Icons.ACTION
    action_type: str = "row"  # "row" or "bulk"
    callback: Optional[Callable] = None
    confirmation_required: bool = False
    confirmation_message: str = ""
    enabled_condition: Optional[Callable] = None  # Function to determine if action is enabled
    style: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate action configuration"""
        if not self.key or not self.title:
            raise ValueError("Action key and title are required")
        
        if self.action_type not in ["row", "bulk"]:
            raise ValueError("Action type must be 'row' or 'bulk'")
        
        if self.confirmation_required and not self.confirmation_message:
            self.confirmation_message = f"Are you sure you want to {self.title.lower()}?"


@dataclass
class TableSettings:
    """Configuration for table behavior and appearance"""
    rows_per_page: int = 25
    enable_search: bool = True
    enable_filters: bool = True
    enable_sorting: bool = True
    enable_export: bool = True
    enable_column_resize: bool = True
    enable_column_reorder: bool = False
    show_row_numbers: bool = False
    striped_rows: bool = True
    compact_mode: bool = False
    auto_refresh_interval: Optional[int] = None  # seconds
    
    def __post_init__(self):
        """Validate table settings"""
        if self.rows_per_page <= 0:
            self.rows_per_page = 25
        
        if self.auto_refresh_interval is not None and self.auto_refresh_interval < 5:
            self.auto_refresh_interval = 5  # Minimum 5 seconds


@dataclass
class FilterState:
    """Current state of table filtering"""
    column_filters: Dict[str, ColumnFilter]
    global_search: str
    active_filter_count: int = 0
    
    def __post_init__(self):
        """Update active filter count"""
        self.active_filter_count = len(self.column_filters)
        if self.global_search and self.global_search.strip():
            self.active_filter_count += 1


@dataclass
class SortState:
    """Current state of table sorting"""
    column_sorts: Dict[str, ColumnSort]
    active_sort_count: int = 0
    
    def __post_init__(self):
        """Update active sort count"""
        self.active_sort_count = len(self.column_sorts)


@dataclass
class PaginationState:
    """Current state of table pagination"""
    current_page: int = 1
    rows_per_page: int = 25
    total_rows: int = 0
    total_pages: int = 1
    
    def __post_init__(self):
        """Calculate total pages"""
        if self.total_rows > 0 and self.rows_per_page > 0:
            self.total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page
        else:
            self.total_pages = 1
        
        # Ensure current page is valid
        if self.current_page < 1:
            self.current_page = 1
        elif self.current_page > self.total_pages:
            self.current_page = self.total_pages


@dataclass
class TableState:
    """Complete state of the enhanced table"""
    filter_state: FilterState
    sort_state: SortState
    pagination_state: PaginationState
    selected_rows: List[Any]
    loading: bool = False
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Initialize state components if not provided"""
        if not hasattr(self, 'filter_state') or self.filter_state is None:
            self.filter_state = FilterState({}, "")
        
        if not hasattr(self, 'sort_state') or self.sort_state is None:
            self.sort_state = SortState({})
        
        if not hasattr(self, 'pagination_state') or self.pagination_state is None:
            self.pagination_state = PaginationState()
        
        if not hasattr(self, 'selected_rows') or self.selected_rows is None:
            self.selected_rows = []
    
    def clear_selections(self):
        """Clear all selected rows"""
        self.selected_rows.clear()
    
    def reset_filters(self):
        """Reset all filters to default state"""
        self.filter_state = FilterState({}, "")
    
    def reset_sorting(self):
        """Reset all sorting to default state"""
        self.sort_state = SortState({})
    
    def reset_pagination(self):
        """Reset pagination to first page"""
        self.pagination_state.current_page = 1


# Type aliases for better code readability
TableData = List[Dict[str, Any]]
ColumnConfig = List[TableColumn]
ActionConfig = List[TableAction]
FilterConfig = Dict[str, ColumnFilter]
SortConfig = Dict[str, ColumnSort]
