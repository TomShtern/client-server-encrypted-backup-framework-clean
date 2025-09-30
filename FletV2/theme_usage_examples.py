#!/usr/bin/env python3
"""
Theme System Usage Examples - Demonstrating Enhanced Features
Flet 0.28.3 - Material Design 3 + Neumorphism (40-45%) + Glassmorphism (20-30%)

This file demonstrates the enhanced theme.py capabilities with practical examples.
"""

import flet as ft
from theme import (
    # Pre-computed shadow constants
    PRONOUNCED_NEUMORPHIC_SHADOWS,
    MODERATE_NEUMORPHIC_SHADOWS,
    SUBTLE_NEUMORPHIC_SHADOWS,
    INSET_NEUMORPHIC_SHADOWS,
    # Glassmorphic configurations
    GLASS_STRONG,
    GLASS_MODERATE,
    GLASS_SUBTLE,
    # Enhanced component factories
    create_neumorphic_metric_card,
    create_glassmorphic_overlay,
    create_hybrid_gauge_container,
    create_neumorphic_container,
    create_glassmorphic_container,
    # Animation helpers
    create_hover_animation,
    create_press_animation,
    create_fade_animation,
    apply_interactive_animations,
    # Utilities
    setup_sophisticated_theme,
)


def example_neumorphic_metric_cards():
    """Example: Dashboard metric cards with different intensity levels."""
    return ft.Column([
        ft.Text("Neumorphic Metric Cards", size=24, weight=ft.FontWeight.BOLD),

        # Pronounced intensity (40-45%) - Primary metrics
        create_neumorphic_metric_card(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.STORAGE, size=32, color=ft.Colors.BLUE),
                    ft.Text("Storage Used", style=ft.TextThemeStyle.TITLE_MEDIUM),
                ]),
                ft.Text("847 GB", size=32, weight=ft.FontWeight.BOLD),
                ft.Text("↑ 12% from last week", size=12, color=ft.Colors.GREEN),
            ], spacing=8),
            intensity="pronounced",  # 40-45% intensity
            enable_hover=True
        ),

        # Moderate intensity (30%) - Secondary metrics
        create_neumorphic_metric_card(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.BACKUP, size=28, color=ft.Colors.PURPLE),
                    ft.Text("Backups", style=ft.TextThemeStyle.TITLE_SMALL),
                ]),
                ft.Text("142", size=28, weight=ft.FontWeight.BOLD),
            ], spacing=6),
            intensity="moderate",  # 30% intensity
            enable_hover=True
        ),

        # Subtle intensity (20%) - Tertiary metrics
        create_neumorphic_metric_card(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, size=24, color=ft.Colors.GREEN),
                ft.Text("Status: Healthy", size=16),
            ], spacing=8),
            intensity="subtle",  # 20% intensity
            enable_hover=False
        ),
    ], spacing=20)


def example_glassmorphic_overlays():
    """Example: Modal overlays with glassmorphic effects."""
    return ft.Column([
        ft.Text("Glassmorphic Overlays", size=24, weight=ft.FontWeight.BOLD),

        # Strong intensity (30%) - Modal dialogs
        create_glassmorphic_overlay(
            content=ft.Column([
                ft.Text("Confirm Action", size=20, weight=ft.FontWeight.BOLD),
                ft.Text("This action cannot be undone.", size=14),
                ft.Row([
                    ft.FilledButton("Confirm", on_click=lambda e: None),
                    ft.OutlinedButton("Cancel", on_click=lambda e: None),
                ], spacing=10),
            ], spacing=12),
            intensity="strong"  # 30% intensity
        ),

        # Moderate intensity (25%) - Info panels
        create_glassmorphic_container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE),
                ft.Text("Information panel with moderate glass effect"),
            ], spacing=10),
            intensity="moderate"  # 25% intensity
        ),

        # Subtle intensity (20%) - Background elements
        create_glassmorphic_container(
            content=ft.Text("Subtle glass background element"),
            intensity="subtle"  # 20% intensity
        ),
    ], spacing=20)


