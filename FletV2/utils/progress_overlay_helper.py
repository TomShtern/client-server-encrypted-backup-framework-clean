#!/usr/bin/env python3
"""
Progress Overlay Utilities for FletV2
Standardized progress indicators for async operations with automatic cleanup.
"""

import flet as ft
from typing import Optional, Union
from utils.debug_setup import get_logger

logger = get_logger(__name__)


class ProgressOverlay:
    """
    Context manager for progress overlays that automatically handles creation, 
    display, updating, and cleanup of progress indicators.
    
    Example:
        async with ProgressOverlay(page, "Downloading file...") as progress:
            await long_operation()
            progress.update_progress(0.5, "Processing...")
            await another_operation()
    """
    
    def __init__(
        self, 
        page: ft.Page, 
        message: str, 
        operation_type: str = "info",
        show_progress_value: bool = True
    ):
        """
        Initialize progress overlay.
        
        Args:
            page: Flet page instance
            message: Initial progress message
            operation_type: Type of operation ('info', 'error', 'success')
            show_progress_value: Whether to show progress ring with value
        """
        self.page = page
        self.message = message
        self.operation_type = operation_type
        self.show_progress_value = show_progress_value
        
        # Create UI components
        self.progress_ring = ft.ProgressRing(
            value=0.0 if show_progress_value else None, 
            width=24, 
            height=24
        )
        self.message_text = ft.Text(message, size=12)
        self.feedback_row = ft.Row([self.progress_ring, self.message_text], spacing=8)
        
        # Choose background color based on operation type
        bgcolor_map = {
            'info': ft.Colors.SURFACE,
            'error': ft.Colors.ERROR_CONTAINER,
            'success': ft.Colors.SURFACE,
            'warning': ft.Colors.WARNING_CONTAINER
        }
        
        self.progress_container = ft.Container(
            content=self.feedback_row,
            padding=ft.Padding(20, 10, 20, 10),
            bgcolor=bgcolor_map.get(operation_type, ft.Colors.SURFACE),
            border_radius=8,
            visible=False  # Start invisible
        )
        
    def __enter__(self):
        """Enter context manager - show progress overlay."""
        try:
            self.page.overlay.append(self.progress_container)
            self.progress_container.visible = True
            self.progress_container.update()
            logger.debug(f"Progress overlay shown: {self.message}")
        except Exception as e:
            logger.error(f"Failed to show progress overlay: {e}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - clean up progress overlay."""
        try:
            if self.progress_container in self.page.overlay:
                self.page.overlay.remove(self.progress_container)
                self.page.update()
                logger.debug(f"Progress overlay cleaned up: {self.message}")
        except Exception as e:
            logger.error(f"Failed to clean up progress overlay: {e}")
        return False  # Don't suppress exceptions
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self.__enter__()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        return self.__exit__(exc_type, exc_val, exc_tb)
    
    def update_progress(self, value: Optional[float] = None, message: Optional[str] = None):
        """
        Update progress indicator and message.
        
        Args:
            value: Progress value (0.0 to 1.0) or None to keep current
            message: New message or None to keep current
        """
        try:
            if value is not None and self.show_progress_value:
                self.progress_ring.value = value
                self.progress_ring.update()
            
            if message is not None:
                self.message_text.value = message
                self.message_text.update()
                
        except Exception as e:
            logger.error(f"Failed to update progress: {e}")
    
    def complete(self, final_message: Optional[str] = None):
        """
        Mark progress as complete.
        
        Args:
            final_message: Final message to show
        """
        try:
            if self.show_progress_value:
                self.progress_ring.value = 1.0
                self.progress_ring.update()
            
            if final_message:
                self.message_text.value = final_message
                self.message_text.update()
                
        except Exception as e:
            logger.error(f"Failed to complete progress: {e}")


def create_quick_progress_overlay(
    page: ft.Page,
    message: str,
    operation_type: str = "info"
) -> ft.Container:
    """
    Create a simple progress overlay for immediate use (non-context manager).
    
    Args:
        page: Flet page instance
        message: Progress message
        operation_type: Operation type for styling
    
    Returns:
        Container that can be manually added to page.overlay
        
    Example:
        progress = create_quick_progress_overlay(page, "Loading...")
        page.overlay.append(progress)
        progress.visible = True
        progress.update()
        # ... do work ...
        page.overlay.remove(progress)
        page.update()
    """
    progress_ring = ft.ProgressRing(width=24, height=24)
    feedback_row = ft.Row([progress_ring, ft.Text(message, size=12)], spacing=8)
    
    bgcolor_map = {
        'info': ft.Colors.SURFACE,
        'error': ft.Colors.ERROR_CONTAINER, 
        'success': ft.Colors.SURFACE,
        'warning': ft.Colors.WARNING_CONTAINER
    }
    
    return ft.Container(
        content=feedback_row,
        padding=ft.Padding(20, 10, 20, 10),
        bgcolor=bgcolor_map.get(operation_type, ft.Colors.SURFACE),
        border_radius=8,
        visible=False
    )