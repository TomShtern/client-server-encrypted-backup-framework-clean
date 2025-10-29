#!/usr/bin/env python3
"""
Sophisticated Tri-Style Component System for Flet 0.28.3
Harmoniously combines Neumorphism + Glassmorphism + Material Design 3

Design Hierarchy:
- Material Design 3: Foundation (buttons, icons, colors, typography)
- Neumorphism: Structure (main panels, container backgrounds)
- Glassmorphism: Focal points (floating cards, overlays)

This system creates visual depth and sophistication while maintaining excellent UX.
"""

import inspect
from typing import Any

import flet as ft

# ==================== COLOR SYSTEM FOR TRI-STYLE HARMONY ====================

class TriStyleColors:
    """Cohesive color system that makes all three styles work together."""

    # Material Design 3 semantic colors (foundation)
    MD3_PRIMARY = ft.Colors.BLUE_600
    MD3_SECONDARY = ft.Colors.PURPLE_600
    MD3_SURFACE = ft.Colors.SURFACE
    MD3_ON_SURFACE = ft.Colors.ON_SURFACE
    MD3_OUTLINE = ft.Colors.OUTLINE

    # Neumorphism colors (soft, muted)
    NEURO_LIGHT = "#F0F4F8"      # Light background for neumorphic surfaces
    NEURO_DARK = "#1A202C"       # Dark background for neumorphic surfaces
    NEURO_SHADOW_LIGHT = "#C7D2FE"   # Light shadow for depth
    NEURO_SHADOW_DARK = "#0F172A"    # Dark shadow for depth
    NEURO_HIGHLIGHT = "#FFFFFF"      # Highlight for raised effect

    # Glassmorphism colors (transparent, bright)
    GLASS_BASE_LIGHT = "#FFFFFF"     # Base glass color for light theme
    GLASS_BASE_DARK = "#1E293B"      # Base glass color for dark theme
    GLASS_ACCENT_BLUE = "#3B82F6"    # Accent color with transparency
    GLASS_ACCENT_PURPLE = "#8B5CF6"   # Secondary accent
    GLASS_ACCENT_GREEN = "#10B981"    # Success accent

    @staticmethod
    def get_neuro_background(is_dark: bool = False) -> str:
        """Get appropriate neumorphic background color."""
        return TriStyleColors.NEURO_DARK if is_dark else TriStyleColors.NEURO_LIGHT

    @staticmethod
    def get_glass_background(is_dark: bool = False, opacity: float = 0.1) -> str:
        """Get glassmorphic background with proper opacity."""
        base = TriStyleColors.GLASS_BASE_DARK if is_dark else TriStyleColors.GLASS_BASE_LIGHT
        return ft.Colors.with_opacity(opacity, base)

# ==================== SHADOW HIERARCHY SYSTEM ====================

class ShadowSystem:
    """Sophisticated shadow hierarchy for visual depth."""

    @staticmethod
    def neuro_inset_shadow(intensity: float = 1.0) -> list[ft.BoxShadow]:
        """Create inset neumorphic shadow effect."""
        return [
            # Inset shadow (top-left light)
            ft.BoxShadow(
                spread_radius=-2,
                blur_radius=8 * intensity,
                color=ft.Colors.with_opacity(0.4, TriStyleColors.NEURO_HIGHLIGHT),
                offset=ft.Offset(-4 * intensity, -4 * intensity)
            ),
            # Inset shadow (bottom-right dark)
            ft.BoxShadow(
                spread_radius=-2,
                blur_radius=12 * intensity,
                color=ft.Colors.with_opacity(0.3, TriStyleColors.NEURO_SHADOW_LIGHT),
                offset=ft.Offset(4 * intensity, 4 * intensity)
            )
        ]

    @staticmethod
    def neuro_raised_shadow(intensity: float = 1.0) -> list[ft.BoxShadow]:
        """Create raised neumorphic shadow effect."""
        return [
            # Raised shadow (soft, light)
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=16 * intensity,
                color=ft.Colors.with_opacity(0.15, TriStyleColors.NEURO_SHADOW_LIGHT),
                offset=ft.Offset(0, 4 * intensity)
            ),
            # Raised shadow (crisp, focused)
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=6 * intensity,
                color=ft.Colors.with_opacity(0.1, TriStyleColors.NEURO_SHADOW_DARK),
                offset=ft.Offset(0, 2 * intensity)
            )
        ]

    @staticmethod
    def glass_shadow(intensity: float = 1.0, color: str = TriStyleColors.GLASS_ACCENT_BLUE) -> ft.BoxShadow:
        """Create glassmorphic glow shadow."""
        return ft.BoxShadow(
            spread_radius=0,
            blur_radius=20 * intensity,
            color=ft.Colors.with_opacity(0.3 * intensity, color),
            offset=ft.Offset(0, 8 * intensity)
        )

