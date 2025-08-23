#!/usr/bin/env python3
"""
Enhanced Dialog Components
Custom Material Design 3 dialogs with advanced animations and interactions.
"""

import flet as ft
from typing import Optional, Callable, List, Union
import asyncio


class EnhancedAlertDialog(ft.AlertDialog):
    """Enhanced alert dialog with advanced animations and interactions"""
    
    def __init__(self,
                 title: Optional[ft.Control] = None,
                 content: Optional[ft.Control] = None,
                 actions: Optional[List[ft.Control]] = None,
                 on_dismiss: Optional[Callable] = None,
                 modal: bool = True,
                 animate_scale: int = 200,
                 animate_opacity: int = 150,
                 **kwargs):
        super().__init__(
            title=title,
            content=content,
            actions=actions,
            on_dismiss=on_dismiss,
            modal=modal,
            **kwargs
        )
        
        # Enhanced animation properties
        self.animate_scale = ft.Animation(animate_scale, ft.AnimationCurve.EASE_OUT)
        self.animate_opacity = ft.Animation(animate_opacity, ft.AnimationCurve.EASE_OUT)
        
        self.original_scale = ft.Scale(1)
        self.scale = ft.Scale(1)
        self.offset = ft.Offset(0, 0)
        self.animate_scale = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        self.animate_offset = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
    
    async def show_async(self, page: ft.Page):
        """Show dialog with entrance animation"""
        page.dialog = self
        self.open = True
        page.update()
        
        # Animate entrance
        self.scale = ft.Scale(1)
        self.opacity = 1
        await page.update_async()
    
    def show(self, page: ft.Page):
        """Show dialog with entrance animation (synchronous)"""
        page.dialog = self
        self.open = True
        page.update()
        
        # Animate entrance
        self.scale = ft.Scale(1)
        self.opacity = 1
        page.update()


class ConfirmationDialog(EnhancedAlertDialog):
    """Specialized confirmation dialog with yes/no buttons"""
    
    def __init__(self,
                 title: str,
                 message: str,
                 on_confirm: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None,
                 confirm_text: str = "Yes",
                 cancel_text: str = "No",
                 **kwargs):
        # Create actions
        actions = [
            ft.TextButton(cancel_text, on_click=lambda e: self._handle_cancel(e, on_cancel)),
            ft.FilledButton(confirm_text, on_click=lambda e: self._handle_confirm(e, on_confirm))
        ]
        
        super().__init__(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=actions,
            **kwargs
        )
        
        self.on_confirm_callback = on_confirm
        self.on_cancel_callback = on_cancel
    
    def _handle_confirm(self, e, callback):
        """Handle confirm button click"""
        if callback:
            callback(e)
        self.open = False
        self.page.update()
    
    def _handle_cancel(self, e, callback):
        """Handle cancel button click"""
        if callback:
            callback(e)
        self.open = False
        self.page.update()


class InputDialog(EnhancedAlertDialog):
    """Specialized input dialog with text field"""
    
    def __init__(self,
                 title: str,
                 label: str,
                 on_submit: Optional[Callable] = None,
                 on_cancel: Optional[Callable] = None,
                 submit_text: str = "Submit",
                 cancel_text: str = "Cancel",
                 multiline: bool = False,
                 **kwargs):
        # Create text field
        self.input_field = ft.TextField(
            label=label,
            multiline=multiline,
            min_lines=1 if not multiline else 3,
            max_lines=5 if multiline else 1
        )
        
        # Create actions
        actions = [
            ft.TextButton(cancel_text, on_click=lambda e: self._handle_cancel(e, on_cancel)),
            ft.FilledButton(submit_text, on_click=lambda e: self._handle_submit(e, on_submit))
        ]
        
        super().__init__(
            title=ft.Text(title),
            content=self.input_field,
            actions=actions,
            **kwargs
        )
        
        self.on_submit_callback = on_submit
        self.on_cancel_callback = on_cancel
    
    def _handle_submit(self, e, callback):
        """Handle submit button click"""
        if callback:
            callback(e, self.input_field.value)
        self.open = False
        self.page.update()
    
    def _handle_cancel(self, e, callback):
        """Handle cancel button click"""
        if callback:
            callback(e)
        self.open = False
        self.page.update()


