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
from collections.abc import Callable, Coroutine, Iterable
from concurrent.futures import Future
from datetime import datetime
from typing import TYPE_CHECKING, Any

import flet as ft

if TYPE_CHECKING:
    from FletV2.main import AsyncManager

import Shared.utils.utf8_solution as _  # noqa: F401
from FletV2.components.log_card import LogCard
from FletV2.utils.async_helpers import debounce, run_sync_in_executor, safe_server_call
from FletV2.utils.data_export import export_to_csv, export_to_json, generate_export_filename
from FletV2.utils.loading_states import (
    create_empty_state,
    create_error_display,
    create_loading_indicator,
)
from FletV2.utils.simple_state import SimpleState
from FletV2.utils.ui_builders import (
    create_action_button,
    create_filter_dropdown,
    create_search_bar,
    create_view_header,
)
from FletV2.utils.ui_components import AppCard
from FletV2.utils.user_feedback import show_error_message, show_success_message

# Ensure repository roots are on sys.path for runtime resolution
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

logger = logging.getLogger(__name__)

try:
    from Shared.logging.flet_log_capture import get_flet_log_capture

    _flet_log_capture = get_flet_log_capture()
except Exception:  # pragma: no cover - log capture optional in GUI-only mode
    _flet_log_capture = None


# ============================================================================
# SECTION 1: DATA FETCHING HELPERS
# ============================================================================

async def fetch_server_logs_async(bridge: Any | None, _page: ft.Page) -> list[dict[str, Any]]:
    """Retrieve and normalize server logs without blocking the UI."""

    if not bridge:
        return []

    def blocking_operation():
        return safe_server_call(bridge, "get_logs")

    result = await run_sync_in_executor(blocking_operation)
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


async def fetch_app_logs_async(_page: ft.Page) -> list[dict[str, Any]]:
    """Fetch logs captured from the Flet application itself."""

    capture = _flet_log_capture
    if not capture:
        return []

    def blocking_operation():
        return capture.get_app_logs()

    try:
        app_logs = await run_sync_in_executor(blocking_operation)
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

    badges = [
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=10, color=ft.Colors.PRIMARY),
                ft.Text(f"{level}: {count}", size=12),
            ], spacing=6),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=8,
            bgcolor=ft.Colors.SURFACE,
        )
        for level, count in stats["by_level"].items()
    ]

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
    return [
        LogCard(entry, index=index, search_query=search_query, page=page)
        for index, entry in enumerate(logs)
    ]


# ============================================================================
# SECTION 3: LOGIC HELPERS
# ============================================================================

def _create_level_filter() -> ft.Control:
    """Create the level filter dropdown control."""
    return create_filter_dropdown(
        "Level",
        [("All", "All")],
        lambda __: None,
        value="All",
        width=200,
    )