# ==================== NEUMORPHIC COMPONENTS (STRUCTURE) ====================

def create_neuro_container(
    content: ft.Control,
    width: float | None = None,
    height: float | None = None,
    is_inset: bool = False,
    is_dark_theme: bool = False,
    border_radius: float = 20,
    padding: float | ft.padding.Padding = 24
) -> ft.Container:
    """
    Create neumorphic container with soft shadows and subtle depth.
    Perfect for main panels and structural elements.
    """

    bg_color = TriStyleColors.get_neuro_background(is_dark_theme)
    shadow_list = ShadowSystem.neuro_inset_shadow(0.8) if is_inset else ShadowSystem.neuro_raised_shadow(0.8)

    return ft.Container(
        content=content,
        width=width,
        height=height,
        bgcolor=bg_color,
        border_radius=border_radius,
        padding=padding if isinstance(padding, ft.padding.Padding) else ft.padding.all(padding),
        # Note: Flet 0.28.3 only supports single BoxShadow, use the primary shadow
        shadow=shadow_list[0] if shadow_list else None,
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
    )

def create_neuro_button(
    text: str,
    on_click: Any | None = None,
    icon: str | None = None,
    is_dark_theme: bool = False,
    color: str = TriStyleColors.MD3_PRIMARY,
    width: float | None = None
) -> ft.Container:
    """
    Create neumorphic button with tactile pressed effect.
    Combines neumorphic structure with Material Design 3 semantics.
    """

    button_content = ft.Row([
        ft.Icon(icon, color=color, size=20) if icon else ft.Container(width=0),
        ft.Text(
            text,
            color=color,
            size=14,
            weight=ft.FontWeight.W_600,
            font_family="Inter"
        )
    ], spacing=8, alignment=ft.MainAxisAlignment.CENTER)

    async def handle_click(e):
        # Animate pressed effect
        e.control.scale = 0.98
        e.control.update()

        # Call original handler
        if callable(on_click):
            if inspect.iscoroutinefunction(on_click):
                await on_click(e)
            else:
                result = on_click(e)
                if inspect.isawaitable(result):
                    await result

        # Restore scale
        e.control.scale = 1.0
        e.control.update()

    return ft.Container(
        content=button_content,
        width=width,
        bgcolor=TriStyleColors.get_neuro_background(is_dark_theme),
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        shadow=ShadowSystem.neuro_raised_shadow(0.6)[0],
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(100, ft.AnimationCurve.EASE_IN_OUT),
        on_click=handle_click,
        scale=1.0
    )

def create_neuro_metric_panel(
    title: str,
    value: str,
    subtitle: str | None = None,
    icon: str | None = None,
    color: str = TriStyleColors.MD3_PRIMARY,
    is_dark_theme: bool = False
) -> ft.Container:
    """
    Create neumorphic metric panel for dashboard KPIs.
    Provides structural foundation with subtle depth.
    """

    content_rows = [
        # Header row
        ft.Row([
            ft.Icon(icon, color=color, size=24) if icon else ft.Container(),
            ft.Text(
                title,
                size=14,
                weight=ft.FontWeight.W_600,
                color=ft.Colors.ON_SURFACE,
                expand=True
            )
        ], spacing=12),

        # Value row
        ft.Container(
            content=ft.Text(
                value,
                size=32,
                weight=ft.FontWeight.BOLD,
                color=color,
                font_family="Inter"
            ),
            margin=ft.margin.only(top=8, bottom=4)
        )
    ]

    if subtitle:
        content_rows.append(
            ft.Text(
                subtitle,
                size=12,
                color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE)
            )
        )

    return create_neuro_container(
        content=ft.Column(content_rows, spacing=6),
        is_dark_theme=is_dark_theme,
        border_radius=18,
        padding=20
    )

# ==================== GLASSMORPHIC COMPONENTS (FOCAL POINTS) ====================

