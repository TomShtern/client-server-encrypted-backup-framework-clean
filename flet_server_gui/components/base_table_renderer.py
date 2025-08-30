#!/usr/bin/env python3
"""
Base Table Renderer Component (CONSOLIDATED)
Abstract base class for table rendering with common functionality extracted from:
- ClientTableRenderer (338 lines) - checkbox handlers, styling, selection management
- DatabaseTableRenderer (329 lines) - table creation patterns, formatting utilities
- FileTableRenderer (343 lines) - container creation, update methods, file size formatting

This consolidation eliminates ~250 lines of duplicated code across the three renderers.
"""

import flet as ft
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod
from flet_server_gui.ui.unified_theme_system import TOKENS

# Add project root to path for imports
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from flet_server_gui.utils.server_bridge import ServerBridge
    from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
except ImportError:
    # Fallback for direct execution
    ServerBridge = object
    ActionButtonFactory = object


class BaseTableRenderer(ABC):
    """
    Abstract base class for table rendering with common functionality.
    
    Consolidates common patterns from Client/Database/File table renderers:
    - Table creation with consistent styling
    - Checkbox selection management
    - Common formatting utilities (file size, dates)
    - Container creation and responsive design
    - Selection state management
    - Update and display methods
    """
    
    def __init__(self, server_bridge: ServerBridge, button_factory: ActionButtonFactory, page: ft.Page):
        """Initialize base table renderer with common dependencies"""
        self.server_bridge = server_bridge
        self.button_factory = button_factory
        self.page = page
        
        # Common table state - will be used by subclasses
        self.table = None
        self.selected_items = []
    
    @abstractmethod
    def get_table_columns(self) -> List[ft.DataColumn]:
        """Get table columns specific to this table type"""
        pass
    
    @abstractmethod
    def create_row_cells(self, item: Any, on_item_select: Callable) -> List[ft.DataCell]:
        """Create table row cells specific to this item type"""
        pass
    
    @abstractmethod
    def get_item_identifier(self, item: Any) -> str:
        """Get unique identifier for this item type"""
        pass
    
    def create_base_table(self) -> ft.DataTable:
        """
        Create table with standardized styling and configuration.
        Consolidates common table creation patterns from all renderers.
        """
        columns = self.get_table_columns()
        
        self.table = ft.DataTable(
            columns=columns,
            rows=[],
            # Consolidated styling from all table renderers
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            heading_row_color=TOKENS['surface_variant'],
            heading_row_height=44,  # Optimized for touch targets
            data_row_max_height=None,  # Allow flexible row height
            data_row_min_height=40,   # Minimum touch target height
            show_checkbox_column=False,  # We handle checkboxes manually
            horizontal_lines=ft.border.BorderSide(0.5, TOKENS['outline']),
            column_spacing=4,  # Adjustable by subclasses
            clip_behavior=ft.ClipBehavior.NONE,  # Prevent content clipping
        )
        return self.table
    
    def create_checkbox_handler(self, item_id: str, on_item_select: Callable = None) -> Callable:
        """
        Create checkbox handler with standardized selection logic.
        Consolidates identical checkbox handler patterns from all renderers.
        """
        def handler(e):
            # Update local selection state immediately
            if e.control.value:  # Checkbox is now checked
                if item_id not in self.selected_items:
                    self.selected_items.append(item_id)
            else:  # Checkbox is now unchecked
                if item_id in self.selected_items:
                    self.selected_items.remove(item_id)
            
            # Call the parent's selection handler if provided
            if on_item_select:
                e.data = item_id
                on_item_select(e)
        return handler
    
    def create_selection_checkbox(self, item_id: str, on_item_select: Callable = None) -> ft.Checkbox:
        """
        Create selection checkbox with standardized behavior.
        Consolidates checkbox creation pattern from all renderers.
        """
        return ft.Checkbox(
            value=item_id in self.selected_items,
            on_change=self.create_checkbox_handler(item_id, on_item_select),
            data=item_id
        )
    
    def populate_table(self, items: List[Any], on_item_select: Callable = None, 
                      selected_items: List[str] = None) -> None:
        """
        Populate table with items using standardized logic.
        Consolidates table population patterns from all renderers.
        """
        if not self.table:
            return
        
        self.table.rows.clear()
        self.selected_items = selected_items or []
        
        for item in items:
            # Get item identifier
            item_id = self.get_item_identifier(item)
            
            # Create row cells (delegated to subclass)
            row_cells = self.create_row_cells(item, on_item_select)
            
            # Create table row
            self.table.rows.append(ft.DataRow(cells=row_cells))
    
    def get_table_container(self) -> ft.Container:
        """
        Get table wrapped in responsive container with standardized styling.
        Consolidates container creation patterns from all renderers.
        """
        if not self.table:
            self.create_base_table()
        
        # Create responsive scrollable container
        table_column = ft.Column(
            controls=[self.table],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0,
            tight=True  # Reduce extra spacing
        )
        
        # Wrap in responsive container with standardized styling
        return ft.Container(
            content=table_column,
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            padding=6,  # Optimized padding
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            width=None,  # Auto width
            height=None  # Auto height
        )
    
    def update_table_data(self, items: List[Any], on_item_select: Callable = None, 
                         selected_items: List[str] = None) -> None:
        """
        Update table with new data using standardized logic.
        Consolidates update patterns from all renderers.
        """
        if selected_items is None:
            selected_items = self.selected_items
            
        self.populate_table(items, on_item_select, selected_items)
        self.update_table_display()
    
    def update_table_display(self) -> None:
        """
        Update table display using standardized logic.
        Consolidates display update patterns from all renderers.
        """
        if self.page and self.table:
            self.page.update()
    
    def select_all_rows(self) -> None:
        """
        Select all rows using standardized logic.
        Consolidates selection management from all renderers.
        """
        if not self.table:
            return
            
        # Update all checkboxes in the table and sync selection state
        for row in self.table.rows:
            if row.cells and len(row.cells) > 0:
                checkbox = row.cells[0].content
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.value = True
                    item_id = checkbox.data
                    if item_id and item_id not in self.selected_items:
                        self.selected_items.append(item_id)
                    
        if self.page:
            self.page.update()
    
    def deselect_all_rows(self) -> None:
        """
        Deselect all rows using standardized logic.
        Consolidates deselection management from all renderers.
        """
        if not self.table:
            return
            
        # Update all checkboxes in the table and sync selection state
        for row in self.table.rows:
            if row.cells and len(row.cells) > 0:
                checkbox = row.cells[0].content
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.value = False
                    item_id = checkbox.data
                    if item_id and item_id in self.selected_items:
                        self.selected_items.remove(item_id)
                    
        if self.page:
            self.page.update()
    
    def clear_selection(self) -> None:
        """Clear selection state and update UI"""
        self.selected_items.clear()
        self.deselect_all_rows()
    
    def get_selected_count(self) -> int:
        """Get count of currently selected items"""
        return len(self.selected_items)
    
    # Common formatting utilities (consolidated from all renderers)
    
    def format_file_size(self, size: int) -> str:
        """
        Format file size to human-readable format.
        Consolidates identical formatting logic from all renderers.
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
        Consolidates date formatting logic from renderers.
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
        Consolidates cell formatting logic from database renderer.
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
        """Create standardized text component for table cells"""
        return ft.Text(
            text,
            size=size,
            max_lines=max_lines,
            overflow=ft.TextOverflow.ELLIPSIS
        )
    
    def create_bold_header(self, text: str) -> ft.Text:
        """Create standardized header text for table columns"""
        return ft.Text(
            text,
            weight=ft.FontWeight.BOLD,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS
        )