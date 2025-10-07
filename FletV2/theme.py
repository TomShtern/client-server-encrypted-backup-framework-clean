#!/usr/bin/env python3
"""
Sophisticated FletV2 Theme System - Material Design 3 + Neumorphism + Glassmorphism
Flet 0.28.3 implementation with triple design system architecture.
Foundation: Material Design 3 semantic colors and typography
Structure: Neumorphic soft shadows and tactile depth (40-45% intensity)
Focus: Glassmorphic transparency and blur effects (20-30% intensity)

Performance Optimizations:
- Pre-computed shadow constants for zero-allocation performance
- Reusable shadow objects prevent GC pressure
- GPU-accelerated animations (scale, opacity only)
"""

from typing import cast, Literal

import flet as ft

# Material Design 3 semantic color system with enhanced palette
BRAND_COLORS = {
    "primary": "#3B82F6",      # Material Blue 500
    "secondary": "#8B5CF6",    # Material Purple 500
    "tertiary": "#10B981",     # Material Emerald 500
    "success": "#22C55E",      # Material Green 500
    "warning": "#EAB308",      # Material Yellow 500
    "error": "#EF4444",        # Material Red 500
    "info": "#0EA5E9",         # Material Sky 500
    "surface": "#F8FAFC",      # Material Slate 50
    "surface_variant": "#F1F5F9",  # Material Slate 100
    "outline": "#CBD5E1",      # Material Slate 300
}

# ========================================================================================
# PRE-COMPUTED NEUMORPHIC SHADOWS (40-45% Intensity)
# Performance: Reused objects prevent allocation overhead
# ========================================================================================

# PRONOUNCED NEUMORPHIC SHADOWS (40-45% intensity) - For primary interactive elements
PRONOUNCED_NEUMORPHIC_SHADOWS = [
    # ENHANCED: Stronger dark shadow for visibility in dark theme (40-45% intensity)
    ft.BoxShadow(
        spread_radius=3,  # Increased from 2
        blur_radius=16,   # Increased from 12
        color=ft.Colors.with_opacity(0.4, "#000000"),  # Increased from 0.25
        offset=ft.Offset(8, 8),  # Increased from (6,6)
        blur_style=ft.ShadowBlurStyle.NORMAL
    ),
    # REDUCED: Weaker light highlight to prevent shadow cancellation in dark theme
    ft.BoxShadow(
        spread_radius=2,
        blur_radius=12,
        color=ft.Colors.with_opacity(0.5, "#FFFFFF"),  # REDUCED from 0.9
        offset=ft.Offset(-4, -4),  # Reduced from (-6,-6)
        blur_style=ft.ShadowBlurStyle.NORMAL
    ),
]

# MODERATE NEUMORPHIC SHADOWS (30% intensity) - For secondary elements
MODERATE_NEUMORPHIC_SHADOWS = [
    ft.BoxShadow(
        spread_radius=1,
        blur_radius=8,
        color=ft.Colors.with_opacity(0.18, "#000000"),
        offset=ft.Offset(4, 4),
        blur_style=ft.ShadowBlurStyle.NORMAL
    ),
    ft.BoxShadow(
        spread_radius=1,
        blur_radius=8,
        color=ft.Colors.with_opacity(0.7, "#FFFFFF"),
        offset=ft.Offset(-4, -4),
        blur_style=ft.ShadowBlurStyle.NORMAL
    ),
]

# SUBTLE NEUMORPHIC SHADOWS (20% intensity) - For tertiary elements
SUBTLE_NEUMORPHIC_SHADOWS = [
    ft.BoxShadow(
        spread_radius=1,
        blur_radius=6,
        color=ft.Colors.with_opacity(0.12, "#000000"),
        offset=ft.Offset(3, 3),
        blur_style=ft.ShadowBlurStyle.NORMAL
    ),
    ft.BoxShadow(
        spread_radius=1,
        blur_radius=6,
        color=ft.Colors.with_opacity(0.6, "#FFFFFF"),
        offset=ft.Offset(-3, -3),
        blur_style=ft.ShadowBlurStyle.NORMAL
    ),
]

