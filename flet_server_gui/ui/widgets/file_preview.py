#!/usr/bin/env python3
"""
UI Widgets - File Preview
Purpose: File preview component with enhanced UI and actions
Logic: File preview generation and detailed file information display
UI: Material Design 3 component for previewing file contents
"""

import flet as ft
import base64
import os
from typing import Optional, Callable, List, Dict, Any
from ...components.enhanced_components import (
    EnhancedCard
)
from flet_server_gui.core.theme_compatibility import TOKENS
from ..dialogs import ToastManager


class FilePreview(EnhancedCard):
    """File preview component with enhanced UI and actions"""
    
    def __init__(self, 
                 file_path: str = "",
                 file_content: str = "",
                 on_close: Optional[Callable] = None,
                 on_download: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None,
                 animate_duration: int = 200,
                 **kwargs):
        self.file_path = file_path
        self.file_content = file_content
        self.on_close = on_close
        self.on_download = on_download
        self.on_delete = on_delete
        
        # Create the main content
        content = self._build_content()
        
        super().__init__(
            content=content,
            animate_duration=animate_duration,
            **kwargs
        )
    
    def _build_content(self) -> ft.Control:
        """Build the file preview content"""
        # Extract file information
        file_name = os.path.basename(self.file_path) if self.file_path else "Untitled"
        file_ext = os.path.splitext(file_name)[1].lower() if self.file_path else ""
        
        # Header with file info and controls
        header = ft.Row([
            ft.Icon(ft.Icons.DESCRIPTION, size=24),
            ft.Text(file_name, weight=ft.FontWeight.BOLD, size=16, expand=True),
            ft.IconButton(
                icon=ft.Icons.CLOSE,
                tooltip="Close Preview",
                on_click=self._on_close_click
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # File details
        file_size = self._get_file_size()
        file_info = ft.Text(f"Size: {file_size} | Type: {file_ext.upper() if file_ext else 'Unknown'}", size=12, color=TOKENS['outline'])
        
        # Content preview
        if self.file_content:
            # For text files, show content in a scrollable text area
            if file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv']:
                content_preview = ft.Container(
                    content=ft.TextField(
                        value=self.file_content,
                        read_only=True,
                        multiline=True,
                        expand=True,
                        border=ft.InputBorder.NONE
                    ),
                    expand=True,
                    padding=ft.padding.all(12)
                )
            # For image files, show a placeholder
            elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                content_preview = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.IMAGE, size=64, color=TOKENS['outline']),
                        ft.Text("Image Preview", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text("Image previews are not implemented in this demo", size=12, color=TOKENS['outline'])
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
            # For other files, show a generic preview
            else:
                content_preview = ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.DESCRIPTION, size=64, color=TOKENS['outline']),
                        ft.Text("File Preview", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text("Preview not available for this file type", size=12, color=TOKENS['outline']),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
        else:
            content_preview = ft.Container(
                content=ft.Text("No content available", size=14, color=TOKENS['outline']),
                expand=True,
                alignment=ft.alignment.center
            )
        
        # Action buttons
        action_buttons = ft.Row([
            ft.ElevatedButton(
                "Download",
                icon=ft.Icons.DOWNLOAD,
                on_click=self._on_download_click,
                style=ft.ButtonStyle(
                    bgcolor=TOKENS['primary'],
                    color=TOKENS['on_primary']
                )
            ),
            ft.OutlinedButton(
                "Delete",
                icon=ft.Icons.DELETE,
                on_click=self._on_delete_click,
                style=ft.ButtonStyle(
                    color=TOKENS['error']
                )
            )
        ], alignment=ft.MainAxisAlignment.END)
        
        # Main layout
        preview_layout = ft.Column([
            header,
            ft.Divider(),
            file_info,
            ft.Divider(),
            content_preview,
            ft.Divider(),
            action_buttons
        ], spacing=12, expand=True)
        
        return ft.Container(
            content=preview_layout,
            padding=ft.padding.all(16),
            expand=True
        )
    
    def _get_file_size(self) -> str:
        """Get formatted file size"""
        try:
            if self.file_path and os.path.exists(self.file_path):
                size = os.path.getsize(self.file_path)
            else:
                # Estimate from content
                size = len(self.file_content.encode('utf-8'))
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except Exception:
            return "Unknown"
    
    def _on_download_click(self, e):
        """Handle download button click"""
        if self.on_download:
            try:
                self.on_download(self.file_path)
            except Exception as ex:
                print(f"Error downloading file: {ex}")
    
    def _on_delete_click(self, e):
        """Handle delete button click"""
        if self.on_delete:
            try:
                self.on_delete(self.file_path)
            except Exception as ex:
                print(f"Error deleting file: {ex}")
    
    def _on_close_click(self, e):
        """Handle close button click"""
        if self.on_close:
            try:
                self.on_close()
            except Exception as ex:
                print(f"Error closing preview: {ex}")


class FilePreviewManager:
    """Manages file preview and detailed information display"""
    
    def __init__(self, server_bridge, dialog_system, page: ft.Page):
        self.server_bridge = server_bridge
        self.dialog_system = dialog_system
        self.page = page
        
        # Preview cache for performance
        self.preview_cache = {}
    
    def create_preview_area(self) -> ft.Control:
        """Create a preview area for file previews"""
        return ft.Container(
            content=ft.Text("Select a file to preview", size=14, color=TOKENS['outline']),
            alignment=ft.alignment.center,
            expand=True,
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=ft.border_radius.all(8)
        )
    
    async def show_file_preview(self, filename: str) -> None:
        """Show file preview in a dialog"""
        try:
            # Check cache first
            if filename in self.preview_cache:
                preview_content = self.preview_cache[filename]
            else:
                # Generate new preview
                preview_content = await self._generate_file_preview(filename)
                if preview_content:
                    self.preview_cache[filename] = preview_content
            
            if not preview_content:
                preview_content = self._create_no_preview_content(filename)
            
            # Show preview dialog
            self.dialog_system.show_custom_dialog(
                title=f"Preview: {filename}",
                content=preview_content,
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self._close_dialog())
                ]
            )
            
        except Exception as e:
            self.dialog_system.show_error_dialog(
                title="Preview Error",
                message=f"Failed to preview file '{filename}': {str(e)}"
            )
    
    async def _generate_file_preview(self, filename: str) -> Optional[ft.Control]:
        """Generate file preview content"""
        try:
            # Get file content from server
            file_content = await self.server_bridge.get_file_content(filename)

            if not file_content:
                return None

            return FilePreview(
                file_path=filename,
                file_content=file_content,
                on_close=self._close_dialog,
                on_download=self._download_file,
                on_delete=self._delete_file,
            )
        except Exception as e:
            print(f"Error generating preview for {filename}: {e}")
            return None
    
    def _create_no_preview_content(self, filename: str) -> ft.Control:
        """Create content for files that cannot be previewed"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.VISIBILITY_OFF, size=48, color=TOKENS['outline']),
                ft.Text("Preview Not Available", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"File: {filename}", size=14),
                ft.Text("This file type cannot be previewed directly.", size=12, color=TOKENS['outline']),
                ft.Container(height=16),
                ft.Row([
                    ft.ElevatedButton(
                        text="Download File",
                        icon=ft.Icons.DOWNLOAD,
                        on_click=lambda e: self._download_file(filename)
                    )
                ], alignment=ft.MainAxisAlignment.CENTER)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def _close_dialog(self, e=None):
        """Close the preview dialog"""
        self.dialog_system.close_dialog()
    
    def _download_file(self, filename: str):
        """Download the file"""
        try:
            # In a real implementation, this would trigger the actual download
            print(f"Downloading file: {filename}")
            ToastManager(self.page).show_info(f"Downloading {filename}...")
        except Exception as e:
            ToastManager(self.page).show_error(f"Download failed: {str(e)}")
    
    def _delete_file(self, filename: str):
        """Delete the file"""
        try:
            # In a real implementation, this would trigger the actual deletion
            print(f"Deleting file: {filename}")
            ToastManager(self.page).show_info(f"Deleting {filename}...")
        except Exception as e:
            ToastManager(self.page).show_error(f"Deletion failed: {str(e)}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get preview cache information"""
        return {
            'cached_files': len(self.preview_cache),
            'cache_size': sum(len(str(preview)) for preview in self.preview_cache.values())
        }
    
    def clear_preview_cache(self):
        """Clear the preview cache"""
        self.preview_cache.clear()
        print("Preview cache cleared")


# Factory functions for easy component creation
def create_file_preview(file_path: str = "",
                       file_content: str = "",
                       on_close: Optional[Callable] = None,
                       on_download: Optional[Callable] = None,
                       on_delete: Optional[Callable] = None,
                       **kwargs) -> FilePreview:
    """Create a file preview component"""
    return FilePreview(
        file_path=file_path,
        file_content=file_content,
        on_close=on_close,
        on_download=on_download,
        on_delete=on_delete,
        **kwargs
    )


def create_file_preview_manager(server_bridge, dialog_system, page: ft.Page) -> FilePreviewManager:
    """Create a file preview manager"""
    return FilePreviewManager(server_bridge, dialog_system, page)