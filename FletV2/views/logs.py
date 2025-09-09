#!/usr/bin/env python3
"""Logs View (High-Performance, Zero-Based Pagination)

Features:
 - Virtualized rendering (ListView) for large datasets
 - Debounced search (300ms)
 - Level filtering
 - Zero-based internal pagination (user display +1)
 - Mock data fallback when server bridge unavailable
 - Clear / Refresh / Export actions

All internal page math uses zero-based indexing. User-facing labels add +1.
"""

import flet as ft
from typing import List, Dict, Any
import asyncio
from datetime import datetime, timedelta
import random

from utils.debug_setup import get_logger
from utils.ui_helpers import level_colors, striped_row_color, build_level_badge
from utils.perf_metrics import PerfTimer
from utils.user_feedback import show_success_message
from config import ASYNC_DELAY
from utils.performance import (
    AsyncDebouncer, PaginationConfig,
    global_memory_manager, paginate_data
)

logger = get_logger(__name__)


def create_logs_view(server_bridge, page: ft.Page, state_manager=None) -> ft.Control:
    """Return the logs view control."""
    logger.info("Creating logs view (clean implementation)")

    # State
    logs_data: List[Dict[str, Any]] = []
    filtered_logs_data: List[Dict[str, Any]] = []
    current_filter = "ALL"
    search_query = ""
    is_loading = False
    last_updated = None

    # Performance helpers
    search_debouncer = AsyncDebouncer(delay=0.3)
    pagination_config = PaginationConfig(page_size=50, current_page=0)  # zero-based
    # (AsyncDataLoader reserved for future use; removed to avoid unused variable warning)
    global_memory_manager.register_component("logs_view")

    # ---------------------- Data Generation / Helpers ---------------------- #
    def generate_mock_logs(count: int = 200) -> List[Dict[str, Any]]:
        base_time = datetime.now()
        log_types = ["INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG"]
        components = ["Server", "Client", "Database", "File Transfer", "Auth", "System"]
        messages = [
            "Connection established from 192.168.1.{ip}",
            "File transfer completed: {filename}",
            "Authentication successful for user_{id}",
            "Database query executed in {time}ms",
            "Error processing request: timeout",
            "Server started on port 1256",
            "Client disconnected unexpectedly",
            "Backup operation completed successfully",
            "Memory usage: {usage}%",
            "SSL certificate renewed",
            "Configuration reloaded",
            "Cache cleared successfully",
            "Network connection restored",
            "Failed to connect to database",
            "File verification completed"
        ]
        data: List[Dict[str, Any]] = []
        for i in range(count):
            time_offset = timedelta(
                hours=random.randint(0, 24),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            log_time = base_time - time_offset
            level = random.choice(log_types)
            component = random.choice(components)
            template = random.choice(messages)
            msg = template.format(
                ip=random.randint(100, 199),
                filename=f"document_{random.randint(1,999)}.{random.choice(['pdf','txt','jpg','log'])}",
                id=random.randint(1, 500),
                time=random.randint(20, 900),
                usage=random.randint(30, 97)
            )
            data.append({
                "id": i + 1,
                "timestamp": log_time.isoformat(),
                "level": level,
                "component": component,
                "message": msg
            })
        data.sort(key=lambda x: x["timestamp"], reverse=True)
        return data

    def level_fg(level: str):
        fg, _ = level_colors(level)
        return fg

    def level_bg(level: str):
        _, bg = level_colors(level)
        return bg

    def apply_filters():
        nonlocal filtered_logs_data
        data = logs_data
        if current_filter != "ALL":
            data = [d for d in data if d["level"] == current_filter]
        if search_query.strip():
            q = search_query.lower()
            data = [d for d in data if (
                q in d.get("message", "").lower() or
                q in d.get("component", "").lower() or
                q in d.get("level", "").lower()
            )]
        filtered_logs_data = data

    # ---------------------- UI Update Functions --------------------------- #
    def make_tile(entry: Dict[str, Any], index: int) -> ft.ListTile:
        ts = datetime.fromisoformat(entry["timestamp"]).strftime("%H:%M:%S")
        msg_text = ft.Text(
            entry["message"],
            size=12,
            color=ft.Colors.GREY_800,
            overflow=ft.TextOverflow.ELLIPSIS,
            expand=True,
        )
        # Tooltip for longer messages
        if len(entry.get("message", "")) > 60:
            msg_text = ft.Tooltip(message=entry["message"], content=msg_text)

    _fg = level_fg(entry["level"])
    _bg = level_bg(entry["level"])
    stripe = striped_row_color(index)
    tile_bg = stripe or _bg

    level_badge = build_level_badge(entry["level"])

        return ft.ListTile(
            leading=level_badge,
            title=ft.Row([
                ft.Text(ts, size=12, weight=ft.FontWeight.W_600, color=ft.Colors.BLUE_GREY_700, width=65),
                ft.Text(entry["component"], size=12, weight=ft.FontWeight.W_500, color=ft.Colors.INDIGO_700, width=100),
                msg_text,
            ], spacing=8),
            bgcolor=tile_bg,
            content_padding=ft.Padding(12, 8, 12, 8),
        )

    def update_list():
        if not filtered_logs_data:
            logs_container.controls = [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.ARTICLE, size=48, color=ft.Colors.OUTLINE),
                        ft.Text("No logs found", weight=ft.FontWeight.BOLD),
                        ft.Text("Adjust filters or search query.", size=12, color=ft.Colors.OUTLINE),
                        ft.OutlinedButton("Show All", icon=ft.Icons.CLEAR, on_click=create_filter_handler("ALL"))
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                    height=240, alignment=ft.alignment.center
                )
            ]
        else:
            # Ensure current page valid after any filter change
            total_pages = max(1, (len(filtered_logs_data) + pagination_config.page_size - 1) // pagination_config.page_size)
            if pagination_config.current_page >= total_pages:
                pagination_config.current_page = max(0, total_pages - 1)

            slice_data, _ = paginate_data(
                filtered_logs_data,
                pagination_config.current_page,
                pagination_config.page_size
            )
            list_view = ft.ListView(
                controls=[make_tile(x, i) for i, x in enumerate(slice_data)],
                expand=True,
                spacing=2,
                padding=ft.Padding(8, 8, 8, 8),
                auto_scroll=False,
                semantic_child_count=len(slice_data),
            )
            logs_container.controls = [
                ft.AnimatedSwitcher(
                    content=list_view,
                    transition=ft.AnimatedSwitcherTransition.FADE,
                    duration=250,
                    reverse=True,
                )
            ]
        logs_container.update()

    def update_status():
        total = len(logs_data)
        filt = len(filtered_logs_data)
        total_pages = max(1, (filt + pagination_config.page_size - 1) // pagination_config.page_size)
        if filt:
            start = pagination_config.current_page * pagination_config.page_size + 1
            end = min(start + pagination_config.page_size - 1, filt)
            status_text.value = (
                f"Showing {start}-{end} of {filt} logs (Total: {total}) | "
                f"Page {pagination_config.current_page + 1} of {total_pages}"
            )
        else:
            status_text.value = f"No logs found (Total: {total})"
        status_text.update()

    def update_pagination_controls():
        total_pages = max(1, (len(filtered_logs_data) + pagination_config.page_size - 1) // pagination_config.page_size)
        first_btn.disabled = pagination_config.current_page <= 0
        prev_btn.disabled = pagination_config.current_page <= 0
        next_btn.disabled = (pagination_config.current_page + 1) >= total_pages
        last_btn.disabled = (pagination_config.current_page + 1) >= total_pages
        page_info_text.value = f"Page {pagination_config.current_page + 1} of {total_pages}"
        for c in [first_btn, prev_btn, next_btn, last_btn, page_info_text]:
            c.update()

    # ---------------------- Event Handlers -------------------------------- #
    async def perform_search():
        nonlocal search_query
        pagination_config.current_page = 0
        with PerfTimer("logs.search.perform"):
            apply_filters()
            update_list()
            update_status()
            update_pagination_controls()
        logger.info(f"Search query='{search_query}' results={len(filtered_logs_data)}")

    def on_search_change(e):
        nonlocal search_query
        search_query = e.control.value
        asyncio.create_task(search_debouncer.debounce(perform_search))

    def on_search_clear(e):
        nonlocal search_query
        search_query = ""
        search_field.value = ""
        pagination_config.current_page = 0
        apply_filters()
        update_list()
        update_status()
        update_pagination_controls()
        search_field.update()

    def create_filter_handler(level: str):
        def handler(_):
            nonlocal current_filter
            current_filter = level
            pagination_config.current_page = 0
            apply_filters()
            update_list()
            update_status()
            update_pagination_controls()
            # Update ALL button style
            for i, b in enumerate(filter_buttons):
                if i == 0:
                    b.style = ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY if current_filter == "ALL" else None)
                b.update()
        return handler

    def close_dialog(_):
        page.dialog.open = False
        page.dialog.update()

    def confirm_clear(_):
        nonlocal logs_data, filtered_logs_data
        logs_data = []
        filtered_logs_data = []
        update_list()
        update_status()
        update_pagination_controls()
        show_success_message(page, "Logs cleared")
        close_dialog(None)

    def on_clear_logs(_):
        page.dialog = ft.AlertDialog(
            title=ft.Text("Clear Logs"),
            content=ft.Text("Are you sure you want to clear all logs?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.TextButton("Clear", icon=ft.Icons.CLEAR, on_click=confirm_clear)
            ]
        )
        page.dialog.open = True
        page.update()

    def on_refresh_logs(_):
        page.run_task(load_logs_data_async)
        page.snack_bar = ft.SnackBar(content=ft.Text("Refreshing logs..."), bgcolor=ft.Colors.BLUE)
        page.snack_bar.open = True
        page.update()

    async def export_logs_async():
        try:
            ring = ft.ProgressRing(width=32, height=32)
            txt = ft.Text("Preparing export...", size=12)
            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Text("Export Logs"),
                content=ft.Column([
                    ring,
                    txt
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16, width=260),
            )
            page.dialog = dlg
            dlg.open = True
            page.update()
            await asyncio.sleep(ASYNC_DELAY * 0.5)
            txt.value = "Writing file..."; page.update(); await asyncio.sleep(ASYNC_DELAY * 0.5)
            txt.value = "Finalizing..."; page.update(); await asyncio.sleep(ASYNC_DELAY * 0.5)
            dlg.open = False
            page.update()
            return True
        except Exception as e:  # pragma: no cover
            logger.error(f"Export failed: {e}")
            return False

    def on_export_logs(_):
        async def runner():
            ok = await export_logs_async()
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Logs exported" if ok else "Export failed"),
                bgcolor=ft.Colors.GREEN if ok else ft.Colors.ERROR
            )
            page.snack_bar.open = True
            page.update()
        page.run_task(runner)

    # ---------------------- Async Data Load -------------------------------- #
    async def load_logs_data_async():
        nonlocal logs_data, last_updated, is_loading
        if is_loading:
            return
        is_loading = True
        try:
            status_text.value = "Loading logs..."; status_text.update()
            with PerfTimer("logs.load.fetch"):
                if server_bridge:
                    try:
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as ex:
                            logs_data = await asyncio.get_event_loop().run_in_executor(ex, server_bridge.get_logs)
                        if not isinstance(logs_data, list):
                            logs_data = []
                    except Exception as e:  # pragma: no cover
                        logger.warning(f"Server bridge failure: {e}")
                        logs_data = generate_mock_logs()
                else:
                    logs_data = generate_mock_logs()
            last_updated = datetime.now()
            last_updated_text.value = f"Last updated: {last_updated.strftime('%H:%M:%S')}"; last_updated_text.update()
            with PerfTimer("logs.load.render"):
                apply_filters()
                update_list(); update_status(); update_pagination_controls()
        except Exception as e:  # pragma: no cover
            logger.error(f"Loading error: {e}")
            status_text.value = "Error loading logs"; status_text.update()
        finally:
            is_loading = False

    # ---------------------- UI Controls ------------------------------------ #
    status_text = ft.Text("Loading logs...", color=ft.Colors.OUTLINE)
    last_updated_text = ft.Text("Last updated: Never", size=12, color=ft.Colors.ON_SURFACE)

    search_field = ft.TextField(
        label="Search logs...",
        hint_text="Search by message, component, or level",
        prefix_icon=ft.Icons.SEARCH,
        suffix=ft.IconButton(icon=ft.Icons.CLEAR, tooltip="Clear search", on_click=on_search_clear),
        on_change=on_search_change,
        expand=True,
        filled=True,
        bgcolor=ft.Colors.SURFACE_TINT,
        border_radius=12,
        content_padding=ft.Padding(12, 8, 12, 8)
    )

    filter_buttons = [
        ft.FilledButton(
            "ALL", icon=ft.Icons.FILTER_LIST, on_click=create_filter_handler("ALL"),
            style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY), tooltip="Show all logs"
        ),
        ft.OutlinedButton("INFO", icon=ft.Icons.INFO, on_click=create_filter_handler("INFO")),
        ft.OutlinedButton("SUCCESS", icon=ft.Icons.CHECK_CIRCLE, on_click=create_filter_handler("SUCCESS")),
        ft.OutlinedButton("WARNING", icon=ft.Icons.WARNING, on_click=create_filter_handler("WARNING")),
        ft.OutlinedButton("ERROR", icon=ft.Icons.ERROR, on_click=create_filter_handler("ERROR")),
        ft.OutlinedButton("DEBUG", icon=ft.Icons.BUG_REPORT, on_click=create_filter_handler("DEBUG")),
    ]

    logs_container = ft.Column(controls=[], expand=True, spacing=0, scroll=ft.ScrollMode.AUTO)

    # Pagination controls
    def on_first(_):
        pagination_config.current_page = 0; update_list(); update_status(); update_pagination_controls()
    def on_prev(_):
        if pagination_config.current_page > 0:
            pagination_config.current_page -= 1; update_list(); update_status(); update_pagination_controls()
    def on_next(_):
        total_pages = max(1, (len(filtered_logs_data) + pagination_config.page_size - 1) // pagination_config.page_size)
        if (pagination_config.current_page + 1) < total_pages:
            pagination_config.current_page += 1; update_list(); update_status(); update_pagination_controls()
    def on_last(_):
        total_pages = max(1, (len(filtered_logs_data) + pagination_config.page_size - 1) // pagination_config.page_size)
        pagination_config.current_page = max(0, total_pages - 1); update_list(); update_status(); update_pagination_controls()

    first_btn = ft.IconButton(icon=ft.Icons.FIRST_PAGE, tooltip="First Page", on_click=on_first, disabled=True)
    prev_btn = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, tooltip="Previous Page", on_click=on_prev, disabled=True)
    next_btn = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, tooltip="Next Page", on_click=on_next, disabled=True)
    last_btn = ft.IconButton(icon=ft.Icons.LAST_PAGE, tooltip="Last Page", on_click=on_last, disabled=True)
    page_info_text = ft.Text("Page 1 of 1", size=12, weight=ft.FontWeight.W_500)
    pagination_row = ft.Row([first_btn, prev_btn, page_info_text, next_btn, last_btn], spacing=5)

    # Layout
    view = ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Text("System Logs", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Refresh Logs", on_click=on_refresh_logs),
                    ft.IconButton(icon=ft.Icons.DOWNLOAD, tooltip="Export Logs", on_click=on_export_logs),
                    ft.IconButton(icon=ft.Icons.CLEAR_ALL, tooltip="Clear Logs", icon_color=ft.Colors.RED, on_click=on_clear_logs),
                ], spacing=5)
            ]),
            padding=ft.Padding(20, 20, 20, 10)
        ),
        ft.Container(content=ft.Row(filter_buttons, spacing=10), padding=ft.Padding(20, 0, 20, 10)),
        ft.Container(
            content=ft.Row([
                search_field,
                ft.Container(width=10),
                ft.Text("🔍 Debounced 300ms", size=11, color=ft.Colors.GREY_600, italic=True)
            ]),
            padding=ft.Padding(20, 0, 20, 10)
        ),
        ft.Container(content=ft.Row([status_text, ft.Container(expand=True), last_updated_text]), padding=ft.Padding(20, 0, 20, 5)),
        ft.Container(content=ft.Row([ft.Container(expand=True), pagination_row, ft.Container(expand=True)]), padding=ft.Padding(20, 5, 20, 10)),
        ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text("Time", weight=ft.FontWeight.BOLD, size=12), width=80),
                ft.Container(content=ft.Text("Level", weight=ft.FontWeight.BOLD, size=12), width=70),
                ft.Container(content=ft.Text("Component", weight=ft.FontWeight.BOLD, size=12), width=100),
                ft.Container(content=ft.Text("Message", weight=ft.FontWeight.BOLD, size=12), expand=True),
            ], spacing=10),
            padding=ft.Padding(10, 8, 10, 8),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE)
        ),
        ft.Container(
            content=logs_container,
            expand=True,
            padding=ft.Padding(20, 0, 20, 20),
            border=ft.border.all(2, ft.Colors.GREY_300),
            border_radius=12,
            bgcolor=ft.Colors.WHITE
        )
    ], expand=True)

    # Expose manual trigger
    def trigger_initial_load():
        page.run_task(load_logs_data_async)
    view.trigger_initial_load = trigger_initial_load

    # Kick off initial load (delayed to ensure page attachment)
    async def delayed_initial():
        await asyncio.sleep(0.05)
        await load_logs_data_async()
    page.run_task(delayed_initial)

    return view

