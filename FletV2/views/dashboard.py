#!/usr/bin/env python3
"""Modern dashboard view with modular sections and async-safe server access."""

from __future__ import annotations

import asyncio
import contextlib
import inspect
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Coroutine

import flet as ft

# Ensure repository roots are on sys.path for runtime resolution
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import Shared.utils.utf8_solution as _  # noqa: F401

from FletV2.utils.async_helpers import run_sync_in_executor, safe_server_call
from FletV2.utils.data_export import generate_export_filename, export_to_csv
from FletV2.utils.loading_states import (
    create_empty_state,
    create_error_display,
    create_loading_indicator,
    show_error_snackbar,
    show_success_snackbar,
)
from FletV2.utils.ui_builders import create_action_button, create_view_header
from FletV2.utils.ui_components import AppCard

logger = logging.getLogger(__name__)

try:
    from theme import (
        PRONOUNCED_NEUMORPHIC_SHADOWS,
        MODERATE_NEUMORPHIC_SHADOWS,
        GLASS_SUBTLE,
    )
except Exception:  # pragma: no cover - theme fallbacks in dev mode
    PRONOUNCED_NEUMORPHIC_SHADOWS = []
    MODERATE_NEUMORPHIC_SHADOWS = []
    GLASS_SUBTLE = {"blur": 12, "bg_opacity": 0.1, "border_opacity": 0.15}


# ============================================================================
# SECTION 1: DATA FETCHING HELPERS
# ============================================================================

@dataclass(slots=True)
class DashboardData:
    total_clients: int = 0
    total_files: int = 0
    storage_gb: float = 0.0
    uptime_seconds: float = 0.0
    recent_activity: list[dict[str, Any]] | None = None
    cpu_usage: float | None = None
    memory_usage: float | None = None
    status: str = "offline"


async def fetch_dashboard_summary(bridge: Any | None) -> DashboardData:
    if not bridge:
        return DashboardData()

    summary_result = await run_sync_in_executor(safe_server_call, bridge, "get_dashboard_summary")
    status_result = await run_sync_in_executor(safe_server_call, bridge, "get_system_status")
    activity_result = await run_sync_in_executor(safe_server_call, bridge, "get_recent_activity", 12)

    data = DashboardData()

    if summary_result.get("success"):
        payload = summary_result.get("data") or {}
        data.total_clients = int(payload.get("total_clients", 0) or 0)
        data.total_files = int(payload.get("total_files", 0) or 0)
        data.storage_gb = float(payload.get("storage_gb", 0.0) or 0.0)

    if status_result.get("success"):
        payload = status_result.get("data") or {}
        data.uptime_seconds = float(payload.get("uptime_seconds", 0.0) or 0.0)
        data.cpu_usage = _safe_percent(payload.get("cpu_usage"))
        data.memory_usage = _safe_percent(payload.get("memory_usage"))
        data.status = str(payload.get("status", "offline"))

    if activity_result.get("success"):
        data.recent_activity = activity_result.get("data") or []

    return data


def _safe_percent(value: Any) -> float | None:
    with contextlib.suppress(TypeError, ValueError):
        number = float(value)
        if number < 0:
            return 0.0
        if number > 100:
            number = 100.0
        return number
    return None


# ============================================================================
# SECTION 2: BUSINESS LOGIC HELPERS
# ============================================================================

def format_uptime(seconds: float) -> str:
    if seconds <= 0:
        return "?"
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


