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
from .cards import Card
from flet_server_gui.managers.theme_manager import TOKENS
from flet_server_gui.managers.toast_manager import ToastManager


class FilePreview(Card):
    """File preview component with enhanced UI and actions"""
    
    def __init__(self, 
                 file_path: str = "",
                 file_content: str = "",
                 on_close: Optional[Callable] = None,
                 on_download: Optional[Callable] = None,
                 on_delete: Optional[Callable] = None,
                 animate_duration: int = 200,
                 **kwargs):
        # Initialize parent Card with appropriate parameters
        super().__init__(**kwargs)
        self.file_path = file_path
        self.file_content = file_content
        self.on_close = on_close
        self.on_download = on_download
        self.on_delete = on_delete
        self.animate_duration = animate_duration

def create_file_preview(
    file_path: str,
    file_content: str = "",
    on_close: Optional[Callable] = None,
    on_download: Optional[Callable] = None,
    on_delete: Optional[Callable] = None
) -> FilePreview:
    """Create a file preview component"""
    return FilePreview(
        file_path=file_path,
        file_content=file_content,
        on_close=on_close,
        on_download=on_download,
        on_delete=on_delete
    )


class FilePreviewManager:
    """Manager for handling multiple file previews"""
    
    def __init__(self):
        self.previews: Dict[str, FilePreview] = {}
    
    def add_preview(self, preview_id: str, preview: FilePreview):
        """Add a file preview to the manager"""
        self.previews[preview_id] = preview
    
    def remove_preview(self, preview_id: str):
        """Remove a file preview from the manager"""
        if preview_id in self.previews:
            del self.previews[preview_id]
    
    def get_preview(self, preview_id: str) -> Optional[FilePreview]:
        """Get a file preview by ID"""
        return self.previews.get(preview_id)

def create_file_preview_manager() -> FilePreviewManager:
    """Create a file preview manager"""
    return FilePreviewManager()