# INSET NEUMORPHIC SHADOWS - For pressed/depressed states
INSET_NEUMORPHIC_SHADOWS = [
    ft.BoxShadow(
        spread_radius=1,
        blur_radius=6,
        color=ft.Colors.with_opacity(0.2, "#000000"),
        offset=ft.Offset(2, 2),
        blur_style=ft.ShadowBlurStyle.INNER
    ),
    ft.BoxShadow(
        spread_radius=1,
        blur_radius=6,
        color=ft.Colors.with_opacity(0.6, "#FFFFFF"),
        offset=ft.Offset(-2, -2),
        blur_style=ft.ShadowBlurStyle.INNER
    ),
]

# ========================================================================================
# GLASSMORPHIC CONFIGURATION CONSTANTS (20-30% Intensity)
# Performance: Direct dictionary access faster than function calls
# ========================================================================================

GLASS_STRONG = {
    "blur": 15,
    "bg_opacity": 0.12,
    "border_opacity": 0.2
}

GLASS_MODERATE = {
    "blur": 12,
    "bg_opacity": 0.10,
    "border_opacity": 0.15
}

GLASS_SUBTLE = {
    "blur": 10,
    "bg_opacity": 0.08,
    "border_opacity": 0.12
}

# Legacy configuration for backward compatibility
NEUMORPHIC_SHADOWS = {
    "raised": {
        "light_shadow": {
            "color": "#FFFFFF",
            "opacity": 0.8,
            "offset": (-4, -4),
            "blur": 8
        },
        "dark_shadow": {
            "color": "#000000",
            "opacity": 0.15,
            "offset": (4, 4),
            "blur": 8
        }
    },
    "inset": {
        "light_shadow": {
            "color": "#FFFFFF",
            "opacity": 0.6,
            "offset": (-2, -2),
            "blur": 6
        },
        "dark_shadow": {
            "color": "#000000",
            "opacity": 0.2,
            "offset": (2, 2),
            "blur": 6
        }
    }
}

# Legacy glassmorphic configuration
GLASSMORPHIC_CONFIG = {
    "background_opacity": 0.08,
    "border_opacity": 0.12,
    "blur_sigma": 20,
    "backdrop_blur": 15
}

