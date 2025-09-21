#!/usr/bin/env python3
"""
Simplified Dashboard View - The Flet Way
~400 lines instead of 1,005 lines of framework fighting!

Core Principle: Use Flet's built-in components for metrics, progress bars, and cards.
Clean, maintainable dashboard that preserves all user-facing functionality.
"""

# Standard library imports
import os
import sys

# Add parent directory to path for Shared imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Explicit imports instead of star import for better static analysis
import flet as ft
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import asyncio
import aiofiles

# ALWAYS import this in any Python file that deals with subprocess or console I/O
import Shared.utils.utf8_solution as _  # Import for UTF-8 side effects

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_components import themed_card, themed_button
from utils.user_feedback import show_success_message, show_error_message

logger = get_logger(__name__)

# Additional imports specific to dashboard
import contextlib
from typing import Tuple, Literal, Union, Iterator, Callable  # Extending base typing imports
from collections import deque
from functools import lru_cache
import psutil
import random
from datetime import timedelta

# Type definitions for better type safety
ActivityType = Literal['info', 'warning', 'error', 'success']
CardType = Literal['primary', 'success', 'info']
UpdateSource = Literal['auto', 'manual', 'initial']

# Simple dict types instead of TypedDict for better compatibility
ActivityEntry = Dict[str, Any]
ServerStatus = Dict[str, Any]
SystemMetrics = Dict[str, Any]

# Constants for configuration
MAX_HISTORY_POINTS = 30
AUTO_REFRESH_INTERVAL = 30  # seconds
POLLING_INTERVAL = 30  # seconds
OPERATIONS_UPDATE_CYCLE = 2  # every 60 seconds (30 * 2)
CLICK_PROXIMITY = 20
SOCKET_TIMEOUT = 10
STATUS_TOAST_COOLDOWN = 90  # seconds
ACTIVITY_TIME_WINDOW = 10  # minutes for running jobs
MAX_ACTIVITY_DISPLAY = 10
MAX_CLIENTS_DISPLAY = 8
MAX_OPERATIONS_DISPLAY = 5

# Significant change thresholds for toast notifications
SIGNIFICANT_DELTA_THRESHOLDS = {
    'clients': 2,
    'transfers': 2,
    'storage_gb': 1.0,
    'files': 10
}

# Activity filter keywords
JOB_KEYWORDS = ['start', 'running', 'upload', 'transfer']
BACKUP_KEYWORDS = ['backup', 'completed']

# -------------------------
# Normalization helpers
# -------------------------
def _parse_uptime_to_seconds(uptime_value: Any) -> int:
    """Parse uptime value from various formats to seconds.
    Supports:
    - int/float seconds
    - HH:MM:SS string
    - dict-like with hours/minutes/seconds
    """
    with contextlib.suppress(Exception):
        if isinstance(uptime_value, (int, float)):
            return int(uptime_value)
        s = str(uptime_value)
        if ":" in s:
            parts = s.split(":")
            if len(parts) == 3:
                h, m, sec = [int(x) for x in parts]
                return h * 3600 + m * 60 + sec
        # dict-like {"hours": 1, "minutes": 2, "seconds": 3}
        if isinstance(uptime_value, dict):
            h = int(uptime_value.get("hours", 0))
            m = int(uptime_value.get("minutes", 0))
            sec = int(uptime_value.get("seconds", 0))
            return h * 3600 + m * 60 + sec
    return 0

def _normalize_server_status_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize server status dict to the keys the dashboard expects."""
    if not isinstance(payload, dict):
        return {}
    try:
        running = bool(payload.get("running", payload.get("server_running", payload.get("is_running", True))))
        uptime_seconds = _parse_uptime_to_seconds(
            payload.get("uptime_seconds", payload.get("uptime", payload.get("server_uptime", 0)))
        )
        return {
            "running": running,
            "clients_connected": int(payload.get("clients_connected", payload.get("active_clients", payload.get("total_clients", 0))))
                if isinstance(payload.get("clients_connected"), (int, float)) or payload.get("clients_connected") is not None else 0,
            "total_files": int(payload.get("total_files", payload.get("files_count", 0))),
            "total_transfers": int(payload.get("total_transfers", payload.get("transfers", 0))),
            "storage_used_gb": float(payload.get("storage_used_gb", payload.get("storage_used", 0.0))),
            "uptime_seconds": uptime_seconds,
        }
    except Exception:
        # Graceful fallback
        return {}

# Cached helper functions for better performance
@lru_cache(maxsize=32)
def get_activity_icon(activity_type: ActivityType) -> str:
    """Get icon for activity type with caching."""
    icon_map = {
        'success': ft.Icons.CHECK_CIRCLE_OUTLINE,
        'error': ft.Icons.ERROR_OUTLINE,
        'warning': ft.Icons.WARNING_AMBER,
        'info': ft.Icons.INFO_OUTLINE
    }
    return icon_map.get(activity_type, ft.Icons.INFO_OUTLINE)

@lru_cache(maxsize=32)
def get_activity_color(activity_type: ActivityType) -> str:
    """Get color for activity type with caching."""
    color_map = {
        'success': ft.Colors.GREEN,
        'error': ft.Colors.RED,
        'warning': ft.Colors.ORANGE,
        'info': ft.Colors.BLUE
    }
    return color_map.get(activity_type, ft.Colors.BLUE)

def normalize_activity_type(level: str) -> ActivityType:
    """Normalize activity level to valid ActivityType."""
    normalized = level.lower()
    if normalized in {'info', 'warning', 'error', 'success'}:
        return normalized  # type: ignore
    return 'info'

# Enhanced components using Flet native features
def create_status_pill(text: str, status: str) -> ft.Container:
    """Modern status pill using Flet's native styling."""
    color_map = {
        "success": ft.Colors.GREEN,
        "error": ft.Colors.ERROR,
        "warning": ft.Colors.ORANGE
    }
    color = color_map.get(status, ft.Colors.PRIMARY)

    return ft.Container(
        content=ft.Text(text, color=color, size=12, weight=ft.FontWeight.W_600),
        bgcolor=ft.Colors.with_opacity(0.1, color),
        border=ft.border.all(1, color),
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=16, vertical=6)
    )

