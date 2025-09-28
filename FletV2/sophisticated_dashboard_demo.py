#!/usr/bin/env python3
"""
SOPHISTICATED DASHBOARD DEMO - Material Design 3 + Neumorphism + Glassmorphism
Flet 0.28.3 implementation showcasing triple design system architecture.

This is a standalone demo showcasing the sophisticated dashboard design
that combines all three design philosophies in a cohesive interface.

Run with: python sophisticated_dashboard_demo.py
"""

import flet as ft
from datetime import datetime
import asyncio
import random

# Material Design 3 semantic color system
BRAND_COLORS = {
    "primary": "#3B82F6",
    "secondary": "#8B5CF6",
    "tertiary": "#10B981",
    "success": "#22C55E",
    "warning": "#EAB308",
    "error": "#EF4444",
    "surface": "#F8FAFC",
    "surface_variant": "#F1F5F9",
    "outline": "#CBD5E1",
}

def create_neumorphic_container(content, effect_type="raised"):
    """Create neumorphic container with dual shadow effects."""
    if effect_type == "raised":
        shadows = [
            # Dark shadow (bottom-right)
            ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(4, 4),
            ),
            # Light highlight (top-left)
            ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.8, ft.Colors.WHITE),
                offset=ft.Offset(-4, -4),
            ),
        ]
    else:  # inset
        shadows = [
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                offset=ft.Offset(2, 2),
                blur_style=ft.ShadowBlurStyle.INNER
            ),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                offset=ft.Offset(-2, -2),
                blur_style=ft.ShadowBlurStyle.INNER
            ),
        ]

    return ft.Container(
        content=content,
        padding=24,
        border_radius=20,
        bgcolor=ft.Colors.SURFACE,
        shadow=shadows
    )

def create_glassmorphic_container(content, intensity="medium"):
    """Create glassmorphic container with blur and transparency."""
    config = {
        "light": {"opacity": 0.05, "border_opacity": 0.08, "blur": 10},
        "medium": {"opacity": 0.08, "border_opacity": 0.12, "blur": 15},
        "strong": {"opacity": 0.12, "border_opacity": 0.18, "blur": 20}
    }[intensity]

    return ft.Container(
        content=content,
        padding=20,
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(config["opacity"], ft.Colors.SURFACE_VARIANT),
        border=ft.border.all(1, ft.Colors.with_opacity(config["border_opacity"], ft.Colors.OUTLINE)),
        blur=ft.Blur(sigma_x=config["blur"], sigma_y=config["blur"], tile_mode=ft.TileMode.MIRROR)
    )