def setup_sophisticated_theme(page: ft.Page):
    """Set up Material Design 3 + Neumorphism + Glassmorphism theme system."""

    # Light theme using Flet's ColorScheme
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=BRAND_COLORS["primary"],
            secondary=BRAND_COLORS["secondary"],
            tertiary=BRAND_COLORS["tertiary"],
            surface=ft.Colors.SURFACE,
            background=ft.Colors.SURFACE,  # ✅ FIXED: Use SURFACE instead of SURFACE_TINT
            error=BRAND_COLORS["error"],
            on_primary=ft.Colors.WHITE,
            on_secondary=ft.Colors.WHITE,
            on_surface=ft.Colors.ON_SURFACE,
            on_background=ft.Colors.ON_SURFACE,
        ),
        # Use Flet's built-in text theme
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(size=64, weight=ft.FontWeight.W_900),
            display_medium=ft.TextStyle(size=48, weight=ft.FontWeight.W_800),
            headline_large=ft.TextStyle(size=28, weight=ft.FontWeight.BOLD),
            headline_medium=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD),
            title_large=ft.TextStyle(size=18, weight=ft.FontWeight.W_600),
            title_medium=ft.TextStyle(size=16, weight=ft.FontWeight.W_600),
            body_large=ft.TextStyle(size=16, weight=ft.FontWeight.W_400),
            body_medium=ft.TextStyle(size=14, weight=ft.FontWeight.W_400),
            label_large=ft.TextStyle(size=14, weight=ft.FontWeight.W_500),
        ),
        font_family="Inter",
        visual_density=ft.VisualDensity.STANDARD,
        use_material3=True
    )

    # Material Design 3 dark theme with enhanced colors for neumorphism
    page.dark_theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary="#60A5FA",           # Bright blue for dark
            secondary="#A78BFA",         # Bright purple for dark
            tertiary="#34D399",          # Bright emerald for dark
            surface=ft.Colors.SURFACE,
            background=ft.Colors.SURFACE,  # ✅ FIXED: Use SURFACE instead of SURFACE_TINT
            error="#F87171",
            on_primary=ft.Colors.WHITE,  # White text on bright blue
            on_secondary=ft.Colors.WHITE, # White text on bright purple
            on_surface=ft.Colors.ON_SURFACE,
            on_background=ft.Colors.ON_SURFACE,
        ),
        text_theme=ft.TextTheme(
            display_large=ft.TextStyle(size=64, weight=ft.FontWeight.W_900, color="#FFFFFF"),
            display_medium=ft.TextStyle(size=48, weight=ft.FontWeight.W_800, color="#FFFFFF"),
            headline_large=ft.TextStyle(size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            headline_medium=ft.TextStyle(size=24, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            title_large=ft.TextStyle(size=18, weight=ft.FontWeight.W_600, color="#E5E7EB"),
            title_medium=ft.TextStyle(size=16, weight=ft.FontWeight.W_600, color="#E5E7EB"),
            body_large=ft.TextStyle(size=16, weight=ft.FontWeight.W_400, color="#D1D5DB"),
            body_medium=ft.TextStyle(size=14, weight=ft.FontWeight.W_400, color="#D1D5DB"),
            label_large=ft.TextStyle(size=14, weight=ft.FontWeight.W_500, color="#9CA3AF"),
        ),
        font_family="Inter",
        visual_density=ft.VisualDensity.STANDARD,
        use_material3=True
    )

    # Use system preference for theme mode
    page.theme_mode = ft.ThemeMode.SYSTEM

def create_modern_card(
    content: ft.Control,
    elevation: int | None = None,
    hover_effect: bool = True
) -> ft.Container:
    """Create modern card using Flet's built-in styling."""
    return ft.Container(
        content=content,
        bgcolor=ft.Colors.SURFACE,
        border_radius=16,
        padding=ft.padding.all(20),
        shadow=ft.BoxShadow(
            blur_radius=elevation or 8,
            offset=ft.Offset(0, 2),
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)
        ),
        # Use ft.Animation (public symbol) rather than ft.animation.Animation
        animate=ft.Animation(150) if hover_effect else None
    )

def themed_button(
    text: str,
    on_click=None,
    variant: str = "filled",  # filled, outlined, text
    icon: str | None = None,
    disabled: bool = False
) -> ft.ElevatedButton | ft.OutlinedButton | ft.TextButton:
    """Create themed button using Flet's built-in button types."""

    if variant == "filled":
        return ft.ElevatedButton(
            text=text,
            icon=icon,
            on_click=on_click,
            disabled=disabled,
                style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                # pyright expects ControlState-keyed dict; cast to satisfy type checker
                elevation=cast(dict, {ft.ControlState.DEFAULT: 2, ft.ControlState.HOVERED: 6})
            )
        )
    elif variant == "outlined":
        return ft.OutlinedButton(
            text=text,
            icon=icon,
            on_click=on_click,
            disabled=disabled,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12)
            )
        )
    else:  # text variant
        return ft.TextButton(
            text=text,
            icon=icon,
            on_click=on_click,
            disabled=disabled,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12)
            )
        )

