#!/usr/bin/env python3
"""
File Filter Manager Component
Handles search, filtering, and sorting logic for file data with debouncing.
"""

import flet as ft
import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime


class FileFilterManager:
    """Manages filtering, search, and sorting functionality for file data"""
    
    def __init__(self, page: ft.Page, toast_manager=None):
        self.page = page
        self.toast_manager = toast_manager
        
        # Data storage
        self.all_files = []
        self.filtered_files = []
        
        # Filter state
        self._current_type_filter = "all"
        self._current_sort = "date_desc"
        
        # Search debouncing
        self._search_timer: Optional[asyncio.Task] = None
        
        # UI Components
        self.search_field = None
        self.type_filter_dropdown = None
        self.sort_dropdown = None
        
        # Callbacks
        self.on_filter_changed: Optional[Callable] = None
    
    def create_search_controls(self, on_filter_change_callback: Callable) -> ft.Column:
        """Create search, filter, and sort UI controls"""
        self.on_filter_changed = on_filter_change_callback
        
        # Search field with debouncing
        self.search_field = ft.TextField(
            label="Search files...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            expand=True,
        )
        
        # File type filter dropdown
        self.type_filter_dropdown = ft.Dropdown(
            label="File Type",
            value="all",
            options=[
                ft.dropdown.Option("all", "All Files"),
                ft.dropdown.Option("txt", "Text Files"),
                ft.dropdown.Option("pdf", "PDF Files"),
                ft.dropdown.Option("doc", "Word Documents"),
                ft.dropdown.Option("xls", "Excel Files"),
                ft.dropdown.Option("ppt", "PowerPoint Files"),
                ft.dropdown.Option("image", "Images"),
                ft.dropdown.Option("video", "Videos"),
                ft.dropdown.Option("audio", "Audio Files"),
                ft.dropdown.Option("archive", "Archives"),
                ft.dropdown.Option("other", "Other"),
            ],
            on_change=self._on_type_filter_change,
            width=200
        )
        
        # Sort dropdown
        self.sort_dropdown = ft.Dropdown(
            label="Sort By",
            value="date_desc",
            options=[
                ft.dropdown.Option("date_desc", "Date (Newest First)"),
                ft.dropdown.Option("date_asc", "Date (Oldest First)"),
                ft.dropdown.Option("name_asc", "Name (A-Z)"),
                ft.dropdown.Option("name_desc", "Name (Z-A)"),
                ft.dropdown.Option("size_desc", "Size (Largest First)"),
                ft.dropdown.Option("size_asc", "Size (Smallest First)"),
                ft.dropdown.Option("type_asc", "Type (A-Z)"),
            ],
            on_change=self._on_sort_change,
            width=200
        )
        
        return ft.Column([
            ft.Row([
                self.search_field,
            ], expand=True),
            ft.Divider(height=10),
            ft.Row([
                self.type_filter_dropdown,
                ft.VerticalDivider(width=10),
                self.sort_dropdown,
            ], spacing=10),
        ], spacing=10)
    
    def set_file_data(self, files: List[Any]) -> None:
        """Set the file data to filter"""
        self.all_files = files
        self._apply_filters_and_sort()
    
    def update_file_data(self, files: List[Any]) -> None:
        """Update file data - alias for set_file_data"""
        self.set_file_data(files)
    
    def get_filtered_files(self) -> List[Any]:
        """Get the current filtered and sorted file list"""
        return self.filtered_files
    
    def _apply_filters_and_sort(self) -> None:
        """Apply current search, filter, and sort criteria"""
        # Start with all files
        filtered = self.all_files[:]
        
        # Apply search filter
        search_term = self.search_field.value.lower() if self.search_field and self.search_field.value else ""
        if search_term:
            filtered = [f for f in filtered if search_term in f.filename.lower()]
        
        # Apply type filter
        if self._current_type_filter != "all":
            filtered = self._apply_type_filter(filtered, self._current_type_filter)
        
        # Apply sorting
        filtered = self._apply_sort(filtered, self._current_sort)
        
        self.filtered_files = filtered
        
        # Notify parent of filter change
        if self.on_filter_changed:
            self.on_filter_changed(self.filtered_files)
    
    def _apply_type_filter(self, files: List[Any], type_filter: str) -> List[Any]:
        """Apply file type filtering"""
        if type_filter == "all":
            return files
        
        type_mappings = {
            "txt": ["txt", "text", "log"],
            "pdf": ["pdf"],
            "doc": ["doc", "docx", "rtf"],
            "xls": ["xls", "xlsx", "csv"],
            "ppt": ["ppt", "pptx"],
            "image": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg"],
            "video": ["mp4", "avi", "mkv", "mov", "wmv", "flv"],
            "audio": ["mp3", "wav", "flac", "aac", "ogg"],
            "archive": ["zip", "rar", "7z", "tar", "gz"],
        }
        
        if type_filter == "other":
            # Files that don't match any category
            all_extensions = set()
            for extensions in type_mappings.values():
                all_extensions.update(extensions)
            
            return [f for f in files if self._get_file_extension(f.filename) not in all_extensions]
        
        target_extensions = type_mappings.get(type_filter, [])
        return [f for f in files if self._get_file_extension(f.filename) in target_extensions]
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        return filename.split('.')[-1].lower() if '.' in filename else ''
    
    def _apply_sort(self, files: List[Any], sort_option: str) -> List[Any]:
        """Apply sorting to file list"""
        try:
            if sort_option == "date_desc":
                return sorted(files, key=lambda f: getattr(f, 'date_received', ''), reverse=True)
            elif sort_option == "date_asc":
                return sorted(files, key=lambda f: getattr(f, 'date_received', ''))
            elif sort_option == "name_asc":
                return sorted(files, key=lambda f: f.filename.lower())
            elif sort_option == "name_desc":
                return sorted(files, key=lambda f: f.filename.lower(), reverse=True)
            elif sort_option == "size_desc":
                return sorted(files, key=lambda f: getattr(f, 'size', 0), reverse=True)
            elif sort_option == "size_asc":
                return sorted(files, key=lambda f: getattr(f, 'size', 0))
            elif sort_option == "type_asc":
                return sorted(files, key=lambda f: self._get_file_extension(f.filename))
            else:
                return files
        except Exception as e:
            print(f"Error sorting files: {e}")
            return files
    
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
                self.page.run_in_thread(self._apply_filters_and_sort)
        except asyncio.CancelledError:
            # Timer was cancelled, ignore
            pass
        except Exception as e:
            print(f"Error in debounced search: {e}")
    
    def _on_type_filter_change(self, e):
        """Handle file type filter change"""
        self._current_type_filter = e.control.value
        self._apply_filters_and_sort()
        
        if self.toast_manager:
            filter_name = next((opt.text for opt in self.type_filter_dropdown.options if opt.key == e.control.value), e.control.value)
            self.toast_manager.show_success(f"Filtered by: {filter_name}")
    
    def _on_sort_change(self, e):
        """Handle sort option change"""
        self._current_sort = e.control.value
        self._apply_filters_and_sort()
        
        if self.toast_manager:
            sort_name = next((opt.text for opt in self.sort_dropdown.options if opt.key == e.control.value), e.control.value)
            self.toast_manager.show_success(f"Sorted by: {sort_name}")
    
    def reset_filters(self) -> None:
        """Reset all filters to default state"""
        # Reset search field
        if self.search_field:
            self.search_field.value = ""
        
        # Reset dropdowns
        if self.type_filter_dropdown:
            self.type_filter_dropdown.value = "all"
        if self.sort_dropdown:
            self.sort_dropdown.value = "date_desc"
        
        # Reset internal state
        self._current_type_filter = "all"
        self._current_sort = "date_desc"
        
        # Apply filters
        self._apply_filters_and_sort()
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """Get statistics about current filtering"""
        return {
            'total_files': len(self.all_files),
            'filtered_files': len(self.filtered_files),
            'current_type_filter': self._current_type_filter,
            'current_sort': self._current_sort,
            'search_active': bool(self.search_field and self.search_field.value)
        }
    
    def get_available_file_types(self) -> Dict[str, int]:
        """Get count of available file types in current data"""
        type_counts = {}
        for file_obj in self.all_files:
            extension = self._get_file_extension(file_obj.filename)
            type_counts[extension] = type_counts.get(extension, 0) + 1
        
        return type_counts