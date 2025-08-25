#!/usr/bin/env python3
"""
Comprehensive File Management Component (Refactored)
Complete feature parity with TKinter GUI file management functionality.
Now uses modular architecture with separate components for better maintainability.
"""

import flet as ft
import asyncio
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from ..utils.server_bridge import ServerBridge
from .base_component import BaseComponent
from .button_factory import ActionButtonFactory
from .file_table_renderer import FileTableRenderer
from .file_filter_manager import FileFilterManager
from .file_action_handlers import FileActionHandlers
from .file_preview_manager import FilePreviewManager
from ..actions import FileActions


class ComprehensiveFileManagement(BaseComponent):
    """
    Complete file management with modular architecture.
    Composed of specialized components for table rendering, filtering, actions, and preview.
    """
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, toast_manager, page):
        super().__init__(page, dialog_system, toast_manager)
        self.server_bridge = server_bridge
        
        # Initialize button factory
        self.button_factory = ActionButtonFactory(self, server_bridge, page)
        
        # Initialize modular components
        self.table_renderer = FileTableRenderer(server_bridge, self.button_factory, page)
        self.filter_manager = FileFilterManager(page, toast_manager)
        self.action_handlers = FileActionHandlers(server_bridge, dialog_system, toast_manager, page)
        self.preview_manager = FilePreviewManager(server_bridge, dialog_system, page)
        
        # Setup callbacks
        self.filter_manager.on_filter_changed = self._on_filtered_data_changed
        self.action_handlers.set_data_changed_callback(self._refresh_files)
        
        # UI Components
        self.status_text = None
        self.refresh_button = None
        self.bulk_actions_row = None
        self.select_all_checkbox = None
        
        # Data
        self.selected_files = []
    
    def build(self) -> ft.Control:
        """Build the comprehensive file management view using modular components."""
        
        # Header with title and status
        self.status_text = ft.Text(
            "Loading file data...",
            size=14,
            color=ft.Colors.BLUE_600
        )
        
        # Refresh button
        self.refresh_button = ft.ElevatedButton(
            "Refresh Files",
            icon=ft.Icons.REFRESH,
            on_click=self._refresh_files,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY,
                color=ft.Colors.ON_PRIMARY
            )
        )
        
        # Search, filter, and sort controls from filter manager
        filter_controls = self.filter_manager.create_search_controls(self._on_filtered_data_changed)
        
        # File table from table renderer
        file_table_container = self.table_renderer.get_table_container()
        
        # Select all checkbox
        self.select_all_checkbox = ft.Checkbox(
            label="Select All",
            on_change=self._on_select_all
        )
        
        # Bulk actions row
        self.bulk_actions_row = ft.Row([
            ft.Text("Bulk Actions:", weight=ft.FontWeight.BOLD),
            ft.ElevatedButton(
                "Download Selected",
                icon=ft.Icons.DOWNLOAD,
                on_click=self._bulk_download,
                style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_100),
                visible=False
            ),
            ft.ElevatedButton(
                "Verify Selected",
                icon=ft.Icons.VERIFIED,
                on_click=self._bulk_verify,
                style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_100),
                visible=False
            ),
            ft.ElevatedButton(
                "Delete Selected",
                icon=ft.Icons.DELETE_FOREVER,
                on_click=self._bulk_delete,
                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_100),
                visible=False
            ),
        ], spacing=10)
        
        # File statistics card
        stats_card = self._create_file_stats_card()
        
        # Main layout
        return ft.Container(
            content=ft.Column([
                # Header section
                ft.Row([
                    ft.Icon(ft.Icons.FOLDER, size=24),
                    ft.Text("File Management", style=ft.TextThemeStyle.TITLE_LARGE, expand=True),
                    self.refresh_button
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                # Status and statistics
                ft.Row([
                    self.status_text,
                    stats_card
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Divider(),
                
                # Search, filters, and sorting
                filter_controls,
                
                ft.Divider(),
                
                # Selection and bulk actions
                ft.Row([
                    self.select_all_checkbox,
                    ft.VerticalDivider(width=20),
                    self.bulk_actions_row
                ]),
                
                ft.Divider(),
                
                # File table
                file_table_container,
                
            ], spacing=10, expand=True),
            padding=20,
            expand=True
        )
    
    def _create_file_stats_card(self) -> ft.Container:
        """Create file statistics card"""
        return ft.Container(
            content=ft.Column([
                ft.Text("File Statistics", weight=ft.FontWeight.BOLD, size=12),
                ft.Text("0 files", size=10, key="file_count"),
                ft.Text("0 B total", size=10, key="total_size"),
            ], spacing=2, tight=True),
            bgcolor=ft.Colors.SURFACE_VARIANT,
            padding=8,
            border_radius=6,
            width=120
        )
    
    async def _refresh_files(self, e=None):
        """Refresh file data from server"""
        try:
            self.status_text.value = "Refreshing file data..."
            self.page.update()
            
            # Get fresh file data from server bridge
            files_data = await self.execute_with_loading(
                self.server_bridge.get_all_files(),
                "Loading files..."
            )
            
            if files_data:
                # Update filter manager with new data
                self.filter_manager.set_file_data(files_data)
                
                # Update statistics
                stats = self.table_renderer.get_file_statistics(files_data)
                self._update_file_stats_card(stats)
                
                # Update status
                self.status_text.value = f"✅ Found {len(files_data)} files"
                self.status_text.color = ft.Colors.GREEN_600
            else:
                # No files found
                self.filter_manager.set_file_data([])
                self._update_file_stats_card({'total_files': 0, 'total_size': 0})
                self.status_text.value = "No files found"
                self.status_text.color = ft.Colors.GREY_600
            
            # Clear selections
            self.selected_files.clear()
            self._update_bulk_actions_visibility()
            
            self.page.update()
            
        except Exception as e:
            # Handle error
            self.status_text.value = f"❌ Error loading files: {str(e)}"
            self.status_text.color = ft.Colors.ERROR
            self.page.update()
            
            if self.toast_manager:
                self.toast_manager.show_error(f"Failed to refresh files: {str(e)}")
    
    def _update_file_stats_card(self, stats: Dict[str, Any]):
        """Update the file statistics card"""
        try:
            # Find and update the stats card controls
            stats_card = None
            for control in self.page.controls:
                if hasattr(control, 'content') and isinstance(control.content, ft.Column):
                    for col_control in control.content.controls:
                        if hasattr(col_control, 'content') and isinstance(col_control.content, ft.Column):
                            for inner_control in col_control.content.controls:
                                if hasattr(inner_control, 'key') and inner_control.key == "file_count":
                                    inner_control.value = f"{stats.get('total_files', 0)} files"
                                elif hasattr(inner_control, 'key') and inner_control.key == "total_size":
                                    inner_control.value = stats.get('total_size_formatted', '0 B')
        except Exception:
            pass  # Ignore stats update errors
    
    def _on_filtered_data_changed(self, filtered_files: List[Any]):
        """Handle when filtered file data changes"""
        # Update table renderer with filtered data
        self.table_renderer.populate_file_table(
            filtered_files, 
            self._on_file_select, 
            self.selected_files
        )
        
        # Update status
        total_files = len(self.filter_manager.all_files)
        filtered_count = len(filtered_files)
        
        if filtered_count == total_files:
            self.status_text.value = f"✅ Showing all {total_files} files"
        else:
            self.status_text.value = f"✅ Showing {filtered_count} of {total_files} files"
        
        self.status_text.color = ft.Colors.GREEN_600
        
        # Update filtered statistics
        if filtered_files:
            filtered_stats = self.table_renderer.get_file_statistics(filtered_files)
            self._update_file_stats_card(filtered_stats)
        
        # Update UI
        self.page.update()
    
    def _on_select_all(self, e):
        """Handle select all checkbox"""
        select_all = e.control.value
        self.selected_files.clear()
        
        filtered_files = self.filter_manager.get_filtered_files()
        
        if select_all:
            self.selected_files = [file_obj.filename for file_obj in filtered_files]
        
        # Update table display
        self.table_renderer.populate_file_table(
            filtered_files,
            self._on_file_select,
            self.selected_files
        )
        
        self._update_bulk_actions_visibility()
        self.page.update()
    
    def _on_file_select(self, e):
        """Handle individual file selection"""
        filename = e.control.data
        
        if e.control.value:
            if filename not in self.selected_files:
                self.selected_files.append(filename)
        else:
            if filename in self.selected_files:
                self.selected_files.remove(filename)
        
        # Update select all checkbox state
        filtered_files = self.filter_manager.get_filtered_files()
        total_filtered = len(filtered_files)
        selected_count = len(self.selected_files)
        
        if selected_count == 0:
            self.select_all_checkbox.value = False
        elif selected_count == total_filtered:
            self.select_all_checkbox.value = True
        else:
            self.select_all_checkbox.value = None  # Indeterminate state
        
        self._update_bulk_actions_visibility()
        self.page.update()
    
    def _update_bulk_actions_visibility(self):
        """Update visibility of bulk action buttons"""
        has_selections = len(self.selected_files) > 0
        
        if self.bulk_actions_row and len(self.bulk_actions_row.controls) > 1:
            # Show/hide bulk action buttons (skip the label)
            for i, control in enumerate(self.bulk_actions_row.controls):
                if i > 0 and isinstance(control, ft.ElevatedButton):
                    control.visible = has_selections
    
    async def _bulk_download(self, e):
        """Handle bulk download action"""
        await self.action_handlers.perform_bulk_action("download", self.selected_files)
        self.selected_files.clear()
        self._update_bulk_actions_visibility()
        self.select_all_checkbox.value = False
    
    async def _bulk_verify(self, e):
        """Handle bulk verify action"""
        await self.action_handlers.perform_bulk_action("verify", self.selected_files)
        self.selected_files.clear()
        self._update_bulk_actions_visibility()
        self.select_all_checkbox.value = False
    
    async def _bulk_delete(self, e):
        """Handle bulk delete action"""
        await self.action_handlers.perform_bulk_action("delete", self.selected_files)
        self.selected_files.clear()
        self._update_bulk_actions_visibility()
        self.select_all_checkbox.value = False
    
    # Auto-refresh functionality
    async def start_auto_refresh(self, interval_seconds: int = 60):
        """Start automatic refresh of file data"""
        while True:
            await asyncio.sleep(interval_seconds)
            if self.page:  # Check if page is still active
                await self._refresh_files()
    
    def get_component_stats(self) -> Dict[str, Any]:
        """Get statistics about the component state"""
        return {
            'total_files': len(self.filter_manager.all_files),
            'filtered_files': len(self.filter_manager.get_filtered_files()),
            'selected_files': len(self.selected_files),
            'filter_stats': self.filter_manager.get_filter_stats(),
            'file_types_available': self.filter_manager.get_available_file_types(),
            'preview_cache_info': self.preview_manager.get_cache_info()
        }
    
    def clear_caches(self):
        """Clear all caches for memory management"""
        self.preview_manager.clear_preview_cache()