def create_metric_card(
    title: str,
    value: str,
    change: str | None = None,
    icon: str | None = None,
    color_type: str = "primary"
) -> ft.Container:
    """Create metric card using simplified styling."""

    # Use Flet's semantic colors
    if color_type == "success":
        accent_color = ft.Colors.GREEN
    elif color_type == "warning":
        accent_color = ft.Colors.ORANGE
    elif color_type == "error":
        accent_color = ft.Colors.RED
    else:
        accent_color = ft.Colors.PRIMARY

    content = ft.Column([
        ft.Row([
            ft.Icon(icon, size=32, color=accent_color) if icon else ft.Container(),
            ft.Text(title, style=ft.TextThemeStyle.TITLE_MEDIUM),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Text(value, style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight=ft.FontWeight.BOLD),
        ft.Text(change, style=ft.TextThemeStyle.BODY_SMALL, color=accent_color) if change else ft.Container()
    ], spacing=8)

    return create_modern_card(content)

def create_status_badge(status: str, variant: str = "filled") -> ft.Container:
    """Create status badge using Flet's semantic colors."""

    # Use Flet's built-in status colors
    if status.lower() in {"active", "online", "success"}:
        color = ft.Colors.GREEN
        bg_color = ft.Colors.with_opacity(0.1, ft.Colors.GREEN)
    elif status.lower() in {"warning", "pending"}:
        color = ft.Colors.ORANGE
        bg_color = ft.Colors.with_opacity(0.1, ft.Colors.ORANGE)
    elif status.lower() in {"error", "offline", "failed"}:
        color = ft.Colors.RED
        bg_color = ft.Colors.with_opacity(0.1, ft.Colors.RED)
    else:
        color = ft.Colors.BLUE
        bg_color = ft.Colors.with_opacity(0.1, ft.Colors.BLUE)

    return ft.Container(
        content=ft.Text(
            status,
            style=ft.TextThemeStyle.LABEL_SMALL,
            color=color if variant == "outlined" else ft.Colors.WHITE,
            weight=ft.FontWeight.W_500
        ),
        bgcolor=ft.Colors.TRANSPARENT if variant == "outlined" else color,
        border=ft.border.all(1, color) if variant == "outlined" else None,
        border_radius=12,
        padding=ft.padding.symmetric(horizontal=8, vertical=4)
    )

def toggle_theme_mode(page: ft.Page):
    """Toggle between light and dark theme."""
    if page.theme_mode == ft.ThemeMode.LIGHT:
        page.theme_mode = ft.ThemeMode.DARK
    elif page.theme_mode == ft.ThemeMode.DARK:
        page.theme_mode = ft.ThemeMode.SYSTEM
    else:
        page.theme_mode = ft.ThemeMode.LIGHT
    page.update()

def create_section_divider(title: str | None = None) -> ft.Container:
    """Create section divider with optional title."""
    if title:
        return ft.Container(
            content=ft.Row([
                # Divider has no 'expand' param in some stubs; wrap in Container for expansion
                ft.Container(content=ft.Divider(height=1), expand=True),
                ft.Text(title, style=ft.TextThemeStyle.LABEL_LARGE, color=ft.Colors.OUTLINE),
                ft.Container(content=ft.Divider(height=1), expand=True)
            ], alignment=ft.MainAxisAlignment.CENTER),
            margin=ft.margin.symmetric(vertical=16)
        )
    else:
        return ft.Container(
            content=ft.Divider(height=1),
            margin=ft.margin.symmetric(vertical=16)
        )

def create_loading_indicator(text: str = "Loading...") -> ft.Container:
    """Create loading indicator using Flet's built-in progress ring."""
    return ft.Container(
        content=ft.Column([
            ft.ProgressRing(width=32, height=32),
            ft.Text(text, style=ft.TextThemeStyle.BODY_MEDIUM)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        alignment=ft.alignment.center,
        padding=ft.padding.all(20)
    )

# Design tokens for compatibility with ui_components.py
def get_design_tokens() -> dict:
    """Return simplified design tokens using Flet's built-in values."""
    return {
        "spacing": {
            "xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32, "2xl": 48
        },
        "radii": {
            "none": 0, "sm": 4, "md": 8, "lg": 12, "xl": 16, "2xl": 24
        },
        "type": {
            "body": {"size": 14, "weight": ft.FontWeight.W_400},
            "heading": {"size": 20, "weight": ft.FontWeight.W_600},
            "caption": {"size": 12, "weight": ft.FontWeight.W_400}
        }
    }

# Triple design system helper functions
def create_material_card(content: ft.Control) -> ft.Container:
    """Create Material Design 3 card with elevation."""
    return ft.Container(
        content=content,
        bgcolor=ft.Colors.SURFACE,
        border_radius=12,
        padding=ft.padding.all(16),
        shadow=ft.BoxShadow(
            blur_radius=3,
            offset=ft.Offset(0, 1),
            color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK)
        )
    )

def create_neumorphic_container(
    content: ft.Control,
    effect_type: str = "raised",  # "raised" or "inset"
    hover_effect: bool = True,
    intensity: Literal["pronounced", "moderate", "subtle"] = "moderate"
) -> ft.Container:
    """
    Create neumorphic container with dual shadow effects.

    Args:
        content: The control to wrap in neumorphic styling
        effect_type: "raised" for elevated look, "inset" for pressed look
        hover_effect: Enable scale animation on hover (GPU-accelerated)
        intensity: Shadow intensity - "pronounced" (40-45%), "moderate" (30%), "subtle" (20%)

    Performance: Uses pre-computed shadow constants for zero-allocation overhead
    """
    # Use pre-computed shadows for performance
    if effect_type == "inset":
        shadows = INSET_NEUMORPHIC_SHADOWS
    elif intensity == "pronounced":
        shadows = PRONOUNCED_NEUMORPHIC_SHADOWS
    elif intensity == "moderate":
        shadows = MODERATE_NEUMORPHIC_SHADOWS
    else:  # subtle
        shadows = SUBTLE_NEUMORPHIC_SHADOWS

    return ft.Container(
        content=content,
        bgcolor=ft.Colors.SURFACE,
        border_radius=20,
        padding=ft.padding.all(24),
        shadow=shadows,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT_CUBIC) if hover_effect else None,
        animate_scale=ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC) if hover_effect else None
    )

def create_neumorphic_metric_card(
    content: ft.Control,
    intensity: Literal["pronounced", "moderate", "subtle"] = "pronounced",
    enable_hover: bool = True
) -> ft.Container:
    """
    Create neumorphic metric card optimized for dashboard metrics.

    Args:
        content: The metric content (typically Text/Icon combinations)
        intensity: Shadow intensity - "pronounced" (40-45%) for primary metrics
        enable_hover: Enable subtle scale animation on hover

    Features:
        - Pre-computed shadows for performance
        - GPU-accelerated scale animation (1.0 -> 1.02)
        - Optimized for frequent updates (uses control.update() pattern)
    """
    # Select shadow intensity
    if intensity == "pronounced":
        shadows = PRONOUNCED_NEUMORPHIC_SHADOWS
    elif intensity == "moderate":
        shadows = MODERATE_NEUMORPHIC_SHADOWS
    else:
        shadows = SUBTLE_NEUMORPHIC_SHADOWS

    container = ft.Container(
        content=content,
        bgcolor=ft.Colors.SURFACE,
        border_radius=16,
        padding=ft.padding.all(20),
        shadow=shadows,
        animate_scale=ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC) if enable_hover else None
    )

    if enable_hover:
        # GPU-accelerated hover effect
        def on_hover(e):
            container.scale = 1.02 if e.data == "true" else 1.0
            container.update()

        container.on_hover = on_hover

    return container

