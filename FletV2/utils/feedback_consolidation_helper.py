#!/usr/bin/env python3
"""
Feedback Consolidation Utilities for FletV2
Standardized user feedback patterns to eliminate repeated feedback implementations.
"""

import flet as ft
from typing import Optional, Callable, Dict, Any
from utils.debug_setup import get_logger

logger = get_logger(__name__)


class FeedbackManager:
    """
    Centralized feedback management with standardized patterns.
    Replaces the repeated feedback container and message display patterns.
    """
    
    @staticmethod
    def create_feedback_row(
        message: str = "Ready",
        operation_type: str = "info",
        show_progress: bool = False,
        progress_value: Optional[float] = None
    ) -> ft.Row:
        """
        Create standardized feedback row with optional progress indicator.
        
        Args:
            message: Feedback message
            operation_type: Type ('info', 'success', 'warning', 'error')
            show_progress: Whether to show progress ring
            progress_value: Progress value (0.0-1.0) or None for indeterminate
        """
        # Icon mapping for different operation types
        icon_map = {
            'info': ft.Icons.INFO_OUTLINE,
            'success': ft.Icons.CHECK_CIRCLE_OUTLINE,
            'warning': ft.Icons.WARNING_AMBER_OUTLINED,
            'error': ft.Icons.ERROR_OUTLINE
        }
        
        # Color mapping for different operation types
        color_map = {
            'info': ft.Colors.BLUE,
            'success': ft.Colors.GREEN,
            'warning': ft.Colors.ORANGE,
            'error': ft.Colors.RED
        }
        
        controls = []
        
        # Add progress ring if requested
        if show_progress:
            progress_ring = ft.ProgressRing(
                value=progress_value,
                width=20,
                height=20,
                color=color_map.get(operation_type, ft.Colors.BLUE)
            )
            controls.append(progress_ring)
        else:
            # Add status icon
            icon = ft.Icon(
                icon_map.get(operation_type, ft.Icons.INFO_OUTLINE),
                size=20,
                color=color_map.get(operation_type, ft.Colors.BLUE)
            )
            controls.append(icon)
        
        # Add message text
        message_text = ft.Text(
            message,
            size=12,
            color=color_map.get(operation_type, ft.Colors.BLUE)
        )
        controls.append(message_text)
        
        return ft.Row(controls, spacing=8)
    
    @staticmethod
    def create_feedback_container(
        content: ft.Control,
        operation_type: str = "info",
        padding: Optional[ft.Padding] = None,
        visible: bool = True
    ) -> ft.Container:
        """
        Create standardized feedback container with consistent styling.
        
        Args:
            content: Content to display in container
            operation_type: Type for styling ('info', 'success', 'warning', 'error')  
            padding: Optional custom padding
            visible: Initial visibility
        """
        # Background color mapping
        bgcolor_map = {
            'info': ft.Colors.SURFACE,
            'success': ft.Colors.GREEN_50,
            'warning': ft.Colors.ORANGE_50,
            'error': ft.Colors.RED_50
        }
        
        # Border color mapping  
        border_color_map = {
            'info': ft.Colors.BLUE_200,
            'success': ft.Colors.GREEN_200,
            'warning': ft.Colors.ORANGE_200,
            'error': ft.Colors.RED_200
        }
        
        return ft.Container(
            content=content,
            padding=padding or ft.Padding(20, 10, 20, 10),
            bgcolor=bgcolor_map.get(operation_type, ft.Colors.SURFACE),
            border=ft.border.all(1, border_color_map.get(operation_type, ft.Colors.BLUE_200)),
            border_radius=8,
            visible=visible
        )
    
    @staticmethod
    def update_feedback_text(
        text_control: ft.Control,
        message: str,
        operation_type: str = "info",
        auto_update: bool = True
    ):
        """
        Update feedback text with consistent styling.
        
        Args:
            text_control: Text control to update
            message: New message
            operation_type: Type for styling
            auto_update: Whether to call update() automatically
        """
        color_map = {
            'info': ft.Colors.BLUE,
            'success': ft.Colors.GREEN,
            'warning': ft.Colors.ORANGE,
            'error': ft.Colors.RED
        }
        
        if hasattr(text_control, 'value'):
            text_control.value = message
        if hasattr(text_control, 'color'):
            text_control.color = color_map.get(operation_type, ft.Colors.BLUE)
        
        if auto_update:
            text_control.update()


