#!/usr/bin/env python3
"""
File Table Renderer Component (CONSOLIDATED)
Handles UI rendering of file data in tables with proper formatting and responsive design.
Inherits from BaseTableRenderer to eliminate code duplication.

CONSOLIDATION BENEFITS:
- Removes ~150 lines of duplicate code (file size formatting, selection management, table creation)
- Inherits standardized table functionality while preserving file-specific formatting
- Maintains backward compatibility with all existing file table operations
"""

import flet as ft
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from flet_server_gui.core.theme_compatibility import TOKENS

# Add project root to path for imports
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from flet_server_gui.utils.server_bridge import ServerBridge
    from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
    from .base_table_renderer import BaseTableRenderer
except ImportError:
    # Fallback to relative imports for direct execution
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
        from utils.server_bridge import ServerBridge
        from ui.widgets.buttons import ActionButtonFactory
        from base_table_renderer import BaseTableRenderer
    except ImportError:
        ServerBridge = object
        ActionButtonFactory = object
        BaseTableRenderer = object


class FileTableRenderer(BaseTableRenderer):
    """Handles rendering of file data in table format using consolidated base functionality"""
    
    def __init__(self, server_bridge: ServerBridge, button_factory: ActionButtonFactory, page: ft.Page):
        super().__init__(server_bridge, button_factory, page)
        # File-specific aliases for backward compatibility
        self.file_table = self.table
        self.selected_files = self.selected_items
    
    # Abstract method implementations for file-specific table structure
    
    def get_table_columns(self) -> List[ft.DataColumn]:
        """Get file table columns"""
        return [
            ft.DataColumn(ft.Checkbox(on_change=None)),  # Select all handled by parent
            ft.DataColumn(self.create_bold_header("Filename")),
            ft.DataColumn(self.create_bold_header("Type")),
            ft.DataColumn(self.create_bold_header("Size")),
            ft.DataColumn(self.create_bold_header("Date")),
            ft.DataColumn(self.create_bold_header("Client")),
            ft.DataColumn(self.create_bold_header("Actions")),
        ]
    
    def get_item_identifier(self, file_obj: Any) -> str:
        """Get file identifier"""
        return getattr(file_obj, 'filename', None) or (
            file_obj['filename'] if hasattr(file_obj, '__getitem__') and 'filename' in file_obj else (
                file_obj.get('name', 'Unknown') if hasattr(file_obj, 'get') else 'Unknown'
            )
        )
    
    def create_row_cells(self, file_obj: Any, on_file_select: Callable) -> List[ft.DataCell]:
        """Create file table row cells"""
        filename = self.get_item_identifier(file_obj)
        
        # Selection checkbox using base class method
        file_checkbox = self.create_selection_checkbox(filename, on_file_select)
        
        # File type icon and display
        file_type_display = self._get_file_type_display(filename)
        
        # Size formatting using base class method
        size_attr = getattr(file_obj, 'size', 0)
        file_size = size_attr or (
            file_obj['size'] if hasattr(file_obj, '__getitem__') and 'size' in file_obj else (
                file_obj.get('size', 0) if hasattr(file_obj, 'get') else 0
            )
        )
        size_display = self.format_file_size(file_size)
        
        # Date formatting using base class method
        date_received = getattr(file_obj, 'date_received', None) or (
            file_obj['date_received'] if hasattr(file_obj, '__getitem__') and 'date_received' in file_obj else (
                file_obj.get('date', '') if hasattr(file_obj, 'get') else ''
            )
        )
        date_display = self.format_date_relative(date_received)
        
        # Client display
        client_display = getattr(file_obj, 'client_id', None) or (
            file_obj['client_id'] if hasattr(file_obj, '__getitem__') and 'client_id' in file_obj else (
                file_obj.get('client', 'Unknown') if hasattr(file_obj, 'get') else 'Unknown'
            )
        )
        
        # Action buttons
        action_buttons = self._create_file_action_buttons(file_obj)
        
        return [
            ft.DataCell(file_checkbox),
            ft.DataCell(self.create_compact_text(filename)),
            ft.DataCell(file_type_display),
            ft.DataCell(self.create_compact_text(size_display, size=11)),
            ft.DataCell(self.create_compact_text(date_display, size=11)),
            ft.DataCell(self.create_compact_text(client_display, size=11)),
            ft.DataCell(action_buttons),
        ]
    
    def create_file_table(self) -> ft.DataTable:
        """Create file table using base class (backward compatibility)"""
        self.file_table = self.create_base_table()
        return self.file_table
    
    def populate_file_table(self, filtered_files: List[Any], on_file_select: callable, 
                           selected_files: List[str]) -> None:
        """Populate file table using base class (backward compatibility)"""
        self.populate_table(filtered_files, on_file_select, selected_files)
        # Update aliases for backward compatibility
        self.selected_files = self.selected_items
        self.file_table = self.table
    
    def _get_file_type_display(self, filename: str) -> ft.Control:
        """Get file type display with icon and label"""
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
    
    # File-specific formatting methods (unique to file table)
    
    
    def _create_file_action_buttons(self, file_obj) -> ft.Row:
        """Create action buttons for a file row"""
        # Get filename safely
        filename = getattr(file_obj, 'filename', None) or (file_obj['filename'] if hasattr(file_obj, '__getitem__') and 'filename' in file_obj else (file_obj.get('name', 'Unknown') if hasattr(file_obj, 'get') else 'Unknown'))
        
        # Create wrapper functions to properly capture filename
        def make_file_getter(filename):
            return lambda: [filename]
        
        return ft.Row([
            self.button_factory.create_action_button(
                'file_view_details', 
                make_file_getter(filename)
            ),
            self.button_factory.create_action_button(
                'file_preview', 
                make_file_getter(filename)
            ),
            self.button_factory.create_action_button(
                'file_download', 
                make_file_getter(filename)
            ),
            self.button_factory.create_action_button(
                'file_verify', 
                make_file_getter(filename)
            ),
            self.button_factory.create_action_button(
                'file_delete', 
                make_file_getter(filename)
            ),
        ], tight=True, spacing=5)
    
    # Backward compatibility aliases that delegate to base class
    
    def update_table_data(self, filtered_files: List[Any], on_file_select: callable = None, 
                         selected_files: List[str] = None) -> None:
        """Update table with new data using base class"""
        super().update_table_data(filtered_files, on_file_select, selected_files)
        # Update aliases for backward compatibility
        self.selected_files = self.selected_items
        self.file_table = self.table
    
    
    def select_all_rows(self) -> None:
        """Select all rows using base class"""
        super().select_all_rows()
        self.selected_files = self.selected_items
    
    def deselect_all_rows(self) -> None:
        """Deselect all rows using base class"""
        super().deselect_all_rows()
        self.selected_files = self.selected_items
    
    def get_table_container(self) -> ft.Container:
        """Get table container using base class (backward compatibility)"""
        container = super().get_table_container()
        self.file_table = self.table  # Ensure alias is updated
        return container
    
    def get_file_statistics(self, files: List[Any]) -> Dict[str, Any]:
        """Get statistics about the current file list"""
        if not files:
            return {
                'total_files': 0,
                'total_size': 0,
                'file_types': {},
                'avg_size': 0
            }
        
        total_size = sum(getattr(f, 'size', 0) for f in files)
        file_types = {}
        
        for file_obj in files:
            filename = getattr(file_obj, 'filename', None) or (file_obj['filename'] if hasattr(file_obj, '__getitem__') and 'filename' in file_obj else (file_obj.get('name', 'Unknown') if hasattr(file_obj, 'get') else 'Unknown'))
            extension = filename.split('.')[-1].lower() if '.' in filename else 'no_ext'
            file_types[extension] = file_types.get(extension, 0) + 1
        
        return {
            'total_files': len(files),
            'total_size': total_size,
            'total_size_formatted': self._format_file_size(total_size),
            'file_types': file_types,
            'avg_size': total_size // len(files) if files else 0,
            'avg_size_formatted': self._format_file_size(total_size // len(files)) if files else "0 B"
        }