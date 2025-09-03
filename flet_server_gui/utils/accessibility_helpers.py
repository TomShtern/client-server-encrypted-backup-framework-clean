#!/usr/bin/env python3
"""
Accessibility Helper Functions

Extracted from the massive responsive.py file to provide focused accessibility
utilities that work with simple Flet patterns without framework-fighting.

This module provides helper functions for creating accessible components with
proper touch targets, color contrast, and interaction support.
"""

import flet as ft
from typing import Callable, Set, Union, Optional
try:
    from .responsive_enums import TouchTargetSpec, InteractionMethod
except ImportError:
    # Fallback for standalone import during testing
    from responsive_enums import TouchTargetSpec, InteractionMethod

# Auto-enable UTF-8 for all subprocess operations
import Shared.utils.utf8_solution


def create_accessible_container(
    content: ft.Control,
    min_width: Optional[float] = None,
    min_height: Optional[float] = None,
    padding: Union[int, ft.Padding] = 16,
    margin: Union[int, ft.Margin] = 8,
    interaction_methods: Optional[Set[InteractionMethod]] = None,
    **kwargs
) -> ft.Container:
    """
    Create a container with proper accessibility support and clipping prevention.
    
    Args:
        content: The content to wrap
        min_width: Minimum width constraint
        min_height: Minimum height constraint
        padding: Padding around content
        margin: Margin around container
        interaction_methods: Supported interaction methods
        **kwargs: Additional Container properties
        
    Returns:
        ft.Container with accessibility features
    """
    if interaction_methods is None:
        interaction_methods = {InteractionMethod.MOUSE, InteractionMethod.TOUCH}
    
    # Create base container configuration
    container_kwargs = {
        "content": content,
        "padding": padding,
        "margin": margin,
        "clip_behavior": ft.ClipBehavior.NONE,  # Prevent clipping issues
        "expand": True,
    }
    
    # Add accessibility margins if needed
    spec = TouchTargetSpec()
    if InteractionMethod.ACCESSIBILITY in interaction_methods:
        if min_width:
            min_width += spec.accessibility_margin * 2
        if min_height:
            min_height += spec.accessibility_margin * 2
    
    # Add minimum constraints
    if min_width:
        container_kwargs["min_width"] = min_width
    if min_height:
        container_kwargs["min_height"] = min_height
    
    # Add any additional properties
    container_kwargs.update(kwargs)
    
    return ft.Container(**container_kwargs)


def create_accessible_button(
    text: str, 
    on_click: Callable,
    spec: Optional[TouchTargetSpec] = None,
    interaction_methods: Optional[Set[InteractionMethod]] = None,
    button_type: str = "elevated",
    **button_kwargs
) -> ft.Control:
    """
    Create button with accessibility-compliant touch target sizing.
    
    Args:
        text: Button text
        on_click: Click handler function
        spec: Touch target specifications (uses default if None) 
        interaction_methods: Supported interaction methods
        button_type: Type of button ("elevated", "filled", "outlined", "text")
        **button_kwargs: Additional button properties
        
    Returns:
        Accessible button with proper sizing
    """
    if spec is None:
        spec = TouchTargetSpec()
        
    if interaction_methods is None:
        interaction_methods = {InteractionMethod.MOUSE, InteractionMethod.TOUCH, InteractionMethod.ACCESSIBILITY}
    
    # Calculate minimum width based on text length and specifications
    estimated_text_width = len(text) * 8 + 32  # Rough estimate
    min_width = max(estimated_text_width, spec.min_width)
    min_height = spec.min_height
    
    # Add accessibility margin if needed
    if InteractionMethod.ACCESSIBILITY in interaction_methods:
        min_width += spec.accessibility_margin * 2
        min_height += spec.accessibility_margin * 2
    
    # Common button properties
    common_props = {
        "text": text,
        "on_click": on_click,
        "height": max(min_height, 44),  # Ensure minimum height
        "width": min_width,
        **button_kwargs
    }
    
    # Create button based on type
    if button_type == "filled":
        return ft.FilledButton(**common_props)
    elif button_type == "outlined":
        return ft.OutlinedButton(**common_props)
    elif button_type == "text":
        return ft.TextButton(**common_props)
    else:  # Default to elevated
        return ft.ElevatedButton(**common_props)


def ensure_minimum_touch_target(
    component: ft.Control, 
    spec: Optional[TouchTargetSpec] = None,
    interaction_methods: Optional[Set[InteractionMethod]] = None
) -> ft.Container:
    """
    Ensure component meets minimum touch target requirements.
    
    Args:
        component: Component to wrap with proper touch target
        spec: Touch target specifications (uses default if None)
        interaction_methods: Supported interaction methods (auto-detects if None)
        
    Returns:
        Container with guaranteed minimum touch target size
    """
    if spec is None:
        spec = TouchTargetSpec()
        
    if interaction_methods is None:
        interaction_methods = {InteractionMethod.MOUSE, InteractionMethod.TOUCH}
    
    # Calculate required dimensions based on interaction methods
    min_width = spec.min_width
    min_height = spec.min_height
    
    # Add accessibility margin if accessibility support is needed
    if InteractionMethod.ACCESSIBILITY in interaction_methods:
        min_width += spec.accessibility_margin * 2
        min_height += spec.accessibility_margin * 2
    
    return ft.Container(
        content=component,
        min_width=min_width,
        min_height=min_height,
        alignment=ft.alignment.center,
        clip_behavior=ft.ClipBehavior.NONE,
        padding=ft.padding.all(spec.touch_padding),
    )


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
        
    Returns:
        Container with proper button hitbox
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


