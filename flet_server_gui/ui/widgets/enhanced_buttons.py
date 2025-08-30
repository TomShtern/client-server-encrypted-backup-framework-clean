#!/usr/bin/env python3
"""
Enhanced Button Components - Advanced button system with animations and Material Design 3

Purpose: Provide consistent, animated button components with proper styling
Logic: Button creation, styling, event handling, and state management
UI: Material Design 3 styled buttons with hover effects and animations
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any, Union
from enum import Enum
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


class ButtonVariant(Enum):
    """Button style variants"""
    FILLED = "filled"
    TONAL = "tonal"
    OUTLINED = "outlined"
    TEXT = "text"
    ICON = "icon"
    FAB = "fab"  # Floating Action Button


class ButtonSize(Enum):
    """Button sizes"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class ButtonState(Enum):
    """Button states"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    LOADING = "loading"
    SUCCESS = "success"
    ERROR = "error"


@dataclass
class EnhancedButtonConfig:
    """Configuration for enhanced buttons"""
    text: str = ""
    icon: Optional[str] = None
    variant: ButtonVariant = ButtonVariant.FILLED
    size: ButtonSize = ButtonSize.MEDIUM
    color: Optional[str] = None  # Custom color
    width: Optional[int] = None
    height: Optional[int] = None
    tooltip: Optional[str] = None
    on_click: Optional[Callable] = None
    on_hover: Optional[Callable] = None
    disabled: bool = False
    loading: bool = False
    autofocus: bool = False
    animate: bool = True
    animation_duration: int = 200  # milliseconds
    elevation: int = 1
    border_radius: int = 20  # Default MD3 border radius
    expand: Union[bool, int] = False


class EnhancedButton:
    """
    Enhanced button with Material Design 3 styling and animations
    """
    
    # Size mappings
    SIZE_HEIGHTS = {
        ButtonSize.SMALL: 32,
        ButtonSize.MEDIUM: 40,
        ButtonSize.LARGE: 56
    }
    
    SIZE_TEXT_STYLES = {
        ButtonSize.SMALL: ft.TextThemeStyle.BODY_MEDIUM,
        ButtonSize.MEDIUM: ft.TextThemeStyle.BODY_LARGE,
        ButtonSize.LARGE: ft.TextThemeStyle.TITLE_MEDIUM
    }
    
    def __init__(self, page: ft.Page, config: EnhancedButtonConfig):
        self.page = page
        self.config = config
        self.button_ref = ft.Ref[ft.Control]()
        self.current_state = ButtonState.ENABLED
        self.original_on_click = config.on_click
        
        # Create the button
        self.button = self._create_button()
    
    def _create_button(self) -> ft.Control:
        """Create the enhanced button based on variant"""
        # Common properties
        common_props = {
            "ref": self.button_ref,
            "tooltip": self.config.tooltip,
            "disabled": self.config.disabled,
            "autofocus": self.config.autofocus,
            "expand": self.config.expand,
            "height": (
                self.SIZE_HEIGHTS.get(self.config.size, 40)
                if self.config.height is None
                else self.config.height
            ),
        }

        if self.config.width:
            common_props["width"] = self.config.width

        # Create button based on variant
        if self.config.variant == ButtonVariant.FILLED:
            return self._create_filled_button(common_props)
        elif self.config.variant == ButtonVariant.TONAL:
            return self._create_tonal_button(common_props)
        elif self.config.variant == ButtonVariant.OUTLINED:
            return self._create_outlined_button(common_props)
        elif self.config.variant == ButtonVariant.TEXT:
            return self._create_text_button(common_props)
        elif self.config.variant == ButtonVariant.ICON:
            return self._create_icon_button(common_props)
        elif self.config.variant == ButtonVariant.FAB:
            return self._create_fab_button(common_props)
        else:
            return self._create_filled_button(common_props)
    
    def _create_filled_button(self, common_props: Dict) -> ft.ElevatedButton:
        """Create filled button (primary action)"""
        content = self._create_button_content()

        return ft.ElevatedButton(
            content=content,
            on_click=self._on_click,
            on_hover=self._on_hover,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=self.config.border_radius),
                elevation=self.config.elevation,
                padding=(
                    ft.Padding(20, 0, 20, 0)
                    if self.config.size != ButtonSize.SMALL
                    else ft.Padding(16, 0, 16, 0)
                ),
            ),
            **common_props
        )
    
    def _create_tonal_button(self, common_props: Dict) -> ft.FilledButton:
        """Create tonal button (secondary action)"""
        content = self._create_button_content()

        return ft.FilledButton(
            content=content,
            on_click=self._on_click,
            on_hover=self._on_hover,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=self.config.border_radius),
                elevation=self.config.elevation,
                padding=(
                    ft.Padding(20, 0, 20, 0)
                    if self.config.size != ButtonSize.SMALL
                    else ft.Padding(16, 0, 16, 0)
                ),
            ),
            **common_props
        )
    
    def _create_outlined_button(self, common_props: Dict) -> ft.OutlinedButton:
        """Create outlined button (alternative action)"""
        content = self._create_button_content()

        return ft.OutlinedButton(
            content=content,
            on_click=self._on_click,
            on_hover=self._on_hover,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=self.config.border_radius),
                padding=(
                    ft.Padding(20, 0, 20, 0)
                    if self.config.size != ButtonSize.SMALL
                    else ft.Padding(16, 0, 16, 0)
                ),
            ),
            **common_props
        )
    
    def _create_text_button(self, common_props: Dict) -> ft.TextButton:
        """Create text button (low emphasis action)"""
        content = self._create_button_content()

        return ft.TextButton(
            content=content,
            on_click=self._on_click,
            on_hover=self._on_hover,
            style=ft.ButtonStyle(
                padding=(
                    ft.Padding(12, 0, 12, 0)
                    if self.config.size != ButtonSize.SMALL
                    else ft.Padding(8, 0, 8, 0)
                )
            ),
            **common_props
        )
    
    def _create_icon_button(self, common_props: Dict) -> ft.IconButton:
        """Create icon button (minimal action)"""
        return ft.IconButton(
            icon=self.config.icon,
            on_click=self._on_click,
            on_hover=self._on_hover,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=self.config.border_radius),
                padding=8,
            ),
            **common_props
        )
    
    def _create_fab_button(self, common_props: Dict) -> ft.FloatingActionButton:
        """Create floating action button"""
        return ft.FloatingActionButton(
            icon=self.config.icon,
            on_click=self._on_click,
            on_hover=self._on_hover,
            **common_props
        )
    
    def _create_button_content(self) -> Optional[ft.Control]:
        """Create button content (text + icon)"""
        if not self.config.text:
            return None

        # Create text
        text_style = self.SIZE_TEXT_STYLES.get(self.config.size, ft.TextThemeStyle.BODY_LARGE)
        text_control = ft.Text(self.config.text, style=text_style)

        # If no icon, return just text
        if not self.config.icon:
            return text_control

        # Create icon
        icon_control = ft.Icon(self.config.icon)

        # Create row with icon and text
        return ft.Row(
            [icon_control, text_control],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8
        )
    
    def _on_click(self, e):
        """Handle button click"""
        if self.current_state in [ButtonState.DISABLED, ButtonState.LOADING]:
            return

        try:
            if self.original_on_click:
                self.original_on_click(e)
        except Exception as ex:
            logger.error(f"Error in button click handler: {ex}")
    
    def _on_hover(self, e):
        """Handle button hover"""
        if self.config.on_hover:
            self.config.on_hover(e)
    
    def set_state(self, state: ButtonState, update_text: Optional[str] = None):
        """Set button state"""
        self.current_state = state
        
        if state == ButtonState.LOADING:
            # Show loading indicator
            if hasattr(self.button, 'content') and self.button.content:
                if isinstance(self.button.content, ft.Row):
                    # Replace text with loading indicator
                    for i, control in enumerate(self.button.content.controls):
                        if isinstance(control, ft.Text):
                            self.button.content.controls[i] = ft.ProgressRing(width=16, height=16)
                            break
            else:
                # For icon buttons, just disable
                self.button.disabled = True
        elif state == ButtonState.SUCCESS:
            # Show success state
            if update_text:
                self.set_text(update_text)
            self.button.disabled = True
        elif state == ButtonState.ERROR:
            # Show error state
            if update_text:
                self.set_text(update_text)
            self.button.disabled = True
        elif state == ButtonState.DISABLED:
            self.button.disabled = True
        elif state == ButtonState.ENABLED:
            self.button.disabled = False
            # Restore original text if it was changed
            if update_text:
                self.set_text(update_text)
        
        self.page.update()
    
    def set_text(self, text: str):
        """Update button text"""
        if hasattr(self.button, 'content') and self.button.content:
            if isinstance(self.button.content, ft.Row):
                # Find text control and update it
                for control in self.button.content.controls:
                    if isinstance(control, ft.Text):
                        control.value = text
                        break
            elif isinstance(self.button.content, ft.Text):
                self.button.content.value = text
        elif hasattr(self.button, 'text'):
            self.button.text = text
            
        self.page.update()
    
    def set_disabled(self, disabled: bool):
        """Set button disabled state"""
        self.button.disabled = disabled
        self.page.update()
    
    def get_control(self) -> ft.Control:
        """Get the Flet control"""
        return self.button


# Convenience functions for common button types
def create_primary_button(page: ft.Page, text: str, on_click: Callable, **kwargs) -> EnhancedButton:
    """Create primary (filled) button"""
    config = EnhancedButtonConfig(
        text=text,
        on_click=on_click,
        variant=ButtonVariant.FILLED,
        **kwargs
    )
    return EnhancedButton(page, config)


def create_secondary_button(page: ft.Page, text: str, on_click: Callable, **kwargs) -> EnhancedButton:
    """Create secondary (tonal) button"""
    config = EnhancedButtonConfig(
        text=text,
        on_click=on_click,
        variant=ButtonVariant.TONAL,
        **kwargs
    )
    return EnhancedButton(page, config)


def create_outline_button(page: ft.Page, text: str, on_click: Callable, **kwargs) -> EnhancedButton:
    """Create outline button"""
    config = EnhancedButtonConfig(
        text=text,
        on_click=on_click,
        variant=ButtonVariant.OUTLINED,
        **kwargs
    )
    return EnhancedButton(page, config)


def create_text_button(page: ft.Page, text: str, on_click: Callable, **kwargs) -> EnhancedButton:
    """Create text button"""
    config = EnhancedButtonConfig(
        text=text,
        on_click=on_click,
        variant=ButtonVariant.TEXT,
        **kwargs
    )
    return EnhancedButton(page, config)


def create_icon_button(page: ft.Page, icon: str, on_click: Callable, **kwargs) -> EnhancedButton:
    """Create icon button"""
    config = EnhancedButtonConfig(
        icon=icon,
        on_click=on_click,
        variant=ButtonVariant.ICON,
        **kwargs
    )
    return EnhancedButton(page, config)


def create_fab_button(page: ft.Page, icon: str, on_click: Callable, **kwargs) -> EnhancedButton:
    """Create floating action button"""
    config = EnhancedButtonConfig(
        icon=icon,
        on_click=on_click,
        variant=ButtonVariant.FAB,
        **kwargs
    )
    return EnhancedButton(page, config)


# Test function
async def test_enhanced_buttons(page: ft.Page):
    """Test enhanced buttons functionality"""
    print("Testing enhanced buttons...")
    
    # Create different button types
    primary_btn = create_primary_button(page, "Primary", lambda e: print("Primary clicked"))
    secondary_btn = create_secondary_button(page, "Secondary", lambda e: print("Secondary clicked"))
    outline_btn = create_outline_button(page, "Outline", lambda e: print("Outline clicked"))
    text_btn = create_text_button(page, "Text", lambda e: print("Text clicked"))
    icon_btn = create_icon_button(page, ft.Icons.ADD, lambda e: print("Icon clicked"))
    
    # Create layout
    layout = ft.Column([
        ft.Text("Enhanced Buttons Test", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
        ft.Row([primary_btn.get_control(), secondary_btn.get_control()], spacing=16),
        ft.Row([outline_btn.get_control(), text_btn.get_control()], spacing=16),
        icon_btn.get_control()
    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
    
    # Add to page
    page.add(layout)
    page.update()
    
    # Test state changes
    await asyncio.sleep(1)
    primary_btn.set_state(ButtonState.LOADING)
    await asyncio.sleep(2)
    primary_btn.set_state(ButtonState.SUCCESS, "Done!")
    
    print("Enhanced buttons test completed")


if __name__ == "__main__":
    print("Enhanced Button Components Module")
    print("This module provides enhanced button components for the Flet Server GUI")