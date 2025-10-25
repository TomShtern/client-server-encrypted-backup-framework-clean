#!/usr/bin/env python3
"""Modularized enhanced logs view with async-safe server integration."""

from __future__ import annotations

import asyncio
import contextlib
import inspect
import logging
import os
import re
import sys
from datetime import datetime
from typing import Any, Callable, Coroutine, Iterable

import flet as ft

# Ensure repository roots are on sys.path for runtime resolution
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import Shared.utils.utf8_solution as _  # noqa: F401

from FletV2.components.log_card import LogCard
from FletV2.utils.async_helpers import debounce
from FletV2.utils.data_export import export_to_csv, export_to_json, generate_export_filename
from FletV2.utils.loading_states import (
    create_empty_state,
    create_error_display,
    create_loading_indicator,
)
from FletV2.utils.user_feedback import show_error_message, show_success_message
from FletV2.utils.ui_builders import (
    create_action_button,
    create_filter_dropdown,
    create_search_bar,
    create_view_header,
)
from FletV2.utils.ui_components import AppCard

logger = logging.getLogger(__name__)

try:
    from Shared.logging.flet_log_capture import get_flet_log_capture

    _flet_log_capture = get_flet_log_capture()
except Exception:  # pragma: no cover - log capture optional in GUI-only mode
    _flet_log_capture = None


# ============================================================================
# SECTION 1: DATA FETCHING HELPERS
# ============================================================================

async def fetch_server_logs_async(bridge: Any | None, page: ft.Page) -> list[dict[str, Any]]:
    """Retrieve and normalize server logs without blocking the UI."""

    if not bridge:
        return []

    def blocking_operation():
        return safe_server_call(bridge, "get_logs")

    result = await page.run_thread(blocking_operation)
    if not result.get("success"):
        logger.debug("Server log fetch failed: %s", result.get("error"))
        return []

    data = result.get("data", {})
    if isinstance(data, dict):
        raw_logs: Iterable[Any] = data.get("logs", []) or []
    elif isinstance(data, list):
        raw_logs = data
    else:
        raw_logs = []

    return [_normalize_log_entry(item, "Server") for item in raw_logs]


async def fetch_app_logs_async(page: ft.Page) -> list[dict[str, Any]]:
    """Fetch logs captured from the Flet application itself."""

    if not _flet_log_capture:
        return []

    def blocking_operation():
        return _flet_log_capture.get_app_logs()

    try:
        app_logs = await page.run_thread(blocking_operation)
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.debug("App log fetch failed: %s", exc)
        return []

    return [_normalize_log_entry(item, "GUI") for item in app_logs]


def _normalize_log_entry(raw: Any, source: str) -> dict[str, Any]:
    """Convert raw log structures into a consistent dictionary format."""

    if isinstance(raw, dict):
        return {
            "time": str(raw.get("time") or raw.get("timestamp") or ""),
            "level": str(raw.get("level") or raw.get("severity") or "INFO"),
            "component": str(raw.get("component") or raw.get("module") or source),
            "message": str(raw.get("message") or raw.get("msg") or ""),
            "source": source,
        }

    if isinstance(raw, str):
        parts = raw.split(" - ", 2)
        if len(parts) >= 3:
            return {
                "time": parts[0].strip(),
                "level": parts[1].strip(),
                "message": parts[2].strip(),
                "component": source,
                "source": source,
            }
        return {
            "time": "",
            "level": "INFO",
            "message": raw,
            "component": source,
            "source": source,
        }

    return {
        "time": "",
        "level": "INFO",
        "message": str(raw),
        "component": source,
        "source": source,
    }


def _determine_levels(logs: Iterable[dict[str, Any]]) -> list[str]:
    return sorted({entry.get("level", "INFO") for entry in logs if entry.get("level")})


def _filter_by_level(logs: list[dict[str, Any]], level: str) -> list[dict[str, Any]]:
    if level == "All":
        return logs
    return [entry for entry in logs if entry.get("level") == level]


