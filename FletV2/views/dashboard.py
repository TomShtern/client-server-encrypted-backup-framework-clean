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
import os

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
    )
    from ..utils.user_feedback import show_error_message, show_success_message
    from ..utils.data_export import export_to_csv, generate_export_filename
    from ..utils.formatters import (
        as_float,
        as_int,
        format_timestamp,
        format_uptime,
        normalize_text,
    )
    from ..theme import create_skeleton_loader
except Exception:  # pragma: no cover - fallback when executing directly
    from FletV2.utils.async_helpers import run_sync_in_executor
    from FletV2.utils.ui_builders import create_action_button, create_info_row, create_view_header
    from FletV2.utils.ui_components import AppCard, create_pulsing_status_indicator
    from FletV2.utils.loading_states import (
        create_empty_state,
        create_error_display,
        create_loading_indicator,
    )
    from FletV2.utils.user_feedback import show_error_message, show_success_message
    from FletV2.utils.data_export import export_to_csv, generate_export_filename  # type: ignore
    from FletV2.utils.formatters import (
        as_float,
        as_int,
        format_timestamp,
        format_uptime,
        normalize_text,
    )
    from FletV2.theme import create_skeleton_loader


# ============================================================================
# DATA STRUCTURES
# ============================================================================

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

# Formatters moved to FletV2.utils.formatters module:
# - normalize_text, format_uptime, format_timestamp, as_float, as_int


# ============================================================================
# SECTION 2: BUSINESS LOGIC HELPERS
# Severity inference, color palettes, data transformations
# ============================================================================

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


# ============================================================================
# SECTION 1: DATA FETCHING
# Async wrappers for ServerBridge calls with proper run_in_executor
# ============================================================================

async def _call_bridge(server_bridge: Any | None, method_name: str, *args: Any) -> dict[str, Any]:
    DEBUG = os.environ.get("FLET_DASHBOARD_DEBUG") == "1"
    if not server_bridge:
        if DEBUG:
            print(f"[DASH] _call_bridge('{method_name}') skipped - no server bridge")
        return {"success": False, "data": None, "error": "Server bridge unavailable"}

    method = getattr(server_bridge, method_name, None)
    if method is None:
        return {"success": False, "data": None, "error": f"Method {method_name} not found"}

    try:
        if DEBUG:
            print(f"[DASH] _call_bridge → calling {method_name} ({'async' if asyncio.iscoroutinefunction(method) else 'sync'}) with args={args}")
        if asyncio.iscoroutinefunction(method):
            result = await method(*args)
        else:
            result = await run_sync_in_executor(method, *args)
    except Exception as exc:  # pragma: no cover - defensive guard
        if DEBUG:
            print(f"[DASH] _call_bridge('{method_name}') raised: {exc}")
        return {"success": False, "data": None, "error": str(exc)}

    if isinstance(result, dict):
        if DEBUG:
            print(f"[DASH] _call_bridge('{method_name}') returned (dict): success={result.get('success')} keys={list(result.keys())}")
        return result
    if DEBUG:
        print(f"[DASH] _call_bridge('{method_name}') returned (raw): type={type(result)}")
    return {"success": True, "data": result, "error": None}


