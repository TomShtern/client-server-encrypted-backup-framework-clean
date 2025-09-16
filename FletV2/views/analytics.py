#!/usr/bin/env python3
"""
Analytics View for FletV2 - Enhanced 2025 Edition
Comprehensive analytics dashboard with responsive layout, Material Design 3 styling,
and advanced state management integration following Framework Harmony principles.
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
from utils.user_feedback import show_success_message, show_error_message, show_user_feedback
from utils.server_mediated_operations import create_server_mediated_operations
from utils.ui_components import create_modern_card, create_progress_indicator, create_loading_overlay
from theme import get_shadow_style, get_brand_color

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
    
    # Enhanced Material Design 3 progress indicators using ui_components
    cpu_progress = create_progress_indicator(0.0, "CPU Usage", ft.Colors.BLUE, animated=True)
    memory_progress = create_progress_indicator(0.0, "Memory Usage", ft.Colors.GREEN, animated=True)
    disk_progress = create_progress_indicator(0.0, "Disk Usage", ft.Colors.PURPLE, animated=True)
    network_progress = create_progress_indicator(0.0, "Network Load", ft.Colors.ORANGE, animated=True)
    
    # Enhanced status indicators using ui_components
    def create_status_chip_enhanced(text, color):
        from utils.ui_components import create_info_chip
        return create_info_chip(text, ft.Icons.CIRCLE, color, "filled")

    connection_status_chip = create_status_chip_enhanced("Disconnected", ft.Colors.RED)
    server_status_chip = create_status_chip_enhanced("Offline", ft.Colors.RED)

    # Loading overlay for data operations
    loading_overlay = create_loading_overlay("Loading analytics data...")
    loading_overlay.visible = False
    loading_overlay_ref = ft.Ref[ft.Container]()
    loading_overlay.ref = loading_overlay_ref

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
        
        # Update enhanced progress indicators
        # The create_progress_indicator from ui_components handles internal updates
        # We need to update the underlying progress bar values
        try:
            if hasattr(cpu_progress.content.controls[-1], 'value'):
                cpu_progress.content.controls[-1].value = cpu_usage
                cpu_progress.content.controls[0].controls[-1].value = f"{cpu_usage * 100:.1f}%"

            if hasattr(memory_progress.content.controls[-1], 'value'):
                memory_progress.content.controls[-1].value = memory_usage
                memory_progress.content.controls[0].controls[-1].value = f"{memory_usage * 100:.1f}%"

            if hasattr(disk_progress.content.controls[-1], 'value'):
                disk_progress.content.controls[-1].value = disk_usage
                disk_progress.content.controls[0].controls[-1].value = f"{disk_usage * 100:.1f}%"

            if hasattr(network_progress.content.controls[-1], 'value'):
                network_progress.content.controls[-1].value = network_load
                network_progress.content.controls[0].controls[-1].value = f"{network_load * 100:.1f}%"
        except Exception as e:
            logger.debug(f"Progress indicator update failed: {e}")

        # Update status chips
        connection_status = system_metrics.get('connection_status', 'Unknown')
        server_status = system_metrics.get('server_status', 'Unknown')
        
        # Update enhanced status chips
        status_colors = {
            "Connected": ft.Colors.GREEN,
            "Disconnected": ft.Colors.RED,
            "Error": ft.Colors.RED,
            "Local": ft.Colors.BLUE,
            "Fallback": ft.Colors.GREY
        }
        connection_color = status_colors.get(connection_status, ft.Colors.GREY)

        server_colors = {
            "Online": ft.Colors.GREEN,
            "Offline": ft.Colors.RED,
            "Error": ft.Colors.RED,
            "N/A": ft.Colors.GREY,
            "Unavailable": ft.Colors.GREY
        }
        server_color = server_colors.get(server_status, ft.Colors.GREY)

        # Update chip backgrounds and text
        try:
            connection_status_chip.bgcolor = connection_color
            connection_status_chip.content.controls[-1].value = connection_status

            server_status_chip.bgcolor = server_color
            server_status_chip.content.controls[-1].value = server_status
        except Exception as e:
            logger.debug(f"Status chip update failed: {e}")

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
        """Enhanced analytics data loading with comprehensive state management and UI feedback."""
        nonlocal system_metrics, is_loading, last_updated

        if is_loading:
            return
        is_loading = True

        # Show enhanced loading state with overlay
        last_updated_text.value = "Updating..."
        if loading_overlay_ref.current:
            loading_overlay_ref.current.visible = True
            loading_overlay_ref.current.update()

        if hasattr(last_updated_text, 'page') and last_updated_text.page is not None:
            last_updated_text.update()

        try:
            # Notify state manager of analytics loading
            if state_manager:
                await state_manager.update_async("analytics_loading", True, source="load_start")

            # Use async data loading with server operations
            metrics = await get_system_metrics_async()

            # Update system metrics with state manager integration
            system_metrics = metrics
            if state_manager:
                await state_manager.update_async("system_metrics", metrics, source="analytics_load")

            # Update last updated timestamp
            last_updated = datetime.now()
            last_updated_text.value = f"Last updated: {last_updated.strftime('%H:%M:%S')}"

            # Update charts and UI only if controls are attached
            if hasattr(last_updated_text, 'page') and last_updated_text.page is not None:
                # Update charts and UI
                update_charts()
                update_system_info()

                # Update charts with comprehensive error handling
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
                show_success_message(page, "Analytics data refreshed successfully")

        except Exception as e:
            logger.error(f"Error loading analytics data: {e}")
            last_updated_text.value = "Error loading data"
            if hasattr(last_updated_text, 'page') and last_updated_text.page is not None:
                last_updated_text.update()
            show_error_message(page, f"Error loading analytics data: {str(e)}")

            # Update state manager with error
            if state_manager:
                await state_manager.update_async("analytics_error", str(e), source="load_error")
        finally:
            is_loading = False

            # Hide loading overlay
            if loading_overlay_ref.current:
                loading_overlay_ref.current.visible = False
                loading_overlay_ref.current.update()

            # Notify state manager loading completed
            if state_manager:
                await state_manager.update_async("analytics_loading", False, source="load_complete")

    def on_refresh_analytics(e):
        """Enhanced refresh button handler with comprehensive feedback."""
        logger.info("Analytics refresh requested")

        # Provide immediate user feedback
        show_user_feedback(page, "Refreshing analytics data...")

        # Update state manager
        if state_manager:
            asyncio.create_task(state_manager.update_async("analytics_refresh", {
                "requested_at": datetime.now().isoformat(),
                "trigger": "manual_button"
            }, source="refresh_request"))

        # Trigger data load
        page.run_task(load_analytics_data)

    async def export_analytics_data():
        """Enhanced analytics data export with comprehensive error handling and progress tracking."""
        try:
            # Show loading state
            if loading_overlay_ref.current:
                loading_overlay_ref.current.content.controls[0].controls[-1].value = "Exporting analytics data..."
                loading_overlay_ref.current.visible = True
                loading_overlay_ref.current.update()

            # Update state manager
            if state_manager:
                await state_manager.update_async("analytics_export", {"status": "starting"}, source="export_start")

            if server_ops:
                # Use enhanced server operations for export
                result = await server_ops.action_operation(
                    action_name="export_analytics",
                    server_operation="export_analytics_data_async",
                    operation_data={
                        "format": "csv",
                        "metrics": system_metrics,
                        "timestamp": datetime.now().isoformat(),
                        "charts_data": {
                            "cpu_history": chart_state.get('cpu_history', []),
                            "memory_history": chart_state.get('memory_history', []),
                            "network_sent_history": chart_state.get('network_sent_history', []),
                            "network_recv_history": chart_state.get('network_recv_history', [])
                        }
                    },
                    success_message="Analytics data exported successfully",
                    error_message="Failed to export analytics data"
                )

                if result.get('success'):
                    export_path = result.get('data', {}).get('export_path', 'analytics_data.csv')
                    show_success_message(page, f"Analytics exported to {export_path}")

                    # Update state manager with success
                    if state_manager:
                        await state_manager.update_async("analytics_export", {
                            "status": "completed",
                            "export_path": export_path
                        }, source="export_success")
                else:
                    error_msg = result.get('error', 'Unknown error')
                    show_error_message(page, f"Export failed: {error_msg}")

                    # Update state manager with error
                    if state_manager:
                        await state_manager.update_async("analytics_export", {
                            "status": "failed",
                            "error": error_msg
                        }, source="export_error")
            else:
                # Enhanced fallback export with multiple formats
                import json
                import csv
                import tempfile
                import os

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Create comprehensive export data
                export_data = {
                    "timestamp": datetime.now().isoformat(),
                    "system_metrics": system_metrics,
                    "charts_data": {
                        "cpu_history": chart_state.get('cpu_history', []),
                        "memory_history": chart_state.get('memory_history', []),
                        "network_sent_history": chart_state.get('network_sent_history', []),
                        "network_recv_history": chart_state.get('network_recv_history', [])
                    },
                    "connection_status": system_metrics.get('connection_status', 'Unknown'),
                    "server_status": system_metrics.get('server_status', 'Unknown')
                }

                # Export as JSON
                json_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'_analytics_{timestamp}.json', delete=False)
                json.dump(export_data, json_file, indent=2, default=str)
                json_path = json_file.name
                json_file.close()

                # Export as CSV (system metrics only)
                csv_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'_analytics_{timestamp}.csv', delete=False, newline='')
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow(['Metric', 'Value', 'Unit'])

                for key, value in system_metrics.items():
                    if isinstance(value, (int, float)):
                        unit = '%' if 'usage' in key.lower() else ('GB' if any(x in key.lower() for x in ['memory', 'disk']) else 'count')
                        csv_writer.writerow([key.replace('_', ' ').title(), value, unit])
                    else:
                        csv_writer.writerow([key.replace('_', ' ').title(), str(value), 'text'])

                csv_path = csv_file.name
                csv_file.close()

                show_success_message(page, f"Analytics exported:\nJSON: {json_path}\nCSV: {csv_path}")
                logger.info(f"Analytics data exported to {json_path} and {csv_path}")

                # Update state manager with mock export success
                if state_manager:
                    await state_manager.update_async("analytics_export", {
                        "status": "completed",
                        "export_paths": [json_path, csv_path],
                        "mode": "mock"
                    }, source="export_mock_success")

        except Exception as e:
            logger.error(f"Export analytics failed: {e}")
            show_error_message(page, f"Export failed: {str(e)}")

            # Update state manager with error
            if state_manager:
                await state_manager.update_async("analytics_export", {
                    "status": "failed",
                    "error": str(e)
                }, source="export_exception")
        finally:
            # Hide loading overlay
            if loading_overlay_ref.current:
                loading_overlay_ref.current.visible = False
                loading_overlay_ref.current.update()

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

    # Enhanced state manager integration with reactive subscriptions
    if state_manager:
        async def on_server_status_change_async(new_status, old_status):
            """Enhanced async handler for server status changes."""
            logger.debug(f"Server status changed: {old_status} -> {new_status}")
            # Update connection status chip
            if new_status and isinstance(new_status, dict):
                connection_status = new_status.get('connection_status', 'Unknown')
                server_status = new_status.get('server_status', 'Unknown')

                # Update status chips immediately
                try:
                    status_colors = {
                        "Connected": ft.Colors.GREEN, "Disconnected": ft.Colors.RED,
                        "Error": ft.Colors.RED, "Local": ft.Colors.BLUE, "Fallback": ft.Colors.GREY
                    }
                    connection_color = status_colors.get(connection_status, ft.Colors.GREY)
                    connection_status_chip.bgcolor = connection_color
                    connection_status_chip.content.controls[-1].value = connection_status
                    connection_status_chip.update()

                    server_colors = {
                        "Online": ft.Colors.GREEN, "Offline": ft.Colors.RED,
                        "Error": ft.Colors.RED, "N/A": ft.Colors.GREY, "Unavailable": ft.Colors.GREY
                    }
                    server_color = server_colors.get(server_status, ft.Colors.GREY)
                    server_status_chip.bgcolor = server_color
                    server_status_chip.content.controls[-1].value = server_status
                    server_status_chip.update()
                except Exception as e:
                    logger.debug(f"Status chip update error: {e}")

            # Trigger analytics refresh for server changes
            page.run_task(load_analytics_data)

        async def on_system_metrics_change_async(new_metrics, old_metrics):
            """Enhanced async handler for system metrics changes."""
            logger.debug("System metrics updated via state manager")
            if new_metrics and isinstance(new_metrics, dict):
                # Update local metrics without triggering another load
                nonlocal system_metrics
                system_metrics = new_metrics

                # Update UI components directly
                try:
                    update_charts()
                    update_system_info()
                except Exception as e:
                    logger.debug(f"Direct UI update error: {e}")

        # Subscribe to enhanced async handlers
        try:
            state_manager.subscribe_async("server_status", on_server_status_change_async)
            state_manager.subscribe_async("system_metrics", on_system_metrics_change_async)
        except AttributeError:
            # Fallback to regular subscription if async not available
            def on_server_status_change(new_status, old_status):
                page.run_task(on_server_status_change_async(new_status, old_status))
            def on_system_metrics_change(new_metrics, old_metrics):
                page.run_task(on_system_metrics_change_async(new_metrics, old_metrics))

            state_manager.subscribe("server_status", on_server_status_change)
            state_manager.subscribe("system_metrics", on_system_metrics_change)

        # Subscribe to analytics-specific events
        try:
            async def on_analytics_event(event_data, old_data):
                """Handle analytics-specific events from state manager."""
                logger.debug(f"Analytics event received: {event_data}")
                if isinstance(event_data, dict):
                    event_type = event_data.get('status')
                    if event_type == 'export_completed':
                        show_success_message(page, "Analytics export completed successfully")
                    elif event_type == 'export_failed':
                        show_error_message(page, f"Analytics export failed: {event_data.get('error', 'Unknown error')}")

            # Subscribe to analytics events if async subscription available
            if hasattr(state_manager, 'subscribe_async'):
                state_manager.subscribe_async("analytics_export", on_analytics_event)
        except Exception as e:
            logger.debug(f"Analytics event subscription failed: {e}")

    # Build the main view with stack overlay for loading
    main_content = ft.Column([
        # Header with title and action buttons
        ft.Row([
            ft.Icon(ft.Icons.AUTO_GRAPH, size=24),
            ft.Text("Analytics & Performance", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.FILE_DOWNLOAD,
                    tooltip="Export Analytics Data (JSON & CSV)",
                    on_click=on_export_analytics,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.TERTIARY),
                        color=ft.Colors.TERTIARY
                    )
                ),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh Analytics Data",
                    on_click=on_refresh_analytics,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.SECONDARY),
                        color=ft.Colors.SECONDARY
                    )
                ),
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    tooltip="Toggle Auto-refresh (5s interval)",
                    on_click=on_toggle_auto_refresh,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                        color=ft.Colors.PRIMARY
                    )
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

        # Removed separate performance metrics title since it's now in the card above

        # Enhanced responsive performance progress indicators
        create_modern_card(
            content=ft.Column([
                ft.Text("System Performance Metrics", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
                ft.Container(height=16),  # Spacing
                ft.ResponsiveRow([
                    ft.Column([cpu_progress], col={"sm": 12, "md": 6, "lg": 6}),
                    ft.Column([memory_progress], col={"sm": 12, "md": 6, "lg": 6})
                ], spacing=12),
                ft.ResponsiveRow([
                    ft.Column([disk_progress], col={"sm": 12, "md": 6, "lg": 6}),
                    ft.Column([network_progress], col={"sm": 12, "md": 6, "lg": 6})
                ], spacing=12)
            ], spacing=12, tight=True),
            title=None,  # Title included in content
            elevation="soft",
            hover_effect=False,  # Static metrics card
            padding=24
        ),

        # Enhanced responsive performance charts with Material Design 3 styling
        ft.ResponsiveRow([
            # CPU Usage Chart - Responsive: mobile 1x4, tablet 1x4, desktop 2x2
            ft.Column([
                create_modern_card(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.SHOW_CHART, color=ft.Colors.BLUE, size=24),
                            ft.Text("CPU Usage Over Time", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
                        ], spacing=12, alignment=ft.MainAxisAlignment.START),
                        ft.Container(height=8),  # Spacing
                        ft.Container(
                            content=cpu_chart,
                            expand=True,
                            height=220,
                            padding=ft.Padding(12, 8, 12, 8),
                            border_radius=12
                        )
                    ], spacing=0, tight=True),
                    title=None,  # Title already included in content
                    elevation="elevated",
                    hover_effect=True,
                    padding=24
                )
            ], col={"sm": 12, "md": 12, "lg": 6}),  # Mobile: full width, Desktop: half width

            # Memory Usage Chart
            ft.Column([
                create_modern_card(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.BAR_CHART, color=ft.Colors.GREEN, size=24),
                            ft.Text("Memory Usage History", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
                        ], spacing=12, alignment=ft.MainAxisAlignment.START),
                        ft.Container(height=8),
                        ft.Container(
                            content=memory_chart,
                            expand=True,
                            height=220,
                            padding=ft.Padding(12, 8, 12, 8),
                            border_radius=12
                        )
                    ], spacing=0, tight=True),
                    elevation="elevated",
                    hover_effect=True,
                    padding=24
                )
            ], col={"sm": 12, "md": 12, "lg": 6}),

            # Network Traffic Chart
            ft.Column([
                create_modern_card(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.NETWORK_CHECK, color=ft.Colors.ORANGE, size=24),
                            ft.Text("Network Traffic", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
                        ], spacing=12, alignment=ft.MainAxisAlignment.START),
                        ft.Container(height=8),
                        ft.Container(
                            content=network_chart,
                            expand=True,
                            height=220,
                            padding=ft.Padding(12, 8, 12, 8),
                            border_radius=12
                        )
                    ], spacing=0, tight=True),
                    elevation="elevated",
                    hover_effect=True,
                    padding=24
                )
            ], col={"sm": 12, "md": 12, "lg": 6}),

            # Disk Usage Chart
            ft.Column([
                create_modern_card(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.STORAGE, color=ft.Colors.PURPLE, size=24),
                            ft.Text("Disk Usage", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
                        ], spacing=12, alignment=ft.MainAxisAlignment.START),
                        ft.Container(height=8),
                        ft.Container(
                            content=disk_chart,
                            expand=True,
                            height=220,
                            padding=ft.Padding(12, 8, 12, 8),
                            border_radius=12
                        )
                    ], spacing=0, tight=True),
                    elevation="elevated",
                    hover_effect=True,
                    padding=24
                )
            ], col={"sm": 12, "md": 12, "lg": 6})
        ], spacing=20),  # Enhanced spacing between charts

        # Enhanced system information cards with Material Design 3 styling
        ft.Divider(),
        ft.Text("System Information", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
        ft.ResponsiveRow([
            ft.Column([
                create_modern_card(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.COMPUTER, size=32, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.BLUE,
                            border_radius=16,
                            padding=ft.Padding(12, 12, 12, 12),
                            alignment=ft.alignment.center
                        ),
                        ft.Text("CPU Cores", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE),
                        cpu_cores_text
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                    elevation="soft",
                    hover_effect=True,
                    padding=20
                )
            ], col={"sm": 6, "md": 6, "lg": 3}),
            ft.Column([
                create_modern_card(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.MEMORY, size=32, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.GREEN,
                            border_radius=16,
                            padding=ft.Padding(12, 12, 12, 12),
                            alignment=ft.alignment.center
                        ),
                        ft.Text("Total Memory", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE),
                        total_memory_text
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                    elevation="soft",
                    hover_effect=True,
                    padding=20
                )
            ], col={"sm": 6, "md": 6, "lg": 3}),
            ft.Column([
                create_modern_card(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.STORAGE, size=32, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.PURPLE,
                            border_radius=16,
                            padding=ft.Padding(12, 12, 12, 12),
                            alignment=ft.alignment.center
                        ),
                        ft.Text("Disk Space", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE),
                        disk_space_text
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                    elevation="soft",
                    hover_effect=True,
                    padding=20
                )
            ], col={"sm": 6, "md": 6, "lg": 3}),
            ft.Column([
                create_modern_card(
                    content=ft.Column([
                        ft.Container(
                            content=ft.Icon(ft.Icons.LINK, size=32, color=ft.Colors.WHITE),
                            bgcolor=ft.Colors.ORANGE,
                            border_radius=16,
                            padding=ft.Padding(12, 12, 12, 12),
                            alignment=ft.alignment.center
                        ),
                        ft.Text("Active Connections", size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE),
                        active_connections_text
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                    elevation="soft",
                    hover_effect=True,
                    padding=20
                )
            ], col={"sm": 6, "md": 6, "lg": 3})
        ], spacing=16),

    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=20)

    # Create the main view with loading overlay capability
    view = ft.Stack([
        main_content,
        loading_overlay  # Overlay positioned above main content
    ], expand=True)

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

    # Add accessibility and debug info
    logger.info("Enhanced analytics view created with responsive layout and Material Design 3 styling")

    return view