def create_glassmorphic_container(
    content: ft.Control,
    intensity: Literal["subtle", "moderate", "strong"] = "moderate"
) -> ft.Container:
    """
    Create glassmorphic container with blur and transparency.

    Args:
        content: The control to wrap in glassmorphic styling
        intensity: Glass effect intensity - "subtle" (20%), "moderate" (25%), "strong" (30%)

    Performance: Uses pre-computed configuration constants for optimal access
    """
    # Use pre-computed glass configurations
    if intensity == "strong":
        config = GLASS_STRONG
    elif intensity == "moderate":
        config = GLASS_MODERATE
    else:
        config = GLASS_SUBTLE

    return ft.Container(
        content=content,
        border_radius=16,
        padding=ft.padding.all(20),
        bgcolor=ft.Colors.with_opacity(config["bg_opacity"], ft.Colors.SURFACE),
        border=ft.border.all(1, ft.Colors.with_opacity(config["border_opacity"], ft.Colors.OUTLINE)),
        blur=ft.Blur(sigma_x=config["blur"], sigma_y=config["blur"])
    )

def create_glassmorphic_overlay(
    content: ft.Control,
    intensity: Literal["subtle", "moderate", "strong"] = "strong"
) -> ft.Container:
    """
    Create glassmorphic overlay optimized for modal/dialog overlays.

    Args:
        content: The overlay content
        intensity: Glass effect intensity - "strong" (30%) recommended for focal overlays

    Features:
        - Optimized blur application for performance
        - Higher opacity for clear content visibility
        - Designed for floating elements that need focus
    """
    # Use pre-computed glass configurations
    if intensity == "strong":
        config = GLASS_STRONG
    elif intensity == "moderate":
        config = GLASS_MODERATE
    else:
        config = GLASS_SUBTLE

    return ft.Container(
        content=content,
        border_radius=20,
        padding=ft.padding.all(24),
        bgcolor=ft.Colors.with_opacity(config["bg_opacity"], ft.Colors.SURFACE),
        border=ft.border.all(1.5, ft.Colors.with_opacity(config["border_opacity"], ft.Colors.OUTLINE)),
        blur=ft.Blur(sigma_x=config["blur"], sigma_y=config["blur"]),
        shadow=[
            ft.BoxShadow(
                blur_radius=20,
                spread_radius=0,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(0, 10)
            )
        ]
    )

