#!/usr/bin/env python3
"""
File Preview Manager Component
Handles file preview generation and detailed file information display.
"""

import flet as ft
import base64
import os
from typing import List, Dict, Any, Optional
from ..utils.server_bridge import ServerBridge


class FilePreviewManager:
    """Manages file preview and detailed information display"""
    
    def __init__(self, server_bridge: ServerBridge, dialog_system, page: ft.Page):
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
                message=f"Error generating preview for '{filename}': {str(e)}"
            )
    
    async def _generate_file_preview(self, filename: str) -> Optional[ft.Control]:
        """Generate preview content based on file type"""
        try:
            # Get file extension
            file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
            
            # Get file data from server
            file_data = await self.server_bridge.get_file_content(filename)
            if not file_data:
                return None
            
            # Generate preview based on file type
            if file_extension in ['txt', 'log', 'md', 'py', 'js', 'css', 'html', 'json', 'xml']:
                return self._create_text_preview(file_data, file_extension)
            elif file_extension in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                return self._create_image_preview(file_data, filename)
            elif file_extension == 'pdf':
                return self._create_pdf_preview(file_data, filename)
            else:
                return self._create_file_info_preview(filename, file_data)
                
        except Exception as e:
            print(f"Error generating preview: {e}")
            return None
    
    def _create_text_preview(self, file_data: bytes, file_extension: str) -> ft.Control:
        """Create preview for text-based files"""
        try:
            # Decode text content
            text_content = file_data.decode('utf-8', errors='ignore')
            
            # Limit preview length
            max_chars = 5000
            if len(text_content) > max_chars:
                text_content = text_content[:max_chars] + "\n\n... (content truncated)"
            
            # Syntax highlighting based on extension (basic)
            if file_extension in ['py', 'js', 'css', 'html', 'json', 'xml']:
                return ft.Container(
                    content=ft.Column([
                        ft.Text(f"File Type: {file_extension.upper()}", weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.TextField(
                            value=text_content,
                            multiline=True,
                            min_lines=20,
                            max_lines=30,
                            read_only=True,
                            border_color=ft.Colors.OUTLINE
                        )
                    ]),
                    height=500,
                    width=700
                )
            else:
                return ft.Container(
                    content=ft.Column([
                        ft.Text("Text File Preview", weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.TextField(
                            value=text_content,
                            multiline=True,
                            min_lines=20,
                            max_lines=30,
                            read_only=True,
                            border_color=ft.Colors.OUTLINE
                        )
                    ]),
                    height=500,
                    width=700
                )
                
        except Exception as e:
            return ft.Text(f"Error displaying text preview: {str(e)}")
    
    def _create_image_preview(self, file_data: bytes, filename: str) -> ft.Control:
        """Create preview for image files"""
        try:
            # Convert image data to base64 for display
            base64_data = base64.b64encode(file_data).decode()
            file_extension = filename.split('.')[-1].lower()
            
            # Create image preview
            return ft.Container(
                content=ft.Column([
                    ft.Text(f"Image Preview: {filename}", weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    ft.Image(
                        src_base64=base64_data,
                        width=600,
                        height=400,
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=8
                    ),
                    ft.Text(f"Format: {file_extension.upper()}", size=12)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                height=500,
                width=700
            )
            
        except Exception as e:
            return ft.Text(f"Error displaying image preview: {str(e)}")
    
    def _create_pdf_preview(self, file_data: bytes, filename: str) -> ft.Control:
        """Create preview for PDF files"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.PICTURE_AS_PDF, size=64, color=ft.Colors.RED_400),
                ft.Text(f"PDF Document: {filename}", weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("PDF Preview not available in this interface.", size=14),
                ft.Text(f"File size: {len(file_data)} bytes", size=12),
                ft.ElevatedButton(
                    "Download to View",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._suggest_download(filename)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            height=300,
            width=500
        )
    
    def _create_file_info_preview(self, filename: str, file_data: bytes) -> ft.Control:
        """Create info preview for unsupported file types"""
        file_extension = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
        file_size = len(file_data)
        
        # Get appropriate icon based on file type
        icon_map = {
            'zip': ft.Icons.ARCHIVE,
            'rar': ft.Icons.ARCHIVE,
            '7z': ft.Icons.ARCHIVE,
            'mp3': ft.Icons.AUDIO_FILE,
            'wav': ft.Icons.AUDIO_FILE,
            'mp4': ft.Icons.VIDEO_FILE,
            'avi': ft.Icons.VIDEO_FILE,
            'doc': ft.Icons.DESCRIPTION,
            'docx': ft.Icons.DESCRIPTION,
            'xls': ft.Icons.TABLE_CHART,
            'xlsx': ft.Icons.TABLE_CHART,
        }
        
        icon = icon_map.get(file_extension, ft.Icons.FILE_PRESENT)
        
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=64, color=ft.Colors.BLUE_400),
                ft.Text(filename, weight=ft.FontWeight.BOLD, size=16),
                ft.Divider(),
                ft.Text(f"File Type: {file_extension.upper()}", size=14),
                ft.Text(f"Size: {self._format_file_size(file_size)}", size=14),
                ft.Divider(),
                ft.Text("Preview not available for this file type.", size=12),
                ft.ElevatedButton(
                    "Download File",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._suggest_download(filename)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            height=300,
            width=500
        )
    
    def _create_no_preview_content(self, filename: str) -> ft.Control:
        """Create content when preview cannot be generated"""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=64, color=ft.Colors.ORANGE_400),
                ft.Text("Preview Unavailable", weight=ft.FontWeight.BOLD, size=16),
                ft.Divider(),
                ft.Text(f"Could not generate preview for '{filename}'", size=14),
                ft.Text("The file may be corrupted or in an unsupported format.", size=12),
                ft.ElevatedButton(
                    "Try Download",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: self._suggest_download(filename)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            height=250,
            width=400
        )
    
    def _suggest_download(self, filename: str):
        """Suggest downloading the file"""
        self._close_dialog()
        # This would typically trigger the download action
        # For now, just close the dialog
    
    def _format_file_size(self, size: int) -> str:
        """Format file size to human-readable format"""
        if not size or size == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def clear_preview_cache(self) -> None:
        """Clear the preview cache"""
        self.preview_cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the preview cache"""
        return {
            'cached_files': len(self.preview_cache),
            'cache_keys': list(self.preview_cache.keys())
        }
    
    def _close_dialog(self):
        """Close the current dialog"""
        if self.dialog_system and hasattr(self.dialog_system, 'current_dialog'):
            if self.dialog_system.current_dialog:
                self.dialog_system.current_dialog.open = False
                self.page.update()