async def _fetch_snapshot(server_bridge: Any | None) -> DashboardSnapshot:
    DEBUG = os.environ.get("FLET_DASHBOARD_DEBUG") == "1"
    snapshot = DashboardSnapshot()
    issues: list[str] = []

    # Gracefully handle GUI-only mode (no real server/bridge). In this case, don't
    # spam errors; return neutral, empty snapshot so the UI renders clean placeholders.
    if not server_bridge or (hasattr(server_bridge, "real_server") and not getattr(server_bridge, "real_server")):
        snapshot.server_status = "offline"
        snapshot.errors = None
        snapshot.recent_activity = []
        return snapshot

    if DEBUG:
        print("[DASH] _fetch_snapshot → fetching get_dashboard_summary")
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

    if DEBUG:
        print("[DASH] _fetch_snapshot → fetching get_performance_metrics")
    performance = await _call_bridge(server_bridge, "get_performance_metrics")
    if performance.get("success"):
        payload = performance.get("data") or {}
        snapshot.cpu_usage = as_float(payload.get("cpu_usage_percent"))
        snapshot.memory_usage_mb = as_float(payload.get("memory_usage_mb"))
        snapshot.db_response_ms = as_int(payload.get("database_response_time_ms"))
        active = as_int(payload.get("active_connections"))
        if active is not None:
            snapshot.active_connections = max(active, 0)
    else:
        issues.append(performance.get("error") or "Performance metrics unavailable")

    if DEBUG:
        print("[DASH] _fetch_snapshot → fetching get_server_statistics")
    stats = await _call_bridge(server_bridge, "get_server_statistics")
    if stats.get("success"):
        payload = stats.get("data") or {}
        server_block = payload.get("server") if isinstance(payload, dict) else {}
        clients_block = payload.get("clients") if isinstance(payload, dict) else {}
        files_block = payload.get("files") if isinstance(payload, dict) else {}

        if isinstance(server_block, dict):
            port = as_int(server_block.get("port"))
            if port is not None:
                snapshot.port = port
            uptime = as_float(server_block.get("uptime_seconds"))
            if uptime is not None and uptime > snapshot.uptime_seconds:
                snapshot.uptime_seconds = uptime
            version = server_block.get("version")
            if version and not snapshot.server_version:
                snapshot.server_version = str(version)

        if isinstance(clients_block, dict):
            current = as_int(clients_block.get("currently_connected"))
            if current is not None:
                snapshot.connected_clients = current

        if isinstance(files_block, dict):
            totals = as_int(files_block.get("total_files"))
            if totals is not None:
                snapshot.total_files = totals
    else:
        issues.append(stats.get("error") or "Server statistics unavailable")

    if DEBUG:
        print("[DASH] _fetch_snapshot → fetching get_recent_activity_async (limit=12)")
    activity = await _call_bridge(server_bridge, "get_recent_activity_async", 12)
    if not activity.get("success"):
        if DEBUG:
            print("[DASH] _fetch_snapshot → async activity failed, trying sync get_recent_activity")
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


# ============================================================================
# SECTION 3: UI COMPONENTS
# Flet control builders for metrics, activity, status displays
# ============================================================================

def _build_metric_block(
    title: str,
    subtitle: str,
    icon: str,
    accent: str,
    column_span: dict[str, int],
    navigate_callback: Callable[[str], None] | None,
    route: str | None,
) -> dict[str, ft.Control]:
    """Build enhanced metric block with neumorphic styling and hover effects."""
    # Use ft.Ref for controls that need to be updated
    value_text_ref = ft.Ref[ft.Text]()
    footnote_text_ref = ft.Ref[ft.Text]()

    # Create Text controls with refs
    value_text = ft.Text("—", size=30, weight=ft.FontWeight.W_700, color=ft.Colors.ON_SURFACE, ref=value_text_ref)
    footnote_text = ft.Text(subtitle, size=12, color=ft.Colors.ON_SURFACE_VARIANT, ref=footnote_text_ref)

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

    # Clean card with subtle shadow and color accent
    card_content = ft.Container(
        content=body,
        padding=ft.padding.all(20),
        bgcolor=ft.Colors.SURFACE,
        border_radius=12,
        border=ft.border.only(top=ft.BorderSide(3, accent)),
        shadow=[ft.BoxShadow(
            blur_radius=8,
            spread_radius=1,
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
            offset=ft.Offset(0, 2),
        )],
        animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )

    # Add hover effect
    def on_hover(e):
        card_content.scale = 1.02 if e.data == "true" else 1.0
        card_content.update()

    card_content.on_hover = on_hover

    wrapper = ft.Container(
        content=card_content,
        col=column_span,
        on_click=(lambda _: navigate_callback(route)) if route and navigate_callback else None,
        ink=True if route and navigate_callback else False,
    )

    # Return refs for direct access to controls
    return {
        "wrapper": wrapper,
        "value_text": value_text,
        "value_text_ref": value_text_ref,
        "footnote_text": footnote_text,
        "footnote_text_ref": footnote_text_ref
    }