def _create_filter_controls(
    level_filter: ft.Control,
    include_switch: ft.Switch,
    last_refresh_text: ft.Control,
    search_on_change: Callable[[ft.ControlEvent | str], None],
    on_refresh: Callable[[ft.ControlEvent], None],
) -> ft.ResponsiveRow:
    """Create the filter controls layout."""
    return ft.ResponsiveRow(
        controls=[
            ft.Container(content=create_search_bar(on_change=search_on_change, placeholder="Search logs…"),
                        col={"xs": 12, "sm": 8, "md": 6, "lg": 5}),
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


def _create_export_actions(handle_export: Callable[[str], None]) -> list[ft.Control]:
    """Create export action buttons."""
    return [
        create_action_button("Export CSV", lambda __: handle_export("csv"), icon=ft.Icons.DOWNLOAD),
        create_action_button("Export JSON", lambda __: handle_export("json"), icon=ft.Icons.CODE, primary=False),
    ]


def _create_main_content(
    header: ft.Control,
    stats_section: ft.Control,
    filter_section: ft.Control,
    error_container: ft.Container,
    logs_section: ft.Control,
) -> ft.Column:
    """Create the main content column."""
    return ft.Column(
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


# ============================================================================
# SECTION 4: EVENT HANDLERS
# ============================================================================

def _create_event_handlers(
    page: ft.Page,
    state: dict[str, Any],
    log_list_container: ft.Column,
    stats_container: ft.Container,
    level_filter: ft.Control,
    last_refresh_text: ft.Control,
) -> tuple[
    Callable[[str], None],
    Callable[[str | None], None],
    Callable[[bool], None],
    Callable[[], None],
]:
    """Create and return all event handlers."""

    def _safe_control_update(control: ft.Control | None) -> None:
        if control and getattr(control, "page", None):
            with contextlib.suppress(Exception):
                control.update()

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
        _safe_control_update(log_list_container)
        _safe_control_update(stats_container)
        _safe_control_update(level_filter)
        _safe_control_update(last_refresh_text)

    def handle_search(query: str) -> None:
        state["search_query"] = query
        apply_filters_and_render()

    def handle_level_change(value: str | None) -> None:
        state["selected_level"] = value or "All"
        apply_filters_and_render()

    def handle_include_toggle(value: bool) -> None:
        state["include_app_logs"] = value
        apply_filters_and_render()

    def handle_refresh() -> None:
        apply_filters_and_render()

    return handle_search, handle_level_change, handle_include_toggle, handle_refresh


# ============================================================================
# SECTION 5: MAIN VIEW FACTORY
# ============================================================================

# sourcery skip: high-cognitive-complexity


class _LogsViewController:
    def __init__(self, server_bridge: Any | None, page: ft.Page, async_manager: AsyncManager | None = None) -> None:
        self.server_bridge = server_bridge
        self.page = page
        self.async_manager = async_manager
        self.state = {
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

        self.disposed = False
        self.background_tasks: set[Any] = set()

        # UI components
        self.log_list_container = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.stats_container = ft.Container(expand=False)
        self.error_container = ft.Container(visible=False)
        self.level_filter = _create_level_filter()
        self.include_switch = ft.Switch(label="Include app logs", value=self.state["include_app_logs"])
        self.last_refresh_text = ft.Text("Last refresh: ?", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        self.loading_overlay = ft.Container(
            content=create_loading_indicator("Loading logs…"),
            visible=False,
            alignment=ft.alignment.center,
            expand=True,
        )

        (
            self.handle_search,
            self.handle_level_change,
            self.handle_include_toggle,
            self.handle_refresh,
        ) = _create_event_handlers(
            page,
            self.state,
            self.log_list_container,
            self.stats_container,
            self.level_filter,
            self.last_refresh_text,
        )

        self.debounced_search = debounce(0.4)(self._handle_search_async)

        # Wire events
        self.level_filter.on_change = self._on_level_change
        self.include_switch.on_change = self._on_include_change

        self.filters_layout = _create_filter_controls(
            self.level_filter,
            self.include_switch,
            self.last_refresh_text,
            self._on_search_change,
            self._on_refresh,
        )

        self.stats_section = AppCard(self.stats_container, title="Summary")
        self.filter_actions = _create_export_actions(self._handle_export)
        self.filter_section = AppCard(self.filters_layout, title="Filters", actions=self.filter_actions)
        self.logs_section = AppCard(self.log_list_container, title="Log entries")
        self.logs_section.expand = True

        self.header = create_view_header(
            "Logs",
            icon=ft.Icons.RECEIPT_LONG,
            description="Inspect server and GUI diagnostics.",
            actions=[create_action_button("Refresh", self._on_refresh, icon=ft.Icons.REFRESH)],
        )

        content_column = _create_main_content(
            self.header,
            self.stats_section,
            self.filter_section,
            self.error_container,
            self.logs_section,
        )

        main_layout = ft.Container(
            content=content_column,
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
            expand=True,
        )

        self.content_stack = ft.Stack([main_layout, self.loading_overlay], expand=True)

    # ------------------------------------------------------------------
    # Internal utilities
    # ------------------------------------------------------------------

    def _safe_update(self, control: ft.Control | None) -> None:
        if self.disposed or not control:
            return
        if getattr(control, "page", None):
            with contextlib.suppress(Exception):
                control.update()

    async def _handle_search_async(self, query: str) -> None:
        await asyncio.sleep(0)
        self.handle_search(query)

    async def _execute_task_source(self, task_source: Any) -> None:
        if inspect.isawaitable(task_source):
            await task_source
            return

        if callable(task_source):
            result = task_source()
            if inspect.isawaitable(result):
                await result

    async def _run_task(self, task_source: Any) -> None:
        if self.disposed:
            return
        try:
            await self._execute_task_source(task_source)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Logs background task failed")

    def _schedule_task(self, task_source: Any) -> None:
        if self.disposed:
            return

        async def runner() -> None:
            await self._run_task(task_source)

        scheduled: asyncio.Task[Any] | Future[Any] | None = None

        try:
            if hasattr(self.page, "run_task"):
                scheduled = self.page.run_task(runner)
            else:
                scheduled = asyncio.create_task(runner())
        except AssertionError:
            scheduled = asyncio.create_task(runner())
        except RuntimeError as exc:
            message = str(exc).lower()
            if "shutdown" in message or "closed" in message:
                logger.debug("Skipping log task scheduling after loop shutdown: %s", exc)
                return
            raise

        if scheduled is None:
            return

        self.background_tasks.add(scheduled)

        def _cleanup(fut: Any) -> None:
            self.background_tasks.discard(fut)

        scheduled.add_done_callback(_cleanup)

    # ------------------------------------------------------------------
    # Event bridges
    # ------------------------------------------------------------------

    def _on_search_change(self, event: ft.ControlEvent | str) -> None:
        value = event if isinstance(event, str) else getattr(getattr(event, "control", None), "value", "")
        self._schedule_task(lambda: self.debounced_search(value or ""))

    def _on_level_change(self, event: ft.ControlEvent) -> None:
        self._schedule_task(lambda: self.handle_level_change(event.control.value))

    def _on_include_change(self, event: ft.ControlEvent) -> None:
        self._schedule_task(lambda: self.handle_include_toggle(bool(event.control.value)))

    def _on_refresh(self, _event: ft.ControlEvent | None = None) -> None:
        self._schedule_task(lambda: self.refresh_logs(toast=True))

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    async def refresh_logs(self, initial: bool = False, toast: bool = False) -> None:
        if self.disposed:
            return

        # Check for cancellation before starting operation
        if self.async_manager and self.async_manager.is_cancelled():
            logger.debug("[LOGS] Refresh cancelled before operation")
            return

        self.error_container.visible = False
        self.loading_overlay.visible = True
        self._safe_update(self.error_container)
        self._safe_update(self.loading_overlay)

        try:
            # Check for cancellation before expensive operations
            if self.async_manager and self.async_manager.is_cancelled():
                logger.debug("[LOGS] Refresh cancelled before expensive operations")
                return

            server_task = fetch_server_logs_async(self.server_bridge, self.page)
            app_task = fetch_app_logs_async(self.page)
            server_logs, app_logs = await asyncio.gather(server_task, app_task)

            # Check for cancellation after expensive operations
            if self.async_manager and self.async_manager.is_cancelled():
                logger.debug("[LOGS] Refresh cancelled after expensive operations")
                return

            self.state["server_logs"] = server_logs
            self.state["app_logs"] = app_logs
            self.state["last_refresh"] = datetime.now()

            self.handle_refresh()

            if toast and not initial:
                show_success_message(self.page, "Logs refreshed")
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # pragma: no cover - defensive UI feedback
            logger.exception("Failed to refresh logs")
            self.error_container.content = AppCard(create_error_display(str(exc)), title="Error")
            self.error_container.visible = True
            self._safe_update(self.error_container)
            show_error_message(self.page, f"Failed to refresh logs: {exc}")
        finally:
            self.loading_overlay.visible = False
            self._safe_update(self.loading_overlay)

    def _handle_export(self, format_type: str) -> None:
        logs = self.state["filtered_logs"]
        if not logs:
            show_error_message(self.page, "No logs to export")
            return

        filename = generate_export_filename("logs", format_type)
        try:
            if format_type == "csv":
                export_to_csv(logs, filename)
            elif format_type == "json":
                export_to_json(logs, filename)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
            show_success_message(self.page, f"Exported {len(logs)} logs to {filename}")
        except Exception as exc:  # pragma: no cover - defensive UI feedback
            show_error_message(self.page, f"Export failed: {exc}")

    # ------------------------------------------------------------------
    # Lifecycle hooks
    # ------------------------------------------------------------------

    def dispose(self) -> None:
        if self.disposed:
            return
        self.disposed = True

        # Use AsyncManager to cancel tasks if available
        if self.async_manager:
            self.async_manager.cancel_all()

        with contextlib.suppress(AttributeError):
            self.level_filter.on_change = None
        with contextlib.suppress(AttributeError):
            self.include_switch.on_change = None

        for task in tuple(self.background_tasks):
            if hasattr(task, "cancel") and not task.done():
                task.cancel()
        self.background_tasks.clear()

    async def setup(self) -> None:
        await self.refresh_logs(initial=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
        return self.content_stack, self.dispose, self.setup


def create_logs_view(
    server_bridge: Any | None,
    page: ft.Page,
    _state_manager: SimpleState | None = None,
    async_manager: AsyncManager | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    controller = _LogsViewController(server_bridge, page, async_manager)
    return controller.build()
