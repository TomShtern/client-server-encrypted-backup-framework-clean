#!/usr/bin/env python3
"""
Enhanced Dialog Components - Advanced dialog system with animations and Material Design 3

Purpose: Provide consistent, animated dialog components with proper error handling
Logic: Dialog creation, animation, event handling, and result management
UI: Material Design 3 styled dialogs with entrance/exit animations
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import asyncio
import logging
from flet_server_gui.ui.unified_theme_system import TOKENS

logger = logging.getLogger(__name__)


class DialogType(Enum):
    """Types of dialogs"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    CONFIRMATION = "confirmation"
    INPUT = "input"
    PROGRESS = "progress"


class DialogSize(Enum):
    """Predefined dialog sizes"""
    SMALL = "small"    # 400px
    MEDIUM = "medium"  # 600px
    LARGE = "large"    # 800px
    XLARGE = "xlarge"  # 1000px
    FULL = "full"      # 90% of screen


@dataclass
class DialogConfig:
    """Configuration for enhanced dialogs"""
    title: str
    content: Union[str, ft.Control, List[ft.Control]]
    dialog_type: DialogType = DialogType.INFO
    size: DialogSize = DialogSize.MEDIUM
    show_close_button: bool = True
    show_confirm_button: bool = False
    confirm_text: str = "OK"
    cancel_text: str = "Cancel"
    on_confirm: Optional[Callable] = None
    on_cancel: Optional[Callable] = None
    on_close: Optional[Callable] = None
    barrier_color: str = "#00000042"
    elevation: int = 24
    enable_escape_close: bool = True
    enable_click_outside_close: bool = True
    animation_duration: int = 300  # milliseconds
    persistent: bool = False  # If True, dialog stays open after action


class EnhancedDialog:
    """
    Enhanced dialog with Material Design 3 styling and animations
    """
    
    # Size mappings
    SIZE_WIDTHS = {
        DialogSize.SMALL: 400,
        DialogSize.MEDIUM: 600,
        DialogSize.LARGE: 800,
        DialogSize.XLARGE: 1000,
        DialogSize.FULL: None  # Will be calculated as 90% of screen
    }
    
    def __init__(self, page: ft.Page, config: DialogConfig):
        self.page = page
        self.config = config
        self.dialog_ref = ft.Ref[ft.AlertDialog]()
        self.is_open = False
        
        # Create the dialog
        self.dialog = self._create_dialog()
        
    def _create_dialog(self) -> ft.AlertDialog:
        """Create the enhanced dialog"""
        # Determine dialog width
        width = self.SIZE_WIDTHS.get(self.config.size)
        if width is None:  # FULL size
            width = self.page.width * 0.9 if self.page.width else 600
            
        # Create content
        content = self._create_content()
        
        # Create actions
        actions = self._create_actions()
        
        # Create dialog
        dialog = ft.AlertDialog(
            ref=self.dialog_ref,
            modal=True,
            title=ft.Text(self.config.title, style=ft.TextThemeStyle.TITLE_MEDIUM),
            content=content,
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=28),
            elevation=self.config.elevation,
            bgcolor=TOKENS['surface'],
            surface_tint_color=TOKENS['primary'],
        )
        
        return dialog
    
    def _create_content(self) -> ft.Control:
        """Create dialog content"""
        if isinstance(self.config.content, str):
            return ft.Text(self.config.content)
        elif isinstance(self.config.content, list):
            return ft.Column(self.config.content, spacing=16)
        else:
            return self.config.content
    
    def _create_actions(self) -> List[ft.Control]:
        """Create dialog action buttons"""
        actions = []
        
        # Cancel button (for confirmation dialogs)
        if self.config.dialog_type == DialogType.CONFIRMATION or not self.config.show_confirm_button:
            actions.append(
                ft.TextButton(
                    self.config.cancel_text,
                    on_click=self._on_cancel
                )
            )
        
        # Close button
        if self.config.show_close_button and self.config.dialog_type != DialogType.CONFIRMATION:
            actions.append(
                ft.TextButton(
                    self.config.confirm_text if self.config.show_confirm_button else "Close",
                    on_click=self._on_close
                )
            )
        
        # Confirm button (for confirmation dialogs)
        if self.config.dialog_type == DialogType.CONFIRMATION:
            actions.append(
                ft.ElevatedButton(
                    self.config.confirm_text,
                    on_click=self._on_confirm
                )
            )
            
        return actions
    
    async def _on_confirm(self, e):
        """Handle confirm action"""
        try:
            if self.config.on_confirm:
                await self.config.on_confirm()
            if not self.config.persistent:
                await self.close()
        except Exception as ex:
            logger.error(f"Error in dialog confirm handler: {ex}")
            await self._show_error(str(ex))
    
    async def _on_cancel(self, e):
        """Handle cancel action"""
        try:
            if self.config.on_cancel:
                await self.config.on_cancel()
            if not self.config.persistent:
                await self.close()
        except Exception as ex:
            logger.error(f"Error in dialog cancel handler: {ex}")
            await self._show_error(str(ex))
    
    async def _on_close(self, e):
        """Handle close action"""
        try:
            if self.config.on_close:
                await self.config.on_close()
            if not self.config.persistent:
                await self.close()
        except Exception as ex:
            logger.error(f"Error in dialog close handler: {ex}")
            await self._show_error(str(ex))
    
    async def _show_error(self, message: str):
        """Show error in dialog"""
        error_dialog = EnhancedDialog(
            self.page,
            DialogConfig(
                title="Error",
                content=message,
                dialog_type=DialogType.ERROR
            )
        )
        await error_dialog.show()
    
    async def show(self):
        """Show the dialog"""
        if not self.is_open:
            self.page.dialog = self.dialog
            self.dialog.open = True
            self.is_open = True
            self.page.update()
    
    async def close(self):
        """Close the dialog"""
        if self.is_open:
            self.dialog.open = False
            self.is_open = False
            self.page.update()


