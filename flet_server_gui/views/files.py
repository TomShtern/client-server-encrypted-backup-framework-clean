"""
Purpose: File management view
Logic: File listing, filtering, and management operations
UI: File table, action buttons, and file details
"""

#!/usr/bin/env python3
"""
File Management View
Complete feature parity with TKinter GUI file management functionality.
Now uses modular architecture with separate components for better maintainability.
"""

import flet as ft
import asyncio
import os
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from core.file_management import FileManager
from ui.widgets.tables import EnhancedTable
from ui.widgets.buttons import ActionButtonFactory
from ui.components.file_table_renderer import FileTableRenderer
from ui.components.file_filter_manager import FileFilterManager
from ui.components.file_action_handlers import FileActionHandlers
from ui.components.file_preview_manager import FilePreviewManager
from actions.file_actions import FileActions


class FilesView:
    """
    Complete file management view with modular architecture.
    Composed of specialized components for table rendering, filtering, actions, and preview.
    """
    
    def __init__(self, server_bridge: "ServerBridge", dialog_system, toast_manager, page):
        self.server_bridge = server_bridge
        self.page = page
        
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
        
        # Search and filter controls from filter manager
        search_controls = self.filter_manager.create_search_controls(self._on_filtered_data_changed)
        
        # File table from table renderer
        file_table_container = self.table_renderer.get_table_container()
        
        # File preview area
        preview_container = self.preview_manager.create_preview_area()
        
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
        
        # Main layout
        return ft.Container(
            content=ft.Column([
                # Header section
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.FOLDER, size=24),
                            ft.Text("File Management", style=ft.TextThemeStyle.TITLE_LARGE),
                        ])
                    ], col={"xs": 12, "sm": 6, "md": 8}),
                    ft.Column([
                        self.refresh_button
                    ], col={"xs": 12, "sm": 6, "md": 4}, alignment=ft.MainAxisAlignment.END)
                ]),
                
                ft.Divider(),
                
                # Status
                self.status_text,
                
                ft.Divider(),
                
                # Search and filters
                search_controls,
                
                ft.Divider(),
                
                # Selection and bulk actions
                ft.ResponsiveRow([
                    ft.Column([
                        self.select_all_checkbox
                    ], col={"xs": 12, "sm": 6}),
                    ft.Column([
                        self.bulk_actions_row
                    ], col={"xs": 12, "sm": 6})
                ]),
                
                ft.Divider(),
                
                # File table and preview
                ft.ResponsiveRow([
                    ft.Column([
                        file_table_container
                    ], col={"xs": 12, "lg": 8}),
                    ft.Column([
                        preview_container
                    ], col={"xs": 12, "lg": 4})
                ], expand=True),
                
            ], spacing=10, expand=True),
            padding=20,
            expand=True
        )
    
    async def _refresh_files(self, e=None):
        """Refresh file data from server with loading state management."""
        try:
            if self.refresh_button:
                self.refresh_button.disabled = True
                self.refresh_button.text = "Refreshing..."
                self.page.update()
            
            # Get fresh file data
            files = await self.server_bridge.get_files()
            
            # Update filter manager with new data
            self.filter_manager.update_file_data(files)
            
            # Update table with filtered data
            filtered_files = self.filter_manager.get_filtered_files()
            self.table_renderer.update_table_data(filtered_files)
            
            # Update status
            if self.status_text:
                self.status_text.value = f"Loaded {len(files)} files ({len(filtered_files)} shown)"
                self.status_text.color = ft.Colors.GREEN_600
            
            # Reset selection
            self.selected_files.clear()
            if self.select_all_checkbox:
                self.select_all_checkbox.value = False
            
        except Exception as ex:
            if self.status_text:
                self.status_text.value = f"Error loading files: {str(ex)}"
                self.status_text.color = ft.Colors.RED_600
        finally:
            if self.refresh_button:
                self.refresh_button.disabled = False
                self.refresh_button.text = "Refresh Files"
                self.page.update()
    
    def _on_filtered_data_changed(self, filtered_files: List[Dict[str, Any]]):
        """Handle filtered data changes from filter manager."""
        try:
            # Update table with new filtered data
            self.table_renderer.update_table_data(filtered_files)
            
            # Update status text
            if self.status_text:
                total_files = len(self.filter_manager.all_files)
                self.status_text.value = f"Showing {len(filtered_files)} of {total_files} files"
                self.status_text.color = ft.Colors.BLUE_600
            
            # Reset selection when filter changes
            self.selected_files.clear()
            if self.select_all_checkbox:
                self.select_all_checkbox.value = False
                self._update_bulk_actions_visibility()
            
            self.page.update()
            
        except Exception as ex:
            if self.status_text:
                self.status_text.value = f"Error updating filter: {str(ex)}"
                self.status_text.color = ft.Colors.RED_600
            self.page.update()
    
    def _on_select_all(self, e):
        """Handle select all checkbox changes."""
        try:
            if e.control.value:  # Select all
                filtered_files = self.filter_manager.get_filtered_files()
                self.selected_files = [file['id'] for file in filtered_files]
                # Update table selection
                self.table_renderer.select_all_rows()
            else:  # Deselect all
                self.selected_files.clear()
                # Update table selection
                self.table_renderer.deselect_all_rows()
            
            self._update_bulk_actions_visibility()
            self.page.update()
            
        except Exception as ex:
            if self.toast_manager:
                self.toast_manager.show_error(f"Error in selection: {str(ex)}")
    
    def _on_file_selected(self, file_id: str, selected: bool):
        """Handle individual file selection from table."""
        try:
            if selected:
                if file_id not in self.selected_files:
                    self.selected_files.append(file_id)
            else:
                if file_id in self.selected_files:
                    self.selected_files.remove(file_id)
            
            # Update select all checkbox state
            self._update_select_all_checkbox()
            
            self._update_bulk_actions_visibility()
            self.page.update()
            
        except Exception as ex:
            if self.toast_manager:
                self.toast_manager.show_error(f"Error in file selection: {str(ex)}")
    
    def _update_select_all_checkbox(self):
        """Update select all checkbox based on current selection state."""
        try:
            filtered_files = self.filter_manager.get_filtered_files()
            total_filtered = len(filtered_files)
            selected_count = len(self.selected_files)
            
            if self.select_all_checkbox is None:
                return
                
            if selected_count == 0:
                self.select_all_checkbox.value = False
            elif selected_count == total_filtered:
                self.select_all_checkbox.value = True
            else:
                self.select_all_checkbox.value = None  # Indeterminate state
            
            self._update_bulk_actions_visibility()
            self.page.update()
        except Exception:
            pass  # Ignore errors in checkbox updates
    
    def _update_bulk_actions_visibility(self):
        """Update visibility of bulk action buttons"""
        try:
            has_selections = len(self.selected_files) > 0
            
            if self.bulk_actions_row and len(self.bulk_actions_row.controls) > 1:
                # Show/hide bulk action buttons (skip the label)
                for i, control in enumerate(self.bulk_actions_row.controls):
                    if i > 0 and isinstance(control, ft.ElevatedButton):
                        control.visible = has_selections
        except Exception:
            pass  # Ignore errors in visibility updates
    
    async def _bulk_download(self, e):
        """Handle bulk download action"""
        try:
            await self.action_handlers.perform_bulk_action("download", self.selected_files)
            self.selected_files.clear()
            self._update_bulk_actions_visibility()
            if self.select_all_checkbox:
                self.select_all_checkbox.value = False
            await self._refresh_files()
        except Exception as ex:
            if self.toast_manager:
                self.toast_manager.show_error(f"Error in bulk download: {str(ex)}")
    
    async def _bulk_verify(self, e):
        """Handle bulk verify action"""
        try:
            await self.action_handlers.perform_bulk_action("verify", self.selected_files)
            self.selected_files.clear()
            self._update_bulk_actions_visibility()
            if self.select_all_checkbox:
                self.select_all_checkbox.value = False
            await self._refresh_files()
        except Exception as ex:
            if self.toast_manager:
                self.toast_manager.show_error(f"Error in bulk verify: {str(ex)}")
    
    async def _bulk_delete(self, e):
        """Handle bulk delete action"""
        try:
            await self.action_handlers.perform_bulk_action("delete", self.selected_files)
            self.selected_files.clear()
            self._update_bulk_actions_visibility()
            if self.select_all_checkbox:
                self.select_all_checkbox.value = False
            await self._refresh_files()
        except Exception as ex:
            if self.toast_manager:
                self.toast_manager.show_error(f"Error in bulk delete: {str(ex)}")
    
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

    def update_data(self):
        """Update file data"""
        # Implementation will be added here
        pass