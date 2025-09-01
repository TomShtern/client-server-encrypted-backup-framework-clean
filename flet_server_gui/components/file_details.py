#!/usr/bin/env python3
"""
File Details Component
Material Design 3 component for detailed file information with enhanced UI.
"""

import flet as ft
from typing import Dict, Optional, Callable
import os
# Unified theme system - consolidated theme functionality
from flet_server_gui.core.theme_compatibility import TOKENS
from flet_server_gui.components.enhanced_components import (
    EnhancedCard,
    create_enhanced_button,
    create_enhanced_icon_button
)


class FileDetails(EnhancedCard):
    """File details component with comprehensive information"""
    
    def __init__(self,
                 file_info: Dict = None,
                 on_close: Optional[Callable] = None,
                 on_download: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None,
                 on_preview: Optional[Callable] = None,
                 animate_duration: int = 200,
                 **kwargs):
        self.file_info = file_info or {}
        self.on_close = on_close
        self.on_download = on_download
        self.on_delete = on_delete
        self.on_preview = on_preview
        
        # Create the main content
        content = self._build_content()
        
        super().__init__(
            content=content,
            animate_duration=animate_duration,
            **kwargs
        )
    
    def _build_content(self) -> ft.Control:
        """Build the file details content"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.INFO, size=24),
            ft.Text("File Details", style=ft.TextThemeStyle.TITLE_LARGE),
            ft.Container(expand=True),
            create_enhanced_icon_button(
                icon=ft.Icons.CLOSE,
                tooltip="Close details",
                on_click=self._on_close
            )
        ], spacing=12)
        
        # File information grid
        info_grid = self._create_info_grid()
        
        # Action buttons
        action_buttons = self._create_action_buttons()
        
        # Metadata section
        metadata_section = self._create_metadata_section()
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                info_grid,
                ft.Divider(),
                action_buttons,
                ft.Divider(),
                metadata_section
            ], spacing=16),
            padding=ft.padding.all(20),
            width=500
        )
    
    def _create_info_grid(self) -> ft.Control:
        """Create file information grid"""
        file_name = self.file_info.get("name", "Unknown")
        file_path = self.file_info.get("path", "Unknown")
        file_size = self.file_info.get("size", "Unknown")
        file_type = self.file_info.get("type", "Unknown")
        modified = self.file_info.get("modified", "Unknown")
        created = self.file_info.get("created", "Unknown")
        owner = self.file_info.get("owner", "Unknown")
        permissions = self.file_info.get("permissions", "Unknown")
        
        return ft.ResponsiveRow([
            # Name
            ft.Column([
                ft.Text("Name", style=ft.TextThemeStyle.LABEL_LARGE, color=TOKENS['outline']),
                ft.Text(file_name, style=ft.TextThemeStyle.BODY_LARGE)
            ], col={"sm": 12, "md": 6}),
            
            # Path
            ft.Column([
                ft.Text("Path", style=ft.TextThemeStyle.LABEL_LARGE, color=TOKENS['outline']),
                ft.Text(file_path, style=ft.TextThemeStyle.BODY_LARGE, selectable=True)
            ], col={"sm": 12, "md": 6}),
            
            # Size
            ft.Column([
                ft.Text("Size", style=ft.TextThemeStyle.LABEL_LARGE, color=TOKENS['outline']),
                ft.Text(file_size, style=ft.TextThemeStyle.BODY_LARGE)
            ], col={"sm": 12, "md": 6}),
            
            # Type
            ft.Column([
                ft.Text("Type", style=ft.TextThemeStyle.LABEL_LARGE, color=TOKENS['outline']),
                ft.Text(file_type, style=ft.TextThemeStyle.BODY_LARGE)
            ], col={"sm": 12, "md": 6}),
            
            # Modified
            ft.Column([
                ft.Text("Modified", style=ft.TextThemeStyle.LABEL_LARGE, color=TOKENS['outline']),
                ft.Text(modified, style=ft.TextThemeStyle.BODY_LARGE)
            ], col={"sm": 12, "md": 6}),
            
            # Created
            ft.Column([
                ft.Text("Created", style=ft.TextThemeStyle.LABEL_LARGE, color=TOKENS['outline']),
                ft.Text(created, style=ft.TextThemeStyle.BODY_LARGE)
            ], col={"sm": 12, "md": 6}),
            
            # Owner
            ft.Column([
                ft.Text("Owner", style=ft.TextThemeStyle.LABEL_LARGE, color=TOKENS['outline']),
                ft.Text(owner, style=ft.TextThemeStyle.BODY_LARGE)
            ], col={"sm": 12, "md": 6}),
            
            # Permissions
            ft.Column([
                ft.Text("Permissions", style=ft.TextThemeStyle.LABEL_LARGE, color=TOKENS['outline']),
                ft.Text(permissions, style=ft.TextThemeStyle.BODY_LARGE)
            ], col={"sm": 12, "md": 6}),
        ], spacing=12)
    
    def _create_action_buttons(self) -> ft.Control:
        """Create action buttons"""
        return ft.Row([
            create_enhanced_button(
                text="Preview",
                icon=ft.Icons.VISIBILITY,
                on_click=self._on_preview,
                width=150
            ),
            create_enhanced_button(
                text="Download",
                icon=ft.Icons.DOWNLOAD,
                on_click=self._on_download,
                width=150
            ),
            create_enhanced_button(
                text="Delete",
                icon=ft.Icons.DELETE,
                on_click=self._on_delete,
                width=150
            )
        ], spacing=12, alignment=ft.MainAxisAlignment.CENTER)
    
    def _create_metadata_section(self) -> ft.Control:
        """Create metadata section"""
        metadata = self.file_info.get("metadata", {})

        if not metadata:
            return ft.Container()

        metadata_items = [
            ft.ListTile(
                title=ft.Text(
                    key.replace("_", " ").title(),
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                ),
                subtitle=ft.Text(str(value), style=ft.TextThemeStyle.BODY_SMALL),
                dense=True,
            )
            for key, value in metadata.items()
        ]
        return ft.Column([
            ft.Text("Metadata", style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Card(
                content=ft.Container(
                    content=ft.Column(metadata_items, spacing=2),
                    padding=ft.padding.all(12)
                )
            )
        ], spacing=8)
    
    def _on_close(self, e):
        """Handle close action"""
        if self.on_close:
            self.on_close(e)
    
    def _on_preview(self, e):
        """Handle preview action"""
        if self.on_preview:
            self.on_preview(e)
        else:
            toast = create_toast_notification(
                message="Opening file preview",
                bgcolor=TOKENS['container']
            )
            toast.show(self.page)
    
    def _on_download(self, e):
        """Handle download action"""
        if self.on_download:
            self.on_download(e)
        else:
            toast = create_toast_notification(
                message="File download started",
                bgcolor=TOKENS['container']
            )
            toast.show(self.page)
    
    def _on_delete(self, e):
        """Handle delete action"""
        if self.on_delete:
            self.on_delete(e)
        else:
            from flet_server_gui.components.dialogs import create_confirmation_dialog
            file_name = self.file_info.get("name", "this file")
            dialog = create_confirmation_dialog(
                title="Delete File",
                message=f"Are you sure you want to delete '{file_name}'?",
                on_confirm=self._on_delete_confirm
            )
            dialog.show(self.page)
    
    def _on_delete_confirm(self, e):
        """Handle delete confirmation"""
        toast = create_toast_notification(
            message="File deleted successfully",
            bgcolor=TOKENS['surface_variant']
        )
        toast.show(self.page)


# Factory function
def create_file_details(file_info: Dict = None, **kwargs) -> FileDetails:
    """Create file details component"""
    return FileDetails(file_info=file_info, **kwargs)