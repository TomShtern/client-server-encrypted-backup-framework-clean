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
        
        # Header with file info and actions
        header = ft.Row([
            ft.Icon(self._get_file_icon(file_ext), size=24),
            ft.Text(file_name, style=ft.TextThemeStyle.TITLE_MEDIUM, expand=True),
            ft.Row([
                create_enhanced_icon_button(
                    icon=ft.Icons.DOWNLOAD,
                    tooltip="Download File",
                    on_click=self._on_download_click,
                    size=20
                ) if self.on_download else ft.Container(),
                create_enhanced_icon_button(
                    icon=ft.Icons.DELETE,
                    tooltip="Delete File",
                    on_click=self._on_delete_click,
                    size=20
                ) if self.on_delete else ft.Container(),
                create_enhanced_icon_button(
                    icon=ft.Icons.CLOSE,
                    tooltip="Close Preview",
                    on_click=self._on_close_click,
                    size=20
                ) if self.on_close else ft.Container(),
            ], spacing=0)
        ], spacing=12)
        
        # Preview content area
        if self.file_content:
            # Determine content type and create appropriate preview
            if self._is_text_file(file_ext):
                preview_content = self._create_text_preview()
            elif self._is_image_file(file_ext):
                preview_content = self._create_image_preview()
            else:
                preview_content = self._create_binary_preview()
        else:
            preview_content = ft.Text(
                "No preview available for this file type.",
                italic=True,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
        
        # File info
        file_size = self._get_file_size()
        file_info = ft.Row([
            ft.Text(f"Size: {file_size}", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Text(f"Type: {file_ext.upper() if file_ext else 'Unknown'}", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
        ], spacing=16)
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                ft.Container(content=preview_content, expand=True),
                ft.Divider(),
                file_info
            ], spacing=8, expand=True),
            padding=16,
            expand=True
        )
    
    def _get_file_icon(self, file_ext: str) -> str:
        """Get appropriate icon for file type"""
        if file_ext in ['.txt', '.md', '.log', '.csv']:
            return ft.Icons.DESCRIPTION
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            return ft.Icons.IMAGE
        elif file_ext in ['.pdf']:
            return ft.Icons.PICTURE_AS_PDF
        elif file_ext in ['.doc', '.docx']:
            return ft.Icons.DESCRIPTION
        elif file_ext in ['.xls', '.xlsx']:
            return ft.Icons.TABLE_CHART
        elif file_ext in ['.zip', '.rar', '.7z']:
            return ft.Icons.FOLDER_ZIP
        else:
            return ft.Icons.INSERT_DRIVE_FILE
    
    def _is_text_file(self, file_ext: str) -> bool:
        """Check if file is a text file"""
        text_extensions = ['.txt', '.md', '.log', '.csv', '.json', '.xml', '.html', '.css', '.js', '.py', '.java', '.cpp', '.h']
        return file_ext in text_extensions
    
    def _is_image_file(self, file_ext: str) -> bool:
        """Check if file is an image file"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return file_ext in image_extensions
    
    def _create_text_preview(self) -> ft.Control:
        """Create text file preview"""
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    self.file_content[:1000],  # Limit preview size
                    style=ft.TextThemeStyle.BODY_MEDIUM,
                    selectable=True,
                    overflow=ft.TextOverflow.ELLIPSIS
                ),
                ft.Text(
                    "... (preview truncated)" if len(self.file_content) > 1000 else "",
                    italic=True,
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ], spacing=8),
            padding=8,
            border_radius=4,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            expand=True
        )
    
    def _create_image_preview(self) -> ft.Control:
        """Create image file preview"""
        try:
            # For now, show a placeholder - in a real implementation this would show the actual image
            return ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.IMAGE, size=64, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text("Image Preview", size=14, weight=ft.FontWeight.BOLD),
                    ft.Text("Image preview would be displayed here", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                ], 
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8),
                alignment=ft.alignment.center,
                expand=True
            )
        except Exception:
            return self._create_binary_preview()
    
    def _create_binary_preview(self) -> ft.Control:
        """Create binary file preview"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INSERT_DRIVE_FILE, size=64, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text("Binary File", size=14, weight=ft.FontWeight.BOLD),
                ft.Text("Binary file content cannot be previewed", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8),
            alignment=ft.alignment.center,
            expand=True
        )
    
    def _get_file_size(self) -> str:
        """Get formatted file size"""
        try:
            if self.file_path and os.path.exists(self.file_path):
                size = os.path.getsize(self.file_path)
                for unit in ['B', 'KB', 'MB', 'GB']:
                    if size < 1024.0:
                        return f"{size:.1f} {unit}"
                    size /= 1024.0
                return f"{size:.1f} TB"
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
            
            # Create preview component
            preview = FilePreview(
                file_path=filename,
                file_content=file_content,
                on_close=self._close_dialog,
                on_download=self._download_file,
                on_delete=self._delete_file
            )
            
            return preview
            
        except Exception as e:
            print(f"Error generating preview for {filename}: {e}")
            return None
    
    def _create_no_preview_content(self, filename: str) -> ft.Control:
        """Create content for files that cannot be previewed"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.VISIBILITY_OFF, size=48, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text("Preview Not Available", size=16, weight=ft.FontWeight.BOLD),
                ft.Text(f"File: {filename}", size=14),
                ft.Text("This file type cannot be previewed directly.", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Container(height=16),
                ft.Row([
                    create_enhanced_button(
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
            create_toast_notification(self.page, f"Downloading {filename}...", "info")
        except Exception as e:
            create_toast_notification(self.page, f"Download failed: {str(e)}", "error")
    
    def _delete_file(self, filename: str):
        """Delete the file"""
        try:
            # In a real implementation, this would trigger the actual deletion
            print(f"Deleting file: {filename}")
            create_toast_notification(self.page, f"Deleting {filename}...", "info")
        except Exception as e:
            create_toast_notification(self.page, f"Deletion failed: {str(e)}", "error")
    
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