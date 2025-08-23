#!/usr/bin/env python3
"""
Material Design 3 Theme Manager for Flet Server GUI
Handles theme switching, color schemes, and Material Design 3 styling.
Integrates custom theme from ui/theme_m3.py
"""

import flet as ft
import sys
import os

# Add ui folder to path to access theme_m3.py
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ui_path = os.path.join(project_root, "ui")
sys.path.insert(0, ui_path)

try:
    from theme_m3 import TOKENS, create_theme, linear_gradient
    THEME_AVAILABLE = True
except ImportError:
    THEME_AVAILABLE = False
    print("[WARNING] Custom theme not available, using default M3 theme")

class ThemeManager:
    """Manages Material Design 3 themes and styling using custom design tokens."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        # Set the default theme mode. SYSTEM is a good choice.
        self.page.theme_mode = ft.ThemeMode.SYSTEM

    def apply_theme(self):
        """
        Applies light and dark themes to the page using custom design tokens.
        Falls back to default M3 theme if custom theme is not available.
        """
        if THEME_AVAILABLE:
            # Use custom theme with design tokens
            self.page.theme = create_theme(use_material3=True, dark=False)
            self.page.dark_theme = create_theme(use_material3=True, dark=True)
            
            # Apply custom font if available
            if hasattr(self.page.theme, 'font_family'):
                self.page.theme.font_family = "Inter"
                self.page.dark_theme.font_family = "Inter"
        else:
            # Fallback to default M3 theme
            self.page.theme = ft.Theme(
                color_scheme_seed=TOKENS.get("primary", "blue") if THEME_AVAILABLE else "blue",
                use_material3=True
            )
            self.page.dark_theme = ft.Theme(
                color_scheme_seed=TOKENS.get("primary", "indigo") if THEME_AVAILABLE else "indigo",
                use_material3=True
            )
        self.page.update()

    def toggle_theme(self, e=None):
        """Toggle between light, dark, and system theme modes."""
        current_mode = self.page.theme_mode
        if current_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
        elif current_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.SYSTEM
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
        
        self.page.update()

    def get_tokens(self):
        """Return the design tokens for direct use in components."""
        return TOKENS if THEME_AVAILABLE else {}

    def get_gradient(self, colors=None, begin=ft.alignment.top_left, end=ft.alignment.bottom_right, stops=None):
        """Return a linear gradient using the custom theme."""
        if THEME_AVAILABLE:
            return linear_gradient(colors, begin, end, stops)
        else:
            # Fallback gradient
            if colors is None:
                colors = ["#A8CBF3", "#7C5CD9"] if THEME_AVAILABLE else ["#2196F3", "#3F51B5"]
            return ft.LinearGradient(colors=colors, begin=begin, end=end, stops=stops)