def create_hybrid_gauge_container(content: ft.Control) -> ft.Container:
    """
    Create hybrid container combining neumorphic base + glassmorphic overlay.

    Args:
        content: Gauge or chart content to display

    Design Philosophy:
        - Neumorphic base provides tactile structure (40% intensity)
        - Glassmorphic overlay adds depth and focus (25% intensity)
        - Optimized for dashboard gauges and data visualizations

    Performance: Pre-computed shadows and glass configs ensure zero overhead
    """
    # Glassmorphic overlay on top
    glass_overlay = ft.Container(
        content=content,
        border_radius=16,
        padding=ft.padding.all(16),
        bgcolor=ft.Colors.with_opacity(GLASS_MODERATE["bg_opacity"], ft.Colors.SURFACE),
        border=ft.border.all(1, ft.Colors.with_opacity(GLASS_MODERATE["border_opacity"], ft.Colors.OUTLINE)),
        blur=ft.Blur(sigma_x=GLASS_MODERATE["blur"], sigma_y=GLASS_MODERATE["blur"])
    )

    # Neumorphic base container
    return ft.Container(
        content=glass_overlay,
        bgcolor=ft.Colors.SURFACE,
        border_radius=20,
        padding=ft.padding.all(8),
        shadow=PRONOUNCED_NEUMORPHIC_SHADOWS
    )

def get_neumorphic_shadows(
    effect_type: str = "raised",
    intensity: Literal["pronounced", "moderate", "subtle"] = "moderate"
) -> list[ft.BoxShadow]:
    """
    Get neumorphic shadow configuration.

    Args:
        effect_type: "raised" for elevated, "inset" for pressed (legacy parameter)
        intensity: Shadow intensity - "pronounced" (40-45%), "moderate" (30%), "subtle" (20%)

    Returns:
        List of pre-computed BoxShadow objects for performance

    Performance: Returns reference to module-level constants (zero allocation)
    """
    # Use pre-computed shadows for performance
    if effect_type == "inset":
        return INSET_NEUMORPHIC_SHADOWS
    elif intensity == "pronounced":
        return PRONOUNCED_NEUMORPHIC_SHADOWS
    elif intensity == "moderate":
        return MODERATE_NEUMORPHIC_SHADOWS
    else:
        return SUBTLE_NEUMORPHIC_SHADOWS

def create_glassmorphic_status_badge(text: str, color: str = ft.Colors.BLUE) -> ft.Container:
    """Create glassmorphic status badge with blur effect."""
    return ft.Container(
        content=ft.Text(
            text,
            size=12,
            weight=ft.FontWeight.W_600,
            color=color
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.1, color),
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, color)),
        blur=ft.Blur(sigma_x=10, sigma_y=10)
    )


