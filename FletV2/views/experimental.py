#!/usr/bin/env python3
"""
Experimental View - Testing and Development Playground
For experimental features, UI prototypes, and development testing.
"""

import os
import sys
from typing import Any, Callable

import flet as ft

# Path setup
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import Shared.utils.utf8_solution as _  # noqa: F401

# Import neumorphic shadows
try:
    from theme import PRONOUNCED_NEUMORPHIC_SHADOWS, MODERATE_NEUMORPHIC_SHADOWS
except ImportError:
    PRONOUNCED_NEUMORPHIC_SHADOWS = []
    MODERATE_NEUMORPHIC_SHADOWS = []


def create_experimental_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None
) -> tuple[ft.Control, Callable[[], None], Callable[[], None]]:
    """Create experimental view for testing and development."""

    # Experimental features showcase
    experimental_cards = [
        {
            "title": "UI Component Testing",
            "description": "Test new UI components and layouts before integration",
            "icon": ft.Icons.WIDGETS,
            "color": ft.Colors.PURPLE_500,
        },
        {
            "title": "Theme Variations",
            "description": "Experiment with color schemes and neumorphic depths",
            "icon": ft.Icons.PALETTE,
            "color": ft.Colors.PINK_500,
        },
        {
            "title": "Performance Profiling",
            "description": "Monitor render times and optimize slow operations",
            "icon": ft.Icons.SPEED,
            "color": ft.Colors.ORANGE_500,
        },
        {
            "title": "Data Visualization Prototypes",
            "description": "Test new chart types and visualization techniques",
            "icon": ft.Icons.BAR_CHART,
            "color": ft.Colors.CYAN_500,
        },
    ]

    def create_experimental_card(card_data: dict) -> ft.Container:
        """Create a card for experimental feature."""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(card_data["icon"], size=32, color=card_data["color"]),
                    ft.Text(card_data["title"], size=18, weight=ft.FontWeight.BOLD),
                ], spacing=12),
                ft.Text(
                    card_data["description"],
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Row([
                    ft.FilledTonalButton("Test", icon=ft.Icons.PLAY_ARROW),
                    ft.OutlinedButton("Configure", icon=ft.Icons.SETTINGS),
                ], spacing=8),
            ], spacing=16),
            padding=24,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            shadow=MODERATE_NEUMORPHIC_SHADOWS,
        )

    # Create responsive grid of experimental cards
    cards_grid = ft.ResponsiveRow([
        ft.Container(
            content=create_experimental_card(card),
            col={"sm": 12, "md": 6, "lg": 6},
        )
        for card in experimental_cards
    ], spacing=20, run_spacing=20)

    # Experimental tools section
    tools_section = ft.Container(
        content=ft.Column([
            ft.Text("Development Tools", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.FilledButton("Generate Sample Data", icon=ft.Icons.DATA_ARRAY),
                ft.FilledTonalButton("Clear Cache", icon=ft.Icons.DELETE_SWEEP),
                ft.OutlinedButton("Export State", icon=ft.Icons.DOWNLOAD),
                ft.OutlinedButton("Import State", icon=ft.Icons.UPLOAD),
            ], spacing=12, wrap=True),
        ], spacing=16),
        padding=24,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE,
        shadow=MODERATE_NEUMORPHIC_SHADOWS,
    )

    # Main content
    content = ft.Column([
        # Header with lab icon
        ft.Row([
            ft.Icon(ft.Icons.SCIENCE, size=40, color=ft.Colors.DEEP_PURPLE_500),
            ft.Text("Experimental Lab", size=32, weight=ft.FontWeight.BOLD),
        ], spacing=12),

        ft.Text(
            "This is a safe space for testing new features, UI experiments, and development workflows.",
            size=16,
            color=ft.Colors.ON_SURFACE_VARIANT,
        ),

        ft.Divider(height=32),

        # Experimental cards grid
        cards_grid,

        ft.Divider(height=32),

        # Tools section
        tools_section,

    ], spacing=24, expand=True, scroll="auto")

    main_container = ft.Container(
        content=content,
        padding=24,
        expand=True,
    )

    def dispose():
        """Cleanup."""
        pass

    def setup_subscriptions():
        """Setup."""
        pass

    return main_container, dispose, setup_subscriptions