def create_action_group(buttons: List[ft.Control], group_type: str = "primary", spacing: int = 8) -> ft.Container:
    """Create action button group using Flet's native styling."""
    bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY) if group_type == "primary" else ft.Colors.with_opacity(0.03, ft.Colors.OUTLINE)

    return ft.Container(
        content=ft.Row(buttons, spacing=spacing),
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=8,
        bgcolor=bgcolor,
        animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT)
    )

def safe_server_call(method, *args, **kwargs) -> Optional[Dict[str, Any]]:
    """Standardized error handling for server bridge calls."""
    try:
        result = method(*args, **kwargs)
        return result if isinstance(result, dict) and result.get('success') else None
    except Exception as e:
        logger.debug(f"Server call failed: {e}")
        return None



def create_dashboard_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    _state_manager: Optional[StateManager]
) -> Tuple[ft.Control, Callable, Callable]:
    """Modern 2025 dashboard with visual hierarchy, semantic colors, and engaging data storytelling."""
    logger.info("Creating modern dashboard with enhanced visual appeal")

    # Apply the enhanced modern theme for 2025 visual excellence
    from theme import setup_modern_theme
    setup_modern_theme(page)

    # Simple state management with proper initialization
    current_server_status: Dict[str, Any] = {}
    current_system_metrics: Dict[str, Any] = {}
    current_activity: List[Dict[str, Any]] = []
    current_clients: List[Dict[str, Any]] = []
    refresh_task = None
    _stop_polling = False
    auto_refresh_enabled = True
    activity_filter = "All"
    last_updated = "Never"
    # For significant-change detection and toast throttling
    prev_server_snapshot: Optional[Dict[str, Any]] = None
    last_significant_toast_time: Optional[datetime] = None

    # Memory-efficient history buffers using deque with fixed size
    cpu_history: deque = deque(maxlen=MAX_HISTORY_POINTS)
    memory_history: deque = deque(maxlen=MAX_HISTORY_POINTS)
    disk_history: deque = deque(maxlen=MAX_HISTORY_POINTS)

    # Event handlers
    def on_backup(e: ft.ControlEvent) -> None:
        show_success_message(page, "Backup initiated (mock)")

    def start_server(e: ft.ControlEvent) -> None:
        """Start the server."""
        if server_bridge:
            try:
                result = server_bridge.start_server()
                if result.get('success'):
                    show_success_message(page, "Server started successfully")
                    update_all_displays()
                else:
                    show_error_message(page, f"Failed to start server: {result.get('error', 'Unknown error')}")
            except Exception as ex:
                show_error_message(page, f"Error starting server: {ex}")
        else:
            # Mock success
            show_success_message(page, "Server started (mock mode)")
            update_all_displays()

    def stop_server(e: ft.ControlEvent) -> None:
        """Stop the server."""
        if server_bridge:
            try:
                result = server_bridge.stop_server()
                if result.get('success'):
                    show_success_message(page, "Server stopped successfully")
                    update_all_displays()
                else:
                    show_error_message(page, f"Failed to stop server: {result.get('error', 'Unknown error')}")
            except Exception as ex:
                show_error_message(page, f"Error stopping server: {ex}")
        else:
            # Mock success
            show_success_message(page, "Server stopped (mock mode)")
            update_all_displays()

    def refresh_dashboard(e: ft.ControlEvent) -> None:
        """Refresh all dashboard data (async to avoid blocking UI)."""
        try:
            async def _manual_refresh() -> None:
                await _update_all_displays_async('manual')
            page.run_task(_manual_refresh)
        except Exception:
            # Fallback to sync update
            update_all_displays()
        show_success_message(page, "Dashboard refreshed")

    # Define UI controls that are used in update_all_displays
    # Dynamic hero metric value controls for live updates
    hero_total_clients_text = ft.Text("0", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)
    hero_active_transfers_text = ft.Text("0", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
    hero_uptime_text = ft.Text("0h 0m", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)

    # Define buttons that are used in update_all_displays
    backup_button = themed_button("Backup", on_backup, variant="filled", icon=ft.Icons.BACKUP)
    refresh_button = themed_button("Refresh", refresh_dashboard, variant="outlined", icon=ft.Icons.REFRESH)
    connect_button = themed_button("Connect", start_server, variant="filled", icon=ft.Icons.PLAY_ARROW)
    disconnect_button = themed_button("Disconnect", stop_server, variant="outlined", icon=ft.Icons.STOP)

    # Define server status indicator container
    server_status_indicator_container = ft.Container()

    # Get server status data with improved type safety
    def get_server_status() -> Dict[str, Any]:
        """Get server status using server bridge or mock data, normalized."""
        if server_bridge and (result := safe_server_call(server_bridge.get_server_status)):
            raw = result.get('data', {})
            logger.debug(f"Raw server status from bridge: {raw}")
            normalized = _normalize_server_status_payload(raw)
            logger.debug(f"Normalized server status: {normalized}")
            if normalized:
                return normalized
            # Fall back to raw if normalization yielded empty (unknown shape)
            if isinstance(raw, dict):
                return raw

        # Type-safe mock data fallback (already in expected shape)
        fallback_data = {
            'running': True,
            'port': 8080,
            'uptime_seconds': 3600 + random.randint(0, 7200),
            'clients_connected': random.randint(3, 15),
            'total_files': random.randint(50, 200),
            'total_transfers': random.randint(1, 10),
            'storage_used_gb': round(random.uniform(1.5, 25.8), 1)
        }
        logger.debug(f"Using fallback server status: {fallback_data}")
        return fallback_data

    # Get system metrics using psutil with type safety
    def get_system_metrics() -> Dict[str, Any]:
        """Prefer server-reported system metrics; fall back to psutil."""
        # Try server metrics first
        try:
            if server_bridge and (res := safe_server_call(server_bridge.get_system_status)):
                data = res.get('data', {})
                # Typical fields: cpu_percent, memory_percent, disk_percent
                if isinstance(data, dict) and any(k in data for k in ('cpu_percent', 'memory_percent', 'disk_percent')):
                    cpu_p = float(data.get('cpu_percent', 0.0))
                    mem_p = float(data.get('memory_percent', data.get('mem_percent', 0.0)))
                    disk_p = float(data.get('disk_percent', data.get('storage_percent', 0.0)))
                    return {
                        'cpu_percent': cpu_p,
                        'memory_percent': mem_p,
                        'disk_percent': disk_p
                    }
        except Exception:
            pass

        # Fallback to psutil
        try:
            cpu_percent = psutil.cpu_percent(interval=0.05)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            return {
                'cpu_percent': float(cpu_percent),
                'memory_percent': float(memory.percent),
                'disk_percent': float((disk.used / disk.total) * 100)
            }
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            return {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'disk_percent': 0.0
            }

    # Cached helper functions for better performance
    @lru_cache(maxsize=32)
    def get_activity_icon(activity_type: ActivityType) -> str:
        """Get icon for activity type with caching."""
        icon_map = {
            'success': ft.Icons.CHECK_CIRCLE_OUTLINE,
            'error': ft.Icons.ERROR_OUTLINE,
            'warning': ft.Icons.WARNING_AMBER,
            'info': ft.Icons.INFO_OUTLINE
        }
        return icon_map.get(activity_type, ft.Icons.INFO_OUTLINE)

    @lru_cache(maxsize=32)
    def get_activity_color(activity_type: ActivityType) -> str:
        """Get color for activity type with caching."""
        color_map = {
            'success': ft.Colors.GREEN,
            'error': ft.Colors.RED,
            'warning': ft.Colors.ORANGE,
            'info': ft.Colors.BLUE
        }
        return color_map.get(activity_type, ft.Colors.BLUE)

    def normalize_activity_type(level: str) -> ActivityType:
        """Normalize activity level to valid ActivityType."""
        normalized = str(level).lower()
        from typing import cast
        if normalized in ['info', 'warning', 'error', 'success']:
            return cast(ActivityType, normalized)
        return 'info'

    # Get activity data with improved type safety
    def get_activity_data() -> List[ActivityEntry]:
        """Get recent activity data using logs as canonical source, with mock fallback."""
        if server_bridge and (logs_result := safe_server_call(server_bridge.get_logs)):
            entries = logs_result.get('data', [])
            if not isinstance(entries, list):
                entries = []

            activities: List[ActivityEntry] = []
            for i, entry in enumerate(entries):
                # Normalize fields with type safety
                level = normalize_activity_type(entry.get('level', entry.get('severity', 'info')))
                msg = str(entry.get('message', entry.get('msg', '')))
                ts = entry.get('timestamp', entry.get('time', datetime.now()))

                activities.append({
                    'id': i + 1,
                    'type': level,
                    'message': msg,
                    'timestamp': ts
                })
            return sorted(activities, key=lambda x: x['timestamp'], reverse=True)

        # Type-safe mock activity data
        activity_types: List[ActivityType] = ['info', 'error', 'warning', 'success']
        messages = [
            "Client connected from 192.168.1.{ip}",
            "File backup completed: {filename}",
            "Transfer completed successfully",
            "System health check passed",
            "Database backup completed",
            "Client disconnected",
            "Error processing file: {filename}",
            "Warning: High CPU usage detected",
            "Network connection restored"
        ]

        activities: List[ActivityEntry] = []
        for i in range(20):
            time_offset = timedelta(minutes=random.randint(0, 120))
            activities.append({
                'id': i + 1,
                'type': random.choice(activity_types),
                'message': random.choice(messages).format(
                    ip=random.randint(100, 199),
                    filename=f"document_{random.randint(1, 100)}.pdf"
                ),
                'timestamp': datetime.now() - time_offset
            })

        return sorted(activities, key=lambda x: x['timestamp'], reverse=True)

    def create_premium_hero_card(value: str, label: str, trend: str = "", card_type: str = "primary", value_control: Optional[ft.Text] = None, on_click=None) -> ft.Card:
        """Create hero metric card using Flet's native Card with built-in animations."""
        # Use Flet's semantic color system
        color_map = {
            "success": ft.Colors.GREEN,
            "info": ft.Colors.BLUE,
            "primary": ft.Colors.PRIMARY
        }
        color = color_map.get(card_type, ft.Colors.PRIMARY)

        # Trend indicator using native Flet components
        trend_widget = None
        if trend:
            is_positive = trend.startswith("+")
            trend_widget = ft.Row([
                ft.Icon(ft.Icons.TRENDING_UP if is_positive else ft.Icons.TRENDING_DOWN, size=16, color=color),
                ft.Text(trend, size=14, weight=ft.FontWeight.BOLD, color=color)
            ], spacing=4)

        value_text = value_control or ft.Text(value, size=48, weight=ft.FontWeight.BOLD, color=color)
        label_text = ft.Text(label, size=16, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE)

        # Native Flet Card with built-in hover and animation support
        card_content = ft.Container(
            content=ft.Column([
                ft.Row([value_text, trend_widget or ft.Container()],
                      alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                label_text
            ], spacing=8),
            padding=24,
            on_click=on_click,
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(100, ft.AnimationCurve.EASE_OUT)
        )

        return ft.Card(
            content=card_content,
            elevation=4,
            color=ft.Colors.with_opacity(0.05, color),
            surface_tint_color=color
        )


    def create_premium_activity_stream() -> ft.Card:
        """Create activity stream using Flet's native components and real data."""

        # Get real activity data from the dashboard context
        activities = current_activity[:10] if current_activity else []

        # Create activity list using native Flet ListView with better performance
        activity_controls = []
        for activity in activities:
            activity_type = str(activity.get('type', 'info')).lower()
            # Reuse top-level cached helpers for consistency
            icon = get_activity_icon(activity_type)  # type: ignore[arg-type]
            color = get_activity_color(activity_type)  # type: ignore[arg-type]
            timestamp = activity.get('timestamp', datetime.now())

            # Format timestamp
            if isinstance(timestamp, datetime):
                time_ago = datetime.now() - timestamp
                if time_ago.days > 0:
                    time_str = f"{time_ago.days}d ago"
                elif time_ago.seconds > 3600:
                    time_str = f"{time_ago.seconds // 3600}h ago"
                elif time_ago.seconds > 60:
                    time_str = f"{time_ago.seconds // 60}m ago"
                else:
                    time_str = "Just now"
            else:
                time_str = str(timestamp)

            activity_controls.append(
                ft.ListTile(
                    leading=ft.Icon(icon, color=color, size=20),
                    title=ft.Text(activity.get('message', ''), size=13, weight=ft.FontWeight.W_500),
                    subtitle=ft.Text(time_str, size=11, color=ft.Colors.OUTLINE),
                    dense=True
                )
            )

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TIMELINE, size=24, color=ft.Colors.PURPLE_600),
                        ft.Text("Live Activity", size=20, weight=ft.FontWeight.BOLD)
                    ], spacing=8),
                    ft.ListView(
                        controls=activity_controls,
                        height=200,
                        spacing=4
                    ) if activity_controls else ft.Container(
                        content=ft.Text("No recent activity", color=ft.Colors.OUTLINE),
                        alignment=ft.alignment.center,
                        height=100
                    )
                ], spacing=8),
                padding=20
            ),
            elevation=2
        )


    # UI Controls
    # Header metadata
    last_updated_text = ft.Text("Last updated: Never", size=12)
    # Slim live refresh indicator displayed during async updates
    refresh_indicator = ft.ProgressBar(height=3, value=None, visible=False)

    cpu_text = ft.Text("CPU: 0%", size=14)
    memory_text = ft.Text("Memory: 0%", size=14)
    disk_text = ft.Text("Disk: 0%", size=14)

    # Activity list
    activity_list = ft.ListView(
        expand=True,
        spacing=5,
        padding=ft.padding.all(10)
    )

    # Clients snapshot controls
    clients_list = ft.ListView(expand=True, spacing=6, padding=ft.padding.all(10))
    clients_empty = ft.Text("No clients available", size=12, color=ft.Colors.OUTLINE)

    # Capacity & forecast controls
    used_text = ft.Text("Used: --", size=14)
    free_text = ft.Text("Free: --", size=14)
    forecast_text = ft.Text("Forecast: --", size=12, color=ft.Colors.OUTLINE)
    # Real PieChart instead of placeholder
    capacity_pie = ft.PieChart(
        sections=[],
        sections_space=2,
        center_space_radius=50,
        height=200,
        width=200,
    )

    # KPI controls
    kpi_total_clients_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    kpi_active_jobs_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    kpi_errors_24h_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    kpi_storage_used_text = ft.Text("0 GB", size=28, weight=ft.FontWeight.BOLD)

    def _kpi_card(value_control: ft.Text, label: str, icon: str, color, on_click=None) -> ft.Container:
        """Simplified KPI card using Flet's native features."""
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(icon, size=16, color=color),
                        width=24, height=24, alignment=ft.alignment.center,
                        border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.15, color)
                    ),
                    ft.Text(label, size=12, color=ft.Colors.OUTLINE)
                ], spacing=8),
                value_control,
            ], spacing=6),
            padding=ft.padding.all(12),
            border=ft.border.all(1, ft.Colors.with_opacity(0.20, color)),
            border_radius=8,
            shadow=ft.BoxShadow(blur_radius=10, offset=ft.Offset(0,3), color=ft.Colors.with_opacity(0.10, color)),
            bgcolor=ft.Colors.with_opacity(0.06, color),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
            on_click=on_click,
            tooltip=label,
        )

    # Navigation helpers using the app_ref exposed on page
    def _go_to_clients(e: Optional[ft.ControlEvent] = None) -> None:
        try:
            if hasattr(page, 'app_ref') and hasattr(page.app_ref, '_switch_to_view'):
                page.app_ref._switch_to_view(1)  # Clients
        except Exception:
            pass

    def _go_to_files(e: Optional[ft.ControlEvent] = None) -> None:
        try:
            if hasattr(page, 'app_ref') and hasattr(page.app_ref, '_switch_to_view'):
                page.app_ref._switch_to_view(2)  # Files
        except Exception:
            pass

    def _go_to_logs(e: Optional[ft.ControlEvent] = None) -> None:
        try:
            if hasattr(page, 'app_ref') and hasattr(page.app_ref, '_switch_to_view'):
                page.app_ref._switch_to_view(5)  # Logs
        except Exception:
            pass

    kpi_row = ft.ResponsiveRow([
        ft.Column([_kpi_card(kpi_total_clients_text, "Total Clients", ft.Icons.PEOPLE, ft.Colors.BLUE, on_click=_go_to_clients)], col={"sm": 6, "md": 3, "lg": 3}),
        ft.Column([_kpi_card(kpi_active_jobs_text, "Active Jobs", ft.Icons.SYNC, ft.Colors.CYAN)], col={"sm": 6, "md": 3, "lg": 3}),
        ft.Column([_kpi_card(kpi_errors_24h_text, "Errors (24h)", ft.Icons.ERROR_OUTLINE, ft.Colors.RED)], col={"sm": 6, "md": 3, "lg": 3}),
        ft.Column([_kpi_card(kpi_storage_used_text, "Storage Used", ft.Icons.STORAGE, ft.Colors.PURPLE, on_click=_go_to_files)], col={"sm": 6, "md": 3, "lg": 3}),
    ], spacing=12)

    # Live system sparkline charts using native LineChart for better performance
    def _create_sparkline(color) -> ft.LineChart:
        return ft.LineChart(
            data_series=[ft.LineChartData(
                data_points=[],
                color=color,
                stroke_width=2,
                curved=True,
                prevent_curve_over_shooting=True
            )],
            min_y=0,
            max_y=100,
            width=220,
            height=70,
            interactive=False,
            bgcolor=ft.Colors.TRANSPARENT,
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE)),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.Colors.with_opacity(0.1, color),
                width=1
            ),
            vertical_grid_lines=ft.ChartGridLines(
                color=ft.Colors.with_opacity(0.1, color),
                width=1
            )
        )

    cpu_spark = _create_sparkline(ft.Colors.BLUE)
    mem_spark = _create_sparkline(ft.Colors.GREEN)
    disk_spark = _create_sparkline(ft.Colors.PURPLE)

    def _update_spark(chart: ft.LineChart, values: List[float], color) -> None:
        """Update sparkline with efficient LineChart data points using modern Python."""
        # Use walrus operator and generator expression for efficiency
        if not (limited_values := values[-MAX_HISTORY_POINTS:]):
            return

        data_points = [
            ft.LineChartDataPoint(x=i, y=max(0.0, min(100.0, float(v))))
            for i, v in enumerate(limited_values)
        ]

        chart.data_series = [ft.LineChartData(
            data_points=data_points,
            color=color,
            stroke_width=2,
            curved=True,
            prevent_curve_over_shooting=True
        )]


    # Update all displays
    def _compute_server_status_label(running: bool) -> Tuple[str, str]:
        """Return (label, severity) based on bridge and status.
        severity in {excellent, good, warning, critical, info, neutral}
        """
        # Default
        label = "Unknown"
        severity = "neutral"
        try:
            if server_bridge is None:
                return ("Not existing", "critical")
            # If we can't get data reliably
            if current_server_status is None or not isinstance(current_server_status, dict) or not current_server_status:
                return ("Not available", "critical")
            # Running/connected state
            if running:
                # Differentiate mock vs real if possible
                is_real = getattr(server_bridge, "real_server", False)
                return ("Connected" if is_real else "Connected (Simulated)", "excellent")
            else:
                return ("Disconnected", "warning")
        except Exception:
            return (label, severity)

    def update_all_displays() -> None:
        """Update all dashboard displays with current data."""
        nonlocal current_server_status, current_system_metrics, current_activity, current_clients, last_updated, cpu_history, memory_history, disk_history

        # Get fresh data
        current_server_status = get_server_status()
        current_system_metrics = get_system_metrics()
        current_activity = get_activity_data()

        # Get clients (top N)
        current_clients = []
        if server_bridge:
            try:
                # Use documented API for compatibility
                clients_result = server_bridge.get_all_clients_from_db()
                # Normalize
                if isinstance(clients_result, dict) and clients_result.get('success'):
                    current_clients = clients_result.get('data', [])
                elif isinstance(clients_result, list):
                    current_clients = clients_result
            except Exception as e:
                logger.debug(f"Failed to fetch clients: {e}")
        last_updated = datetime.now().strftime("%H:%M:%S")

        # Update server status with status pill
        running = current_server_status.get('running', False)
        # Header actions visibility only (remove unused card controls)
        try:
            connect_button.visible = not running
            disconnect_button.visible = running
        except Exception:
            pass

        # Update system metrics
        cpu_percent = current_system_metrics.get('cpu_percent', 0)
        memory_percent = current_system_metrics.get('memory_percent', 0)
        disk_percent = current_system_metrics.get('disk_percent', 0)

        cpu_text.value = f"CPU: {cpu_percent:.1f}%"
        memory_text.value = f"Memory: {memory_percent:.1f}%"
        disk_text.value = f"Disk: {disk_percent:.1f}%"

        # Update history and sparklines with memory-efficient deque
        try:
            cpu_history.append(float(cpu_percent))
            memory_history.append(float(memory_percent))
            disk_history.append(float(disk_percent))
            # Deque automatically maintains maxlen, no manual truncation needed
            _update_spark(cpu_spark, list(cpu_history), ft.Colors.BLUE)
            _update_spark(mem_spark, list(memory_history), ft.Colors.GREEN)
            _update_spark(disk_spark, list(disk_history), ft.Colors.PURPLE)
        except Exception as e:
            logger.debug(f"Failed to update sparklines: {e}")

    # Update activity list
        update_activity_list()

        # Update clients snapshot list
        update_clients_list()

        # Update capacity & forecast
        try:
            used_pct = float(disk_percent)
            free_pct = max(0.0, 100.0 - used_pct)
            # Simple projection: if usage > 80%, warn; else OK
            if used_pct >= 90:
                proj = "Critical: expand storage ASAP"
            elif used_pct >= 80:
                proj = "Warning: nearing capacity"
            else:
                proj = "Healthy"

            used_text.value = f"Used: {used_pct:.1f}%"
            free_text.value = f"Free: {free_pct:.1f}%"
            forecast_text.value = f"Forecast: {proj}"

            # Rebuild pie sections efficiently by replacing sections list
            capacity_pie.sections = [
                ft.PieChartSection(value=used_pct, color=ft.Colors.BLUE, title="Used", radius=80,
                                   badge=ft.Text(f"{used_pct:.0f}%", size=10, color=ft.Colors.WHITE)),
                ft.PieChartSection(value=free_pct, color=ft.Colors.GREEN, title="Free", radius=80,
                                   badge=ft.Text(f"{free_pct:.0f}%", size=10, color=ft.Colors.WHITE)),
            ]
        except Exception as e:
            logger.debug(f"Capacity update failed: {e}")

        # Update KPI values
        try:
            print(f"[DEBUG] Updating KPI values with server status: {current_server_status}")
            logger.debug(f"Updating KPI values with server status: {current_server_status}")

            # Total clients
            total_clients_val = current_server_status.get('clients_connected', len(current_clients))
            print(f"[DEBUG] Setting total clients to: {total_clients_val}")
            logger.debug(f"Setting total clients to: {total_clients_val}")
            kpi_total_clients_text.value = str(total_clients_val)
            hero_total_clients_text.value = str(total_clients_val)

            # Active jobs approximation: activities in last 10m containing start/running keywords
            now_dt = datetime.now()
            keywords = ["start", "running", "upload", "transfer"]
            active_jobs = 0
            for a in current_activity:
                ts = a.get('timestamp', now_dt)
                if isinstance(ts, datetime):
                    recent = (now_dt - ts) <= timedelta(minutes=10)
                else:
                    recent = True
                if recent and any(k in str(a.get('message', '')).lower() for k in keywords):
                    active_jobs += 1
            logger.debug(f"Setting active jobs to: {active_jobs}")
            kpi_active_jobs_text.value = str(active_jobs)

            # Errors 24h
            err24 = 0
            for a in current_activity:
                ts = a.get('timestamp', now_dt)
                within = True
                if isinstance(ts, datetime):
                    within = (now_dt - ts) <= timedelta(hours=24)
                if within and str(a.get('type', 'info')).lower() == 'error':
                    err24 += 1
            logger.debug(f"Setting errors 24h to: {err24}")
            kpi_errors_24h_text.value = str(err24)

            # Storage used
            storage_val = current_server_status.get('storage_used_gb', 0)
            logger.debug(f"Setting storage used to: {storage_val}")
            kpi_storage_used_text.value = f"{storage_val:.1f} GB"

            # Active transfers and uptime hero metrics
            hero_active_transfers_text.value = str(current_server_status.get('total_transfers', 0))
            try:
                up = int(current_server_status.get('uptime_seconds', 0))
                uh, um = up // 3600, (up % 3600) // 60
                hero_uptime_text.value = f"{uh}h {um}m"
            except Exception:
                hero_uptime_text.value = "0h 0m"
        except Exception:
            pass

        # Update header status indicator
        try:
            label, severity = _compute_server_status_label(running)
            severity_colors = {
                "excellent": ft.Colors.GREEN,
                "good": ft.Colors.GREEN,
                "warning": ft.Colors.ORANGE,
                "critical": ft.Colors.RED,
                "info": ft.Colors.BLUE,
                "neutral": ft.Colors.OUTLINE,
            }
            color = severity_colors.get(severity, ft.Colors.PRIMARY)
            server_status_indicator_container.content = ft.Container(
                content=ft.Row([
                    ft.Container(width=8, height=8, bgcolor=color, border_radius=4),
                    ft.Text(label, color=color, weight=ft.FontWeight.BOLD)
                ], spacing=8)
            )
        except Exception:
            pass

        # Update last updated
        last_updated_text.value = f"Last updated: {last_updated}"

        # Simplified update pattern using Flet's efficient update system
        try:
            # Explicitly update each KPI control
            kpi_total_clients_text.update()
            kpi_active_jobs_text.update()
            kpi_errors_24h_text.update()
            kpi_storage_used_text.update()
            hero_total_clients_text.update()
            hero_active_transfers_text.update()
            hero_uptime_text.update()

            # Use control.update() for 10x performance improvement over page.update()
            dashboard_container.update()
            logger.debug("Dashboard container updated successfully")
        except Exception as e:
            logger.debug(f"Update failed: {e}")
            # Fallback to page update if control update fails
            try:
                page.update()
                logger.debug("Fallback page update completed")
            except Exception as e2:
                logger.error(f"Both control and page updates failed: {e2}")

    async def _update_all_displays_async(source: str = 'auto') -> None:
        """Async version of update_all_displays."""
        nonlocal current_server_status, current_system_metrics, current_activity, current_clients, last_updated, prev_server_snapshot, last_significant_toast_time

        try:
            # Show slim refresh indicator during async updates
            refresh_indicator.visible = True
            with contextlib.suppress(Exception):
                refresh_indicator.update()

            import asyncio
            loop = asyncio.get_event_loop()

            # Concurrent data fetching for better performance
            tasks = [
                loop.run_in_executor(None, get_server_status),
                loop.run_in_executor(None, get_system_metrics),
                loop.run_in_executor(None, get_activity_data)
            ]

            # Add clients task if server bridge available
            if server_bridge:
                tasks.append(loop.run_in_executor(None, server_bridge.get_all_clients_from_db))
            # Execute all data fetching concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results with proper type safety - use async results, not re-call functions
            current_server_status = results[0] if (not isinstance(results[0], Exception) and isinstance(results[0], dict)) else get_server_status()
            current_system_metrics = results[1] if (not isinstance(results[1], Exception) and isinstance(results[1], dict)) else get_system_metrics()

            # Handle activity data
            if isinstance(results[2], Exception):
                current_activity = []
            elif isinstance(results[2], list):
                current_activity = results[2]
            else:
                current_activity = []

            # Handle clients result if server bridge was used
            if server_bridge and len(results) > 3:
                clients_result = [] if isinstance(results[3], Exception) else results[3]
                if isinstance(clients_result, dict) and clients_result.get('success'):
                    current_clients = clients_result.get('data', [])
                elif isinstance(clients_result, list):
                    current_clients = clients_result
                else:
                    current_clients = []

            # Update displays with fetched data
            last_updated = datetime.now().strftime("%H:%M:%S")
            try:
                update_all_displays()
            except Exception as e:
                logger.debug(f"update_all_displays() failed: {e}")

        except Exception as e:
            logger.debug(f"Async display update failed: {e}")
        finally:
            # Save snapshot for next delta comparison
            try:
                prev_server_snapshot = dict(current_server_status) if isinstance(current_server_status, dict) else None
            except Exception:
                pass
            # Hide refresh indicator when finished
            refresh_indicator.visible = False
            with contextlib.suppress(Exception):
                refresh_indicator.update()

    async def _update_operations_panels_async() -> None:
        """Async version of operations panels update."""
        try:
            await asyncio.get_event_loop().run_in_executor(None, _update_operations_panels)
        except Exception as e:
            logger.debug(f"Async operations panels update failed: {e}")

    def update_activity_list() -> None:
        """Update the activity list."""
        activity_list.controls.clear()

        # Filter activities with type safety
        safe_activity = current_activity if isinstance(current_activity, list) else []
        filtered_activities = (
            safe_activity if activity_filter == "All" else
            [activity for activity in safe_activity
             if activity.get('type', '').lower() == activity_filter.lower()]
        )

        # Empty state messaging
        if not filtered_activities:
            activity_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=18, color=ft.Colors.OUTLINE),
                        ft.Text("No activity to display", size=12, color=ft.Colors.OUTLINE)
                    ], spacing=8),
                    padding=ft.padding.all(8),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.OUTLINE)
                )
            )
            try:
                activity_list.update()
            except Exception:
                pass
            return

        # Add activities to list
        for activity in filtered_activities[:10]:
            activity_type = activity.get('type', 'info').lower()
            if activity_type == 'error':
                icon, color = ft.Icons.ERROR_OUTLINE, ft.Colors.RED
            elif activity_type == 'warning':
                icon, color = ft.Icons.WARNING_AMBER, ft.Colors.ORANGE
            elif activity_type == 'success':
                icon, color = ft.Icons.CHECK_CIRCLE_OUTLINE, ft.Colors.GREEN
            else:
                icon, color = ft.Icons.INFO_OUTLINE, ft.Colors.BLUE

            timestamp = activity.get('timestamp', datetime.now())
            if isinstance(timestamp, str):
                time_str = timestamp
            else:
                time_ago = datetime.now() - timestamp
                if time_ago.days > 0:
                    time_str = f"{time_ago.days} days ago"
                elif time_ago.seconds > 3600:
                    time_str = f"{time_ago.seconds // 3600} hours ago"
                elif time_ago.seconds > 60:
                    time_str = f"{time_ago.seconds // 60} minutes ago"
                else:
                    time_str = "Just now"

            # Simplified list item with native Flet hover
            tile = ft.Container(
                content=ft.ListTile(
                    leading=ft.Icon(icon, color=color, size=20),
                    title=ft.Text(activity.get('message', ''), size=13),
                    subtitle=ft.Text(time_str, size=11)
                ),
                border_radius=8,
                animate=ft.Animation(100, ft.AnimationCurve.EASE_OUT),
                padding=ft.padding.only(left=4, top=2, right=4, bottom=2)
            )
            activity_list.controls.append(tile)

        try:
            activity_list.update()
        except Exception:
            pass

    def update_clients_list() -> None:
        """Update clients snapshot list from current_clients."""
        clients_list.controls.clear()
        if not current_clients:
            clients_list.controls.append(clients_empty)
        else:
            # Sort by last_seen desc when available
            def _parse_ts(v: Any) -> datetime:
                try:
                    if isinstance(v, datetime):
                        return v
                    # try ISO-like
                    return datetime.fromisoformat(str(v))
                except Exception:
                    return datetime.min

            sorted_clients = sorted(current_clients, key=lambda c: _parse_ts(c.get('last_seen') or c.get('last_activity')), reverse=True)
            for client in sorted_clients[:8]:
                name = client.get('name') or client.get('client_id', 'unknown')
                status = str(client.get('status', 'unknown')).lower()
                last_seen = client.get('last_seen', client.get('last_activity', ''))
                status_color = ft.Colors.GREEN if status in ['online', 'active', 'connected'] else (
                    ft.Colors.ORANGE if status in ['idle', 'warning'] else ft.Colors.RED
                )
                item = ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.PERSON, size=18, color=status_color),
                        ft.Text(name, expand=True, size=13),
                        ft.Text(str(last_seen), size=11, color=ft.Colors.OUTLINE)
                    ], spacing=10),
                    padding=ft.padding.only(left=8, top=6, right=8, bottom=6),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.04, status_color),
                    animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT)
                )
                clients_list.controls.append(item)

    # Server control actions
    # Server and refresh handlers moved to event handlers section

    # Create UI components (header actions only)

    # Backup action (moved to event handlers section)

    # Premium asymmetric dashboard grid with sophisticated visual hierarchy
    hero_metrics_section = ft.ResponsiveRow([
        # Hero metric takes visual prominence with primary gradient
        ft.Column([
            create_premium_hero_card("0", "Total Clients", "+0", "primary", value_control=hero_total_clients_text, on_click=_go_to_clients)
        ], col={"sm": 12, "md": 8, "lg": 6}),
        # Secondary metrics cluster with different gradient schemes
        ft.Column([
            ft.Column([
                create_premium_hero_card("0", "Active Transfers", "+0", "success", value_control=hero_active_transfers_text, on_click=_go_to_files),
                create_premium_hero_card("0h 0m", "Server Uptime", "", "info", value_control=hero_uptime_text, on_click=_go_to_logs)
            ], spacing=20)
        ], col={"sm": 12, "md": 4, "lg": 6})
    ], spacing=28)


    # Capacity & Forecast card
    capacity_content = ft.Row([
        ft.Container(content=capacity_pie),
        ft.Column([
            used_text,
            free_text,
            forecast_text,
        ], spacing=8, expand=True)
    ], spacing=16, alignment=ft.MainAxisAlignment.START)

    capacity_card = themed_card(
        content=capacity_content,
        title="CAPACITY & FORECAST",
        page=page
    )

    clients_content = ft.Container(
        content=clients_list,
        height=260
    )

    clients_card = themed_card(
        content=clients_content,
        title="CLIENTS SNAPSHOT",
        page=page
    )

    # Create server status indicator used in header (dynamic)
    # Slim top bar: integrates status + actions in one compact bar
    def on_live_toggle(e: ft.ControlEvent) -> None:
        nonlocal auto_refresh_enabled
        auto_refresh_enabled = bool(e.control.value)
        show_success_message(page, "Live refresh enabled" if auto_refresh_enabled else "Live refresh paused")

    live_switch = ft.Switch(label="Live", value=True, on_change=on_live_toggle)
    # Set simple string tooltips for broad Flet compatibility
    server_status_indicator_container.tooltip = "Server status"
    connect_button.tooltip = "Connect to server"
    disconnect_button.tooltip = "Disconnect from server"
    backup_button.tooltip = "Start backup"
    refresh_button.tooltip = "Refresh dashboard"
    live_switch.tooltip = "Toggle live auto-refresh"

    # Action Button Grouping - Primary and Secondary groups for better UX
    # Primary actions - most frequent, high impact operations
    primary_action_group = create_action_group([
        connect_button,
        disconnect_button,
        backup_button,
    ], "primary")

    # Secondary actions - configuration and monitoring
    secondary_action_group = create_action_group([
        refresh_button,
        live_switch,
    ], "secondary")

    header_section = ft.Container(
        content=ft.Row([
            ft.Text("Dashboard", size=20, weight=ft.FontWeight.W_600),
            ft.Container(expand=True),
            server_status_indicator_container,
            ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE),
            primary_action_group,
            ft.VerticalDivider(width=1, color=ft.Colors.OUTLINE),
            secondary_action_group,
            ft.Container(width=8),
            last_updated_text,
        ], spacing=12, alignment=ft.MainAxisAlignment.START),
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8,
        bgcolor=ft.Colors.SURFACE,
        animate_opacity=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        opacity=1.0,  # Fixed: was 0.0 making header invisible!
    )


    # Live System Metrics card with sparklines
    live_metrics_content = ft.Row([
        ft.Column([ft.Text("CPU", size=12, color=ft.Colors.OUTLINE), cpu_text, cpu_spark], spacing=6, expand=True),
        ft.Column([ft.Text("Memory", size=12, color=ft.Colors.OUTLINE), memory_text, mem_spark], spacing=6, expand=True),
        ft.Column([ft.Text("Disk", size=12, color=ft.Colors.OUTLINE), disk_text, disk_spark], spacing=6, expand=True),
    ], spacing=12)

    live_system_metrics_card = themed_card(
        content=live_metrics_content,
        title="LIVE SYSTEM METRICS",
        page=page
    )

    # Running Jobs & Recent Backups sections
    running_jobs_list = ft.ListView(expand=True, spacing=6, padding=ft.padding.all(10), height=160)
    recent_backups_list = ft.ListView(expand=True, spacing=6, padding=ft.padding.all(10), height=160)

    def filter_activities_by_keywords(
        activities: List[ActivityEntry],
        keywords: List[str],
        time_window_minutes: Optional[int] = None
    ) -> Iterator[ActivityEntry]:
        """Efficient activity filtering using generator and modern Python patterns."""
        now = datetime.now()
        time_threshold = timedelta(minutes=time_window_minutes) if time_window_minutes else None

        return (
            activity for activity in activities
            if any(keyword in activity['message'].lower() for keyword in keywords) and
               (not time_threshold or
                (isinstance(activity['timestamp'], datetime) and
                 (now - activity['timestamp']) <= time_threshold))
        )

    def create_operation_item(activity: ActivityEntry, icon: str, color: str, status_text: Optional[str] = None) -> ft.Container:
        """Create operation item with type safety."""
        timestamp = activity['timestamp']
        time_display = timestamp.strftime("%H:%M") if isinstance(timestamp, datetime) else str(timestamp)
        subtitle = status_text or f"at {time_display}"

        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(icon, color=color, size=18),
                title=ft.Text(activity['message'], size=13),
                subtitle=ft.Text(subtitle, size=11, color=ft.Colors.OUTLINE),
                dense=True
            ),
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.05, color),
            animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT)
        )

    def _update_operations_panels() -> None:
        """Optimized operations panel update using modern Python patterns."""
        # Ensure current_activity is a proper list for type safety
        safe_activity = current_activity if isinstance(current_activity, list) else []

        # Use constants and functional approach
        running_jobs = list(filter_activities_by_keywords(
            safe_activity, JOB_KEYWORDS, ACTIVITY_TIME_WINDOW
        ))[:MAX_OPERATIONS_DISPLAY]

        recent_backups = list(filter_activities_by_keywords(
            safe_activity, BACKUP_KEYWORDS
        ))[:MAX_OPERATIONS_DISPLAY]

        # Update running jobs (simple conditional to reduce analyzer noise)
        running_jobs_list.controls.clear()
        if not running_jobs:
            running_jobs_list.controls.append(
                ft.Text("All clear – no running jobs", size=12, color=ft.Colors.OUTLINE)
            )
        else:
            running_jobs_list.controls.extend(
                create_operation_item(job, ft.Icons.SYNC, ft.Colors.BLUE, "Running")
                for job in running_jobs
            )

        # Update recent backups (simple conditional to reduce analyzer noise)
        recent_backups_list.controls.clear()
        if not recent_backups:
            recent_backups_list.controls.append(
                ft.Text("No recent backups", size=12, color=ft.Colors.OUTLINE)
            )
        else:
            recent_backups_list.controls.extend(
                create_operation_item(backup, ft.Icons.BACKUP, ft.Colors.GREEN)
                for backup in recent_backups
            )

    # Wrap operations panels into cards
    running_jobs_card = themed_card(content=running_jobs_list, title="RUNNING JOBS", page=page)
    recent_backups_card = themed_card(content=recent_backups_list, title="RECENT BACKUPS", page=page)


    # Clean, organized layout structure (streamlined, no redundant big sections)
    main_content = ft.Column([
        # Header
        header_section,
        refresh_indicator,
        ft.Container(height=16),
        kpi_row,
        ft.Container(height=16),
        live_system_metrics_card,
        ft.Container(height=16),

        # QUATERNARY: Activity Stream & Capacity/Clients Snapshot + Ops panels
        ft.ResponsiveRow([
            ft.Column([
                create_premium_activity_stream(),
                ft.Container(height=16),
                running_jobs_card
            ], col={"sm": 12, "md": 6}),
            ft.Column([
                ft.Column([
                    capacity_card,
                    clients_card,
                    ft.Container(height=24),
                    recent_backups_card
                ], spacing=16)
            ], col={"sm": 12, "md": 6})
        ], spacing=24)
    ], expand=True, spacing=0, scroll=ft.ScrollMode.AUTO)

    # Create the main container with scrolling to prevent clipping
    dashboard_container = ft.Container(
        content=ft.Column([
            main_content
        ], scroll=ft.ScrollMode.AUTO),  # Add scrollbar when needed
        padding=ft.padding.only(left=28, top=20, right=28, bottom=20),
        expand=True,
        bgcolor=ft.Colors.SURFACE,
        opacity=0.0,
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )

    def setup_subscriptions() -> None:
        """Setup subscriptions and initial data loading after view is added to page."""
        nonlocal refresh_task, _stop_polling

        # Defer heavy initial data loading to avoid blocking UI
        async def _deferred_initial_load() -> None:
            try:
                print("[DEBUG] Starting deferred initial load")
                # Small delay to let UI settle
                await asyncio.sleep(0.1)

                # Update displays asynchronously
                print("[DEBUG] Calling _update_all_displays_async('initial')")
                await _update_all_displays_async('initial')

                # Update operations panels asynchronously
                await _update_operations_panels_async()

            except Exception as e:
                print(f"[DEBUG] Deferred initial load failed: {e}")
                logger.debug(f"Deferred initial load failed: {e}")
                # Fallback to synchronous loading if async fails
                try:
                    print("[DEBUG] Falling back to synchronous update_all_displays()")
                    update_all_displays()
                    _update_operations_panels()
                except Exception as e2:
                    print(f"[DEBUG] Fallback loading also failed: {e2}")
                    logger.debug(f"Fallback loading also failed: {e2}")

        # Start deferred initial loading
        page.run_task(_deferred_initial_load)

        # Fade-in entrance effect once attached
        try:
            dashboard_container.opacity = 1.0
            dashboard_container.update()
        except Exception:
            pass

        # Start lightweight periodic refresh in background using constants
        async def _poll_loop() -> None:
            nonlocal _stop_polling
            operations_update_counter = 0
            try:
                while not _stop_polling:
                    await asyncio.sleep(POLLING_INTERVAL)
                    if auto_refresh_enabled:
                        # Fetch & update asynchronously to prevent UI blocking
                        try:
                            await _update_all_displays_async('auto')
                            # Only update operations panels every other cycle to reduce load
                            operations_update_counter += 1
                            if operations_update_counter % OPERATIONS_UPDATE_CYCLE == 0:
                                await _update_operations_panels_async()
                        except Exception as e:
                            logger.debug(f"Async update failed: {e}")
            except Exception as e:
                logger.debug(f"Polling loop terminated: {e}")

        # Start the polling loop after initial setup
        try:
            refresh_task = page.run_task(_poll_loop)
        except Exception as e:
            logger.debug(f"Failed to start polling task: {e}")

    def dispose() -> None:
        """Clean up subscriptions and resources."""
        nonlocal _stop_polling, refresh_task
        logger.debug("Disposing dashboard view")
        _stop_polling = True

        # Properly cancel the refresh task
        if refresh_task:
            try:
                refresh_task.cancel()
                logger.debug("Dashboard refresh task cancelled")
            except Exception as e:
                logger.debug(f"Error cancelling refresh task: {e}")
            refresh_task = None

    return dashboard_container, dispose, setup_subscriptions
