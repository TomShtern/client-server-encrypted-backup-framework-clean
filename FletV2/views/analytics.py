#!/usr/bin/env python3
"""Streamlined analytics view with executor-safe server access."""

from __future__ import annotations

import asyncio
import contextlib
import inspect
import logging
import os
import sys
from dataclasses import dataclass
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
    from theme import MODERATE_NEUMORPHIC_SHADOWS, PRONOUNCED_NEUMORPHIC_SHADOWS
except Exception:  # pragma: no cover - fallback for dev mode
    MODERATE_NEUMORPHIC_SHADOWS = []
    PRONOUNCED_NEUMORPHIC_SHADOWS = []


# ============================================================================
# SECTION 1: DATA FETCHING HELPERS
# ============================================================================

@dataclass(slots=True)
class AnalyticsData:
    total_backups: int = 0
    total_storage_gb: float = 0.0
    success_rate: float = 0.0
    avg_backup_size_gb: float = 0.0
    backup_trend: list[dict[str, Any]] | None = None
    client_storage: list[dict[str, Any]] | None = None
    file_type_distribution: list[dict[str, Any]] | None = None


async def fetch_analytics_data(bridge: Any | None) -> AnalyticsData:
    if not bridge:
        return AnalyticsData()

    result = await run_sync_in_executor(safe_server_call, bridge, "get_analytics_data")
    if not result.get("success"):
        logger.debug("Analytics fetch failed: %s", result.get("error"))
        return AnalyticsData()

    payload = result.get("data") or {}
    return AnalyticsData(
        total_backups=int(payload.get("total_backups", 0) or 0),
        total_storage_gb=float(payload.get("total_storage_gb", 0.0) or 0.0),
        success_rate=float(payload.get("success_rate", 0.0) or 0.0),
        avg_backup_size_gb=float(payload.get("avg_backup_size_gb", 0.0) or 0.0),
        backup_trend=list(payload.get("backup_trend") or []),
        client_storage=list(payload.get("client_storage") or []),
        file_type_distribution=list(payload.get("file_type_distribution") or []),
    )


# ============================================================================
# SECTION 2: BUSINESS LOGIC HELPERS
# ============================================================================

def _build_backup_trend_rows(data: list[dict[str, Any]] | None) -> list[list[str]]:
    rows: list[list[str]] = []
    if not data:
        return rows
    for item in data:
        rows.append([
            str(item.get("date") or item.get("label") or ""),
            str(item.get("count") or item.get("value") or 0),
        ])
    return rows


def _build_client_storage_rows(data: list[dict[str, Any]] | None) -> list[list[str]]:
    rows: list[list[str]] = []
    if not data:
        return rows
    for item in data:
        rows.append([
            str(item.get("client") or item.get("name") or ""),
            f"{float(item.get('storage_gb', 0.0) or 0.0):.2f} GB",
        ])
    return rows


def _build_file_type_rows(data: list[dict[str, Any]] | None) -> list[list[str]]:
    rows: list[list[str]] = []
    if not data:
        return rows
    for item in data:
        rows.append([
            str(item.get("type") or item.get("label") or "Unknown"),
            str(item.get("count") or item.get("value") or 0),
        ])
    return rows


# ============================================================================
# SECTION 3: UI BUILDERS
# ============================================================================

def _metric_card(title: str, value: str, subtitle: str, icon: str, color: str) -> ft.Control:
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(icon, size=28, color=color),
                ft.Text(title, size=14, color=ft.Colors.ON_SURFACE_VARIANT),
            ], spacing=12),
            ft.Text(value, size=30, weight=ft.FontWeight.BOLD),
            ft.Text(subtitle, size=12, color=ft.Colors.ON_SURFACE_VARIANT),
        ], spacing=8),
        padding=20,
        bgcolor=ft.Colors.SURFACE,
        border_radius=16,
        shadow=PRONOUNCED_NEUMORPHIC_SHADOWS,
    )


def _data_table(headers: list[str], rows: list[list[str]]) -> ft.Control:
    if not rows:
        return create_empty_state("No data", "Refresh to load analytics from the server.")

    header_row = ft.Row([
        ft.Text(label, weight=ft.FontWeight.BOLD, expand=True) for label in headers
    ], spacing=12)

    body_rows = [header_row, ft.Divider(height=1)]
    for row in rows:
        body_rows.append(
            ft.Row([
                ft.Text(cell, expand=True) for cell in row
            ], spacing=12)
        )

    return ft.Container(
        content=ft.Column(body_rows, spacing=8),
        padding=20,
        bgcolor=ft.Colors.SURFACE,
        border_radius=16,
        shadow=MODERATE_NEUMORPHIC_SHADOWS,
    )


