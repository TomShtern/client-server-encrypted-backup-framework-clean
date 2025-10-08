#!/usr/bin/env python3
"""
Logs View - Neumorphic, MD3-styled dual tabs

- System Logs: fetched from server bridge
- Flet Logs: captured via logging.Handler (optional live updates)

Design goals:
- Neumorphic cards with subtle elevation (theme shadows)
- MD3 accents and color-coded log levels
- Efficient ListView rendering (avoid DataTable freezes in 0.28.3)
"""

import os
import sys
import logging
import contextlib
from datetime import datetime
import asyncio
import json
from typing import Any, Callable

import flet as ft

# Path setup
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import Shared.utils.utf8_solution as _  # noqa: F401

# --------------------------------------------------------------------------------------
# MD3 color token polyfills for Flet 0.28.x
# Some Material 3 colors like SURFACE_CONTAINER_LOW/HIGHEST may not exist in older
# Flet versions. Define graceful fallbacks so the view doesn't crash at runtime.
# --------------------------------------------------------------------------------------
def _ensure_color_attr(attr_name: str, fallback_factory: Callable[[], str]) -> None:
    try:
        if not hasattr(ft.Colors, attr_name):
            setattr(ft.Colors, attr_name, fallback_factory())
    except Exception:
        # Last-resort fallback to SURFACE
        with contextlib.suppress(Exception):
            setattr(ft.Colors, attr_name, getattr(ft.Colors, "SURFACE", "#121212"))

_ensure_color_attr(
    "SURFACE_CONTAINER_LOW",
    lambda: ft.Colors.with_opacity(0.06, getattr(ft.Colors, "SURFACE", "#121212")),
)
_ensure_color_attr(
    "SURFACE_CONTAINER_HIGHEST",
    lambda: ft.Colors.with_opacity(0.16, getattr(ft.Colors, "SURFACE", "#121212")),
)
_ensure_color_attr(
    "ON_SURFACE_VARIANT",
    # If missing, approximate with a dimmed ON_SURFACE (or SURFACE as last resort)
    lambda: ft.Colors.with_opacity(0.70, getattr(ft.Colors, "ON_SURFACE", getattr(ft.Colors, "SURFACE", "#FFFFFF"))),
)
_ensure_color_attr(
    "OUTLINE",
    # Approximate MD outline with 12% of on-surface
    lambda: ft.Colors.with_opacity(0.12, getattr(ft.Colors, "ON_SURFACE", getattr(ft.Colors, "SURFACE", "#FFFFFF"))),
)

# Import neumorphic shadows from theme (using relative import to avoid circular imports)
try:
    from theme import PRONOUNCED_NEUMORPHIC_SHADOWS, MODERATE_NEUMORPHIC_SHADOWS, SUBTLE_NEUMORPHIC_SHADOWS
except ImportError:
    PRONOUNCED_NEUMORPHIC_SHADOWS = []
    MODERATE_NEUMORPHIC_SHADOWS = []
    SUBTLE_NEUMORPHIC_SHADOWS = []


# ======================================================================================
# FLET LOG CAPTURE SYSTEM
# ======================================================================================

class FletLogCapture(logging.Handler):
    """Custom logging handler to capture Flet framework logs in real-time."""

    def __init__(self):
        super().__init__()
        self.logs = []
        self.max_logs = 100  # Keep last 100 logs

    def emit(self, record):
        """Capture log record and format it."""
        with contextlib.suppress(Exception):
            self.logs.insert(0, {
                "time": datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
                "level": record.levelname,
                "component": record.name,
                "message": self.format(record)
            })
            # Limit to max_logs
            if len(self.logs) > self.max_logs:
                self.logs = self.logs[:self.max_logs]


# Global Flet log capture instance
_flet_log_capture = FletLogCapture()
_flet_log_capture.setFormatter(logging.Formatter('%(message)s'))

# Attach to root logger to capture all logs (avoid duplicates on hot reload)
_root_logger = logging.getLogger()
if not any(isinstance(h, FletLogCapture) for h in _root_logger.handlers):
    _root_logger.addHandler(_flet_log_capture)


# ======================================================================================
# DATA FETCHING
# ======================================================================================

def get_system_logs(server_bridge: Any | None) -> list[dict]:
    """Get system logs from server or return empty list."""
    if not server_bridge:
        return []  # Return empty, not mock data
    try:
        result = server_bridge.get_logs()
        if isinstance(result, dict) and result.get('success'):
            return result.get('data', [])
        return []
    except Exception:
        return []


