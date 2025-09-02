#!/usr/bin/env python3
"""
Dialog Components - Flet-style implementation

Purpose: Provide dialog components following Flet's best practices
Logic: Inherit from Flet's native AlertDialog control with added functionality
UI: Material Design 3 styled dialogs with enhanced features
"""

import flet as ft
from typing import Optional, List, Callable, Union
import asyncio
from flet_server_gui.managers.theme_manager import TOKENS


class Dialog(ft.AlertDialog):
    """Dialog with additional features"""
    
    def __init__(
        self,
        title: str,
        content: Union[str, ft.Control, List[ft.Control]],
        dialog_type: str = "info",  # info, warning, error, success, confirmation, input, progress
        size: str = "medium",  # small, medium, large, xlarge
        show_close_button: bool = True,
        show_confirm_button: bool = False,
        confirm_text: str = "OK",
        cancel_text: str = "Cancel",
        on_confirm: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        **kwargs
    ):
        self.dialog_type = dialog_type
        self.size = size
        self.show_close_button = show_close_button
        self.show_confirm_button = show_confirm_button
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
        self.on_close = on_close
        
        # Create content
        dialog_content = self._create_content(content)
        
        # Create actions
        actions = self._create_actions()
        
        # Set size-based width
        width = self._get_width()
        
        # Initialize parent class
        super().__init__(
            modal=True,
            title=ft.Text(title, size=16),
            content=dialog_content,
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=28),
            bgcolor=TOKENS['surface'],
            surface_tint_color=TOKENS['primary'],
            width=width,
            **kwargs
        )
    
    def _get_width(self) -> int:
        """Get dialog width based on size"""
        size_widths = {
            "small": 400,
            "medium": 600,
            "large": 800,
            "xlarge": 1000
        }
        return size_widths.get(self.size, 600)
    
    def _create_content(self, content: Union[str, ft.Control, List[ft.Control]]) -> ft.Control:
        """Create dialog content"""
        if isinstance(content, str):
            return ft.Text(content)
        elif isinstance(content, list):
            return ft.Column(content, spacing=16)
        else:
            return content
    
    def _create_actions(self) -> List[ft.Control]:
        """Create dialog action buttons"""
        actions = []
        
        # Cancel button (for confirmation dialogs)
        if self.dialog_type == "confirmation" or not self.show_confirm_button:
            actions.append(
                ft.TextButton(
                    self.cancel_text,
                    on_click=self._on_cancel
                )
            )
        
        # Close button
        if self.show_close_button and self.dialog_type != "confirmation":
            actions.append(
                ft.TextButton(
                    self.confirm_text if self.show_confirm_button else "Close",
                    on_click=self._on_close
                )
            )
        
        # Confirm button (for confirmation dialogs)
        if self.dialog_type == "confirmation":
            actions.append(
                ft.ElevatedButton(
                    self.confirm_text,
                    on_click=self._on_confirm
                )
            )
            
        return actions
    
    def _on_confirm(self, e):
        """Handle confirm action"""
        if self.on_confirm:
            self.on_confirm()
        self.open = False
    
    def _on_cancel(self, e):
        """Handle cancel action"""
        if self.on_cancel:
            self.on_cancel()
        self.open = False
    
    def _on_close(self, e):
        """Handle close action"""
        if self.on_close:
            self.on_close()
        self.open = False


