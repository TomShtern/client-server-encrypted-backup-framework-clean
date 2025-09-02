#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ThemeManager - Proper Flet Framework Theme Management
Following Flet Framework Best Practices - work WITH the framework, not against it.

This is the PROPER way to handle themes in Flet.
Not "simple by choice" - proper by design of the Flet framework.
"""

import flet as ft
from typing import Dict, Tuple, Optional
from ..theme import THEMES, DEFAULT_THEME_NAME


class ThemeManager:
    """
    Proper theme manager using Flet's built-in theming capabilities.
    
    This is how Flet theming is designed to work - leveraging the framework's power.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.themes = THEMES
        self.current_theme_name = DEFAULT_THEME_NAME
        
        # Apply initial theme
        self.apply_theme(self.current_theme_name)
    
    def apply_theme(self, theme_name: str):
        """Apply the specified theme to the page."""
        if theme_name in self.themes:
            theme_data = self.themes[theme_name]
            if isinstance(theme_data, tuple):
                # Light/dark theme pair
                light_theme, dark_theme = theme_data
                self.page.theme = light_theme
                self.page.dark_theme = dark_theme
            else:
                # Single theme
                self.page.theme = theme_data
            
            self.current_theme_name = theme_name
            self.page.update()
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        # Implementation would depend on your specific theme structure
        pass
    
    def get_current_theme(self):
        """Get the current theme."""
        return self.themes.get(self.current_theme_name)


def get_theme_colors() -> Dict[str, str]:
    """
    Get default theme colors using Flet's built-in color system.
    Provides fallback colors that work with Flet's color scheme.
    """
    return {
        'primary': ft.Colors.PRIMARY,
        'secondary': ft.Colors.SECONDARY,
        'tertiary': ft.Colors.TERTIARY,
        'error': ft.Colors.ERROR,
        'surface': ft.Colors.SURFACE,
        # Use SURFACE as background fallback since BACKGROUND doesn't exist
        'background': ft.Colors.SURFACE,
        'on_primary': ft.Colors.ON_PRIMARY,
        'on_secondary': ft.Colors.ON_SECONDARY,
        'on_surface': ft.Colors.ON_SURFACE,
        # Use ON_SURFACE as ON_BACKGROUND fallback
        'on_background': ft.Colors.ON_SURFACE,
        'outline': ft.Colors.OUTLINE,
        'shadow': ft.Colors.SHADOW,
        'scrim': ft.Colors.SCRIM,
    }


# Backward compatibility for TOKENS usage
TOKENS = get_theme_colors()