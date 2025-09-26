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

# 2025 Typography System - Professional enterprise typography
TYPOGRAPHY_SCALE = {
    # Display typography for major headings
    "display_large": {"size": 64, "weight": ft.FontWeight.W_900, "letter_spacing": -1.5},
    "display_medium": {"size": 48, "weight": ft.FontWeight.W_800, "letter_spacing": -1.0},
    "display_small": {"size": 36, "weight": ft.FontWeight.W_700, "letter_spacing": -0.5},

    # Headline typography for section headers
    "headline_large": {"size": 28, "weight": ft.FontWeight.BOLD, "letter_spacing": 0},
    "headline_medium": {"size": 24, "weight": ft.FontWeight.BOLD, "letter_spacing": 0},
    "headline_small": {"size": 20, "weight": ft.FontWeight.W_600, "letter_spacing": 0.1},

    # Title typography for card headers
    "title_large": {"size": 18, "weight": ft.FontWeight.W_600, "letter_spacing": 0.1},
    "title_medium": {"size": 16, "weight": ft.FontWeight.W_600, "letter_spacing": 0.15},
    "title_small": {"size": 14, "weight": ft.FontWeight.W_600, "letter_spacing": 0.2},

    # Body typography for content
    "body_large": {"size": 16, "weight": ft.FontWeight.W_400, "letter_spacing": 0.25},
    "body_medium": {"size": 14, "weight": ft.FontWeight.W_400, "letter_spacing": 0.25},
    "body_small": {"size": 12, "weight": ft.FontWeight.W_400, "letter_spacing": 0.4},

    # Label typography for buttons and inputs
    "label_large": {"size": 14, "weight": ft.FontWeight.W_500, "letter_spacing": 0.5},
    "label_medium": {"size": 12, "weight": ft.FontWeight.W_500, "letter_spacing": 0.5},
    "label_small": {"size": 10, "weight": ft.FontWeight.W_500, "letter_spacing": 0.8},
}

# Professional spacing system for consistent layouts
SPACING_SCALE = {
    "xs": 4,   # Micro spacing
    "sm": 8,   # Small spacing
    "md": 16,  # Medium spacing
    "lg": 24,  # Large spacing
    "xl": 32,  # Extra large spacing
    "2xl": 48, # Double extra large
    "3xl": 64, # Triple extra large
    "4xl": 96, # Massive spacing
}