def create_glass_card(
    content: ft.Control,
    width: float | None = None,
    height: float | None = None,
    accent_color: str = TriStyleColors.GLASS_ACCENT_BLUE,
    backdrop_opacity: float = 0.1,
    border_opacity: float = 0.2,
    glow_intensity: float = 1.0,
    border_radius: float = 24,
    padding: float | ft.padding.Padding = 24,
    is_dark_theme: bool = False
) -> ft.Container:
    """
    Create glassmorphic floating card with transparency and glow.
    Perfect for focal points and important content overlays.
    """

    glass_bg = TriStyleColors.get_glass_background(is_dark_theme, backdrop_opacity)
    border_color = ft.Colors.with_opacity(border_opacity, accent_color)

    return ft.Container(
        content=content,
        width=width,
        height=height,
        bgcolor=glass_bg,
        border_radius=border_radius,
        padding=padding if isinstance(padding, ft.padding.Padding) else ft.padding.all(padding),
        border=ft.border.all(1.5, border_color),
        shadow=ShadowSystem.glass_shadow(glow_intensity, accent_color),
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        animate_opacity=ft.Animation(250, ft.AnimationCurve.EASE_IN_OUT),
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
    )

def create_glass_hero_card(
    title: str,
    value: str,
    trend: str | None = None,
    icon: str = ft.Icons.DASHBOARD,
    accent_color: str = TriStyleColors.GLASS_ACCENT_BLUE,
    is_dark_theme: bool = False
) -> ft.Container:
    """
    Create glassmorphic hero card for dashboard top metrics.
    Draws attention while maintaining visual hierarchy.
    """

    # Trend indicator
    trend_component = ft.Container()
    if trend:
        trend_color = (ft.Colors.GREEN_400 if trend.startswith('+') and trend != '+0'
                      else ft.Colors.RED_400 if trend.startswith('-')
                      else ft.Colors.BLUE_GREY_400)

        trend_component = ft.Container(
            content=ft.Text(
                trend,
                size=11,
                weight=ft.FontWeight.BOLD,
                color=trend_color
            ),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            border_radius=16,
            bgcolor=ft.Colors.with_opacity(0.15, trend_color),
            border=ft.border.all(1, ft.Colors.with_opacity(0.3, trend_color))
        )

    card_content = ft.Column([
        # Header with icon and trend
        ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=22, color=accent_color),
                    padding=8,
                    border_radius=12,
                    bgcolor=ft.Colors.with_opacity(0.15, accent_color),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.3, accent_color))
                ),
                ft.Text(
                    title,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.WHITE if is_dark_theme else ft.Colors.ON_SURFACE
                )
            ], spacing=10),
            trend_component
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

        # Large value with glow effect
        ft.Container(
            content=ft.Text(
                value,
                size=36,
                weight=ft.FontWeight.BOLD,
                color=accent_color,
                font_family="Inter"
            ),
            animate_scale=ft.Animation(400, ft.AnimationCurve.BOUNCE_OUT),
            scale=1
        ),

        # Glass progress indicator
        ft.Container(
            width=60,
            height=4,
            border_radius=2,
            bgcolor=ft.Colors.with_opacity(0.2, accent_color),
            content=ft.Container(
                width=30,
                height=4,
                border_radius=2,
                bgcolor=accent_color,
                shadow=ShadowSystem.glass_shadow(0.5, accent_color),
                animate_size=ft.Animation(800, ft.AnimationCurve.EASE_OUT)
            ),
            alignment=ft.alignment.center_left
        )
    ], spacing=14)

    return create_glass_card(
        content=card_content,
        accent_color=accent_color,
        backdrop_opacity=0.12,
        border_opacity=0.25,
        glow_intensity=0.8,
        is_dark_theme=is_dark_theme
    )

def create_glass_overlay_panel(
    content: ft.Control,
    title: str | None = None,
    accent_color: str = TriStyleColors.GLASS_ACCENT_PURPLE,
    is_dark_theme: bool = False,
    width: float | None = None,
    height: float | None = None
) -> ft.Container:
    """
    Create glassmorphic overlay panel for floating content.
    Perfect for modal dialogs, popups, and floating menus.
    """

    panel_content = content
    if title:
        header = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.LAYERS, color=accent_color, size=20),
                    padding=8,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.15, accent_color),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.3, accent_color))
                ),
                ft.Text(
                    title,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE if is_dark_theme else ft.Colors.ON_SURFACE
                )
            ], spacing=12),
            margin=ft.margin.only(bottom=16)
        )

        panel_content = ft.Column([header, content], spacing=0)

    return create_glass_card(
        content=panel_content,
        width=width,
        height=height,
        accent_color=accent_color,
        backdrop_opacity=0.08,
        border_opacity=0.2,
        glow_intensity=1.2,
        border_radius=20,
        is_dark_theme=is_dark_theme
    )

# ==================== MATERIAL DESIGN 3 INTERACTIVE ELEMENTS ====================

