#!/usr/bin/env python3
"""
Button Components - Flet-style implementation

Purpose: Provide button components following Flet's best practices
Logic: Inherit from Flet's native button controls with added functionality
UI: Material Design 3 styled buttons with enhanced features
"""

import flet as ft
from typing import Optional, Callable, Union
import asyncio


class Button(ft.FilledButton):
    """Button with additional features (FilledButton by default)"""
    
    def __init__(
        self,
        text: str = "",
        icon: Optional[str] = None,
        variant: str = "filled",  # filled, outlined, text, icon, fab
        size: str = "medium",  # small, medium, large
        state: str = "enabled",  # enabled, disabled, loading, success, error
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        # Set icon if provided
        if icon:
            kwargs["icon"] = icon
            
        # Initialize the appropriate base class based on variant
        if variant == "filled":
            super().__init__(text=text, on_click=on_click, **kwargs)
        elif variant == "outlined":
            # We'll override the base class in this case
            ft.OutlinedButton.__init__(self, text=text, on_click=on_click, **kwargs)
        elif variant == "text":
            # We'll override the base class in this case
            ft.TextButton.__init__(self, text=text, on_click=on_click, **kwargs)
        elif variant == "icon":
            # We'll override the base class in this case
            ft.IconButton.__init__(self, icon=icon, on_click=on_click, **kwargs)
        elif variant == "fab":
            # We'll override the base class in this case
            ft.FloatingActionButton.__init__(self, icon=icon, on_click=on_click, **kwargs)
        else:
            super().__init__(text=text, on_click=on_click, **kwargs)
        
        self.original_text = text
        self.variant = variant
        self.size = size
        self.state = state
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling based on size"""
        if self.size == "small":
            self.height = 32
        elif self.size == "medium":
            self.height = 40
        elif self.size == "large":
            self.height = 56
    
    def set_state(self, state: str):
        """Set button state"""
        self.state = state
        if state == "loading":
            self.disabled = True
            # In a real implementation, you might want to show a loading indicator
        elif state == "disabled":
            self.disabled = True
        elif state == "success":
            self.disabled = True
        elif state == "error":
            self.disabled = True
        else:  # enabled
            self.disabled = False
        self.update()
    
    def set_text(self, text: str):
        """Update button text"""
        self.text = text
        self.update()


class FilledButton(ft.FilledButton):
    """FilledButton with additional features"""
    
    def __init__(
        self,
        text: str = "",
        icon: Optional[str] = None,
        size: str = "medium",  # small, medium, large
        state: str = "enabled",  # enabled, disabled, loading, success, error
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        # Set icon if provided
        if icon:
            kwargs["icon"] = icon
            
        super().__init__(text=text, on_click=on_click, **kwargs)
        self.original_text = text
        self.size = size
        self.state = state
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling based on size"""
        if self.size == "small":
            self.height = 32
        elif self.size == "medium":
            self.height = 40
        elif self.size == "large":
            self.height = 56
    
    def set_state(self, state: str):
        """Set button state"""
        self.state = state
        if state == "loading":
            self.disabled = True
            # In a real implementation, you might want to show a loading indicator
        elif state == "disabled":
            self.disabled = True
        elif state == "success":
            self.disabled = True
        elif state == "error":
            self.disabled = True
        else:  # enabled
            self.disabled = False
        self.update()
    
    def set_text(self, text: str):
        """Update button text"""
        self.text = text
        self.update()


class OutlinedButton(ft.OutlinedButton):
    """OutlinedButton with additional features"""
    
    def __init__(
        self,
        text: str = "",
        icon: Optional[str] = None,
        size: str = "medium",
        state: str = "enabled",
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        # Set icon if provided
        if icon:
            kwargs["icon"] = icon
            
        super().__init__(text=text, on_click=on_click, **kwargs)
        self.original_text = text
        self.size = size
        self.state = state
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling based on size"""
        if self.size == "small":
            self.height = 32
        elif self.size == "medium":
            self.height = 40
        elif self.size == "large":
            self.height = 56
    
    def set_state(self, state: str):
        """Set button state"""
        self.state = state
        if state == "loading":
            self.disabled = True
        elif state == "disabled":
            self.disabled = True
        elif state == "success":
            self.disabled = True
        elif state == "error":
            self.disabled = True
        else:  # enabled
            self.disabled = False
        self.update()
    
    def set_text(self, text: str):
        """Update button text"""
        self.text = text
        self.update()


class TextButton(ft.TextButton):
    """TextButton with additional features"""
    
    def __init__(
        self,
        text: str = "",
        icon: Optional[str] = None,
        size: str = "medium",
        state: str = "enabled",
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        # Set icon if provided
        if icon:
            kwargs["icon"] = icon
            
        super().__init__(text=text, on_click=on_click, **kwargs)
        self.original_text = text
        self.size = size
        self.state = state
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling based on size"""
        if self.size == "small":
            self.height = 32
        elif self.size == "medium":
            self.height = 40
        elif self.size == "large":
            self.height = 56
    
    def set_state(self, state: str):
        """Set button state"""
        self.state = state
        if state == "loading":
            self.disabled = True
        elif state == "disabled":
            self.disabled = True
        elif state == "success":
            self.disabled = True
        elif state == "error":
            self.disabled = True
        else:  # enabled
            self.disabled = False
        self.update()
    
    def set_text(self, text: str):
        """Update button text"""
        self.text = text
        self.update()


class IconButton(ft.IconButton):
    """IconButton with additional features"""
    
    def __init__(
        self,
        icon: str,
        state: str = "enabled",
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(icon=icon, on_click=on_click, **kwargs)
        self.state = state
        self.set_state(state)
    
    def set_state(self, state: str):
        """Set button state"""
        self.state = state
        if state == "loading":
            self.disabled = True
        elif state == "disabled":
            self.disabled = True
        elif state == "success":
            self.disabled = True
        elif state == "error":
            self.disabled = True
        else:  # enabled
            self.disabled = False
        self.update()


class FloatingActionButton(ft.FloatingActionButton):
    """FloatingActionButton with additional features"""
    
    def __init__(
        self,
        icon: str,
        state: str = "enabled",
        on_click: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(icon=icon, on_click=on_click, **kwargs)
        self.state = state
        self.set_state(state)
    
    def set_state(self, state: str):
        """Set button state"""
        self.state = state
        if state == "loading":
            self.disabled = True
        elif state == "disabled":
            self.disabled = True
        elif state == "success":
            self.disabled = True
        elif state == "error":
            self.disabled = True
        else:  # enabled
            self.disabled = False
        self.update()


# Convenience functions for creating buttons (descriptive names)
def create_filled_button(text: str, on_click: Callable, **kwargs) -> FilledButton:
    """Create a filled button"""
    return FilledButton(text=text, on_click=on_click, **kwargs)

def create_outlined_button(text: str, on_click: Callable, **kwargs) -> OutlinedButton:
    """Create an outlined button"""
    return OutlinedButton(text=text, on_click=on_click, **kwargs)

def create_text_button(text: str, on_click: Callable, **kwargs) -> TextButton:
    """Create a text button"""
    return TextButton(text=text, on_click=on_click, **kwargs)

def create_icon_button(icon: str, on_click: Callable, **kwargs) -> IconButton:
    """Create an icon button"""
    return IconButton(icon=icon, on_click=on_click, **kwargs)

def create_floating_action_button(icon: str, on_click: Callable, **kwargs) -> FloatingActionButton:
    """Create a floating action button"""
    return FloatingActionButton(icon=icon, on_click=on_click, **kwargs)

def create_primary_button(text: str, on_click: Callable, **kwargs) -> FilledButton:
    """Create a primary (filled) button"""
    return FilledButton(text=text, on_click=on_click, **kwargs)

def create_secondary_button(text: str, on_click: Callable, **kwargs) -> OutlinedButton:
    """Create a secondary (outlined) button"""
    return OutlinedButton(text=text, on_click=on_click, **kwargs)


# Test function
async def test_buttons(page: ft.Page):
    """Test buttons functionality"""
    print("Testing buttons...")
    
    # Create different button types
    filled_btn = create_filled_button("Filled", lambda e: print("Filled clicked"))
    outlined_btn = create_outlined_button("Outlined", lambda e: print("Outlined clicked"))
    text_btn = create_text_button("Text", lambda e: print("Text clicked"))
    icon_btn = create_icon_button(ft.icons.ADD, lambda e: print("Icon clicked"))
    
    # Create layout
    layout = ft.Column([
        ft.Text("Buttons Test", size=20, weight=ft.FontWeight.BOLD),
        ft.Row([filled_btn, outlined_btn], spacing=16),
        ft.Row([text_btn, icon_btn], spacing=16)
    ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)
    
    # Add to page
    page.add(layout)
    page.update()
    
    # Test state changes
    await asyncio.sleep(1)
    filled_btn.set_state("loading")
    await asyncio.sleep(2)
    filled_btn.set_state("success")
    
    print("Buttons test completed")


if __name__ == "__main__":
    print("Button Components Module")
    print("This module provides button components following Flet best practices")