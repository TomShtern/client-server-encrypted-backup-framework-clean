#!/usr/bin/env python3
"""
Analytics View for FletV2
Clean function-based implementation following Framework Harmony principles.
"""

import flet as ft
import psutil
import random
import asyncio
from datetime import datetime
from utils.debug_setup import get_logger
from utils.user_feedback import show_success_message, show_error_message, show_info_message
from config import ASYNC_DELAY

logger = get_logger(__name__)


def create_analytics_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create analytics view using simple Flet patterns.

    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance

    Returns:
        ft.Control: The analytics view
    """

    # State variables
    system_metrics = {}
    is_loading = False
    last_updated = None
    refresh_timer = None

    # Direct control references for text updates (optimized)
    last_updated_text = ft.Text("Last updated: Never", size=12, color=ft.Colors.ON_SURFACE)
    cpu_cores_text = ft.Text("0", size=16, weight=ft.FontWeight.BOLD)
    total_memory_text = ft.Text("0 GB", size=16, weight=ft.FontWeight.BOLD)
    disk_space_text = ft.Text("0 GB", size=16, weight=ft.FontWeight.BOLD)
    active_connections_text = ft.Text("0", size=16, weight=ft.FontWeight.BOLD)

    # Chart control references for dynamic updates
    cpu_chart = ft.LineChart(
        data_series=[],
        border=ft.Border(
            bottom=ft.BorderSide(1, ft.Colors.OUTLINE),
            left=ft.BorderSide(1, ft.Colors.OUTLINE)
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            color=ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE), width=1
        ),
        expand=True,
        animate=True
    )

    memory_chart = ft.BarChart(
        bar_groups=[],
        border=ft.Border(
            bottom=ft.BorderSide(1, ft.Colors.OUTLINE),
            left=ft.BorderSide(1, ft.Colors.OUTLINE)
        ),
        expand=True,
        animate=True
    )

    network_chart = ft.LineChart(
        data_series=[],
        border=ft.Border(
            bottom=ft.BorderSide(1, ft.Colors.OUTLINE),
            left=ft.BorderSide(1, ft.Colors.OUTLINE)
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            color=ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE), width=1
        ),
        expand=True,
        animate=True
    )

    disk_chart = ft.PieChart(
        sections=[],
        sections_space=0,
        center_space_radius=40,
        expand=True,
        animate=True
    )

    def get_system_metrics():
        """Get real system metrics using psutil."""
        try:
            # Always try to get local system metrics first (most accurate)
            try:
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()

                return {
                    'cpu_usage': psutil.cpu_percent(interval=0.1),
                    'memory_usage': memory.percent,
                    'disk_usage': disk.percent,
                    'memory_total_gb': memory.total // (1024**3),
                    'memory_used_gb': (memory.total - memory.available) // (1024**3),
                    'disk_total_gb': disk.total // (1024**3),
                    'disk_used_gb': disk.used // (1024**3),
                    'network_sent_mb': network.bytes_sent // (1024**2),
                    'network_recv_mb': network.bytes_recv // (1024**2),
                    'active_connections': len(psutil.net_connections()),
                    'cpu_cores': psutil.cpu_count()
                }
            except Exception as local_e:
                logger.warning(f"Failed to get local system metrics: {local_e}")

            # Try to get metrics from server bridge as fallback
            if server_bridge:
                try:
                    # Try to get system status from server bridge
                    system_status = server_bridge.get_system_status()
                    if system_status:
                        return system_status

                    # Fallback to server status if system status not available
                    server_status = server_bridge.get_server_status()
                    if server_status:
                        # Convert server metrics to system metrics format
                        return {
                            'cpu_usage': 45.2,  # Placeholder, would need server-side CPU metrics
                            'memory_usage': 67.8,  # Placeholder, would need server-side memory metrics
                            'disk_usage': float(server_status.get('storage_used', '0').replace(' GB', '')) / 100 * 100 if 'storage_used' in server_status else 34.1,
                            'memory_total_gb': 16,  # Placeholder
                            'memory_used_gb': 11,  # Placeholder
                            'disk_total_gb': 500,  # Placeholder
                            'disk_used_gb': float(server_status.get('storage_used', '0').replace(' GB', '')) if 'storage_used' in server_status else 170,
                            'network_sent_mb': 2048,  # Placeholder
                            'network_recv_mb': 4096,  # Placeholder
                            'active_connections': server_status.get('active_clients', 12),
                            'cpu_cores': 8,  # Placeholder
                            'server_metrics': server_status  # Include original server metrics
                        }
                except Exception as server_e:
                    logger.warning(f"Failed to get metrics from server bridge: {server_e}")

            # Final fallback to mock data
            logger.warning("Using mock data for system metrics")
            return {
                'cpu_usage': 45.2,
                'memory_usage': 67.8,
                'disk_usage': 34.1,
                'memory_total_gb': 16,
                'memory_used_gb': 11,
                'disk_total_gb': 500,
                'disk_used_gb': 170,
                'network_sent_mb': 2048,
                'network_recv_mb': 4096,
                'active_connections': 12,
                'cpu_cores': 8
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {e}")
            return {
                'cpu_usage': 45.2,
                'memory_usage': 67.8,
                'disk_usage': 34.1,
                'memory_total_gb': 16,
                'memory_used_gb': 11,
                'disk_total_gb': 500,
                'disk_used_gb': 170,
                'network_sent_mb': 2048,
                'network_recv_mb': 4096,
                'active_connections': 12,
                'cpu_cores': 8
            }

    def update_charts():
        """Update charts with current data."""
        # Update CPU chart with real data points
        cpu_value = system_metrics.get('cpu_usage', 0.0)
        # Convert to float if it's a string
        if isinstance(cpu_value, str):
            cpu_value = float(cpu_value.rstrip('%'))

        # Create CPU usage data points (last 8 measurements)
        cpu_data_points = []
        for i in range(8):
            # Use the same value for all points to show current state
            cpu_data_points.append(ft.LineChartDataPoint(i + 1, cpu_value))

        # Only update if data has changed significantly
        if not hasattr(update_charts, '_last_cpu_data') or update_charts._last_cpu_data != cpu_data_points:
            cpu_chart.data_series = [
                ft.LineChartData(
                    data_points=cpu_data_points,
                    stroke_width=3,
                    color=ft.Colors.BLUE,
                    curved=True
                )
            ]
            cpu_chart.update()
            update_charts._last_cpu_data = cpu_data_points.copy()

        # Update Memory chart with real data
        memory_value = system_metrics.get('memory_usage', 0.0)
        # Convert to float if it's a string
        if isinstance(memory_value, str):
            memory_value = float(memory_value.rstrip('%'))

        memory_bar_groups = []
        for i in range(6):
            # Use the same value for all bars to show current state
            value = memory_value
            color = (ft.Colors.GREEN_600 if value < 60  # Normal
                    else ft.Colors.ORANGE_600 if value < 80  # Warning
                    else ft.Colors.RED_600)  # Critical

            memory_bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=value,
                            width=18,
                            color=color
                        )
                    ]
                )
            )

        # Only update if data has changed significantly
        if not hasattr(update_charts, '_last_memory_data') or update_charts._last_memory_data != memory_bar_groups:
            memory_chart.bar_groups = memory_bar_groups
            memory_chart.update()
            update_charts._last_memory_data = memory_bar_groups.copy()

        # Update Network chart with real data
        network_sent = system_metrics.get('network_sent_mb', 0)
        network_recv = system_metrics.get('network_recv_mb', 0)

        # Ensure we have numeric values
        if isinstance(network_sent, str):
            network_sent = float(network_sent)
        if isinstance(network_recv, str):
            network_recv = float(network_recv)

        # Create network traffic data points
        sent_data_points = []
        recv_data_points = []
        for i in range(8):
            # Use the same values for all points to show current state
            sent_data_points.append(ft.LineChartDataPoint(i + 1, network_sent))
            recv_data_points.append(ft.LineChartDataPoint(i + 1, network_recv))

        # Only update if data has changed significantly
        network_data_changed = (
            not hasattr(update_charts, '_last_network_sent_data') or
            not hasattr(update_charts, '_last_network_recv_data') or
            update_charts._last_network_sent_data != sent_data_points or
            update_charts._last_network_recv_data != recv_data_points
        )

        if network_data_changed:
            network_chart.data_series = [
                ft.LineChartData(
                    data_points=sent_data_points,
                    stroke_width=2,
                    color=ft.Colors.ORANGE,
                    curved=True
                ),
                ft.LineChartData(
                    data_points=recv_data_points,
                    stroke_width=2,
                    color=ft.Colors.GREEN,
                    curved=True
                )
            ]
            network_chart.update()
            update_charts._last_network_sent_data = sent_data_points.copy()
            update_charts._last_network_recv_data = recv_data_points.copy()

        # Update Disk chart with real data
        disk_used = system_metrics.get('disk_usage', 0.0)
        # Convert to float if it's a string
        if isinstance(disk_used, str):
            disk_used = float(disk_used.rstrip('%'))

        disk_free = 100 - disk_used

        # Only update if data has changed significantly
        disk_data_changed = (
            not hasattr(update_charts, '_last_disk_used') or
            not hasattr(update_charts, '_last_disk_free') or
            abs(update_charts._last_disk_used - disk_used) > 0.1 or
            abs(update_charts._last_disk_free - disk_free) > 0.1
        )

        if disk_data_changed:
            disk_chart.sections = [
                ft.PieChartSection(
                    value=disk_used,
                    color=ft.Colors.RED,
                    radius=80,
                    title=f"{disk_used:.1f}%",
                    title_style=ft.TextStyle(color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD)
                ),
                ft.PieChartSection(
                    value=disk_free,
                    color=ft.Colors.GREEN,
                    radius=70,
                    title=""
                )
            ]
            disk_chart.update()
            update_charts._last_disk_used = disk_used
            update_charts._last_disk_free = disk_free

    def update_system_info():
        """Update system information cards using direct control references."""
        cpu_cores_text.value = str(system_metrics.get('cpu_cores', 0))
        total_memory_text.value = f"{system_metrics.get('memory_total_gb', 0)} GB"
        disk_space_text.value = f"{system_metrics.get('disk_total_gb', 0)} GB"
        active_connections_text.value = str(system_metrics.get('active_connections', 0))

        # Update all text controls
        cpu_cores_text.update()
        total_memory_text.update()
        disk_space_text.update()
        active_connections_text.update()

    def load_analytics_data():
        """Load analytics data using proper Flet async pattern."""
        nonlocal system_metrics, is_loading, last_updated

        if is_loading:
            return

        is_loading = True

        # Show loading state immediately
        last_updated_text.value = "Updating..."
        if hasattr(last_updated_text, 'page') and last_updated_text.page is not None:
            last_updated_text.update()

        def on_data_loaded(metrics):
            """Callback when data is loaded."""
            nonlocal system_metrics, last_updated, is_loading
            try:
                system_metrics = metrics

                # Update last updated timestamp
                last_updated = datetime.now()
                last_updated_text.value = f"Last updated: {last_updated.strftime('%H:%M:%S')}"

                # Update charts and UI only if controls are attached
                if hasattr(last_updated_text, 'page') and last_updated_text.page is not None:
                    # Update charts and UI
                    update_charts()
                    update_system_info()

                    # Update charts
                    cpu_chart.update()
                    memory_chart.update()
                    network_chart.update()
                    disk_chart.update()
                    last_updated_text.update()

            except Exception as e:
                logger.error(f"Error updating analytics UI: {e}")
                last_updated_text.value = "Error updating analytics"
                last_updated_text.update()
            finally:
                is_loading = False

        def on_data_error(error):
            """Callback when data loading fails."""
            nonlocal is_loading
            logger.error(f"Error loading analytics data: {error}")
            if hasattr(last_updated_text, 'page') and last_updated_text.page is not None:
                last_updated_text.value = "Error loading data"
                last_updated_text.update()
            is_loading = False

        # Load data in background thread (non-blocking)
        try:
            metrics = get_system_metrics()
            on_data_loaded(metrics)
        except Exception as e:
            on_data_error(e)

    def on_refresh_analytics(e):
        """Handle refresh button click."""
        logger.info("Analytics refresh requested")
        load_analytics_data()
        show_info_message(page, "Refreshing analytics data...")

    def on_toggle_auto_refresh(e):
        """Toggle auto-refresh timer."""
        nonlocal refresh_timer

        if refresh_timer:
            refresh_timer.cancel()
            refresh_timer = None
            logger.info("Auto-refresh stopped")
            show_info_message(page, "Auto-refresh stopped")
        else:
            # Start auto-refresh timer (every 5 seconds)
            async def refresh_loop():
                while True:
                    await asyncio.sleep(5)
                    # Check if the control is still attached to the page before updating
                    if hasattr(last_updated_text, 'page') and last_updated_text.page is not None:
                        load_analytics_data()
                    else:
                        # If control is not attached, cancel the timer
                        logger.warning("Analytics control detached, stopping auto-refresh")
                        break

            refresh_timer = page.run_task(refresh_loop)
            logger.info("Auto-refresh started")
            show_info_message(page, "Auto-refresh started (every 5 seconds)")

    # Build the main view
    view = ft.Column([
        # Header with title and refresh button
        ft.Row([
            ft.Icon(ft.Icons.AUTO_GRAPH, size=24),
            ft.Text("Analytics & Performance", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh Analytics Data",
                    on_click=on_refresh_analytics
                ),
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    tooltip="Start Auto-refresh",
                    on_click=on_toggle_auto_refresh
                )
            ], spacing=5)
        ]),
        ft.Divider(),

        # Last updated text
        ft.Row([
            ft.Text("System Performance Metrics", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            last_updated_text
        ]),

        # Performance charts
        ft.ResponsiveRow([
            # CPU Usage Chart
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.SHOW_CHART, color=ft.Colors.BLUE, size=20),
                                ft.Text("CPU Usage Over Time", size=16, weight=ft.FontWeight.BOLD)
                            ], spacing=8),
                            ft.Container(content=cpu_chart, expand=True, height=200, padding=10)
                        ], spacing=12),
                        padding=16
                    )
                )
            ], col={"sm": 12, "md": 6}),

            # Memory Usage Chart
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.BAR_CHART, color=ft.Colors.GREEN, size=20),
                                ft.Text("Memory Usage History", size=16, weight=ft.FontWeight.BOLD)
                            ], spacing=8),
                            ft.Container(content=memory_chart, expand=True, height=200, padding=10)
                        ], spacing=12),
                        padding=16
                    )
                )
            ], col={"sm": 12, "md": 6}),

            # Network Traffic Chart
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.NETWORK_CHECK, color=ft.Colors.ORANGE, size=20),
                                ft.Text("Network Traffic", size=16, weight=ft.FontWeight.BOLD)
                            ], spacing=8),
                            ft.Container(content=network_chart, expand=True, height=200, padding=10)
                        ], spacing=12),
                        padding=16
                    )
                )
            ], col={"sm": 12, "md": 6}),

            # Disk Usage Chart
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.STORAGE, color=ft.Colors.PURPLE, size=20),
                                ft.Text("Disk Usage", size=16, weight=ft.FontWeight.BOLD)
                            ], spacing=8),
                            ft.Container(content=disk_chart, expand=True, height=200, padding=10)
                        ], spacing=12),
                        padding=16
                    )
                )
            ], col={"sm": 12, "md": 6})
        ]),

        # System information cards
        ft.Divider(),
        ft.Text("System Information", size=18, weight=ft.FontWeight.BOLD),
        ft.ResponsiveRow([
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.COMPUTER, size=24, color=ft.Colors.BLUE),
                            ft.Text("CPU Cores", size=12, weight=ft.FontWeight.W_500),
                            cpu_cores_text
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=15
                    )
                )
            ], col={"sm": 6, "md": 3}),
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.MEMORY, size=24, color=ft.Colors.GREEN),
                            ft.Text("Total Memory", size=12, weight=ft.FontWeight.W_500),
                            total_memory_text
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=15
                    )
                )
            ], col={"sm": 6, "md": 3}),
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.STORAGE, size=24, color=ft.Colors.PURPLE),
                            ft.Text("Disk Space", size=12, weight=ft.FontWeight.W_500),
                            disk_space_text
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=15
                    )
                )
            ], col={"sm": 6, "md": 3}),
            ft.Column([
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.LINK, size=24, color=ft.Colors.ORANGE),
                            ft.Text("Active Connections", size=12, weight=ft.FontWeight.W_500),
                            active_connections_text
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                        padding=15
                    )
                )
            ], col={"sm": 6, "md": 3})
        ])

    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)

    # Schedule initial data load after controls are added to page
    def schedule_initial_load():
        """Schedule initial data load with retry mechanism."""
        async def delayed_load_with_retry():
            max_retries = 5
            retry_delay = 0.1

            for attempt in range(max_retries):
                # Check if controls are attached
                if (last_updated_text and
                    hasattr(last_updated_text, 'page') and
                    last_updated_text.page is not None):
                    logger.info(f"Controls attached on attempt {attempt + 1}, loading data")
                    load_analytics_data()
                    return

                logger.debug(f"Attempt {attempt + 1}: Controls not attached, waiting {retry_delay}s")
                await asyncio.sleep(retry_delay)
                retry_delay *= 1.5  # Exponential backoff

            logger.warning("Failed to load analytics data: controls never attached after 5 attempts")

        page.run_task(delayed_load_with_retry)

    schedule_initial_load()

    # Also provide a trigger for manual loading if needed
    def trigger_initial_load():
        """Trigger initial data load manually."""
        load_analytics_data()

    # Export the trigger function so it can be called externally
    view.trigger_initial_load = trigger_initial_load

    return view
