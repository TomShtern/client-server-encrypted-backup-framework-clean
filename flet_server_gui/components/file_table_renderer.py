#!/usr/bin/env python3
"""
File Table Renderer Component
Handles UI rendering of file data in tables with proper formatting and responsive design.
"""

import flet as ft
import sys
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from flet_server_gui.ui.unified_theme_system import TOKENS

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


class FileTableRenderer:
    """Handles rendering of file data in table format"""
    
    def __init__(self, server_bridge: ServerBridge, button_factory: ActionButtonFactory, page: ft.Page):
        self.server_bridge = server_bridge
        self.button_factory = button_factory
        self.page = page
        
        # Table components
        self.file_table = None
        self.selected_files = []
    
    def create_file_table(self) -> ft.DataTable:
        """Create the file data table with headers"""
        self.file_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Checkbox(on_change=None)),  # Select all handled by parent
                ft.DataColumn(ft.Text("Filename", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataColumn(ft.Text("Client", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
            ],
            rows=[],
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            heading_row_color=TOKENS['surface_variant'],
            heading_row_height=50,
            data_row_max_height=60,
            show_checkbox_column=False,  # We handle checkboxes manually
        )
        return self.file_table
    
    def populate_file_table(self, filtered_files: List[Any], on_file_select: callable, 
                           selected_files: List[str]) -> None:
        """Populate the file table with filtered file data"""
        if not self.file_table:
            return
        
        self.file_table.rows.clear()
        self.selected_files = selected_files or []
        
        for file_obj in filtered_files:
            # File selection checkbox
            filename = getattr(file_obj, 'filename', None) or (file_obj['filename'] if hasattr(file_obj, '__getitem__') and 'filename' in file_obj else (file_obj.get('name', 'Unknown') if hasattr(file_obj, 'get') else 'Unknown'))
            
            # Create a wrapper function to capture the filename
            def create_checkbox_handler(filename):
                def handler(e):
                    # Call the parent's selection handler if provided
                    if on_file_select:
                        # Create a mock event with the filename as data
                        class MockEvent:
                            def __init__(self, filename, checked):
                                self.data = filename
                                self.control = type('Control', (), {'value': checked})()
                        # Determine new state (opposite of current)
                        new_state = not (filename in self.selected_files)
                        mock_event = MockEvent(filename, new_state)
                        on_file_select(mock_event)
                return handler
            
            file_checkbox = ft.Checkbox(
                value=filename in self.selected_files,
                on_change=create_checkbox_handler(filename),
                data=filename
            )
            
            # File type icon and display
            filename = getattr(file_obj, 'filename', None) or (file_obj['filename'] if hasattr(file_obj, '__getitem__') and 'filename' in file_obj else (file_obj.get('name', 'Unknown') if hasattr(file_obj, 'get') else 'Unknown'))
            file_type_display = self._get_file_type_display(filename)
            
            # Size formatting
            size_attr = getattr(file_obj, 'size', 0)
            size_display = self._format_file_size(size_attr or (file_obj['size'] if hasattr(file_obj, '__getitem__') and 'size' in file_obj else (file_obj.get('size', 0) if hasattr(file_obj, 'get') else 0)))
            
            # Date formatting
            date_received = getattr(file_obj, 'date_received', None) or (file_obj['date_received'] if hasattr(file_obj, '__getitem__') and 'date_received' in file_obj else (file_obj.get('date', '') if hasattr(file_obj, 'get') else ''))
            date_display = self._format_date(date_received)
            
            # Client display
            client_display = getattr(file_obj, 'client_id', None) or (file_obj['client_id'] if hasattr(file_obj, '__getitem__') and 'client_id' in file_obj else (file_obj.get('client', 'Unknown') if hasattr(file_obj, 'get') else 'Unknown'))
            
            # Action buttons
            action_buttons = self._create_file_action_buttons(file_obj)
            
            # Create table row
            self.file_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(file_checkbox),
                        ft.DataCell(ft.Text(filename, size=12, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(file_type_display),
                        ft.DataCell(ft.Text(size_display, size=11, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(date_display, size=11, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(ft.Text(client_display, size=11, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)),
                        ft.DataCell(action_buttons),
                    ]
                )
            )
    
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
    
    def _format_file_size(self, size: int) -> str:
        """Format file size to human-readable format"""
        if not size or size == 0:
            return "0 B"
        
        # Convert bytes to appropriate unit
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def _format_date(self, date_str: str) -> str:
        """Format date to human-readable format"""
        try:
            if not date_str or date_str == "Unknown":
                return "Unknown"
            
            # Parse the datetime string
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            now = datetime.now()
            
            # Calculate time difference
            diff = now - date_obj.replace(tzinfo=None)
            
            if diff.days > 7:
                return date_obj.strftime("%Y-%m-%d")
            elif diff.days > 0:
                return f"{diff.days}d ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours}h ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes}m ago"
            else:
                return "Just now"
                
        except (ValueError, AttributeError):
            return "Unknown"
    
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
    
    def get_table_container(self) -> ft.Container:
        """Get the file table wrapped in a responsive container"""
        if not self.file_table:
            self.create_file_table()
        
        # Create a scrollable container for the table with proper responsive properties
        table_scroll_container = ft.Container(
            content=ft.Column([
                self.file_table
            ], scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE
        )
        
        # Wrap in a responsive container with proper sizing
        return ft.Container(
            content=table_scroll_container,
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            padding=10,
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            width=float("inf")  # Allow infinite width for proper scaling
        )
    
    def update_table_data(self, filtered_files: List[Any], on_file_select: callable = None, 
                         selected_files: List[str] = None) -> None:
        """Update table with new data"""
        if selected_files is None:
            selected_files = self.selected_files
            
        self.populate_file_table(filtered_files, on_file_select, selected_files)
        self.update_table_display()
    
    def update_table_display(self) -> None:
        """Update table display after changes"""
        if self.page:
            self.page.update()
    
    def select_all_rows(self) -> None:
        """Select all rows in the table"""
        if not self.file_table:
            return
            
        # Update all checkboxes in the table
        for row in self.file_table.rows:
            if row.cells and len(row.cells) > 0:
                checkbox = row.cells[0].content
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.value = True
                    
        if self.page:
            self.page.update()
    
    def deselect_all_rows(self) -> None:
        """Deselect all rows in the table"""
        if not self.file_table:
            return
            
        # Update all checkboxes in the table
        for row in self.file_table.rows:
            if row.cells and len(row.cells) > 0:
                checkbox = row.cells[0].content
                if isinstance(checkbox, ft.Checkbox):
                    checkbox.value = False
                    
        if self.page:
            self.page.update()
    
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