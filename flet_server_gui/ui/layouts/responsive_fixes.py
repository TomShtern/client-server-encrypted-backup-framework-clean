#!/usr/bin/env python3
"""
Responsive Layout Fixes
Utilities to fix content clipping and hitbox misalignment issues.
"""

import flet as ft
from typing import List, Optional, Union


class ResponsiveLayoutFixes:
    """Collection of utilities to fix common responsive layout issues."""
    
    @staticmethod
    def create_clipping_safe_container(
        content: ft.Control,
        min_width: Optional[float] = None,
        min_height: Optional[float] = None,
        padding: Union[int, ft.Padding] = 16,
        margin: Union[int, ft.Margin] = 8,
        **kwargs
    ) -> ft.Container:
        """
        Create a container that prevents content clipping.
        
        Args:
            content: The content to wrap
            min_width: Minimum width constraint
            min_height: Minimum height constraint
            padding: Padding around content
            margin: Margin around container
            **kwargs: Additional Container properties
        """
        container_kwargs = {
            "content": content,
            "padding": padding,
            "margin": margin,
            "clip_behavior": ft.ClipBehavior.NONE,  # Prevent clipping
            "expand": True,
        }

        # Add optional constraints
        if min_width:
            container_kwargs["min_width"] = min_width
        if min_height:
            container_kwargs["min_height"] = min_height

        # Add any additional kwargs
        container_kwargs |= kwargs

        return ft.Container(**container_kwargs)
    
    @staticmethod
    def fix_hitbox_alignment(
        content: ft.Control,
        width: Optional[float] = None,
        height: Optional[float] = None,
        alignment: ft.Alignment = ft.alignment.center,
        **kwargs
    ) -> ft.Container:
        """
        Fix hitbox alignment issues by ensuring proper sizing and alignment.
        
        Args:
            content: The content to fix
            width: Fixed width (None for responsive)
            height: Fixed height (None for responsive)
            alignment: Alignment within container
            **kwargs: Additional Container properties
        """
        container_kwargs = {
            "content": content,
            "alignment": alignment,
            "clip_behavior": ft.ClipBehavior.NONE,
        }

        # Add sizing if specified
        if width:
            container_kwargs["width"] = width
        if height:
            container_kwargs["height"] = height

        # Add any additional kwargs
        container_kwargs |= kwargs

        return ft.Container(**container_kwargs)
    
    @staticmethod
    def create_responsive_scroll_container(
        content: ft.Control,
        max_height: Optional[float] = None,
        padding: Union[int, ft.Padding] = 16,
        **kwargs
    ) -> ft.Container:
        """
        Create a scrollable container that works well in responsive layouts.
        
        Args:
            content: The content to make scrollable
            max_height: Maximum height before scrolling
            padding: Padding around content
            **kwargs: Additional Container properties
        """
        # Wrap content in a scrollable column
        scrollable_content = ft.Column(
            controls=content.controls if isinstance(content, (ft.Column, ft.Row)) else [content],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        container_kwargs = {
            "content": scrollable_content,
            "padding": padding,
            "expand": True,
            "clip_behavior": ft.ClipBehavior.NONE,
        }

        # Add max height if specified
        if max_height:
            container_kwargs["max_height"] = max_height

        # Add any additional kwargs
        container_kwargs |= kwargs

        return ft.Container(**container_kwargs)
    
    @staticmethod
    def fix_button_hitbox(
        button: ft.Control,
        min_width: float = 48,
        min_height: float = 48,
        padding: Union[int, ft.Padding] = 8,
        **kwargs
    ) -> ft.Container:
        """
        Fix button hitbox issues by ensuring minimum touch target size.
        
        Args:
            button: The button to fix
            min_width: Minimum touch target width (48px recommended)
            min_height: Minimum touch target height (48px recommended)
            padding: Padding around button
            **kwargs: Additional Container properties
        """
        return ft.Container(
            content=button,
            width=min_width,
            height=min_height,
            padding=padding,
            alignment=ft.alignment.center,
            clip_behavior=ft.ClipBehavior.NONE,
            **kwargs
        )
    
    @staticmethod
    def create_windowed_layout_fix(
        content: ft.Control,
        window_width: int = 800,
        window_height: int = 600,
        padding: Union[int, ft.Padding] = 16,
        **kwargs
    ) -> ft.Container:
        """
        Create layout that works well in windowed mode (800x600 minimum).
        
        Args:
            content: The content to fix for windowed mode
            window_width: Target window width (800px minimum)
            window_height: Target window height (600px minimum)
            padding: Padding around content
            **kwargs: Additional Container properties
        """
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=content,
                    expand=True,
                )
            ], expand=True),
            padding=padding,
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            **kwargs
        )


def apply_layout_fixes(page: ft.Page) -> None:
    """
    Apply general layout fixes to the entire page.
    
    Args:
        page: The Flet page to apply fixes to
    """
    # Ensure page has proper constraints
    if not page.window_min_width:
        page.window_min_width = 800
    if not page.window_min_height:
        page.window_min_height = 600
        
    # Apply clipping behavior to root container if it exists
    if hasattr(page, 'controls') and page.controls:
        for control in page.controls:
            if isinstance(control, ft.Container):
                control.clip_behavior = ft.ClipBehavior.NONE


# Helper functions for common fixes
def fix_content_clipping(content: ft.Control) -> ft.Container:
    """Quick fix for content clipping issues."""
    return ResponsiveLayoutFixes.create_clipping_safe_container(content)


def fix_button_clickable_areas(button: ft.Control) -> ft.Container:
    """Quick fix for button clickable area issues."""
    return ResponsiveLayoutFixes.fix_button_hitbox(button)


def ensure_windowed_compatibility(content: ft.Control) -> ft.Container:
    """Ensure content works well in windowed mode (800x600)."""
    return ResponsiveLayoutFixes.create_windowed_layout_fix(content)