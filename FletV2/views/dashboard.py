#!/usr/bin/env python3
"""Professional Matte Dashboard - Compact, Clickable, Auto-Refreshing.

Production-ready dashboard with:
- Auto-refresh loop (10-second interval)
- Connection status indicator
- Clickable metric cards
- Proper exception handling
- Last-updated timestamp
"""

from __future__ import annotations

import asyncio
import datetime
import logging
from typing import Any, Callable, Coroutine

import flet as ft

try:
    import psutil

    _PSUTIL_AVAILABLE = True
except ImportError:
    psutil = None  # type: ignore[assignment]
    _PSUTIL_AVAILABLE = False

import base64

from utils.helpers import format_relative_timestamp, get_disk_usage
from utils.ui_components import (
    ActivityItem,
    DiskUsageBar,
    HealthGaugeWithTooltip,
    create_matte_card,
    safe_update_control,
)

# Setup logger
logger = logging.getLogger(__name__)

# ============================================================================
# SPARKLINE SVG GENERATOR
# ============================================================================


def generate_sparkline_svg(
    data: list[float], color_hex: str, width: int = 100, height: int = 50
) -> str:
    """Generate a base64 encoded SVG sparkline."""
    if not data:
        # Return a blank SVG or a default line if no data
        svg = f"""
        <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
            <polyline points="0,{height / 2} {width},{height / 2}" fill="none" stroke="{color_hex}" stroke-width="1" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """
        return base64.b64encode(svg.encode("utf-8")).decode("utf-8")

    # Normalize data to height
    # Assume data is 0-100
    points = []
    step_x = width / (len(data) - 1) if len(data) > 1 else width

    # Add padding to prevent stroke clipping
    padding = 4
    draw_height = height - (padding * 2)

    for i, val in enumerate(data):
        x = i * step_x
        # Invert Y (SVG 0 is top)
        y = padding + draw_height - (val / 100 * draw_height)
        points.append(f"{x:.1f},{y:.1f}")

    polyline_points = " ".join(points)

    # Area path (close layout)
    area_points = f"0,{height} {polyline_points} {width},{height}"

    # Gradient ID must be unique
    gradient_id = f"grad_{color_hex.replace('#', '')}"

    svg = f"""
    <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <linearGradient id="{gradient_id}" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" style="stop-color:{color_hex};stop-opacity:0.3" />
                <stop offset="100%" style="stop-color:{color_hex};stop-opacity:0" />
            </linearGradient>
        </defs>
        <path d="M {area_points} Z" fill="url(#{gradient_id})" stroke="none"/>
        <polyline points="{polyline_points}" fill="none" stroke="{color_hex}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    """

    return base64.b64encode(svg.encode("utf-8")).decode("utf-8")


# ============================================================================
# SYSTEM STAT CARD (CPU/Memory)
# ============================================================================


def _create_stat_card(
    title: str,
    value_ref: ft.Ref[ft.Text],
    chart_ref: ft.Ref[ft.Image],
    color_hex: str,
    unavailable_ref: ft.Ref[ft.Text] | None = None,
) -> ft.Container:
    """Premium matte stat card with squircle shape and subtle glow."""

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            title,
                            size=10,
                            weight=ft.FontWeight.W_600,
                            color="#94A3B8",  # Slate-400
                        ),
                        ft.Text(
                            "--%",
                            size=20,
                            weight=ft.FontWeight.W_700,
                            color="#F1F5F9",  # Slate-100
                            ref=value_ref,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Unavailable notice (hidden by default)
                ft.Text(
                    "",
                    size=10,
                    color="#94A3B8",
                    italic=True,
                    ref=unavailable_ref,
                    visible=False,
                )
                if unavailable_ref
                else ft.Container(),
                # Chart Container
                ft.Container(
                    content=ft.Image(
                        src=f"data:image/svg+xml;base64,{generate_sparkline_svg([0] * 20, color_hex)}",
                        fit="fill",
                        ref=chart_ref,
                    ),
                    height=60,
                    expand=True,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    border_radius=8,
                ),
            ],
            spacing=8,
        ),
        bgcolor="#1E293B",  # Slate-800 - matte background
        border=ft.border.all(1, "#334155"),  # Slate-700
        border_radius=16,  # Rounded corners (consistent with matte cards)
        padding=16,
        expand=True,
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=12,
            color=ft.Colors.with_opacity(0.2, color_hex),  # Colored glow
            offset=ft.Offset(0, 3),
        ),
    )


