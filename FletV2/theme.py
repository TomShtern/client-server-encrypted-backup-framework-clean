#!/usr/bin/env python3
"""
2025 Modern Theme System with Vibrant Colors, Layering, and Advanced Effects
Following 2025 design trends: vibrant color palettes, layering/dimensionality, morphism effects
"""

import flet as ft

# 2025 Vibrant Color Palette - Enhanced brand colors with modern saturation
BRAND_COLORS = {
    # Primary vibrant colors
    "primary": "#3B82F6",  # Vibrant blue
    "primary_variant": "#1E40AF",  # Deeper blue
    "secondary": "#8B5CF6",  # Vibrant purple
    "secondary_variant": "#7C3AED",  # Deeper purple

    # Accent colors for 2025 layering
    "accent_cyan": "#06B6D4",  # Modern cyan
    "accent_emerald": "#10B981",  # Fresh emerald
    "accent_amber": "#F59E0B",  # Warm amber
    "accent_rose": "#F43F5E",  # Vibrant rose

    # Surface colors with depth
    "surface_elevated": "#F8FAFC",  # Elevated surface
    "surface_container": "#F1F5F9",  # Container surface
    "surface_variant": "#E2E8F0",  # Variant surface

    # Status colors - vibrant but accessible
    "success": "#22C55E",
    "warning": "#EAB308",
    "error": "#EF4444",
    "info": "#3B82F6",
}

# Dark theme vibrant colors
DARK_BRAND_COLORS = {
    "primary": "#60A5FA",  # Bright blue for dark
    "primary_variant": "#3B82F6",
    "secondary": "#A78BFA",  # Bright purple for dark
    "secondary_variant": "#8B5CF6",

    "accent_cyan": "#22D3EE",
    "accent_emerald": "#34D399",
    "accent_amber": "#FBBF24",
    "accent_rose": "#FB7185",

    "surface_elevated": "#1E293B",
    "surface_container": "#334155",
    "surface_variant": "#475569",

    "success": "#4ADE80",
    "warning": "#FCD34D",
    "error": "#F87171",
    "info": "#60A5FA",
}

# 2025 Shadow System - Enhanced depth and layering
SHADOW_STYLES = {
    "subtle": ft.BoxShadow(
        spread_radius=0,
        blur_radius=4,
        offset=ft.Offset(0, 1),
        color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
    ),
    "soft": ft.BoxShadow(
        spread_radius=0,
        blur_radius=8,
        offset=ft.Offset(0, 2),
        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
    ),
    "medium": ft.BoxShadow(
        spread_radius=0,
        blur_radius=16,
        offset=ft.Offset(0, 4),
        color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
    ),
    "elevated": ft.BoxShadow(
        spread_radius=0,
        blur_radius=24,
        offset=ft.Offset(0, 8),
        color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
    ),
    "floating": ft.BoxShadow(
        spread_radius=0,
        blur_radius=32,
        offset=ft.Offset(0, 12),
        color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
    ),
    # Colored shadows for vibrant effects
    "primary_glow": ft.BoxShadow(
        spread_radius=0,
        blur_radius=20,
        offset=ft.Offset(0, 4),
        color=ft.Colors.with_opacity(0.3, BRAND_COLORS["primary"]),
    ),
    "secondary_glow": ft.BoxShadow(
        spread_radius=0,
        blur_radius=20,
        offset=ft.Offset(0, 4),
        color=ft.Colors.with_opacity(0.3, BRAND_COLORS["secondary"]),
    )
}

# Dark theme shadows
DARK_SHADOW_STYLES = {
    "subtle": ft.BoxShadow(
        spread_radius=0,
        blur_radius=4,
        offset=ft.Offset(0, 1),
        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
    ),
    "soft": ft.BoxShadow(
        spread_radius=0,
        blur_radius=8,
        offset=ft.Offset(0, 2),
        color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
    ),
    "medium": ft.BoxShadow(
        spread_radius=0,
        blur_radius=16,
        offset=ft.Offset(0, 4),
        color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
    ),
    "elevated": ft.BoxShadow(
        spread_radius=0,
        blur_radius=24,
        offset=ft.Offset(0, 8),
        color=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
    ),
    "floating": ft.BoxShadow(
        spread_radius=0,
        blur_radius=32,
        offset=ft.Offset(0, 12),
        color=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
    ),
    "primary_glow": ft.BoxShadow(
        spread_radius=0,
        blur_radius=20,
        offset=ft.Offset(0, 4),
        color=ft.Colors.with_opacity(0.4, DARK_BRAND_COLORS["primary"]),
    ),
    "secondary_glow": ft.BoxShadow(
        spread_radius=0,
        blur_radius=20,
        offset=ft.Offset(0, 4),
        color=ft.Colors.with_opacity(0.4, DARK_BRAND_COLORS["secondary"]),
    )
}

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
# FRAMEWORK-HARMONIOUS DARK THEME - Using Flet's Native System
# ==============================================================================

