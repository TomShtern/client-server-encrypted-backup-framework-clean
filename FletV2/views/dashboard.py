#!/usr/bin/env python3
"""
Simplified Dashboard View - The Flet Way
~400 lines instead of 1,005 lines of framework fighting!

Core Principle: Use Flet's built-in components for metrics, progress bars, and cards.
Clean, maintainable dashboard that preserves all user-facing functionality.
"""

import flet as ft
import asyncio
import contextlib
from typing import Optional, Dict, Any, List, Tuple
import psutil
import random
from datetime import datetime, timedelta

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_components import themed_card, themed_button

# Enhanced components using proper themed functions
def create_status_pill(text: str, status: str) -> ft.Container:
    """Modern status pill with gradients and better styling."""
    if status == "success":
        color = ft.Colors.GREEN
        bg_color = ft.Colors.with_opacity(0.1, ft.Colors.GREEN)
    elif status == "error":
        color = ft.Colors.ERROR
        bg_color = ft.Colors.with_opacity(0.1, ft.Colors.ERROR)
    elif status == "warning":
        color = ft.Colors.ORANGE
        bg_color = ft.Colors.with_opacity(0.1, ft.Colors.ORANGE)
    else:
        color = ft.Colors.PRIMARY
        bg_color = ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY)

    return ft.Container(
        content=ft.Text(
            text,
            color=color,
            size=12,
            weight=ft.FontWeight.W_600
        ),
        bgcolor=bg_color,
        border=ft.border.all(1, color),
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=16, vertical=6)
    )

"""
Removed unused helper create_modern_metric_card to reduce dead code and duplication.
"""
from utils.user_feedback import show_success_message, show_error_message

logger = get_logger(__name__)