# ============================================================================
# SECTION 4: MAIN VIEW
# ============================================================================

def create_analytics_view(
    server_bridge: Any | None,
    page: ft.Page,
    _state_manager: Any | None,
    navigate_callback: Callable[[str], None] | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    state = {
        "data": AnalyticsData(),
    }

    loading_overlay = create_loading_indicator("Loading analytics…")
    error_panel = ft.Container(visible=False)

    metrics_row = ft.ResponsiveRow([], spacing=16, run_spacing=16)
    trend_panel = ft.Container()
    storage_panel = ft.Container()
    file_type_panel = ft.Container()

    metrics_section = AppCard(metrics_row, title="Key metrics")
    trend_section = AppCard(trend_panel, title="Backup trend")
    storage_section = AppCard(storage_panel, title="Client storage")
    file_type_section = AppCard(file_type_panel, title="File types")

    trend_section.col = {"sm": 12, "md": 6, "lg": 4}
    storage_section.col = {"sm": 12, "md": 6, "lg": 4}
    file_type_section.col = {"sm": 12, "md": 12, "lg": 4}
    file_type_section.expand = True

    def apply_data(data: AnalyticsData) -> None:
        metrics_row.controls = [
            ft.Container(
                _metric_card("Total Backups", str(data.total_backups), "Jobs captured", ft.Icons.BACKUP_TABLE, ft.Colors.BLUE),
                col={"xs": 12, "sm": 12, "md": 6, "lg": 3},
            ),
            ft.Container(
                _metric_card("Total Storage", f"{data.total_storage_gb:.2f} GB", "Encrypted", ft.Icons.STORAGE, ft.Colors.GREEN),
                col={"xs": 12, "sm": 12, "md": 6, "lg": 3},
            ),
            ft.Container(
                _metric_card("Success Rate", f"{data.success_rate:.1f}%", "Completed successfully", ft.Icons.CHECK_CIRCLE_OUTLINE, ft.Colors.PURPLE),
                col={"xs": 12, "sm": 12, "md": 6, "lg": 3},
            ),
            ft.Container(
                _metric_card("Avg Backup Size", f"{data.avg_backup_size_gb:.2f} GB", "Median per job", ft.Icons.PIE_CHART_OUTLINE, ft.Colors.TEAL),
                col={"xs": 12, "sm": 12, "md": 6, "lg": 3},
            ),
        ]
        metrics_row.update()

        trend_panel.content = _data_table(["Period", "Backups"], _build_backup_trend_rows(data.backup_trend))
        storage_panel.content = _data_table(["Client", "Storage"], _build_client_storage_rows(data.client_storage))
        file_type_panel.content = _data_table(["Type", "Count"], _build_file_type_rows(data.file_type_distribution))
        for panel in (trend_panel, storage_panel, file_type_panel):
            panel.update()

    async def refresh_data(toast: bool = False) -> None:
        error_panel.visible = False
        error_panel.update()
        overlay_container.visible = True
        overlay_container.update()

        try:
            data = await fetch_analytics_data(server_bridge)
            state["data"] = data
            apply_data(data)
            if toast:
                show_success_snackbar(page, "Analytics refreshed")
        except Exception as exc:  # pragma: no cover - defensive UI feedback
            logger.exception("Analytics refresh failed")
            error_panel.content = AppCard(create_error_display(str(exc)), title="Error")
            error_panel.visible = True
            error_panel.update()
            show_error_snackbar(page, f"Analytics load failed: {exc}")
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
        schedule_task(lambda: refresh_data(toast=True))

    header = create_view_header(
        "Analytics",
        icon=ft.Icons.INSIGHTS,
        description="Understand backup performance and capacity usage.",
        actions=[create_action_button("Refresh", on_refresh, icon=ft.Icons.REFRESH)],
    )

    secondary_sections = ft.ResponsiveRow(
        [trend_section, storage_section, file_type_section],
        spacing=16,
        run_spacing=16,
    )

    content_column = ft.Column(
        [
            header,
            metrics_section,
            secondary_sections,
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
        await refresh_data()
        overlay_container.visible = False
        overlay_container.update()

    return stack, (lambda: None), setup