def example_hybrid_gauge():
    """Example: Hybrid container for gauges/charts."""
    # Simulated gauge content (use actual gauge in production)
    gauge_content = ft.Container(
        content=ft.Column([
            ft.Text("CPU Usage", size=16, weight=ft.FontWeight.BOLD),
            ft.ProgressRing(value=0.67, width=80, height=80),
            ft.Text("67%", size=24, weight=ft.FontWeight.BOLD),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        alignment=ft.alignment.center,
    )

    return ft.Column([
        ft.Text("Hybrid Gauge Container", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Neumorphic base (40%) + Glassmorphic overlay (25%)", size=14, color=ft.Colors.OUTLINE),

        create_hybrid_gauge_container(gauge_content),
    ], spacing=20)


def example_custom_animations():
    """Example: Custom interactive animations."""
    # Manual animation application
    card = ft.Container(
        content=ft.Column([
            ft.Icon(ft.Icons.TOUCH_APP, size=48, color=ft.Colors.BLUE),
            ft.Text("Hover over me!", size=16),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
        bgcolor=ft.Colors.SURFACE,
        border_radius=16,
        padding=ft.padding.all(24),
        shadow=MODERATE_NEUMORPHIC_SHADOWS,
    )

    # Apply interactive animations
    apply_interactive_animations(
        card,
        enable_hover=True,
        enable_press=False,
        hover_scale=1.03  # 3% scale on hover
    )

    return ft.Column([
        ft.Text("Interactive Animations", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("GPU-accelerated scale effect (180ms ease-out-cubic)", size=14, color=ft.Colors.OUTLINE),
        card,
    ], spacing=20)


def example_direct_constant_usage():
    """Example: Using pre-computed constants directly for maximum performance."""
    return ft.Column([
        ft.Text("Direct Constant Usage", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Maximum performance by using pre-computed constants", size=14, color=ft.Colors.OUTLINE),

        # Direct shadow constant usage
        ft.Container(
            content=ft.Text("Using PRONOUNCED_NEUMORPHIC_SHADOWS", size=16),
            bgcolor=ft.Colors.SURFACE,
            border_radius=16,
            padding=ft.padding.all(20),
            shadow=PRONOUNCED_NEUMORPHIC_SHADOWS,  # Direct constant reference
            animate_scale=create_hover_animation(duration_ms=150),
        ),

        # Direct glass config usage
        ft.Container(
            content=ft.Text("Using GLASS_STRONG config", size=16),
            border_radius=16,
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.with_opacity(GLASS_STRONG["bg_opacity"], ft.Colors.SURFACE),
            border=ft.border.all(1, ft.Colors.with_opacity(GLASS_STRONG["border_opacity"], ft.Colors.OUTLINE)),
            blur=ft.Blur(sigma_x=GLASS_STRONG["blur"], sigma_y=GLASS_STRONG["blur"]),
        ),
    ], spacing=20)


def example_intensity_comparison():
    """Example: Side-by-side comparison of different intensity levels."""
    return ft.Column([
        ft.Text("Intensity Comparison", size=24, weight=ft.FontWeight.BOLD),

        # Neumorphic intensity levels
        ft.Text("Neumorphic Shadows:", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([
            create_neumorphic_container(
                ft.Text("Pronounced\n40-45%", text_align=ft.TextAlign.CENTER),
                intensity="pronounced"
            ),
            create_neumorphic_container(
                ft.Text("Moderate\n30%", text_align=ft.TextAlign.CENTER),
                intensity="moderate"
            ),
            create_neumorphic_container(
                ft.Text("Subtle\n20%", text_align=ft.TextAlign.CENTER),
                intensity="subtle"
            ),
        ], spacing=15),

        # Glassmorphic intensity levels
        ft.Text("Glassmorphic Effects:", size=18, weight=ft.FontWeight.BOLD),
        ft.Row([
            create_glassmorphic_container(
                ft.Text("Strong\n30%", text_align=ft.TextAlign.CENTER),
                intensity="strong"
            ),
            create_glassmorphic_container(
                ft.Text("Moderate\n25%", text_align=ft.TextAlign.CENTER),
                intensity="moderate"
            ),
            create_glassmorphic_container(
                ft.Text("Subtle\n20%", text_align=ft.TextAlign.CENTER),
                intensity="subtle"
            ),
        ], spacing=15),
    ], spacing=20)


def main(page: ft.Page):
    """Main application demonstrating all theme enhancements."""
    page.title = "Enhanced Theme System Examples"
    page.padding = 30

    # Setup sophisticated theme
    setup_sophisticated_theme(page)

    # Create scrollable content with all examples
    page.add(
        ft.Column([
            ft.Text(
                "Enhanced Theme System - Flet 0.28.3",
                size=32,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Divider(height=2),

            example_neumorphic_metric_cards(),
            ft.Divider(height=1),

            example_glassmorphic_overlays(),
            ft.Divider(height=1),

            example_hybrid_gauge(),
            ft.Divider(height=1),

            example_custom_animations(),
            ft.Divider(height=1),

            example_direct_constant_usage(),
            ft.Divider(height=1),

            example_intensity_comparison(),

        ], scroll=ft.ScrollMode.AUTO, spacing=30)
    )


if __name__ == "__main__":
    ft.app(target=main)