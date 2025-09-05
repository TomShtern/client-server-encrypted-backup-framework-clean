#!/usr/bin/env python3
"""
Streamlined Theme System for FletV2
Custom theme colors with simplified framework-harmonious implementation.

Preserves your custom color schemes while following Flet best practices.
Reduced from 297 lines to ~100 lines by eliminating over-engineering.
"""

import flet as ft

# ==============================================================================
# CUSTOM COLOR SCHEMES - Your Original Colors Preserved
# ==============================================================================

# Teal Theme Colors (Professional & Balanced)
TEAL_LIGHT_COLORS = {
    "primary": "#38A298", "on_primary": "#FFFFFF", "primary_container": "#B9F6F0", "on_primary_container": "#00201D",
    "secondary": "#7C5CD9", "on_secondary": "#FFFFFF", "secondary_container": "#EADDFF", "on_secondary_container": "#21005D",
    "tertiary": "#FFA726", "on_tertiary": "#000000", "tertiary_container": "#FFE0B2", "on_tertiary_container": "#2A1800",
    "error": "#EF5350", "on_error": "#FFFFFF", "error_container": "#FFDAD6", "on_error_container": "#410002",
    "background": "#F8F9FA", "on_background": "#1C2A35", "surface": "#F0F4F8", "on_surface": "#1C2A35",
    "surface_variant": "#DAE5E7", "on_surface_variant": "#3F484B", "outline": "#6F797B", "outline_variant": "#BFC8CB",
    "shadow": "#000000", "scrim": "#000000", "inverse_surface": "#2F3033", "on_inverse_surface": "#F1F0F4", "inverse_primary": "#A2D2E0",
}

TEAL_DARK_COLORS = {
    "primary": "#82D9CF", "on_primary": "#003732", "primary_container": "#00504A", "on_primary_container": "#B9F6F0",
    "secondary": "#D0BCFF", "on_secondary": "#381E72", "secondary_container": "#4F378B", "on_secondary_container": "#EADDFF",
    "tertiary": "#FFB868", "on_tertiary": "#482900", "tertiary_container": "#663D00", "on_tertiary_container": "#FFDDB3",
    "error": "#FFB4AB", "on_error": "#690005", "error_container": "#93000A", "on_error_container": "#FFDAD6",
    "background": "#12181C", "on_background": "#E2E2E6", "surface": "#1A2228", "on_surface": "#E2E2E6",
    "surface_variant": "#3F484B", "on_surface_variant": "#BFC8CB", "outline": "#899295", "outline_variant": "#3F484B",
    "shadow": "#000000", "scrim": "#000000", "inverse_surface": "#E2E2E6", "on_inverse_surface": "#1A2228", "inverse_primary": "#38A298",
}

# Purple Theme Colors (Bold & Dynamic)
PURPLE_LIGHT_COLORS = {
    "primary": "#7C5CD9", "on_primary": "#FFFFFF", "primary_container": "#EADDFF", "on_primary_container": "#21005D",
    "secondary": "#FFA726", "on_secondary": "#000000", "secondary_container": "#FFE0B2", "on_secondary_container": "#2A1800",
    "tertiary": "#38A298", "on_tertiary": "#FFFFFF", "tertiary_container": "#B9F6F0", "on_tertiary_container": "#00201D",
    "error": "#EF5350", "on_error": "#FFFFFF", "error_container": "#FFDAD6", "on_error_container": "#410002",
    "background": "#F8F9FA", "on_background": "#1C2A35", "surface": "#F0F4F8", "on_surface": "#1C2A35",
    "surface_variant": "#DAE5E7", "on_surface_variant": "#3F484B", "outline": "#6F797B", "outline_variant": "#BFC8CB",
    "shadow": "#000000", "scrim": "#000000", "inverse_surface": "#2F3033", "on_inverse_surface": "#F1F0F4", "inverse_primary": "#D0BCFF",
}