def setup_stunning_dark_theme(page: ft.Page):
    """Professional dark theme using Flet's native ft.ColorScheme - Framework Harmony!"""

    # Use Flet's built-in dark theme with beautiful colors
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,  # Let Flet generate harmonious colors
        use_material3=True,
        font_family="Inter"
    )

    # Enhanced dark theme with professional colors - Framework Harmonious!
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            # Professional dark colors that work with Material Design 3
            primary="#3B82F6",           # Beautiful blue
            on_primary="#FFFFFF",
            secondary="#10B981",         # Elegant green
            on_secondary="#FFFFFF",
            tertiary="#F59E0B",          # Warm orange
            on_tertiary="#FFFFFF",
            error="#EF4444",             # Clear red
            on_error="#FFFFFF",
            background="#0F172A",        # Deep dark background
            on_background="#F8FAFC",
            surface="#1E293B",           # Card surface
            on_surface="#F8FAFC",
            surface_variant="#334155",   # Elevated surface
            on_surface_variant="#CBD5E1",
            outline="#64748B",
            outline_variant="#475569"
        ),
        use_material3=True,
        font_family="Inter"
    )

    # Set to dark mode - let Flet handle everything!
    page.theme_mode = ft.ThemeMode.DARK
    page.update()  # Only acceptable page.update() for theme changes

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

def setup_enhanced_typography(page: ft.Page):
    """Enhanced typography system using Flet's built-in TextTheme for visual hierarchy."""
    text_theme = ft.TextTheme(
        # Page titles - Large and bold
        headline_large=ft.TextStyle(size=28, weight=ft.FontWeight.BOLD),
        # Section headers - Medium, lighter weight
        headline_medium=ft.TextStyle(size=20, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT),
        # Body/data text - Comfortable reading
        body_large=ft.TextStyle(size=16, weight=ft.FontWeight.NORMAL),
        # Labels and captions
        label_medium=ft.TextStyle(size=14, weight=ft.FontWeight.W_500)
    )

    # Apply to both themes
    if page.theme:
        page.theme.text_theme = text_theme
    if page.dark_theme:
        page.dark_theme.text_theme = text_theme

def setup_default_theme(page: ft.Page) -> None:
    """
    Set up the default theme using Flet's native theming system with working 2025 design elements.

    Uses only verified working Flet 0.28.3 APIs for reliability.
    """

    # Enhanced light theme with working APIs
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(**TEAL_LIGHT_COLORS),
        font_family="Inter",
        visual_density=ft.VisualDensity.COMPACT,
        use_material3=True
    )

    # Enhanced dark theme with working APIs
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(**TEAL_DARK_COLORS),
        font_family="Inter",
        visual_density=ft.VisualDensity.COMPACT,
        use_material3=True
    )

    page.theme_mode = ft.ThemeMode.SYSTEM

    # Apply enhanced typography
    setup_enhanced_typography(page)


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

# ==============================================================================
# 2025 MODERN UI ENHANCEMENTS - VIBRANT EFFECTS & LAYERING
# ==============================================================================

def setup_modern_theme(page: ft.Page) -> None:
    """
    Set up 2025 modern theme with vibrant colors, enhanced depth, and layering effects.
    Enhanced version of setup_default_theme with 2025 design trends.
    """
    # Enhanced light theme with vibrant color system
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=BRAND_COLORS["primary"],
            primary_container=BRAND_COLORS["surface_container"],
            secondary=BRAND_COLORS["secondary"],
            secondary_container=BRAND_COLORS["surface_elevated"],
            tertiary=BRAND_COLORS["accent_emerald"],
            surface=BRAND_COLORS["surface_elevated"],
            surface_variant=BRAND_COLORS["surface_variant"],
            background=BRAND_COLORS["surface_elevated"],
            error=BRAND_COLORS["error"],
            on_primary=ft.Colors.WHITE,
            on_secondary=ft.Colors.WHITE,
            on_surface=ft.Colors.GREY_900,
            on_background=ft.Colors.GREY_900,
        ),
        font_family="Inter",
        visual_density=ft.VisualDensity.COMPACT,
        use_material3=True
    )

    # Enhanced dark theme with vibrant colors
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=DARK_BRAND_COLORS["primary"],
            primary_container=DARK_BRAND_COLORS["surface_container"],
            secondary=DARK_BRAND_COLORS["secondary"],
            secondary_container=DARK_BRAND_COLORS["surface_elevated"],
            tertiary=DARK_BRAND_COLORS["accent_emerald"],
            surface=DARK_BRAND_COLORS["surface_elevated"],
            surface_variant=DARK_BRAND_COLORS["surface_variant"],
            background=DARK_BRAND_COLORS["surface_elevated"],
            error=DARK_BRAND_COLORS["error"],
            on_primary=ft.Colors.GREY_900,
            on_secondary=ft.Colors.GREY_900,
            on_surface=ft.Colors.GREY_100,
            on_background=ft.Colors.GREY_100,
        ),
        font_family="Inter",
        visual_density=ft.VisualDensity.COMPACT,
        use_material3=True
    )

    page.theme_mode = ft.ThemeMode.SYSTEM

    # Apply enhanced typography
    setup_enhanced_typography(page)

