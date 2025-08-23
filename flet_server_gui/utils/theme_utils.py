#!/usr/bin/env python3
"""
Theme Utility Functions
Provides helper functions for accessing theme tokens and colors throughout the application.
"""

import flet as ft
from typing import Optional, Dict, Any

# Cache for theme tokens to avoid repeated imports
_cached_tokens = None

def get_theme_tokens() -> Dict[str, str]:
    """Get theme tokens with caching for performance."""
    global _cached_tokens
    if _cached_tokens is not None:
        return _cached_tokens
    
    try:
        from flet_server_gui.ui.theme_m3 import TOKENS
        _cached_tokens = TOKENS
        return TOKENS
    except ImportError:
        # Return default tokens if theme is not available
        _cached_tokens = {
            "primary_gradient": ["#A8CBF3", "#7C5CD9"],
            "primary": "#7C5CD9",
            "on_primary": "#FFFFFF",
            "secondary": "#FCA651", 
            "on_secondary": "#000000",
            "tertiary": "#AB6DA4",
            "on_tertiary": "#FFFFFF",
            "container": "#38A298",
            "on_container": "#FFFFFF",
            "surface": "#F6F8FB",
            "surface_variant": "#E7EDF7", 
            "surface_dark": "#0F1720",
            "background": "#FFFFFF",
            "on_background": "#000000",
            "outline": "#666666",
            "error": "#B00020",
            "on_error": "#FFFFFF"
        }
        return _cached_tokens

def get_theme_color(color_name: str, default: str = "#000000") -> str:
    """Get a specific theme color by name."""
    tokens = get_theme_tokens()
    return tokens.get(color_name, default)

def get_primary_color() -> str:
    """Get the primary color."""
    return get_theme_color("primary", "#7C5CD9")

def get_secondary_color() -> str:
    """Get the secondary color."""
    return get_theme_color("secondary", "#FCA651")

def get_tertiary_color() -> str:
    """Get the tertiary color."""
    return get_theme_color("tertiary", "#AB6DA4")

def get_container_color() -> str:
    """Get the container color."""
    return get_theme_color("container", "#38A298")

def get_gradient_colors() -> list:
    """Get the primary gradient colors."""
    tokens = get_theme_tokens()
    return tokens.get("primary_gradient", ["#A8CBF3", "#7C5CD9"])

def get_linear_gradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right, stops=None) -> ft.LinearGradient:
    """Create a linear gradient using theme colors."""
    try:
        from flet_server_gui.ui.theme_m3 import linear_gradient
        return linear_gradient(begin=begin, end=end, stops=stops)
    except ImportError:
        # Fallback gradient
        colors = get_gradient_colors()
        return ft.LinearGradient(colors=colors, begin=begin, end=end, stops=stops)

def get_gradient_button_style() -> Dict[str, Any]:
    """Get style dictionary for gradient buttons."""
    return {
        "gradient": get_linear_gradient(),
        "border_radius": ft.border_radius.all(12)
    }

def apply_theme_to_component(component: ft.Control, page: ft.Page) -> None:
    """Apply theme colors to a component based on its type and purpose."""
    # This function can be extended to automatically style components
    # based on theme tokens
    pass

def create_themed_button(text: str, icon=None, button_type: str = "filled", **kwargs) -> ft.Control:
    """Create a themed button using the appropriate theme colors."""
    try:
        from flet_server_gui.ui.theme_m3 import gradient_button
        if button_type == "gradient":
            return gradient_button(ft.Row([ft.Icon(icon), ft.Text(text)]) if icon else ft.Text(text), **kwargs)
    except ImportError:
        pass
    
    # Fallback to standard buttons
    if button_type == "filled":
        return ft.FilledButton(text, icon=icon, **kwargs)
    elif button_type == "outlined":
        return ft.OutlinedButton(text, icon=icon, **kwargs)
    else:
        return ft.TextButton(text, icon=icon, **kwargs)