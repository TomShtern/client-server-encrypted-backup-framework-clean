#!/usr/bin/env python3
"""
Progress Indicator Utilities for FletV2
Provides consistent progress feedback for async operations.
"""

import flet as ft
from utils.debug_setup import get_logger

logger = get_logger(__name__)


class ProgressIndicator:
    """Manages progress indicators for async operations."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.progress_ring = None
        self.progress_bar = None
        self.status_text = None
    
    def show_progress_ring(self, message: str = "Processing..."):
        """Show a progress ring with optional message."""
        try:
            # Create progress ring dialog
            self.progress_ring = ft.AlertDialog(
                content=ft.Column([
                    ft.Row([
                        ft.ProgressRing(width=24, height=24),
                        ft.Text(message, size=16)
                    ], spacing=15, alignment=ft.MainAxisAlignment.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                modal=True
            )
            
            self.page.dialog = self.progress_ring
            self.progress_ring.open = True
            self.page.update()
            
            logger.info(f"Progress ring shown with message: {message}")
        except Exception as e:
            logger.error(f"Failed to show progress ring: {e}")
    
    def hide_progress_ring(self):
        """Hide the progress ring."""
        try:
            if self.progress_ring and self.progress_ring.open:
                self.progress_ring.open = False
                self.page.update()
                logger.info("Progress ring hidden")
        except Exception as e:
            logger.error(f"Failed to hide progress ring: {e}")
    
    def show_progress_bar(self, message: str = "Processing...", initial_value: float = 0.0):
        """Show a progress bar with optional message."""
        try:
            # Create progress bar dialog
            self.status_text = ft.Text(message, size=14, text_align=ft.TextAlign.CENTER)
            self.progress_bar = ft.ProgressBar(value=initial_value, width=300)
            
            self.progress_bar_dialog = ft.AlertDialog(
                content=ft.Column([
                    self.status_text,
                    self.progress_bar,
                    ft.Text(f"{int(initial_value * 100)}%", size=12, text_align=ft.TextAlign.CENTER, ref=ft.Ref[ft.Text]())
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                modal=True
            )
            
            self.page.dialog = self.progress_bar_dialog
            self.progress_bar_dialog.open = True
            self.page.update()
            
            logger.info(f"Progress bar shown with message: {message}")
        except Exception as e:
            logger.error(f"Failed to show progress bar: {e}")
    
    def update_progress_bar(self, value: float, message: str = None):
        """Update the progress bar value and optional message."""
        try:
            if self.progress_bar:
                self.progress_bar.value = max(0.0, min(1.0, value))
                
                # Update percentage text
                if len(self.progress_bar_dialog.content.controls) > 2:
                    percentage_text = self.progress_bar_dialog.content.controls[2]
                    percentage_text.value = f"{int(value * 100)}%"
                
                # Update message if provided
                if message and self.status_text:
                    self.status_text.value = message
                
                self.page.update()
        except Exception as e:
            logger.error(f"Failed to update progress bar: {e}")
    
    def hide_progress_bar(self):
        """Hide the progress bar."""
        try:
            if self.progress_bar_dialog and self.progress_bar_dialog.open:
                self.progress_bar_dialog.open = False
                self.page.update()
                logger.info("Progress bar hidden")
        except Exception as e:
            logger.error(f"Failed to hide progress bar: {e}")
    
    def show_snack_progress(self, message: str = "Processing..."):
        """Show progress in a snackbar."""
        try:
            # Create snackbar with progress
            self.snack_progress = ft.SnackBar(
                content=ft.Row([
                    ft.ProgressRing(width=16, height=16, stroke_width=2),
                    ft.Text(message, size=14)
                ], spacing=10),
                bgcolor=ft.Colors.BLUE,
                duration=0  # Keep open until explicitly closed
            )
            
            self.page.snack_bar = self.snack_progress
            self.snack_progress.open = True
            self.page.update()
            
            logger.info(f"Snackbar progress shown with message: {message}")
        except Exception as e:
            logger.error(f"Failed to show snackbar progress: {e}")
    
    def hide_snack_progress(self):
        """Hide the snackbar progress."""
        try:
            if self.snack_progress and self.snack_progress.open:
                self.snack_progress.open = False
                self.page.update()
                logger.info("Snackbar progress hidden")
        except Exception as e:
            logger.error(f"Failed to hide snackbar progress: {e}")


def show_async_operation_feedback(page: ft.Page, operation_name: str):
    """
    Show consistent feedback for async operations.
    
    Args:
        page: Flet page instance
        operation_name: Name of the operation being performed
    """
    try:
        # Show progress indicator
        progress = ProgressIndicator(page)
        progress.show_progress_ring(f"{operation_name}...")
        
        # Store progress indicator in page for later access
        page.progress_indicator = progress
        
        logger.info(f"Started async operation feedback for: {operation_name}")
    except Exception as e:
        logger.error(f"Failed to show async operation feedback: {e}")


def hide_async_operation_feedback(page: ft.Page):
    """
    Hide async operation feedback.
    
    Args:
        page: Flet page instance
    """
    try:
        # Hide progress indicator
        if hasattr(page, 'progress_indicator') and page.progress_indicator:
            page.progress_indicator.hide_progress_ring()
            page.progress_indicator = None
            
        logger.info("Hidden async operation feedback")
    except Exception as e:
        logger.error(f"Failed to hide async operation feedback: {e}")


def show_operation_success(page: ft.Page, operation_name: str, details: str = ""):
    """
    Show success feedback for completed operations.
    
    Args:
        page: Flet page instance
        operation_name: Name of the completed operation
        details: Additional details about the operation
    """
    try:
        message = f"{operation_name} completed successfully"
        if details:
            message += f": {details}"
            
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()
        
        logger.info(f"Operation success shown: {message}")
    except Exception as e:
        logger.error(f"Failed to show operation success: {e}")


def show_operation_error(page: ft.Page, operation_name: str, error: str = ""):
    """
    Show error feedback for failed operations.
    
    Args:
        page: Flet page instance
        operation_name: Name of the failed operation
        error: Error details
    """
    try:
        message = f"{operation_name} failed"
        if error:
            message += f": {error}"
            
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED
        )
        page.snack_bar.open = True
        page.update()
        
        logger.error(f"Operation error shown: {message}")
    except Exception as e:
        logger.error(f"Failed to show operation error: {e}")