def _filter_by_query(logs: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    if not query:
        return logs

    regex = _compile_search_regex(query)
    return [entry for entry in logs if regex.search(entry.get("message", "")) or regex.search(entry.get("component", ""))]


def _compile_search_regex(query: str) -> re.Pattern[str]:
    if not query:
        return re.compile("")

    if query.startswith("/") and query.count("/") >= 2:
        parts = query.split("/")
        pattern = parts[1]
        flag_tokens = parts[2] if len(parts) > 2 else ""
        flags = 0
        if "i" in flag_tokens:
            flags |= re.IGNORECASE
        if "m" in flag_tokens:
            flags |= re.MULTILINE
        if "s" in flag_tokens:
            flags |= re.DOTALL
        with contextlib.suppress(re.error):
            return re.compile(pattern, flags)

    return re.compile(re.escape(query), re.IGNORECASE)


def _parse_timestamp(value: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S,%f"):
        with contextlib.suppress(ValueError):
            return datetime.strptime(value, fmt)
    return datetime.min


def _calculate_statistics(logs: list[dict[str, Any]]) -> dict[str, Any]:
    stats = {"total": len(logs), "by_level": {}}
    for entry in logs:
        level = entry.get("level", "INFO")
        stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
    return stats


# ============================================================================
# SECTION 2: UI BUILDERS
# ============================================================================

def _build_stats_view(stats: dict[str, Any]) -> ft.Control:
    if not stats["total"]:
        return ft.Container()

    badges = []
    for level, count in stats["by_level"].items():
        badges.append(
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CIRCLE, size=10, color=ft.Colors.PRIMARY),
                    ft.Text(f"{level}: {count}", size=12),
                ], spacing=6),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=8,
                bgcolor=ft.Colors.SURFACE,
            )
        )

    return ft.Container(
        content=ft.Row([
            ft.Text(f"Total logs: {stats['total']}", size=14, weight=ft.FontWeight.BOLD),
            ft.VerticalDivider(width=1),
            *badges,
        ], spacing=10, wrap=True),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=12,
        bgcolor=ft.Colors.SURFACE,
    )


def _render_log_controls(logs: list[dict[str, Any]], search_query: str, page: ft.Page) -> list[ft.Control]:
    controls: list[ft.Control] = []
    for index, entry in enumerate(logs):
        controls.append(LogCard(entry, index=index, search_query=search_query, page=page))
    return controls


# ============================================================================
# SECTION 3: MAIN VIEW FACTORY
# ============================================================================

