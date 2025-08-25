#!/usr/bin/env python3
"""
Enhanced Table Sorting Engine
Advanced multi-column sorting functionality for table data.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from .data_models import SortDirection, ColumnSort, SortState, TableData, TableColumn


class SortingEngine:
    """Advanced sorting engine for table data"""
    
    @staticmethod
    def apply_sorting(data: TableData, sort_state: SortState, 
                     column_configs: Optional[Dict[str, TableColumn]] = None) -> TableData:
        """Apply multi-column sorting to the data"""
        if not data or not sort_state.column_sorts:
            return data
        
        # Create a copy to avoid modifying original data
        sorted_data = data.copy()
        
        # Get sort configurations ordered by priority
        sort_configs = sorted(
            sort_state.column_sorts.values(),
            key=lambda s: s.priority
        )
        
        # Apply sorts in reverse priority order (stable sort)
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
        
        # Get column configuration if available
        column_config = column_configs.get(column_key) if column_configs else None
        data_type = column_config.data_type if column_config else "string"
        
        try:
            # Sort with appropriate key function based on data type
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
            return data  # Return original data if sorting fails
    
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
            return float('-inf')  # Sort None values to the beginning
        
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Try to parse string as number
                cleaned_value = value.replace(',', '').replace('$', '').replace('%', '')
                return float(cleaned_value)
            else:
                return float('-inf')  # Non-numeric types go to beginning
        except (ValueError, TypeError):
            return float('-inf')  # Invalid values go to beginning
    
    @staticmethod
    def _get_date_sort_key(row: Dict[str, Any], column_key: str) -> datetime:
        """Get sort key for date values"""
        value = row.get(column_key)
        if value is None:
            return datetime.min  # Sort None values to the beginning
        
        try:
            if isinstance(value, datetime):
                return value
            elif isinstance(value, str):
                # Try common date formats
                date_formats = [
                    "%Y-%m-%d",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%d/%m/%Y",
                    "%m/%d/%Y",
                    "%d-%m-%Y",
                    "%m-%d-%Y"
                ]
                
                for fmt in date_formats:
                    try:
                        return datetime.strptime(value, fmt)
                    except ValueError:
                        continue
                
                # If no format matches, try ISO format parsing
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    return datetime.min
            else:
                return datetime.min  # Non-date types go to beginning
        except Exception:
            return datetime.min  # Invalid dates go to beginning
    
    @staticmethod
    def _get_boolean_sort_key(row: Dict[str, Any], column_key: str) -> int:
        """Get sort key for boolean values"""
        value = row.get(column_key)
        if value is None:
            return -1  # Sort None values to the beginning
        
        try:
            if isinstance(value, bool):
                return int(value)
            elif isinstance(value, str):
                # Convert string representations to boolean
                lower_value = value.lower().strip()
                if lower_value in ['true', '1', 'yes', 'on', 'enabled']:
                    return 1
                elif lower_value in ['false', '0', 'no', 'off', 'disabled']:
                    return 0
                else:
                    return -1  # Unknown string values go to beginning
            elif isinstance(value, (int, float)):
                return 1 if value != 0 else 0
            else:
                return -1  # Other types go to beginning
        except Exception:
            return -1  # Invalid values go to beginning
    
    @staticmethod
    def add_sort(sort_state: SortState, column_key: str, direction: SortDirection,
                priority: Optional[int] = None) -> SortState:
        """Add or update a sort configuration"""
        if priority is None:
            # Find next available priority
            existing_priorities = [sort.priority for sort in sort_state.column_sorts.values()]
            priority = max(existing_priorities, default=0) + 1
        
        sort_state.column_sorts[column_key] = ColumnSort(
            column_key=column_key,
            direction=direction,
            priority=priority
        )
        
        # Update active sort count
        sort_state.active_sort_count = len(sort_state.column_sorts)
        
        return sort_state
    
    @staticmethod
    def remove_sort(sort_state: SortState, column_key: str) -> SortState:
        """Remove a sort configuration"""
        if column_key in sort_state.column_sorts:
            removed_priority = sort_state.column_sorts[column_key].priority
            del sort_state.column_sorts[column_key]
            
            # Adjust priorities of remaining sorts
            for sort_config in sort_state.column_sorts.values():
                if sort_config.priority > removed_priority:
                    sort_config.priority -= 1
            
            # Update active sort count
            sort_state.active_sort_count = len(sort_state.column_sorts)
        
        return sort_state
    
    @staticmethod
    def clear_all_sorts(sort_state: SortState) -> SortState:
        """Clear all sort configurations"""
        sort_state.column_sorts.clear()
        sort_state.active_sort_count = 0
        return sort_state
    
    @staticmethod
    def toggle_sort(sort_state: SortState, column_key: str) -> Tuple[SortState, SortDirection]:
        """Toggle sort direction for a column (ASC -> DESC -> None -> ASC...)"""
        if column_key in sort_state.column_sorts:
            current_sort = sort_state.column_sorts[column_key]
            if current_sort.direction == SortDirection.ASC:
                # Change to DESC
                current_sort.direction = SortDirection.DESC
                new_direction = SortDirection.DESC
            else:
                # Remove sort (DESC -> None)
                sort_state = SortingEngine.remove_sort(sort_state, column_key)
                new_direction = None
        else:
            # Add ASC sort (None -> ASC)
            sort_state = SortingEngine.add_sort(sort_state, column_key, SortDirection.ASC)
            new_direction = SortDirection.ASC
        
        return sort_state, new_direction
    
    @staticmethod
    def create_sort_summary(sort_state: SortState) -> Dict[str, Any]:
        """Create a summary of active sorts"""
        return {
            'total_sorts': sort_state.active_sort_count,
            'sort_details': {
                column: {
                    'direction': sort_config.direction.value,
                    'priority': sort_config.priority
                }
                for column, sort_config in sort_state.column_sorts.items()
            },
            'sort_order': sorted(
                [(col, config.direction.value) for col, config in sort_state.column_sorts.items()],
                key=lambda x: sort_state.column_sorts[x[0]].priority
            )
        }
    
    @staticmethod
    def validate_sort_config(sort_config: ColumnSort) -> List[str]:
        """Validate sort configuration and return list of errors"""
        errors = []
        
        try:
            if not sort_config.column_key:
                errors.append("Column key is required")
            
            if not isinstance(sort_config.direction, SortDirection):
                errors.append("Invalid sort direction")
            
            if sort_config.priority < 0:
                errors.append("Sort priority must be non-negative")
            
        except Exception as e:
            errors.append(f"Sort validation error: {str(e)}")
        
        return errors
    
    @staticmethod
    def get_sortable_columns(column_configs: Dict[str, TableColumn]) -> List[str]:
        """Get list of sortable column keys"""
        return [key for key, config in column_configs.items() if config.sortable]
    
    @staticmethod
    def optimize_sort_priorities(sort_state: SortState) -> SortState:
        """Optimize sort priorities to remove gaps"""
        sorted_configs = sorted(
            sort_state.column_sorts.items(),
            key=lambda x: x[1].priority
        )
        
        for i, (column_key, sort_config) in enumerate(sorted_configs):
            sort_config.priority = i + 1
        
        return sort_state