def build_metric_rows(data: DashboardData) -> list[dict[str, Any]]:
    return [
        {
            "title": "Clients",
            "value": str(data.total_clients),
            "subtitle": "Registered",
            "icon": ft.Icons.PEOPLE_ALT_OUTLINED,
            "intent": ft.Colors.PRIMARY,
        },
        {
            "title": "Files",
            "value": str(data.total_files),
            "subtitle": "Backed up",
            "icon": ft.Icons.INSERT_DRIVE_FILE_OUTLINED,
            "intent": ft.Colors.BLUE,
        },
        {
            "title": "Storage",
            "value": f"{data.storage_gb:.2f} GB",
            "subtitle": "Encrypted",
            "icon": ft.Icons.CLOUD_OUTLINED,
            "intent": ft.Colors.TEAL,
        },
        {
            "title": "Uptime",
            "value": format_uptime(data.uptime_seconds),
            "subtitle": "Runtime",
            "icon": ft.Icons.SCHEDULE,
            "intent": ft.Colors.GREEN,
        },
    ]


def build_activity_rows(activity: list[dict[str, Any]] | None) -> list[list[str]]:
    if not activity:
        return []
    return [
        [
            str(item.get("timestamp") or item.get("time") or ""),
            str(item.get("client") or item.get("actor") or "System"),
            str(item.get("action") or item.get("event") or ""),
        ]
        for item in activity
    ]


# ============================================================================
# SECTION 3: UI BUILDERS
# ============================================================================

def _metric_card(config: dict[str, Any]) -> ft.Control:
    return ft.Container(
        content=ft.Column(
            [
                ft.Row([
            ft.Icon(config["icon"], size=28, color=config["intent"]),
                    ft.Text(config["title"], size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                ], spacing=12),
                ft.Text(config["value"], size=30, weight=ft.FontWeight.BOLD),
                ft.Text(config["subtitle"], size=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ],
            spacing=8,
        ),
        bgcolor=ft.Colors.SURFACE,
        padding=20,
        border_radius=16,
        shadow=PRONOUNCED_NEUMORPHIC_SHADOWS,
    )


def _status_chip(label: str, status: str) -> ft.Control:
    color_map = {
        "online": ft.Colors.GREEN,
        "degraded": ft.Colors.AMBER,
        "offline": ft.Colors.RED,
    }
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.CIRCLE, size=10, color=color_map.get(status, ft.Colors.BLUE)),
            ft.Text(label, size=12),
        ], spacing=6),
        padding=ft.padding.symmetric(horizontal=10, vertical=6),
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(0.08, color_map.get(status, ft.Colors.BLUE)),
    )


def _activity_table(rows: list[list[str]]) -> ft.Control:
    if not rows:
        return create_empty_state("No recent activity", "Operations will appear here once the server starts sending events.")

    header = ft.Row([
        ft.Text("Timestamp", weight=ft.FontWeight.BOLD, width=180),
        ft.Text("Client", weight=ft.FontWeight.BOLD, width=160),
        ft.Text("Action", weight=ft.FontWeight.BOLD, expand=True),
    ], spacing=12)

    items = [header, ft.Divider(height=1)] + [
        ft.Row([
            ft.Text(timestamp, width=180),
            ft.Text(actor, width=160),
            ft.Text(action, expand=True),
        ], spacing=12)
        for timestamp, actor, action in rows
    ]
    return ft.Column(items, spacing=8)


# ============================================================================
# SECTION 4: MAIN VIEW
# ============================================================================