# Border radius scale for consistent curves
BORDER_RADIUS_SCALE = {
    "none": 0,
    "sm": 4,
    "md": 8,
    "lg": 12,
    "xl": 16,
    "2xl": 20,
    "3xl": 24,
    "full": 1000,  # Perfect circle
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
# 2025 SEMANTIC COLOR SYSTEM - STATUS & DATA STORYTELLING
# ==============================================================================

# Semantic status colors for data visualization and user feedback
SEMANTIC_COLORS = {
    "excellent": {
        "bg": ft.Colors.GREEN_50,
        "accent": ft.Colors.GREEN_400,
        "text": ft.Colors.GREEN_800,
        "description": "Optimal performance, healthy status"
    },
    "good": {
        "bg": ft.Colors.BLUE_50,
        "accent": ft.Colors.BLUE_400,
        "text": ft.Colors.BLUE_800,
        "description": "Normal operation, informational"
    },
    "warning": {
        "bg": ft.Colors.AMBER_50,
        "accent": ft.Colors.AMBER_400,
        "text": ft.Colors.AMBER_800,
        "description": "Attention needed, caution advised"
    },
    "critical": {
        "bg": ft.Colors.RED_50,
        "accent": ft.Colors.RED_400,
        "text": ft.Colors.RED_800,
        "description": "Immediate action required"
    },
    "neutral": {
        "bg": ft.Colors.GREY_50,
        "accent": ft.Colors.GREY_400,
        "text": ft.Colors.GREY_800,
        "description": "Inactive or unknown status"
    }
}

# Dark theme semantic colors
DARK_SEMANTIC_COLORS = {
    "excellent": {
        "bg": ft.Colors.with_opacity(0.1, ft.Colors.GREEN_400),
        "accent": ft.Colors.GREEN_400,
        "text": ft.Colors.GREEN_200,
        "description": "Optimal performance, healthy status"
    },
    "good": {
        "bg": ft.Colors.with_opacity(0.1, ft.Colors.BLUE_400),
        "accent": ft.Colors.BLUE_400,
        "text": ft.Colors.BLUE_200,
        "description": "Normal operation, informational"
    },
    "warning": {
        "bg": ft.Colors.with_opacity(0.1, ft.Colors.AMBER_400),
        "accent": ft.Colors.AMBER_400,
        "text": ft.Colors.AMBER_200,
        "description": "Attention needed, caution advised"
    },
    "critical": {
        "bg": ft.Colors.with_opacity(0.1, ft.Colors.RED_400),
        "accent": ft.Colors.RED_400,
        "text": ft.Colors.RED_200,
        "description": "Immediate action required"
    },
    "neutral": {
        "bg": ft.Colors.with_opacity(0.1, ft.Colors.GREY_400),
        "accent": ft.Colors.GREY_400,
        "text": ft.Colors.GREY_200,
        "description": "Inactive or unknown status"
    }
}

def get_semantic_colors(status: str, is_dark: bool = False) -> dict:
    """Get semantic color scheme for status visualization."""
    colors = DARK_SEMANTIC_COLORS if is_dark else SEMANTIC_COLORS
    return colors.get(status, colors["neutral"])

def get_memory_status(percentage: int) -> str:
    """Determine memory status based on usage percentage."""
    if percentage < 70:
        return "excellent"
    elif percentage < 85:
        return "warning"
    else:
        return "critical"

def get_disk_status(percentage: int) -> str:
    """Determine disk status based on usage percentage."""
    if percentage < 80:
        return "excellent"
    elif percentage < 90:
        return "warning"
    else:
        return "critical"

# ==============================================================================
# 2025 MODERN UI ENHANCEMENTS - VIBRANT EFFECTS & LAYERING
# ==============================================================================

def setup_modern_theme(page: ft.Page) -> None:
    """
    Set up 2025 modern theme with vibrant colors, enhanced depth, and layering effects.
    Optimized for dashboard visual hierarchy and semantic color storytelling.
    """
    # Enhanced light theme with modern Material Design 3 approach
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,  # Let Flet generate harmonious colors
        font_family="Inter",
        visual_density=ft.VisualDensity.COMPACT,
        use_material3=True
    )

    # Enhanced dark theme with professional dashboard colors
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            # Professional dark colors optimized for data visualization
            primary="#60A5FA",              # Bright blue for dark mode
            on_primary="#1E3A8A",
            primary_container="#1E40AF",
            on_primary_container="#DBEAFE",

            secondary="#34D399",            # Emerald for secondary actions
            on_secondary="#064E3B",
            secondary_container="#065F46",
            on_secondary_container="#D1FAE5",

            tertiary="#FBBF24",             # Amber for warnings/highlights
            on_tertiary="#92400E",
            tertiary_container="#B45309",
            on_tertiary_container="#FEF3C7",

            error="#F87171",               # Clear error state
            on_error="#7F1D1D",
            error_container="#991B1B",
            on_error_container="#FEE2E2",

            background="#0F172A",          # Deep dark background
            on_background="#F8FAFC",
            surface="#1E293B",             # Card surfaces
            on_surface="#F8FAFC",
            surface_variant="#334155",     # Elevated surfaces
            on_surface_variant="#CBD5E1",

            outline="#64748B",
            outline_variant="#475569",
            shadow="#000000",
            scrim="#000000",

            inverse_surface="#F8FAFC",
            on_inverse_surface="#1E293B",
            inverse_primary="#3B82F6"
        ),
        font_family="Inter",
        visual_density=ft.VisualDensity.COMPACT,
        use_material3=True
    )

    # Set theme mode for optimal dashboard viewing
    page.theme_mode = ft.ThemeMode.DARK  # Dashboard typically better in dark mode

    # Apply enhanced typography for dashboard hierarchy
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

# ==============================================================================
# MODERN COMPONENT FACTORY FUNCTIONS - FLET 0.28.3 OPTIMIZED
# ==============================================================================

def create_modern_card_container(
    content: ft.Control,
    title: str = "",
    elevation: str = "soft",
    status: str = "neutral",
    is_dark: bool = False
) -> ft.Container:
    """Create modern card container with proper elevation and semantic colors."""
    semantic_colors = get_semantic_colors(status, is_dark)
    shadow = get_shadow_style(elevation, is_dark)

    card_content = content
    if title:
        card_content = ft.Column([
            ft.Text(title, size=18, weight=ft.FontWeight.W_600),
            content
        ], spacing=16)

    return ft.Container(
        content=card_content,
        bgcolor=semantic_colors["bg"] if status != "neutral" else ft.Colors.SURFACE,
        border_radius=20,
        padding=24,
        shadow=shadow,
        animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
    )

def create_trend_indicator(value: str, is_positive: bool = True) -> ft.Container:
    """Create trend indicator badge with proper colors."""
    return ft.Container(
        content=ft.Text(
            value,
            size=12,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.WHITE
        ),
        bgcolor=ft.Colors.GREEN_400 if is_positive else ft.Colors.RED_400,
        border_radius=8,
        padding=ft.Padding(6, 3, 6, 3)
    )

