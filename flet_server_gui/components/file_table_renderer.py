#!/usr/bin/env python3
"""
File Table Renderer Component
Handles UI rendering of file data in tables with proper formatting and responsive design.
"""

import flet as ft
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..utils.server_bridge import ServerBridge
from .button_factory import ActionButtonFactory


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
                ft.DataColumn(ft.Text("Filename", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Size", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Client", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD)),
            ],
            rows=[],
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            heading_row_color=ft.Colors.ON_SURFACE_VARIANT,
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
        self.selected_files = selected_files
        
        for file_obj in filtered_files:
            # File selection checkbox
            file_checkbox = ft.Checkbox(
                value=file_obj.filename in selected_files,
                on_change=on_file_select,
                data=file_obj.filename
            )
            
            # File type icon and display
            file_type_display = self._get_file_type_display(file_obj.filename)
            
            # Size formatting
            size_display = self._format_file_size(getattr(file_obj, 'size', 0))
            
            # Date formatting
            date_display = self._format_date(getattr(file_obj, 'date_received', ''))
            
            # Client display
            client_display = getattr(file_obj, 'client_id', 'Unknown')
            
            # Action buttons
            action_buttons = self._create_file_action_buttons(file_obj)
            
            # Create table row
            self.file_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(file_checkbox),
                        ft.DataCell(ft.Text(file_obj.filename, size=12)),
                        ft.DataCell(file_type_display),
                        ft.DataCell(ft.Text(size_display, size=11)),
                        ft.DataCell(ft.Text(date_display, size=11)),
                        ft.DataCell(ft.Text(client_display, size=11)),
                        ft.DataCell(action_buttons),
                    ]
                )
            )
    
    def _get_file_type_display(self, filename: str) -> ft.Control:
        """Get file type display with icon and label"""
        file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
        
        # File type mappings
        type_mappings = {
            'txt': ('📄', 'Text', ft.Colors.BLUE_100),
            'pdf': ('📕', 'PDF', ft.Colors.RED_100),
            'doc': ('📘', 'Word', ft.Colors.BLUE_200),
            'docx': ('📘', 'Word', ft.Colors.BLUE_200),
            'xls': ('📗', 'Excel', ft.Colors.GREEN_200),
            'xlsx': ('📗', 'Excel', ft.Colors.GREEN_200),
            'ppt': ('📙', 'PowerPoint', ft.Colors.ORANGE_200),
            'pptx': ('📙', 'PowerPoint', ft.Colors.ORANGE_200),
            'jpg': ('🖼️', 'Image', ft.Colors.PURPLE_100),
            'jpeg': ('🖼️', 'Image', ft.Colors.PURPLE_100),
            'png': ('🖼️', 'Image', ft.Colors.PURPLE_100),
            'gif': ('🖼️', 'Image', ft.Colors.PURPLE_100),
            'mp4': ('🎬', 'Video', ft.Colors.TEAL_100),
            'avi': ('🎬', 'Video', ft.Colors.TEAL_100),
            'mp3': ('🎵', 'Audio', ft.Colors.PINK_100),
            'wav': ('🎵', 'Audio', ft.Colors.PINK_100),
            'zip': ('🗜️', 'Archive', ft.Colors.GREY_200),
            'rar': ('🗜️', 'Archive', ft.Colors.GREY_200),
            '7z': ('🗜️', 'Archive', ft.Colors.GREY_200),
        }
        
        icon, type_name, bg_color = type_mappings.get(file_extension, ('📄', 'File', ft.Colors.GREY_100))
        
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
        return ft.Row([
            self.button_factory.create_action_button(
                'file_view_details', 
                lambda f=file_obj: [f.filename]
            ),
            self.button_factory.create_action_button(
                'file_preview', 
                lambda f=file_obj: [f.filename]
            ),
            self.button_factory.create_action_button(
                'file_download', 
                lambda f=file_obj: [f.filename]
            ),
            self.button_factory.create_action_button(
                'file_verify', 
                lambda f=file_obj: [f.filename]
            ),
            self.button_factory.create_action_button(
                'file_delete', 
                lambda f=file_obj: [f.filename]
            ),
        ], tight=True, spacing=5)
    
    def get_table_container(self) -> ft.Container:
        """Get the file table wrapped in a responsive container"""
        if not self.file_table:
            self.create_file_table()
        
        return ft.Container(
            content=ft.Column([
                self.file_table
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
            extension = file_obj.filename.split('.')[-1].lower() if '.' in file_obj.filename else 'no_ext'
            file_types[extension] = file_types.get(extension, 0) + 1
        
        return {
            'total_files': len(files),
            'total_size': total_size,
            'total_size_formatted': self._format_file_size(total_size),
            'file_types': file_types,
            'avg_size': total_size // len(files) if files else 0,
            'avg_size_formatted': self._format_file_size(total_size // len(files)) if files else "0 B"
        }