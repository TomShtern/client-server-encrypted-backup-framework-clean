#!/usr/bin/env python3
"""
Tri-Style Dashboard Demo - Practical Integration Example
Shows how to apply Neumorphism + Glassmorphism + Material Design 3 to the existing dashboard.

This demonstrates the sophisticated component system applied to real dashboard elements:
- Hero cards use Glassmorphism (focal points, draw attention)
- System metrics use Neumorphism (structure, subtle depth)
- Interactive elements use Material Design 3 (foundation, accessibility)
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Callable, Any

# Path setup for imports
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import flet as ft
import Shared.utils.utf8_solution as _  # noqa: F401

from FletV2.utils.tri_style_components import (
    TriStyleColors, ShadowSystem,
    create_neuro_container, create_neuro_metric_panel, create_neuro_button,
    create_glass_hero_card, create_glass_overlay_panel,
    create_md3_action_button, create_md3_icon_button, create_md3_fab,
    create_tri_style_dashboard_section
)
from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.state_manager import StateManager
from FletV2.utils.user_feedback import show_success_message, show_error_message

def create_tri_style_dashboard_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    state_manager: StateManager | None
) -> tuple[ft.Control, Callable, Callable]:
    """
    Create tri-style dashboard demonstrating sophisticated design integration.
    This shows how to combine all three design languages harmoniously.
    """

    # Detect theme mode for appropriate styling
    is_dark_theme = page.theme_mode == ft.ThemeMode.DARK

    # ==================== REFS FOR DYNAMIC UPDATES ====================
    hero_clients_ref = ft.Ref[ft.Text]()
    hero_storage_ref = ft.Ref[ft.Text]()
    hero_uptime_ref = ft.Ref[ft.Text]()
    hero_throughput_ref = ft.Ref[ft.Text]()

    cpu_metric_ref = ft.Ref[ft.Text]()
    memory_metric_ref = ft.Ref[ft.Text]()
    disk_metric_ref = ft.Ref[ft.Text]()
    network_metric_ref = ft.Ref[ft.Text]()

    activity_list_ref = ft.Ref[ft.ListView]()
    status_ref = ft.Ref[ft.Text]()

    # ==================== GLASSMORPHIC HERO SECTION (FOCAL POINTS) ====================
    def create_hero_metrics_section() -> ft.Container:
        """Create hero metrics using glassmorphic design for maximum visual impact."""

        hero_cards = ft.ResponsiveRow([
            # Connected Clients - Blue accent
            ft.Container(
                content=create_glass_hero_card(
                    title="Connected Clients",
                    value="--",
                    trend="+2",
                    icon=ft.Icons.PEOPLE_ALT,
                    accent_color=TriStyleColors.GLASS_ACCENT_BLUE,
                    is_dark_theme=is_dark_theme
                ),
                col={"sm": 12, "md": 6, "lg": 3},
                animate_opacity=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
                opacity=0  # Start hidden for entrance animation
            ),

            # Storage Usage - Green accent
            ft.Container(
                content=create_glass_hero_card(
                    title="Storage Used",
                    value="--",
                    trend="62%",
                    icon=ft.Icons.STORAGE,
                    accent_color=TriStyleColors.GLASS_ACCENT_GREEN,
                    is_dark_theme=is_dark_theme
                ),
                col={"sm": 12, "md": 6, "lg": 3},
                animate_opacity=ft.Animation(500, ft.AnimationCurve.EASE_OUT),
                opacity=0  # Start hidden for entrance animation
            ),

            # Server Uptime - Purple accent
            ft.Container(
                content=create_glass_hero_card(
                    title="Server Uptime",
                    value="--",
                    trend="Stable",
                    icon=ft.Icons.TIMER,
                    accent_color=TriStyleColors.GLASS_ACCENT_PURPLE,
                    is_dark_theme=is_dark_theme
                ),
                col={"sm": 12, "md": 6, "lg": 3},
                animate_opacity=ft.Animation(600, ft.AnimationCurve.EASE_OUT),
                opacity=0  # Start hidden for entrance animation
            ),

            # Network Throughput - Cyan accent
            ft.Container(
                content=create_glass_hero_card(
                    title="Network Throughput",
                    value="--",
                    trend="+15%",
                    icon=ft.Icons.NETWORK_CHECK,
                    accent_color="#00BCD4",  # Cyan
                    is_dark_theme=is_dark_theme
                ),
                col={"sm": 12, "md": 6, "lg": 3},
                animate_opacity=ft.Animation(700, ft.AnimationCurve.EASE_OUT),
                opacity=0  # Start hidden for entrance animation
            ),
        ], spacing=20)

        # Store references for data updates
        hero_clients_ref.current = hero_cards.controls[0].content.content.controls[1].content  # Get the value text
        hero_storage_ref.current = hero_cards.controls[1].content.content.controls[1].content
        hero_uptime_ref.current = hero_cards.controls[2].content.content.controls[1].content
        hero_throughput_ref.current = hero_cards.controls[3].content.content.controls[1].content

        return ft.Container(
            content=ft.Column([
                # Section header with glass styling
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.DASHBOARD, color=TriStyleColors.GLASS_ACCENT_BLUE, size=28),
                        ft.Text(
                            "SYSTEM OVERVIEW",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.WHITE if is_dark_theme else ft.Colors.ON_SURFACE,
                            font_family="Inter"
                        )
                    ], spacing=12),
                    margin=ft.margin.only(bottom=24)
                ),
                hero_cards
            ]),
            margin=ft.margin.only(bottom=32)
        )

    # ==================== NEUMORPHIC SYSTEM METRICS (STRUCTURE) ====================
    def create_system_metrics_section() -> ft.Container:
        """Create system metrics using neumorphic design for structural depth."""

        cpu_panel = create_neuro_metric_panel(
            title="CPU Usage",
            value="--",
            subtitle="Processing load",
            icon=ft.Icons.MEMORY,
            color=TriStyleColors.MD3_PRIMARY,
            is_dark_theme=is_dark_theme
        )

        memory_panel = create_neuro_metric_panel(
            title="Memory Usage",
            value="--",
            subtitle="RAM utilization",
            icon=ft.Icons.DEVELOPER_BOARD,
            color=TriStyleColors.GLASS_ACCENT_GREEN,
            is_dark_theme=is_dark_theme
        )

        disk_panel = create_neuro_metric_panel(
            title="Disk Usage",
            value="--",
            subtitle="Storage capacity",
            icon=ft.Icons.STORAGE,
            color=TriStyleColors.GLASS_ACCENT_PURPLE,
            is_dark_theme=is_dark_theme
        )

        network_panel = create_neuro_metric_panel(
            title="Network I/O",
            value="--",
            subtitle="Data transfer rate",
            icon=ft.Icons.NETWORK_WIFI,
            color="#FF9800",  # Orange
            is_dark_theme=is_dark_theme
        )

        # Store references for data updates
        cpu_metric_ref.current = cpu_panel.content.controls[1].content  # Get the value text
        memory_metric_ref.current = memory_panel.content.controls[1].content
        disk_metric_ref.current = disk_panel.content.controls[1].content
        network_metric_ref.current = network_panel.content.controls[1].content

        metrics_row = ft.ResponsiveRow([
            ft.Container(content=cpu_panel, col={"sm": 12, "md": 6, "lg": 3}),
            ft.Container(content=memory_panel, col={"sm": 12, "md": 6, "lg": 3}),
            ft.Container(content=disk_panel, col={"sm": 12, "md": 6, "lg": 3}),
            ft.Container(content=network_panel, col={"sm": 12, "md": 6, "lg": 3}),
        ], spacing=20)

        return create_tri_style_dashboard_section(
            title="SYSTEM PERFORMANCE",
            content=metrics_row,
            style_type="neuro",
            accent_color=TriStyleColors.MD3_PRIMARY,
            is_dark_theme=is_dark_theme
        )

    # ==================== GLASSMORPHIC ACTIVITY STREAM (FOCAL POINT) ====================
    def create_activity_section() -> ft.Container:
        """Create activity stream using glassmorphic design for visual prominence."""

        # Activity list with glassmorphic container
        activity_list = ft.ListView(
            ref=activity_list_ref,
            height=300,
            spacing=8,
            padding=ft.padding.all(16),
            auto_scroll=True
        )

        # Search and filter controls using MD3 foundation
        search_controls = ft.Row([
            ft.Container(
                content=ft.TextField(
                    hint_text="Search activity...",
                    prefix_icon=ft.Icons.SEARCH,
                    border_radius=20,
                    dense=True,
                    width=300,
                    border_color=ft.Colors.with_opacity(0.3, TriStyleColors.GLASS_ACCENT_BLUE),
                    focused_border_color=TriStyleColors.GLASS_ACCENT_BLUE
                ),
                expand=True
            ),
            create_md3_icon_button(
                icon=ft.Icons.FILTER_LIST,
                variant="tonal",
                color=TriStyleColors.GLASS_ACCENT_BLUE,
                tooltip="Filter activities"
            ),
            create_md3_icon_button(
                icon=ft.Icons.REFRESH,
                variant="outlined",
                color=TriStyleColors.GLASS_ACCENT_BLUE,
                tooltip="Refresh"
            )
        ], spacing=12)

        activity_content = ft.Column([
            search_controls,
            ft.Container(height=16),  # Spacer
            activity_list
        ])

        return create_glass_overlay_panel(
            content=activity_content,
            title="Live Activity Stream",
            accent_color=TriStyleColors.GLASS_ACCENT_BLUE,
            is_dark_theme=is_dark_theme,
            height=400
        )

    # ==================== MD3 ACTION CONTROLS (FOUNDATION) ====================
    def create_action_controls() -> ft.Container:
        """Create action controls using Material Design 3 for accessibility and usability."""

        async def refresh_data(e):
            """Refresh dashboard data with user feedback."""
            try:
                if status_ref.current:
                    status_ref.current.value = "Refreshing..."
                    status_ref.current.color = ft.Colors.ORANGE_600
                    status_ref.current.update()

                # Simulate data refresh
                await asyncio.sleep(1)

                # Update hero metrics with mock data
                if hero_clients_ref.current:
                    hero_clients_ref.current.value = "24"
                    hero_clients_ref.current.update()

                if hero_storage_ref.current:
                    hero_storage_ref.current.value = "1.8TB"
                    hero_storage_ref.current.update()

                if hero_uptime_ref.current:
                    hero_uptime_ref.current.value = "2d 14h"
                    hero_uptime_ref.current.update()

                if hero_throughput_ref.current:
                    hero_throughput_ref.current.value = "45.2 MB/s"
                    hero_throughput_ref.current.update()

                # Update system metrics
                if cpu_metric_ref.current:
                    cpu_metric_ref.current.value = "34%"
                    cpu_metric_ref.current.update()

                if memory_metric_ref.current:
                    memory_metric_ref.current.value = "67%"
                    memory_metric_ref.current.update()

                if disk_metric_ref.current:
                    disk_metric_ref.current.value = "82%"
                    disk_metric_ref.current.update()

                if network_metric_ref.current:
                    network_metric_ref.current.value = "45 MB/s"
                    network_metric_ref.current.update()

                show_success_message(page, "Dashboard data refreshed successfully")

                if status_ref.current:
                    status_ref.current.value = "System Online"
                    status_ref.current.color = ft.Colors.GREEN_600
                    status_ref.current.update()

            except Exception as ex:
                show_error_message(page, f"Refresh failed: {str(ex)}")

        async def export_report(e):
            """Export system report."""
            show_success_message(page, "System report exported successfully")

        async def open_settings(e):
            """Open settings panel."""
            show_success_message(page, "Settings panel would open here")

        primary_actions = ft.Row([
            create_md3_action_button(
                text="Refresh Data",
                icon=ft.Icons.REFRESH,
                variant="filled",
                color=TriStyleColors.MD3_PRIMARY,
                on_click=refresh_data
            ),
            create_md3_action_button(
                text="Export Report",
                icon=ft.Icons.DOWNLOAD,
                variant="tonal",
                color=TriStyleColors.GLASS_ACCENT_GREEN,
                on_click=export_report
            ),
            create_md3_action_button(
                text="View Analytics",
                icon=ft.Icons.ANALYTICS,
                variant="outlined",
                color=TriStyleColors.GLASS_ACCENT_PURPLE
            )
        ], spacing=16)

        secondary_actions = ft.Row([
            create_md3_icon_button(
                icon=ft.Icons.SETTINGS,
                variant="tonal",
                color=TriStyleColors.MD3_PRIMARY,
                tooltip="Settings",
                on_click=open_settings
            ),
            create_md3_icon_button(
                icon=ft.Icons.NOTIFICATIONS,
                variant="outlined",
                color=TriStyleColors.GLASS_ACCENT_BLUE,
                tooltip="Notifications"
            ),
            create_md3_icon_button(
                icon=ft.Icons.HELP_OUTLINE,
                variant="standard",
                color=ft.Colors.OUTLINE,
                tooltip="Help"
            ),
            # Status indicator
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=12, color=ft.Colors.GREEN_600),
                    ft.Text("--", ref=status_ref, size=12, color=ft.Colors.GREEN_600)
                ], spacing=6),
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                border_radius=16,
                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN_600)
            )
        ], spacing=12)

        return ft.Container(
            content=ft.Column([
                primary_actions,
                ft.Container(height=16),  # Spacer
                secondary_actions
            ], horizontal_alignment=ft.CrossAxisAlignment.START),
            padding=ft.padding.all(24),
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            margin=ft.margin.only(top=24)
        )

    # ==================== ENTRANCE ANIMATIONS ====================
    async def perform_entrance_animations():
        """Animate dashboard elements entrance for polished UX."""
        try:
            await asyncio.sleep(0.2)  # Initial delay

            # Animate hero cards
            for i, card_container in enumerate(hero_section.content.controls[1].controls):
                card_container.opacity = 1
                card_container.update()
                await asyncio.sleep(0.1)

        except Exception as e:
            print(f"Animation error: {e}")

    # ==================== MAIN LAYOUT ASSEMBLY ====================

    # Create all sections
    hero_section = create_hero_metrics_section()
    metrics_section = create_system_metrics_section()
    activity_section = create_activity_section()
    controls_section = create_action_controls()

    # Two-column responsive layout
    left_column = ft.Column([
        hero_section,
        metrics_section
    ], spacing=0)

    right_column = ft.Column([
        activity_section,
        controls_section
    ], spacing=0)

    main_layout = ft.ResponsiveRow([
        ft.Container(
            content=left_column,
            col={"sm": 12, "md": 7, "lg": 8},
            padding=ft.padding.only(right=16)
        ),
        ft.Container(
            content=right_column,
            col={"sm": 12, "md": 5, "lg": 4},
            padding=ft.padding.only(left=16)
        )
    ])

    dashboard_container = ft.Container(
        content=ft.Column([
            # Page header
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        "TRI-STYLE DASHBOARD",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE,
                        font_family="Inter"
                    ),
                    ft.Container(
                        content=ft.Text(
                            "Neumorphism + Glassmorphism + Material Design 3",
                            size=14,
                            color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE),
                            font_family="Inter"
                        ),
                        expand=True,
                        alignment=ft.alignment.center_right
                    )
                ]),
                padding=ft.padding.all(24),
                border_radius=16,
                bgcolor=ft.Colors.SURFACE,
                border=ft.border.all(1, ft.Colors.OUTLINE),
                margin=ft.margin.only(bottom=24)
            ),
            main_layout
        ], scroll=ft.ScrollMode.AUTO),
        expand=True,
        padding=ft.padding.symmetric(horizontal=24, vertical=16)
    )

    # ==================== LIFECYCLE MANAGEMENT ====================
    def setup_subscriptions():
        """Setup background tasks and animations."""
        if page and hasattr(page, 'run_task'):
            page.run_task(perform_entrance_animations)

    def dispose():
        """Clean up resources."""
        pass

    return dashboard_container, dispose, setup_subscriptions