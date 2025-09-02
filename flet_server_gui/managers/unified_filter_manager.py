#!/usr/bin/env python3
"""
Unified Filter Manager Component
Consolidates client and file filtering using Flet framework patterns.
Eliminates "Slightly Different" Fallacy by providing single abstracted filtering solution.

Follows Duplication Mindset principles:
- Single Responsibility: ONE manager for ALL filtering concerns
- Framework Harmony: Uses Flet's built-in controls (Chip, SearchBar, Dropdown)
- Configuration Over Proliferation: data_type parameter handles different filter types
"""

import flet as ft
import asyncio
from typing import List, Dict, Any, Optional, Callable, Union
from datetime import datetime
from enum import Enum


class FilterDataType(Enum):
    """Supported data types for filtering"""
    CLIENTS = "clients"
    FILES = "files"


class FilterConfig:
    """Configuration for different filter types"""
    
    @staticmethod
    def get_client_config() -> Dict[str, Any]:
        """Configuration for client filtering"""
        return {
            'data_type': FilterDataType.CLIENTS,
            'search_fields': ['client_id'],
            'filter_options': [
                {'key': 'all', 'label': 'All', 'selected': True},
                {'key': 'connected', 'label': 'Connected'},
                {'key': 'registered', 'label': 'Registered'},
                {'key': 'offline', 'label': 'Offline'}
            ],
            'filter_field': 'status',
            'sort_options': [
                {'key': 'id_asc', 'label': 'ID (A-Z)'},
                {'key': 'id_desc', 'label': 'ID (Z-A)'},
                {'key': 'status_asc', 'label': 'Status (A-Z)'},
                {'key': 'date_desc', 'label': 'Last Activity (Recent)'},
                {'key': 'date_asc', 'label': 'Last Activity (Oldest)'}
            ],
            'default_sort': 'id_asc',
            'use_chips': True  # Flet Chip pattern for client status
        }
    
    @staticmethod
    def get_file_config() -> Dict[str, Any]:
        """Configuration for file filtering"""
        return {
            'data_type': FilterDataType.FILES,
            'search_fields': ['filename'],
            'filter_options': [
                {'key': 'all', 'label': 'All Files'},
                {'key': 'txt', 'label': 'Text Files'},
                {'key': 'pdf', 'label': 'PDF Files'},
                {'key': 'doc', 'label': 'Word Documents'},
                {'key': 'xls', 'label': 'Excel Files'},
                {'key': 'ppt', 'label': 'PowerPoint Files'},
                {'key': 'image', 'label': 'Images'},
                {'key': 'video', 'label': 'Videos'},
                {'key': 'audio', 'label': 'Audio Files'},
                {'key': 'archive', 'label': 'Archives'},
                {'key': 'other', 'label': 'Other'}
            ],
            'filter_field': 'file_type',
            'sort_options': [
                {'key': 'date_desc', 'label': 'Date (Newest First)'},
                {'key': 'date_asc', 'label': 'Date (Oldest First)'},
                {'key': 'name_asc', 'label': 'Name (A-Z)'},
                {'key': 'name_desc', 'label': 'Name (Z-A)'},
                {'key': 'size_desc', 'label': 'Size (Largest First)'},
                {'key': 'size_asc', 'label': 'Size (Smallest First)'},
                {'key': 'type_asc', 'label': 'Type (A-Z)'}
            ],
            'default_sort': 'date_desc',
            'use_chips': False  # Dropdown pattern for file types
        }