class AlertDialog:
    """Alert dialog with simplified interface"""
    
    @staticmethod
    def show_info_dialog(page: ft.Page, title: str, message: str, on_close: Optional[Callable] = None):
        """Show info dialog"""
        dialog = Dialog(
            title=title,
            content=message,
            dialog_type="info",
            on_close=on_close
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    @staticmethod
    def show_success_dialog(page: ft.Page, title: str, message: str, on_close: Optional[Callable] = None):
        """Show success dialog"""
        dialog = Dialog(
            title=title,
            content=message,
            dialog_type="success",
            on_close=on_close
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    @staticmethod
    def show_warning_dialog(page: ft.Page, title: str, message: str, on_close: Optional[Callable] = None):
        """Show warning dialog"""
        dialog = Dialog(
            title=title,
            content=message,
            dialog_type="warning",
            on_close=on_close
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    @staticmethod
    def show_error_dialog(page: ft.Page, title: str, message: str, on_close: Optional[Callable] = None):
        """Show error dialog"""
        dialog = Dialog(
            title=title,
            content=message,
            dialog_type="error",
            on_close=on_close
        )
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    @staticmethod
    def show_confirmation_dialog(
        page: ft.Page, 
        title: str, 
        message: str, 
        on_confirm: Callable, 
        on_cancel: Optional[Callable] = None,
        confirm_text: str = "Yes",
        cancel_text: str = "No"
    ):
        """Show confirmation dialog"""
        dialog = Dialog(
            title=title,
            content=message,
            dialog_type="confirmation",
            confirm_text=confirm_text,
            cancel_text=cancel_text,
            on_confirm=on_confirm,
            on_cancel=on_cancel
        )
        page.dialog = dialog
        dialog.open = True
        page.update()


class ConfirmDialog:
    """Specialized confirmation dialog with customizable options"""
    
    @staticmethod
    async def show_with_options(
        page: ft.Page,
        title: str,
        message: str,
        options: List[str],
        on_select: Callable,
        cancel_text: str = "Cancel"
    ):
        """Show confirmation dialog with multiple options"""
        selected_option = asyncio.Future()
        
        def create_option_handler(option):
            def handler():
                selected_option.set_result(option)
                if on_select:
                    on_select(option)
            return handler
        
        # Create option buttons
        actions = []
        for option in options:
            actions.append(
                ft.TextButton(
                    option,
                    on_click=lambda e, opt=option: create_option_handler(opt)()
                )
            )
        
        actions.append(
            ft.TextButton(
                cancel_text,
                on_click=lambda e: selected_option.set_result(None)
            )
        )
        
        dialog = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        page.dialog = dialog
        dialog.open = True
        page.update()
        
        return await selected_option


# Convenience functions with descriptive names
def create_info_dialog(
    title: str,
    content: Union[str, ft.Control, List[ft.Control]],
    **kwargs
) -> Dialog:
    """Create an info dialog"""
    return Dialog(
        title=title,
        content=content,
        dialog_type="info",
        **kwargs
    )

def create_success_dialog(
    title: str,
    content: Union[str, ft.Control, List[ft.Control]],
    **kwargs
) -> Dialog:
    """Create a success dialog"""
    return Dialog(
        title=title,
        content=content,
        dialog_type="success",
        **kwargs
    )

def create_warning_dialog(
    title: str,
    content: Union[str, ft.Control, List[ft.Control]],
    **kwargs
) -> Dialog:
    """Create a warning dialog"""
    return Dialog(
        title=title,
        content=content,
        dialog_type="warning",
        **kwargs
    )

def create_error_dialog(
    title: str,
    content: Union[str, ft.Control, List[ft.Control]],
    **kwargs
) -> Dialog:
    """Create an error dialog"""
    return Dialog(
        title=title,
        content=content,
        dialog_type="error",
        **kwargs
    )

def create_confirmation_dialog(
    title: str,
    content: Union[str, ft.Control, List[ft.Control]],
    on_confirm: Callable,
    on_cancel: Optional[Callable] = None,
    confirm_text: str = "Yes",
    cancel_text: str = "No",
    **kwargs
) -> Dialog:
    """Create a confirmation dialog"""
    return Dialog(
        title=title,
        content=content,
        dialog_type="confirmation",
        on_confirm=on_confirm,
        on_cancel=on_cancel,
        confirm_text=confirm_text,
        cancel_text=cancel_text,
        **kwargs
    )

def create_progress_dialog(
    title: str,
    content: Union[str, ft.Control, List[ft.Control]],
    **kwargs
) -> Dialog:
    """Create a progress dialog"""
    return Dialog(
        title=title,
        content=content,
        dialog_type="progress",
        show_close_button=False,
        **kwargs
    )

def create_input_dialog(
    title: str,
    content: Union[str, ft.Control, List[ft.Control]],
    on_confirm: Callable,
    on_cancel: Optional[Callable] = None,
    confirm_text: str = "OK",
    cancel_text: str = "Cancel",
    **kwargs
) -> Dialog:
    """Create an input dialog"""
    return Dialog(
        title=title,
        content=content,
        dialog_type="input",
        on_confirm=on_confirm,
        on_cancel=on_cancel,
        confirm_text=confirm_text,
        cancel_text=cancel_text,
        **kwargs
    )


# Test function
async def test_dialogs(page: ft.Page):
    """Test dialogs functionality"""
    print("Testing dialogs...")
    
    # Test info dialog
    AlertDialog.show_info_dialog(page, "Info", "This is an info message")
    
    # Test success dialog
    AlertDialog.show_success_dialog(page, "Success", "Operation completed successfully")
    
    # Test warning dialog
    AlertDialog.show_warning_dialog(page, "Warning", "This is a warning message")
    
    # Test error dialog
    AlertDialog.show_error_dialog(page, "Error", "An error occurred")
    
    # Test confirmation dialog
    def on_confirm():
        print("Confirmed")
    
    def on_cancel():
        print("Cancelled")
    
    AlertDialog.show_confirmation_dialog(
        page, 
        "Confirm", 
        "Are you sure you want to proceed?",
        on_confirm=on_confirm,
        on_cancel=on_cancel
    )
    
    print("Dialogs test completed")


if __name__ == "__main__":
    print("Dialog Components Module")
    print("This module provides dialog components following Flet best practices")