def create_logs_view(
    server_bridge: Any | None,
    page: ft.Page,
    _state_manager: Any | None,
    navigate_callback: Callable[[str], None] | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    state = {
        "server_logs": [],
        "app_logs": [],
        "filtered_logs": [],
        "search_query": "",
        "selected_level": "All",
        "available_levels": [],
        "include_app_logs": bool(_flet_log_capture),
        "stats": {"total": 0, "by_level": {}},
        "last_refresh": None,
    }

    log_list_container = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    stats_container = ft.Container(expand=False)
    error_container = ft.Container(visible=False)

    level_filter = create_filter_dropdown(
        "Level",
        [("All", "All")],
        lambda _e: None,
        value="All",
        width=200,
    )

    include_switch = ft.Switch(label="Include app logs", value=state["include_app_logs"])
    last_refresh_text = ft.Text("Last refresh: ?", size=12, color=ft.Colors.ON_SURFACE_VARIANT)

    loading_overlay = ft.Container(
        content=create_loading_indicator("Loading logs…"),
        visible=False,
        alignment=ft.alignment.center,
        expand=True,
    )

    def apply_filters_and_render() -> None:
        combined = list(state["server_logs"])
        if state["include_app_logs"]:
            combined.extend(state["app_logs"])

        combined.sort(key=lambda entry: _parse_timestamp(entry.get("time", "")), reverse=True)

        state["available_levels"] = _determine_levels(combined)
        available_with_all = ["All", *state["available_levels"]]
        if state["selected_level"] not in available_with_all:
            state["selected_level"] = "All"

        filtered = _filter_by_level(combined, state["selected_level"])
        filtered = _filter_by_query(filtered, state["search_query"])

        state["filtered_logs"] = filtered
        state["stats"] = _calculate_statistics(filtered)

        # Batch UI updates for better performance
        log_list_container.controls.clear()
        if filtered:
            log_list_container.controls.extend(_render_log_controls(filtered, state["search_query"], page))
        else:
            log_list_container.controls.append(create_empty_state("No logs", "Adjust filters or refresh to load logs."))

        stats_container.content = _build_stats_view(state["stats"])

        level_filter.options = [ft.dropdown.Option(value) for value in available_with_all]
        level_filter.value = state["selected_level"]

        if state["last_refresh"]:
            last_refresh_text.value = state["last_refresh"].strftime("Last refresh: %Y-%m-%d %H:%M:%S")
        else:
            last_refresh_text.value = "Last refresh: ?"

        # Batch update all controls to minimize redraw operations
        log_list_container.update()
        stats_container.update()
        level_filter.update()
        last_refresh_text.update()

    async def refresh_logs(initial: bool = False, toast: bool = False) -> None:
        # Batch initial UI updates
        error_container.visible = False
        loading_overlay.visible = True
        error_container.update()
        loading_overlay.update()

        try:
            server_task = fetch_server_logs_async(server_bridge, page)
            app_task = fetch_app_logs_async(page)
            server_logs, app_logs = await asyncio.gather(server_task, app_task)

            state["server_logs"] = server_logs
            state["app_logs"] = app_logs
            state["last_refresh"] = datetime.now()

            apply_filters_and_render()

            if toast and not initial:
                show_success_message(page, "Logs refreshed")
        except Exception as exc:  # pragma: no cover - defensive UI feedback
            logger.exception("Failed to refresh logs")
            error_container.content = AppCard(create_error_display(str(exc)), title="Error")
            error_container.visible = True
            error_container.update()
            show_error_message(page, f"Failed to refresh logs: {exc}")
        finally:
            # Batch final UI updates
            loading_overlay.visible = False
            loading_overlay.update()

    async def handle_search(query: str) -> None:
        state["search_query"] = query
        apply_filters_and_render()

    async def handle_level_change(value: str | None) -> None:
        state["selected_level"] = value or "All"
        apply_filters_and_render()

    async def handle_include_toggle(value: bool) -> None:
        state["include_app_logs"] = value
        apply_filters_and_render()

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

    debounced_search = debounce(0.4)(handle_search)

    def on_search_change(event: ft.ControlEvent) -> None:
        schedule_task(debounced_search(event.control.value or ""))

    def on_level_change(event: ft.ControlEvent) -> None:
        schedule_task(handle_level_change(event.control.value))

    def on_include_change(event: ft.ControlEvent) -> None:
        schedule_task(handle_include_toggle(bool(event.control.value)))

    def on_refresh(event: ft.ControlEvent) -> None:
        schedule_task(lambda: refresh_logs(toast=True))

    def handle_export(format_type: str) -> None:
        logs = state["filtered_logs"]
        if not logs:
            show_error_message(page, "No logs to export")
            return

        filename = generate_export_filename("logs", format_type)
        try:
            if format_type == "csv":
                export_to_csv(logs, filename)
            elif format_type == "json":
                export_to_json(logs, filename)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
            show_success_message(page, f"Exported {len(logs)} logs to {filename}")
        except Exception as exc:  # pragma: no cover - defensive UI feedback
            show_error_message(page, f"Export failed: {exc}")

    search_field = create_search_bar(on_change=on_search_change, placeholder="Search logs…")

    level_filter.on_change = on_level_change
    include_switch.on_change = on_include_change

    filters_layout = ft.ResponsiveRow(
        controls=[
            ft.Container(content=search_field, col={"xs": 12, "sm": 8, "md": 6, "lg": 5}),
            ft.Container(content=level_filter, col={"xs": 12, "sm": 4, "md": 3, "lg": 2}),
            ft.Container(
                content=include_switch,
                col={"xs": 12, "sm": 6, "md": 3, "lg": 2},
                alignment=ft.alignment.center_left,
            ),
            ft.Container(
                content=create_action_button("Refresh", on_refresh, icon=ft.Icons.REFRESH, primary=False),
                col={"xs": 12, "sm": 6, "md": 3, "lg": 2},
                alignment=ft.alignment.center_left,
            ),
            ft.Container(
                content=last_refresh_text,
                padding=ft.padding.only(left=4),
                col={"xs": 12, "sm": 12, "md": 6, "lg": 3},
                alignment=ft.alignment.center_left,
            ),
        ],
        spacing=12,
        run_spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    filter_actions = [
        create_action_button("Export CSV", lambda _: handle_export("csv"), icon=ft.Icons.DOWNLOAD),
        create_action_button("Export JSON", lambda _: handle_export("json"), icon=ft.Icons.CODE, primary=False),
    ]

    stats_section = AppCard(stats_container, title="Summary")
    filter_section = AppCard(filters_layout, title="Filters", actions=filter_actions)
    logs_section = AppCard(log_list_container, title="Log entries")
    logs_section.expand = True

    header = create_view_header(
        "Logs",
        icon=ft.Icons.RECEIPT_LONG,
        description="Inspect server and GUI diagnostics.",
        actions=[create_action_button("Refresh", on_refresh, icon=ft.Icons.REFRESH)],
    )

    content_column = ft.Column(
        [
            header,
            stats_section,
            filter_section,
            error_container,
            logs_section,
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

    content_stack = ft.Stack([main_layout, loading_overlay], expand=True)

    async def setup() -> None:
        await refresh_logs(initial=True)

    return content_stack, (lambda: None), setup
