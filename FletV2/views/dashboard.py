#!/usr/bin/env python3
"""Professional dashboard view with Material 3 styling for Flet 0.28.3."""

from __future__ import annotations

import asyncio
import contextlib
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
import time
from typing import Any, Callable, Coroutine

import flet as ft

try:  # pragma: no cover - UTF-8 bootstrap required by project
    import Shared.utils.utf8_solution as _
except Exception:  # pragma: no cover - allow running in isolation
    pass

try:
    from ..utils.async_helpers import run_sync_in_executor
    from ..utils.ui_builders import create_action_button, create_info_row, create_view_header
    from ..utils.ui_components import AppCard, create_pulsing_status_indicator
    from ..utils.loading_states import (
        create_empty_state,
        create_error_display,
        create_loading_indicator,
        show_error_snackbar,
        show_success_snackbar,
    )
    from ..utils.data_export import export_to_csv, generate_export_filename
except Exception:  # pragma: no cover - fallback when executing directly
    from FletV2.utils.async_helpers import run_sync_in_executor
    from FletV2.utils.ui_builders import create_action_button, create_info_row, create_view_header
    from FletV2.utils.ui_components import AppCard, create_pulsing_status_indicator
    from FletV2.utils.loading_states import (
        create_empty_state,
        create_error_display,
        create_loading_indicator,
        show_error_snackbar,
        show_success_snackbar,
    )
    from FletV2.utils.data_export import export_to_csv, generate_export_filename  # type: ignore


@dataclass(slots=True)
class DashboardSnapshot:
    total_clients: int = 0
    connected_clients: int = 0
    total_files: int = 0
    uptime_seconds: float = 0.0
    server_status: str = "offline"
    server_version: str = ""
    port: int | None = None
    cpu_usage: float | None = None
    memory_usage_mb: float | None = None
    db_response_ms: int | None = None
    active_connections: int = 0
    recent_activity: list[dict[str, Any]] | None = None
    errors: list[str] | None = None


# Removed MetricBlock dataclass - using simple dict instead for metric tracking


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _format_uptime(seconds: float) -> str:
    if seconds <= 0:
        return "—"
    minutes, _ = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return " ".join(parts) or "<1m"


def _format_timestamp(value: Any) -> str:
    if not value:
        return "—"
    try:
        parsed = datetime.fromisoformat(str(value))
        return parsed.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(value)


def _as_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _infer_severity(entry: dict[str, Any]) -> str:
    if not isinstance(entry, dict):
        return "info"

    priority = ("severity", "level", "status", "type", "category")
    for key in priority:
        raw = entry.get(key)
        if raw is None:
            continue
        normalized = str(raw).strip().lower()
        if not normalized:
            continue
        if normalized in {"critical", "fatal"}:
            return "critical"
        if normalized in {"error", "err", "failed", "failure"}:
            return "error"
        if normalized in {"warn", "warning", "degraded", "maintenance"}:
            return "warning"
        if normalized in {"success", "ok", "completed"}:
            return "success"
        if normalized in {"audit", "policy"}:
            return "audit"
        if normalized in {"info", "information", "event"}:
            return "info"

    if entry.get("success") is False:
        return "error"
    return "info"


