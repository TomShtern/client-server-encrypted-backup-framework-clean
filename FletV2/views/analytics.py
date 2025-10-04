#!/usr/bin/env python3
"""
Analytics View - Data Visualization Dashboard
Shows backup statistics with charts and metrics.
"""

import os
import sys
from collections.abc import Coroutine
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
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    """Create analytics view with charts and metrics.

    Returns:
        tuple: (main_container, dispose_func, setup_subscriptions_async_func)
            - main_container: The main UI control for the analytics view
            - dispose_func: Cleanup function (synchronous)
            - setup_subscriptions_async_func: Async setup function for data loading
    """

    # Initialize with placeholder data (will load async in setup_subscriptions)
    metrics = {'total_backups': 0, 'total_storage_gb': 0, 'success_rate': 0.0, 'avg_backup_size_gb': 0.0}
    backup_trend_data = []
    client_storage_data = []
    file_type_data = []

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

    # Backup trend chart - SIMPLIFIED to prevent browser crashes
    # Complex charts (LineChart) cause fatal glitches in Flet 0.28.3
    # backup_trend_data initialized at top with empty list, will be loaded async

    # Simple bar visualization instead of LineChart
    backup_trend_bars = ft.Column([
        ft.Row([
            ft.Container(
                width=40,
                height=max(1, int(val * 3)) if backup_trend_data else 20,  # Scale height
                bgcolor=ft.Colors.BLUE_400,
                border_radius=4,
                tooltip=f"Day {i+1}: {val} backups" if backup_trend_data else "",
            )
            for i, val in enumerate(backup_trend_data[:7] if backup_trend_data else [10, 20, 15, 25, 30, 22, 28])
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
        ft.Row([
            ft.Text(f"{i+1}", size=10, color=ft.Colors.GREY)
            for i in range(7)
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
    ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # Storage by client chart - SIMPLIFIED to prevent crashes
    # client_storage_data initialized at top with empty list, will be loaded async

    # Simple progress bars instead of BarChart
    storage_bars = ft.Column([
        ft.Row([
            ft.Text(f"Client {i+1}", size=12, width=80),
            ft.Container(
                content=ft.ProgressBar(value=val/1400 if client_storage_data else 0.3, color=color, bgcolor=ft.Colors.with_opacity(0.2, color)),
                expand=True,
            ),
            ft.Text(f"{val} GB" if client_storage_data else f"{int(val*1000)} GB", size=12, width=80),
        ], spacing=12)
        for i, (val, color) in enumerate(zip(
            client_storage_data[:4] if client_storage_data else [0.8, 0.6, 0.4, 0.5],
            [ft.Colors.BLUE_400, ft.Colors.GREEN_400, ft.Colors.PURPLE_400, ft.Colors.AMBER_400]
        ))
    ], spacing=16)

    # File type distribution chart - SIMPLIFIED to prevent crashes
    # file_type_data initialized at top with empty list, will be loaded async

    colors = [ft.Colors.BLUE_400, ft.Colors.GREEN_400, ft.Colors.PURPLE_400, ft.Colors.AMBER_400]
    default_labels = ['Documents', 'Images', 'Videos', 'Other']
    default_values = [40, 30, 20, 10]

    # Simple circular progress indicators instead of PieChart
    file_type_viz = ft.Column([
        ft.Row([
            ft.Column([
                ft.ProgressRing(value=val/100, color=color, width=80, height=80, stroke_width=8),
                ft.Text(label, size=12, text_align=ft.TextAlign.CENTER),
                ft.Text(f"{val}%", size=10, color=ft.Colors.GREY),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
            for (val, label), color in zip(
                zip(
                    file_type_data if file_type_data else default_values,
                    file_type_data and len(file_type_data) >= 4
                    and ['Custom1', 'Custom2', 'Custom3', 'Custom4']
                    or default_labels
                ),
                colors
            )
        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, wrap=True),
    ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    charts_row = ft.ResponsiveRow([
        # Backup trends
        ft.Container(
            content=ft.Column([
                ft.Text("Backup Trends" if backup_trend_data else "No Backup Trends", size=18, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=backup_trend_bars if backup_trend_data else ft.Column([
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
                    content=file_type_viz if file_type_data else ft.Column([
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
                content=storage_bars if client_storage_data else ft.Column([
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

    async def load_analytics_data_async() -> None:
        """Load analytics data from server and update UI controls (async version - NON-BLOCKING)."""
        nonlocal metrics, backup_trend_data, client_storage_data, file_type_data

        if not server_bridge:
            # No server bridge available, keep placeholder data
            return

        try:
            # Fetch analytics data from server using BackupServer's async method
            # This avoids connection pool exhaustion issues
            server_data = await server_bridge._call_real_server_method_async('get_analytics_data_async')
            if not isinstance(server_data, dict) or not server_data.get('success'):
                # Server call failed, keep placeholder data
                return

            data = server_data.get('data', {})

            # Update metrics
            metrics = {
                'total_backups': data.get('total_backups', 0),
                'total_storage_gb': data.get('total_storage_gb', 0),
                'success_rate': data.get('success_rate', 0.0),
                'avg_backup_size_gb': data.get('avg_backup_size_gb', 0.0)
            }

            # Update chart data
            backup_trend_data = data.get('backup_trend', [])
            client_storage_data = data.get('client_storage', [])
            file_type_data = data.get('file_type_distribution', [])

            # Rebuild metric cards with new data
            metrics_empty = metrics['total_backups'] == 0 and metrics['total_storage_gb'] == 0
            new_metrics = [
                create_metric_card(
                    "Total Backups" if not metrics_empty else "No Backups Found",
                    str(metrics['total_backups']) if not metrics_empty else "",
                    ft.Icons.BACKUP if not metrics_empty else ft.Icons.INFO_OUTLINE,
                    ft.Colors.BLUE_400 if not metrics_empty else ft.Colors.GREY,
                    is_empty=metrics_empty
                ),
                create_metric_card(
                    "Total Storage" if not metrics_empty else "No Storage Data",
                    f"{metrics['total_storage_gb']} GB" if not metrics_empty else "",
                    ft.Icons.STORAGE if not metrics_empty else ft.Icons.INFO_OUTLINE,
                    ft.Colors.GREEN_400 if not metrics_empty else ft.Colors.GREY,
                    is_empty=metrics_empty
                ),
                create_metric_card(
                    "Success Rate" if not metrics_empty else "No Success Data",
                    f"{metrics['success_rate']}%" if not metrics_empty else "",
                    ft.Icons.CHECK_CIRCLE if not metrics_empty else ft.Icons.INFO_OUTLINE,
                    ft.Colors.PURPLE_400 if not metrics_empty else ft.Colors.GREY,
                    is_empty=metrics_empty
                ),
                create_metric_card(
                    "Avg Backup Size" if not metrics_empty else "No Backup Size Data",
                    f"{metrics['avg_backup_size_gb']} GB" if not metrics_empty else "",
                    ft.Icons.PIE_CHART if not metrics_empty else ft.Icons.INFO_OUTLINE,
                    ft.Colors.AMBER_400 if not metrics_empty else ft.Colors.GREY,
                    is_empty=metrics_empty
                ),
            ]

            # Update metrics row controls
            if hasattr(metrics_row, 'controls') and len(metrics_row.controls) == 4:
                for i, new_card in enumerate(new_metrics):
                    metrics_row.controls[i].content = new_card

            # Update backup trend bars
            new_bars = ft.Row([
                ft.Container(
                    width=40,
                    height=max(1, int(val * 3)),
                    bgcolor=ft.Colors.BLUE_400,
                    border_radius=4,
                    tooltip=f"Day {i+1}: {val} backups",
                )
                for i, val in enumerate(backup_trend_data[:7] if backup_trend_data else [])
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)

            # Safely update backup trend bars only if fully attached
            if (hasattr(backup_trend_bars, 'controls') and len(backup_trend_bars.controls) > 0
                and hasattr(backup_trend_bars, 'page') and backup_trend_bars.page):
                backup_trend_bars.controls[0] = new_bars

            # Update storage bars
            if client_storage_data:
                new_storage_bars = [
                    ft.Row([
                        ft.Text(f"Client {i+1}", size=12, width=80),
                        ft.Container(
                            content=ft.ProgressBar(value=val/1400, color=color, bgcolor=ft.Colors.with_opacity(0.2, color)),
                            expand=True,
                        ),
                        ft.Text(f"{val} GB", size=12, width=80),
                    ], spacing=12)
                    for i, (val, color) in enumerate(zip(
                        client_storage_data[:4],
                        [ft.Colors.BLUE_400, ft.Colors.GREEN_400, ft.Colors.PURPLE_400, ft.Colors.AMBER_400]
                    ))
                ]
                # Safely update only if attached to page
                if (hasattr(storage_bars, 'controls')
                    and hasattr(storage_bars, 'page') and storage_bars.page):
                    storage_bars.controls = new_storage_bars

            # Update file type visualization
            if file_type_data and len(file_type_data) >= 4:
                new_file_type_viz = ft.Row([
                    ft.Column([
                        ft.ProgressRing(value=val/100, color=color, width=80, height=80, stroke_width=8),
                        ft.Text(label, size=12, text_align=ft.TextAlign.CENTER),
                        ft.Text(f"{val}%", size=10, color=ft.Colors.GREY),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
                    for (val, label), color in zip(
                        zip(file_type_data[:4], ['Type 1', 'Type 2', 'Type 3', 'Type 4']),
                        colors
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, wrap=True)

                # Safely update only if attached to page
                if (hasattr(file_type_viz, 'controls') and len(file_type_viz.controls) > 0
                    and hasattr(file_type_viz, 'page') and file_type_viz.page):
                    file_type_viz.controls[0] = new_file_type_viz

            # Update all controls if attached to page (each control checked individually)
            if hasattr(metrics_row, 'page') and metrics_row.page:
                try:
                    metrics_row.update()
                except Exception:
                    pass  # Silently ignore if not yet attached

            if hasattr(backup_trend_bars, 'page') and backup_trend_bars.page:
                try:
                    backup_trend_bars.update()
                except Exception:
                    pass

            if hasattr(storage_bars, 'page') and storage_bars.page:
                try:
                    storage_bars.update()
                except Exception:
                    pass

            if hasattr(file_type_viz, 'page') and file_type_viz.page:
                try:
                    file_type_viz.update()
                except Exception:
                    pass

        except Exception as ex:
            # Log error but don't crash the UI
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to load analytics data: {ex}")

    def dispose():
        """Cleanup."""
        pass

    async def setup_subscriptions():
        """Setup - Load analytics data asynchronously after view is attached."""
        # CRITICAL: Delay to ensure view is fully attached to page AND AnimatedSwitcher transition completed
        # Total delay chain: main.py (250ms) + this (500ms) = 750ms total
        # This prevents "Control must be added to page first" errors
        import asyncio
        await asyncio.sleep(0.5)  # Increased from 0.2 to 0.5 seconds for robust page attachment

        # Load data asynchronously using TRUE async function (NOT fake wrapper!)
        page.run_task(load_analytics_data_async)

    return main_container, dispose, setup_subscriptions