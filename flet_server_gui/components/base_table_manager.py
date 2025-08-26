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
            border=ft.Border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            heading_row_color=ft.Colors.SURFACE_VARIANT,
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
                self.page.run_in_thread(self._apply_filters)
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