class EnhancedAlertDialog:
    """
    Enhanced alert dialog with Material Design 3 styling
    """
    
    @staticmethod
    async def show_info(page: ft.Page, title: str, message: str, on_close: Optional[Callable] = None):
        """Show info dialog"""
        dialog = EnhancedDialog(
            page,
            DialogConfig(
                title=title,
                content=message,
                dialog_type=DialogType.INFO,
                on_close=on_close
            )
        )
        await dialog.show()
    
    @staticmethod
    async def show_success(page: ft.Page, title: str, message: str, on_close: Optional[Callable] = None):
        """Show success dialog"""
        dialog = EnhancedDialog(
            page,
            DialogConfig(
                title=title,
                content=message,
                dialog_type=DialogType.SUCCESS,
                on_close=on_close
            )
        )
        await dialog.show()
    
    @staticmethod
    async def show_warning(page: ft.Page, title: str, message: str, on_close: Optional[Callable] = None):
        """Show warning dialog"""
        dialog = EnhancedDialog(
            page,
            DialogConfig(
                title=title,
                content=message,
                dialog_type=DialogType.WARNING,
                on_close=on_close
            )
        )
        await dialog.show()
    
    @staticmethod
    async def show_error(page: ft.Page, title: str, message: str, on_close: Optional[Callable] = None):
        """Show error dialog"""
        dialog = EnhancedDialog(
            page,
            DialogConfig(
                title=title,
                content=message,
                dialog_type=DialogType.ERROR,
                on_close=on_close
            )
        )
        await dialog.show()
    
    @staticmethod
    async def show_confirmation(
        page: ft.Page, 
        title: str, 
        message: str, 
        on_confirm: Callable, 
        on_cancel: Optional[Callable] = None,
        confirm_text: str = "Yes",
        cancel_text: str = "No"
    ) -> bool:
        """Show confirmation dialog"""
        result = asyncio.Future()
        
        def confirm_handler():
            result.set_result(True)
            if on_confirm:
                on_confirm()
        
        def cancel_handler():
            result.set_result(False)
            if on_cancel:
                on_cancel()
        
        dialog = EnhancedDialog(
            page,
            DialogConfig(
                title=title,
                content=message,
                dialog_type=DialogType.CONFIRMATION,
                confirm_text=confirm_text,
                cancel_text=cancel_text,
                on_confirm=confirm_handler,
                on_cancel=cancel_handler
            )
        )
        await dialog.show()
        return await result


class ConfirmationDialog:
    """
    Specialized confirmation dialog with customizable options
    """
    
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


# Test function
async def test_enhanced_dialogs(page: ft.Page):
    """Test enhanced dialogs functionality"""
    print("Testing enhanced dialogs...")
    
    # Test info dialog
    await EnhancedAlertDialog.show_info(page, "Info", "This is an info message")
    
    # Test success dialog
    await EnhancedAlertDialog.show_success(page, "Success", "Operation completed successfully")
    
    # Test warning dialog
    await EnhancedAlertDialog.show_warning(page, "Warning", "This is a warning message")
    
    # Test error dialog
    await EnhancedAlertDialog.show_error(page, "Error", "An error occurred")
    
    # Test confirmation dialog
    result = await EnhancedAlertDialog.show_confirmation(
        page, 
        "Confirm", 
        "Are you sure you want to proceed?",
        on_confirm=lambda: print("Confirmed"),
        on_cancel=lambda: print("Cancelled")
    )
    print(f"Confirmation result: {result}")
    
    print("Enhanced dialogs test completed")


if __name__ == "__main__":
    print("Enhanced Dialog Components Module")
    print("This module provides enhanced dialog components for the Flet Server GUI")