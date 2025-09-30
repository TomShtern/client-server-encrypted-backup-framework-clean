#!/usr/bin/env python3
"""
Analytics View - Data Visualization Dashboard
Shows backup statistics with charts and metrics.
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

def create_analytics_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None,
    navigate_callback: Callable[[str], None] | None = None
) -> tuple[ft.Control, Callable[[], None], Callable[[], None]]:
    """Create analytics view with charts and metrics."""

    # Sample data
    sample_backups = 1247
    sample_storage_gb = 3856
    sample_success_rate = 98.3
    sample_avg_size_gb = 3.09

    # Metric card helper
    def create_metric_card(title: str, value: str, icon: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, color=color, size=24),
                        width=48,
                        height=48,
                        bgcolor=ft.Colors.with_opacity(0.12, color),
                        border_radius=24,
                        alignment=ft.alignment.center,
                    ),
                    ft.Text(title, size=14, weight=ft.FontWeight.W_500),
                ], spacing=12),
                ft.Text(value, size=32, weight=ft.FontWeight.BOLD),
            ], spacing=12),
            padding=20,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            expand=True,
        )

    # Metric cards row
    metrics_row = ft.ResponsiveRow([
        ft.Container(
            create_metric_card("Total Backups", str(sample_backups), ft.Icons.BACKUP, ft.Colors.BLUE_400),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            create_metric_card("Total Storage", f"{sample_storage_gb} GB", ft.Icons.STORAGE, ft.Colors.GREEN_400),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            create_metric_card("Success Rate", f"{sample_success_rate}%", ft.Icons.CHECK_CIRCLE, ft.Colors.PURPLE_400),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            create_metric_card("Avg Backup Size", f"{sample_avg_size_gb} GB", ft.Icons.PIE_CHART, ft.Colors.AMBER_400),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
    ], spacing=16)

    # Sample chart data
    backup_trend_chart = ft.LineChart(
        data_series=[
            ft.LineChartData(
                data_points=[
                    ft.LineChartDataPoint(0, 20),
                    ft.LineChartDataPoint(1, 35),
                    ft.LineChartDataPoint(2, 28),
                    ft.LineChartDataPoint(3, 42),
                    ft.LineChartDataPoint(4, 38),
                    ft.LineChartDataPoint(5, 50),
                    ft.LineChartDataPoint(6, 45),
                ],
                stroke_width=3,
                color=ft.Colors.BLUE_400,
                curved=True,
                stroke_cap_round=True,
            )
        ],
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE)),
        horizontal_grid_lines=ft.ChartGridLines(
            interval=10,
            color=ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE),
            width=1,
        ),
        vertical_grid_lines=ft.ChartGridLines(
            interval=1,
            color=ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE),
            width=1,
        ),
        left_axis=ft.ChartAxis(
            labels_size=40,
            title=ft.Text("Backups", size=12),
        ),
        bottom_axis=ft.ChartAxis(
            labels_size=32,
            title=ft.Text("Days", size=12),
        ),
        tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.SURFACE),
        min_y=0,
        max_y=60,
        min_x=0,
        max_x=6,
    )

    # Storage by client chart
    storage_chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=0,
                bar_rods=[ft.BarChartRod(from_y=0, to_y=850, width=40, color=ft.Colors.BLUE_400, border_radius=4)],
            ),
            ft.BarChartGroup(
                x=1,
                bar_rods=[ft.BarChartRod(from_y=0, to_y=1200, width=40, color=ft.Colors.GREEN_400, border_radius=4)],
            ),
            ft.BarChartGroup(
                x=2,
                bar_rods=[ft.BarChartRod(from_y=0, to_y=950, width=40, color=ft.Colors.PURPLE_400, border_radius=4)],
            ),
            ft.BarChartGroup(
                x=3,
                bar_rods=[ft.BarChartRod(from_y=0, to_y=700, width=40, color=ft.Colors.AMBER_400, border_radius=4)],
            ),
        ],
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE)),
        horizontal_grid_lines=ft.ChartGridLines(
            interval=200,
            color=ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE),
            width=1,
        ),
        left_axis=ft.ChartAxis(
            labels_size=40,
            title=ft.Text("Storage (GB)", size=12),
        ),
        bottom_axis=ft.ChartAxis(
            labels=[
                ft.ChartAxisLabel(value=0, label=ft.Text("Client A", size=10)),
                ft.ChartAxisLabel(value=1, label=ft.Text("Client B", size=10)),
                ft.ChartAxisLabel(value=2, label=ft.Text("Client C", size=10)),
                ft.ChartAxisLabel(value=3, label=ft.Text("Client D", size=10)),
            ],
            labels_size=32,
        ),
        tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.SURFACE),
        max_y=1400,
    )

    # File type distribution
    file_type_chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                value=40,
                title="Documents",
                color=ft.Colors.BLUE_400,
                radius=80,
            ),
            ft.PieChartSection(
                value=30,
                title="Images",
                color=ft.Colors.GREEN_400,
                radius=80,
            ),
            ft.PieChartSection(
                value=20,
                title="Videos",
                color=ft.Colors.PURPLE_400,
                radius=80,
            ),
            ft.PieChartSection(
                value=10,
                title="Other",
                color=ft.Colors.AMBER_400,
                radius=80,
            ),
        ],
        sections_space=2,
        center_space_radius=0,
    )

    # Charts row
    charts_row = ft.ResponsiveRow([
        # Backup trends
        ft.Container(
            content=ft.Column([
                ft.Text("Backup Trends", size=18, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=backup_trend_chart,
                    height=300,
                ),
            ], spacing=12),
            padding=20,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            col={"sm": 12, "md": 12, "lg": 8}
        ),
        # File type distribution
        ft.Container(
            content=ft.Column([
                ft.Text("File Type Distribution", size=18, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=file_type_chart,
                    height=300,
                    alignment=ft.alignment.center,
                ),
            ], spacing=12),
            padding=20,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            col={"sm": 12, "md": 12, "lg": 4}
        ),
    ], spacing=16)

    # Storage by client
    storage_row = ft.Container(
        content=ft.Column([
            ft.Text("Storage by Client", size=18, weight=ft.FontWeight.W_600),
            ft.Container(
                content=storage_chart,
                height=300,
            ),
        ], spacing=12),
        padding=20,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE,
        border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
    )

    # Time period selector
    period_selector = ft.Row([
        ft.Text("Time Period:", size=14, weight=ft.FontWeight.W_500),
        ft.SegmentedButton(
            segments=[
                ft.Segment(value="7d", label=ft.Text("7 Days")),
                ft.Segment(value="30d", label=ft.Text("30 Days")),
                ft.Segment(value="90d", label=ft.Text("90 Days")),
                ft.Segment(value="all", label=ft.Text("All Time")),
            ],
            selected={"7d"},
        ),
    ], spacing=12)

    # Main content
    content = ft.Column([
        # Header
        ft.Row([
            ft.Text("Analytics Dashboard", size=28, weight=ft.FontWeight.BOLD),
            period_selector,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),

        # Metrics
        metrics_row,

        # Charts
        charts_row,

        # Storage
        storage_row,
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)

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