# ============================================================================
# ACTIVITY PANEL
# ============================================================================


def _create_activity_panel(
    navigate_callback: Callable | None,
    list_view_ref: ft.Ref[ft.ListView],
    filter_callback: Callable[[str], None] | None = None,
) -> ft.Container:
    """Premium matte activity panel with glassmorphism and filtering."""

    def on_filter_change(e):
        if filter_callback:
            filter_callback(e.control.label.value.lower())

    filter_row = ft.Row(
        [
            ft.Chip(
                label=ft.Text("All"),
                on_click=on_filter_change,
                selected=True,
                show_checkmark=False,
                bgcolor=ft.Colors.with_opacity(0.1, "#38BDF8"),
            ),
            ft.Chip(
                label=ft.Text("Success"),
                on_click=on_filter_change,
                show_checkmark=False,
            ),
            ft.Chip(
                label=ft.Text("Warning"),
                on_click=on_filter_change,
                show_checkmark=False,
            ),
            ft.Chip(
                label=ft.Text("Error"),
                on_click=on_filter_change,
                show_checkmark=False,
            ),
        ],
        spacing=8,
        scroll=ft.ScrollMode.HIDDEN,
    )

    return ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Text(
                            "RECENT ACTIVITY",
                            size=10,
                            weight=ft.FontWeight.W_600,
                            color="#94A3B8",  # Slate-400
                        ),
                        ft.OutlinedButton(
                            "View All",
                            icon=ft.Icons.ARROW_FORWARD,
                            style=ft.ButtonStyle(
                                color="#38BDF8",  # Cyan accent
                                side=ft.BorderSide(
                                    1, ft.Colors.with_opacity(0.3, "#38BDF8")
                                ),
                                padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                            on_click=lambda _: navigate_callback("logs")
                            if navigate_callback
                            else None,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                ft.Divider(height=1, color="#334155"),
                ft.Container(height=4),
                filter_row,
                ft.Container(height=4),
                # Activity List with default empty state
                ft.ListView(
                    ref=list_view_ref,
                    controls=[
                        # Default empty state (replaced when data loads)
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Icon(
                                        ft.Icons.INBOX_OUTLINED,
                                        size=48,
                                        color="#475569",
                                    ),
                                    ft.Text(
                                        "No recent activity",
                                        size=14,
                                        weight=ft.FontWeight.W_500,
                                        color="#64748B",
                                    ),
                                    ft.Text(
                                        "Activity will appear here when actions occur",
                                        size=11,
                                        color="#475569",
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=8,
                            ),
                            alignment=ft.Alignment(0, 0),
                            expand=True,
                            padding=24,
                        ),
                    ],
                    expand=True,
                    spacing=0,
                    padding=0,
                ),
            ],
            spacing=4,
        ),
        bgcolor="#1E293B",  # Slate-800 - matte background
        border=ft.border.all(1, "#334155"),  # Slate-700
        border_radius=16,  # Rounded corners (consistent with matte cards)
        padding=ft.Padding.all(16),
        blur=ft.Blur(10, 10, ft.BlurTileMode.REPEATED),  # Glass effect
        expand=True,
    )


# ============================================================================
# CONNECTION STATUS BADGE
# ============================================================================


# ============================================================================
# DASHBOARD VIEW
# ============================================================================


