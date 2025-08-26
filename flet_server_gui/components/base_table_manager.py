#!/usr/bin/env python3
"""
Base Table Manager
Shared functionality for table rendering components.
"""

import flet as ft
import asyncio
import sys
import os
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod

# Add project root to path for imports
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from flet_server_gui.utils.server_bridge import ServerBridge
    from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
except ImportError:
    # Fallback to relative imports for direct execution
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
        from utils.server_bridge import ServerBridge
        from ui.widgets.buttons import ActionButtonFactory
    except ImportError:
        ServerBridge = object
        ActionButtonFactory = object


class BaseTableManager(ABC):
    """Base class for table management with common functionality"""
    
    def __init__(self, server_bridge, button_factory, page: ft.Page):
        self.server_bridge = server_bridge
        self.button_factory = button_factory
        self.page = page
        
        # Table components
        self.data_table = None
        self.selected_items = []
        
        # Phase 2 enhancements - TODO: Complete implementation
        self.sort_column = None
        self.sort_ascending = True
        self.current_page = 1
        self.items_per_page = 50
        self.total_items = 0
        
        # Performance optimization
        self.virtual_scrolling = False
        self.lazy_loading = False
        
        # TODO: Initialize Phase 2 managers (complete in Phase 2)
        self.error_handler = None  # Will be set by initialize_phase2_components()
        self.toast_manager = None  # Will be set by initialize_phase2_components()
    
    @abstractmethod
    def get_table_columns(self) -> List[ft.DataColumn]:
        """Get the columns for the data table"""
        pass
    
    @abstractmethod
    def create_table_row(self, item: Any, on_item_select: Callable) -> ft.DataRow:
        """Create a table row for the given item"""
        pass
    
    def create_data_table(self) -> ft.DataTable:
        """Create the data table with standard styling"""
        self.data_table = ft.DataTable(
            columns=self.get_table_columns(),
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            heading_row_color=ft.Colors.SURFACE_TINT,
            heading_row_height=50,
            data_row_max_height=60,
            show_checkbox_column=False,  # We handle checkboxes manually
        )
        return self.data_table
    
    def populate_table(self, filtered_items: List[Any], on_item_select: Callable, 
                      selected_items: List[str]) -> None:
        """Populate the table with filtered data"""
        if not self.data_table:
            return
        
        self.data_table.rows.clear()
        self.selected_items = selected_items
        
        for item in filtered_items:
            row = self.create_table_row(item, on_item_select)
            self.data_table.rows.append(row)
    
    def get_table_container(self) -> ft.Container:
        """Get the table wrapped in a responsive container"""
        if not self.data_table:
            self.create_data_table()
        
        return ft.Container(
            content=ft.Column([
                self.data_table
            ], scroll=ft.ScrollMode.AUTO),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
            expand=True
        )
    
    def update_table_display(self) -> None:
        """Update table display after changes"""
        if self.page:
            self.page.update()
    
    def create_selection_checkbox(self, item_id: str, selected_items: List[str], 
                                 on_select: Callable) -> ft.Checkbox:
        """Create a selection checkbox for table rows"""
        return ft.Checkbox(
            value=item_id in selected_items,
            on_change=on_select,
            data=item_id
        )
    
    def select_all_rows(self):
        """Select all rows in table"""
        if not self.data_table or not self.data_table.rows:
            return
        
        # Extract all item IDs from table rows
        all_item_ids = []
        for row in self.data_table.rows:
            # Look for checkbox in first cell to get item ID
            if row.cells and len(row.cells) > 0:
                first_cell = row.cells[0]
                if hasattr(first_cell, 'content') and hasattr(first_cell.content, 'data'):
                    item_id = first_cell.content.data
                    if item_id:
                        all_item_ids.append(item_id)
        
        # Update selected_items list
        self.selected_items = all_item_ids[:]
        
        # Update all checkboxes to checked state
        for row in self.data_table.rows:
            if row.cells and len(row.cells) > 0:
                first_cell = row.cells[0]
                if hasattr(first_cell, 'content') and isinstance(first_cell.content, ft.Checkbox):
                    first_cell.content.value = True
        
        # Update the display
        self.update_table_display()
    
    def clear_selection(self):
        """Clear all row selections"""
        if not self.data_table or not self.data_table.rows:
            return
        
        # Clear the selected_items list
        self.selected_items.clear()
        
        # Update all checkboxes to unchecked state
        for row in self.data_table.rows:
            if row.cells and len(row.cells) > 0:
                first_cell = row.cells[0]
                if hasattr(first_cell, 'content') and isinstance(first_cell.content, ft.Checkbox):
                    first_cell.content.value = False
        
        # Update the display
        self.update_table_display()
    
    def get_selected_data(self) -> List[Dict[str, Any]]:
        """Get data for all selected rows"""
        selected_data = []
        
        if not self.data_table or not self.data_table.rows or not self.selected_items:
            return selected_data
        
        # Iterate through table rows to find selected ones
        for row in self.data_table.rows:
            if not row.cells or len(row.cells) == 0:
                continue
                
            # Get item ID from first cell (checkbox)
            first_cell = row.cells[0]
            item_id = None
            if hasattr(first_cell, 'content') and hasattr(first_cell.content, 'data'):
                item_id = first_cell.content.data
            
            # If this row is selected, extract its data
            if item_id and item_id in self.selected_items:
                row_data = {'id': item_id}
                
                # Extract data from each cell
                for i, cell in enumerate(row.cells):
                    if hasattr(cell, 'content'):
                        if isinstance(cell.content, ft.Text):
                            row_data[f'column_{i}'] = cell.content.value
                        elif isinstance(cell.content, ft.Checkbox):
                            # Skip checkbox column, already have ID
                            pass
                        elif hasattr(cell.content, 'value'):
                            row_data[f'column_{i}'] = cell.content.value
                        else:
                            row_data[f'column_{i}'] = str(cell.content)
                
                selected_data.append(row_data)
        
        return selected_data
    
    # ============================================================================
    # PHASE 2 ENHANCEMENTS - Advanced Table Features
    # ============================================================================
    
    def initialize_phase2_components(self, error_handler=None, toast_manager=None):
        """
        Initialize Phase 2 infrastructure components
        
        Args:
            error_handler: ErrorHandler instance for centralized error handling
            toast_manager: ToastManager instance for user notifications
        """
        self.error_handler = error_handler
        self.toast_manager = toast_manager
        
        # Initialize advanced table features
        self._setup_virtual_scrolling()
        self._setup_lazy_loading()
        self._setup_keyboard_navigation()
    
    @abstractmethod
    def get_sortable_columns(self) -> List[str]:
        """
        Get list of column names that support sorting
        
        Returns:
            List of column identifiers that can be sorted
        """
        pass
    
    @abstractmethod 
    def sort_data(self, data: List[Any], column: str, ascending: bool = True) -> List[Any]:
        """
        Sort data by specified column
        
        Args:
            data: List of data items to sort
            column: Column identifier to sort by
            ascending: True for ascending, False for descending
            
        Returns:
            Sorted list of data items
        """
        pass
    
    def enable_sorting(self, column: str, ascending: bool = True) -> None:
        """
        Enable sorting on the specified column
        
        Args:
            column: Column to sort by
            ascending: Sort direction
        """
        try:
            if column not in self.get_sortable_columns():
                if self.toast_manager:
                    self.toast_manager.show_warning(f"Column '{column}' is not sortable")
                return
            
            self.sort_column = column
            self.sort_ascending = ascending
            
            # Apply sorting and update display
            # This would typically be called by the parent component to refresh data
            if self.toast_manager:
                direction = "ascending" if ascending else "descending"
                self.toast_manager.show_info(f"Sorted by {column} ({direction})")
                
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(e, "UI", "MEDIUM")
    
    def setup_pagination(self, items_per_page: int = 50) -> None:
        """
        Setup pagination for large datasets
        
        Args:
            items_per_page: Number of items to show per page
        """
        self.items_per_page = items_per_page
        # Initialize pagination UI components would be handled by parent view
    
    def get_current_page_data(self, all_data: List[Any]) -> List[Any]:
        """
        Get data for the current page
        
        Args:
            all_data: Complete dataset
            
        Returns:
            Data items for current page
        """
        if not all_data:
            return []
            
        self.total_items = len(all_data)
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page
        
        return all_data[start_index:end_index]
    
    def goto_page(self, page_number: int) -> bool:
        """
        Navigate to specific page
        
        Args:
            page_number: Target page number (1-based)
            
        Returns:
            bool: True if navigation successful, False otherwise
        """
        max_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        
        if page_number < 1 or page_number > max_pages:
            if self.toast_manager:
                self.toast_manager.show_warning(f"Invalid page number: {page_number}")
            return False
        
        self.current_page = page_number
        # Refresh table display with new page would be handled by parent view
        return True
    
    def export_data(self, format_type: str = "csv", selected_only: bool = False) -> Optional[str]:
        """
        Export table data to various formats
        
        Args:
            format_type: Export format (csv, json, excel)
            selected_only: Export only selected rows if True
            
        Returns:
            str: File path of exported data, None if failed
        """
        try:
            data_to_export = self.get_selected_data() if selected_only else []
            
            # Implement format-specific export logic
            if format_type == "csv":
                return self._export_to_csv(data_to_export)
            elif format_type == "json":
                return self._export_to_json(data_to_export)
            elif format_type == "excel":
                return self._export_to_excel(data_to_export)
            else:
                if self.toast_manager:
                    self.toast_manager.show_error(f"Unsupported export format: {format_type}")
                return None
                
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(e, "DATA", "MEDIUM")
            return None
    
    def _export_to_csv(self, data: List[Dict[str, Any]]) -> Optional[str]:
        """Export data to CSV format"""
        try:
            import csv
            from datetime import datetime
            import os
            
            if not data:
                if self.toast_manager:
                    self.toast_manager.show_warning("No data to export")
                return None
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"table_export_{timestamp}.csv"
            
            # Write to file
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if data:
                    # Get fieldnames from first row
                    fieldnames = list(data[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            
            if self.toast_manager:
                self.toast_manager.show_success(f"Data exported to {filename}")
            
            return filename
            
        except Exception as e:
            if self.toast_manager:
                self.toast_manager.show_error(f"CSV export failed: {str(e)}")
            return None
    
    def _export_to_json(self, data: List[Dict[str, Any]]) -> Optional[str]:
        """Export data to JSON format"""
        try:
            import json
            from datetime import datetime
            import os
            
            if not data:
                if self.toast_manager:
                    self.toast_manager.show_warning("No data to export")
                return None
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"table_export_{timestamp}.json"
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)
            
            if self.toast_manager:
                self.toast_manager.show_success(f"Data exported to {filename}")
            
            return filename
            
        except Exception as e:
            if self.toast_manager:
                self.toast_manager.show_error(f"JSON export failed: {str(e)}")
            return None
    
    def _export_to_excel(self, data: List[Dict[str, Any]]) -> Optional[str]:
        """Export data to Excel format"""
        try:
            from datetime import datetime
            import os
            
            if not data:
                if self.toast_manager:
                    self.toast_manager.show_warning("No data to export")
                return None
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"table_export_{timestamp}.xlsx"
            
            # Show message that Excel export requires additional dependencies
            if self.toast_manager:
                self.toast_manager.show_info("Excel export requires pandas and openpyxl libraries")
            
            return filename
            
        except Exception as e:
            if self.toast_manager:
                self.toast_manager.show_error(f"Excel export failed: {str(e)}")
            return None
    
    def get_table_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive table statistics
        
        Returns:
            Dict containing table performance and usage statistics
        """
        return {
            "total_rows": len(self.data_table.rows) if self.data_table else 0,
            "selected_rows": len(self.selected_items),
            "current_page": self.current_page,
            "items_per_page": self.items_per_page,
            "total_items": self.total_items,
            "sort_column": self.sort_column,
            "sort_ascending": self.sort_ascending,
            "virtual_scrolling": self.virtual_scrolling,
            "lazy_loading": self.lazy_loading
        }
    
    def refresh_table(self, new_data: List[Any] = None) -> None:
        """
        Refresh table with new data or current data
        
        Args:
            new_data: Optional new data to display, uses current if None
        """
        try:
            # Clear current table state
            if self.data_table:
                self.data_table.rows.clear()
            
            if new_data is not None:
                # Update data source and refresh would be handled by parent component
                pass
            
            # Apply current sorting
            if self.sort_column:
                # Apply sorting to data would be handled by parent component
                pass
            
            # Apply pagination would be handled by parent component
            # current_page_data = self.get_current_page_data(sorted_data)
            
            # Update table display
            self.update_table_display()
            
        except Exception as e:
            if self.error_handler:
                self.error_handler.handle_error(e, "UI", "MEDIUM")
    
    def enable_virtual_scrolling(self, enabled: bool = True) -> None:
        """
        Enable/disable virtual scrolling for large datasets
        """
        self.virtual_scrolling = enabled
    
    def enable_lazy_loading(self, enabled: bool = True) -> None:
        """
        Enable/disable lazy loading of table data
        """
        self.lazy_loading = enabled
    
    def setup_keyboard_navigation(self) -> None:
        """
        Setup keyboard navigation for accessibility
        """
        # Keyboard navigation would be implemented in concrete table managers
        pass
    
    def get_accessibility_info(self) -> Dict[str, Any]:
        """
        Get accessibility information for screen readers
        
        Returns:
            Dict with accessibility metadata
        """
        return {
            "total_rows": len(self.data_table.rows) if self.data_table else 0,
            "selected_count": len(self.selected_items),
            "sort_info": f"Sorted by {self.sort_column}" if self.sort_column else "No sorting",
            "navigation_help": "Use arrow keys to navigate, Space to select, Enter for actions"
        }
    
    # Helper methods for advanced table features
    def _setup_virtual_scrolling(self):
        """Setup virtual scrolling container"""
        # Virtual scrolling implementation would be handled in concrete managers
        pass
    
    def _setup_lazy_loading(self):
        """Setup lazy loading trigger points"""
        # Lazy loading implementation would be handled in concrete managers
        pass
    
    def _setup_keyboard_navigation(self):
        """Setup keyboard navigation between interactive elements"""
        # Keyboard navigation implementation would be handled in concrete managers
        pass


class BaseFilterManager(ABC):
    """Base class for filter management with common functionality"""
    
    def __init__(self, page: ft.Page, toast_manager=None):
        self.page = page
        self.toast_manager = toast_manager
        
        # Data storage
        self.all_items = []
        self.filtered_items = []
        
        # Search debouncing
        self._search_timer: Optional[asyncio.Task] = None
        
        # UI Components
        self.search_field = None
        
        # Callbacks
        self.on_filter_changed: Optional[Callable] = None
    
    @abstractmethod
    def _apply_custom_filters(self, items: List[Any]) -> List[Any]:
        """Apply custom filters specific to the data type"""
        pass
    
    def create_search_field(self, label: str, on_filter_change_callback: Callable) -> ft.TextField:
        """Create search field with debouncing"""
        self.on_filter_changed = on_filter_change_callback
        
        self.search_field = ft.TextField(
            label=label,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            expand=True,
        )
        return self.search_field
    
    def set_data(self, items: List[Any]) -> None:
        """Set the data to filter"""
        self.all_items = items
        self._apply_filters()
    
    def get_filtered_data(self) -> List[Any]:
        """Get the current filtered list"""
        return self.filtered_items
    
    def _apply_filters(self) -> None:
        """Apply current search and custom filters"""
        # Start with all items
        filtered = self.all_items[:]
        
        # Apply search filter
        search_term = self.search_field.value.lower() if self.search_field and self.search_field.value else ""
        if search_term:
            filtered = self._apply_search_filter(filtered, search_term)
        
        # Apply custom filters
        filtered = self._apply_custom_filters(filtered)
        
        self.filtered_items = filtered
        
        # Notify parent of filter change
        if self.on_filter_changed:
            self.on_filter_changed(self.filtered_items)
    
    @abstractmethod
    def _apply_search_filter(self, items: List[Any], search_term: str) -> List[Any]:
        """Apply search filtering specific to the data type"""
        pass
    
    def _on_search_change(self, e):
        """Handle search field changes with debouncing"""
        # Cancel existing timer if running
        if self._search_timer and not self._search_timer.done():
            self._search_timer.cancel()
        
        # Start new debounced search timer
        self._search_timer = asyncio.create_task(self._debounced_search(e.control.value))
    
    async def _debounced_search(self, query: str):
        """Execute search after debounce delay"""
        try:
            # Wait for debounce delay (300ms)
            await asyncio.sleep(0.3)
            
            # Apply filters on main thread
            if self.page:
                self.page.run_thread(self._apply_filters)
        except asyncio.CancelledError:
            # Timer was cancelled, ignore
            pass
        except Exception as e:
            print(f"Error in debounced search: {e}")
    
    def reset_filters(self) -> None:
        """Reset all filters to default state"""
        if self.search_field:
            self.search_field.value = ""
        self._apply_filters()
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """Get statistics about current filtering"""
        return {
            'total_items': len(self.all_items),
            'filtered_items': len(self.filtered_items),
            'search_active': bool(self.search_field and self.search_field.value)
        }


class BaseActionHandler(ABC):
    """Base class for action handlers with common functionality"""
    
    def __init__(self, server_bridge, dialog_system, toast_manager, page: ft.Page):
        self.server_bridge = server_bridge
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.page = page
        
        # Callbacks for parent component
        self.on_data_changed: Optional[Callable] = None
    
    def set_data_changed_callback(self, callback: Callable):
        """Set callback for when data changes and refresh is needed"""
        self.on_data_changed = callback
    
    @abstractmethod
    async def perform_bulk_action(self, action: str, item_ids: List[str]) -> None:
        """Perform bulk action on multiple items"""
        pass
    
    def _close_dialog(self):
        """Close the current dialog"""
        if self.dialog_system and hasattr(self.dialog_system, 'current_dialog'):
            if self.dialog_system.current_dialog:
                self.dialog_system.current_dialog.open = False
                self.page.update()
    
    def _create_progress_dialog(self, title: str, message: str) -> ft.Control:
        """Create a progress dialog content"""
        return ft.Column([
            ft.Text(message),
            ft.ProgressBar(),
            ft.Text("Please wait...")
        ], spacing=10)
    
    def _show_confirmation_dialog(self, title: str, message: str, 
                                 on_confirm: Callable, on_cancel: Callable = None):
        """Show confirmation dialog with standard styling"""
        self.dialog_system.show_confirmation_dialog(
            title=title,
            message=message,
            on_confirm=on_confirm,
            on_cancel=on_cancel or (lambda: self._close_dialog())
        )
    
    async def _show_progress_dialog(self, title: str, message: str) -> None:
        """Show progress dialog during long operations"""
        if self.dialog_system:
            progress_content = self._create_progress_dialog(title, message)
            self.dialog_system.show_custom_dialog(title, progress_content)
    
    def _update_progress(self, progress: float, message: str = "") -> None:
        """Update progress during long operations"""
        # This would update an existing progress dialog
        pass
    
    async def _handle_action_with_progress(self, action_name: str, action_func: Callable, 
                                         item_ids: List[str]) -> None:
        """Handle action with progress tracking and error handling"""
        try:
            # Show progress dialog
            await self._show_progress_dialog("Processing", f"{action_name} in progress...")
            
            # Perform the action
            await action_func(item_ids)
            
            # Close progress dialog
            self._close_dialog()
            
            # Show success message
            if self.toast_manager:
                self.toast_manager.show_success(f"{action_name} completed successfully")
            
            # Notify parent of data change
            if self.on_data_changed:
                self.on_data_changed()
                
        except Exception as e:
            # Close progress dialog
            self._close_dialog()
            
            # Show error message
            if self.toast_manager:
                self.toast_manager.show_error(f"{action_name} failed: {str(e)}")
            
            # Handle error
            if self.error_handler:
                self.error_handler.handle_error(e, "ACTION", "MEDIUM")
    
    async def _execute_with_progress(self, operation: Callable, progress_callback: Callable = None) -> Any:
        """Execute operation with progress tracking"""
        try:
            # Show progress dialog
            progress_dialog = self._create_progress_dialog("Processing", "Please wait...")
            # In a real implementation, this would show the dialog
            
            # Execute operation
            if asyncio.iscoroutinefunction(operation):
                result = await operation()
            else:
                result = operation()
            
            # Close progress dialog
            self._close_dialog()
            
            return result
            
        except Exception as e:
            self._close_dialog()
            if self.toast_manager:
                self.toast_manager.show_error(f"Operation failed: {str(e)}")
            raise
    
    def _show_success_message(self, message: str):
        """Show success message to user"""
        if self.toast_manager:
            self.toast_manager.show_success(message)
    
    def _show_error_message(self, message: str):
        """Show error message to user"""
        if self.toast_manager:
            self.toast_manager.show_error(message)
    
    def _trigger_data_refresh(self):
        """Trigger data refresh callback if set"""
        if self.on_data_changed:
            self.on_data_changed()
    
    async def _show_progress_dialog(self, title: str, message: str) -> None:
        """Show progress dialog during long operations"""
        try:
            progress_content = self._create_progress_dialog(title, message)
            
            self.dialog_system.show_custom_dialog(
                title=title,
                content=progress_content,
                actions=[]
            )
            
            self.page.update()
            
        except Exception as e:
            if self.toast_manager:
                self.toast_manager.show_error(f"Failed to show progress dialog: {str(e)}")
    
    def _update_progress_dialog(self, message: str) -> None:
        """Update progress dialog with new message"""
        try:
            # This would update the existing dialog content
            # Implementation depends on how dialogs are managed
            pass
        except Exception as e:
            if self.toast_manager:
                self.toast_manager.show_error(f"Failed to update progress dialog: {str(e)}")
    
    def _close_progress_dialog(self) -> None:
        """Close the progress dialog"""
        try:
            self._close_dialog()
        except Exception as e:
            if self.toast_manager:
                self.toast_manager.show_error(f"Failed to close progress dialog: {str(e)}")
    
    async def _execute_with_progress(self, operation: Callable, 
                                   progress_title: str, progress_message: str) -> Any:
        """Execute operation with progress dialog"""
        try:
            await self._show_progress_dialog(progress_title, progress_message)
            
            # Execute the operation
            result = await operation() if asyncio.iscoroutinefunction(operation) else operation()
            
            # Close progress dialog
            self._close_progress_dialog()
            
            return result
            
        except Exception as e:
            # Close progress dialog on error
            self._close_progress_dialog()
            
            # Show error to user
            if self.toast_manager:
                self.toast_manager.show_error(f"Operation failed: {str(e)}")
            
            # Re-raise for caller to handle
            raise
    
    def _show_success_message(self, message: str) -> None:
        """Show success message to user"""
        if self.toast_manager:
            self.toast_manager.show_success(message)
    
    def _show_error_message(self, message: str) -> None:
        """Show error message to user"""
        if self.toast_manager:
            self.toast_manager.show_error(message)
    
    def _show_warning_message(self, message: str) -> None:
        """Show warning message to user"""
        if self.toast_manager:
            self.toast_manager.show_warning(message)
    
    def _show_info_message(self, message: str) -> None:
        """Show info message to user"""
        if self.toast_manager:
            self.toast_manager.show_info(message)
    
    def _trigger_data_refresh(self) -> None:
        """Trigger data refresh callback if set"""
        if self.on_data_changed:
            try:
                self.on_data_changed()
            except Exception as e:
                if self.toast_manager:
                    self.toast_manager.show_error(f"Data refresh failed: {str(e)}")
    
    async def _handle_async_operation(self, operation: Callable, 
                                     success_message: str = "Operation completed successfully",
                                     error_message: str = "Operation failed") -> bool:
        """Handle async operation with proper error handling"""
        try:
            result = await operation() if asyncio.iscoroutinefunction(operation) else operation()
            
            if result:
                self._show_success_message(success_message)
                self._trigger_data_refresh()
                return True
            else:
                self._show_error_message(error_message)
                return False
                
        except Exception as e:
            self._show_error_message(f"{error_message}: {str(e)}")
            return False
    
    def _validate_item_ids(self, item_ids: List[str]) -> bool:
        """Validate item IDs before performing actions"""
        if not item_ids:
            self._show_warning_message("No items selected for action")
            return False
        
        if not all(isinstance(item_id, str) and item_id.strip() for item_id in item_ids):
            self._show_error_message("Invalid item IDs provided")
            return False
        
        return True
    
    async def _confirm_bulk_action(self, action: str, item_count: int, 
                                  on_confirm: Callable) -> None:
        """Show confirmation dialog for bulk actions"""
        confirmation_messages = {
            "delete": f"Are you sure you want to delete {item_count} items? This cannot be undone.",
            "disconnect": f"Are you sure you want to disconnect {item_count} clients?",
            "backup": f"Are you sure you want to backup {item_count} files?",
            "restore": f"Are you sure you want to restore {item_count} files?",
            "export": f"Are you sure you want to export {item_count} items?",
            "import": f"Are you sure you want to import {item_count} items?",
        }
        
        message = confirmation_messages.get(action, f"Are you sure you want to perform {action} on {item_count} items?")
        
        def confirm_wrapper():
            self._close_dialog()
            asyncio.create_task(on_confirm())
        
        self._show_confirmation_dialog(
            title=f"Confirm {action.title()}",
            message=message,
            on_confirm=confirm_wrapper
        )