# ============================================================================
# SECTION 5: MAIN VIEW
# Dashboard composition, setup, and lifecycle management
# ============================================================================

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

    # Simple text displays for CPU and Memory
    cpu_value_text = ft.Text("—", size=12, weight=ft.FontWeight.W_600)
    cpu_bar = ft.ProgressBar(value=0.0, bar_height=8)
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

    # Clean status header with subtle depth
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
        padding=ft.padding.all(16),
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SURFACE_TINT),
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE)),
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

    # Add skeleton loaders matching final content structure
    for _ in range(4):  # Show 4 skeleton tiles
        skeleton_tile = ft.Container(
            content=ft.Row([
                create_skeleton_loader(height=40, width=40, radius=20),  # Icon placeholder
                ft.Column([
                    create_skeleton_loader(height=16, width=200),  # Title
                    create_skeleton_loader(height=12, width=300),  # Subtitle
                    create_skeleton_loader(height=10, width=150),  # Timestamp
                ], spacing=4),
            ], spacing=12),
            padding=ft.padding.all(12),
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SURFACE),
            border_radius=12,
        )
        activity_list.controls.append(skeleton_tile)

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

    # Store content_column in a closure for _apply_snapshot to access
    def get_content_column():
        return content_column

    def _derive_status(snapshot: DashboardSnapshot) -> tuple[str, str]:
        # If there's no server bridge or no real server behind it, we're in GUI-only
        # standalone mode. Show a neutral banner instead of critical/offline.
        if not server_bridge or (hasattr(server_bridge, "real_server") and not getattr(server_bridge, "real_server")):
            return "neutral", "GUI: Standalone mode"

        # Check if bridge has real server instance (but DON'T call is_connected() - it blocks!)
        direct_bridge_present = False
        if server_bridge and hasattr(server_bridge, "real_server"):
            try:
                direct_bridge_present = bool(getattr(server_bridge, "real_server"))
            except Exception:
                direct_bridge_present = False

        raw_status = normalize_text(snapshot.server_status).lower()

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
            if direct_bridge_present or evidence_connected:
                return "excellent", "Server: Connected (Direct)"
            return "critical", f"Server: {snapshot.server_status.title()}"

        # Priority 4: Direct bridge present but no clear status
        if direct_bridge_present:
            return "warning", "Server: Unknown status"

        # Default: Disconnected
        return "critical", "Server: Disconnected"

    def _update_control(control: ft.Control, value: Any, parent: ft.Control | None = None, force_page_update: bool = False) -> None:
        """Set control value and perform hierarchical updates for Flet 0.28.3.

        Notes for Flet 0.28.3:
        - Child property changes are not always propagated by updating an ancestor.
        - Must call update() on control, parent, and sometimes page for reliable propagation.
        - For critical controls like metric values, force a page update to ensure visibility.
        """
        try:
            control.value = value
            # Flet 0.28.3 requires hierarchical updates to ensure visual changes
            with contextlib.suppress(Exception):
                control.update()

            # Update parent if provided (important for nested controls)
            if parent:
                with contextlib.suppress(Exception):
                    parent.update()

            # Force page update for critical controls that aren't showing up
            if force_page_update:
                with contextlib.suppress(Exception):
                    page.update()

            if os.environ.get("FLET_DASHBOARD_DEBUG") == "1":
                print(f"[DASH] _update_control: set {type(control).__name__} to '{value}'")

        except Exception as e:
            if os.environ.get("FLET_DASHBOARD_DEBUG") == "1":
                print(f"[DASH][WARN] control value set failed: {e}")

    async def _apply_snapshot(snapshot: DashboardSnapshot) -> None:
        DEBUG = os.environ.get("FLET_DASHBOARD_DEBUG") == "1"
        nonlocal snapshot_ref
        nonlocal fallback_uptime_start
        nonlocal metrics_row
        if DEBUG:
            print("[DASH] _apply_snapshot ENTER")
            print(f"[DASH] snapshot: clients={snapshot.total_clients}, connected={snapshot.connected_clients}, files={snapshot.total_files}, status={snapshot.server_status}, uptime={snapshot.uptime_seconds}")
        try:
            snapshot_ref = snapshot

            # Get reference to content column for aggressive rebuilds
            content_col = get_content_column()

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

            # Update metric blocks with COMPLETE REBUILD for Flet 0.28.3 compatibility
            if DEBUG:
                print("[DASH] _apply_snapshot → REBUILDING metric blocks (complete replacement)")

            # CRITICAL: Complete metric block replacement to ensure visibility
            # This works around Flet 0.28.3's update propagation issues

            # Update all metric blocks efficiently - set values first, update container once
            clients_block = metric_blocks["total_clients"]
            new_clients_value = f"{snapshot.total_clients:,}" if snapshot.total_clients else "0"
            if "value_text_ref" in clients_block and clients_block["value_text_ref"].current:
                clients_block["value_text_ref"].current.value = new_clients_value
                if DEBUG:
                    print(f"[DASH] Updated clients metric to: {new_clients_value}")

            active_block = metric_blocks["active_clients"]
            new_active_value = f"{snapshot.connected_clients:,}" if snapshot.connected_clients else "0"
            ratio_text = f"{(snapshot.connected_clients / snapshot.total_clients) * 100:.0f}% online" if snapshot.total_clients > 0 else "Currently connected"
            if "value_text_ref" in active_block and active_block["value_text_ref"].current:
                active_block["value_text_ref"].current.value = new_active_value
                if "footnote_text_ref" in active_block and active_block["footnote_text_ref"].current:
                    active_block["footnote_text_ref"].current.value = ratio_text
                if DEBUG:
                    print(f"[DASH] Updated active clients metric to: {new_active_value}")

            files_block = metric_blocks["total_files"]
            new_files_value = f"{snapshot.total_files:,}" if snapshot.total_files else "0"
            if "value_text_ref" in files_block and files_block["value_text_ref"].current:
                files_block["value_text_ref"].current.value = new_files_value
                if DEBUG:
                    print(f"[DASH] Updated files metric to: {new_files_value}")

            try:
                if DEBUG:
                    print(f"[DASH] About to update uptime block...")
                uptime_block = metric_blocks["uptime"]
                if DEBUG:
                    print(f"[DASH] Got uptime_block reference, display_uptime_seconds={display_uptime_seconds}")
                new_uptime_value = format_uptime(display_uptime_seconds)
                if DEBUG:
                    print(f"[DASH] format_uptime() returned: {new_uptime_value}")
                chip_level, chip_label = _derive_status(snapshot)
                if DEBUG:
                    print(f"[DASH] _derive_status() returned: {chip_level}, {chip_label}")
                if "value_text_ref" in uptime_block and uptime_block["value_text_ref"].current:
                    uptime_block["value_text_ref"].current.value = new_uptime_value
                    if "footnote_text_ref" in uptime_block and uptime_block["footnote_text_ref"].current:
                        uptime_block["footnote_text_ref"].current.value = chip_label
                    if DEBUG:
                        print(f"[DASH] Updated uptime metric to: {new_uptime_value}")
            except Exception as e:
                print(f"[DASH][CRITICAL ERROR] Uptime block update failed: {e}")
                import traceback
                traceback.print_exc()

            # CRITICAL: Yield control back to event loop before updating
            # This prevents deadlock in Flet 0.28.3 where .update() waits for event loop
            if DEBUG:
                print("[DASH] Yielding to event loop before metrics_row update")
            await asyncio.sleep(0)  # Allow event loop to process pending tasks

            if DEBUG:
                print("[DASH] Triggering single metrics_row update")
            # Safety: Only update if attached to page
            if metrics_row.page:
                metrics_row.update()
                if DEBUG:
                    print("[DASH] metrics_row.update() completed")
            else:
                if DEBUG:
                    print("[DASH] WARNING: metrics_row not attached to page, skipping update")
            if DEBUG:
                print("[DASH] Metric blocks rebuilt completely")

            # Update status chip
            try:
                chip_level, chip_label = _derive_status(snapshot)
                status_chip_holder.content = create_pulsing_status_indicator(chip_level, chip_label)
                with contextlib.suppress(Exception):
                    status_chip_holder.update()
            except Exception as e:
                if DEBUG:
                    print(f"[DASH][ERROR] status chip update failed: {e}")

            # Update status summary cards
            _update_control(uptime_value_text, format_uptime(display_uptime_seconds), parent=status_header_panel, force_page_update=True)

            try:
                if snapshot.cpu_usage is not None:
                    cpu_bar.value = max(0.0, min(snapshot.cpu_usage / 100.0, 1.0))
                    cpu_value_text.value = f"{snapshot.cpu_usage:.1f}%"
                else:
                    cpu_bar.value = 0.0
                    cpu_value_text.value = "—"
                with contextlib.suppress(Exception):
                    cpu_bar.update()
                    cpu_value_text.update()
                    # Force header panel update to show CPU changes
                    status_header_panel.update()
            except Exception as e:
                if DEBUG:
                    print(f"[DASH][WARN] CPU controls update failed: {e}")

            try:
                _update_control(memory_value_text, f"{snapshot.memory_usage_mb:.1f} MB" if snapshot.memory_usage_mb is not None else "—", parent=status_header_panel, force_page_update=True)
                _update_control(db_value_text, f"{snapshot.db_response_ms} ms" if snapshot.db_response_ms is not None and snapshot.db_response_ms >= 0 else "—", parent=status_header_panel, force_page_update=True)
                _update_control(connections_value_text, str(max(snapshot.active_connections, snapshot.connected_clients)), parent=status_header_panel, force_page_update=True)
                _update_control(version_value_text, snapshot.server_version or "—", parent=status_header_panel)
                _update_control(port_value_text, str(snapshot.port) if snapshot.port is not None else "—", parent=status_header_panel)
            except Exception as e:
                if DEBUG:
                    print(f"[DASH][WARN] Header values update failed: {e}")

            # Targeted parent updates to ensure children diffs are propagated in 0.28.3
            if DEBUG:
                print("[DASH] _apply_snapshot → updating header containers")
            with contextlib.suppress(Exception):
                status_header_panel.update()
            with contextlib.suppress(Exception):
                metrics_row.update()

            # Early flush so metrics and header appear even if later sections fail
            if DEBUG:
                print("[DASH] _apply_snapshot → early flush after metrics/header")
            with contextlib.suppress(Exception):
                root.update()
            with contextlib.suppress(Exception):
                if getattr(page, 'update', None):
                    page.update()

            if DEBUG:
                print("[DASH] _apply_snapshot → applying activity filters")
            nonlocal activity_full_data
            activity_full_data = snapshot.recent_activity or []
            try:
                _apply_activity_filters()
            except Exception as e:
                if DEBUG:
                    print(f"[DASH][WARN] Activity filters failed: {e}")

            footer_text.value = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            with contextlib.suppress(Exception):
                footer_text.update()

            if snapshot.errors:
                joined = "\n".join(snapshot.errors)
                error_panel.content = AppCard(create_error_display(joined), title="Dashboard issues", expand_content=False, disable_hover=True)
                error_panel.visible = True
                with contextlib.suppress(Exception):
                    error_panel.update()
            else:
                error_panel.content = None
                error_panel.visible = False
                with contextlib.suppress(Exception):
                    error_panel.update()
        except Exception as e:
            if DEBUG:
                import traceback
                print(f"[DASH][ERROR] _apply_snapshot exception: {e}\n{traceback.format_exc()}")
            if DEBUG:
                print("[DASH] _apply_snapshot EXIT (UI updated)")

    async def _refresh() -> None:
        DEBUG = os.environ.get("FLET_DASHBOARD_DEBUG") == "1"
        if disposed:
            return
        async with refresh_lock:
            try:
                if DEBUG:
                    print("[DASH] _refresh → calling _fetch_snapshot()")
                snapshot = await _fetch_snapshot(server_bridge)
            except Exception as exc:  # pragma: no cover - defensive guard
                show_error_message(page, f"Dashboard refresh failed: {exc}")
                return

            if disposed:
                return

            await _apply_snapshot(snapshot)
            if DEBUG:
                print("[DASH] _refresh → snapshot applied")

    def _on_refresh(_: ft.ControlEvent) -> None:
        if disposed:
            return
        page.run_task(_refresh)

    def _on_export(_: ft.ControlEvent) -> None:
        if disposed:
            return
        if not snapshot_ref or not snapshot_ref.recent_activity:
            show_error_message(page, "No activity available for export")
            return

        try:
            export_rows = []
            for item in snapshot_ref.recent_activity[:100]:
                if not isinstance(item, dict):
                    continue
                export_rows.append(
                    {
                        "timestamp": format_timestamp(item.get("timestamp") or item.get("time")),
                        "category": str(item.get("type") or item.get("level") or "info"),
                        "message": str(item.get("message") or item.get("details") or ""),
                    }
                )

            if not export_rows:
                show_error_message(page, "No activity entries to export")
                return

            filename = generate_export_filename("dashboard_activity", "csv")
            export_to_csv(export_rows, filename, fieldnames=["timestamp", "category", "message"])
            show_success_message(page, f"Activity exported to {filename}")
        except Exception as exc:  # pragma: no cover - defensive guard
            show_error_message(page, f"Export failed: {exc}")

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
        """Build enhanced activity tile with strong color coding and hover effects."""
        severity = _infer_severity(entry)
        scheme = page.theme.color_scheme if getattr(page, "theme", None) and getattr(page.theme, "color_scheme", None) else None
        palette = _activity_palette(severity, scheme)

        timestamp = format_timestamp(entry.get("timestamp") or entry.get("time"))
        category = normalize_text(entry.get("type") or entry.get("category") or "event").title() or "Event"
        message = normalize_text(entry.get("message") or entry.get("details") or entry.get("description") or "—")

        # Build subtitle with timestamp and metadata
        subtitle_parts = [timestamp]
        if component := normalize_text(entry.get("component") or entry.get("origin") or ""):
            subtitle_parts.append(f"Component: {component}")
        if client_id := normalize_text(entry.get("client_id") or entry.get("client") or ""):
            subtitle_parts.append(f"Client: {client_id}")

        # Build tile with severity badge pill for quick visual scanning
        tile = ft.ListTile(
            leading=ft.Container(
                content=ft.Icon(palette["icon"], size=20, color=palette["text"]),
                width=40,
                height=40,
                bgcolor=ft.Colors.with_opacity(0.18, palette["accent"]),
                border_radius=20,
                alignment=ft.alignment.center,
            ),
            title=ft.Row([
                # Severity badge pill
                ft.Container(
                    content=ft.Text(
                        severity.upper(),
                        size=10,
                        weight=ft.FontWeight.W_700,
                        color=palette["text"]
                    ),
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    bgcolor=ft.Colors.with_opacity(0.2, palette["accent"]),
                    border_radius=8,
                ),
                ft.Text(f" • {category}", size=14, weight=ft.FontWeight.W_600),
            ]),
            subtitle=ft.Column(
                [
                    ft.Text(message, size=13, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(" • ".join(subtitle_parts), size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                ],
                spacing=4,
                tight=True,
            ),
            trailing=ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color=ft.Colors.ON_SURFACE_VARIANT),
        )

        # Enhanced container with stronger colors, left border, hover animation, and click handling
        tile_container = ft.Container(
            content=tile,
            bgcolor=ft.Colors.with_opacity(0.10, palette["accent"]),
            border_radius=12,
            border=ft.border.only(left=ft.BorderSide(4, palette["accent"])),
            animate_scale=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
            ink=True,
            on_click=lambda e: _open_activity_details(entry),
        )

        # Add hover effect for interactivity
        def on_tile_hover(e):
            tile_container.scale = 1.01 if e.data == "true" else 1.0
            tile_container.update()

        tile_container.on_hover = on_tile_hover

        return ft.Card(
            content=tile_container,
            elevation=2,
        )

    def _apply_activity_filters() -> None:
        """Display all activity without filtering.

        IMPORTANT: Do not call control.update() here. Let the caller batch and
        flush updates once to avoid render thrashing in Flet 0.28.3.
        """
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
            with contextlib.suppress(Exception):
                activity_summary_text.update()
            with contextlib.suppress(Exception):
                activity_list.update()
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
            with contextlib.suppress(Exception):
                activity_summary_text.update()
            with contextlib.suppress(Exception):
                activity_list.update()

    auto_refresh_task: asyncio.Task | None = None
    stop_event = asyncio.Event()

    async def _auto_refresh_loop() -> None:
        while not stop_event.is_set():
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=45)
            except asyncio.TimeoutError:
                if not stop_event.is_set():
                    await _refresh()

    async def setup() -> None:
        DEBUG = os.environ.get("FLET_DASHBOARD_DEBUG") == "1"
        # CRITICAL: Wait for CanvasKit to fully render controls before updating them
        # Flet 0.28.3 requires delay for proper control attachment
        await asyncio.sleep(0.3)  # Reasonable delay for control attachment
        if DEBUG:
            print("[DASH] setup → controls should now be fully attached")

        if not disposed:
            # Start progressive loading with page.run_task to avoid blocking UI
            if DEBUG:
                print("[DASH] setup → scheduling _start_progressive_loading")
            page.run_task(_start_progressive_loading)

        if not disposed:
            nonlocal auto_refresh_task
            if DEBUG:
                print("[DASH] setup → scheduling _auto_refresh_loop")
            auto_refresh_task = page.run_task(_auto_refresh_loop)

        # Proactively force an initial full refresh to populate all sections
        if not disposed:
            if DEBUG:
                print("[DASH] setup → scheduling initial _refresh")
            page.run_task(_refresh)

    async def _start_progressive_loading() -> None:
        DEBUG = os.environ.get("FLET_DASHBOARD_DEBUG") == "1"
        """Start progressive loading of dashboard data with phased updates."""
        if disposed:
            return

        try:
            if DEBUG:
                print("[DASH] _start_progressive_loading → Phase 1: critical metrics")
            # Phase 1: Critical metrics (server status, basic stats)
            await _load_critical_metrics()

            # Phase 2: Performance data (CPU, memory, database)
            if DEBUG:
                print("[DASH] _start_progressive_loading → Phase 2: performance data")
            await _load_performance_data()

            # Phase 3: Activity data (recent events)
            if DEBUG:
                print("[DASH] _start_progressive_loading → Phase 3: activity data")
            await _load_activity_data()

            if DEBUG:
                print("[DASH] _start_progressive_loading → Completed all phases")
        except Exception as e:
            show_error_message(page, f"Dashboard loading failed: {e}")

    async def _load_critical_metrics() -> None:
        DEBUG = os.environ.get("FLET_DASHBOARD_DEBUG") == "1"
        """Load critical metrics without blocking UI."""
        if disposed:
            return

        try:
            # _call_bridge is already async, so we just await it
            if DEBUG:
                print("[DASH] _load_critical_metrics → calling get_dashboard_summary")
            summary = await _call_bridge(server_bridge, "get_dashboard_summary")

            if summary and summary.get("success"):
                # Update UI with critical metrics
                payload = summary.get("data") or {}
                snapshot = DashboardSnapshot(
                    total_clients=int(payload.get("total_clients") or 0),
                    connected_clients=int(payload.get("connected_clients") or 0),
                    total_files=int(payload.get("total_files") or 0),
                    uptime_seconds=float(payload.get("uptime") or 0.0),
                    server_status=str(payload.get("server_status") or "offline"),
                    server_version=str(payload.get("server_version") or ""),
                )

                # Apply critical metrics to UI
                if DEBUG:
                    print("[DASH] _load_critical_metrics → applying snapshot")
                await _apply_snapshot(snapshot)
                if DEBUG:
                    print("[DASH] _load_critical_metrics → snapshot applied")
            else:
                if DEBUG:
                    print(f"[DASH] _load_critical_metrics → FAILED: {summary}")

        except Exception as e:
            print(f"Failed to load critical metrics: {e}")

    async def _load_performance_data() -> None:
        DEBUG = os.environ.get("FLET_DASHBOARD_DEBUG") == "1"
        """Load performance data without blocking UI."""
        if disposed:
            return

        try:
            # _call_bridge is already async, so we just await it
            if DEBUG:
                print("[DASH] _load_performance_data → calling get_performance_metrics")
            performance = await _call_bridge(server_bridge, "get_performance_metrics")

            if performance and performance.get("success"):
                # Merge performance data into a snapshot and apply via unified updater
                payload = performance.get("data") or {}

                # Build partial snapshot based on latest snapshot_ref to preserve existing values
                base = snapshot_ref or DashboardSnapshot()
                merged = DashboardSnapshot(
                    total_clients=base.total_clients,
                    connected_clients=base.connected_clients,
                    total_files=base.total_files,
                    uptime_seconds=base.uptime_seconds,
                    server_status=base.server_status,
                    server_version=base.server_version,
                    port=base.port,
                    cpu_usage=as_float(payload.get("cpu_usage_percent")),
                    memory_usage_mb=as_float(payload.get("memory_usage_mb")),
                    db_response_ms=as_int(payload.get("database_response_time_ms")),
                    active_connections=max(0, as_int(payload.get("active_connections")) or 0),
                    recent_activity=base.recent_activity,
                    errors=base.errors,
                )

                await _apply_snapshot(merged)
            else:
                if DEBUG:
                    print(f"[DASH] _load_performance_data → FAILED: {performance}")

        except Exception as e:
            print(f"Failed to load performance data: {e}")

    async def _load_activity_data() -> None:
        DEBUG = os.environ.get("FLET_DASHBOARD_DEBUG") == "1"
        """Load activity data without blocking UI."""
        if disposed:
            return

        try:
            # Try async version first
            if DEBUG:
                print("[DASH] _load_activity_data → calling get_recent_activity_async")
            activity = await _call_bridge(server_bridge, "get_recent_activity_async", 12)

            if not activity or not activity.get("success"):
                # Fallback to sync version
                if DEBUG:
                    print("[DASH] _load_activity_data → async failed, trying sync get_recent_activity")
                activity = await _call_bridge(server_bridge, "get_recent_activity", 12)

            if activity and activity.get("success"):
                data = activity.get("data")
                if isinstance(data, list):
                    # Merge activity into a snapshot and apply via unified updater
                    base = snapshot_ref or DashboardSnapshot()
                    merged = DashboardSnapshot(
                        total_clients=base.total_clients,
                        connected_clients=base.connected_clients,
                        total_files=base.total_files,
                        uptime_seconds=base.uptime_seconds,
                        server_status=base.server_status,
                        server_version=base.server_version,
                        port=base.port,
                        cpu_usage=base.cpu_usage,
                        memory_usage_mb=base.memory_usage_mb,
                        db_response_ms=base.db_response_ms,
                        active_connections=base.active_connections,
                        recent_activity=list(data[:12]),
                        errors=base.errors,
                    )
                    await _apply_snapshot(merged)
                else:
                    if DEBUG:
                        print("[DASH] _load_activity_data → success but no data")
            else:
                if DEBUG:
                    print(f"[DASH] _load_activity_data → FAILED: {activity}")

        except Exception as e:
            print(f"Failed to load activity data: {e}")

    def dispose() -> None:
        nonlocal disposed
        disposed = True
        stop_event.set()
        if auto_refresh_task and not auto_refresh_task.done():
            auto_refresh_task.cancel()

    # ============================================================================
    # SECTION 2.5: AGGRESSIVE VISIBILITY FIXES
    # Workarounds for Flet 0.28.3 rendering issues
    # ============================================================================

    def _force_rebuild_metrics_row(
        snapshot: DashboardSnapshot,
        metrics_config: list[tuple],
        metric_blocks: dict[str, dict[str, ft.Control]],
        navigate_callback: Callable[[str], None] | None,
        display_uptime_seconds: float,
    ) -> ft.ResponsiveRow:
        """Force complete rebuild of metrics row to ensure visibility in Flet 0.28.3."""
        DEBUG = os.environ.get("FLET_DASHBOARD_DEBUG") == "1"

        if DEBUG:
            print("[DASH] _force_rebuild_metrics_row → rebuilding all metric blocks")

        # Create new metric blocks with actual values
        new_metric_controls = []

        for key, title, subtitle, icon, accent, route in metrics_config:
            # Get the actual value to display
            if key == "total_clients":
                display_value = f"{snapshot.total_clients:,}" if snapshot.total_clients else "0"
                display_subtitle = subtitle
            elif key == "active_clients":
                display_value = f"{snapshot.connected_clients:,}" if snapshot.connected_clients else "0"
                ratio_text = f"{(snapshot.connected_clients / snapshot.total_clients) * 100:.0f}% online" if snapshot.total_clients > 0 else "Currently connected"
                display_subtitle = ratio_text
            elif key == "total_files":
                display_value = f"{snapshot.total_files:,}" if snapshot.total_files else "0"
                display_subtitle = subtitle
            elif key == "uptime":
                display_value = format_uptime(display_uptime_seconds)
                chip_level, chip_label = _derive_status(snapshot)
                display_subtitle = chip_label
            else:
                display_value = "0"
                display_subtitle = subtitle

            # Create Text control with the actual value (not placeholder)
            value_text = ft.Text(
                display_value,
                size=30,
                weight=ft.FontWeight.W_700,
                color=ft.Colors.ON_SURFACE
            )

            footnote_text = ft.Text(
                display_subtitle,
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT
            )

            # Build the metric block with real values
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

            card_content = ft.Container(
                content=body,
                padding=ft.padding.all(20),
                bgcolor=ft.Colors.SURFACE,
                border_radius=12,
                border=ft.border.only(top=ft.BorderSide(3, accent)),
                shadow=[ft.BoxShadow(
                    blur_radius=8,
                    spread_radius=1,
                    color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                    offset=ft.Offset(0, 2),
                )],
                animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            )

            # Add hover effect
            def on_hover(e):
                card_content.scale = 1.02 if e.data == "true" else 1.0
                card_content.update()

            card_content.on_hover = on_hover

            wrapper = ft.Container(
                content=card_content,
                col={"xs": 12, "sm": 6, "md": 3},
                on_click=(lambda _: navigate_callback(route)) if route and navigate_callback else None,
                ink=True if route and navigate_callback else False,
            )

            new_metric_controls.append(wrapper)

            # Update the metric_blocks reference
            block_data = {
                "wrapper": wrapper,
                "value_text": value_text,
                "footnote_text": footnote_text,
            }
            metric_blocks[key] = block_data

        # Create and return new ResponsiveRow
        new_metrics_row = ft.ResponsiveRow(new_metric_controls, spacing=12, run_spacing=12)

        if DEBUG:
            print(f"[DASH] _force_rebuild_metrics_row → created new row with {len(new_metric_controls)} blocks")

        return new_metrics_row

    return root, dispose, setup
