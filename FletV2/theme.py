#!/usr/bin/env python3
"""
Sophisticated FletV2 Theme System - Material Design 3 + Neumorphism + Glassmorphism
Flet 0.28.3 implementation with triple design system architecture.
Foundation: Material Design 3 semantic colors and typography
Structure: Neumorphic soft shadows and tactile depth
Focus: Glassmorphic transparency and blur effects
"""

from typing import cast

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

# Neumorphic shadow configurations
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

# Glassmorphic configuration
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
    hover_effect: bool = True
) -> ft.Container:
    """Create neumorphic container with dual shadow effects."""
    shadow_config = NEUMORPHIC_SHADOWS[effect_type]

    shadows = [
        # Dark shadow
        ft.BoxShadow(
            spread_radius=1,
            blur_radius=shadow_config["dark_shadow"]["blur"],
            color=ft.Colors.with_opacity(
                shadow_config["dark_shadow"]["opacity"],
                shadow_config["dark_shadow"]["color"]
            ),
            offset=ft.Offset(*shadow_config["dark_shadow"]["offset"]),
            blur_style=ft.ShadowBlurStyle.INNER if effect_type == "inset" else ft.ShadowBlurStyle.NORMAL
        ),
        # Light highlight
        ft.BoxShadow(
            spread_radius=1,
            blur_radius=shadow_config["light_shadow"]["blur"],
            color=ft.Colors.with_opacity(
                shadow_config["light_shadow"]["opacity"],
                shadow_config["light_shadow"]["color"]
            ),
            offset=ft.Offset(*shadow_config["light_shadow"]["offset"]),
            blur_style=ft.ShadowBlurStyle.INNER if effect_type == "inset" else ft.ShadowBlurStyle.NORMAL
        ),
    ]

    return ft.Container(
        content=content,
        bgcolor=ft.Colors.SURFACE,
        border_radius=20,
        padding=ft.padding.all(24),
        shadow=shadows,
        animate=ft.Animation(200) if hover_effect else None
    )

def create_glassmorphic_container(
    content: ft.Control,
    intensity: str = "medium"  # "light", "medium", "strong"
) -> ft.Container:
    """Create glassmorphic container with blur and transparency."""
    intensity_config = {
        "light": {"opacity": 0.05, "border_opacity": 0.08, "blur": 10},
        "medium": {"opacity": 0.08, "border_opacity": 0.12, "blur": 15},
        "strong": {"opacity": 0.12, "border_opacity": 0.18, "blur": 20}
    }

    config = intensity_config[intensity]

    return ft.Container(
        content=content,
        border_radius=16,
        padding=ft.padding.all(20),
        bgcolor=ft.Colors.with_opacity(config["opacity"], ft.Colors.SURFACE),
        border=ft.border.all(1, ft.Colors.with_opacity(config["border_opacity"], ft.Colors.OUTLINE)),
        blur=ft.Blur(sigma_x=config["blur"], sigma_y=config["blur"])
    )

def get_neumorphic_shadows(effect_type: str = "raised") -> list[ft.BoxShadow]:
    """Get neumorphic shadow configuration."""
    shadow_config = NEUMORPHIC_SHADOWS[effect_type]
    return [
        ft.BoxShadow(
            spread_radius=1,
            blur_radius=shadow_config["dark_shadow"]["blur"],
            color=ft.Colors.with_opacity(
                shadow_config["dark_shadow"]["opacity"],
                shadow_config["dark_shadow"]["color"]
            ),
            offset=ft.Offset(*shadow_config["dark_shadow"]["offset"]),
            blur_style=ft.ShadowBlurStyle.INNER if effect_type == "inset" else ft.ShadowBlurStyle.NORMAL
        ),
        ft.BoxShadow(
            spread_radius=1,
            blur_radius=shadow_config["light_shadow"]["blur"],
            color=ft.Colors.with_opacity(
                shadow_config["light_shadow"]["opacity"],
                shadow_config["light_shadow"]["color"]
            ),
            offset=ft.Offset(*shadow_config["light_shadow"]["offset"]),
            blur_style=ft.ShadowBlurStyle.INNER if effect_type == "inset" else ft.ShadowBlurStyle.NORMAL
        ),
    ]

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

# Maintain compatibility with existing code by providing aliases
setup_modern_theme = setup_sophisticated_theme  # Backward compatibility
create_modern_button_style = themed_button
create_modern_card_container = create_neumorphic_container
create_trend_indicator = create_status_badge
create_text_with_typography = lambda text, typography_type, **kwargs: ft.Text(text, **kwargs)
create_text_with_typography = lambda text, typography_type, **kwargs: ft.Text(text, **kwargs)