# ======================================================================================
# UI CREATION
# ======================================================================================

def create_logs_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Any]]:
    """Create logs view with dual-tab system and neumorphic design."""

    # ---------------------------------------------
    # Level config and helpers
    # ---------------------------------------------
    LEVELS = {
        # canonical level -> dict of styles
        "DEBUG": {
            "color": ft.Colors.GREY_500,
            "bg": ft.Colors.GREY_100,
            "icon": ft.Icons.BUG_REPORT,
            "label": "DEBUG",
        },
        "INFO": {
            "color": ft.Colors.BLUE_500,
            "bg": ft.Colors.BLUE_100,
            "icon": ft.Icons.INFO,
            "label": "INFO",
        },
        "SUCCESS": {
            "color": ft.Colors.GREEN_600,
            "bg": ft.Colors.GREEN_100,
            "icon": ft.Icons.CHECK_CIRCLE,
            "label": "SUCCESS",
        },
        "WARNING": {
            "color": ft.Colors.AMBER_600,
            "bg": ft.Colors.AMBER_100,
            "icon": ft.Icons.WARNING_AMBER,
            "label": "WARNING",
        },
        "IMPORTANT": {  # important warning / orange
            "color": ft.Colors.ORANGE_700,
            "bg": ft.Colors.ORANGE_100,
            "icon": ft.Icons.REPORT_GMAILERRORRED,
            "label": "IMPORTANT",
        },
        "ERROR": {
            "color": ft.Colors.RED_600,
            "bg": ft.Colors.RED_100,
            "icon": ft.Icons.ERROR,
            "label": "ERROR",
        },
        "CRITICAL": {
            "color": ft.Colors.DEEP_ORANGE_700,
            "bg": ft.Colors.DEEP_ORANGE_100,
            "icon": ft.Icons.ERROR_OUTLINE,
            "label": "CRITICAL",
        },
        "SPECIAL": {
            "color": ft.Colors.DEEP_PURPLE_500,
            "bg": ft.Colors.DEEP_PURPLE_100,
            "icon": ft.Icons.STARS,
            "label": "SPECIAL",
        },
        "EVENT": {
            "color": ft.Colors.PURPLE_500,
            "bg": ft.Colors.PURPLE_100,
            "icon": ft.Icons.EVENT,
            "label": "EVENT",
        },
    }

    def map_level(raw: str | None) -> str:
        if not raw:
            return "INFO"
        r = str(raw).strip().upper()
        # common aliases
        if r in {"WARN", "WARNING"}:  # prefer WARNING
            return "WARNING"
        if r in {"CRIT", "FATAL"}:  # critical
            return "CRITICAL"
        if r in {"OK", "SUCCESS"}:  # success
            return "SUCCESS"
        if r in {"IMPORTANT", "ALERT"}:  # orange
            return "IMPORTANT"
        if r in {"SPECIAL", "NOTICE", "EVENT"}:  # purple family
            return "SPECIAL"
        return r if r in LEVELS else "INFO"

    def level_styles(level: str) -> dict:
        l = LEVELS.get(level, LEVELS["INFO"])
        # subtle surface tint using opacity
        tint = ft.Colors.with_opacity(0.08, l["color"])  # subtle card tint
        accent = l["color"]
        return {
            "tint": tint,
            "accent": accent,
            "icon": l["icon"],
            "label": l["label"],
        }

    # ---------------------------------------------
    # Card builder
    # ---------------------------------------------
    def build_log_card(log: dict) -> ft.Control:
        # Safe access
        time_s = str(log.get("time", ""))
        level = map_level(log.get("level"))
        comp = str(log.get("component", ""))
        msg = str(log.get("message", ""))

        st = level_styles(level)

        # Level dot (leading)
        dot = ft.Container(width=10, height=10, border_radius=999, bgcolor=st["accent"])

        # Level pill (trailing)
        level_pill = ft.Container(
            content=ft.Row([
                ft.Icon(st["icon"], size=14, color=st["accent"]),
                ft.Text(level, size=11, weight=ft.FontWeight.W_600, color=st["accent"]),
            ], spacing=4, tight=True),
            bgcolor=ft.Colors.with_opacity(0.10, st["accent"]),
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            border_radius=999,
        )

        title = ft.Text(
            msg or "(no message)",
            size=14,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.ON_SURFACE,
            max_lines=3,
            overflow=ft.TextOverflow.ELLIPSIS,
            selectable=True,
        )

        subtitle_items: list[ft.Control] = []
        if comp:
            subtitle_items.append(ft.Text(comp, size=12, color=ft.Colors.ON_SURFACE_VARIANT))
        if time_s:
            if subtitle_items:
                subtitle_items.append(ft.Text(" • ", size=12, color=ft.Colors.ON_SURFACE_VARIANT))
            subtitle_items.append(ft.Text(time_s, size=12, color=ft.Colors.ON_SURFACE_VARIANT))

        subtitle = ft.Row(subtitle_items, spacing=4)

        card_surface = ft.Container(
            content=ft.Row([
                dot,
                ft.Container(width=10),
                ft.Column([
                    title,
                    subtitle,
                ], spacing=6, expand=True),
                level_pill,
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            padding=14,
            border_radius=12,
            bgcolor=ft.Colors.TRANSPARENT,
            border=ft.border.all(1, ft.Colors.with_opacity(0.08, st["accent"]))
        )

        # Return the flat card surface (no extra shadow container to avoid panel look)
        return card_surface

    # ---------------------------------------------
    # UI State & Refs
    # ---------------------------------------------
    system_list_ref: ft.Ref[ft.ListView] = ft.Ref()
    flet_list_ref: ft.Ref[ft.ListView] = ft.Ref()
    system_loading_ref: ft.Ref[ft.Container] = ft.Ref()
    flet_loading_ref: ft.Ref[ft.Container] = ft.Ref()

    # stores
    system_logs_data: list[dict] = []
    flet_logs_data: list[dict] = []

    # Builders for list views (no updates yet)
    def make_listview(ref: ft.Ref[ft.ListView]) -> ft.ListView:
        return ft.ListView(ref=ref, spacing=10, padding=0, auto_scroll=False, controls=[], expand=True)

    def make_loading_overlay(ref: ft.Ref[ft.Container]) -> ft.Container:
        return ft.Container(
            ref=ref,
            content=ft.Row([
                ft.ProgressRing(),
                ft.Text("Loading...", size=12, color=ft.Colors.ON_SURFACE_VARIANT),
            ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=ft.Colors.TRANSPARENT,
            alignment=ft.alignment.center,
            visible=False,
            padding=20,
        )

    # System tab content
    system_stack = ft.Stack([
        make_listview(system_list_ref),
        make_loading_overlay(system_loading_ref),
    ], expand=True)

    # Flet tab content
    flet_stack = ft.Stack([
        make_listview(flet_list_ref),
        make_loading_overlay(flet_loading_ref),
    ], expand=True)

    # Filter chips (level filtering)
    selected_levels: set[str] = set()  # empty => all
    _chip_refs: dict[str, ft.Chip] = {}

    def _style_chip(name: str):
        ch = _chip_refs.get(name)
        if not ch:
            return
        st = level_styles(name)
        sel = bool(ch.selected)
        ch.bgcolor = ft.Colors.with_opacity(0.16 if sel else 0.06, st["accent"])
        # Update leading icon color
        # Update icon color if chip has an Icon leading
        with contextlib.suppress(Exception):
            if getattr(ch, "leading", None) is not None:
                ch.leading.color = st["accent"]

    def _build_filter_chip(name: str) -> ft.Chip:
        st = level_styles(name)
        chip = ft.Chip(
            label=ft.Text(st["label"], size=12, weight=ft.FontWeight.W_600),
            selected=(name in selected_levels),
            on_select=lambda e, n=name: _on_toggle_level(n, e.control.selected),
            leading=ft.Icon(st["icon"], size=14, color=st["accent"]),
        )
        _chip_refs[name] = chip
        _style_chip(name)
        return chip

    def _on_toggle_level(name: str, selected: bool):
        nonlocal selected_levels
        if selected:
            selected_levels.add(name)
        else:
            selected_levels.discard(name)
        # update chip visuals
        ch = _chip_refs.get(name)
        if ch:
            ch.selected = selected
            _style_chip(name)
            ch.update()
        _refresh_lists_by_filter()

    def _passes_filter(log: dict) -> bool:
        if not selected_levels:
            return True
        return map_level(log.get("level")) in selected_levels

    def _render_list(lst_ref: ft.Ref[ft.ListView], data: list[dict]):
        if lst_ref.current:
            if not data:
                lst_ref.current.controls = [
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.INBOX, color=ft.Colors.ON_SURFACE_VARIANT, size=18),
                            ft.Text("No logs", color=ft.Colors.ON_SURFACE_VARIANT),
                        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                        padding=16,
                        border_radius=12,
                        bgcolor=ft.Colors.TRANSPARENT,
                        border=ft.border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.OUTLINE)),
                    )
                ]
            else:
                lst_ref.current.controls = [build_log_card(row) for row in data if _passes_filter(row)]
            lst_ref.current.update()

    def _refresh_lists_by_filter():
        _render_list(system_list_ref, system_logs_data)
        _render_list(flet_list_ref, flet_logs_data)

    # Custom flat tab bar (to avoid any internal background from Flet Tabs)
    active_tab_index = 0

    def _tab_button(label: str, icon: str, idx: int, current: int) -> ft.TextButton:
        return ft.TextButton(
            content=ft.Row([
                ft.Icon(icon, size=16, color=(ft.Colors.PRIMARY if idx == current else ft.Colors.ON_SURFACE_VARIANT)),
                ft.Text(label, size=14, weight=(ft.FontWeight.W_600 if idx == current else ft.FontWeight.NORMAL), color=(ft.Colors.PRIMARY if idx == current else ft.Colors.ON_SURFACE_VARIANT)),
            ], spacing=6),
            style=ft.ButtonStyle(
                overlay_color=ft.Colors.with_opacity(0.04, ft.Colors.PRIMARY),
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                shape=ft.RoundedRectangleBorder(radius=8),
                bgcolor=ft.Colors.TRANSPARENT,
            ),
            on_click=lambda e, i=idx: _on_tab_click(i),
        )

    tabbar_row_ref: ft.Ref[ft.Row] = ft.Ref()
    content_host_ref: ft.Ref[ft.Container] = ft.Ref()

    def _render_tabbar():
        if not tabbar_row_ref.current:
            return
        tabbar_row_ref.current.controls = [
            _tab_button("System Logs", ft.Icons.ARTICLE, 0, active_tab_index),
            _tab_button("Flet Logs", ft.Icons.CODE, 1, active_tab_index),
        ]
        tabbar_row_ref.current.update()

    def _render_active_content():
        if not content_host_ref.current:
            return
        content_host_ref.current.content = (system_stack if active_tab_index == 0 else flet_stack)
        content_host_ref.current.update()

    def _on_tab_click(i: int):
        nonlocal active_tab_index
        if i == active_tab_index:
            return
        active_tab_index = i
        _render_tabbar()
        _render_active_content()

    # ---------------------------------------------
    # Actions
    # ---------------------------------------------
    _system_first_load = True

    async def refresh_system_logs(show_toast: bool = False, show_spinner: bool = False):
        nonlocal _system_first_load
        if system_loading_ref.current and (show_spinner or _system_first_load):
            system_loading_ref.current.visible = True
            system_loading_ref.current.update()
        logs = get_system_logs(server_bridge)
        # Normalize records
        safe_logs: list[dict] = []
        for it in logs:
            if isinstance(it, dict):
                safe_logs.append({
                    "time": it.get("time") or it.get("timestamp") or "",
                    "level": it.get("level") or it.get("severity") or "INFO",
                    "component": it.get("component") or it.get("module") or "",
                    "message": it.get("message") or it.get("msg") or "",
                })
            else:
                safe_logs.append({"time": "", "level": "INFO", "component": "", "message": str(it)})
        nonlocal system_logs_data
        system_logs_data = safe_logs
        _render_list(system_list_ref, system_logs_data)
        if system_loading_ref.current and (show_spinner or _system_first_load):
            system_loading_ref.current.visible = False
            system_loading_ref.current.update()
        _system_first_load = False
        if show_toast:
            _toast(page, "System logs refreshed")

    def get_flet_logs_snapshot() -> list[dict]:
        if _flet_log_capture and _flet_log_capture.logs:
            return _flet_log_capture.logs.copy()
        return []

    _flet_first_load = True

    async def refresh_flet_logs(show_toast: bool = False, show_spinner: bool = False):
        nonlocal _flet_first_load
        if flet_loading_ref.current and (show_spinner or _flet_first_load):
            flet_loading_ref.current.visible = True
            flet_loading_ref.current.update()
        nonlocal flet_logs_data
        flet_logs_data = get_flet_logs_snapshot()
        _render_list(flet_list_ref, flet_logs_data)
        if flet_loading_ref.current and (show_spinner or _flet_first_load):
            flet_loading_ref.current.visible = False
            flet_loading_ref.current.update()
        _flet_first_load = False
        if show_toast:
            _toast(page, "Flet logs refreshed")

    def on_refresh_click(_: ft.ControlEvent):
        # decide which tab
        idx = active_tab_index or 0
        if idx == 0:
            page.run_task(refresh_system_logs(True, show_spinner=True))
        else:
            page.run_task(refresh_flet_logs(True, show_spinner=True))

    def on_export_click(_: ft.ControlEvent):
        try:
            export_dir = os.path.join(_repo_root, "logs_exports")
            os.makedirs(export_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            payload = {
                "exported_at": ts,
                "system": system_logs_data,
                "flet": flet_logs_data or get_flet_logs_snapshot(),
            }
            path = os.path.join(export_dir, f"logs_{ts}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            _toast(page, f"Exported to {path}")
        except Exception as e:
            _toast(page, f"Export failed: {e}", error=True)

    def on_clear_flet_click(_: ft.ControlEvent):
        try:
            _flet_log_capture.logs.clear()
            # refresh list
            page.run_task(refresh_flet_logs(False))
            _toast(page, "Cleared Flet logs")
        except Exception as e:
            _toast(page, f"Clear failed: {e}", error=True)

    # Auto-refresh switch
    auto_refresh_switch = ft.Switch(label="Auto-refresh", value=True)

    # Action buttons with neumorphic styling
    action_buttons = ft.Row([
        ft.FilledTonalButton(
            "Refresh",
            icon=ft.Icons.REFRESH,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            on_click=on_refresh_click,
        ),
        ft.OutlinedButton(
            "Export",
            icon=ft.Icons.DOWNLOAD,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            on_click=on_export_click,
        ),
        ft.OutlinedButton(
            "Clear Flet Logs",
            icon=ft.Icons.DELETE_SWEEP,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
            on_click=on_clear_flet_click,
        ),
    ], spacing=10)

    # Header & body
    # Filter row
    filter_row = ft.Row([
        _build_filter_chip("INFO"),
        _build_filter_chip("SUCCESS"),
        _build_filter_chip("WARNING"),
        _build_filter_chip("IMPORTANT"),
        _build_filter_chip("ERROR"),
        _build_filter_chip("CRITICAL"),
        _build_filter_chip("SPECIAL"),
    ], scroll="auto", spacing=8)

    # Tab bar + content host
    tabbar = ft.Row(ref=tabbar_row_ref, spacing=16)
    content_host = ft.Container(ref=content_host_ref, expand=True, bgcolor=ft.Colors.TRANSPARENT)

    content = ft.Column([
        ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.ARTICLE, size=36, color=ft.Colors.PRIMARY),
                    ft.Text("Logs", size=28, weight=ft.FontWeight.BOLD),
                ], spacing=12),
                ft.Row([auto_refresh_switch, action_buttons], spacing=12),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(bottom=16),
        ),
        ft.Container(filter_row, padding=ft.padding.only(bottom=4)),
        tabbar,
        content_host,
    ], spacing=18, expand=True)

    main_container = ft.Container(content=content, padding=24, expand=True)

    # ---------------------------------------------
    # Toast helper
    # ---------------------------------------------
    def _toast(pg: ft.Page, message: str, *, error: bool = False):
        try:
            pg.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=(ft.Colors.ERROR_CONTAINER if error else ft.Colors.SURFACE_CONTAINER_HIGHEST),
                show_close_icon=True,
                duration=2500,
            )
            pg.snack_bar.open = True
            pg.update()
        except Exception:
            # snack_bar can fail if page not ready; ignore
            with contextlib.suppress(Exception):
                ...

    # ---------------------------------------------
    # Lifecycle
    # ---------------------------------------------
    _live_task: asyncio.Task | None = None

    def dispose():
        nonlocal _live_task
        if _live_task and not _live_task.done():
            _live_task.cancel()
        _live_task = None

    async def _live_flet_refresh_loop():
        try:
            while True:
                # respect auto-refresh switch
                if auto_refresh_switch.value:
                    if active_tab_index == 0:
                        await refresh_system_logs(False, show_spinner=False)
                    else:
                        await refresh_flet_logs(False, show_spinner=False)
                await asyncio.sleep(1.5)
        except asyncio.CancelledError:
            return
        except Exception:
            # Don't crash the app on background errors
            return

    async def setup_subscriptions():
        nonlocal _live_task
        # Initial loads after attachment
        _render_tabbar()
        _render_active_content()
        await refresh_system_logs(False, show_spinner=True)
        await refresh_flet_logs(False, show_spinner=True)
        # Start background polling for flet logs
        try:
            _live_task = asyncio.create_task(_live_flet_refresh_loop())
        except Exception:
            _live_task = None

    return main_container, dispose, setup_subscriptions
