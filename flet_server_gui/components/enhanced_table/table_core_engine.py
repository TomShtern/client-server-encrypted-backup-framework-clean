#!/usr/bin/env python3
"""
Enhanced Table Core Engine
Combines data models, filtering, sorting, and export functionality.
Consolidated from multiple small modules into one comprehensive engine.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Callable, Any, List, Dict, Tuple
import flet as ft
import re
import json
from datetime import datetime


# =============================================================================
# DATA MODELS AND ENUMS
# =============================================================================

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
        if self.operator in [FilterOperator.IS_EMPTY, FilterOperator.IS_NOT_EMPTY]:
            self.value = None


@dataclass
class ColumnSort:
    """Configuration for column sorting"""
    column_key: str
    direction: SortDirection
    priority: int = 0
    
    def __post_init__(self):
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
        if not self.key or not self.title:
            raise ValueError("Column key and title are required")
        if self.width is not None and self.width <= 0:
            raise ValueError("Column width must be positive")
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
    enabled_condition: Optional[Callable] = None
    style: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.key or not self.title:
            raise ValueError("Action key and title are required")
        if self.action_type not in ["row", "bulk"]:
            raise ValueError("Action type must be 'row' or 'bulk'")
        if self.confirmation_required and not self.confirmation_message:
            self.confirmation_message = f"Are you sure you want to {self.title.lower()}?"


@dataclass
class FilterState:
    """Current state of table filtering"""
    column_filters: Dict[str, ColumnFilter]
    global_search: str
    active_filter_count: int = 0
    
    def __post_init__(self):
        self.active_filter_count = len(self.column_filters)
        if self.global_search and self.global_search.strip():
            self.active_filter_count += 1


@dataclass
class SortState:
    """Current state of table sorting"""
    column_sorts: Dict[str, ColumnSort]
    active_sort_count: int = 0
    
    def __post_init__(self):
        self.active_sort_count = len(self.column_sorts)


@dataclass
class PaginationState:
    """Current state of table pagination"""
    current_page: int = 1
    rows_per_page: int = 25
    total_rows: int = 0
    total_pages: int = 1
    
    def __post_init__(self):
        if self.total_rows > 0 and self.rows_per_page > 0:
            self.total_pages = (self.total_rows + self.rows_per_page - 1) // self.rows_per_page
        else:
            self.total_pages = 1
        if self.current_page < 1:
            self.current_page = 1
        elif self.current_page > self.total_pages:
            self.current_page = self.total_pages


# Type aliases
TableData = List[Dict[str, Any]]
ColumnConfig = List[TableColumn]
ActionConfig = List[TableAction]


# =============================================================================
# FILTER ENGINE
# =============================================================================

class FilterEngine:
    """Advanced filtering engine for table data"""
    
    @staticmethod
    def apply_filters(data: TableData, filter_state: FilterState, 
                     searchable_columns: Optional[List[str]] = None) -> TableData:
        """Apply all active filters to the data"""
        if not data:
            return data
        
        filtered_data = data
        
        # Apply column-specific filters
        for column_key, column_filter in filter_state.column_filters.items():
            filtered_data = FilterEngine._apply_column_filter(filtered_data, column_filter)
        
        # Apply global search
        if filter_state.global_search and filter_state.global_search.strip():
            filtered_data = FilterEngine._apply_global_search(
                filtered_data, filter_state.global_search, searchable_columns or []
            )
        
        return filtered_data
    
    @staticmethod
    def _apply_column_filter(data: TableData, column_filter: ColumnFilter) -> TableData:
        """Apply a single column filter to the data"""
        if not data or not column_filter:
            return data
        
        filtered_data = []
        for row in data:
            if FilterEngine._row_matches_filter(row, column_filter):
                filtered_data.append(row)
        return filtered_data
    
    @staticmethod
    def _row_matches_filter(row: Dict[str, Any], column_filter: ColumnFilter) -> bool:
        """Check if a row matches the specified filter"""
        try:
            column_value = row.get(column_filter.column_key)
            
            if column_value is None:
                return column_filter.operator in [FilterOperator.IS_EMPTY]
            
            if not isinstance(column_value, str):
                column_value_str = str(column_value)
            else:
                column_value_str = column_value
            
            filter_value = column_filter.value
            if filter_value is not None and not isinstance(filter_value, str):
                filter_value = str(filter_value)
            
            if not column_filter.case_sensitive and isinstance(column_value_str, str):
                column_value_str = column_value_str.lower()
                if filter_value:
                    filter_value = filter_value.lower()
            
            return FilterEngine._evaluate_filter_condition(
                column_value_str, column_filter.operator, filter_value, column_value
            )
            
        except Exception as e:
            print(f"Error applying filter to row: {e}")
            return True
    
    @staticmethod
    def _evaluate_filter_condition(value_str: str, operator: FilterOperator, 
                                  filter_value: Any, original_value: Any) -> bool:
        """Evaluate filter condition based on operator"""
        try:
            if operator == FilterOperator.CONTAINS:
                return filter_value in value_str if filter_value else True
            elif operator == FilterOperator.EQUALS:
                return value_str == filter_value if filter_value is not None else True
            elif operator == FilterOperator.NOT_EQUALS:
                return value_str != filter_value if filter_value is not None else True
            elif operator == FilterOperator.STARTS_WITH:
                return value_str.startswith(filter_value) if filter_value else True
            elif operator == FilterOperator.ENDS_WITH:
                return value_str.endswith(filter_value) if filter_value else True
            elif operator == FilterOperator.REGEX:
                if filter_value:
                    try:
                        return bool(re.search(filter_value, value_str))
                    except re.error:
                        return True
                return True
            elif operator == FilterOperator.IS_EMPTY:
                return not value_str or value_str.strip() == ""
            elif operator == FilterOperator.IS_NOT_EMPTY:
                return bool(value_str and value_str.strip())
            elif operator in [FilterOperator.GREATER_THAN, FilterOperator.LESS_THAN,
                            FilterOperator.GREATER_EQUAL, FilterOperator.LESS_EQUAL]:
                return FilterEngine._evaluate_numeric_filter(original_value, operator, filter_value)
            else:
                return True
        except Exception as e:
            print(f"Error evaluating filter condition: {e}")
            return True
    
    @staticmethod
    def _evaluate_numeric_filter(value: Any, operator: FilterOperator, filter_value: Any) -> bool:
        """Evaluate numeric comparison filters"""
        try:
            if isinstance(value, str):
                try:
                    numeric_value = float(value)
                except ValueError:
                    return True
            elif isinstance(value, (int, float)):
                numeric_value = float(value)
            else:
                return True
            
            if isinstance(filter_value, str):
                try:
                    numeric_filter = float(filter_value)
                except ValueError:
                    return True
            elif isinstance(filter_value, (int, float)):
                numeric_filter = float(filter_value)
            else:
                return True
            
            if operator == FilterOperator.GREATER_THAN:
                return numeric_value > numeric_filter
            elif operator == FilterOperator.LESS_THAN:
                return numeric_value < numeric_filter
            elif operator == FilterOperator.GREATER_EQUAL:
                return numeric_value >= numeric_filter
            elif operator == FilterOperator.LESS_EQUAL:
                return numeric_value <= numeric_filter
            else:
                return True
                
        except Exception as e:
            print(f"Error in numeric filter evaluation: {e}")
            return True
    
    @staticmethod
    def _apply_global_search(data: TableData, search_term: str, 
                           searchable_columns: List[str]) -> TableData:
        """Apply global search across specified columns"""
        if not search_term or not search_term.strip():
            return data
        
        search_term = search_term.lower().strip()
        filtered_data = []
        
        for row in data:
            if FilterEngine._row_matches_search(row, search_term, searchable_columns):
                filtered_data.append(row)
        
        return filtered_data
    
    @staticmethod
    def _row_matches_search(row: Dict[str, Any], search_term: str, 
                          searchable_columns: List[str]) -> bool:
        """Check if a row matches the global search term"""
        try:
            columns_to_search = searchable_columns if searchable_columns else row.keys()
            
            for column in columns_to_search:
                if column in row:
                    value = row[column]
                    if value is not None:
                        value_str = str(value).lower()
                        if search_term in value_str:
                            return True
            return False
        except Exception as e:
            print(f"Error in global search: {e}")
            return True


# =============================================================================
# SORTING ENGINE
# =============================================================================

class SortingEngine:
    """Advanced sorting engine for table data"""
    
    @staticmethod
    def apply_sorting(data: TableData, sort_state: SortState, 
                     column_configs: Optional[Dict[str, TableColumn]] = None) -> TableData:
        """Apply multi-column sorting to the data"""
        if not data or not sort_state.column_sorts:
            return data
        
        sorted_data = data.copy()
        
        sort_configs = sorted(
            sort_state.column_sorts.values(),
            key=lambda s: s.priority
        )
        
        for sort_config in reversed(sort_configs):
            sorted_data = SortingEngine._apply_single_column_sort(
                sorted_data, sort_config, column_configs
            )
        
        return sorted_data
    
    @staticmethod
    def _apply_single_column_sort(data: TableData, sort_config: ColumnSort,
                                column_configs: Optional[Dict[str, TableColumn]] = None) -> TableData:
        """Apply sorting for a single column"""
        if not data:
            return data
        
        column_key = sort_config.column_key
        reverse = sort_config.direction == SortDirection.DESC
        
        column_config = column_configs.get(column_key) if column_configs else None
        data_type = column_config.data_type if column_config else "string"
        
        try:
            if data_type == "number":
                sorted_data = sorted(
                    data,
                    key=lambda row: SortingEngine._get_numeric_sort_key(row, column_key),
                    reverse=reverse
                )
            elif data_type == "date":
                sorted_data = sorted(
                    data,
                    key=lambda row: SortingEngine._get_date_sort_key(row, column_key),
                    reverse=reverse
                )
            elif data_type == "boolean":
                sorted_data = sorted(
                    data,
                    key=lambda row: SortingEngine._get_boolean_sort_key(row, column_key),
                    reverse=reverse
                )
            else:  # string or default
                sorted_data = sorted(
                    data,
                    key=lambda row: SortingEngine._get_string_sort_key(row, column_key),
                    reverse=reverse
                )
            
            return sorted_data
        except Exception as e:
            print(f"Error sorting by column {column_key}: {e}")
            return data
    
    @staticmethod
    def _get_string_sort_key(row: Dict[str, Any], column_key: str) -> str:
        """Get sort key for string values"""
        value = row.get(column_key)
        if value is None:
            return ""
        return str(value).lower()
    
    @staticmethod
    def _get_numeric_sort_key(row: Dict[str, Any], column_key: str) -> float:
        """Get sort key for numeric values"""
        value = row.get(column_key)
        if value is None:
            return float('-inf')
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                cleaned_value = value.replace(',', '').replace('$', '').replace('%', '')
                return float(cleaned_value)
            else:
                return float('-inf')
        except (ValueError, TypeError):
            return float('-inf')
    
    @staticmethod
    def _get_date_sort_key(row: Dict[str, Any], column_key: str) -> datetime:
        """Get sort key for date values"""
        value = row.get(column_key)
        if value is None:
            return datetime.min
        
        try:
            if isinstance(value, datetime):
                return value
            elif isinstance(value, str):
                date_formats = [
                    "%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"
                ]
                
                for fmt in date_formats:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    return datetime.min
            else:
                return datetime.min
        except Exception:
            return datetime.min
    
    @staticmethod
    def _get_boolean_sort_key(row: Dict[str, Any], column_key: str) -> int:
        """Get sort key for boolean values"""
        value = row.get(column_key)
        if value is None:
            return -1
        
        try:
            if isinstance(value, bool):
                return int(value)
            elif isinstance(value, str):
                lower_value = value.lower().strip()
                if lower_value in ['true', '1', 'yes', 'on', 'enabled']:
                    return 1
                elif lower_value in ['false', '0', 'no', 'off', 'disabled']:
                    return 0
                else:
                    return -1
            elif isinstance(value, (int, float)):
                return 1 if value != 0 else 0
            else:
                return -1
        except Exception:
            return -1
    
    @staticmethod
    def toggle_sort(sort_state: SortState, column_key: str) -> Tuple[SortState, Optional[SortDirection]]:
        """Toggle sort direction for a column (ASC -> DESC -> None -> ASC...)"""
        if column_key in sort_state.column_sorts:
            current_sort = sort_state.column_sorts[column_key]
            if current_sort.direction == SortDirection.ASC:
                current_sort.direction = SortDirection.DESC
                new_direction = SortDirection.DESC
            else:
                # Remove sort
                removed_priority = sort_state.column_sorts[column_key].priority
                del sort_state.column_sorts[column_key]
                
                # Adjust priorities
                for sort_config in sort_state.column_sorts.values():
                    if sort_config.priority > removed_priority:
                        sort_config.priority -= 1
                
                sort_state.active_sort_count = len(sort_state.column_sorts)
                new_direction = None
        else:
            # Add ASC sort
            existing_priorities = [sort.priority for sort in sort_state.column_sorts.values()]
            priority = max(existing_priorities, default=0) + 1
            
            sort_state.column_sorts[column_key] = ColumnSort(
                column_key=column_key,
                direction=SortDirection.ASC,
                priority=priority
            )
            sort_state.active_sort_count = len(sort_state.column_sorts)
            new_direction = SortDirection.ASC
        
        return sort_state, new_direction


# =============================================================================
# DATA EXPORT ENGINE
# =============================================================================

class DataExporter:
    """Data export functionality for table data"""
    
    @staticmethod
    def export_to_json(data: TableData, export_type: str = "visible", 
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """Export table data to JSON format"""
        try:
            export_data = {
                'metadata': {
                    'export_type': export_type,
                    'exported_at': datetime.now().isoformat(),
                    'total_rows': len(data),
                    'application': 'Enhanced Data Table'
                },
                'data': data
            }
            
            if metadata:
                export_data['metadata'].update(metadata)
            
            return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return "{}"
    
    @staticmethod
    def export_to_csv(data: TableData, columns: Optional[List[str]] = None) -> str:
        """Export table data to CSV format"""
        try:
            if not data:
                return ""
            
            # Use provided columns or infer from first row
            if columns is None:
                columns = list(data[0].keys()) if data else []
            
            # Create CSV header
            csv_lines = []
            csv_lines.append(','.join(f'"{col}"' for col in columns))
            
            # Add data rows
            for row in data:
                values = []
                for col in columns:
                    value = row.get(col, '')
                    # Escape quotes and wrap in quotes
                    escaped_value = str(value).replace('"', '""')
                    values.append(f'"{escaped_value}"')
                csv_lines.append(','.join(values))
            
            return '\n'.join(csv_lines)
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return ""
    
    @staticmethod
    def get_export_summary(data: TableData, filter_state: Optional[FilterState] = None,
                         sort_state: Optional[SortState] = None) -> Dict[str, Any]:
        """Get summary information about the export"""
        return {
            'total_rows': len(data),
            'columns': list(data[0].keys()) if data else [],
            'filters_applied': len(filter_state.column_filters) if filter_state else 0,
            'sorts_applied': len(sort_state.column_sorts) if sort_state else 0,
            'export_timestamp': datetime.now().isoformat()
        }
