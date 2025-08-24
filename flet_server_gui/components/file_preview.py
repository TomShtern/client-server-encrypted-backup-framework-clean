#!/usr/bin/env python3
"""
File Preview Component
Material Design 3 component for previewing file contents with enhanced UI.
"""

import flet as ft
from typing import Optional, Callable
import os
from flet_server_gui.components.enhanced_components import (
    EnhancedCard,
    create_enhanced_button,
    create_enhanced_icon_button
)
from flet_server_gui.components.dialogs import create_toast_notification


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
            ft.Column([
                ft.Text(file_name, style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Text(self.file_path, style=ft.TextThemeStyle.BODY_SMALL, color=ft.Colors.ON_SURFACE_VARIANT)
            ], spacing=2),
            ft.Container(expand=True),
            ft.Row([
                create_enhanced_icon_button(
                    icon=ft.Icons.DOWNLOAD,
                    tooltip="Download file",
                    on_click=self._on_download
                ),
                create_enhanced_icon_button(
                    icon=ft.Icons.DELETE,
                    tooltip="Delete file",
                    on_click=self._on_delete
                ),
                create_enhanced_icon_button(
                    icon=ft.Icons.CLOSE,
                    tooltip="Close preview",
                    on_click=self._on_close
                )
            ], spacing=4)
        ], spacing=12)
        
        # File content preview
        content_preview = self._create_content_preview(file_ext)
        
        # File info
        file_info = ft.Row([
            ft.Chip(label=ft.Text(f"Size: {self._get_file_size()}")),
            ft.Chip(label=ft.Text(f"Type: {self._get_file_type(file_ext)}")),
            ft.Chip(label=ft.Text(f"Modified: {self._get_file_modified()}"))
        ], spacing=8)
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                content_preview,
                ft.Divider(),
                file_info
            ], spacing=16),
            padding=ft.padding.all(20),
            width=600,
            height=500
        )
    
    def _get_file_icon(self, file_ext: str) -> ft.Icons:
        """Get appropriate icon for file type"""
        icon_map = {
            ".txt": ft.Icons.TEXT_SNIPPET,
            ".pdf": ft.Icons.PICTURE_AS_PDF,
            ".jpg": ft.Icons.IMAGE,
            ".png": ft.Icons.IMAGE,
            ".gif": ft.Icons.IMAGE,
            ".doc": ft.Icons.DESCRIPTION,
            ".docx": ft.Icons.DESCRIPTION,
            ".xls": ft.Icons.TABLE_CHART,
            ".xlsx": ft.Icons.TABLE_CHART,
            ".zip": ft.Icons.FOLDER_ZIP,
            ".rar": ft.Icons.FOLDER_ZIP,
            ".mp3": ft.Icons.AUDIOTRACK,
            ".mp4": ft.Icons.VIDEOCAM,
            ".avi": ft.Icons.VIDEOCAM,
        }
        return icon_map.get(file_ext, ft.Icons.DESCRIPTION)
    
    def _get_file_size(self) -> str:
        """Get formatted file size"""
        if not self.file_path or not os.path.exists(self.file_path):
            return "Unknown"
        
        try:
            size = os.path.getsize(self.file_path)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        except:
            return "Unknown"
    
    def _get_file_type(self, file_ext: str) -> str:
        """Get file type description"""
        type_map = {
            ".txt": "Text Document",
            ".pdf": "PDF Document",
            ".jpg": "JPEG Image",
            ".png": "PNG Image",
            ".gif": "GIF Image",
            ".doc": "Word Document",
            ".docx": "Word Document",
            ".xls": "Excel Spreadsheet",
            ".xlsx": "Excel Spreadsheet",
            ".zip": "ZIP Archive",
            ".rar": "RAR Archive",
            ".mp3": "Audio File",
            ".mp4": "Video File",
            ".avi": "Video File",
        }
        return type_map.get(file_ext, f"{file_ext.upper()[1:]} File")
    
    def _get_file_modified(self) -> str:
        """Get file modification date"""
        if not self.file_path or not os.path.exists(self.file_path):
            return "Unknown"
        
        try:
            import datetime
            mtime = os.path.getmtime(self.file_path)
            return datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
        except:
            return "Unknown"
    
    def _create_content_preview(self, file_ext: str) -> ft.Control:
        """Create appropriate content preview based on file type"""
        # For text files, show content in a scrollable text area
        if file_ext in [".txt", ".log", ".md", ".csv"]:
            return ft.Container(
                content=ft.Column([
                    ft.Text("File Content", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.Container(
                        content=ft.TextField(
                            value=self.file_content[:1000] + ("..." if len(self.file_content) > 1000 else ""),
                            read_only=True,
                            multiline=True,
                            min_lines=10,
                            max_lines=15,
                            text_size=12
                        ),
                        border=ft.border.all(1, ft.Colors.OUTLINE),
                        border_radius=4,
                        padding=8
                    )
                ], spacing=8),
                expand=True
            )
        
        # For image files, show a placeholder
        elif file_ext in [".jpg", ".png", ".gif"]:
            return ft.Container(
                content=ft.Column([
                    ft.Text("Image Preview", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.Container(
                        content=ft.Icon(ft.Icons.IMAGE, size=100, color=ft.Colors.ON_SURFACE_VARIANT),
                        alignment=ft.alignment.center,
                        expand=True
                    )
                ], spacing=8, expand=True),
                alignment=ft.alignment.center,
                expand=True
            )
        
        # For PDF files, show a placeholder
        elif file_ext == ".pdf":
            return ft.Container(
                content=ft.Column([
                    ft.Text("PDF Preview", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.Container(
                        content=ft.Icon(ft.Icons.PICTURE_AS_PDF, size=100, color=ft.Colors.ON_SURFACE_VARIANT),
                        alignment=ft.alignment.center,
                        expand=True
                    )
                ], spacing=8, expand=True),
                alignment=ft.alignment.center,
                expand=True
            )
        
        # For other files, show a generic preview
        else:
            return ft.Container(
                content=ft.Column([
                    ft.Text("File Preview", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(self._get_file_icon(file_ext), size=64, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text("No preview available for this file type", color=ft.Colors.ON_SURFACE_VARIANT)
                        ], 
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        alignment=ft.alignment.center,
                        expand=True
                    )
                ], spacing=8, expand=True),
                alignment=ft.alignment.center,
                expand=True
            )
    
    def _on_close(self, e):
        """Handle close action"""
        if self.on_close:
            self.on_close(e)
    
    def _on_download(self, e):
        """Handle download action"""
        if self.on_download:
            self.on_download(e)
        else:
            toast = create_toast_notification(
                message="File download started",
                bgcolor=ft.Colors.PRIMARY_CONTAINER
            )
            toast.show(self.page)
    
    def _on_delete(self, e):
        """Handle delete action"""
        if self.on_delete:
            self.on_delete(e)
        else:
            from flet_server_gui.components.dialogs import create_confirmation_dialog
            dialog = create_confirmation_dialog(
                title="Delete File",
                message=f"Are you sure you want to delete {os.path.basename(self.file_path) if self.file_path else 'this file'}?",
                on_confirm=self._on_delete_confirm
            )
            dialog.show(self.page)
    
    def _on_delete_confirm(self, e):
        """Handle delete confirmation"""
        toast = create_toast_notification(
            message="File deleted successfully",
            bgcolor=ft.Colors.SECONDARY_CONTAINER
        )
        toast.show(self.page)


# Factory function
def create_file_preview(file_path: str = "", file_content: str = "", **kwargs) -> FilePreview:
    """Create file preview component"""
    return FilePreview(file_path=file_path, file_content=file_content, **kwargs)