def main(page: ft.Page):
    page.title = "Sophisticated Dashboard - Triple Design System"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0

    # Material Design 3 theme setup
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=BRAND_COLORS["primary"],
            secondary=BRAND_COLORS["secondary"],
            tertiary=BRAND_COLORS["tertiary"],
            surface=BRAND_COLORS["surface"],
            surface_variant=BRAND_COLORS["surface_variant"],
            background=BRAND_COLORS["surface"],
            error=BRAND_COLORS["error"],
            outline=BRAND_COLORS["outline"],
            on_primary=ft.Colors.WHITE,
            on_secondary=ft.Colors.WHITE,
            on_tertiary=ft.Colors.WHITE,
            on_surface=ft.Colors.with_opacity(0.87, ft.Colors.BLACK),
            on_surface_variant=ft.Colors.with_opacity(0.6, ft.Colors.BLACK),
            on_background=ft.Colors.with_opacity(0.87, ft.Colors.BLACK),
            on_error=ft.Colors.WHITE,
        ),
        font_family="Inter",
        use_material3=True
    )

    # Data refs for real-time updates
    clients_ref = ft.Ref[ft.Text]()
    files_ref = ft.Ref[ft.Text]()
    storage_ref = ft.Ref[ft.Text]()
    uptime_ref = ft.Ref[ft.Text]()
    storage_progress_ref = ft.Ref[ft.ProgressRing]()
    cpu_progress_ref = ft.Ref[ft.ProgressRing]()
    memory_progress_ref = ft.Ref[ft.ProgressRing]()
    status_badge_ref = ft.Ref[ft.Container]()

    # Mock data generator
    def get_mock_data():
        return {
            'clients': random.randint(5, 15),
            'files': random.randint(1000, 2000),
            'storage_used': random.randint(45, 85),
            'uptime': f"{random.randint(1, 7)}d {random.randint(0, 23)}h",
            'cpu_usage': random.randint(15, 75),
            'memory_usage': random.randint(25, 80)
        }

    # Neumorphic metric card
    def create_metric_card(title, value_ref, icon, color):
        return create_neumorphic_container(
            ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=28),
                    ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE)
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(
                    content=ft.Text("Loading...", ref=value_ref, size=36, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                    margin=ft.margin.only(top=12)
                ),
            ], spacing=8)
        )

    # Neumorphic gauge with inset effect
    def create_gauge_card(title, progress_ref, icon, color):
        return create_neumorphic_container(
            ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=28),
                    ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE)
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(
                    content=create_neumorphic_container(
                        ft.ProgressRing(
                            ref=progress_ref,
                            width=80,
                            height=80,
                            stroke_width=8,
                            color=color,
                            bgcolor=ft.Colors.with_opacity(0.1, color),
                            value=0
                        ),
                        effect_type="inset"
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=16)
                )
            ], spacing=8)
        )

    # Glassmorphic floating header
    def create_header():
        return create_glassmorphic_container(
            ft.Row([
                ft.Column([
                    ft.Text(
                        "SOPHISTICATED DASHBOARD",
                        size=36,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE
                    ),
                    ft.Text(
                        "Material Design 3 + Neumorphism + Glassmorphism",
                        size=14,
                        color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE)
                    )
                ], spacing=4),
                ft.Container(
                    ref=status_badge_ref,
                    content=ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.GREEN, size=16),
                        ft.Text("System Online", size=16, weight=ft.FontWeight.W_600, color=ft.Colors.GREEN)
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                    border_radius=25,
                    bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.GREEN),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.GREEN)),
                    blur=ft.Blur(sigma_x=10, sigma_y=10, tile_mode=ft.TileMode.MIRROR)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            intensity="strong"
        )

    # Neumorphic activity panel
    def create_activity_panel():
        activities = [
            ["Client-001", "Backup Complete", "2 min ago", "Success"],
            ["Client-003", "File Transfer", "5 min ago", "In Progress"],
            ["Client-007", "System Scan", "8 min ago", "Success"],
            ["Client-012", "Data Sync", "12 min ago", "Success"],
        ]

        return create_neumorphic_container(
            ft.Column([
                ft.Text("Recent Activity", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                ft.Container(
                    content=ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Client", weight=ft.FontWeight.W_600)),
                            ft.DataColumn(ft.Text("Action", weight=ft.FontWeight.W_600)),
                            ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.W_600)),
                            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.W_600)),
                        ],
                        rows=[
                            ft.DataRow(cells=[
                                ft.DataCell(ft.Text(activity[0], size=14)),
                                ft.DataCell(ft.Text(activity[1], size=14)),
                                ft.DataCell(ft.Text(activity[2], size=14)),
                                ft.DataCell(create_glassmorphic_container(
                                    ft.Text(
                                        activity[3],
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=ft.Colors.GREEN if activity[3] == "Success"
                                              else ft.Colors.BLUE if activity[3] == "In Progress"
                                              else ft.Colors.RED
                                    ),
                                    intensity="light"
                                )),
                            ]) for activity in activities
                        ],
                        border_radius=12,
                    ),
                    margin=ft.margin.only(top=16)
                )
            ], spacing=0)
        )

    # Glassmorphic info alert
    info_alert = create_glassmorphic_container(
        ft.Row([
            ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE, size=24),
            ft.Text("Triple design system demo: combining Material Design 3, Neumorphism, and Glassmorphism",
                   size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE, expand=True),
            ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_size=20,
                on_click=lambda e: page.remove(info_alert)
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        intensity="medium"
    )

    # Metrics grid with neumorphic cards
    metrics_grid = ft.ResponsiveRow([
        ft.Container(
            content=create_metric_card("Active Clients", clients_ref, ft.Icons.PEOPLE, ft.Colors.BLUE),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            content=create_metric_card("Total Files", files_ref, ft.Icons.FOLDER, ft.Colors.GREEN),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            content=create_metric_card("Storage Used", storage_ref, ft.Icons.STORAGE, ft.Colors.ORANGE),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            content=create_metric_card("Uptime", uptime_ref, ft.Icons.TIMER, ft.Colors.PURPLE),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
    ], spacing=20)

    # Gauge grid with neumorphic inset effects
    gauge_grid = ft.ResponsiveRow([
        ft.Container(
            content=create_gauge_card("Storage", storage_progress_ref, ft.Icons.STORAGE, ft.Colors.ORANGE),
            col={"sm": 12, "md": 4}
        ),
        ft.Container(
            content=create_gauge_card("CPU Usage", cpu_progress_ref, ft.Icons.MEMORY, ft.Colors.RED),
            col={"sm": 12, "md": 4}
        ),
        ft.Container(
            content=create_gauge_card("Memory", memory_progress_ref, ft.Icons.DEVELOPER_BOARD, ft.Colors.BLUE),
            col={"sm": 12, "md": 4}
        ),
    ], spacing=20)

    # Update data function
    def update_dashboard_data():
        data = get_mock_data()

        # Update metric values
        if clients_ref.current:
            clients_ref.current.value = str(data['clients'])
            clients_ref.current.update()

        if files_ref.current:
            files_ref.current.value = f"{data['files']:,}"
            files_ref.current.update()

        if storage_ref.current:
            storage_ref.current.value = f"{data['storage_used']}%"
            storage_ref.current.update()

        if uptime_ref.current:
            uptime_ref.current.value = data['uptime']
            uptime_ref.current.update()

        # Update progress rings
        if storage_progress_ref.current:
            storage_progress_ref.current.value = data['storage_used'] / 100
            storage_progress_ref.current.update()

        if cpu_progress_ref.current:
            cpu_progress_ref.current.value = data['cpu_usage'] / 100
            cpu_progress_ref.current.update()

        if memory_progress_ref.current:
            memory_progress_ref.current.value = data['memory_usage'] / 100
            memory_progress_ref.current.update()

        # Update glassmorphic status badge based on system health
        if status_badge_ref.current:
            cpu_usage = data['cpu_usage']
            memory_usage = data['memory_usage']

            if cpu_usage > 80 or memory_usage > 80:
                # High load - red glassmorphic badge
                status_badge_ref.current.bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.RED)
                status_badge_ref.current.border = ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.RED))
                status_badge_ref.current.content.controls[0].color = ft.Colors.RED
                status_badge_ref.current.content.controls[1].value = "High Load"
                status_badge_ref.current.content.controls[1].color = ft.Colors.RED
            elif cpu_usage > 60 or memory_usage > 60:
                # Medium load - orange glassmorphic badge
                status_badge_ref.current.bgcolor = ft.Colors.with_opacity(0.15, ft.Colors.ORANGE)
                status_badge_ref.current.border = ft.border.all(1, ft.Colors.with_opacity(0.3, ft.Colors.ORANGE))
                status_badge_ref.current.content.controls[0].color = ft.Colors.ORANGE
                status_badge_ref.current.content.controls[1].value = "Medium Load"
                status_badge_ref.current.content.controls[1].color = ft.Colors.ORANGE
            else:
                # Normal load - green glassmorphic badge
                status_badge_ref.current.bgcolor = ft.Colors.with_opacity(0.1, ft.Colors.GREEN)
                status_badge_ref.current.border = ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.GREEN))
                status_badge_ref.current.content.controls[0].color = ft.Colors.GREEN
                status_badge_ref.current.content.controls[1].value = "System Online"
                status_badge_ref.current.content.controls[1].color = ft.Colors.GREEN

            status_badge_ref.current.update()

    # Auto-refresh data every 3 seconds
    async def auto_refresh():
        while True:
            await asyncio.sleep(3)
            update_dashboard_data()

    # Main dashboard layout
    dashboard_layout = ft.Container(
        content=ft.Column([
            create_header(),
            info_alert,
            metrics_grid,
            gauge_grid,
            create_activity_panel(),
        ], spacing=24, scroll=ft.ScrollMode.AUTO),
        padding=28,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.SURFACE_VARIANT)
    )

    page.add(dashboard_layout)

    # Initial data load
    update_dashboard_data()

    # Start auto-refresh
    page.run_task(auto_refresh)

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8555)