def _activity_palette(severity: str, scheme: ft.ColorScheme | None = None) -> dict[str, Any]:
    base_palette = {
        "critical": {
            "accent": ft.Colors.RED_ACCENT_200,
            "icon": ft.Icons.ERROR_OUTLINE,
            "text": ft.Colors.RED_900,
        },
        "error": {
            "accent": ft.Colors.RED_ACCENT_100,
            "icon": ft.Icons.ERROR_OUTLINE,
            "text": ft.Colors.RED_900,
        },
        "warning": {
            "accent": ft.Colors.AMBER_ACCENT_100,
            "icon": ft.Icons.WARNING_AMBER,
            "text": ft.Colors.AMBER_900,
        },
        "success": {
            "accent": ft.Colors.GREEN_ACCENT_100,
            "icon": ft.Icons.CHECK_CIRCLE_OUTLINE,
            "text": ft.Colors.GREEN_900,
        },
        "audit": {
            "accent": ft.Colors.PURPLE_ACCENT_100,
            "icon": ft.Icons.ASSIGNMENT_OUTLINED,
            "text": ft.Colors.PURPLE_900,
        },
        "info": {
            "accent": ft.Colors.BLUE_ACCENT_100,
            "icon": ft.Icons.INFO_OUTLINE,
            "text": ft.Colors.BLUE_900,
        },
    }

    def _resolve(attr: str, fallback: str) -> str:
        if scheme is None:
            return fallback
        value = getattr(scheme, attr, None)
        if isinstance(value, str) and value.strip():
            return value
        return fallback

    palette = {
        "critical": {
            "accent": _resolve("error_container", base_palette["critical"]["accent"]),
            "icon": ft.Icons.ERROR_OUTLINE,
            "text": _resolve("on_error_container", base_palette["critical"]["text"]),
        },
        "error": {
            "accent": _resolve("error", base_palette["error"]["accent"]),
            "icon": ft.Icons.ERROR_OUTLINE,
            "text": _resolve("on_error", base_palette["error"]["text"]),
        },
        "warning": {
            "accent": _resolve("tertiary_container", base_palette["warning"]["accent"]),
            "icon": ft.Icons.WARNING_AMBER,
            "text": _resolve("on_tertiary_container", base_palette["warning"]["text"]),
        },
        "success": {
            "accent": _resolve("secondary_container", base_palette["success"]["accent"]),
            "icon": ft.Icons.CHECK_CIRCLE_OUTLINE,
            "text": _resolve("on_secondary_container", base_palette["success"]["text"]),
        },
        "audit": {
            "accent": _resolve("primary_container", base_palette["audit"]["accent"]),
            "icon": ft.Icons.ASSIGNMENT_OUTLINED,
            "text": _resolve("on_primary_container", base_palette["audit"]["text"]),
        },
        "info": {
            "accent": _resolve("surface_variant", base_palette["info"]["accent"]),
            "icon": ft.Icons.INFO_OUTLINE,
            "text": _resolve("on_surface_variant", base_palette["info"]["text"]),
        },
    }

    return palette.get(severity, palette["info"])


async def _call_bridge(server_bridge: Any | None, method_name: str, *args: Any) -> dict[str, Any]:
    if not server_bridge:
        return {"success": False, "data": None, "error": "Server bridge unavailable"}

    method = getattr(server_bridge, method_name, None)
    if method is None:
        return {"success": False, "data": None, "error": f"Method {method_name} not found"}

    try:
        if asyncio.iscoroutinefunction(method):
            result = await method(*args)
        else:
            result = await run_sync_in_executor(method, *args)
    except Exception as exc:  # pragma: no cover - defensive guard
        return {"success": False, "data": None, "error": str(exc)}

    if isinstance(result, dict):
        return result
    return {"success": True, "data": result, "error": None}