def create_md3_action_button(
    text: str,
    on_click: Any | None = None,
    icon: str | None = None,
    variant: str = "filled",  # filled, tonal, outlined, text
    color: str = TriStyleColors.MD3_PRIMARY,
    disabled: bool = False
) -> ft.ElevatedButton:
    """
    Create Material Design 3 action button with proper semantics.
    Foundation for all interactive elements.
    """

    button_style = ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=12),
        bgcolor={
            ft.ControlState.DEFAULT: color if variant == "filled" else ft.Colors.with_opacity(0.12, color),
            ft.ControlState.HOVERED: ft.Colors.with_opacity(0.9, color) if variant == "filled" else ft.Colors.with_opacity(0.16, color),
            ft.ControlState.PRESSED: ft.Colors.with_opacity(0.8, color) if variant == "filled" else ft.Colors.with_opacity(0.20, color)
        },
        color={
            ft.ControlState.DEFAULT: ft.Colors.WHITE if variant == "filled" else color,
            ft.ControlState.DISABLED: ft.Colors.OUTLINE
        },
        elevation={
            ft.ControlState.DEFAULT: 2 if variant == "filled" else 0,
            ft.ControlState.HOVERED: 4 if variant == "filled" else 1,
            ft.ControlState.PRESSED: 1 if variant == "filled" else 0
        } if variant == "filled" else {},
        animation_duration=150
    )

    if variant == "outlined":
        button_style.side = {
            ft.ControlState.DEFAULT: ft.BorderSide(1, color),
            ft.ControlState.HOVERED: ft.BorderSide(1.5, color)
        }

    return ft.ElevatedButton(
        text=text,
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        style=button_style
    )

def create_md3_icon_button(
    icon: str,
    on_click: Any | None = None,
    tooltip: str | None = None,
    variant: str = "standard",  # standard, filled, tonal, outlined
    color: str = TriStyleColors.MD3_PRIMARY,
    size: float = 24
) -> ft.IconButton:
    """
    Create Material Design 3 icon button with proper touch targets.
    Perfect for toolbar actions and quick controls.
    """

    if variant == "filled":
        icon_style = ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: color,
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.9, color)
            },
            color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
            shape=ft.CircleBorder()
        )
    elif variant == "tonal":
        icon_style = ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: ft.Colors.with_opacity(0.12, color),
                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.16, color)
            },
            color={ft.ControlState.DEFAULT: color},
            shape=ft.CircleBorder()
        )
    elif variant == "outlined":
        icon_style = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: color},
            side={ft.ControlState.DEFAULT: ft.BorderSide(1, ft.Colors.OUTLINE)},
            shape=ft.CircleBorder()
        )
    else:  # standard
        icon_style = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: color},
            shape=ft.CircleBorder()
        )

    return ft.IconButton(
        icon=icon,
        icon_size=size,
        tooltip=tooltip,
        on_click=on_click,
        style=icon_style
    )

def create_md3_fab(
    icon: str,
    on_click: Any | None = None,
    label: str | None = None,
    variant: str = "primary",  # primary, secondary, surface, tertiary
    size: str = "normal"  # small, normal, large
) -> ft.FloatingActionButton:
    """
    Create Material Design 3 floating action button.
    Maintains MD3 semantics while working with tri-style system.
    """

    color_map = {
        "primary": TriStyleColors.MD3_PRIMARY,
        "secondary": TriStyleColors.MD3_SECONDARY,
        "surface": ft.Colors.SURFACE,
        "tertiary": TriStyleColors.GLASS_ACCENT_GREEN
    }

    size_map = {
        "small": (40, 40, 20),
        "normal": (56, 56, 24),
        "large": (96, 96, 28)
    }

    bg_color = color_map.get(variant, TriStyleColors.MD3_PRIMARY)
    width, height, _icon_size = size_map.get(size, size_map["normal"])

    return ft.FloatingActionButton(
        icon=icon,
        text=label,
        bgcolor=bg_color,
        foreground_color=ft.Colors.WHITE if variant in ["primary", "secondary", "tertiary"] else ft.Colors.ON_SURFACE,
        width=width,
        height=height,
        shape=ft.CircleBorder() if not label else ft.RoundedRectangleBorder(radius=16),
        on_click=on_click
    )

# ==================== COHESIVE DASHBOARD INTEGRATION ====================