PURPLE_DARK_COLORS = {
    "primary": "#D0BCFF", "on_primary": "#381E72", "primary_container": "#4F378B", "on_primary_container": "#EADDFF",
    "secondary": "#FFB868", "on_secondary": "#482900", "secondary_container": "#663D00", "on_secondary_container": "#FFDDB3",
    "tertiary": "#82D9CF", "on_tertiary": "#003732", "tertiary_container": "#00504A", "on_tertiary_container": "#B9F6F0",
    "error": "#FFB4AB", "on_error": "#690005", "error_container": "#93000A", "on_error_container": "#FFDAD6",
    "background": "#12181C", "on_background": "#E2E2E6", "surface": "#1A2228", "on_surface": "#E2E2E6",
    "surface_variant": "#3F484B", "on_surface_variant": "#BFC8CB", "outline": "#899295", "outline_variant": "#3F484B",
    "shadow": "#000000", "scrim": "#000000", "inverse_surface": "#E2E2E6", "on_inverse_surface": "#1A2228", "inverse_primary": "#7C5CD9",
}

# ==============================================================================
# SIMPLIFIED THEME CREATION - Framework Harmonious
# ==============================================================================

# Available themes with your custom colors
THEMES = {
    "Teal": {
        "light": ft.Theme(color_scheme=ft.ColorScheme(**TEAL_LIGHT_COLORS), font_family="Inter"),
        "dark": ft.Theme(color_scheme=ft.ColorScheme(**TEAL_DARK_COLORS), font_family="Inter")
    },
    "Purple": {
        "light": ft.Theme(color_scheme=ft.ColorScheme(**PURPLE_LIGHT_COLORS), font_family="Inter"),
        "dark": ft.Theme(color_scheme=ft.ColorScheme(**PURPLE_DARK_COLORS), font_family="Inter")
    }
}

DEFAULT_THEME_NAME = "Teal"

# ==============================================================================
# CLEAN API FUNCTIONS - Framework Native Approach
# ==============================================================================

def setup_default_theme(page: ft.Page) -> None:
    """
    Set up the default theme using Flet's native theming system.
    
    Applies your custom colors while following Flet best practices.
    """
    theme_data = THEMES[DEFAULT_THEME_NAME]
    page.theme = theme_data["light"]
    page.dark_theme = theme_data["dark"]
    page.theme_mode = ft.ThemeMode.SYSTEM


def toggle_theme_mode(page: ft.Page) -> None:
    """
    Toggle between light and dark theme modes using Flet's native ThemeMode.
    """
    if page.theme_mode == ft.ThemeMode.LIGHT:
        page.theme_mode = ft.ThemeMode.DARK
    elif page.theme_mode == ft.ThemeMode.DARK:
        page.theme_mode = ft.ThemeMode.LIGHT
    else:
        # Default to LIGHT if SYSTEM or None
        page.theme_mode = ft.ThemeMode.LIGHT
    
    page.update()  # ONLY acceptable page.update() for theme changes


def apply_theme_variant(page: ft.Page, theme_name: str) -> bool:
    """
    Apply different theme variant while preserving current theme mode.
    
    Args:
        page: Flet page instance
        theme_name: Theme name from THEMES dictionary
        
    Returns:
        bool: True if theme was applied successfully
    """
    if theme_name not in THEMES:
        return False
    
    current_mode = page.theme_mode
    theme_data = THEMES[theme_name]
    page.theme = theme_data["light"]
    page.dark_theme = theme_data["dark"]
    page.theme_mode = current_mode  # Preserve current mode
    page.update()  # ONLY acceptable page.update() for theme changes
    return True


def get_available_themes() -> list:
    """Get list of available theme names."""
    return list(THEMES.keys())


def get_current_theme_colors(page: ft.Page) -> dict:
    """
    Get current theme colors using Flet's built-in color system.
    
    Returns semantic color names that work with current theme.
    """
    return {
        'primary': ft.Colors.PRIMARY,
        'secondary': ft.Colors.SECONDARY,
        'tertiary': ft.Colors.TERTIARY,
        'error': ft.Colors.ERROR,
        'surface': ft.Colors.SURFACE,
        'background': ft.Colors.SURFACE,
        'on_primary': ft.Colors.ON_PRIMARY,
        'on_secondary': ft.Colors.ON_SECONDARY,
        'on_surface': ft.Colors.ON_SURFACE,
        'outline': ft.Colors.OUTLINE,
    }