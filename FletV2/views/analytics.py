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

# Import neumorphic shadows from theme (using relative import to avoid circular imports)
try:
    from theme import PRONOUNCED_NEUMORPHIC_SHADOWS, MODERATE_NEUMORPHIC_SHADOWS
except ImportError:
    PRONOUNCED_NEUMORPHIC_SHADOWS = []
    MODERATE_NEUMORPHIC_SHADOWS = []

def create_analytics_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None,
    navigate_callback: Callable[[str], None] | None = None
) -> tuple[ft.Control, Callable[[], None], Callable[[], None]]:
    """Create analytics view with charts and metrics."""

    # Fetch data from server
    if server_bridge and hasattr(server_bridge, 'get_analytics_data'):
        try:
            server_data = server_bridge.get_analytics_data()
            if isinstance(server_data, dict) and server_data.get('success'):
                data = server_data.get('data', {})
                metrics = {
                    'total_backups': data.get('total_backups', 0),
                    'total_storage_gb': data.get('total_storage_gb', 0),
                    'success_rate': data.get('success_rate', 0.0),
                    'avg_backup_size_gb': data.get('avg_backup_size_gb', 0.0)
                }
            else:
                metrics = {'total_backups': 0, 'total_storage_gb': 0, 'success_rate': 0.0, 'avg_backup_size_gb': 0.0}
        except Exception:
            metrics = {'total_backups': 0, 'total_storage_gb': 0, 'success_rate': 0.0, 'avg_backup_size_gb': 0.0}
    else:
        metrics = {'total_backups': 0, 'total_storage_gb': 0, 'success_rate': 0.0, 'avg_backup_size_gb': 0.0}

    # Metric card helper
    def create_metric_card(title: str, value: str, icon: str, color: str, is_empty: bool = False) -> ft.Container:
        if is_empty:
            return ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.GREY, size=24),
                            width=48,
                            height=48,
                            bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.GREY),
                            border_radius=24,
                            alignment=ft.alignment.center,
                        ),
                        ft.Text(title, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.GREY),
                    ], spacing=12),
                    ft.Text("No data", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY),
                    ft.Text("Server not connected", size=10, color=ft.Colors.GREY),
                ], spacing=12, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                border_radius=16,
                bgcolor=ft.Colors.SURFACE,
                shadow=MODERATE_NEUMORPHIC_SHADOWS,
                expand=True,
            )
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
            shadow=MODERATE_NEUMORPHIC_SHADOWS,  # Moderate neumorphism
            expand=True,
        )

    # Metric cards row
    metrics_empty = metrics['total_backups'] == 0 and metrics['total_storage_gb'] == 0
    metrics_row = ft.ResponsiveRow([
        ft.Container(
            create_metric_card(
                "Total Backups" if not metrics_empty else "No Backups Found",
                str(metrics['total_backups']) if not metrics_empty else "",
                ft.Icons.BACKUP if not metrics_empty else ft.Icons.INFO_OUTLINE,
                ft.Colors.BLUE_400 if not metrics_empty else ft.Colors.GREY,
                is_empty=metrics_empty
            ),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            create_metric_card(
                "Total Storage" if not metrics_empty else "No Storage Data",
                f"{metrics['total_storage_gb']} GB" if not metrics_empty else "",
                ft.Icons.STORAGE if not metrics_empty else ft.Icons.INFO_OUTLINE,
                ft.Colors.GREEN_400 if not metrics_empty else ft.Colors.GREY,
                is_empty=metrics_empty
            ),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            create_metric_card(
                "Success Rate" if not metrics_empty else "No Success Data",
                f"{metrics['success_rate']}%" if not metrics_empty else "",
                ft.Icons.CHECK_CIRCLE if not metrics_empty else ft.Icons.INFO_OUTLINE,
                ft.Colors.PURPLE_400 if not metrics_empty else ft.Colors.GREY,
                is_empty=metrics_empty
            ),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
        ft.Container(
            create_metric_card(
                "Avg Backup Size" if not metrics_empty else "No Backup Size Data",
                f"{metrics['avg_backup_size_gb']} GB" if not metrics_empty else "",
                ft.Icons.PIE_CHART if not metrics_empty else ft.Icons.INFO_OUTLINE,
                ft.Colors.AMBER_400 if not metrics_empty else ft.Colors.GREY,
                is_empty=metrics_empty
            ),
            col={"sm": 12, "md": 6, "lg": 3}
        ),
    ], spacing=16)

    # Backup trend chart - handle empty or server data
    backup_trend_data = []
    if server_bridge and hasattr(server_bridge, 'get_analytics_data'):
        try:
            trend_data = server_bridge.get_analytics_data()
            if trend_data and trend_data.get('success'):
                backup_trend_data = trend_data.get('data', {}).get('backup_trend', [])
        except Exception:
            pass

    backup_trend_chart = (
        ft.LineChart(
            data_series=[
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(x, y)
                        for x, y in enumerate(backup_trend_data[:7])
                    ] if backup_trend_data else [],
                    stroke_width=3,
                    color=ft.Colors.BLUE_400,
                    curved=True,
                    stroke_cap_round=True,
                )
            ] if backup_trend_data else [],
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
            max_y=max(backup_trend_data) if backup_trend_data else 50,
            min_x=0,
            max_x=len(backup_trend_data) - 1 if backup_trend_data else 6,
        )
    )

    # Storage by client chart
    client_storage_data = []
    if server_bridge and hasattr(server_bridge, 'get_analytics_data'):
        try:
            storage_data = server_bridge.get_analytics_data()
            if storage_data and storage_data.get('success'):
                client_storage_data = storage_data.get('data', {}).get('client_storage', [])
        except Exception:
            pass

    storage_chart = ft.BarChart(
        bar_groups=[
            ft.BarChartGroup(
                x=x,
                bar_rods=[
                    ft.BarChartRod(
                        from_y=0,
                        to_y=storage,
                        width=40,
                        color=color,
                        border_radius=4
                    )
                ]
            )
            for x, (storage, color) in enumerate(
                zip(
                    client_storage_data[:4],
                    [ft.Colors.BLUE_400, ft.Colors.GREEN_400, ft.Colors.PURPLE_400, ft.Colors.AMBER_400]
                )
            )
        ] if client_storage_data else [],
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
                ft.ChartAxisLabel(value=x, label=ft.Text(f"Client {x+1}", size=10))
                for x in range(len(client_storage_data[:4]))
            ] if client_storage_data else [],
            labels_size=32,
        ),
        tooltip_bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.SURFACE),
        max_y=max(client_storage_data) if client_storage_data else 1400,
    )

    # File type distribution chart
    file_type_data = []
    if server_bridge and hasattr(server_bridge, 'get_analytics_data'):
        try:
            type_data = server_bridge.get_analytics_data()
            if type_data and type_data.get('success'):
                file_type_data = type_data.get('data', {}).get('file_type_distribution', [])
        except Exception:
            pass

    colors = [ft.Colors.BLUE_400, ft.Colors.GREEN_400, ft.Colors.PURPLE_400, ft.Colors.AMBER_400]
    default_labels = ['Documents', 'Images', 'Videos', 'Other']

    file_type_chart = ft.PieChart(
        sections=[
            ft.PieChartSection(
                value=value,
                title=label,
                color=color,
                radius=80,
            )
            for (value, label), color in zip(
                zip(
                    file_type_data if file_type_data else [40, 30, 20, 10],
                    file_type_data and len(file_type_data) >= 4
                    and ['Custom1', 'Custom2', 'Custom3', 'Custom4']
                    or default_labels
                ),
                colors
            )
        ],
        sections_space=2,
        center_space_radius=0,
    )

    charts_row = ft.ResponsiveRow([
        # Backup trends
        ft.Container(
            content=ft.Column([
                ft.Text("Backup Trends" if backup_trend_data else "No Backup Trends", size=18, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=backup_trend_chart if backup_trend_data else ft.Column([
                        ft.Icon(ft.Icons.SHOW_CHART, size=64, color=ft.Colors.GREY),
                        ft.Text("No backup trend data available", color=ft.Colors.GREY)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    height=300,
                    alignment=ft.alignment.center,
                ),
            ], spacing=12),
            padding=20,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            shadow=MODERATE_NEUMORPHIC_SHADOWS,  # Moderate neumorphism
            col={"sm": 12, "md": 12, "lg": 8}
        ),
        # File type distribution
        ft.Container(
            content=ft.Column([
                ft.Text("File Type Distribution" if file_type_data else "No File Type Distribution", size=18, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=file_type_chart if file_type_data else ft.Column([
                        ft.Icon(ft.Icons.PIE_CHART_OUTLINE, size=64, color=ft.Colors.GREY),
                        ft.Text("No file type data available", color=ft.Colors.GREY)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    height=300,
                    alignment=ft.alignment.center,
                ),
            ], spacing=12),
            padding=20,
            border_radius=16,
            bgcolor=ft.Colors.SURFACE,
            shadow=MODERATE_NEUMORPHIC_SHADOWS,  # Moderate neumorphism
            col={"sm": 12, "md": 12, "lg": 4}
        ),
    ], spacing=16)

    # Storage by client
    storage_row = ft.Container(
        content=ft.Column([
            ft.Text("Storage by Client" if client_storage_data else "No Client Storage Data", size=18, weight=ft.FontWeight.W_600),
            ft.Container(
                content=storage_chart if client_storage_data else ft.Column([
                    ft.Icon(ft.Icons.STORAGE, size=64, color=ft.Colors.GREY),
                    ft.Text("No storage data available", color=ft.Colors.GREY)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                height=300,
                alignment=ft.alignment.center,
            ),
        ], spacing=12),
        padding=20,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE,
        shadow=MODERATE_NEUMORPHIC_SHADOWS,  # Moderate neumorphism
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