class ProgressDialog(EnhancedAlertDialog):
    """Specialized progress dialog with progress indicator"""
    
    def __init__(self,
                 title: str,
                 message: str = "Please wait...",
                 **kwargs):
        # Create progress indicator
        self.progress_ring = ft.ProgressRing(width=24, height=24, stroke_width=3)
        
        # Create content
        content = ft.Column([
            ft.Row([
                self.progress_ring,
                ft.Text(message)
            ], spacing=12)
        ], spacing=16)
        
        super().__init__(
            title=ft.Text(title),
            content=content,
            modal=True,
            **kwargs
        )
        
        # Disable closing by clicking outside
        self.on_dismiss = None
    
    def update_message(self, message: str):
        """Update progress dialog message"""
        if self.content and len(self.content.controls) > 0:
            # Find text control and update it
            row = self.content.controls[0]
            if isinstance(row, ft.Row) and len(row.controls) > 1:
                text_control = row.controls[1]
                if isinstance(text_control, ft.Text):
                    text_control.value = message
                    self.page.update()


class ToastNotification(ft.SnackBar):
    """Enhanced toast notification with custom styling and animations"""
    
    def __init__(self,
                 message: str,
                 duration: int = 3000,
                 bgcolor: Optional[str] = None,
                 text_color: Optional[str] = None,
                 action_text: Optional[str] = None,
                 on_action: Optional[Callable] = None,
                 animate_duration: int = 200,
                 **kwargs):
        content = ft.Text(message, color=text_color)
        
        super().__init__(
            content=content,
            duration=duration,
            bgcolor=bgcolor,
            action=action_text,
            on_action=on_action,
            **kwargs
        )
        
        # Enhanced animation properties
        self.animate_offset = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        self.animate_opacity = ft.Animation(animate_duration, ft.AnimationCurve.EASE_OUT)
        
        # Position at bottom with offset for entrance
        self.offset = ft.Offset(0, 1)
    
    async def show_async(self, page: ft.Page):
        """Show toast notification with entrance animation"""
        page.snack_bar = self
        self.open = True
        page.update()
        
        # Animate entrance
        self.offset = ft.Offset(0, 0)
        await page.update_async()
    
    def show(self, page: ft.Page):
        """Show toast notification with entrance animation (synchronous)"""
        page.snack_bar = self
        self.open = True
        page.update()
        
        # Animate entrance
        self.offset = ft.Offset(0, 0)
        page.update()


# Factory functions for easy dialog creation
def create_confirmation_dialog(title: str,
                              message: str,
                              on_confirm: Optional[Callable] = None,
                              on_cancel: Optional[Callable] = None,
                              **kwargs) -> ConfirmationDialog:
    """Create a confirmation dialog"""
    return ConfirmationDialog(
        title=title,
        message=message,
        on_confirm=on_confirm,
        on_cancel=on_cancel,
        **kwargs
    )

def create_input_dialog(title: str,
                       label: str,
                       on_submit: Optional[Callable] = None,
                       on_cancel: Optional[Callable] = None,
                       **kwargs) -> InputDialog:
    """Create an input dialog"""
    return InputDialog(
        title=title,
        label=label,
        on_submit=on_submit,
        on_cancel=on_cancel,
        **kwargs
    )

def create_progress_dialog(title: str,
                          message: str = "Please wait...",
                          **kwargs) -> ProgressDialog:
    """Create a progress dialog"""
    return ProgressDialog(title=title, message=message, **kwargs)

def create_toast_notification(message: str,
                              duration: int = 3000,
                              bgcolor: Optional[str] = None,
                              **kwargs) -> ToastNotification:
    """Create a toast notification"""
    return ToastNotification(message=message, duration=duration, bgcolor=bgcolor, **kwargs)