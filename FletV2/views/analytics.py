#!/usr/bin/env python3
"""
Simplified Analytics View - The Flet Way
~350 lines instead of 1,256 lines of framework fighting!

Core Principle: Use Flet's built-in charts and progress components.
Real system metrics with clean, maintainable code.
"""

import flet as ft
from typing import Optional, Dict, Any
import psutil
import json
import asyncio
from datetime import datetime

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_components import themed_card, themed_button, themed_metric_card
from utils.user_feedback import show_success_message, show_error_message

logger = get_logger(__name__)


def create_analytics_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    _state_manager: StateManager
) -> ft.Control:
    """Simple analytics view with real system metrics."""
    logger.info("Creating simplified analytics view")

    # Simple state management
    current_metrics = {}
    auto_refresh_enabled = False
    refresh_task = None

    # Get real system metrics using psutil
    def get_system_metrics() -> Dict[str, Any]:
        """Get real system metrics using psutil - simple and direct."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_total_gb = memory.total / (1024**3)
            memory_used_gb = memory.used / (1024**3)
            memory_percent = memory.percent

            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_total_gb = disk.total / (1024**3)
            disk_used_gb = disk.used / (1024**3)
            disk_percent = (disk.used / disk.total) * 100

            # Network metrics
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / (1024**2)
            network_recv_mb = network.bytes_recv / (1024**2)

            # Process count (active connections approximation)
            process_count = len(psutil.pids())

            return {
                'cpu_usage': cpu_percent,
                'cpu_cores': cpu_count,
                'memory_usage': memory_percent,
                'memory_total_gb': round(memory_total_gb, 1),
                'memory_used_gb': round(memory_used_gb, 1),
                'disk_usage': disk_percent,
                'disk_total_gb': round(disk_total_gb, 1),
                'disk_used_gb': round(disk_used_gb, 1),
                'network_sent_mb': round(network_sent_mb, 1),
                'network_recv_mb': round(network_recv_mb, 1),
                'active_processes': process_count,
                'connection_status': "Connected",
                'last_updated': datetime.now().strftime("%H:%M:%S")
            }

        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            # Simple fallback data
            return {
                'cpu_usage': 45.0,
                'cpu_cores': 8,
                'memory_usage': 68.0,
                'memory_total_gb': 16.0,
                'memory_used_gb': 11.0,
                'disk_usage': 35.0,
                'disk_total_gb': 500.0,
                'disk_used_gb': 175.0,
                'network_sent_mb': 1024.0,
                'network_recv_mb': 2048.0,
                'active_processes': 150,
                'connection_status': "Mock",
                'last_updated': datetime.now().strftime("%H:%M:%S")
            }

    # Progress indicators using Flet's built-in ProgressBar
    cpu_progress = ft.ProgressBar(width=300, height=20, value=0)
    memory_progress = ft.ProgressBar(width=300, height=20, value=0, color=ft.Colors.GREEN)
    disk_progress = ft.ProgressBar(width=300, height=20, value=0, color=ft.Colors.PURPLE)

    # Metric text displays
    cpu_text = ft.Text("CPU: 0%", size=16, weight=ft.FontWeight.BOLD)
    memory_text = ft.Text("Memory: 0%", size=16, weight=ft.FontWeight.BOLD)
    disk_text = ft.Text("Disk: 0%", size=16, weight=ft.FontWeight.BOLD)
    network_text = ft.Text("Network: 0 MB", size=16, weight=ft.FontWeight.BOLD)
    last_updated_text = ft.Text("Last updated: Never", size=12)

    # Charts using Flet's built-in PieChart
    memory_chart = ft.PieChart(
        sections=[
            ft.PieChartSection(40, color=ft.Colors.BLUE, title="Used"),
            ft.PieChartSection(60, color=ft.Colors.BLUE_100, title="Free"),
        ],
        sections_space=2,
        center_space_radius=40,
        expand=True
    )

    disk_chart = ft.PieChart(
        sections=[
            ft.PieChartSection(30, color=ft.Colors.PURPLE, title="Used"),
            ft.PieChartSection(70, color=ft.Colors.PURPLE_100, title="Free"),
        ],
        sections_space=2,
        center_space_radius=40,
        expand=True
    )

    # Update all displays with new metrics
    def update_displays():
        """Update all UI components with current metrics."""
        nonlocal current_metrics
        current_metrics = get_system_metrics()

        # Update progress bars
        cpu_progress.value = current_metrics['cpu_usage'] / 100
        memory_progress.value = current_metrics['memory_usage'] / 100
        disk_progress.value = current_metrics['disk_usage'] / 100

        # Update text displays
        cpu_text.value = f"CPU: {current_metrics['cpu_usage']:.1f}% ({current_metrics['cpu_cores']} cores)"
        memory_text.value = f"Memory: {current_metrics['memory_usage']:.1f}% ({current_metrics['memory_used_gb']:.1f}/{current_metrics['memory_total_gb']:.1f} GB)"
        disk_text.value = f"Disk: {current_metrics['disk_usage']:.1f}% ({current_metrics['disk_used_gb']:.1f}/{current_metrics['disk_total_gb']:.1f} GB)"
        network_text.value = f"Network: ↑{current_metrics['network_sent_mb']:.1f} MB ↓{current_metrics['network_recv_mb']:.1f} MB"
        last_updated_text.value = f"Last updated: {current_metrics['last_updated']} ({current_metrics['connection_status']})"

        # Update charts
        memory_used_percent = current_metrics['memory_usage']
        memory_free_percent = 100 - memory_used_percent

        memory_chart.sections = [
            ft.PieChartSection(memory_used_percent, color=ft.Colors.GREEN, title="Used"),
            ft.PieChartSection(memory_free_percent, color=ft.Colors.GREEN_100, title="Free"),
        ]

        disk_used_percent = current_metrics['disk_usage']
        disk_free_percent = 100 - disk_used_percent

        disk_chart.sections = [
            ft.PieChartSection(disk_used_percent, color=ft.Colors.PURPLE, title="Used"),
            ft.PieChartSection(disk_free_percent, color=ft.Colors.PURPLE_100, title="Free"),
        ]

        # Update all controls - only if they're already attached to page
        for control in [cpu_progress, memory_progress, disk_progress, cpu_text, memory_text,
                       disk_text, network_text, last_updated_text, memory_chart, disk_chart]:
            if hasattr(control, 'update') and hasattr(control, 'page') and control.page:
                control.update()

    # Auto-refresh functionality
    async def auto_refresh_loop():
        """Simple auto-refresh loop using asyncio."""
        while auto_refresh_enabled:
            try:
                update_displays()
                await asyncio.sleep(2)  # Refresh every 2 seconds
            except Exception as e:
                logger.error(f"Auto-refresh error: {e}")
                break

    def toggle_auto_refresh(e):
        """Toggle auto-refresh on/off."""
        nonlocal auto_refresh_enabled, refresh_task

        auto_refresh_enabled = not auto_refresh_enabled

        if auto_refresh_enabled:
            refresh_task = page.run_task(auto_refresh_loop)
            auto_refresh_button.text = "Stop Auto-Refresh"
            auto_refresh_button.icon = ft.Icons.STOP
            show_success_message(page, "Auto-refresh enabled")
        else:
            auto_refresh_button.text = "Start Auto-Refresh"
            auto_refresh_button.icon = ft.Icons.PLAY_ARROW
            show_success_message(page, "Auto-refresh disabled")

        if hasattr(auto_refresh_button, 'page') and auto_refresh_button.page:
            auto_refresh_button.update()

    # Manual refresh
    def refresh_now(e):
        """Manual refresh of metrics."""
        update_displays()
        show_success_message(page, "Metrics refreshed")

    # Export functionality using FilePicker
    def save_analytics_data(e: ft.FilePickerResultEvent):
        """Export analytics data as JSON."""
        if e.path:
            try:
                export_data = {
                    'timestamp': datetime.now().isoformat(),
                    'metrics': current_metrics,
                    'system_info': {
                        'cpu_cores': current_metrics.get('cpu_cores', 0),
                        'total_memory_gb': current_metrics.get('memory_total_gb', 0),
                        'total_disk_gb': current_metrics.get('disk_total_gb', 0)
                    }
                }

                with open(e.path, 'w') as f:
                    json.dump(export_data, f, indent=2)

                show_success_message(page, f"Analytics exported to {e.path}")
            except Exception as ex:
                show_error_message(page, f"Export failed: {ex}")

    file_picker = ft.FilePicker(on_result=save_analytics_data)
    page.overlay.append(file_picker)

    def export_analytics(e):
        """Export analytics data."""
        file_picker.save_file(
            dialog_title="Export Analytics Data",
            file_name=f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"]
        )

    # Action buttons
    auto_refresh_button = themed_button(
        "Start Auto-Refresh",
        toggle_auto_refresh,
        "filled",
        ft.Icons.PLAY_ARROW
    )

    actions_row = ft.Row([
        themed_button("Refresh Now", refresh_now, "filled", ft.Icons.REFRESH),
        auto_refresh_button,
        themed_button("Export Data", export_analytics, "outlined", ft.Icons.DOWNLOAD),
        ft.Container(expand=True),  # Spacer
        last_updated_text
    ], spacing=10)

    # System info cards
    system_info_row = ft.Row([
        themed_metric_card("Processes", str(current_metrics.get('active_processes', 0)), ft.Icons.MEMORY),
        themed_metric_card("CPU Cores", str(current_metrics.get('cpu_cores', 0)), ft.Icons.DEVELOPER_BOARD),
        themed_metric_card("Total RAM", f"{current_metrics.get('memory_total_gb', 0):.1f} GB", ft.Icons.STORAGE),
        themed_metric_card("Total Disk", f"{current_metrics.get('disk_total_gb', 0):.1f} GB", ft.Icons.FOLDER),
    ], spacing=10)

    # Progress indicators section
    progress_section = ft.Column([
        ft.Text("System Usage", size=20, weight=ft.FontWeight.BOLD),
        ft.Container(height=10),

        # CPU progress
        ft.Row([
            ft.Icon(ft.Icons.DEVELOPER_BOARD, color=ft.Colors.BLUE),
            ft.Container(width=10),
            ft.Column([cpu_text, cpu_progress], spacing=5),
        ]),

        ft.Container(height=10),

        # Memory progress
        ft.Row([
            ft.Icon(ft.Icons.MEMORY, color=ft.Colors.GREEN),
            ft.Container(width=10),
            ft.Column([memory_text, memory_progress], spacing=5),
        ]),

        ft.Container(height=10),

        # Disk progress
        ft.Row([
            ft.Icon(ft.Icons.STORAGE, color=ft.Colors.PURPLE),
            ft.Container(width=10),
            ft.Column([disk_text, disk_progress], spacing=5),
        ]),

        ft.Container(height=10),

        # Network info
        ft.Row([
            ft.Icon(ft.Icons.NETWORK_CHECK, color=ft.Colors.ORANGE),
            ft.Container(width=10),
            network_text,
        ]),

    ], spacing=5)

    # Charts section
    charts_section = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Text("Memory Usage", size=16, weight=ft.FontWeight.BOLD),
                memory_chart
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            padding=10,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Disk Usage", size=16, weight=ft.FontWeight.BOLD),
                disk_chart
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            padding=10,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE
        ),
    ], spacing=20)

    # Main layout
    main_content = ft.Column([
        ft.Text("System Analytics", size=28, weight=ft.FontWeight.BOLD),
        system_info_row,
        actions_row,
        ft.Container(height=20),

        # Two-column layout for progress and charts
        ft.Row([
            ft.Container(
                content=progress_section,
                expand=1,
                padding=20,
                border_radius=12,
                bgcolor=ft.Colors.SURFACE
            ),
            ft.Container(width=20),
            ft.Container(
                content=charts_section,
                expand=1,
            ),
        ], expand=True),

    ], expand=True, spacing=20)

    # Create the main container
    analytics_container = themed_card(main_content, "System Analytics Dashboard")

    def setup_subscriptions():
        """Setup subscriptions and initial data loading after view is added to page."""
        update_displays()

    def dispose():
        """Clean up subscriptions and resources."""
        logger.debug("Disposing analytics view")
        # Remove FilePicker from page overlay
        if file_picker in page.overlay:
            page.overlay.remove(file_picker)

    return analytics_container, dispose, setup_subscriptions