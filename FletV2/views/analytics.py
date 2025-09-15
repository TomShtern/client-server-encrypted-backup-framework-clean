#!/usr/bin/env python3
"""
Analytics View for FletV2
Clean function-based implementation following Framework Harmony principles.
Enhanced with Material Design 3 progress indicators, loading states, and server bridge integration.
"""

import flet as ft
from typing import Optional
import psutil
import random
import asyncio
import os
from datetime import datetime
from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.dialog_consolidation_helper import show_success_message, show_error_message, show_user_feedback
from utils.server_mediated_operations import create_server_mediated_operations

logger = get_logger(__name__)


def create_analytics_view(
    server_bridge: Optional[ServerBridge], 
    page: ft.Page, 
    state_manager: StateManager
) -> ft.Control:
    """
    Create analytics view with enhanced infrastructure and state management.

    Args:
        server_bridge: Enhanced server bridge for data access
        page: Flet page instance
        state_manager: Reactive state manager for cross-view data sharing

    Returns:
        ft.Control: The analytics view
    """
    logger.info("Creating analytics view with enhanced infrastructure")

    # Initialize server operations for async patterns
    server_ops = create_server_mediated_operations(state_manager, page) if state_manager else None

    # State variables
    system_metrics = {}
    is_loading = False
    last_updated = None
    refresh_timer = None
    timer_cancelled = False  # Flag to prevent timer races and leaks
    connection_status = "disconnected"  # Track server connection status
    
    # Chart state management with historical data tracking
    chart_state = {
        'last_cpu_data': None,
        'last_memory_data': None,
        'last_network_sent_data': None,
        'last_network_recv_data': None,
        'last_disk_used': None,
        'last_disk_free': None,
        'cpu_history': [],  # Store last 20 CPU readings
        'memory_history': [],  # Store last 20 memory readings
        'network_sent_history': [],  # Store network sent history
        'network_recv_history': []  # Store network received history
    }

    # Direct control references for text updates (optimized)
    last_updated_text = ft.Text("Last updated: Never", size=12, color=ft.Colors.ON_SURFACE)
    cpu_cores_text = ft.Text("0", size=16, weight=ft.FontWeight.BOLD)
    total_memory_text = ft.Text("0 GB", size=16, weight=ft.FontWeight.BOLD)
    disk_space_text = ft.Text("0 GB", size=16, weight=ft.FontWeight.BOLD)
    active_connections_text = ft.Text("0", size=16, weight=ft.FontWeight.BOLD)
    
    # Material Design 3 progress indicators
    # Create simple progress indicators since we can't import ui_components here
    def create_simple_progress_indicator(value, label, color):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(label, size=14, weight=ft.FontWeight.W_500),
                    ft.Text(f"{value*100:.1f}%", size=12, weight=ft.FontWeight.W_500)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.ProgressBar(value=value, color=color, height=8, border_radius=4)
            ], spacing=4),
            padding=ft.Padding(0, 8, 0, 8)
        )
    
    cpu_progress = create_simple_progress_indicator(0.0, "CPU Usage", ft.Colors.BLUE)
    memory_progress = create_simple_progress_indicator(0.0, "Memory Usage", ft.Colors.GREEN)
    disk_progress = create_simple_progress_indicator(0.0, "Disk Usage", ft.Colors.PURPLE)
    network_progress = create_simple_progress_indicator(0.0, "Network Load", ft.Colors.ORANGE)
    
    # Status indicators (simple version since we can't import ui_components)
    def create_simple_status_chip(text, color):
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=12, color=ft.Colors.WHITE),
                ft.Text(text, size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500)
            ], spacing=4, tight=True),
            bgcolor=color,
            border_radius=12,
            padding=ft.Padding(8, 4, 8, 4)
        )
    
    connection_status_chip = create_simple_status_chip("Disconnected", ft.Colors.RED)
    server_status_chip = create_simple_status_chip("Offline", ft.Colors.RED)

    # Enhanced Chart control references with wow factor styling
    cpu_chart = ft.LineChart(
        data_series=[],
        border=ft.Border(
            bottom=ft.BorderSide(2, ft.Colors.BLUE_300),
            left=ft.BorderSide(2, ft.Colors.BLUE_300),
            top=ft.BorderSide(1, ft.Colors.BLUE_100),
            right=ft.BorderSide(1, ft.Colors.BLUE_100)
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE_200), width=1
        ),
        vertical_grid_lines=ft.ChartGridLines(
            color=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_200), width=0.5
        ),
        expand=True,
        animate=ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT),
        tooltip_bgcolor=ft.Colors.BLUE_50,
        interactive=True,
        min_y=0,
        max_y=100
    )

    memory_chart = ft.BarChart(
        bar_groups=[],
        border=ft.Border(
            bottom=ft.BorderSide(2, ft.Colors.GREEN_300),
            left=ft.BorderSide(2, ft.Colors.GREEN_300),
            top=ft.BorderSide(1, ft.Colors.GREEN_100),
            right=ft.BorderSide(1, ft.Colors.GREEN_100)
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            color=ft.Colors.with_opacity(0.3, ft.Colors.GREEN_200), width=1
        ),
        expand=True,
        animate=ft.Animation(600, ft.AnimationCurve.BOUNCE_IN),
        tooltip_bgcolor=ft.Colors.GREEN_50,
        interactive=True
    )

    network_chart = ft.LineChart(
        data_series=[],
        border=ft.Border(
            bottom=ft.BorderSide(2, ft.Colors.PURPLE_300),
            left=ft.BorderSide(2, ft.Colors.PURPLE_300),
            top=ft.BorderSide(1, ft.Colors.PURPLE_100),
            right=ft.BorderSide(1, ft.Colors.PURPLE_100)
        ),
        horizontal_grid_lines=ft.ChartGridLines(
            color=ft.Colors.with_opacity(0.3, ft.Colors.PURPLE_200), width=1
        ),
        vertical_grid_lines=ft.ChartGridLines(
            color=ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_200), width=0.5
        ),
        expand=True,
        animate=ft.Animation(700, ft.AnimationCurve.ELASTIC_OUT),
        tooltip_bgcolor=ft.Colors.PURPLE_50,
        interactive=True
    )

    disk_chart = ft.PieChart(
        sections=[],
        sections_space=3,
        center_space_radius=50,
        expand=True,
        animate=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT_CUBIC),
        on_chart_event=lambda e: logger.info(f"Disk chart clicked: {e}")
    )

    def get_fallback_metrics():
        """Get fallback metrics for when server is unavailable."""
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
            'cpu_cores': 8,
            'connection_status': "Fallback",
            'server_status': "Unavailable"
        }

    async def get_system_metrics_async():
        """Async version of system metrics collection using server operations pattern."""
        if server_ops:
            try:
                # Use server operations for async data loading
                result = await server_ops.load_data_operation(
                    state_key="system_metrics",
                    server_operation="get_system_status_async",
                    fallback_data=get_fallback_metrics()
                )

                if result.get('success'):
                    return result.get('data', get_fallback_metrics())
                else:
                    logger.warning(f"Server operations failed: {result.get('error')}")
                    return get_fallback_metrics()
            except Exception as e:
                logger.error(f"Async system metrics failed: {e}")
                return get_fallback_metrics()
        else:
            # Fallback to sync method if no server_ops
            return get_system_metrics_sync()

    def get_system_metrics_sync():
        """Get system metrics prioritizing server bridge data over local system data with enhanced server integration."""
        try:
            # FIRST: Try to get metrics from server bridge (remote server system metrics)
            if server_bridge:
                try:
                    # Check connection status first
                    is_connected = server_bridge.is_connected()
                    connection_status = "Connected" if is_connected else "Disconnected"
                    
                    # Try to get system status from server bridge (preferred - remote server metrics)
                    system_status = server_bridge.get_system_status()
                    if system_status:
                        logger.info("Using server bridge system status data")
                        # Add connection status to metrics
                        system_status['connection_status'] = connection_status
                        system_status['server_status'] = "Online" if is_connected else "Offline"
                        return system_status

                    # Fallback to server status if system status not available
                    server_status = server_bridge.get_server_status()
                    if server_status:
                        logger.info("Using server bridge server status data")
                        # Safely extract storage info
                        storage_used_str = server_status.get('storage_used', '0 GB')
                        try:
                            # Extract numeric value from storage string
                            storage_used_gb = float(storage_used_str.replace(' GB', '').replace('GB', ''))
                        except (ValueError, AttributeError):
                            storage_used_gb = 170.0  # Default fallback
                        
                        # Convert server metrics to system metrics format
                        metrics = {
                            'cpu_usage': server_status.get('cpu_usage', 45.2),  # Try to get real CPU data
                            'memory_usage': server_status.get('memory_usage', 67.8),  # Try to get real memory data
                            'disk_usage': min(storage_used_gb / 500 * 100, 100.0),  # Safe percentage calculation
                            'memory_total_gb': server_status.get('memory_total_gb', 16),
                            'memory_used_gb': server_status.get('memory_used_gb', 11),
                            'disk_total_gb': server_status.get('disk_total_gb', 500),
                            'disk_used_gb': storage_used_gb,
                            'network_sent_mb': server_status.get('network_sent_mb', 2048),
                            'network_recv_mb': server_status.get('network_recv_mb', 4096),
                            'active_connections': server_status.get('active_clients', 12),
                            'cpu_cores': server_status.get('cpu_cores', 8),
                            'server_metrics': server_status,  # Include original server metrics
                            'connection_status': connection_status,
                            'server_status': "Online" if is_connected else "Offline"
                        }
                        return metrics
                except Exception as server_e:
                    logger.warning(f"Failed to get metrics from server bridge: {server_e}")
                    # Update connection status
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
                        'cpu_cores': 8,
                        'connection_status': "Error",
                        'server_status': "Offline"
                    }

            # SECOND: Fallback to local system metrics using psutil
            try:
                logger.info("Falling back to local system metrics using psutil")
                memory = psutil.virtual_memory()
                # Cross-platform disk usage - Windows/Linux compatible
                if os.name == 'nt':  # Windows
                    disk = psutil.disk_usage('C:\\')
                else:  # Unix/Linux/macOS
                    disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()

                # Safe network connections count with timeout
                try:
                    active_connections = len(psutil.net_connections())
                except (psutil.AccessDenied, psutil.TimeoutExpired):
                    logger.warning("Cannot access network connections, using fallback")
                    active_connections = 0
                
                metrics = {
                    'cpu_usage': psutil.cpu_percent(interval=0.1),
                    'memory_usage': memory.percent,
                    'disk_usage': disk.percent,
                    'memory_total_gb': memory.total // (1024**3),
                    'memory_used_gb': (memory.total - memory.available) // (1024**3),
                    'disk_total_gb': disk.total // (1024**3),
                    'disk_used_gb': disk.used // (1024**3),
                    'network_sent_mb': network.bytes_sent // (1024**2),
                    'network_recv_mb': network.bytes_recv // (1024**2),
                    'active_connections': active_connections,
                    'cpu_cores': psutil.cpu_count(),
                    'connection_status': "Local",
                    'server_status': "N/A"
                }
                return metrics
            except Exception as local_e:
                logger.warning(f"Failed to get local system metrics: {local_e}")

            # FINAL: Last resort fallback (should rarely be used now)
            logger.warning("Using final fallback data for system metrics")
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
                'cpu_cores': 8,
                'connection_status': "Fallback",
                'server_status': "Unavailable"
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
                'cpu_cores': 8,
                'connection_status': "Error",
                'server_status': "Error"
            }

    def safe_float_conversion(value, default=0.0):
        """Safely convert value to float with proper error handling."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                # Remove common suffixes and convert
                cleaned_value = value.rstrip('%').strip()
                return float(cleaned_value)
            except (ValueError, AttributeError):
                logger.warning(f"Failed to convert '{value}' to float, using default {default}")
                return default
        return default

    def update_charts():
        """Update charts with current data and historical tracking."""
        # Update CPU chart with historical data
        cpu_value = safe_float_conversion(system_metrics.get('cpu_usage', 0.0))
        
        # Add current value to history and maintain max 20 points
        chart_state['cpu_history'].append(cpu_value)
        if len(chart_state['cpu_history']) > 20:
            chart_state['cpu_history'].pop(0)

        # Create CPU usage data points from history
        cpu_data_points = []
        for i, value in enumerate(chart_state['cpu_history']):
            cpu_data_points.append(ft.LineChartDataPoint(i + 1, value))

        # Only update if data has changed significantly or we have new data
        if chart_state['last_cpu_data'] != cpu_data_points:
            cpu_chart.data_series = [
                ft.LineChartData(
                    data_points=cpu_data_points,
                    stroke_width=4,
                    color=ft.Colors.BLUE_600,
                    curved=True,
                    stroke_cap_round=True,
                    # below_line with area filling not available in Flet 0.28.3
                    # Using gradient stroke for visual appeal instead
                )
            ]
            cpu_chart.update()
            chart_state['last_cpu_data'] = cpu_data_points.copy()

        # Update Memory chart with historical data
        memory_value = safe_float_conversion(system_metrics.get('memory_usage', 0.0))
        
        # Add current value to history and maintain max 6 points for bar chart
        chart_state['memory_history'].append(memory_value)
        if len(chart_state['memory_history']) > 6:
            chart_state['memory_history'].pop(0)

        memory_bar_groups = []
        history_to_use = chart_state['memory_history'] if chart_state['memory_history'] else [memory_value]
        
        for i, value in enumerate(history_to_use):
            # Enhanced color scheme - Fixed without gradients
            if value < 60:  # Normal - Green
                color = ft.Colors.GREEN_600
                border_color = ft.Colors.GREEN_300
            elif value < 80:  # Warning - Orange  
                color = ft.Colors.ORANGE_600
                border_color = ft.Colors.ORANGE_300
            else:  # Critical - Red
                color = ft.Colors.RED_600
                border_color = ft.Colors.RED_300

            memory_bar_groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[
                        ft.BarChartRod(
                            from_y=0,
                            to_y=value,
                            width=24,  # Wider bars for better visibility
                            color=color,
                            border_radius=ft.BorderRadius(6, 6, 0, 0),  # More rounded tops
                            tooltip=f"Memory: {value:.1f}%"
                        )
                    ]
                )
            )

        # Only update if data has changed significantly
        if chart_state['last_memory_data'] != memory_bar_groups:
            memory_chart.bar_groups = memory_bar_groups
            memory_chart.update()
            chart_state['last_memory_data'] = memory_bar_groups.copy()

        # Update Network chart with historical data tracking
        network_sent = safe_float_conversion(system_metrics.get('network_sent_mb', 0))
        network_recv = safe_float_conversion(system_metrics.get('network_recv_mb', 0))

        # Add current values to history and maintain max 15 points
        chart_state['network_sent_history'].append(network_sent)
        chart_state['network_recv_history'].append(network_recv)
        
        if len(chart_state['network_sent_history']) > 15:
            chart_state['network_sent_history'].pop(0)
        if len(chart_state['network_recv_history']) > 15:
            chart_state['network_recv_history'].pop(0)

        # Create network traffic data points from history
        sent_data_points = []
        recv_data_points = []
        
        sent_history = chart_state['network_sent_history'] if chart_state['network_sent_history'] else [network_sent]
        recv_history = chart_state['network_recv_history'] if chart_state['network_recv_history'] else [network_recv]
        
        for i, sent_val in enumerate(sent_history):
            sent_data_points.append(ft.LineChartDataPoint(i + 1, sent_val))
        
        for i, recv_val in enumerate(recv_history):
            recv_data_points.append(ft.LineChartDataPoint(i + 1, recv_val))

        # Only update if data has changed significantly
        network_data_changed = (
            chart_state['last_network_sent_data'] != sent_data_points or
            chart_state['last_network_recv_data'] != recv_data_points
        )

        if network_data_changed:
            network_chart.data_series = [
                ft.LineChartData(
                    data_points=sent_data_points,
                    stroke_width=3,
                    color=ft.Colors.ORANGE_600,
                    curved=True,
                    stroke_cap_round=True
                ),
                ft.LineChartData(
                    data_points=recv_data_points,
                    stroke_width=3,
                    color=ft.Colors.GREEN_600,
                    curved=True,
                    stroke_cap_round=True
                )
            ]
            network_chart.update()
            chart_state['last_network_sent_data'] = sent_data_points.copy()
            chart_state['last_network_recv_data'] = recv_data_points.copy()

        # Update Disk chart with real data
        disk_used = safe_float_conversion(system_metrics.get('disk_usage', 0.0))

        disk_free = 100 - disk_used

        # Only update if data has changed significantly
        disk_data_changed = (
            chart_state['last_disk_used'] is None or
            chart_state['last_disk_free'] is None or
            abs(chart_state['last_disk_used'] - disk_used) > 0.1 or
            abs(chart_state['last_disk_free'] - disk_free) > 0.1
        )

        if disk_data_changed:
            # Enhanced pie chart with dynamic colors - Fixed without gradients
            used_color = ft.Colors.RED_600 if disk_used > 80 else ft.Colors.ORANGE_600 if disk_used > 60 else ft.Colors.BLUE_600
            
            disk_chart.sections = [
                ft.PieChartSection(
                    value=disk_used,
                    color=used_color,
                    radius=85,
                    title=f"{disk_used:.1f}%\nUsed",
                    title_style=ft.TextStyle(color=ft.Colors.WHITE, size=14, weight=ft.FontWeight.BOLD),
                    border_side=ft.BorderSide(3, ft.Colors.WHITE)
                ),
                ft.PieChartSection(
                    value=disk_free,
                    color=ft.Colors.GREEN_500,
                    radius=75,
                    title=f"{disk_free:.1f}%\nFree",
                    title_style=ft.TextStyle(color=ft.Colors.WHITE, size=12, weight=ft.FontWeight.BOLD),
                    border_side=ft.BorderSide(2, ft.Colors.WHITE)
                )
            ]
            disk_chart.update()
            chart_state['last_disk_used'] = disk_used
            chart_state['last_disk_free'] = disk_free

    def update_system_info():
        """Update system information cards using direct control references."""
        cpu_cores_text.value = str(system_metrics.get('cpu_cores', 0))
        total_memory_text.value = f"{system_metrics.get('memory_total_gb', 0)} GB"
        disk_space_text.value = f"{system_metrics.get('disk_total_gb', 0)} GB"
        active_connections_text.value = str(system_metrics.get('active_connections', 0))

        # Update progress indicators with Material Design 3 styling
        cpu_usage = safe_float_conversion(system_metrics.get('cpu_usage', 0.0)) / 100.0
        memory_usage = safe_float_conversion(system_metrics.get('memory_usage', 0.0)) / 100.0
        disk_usage = safe_float_conversion(system_metrics.get('disk_usage', 0.0)) / 100.0
        network_sent = safe_float_conversion(system_metrics.get('network_sent_mb', 0))
        network_recv = safe_float_conversion(system_metrics.get('network_recv_mb', 0))
        network_load = min((network_sent + network_recv) / 10000.0, 1.0)  # Normalize network load
        
        # Update progress bars
        cpu_progress.content.controls[1].value = cpu_usage
        cpu_progress.content.controls[0].controls[1].value = f"{cpu_usage * 100:.1f}%"
        
        memory_progress.content.controls[1].value = memory_usage
        memory_progress.content.controls[0].controls[1].value = f"{memory_usage * 100:.1f}%"
        
        disk_progress.content.controls[1].value = disk_usage
        disk_progress.content.controls[0].controls[1].value = f"{disk_usage * 100:.1f}%"
        
        network_progress.content.controls[1].value = network_load
        network_progress.content.controls[0].controls[1].value = f"{network_load * 100:.1f}%"

        # Update status chips
        connection_status = system_metrics.get('connection_status', 'Unknown')
        server_status = system_metrics.get('server_status', 'Unknown')
        
        # Update chip text and colors based on status
        status_colors = {
            "Connected": ft.Colors.GREEN,
            "Disconnected": ft.Colors.RED,
            "Error": ft.Colors.RED,
            "Local": ft.Colors.BLUE,
            "Fallback": ft.Colors.GREY
        }
        connection_color = status_colors.get(connection_status, ft.Colors.GREY)
        connection_status_chip.bgcolor = connection_color
        connection_status_chip.content.controls[1].value = connection_status
        
        server_colors = {
            "Online": ft.Colors.GREEN,
            "Offline": ft.Colors.RED,
            "Error": ft.Colors.RED,
            "N/A": ft.Colors.GREY,
            "Unavailable": ft.Colors.GREY
        }
        server_color = server_colors.get(server_status, ft.Colors.GREY)
        server_status_chip.bgcolor = server_color
        server_status_chip.content.controls[1].value = server_status

        # Update all text controls
        cpu_cores_text.update()
        total_memory_text.update()
        disk_space_text.update()
        active_connections_text.update()
        
        # Update progress indicators
        cpu_progress.update()
        memory_progress.update()
        disk_progress.update()
        network_progress.update()
        
        # Update status chips
        connection_status_chip.update()
        server_status_chip.update()

    async def load_analytics_data():
        """Load analytics data using proper async pattern with server operations."""
        nonlocal system_metrics, is_loading, last_updated

        if is_loading:
            return
        is_loading = True

        # Show loading state immediately with Material Design 3 progress indicator
        last_updated_text.value = "Updating..."
        if hasattr(last_updated_text, 'page') and last_updated_text.page is not None:
            last_updated_text.update()

        try:
            # Use async data loading with server operations
            metrics = await get_system_metrics_async()

            # Update system metrics
            system_metrics = metrics

            # Update last updated timestamp
            last_updated = datetime.now()
            last_updated_text.value = f"Last updated: {last_updated.strftime('%H:%M:%S')}"

            # Update charts and UI only if controls are attached
            if hasattr(last_updated_text, 'page') and last_updated_text.page is not None:
                # Update charts and UI
                update_charts()
                update_system_info()

                # Update charts with error handling
                for chart_name, chart_obj in [
                    ("CPU", cpu_chart),
                    ("Memory", memory_chart),
                    ("Network", network_chart),
                    ("Disk", disk_chart)
                ]:
                    try:
                        chart_obj.update()
                    except Exception as chart_error:
                        logger.debug(f"{chart_name} chart update failed: {chart_error}")

                last_updated_text.update()

        except Exception as e:
            logger.error(f"Error loading analytics data: {e}")
            last_updated_text.value = "Error loading data"
            if hasattr(last_updated_text, 'page') and last_updated_text.page is not None:
                last_updated_text.update()
            show_error_message(page, f"Error loading analytics data: {e}")
        finally:
            is_loading = False

    def on_refresh_analytics(e):
        """Handle refresh button click."""
        logger.info("Analytics refresh requested")
        page.run_task(load_analytics_data)
        show_user_feedback(page, "Refreshing analytics data...")

    async def export_analytics_data():
        """Export analytics data with server integration."""
        try:
            if server_ops:
                # Use server operations for export
                result = await server_ops.action_operation(
                    action_name="export_analytics",
                    server_operation="export_analytics_data_async",
                    operation_data={"format": "csv", "metrics": system_metrics},
                    success_message="Analytics data exported successfully",
                    error_message="Failed to export analytics data"
                )

                if result.get('success'):
                    show_success_message(page, "Analytics exported to analytics_data.csv")
                else:
                    show_error_message(page, f"Export failed: {result.get('error', 'Unknown error')}")
            else:
                # Fallback to mock export
                import json
                import tempfile
                import os

                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(system_metrics, f, indent=2, default=str)
                    temp_path = f.name

                show_success_message(page, f"Mock analytics exported to {temp_path}")
                logger.info(f"Analytics data exported to {temp_path}")

        except Exception as e:
            logger.error(f"Export analytics failed: {e}")
            show_error_message(page, f"Export failed: {str(e)}")

    def on_export_analytics(e):
        """Handle export analytics button click."""
        page.run_task(export_analytics_data)

    def on_toggle_auto_refresh(e):
        """Toggle auto-refresh timer with proper cancellation."""
        nonlocal refresh_timer, timer_cancelled

        if refresh_timer:
            # Stop existing timer
            timer_cancelled = True  # Signal current loop to stop
            refresh_timer.cancel()
            refresh_timer = None
            logger.info("Auto-refresh stopped")
            show_user_feedback(page, "Auto-refresh stopped")
        else:
            # Reset cancellation flag and start new timer
            timer_cancelled = False
            
            # Start auto-refresh timer (every 5 seconds)
            async def refresh_loop():
                try:
                    while not timer_cancelled:  # Use explicit cancellation flag
                        await asyncio.sleep(5)
                        
                        # Double-check cancellation after sleep
                        if timer_cancelled:
                            break
                            
                        # Check if controls are still valid before updating
                        if (hasattr(last_updated_text, 'page') and
                            last_updated_text.page is not None and
                            not timer_cancelled):
                            page.run_task(load_analytics_data)
                        else:
                            # Controls are detached, stop automatically
                            logger.warning("Analytics controls detached, stopping auto-refresh")
                            break
                            
                except asyncio.CancelledError:
                    logger.info("Analytics refresh timer cancelled")
                except Exception as e:
                    logger.error(f"Analytics refresh timer error: {e}")
                    show_error_message(page, f"Analytics refresh timer error: {e}")
                    # Set timer_cancelled to True to stop the loop
                    timer_cancelled = True
                finally:
                    # Cleanup when loop exits
                    timer_cancelled = True

            refresh_timer = page.run_task(refresh_loop)
            logger.info("Auto-refresh started")
            show_user_feedback(page, "Auto-refresh started (every 5 seconds)")

    # Subscribe to state manager updates for real-time data
    if state_manager:
        def on_server_status_change(new_status, old_status):
            """Handle server status changes from state manager."""
            logger.debug(f"Server status changed: {old_status} -> {new_status}")
            # Trigger a refresh when server status changes
            page.run_task(load_analytics_data)
            
        # Subscribe to server status changes
        state_manager.subscribe("server_status", on_server_status_change)
        
        def on_system_metrics_change(new_metrics, old_metrics):
            """Handle system metrics changes from state manager."""
            logger.debug("System metrics updated")
            # Trigger a refresh when system metrics change
            page.run_task(load_analytics_data)
            
        # Subscribe to system metrics changes
        state_manager.subscribe("system_metrics", on_system_metrics_change)

    # Build the main view
    view = ft.Column([
        # Header with title and action buttons
        ft.Row([
            ft.Icon(ft.Icons.AUTO_GRAPH, size=24),
            ft.Text("Analytics & Performance", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.FILE_DOWNLOAD,
                    tooltip="Export Analytics Data",
                    on_click=on_export_analytics
                ),
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

        # Status indicators row
        ft.Row([
            ft.Text("Server Status", size=16, weight=ft.FontWeight.W_500),
            connection_status_chip,
            server_status_chip,
            ft.Container(expand=True),
            last_updated_text
        ], spacing=10, alignment=ft.MainAxisAlignment.START),
        ft.Divider(),

        # Last updated text
        ft.Row([
            ft.Text("System Performance Metrics", size=18, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
        ]),

        # Performance progress indicators
        ft.Column([
            cpu_progress,
            memory_progress,
            disk_progress,
            network_progress
        ], spacing=10),

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
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=20)

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
                    page.run_task(load_analytics_data)
                    return

                logger.debug(f"Attempt {attempt + 1}: Controls not attached, waiting {retry_delay}s")
                await asyncio.sleep(retry_delay)
                retry_delay *= 1.5  # Exponential backoff

            logger.warning("Failed to load analytics data: controls never attached after 5 attempts")

        page.run_task(delayed_load_with_retry)

    # Also provide a trigger for manual loading if needed
    def trigger_initial_load():
        """Trigger initial data load manually."""
        page.run_task(load_analytics_data)

    # Schedule initial load and export trigger function
    schedule_initial_load()
    view.trigger_initial_load = trigger_initial_load

    return view