async def _fetch_snapshot(server_bridge: Any | None) -> DashboardSnapshot:
    snapshot = DashboardSnapshot()
    issues: list[str] = []

    # Gracefully handle GUI-only mode (no real server/bridge). In this case, don't
    # spam errors; return neutral, empty snapshot so the UI renders clean placeholders.
    if not server_bridge or (hasattr(server_bridge, "real_server") and not getattr(server_bridge, "real_server")):
        snapshot.server_status = "offline"
        snapshot.errors = None
        snapshot.recent_activity = []
        return snapshot

    summary = await _call_bridge(server_bridge, "get_dashboard_summary")
    if summary.get("success"):
        payload = summary.get("data") or {}
        snapshot.total_clients = int(payload.get("total_clients") or 0)
        snapshot.connected_clients = int(payload.get("connected_clients") or 0)
        snapshot.total_files = int(payload.get("total_files") or 0)
        snapshot.uptime_seconds = float(payload.get("uptime") or 0.0)
        snapshot.server_status = str(payload.get("server_status") or "offline")
        snapshot.server_version = str(payload.get("server_version") or snapshot.server_version)
    else:
        issues.append(summary.get("error") or "Dashboard summary unavailable")

    performance = await _call_bridge(server_bridge, "get_performance_metrics")
    if performance.get("success"):
        payload = performance.get("data") or {}
        snapshot.cpu_usage = _as_float(payload.get("cpu_usage_percent"))
        snapshot.memory_usage_mb = _as_float(payload.get("memory_usage_mb"))
        snapshot.db_response_ms = _as_int(payload.get("database_response_time_ms"))
        active = _as_int(payload.get("active_connections"))
        if active is not None:
            snapshot.active_connections = max(active, 0)
    else:
        issues.append(performance.get("error") or "Performance metrics unavailable")

    stats = await _call_bridge(server_bridge, "get_server_statistics")
    if stats.get("success"):
        payload = stats.get("data") or {}
        server_block = payload.get("server") if isinstance(payload, dict) else {}
        clients_block = payload.get("clients") if isinstance(payload, dict) else {}
        files_block = payload.get("files") if isinstance(payload, dict) else {}

        if isinstance(server_block, dict):
            port = _as_int(server_block.get("port"))
            if port is not None:
                snapshot.port = port
            uptime = _as_float(server_block.get("uptime_seconds"))
            if uptime is not None and uptime > snapshot.uptime_seconds:
                snapshot.uptime_seconds = uptime
            version = server_block.get("version")
            if version and not snapshot.server_version:
                snapshot.server_version = str(version)

        if isinstance(clients_block, dict):
            current = _as_int(clients_block.get("currently_connected"))
            if current is not None:
                snapshot.connected_clients = current

        if isinstance(files_block, dict):
            totals = _as_int(files_block.get("total_files"))
            if totals is not None:
                snapshot.total_files = totals
    else:
        issues.append(stats.get("error") or "Server statistics unavailable")

    activity = await _call_bridge(server_bridge, "get_recent_activity_async", 12)
    if not activity.get("success"):
        activity = await _call_bridge(server_bridge, "get_recent_activity", 12)

    if activity.get("success"):
        data = activity.get("data")
        if isinstance(data, list):
            snapshot.recent_activity = data
        else:
            snapshot.recent_activity = []
    else:
        issues.append(activity.get("error") or "Recent activity unavailable")

    snapshot.errors = issues or None
    return snapshot


def _build_metric_block(
    title: str,
    subtitle: str,
    icon: str,
    accent: str,
    column_span: dict[str, int],
    navigate_callback: Callable[[str], None] | None,
    route: str | None,
) -> dict[str, ft.Control]:
    """Build metric block and return dict with wrapper and text controls."""
    value_text = ft.Text("—", size=30, weight=ft.FontWeight.W_700, color=ft.Colors.ON_SURFACE)
    footnote_text = ft.Text(subtitle, size=12, color=ft.Colors.ON_SURFACE_VARIANT)

    body = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(icon, size=22, color=accent),
                    ft.Text(title, size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            value_text,
            footnote_text,
        ],
        spacing=6,
    )

    card = AppCard(body, title=None, expand_content=False)

    wrapper = ft.Container(
        content=card,
        col=column_span,
        on_click=(lambda _: navigate_callback(route)) if route and navigate_callback else None,
        ink=True if route and navigate_callback else False,
    )

    return {"wrapper": wrapper, "value_text": value_text, "footnote_text": footnote_text}


