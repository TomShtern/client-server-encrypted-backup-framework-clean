#!/usr/bin/env python3
"""
Bulk Operations Component
Material Design 3 component for bulk file operations with enhanced UI.
"""

import flet as ft
from typing import List, Dict, Optional, Callable
from flet_server_gui.managers.theme_manager import TOKENS
from flet_server_gui.components.enhanced_components import (
    create_enhanced_button,
    create_enhanced_icon_button,
    EnhancedCard
)
from flet_server_gui.components.dialogs import (
    create_confirmation_dialog,
    create_progress_dialog,
    create_toast_notification
)


class BulkOperations(EnhancedCard):
    """Bulk operations component for file management"""
    
    def __init__(self,
                 selected_files: List[Dict] = None,
                 on_delete: Optional[Callable] = None,
                 on_download: Optional[Callable] = None,
                 on_move: Optional[Callable] = None,
                 on_copy: Optional[Callable] = None,
                 animate_duration: int = 200,
                 **kwargs):
        self.selected_files = selected_files or []
        self.on_delete = on_delete
        self.on_download = on_download
        self.on_move = on_move
        self.on_copy = on_copy
        
        # Create the main content
        content = self._build_content()
        
        super().__init__(
            content=content,
            animate_duration=animate_duration,
            **kwargs
        )
    
    def _build_content(self) -> ft.Control:
        """Build the bulk operations content"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.SELECT_ALL, size=24),
            ft.Text("Bulk Operations", style=ft.TextThemeStyle.TITLE_LARGE),
            ft.Container(expand=True),
            ft.Text(f"{len(self.selected_files)} file(s) selected", style=ft.TextThemeStyle.BODY_MEDIUM)
        ], spacing=12)
        
        # Operation buttons
        operation_buttons = ft.Row([
            create_enhanced_button(
                text="Download",
                icon=ft.Icons.DOWNLOAD,
                on_click=self._on_download,
                disabled=len(self.selected_files) == 0
            ),
            create_enhanced_button(
                text="Move",
                icon=ft.Icons.FOLDER,
                on_click=self._on_move,
                disabled=len(self.selected_files) == 0
            ),
            create_enhanced_button(
                text="Copy",
                icon=ft.Icons.CONTENT_COPY,
                on_click=self._on_copy,
                disabled=len(self.selected_files) == 0
            ),
            create_enhanced_button(
                text="Delete",
                icon=ft.Icons.DELETE,
                on_click=self._on_delete,
                disabled=len(self.selected_files) == 0
            )
        ], spacing=12)
        
        # Selected files list
        files_list = self._create_files_list()
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                operation_buttons,
                ft.Divider(),
                files_list
            ], spacing=16),
            padding=ft.padding.all(20),
            width=500
        )
    
    def _create_files_list(self) -> ft.Control:
        """Create list of selected files"""
        if not self.selected_files:
            return ft.Text("No files selected", italic=True, color=TOKENS["outline"])

        file_items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DESCRIPTION, size=16),
                title=ft.Text(file_info.get("name", "Unknown")),
                subtitle=ft.Text(
                    f"{file_info.get('size', 'Unknown')} • {file_info.get('modified', 'Unknown')}"
                ),
                dense=True,
            )
            for file_info in self.selected_files[:10]
        ]
        # If there are more files, add a note
        if len(self.selected_files) > 10:
            file_items.append(
                ft.ListTile(
                    title=ft.Text(f"... and {len(self.selected_files) - 10} more files"),
                    dense=True
                )
            )

        return ft.Column(file_items, spacing=2)
    
    def _on_download(self, e):
        """Handle bulk download"""
        if self.on_download:
            self.on_download(e, self.selected_files)
        else:
            self._perform_bulk_operation("download", "Downloading files...")
    
    def _on_move(self, e):
        """Handle bulk move"""
        if self.on_move:
            self.on_move(e, self.selected_files)
        else:
            self._perform_bulk_operation("move", "Moving files...")
    
    def _on_copy(self, e):
        """Handle bulk copy"""
        if self.on_copy:
            self.on_copy(e, self.selected_files)
        else:
            self._perform_bulk_operation("copy", "Copying files...")
    
    def _on_delete(self, e):
        """Handle bulk delete"""
        if self.on_delete:
            self.on_delete(e, self.selected_files)
        else:
            dialog = create_confirmation_dialog(
                title="Delete Files",
                message=f"Are you sure you want to delete {len(self.selected_files)} selected files?",
                on_confirm=self._perform_bulk_delete
            )
            dialog.show(self.page)
    
    def _perform_bulk_operation(self, operation: str, message: str):
        """Perform a bulk operation with progress dialog"""
        progress_dialog = create_progress_dialog(
            title="Bulk Operation",
            message=message
        )
        progress_dialog.show(self.page)
        
        # Simulate operation with a delay
        import asyncio
        async def simulate_operation():
            # Simulate progress
            for i in range(10):
                await asyncio.sleep(0.2)
                progress_dialog.update_message(f"{message} ({i+1}/10)")
                self.page.update()
            
            # Close dialog
            progress_dialog.open = False
            self.page.update()
            
            # Show completion message
            toast = create_toast_notification(
                message=f"Bulk {operation} completed successfully",
                bgcolor=TOKENS["container"]
            )
            toast.show(self.page)
        
        asyncio.create_task(simulate_operation())
    
    def _perform_bulk_delete(self, e):
        """Perform bulk delete operation"""
        progress_dialog = create_progress_dialog(
            title="Deleting Files",
            message="Deleting selected files..."
        )
        progress_dialog.show(self.page)
        
        # Simulate deletion with a delay
        import asyncio
        async def simulate_deletion():
            # Simulate progress
            for i, file_info in enumerate(self.selected_files):
                await asyncio.sleep(0.1)
                progress_dialog.update_message(f"Deleting {file_info.get('name', 'file')} ({i+1}/{len(self.selected_files)})")
                self.page.update()
            
            # Close dialog
            progress_dialog.open = False
            self.page.update()
            
            # Show completion message
            toast = create_toast_notification(
                message=f"Deleted {len(self.selected_files)} files successfully",
                bgcolor=TOKENS["surface_variant"]
            )
            toast.show(self.page)
            
            # Clear selection
            self.selected_files.clear()
            self._update_content()
        
        asyncio.create_task(simulate_deletion())
    
    def _update_content(self):
        """Update the component content"""
        new_content = self._build_content()
        self.content = new_content
        self.page.update()


# Factory function
def create_bulk_operations(selected_files: List[Dict] = None, **kwargs) -> BulkOperations:
    """Create bulk operations component"""
    return BulkOperations(selected_files=selected_files, **kwargs)