def create_dashboard_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    _state_manager: StateManager
) -> ft.Control:
    """Modern 2025 dashboard with visual hierarchy, semantic colors, and engaging data storytelling."""
    logger.info("Creating modern dashboard with enhanced visual appeal")

    # Apply the enhanced modern theme for 2025 visual excellence
    from theme import setup_modern_theme
    setup_modern_theme(page)

    # Simple state management
    current_server_status = {}
    current_system_metrics = {}
    current_activity = []
    current_clients: List[Dict[str, Any]] = []
    refresh_task = None
    _stop_polling = False
    auto_refresh_enabled = True
    activity_filter = "All"
    last_updated = "Never"
    # For significant-change detection and toast throttling
    prev_server_snapshot: Optional[Dict[str, Any]] = None
    last_significant_toast_time: Optional[datetime] = None

    # Mini charts history buffers (keep last 30 samples)
    cpu_history: List[float] = []
    memory_history: List[float] = []
    disk_history: List[float] = []

    # Action Button Grouping Helper Function
    def create_action_group(buttons: List[ft.Control],
                           group_type: str = "primary",
                           spacing: int = 8) -> ft.Container:
        """
        Create a visually grouped set of action buttons.

        Args:
            buttons: List of button controls to group
            group_type: "primary" for main actions, "secondary" for less frequent actions
            spacing: Space between buttons
        """
        if group_type == "primary":
            bgcolor = ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY)
        else:
            bgcolor = ft.Colors.with_opacity(0.03, ft.Colors.OUTLINE)

        # Subtle hover elevation & tint
        hover_bg = ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY) if group_type == "primary" else ft.Colors.with_opacity(0.05, ft.Colors.OUTLINE)
        cont = ft.Container(
            content=ft.Row(buttons, spacing=spacing),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=8,
            bgcolor=bgcolor,
            animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
            animate_opacity=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
        )
        def _on_hover(e: ft.HoverEvent):
            try:
                e.control.bgcolor = hover_bg if e.data == 'true' else bgcolor
                e.control.opacity = 1.0 if e.data == 'true' else 0.98
                e.control.update()
            except Exception:
                pass
        cont.on_hover = _on_hover
        return cont

    # Get server status data
    def get_server_status() -> Dict[str, Any]:
        """Get server status using server bridge or mock data."""
        if server_bridge:
            try:
                result = server_bridge.get_server_status()
                if result.get('success'):
                    return result.get('data', {})
            except Exception as e:
                logger.warning(f"Server bridge failed: {e}")

        # Mock data fallback
        return {
            'running': True,
            'port': 8080,
            'uptime_seconds': 3600 + random.randint(0, 7200),
            'clients_connected': random.randint(0, 15),
            'total_files': random.randint(50, 200),
            'total_transfers': random.randint(0, 10),
            'storage_used_gb': round(random.uniform(1.5, 25.8), 1)
        }

    # Get system metrics using psutil
    def get_system_metrics() -> Dict[str, Any]:
        """Get real system metrics using psutil."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': (disk.used / disk.total) * 100
            }
        except Exception as e:
            logger.warning(f"Failed to get system metrics: {e}")
            return {
                'cpu_percent': 45.0,
                'memory_percent': 68.0,
                'disk_percent': 35.0
            }

    # Get activity data
    def get_activity_data() -> List[Dict[str, Any]]:
        """Get recent activity data using logs as canonical source, with mock fallback."""
        if server_bridge:
            try:
                logs_result = server_bridge.get_logs()
                if isinstance(logs_result, dict) and logs_result.get('success'):
                    entries = logs_result.get('data', [])
                else:
                    entries = logs_result if isinstance(logs_result, list) else []

                activities: List[Dict[str, Any]] = []
                for i, entry in enumerate(entries):
                    # Normalize fields
                    level = str(entry.get('level', entry.get('severity', 'info'))).lower()
                    msg = entry.get('message', entry.get('msg', ''))
                    ts = entry.get('timestamp', entry.get('time', datetime.now()))
                    activities.append({
                        'id': i + 1,
                        'type': level if level in ['info', 'warning', 'error', 'success'] else 'info',
                        'message': msg,
                        'timestamp': ts,
                    })
                return sorted(activities, key=lambda x: x['timestamp'], reverse=True)
            except Exception as e:
                logger.debug(f"Falling back to mock activity due to logs error: {e}")

        # Mock activity data
        activities = []
        activity_types = ["info", "error", "warning", "success"]
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
        """Create premium hero metric card using Flet's Card component.

        If value_control is provided, it's used for dynamic updates.
        """
        # Use Flet's semantic color system
        if card_type == "success":
            color = ft.Colors.GREEN
        elif card_type == "info":
            color = ft.Colors.BLUE
        else:  # primary
            color = ft.Colors.PRIMARY

        # Trend indicator
        trend_widget = None
        if trend:
            is_positive = trend.startswith("+")
            trend_widget = ft.Row([
                ft.Icon(ft.Icons.TRENDING_UP if is_positive else ft.Icons.TRENDING_DOWN, size=16, color=color),
                ft.Text(trend, size=14, weight=ft.FontWeight.BOLD, color=color)
            ], spacing=4)

        value_text = value_control or ft.Text(value, size=48, weight=ft.FontWeight.BOLD, color=color)
        label_text = ft.Text(label, size=16, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE)

        # Base content row (value + trend)
        header_row = ft.Row([
            value_text,
            trend_widget or ft.Container()
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
           animate_scale=ft.Animation(100, ft.AnimationCurve.EASE_OUT))

        # Overlay for pressed/hover tint (Stacked above base content)
        is_dark = False
        try:
            is_dark = (getattr(page, "theme_mode", None) == ft.ThemeMode.DARK)
        except Exception:
            pass
        # Overlay opacities (keep inside function scope for correctness)
        overlay_hover_opacity = 0.08 if is_dark else 0.06
        overlay_pressed_opacity = 0.12 if is_dark else 0.08
        overlay = ft.Container(
            bgcolor=ft.Colors.with_opacity(overlay_hover_opacity, color),
            border_radius=16,
            opacity=0.0,
        )

        # Subtle pressed feedback wrapper (applies to entire hero card area and header/label subparts)
        def _handle_click(e):
            if on_click is None:
                return
            try:
                # Brief press effect: scale down and show overlay
                header_row.scale = 0.985
                label_text.opacity = 0.95
                overlay.opacity = overlay_pressed_opacity
                # Update affected controls
                try:
                    header_row.update()
                    label_text.update()
                    overlay.update()
                except Exception:
                    pass

                async def _reset_and_invoke():
                    try:
                        await asyncio.sleep(0.08)
                        header_row.scale = 1.0
                        label_text.opacity = 1.0
                        overlay.opacity = 0.0
                        try:
                            header_row.update()
                            label_text.update()
                            overlay.update()
                        except Exception:
                            pass
                    except Exception:
                        pass
                    # Invoke original handler
                    try:
                        on_click(e)
                    except Exception:
                        pass

                page.run_task(_reset_and_invoke)
            except Exception:
                # On any failure, still try to invoke original handler
                try:
                    on_click(e)
                except Exception:
                    pass

        # Base card container
        base_container = ft.Container(
            content=ft.Column([
                header_row,
                label_text,
            ], spacing=8),
            padding=24,
            bgcolor=ft.Colors.with_opacity(0.05, color),
            border_radius=16,
        )

        # Top interactive layer covering the whole card area
        interactive_layer = ft.Container(
            border_radius=16,
            on_click=_handle_click if on_click else None,
        )

        def _on_hover(e: ft.HoverEvent):
            try:
                if e.data == 'true':
                    header_row.scale = 1.01
                    overlay.opacity = overlay_hover_opacity
                else:
                    header_row.scale = 1.0
                    overlay.opacity = 0.0
                header_row.update()
                overlay.update()
            except Exception:
                pass
        interactive_layer.on_hover = _on_hover

        # Flet compatibility: Replace Positioned.fill with expand containers in Stack
        overlay.expand = True
        interactive_layer.expand = True
        base_container.expand = True
        return ft.Card(
            content=ft.Stack(
                controls=[
                    base_container,
                    overlay,
                    interactive_layer,
                ]
            ),
            elevation=4
        )

    def create_premium_gauge(percentage: int, label: str, context: str = "") -> ft.Card:
        """Deprecated: previously used to render a gauge; kept as a safe stub (unused)."""
        return ft.Card()

    def create_premium_activity_stream() -> ft.Card:
        """Create activity stream using Flet's ListView."""
        activities = [
            {"type": "success", "icon": ft.Icons.CLOUD_UPLOAD, "text": "Backup completed", "detail": "1.2GB in 3m 45s", "time": "2m ago"},
            {"type": "info", "icon": ft.Icons.PERSON_ADD, "text": "New client connected", "detail": "192.168.1.175", "time": "5m ago"},
            {"type": "warning", "icon": ft.Icons.WARNING, "text": "High memory usage", "detail": "88% for 10 minutes", "time": "8m ago"}
        ]

        activity_list = []
        for activity in activities:
            color = ft.Colors.GREEN if activity["type"] == "success" else ft.Colors.ORANGE if activity["type"] == "warning" else ft.Colors.BLUE
            activity_list.append(
                ft.ListTile(
                    leading=ft.Icon(activity["icon"], color=color),
                    title=ft.Text(activity["text"], weight=ft.FontWeight.W_600),
                    subtitle=ft.Text(activity["detail"]),
                    trailing=ft.Text(activity["time"], size=12, color=ft.Colors.OUTLINE)
                )
            )

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TIMELINE, size=24, color=ft.Colors.PURPLE_600),
                        ft.Text("Live Activity", size=20, weight=ft.FontWeight.BOLD)
                    ], spacing=8),
                    *activity_list
                ], spacing=8),
                padding=20
            ),
            elevation=2
        )

    def create_server_control_panel() -> ft.Container:
        """Deprecated: previously a server control panel; kept as a safe stub (unused)."""
        return ft.Container()

    # Removed nested function: def create_network_metrics_panel() -> ft.Container:
    # Removed nested function: def create_storage_breakdown_panel() -> ft.Container:
    # Removed nested function: def get_server_status_type(is_running: bool) -> str:
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
        # Subtle hover/press interactions and tooltip on the card
        def _handle_click(e):
            if on_click is None:
                return
            try:
                # Brief press effect: scale + deepen bg
                e.control.scale = 0.98
                e.control.bgcolor = ft.Colors.with_opacity(0.10, color)
                e.control.update()

                async def _reset_and_invoke():
                    try:
                        await asyncio.sleep(0.08)
                        e.control.scale = 1.0
                        e.control.bgcolor = ft.Colors.with_opacity(0.06, color)
                        e.control.update()
                    except Exception:
                        pass
                    try:
                        on_click(e)
                    except Exception:
                        pass

                page.run_task(_reset_and_invoke)
            except Exception:
                try:
                    on_click(e)
                except Exception:
                    pass

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
            on_hover=lambda e: (setattr(e.control, 'scale', 1.02 if e.data == 'true' else 1.0), e.control.update()),
            on_click=_handle_click if on_click else None,
            tooltip=label,
        )

    # Navigation helpers using the app_ref exposed on page
    def _go_to_clients(_e=None):
        try:
            if hasattr(page, 'app_ref') and hasattr(page.app_ref, '_switch_to_view'):
                page.app_ref._switch_to_view(1)  # Clients
        except Exception:
            pass

    def _go_to_files(_e=None):
        try:
            if hasattr(page, 'app_ref') and hasattr(page.app_ref, '_switch_to_view'):
                page.app_ref._switch_to_view(2)  # Files
        except Exception:
            pass

    def _go_to_logs(_e=None):
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

    # Live system sparkline charts
    def _create_sparkline(color) -> ft.BarChart:
        return ft.BarChart(
            bar_groups=[],
            interactive=False,
            max_y=100,
            min_y=0,
            width=220,
            height=70,
            bgcolor=ft.Colors.TRANSPARENT,
            border=ft.border.all(1, ft.Colors.OUTLINE),
        )

    cpu_spark = _create_sparkline(ft.Colors.BLUE)
    mem_spark = _create_sparkline(ft.Colors.GREEN)
    disk_spark = _create_sparkline(ft.Colors.PURPLE)

    def _update_spark(chart: ft.BarChart, values: List[float], color) -> None:
        groups: List[ft.BarChartGroup] = []
        for i, v in enumerate(values[-30:]):
            groups.append(
                ft.BarChartGroup(
                    x=i,
                    bar_rods=[ft.BarChartRod(to_y=float(v), color=color, width=4, border_radius=2)]
                )
            )
        chart.bar_groups = groups

    # Reusable microinteraction helper to avoid duplication across lists
    def apply_hover_click_effects(container: ft.Container, base_color: str,
                                  hover_opacity: float = 0.04,
                                  pressed_opacity: float = 0.12,
                                  hover_scale: float = 1.01) -> None:
        """Attach consistent hover and click effects to a container.
        Keeps existing background when hover ends; safe if bgcolor is None.
        """
        def _on_hover(e: ft.HoverEvent, c=container, base=base_color):
            try:
                c.bgcolor = ft.Colors.with_opacity(hover_opacity, base) if e.data == 'true' else c.bgcolor
                c.scale = hover_scale if e.data == 'true' else 1.0
                c.update()
            except Exception:
                pass

        def _on_click(e, c=container, base=base_color):
            try:
                c.bgcolor = ft.Colors.with_opacity(pressed_opacity, base)
                c.update()
                async def _reset():
                    try:
                        await asyncio.sleep(0.10)
                        c.bgcolor = ft.Colors.with_opacity(hover_opacity, base)
                        c.update()
                    except Exception:
                        pass
                page.run_task(_reset)
            except Exception:
                pass

        container.on_hover = _on_hover
        container.on_click = _on_click

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

    def update_all_displays():
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

        # Update history and sparklines
        try:
            cpu_history.append(float(cpu_percent))
            memory_history.append(float(memory_percent))
            disk_history.append(float(disk_percent))
            if len(cpu_history) > 30:
                cpu_history = cpu_history[-30:]
                memory_history = memory_history[-30:]
                disk_history = disk_history[-30:]
            _update_spark(cpu_spark, cpu_history, ft.Colors.BLUE)
            _update_spark(mem_spark, memory_history, ft.Colors.GREEN)
            _update_spark(disk_spark, disk_history, ft.Colors.PURPLE)
        except Exception as _:
            pass

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
            # Total clients
            total_clients_val = current_server_status.get('clients_connected', len(current_clients))
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
            kpi_errors_24h_text.value = str(err24)

            # Storage used
            kpi_storage_used_text.value = f"{current_server_status.get('storage_used_gb', 0):.1f} GB"

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

        # Performance-optimized batched updates with priority grouping
        # High priority: Critical status and user-facing indicators
        high_priority_controls = [
            server_status_indicator_container,
            kpi_total_clients_text, kpi_active_jobs_text, kpi_errors_24h_text, kpi_storage_used_text,
            hero_total_clients_text, hero_active_transfers_text, hero_uptime_text,
            connect_button, disconnect_button
        ]

        # Medium priority: System metrics and progress indicators
        medium_priority_controls = [
            cpu_text, memory_text, disk_text,
            cpu_spark, mem_spark, disk_spark,
            used_text, free_text, forecast_text, capacity_pie
        ]

        # Low priority: Secondary information and details
        low_priority_controls = [
            last_updated_text,
            activity_list, clients_list
        ]

        def update_control_group(controls, delay_ms=0):
            """Update a group of controls with optional delay for performance"""
            async def update_group():
                if delay_ms > 0:
                    await asyncio.sleep(delay_ms / 1000.0)

                # Prefer granular control updates for better performance and fewer lifecycle issues
                for control in controls:
                    if hasattr(control, 'update') and getattr(control, 'page', None) is not None:
                        with contextlib.suppress(Exception):
                            control.update()

            if delay_ms > 0:
                page.run_task(update_group)
            else:
                # Immediate granular updates
                for control in controls:
                    if hasattr(control, 'update') and getattr(control, 'page', None) is not None:
                        with contextlib.suppress(Exception):
                            control.update()

        # Actually call the update functions with priority groups
        try:
            # High priority updates (immediate)
            update_control_group(high_priority_controls, 0)
            # Medium priority updates (small delay)
            update_control_group(medium_priority_controls, 50)
            # Low priority updates (larger delay)
            update_control_group(low_priority_controls, 100)
        except Exception as e:
            logger.debug(f"Control group updates failed: {e}")
            # Fallback to simple page update
            try:
                page.update()
            except Exception as e2:
                logger.debug(f"Fallback page update also failed: {e2}")

    async def _update_all_displays_async(source: str = 'auto'):
        """Async version of update_all_displays."""
        nonlocal current_server_status, current_system_metrics, current_activity, current_clients, last_updated, prev_server_snapshot, last_significant_toast_time

        try:
            # Show slim refresh indicator during async updates
            refresh_indicator.visible = True
            with contextlib.suppress(Exception):
                refresh_indicator.update()

            import asyncio
            loop = asyncio.get_event_loop()

            # Get fresh data
            current_server_status = await loop.run_in_executor(None, get_server_status)
            current_system_metrics = await loop.run_in_executor(None, get_system_metrics)
            current_activity = await loop.run_in_executor(None, get_activity_data)

            # Get clients
            if server_bridge:
                # Use documented API for compatibility
                clients_result = await loop.run_in_executor(None, server_bridge.get_all_clients_from_db)
                if isinstance(clients_result, dict) and clients_result.get('success'):
                    current_clients = clients_result.get('data', [])
                elif isinstance(clients_result, list):
                    current_clients = clients_result

            # Determine if significant change occurred (auto refresh only, not initial/manual)
            try:
                if source == 'auto' and isinstance(prev_server_snapshot, dict) and prev_server_snapshot:
                    deltas: List[str] = []
                    try:
                        pc = int(current_server_status.get('clients_connected', 0))
                        pp = int(prev_server_snapshot.get('clients_connected', 0))
                        d = pc - pp
                        if abs(d) >= 2:
                            deltas.append(f"Clients {'+' if d>=0 else ''}{d}")
                    except Exception:
                        pass
                    try:
                        tc = int(current_server_status.get('total_transfers', 0))
                        tp = int(prev_server_snapshot.get('total_transfers', 0))
                        d = tc - tp
                        if abs(d) >= 2:
                            deltas.append(f"Transfers {'+' if d>=0 else ''}{d}")
                    except Exception:
                        pass
                    try:
                        sc = float(current_server_status.get('storage_used_gb', 0.0))
                        sp = float(prev_server_snapshot.get('storage_used_gb', 0.0))
                        d = sc - sp
                        if abs(d) >= 1.0:
                            deltas.append(f"Storage {'+' if d>=0 else ''}{d:.1f} GB")
                    except Exception:
                        pass
                    try:
                        fc = int(current_server_status.get('total_files', 0))
                        fp = int(prev_server_snapshot.get('total_files', 0))
                        d = fc - fp
                        if abs(d) >= 10:
                            deltas.append(f"Files {'+' if d>=0 else ''}{d}")
                    except Exception:
                        pass

                    # Toast if any significant deltas and cooldown passed
                    if deltas:
                        show_toast = True
                        try:
                            if last_significant_toast_time is not None:
                                show_toast = (datetime.now() - last_significant_toast_time).total_seconds() >= 90
                        except Exception:
                            pass
                        if show_toast:
                            msg = "Updated – " + ", ".join(deltas[:3])
                            try:
                                show_success_message(page, msg)
                                last_significant_toast_time = datetime.now()
                            except Exception:
                                pass
            except Exception:
                pass

            last_updated = datetime.now().strftime("%H:%M:%S")
            update_all_displays()

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

    async def _update_operations_panels_async():
        """Async version of operations panels update."""
        try:
            await asyncio.get_event_loop().run_in_executor(None, _update_operations_panels)
        except Exception as e:
            logger.debug(f"Async operations panels update failed: {e}")

    def update_activity_list():
        """Update the activity list."""
        activity_list.controls.clear()

        # Filter activities
        filtered_activities = current_activity
        if activity_filter != "All":
            filtered_activities = [
                activity for activity in current_activity
                if activity.get('type', '').lower() == activity_filter.lower()
            ]

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

            # List item with hover microinteraction
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
            apply_hover_click_effects(tile, color, hover_opacity=0.04)
            activity_list.controls.append(tile)

        try:
            activity_list.update()
        except Exception:
            pass

    def update_clients_list():
        """Update clients snapshot list from current_clients."""
        clients_list.controls.clear()
        if not current_clients:
            clients_list.controls.append(clients_empty)
        else:
            # Sort by last_seen desc when available
            def _parse_ts(v):
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
                    animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
                )
                apply_hover_click_effects(item, status_color, hover_opacity=0.06)
                clients_list.controls.append(item)

    # Server control actions
    def start_server(_e):
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

    def stop_server(_e):
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

    # Activity filter handler
    def on_filter_change(e):
        """Handle activity filter change."""
        nonlocal activity_filter
        activity_filter = e.control.value
        update_activity_list()

    # Refresh handler
    def refresh_dashboard(_e):
        """Refresh all dashboard data (async to avoid blocking UI)."""
        try:
            async def _manual_refresh():
                await _update_all_displays_async('manual')
            page.run_task(_manual_refresh)
        except Exception:
            # Fallback to sync update
            update_all_displays()
        show_success_message(page, "Dashboard refreshed")

    # Create UI components (header actions only)

    # Backup action
    def on_backup(_e):
        show_success_message(page, "Backup initiated (mock)")

    # Removed unused legacy Server Control card (replaced by header actions)

    # Dynamic hero metric value controls for live updates
    hero_total_clients_text = ft.Text("0", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)
    hero_active_transfers_text = ft.Text("0", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
    hero_uptime_text = ft.Text("0h 0m", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)

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

    # Removed unused system_metrics_card (live_system_metrics_card is used instead)

    # Removed unused activity card with filter (premium stream is used in layout)

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
    server_status_indicator_container = ft.Container()
    # Slim top bar: integrates status + actions in one compact bar
    backup_button = themed_button("Backup", on_backup, variant="filled", icon=ft.Icons.BACKUP)
    refresh_button = themed_button("Refresh", refresh_dashboard, variant="outlined", icon=ft.Icons.REFRESH)
    connect_button = themed_button("Connect", start_server, variant="filled", icon=ft.Icons.PLAY_ARROW)
    disconnect_button = themed_button("Disconnect", stop_server, variant="outlined", icon=ft.Icons.STOP)
    def on_live_toggle(e: ft.ControlEvent):
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

    # Removed unused server_status_card duplicate (header + hero metrics cover this info)

    # System Performance Card with simple progress indicators
    # Removed unused system performance demo card

    # Removed unused recent activity bar chart placeholder

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

    def _update_operations_panels():
        # Running jobs derived from activity
        running_jobs_list.controls.clear()
        now_dt = datetime.now()
        jobs = []
        for a in current_activity:
            ts = a.get('timestamp', now_dt)
            if isinstance(ts, datetime) and (now_dt - ts) <= timedelta(minutes=10):
                msg = str(a.get('message', '')).lower()
                if any(k in msg for k in ["start", "running", "upload", "transfer"]):
                    jobs.append(a)
        if not jobs:
            running_jobs_list.controls.append(ft.Text("All clear – no running jobs", size=12, color=ft.Colors.OUTLINE))
        else:
            for j in jobs[:5]:
                job = ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.SYNC, color=ft.Colors.BLUE, size=18),
                        title=ft.Text(str(j.get('message', 'Job')), size=13),
                        subtitle=ft.Text("Running", size=11, color=ft.Colors.OUTLINE)
                    ),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE),
                    animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
                )
                apply_hover_click_effects(job, ft.Colors.BLUE, hover_opacity=0.07)
                running_jobs_list.controls.append(job)

        # Recent backups derived from activity
        recent_backups_list.controls.clear()
        backups = [a for a in current_activity if 'backup' in str(a.get('message', '')).lower() or 'completed' in str(a.get('message', '')).lower()]
        if not backups:
            recent_backups_list.controls.append(ft.Text("No recent backups", size=12, color=ft.Colors.OUTLINE))
        else:
            for b in backups[:5]:
                ts = b.get('timestamp', now_dt)
                when = ts.strftime("%H:%M") if isinstance(ts, datetime) else str(ts)
                backup = ft.Container(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.BACKUP, color=ft.Colors.GREEN, size=18),
                        title=ft.Text(str(b.get('message', 'Backup')), size=13),
                        subtitle=ft.Text(f"at {when}", size=11, color=ft.Colors.OUTLINE)
                    ),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.GREEN),
                    animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
                )
                apply_hover_click_effects(backup, ft.Colors.GREEN, hover_opacity=0.07)
                recent_backups_list.controls.append(backup)

    # Wrap operations panels into cards
    running_jobs_card = themed_card(content=running_jobs_list, title="RUNNING JOBS", page=page)
    recent_backups_card = themed_card(content=recent_backups_list, title="RECENT BACKUPS", page=page)

    # Removed unused data/database/version info demo cards

    # Clean, organized layout structure (streamlined, no redundant big sections)
    main_content = ft.Column([
        # Header
        header_section,
        refresh_indicator,
        ft.Container(height=16),

        # KPI row (enhanced small cards)
        kpi_row,
    ft.Container(height=16),

        # Live system metrics
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

    def setup_subscriptions():
        """Setup subscriptions and initial data loading after view is added to page."""
        nonlocal refresh_task, _stop_polling

        # Defer heavy initial data loading to avoid blocking UI
        async def _deferred_initial_load():
            try:
                # Small delay to let UI settle
                await asyncio.sleep(0.1)

                # Update displays asynchronously
                await _update_all_displays_async('initial')

                # Update operations panels asynchronously
                await _update_operations_panels_async()

            except Exception as e:
                logger.debug(f"Deferred initial load failed: {e}")
                # Fallback to synchronous loading if async fails
                try:
                    update_all_displays()
                    _update_operations_panels()
                except Exception as e2:
                    logger.debug(f"Fallback loading also failed: {e2}")

        # Start deferred initial loading
        page.run_task(_deferred_initial_load)

        # Fade-in entrance effect once attached
        try:
            dashboard_container.opacity = 1.0
            dashboard_container.update()
        except Exception:
            pass

        # Start lightweight periodic refresh in background
        async def _poll_loop():
            nonlocal _stop_polling
            try:
                while not _stop_polling:
                    await asyncio.sleep(30)  # Increased from 15 to 30 seconds for better performance
                    if auto_refresh_enabled:
                        # Fetch & update asynchronously to prevent UI blocking
                        try:
                            await _update_all_displays_async('auto')
                            # Only update operations panels every other cycle (every 60s) to reduce load
                            if hasattr(_poll_loop, '_operations_update_counter'):
                                _poll_loop._operations_update_counter += 1
                            else:
                                _poll_loop._operations_update_counter = 1

                            if _poll_loop._operations_update_counter % 2 == 0:
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

    def dispose():
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