def create_tri_style_dashboard_section(
    title: str,
    content: ft.Control,
    style_type: str = "neuro",  # neuro, glass, md3
    accent_color: str = TriStyleColors.MD3_PRIMARY,
    is_dark_theme: bool = False,
    width: float | None = None,
    height: float | None = None
) -> ft.Container:
    """
    Create dashboard section using appropriate tri-style component.
    Automatically applies the correct style based on content type.
    """

    # Create header with MD3 typography
    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.DASHBOARD, color=accent_color, size=24),
            ft.Text(
                title,
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE if is_dark_theme else ft.Colors.ON_SURFACE,
                font_family="Inter"
            )
        ], spacing=12),
        margin=ft.margin.only(bottom=16)
    )

    section_content = ft.Column([header, content], spacing=0)

    if style_type == "glass":
        return create_glass_card(
            content=section_content,
            width=width,
            height=height,
            accent_color=accent_color,
            is_dark_theme=is_dark_theme
        )
    elif style_type == "md3":
        return ft.Container(
            content=section_content,
            width=width,
            height=height,
            bgcolor=ft.Colors.SURFACE,
            border_radius=16,
            padding=ft.padding.all(24),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.08, ft.Colors.SHADOW),
                offset=ft.Offset(0, 2)
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )
    else:  # neuro
        return create_neuro_container(
            content=section_content,
            width=width,
            height=height,
            is_dark_theme=is_dark_theme,
            border_radius=18,
            padding=24
        )

# ==================== USAGE EXAMPLES AND INTEGRATION HELPERS ====================

def demo_tri_style_components(page: ft.Page) -> ft.Column:
    """
    Demonstration of how to use tri-style components together.
    Shows the visual hierarchy and integration patterns.
    """

    is_dark = page.theme_mode == ft.ThemeMode.DARK

    return ft.Column([
        # Hero section with glassmorphic cards (FOCAL POINTS)
        ft.Text("Hero Metrics (Glassmorphic - Focal Points)", size=16, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow([
            ft.Container(
                content=create_glass_hero_card(
                    title="Active Clients",
                    value="24",
                    trend="+3",
                    icon=ft.Icons.PEOPLE,
                    accent_color=TriStyleColors.GLASS_ACCENT_BLUE,
                    is_dark_theme=is_dark
                ),
                col={"sm": 12, "md": 6, "lg": 3}
            ),
            ft.Container(
                content=create_glass_hero_card(
                    title="Storage Used",
                    value="1.2TB",
                    trend="+5%",
                    icon=ft.Icons.STORAGE,
                    accent_color=TriStyleColors.GLASS_ACCENT_GREEN,
                    is_dark_theme=is_dark
                ),
                col={"sm": 12, "md": 6, "lg": 3}
            ),
        ], spacing=16),

        ft.Divider(height=32),

        # Main content with neumorphic panels (STRUCTURE)
        ft.Text("System Metrics (Neumorphic - Structure)", size=16, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow([
            ft.Container(
                content=create_neuro_metric_panel(
                    title="CPU Usage",
                    value="45%",
                    subtitle="Normal load",
                    icon=ft.Icons.MEMORY,
                    color=TriStyleColors.MD3_PRIMARY,
                    is_dark_theme=is_dark
                ),
                col={"sm": 12, "md": 4, "lg": 4}
            ),
            ft.Container(
                content=create_neuro_metric_panel(
                    title="Memory Usage",
                    value="67%",
                    subtitle="Optimal range",
                    icon=ft.Icons.DEVELOPER_BOARD,
                    color=TriStyleColors.GLASS_ACCENT_GREEN,
                    is_dark_theme=is_dark
                ),
                col={"sm": 12, "md": 4, "lg": 4}
            ),
        ], spacing=16),

        ft.Divider(height=32),

        # Interactive elements with Material Design 3 (FOUNDATION)
        ft.Text("Actions (Material Design 3 - Foundation)", size=16, weight=ft.FontWeight.BOLD),
        ft.Row([
            create_md3_action_button(
                text="Refresh Data",
                icon=ft.Icons.REFRESH,
                variant="filled"
            ),
            create_md3_action_button(
                text="Export Report",
                icon=ft.Icons.DOWNLOAD,
                variant="tonal"
            ),
            create_md3_icon_button(
                icon=ft.Icons.SETTINGS,
                variant="outlined",
                tooltip="Settings"
            ),
            create_md3_fab(
                icon=ft.Icons.ADD,
                variant="primary",
                size="normal"
            )
        ], spacing=12)
    ], spacing=16)

# Export key functions for easy importing
__all__ = [
    'ShadowSystem',
    'TriStyleColors',
    'create_glass_card',
    'create_glass_hero_card',
    'create_glass_overlay_panel',
    'create_md3_action_button',
    'create_md3_fab',
    'create_md3_icon_button',
    'create_neuro_button',
    'create_neuro_container',
    'create_neuro_metric_panel',
    'create_tri_style_dashboard_section',
    'demo_tri_style_components'
]
