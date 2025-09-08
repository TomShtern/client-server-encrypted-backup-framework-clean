#!/usr/bin/env python3
"""
Modern UI Components for FletV2
Enhanced 2025 design polish with sophisticated visual elements and accessibility.

Provides polished, reusable components following 2025 UI/UX best practices.
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any


def create_modern_card(
    title: str, 
    content: ft.Control, 
    icon: Optional[str] = None,
    actions: Optional[List[ft.Control]] = None,
    elevation: int = 3,
    width: Optional[float] = None,
    animate_on_hover: bool = True
) -> ft.Card:
    """
    Create a modern card with 2025 design standards.
    
    Features:
    - Rounded corners (20px)
    - Subtle shadows with hover animation
    - Modern typography
    - Optional icon and actions
    - Accessibility support
    """
    
    # Title row with optional icon
    title_controls = []
    if icon:
        title_controls.append(
            ft.Icon(
                icon, 
                size=24, 
                color=ft.Colors.PRIMARY
            )
        )
        title_controls.append(ft.Container(width=12))  # Spacing
    
    title_controls.append(
        ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.ON_SURFACE,
            style=ft.TextThemeStyle.TITLE_MEDIUM
        )
    )
    
    # Build card content
    card_content = [
        ft.Row(
            controls=title_controls,
            alignment=ft.MainAxisAlignment.START
        ),
        ft.Container(height=16),  # Spacing
        content
    ]
    
    # Add actions if provided
    if actions:
        card_content.extend([
            ft.Container(height=20),  # Spacing
            ft.Row(
                controls=actions,
                alignment=ft.MainAxisAlignment.END,
                spacing=8
            )
        ])
    
    card = ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=card_content,
                spacing=0,
                tight=True
            ),
            padding=ft.Padding(24, 20, 24, 20),
            border_radius=ft.BorderRadius(20, 20, 20, 20)
        ),
        elevation=elevation,
        margin=ft.Margin(8, 8, 8, 8),
        width=width
    )
    
    # Add hover animation
    if animate_on_hover:
        card.content.animate = ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    
    return card


def create_stat_card(
    label: str,
    value: str,
    icon: str,
    color: str = ft.Colors.PRIMARY,
    trend: Optional[str] = None,
    trend_color: str = ft.Colors.GREEN
) -> ft.Card:
    """
    Create a modern statistics card with trend indicators.
    
    Features:
    - Large value display
    - Color-coded icons
    - Optional trend indicators
    - Responsive design
    """
    
    # Main content
    content_controls = [
        ft.Row([
            ft.Icon(
                icon,
                size=32,
                color=color
            ),
            ft.Container(expand=True),  # Spacer
            ft.Text(
                value,
                size=28,
                weight=ft.FontWeight.W_700,
                color=ft.Colors.ON_SURFACE,
                style=ft.TextThemeStyle.HEADLINE_MEDIUM
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        
        ft.Container(height=12),
        
        ft.Row([
            ft.Text(
                label,
                size=14,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.ON_SURFACE_VARIANT,
                style=ft.TextThemeStyle.BODY_MEDIUM
            ),
            ft.Container(expand=True)  # Spacer
        ])
    ]
    
    # Add trend if provided
    if trend:
        content_controls.append(
            ft.Container(
                content=ft.Text(
                    trend,
                    size=12,
                    weight=ft.FontWeight.W_500,
                    color=trend_color,
                    style=ft.TextThemeStyle.LABEL_MEDIUM
                ),
                padding=ft.Padding(8, 4, 8, 4),
                bgcolor=ft.Colors.with_opacity(0.1, trend_color),
                border_radius=ft.BorderRadius(12, 12, 12, 12),
                margin=ft.Margin(0, 8, 0, 0)
            )
        )
    
    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                controls=content_controls,
                spacing=0,
                tight=True
            ),
            padding=ft.Padding(20, 16, 20, 16),
            border_radius=ft.BorderRadius(16, 16, 16, 16)
        ),
        elevation=2,
        margin=ft.Margin(4, 4, 4, 4)
    )


def create_modern_button(
    text: str,
    on_click: Callable,
    icon: Optional[str] = None,
    variant: str = "filled",  # "filled", "outlined", "elevated", "text"
    color: str = ft.Colors.PRIMARY,
    size: str = "medium",  # "small", "medium", "large"
    disabled: bool = False,
    loading: bool = False
) -> ft.Control:
    """
    Create a modern button with 2025 design standards.
    
    Features:
    - Multiple variants (filled, outlined, elevated, text)
    - Size variants with proper padding
    - Loading states
    - Icon support
    - Proper accessibility
    """
    
    # Size configurations
    size_configs = {
        "small": {"padding": ft.Padding(16, 8, 16, 8), "text_size": 14, "icon_size": 18},
        "medium": {"padding": ft.Padding(24, 12, 24, 12), "text_size": 16, "icon_size": 20},
        "large": {"padding": ft.Padding(32, 16, 32, 16), "text_size": 18, "icon_size": 22}
    }
    
    config = size_configs.get(size, size_configs["medium"])
    
    # Button content
    button_controls = []
    
    if loading:
        button_controls.append(
            ft.ProgressRing(width=16, height=16, stroke_width=2)
        )
    elif icon:
        button_controls.append(
            ft.Icon(icon, size=config["icon_size"])
        )
    
    if loading:
        button_controls.append(ft.Container(width=8))
        button_controls.append(ft.Text("Loading...", size=config["text_size"]))
    else:
        if icon:
            button_controls.append(ft.Container(width=8))
        button_controls.append(
            ft.Text(
                text, 
                size=config["text_size"],
                weight=ft.FontWeight.W_600
            )
        )
    
    button_content = ft.Row(
        controls=button_controls,
        alignment=ft.MainAxisAlignment.CENTER,
        tight=True
    ) if len(button_controls) > 1 else button_controls[0]
    
    # Create button based on variant
    button_style = ft.ButtonStyle(
        padding=config["padding"],
        shape=ft.RoundedRectangleBorder(radius=16),
        animation_duration=200
    )
    
    if variant == "filled":
        return ft.FilledButton(
            content=button_content,
            on_click=on_click if not disabled and not loading else None,
            disabled=disabled or loading,
            style=button_style
        )
    elif variant == "outlined":
        return ft.OutlinedButton(
            content=button_content,
            on_click=on_click if not disabled and not loading else None,
            disabled=disabled or loading,
            style=button_style
        )
    elif variant == "elevated":
        return ft.ElevatedButton(
            content=button_content,
            on_click=on_click if not disabled and not loading else None,
            disabled=disabled or loading,
            style=button_style
        )
    else:  # text
        return ft.TextButton(
            content=button_content,
            on_click=on_click if not disabled and not loading else None,
            disabled=disabled or loading,
            style=button_style
        )


def create_progress_indicator(
    value: float,
    label: str,
    color: str = ft.Colors.PRIMARY,
    show_percentage: bool = True,
    height: float = 8,
    animated: bool = True
) -> ft.Container:
    """
    Create a modern progress indicator with smooth animations.
    
    Features:
    - Smooth progress animations
    - Color coding for different states
    - Optional percentage display
    - Modern rounded design
    """
    
    # Determine color based on value if not specified
    if color == ft.Colors.PRIMARY and value > 0:
        if value < 0.5:
            display_color = ft.Colors.GREEN
        elif value < 0.8:
            display_color = ft.Colors.ORANGE
        else:
            display_color = ft.Colors.RED
    else:
        display_color = color
    
    # Progress bar
    progress_bar = ft.ProgressBar(
        value=value,
        color=display_color,
        bgcolor=ft.Colors.with_opacity(0.1, display_color),
        height=height,
        border_radius=ft.BorderRadius(height/2, height/2, height/2, height/2)
    )
    
    if animated:
        progress_bar.animate_opacity = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
    
    # Label and percentage
    label_controls = [
        ft.Text(
            label,
            size=14,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.ON_SURFACE_VARIANT,
            style=ft.TextThemeStyle.BODY_MEDIUM
        )
    ]
    
    if show_percentage:
        label_controls.append(
            ft.Text(
                f"{value * 100:.1f}%",
                size=14,
                weight=ft.FontWeight.W_600,
                color=display_color,
                style=ft.TextThemeStyle.BODY_MEDIUM
            )
        )
    
    return ft.Container(
        content=ft.Column([
            ft.Row(
                controls=label_controls,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Container(height=8),
            progress_bar
        ], spacing=0, tight=True),
        padding=ft.Padding(0, 8, 0, 8)
    )


def create_info_chip(
    text: str,
    icon: Optional[str] = None,
    color: str = ft.Colors.PRIMARY,
    variant: str = "filled"  # "filled", "outlined"
) -> ft.Container:
    """
    Create a modern information chip.
    
    Features:
    - Rounded pill design
    - Icon support
    - Multiple color variants
    - Proper accessibility
    """
    
    chip_controls = []
    
    if icon:
        chip_controls.append(
            ft.Icon(
                icon, 
                size=16, 
                color=ft.Colors.ON_PRIMARY if variant == "filled" else color
            )
        )
        chip_controls.append(ft.Container(width=6))
    
    chip_controls.append(
        ft.Text(
            text,
            size=12,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.ON_PRIMARY if variant == "filled" else color,
            style=ft.TextThemeStyle.LABEL_MEDIUM
        )
    )
    
    return ft.Container(
        content=ft.Row(
            controls=chip_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            tight=True
        ),
        padding=ft.Padding(12, 6, 12, 6),
        bgcolor=color if variant == "filled" else ft.Colors.with_opacity(0.1, color),
        border=ft.Border.all(1, color) if variant == "outlined" else None,
        border_radius=ft.BorderRadius(16, 16, 16, 16),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )


def create_loading_overlay(message: str = "Loading...") -> ft.Container:
    """
    Create a modern loading overlay with blur effect.
    
    Features:
    - Semi-transparent backdrop
    - Centered loading indicator
    - Custom message support
    - Smooth fade animations
    """
    return ft.Container(
        content=ft.Column([
            ft.ProgressRing(width=48, height=48, stroke_width=4),
            ft.Container(height=16),
            ft.Text(
                message,
                size=16,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.ON_SURFACE,
                text_align=ft.TextAlign.CENTER,
                style=ft.TextThemeStyle.BODY_LARGE
            )
        ], 
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        width=200,
        height=120,
        bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.SURFACE),
        border_radius=ft.BorderRadius(20, 20, 20, 20),
        padding=ft.Padding(24, 24, 24, 24),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
            offset=ft.Offset(0, 8),
        ),
        animate_opacity=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
    )