def get_shadow_style(style_name: str, is_dark: bool = False) -> ft.BoxShadow:
    """Get shadow style based on current theme mode for 2025 layering effects."""
    shadows = DARK_SHADOW_STYLES if is_dark else SHADOW_STYLES
    return shadows.get(style_name, shadows["soft"])

def get_brand_color(color_name: str, is_dark: bool = False) -> str:
    """Get brand color based on current theme mode."""
    colors = DARK_BRAND_COLORS if is_dark else BRAND_COLORS
    return colors.get(color_name, colors["primary"])

# create_modern_card has been consolidated into utils.ui_components
# Use: from utils.ui_components import create_modern_card

def create_modern_button_style(
    color_type: str = "primary",
    is_dark: bool = False,
    variant: str = "filled"  # filled, outlined, text
) -> ft.ButtonStyle:
    """Create modern button style with enhanced states and 2025 color vibrancy."""
    base_color = get_brand_color(color_type, is_dark)

    if variant == "filled":
        return ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: base_color,
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.9, base_color),
                ft.ControlState.PRESSED: ft.Colors.with_opacity(0.8, base_color),
            },
            color={
                ft.ControlState.DEFAULT: ft.Colors.WHITE,
                ft.ControlState.HOVERED: ft.Colors.WHITE,
                ft.ControlState.PRESSED: ft.Colors.WHITE,
            },
            elevation={
                ft.ControlState.DEFAULT: 2,
                ft.ControlState.HOVERED: 6,
                ft.ControlState.PRESSED: 0,
            },
            shape=ft.RoundedRectangleBorder(radius=12),
            animation_duration=120,  # Shorter animation as requested
        )
    elif variant == "outlined":
        return ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, base_color),
                ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, base_color),
            },
            color={
                ft.ControlState.DEFAULT: base_color,
                ft.ControlState.HOVERED: base_color,
                ft.ControlState.PRESSED: base_color,
            },
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(2, base_color),
                ft.ControlState.HOVERED: ft.BorderSide(2, base_color),
                ft.ControlState.PRESSED: ft.BorderSide(2, base_color),
            },
            shape=ft.RoundedRectangleBorder(radius=12),
            animation_duration=120,
        )
    else:  # text variant
        return ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, base_color),
                ft.ControlState.PRESSED: ft.Colors.with_opacity(0.2, base_color),
            },
            color={
                ft.ControlState.DEFAULT: base_color,
                ft.ControlState.HOVERED: base_color,
                ft.ControlState.PRESSED: base_color,
            },
            shape=ft.RoundedRectangleBorder(radius=12),
            animation_duration=120,
        )

def create_gradient_container(
    content: ft.Control,
    colors: list,
    begin: ft.Alignment = ft.alignment.top_left,
    end: ft.Alignment = ft.alignment.bottom_right,
    **kwargs
) -> ft.Container:
    """Create container with modern gradient background for 2025 vibrant effects."""
    return ft.Container(
        content=content,
        gradient=ft.LinearGradient(
            colors=colors,
            begin=begin,
            end=end,
        ),
        **kwargs
    )

# create_floating_action_button has been consolidated into utils.ui_components
# Use: from utils.ui_components import create_floating_action_button

# ======================================================================
# DESIGN TOKENS (Spacing, Radii, Typographic scale) — additive and safe
# ======================================================================

# 8px-based spacing scale
SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32,
}

# Standardized radii
RADII = {
    "card": 12,
    "input": 8,
    "button": 8,
    "chip": 12,
}

# Suggested typography scale (kept simple; actual sizes applied via setup_enhanced_typography)
TYPE_SCALE = {
    "h1": 30,
    "h2": 22,
    "subtitle": 16,
    "body": 14,
    "caption": 12,
}

def get_design_tokens() -> dict:
    """Return design tokens for spacing/radii/typography (safe, read-only)."""
    return {
        "spacing": SPACING,
        "radii": RADII,
        "type": TYPE_SCALE,
    }