def create_accessible_text_input(
    label: str,
    hint_text: Optional[str] = None,
    on_change: Optional[Callable] = None,
    spec: Optional[TouchTargetSpec] = None,
    **input_kwargs
) -> ft.TextField:
    """
    Create accessible text input with proper sizing and labeling.
    
    Args:
        label: Input label text
        hint_text: Optional hint text
        on_change: Optional change handler
        spec: Touch target specifications
        **input_kwargs: Additional TextField properties
        
    Returns:
        Accessible TextField
    """
    if spec is None:
        spec = TouchTargetSpec()
    
    return ft.TextField(
        label=label,
        hint_text=hint_text,
        on_change=on_change,
        height=max(spec.min_height, 56),  # Material Design text field height
        border_radius=ft.border_radius.all(8),
        **input_kwargs
    )


def create_accessible_card(
    content: ft.Control,
    min_width: Optional[float] = None,
    min_height: Optional[float] = None,
    elevation: int = 2,
    padding: Union[int, ft.Padding] = 16,
    **card_kwargs
) -> ft.Card:
    """
    Create accessible card with proper touch targets and spacing.
    
    Args:
        content: Card content
        min_width: Minimum card width
        min_height: Minimum card height
        elevation: Card elevation
        padding: Content padding
        **card_kwargs: Additional Card properties
        
    Returns:
        Accessible Card component
    """
    # Wrap content with accessible container
    accessible_content = create_accessible_container(
        content=content,
        min_width=min_width,
        min_height=min_height,
        padding=padding
    )
    
    return ft.Card(
        content=accessible_content,
        elevation=elevation,
        expand=True,
        **card_kwargs
    )


def apply_high_contrast_theme(component: ft.Control, high_contrast: bool = False) -> ft.Control:
    """
    Apply high contrast styling to a component for accessibility.
    
    Args:
        component: Component to style
        high_contrast: Whether to apply high contrast mode
        
    Returns:
        Component with appropriate contrast styling
    """
    if not high_contrast:
        return component
    
    # Apply high contrast styling based on component type
    if isinstance(component, ft.Text):
        component.color = ft.colors.BLACK if component.color != ft.colors.WHITE else ft.colors.WHITE
        component.bgcolor = ft.colors.WHITE if component.color == ft.colors.BLACK else ft.colors.BLACK
    elif isinstance(component, (ft.ElevatedButton, ft.FilledButton, ft.OutlinedButton)):
        component.bgcolor = ft.colors.BLACK
        component.color = ft.colors.WHITE
    elif isinstance(component, ft.Container):
        if not component.bgcolor:
            component.bgcolor = ft.colors.WHITE
        if not component.border:
            component.border = ft.border.all(2, ft.colors.BLACK)
    
    return component


def create_focus_indicator(component: ft.Control, focus_color: str = None) -> ft.Container:
    """
    Wrap component with focus indicator for keyboard navigation.
    
    Args:
        component: Component to add focus indicator to
        focus_color: Color for focus indicator
        
    Returns:
        Container with focus indicator support
    """
    if focus_color is None:
        focus_color = ft.colors.PRIMARY
    
    return ft.Container(
        content=component,
        border=ft.border.all(2, ft.colors.TRANSPARENT),
        border_radius=ft.border_radius.all(4),
        # Note: In a real implementation, you'd need to handle focus events
        # This is a simplified version for the extraction
    )


# Accessibility constants
WCAG_AA_CONTRAST_RATIO = 4.5
WCAG_AAA_CONTRAST_RATIO = 7.0
MIN_TOUCH_TARGET_SIZE = 44  # Material Design recommendation
RECOMMENDED_TOUCH_TARGET_SIZE = 48  # Better for accessibility


def validate_touch_target_size(width: float, height: float) -> bool:
    """
    Validate that touch target meets minimum size requirements.
    
    Args:
        width: Target width in pixels
        height: Target height in pixels
        
    Returns:
        True if target meets minimum requirements
    """
    return width >= MIN_TOUCH_TARGET_SIZE and height >= MIN_TOUCH_TARGET_SIZE


def get_recommended_spacing_for_targets(target_count: int) -> int:
    """
    Get recommended spacing between touch targets based on count.
    
    Args:
        target_count: Number of adjacent touch targets
        
    Returns:
        Recommended spacing in pixels
    """
    spec = TouchTargetSpec()
    base_spacing = spec.min_spacing
    
    # Increase spacing for more targets to prevent accidental touches
    if target_count > 5:
        return base_spacing * 2
    elif target_count > 3:
        return int(base_spacing * 1.5)
    else:
        return base_spacing


# ============================================================================
# RESPONSIVE LAYOUT FIXES
# ============================================================================

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
        container_kwargs.update(kwargs)
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
        container_kwargs.update(kwargs)
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
        container_kwargs.update(kwargs)
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


# ============================================================================
# LAYOUT FIX UTILITIES  
# ============================================================================

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
    
    # Apply clipping fixes to all controls
    def fix_clipping_recursive(control):
        if hasattr(control, 'controls'):
            for child in control.controls:
                fix_clipping_recursive(child)
        if isinstance(control, ft.Container):
            control.clip_behavior = ft.ClipBehavior.NONE


def fix_content_clipping(content: ft.Control) -> ft.Container:
    """Quick fix for content clipping issues."""
    return ResponsiveLayoutFixes.create_clipping_safe_container(content)


def fix_button_clickable_areas(button: ft.Control) -> ft.Container:
    """Quick fix for button clickable area issues."""
    return ResponsiveLayoutFixes.fix_button_hitbox(button)


def ensure_windowed_compatibility(content: ft.Control) -> ft.Container:
    """Ensure content works well in windowed mode (800x600)."""
    return ResponsiveLayoutFixes.create_windowed_layout_fix(content)