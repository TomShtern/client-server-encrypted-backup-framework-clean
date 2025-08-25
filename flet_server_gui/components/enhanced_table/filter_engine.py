#!/usr/bin/env python3
"""
Enhanced Table Filter Engine
Advanced filtering functionality for table data.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from .data_models import FilterOperator, ColumnFilter, FilterState, TableData


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
            filtered_data = FilterEngine._apply_column_filter(
                filtered_data, column_filter
            )
        
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
            
            # Handle None values
            if column_value is None:
                return column_filter.operator in [FilterOperator.IS_EMPTY]
            
            # Convert to string for most operations
            if not isinstance(column_value, str):
                column_value_str = str(column_value)
            else:
                column_value_str = column_value
            
            filter_value = column_filter.value
            if filter_value is not None and not isinstance(filter_value, str):
                filter_value = str(filter_value)
            
            # Case sensitivity handling
            if not column_filter.case_sensitive and isinstance(column_value_str, str):
                column_value_str = column_value_str.lower()
                if filter_value:
                    filter_value = filter_value.lower()
            
            # Apply filter based on operator
            return FilterEngine._evaluate_filter_condition(
                column_value_str, column_filter.operator, filter_value, column_value
            )
            
        except Exception as e:
            print(f"Error applying filter to row: {e}")
            return True  # Include row if filter evaluation fails
    
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
                        return True  # Invalid regex, include row
                return True
            
            elif operator == FilterOperator.IS_EMPTY:
                return not value_str or value_str.strip() == ""
            
            elif operator == FilterOperator.IS_NOT_EMPTY:
                return bool(value_str and value_str.strip())
            
            elif operator in [FilterOperator.GREATER_THAN, FilterOperator.LESS_THAN,
                            FilterOperator.GREATER_EQUAL, FilterOperator.LESS_EQUAL]:
                return FilterEngine._evaluate_numeric_filter(
                    original_value, operator, filter_value
                )
            
            else:
                return True  # Unknown operator, include row
                
        except Exception as e:
            print(f"Error evaluating filter condition: {e}")
            return True  # Include row if evaluation fails
    
    @staticmethod
    def _evaluate_numeric_filter(value: Any, operator: FilterOperator, filter_value: Any) -> bool:
        """Evaluate numeric comparison filters"""
        try:
            # Try to convert both values to numbers
            if isinstance(value, str):
                # Try parsing as number
                try:
                    numeric_value = float(value)
                except ValueError:
                    return True  # Can't convert to number, include row
            elif isinstance(value, (int, float)):
                numeric_value = float(value)
            else:
                return True  # Not a numeric type, include row
            
            if isinstance(filter_value, str):
                try:
                    numeric_filter = float(filter_value)
                except ValueError:
                    return True  # Can't convert filter to number, include row
            elif isinstance(filter_value, (int, float)):
                numeric_filter = float(filter_value)
            else:
                return True  # Filter is not numeric, include row
            
            # Apply numeric comparison
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
            return True  # Include row if evaluation fails
    
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
            # If no columns specified, search all columns
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
            return True  # Include row if search fails
    
    @staticmethod
    def create_filter_summary(filter_state: FilterState) -> Dict[str, Any]:
        """Create a summary of active filters"""
        return {
            'total_filters': filter_state.active_filter_count,
            'column_filters': len(filter_state.column_filters),
            'global_search': bool(filter_state.global_search and filter_state.global_search.strip()),
            'filter_details': {
                column: {
                    'operator': filter_config.operator.value,
                    'value': filter_config.value,
                    'case_sensitive': filter_config.case_sensitive
                }
                for column, filter_config in filter_state.column_filters.items()
            },
            'search_term': filter_state.global_search if filter_state.global_search else None
        }
    
    @staticmethod
    def validate_filter_config(column_filter: ColumnFilter) -> List[str]:
        """Validate filter configuration and return list of errors"""
        errors = []
        
        try:
            if not column_filter.column_key:
                errors.append("Column key is required")
            
            if not isinstance(column_filter.operator, FilterOperator):
                errors.append("Invalid filter operator")
            
            # Check if value is required for the operator
            value_required_operators = [
                FilterOperator.CONTAINS, FilterOperator.EQUALS, FilterOperator.NOT_EQUALS,
                FilterOperator.STARTS_WITH, FilterOperator.ENDS_WITH, FilterOperator.REGEX,
                FilterOperator.GREATER_THAN, FilterOperator.LESS_THAN,
                FilterOperator.GREATER_EQUAL, FilterOperator.LESS_EQUAL
            ]
            
            if column_filter.operator in value_required_operators:
                if column_filter.value is None or (isinstance(column_filter.value, str) and not column_filter.value.strip()):
                    errors.append(f"Value is required for {column_filter.operator.value} operator")
            
            # Validate regex pattern if using regex operator
            if column_filter.operator == FilterOperator.REGEX and column_filter.value:
                try:
                    re.compile(column_filter.value)
                except re.error as e:
                    errors.append(f"Invalid regex pattern: {str(e)}")
            
        except Exception as e:
            errors.append(f"Filter validation error: {str(e)}")
        
        return errors