def create_skeleton_loader(height: int = 20, width: int | None = None, radius: int = 8) -> ft.Container:
    """Create a skeleton loader for loading states."""
    return ft.Container(
        height=height,
        width=width,
        border_radius=radius,
    # SURFACE_VARIANT not available; approximate with SURFACE tint
    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SURFACE),
        animate=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    )

# ========================================================================================
# MICRO-ANIMATION HELPERS
# Performance: GPU-accelerated properties only (scale, opacity, rotation)
# ========================================================================================

def create_hover_animation(
    scale_from: float = 1.0,
    scale_to: float = 1.02,
    duration_ms: int = 180
) -> ft.Animation:
    """
    Create hover animation configuration for interactive elements.

    Args:
        scale_from: Starting scale (typically 1.0)
        scale_to: Target scale on hover (1.02 = 2% larger)
        duration_ms: Animation duration in milliseconds (180ms recommended)

    Returns:
        Animation object configured for smooth GPU-accelerated scaling

    Performance: Uses EASE_OUT_CUBIC for natural deceleration
    Usage: Apply to container.animate_scale property
    """
    return ft.Animation(duration_ms, ft.AnimationCurve.EASE_OUT_CUBIC)

def create_press_animation(duration_ms: int = 100) -> ft.Animation:
    """
    Create press/click animation configuration.

    Args:
        duration_ms: Animation duration (100ms recommended for snappy feedback)

    Returns:
        Animation object configured for quick responsive feedback

    Performance: Uses EASE_IN_OUT for balanced acceleration
    Usage: Apply to button press effects with scale: 1.0 -> 0.98 -> 1.0
    """
    return ft.Animation(duration_ms, ft.AnimationCurve.EASE_IN_OUT)

def create_fade_animation(duration_ms: int = 300) -> ft.Animation:
    """
    Create fade in/out animation configuration.

    Args:
        duration_ms: Animation duration (300ms recommended for smooth fades)

    Returns:
        Animation object configured for opacity transitions

    Performance: GPU-accelerated opacity changes
    Usage: Apply to container.animate_opacity property
    """
    return ft.Animation(duration_ms, ft.AnimationCurve.EASE_OUT)

def create_slide_animation(duration_ms: int = 250) -> ft.Animation:
    """
    Create slide animation configuration for transitions.

    Args:
        duration_ms: Animation duration (250ms recommended for smooth slides)

    Returns:
        Animation object configured for position-based animations

    Performance: Uses DECELERATE curve for natural motion
    Usage: Apply to container.animate_position property
    """
    return ft.Animation(duration_ms, ft.AnimationCurve.DECELERATE)

def apply_interactive_animations(
    container: ft.Container,
    enable_hover: bool = True,
    enable_press: bool = False,
    hover_scale: float = 1.02
) -> ft.Container:
    """
    Apply interactive animations to a container.

    Args:
        container: The container to enhance with animations
        enable_hover: Enable hover scale effect
        enable_press: Enable press feedback effect
        hover_scale: Target scale on hover (1.02 = 2% larger)

    Returns:
        The same container with animations applied (for chaining)

    Usage:
        container = apply_interactive_animations(
            ft.Container(...),
            enable_hover=True,
            hover_scale=1.03
        )
    """
    if enable_hover:
        container.animate_scale = create_hover_animation()

        def on_hover(e):
            container.scale = hover_scale if e.data == "true" else 1.0
            container.update()

        container.on_hover = on_hover

    if enable_press:
        container.animate_scale = create_press_animation()

    return container

# ========================================================================================
# BACKWARD COMPATIBILITY ALIASES
# Maintain compatibility with existing code
# ========================================================================================

setup_modern_theme = setup_sophisticated_theme  # Backward compatibility
create_modern_button_style = themed_button
create_modern_card_container = create_neumorphic_container
create_trend_indicator = create_status_badge
create_text_with_typography = lambda text, typography_type, **kwargs: ft.Text(text, **kwargs)