class ActionFeedback:
    """
    Context manager for action feedback with automatic cleanup.
    Standardizes the repeated pattern of show feedback -> perform action -> update feedback.
    """
    
    def __init__(
        self,
        page: ft.Page,
        feedback_control: Optional[ft.Control] = None,
        initial_message: str = "Processing...",
        success_message: str = "Operation completed successfully",
        error_message: str = "Operation failed"
    ):
        self.page = page
        self.feedback_control = feedback_control
        self.initial_message = initial_message
        self.success_message = success_message
        self.error_message = error_message
        self.operation_successful = True
    
    def __enter__(self):
        """Start feedback display."""
        if self.feedback_control:
            FeedbackManager.update_feedback_text(
                self.feedback_control, 
                self.initial_message,
                "info"
            )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete feedback display."""
        if self.feedback_control:
            if exc_type is None and self.operation_successful:
                FeedbackManager.update_feedback_text(
                    self.feedback_control,
                    self.success_message,
                    "success"
                )
            else:
                error_msg = self.error_message
                if exc_val:
                    error_msg = f"{self.error_message}: {str(exc_val)}"
                FeedbackManager.update_feedback_text(
                    self.feedback_control,
                    error_msg,
                    "error"
                )
        return False  # Don't suppress exceptions
    
    def set_error(self, error_message: Optional[str] = None):
        """Mark operation as failed with optional custom message."""
        self.operation_successful = False
        if error_message:
            self.error_message = error_message
    
    def update_progress(self, message: str, operation_type: str = "info"):
        """Update progress message during operation."""
        if self.feedback_control:
            FeedbackManager.update_feedback_text(
                self.feedback_control,
                message,
                operation_type
            )


def create_action_feedback_control(
    initial_message: str = "Ready",
    operation_type: str = "info"
) -> ft.Text:
    """
    Create a standardized feedback text control for action feedback.
    
    Example:
        feedback_text = create_action_feedback_control("Ready")
        
        with ActionFeedback(page, feedback_text, "Deleting file...", "File deleted", "Delete failed"):
            delete_operation()
    """
    color_map = {
        'info': ft.Colors.BLUE,
        'success': ft.Colors.GREEN, 
        'warning': ft.Colors.ORANGE,
        'error': ft.Colors.RED
    }
    
    return ft.Text(
        initial_message,
        size=12,
        color=color_map.get(operation_type, ft.Colors.BLUE),
        weight=ft.FontWeight.W_400
    )


def batch_update_controls(*controls: ft.Control):
    """
    Batch update multiple controls for better performance.
    Replaces the repeated pattern of individual control.update() calls.
    
    Example:
        batch_update_controls(text1, text2, text3, container1)
    """
    for control in controls:
        if control and hasattr(control, 'update'):
            try:
                control.update()
            except Exception as e:
                logger.error(f"Failed to update control: {e}")


def show_operation_feedback(
    page: ft.Page,
    message: str,
    operation_type: str = "info",
    duration: int = 3000
):
    """
    Show temporary operation feedback using snackbar.
    Standardizes the repeated pattern of user feedback messages.
    
    Args:
        page: Flet page instance
        message: Message to display
        operation_type: Type for styling ('info', 'success', 'warning', 'error')
        duration: Display duration in milliseconds
    """
    color_map = {
        'info': ft.Colors.BLUE,
        'success': ft.Colors.GREEN,
        'warning': ft.Colors.ORANGE,
        'error': ft.Colors.RED
    }
    
    bgcolor_map = {
        'info': ft.Colors.BLUE_50,
        'success': ft.Colors.GREEN_50,
        'warning': ft.Colors.ORANGE_50,
        'error': ft.Colors.RED_50
    }
    
    page.snack_bar = ft.SnackBar(
        content=ft.Text(
            message,
            color=color_map.get(operation_type, ft.Colors.BLUE),
            weight=ft.FontWeight.W_500
        ),
        bgcolor=bgcolor_map.get(operation_type, ft.Colors.BLUE_50),
        duration=duration
    )
    page.snack_bar.open = True
    page.update()