def create_dashboard_view(
    server_bridge: Any | None,
    page: ft.Page,
    _state_manager: Any | None,
    navigate_callback: Callable[[str], None] | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    """Create the dashboard view with Material 3 + subtle neumorphism."""

    snapshot_ref: DashboardSnapshot | None = None
    disposed = False
    refresh_lock = asyncio.Lock()
    # Fallback uptime tracking when server reports 0 but direct bridge is active
    fallback_uptime_start: float | None = None
    # Do not modify page.scroll; keep page-level scroll behavior unchanged

    metrics_config = [
        ("total_clients", "Clients", "Registered endpoints", ft.Icons.PEOPLE_OUTLINED, ft.Colors.PRIMARY, "clients"),
        (
            "active_clients",
            "Active",
            "Currently connected",
            ft.Icons.CAST_CONNECTED,
            ft.Colors.TEAL,
            "clients",
        ),
        ("total_files", "Files", "Backed-up assets", ft.Icons.INSERT_DRIVE_FILE_OUTLINED, ft.Colors.BLUE, "files"),
        ("uptime", "Uptime", "Since last restart", ft.Icons.SCHEDULE, ft.Colors.GREEN, None),
    ]

    metric_blocks: dict[str, dict[str, ft.Control]] = {}
    metric_controls: list[ft.Control] = []
    for key, title, subtitle, icon, accent, route in metrics_config:
        block = _build_metric_block(title, subtitle, icon, accent, {"xs": 12, "sm": 6, "md": 3}, navigate_callback, route)
        metric_blocks[key] = block
        metric_controls.append(block["wrapper"])

    metrics_row = ft.ResponsiveRow(metric_controls, spacing=12, run_spacing=12)

    # --- Live-updated controls used in the header panel
    status_chip_holder = ft.Container(content=create_pulsing_status_indicator("neutral", "Server: Unknown"))
    uptime_value_text = ft.Text("—", size=13, weight=ft.FontWeight.W_600)

    cpu_bar = ft.ProgressBar(value=0.0, bar_height=8)
    cpu_value_text = ft.Text("—", size=12, weight=ft.FontWeight.W_600)
    memory_value_text = ft.Text("—", size=12, weight=ft.FontWeight.W_600)
    db_value_text = ft.Text("—", size=12, weight=ft.FontWeight.W_600)
    connections_value_text = ft.Text("—", size=12, weight=ft.FontWeight.W_600)
    version_value_text = ft.Text("—", size=12, color=ft.Colors.ON_SURFACE)
    port_value_text = ft.Text("—", size=12, color=ft.Colors.ON_SURFACE)

    # --- Helper: simple chip/pill for header stats (FilterChip not reliable in 0.28.3)
    def _pill(icon: str, text_ctrl: ft.Control, bg: str, fg: str) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                [ft.Icon(icon, size=14, color=fg), text_ctrl],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=10, vertical=6),
            bgcolor=ft.Colors.with_opacity(0.10, bg),
            border=ft.border.all(1, ft.Colors.with_opacity(0.18, bg)),
            border_radius=12,
        )

    def _create_status_card(content: ft.Control, bgcolor_color: str = ft.Colors.PRIMARY_CONTAINER, opacity: float = 0.06) -> ft.Container:
        """Create a consistently styled status card with standard padding, border radius, and responsive columns."""
        return ft.Container(
            content=content,
            padding=ft.padding.all(14),
            bgcolor=ft.Colors.with_opacity(opacity, bgcolor_color),
            border_radius=16,
            col={"xs": 12, "md": 4},
        )

    # --- New 2025-style compact status header (glass + pills)
    header_status_left = ft.Column(
        [
            status_chip_holder,
            ft.Row(
                [
                    _pill(ft.Icons.HOURGLASS_BOTTOM, uptime_value_text, ft.Colors.PRIMARY, ft.Colors.ON_PRIMARY),
                    _pill(ft.Icons.HUB, connections_value_text, ft.Colors.SECONDARY, ft.Colors.ON_SECONDARY),
                    _pill(ft.Icons.STORAGE, db_value_text, ft.Colors.PRIMARY_CONTAINER, ft.Colors.ON_PRIMARY_CONTAINER),
                ],
                spacing=8,
                wrap=True,
            ),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.START,
    )

    header_status_right = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.TRENDING_UP, size=16, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text("CPU", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Container(expand=True),
                    cpu_value_text,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            cpu_bar,
            ft.Row(
                [
                    ft.Icon(ft.Icons.MEMORY, size=16, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Text("Memory", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Container(expand=True),
                    memory_value_text,
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Row(
                [
                    _pill(ft.Icons.BUILD_OUTLINED, version_value_text, ft.Colors.PRIMARY, ft.Colors.ON_PRIMARY),
                    _pill(ft.Icons.SETTINGS_ETHERNET, port_value_text, ft.Colors.SECONDARY, ft.Colors.ON_SECONDARY),
                ],
                spacing=8,
                wrap=True,
            ),
        ],
        spacing=8,
        alignment=ft.MainAxisAlignment.START,
    )

    status_header_panel = ft.Container(
        content=ft.Row(
            [
                ft.Container(content=header_status_left, expand=True),
                ft.Container(width=12),
                ft.Container(content=header_status_right, width=340),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.START,
        ),
        padding=ft.padding.all(14),
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY_CONTAINER),
    )

    header_actions = [
        create_action_button("Refresh", None, icon=ft.Icons.REFRESH),
        create_action_button("Export activity", None, icon=ft.Icons.DOWNLOAD, primary=False),
    ]

    header = ft.Column(
        [
            create_view_header(
                "System dashboard",
                icon=ft.Icons.DASHBOARD,
                description="Live overview of clients, throughput, and operational health.",
                actions=header_actions,
            ),
            status_header_panel,
        ],
        spacing=12,
    )

    activity_full_data: list[dict[str, Any]] = []

    activity_summary_text = ft.Text("No activity", size=12, color=ft.Colors.ON_SURFACE_VARIANT)

    # Use ListView instead of Column for automatic scrolling and height management
    activity_list = ft.ListView(spacing=12, padding=ft.padding.symmetric(vertical=6), expand=True)
    activity_list.controls.append(create_loading_indicator("Loading activity…"))

    # Activity section with summary text in the header
    activity_header = ft.Row(
        [
            ft.Text("Recent activity", size=16, weight=ft.FontWeight.W_600),
            ft.Container(expand=True),
            activity_summary_text,
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    activity_section = ft.Column(
        [
            activity_header,
            activity_list,  # ListView handles its own container
        ],
        spacing=12,
        expand=True,
    )

    footer_text = ft.Text("Last updated: —", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
    # The footer should be part of the main content column, not a separate container that might cause layout issues.
    # It should also be aligned to the end of the column, not necessarily the bottom right of a separate container.
    footer_container = ft.Container(content=footer_text, alignment=ft.alignment.center_right)

    error_panel = ft.Container(visible=False)

    content_column = ft.Column(
        [
            header,
            metrics_row,
            activity_section,  # Activity section without filters
            footer_container,
            error_panel,
        ],
        spacing=18,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        scroll=ft.ScrollMode.AUTO,  # Enable scrolling on the column itself
    )

    # Main layout container with proper scrolling support
    root = ft.Container(
        content=content_column,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        expand=True,  # Allow container to fill available space
    )

    def _derive_status(snapshot: DashboardSnapshot) -> tuple[str, str]:
        # If there's no server bridge or no real server behind it, we're in GUI-only
        # standalone mode. Show a neutral banner instead of critical/offline.
        if not server_bridge or (hasattr(server_bridge, "real_server") and not getattr(server_bridge, "real_server")):
            return "neutral", "GUI: Standalone mode"
        # Check if bridge has real server instance
        bridge_connected = False
        direct_bridge_present = False
        if server_bridge and hasattr(server_bridge, "is_connected"):
            with contextlib.suppress(Exception):
                bridge_connected = bool(server_bridge.is_connected())
        # In integrated mode, a real server object can be present even if is_connected() is False
        # (e.g., network listener not started). Detect that and report as Connected (Direct).
        if server_bridge and hasattr(server_bridge, "real_server"):
            try:
                direct_bridge_present = bool(getattr(server_bridge, "real_server"))
            except Exception:
                direct_bridge_present = False

        raw_status = _normalize_text(snapshot.server_status).lower()

        # Additional evidence that the server is live even if status says stopped
        evidence_connected = any([
            snapshot.uptime_seconds and snapshot.uptime_seconds > 0,
            (snapshot.total_clients or 0) > 0,
            (snapshot.total_files or 0) > 0,
            bool(snapshot.server_version),
            snapshot.port is not None,
        ])

        # Priority 1: Check actual server running status from snapshot
        if raw_status in {"running", "online", "active", "operational"}:
            return "excellent", f"Server: {snapshot.server_status.title()}"

        # Priority 2: Server in degraded/warning state
        if raw_status in {"degraded", "warning", "maintenance"}:
            return "warning", f"Server: {snapshot.server_status.title()}"

        # Priority 3: Server explicitly offline/stopped
        if raw_status in {"offline", "stopped", "disconnected"}:
            # In integrated GUI mode, network listener may be stopped while direct bridge is alive.
            # Reflect that as Connected (Direct) to avoid alarming red statuses.
            if bridge_connected or direct_bridge_present or evidence_connected:
                return "excellent", "Server: Connected (Direct)"
            return "critical", f"Server: {snapshot.server_status.title()}"

        # Priority 4: Bridge connected but no clear status
        if bridge_connected:
            return "warning", "Server: Unknown status"

        # Default: Disconnected
        return "critical", "Server: Disconnected"

    def _update_control(control: ft.Control, value: Any) -> None:
        """Helper to update a control's value and trigger UI update."""
        control.value = value
        control.update()

    async def _apply_snapshot(snapshot: DashboardSnapshot) -> None:
        nonlocal snapshot_ref
        nonlocal fallback_uptime_start
        snapshot_ref = snapshot

        # Compute display uptime with monotonic fallback when uptime_seconds is 0 but evidence suggests server is alive
        display_uptime_seconds = snapshot.uptime_seconds if snapshot.uptime_seconds and snapshot.uptime_seconds > 0 else 0.0

        if display_uptime_seconds <= 0:
            direct_bridge_present = False
            if server_bridge and hasattr(server_bridge, "real_server"):
                with contextlib.suppress(Exception):
                    direct_bridge_present = bool(getattr(server_bridge, "real_server"))

            evidence_connected = any([
                (snapshot.total_clients or 0) > 0,
                (snapshot.total_files or 0) > 0,
                bool(snapshot.server_version),
                snapshot.port is not None,
            ])

            if direct_bridge_present or evidence_connected:
                if fallback_uptime_start is None:
                    fallback_uptime_start = time.monotonic()
                display_uptime_seconds = max(0.0, time.monotonic() - fallback_uptime_start)
            else:
                fallback_uptime_start = None

        # Update metric blocks
        clients_block = metric_blocks["total_clients"]
        _update_control(clients_block["value_text"], f"{snapshot.total_clients:,}" if snapshot.total_clients else "0")

        active_block = metric_blocks["active_clients"]
        _update_control(active_block["value_text"], f"{snapshot.connected_clients:,}" if snapshot.connected_clients else "0")
        ratio_text = f"{(snapshot.connected_clients / snapshot.total_clients) * 100:.0f}% online" if snapshot.total_clients > 0 else "Currently connected"
        _update_control(active_block["footnote_text"], ratio_text)

        files_block = metric_blocks["total_files"]
        _update_control(files_block["value_text"], f"{snapshot.total_files:,}" if snapshot.total_files else "0")

        uptime_block = metric_blocks["uptime"]
        _update_control(uptime_block["value_text"], _format_uptime(display_uptime_seconds))
        chip_level, chip_label = _derive_status(snapshot)
        _update_control(uptime_block["footnote_text"], chip_label)

        # Update status chip
        chip_level, chip_label = _derive_status(snapshot)
        status_chip_holder.content = create_pulsing_status_indicator(chip_level, chip_label)
        status_chip_holder.update()

        # Update status summary cards
        _update_control(uptime_value_text, _format_uptime(display_uptime_seconds))

        if snapshot.cpu_usage is not None:
            cpu_bar.value = max(0.0, min(snapshot.cpu_usage / 100.0, 1.0))
            cpu_value_text.value = f"{snapshot.cpu_usage:.1f}%"
        else:
            cpu_bar.value = 0.0
            cpu_value_text.value = "—"
        cpu_bar.update()
        cpu_value_text.update()

        _update_control(memory_value_text, f"{snapshot.memory_usage_mb:.1f} MB" if snapshot.memory_usage_mb is not None else "—")
        _update_control(db_value_text, f"{snapshot.db_response_ms} ms" if snapshot.db_response_ms is not None and snapshot.db_response_ms >= 0 else "—")
        _update_control(connections_value_text, str(max(snapshot.active_connections, snapshot.connected_clients)))
        _update_control(version_value_text, snapshot.server_version or "—")
        _update_control(port_value_text, str(snapshot.port) if snapshot.port is not None else "—")

        rows: list[list[str]] = []
        for item in (snapshot.recent_activity or [])[:12]:
            if not isinstance(item, dict):
                continue
            timestamp = _format_timestamp(item.get("timestamp") or item.get("time"))
            category = str(item.get("type") or item.get("level") or "Info").title()
            message = str(item.get("message") or item.get("details") or "")
            rows.append([timestamp, category, message])

        nonlocal activity_full_data
        activity_full_data = snapshot.recent_activity or []
        _apply_activity_filters()

        footer_text.value = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer_text.update()

        if snapshot.errors:
            joined = "\n".join(snapshot.errors)
            error_panel.content = AppCard(create_error_display(joined), title="Dashboard issues", expand_content=False, disable_hover=True)
            error_panel.visible = True
        else:
            error_panel.content = None
            error_panel.visible = False
        error_panel.update()

    async def _refresh() -> None:
        if disposed:
            return
        async with refresh_lock:
            try:
                snapshot = await _fetch_snapshot(server_bridge)
            except Exception as exc:  # pragma: no cover - defensive guard
                show_error_snackbar(page, f"Dashboard refresh failed: {exc}")
                return

            if disposed:
                return

            await _apply_snapshot(snapshot)

    def _on_refresh(_: ft.ControlEvent) -> None:
        if disposed:
            return
        page.run_task(_refresh)

    def _on_export(_: ft.ControlEvent) -> None:
        if disposed:
            return
        if not snapshot_ref or not snapshot_ref.recent_activity:
            show_error_snackbar(page, "No activity available for export")
            return

        try:
            export_rows = []
            for item in snapshot_ref.recent_activity[:100]:
                if not isinstance(item, dict):
                    continue
                export_rows.append(
                    {
                        "timestamp": _format_timestamp(item.get("timestamp") or item.get("time")),
                        "category": str(item.get("type") or item.get("level") or "info"),
                        "message": str(item.get("message") or item.get("details") or ""),
                    }
                )

            if not export_rows:
                show_error_snackbar(page, "No activity entries to export")
                return

            filename = generate_export_filename("dashboard_activity", "csv")
            export_to_csv(export_rows, filename, fieldnames=["timestamp", "category", "message"])
            show_success_snackbar(page, f"Activity exported to {filename}")
        except Exception as exc:  # pragma: no cover - defensive guard
            show_error_snackbar(page, f"Export failed: {exc}")

    header_actions[0].on_click = _on_refresh
    header_actions[1].on_click = _on_export

    def _open_activity_details(entry: dict[str, Any]) -> None:
        pretty = json.dumps(entry, indent=2, default=str)
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Event details"),
            content=ft.Container(
                content=ft.ListView(
                    controls=[ft.Text(pretty, size=12, selectable=True)],
                    spacing=6,
                    padding=ft.padding.all(6),
                    expand=True,
                ),
                width=600,
                height=420,
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: _close_dialog())],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def _close_dialog() -> None:
        if page.dialog:
            page.dialog.open = False
            page.update()

    def _build_activity_tile(entry: dict[str, Any]) -> ft.Control:
        """Build activity tile using simplified pattern."""
        severity = _infer_severity(entry)
        scheme = page.theme.color_scheme if getattr(page, "theme", None) and getattr(page.theme, "color_scheme", None) else None
        palette = _activity_palette(severity, scheme)

        timestamp = _format_timestamp(entry.get("timestamp") or entry.get("time"))
        category = _normalize_text(entry.get("type") or entry.get("category") or "event").title() or "Event"
        message = _normalize_text(entry.get("message") or entry.get("details") or entry.get("description") or "—")

        # Build subtitle with timestamp and metadata
        subtitle_parts = [timestamp]
        if component := _normalize_text(entry.get("component") or entry.get("origin") or ""):
            subtitle_parts.append(f"Component: {component}")
        if client_id := _normalize_text(entry.get("client_id") or entry.get("client") or ""):
            subtitle_parts.append(f"Client: {client_id}")

        # Use ListTile for cleaner structure
        return ft.Card(
            content=ft.ListTile(
                leading=ft.Container(
                    content=ft.Icon(palette["icon"], size=20, color=palette["text"]),
                    width=40,
                    height=40,
                    bgcolor=ft.Colors.with_opacity(0.18, palette["accent"]),
                    border_radius=20,
                    alignment=ft.alignment.center,
                ),
                title=ft.Text(f"{severity.title()} • {category}", size=14, weight=ft.FontWeight.W_600),
                subtitle=ft.Column(
                    [
                        ft.Text(message, size=13, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(" • ".join(subtitle_parts), size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                    ],
                    spacing=4,
                    tight=True,
                ),
                on_click=lambda _: _open_activity_details(entry),
                trailing=ft.IconButton(
                    icon=ft.Icons.OPEN_IN_NEW,
                    tooltip="View details",
                    icon_size=18,
                    on_click=lambda _: _open_activity_details(entry),
                ),
            ),
            elevation=1,
            color=ft.Colors.with_opacity(0.06, palette["accent"]),
        )

    def _apply_activity_filters() -> None:
        """Display all activity without filtering."""
        activity_list.controls.clear()

        if not activity_full_data:
            # Empty state
            activity_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.HISTORY, size=48, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text("No recent activity", size=16, weight=ft.FontWeight.W_600),
                            ft.Text(
                                "Operational events will appear here once the server receives requests.",
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                    ),
                    padding=40,
                    alignment=ft.alignment.center,
                )
            )
            activity_summary_text.value = "No activity"
        else:
            # Show all events
            for entry in activity_full_data:
                activity_list.controls.append(_build_activity_tile(entry))

            # Update summary with severity counts
            severity_counter = Counter(_infer_severity(entry) for entry in activity_full_data)
            summary_bits = [f"{len(activity_full_data)} events"]
            for key in ("critical", "error", "warning", "info"):
                if severity_counter.get(key):
                    summary_bits.append(f"{severity_counter[key]} {key}")
            activity_summary_text.value = " • ".join(summary_bits)

        activity_list.update()
        activity_summary_text.update()

    auto_refresh_task: asyncio.Task | None = None

    async def _auto_refresh_loop() -> None:
        try:
            while not disposed:
                await asyncio.sleep(45)
                if disposed:
                    break
                await _refresh()
        except asyncio.CancelledError:  # pragma: no cover - cancellation path
            return

    async def setup() -> None:
        await asyncio.sleep(0.1)
        if not disposed:
            await _refresh()
        if not disposed:
            nonlocal auto_refresh_task
            auto_refresh_task = page.run_task(_auto_refresh_loop)

    def dispose() -> None:
        nonlocal disposed
        disposed = True
        if auto_refresh_task and not auto_refresh_task.done():
            auto_refresh_task.cancel()

    return root, dispose, setup