def create_dashboard_view(
    server_bridge: Any | None,
    page: ft.Page,
    _state_manager: Any | None,
    navigate_callback: Callable[[str], None] | None = None,
    update_status_callback: Callable[[bool], None] | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    """Create the dashboard view - compact, clickable, auto-refreshing.

    Returns:
        tuple: (content, cleanup_function, load_data_function)
    """

    # Refs for dynamic updates
    clients_value_ref = ft.Ref[ft.Text]()
    clients_subtext_ref = ft.Ref[ft.Text]()
    conn_value_ref = ft.Ref[ft.Text]()
    conn_subtext_ref = ft.Ref[ft.Text]()
    files_value_ref = ft.Ref[ft.Text]()
    files_subtext_ref = ft.Ref[ft.Text]()
    uptime_value_ref = ft.Ref[ft.Text]()
    uptime_subtext_ref = ft.Ref[ft.Text]()

    # Metric chart refs
    cpu_value_ref = ft.Ref[ft.Text]()
    cpu_chart_ref = ft.Ref[ft.Image]()
    cpu_unavailable_ref = ft.Ref[ft.Text]()

    mem_value_ref = ft.Ref[ft.Text]()
    mem_chart_ref = ft.Ref[ft.Image]()
    mem_unavailable_ref = ft.Ref[ft.Text]()

    # Disk usage ref
    disk_container_ref = ft.Ref[ft.Container]()

    # Activity list ref
    activity_list_ref = ft.Ref[ft.ListView]()

    # Health gauge ref
    health_gauge_ref = ft.Ref[ft.Stack]()

    # Status indicator is now global in main.py

    # Last updated ref
    last_updated_ref = ft.Ref[ft.Text]()

    # Hex colors for SVG
    COLOR_PRIMARY_HEX = "#38BDF8"
    COLOR_SECONDARY_HEX = "#A78BFA"

    # Refresh state
    _refresh_active = True

    # Navigation handlers for cards
    def go_to_clients(_):
        if navigate_callback:
            navigate_callback("clients")

    def go_to_files(_):
        if navigate_callback:
            navigate_callback("files")

    def go_to_logs(_):
        if navigate_callback:
            navigate_callback("logs")

    def go_to_settings(_):
        if navigate_callback:
            navigate_callback("settings")

    # Metrics Row - cards naturally align via Row's cross-axis alignment
    metrics_row = ft.Row(
        [
            create_matte_card(
                title="CLIENTS",
                icon=ft.Icons.PEOPLE_OUTLINE,
                accent_color=ft.Colors.PRIMARY,
                value_control=ft.Text(
                    "0", size=28, weight=ft.FontWeight.BOLD, ref=clients_value_ref
                ),
                subtext_control=ft.Text(
                    "Connected",
                    size=11,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    ref=clients_subtext_ref,
                ),
                on_click=go_to_clients,
            ),
            create_matte_card(
                title="ACTIVE TRANSFERS",
                icon=ft.Icons.WIFI,
                accent_color=ft.Colors.SECONDARY,
                value_control=ft.Text(
                    "0", size=28, weight=ft.FontWeight.BOLD, ref=conn_value_ref
                ),
                subtext_control=ft.Text(
                    "Transfers",
                    size=11,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    ref=conn_subtext_ref,
                ),
                on_click=go_to_logs,
            ),
            create_matte_card(
                title="FILES",
                icon=ft.Icons.FOLDER_OUTLINED,
                accent_color=ft.Colors.GREEN,
                value_control=ft.Text(
                    "0", size=28, weight=ft.FontWeight.BOLD, ref=files_value_ref
                ),
                subtext_control=ft.Text(
                    "Stored",
                    size=11,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    ref=files_subtext_ref,
                ),
                on_click=go_to_files,
            ),
            create_matte_card(
                title="UPTIME",
                icon=ft.Icons.TIMER_OUTLINED,
                accent_color=ft.Colors.ORANGE,
                value_control=ft.Text(
                    "0h 0m", size=28, weight=ft.FontWeight.BOLD, ref=uptime_value_ref
                ),
                subtext_control=ft.Text(
                    "Online",
                    size=11,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    ref=uptime_subtext_ref,
                ),
                on_click=go_to_settings,
            ),
            # Health Gauge Card - styled to match other matte cards with accent bar
            ft.Container(
                content=ft.Column(
                    [
                        # Accent bar (same approach as matte cards)
                        ft.Container(
                            height=2,
                            bgcolor="#10B981",
                            border_radius=ft.border_radius.only(
                                top_left=14, top_right=14
                            ),
                            margin=ft.margin.only(
                                left=-16, right=-16, top=-12, bottom=8
                            ),
                        ),
                        ft.Row(
                            [
                                ft.Text(
                                    "SYSTEM HEALTH",
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color="#94A3B8",
                                ),
                                ft.Icon(
                                    ft.Icons.MONITOR_HEART_OUTLINED,
                                    size=20,
                                    color="#10B981",
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Container(
                            content=HealthGaugeWithTooltip(100),
                            ref=health_gauge_ref,
                            alignment=ft.Alignment(0, 0),
                        ),
                    ],
                    spacing=4,
                ),
                bgcolor="#1E293B",
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_CENTER,
                    end=ft.Alignment.BOTTOM_CENTER,
                    colors=["#1E293B", "#0F172A"],
                ),
                border=ft.border.all(
                    1, "#334155"
                ),  # Uniform border (keeps border_radius working)
                border_radius=16,
                padding=ft.padding.only(left=16, right=16, top=12, bottom=8),
                expand=True,
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=16,
                    color=ft.Colors.with_opacity(0.15, "#10B981"),
                    offset=ft.Offset(0, 4),
                ),
            ),
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.START,  # Align to top (reverted from STRETCH)
    )

    # Make all cards expand equally within the row
    for control in metrics_row.controls:
        control.expand = True

    # Activity log state
    _current_filter = "all"

    def on_activity_filter(filter_name: str):
        nonlocal _current_filter
        _current_filter = filter_name
        page.run_task(load_dashboard_data)  # Immediate refresh

    # Bottom Row: Activity Panel (left) + Stats Column (right)
    activity_panel = _create_activity_panel(
        navigate_callback, activity_list_ref, filter_callback=on_activity_filter
    )

    # Make charts interactive - clicking navigates to Analytics
    def go_to_analytics(_):
        if navigate_callback:
            navigate_callback("analytics")

    cpu_stat_card = _create_stat_card(
        "CPU USAGE",
        cpu_value_ref,
        cpu_chart_ref,
        COLOR_PRIMARY_HEX,
        cpu_unavailable_ref,
    )
    mem_stat_card = _create_stat_card(
        "MEMORY",
        mem_value_ref,
        mem_chart_ref,
        COLOR_SECONDARY_HEX,
        mem_unavailable_ref,
    )

    # Wrap in GestureDetector for click-to-navigate
    cpu_clickable = ft.GestureDetector(
        content=cpu_stat_card,
        on_tap=go_to_analytics,
        mouse_cursor=ft.MouseCursor.CLICK,
    )
    mem_clickable = ft.GestureDetector(
        content=mem_stat_card,
        on_tap=go_to_analytics,
        mouse_cursor=ft.MouseCursor.CLICK,
    )

    # Initial disk usage (will be updated in load_dashboard_data)
    initial_disk = get_disk_usage()
    disk_bar = ft.Container(
        content=DiskUsageBar(
            percent=initial_disk.get("percent", 0),
            formatted_used=initial_disk.get("formatted_used", "N/A"),
            formatted_total=initial_disk.get("formatted_total", "N/A"),
        ),
        ref=disk_container_ref,
    )

    # Stats column - direct layout without container wrapping
    stats_column = ft.Column(
        [
            cpu_clickable,
            mem_clickable,
            disk_bar,
        ],
        spacing=12,
        expand=True,
    )

    # Bottom row layout
    bottom_row = ft.Row(
        [
            ft.Container(content=activity_panel, expand=2),
            ft.Container(content=stats_column, expand=1),
        ],
        spacing=12,
        expand=True,
        vertical_alignment=ft.CrossAxisAlignment.START,  # Reverted from STRETCH
    )

    # Manual refresh handler
    def on_manual_refresh(_):
        page.run_task(load_dashboard_data)

    # Footer with refresh button and last updated (status moved to top bar)
    footer_row = ft.Row(
        [
            ft.Container(expand=True),  # Spacer
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh Now",
                icon_size=16,
                icon_color="#64748B",  # Slate-500
                on_click=on_manual_refresh,
            ),
            ft.Text(
                "Last updated: --:--:--",
                size=10,
                color=ft.Colors.ON_SURFACE_VARIANT,
                ref=last_updated_ref,
            ),
        ],
        alignment=ft.MainAxisAlignment.END,
        spacing=8,
    )

    # Main Layout - NO SCROLL, fits viewport
    # Wrapped in a Row/Center to respect max_width if screen is huge
    # Main Layout - NO SCROLL, fits viewport
    content = ft.Container(
        content=ft.Column(
            [
                metrics_row,
                ft.Container(height=12),
                bottom_row,
                ft.Container(height=8),
                footer_row,
            ],
            expand=True,
            spacing=0,
        ),
        padding=16,
        expand=True,
    )

    # Data state
    cpu_history: list[float] = [0.0] * 20
    mem_history: list[float] = [0.0] * 20

    def _update_connection_status(connected: bool):
        """Update the global connection status via callback."""
        if update_status_callback:
            update_status_callback(connected)

    async def load_dashboard_data():
        """Update dashboard with live data."""
        nonlocal cpu_history, mem_history

        is_connected = False

        if server_bridge:
            try:
                # 1. Server Status
                status = server_bridge.get_server_status()
                is_connected = True

                if clients_value_ref.current:
                    clients_value_ref.current.value = str(
                        status.get("clients_connected", 0)
                    )
                    safe_update_control(clients_value_ref.current)

                if conn_value_ref.current:
                    conn_value_ref.current.value = str(status.get("total_transfers", 0))
                    safe_update_control(conn_value_ref.current)

                if files_value_ref.current:
                    total = status.get("total_files", 0)
                    files_value_ref.current.value = (
                        f"{total / 1000:.1f}k" if total > 1000 else str(total)
                    )
                    safe_update_control(files_value_ref.current)

                if uptime_value_ref.current:
                    uptime = status.get("uptime_seconds", 0)
                    days = uptime // 86400
                    hours = (uptime % 86400) // 3600
                    minutes = (uptime % 3600) // 60

                    if days > 0:
                        uptime_value_ref.current.value = f"{days}d {hours}h"
                    else:
                        uptime_value_ref.current.value = f"{hours}h {minutes}m"
                    safe_update_control(uptime_value_ref.current)

                # 2. Activity Logs
                try:
                    logs = server_bridge.get_logs()  # Returns list[dict]
                    if activity_list_ref.current:
                        if not logs:
                            activity_list_ref.current.controls = [
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Icon(
                                                ft.Icons.HOURGLASS_EMPTY,
                                                size=32,
                                                color="#475569",  # Slate-600
                                            ),
                                            ft.Text(
                                                "All quiet on the bridge",
                                                size=13,
                                                weight=ft.FontWeight.W_500,
                                                color="#64748B",  # Slate-500
                                            ),
                                            ft.Text(
                                                "Activity will appear here",
                                                size=11,
                                                color="#475569",  # Slate-600
                                            ),
                                            ft.Container(height=8),
                                            ft.FilledButton(
                                                "Start a Backup",
                                                icon=ft.Icons.CLOUD_UPLOAD,
                                                on_click=go_to_files,
                                                style=ft.ButtonStyle(
                                                    bgcolor="#334155",
                                                    color="#94A3B8",
                                                ),
                                            ),
                                        ],
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        spacing=6,
                                    ),
                                    alignment=ft.Alignment(0, 0),
                                    expand=True,
                                    padding=24,
                                )
                            ]
                        else:
                            # Filter based on _current_filter
                            filtered_logs = logs
                            if _current_filter != "all":
                                filtered_logs = [
                                    log_item
                                    for log_item in logs
                                    if log_item.get("level", "info").lower()
                                    == _current_filter
                                ]

                            # Limit to 5-6 items
                            recent = (
                                filtered_logs[:6]
                                if len(filtered_logs) > 6
                                else filtered_logs
                            )
                            new_controls = []
                            for log in recent:
                                level = log.get("level", "info").lower()

                                color = "#38BDF8"  # Default blue
                                icon_name = ft.Icons.INFO_OUTLINE

                                if level == "error":
                                    color = "#EF4444"
                                    icon_name = ft.Icons.ERROR_OUTLINE
                                elif level == "warning":
                                    color = "#F59E0B"
                                    icon_name = ft.Icons.WARNING_AMBER
                                elif level == "success":
                                    color = "#10B981"
                                    icon_name = ft.Icons.CHECK_CIRCLE_OUTLINE

                                # Format time - use relative format
                                time_str = format_relative_timestamp(
                                    log.get("timestamp", "")
                                )

                                new_controls.append(
                                    ActivityItem(
                                        title=log.get("message", "Activity"),
                                        subtitle=log.get("source", "System"),
                                        icon=icon_name,
                                        color=color,
                                        timestamp=time_str,
                                    )
                                )
                            activity_list_ref.current.controls = new_controls

                        safe_update_control(activity_list_ref.current)

                except Exception as log_err:
                    logger.warning(f"Log fetch error: {log_err}")

            except Exception as e:
                logger.warning(f"Dashboard metrics error: {e}")
                is_connected = False

        # Update connection status
        _update_connection_status(is_connected)

        # 3. System Stats (CPU/Mem)
        if _PSUTIL_AVAILABLE and psutil is not None:
            try:
                # CPU
                cpu = psutil.cpu_percent(interval=None)
                cpu_history.append(float(cpu))
                cpu_history.pop(0)

                if cpu_value_ref.current:
                    cpu_value_ref.current.value = f"{cpu:.0f}%"
                    safe_update_control(cpu_value_ref.current)

                if cpu_chart_ref.current:
                    # Update SVG
                    cpu_chart_ref.current.src = f"data:image/svg+xml;base64,{generate_sparkline_svg(cpu_history, COLOR_PRIMARY_HEX)}"
                    safe_update_control(cpu_chart_ref.current)

                # MEMORY
                mem = psutil.virtual_memory().percent
                mem_history.append(float(mem))
                mem_history.pop(0)

                if mem_value_ref.current:
                    mem_value_ref.current.value = f"{mem:.0f}%"
                    safe_update_control(mem_value_ref.current)

                if mem_chart_ref.current:
                    mem_chart_ref.current.src = f"data:image/svg+xml;base64,{generate_sparkline_svg(mem_history, COLOR_SECONDARY_HEX)}"
                    safe_update_control(mem_chart_ref.current)

                # DISK USAGE
                if disk_container_ref.current:
                    disk_data = get_disk_usage()
                    # Re-create content but we need to be careful not to destroy the wrapper?
                    # Actually, disk_container_ref is the content of the card.
                    # DiskUsageBar returns a container.
                    disk_container_ref.current.content = DiskUsageBar(
                        percent=disk_data.get("percent", 0),
                        formatted_used=disk_data.get("formatted_used", "N/A"),
                        formatted_total=disk_data.get("formatted_total", "N/A"),
                    )
                    safe_update_control(disk_container_ref.current)

            except Exception as e:
                logger.warning(f"System stats error: {e}")

        # 4. Update Health Gauge (Simplified logic)
        if health_gauge_ref.current:
            cpu_val = cpu_history[-1] if cpu_history else 0
            mem_val = mem_history[-1] if mem_history else 0
            health = 100 - (cpu_val * 0.4 + mem_val * 0.4)
            if not is_connected:
                health -= 20
            health = max(0, min(100, health))

            # Replace the entire Tooltip with updated health value
            # Structure: Container -> Tooltip -> Stack
            try:
                # We need to target the proper ref. health_gauge_ref was likely attached
                # to the content of the manual container.
                # In the new Matte Card, we didn't attach a ref to the content container directly?
                # Wait, in the create_matte_card call above, we passed a Container as content.
                # We need to make sure we can update it.
                # The health_gauge_ref needs to be attached to the inner HealthGaugeWithTooltip
                # But HealthGaugeWithTooltip returns a Container.

                # Update health gauge with current health value
                if health_gauge_ref.current:
                    health_gauge_ref.current.content = HealthGaugeWithTooltip(health)
                    safe_update_control(health_gauge_ref.current)
            except Exception as gauge_err:
                logger.debug(f"Health gauge update error: {gauge_err}")

        # Update last updated timestamp
        if last_updated_ref.current:
            last_updated_ref.current.value = (
                f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}"
            )
            safe_update_control(last_updated_ref.current)

    async def _refresh_loop():
        """Auto-refresh loop - runs every 10 seconds."""
        nonlocal _refresh_active
        while _refresh_active:
            try:
                await load_dashboard_data()
            except Exception as e:
                logger.error(f"Refresh loop error: {e}")
            await asyncio.sleep(10)

    def stop_refresh():
        """Stop the auto-refresh loop."""
        nonlocal _refresh_active
        _refresh_active = False
        logger.debug("Dashboard refresh loop stopped")

    # Start auto-refresh loop
    page.run_task(_refresh_loop)

    return content, stop_refresh, load_dashboard_data