class UnifiedFilterManager:
    """
    Unified filtering manager supporting both client and file filtering.
    Eliminates duplication by abstracting common filtering patterns.
    Uses Flet framework patterns instead of custom implementations.
    """
    
    def __init__(self, page: ft.Page, data_type: FilterDataType, toast_manager=None):
        self.page = page
        self.data_type = data_type
        self.toast_manager = toast_manager
        
        # Get configuration for this data type
        if data_type == FilterDataType.CLIENTS:
            self.config = FilterConfig.get_client_config()
        else:
            self.config = FilterConfig.get_file_config()
        
        # Data storage
        self.all_data = []
        self.filtered_data = []
        
        # Filter state
        self._current_filter = "all"
        self._current_sort = self.config['default_sort']
        
        # Search debouncing using proper Flet patterns
        self._search_timer: Optional[asyncio.Task] = None
        
        # UI Components (using Flet built-in controls)
        self.search_field = None
        self.filter_controls = None
        self.sort_dropdown = None
        
        # Callbacks
        self.on_filter_changed: Optional[Callable] = None
    
    def create_search_controls(self, on_filter_change_callback: Callable) -> ft.Column:
        """Create search and filter UI controls using Flet patterns"""
        self.on_filter_changed = on_filter_change_callback
        
        # Search field using Flet TextField (better than custom SearchBar for this use case)
        search_label = f"Search {self.data_type.value}..."
        self.search_field = ft.TextField(
            label=search_label,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            expand=True,
            helper_text=f"Search by {', '.join(self.config['search_fields'])}"
        )
        
        # Filter controls - Chips or Dropdown based on config
        if self.config['use_chips']:
            # Use Flet Chip pattern (better for client status)
            self.filter_controls = self._create_filter_chips()
            filter_label = ft.Text("Filter by Status:", size=12, weight=ft.FontWeight.BOLD)
        else:
            # Use Flet Dropdown pattern (better for file types)
            self.filter_controls = self._create_filter_dropdown()
            filter_label = ft.Text("Filter by Type:", size=12, weight=ft.FontWeight.BOLD)
        
        # Sort dropdown using Flet Dropdown
        self.sort_dropdown = ft.Dropdown(
            label="Sort By",
            value=self.config['default_sort'],
            options=[
                ft.dropdown.Option(opt['key'], opt['label']) 
                for opt in self.config['sort_options']
            ],
            on_change=self._on_sort_change,
            width=200
        )
        
        # Layout using Flet responsive patterns
        return ft.Column([
            # Search section
            ft.Row([self.search_field], expand=True),
            ft.Divider(height=10),
            
            # Filter section
            filter_label,
            self.filter_controls,
            ft.Divider(height=10),
            
            # Sort section
            ft.Row([
                ft.Text("Sort:", size=12, weight=ft.FontWeight.BOLD),
                self.sort_dropdown
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        ], spacing=10)
    
    def _create_filter_chips(self) -> ft.Row:
        """Create filter chips using Flet Chip pattern"""
        chips = []
        for i, option in enumerate(self.config['filter_options']):
            chip = ft.Chip(
                label=ft.Text(option['label']),
                selected=option.get('selected', False),
                on_select=lambda e, key=option['key']: self._on_chip_select(key, e),
                bgcolor=self._get_chip_color(option['key']),
                data=option['key']  # Store key for reference
            )
            chips.append(chip)
        
        return ft.Row(chips, spacing=8, wrap=True)
    
    def _create_filter_dropdown(self) -> ft.Dropdown:
        """Create filter dropdown using Flet Dropdown pattern"""
        return ft.Dropdown(
            label=self.config['filter_field'].replace('_', ' ').title(),
            value="all",
            options=[
                ft.dropdown.Option(opt['key'], opt['label']) 
                for opt in self.config['filter_options']
            ],
            on_change=self._on_dropdown_filter_change,
            width=200
        )
    
    def _get_chip_color(self, filter_key: str) -> str:
        """Get appropriate color for chip based on filter type"""
        # Use Flet color system instead of custom tokens
        color_map = {
            'all': ft.Colors.BLUE_GREY,
            'connected': ft.Colors.GREEN,
            'registered': ft.Colors.BLUE,
            'offline': ft.Colors.RED_400
        }
        return color_map.get(filter_key, ft.Colors.BLUE_GREY)
    
    def set_data(self, data: List[Any]) -> None:
        """Set the data to filter (unified interface)"""
        self.all_data = data
        self._apply_filters_and_sort()
    
    def update_data(self, data: List[Any]) -> None:
        """Update data - alias for set_data"""
        self.set_data(data)
    
    def get_filtered_data(self) -> List[Any]:
        """Get the current filtered data"""
        return self.filtered_data
    
    def _apply_filters_and_sort(self) -> None:
        """Apply current search, filter, and sort criteria"""
        # Start with all data
        filtered = self.all_data[:]
        
        # Apply search filter
        search_term = self.search_field.value.lower() if self.search_field and self.search_field.value else ""
        if search_term:
            filtered = self._apply_search_filter(filtered, search_term)
        
        # Apply type/status filter
        if self._current_filter != "all":
            filtered = self._apply_category_filter(filtered, self._current_filter)
        
        # Apply sorting
        filtered = self._apply_sort(filtered, self._current_sort)
        
        self.filtered_data = filtered
        
        # Notify parent of filter change
        if self.on_filter_changed:
            self.on_filter_changed(self.filtered_data)
    
    def _apply_search_filter(self, data: List[Any], search_term: str) -> List[Any]:
        """Apply search filter to data"""
        filtered = []
        search_fields = self.config['search_fields']
        
        for item in data:
            for field in search_fields:
                field_value = ""
                # Handle both object attributes and dictionary access
                if hasattr(item, field):
                    field_value = getattr(item, field, "").lower()
                elif hasattr(item, '__getitem__') and field in item:
                    field_value = item[field].lower()
                
                if search_term in field_value:
                    filtered.append(item)
                    break  # Found match, no need to check other fields
        
        return filtered
    
    def _apply_category_filter(self, data: List[Any], filter_value: str) -> List[Any]:
        """Apply category filter (status for clients, file type for files)"""
        if self.data_type == FilterDataType.CLIENTS:
            return self._apply_client_status_filter(data, filter_value)
        else:
            return self._apply_file_type_filter(data, filter_value)
    
    def _apply_client_status_filter(self, clients: List[Any], status: str) -> List[Any]:
        """Apply client status filter"""
        filtered = []
        for client in clients:
            client_status = ""
            if hasattr(client, 'status'):
                client_status = client.status.lower()
            elif hasattr(client, '__getitem__') and 'status' in client:
                client_status = client['status'].lower()
            
            if client_status == status.lower():
                filtered.append(client)
        
        return filtered
    
    def _apply_file_type_filter(self, files: List[Any], type_filter: str) -> List[Any]:
        """Apply file type filter using extension mapping"""
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
            
            return [f for f in files if self._get_file_extension(f) not in all_extensions]
        
        target_extensions = type_mappings.get(type_filter, [])
        return [f for f in files if self._get_file_extension(f) in target_extensions]
    
    def _get_file_extension(self, file_obj: Any) -> str:
        """Get file extension from file object"""
        filename = ""
        if hasattr(file_obj, 'filename'):
            filename = file_obj.filename
        elif hasattr(file_obj, '__getitem__') and 'filename' in file_obj:
            filename = file_obj['filename']
        
        return filename.split('.')[-1].lower() if '.' in filename else ''
    
    def _apply_sort(self, data: List[Any], sort_option: str) -> List[Any]:
        """Apply sorting to data list"""
        try:
            if self.data_type == FilterDataType.CLIENTS:
                return self._sort_clients(data, sort_option)
            else:
                return self._sort_files(data, sort_option)
        except Exception as e:
            print(f"Error sorting {self.data_type.value}: {e}")
            return data
    
    def _sort_clients(self, clients: List[Any], sort_option: str) -> List[Any]:
        """Sort client data"""
        if sort_option == "id_asc":
            return sorted(clients, key=lambda c: self._get_field_value(c, 'client_id').lower())
        elif sort_option == "id_desc":
            return sorted(clients, key=lambda c: self._get_field_value(c, 'client_id').lower(), reverse=True)
        elif sort_option == "status_asc":
            return sorted(clients, key=lambda c: self._get_field_value(c, 'status').lower())
        elif sort_option.startswith("date_"):
            reverse = sort_option.endswith("_desc")
            return sorted(clients, key=lambda c: self._get_field_value(c, 'last_activity', ''), reverse=reverse)
        return clients
    
    def _sort_files(self, files: List[Any], sort_option: str) -> List[Any]:
        """Sort file data"""
        if sort_option.startswith("date_"):
            reverse = sort_option.endswith("_desc")
            return sorted(files, key=lambda f: self._get_field_value(f, 'date_received', ''), reverse=reverse)
        elif sort_option.startswith("name_"):
            reverse = sort_option.endswith("_desc")
            return sorted(files, key=lambda f: self._get_field_value(f, 'filename').lower(), reverse=reverse)
        elif sort_option.startswith("size_"):
            reverse = sort_option.endswith("_desc")
            return sorted(files, key=lambda f: int(self._get_field_value(f, 'size', '0')), reverse=reverse)
        elif sort_option == "type_asc":
            return sorted(files, key=lambda f: self._get_file_extension(f))
        return files
    
    def _get_field_value(self, obj: Any, field: str, default: str = "") -> str:
        """Get field value from object (handles both attributes and dict access)"""
        if hasattr(obj, field):
            return str(getattr(obj, field, default))
        elif hasattr(obj, '__getitem__') and field in obj:
            return str(obj[field])
        return default
    
    def _on_search_change(self, e):
        """Handle search field changes with proper Flet debouncing"""
        # Cancel existing timer if running
        if self._search_timer and not self._search_timer.done():
            self._search_timer.cancel()
        
        # Start new debounced search timer
        self._search_timer = asyncio.create_task(self._debounced_search())
    
    async def _debounced_search(self):
        """Execute search after debounce delay using Flet patterns"""
        try:
            # Wait for debounce delay (300ms)
            await asyncio.sleep(0.3)
            
            # Apply filters on main thread using Flet's thread-safe method
            if self.page:
                self.page.run_in_thread(self._apply_filters_and_sort)
        except asyncio.CancelledError:
            # Timer was cancelled, ignore
            pass
        except Exception as e:
            print(f"Error in debounced search: {e}")
    
    def _on_chip_select(self, filter_value: str, e):
        """Handle chip selection (for client status filtering)"""
        # Update current filter
        self._current_filter = filter_value
        
        # Update chip selection states using Flet pattern
        if self.filter_controls and hasattr(self.filter_controls, 'controls'):
            for chip in self.filter_controls.controls:
                if isinstance(chip, ft.Chip):
                    chip.selected = (chip.data == filter_value)
        
        # Apply filters and show feedback
        self._apply_filters_and_sort()
        self._show_filter_feedback(filter_value, "status")
    
    def _on_dropdown_filter_change(self, e):
        """Handle dropdown filter change (for file type filtering)"""
        self._current_filter = e.control.value
        self._apply_filters_and_sort()
        
        # Find filter label for feedback
        filter_label = next(
            (opt['label'] for opt in self.config['filter_options'] if opt['key'] == e.control.value), 
            e.control.value
        )
        self._show_filter_feedback(filter_label, "type")
    
    def _on_sort_change(self, e):
        """Handle sort option change"""
        self._current_sort = e.control.value
        self._apply_filters_and_sort()
        
        # Find sort label for feedback
        sort_label = next(
            (opt['label'] for opt in self.config['sort_options'] if opt['key'] == e.control.value),
            e.control.value
        )
        self._show_filter_feedback(sort_label, "sort")
    
    def _show_filter_feedback(self, value: str, action_type: str):
        """Show user feedback using toast manager"""
        if self.toast_manager:
            if action_type == "sort":
                self.toast_manager.show_success(f"Sorted by: {value}")
            else:
                self.toast_manager.show_success(f"Filtered by {action_type}: {value}")
    
    def reset_filters(self) -> None:
        """Reset all filters to default state"""
        # Reset search field
        if self.search_field:
            self.search_field.value = ""
        
        # Reset filter controls
        self._current_filter = "all"
        if self.config['use_chips'] and self.filter_controls:
            # Reset chips
            for chip in self.filter_controls.controls:
                if isinstance(chip, ft.Chip):
                    chip.selected = (chip.data == "all")
        elif not self.config['use_chips'] and isinstance(self.filter_controls, ft.Dropdown):
            # Reset dropdown
            self.filter_controls.value = "all"
        
        # Reset sort
        if self.sort_dropdown:
            self.sort_dropdown.value = self.config['default_sort']
        self._current_sort = self.config['default_sort']
        
        # Apply filters
        self._apply_filters_and_sort()
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """Get statistics about current filtering"""
        return {
            'data_type': self.data_type.value,
            'total_items': len(self.all_data),
            'filtered_items': len(self.filtered_data),
            'current_filter': self._current_filter,
            'current_sort': self._current_sort,
            'search_active': bool(self.search_field and self.search_field.value),
            'filter_config': self.config
        }


# Factory functions for easy creation
def create_client_filter_manager(page: ft.Page, toast_manager=None) -> UnifiedFilterManager:
    """Create a filter manager configured for client data"""
    return UnifiedFilterManager(page, FilterDataType.CLIENTS, toast_manager)


def create_file_filter_manager(page: ft.Page, toast_manager=None) -> UnifiedFilterManager:
    """Create a filter manager configured for file data"""
    return UnifiedFilterManager(page, FilterDataType.FILES, toast_manager)