def create_dashboard_view(
    server_bridge: Any | None,
    page: ft.Page,
    _state_manager: Any | None,
    navigate_callback: Callable[[str], None] | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    state = {
        "data": DashboardData(),
        "loading": False,
        "error": None,
    }

    metrics_row = ft.ResponsiveRow([], spacing=16, run_spacing=16)
    status_row = ft.Row([], spacing=12, wrap=True, vertical_alignment=ft.CrossAxisAlignment.CENTER)
    activity_column = ft.Column([], spacing=12)
    loading_overlay = create_loading_indicator("Fetching dashboard data…")
    error_panel = ft.Container(visible=False)

    metrics_section = AppCard(metrics_row, title="Key metrics")
    status_section = AppCard(status_row, title="System health")
    activity_section = AppCard(activity_column, title="Recent activity")
    activity_section.expand = True

    def apply_data(data: DashboardData) -> None:
        metrics_row.controls = [
            ft.Container(
                content=_metric_card(config),
                col={"sm": 12, "md": 6, "lg": 3},
            )
            for config in build_metric_rows(data)
        ]
        metrics_row.update()

        status_controls: list[ft.Control] = [
            _status_chip("Server", data.status.lower()),
        ]
        if data.cpu_usage is not None:
            status_controls.append(
                _status_chip(
                    f"CPU {data.cpu_usage:.1f}%",
                    "degraded" if data.cpu_usage > 80 else "online",
                )
            )
        if data.memory_usage is not None:
            status_controls.append(
                _status_chip(
                    f"RAM {data.memory_usage:.1f}%",
                    "degraded" if data.memory_usage > 80 else "online",
                )
            )
        status_row.controls = status_controls
        status_row.update()

        activity_rows = build_activity_rows(data.recent_activity)
        activity_column.controls = [
            _activity_table(activity_rows)
        ]
        activity_column.update()

    async def refresh_dashboard(toast: bool = False) -> None:
        error_panel.visible = False
        error_panel.update()
        overlay_container.visible = True
        overlay_container.update()

        try:
            data = await fetch_dashboard_summary(server_bridge)
            state["data"] = data
            apply_data(data)
            if toast:
                show_success_snackbar(page, "Dashboard refreshed")
        except Exception as exc:  # pragma: no cover - defensive UI feedback
            logger.exception("Dashboard refresh failed")
            error_panel.content = AppCard(create_error_display(str(exc)), title="Error")
            error_panel.visible = True
            error_panel.update()
            show_error_snackbar(page, f"Dashboard load failed: {exc}")
        finally:
            overlay_container.visible = False
            overlay_container.update()

    def schedule_task(task: Any) -> None:
        async def runner() -> None:
            if inspect.isawaitable(task):
                await task
                return
            result = task()
            if inspect.isawaitable(result):
                await result

        if hasattr(page, "run_task"):
            page.run_task(runner)
        else:
            asyncio.get_event_loop().create_task(runner())

    def on_refresh(event: ft.ControlEvent) -> None:
        schedule_task(lambda: refresh_dashboard(toast=True))

    def on_export(event: ft.ControlEvent) -> None:
        data = state["data"].recent_activity or []
        if not data:
            show_error_snackbar(page, "No activity to export")
            return
        filename = generate_export_filename("activity", "csv")
        try:
            export_rows = build_activity_rows(data)
            export_to_csv([
                {"timestamp": r[0], "client": r[1], "action": r[2]}
                for r in export_rows
            ], filename)
            show_success_snackbar(page, f"Exported activity to {filename}")
        except Exception as exc:  # pragma: no cover - defensive path
            show_error_snackbar(page, f"Export failed: {exc}")

    header_actions = [
        create_action_button("Refresh", on_refresh, icon=ft.Icons.REFRESH),
        create_action_button(
            "Export activity",
            on_export,
            icon=ft.Icons.DOWNLOAD,
            primary=False,
        ),
    ]

    header = create_view_header(
        "System dashboard",
        icon=ft.Icons.DASHBOARD,
        description="Live overview of clients, storage, and recent operations.",
        actions=header_actions,
    )

    content_column = ft.Column(
        [
            header,
            metrics_section,
            status_section,
            activity_section,
            error_panel,
        ],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    main_layout = ft.Container(
        content=content_column,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        expand=True,
    )

    stack = ft.Stack([
        main_layout,
        ft.Container(
            content=loading_overlay,
            alignment=ft.alignment.center,
            expand=True,
            visible=False,
        ),
    ], expand=True)
    overlay_container = stack.controls[1]

    async def setup() -> None:
        overlay_container.visible = True
        overlay_container.update()
        await refresh_dashboard()
        overlay_container.visible = False
        overlay_container.update()

    return stack, (lambda: None), setup