def create_status_ring(
    percentage: int,
    label: str,
    size: int = 120,
    auto_status: bool = True
) -> ft.Container:
    """Create status ring with automatic color coding."""
    # Auto-determine status or use provided
    if auto_status:
        if "memory" in label.lower():
            status = get_memory_status(percentage)
        elif "disk" in label.lower():
            status = get_disk_status(percentage)
        else:
            status = "excellent" if percentage < 80 else "warning" if percentage < 95 else "critical"
    else:
        status = "good"

    colors = get_semantic_colors(status)

    return ft.Stack([
        # Background ring
        ft.Container(
            width=size, height=size,
            border_radius=size // 2,
            border=ft.border.all(8, ft.Colors.with_opacity(0.2, colors["accent"]))
        ),
        # Progress ring (simulated)
        ft.Container(
            width=size, height=size,
            border_radius=size // 2,
            border=ft.border.all(8, colors["accent"])
        ),
        # Center content
        ft.Container(
            content=ft.Column([
                ft.Text(f"{percentage}%", size=24, weight=ft.FontWeight.BOLD, color=colors["text"]),
                ft.Text(label, size=12, color=ft.Colors.ON_SURFACE_VARIANT)
            ], alignment=ft.MainAxisAlignment.CENTER,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=size, height=size,
            alignment=ft.alignment.center
        )
    ])


# ==============================================================================
# DESIGN TOKEN UTILITY FUNCTIONS - EASY APPLICATION OF PROFESSIONAL STANDARDS
# ==============================================================================

def apply_typography(text_type: str, **kwargs) -> dict:
    """Apply typography tokens to text components for consistent styling."""
    typography = TYPOGRAPHY_SCALE.get(text_type, TYPOGRAPHY_SCALE["body_medium"])

    # Merge typography tokens with any additional kwargs
    text_props = {
        "size": typography["size"],
        "weight": typography["weight"],
    }

    # Add letter spacing if specified
    if "letter_spacing" in typography:
        text_props["letter_spacing"] = typography["letter_spacing"]

    # Override with any custom properties
    text_props.update(kwargs)

    return text_props

def get_spacing(size: str) -> int:
    """Get consistent spacing value from the spacing scale."""
    return SPACING_SCALE.get(size, SPACING_SCALE["md"])

def get_border_radius(size: str) -> int:
    """Get consistent border radius value from the radius scale."""
    return BORDER_RADIUS_SCALE.get(size, BORDER_RADIUS_SCALE["md"])

def create_text_with_typography(text: str, typography_type: str, color: str = None, **kwargs) -> ft.Text:
    """Create Text component with professional typography applied."""
    text_props = apply_typography(typography_type, **kwargs)

    if color:
        text_props["color"] = color

    return ft.Text(text, **text_props)

def create_professional_container(
    content: ft.Control,
    spacing_size: str = "lg",
    radius_size: str = "lg",
    elevation: str = "soft",
    **kwargs
) -> ft.Container:
    """Create container with professional spacing, radius, and shadows."""
    return ft.Container(
        content=content,
        padding=get_spacing(spacing_size),
        border_radius=get_border_radius(radius_size),
        shadow=SHADOW_STYLES.get(elevation, SHADOW_STYLES["soft"]),
        **kwargs
    )

def create_section_header(title: str, subtitle: str = None) -> ft.Column:
    """Create consistent section header with professional typography."""
    header_components = [
        create_text_with_typography(title, "headline_medium", ft.Colors.ON_SURFACE)
    ]

    if subtitle:
        header_components.append(
            ft.Container(height=get_spacing("xs"))
        )
        header_components.append(
            create_text_with_typography(subtitle, "body_medium", ft.Colors.ON_SURFACE_VARIANT)
        )

    return ft.Column(header_components, spacing=0)

def create_metric_display(
    value: str,
    label: str,
    trend: str = None,
    status: str = "neutral"
) -> ft.Column:
    """Create professional metric display with consistent typography."""
    semantic_colors = get_semantic_colors(status)

    components = [
        create_text_with_typography(value, "display_small", semantic_colors["text"]),
        ft.Container(height=get_spacing("xs")),
        create_text_with_typography(label, "body_medium", ft.Colors.ON_SURFACE_VARIANT)
    ]

    if trend:
        components.append(ft.Container(height=get_spacing("sm")))
        components.append(
            create_trend_indicator(trend, trend.startswith("+"))
        )

    return ft.Column(components, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.START)

def create_professional_card_layout(
    header: str,
    content: ft.Control,
    footer: ft.Control = None,
    status: str = "neutral"
) -> ft.Container:
    """Create professional card layout with consistent spacing and typography."""
    semantic_colors = get_semantic_colors(status)

    card_components = [
        create_section_header(header),
        ft.Container(height=get_spacing("lg")),
        content
    ]

    if footer:
        card_components.extend([
            ft.Container(height=get_spacing("lg")),
            footer
        ])

    return create_professional_container(
        content=ft.Column(card_components, spacing=0),
        spacing_size="xl",
        radius_size="xl",
        elevation="medium",
        bgcolor=semantic_colors["bg"] if status != "neutral" else ft.Colors.SURFACE,
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, semantic_colors["accent"])) if status != "neutral" else None
    )

# Export commonly used design tokens for direct access
__all__ = [
    "BORDER_RADIUS_SCALE",
    "SHADOW_STYLES",
    "SPACING_SCALE",
    "TYPOGRAPHY_SCALE",
    "apply_typography",
    "create_metric_display",
    "create_professional_card_layout",
    "create_professional_container",
    "create_section_header",
    "create_text_with_typography",
    "get_border_radius",
    "get_spacing"
]
