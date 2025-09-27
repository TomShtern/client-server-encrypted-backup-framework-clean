#!/usr/bin/env python3
"""
Simplified Dashboard View - The Flet Way
~400 lines instead of 1,005 lines of framework fighting!

Core Principle: Use Flet's built-in components for metrics, progress bars, and cards.
Clean, maintainable dashboard that preserves all user-facing functionality.
"""

# Standard library imports
import asyncio
import contextlib
import os
from typing import Any
import sys
from collections import deque
from collections.abc import Callable, Iterator
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Literal, cast

# Ensure repository and package roots are on sys.path for runtime resolution
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Third-party imports
import flet as ft
import psutil

# ALWAYS import this in any Python file that deals with subprocess or console I/O
import Shared.utils.utf8_solution as _  # noqa: F401

try:
    from FletV2.utils.debug_setup import get_logger
except ImportError:  # pragma: no cover - fallback logging
    import logging

    from FletV2 import config

    def get_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name or __name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if getattr(config, "DEBUG_MODE", False) else logging.WARNING)
        return logger

from FletV2.theme import setup_modern_theme
from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.state_manager import StateManager
from FletV2.utils.ui_components import themed_card
from FletV2.utils.user_feedback import show_error_message, show_success_message

logger = get_logger(__name__)
# Set FLET_DASHBOARD_DEBUG=1 to force this module's logger to WARNING -> INFO level override
# even if global debug_setup forced it down to ERROR. This helps during rendering black/blank screen
# investigations where INFO/WARNING visibility is required without changing global policy.
if os.environ.get("FLET_DASHBOARD_DEBUG") == "1":  # pragma: no cover - diagnostic mode
    try:
        import logging as _logging
        logger.setLevel(_logging.WARNING)  # show warnings and above
        logger.warning("[DASHBOARD_DEBUG] Verbose dashboard diagnostics enabled (warnings+) ")
    except Exception:  # noqa: BLE001
        pass


def apply_semantics(control: ft.Control | None, label: str | None) -> None:
    """Assign an accessibility label without upsetting static analyzers."""
    if control is None or not label:
        return
    # Some Flet controls may not expose semantics_label in type stubs; set defensively
    try:  # noqa: SIM105
        setattr(control, 'semantics_label', label)  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - defensive
        pass


# Compatibility shim: Some flet versions don't expose FilterChip.
# Provide a lightweight replacement that mimics the small API used
# by this code (label, selected, on_selected, update()). We attach
# it to the ft module as ft.FilterChip so existing code continues to work.
if not hasattr(ft, "FilterChip"):
    class FilterChip(ft.Container):  # sourcery skip
        # Annotate public attributes for static analysis
        label: str
        selected: bool
        on_selected: Callable[[ft.ControlEvent], None] | None
        def __init__(self, label: str = "", selected: bool = False,
                     on_selected: Callable[[ft.ControlEvent], None] | None = None, **kwargs: Any) -> None:
            # store API-friendly attributes
            self.label = label
            self.selected = selected
            self.on_selected = on_selected

            # create an inner button that will be placed as the visible UI
            self._button = ft.ElevatedButton(
                text=label,
                on_click=self._handle_click,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
            )

            # initialize container with the button as content
            super().__init__(content=self._button, padding=ft.padding.symmetric(horizontal=6, vertical=2), **kwargs)
            self._refresh_style()

        def _handle_click(self, e: ft.ControlEvent) -> None:
            # When clicked, call the provided on_selected callback with
            # an object that exposes `.control` pointing to this instance
            if not callable(self.on_selected):
                return
            with contextlib.suppress(Exception):
                ev = type("Evt", (), {"control": self})()
                self.on_selected(ev)

        def _refresh_style(self) -> None:
            # Visual feedback for selected state
            if self.selected:
                # selected: use a higher-contrast background
                self._button.bgcolor = ft.Colors.PRIMARY
                self._button.color = ft.Colors.ON_PRIMARY
            else:
                # unselected: default button styling
                self._button.bgcolor = None
                self._button.color = None
            # ensure visual is updated
            with contextlib.suppress(Exception):
                self._button.update()

        def update(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover - small wrapper
            # keep interface consistent with Flet controls
            self._refresh_style()
            try:
                super().update(*args, **kwargs)
            except Exception:
                # if the parent update isn't available for some reason,
                # try updating the inner button
                with contextlib.suppress(Exception):
                    self._button.update()

    # attach shim to flet module so other modules can reference ft.FilterChip
    ft.FilterChip = cast(Any, FilterChip)  # type: ignore[attr-defined]

# Compatibility shim for ft.Shimmer (added in recent versions of Flet)
if not hasattr(ft, "Shimmer"):
    class Shimmer(ft.Container):  # type: ignore[override]
        def __init__(self, content: ft.Control | None = None, **kwargs: Any) -> None:
            super().__init__(content=content, **kwargs)

    ft.Shimmer = Shimmer  # type: ignore[attr-defined]

# Type definitions for better type safety
ActivityType = Literal['info', 'warning', 'error', 'success']
CardType = Literal['primary', 'success', 'info']
UpdateSource = Literal['auto', 'manual', 'initial']

# Simple dict types instead of TypedDict for better compatibility
ActivityEntry = dict[str, Any]
ServerStatus = dict[str, Any]
SystemMetrics = dict[str, Any]

# Constants for configuration
MAX_HISTORY_POINTS = 30
AUTO_REFRESH_INTERVAL = 30  # seconds
POLLING_INTERVAL = 30  # seconds
OPERATIONS_UPDATE_CYCLE = 2  # every 60 seconds (30 * 2)
CLICK_PROXIMITY = 20
SOCKET_TIMEOUT = 10
STATUS_TOAST_COOLDOWN = 90  # seconds
ACTIVITY_TIME_WINDOW = 10  # minutes for running jobs
MAX_ACTIVITY_DISPLAY = 10
MAX_CLIENTS_DISPLAY = 8
MAX_OPERATIONS_DISPLAY = 5

# Significant change thresholds for toast notifications
SIGNIFICANT_DELTA_THRESHOLDS = {
    'clients': 2,
    'transfers': 2,
    'storage_gb': 1.0,
    'files': 10
}

# Activity filter keywords
JOB_KEYWORDS = ['start', 'running', 'upload', 'transfer']
BACKUP_KEYWORDS = ['backup', 'completed']

# -------------------------
# Normalization helpers
# -------------------------
def _parse_uptime_to_seconds(uptime_value: Any) -> int:
    """Parse uptime value from various formats to seconds.
    Supports:
    - int/float seconds
    - HH:MM:SS string
    - dict-like with hours/minutes/seconds
    """
    with contextlib.suppress(Exception):
        if isinstance(uptime_value, (int, float)):
            return int(uptime_value)
        s = str(uptime_value)
        if ":" in s:
            parts = s.split(":")
            if len(parts) == 3:
                h, m, sec = [int(x) for x in parts]
                return h * 3600 + m * 60 + sec
        # dict-like {"hours": 1, "minutes": 2, "seconds": 3}
        if isinstance(uptime_value, dict):
            h = int(uptime_value.get("hours", 0))
            m = int(uptime_value.get("minutes", 0))
            sec = int(uptime_value.get("seconds", 0))
            return h * 3600 + m * 60 + sec
    return 0

def _normalize_server_status_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Normalize server status dict to the keys the dashboard expects."""
    if not isinstance(payload, dict):
        return {}
    try:
        running = bool(payload.get("running", payload.get("server_running", payload.get("is_running", True))))
        uptime_seconds = _parse_uptime_to_seconds(
            payload.get("uptime_seconds", payload.get("uptime", payload.get("server_uptime", 0)))
        )
        return {
            "running": running,
            "clients_connected": int(payload.get("clients_connected", payload.get("active_clients", payload.get("total_clients", 0))))
                if isinstance(payload.get("clients_connected"), (int, float)) or payload.get("clients_connected") is not None else 0,
            "total_files": int(payload.get("total_files", payload.get("files_count", 0))),
            "total_transfers": int(payload.get("total_transfers", payload.get("transfers", 0))),
            "storage_used_gb": float(payload.get("storage_used_gb", payload.get("storage_used", 0.0))),
            "uptime_seconds": uptime_seconds,
        }
    except Exception:
        # Graceful fallback
        return {}

# Cached helper functions for better performance
@lru_cache(maxsize=32)
def get_activity_icon(activity_type: ActivityType) -> str:
    """Get icon for activity type with caching."""
    icon_map = {
        'success': ft.Icons.CHECK_CIRCLE_OUTLINE,
        'error': ft.Icons.ERROR_OUTLINE,
        'warning': ft.Icons.WARNING_AMBER,
        'info': ft.Icons.INFO_OUTLINE
    }
    return icon_map.get(activity_type, ft.Icons.INFO_OUTLINE)

@lru_cache(maxsize=32)
def get_activity_color(activity_type: ActivityType) -> str:
    """Get color for activity type with caching."""
    color_map = {
        'success': ft.Colors.GREEN,
        'error': ft.Colors.RED,
        'warning': ft.Colors.ORANGE,
        'info': ft.Colors.BLUE
    }
    return color_map.get(activity_type, ft.Colors.BLUE)

def normalize_activity_type(level: str) -> ActivityType:
    """Normalize activity level to valid ActivityType."""
    normalized = level.lower()
    if normalized in {'info', 'warning', 'error', 'success'}:
        return normalized  # type: ignore
    return 'info'

# Enhanced components using Flet native features
def create_status_pill(text: str, status_type: str) -> ft.Container:
    """Modern status pill using Flet's native styling."""
    color_map = {
        "success": ft.Colors.GREEN,
        "error": ft.Colors.ERROR,
        "warning": ft.Colors.ORANGE
    }
    color = color_map.get(status_type, ft.Colors.PRIMARY)

    return ft.Container(
        content=ft.Text(text, color=color, size=12, weight=ft.FontWeight.W_600),
        bgcolor=ft.Colors.with_opacity(0.1, color),
        border=ft.border.all(1, color),
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=16, vertical=6)
    )

def create_action_group(
    buttons: list[ft.Control],
    group_type: str = "primary",
    spacing: int = 10,
    semantics_label: str | None = None
) -> ft.Container:
    """Create a subtle action group wrapper that adapts to dark/light themes."""
    tone = ft.Colors.PRIMARY if group_type == "primary" else ft.Colors.OUTLINE
    container = ft.Container(
        content=ft.Row(buttons, spacing=spacing, wrap=True, run_spacing=8),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.08, tone),
        animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT)
    )
    apply_semantics(container, semantics_label)
    return container

def safe_server_call(method, *args, **kwargs) -> dict[str, Any] | None:
    """Standardized error handling for server bridge calls."""
    try:
        result = method(*args, **kwargs)
        return result if isinstance(result, dict) and result.get('success') else None
    except Exception as e:
        logger.debug(f"Server call failed: {e}")
        return None


def _create_emergency_simple_dashboard(page: ft.Page) -> tuple[ft.Control, Callable, Callable]:
    """Emergency dashboard with full visuals but immediate Lorem ipsum data loading."""
    logger.info("[EMERGENCY_DASHBOARD] Creating full-featured emergency dashboard with Lorem ipsum data")

    # Temporarily disable the emergency mode environment to prevent recursion
    temp_emergency_mode = os.environ.get('FLET_EMERGENCY_SIMPLE_DASHBOARD')
    os.environ['FLET_EMERGENCY_SIMPLE_DASHBOARD'] = '0'  # Disable to prevent recursion

    try:
        # Create dashboard with no server bridge (None) - this preserves ALL visual elements
        dashboard_control, dispose_func, setup_func = create_dashboard_view(
            server_bridge=None,  # No server - triggers Lorem ipsum mode
            page=page,
            _state_manager=None  # Simplified state management for emergency mode
        )
    finally:
        # Restore the original environment value
        if temp_emergency_mode is not None:
            os.environ['FLET_EMERGENCY_SIMPLE_DASHBOARD'] = temp_emergency_mode
        else:
            os.environ.pop('FLET_EMERGENCY_SIMPLE_DASHBOARD', None)

    def emergency_dispose():
        """Minimal cleanup for emergency mode."""
        logger.info("[EMERGENCY_DASHBOARD] Emergency dashboard disposed")
        if dispose_func:
            dispose_func()

    def emergency_setup():
        """Immediate setup with Lorem ipsum data - no async delays."""
        logger.info("[EMERGENCY_DASHBOARD] Emergency dashboard setup completed immediately")
        if setup_func:
            setup_func()

    return dashboard_control, emergency_dispose, emergency_setup


def _get_lorem_ipsum_server_stats():
    """Return Lorem ipsum style placeholder data for GUI-only mode."""
    return {
        'running': True,
        'port': 8080,
        'uptime_seconds': 3600,  # 1 hour
        'clients_connected': 3,
        'total_files': 42,
        'total_transfers': 7,
        'storage_used_gb': 12.5
    }



def create_dashboard_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    _state_manager: StateManager | None
) -> tuple[ft.Control, Callable, Callable]:
    """Create production dashboard view with dynamic hero metrics.

    Behaviour:
      - If FLET_DASHBOARD_ULTRA_TEST=1 -> show ultra-visible diagnostic version
      - Otherwise show production hero metrics (Total Clients, Active Transfers, Uptime)
      - Periodic (5s) refresh pulling from server_bridge; graceful fallback to placeholders
      - Safe dispose cancels background task
    """
    if page is not None:
        setup_modern_theme(page)

    ultra_mode = os.environ.get("FLET_DASHBOARD_ULTRA_TEST") == "1"

    # ------------------ Helper builders ------------------
    def _hero_card(label: str, value_ctrl: ft.Text, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Text(label, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT),
                value_ctrl
            ], spacing=4),
            padding=16,
            border_radius=16,
            bgcolor=ft.Colors.with_opacity(0.08, color),
        )

    def _fmt_uptime(seconds: int | None) -> str:
        if not seconds or seconds < 0:
            return "0m"
        mins, s = divmod(int(seconds), 60)
        hrs, mins = divmod(mins, 60)
        days, hrs = divmod(hrs, 24)
        if days:
            return f"{days}d {hrs}h"
        if hrs:
            return f"{hrs}h {mins}m"
        return f"{mins}m"

    # ------------------ Ultra test mode ------------------
    if ultra_mode:
        logger.warning("[DASHBOARD] Ultra test mode active")
        header = ft.Container(
            content=ft.Text("🚀 DASHBOARD LOADED SUCCESSFULLY 🚀", size=48, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
            bgcolor=ft.Colors.YELLOW,
            padding=20,
            border_radius=12,
            margin=ft.margin.symmetric(vertical=10)
        )
        info = ft.Container(
            content=ft.Text("If you can see this bright yellow box, the dashboard system works!", size=24, color=ft.Colors.BLUE),
            bgcolor=ft.Colors.CYAN,
            padding=20,
            border_radius=12,
            margin=ft.margin.symmetric(vertical=10)
        )
        note = ft.Container(
            content=ft.Text("Hero metrics will appear below:", size=20, color=ft.Colors.GREEN),
            bgcolor=ft.Colors.LIME,
            padding=20,
            border_radius=12,
            margin=ft.margin.symmetric(vertical=10)
        )
        ultra_column = ft.Column([header, info, note], spacing=20)
        # We'll append hero metrics later using production cards for consistency
    else:
        ultra_column = None  # type: ignore

    # ------------------ Hero Metrics (Production) ------------------
    total_clients_text = ft.Text("0", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
    active_transfers_text = ft.Text("0", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
    uptime_text = ft.Text("0m", size=40, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)

    total_clients_card = _hero_card("Total Clients", total_clients_text, ft.Colors.BLUE)
    active_transfers_card = _hero_card("Active Transfers", active_transfers_text, ft.Colors.GREEN)
    uptime_card = _hero_card("Server Uptime", uptime_text, ft.Colors.PURPLE)

    hero_row = ft.ResponsiveRow([
        ft.Container(content=total_clients_card, col={"sm": 12, "md": 4}),
        ft.Container(content=active_transfers_card, col={"sm": 12, "md": 4}),
        ft.Container(content=uptime_card, col={"sm": 12, "md": 4}),
    ], columns=12, spacing=20)

    # --- layout ---
    body_controls: list[ft.Control] = []
    if ultra_mode and ultra_column is not None:
        body_controls.append(ultra_column)
    body_controls.append(hero_row)

    main_col = ft.Column(body_controls, spacing=28, scroll=ft.ScrollMode.AUTO)
    dashboard_container = ft.Container(
        content=main_col,
        expand=True,
        padding=ft.padding.symmetric(horizontal=32, vertical=24),
        bgcolor=ft.Colors.with_opacity(0.01, ft.Colors.SURFACE),
    )

    # ------------------ Data Refresh Logic ------------------
    stop_flag = False
    refresh_interval = int(os.environ.get("FLET_DASHBOARD_REFRESH_SEC", "5"))

    def _pull_data() -> dict[str, Any]:
        data: dict[str, Any] = {"clients": 0, "active_transfers": 0, "uptime_seconds": None}
        if not server_bridge:
            return data
        # We call methods defensively - not all bridges expose all helpers
        with contextlib.suppress(Exception):
            clients = server_bridge.get_clients()  # type: ignore[attr-defined]
            if isinstance(clients, list):
                data["clients"] = len(clients)
        with contextlib.suppress(Exception):
            status = getattr(server_bridge, "get_server_status", None) or getattr(server_bridge, "get_status", None)
            if callable(status):
                st = status()
                if isinstance(st, dict):
                    # Support various key spellings
                    uptime = st.get("uptime_seconds") or st.get("uptime") or st.get("server_uptime_seconds")
                    if isinstance(uptime, (int, float)):
                        data["uptime_seconds"] = int(uptime)
                    active = st.get("active_transfers") or st.get("transfers_active")
                    if isinstance(active, int):
                        data["active_transfers"] = active
        return data

    def _apply_data(d: dict[str, Any]) -> None:
        total_clients_text.value = str(d.get("clients", 0))
        active_transfers_text.value = str(d.get("active_transfers", 0))
        uptime_text.value = _fmt_uptime(d.get("uptime_seconds"))
        # Prefer control-level updates for perf
        total_clients_text.update()
        active_transfers_text.update()
        uptime_text.update()

    async def _refresh_loop() -> None:
        # First immediate update
        try:
            _apply_data(_pull_data())
        except Exception as e:  # noqa: BLE001
            logger.debug(f"Initial dashboard refresh failed: {e}")
        while not stop_flag:
            await asyncio.sleep(refresh_interval)
            try:
                _apply_data(_pull_data())
            except Exception as e:  # noqa: BLE001
                logger.debug(f"Periodic dashboard refresh failed: {e}")

    def setup_subscriptions() -> None:
        if hasattr(page, "run_task"):
            page.run_task(_refresh_loop)
        else:
            # Fallback: one-time update
            with contextlib.suppress(Exception):
                _apply_data(_pull_data())
        logger.info("[DASHBOARD] Subscriptions / refresh loop started")

    def dispose() -> None:
        nonlocal stop_flag
        stop_flag = True
        logger.info("[DASHBOARD] Disposed dashboard view (refresh loop stop requested)")

    return dashboard_container, dispose, setup_subscriptions

    # ------------------------------------------------------------------
    # NOTE: Legacy dashboard implementation code continues below. This
    # is intentionally left in place for reference during the staged
    # refactor from the original large implementation to the simplified
    # production version above. Everything beyond this point is currently
    # unreachable because of the early return. Once the new implementation
    # is validated end-to-end (metrics + activity + clients), the legacy
    # code will be safely removed.
    # ------------------------------------------------------------------

    # Apply the enhanced modern theme for 2025 visual excellence (if page is available)
    if page is not None:
        setup_modern_theme(page)

    # Simple state management with proper initialization
    current_server_status: dict[str, Any] = {}
    current_system_metrics: dict[str, Any] = {}
    current_activity: list[dict[str, Any]] = []
    current_clients: list[dict[str, Any]] = []
    refresh_task = None
    _stop_polling = False
    auto_refresh_enabled = True
    activity_filter = "All"
    activity_search_query = ""
    activity_filter_chips: dict[str, ft.FilterChip] = {}
    is_loading = False
    countdown_remaining = POLLING_INTERVAL
    last_updated = "Never"
    # Forward declarations for controls created later (satisfy type checkers for closures)
    clients_list: ft.ListView = cast(Any, None)
    # For significant-change detection and toast throttling
    prev_server_snapshot: dict[str, Any] | None = None
    last_significant_toast_time: datetime | None = None

    # Memory-efficient history buffers using deque with fixed size
    cpu_history: deque = deque(maxlen=MAX_HISTORY_POINTS)
    memory_history: deque = deque(maxlen=MAX_HISTORY_POINTS)
    disk_history: deque = deque(maxlen=MAX_HISTORY_POINTS)

    # Event handlers
    def on_backup(e: ft.ControlEvent) -> None:
        show_success_message(page, "Backup initiated (mock)")

    def start_server(e: ft.ControlEvent) -> None:
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

    def stop_server(e: ft.ControlEvent) -> None:
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

    def refresh_dashboard(e: ft.ControlEvent) -> None:
        """Refresh all dashboard data (async to avoid blocking UI)."""
        nonlocal countdown_remaining
        countdown_remaining = POLLING_INTERVAL
        _update_refresh_countdown_display("Refreshing…")
        try:
            async def _manual_refresh() -> None:
                await _update_all_displays_async('manual')
            page.run_task(_manual_refresh)
        except Exception:
            # Fallback to sync update
            update_all_displays()
        show_success_message(page, "Dashboard refreshed")

    # Define UI controls that are used in update_all_displays
    # Dynamic hero metric value controls for live updates
    hero_total_clients_text = ft.Text("0", size=44, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
    hero_total_clients_trend_icon = ft.Icon(ft.Icons.TRENDING_FLAT, size=16, color=ft.Colors.OUTLINE)
    hero_total_clients_trend_text = ft.Text("+0", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.OUTLINE)
    hero_total_clients_trend = ft.Container(
        content=ft.Row([hero_total_clients_trend_icon, hero_total_clients_trend_text], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.14, ft.Colors.OUTLINE)
    )

    hero_active_transfers_text = ft.Text("0", size=44, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
    hero_active_transfers_trend_icon = ft.Icon(ft.Icons.TRENDING_FLAT, size=16, color=ft.Colors.OUTLINE)
    hero_active_transfers_trend_text = ft.Text("+0", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.OUTLINE)
    hero_active_transfers_trend = ft.Container(
        content=ft.Row([hero_active_transfers_trend_icon, hero_active_transfers_trend_text], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.14, ft.Colors.OUTLINE)
    )

    hero_uptime_text = ft.Text("0h 0m", size=44, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
    hero_uptime_trend_icon = ft.Icon(ft.Icons.UPDATE, size=16, color=ft.Colors.OUTLINE)
    hero_uptime_trend_text = ft.Text("Stable", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.OUTLINE)
    hero_uptime_trend = ft.Container(
        content=ft.Row([hero_uptime_trend_icon, hero_uptime_trend_text], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.14, ft.Colors.OUTLINE)
    )

    # Define buttons that are used in update_all_displays
    button_shape = ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12))
    connect_button = ft.FilledButton(text="Connect", icon=ft.Icons.PLAY_ARROW, on_click=start_server, style=button_shape)
    apply_semantics(connect_button, "Connect to server")

    backup_button = ft.FilledTonalButton(text="Backup", icon=ft.Icons.BACKUP, on_click=on_backup, style=button_shape)
    apply_semantics(backup_button, "Start backup")

    disconnect_button = ft.OutlinedButton(
        text="Disconnect",
        icon=ft.Icons.STOP,
        on_click=stop_server,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            color={ft.ControlState.DEFAULT: ft.Colors.ERROR},
            side={ft.ControlState.DEFAULT: ft.BorderSide(1, ft.Colors.ERROR)}
        )
    )
    apply_semantics(disconnect_button, "Disconnect server")

    refresh_button = ft.FilledTonalButton(text="Refresh", icon=ft.Icons.REFRESH, on_click=refresh_dashboard, style=button_shape)
    apply_semantics(refresh_button, "Refresh dashboard")

    # Define server status indicator container
    server_status_indicator_container = ft.Container()
    apply_semantics(server_status_indicator_container, "Server connection status")
    server_status_indicator_container.content = create_status_pill("Checking", "info")

    # Get server status data with improved type safety and timeout protection
    def get_server_status() -> dict[str, Any]:
        """Get server status using server bridge or placeholder data, normalized. Protected against hangs."""
        try:
            # Add timeout protection to prevent hanging
            if server_bridge:
                import signal
                import platform

                def timeout_handler(signum, frame):
                    raise TimeoutError("Server status call timed out")

                # Only use signal on Unix-like systems
                if platform.system() != "Windows":
                    sigalrm = getattr(signal, 'SIGALRM', None)
                    alarm_func = getattr(signal, 'alarm', None)
                    if sigalrm is not None and alarm_func is not None:
                        old_handler = signal.signal(sigalrm, timeout_handler)
                        alarm_func(3)  # 3 second timeout
                    else:
                        old_handler = None

                try:
                    result = safe_server_call(server_bridge.get_server_status)
                    if result:
                        raw = result.get('data', {})
                        logger.debug(f"Raw server status from bridge: {raw}")
                        normalized = _normalize_server_status_payload(raw)
                        logger.debug(f"Normalized server status: {normalized}")
                        if normalized:
                            return normalized
                        # Fall back to raw if normalization yielded empty (unknown shape)
                        if isinstance(raw, dict):
                            return raw
                finally:
                    if platform.system() != "Windows" and old_handler is not None and alarm_func is not None and sigalrm is not None:
                        alarm_func(0)  # Cancel alarm
                        signal.signal(sigalrm, old_handler)
        except Exception as e:
            logger.debug(f"Server status call failed or timed out: {e}")

        # Lorem ipsum style placeholder data for GUI-only mode
        logger.debug("No server data available, returning lorem ipsum placeholder status")
        return {
            'running': True,
            'port': 8080,
            'uptime_seconds': 3600,  # 1 hour
            'clients_connected': 3,
            'total_files': 42,
            'total_transfers': 7,
            'storage_used_gb': 12.5
        }

    # Get system metrics using psutil with type safety and timeout protection
    def get_system_metrics() -> dict[str, Any]:
        """Prefer server-reported system metrics; fall back to psutil. Protected against hangs."""
        # Try server metrics first with timeout protection
        try:
            if server_bridge:
                # Quick timeout for server metrics to prevent hanging
                result = safe_server_call(server_bridge.get_system_status)
                if result:
                    data = result.get('data', {})
                    # Typical fields: cpu_percent, memory_percent, disk_percent
                    if isinstance(data, dict) and any(k in data for k in ('cpu_percent', 'memory_percent', 'disk_percent')):
                        cpu_p = float(data.get('cpu_percent', 0.0))
                        mem_p = float(data.get('memory_percent', data.get('mem_percent', 0.0)))
                        disk_p = float(data.get('disk_percent', data.get('storage_percent', 0.0)))
                        return {
                            'cpu_percent': cpu_p,
                            'memory_percent': mem_p,
                            'disk_percent': disk_p
                        }
        except Exception as e:
            logger.debug(f"Server metrics call failed: {e}")

        # Fallback to psutil with quick timeout
        try:
            # Use shorter interval to avoid blocking
            cpu_percent = psutil.cpu_percent(interval=0.01)  # Faster
            memory = psutil.virtual_memory()
            # Use current directory for disk usage on Windows
            import os
            disk_path = os.getcwd() if os.name == 'nt' else '/'
            disk = psutil.disk_usage(disk_path)
            return {
                'cpu_percent': float(cpu_percent),
                'memory_percent': float(memory.percent),
                'disk_percent': float((disk.used / disk.total) * 100)
            }
        except Exception as e:
            logger.debug(f"Failed to get system metrics: {e}")
            # Lorem ipsum style placeholder system metrics for GUI demonstration
            return {
                'cpu_percent': 35.7,  # Sample CPU usage
                'memory_percent': 62.3,  # Sample memory usage
                'disk_percent': 45.1  # Sample disk usage
            }

    # Cached helper functions for better performance
    @lru_cache(maxsize=32)
    def get_activity_icon(activity_type: ActivityType) -> str:
        """Get icon for activity type with caching."""
        icon_map = {
            'success': ft.Icons.CHECK_CIRCLE_OUTLINE,
            'error': ft.Icons.ERROR_OUTLINE,
            'warning': ft.Icons.WARNING_AMBER,
            'info': ft.Icons.INFO_OUTLINE
        }
        return icon_map.get(activity_type, ft.Icons.INFO_OUTLINE)

    @lru_cache(maxsize=32)
    def get_activity_color(activity_type: ActivityType) -> str:
        """Get color for activity type with caching."""
        color_map = {
            'success': ft.Colors.GREEN,
            'error': ft.Colors.RED,
            'warning': ft.Colors.ORANGE,
            'info': ft.Colors.BLUE
        }
        return color_map.get(activity_type, ft.Colors.BLUE)

    def normalize_activity_type(level: str) -> ActivityType:
        """Normalize activity level to valid ActivityType."""
        normalized = str(level).lower()
        from typing import cast
        if normalized in ['info', 'warning', 'error', 'success']:
            return cast(ActivityType, normalized)
        return 'info'

    # Get activity data with improved type safety and timeout protection
    def get_activity_data() -> list[ActivityEntry]:
        """Get recent activity data using logs as canonical source, with mock fallback. Protected against hangs."""
        try:
            if server_bridge:
                # Quick attempt to get logs with timeout protection
                logs_result = safe_server_call(server_bridge.get_logs)
                if logs_result:
                    entries = logs_result.get('data', [])
                    if isinstance(entries, list) and entries:
                        activities: list[ActivityEntry] = []
                        for i, entry in enumerate(entries[:50]):  # Limit to prevent excessive processing
                            # Normalize fields with type safety
                            level = normalize_activity_type(entry.get('level', entry.get('severity', 'info')))
                            msg = str(entry.get('message', entry.get('msg', '')))
                            ts = entry.get('timestamp', entry.get('time', datetime.now()))

                            activities.append({
                                'id': i + 1,
                                'type': level,
                                'message': msg,
                                'timestamp': ts
                            })
                        return sorted(activities, key=lambda x: x['timestamp'], reverse=True)
        except Exception as e:
            logger.debug(f"Activity data call failed: {e}")

        # Lorem ipsum style placeholder activity data for GUI demonstration
        logger.debug("No activity data available from server, returning lorem ipsum activities")

        # Sample activity entries with Latin-inspired content
        sample_activities = [
            {
                'id': 1,
                'type': 'success',
                'message': 'Lorem client connected successfully from ipsum.network',
                'timestamp': datetime.now() - timedelta(minutes=5)
            },
            {
                'id': 2,
                'type': 'info',
                'message': 'Dolor backup scheduled for 23:00 UTC',
                'timestamp': datetime.now() - timedelta(minutes=12)
            },
            {
                'id': 3,
                'type': 'success',
                'message': 'Amet file transfer completed: document.pdf (2.3 MB)',
                'timestamp': datetime.now() - timedelta(minutes=18)
            },
            {
                'id': 4,
                'type': 'warning',
                'message': 'Consectetur storage usage at 75% capacity',
                'timestamp': datetime.now() - timedelta(minutes=25)
            },
            {
                'id': 5,
                'type': 'info',
                'message': 'Adipiscing database maintenance completed',
                'timestamp': datetime.now() - timedelta(minutes=31)
            },
            {
                'id': 6,
                'type': 'success',
                'message': 'Elit security scan passed for all clients',
                'timestamp': datetime.now() - timedelta(minutes=47)
            }
        ]

        return sample_activities

    def create_premium_hero_card(
        value: str,
        label: str,
        trend: str = "",
        card_type: str = "primary",
        value_control=None,
        trend_control: ft.Control | None = None,
        on_click=None
    ) -> ft.Control:
        """Create a polished hero metric tile with higher contrast and helpful semantics."""
        color_map = {
            "success": ft.Colors.GREEN,
            "info": ft.Colors.BLUE,
            "primary": ft.Colors.PRIMARY
        }
        accent = color_map.get(card_type, ft.Colors.PRIMARY)

        trend_widget = None
        if trend_control is not None:
            trend_widget = trend_control
        elif trend:
            is_positive = trend.startswith("+")
            trend_widget = ft.Row([
                ft.Icon(ft.Icons.TRENDING_UP if is_positive else ft.Icons.TRENDING_DOWN, size=16, color=accent),
                ft.Text(trend, size=14, weight=ft.FontWeight.BOLD, color=accent)
            ], spacing=4)

        value_text = value_control or ft.Text(value, size=44, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
        apply_semantics(value_text, f"{label} value {value}")
        label_text = ft.Text(label, size=16, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE_VARIANT)

        tile = ft.Container(
            content=ft.Column([
                ft.Row([value_text, trend_widget or ft.Container()], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                label_text
            ], spacing=10),
            padding=24,
            border_radius=18,
            bgcolor=ft.Colors.with_opacity(0.08, accent),
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, accent)),
            shadow=ft.BoxShadow(
                blur_radius=8,
                spread_radius=0,
                offset=ft.Offset(0, 4),
                color=ft.Colors.with_opacity(0.15, accent)
            ),
            on_click=on_click,
            animate=ft.Animation(160, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(110, ft.AnimationCurve.EASE_OUT)
        )
        apply_semantics(tile, f"{label} metric card")
        return tile


    def create_premium_activity_stream() -> ft.Card:
        """Create activity stream with interactive filters and search."""

        filter_labels = ["All", "Success", "Info", "Warning", "Error"]
        activity_filter_chips.clear()
        chips: list[ft.FilterChip] = []
        current_filter_key = activity_filter.lower()
        for label in filter_labels:
            key = label.lower()
            chip = cast(Any, ft.FilterChip(
                label=label,
                selected=key == current_filter_key,
                on_selected=lambda event, option=label: _handle_chip_event(option, event)
            ))  # type: ignore[arg-type]
            activity_filter_chips[key] = chip
            chips.append(chip)

        filter_row = ft.Row(chips, spacing=8, wrap=True)

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TIMELINE, size=24, color=ft.Colors.PURPLE_600),
                        ft.Text("Live Activity", size=20, weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        activity_search_field,
                    ], spacing=8, wrap=True, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    filter_row,
                    ft.Container(
                        content=activity_list,
                        height=180,
                        border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.PURPLE_200)
                    )
                ], spacing=12),
                padding=20
            ),
            elevation=2
        )


    # UI Controls
    # Header metadata
    last_updated_text = ft.Text("Last updated: Never", size=12)
    header_summary_text = ft.Text("Server status: Checking…", size=12, color=ft.Colors.OUTLINE)
    refresh_countdown_text = ft.Text("Next refresh: 30s", size=12, color=ft.Colors.OUTLINE)
    # Slim live refresh indicator displayed during async updates
    refresh_indicator = ft.ProgressBar(height=3, value=None, visible=False)

    def _update_refresh_countdown_display(message: str | None = None) -> None:
        if message is not None:
            refresh_countdown_text.value = message
        else:
            if not auto_refresh_enabled:
                refresh_countdown_text.value = "Auto refresh paused"
            else:
                refresh_countdown_text.value = f"Next refresh: {max(0, int(countdown_remaining))}s"
        with contextlib.suppress(Exception):
            refresh_countdown_text.update()

    cpu_text = ft.Text("CPU: 0%", size=14)
    cpu_progress = ft.ProgressBar(value=0.0, width=220, bar_height=6)
    memory_text = ft.Text("Memory: 0%", size=14)
    memory_progress = ft.ProgressBar(value=0.0, width=220, bar_height=6, bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.GREEN))
    disk_text = ft.Text("Disk: 0%", size=14)
    disk_progress = ft.ProgressBar(value=0.0, width=220, bar_height=6, bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.PURPLE))

    # Activity list
    activity_list = ft.ListView(
        expand=True,
        spacing=5,
        padding=ft.padding.all(10)
    )

    def _on_activity_search_change(e: ft.ControlEvent) -> None:
        nonlocal activity_search_query
        activity_search_query = (e.control.value or "").strip()
        update_activity_list()

    def _on_activity_filter_selected(option: str) -> None:
        nonlocal activity_filter
        activity_filter = option
        for key, chip in activity_filter_chips.items():
            try:
                chip.selected = key == option.lower()  # type: ignore[attr-defined]
            except Exception:
                setattr(chip, 'selected', key == option.lower())
            with contextlib.suppress(Exception):
                chip.update()
        update_activity_list()

    def _handle_chip_event(option: str, event: ft.ControlEvent) -> None:
        if not getattr(event.control, 'selected', False):
            try:
                event.control.selected = True  # type: ignore[attr-defined]
            except Exception:
                setattr(event.control, 'selected', True)
            with contextlib.suppress(Exception):
                event.control.update()
            return
        _on_activity_filter_selected(option)

    activity_search_field = ft.TextField(
        hint_text="Search activity",
        prefix_icon=ft.Icons.SEARCH,
        on_change=_on_activity_search_change,
        dense=True,
        filled=True,
        border_radius=20,
        width=280,
    )

    # Clients snapshot controls
    clients_list = ft.ListView(expand=True, spacing=6, padding=ft.padding.all(10))
    clients_empty = ft.Text("No clients available", size=12, color=ft.Colors.OUTLINE)

    # Capacity & forecast controls
    used_text = ft.Text("Used: --", size=14)
    apply_semantics(used_text, "Total storage used")
    free_text = ft.Text("Free: --", size=14)
    apply_semantics(free_text, "Total storage free")
    forecast_text = ft.Text("Forecast: --", size=12, color=ft.Colors.OUTLINE)
    apply_semantics(forecast_text, "Storage forecast")
    capacity_health_badge_text = ft.Text("Healthy", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN)
    capacity_health_badge_icon = ft.Icon(ft.Icons.HEALTH_AND_SAFETY, size=14, color=ft.Colors.GREEN)
    capacity_health_badge = ft.Container(
        content=ft.Row([
            capacity_health_badge_icon,
            capacity_health_badge_text
        ], spacing=6),
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        border_radius=14,
        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.GREEN)
    )
    capacity_ring_percent = ft.Text("0%", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE)
    capacity_progress_ring = ft.ProgressRing(value=0.0, width=160, height=160, stroke_width=8, color=ft.Colors.BLUE)
    # Real PieChart instead of placeholder
    capacity_pie = ft.PieChart(
        sections=[],
        sections_space=2,
        center_space_radius=50,
        height=200,
        width=200,
    )
    capacity_ring_stack = ft.Stack([
        ft.Container(content=capacity_progress_ring, alignment=ft.alignment.center),
        capacity_pie,
        ft.Container(content=capacity_ring_percent, alignment=ft.alignment.center)
    ], width=200, height=200)

    # KPI controls
    kpi_total_clients_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    kpi_active_jobs_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    kpi_errors_24h_text = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
    kpi_storage_used_text = ft.Text("0 GB", size=28, weight=ft.FontWeight.BOLD)

    def _kpi_card(value_control, label: str, icon: str, color, on_click=None) -> ft.Container:
        """Simplified KPI card using Flet's native features."""
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
            on_click=on_click,
            tooltip=label,
        )

    # Navigation helpers using the app_ref exposed on page
    def _switch_view(index: int) -> None:
        app_ref = getattr(page, "app_ref", None)
        if app_ref is None:
            return
        switcher = getattr(app_ref, "_switch_to_view", None)
        if callable(switcher):
            with contextlib.suppress(Exception):
                switcher(index)

    def _go_to_clients(e: ft.ControlEvent | None = None) -> None:
        _switch_view(1)

    def _go_to_files(e: ft.ControlEvent | None = None) -> None:
        _switch_view(2)

    def _go_to_logs(e: ft.ControlEvent | None = None) -> None:
        _switch_view(5)

    kpi_row = ft.ResponsiveRow([
        ft.Column([_kpi_card(kpi_total_clients_text, "Total Clients", ft.Icons.PEOPLE, ft.Colors.BLUE, on_click=_go_to_clients)], col={"sm": 6, "md": 3, "lg": 3}),
        ft.Column([_kpi_card(kpi_active_jobs_text, "Active Jobs", ft.Icons.SYNC, ft.Colors.CYAN)], col={"sm": 6, "md": 3, "lg": 3}),
        ft.Column([_kpi_card(kpi_errors_24h_text, "Errors (24h)", ft.Icons.ERROR_OUTLINE, ft.Colors.RED)], col={"sm": 6, "md": 3, "lg": 3}),
        ft.Column([_kpi_card(kpi_storage_used_text, "Storage Used", ft.Icons.STORAGE, ft.Colors.PURPLE, on_click=_go_to_files)], col={"sm": 6, "md": 3, "lg": 3}),
    ], spacing=12)

    # Live system sparkline charts using native LineChart for better performance
    def _create_sparkline(color) -> ft.LineChart:
        return ft.LineChart(
            data_series=[ft.LineChartData(
                data_points=[],
                color=color,
                stroke_width=2,
                curved=True,
                prevent_curve_over_shooting=True
            )],
            min_y=0,
            max_y=100,
            width=220,
            height=70,
            interactive=False,
            bgcolor=ft.Colors.TRANSPARENT,
            border=ft.border.all(1, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE)),
            horizontal_grid_lines=ft.ChartGridLines(
                color=ft.Colors.with_opacity(0.1, color),
                width=1
            ),
            vertical_grid_lines=ft.ChartGridLines(
                color=ft.Colors.with_opacity(0.1, color),
                width=1
            )
        )

    cpu_spark = _create_sparkline(ft.Colors.BLUE)
    mem_spark = _create_sparkline(ft.Colors.GREEN)
    disk_spark = _create_sparkline(ft.Colors.PURPLE)

    def _metric_tile(title: str, summary_text: ft.Control, progress_bar: ft.ProgressBar, chart: ft.LineChart, accent: str, semantics: str) -> ft.Container:
        container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(title, size=12, color=ft.Colors.with_opacity(0.8, accent), weight=ft.FontWeight.W_600)
                ]),
                summary_text,
                ft.Container(content=progress_bar, padding=ft.padding.only(top=2, bottom=4)),
                chart
            ], spacing=8),
            padding=ft.padding.all(12),
            border_radius=14,
            bgcolor=ft.Colors.with_opacity(0.08, accent),
            shadow=ft.BoxShadow(
                blur_radius=12,
                offset=ft.Offset(0, 6),
                color=ft.Colors.with_opacity(0.15, accent)
            )
        )
        # Per-metric diagnostic coloring (distinct overlay) when metrics diagnostics active
        if os.environ.get("FLET_DASHBOARD_DIAG_METRICS") == "1":  # pragma: no cover - diagnostics only
            try:
                container.border = ft.border.all(1, accent)
                # Slightly stronger background to visually differentiate tiles even if internal content invisible
                container.bgcolor = ft.Colors.with_opacity(0.18, accent)
            except Exception:  # noqa: BLE001
                pass
        apply_semantics(container, semantics)
        return container

    def _update_trend_chip(
        icon_control: Any,
        text_control: Any,
        container: ft.Container,
        delta: float,
        *,
        zero_label: str = "0",
        suffix: str = ""
    ) -> None:
        """Update hero metric trend chip with dynamic coloring and iconography."""
        try:
            if icon_control is None or text_control is None or container is None:
                return

            suffix_text = suffix or ""
            delta_value = float(delta)
            if delta_value > 0:
                color = ft.Colors.GREEN
                icon_control.name = ft.Icons.TRENDING_UP
                display_value = (
                    f"+{int(delta_value)}{suffix_text}"
                    if delta_value.is_integer()
                    else f"+{delta_value:.1f}{suffix_text}"
                )
            elif delta_value < 0:
                color = ft.Colors.RED
                icon_control.name = ft.Icons.TRENDING_DOWN
                display_value = (
                    f"{int(delta_value)}{suffix_text}"
                    if delta_value.is_integer()
                    else f"{delta_value:.1f}{suffix_text}"
                )
            else:
                color = ft.Colors.OUTLINE
                icon_control.name = ft.Icons.TRENDING_FLAT
                display_value = zero_label

            text_control.value = display_value.strip()
            text_control.color = color
            icon_control.color = color
            container.bgcolor = ft.Colors.with_opacity(0.18, color)

            container.update()
            text_control.update()
            icon_control.update()
        except Exception:
            pass

    def _update_spark(chart: ft.LineChart, values: list[float], color) -> None:
        """Update sparkline with efficient LineChart data points using modern Python."""
        # Use walrus operator and generator expression for efficiency
        if not (limited_values := values[-MAX_HISTORY_POINTS:]):
            return

        data_points = [
            ft.LineChartDataPoint(x=i, y=max(0.0, min(100.0, float(v))))
            for i, v in enumerate(limited_values)
        ]

        chart.data_series = [ft.LineChartData(
            data_points=data_points,
            color=color,
            stroke_width=2,
            curved=True,
            prevent_curve_over_shooting=True
        )]
        with contextlib.suppress(Exception):
            chart.update()


    # Update all displays
    def _compute_server_status_label(running: bool) -> tuple[str, str]:
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

    def update_all_displays() -> None:
        """Update all dashboard displays with current data."""
        nonlocal current_server_status, current_system_metrics, current_activity, current_clients, last_updated
        nonlocal cpu_history, memory_history, disk_history, prev_server_snapshot, is_loading

        is_loading = False

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
        else:
            # Lorem ipsum style placeholder clients for GUI demonstration
            current_clients = [
                {
                    'name': 'Lorem Desktop',
                    'client_id': 'lorem-001',
                    'status': 'connected',
                    'type': 'desktop',
                    'last_seen': (datetime.now() - timedelta(minutes=2)).isoformat(),
                    'last_activity': (datetime.now() - timedelta(minutes=2)).isoformat()
                },
                {
                    'name': 'Ipsum Server',
                    'client_id': 'ipsum-002',
                    'status': 'active',
                    'type': 'server',
                    'last_seen': (datetime.now() - timedelta(minutes=15)).isoformat(),
                    'last_activity': (datetime.now() - timedelta(minutes=15)).isoformat()
                },
                {
                    'name': 'Dolor Laptop',
                    'client_id': 'dolor-003',
                    'status': 'idle',
                    'type': 'laptop',
                    'last_seen': (datetime.now() - timedelta(hours=1)).isoformat(),
                    'last_activity': (datetime.now() - timedelta(hours=1)).isoformat()
                }
            ]
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

        # Safely update text controls
        try:
            cpu_text.value = f"CPU: {cpu_percent:.1f}%"
            memory_text.value = f"Memory: {memory_percent:.1f}%"
            disk_text.value = f"Disk: {disk_percent:.1f}%"
        except Exception as e:
            logger.debug(f"Failed to update metric text controls: {e}")

        # Safely update progress controls
        try:
            cpu_progress.value = max(0.0, min(1.0, cpu_percent / 100))
            cpu_progress.color = ft.Colors.BLUE
            memory_progress.value = max(0.0, min(1.0, memory_percent / 100))
            memory_progress.color = ft.Colors.GREEN
            disk_progress.value = max(0.0, min(1.0, disk_percent / 100))
            disk_progress.color = ft.Colors.PURPLE

            # Safely update individual controls
            with contextlib.suppress(Exception):
                cpu_progress.update()
            with contextlib.suppress(Exception):
                memory_progress.update()
            with contextlib.suppress(Exception):
                disk_progress.update()
        except Exception:
            pass

        # Update history and sparklines with memory-efficient deque
        try:
            cpu_history.append(float(cpu_percent))
            memory_history.append(float(memory_percent))
            disk_history.append(float(disk_percent))
            # Deque automatically maintains maxlen, no manual truncation needed
            _update_spark(cpu_spark, list(cpu_history), ft.Colors.BLUE)
            _update_spark(mem_spark, list(memory_history), ft.Colors.GREEN)
            _update_spark(disk_spark, list(disk_history), ft.Colors.PURPLE)
        except Exception as e:
            logger.debug(f"Failed to update sparklines: {e}")

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
            capacity_ring_percent.value = f"{used_pct:.0f}%"

            capacity_color = ft.Colors.GREEN
            if used_pct >= 90:
                capacity_color = ft.Colors.RED
            elif used_pct >= 80:
                capacity_color = ft.Colors.ORANGE
            capacity_progress_ring.value = max(0.0, min(1.0, used_pct / 100))
            capacity_progress_ring.color = capacity_color
            capacity_ring_percent.color = capacity_color
            capacity_health_badge.bgcolor = ft.Colors.with_opacity(0.16, capacity_color)
            capacity_health_badge_text.color = capacity_color
            capacity_health_badge_icon.color = capacity_color
            capacity_health_badge_text.value = proj

            # Rebuild pie sections efficiently by replacing sections list
            capacity_pie.sections = [
                ft.PieChartSection(value=used_pct, color=ft.Colors.BLUE, title="Used", radius=80,
                                   badge=ft.Text(f"{used_pct:.0f}%", size=10, color=ft.Colors.WHITE)),
                ft.PieChartSection(value=free_pct, color=ft.Colors.GREEN, title="Free", radius=80,
                                   badge=ft.Text(f"{free_pct:.0f}%", size=10, color=ft.Colors.WHITE)),
            ]
            with contextlib.suppress(Exception):
                capacity_progress_ring.update()
                capacity_ring_percent.update()
                capacity_health_badge_text.update()
                capacity_health_badge_icon.update()
                capacity_health_badge.update()
        except Exception as e:
            logger.debug(f"Capacity update failed: {e}")

        # Update KPI values
        try:
            logger.debug(f"Updating KPI values with server status: {current_server_status}")

            # Total clients - prefer database count over active connections
            logger.debug(f"KPI calculation - current_clients has {len(current_clients)} items")
            total_clients_val = len(current_clients) if current_clients else current_server_status.get('clients_connected', 0)
            logger.debug(f"Setting total clients to: {total_clients_val} (from {'database' if current_clients else 'server_status'})")

            # Safely update hero metrics (these are the main visible content)
            try:
                kpi_total_clients_text.value = str(total_clients_val)
                hero_total_clients_text.value = str(total_clients_val)
                logger.debug(f"Hero metrics updated: total_clients={total_clients_val}")
            except Exception as e:
                logger.debug(f"Failed to update hero total clients: {e}")

            prev_clients_val = total_clients_val
            prev_transfers_val = current_server_status.get('total_transfers', 0)
            prev_uptime_val = current_server_status.get('uptime_seconds', 0)
            if isinstance(prev_server_snapshot, dict):
                with contextlib.suppress(Exception):
                    prev_clients_val = int(prev_server_snapshot.get('clients_connected', prev_clients_val))
                    prev_transfers_val = int(prev_server_snapshot.get('total_transfers', prev_transfers_val) or 0)
                    prev_uptime_val = int(prev_server_snapshot.get('uptime_seconds', prev_uptime_val))

            delta_clients = total_clients_val - prev_clients_val
            delta_transfers = int(current_server_status.get('total_transfers', 0) or 0) - int(prev_transfers_val or 0)
            delta_uptime = int(current_server_status.get('uptime_seconds', 0) or 0) - int(prev_uptime_val or 0)

            _update_trend_chip(
                hero_total_clients_trend_icon,
                hero_total_clients_trend_text,
                hero_total_clients_trend,
                delta_clients,
                zero_label="No change",
                suffix=" clients"
            )
            _update_trend_chip(
                hero_active_transfers_trend_icon,
                hero_active_transfers_trend_text,
                hero_active_transfers_trend,
                delta_transfers,
                zero_label="No change",
                suffix=" jobs"
            )

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
            logger.debug(f"Setting active jobs to: {active_jobs}")
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
            logger.debug(f"Setting errors 24h to: {err24}")
            kpi_errors_24h_text.value = str(err24)

            # Storage used
            storage_val = current_server_status.get('storage_used_gb', 0)
            logger.debug(f"Setting storage used to: {storage_val}")
            kpi_storage_used_text.value = f"{storage_val:.1f} GB"

            # Active transfers and uptime hero metrics
            try:
                hero_active_transfers_text.value = str(current_server_status.get('total_transfers', 0))
                logger.debug(f"Hero metrics updated: total_transfers={current_server_status.get('total_transfers', 0)}")
            except Exception as e:
                logger.debug(f"Failed to update hero active transfers: {e}")

            try:
                up = int(current_server_status.get('uptime_seconds', 0))
                uh, um = up // 3600, (up % 3600) // 60
                hero_uptime_text.value = f"{uh}h {um}m"
                logger.debug(f"Hero metrics updated: uptime={uh}h {um}m")
            except Exception as e:
                logger.debug(f"Failed to update hero uptime: {e}")
                try:
                    hero_uptime_text.value = "0h 0m"
                except Exception:
                    pass

            # Uptime trend expressed in minutes difference
            with contextlib.suppress(Exception):
                delta_uptime_minutes = int(delta_uptime / 60)
                _update_trend_chip(
                    hero_uptime_trend_icon,
                    hero_uptime_trend_text,
                    hero_uptime_trend,
                    delta_uptime_minutes,
                    zero_label="Stable",
                    suffix=" min"
                )
        except Exception:
            pass

        # Update header status indicator
        try:
            label, severity = _compute_server_status_label(running)
            severity_map = {
                "excellent": "success",
                "good": "success",
                "warning": "warning",
                "critical": "error",
                "info": "info",
                "neutral": "default",
            }
            server_status_indicator_container.content = create_status_pill(label, severity_map.get(severity, "info"))
        except Exception:
            pass

        # Update header summaries
        try:
            port_display = current_server_status.get('port') or current_server_status.get('listening_port') or "—"
            storage_val = current_server_status.get('storage_used_gb')
            storage_display = f"{storage_val:.1f} GB" if isinstance(storage_val, (int, float)) else "—"
            summary_parts = [
                "Online" if running else "Offline",
                f"Port {port_display}",
                f"Storage {storage_display}"
            ]
            header_summary_text.value = " • ".join(summary_parts)
            header_summary_text.update()
        except Exception:
            pass

        # Update last updated
        last_updated_text.value = f"Last updated: {last_updated}"

        # Simplified update pattern using Flet's efficient update system
        try:
            # Explicitly update each KPI control (these are critical for display)
            with contextlib.suppress(Exception):
                kpi_total_clients_text.update()
            with contextlib.suppress(Exception):
                kpi_active_jobs_text.update()
            with contextlib.suppress(Exception):
                kpi_errors_24h_text.update()
            with contextlib.suppress(Exception):
                kpi_storage_used_text.update()

            # Update hero metrics (main dashboard content)
            with contextlib.suppress(Exception):
                hero_total_clients_text.update()
            with contextlib.suppress(Exception):
                hero_active_transfers_text.update()
            with contextlib.suppress(Exception):
                hero_uptime_text.update()
            with contextlib.suppress(Exception):
                last_updated_text.update()

            # Update trend chips to reflect new styling
            with contextlib.suppress(Exception):
                hero_total_clients_trend.update()
            with contextlib.suppress(Exception):
                hero_active_transfers_trend.update()
            with contextlib.suppress(Exception):
                hero_uptime_trend.update()

            # Use control.update() for 10x performance improvement over page.update()
            with contextlib.suppress(Exception):
                dashboard_container.update()
            logger.debug("Dashboard container updated successfully")
        except Exception as e:
            logger.debug(f"Update failed: {e}")
            # Fallback to page update if control update fails
            try:
                page.update()
                logger.debug("Fallback page update completed")
            except Exception as e2:
                logger.error(f"Both control and page updates failed: {e2}")

        with contextlib.suppress(Exception):
            if isinstance(current_server_status, dict):
                prev_server_snapshot = dict(current_server_status)

    async def _update_all_displays_async(source: str = 'auto') -> None:
        """Async version of update_all_displays."""
        nonlocal current_server_status, current_system_metrics, current_activity, current_clients, last_updated, prev_server_snapshot, last_significant_toast_time, is_loading, countdown_remaining

        try:
            # Show slim refresh indicator during async updates
            refresh_indicator.visible = True
            with contextlib.suppress(Exception):
                refresh_indicator.update()
            is_loading = True
            _update_refresh_countdown_display("Refreshing…")

            import asyncio
            loop = asyncio.get_event_loop()

            # Concurrent data fetching for better performance
            tasks = [
                loop.run_in_executor(None, get_server_status),
                loop.run_in_executor(None, get_system_metrics),
                loop.run_in_executor(None, get_activity_data)
            ]

            # Add clients task if server bridge available
            if server_bridge:
                tasks.append(loop.run_in_executor(None, server_bridge.get_all_clients_from_db))
            # Execute all data fetching concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results with proper type safety - use async results, not re-call functions
            current_server_status = results[0] if (not isinstance(results[0], Exception) and isinstance(results[0], dict)) else get_server_status()
            current_system_metrics = results[1] if (not isinstance(results[1], Exception) and isinstance(results[1], dict)) else get_system_metrics()

            # Handle activity data
            if isinstance(results[2], Exception):
                current_activity = []
            elif isinstance(results[2], list):
                current_activity = results[2]
            else:
                current_activity = []

            # Handle clients result if server bridge was used
            if server_bridge and len(results) > 3:
                clients_result = [] if isinstance(results[3], Exception) else results[3]
                if isinstance(clients_result, dict) and clients_result.get('success'):
                    current_clients = clients_result.get('data', [])
                elif isinstance(clients_result, list):
                    current_clients = clients_result
                else:
                    current_clients = []

            # Update displays with fetched data
            last_updated = datetime.now().strftime("%H:%M:%S")
            try:
                update_all_displays()
            except Exception as e:
                logger.debug(f"update_all_displays() failed: {e}")
            is_loading = False
            if source != 'auto':
                countdown_remaining = POLLING_INTERVAL
                _update_refresh_countdown_display()

        except Exception as e:
            logger.debug(f"Async display update failed: {e}")
        finally:
            # Save snapshot for next delta comparison
            try:
                prev_server_snapshot = dict(current_server_status) if isinstance(current_server_status, dict) else None
            except Exception:
                pass
            is_loading = False
            # Hide refresh indicator when finished
            refresh_indicator.visible = False
            with contextlib.suppress(Exception):
                refresh_indicator.update()

    async def _update_operations_panels_async() -> None:
        """Async version of operations panels update."""
        try:
            await asyncio.get_event_loop().run_in_executor(None, _update_operations_panels)
        except Exception as e:
            logger.debug(f"Async operations panels update failed: {e}")

    def update_activity_list() -> None:
        """Update the activity list."""
        nonlocal is_loading
        activity_list.controls.clear()

        if is_loading:
            skeletons = [
                ft.Container(
                    content=ft.ProgressRing(width=26, height=26, stroke_width=4),
                    height=56,
                    alignment=ft.alignment.center,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PURPLE_100),
                    border_radius=10,
                )
                for _ in range(3)
            ]
            activity_list.controls.extend(skeletons)
            with contextlib.suppress(Exception):
                activity_list.update()
            return

        # Filter activities with type safety
        safe_activity = current_activity if isinstance(current_activity, list) else []
        filter_key = activity_filter.lower()
        filtered_activities = (
            safe_activity if filter_key == "all" else
            [activity for activity in safe_activity
             if activity.get('type', '').lower() == filter_key]
        )

        if activity_search_query.strip():
            query = activity_search_query.strip().lower()
            filtered_activities = [
                activity for activity in filtered_activities
                if query in str(activity.get('message', '')).lower()
                or query in str(activity.get('type', '')).lower()
                or query in str(activity.get('timestamp', '')).lower()
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

            # Simplified list item with native Flet hover
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
            activity_list.controls.append(tile)

        try:
            activity_list.update()
        except Exception:
            pass

    def update_clients_list() -> None:
        """Update clients snapshot list from current_clients."""
        nonlocal is_loading
        clients_list.controls.clear()
        if is_loading:
            clients_list.controls.extend([
                ft.Container(
                    content=ft.Row([
                        ft.Shimmer(
                            gradient=ft.LinearGradient(colors=[ft.Colors.OUTLINE_VARIANT, ft.Colors.SURFACE, ft.Colors.OUTLINE_VARIANT]),
                            content=ft.Container(width=32, height=32, border_radius=16, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE))
                        ),
                        ft.Column([
                            ft.Container(width=120, height=10, border_radius=4, bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
                            ft.Container(width=80, height=8, border_radius=4, bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.OUTLINE))
                        ], spacing=6)
                    ], spacing=12, alignment=ft.MainAxisAlignment.START),
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.04, ft.Colors.OUTLINE)
                )
                for _ in range(3)
            ])
            with contextlib.suppress(Exception):
                clients_list.update()
            return
        if not current_clients:
            clients_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.PERSON_SEARCH, size=24, color=ft.Colors.OUTLINE),
                            ft.Text("No clients available", size=12, color=ft.Colors.OUTLINE)
                        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                        ft.ElevatedButton("View clients", icon=ft.Icons.ARROW_FORWARD, on_click=_go_to_clients)
                    ], spacing=12, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(16),
                    border_radius=12,
                    bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.OUTLINE)
                )
            )
        else:
            # Sort by last_seen desc when available
            def _parse_ts(v: Any) -> datetime:
                try:
                    if isinstance(v, datetime):
                        return v
                    # try ISO-like
                    return datetime.fromisoformat(str(v))
                except Exception:
                    return datetime.min

            sorted_clients = sorted(current_clients, key=lambda c: _parse_ts(c.get('last_seen') or c.get('last_activity')), reverse=True)
            status_styles = {
                'connected': 'success',
                'active': 'success',
                'online': 'success',
                'idle': 'warning',
                'warning': 'warning',
                'connecting': 'warning',
                'pending': 'info',
                'disconnected': 'error',
                'offline': 'error',
                'error': 'error'
            }

            device_icons = {
                'desktop': ft.Icons.COMPUTER,
                'server': ft.Icons.DNS,
                'laptop': ft.Icons.LAPTOP,
                'mobile': ft.Icons.SMARTPHONE,
            }

            for client in sorted_clients[:8]:
                name = client.get('name') or client.get('client_id', 'Unknown client')
                status_value = str(client.get('status', 'unknown'))
                status_key = status_value.lower()
                last_seen = client.get('last_seen', client.get('last_activity', '')) or "—"
                client_type = str(client.get('type', '')).lower()

                icon_symbol = device_icons.get(client_type, ft.Icons.DEVICE_HUB)
                status_chip = create_status_pill(status_value.title(), status_styles.get(status_key, 'info'))

                item = ft.Container(
                    content=ft.Row([
                        ft.CircleAvatar(
                            content=ft.Icon(icon_symbol, size=16, color=ft.Colors.WHITE),
                            radius=14,
                            bgcolor=ft.Colors.with_opacity(0.6, ft.Colors.BLUE_GREY_700)
                        ),
                        ft.Column([
                            ft.Text(name, size=13, weight=ft.FontWeight.W_500),
                            ft.Text(f"Last seen: {last_seen}", size=11, color=ft.Colors.OUTLINE)
                        ], spacing=2, expand=True),
                        status_chip,
                        ft.IconButton(
                            icon=ft.Icons.OPEN_IN_NEW,
                            tooltip="Open clients view",
                            on_click=_go_to_clients,
                        )
                    ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE_GREY_200),
                    animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
                )
                clients_list.controls.append(item)

    # Server control actions
    # Server and refresh handlers moved to event handlers section

    # Create UI components (header actions only)

    # Backup action (moved to event handlers section)

    # Premium asymmetric dashboard grid with sophisticated visual hierarchy
    hero_metrics_section = ft.ResponsiveRow([
        # Hero metric takes visual prominence with primary gradient
        ft.Column([
            create_premium_hero_card(
                "0",
                "Total Clients",
                "+0",
                "primary",
                value_control=hero_total_clients_text,
                trend_control=hero_total_clients_trend,
                on_click=_go_to_clients
            )
        ], col={"sm": 12, "md": 8, "lg": 6}),
        # Secondary metrics cluster with different gradient schemes
        ft.Column([
            ft.Column([
                create_premium_hero_card(
                    "0",
                    "Active Transfers",
                    "+0",
                    "success",
                    value_control=hero_active_transfers_text,
                    trend_control=hero_active_transfers_trend,
                    on_click=_go_to_files
                ),
                create_premium_hero_card(
                    "0h 0m",
                    "Server Uptime",
                    "",
                    "info",
                    value_control=hero_uptime_text,
                    trend_control=hero_uptime_trend,
                    on_click=_go_to_logs
                )
            ], spacing=20)
        ], col={"sm": 12, "md": 4, "lg": 6})
    ], spacing=28)


    # Capacity & Forecast card
    capacity_content = ft.Row([
        ft.Container(content=capacity_ring_stack, alignment=ft.alignment.center, width=220, height=220),
        ft.Column([
            ft.Text("Storage breakdown", size=14, weight=ft.FontWeight.W_600),
            capacity_health_badge,
            used_text,
            free_text,
            forecast_text,
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.START, alignment=ft.MainAxisAlignment.START, expand=True)
    ], spacing=24, vertical_alignment=ft.CrossAxisAlignment.CENTER, wrap=True)

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
    # Slim top bar: integrates status + actions in one compact bar
    def on_live_toggle(e: ft.ControlEvent) -> None:
        nonlocal auto_refresh_enabled, countdown_remaining
        auto_refresh_enabled = bool(e.control.value)
        if auto_refresh_enabled:
            countdown_remaining = POLLING_INTERVAL
            _update_refresh_countdown_display()
            show_success_message(page, "Live refresh enabled")
        else:
            _update_refresh_countdown_display("Auto refresh paused")
            show_success_message(page, "Live refresh paused")

    live_switch = ft.Switch(label="Live", value=True, on_change=on_live_toggle)
    apply_semantics(live_switch, "Live auto refresh toggle")
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
    ], "primary", semantics_label="Primary server actions")

    # Secondary actions - configuration and monitoring
    secondary_action_group = create_action_group([
        refresh_button,
        live_switch,
    ], "secondary", semantics_label="Secondary dashboard actions")

    quick_nav_menu = ft.PopupMenuButton(
        icon=ft.Icons.MENU_OPEN,
        items=[
            ft.PopupMenuItem(text="Clients", icon=ft.Icons.PEOPLE_OUTLINE, on_click=_go_to_clients),
            ft.PopupMenuItem(text="Files", icon=ft.Icons.FOLDER_OPEN, on_click=_go_to_files),
            ft.PopupMenuItem(text="Logs", icon=ft.Icons.TERMINAL, on_click=_go_to_logs),
        ],
    )
    quick_nav_menu.tooltip = "Quick navigation"

    header_row = ft.Row(
        [
            ft.Column([
                ft.Row([
                    ft.Text("Dashboard", size=20, weight=ft.FontWeight.W_600),
                    server_status_indicator_container,
                    quick_nav_menu,
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ft.Row([
                    header_summary_text,
                    refresh_countdown_text,
                    last_updated_text,
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], spacing=8, expand=True),
            primary_action_group,
            secondary_action_group,
        ],
        spacing=16,
        run_spacing=12,
        wrap=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    header_section = ft.Card(
        content=ft.Container(
            content=header_row,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.SURFACE_TINT)
        ),
        elevation=4,
        surface_tint_color=ft.Colors.TRANSPARENT,
    )
    header_section.animate_opacity = ft.Animation(250, ft.AnimationCurve.EASE_OUT)
    header_section.opacity = 1.0
    apply_semantics(header_section, "Dashboard controls")


    # Live System Metrics card with sparklines
    def _legend_item(color: str, label: str) -> ft.Container:
        return ft.Container(
            content=ft.Row([
                ft.Container(width=10, height=10, bgcolor=color, border_radius=5),
                ft.Text(label, size=11)
            ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.padding.symmetric(horizontal=8, vertical=4),
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.08, color)
        )

    metrics_tiles_row = ft.Row([
        _metric_tile("CPU", cpu_text, cpu_progress, cpu_spark, ft.Colors.BLUE, "CPU usage sparkline"),
        _metric_tile("Memory", memory_text, memory_progress, mem_spark, ft.Colors.GREEN, "Memory usage sparkline"),
        _metric_tile("Disk", disk_text, disk_progress, disk_spark, ft.Colors.PURPLE, "Disk usage sparkline"),
    ], spacing=16, run_spacing=12, wrap=True)

    # Additional diagnostics: label each tile and log structure when enabled
    if os.environ.get("FLET_DASHBOARD_DIAG_METRICS") == "1":  # pragma: no cover - diagnostics only
        try:
            logger.warning("[METRICS_DIAG] metrics_tiles_row created with %s children", len(metrics_tiles_row.controls))
            for idx, tile in enumerate(metrics_tiles_row.controls):
                try:
                    if isinstance(tile, ft.Container) and isinstance(tile.content, ft.Column):
                        # Prepend an index label so we can see if internal Column renders
                        tile.content.controls.insert(0, ft.Text(f"Tile #{idx}", size=10, color=ft.Colors.AMBER))
                        # Force diagnostic sizing to rule out collapse
                        if tile.width is None:
                            tile.width = 230
                        if tile.height is None:
                            tile.height = 150
                        # Distinct background overlay to differentiate
                        tile.bgcolor = ft.Colors.with_opacity(0.25, ft.Colors.AMBER if idx == 0 else (
                            ft.Colors.with_opacity(0.25, ft.Colors.GREEN) if idx == 1 else ft.Colors.with_opacity(0.25, ft.Colors.PURPLE)
                        ))
                        # Add explicit border for visibility
                        tile.border = ft.border.all(1, ft.Colors.AMBER if idx == 0 else (
                            ft.Colors.GREEN if idx == 1 else ft.Colors.PURPLE
                        ))
                except Exception:  # noqa: BLE001
                    pass
            # Force row non-expanding vertical sizing & log final tile dims
            metrics_tiles_row.alignment = ft.MainAxisAlignment.START
            metrics_tiles_row.vertical_alignment = ft.CrossAxisAlignment.START
            for idx, tile in enumerate(metrics_tiles_row.controls):
                try:
                    logger.warning(
                        "[METRICS_DIAG] Tile %s final size hints w=%s h=%s type=%s", idx, getattr(tile, 'width', None), getattr(tile, 'height', None), type(tile)
                    )
                except Exception:  # noqa: BLE001
                    pass
        except Exception:  # noqa: BLE001
            pass

    metrics_legend = ft.Row([
        _legend_item(ft.Colors.BLUE, "Compute"),
        _legend_item(ft.Colors.GREEN, "Memory"),
        _legend_item(ft.Colors.PURPLE, "Storage"),
    ], spacing=12, wrap=True)

    live_metrics_content = ft.Column([
        metrics_tiles_row,
        metrics_legend
    ], spacing=12)

    live_system_metrics_card = themed_card(
        content=live_metrics_content,
        title="LIVE SYSTEM METRICS",
        page=page
    )
    if os.environ.get("FLET_DASHBOARD_DIAG_METRICS") == "1":  # pragma: no cover
        try:
            logger.warning(
                "[METRICS_DIAG] live_system_metrics_card constructed: tiles=%s legend_controls=%s",
                len(metrics_tiles_row.controls),
                len(metrics_legend.controls)
            )
            # Force card sizing & background for troubleshooting blank/oversized region
            if getattr(live_system_metrics_card, 'content', None) and isinstance(live_system_metrics_card.content, ft.Container):
                inner = live_system_metrics_card.content
                try:
                    # Provide minimum height only; avoid infinite expansion
                    if inner.height is None:
                        inner.height = 250
                except Exception:  # noqa: BLE001
                    pass
            try:
                live_system_metrics_card.bgcolor = ft.Colors.with_opacity(0.10, ft.Colors.PURPLE)
            except Exception:  # noqa: BLE001
                pass
        except Exception:  # noqa: BLE001
            pass

    # Optional per-section diagnostics to highlight structural boundaries and sizes
    # Enable with FLET_DASHBOARD_DIAG_SECTIONS=1 and FLET_ENABLE_SECTION_DIAG=1
    if os.environ.get("FLET_DASHBOARD_DIAG_SECTIONS") == "1" and os.environ.get("FLET_ENABLE_SECTION_DIAG") == "1":  # pragma: no cover - diagnostics
        def _wrap(label: str, ctrl: ft.Control, color: str) -> ft.Control:
            try:
                return ft.Container(
                    content=ft.Column([
                        ft.Text(f"SECTION: {label}", size=12, color=color, weight=ft.FontWeight.BOLD),
                        ctrl
                    ], spacing=4),
                    border=ft.border.all(1, color),
                    padding=10,
                    margin=ft.margin.only(bottom=12),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.03, color)
                )
            except Exception:  # noqa: BLE001
                return ctrl
        header_section_ctrl = header_section
        header_section = _wrap("HEADER", header_section_ctrl, ft.Colors.ORANGE)
        kpi_row = _wrap("KPI_ROW", kpi_row, ft.Colors.CYAN)
        live_system_metrics_card = _wrap("METRICS_CARD", live_system_metrics_card, ft.Colors.PURPLE)

    # Running Jobs & Recent Backups sections
    running_jobs_list = ft.ListView(expand=True, spacing=6, padding=ft.padding.all(10), height=160)
    recent_backups_list = ft.ListView(expand=True, spacing=6, padding=ft.padding.all(10), height=160)

    def filter_activities_by_keywords(
        activities: list[ActivityEntry],
        keywords: list[str],
        time_window_minutes: int | None = None
    ) -> Iterator[ActivityEntry]:
        """Efficient activity filtering using generator and modern Python patterns."""
        now = datetime.now()
        time_threshold = timedelta(minutes=time_window_minutes) if time_window_minutes else None

        return (
            activity for activity in activities
            if any(keyword in activity['message'].lower() for keyword in keywords) and
               (not time_threshold or
                (isinstance(activity['timestamp'], datetime) and
                 (now - activity['timestamp']) <= time_threshold))
        )

    def create_operation_item(activity: ActivityEntry, icon: str, color: str, status_text: str | None = None) -> ft.Container:
        """Create operation item with type safety."""
        timestamp = activity['timestamp']
        time_display = timestamp.strftime("%H:%M") if isinstance(timestamp, datetime) else str(timestamp)
        subtitle = status_text or f"at {time_display}"

        return ft.Container(
            content=ft.ListTile(
                leading=ft.Icon(icon, color=color, size=18),
                title=ft.Text(activity['message'], size=13),
                subtitle=ft.Text(subtitle, size=11, color=ft.Colors.OUTLINE),
                dense=True
            ),
            border_radius=8,
            bgcolor=ft.Colors.with_opacity(0.05, color),
            animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT)
        )

    def _update_operations_panels() -> None:
        """Optimized operations panel update using modern Python patterns."""
        nonlocal is_loading
        # Ensure current_activity is a proper list for type safety
        safe_activity = current_activity if isinstance(current_activity, list) else []

        # Use constants and functional approach
        running_jobs = list(filter_activities_by_keywords(
            safe_activity, JOB_KEYWORDS, ACTIVITY_TIME_WINDOW
        ))[:MAX_OPERATIONS_DISPLAY]

        recent_backups = list(filter_activities_by_keywords(
            safe_activity, BACKUP_KEYWORDS
        ))[:MAX_OPERATIONS_DISPLAY]

        # Update running jobs (simple conditional to reduce analyzer noise)
        running_jobs_list.controls.clear()
        if is_loading:
            running_jobs_list.controls.extend([
                ft.Container(
                    content=ft.Row([
                        ft.ProgressRing(width=22, height=22, stroke_width=4),
                        ft.Text("Loading recent jobs…", size=12, color=ft.Colors.OUTLINE)
                    ], spacing=12),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.BLUE)
                )
                for _ in range(2)
            ])
        elif not running_jobs:
            running_jobs_list.controls.append(
                ft.Text("All clear – no running jobs", size=12, color=ft.Colors.OUTLINE)
            )
        else:
            running_jobs_list.controls.extend(
                create_operation_item(job, ft.Icons.SYNC, ft.Colors.BLUE, "Running")
                for job in running_jobs
            )

        # Update recent backups (simple conditional to reduce analyzer noise)
        recent_backups_list.controls.clear()
        if is_loading:
            recent_backups_list.controls.extend([
                ft.Container(
                    content=ft.Row([
                        ft.ProgressRing(width=22, height=22, stroke_width=4, color=ft.Colors.GREEN),
                        ft.Text("Loading backup history…", size=12, color=ft.Colors.OUTLINE)
                    ], spacing=12),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=8,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.GREEN)
                )
                for _ in range(2)
            ])
        elif not recent_backups:
            recent_backups_list.controls.append(
                ft.Text("No recent backups", size=12, color=ft.Colors.OUTLINE)
            )
        else:
            recent_backups_list.controls.extend(
                create_operation_item(backup, ft.Icons.BACKUP, ft.Colors.GREEN)
                for backup in recent_backups
            )

    # Wrap operations panels into cards
    running_jobs_card = themed_card(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.SYNC, size=18, color=ft.Colors.BLUE),
                    ft.Text("Running Jobs", size=14, weight=ft.FontWeight.W_600)
                ], spacing=8),
                ft.Container(expand=True),
                ft.TextButton("Open logs", icon=ft.Icons.OPEN_IN_NEW, on_click=_go_to_logs)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            running_jobs_list
        ], spacing=12),
        title=None,
        page=page
    )
    recent_backups_card = themed_card(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.BACKUP, size=18, color=ft.Colors.GREEN),
                    ft.Text("Recent Backups", size=14, weight=ft.FontWeight.W_600)
                ], spacing=8),
                ft.Container(expand=True),
                ft.TextButton("Open files", icon=ft.Icons.FOLDER_OPEN, on_click=_go_to_files)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            recent_backups_list
        ], spacing=12),
        title=None,
        page=page
    )


    # Clean, organized layout structure (streamlined, no redundant big sections)
    # Insert a high-contrast TEST MARKER at the very top so we can visually confirm
    # that the dashboard container actually renders when attached. This marker can be
    # disabled by unsetting FLET_DASHBOARD_TEST_MARKER. It intentionally uses a vivid
    # color distinct from gradient backgrounds.
    test_marker_control: ft.Control | None = None
    if os.environ.get("FLET_DASHBOARD_TEST_MARKER", "0") == "1":  # disabled by default to prevent interference
        try:
            test_marker_control = ft.Container(
                content=ft.Text(
                    "📊 DASHBOARD TEST MARKER (remove with FLET_DASHBOARD_TEST_MARKER=0)",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.AMBER,
                ),
                padding=12,
                bgcolor=ft.Colors.BLACK,
                border_radius=ft.border_radius.all(8),
            )
        except Exception as _tm_err:  # noqa: BLE001
            logger.warning(f"Failed to create test marker control: {_tm_err}")

    debug_placeholder = None
    if os.environ.get("FLET_DASHBOARD_PLACEHOLDER", "0") == "1":  # disabled by default to prevent interference
        debug_placeholder = ft.Container(
            content=ft.Text("(debug placeholder content area)"),
            bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.AMBER),
            padding=20,
            border_radius=8,
        )

    main_content = ft.Column([
        *( [test_marker_control] if test_marker_control else [] ),
        *( [debug_placeholder] if debug_placeholder else [] ),
        header_section,
        refresh_indicator,
        ft.Container(height=16),
        hero_metrics_section,
        ft.Container(height=24),
        kpi_row,
        ft.Container(height=16),
        live_system_metrics_card,
        ft.Container(height=16),
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

    # --- Layout Diagnostics -------------------------------------------------
    # Provide an internal enumeration of the immediate children of main_content
    # and (optionally) wrap them with visible borders to confirm they are present
    # even if internal styling makes them appear blank. Controlled via:
    #   FLET_DASHBOARD_DIAG_LAYOUT=1   -> enable verbose layout diagnostics & visual wrappers
    #   FLET_DASHBOARD_DIAG_LAYOUT=2   -> same as 1 plus deeper recursive enumeration
    # NOTE: Disabled by default to prevent rendering interference
    diag_layout_mode = os.environ.get("FLET_DASHBOARD_DIAG_LAYOUT")
    if diag_layout_mode in {"1", "2"} and os.environ.get("FLET_ENABLE_LAYOUT_DIAG") == "1":
        try:  # pragma: no cover - diagnostics only
            children = getattr(main_content, 'controls', []) or []
            logger.warning("[LAYOUT] main_content has %s direct children", len(children))
            color_cycle = [
                ft.Colors.RED, ft.Colors.BLUE, ft.Colors.GREEN, ft.Colors.ORANGE,
                ft.Colors.PURPLE, ft.Colors.CYAN, ft.Colors.PINK
            ]
            wrapped_children = []
            for idx, child in enumerate(children):
                label = ft.Text(f"idx={idx} • {child.__class__.__name__}", size=11, color=ft.Colors.AMBER)
                border_color = color_cycle[idx % len(color_cycle)]
                wrapper = ft.Container(
                    content=ft.Column([
                        label,
                        child
                    ], spacing=4),
                    border=ft.border.all(1, border_color),
                    padding=6,
                    margin=ft.margin.only(bottom=8),
                    border_radius=6,
                    bgcolor=ft.Colors.with_opacity(0.04, border_color)
                )
                wrapped_children.append(wrapper)
                logger.warning("[LAYOUT] Child %s -> %s", idx, child.__class__.__name__)
            # Replace controls only for diagnostics (do not mutate structure when disabled)
            main_content.controls[:] = wrapped_children

            if diag_layout_mode == "2":
                # deeper enumeration (limited depth)
                def _deep_enum(ctrl, depth=0, max_depth=3):  # noqa: ANN001
                    try:
                        if ctrl is None or depth > max_depth:
                            return
                        prefix = '  ' * depth
                        name = ctrl.__class__.__name__
                        extra = ''
                        if hasattr(ctrl, 'text') and getattr(ctrl, 'text'):
                            extra = f" text={getattr(ctrl, 'text')!r}"
                        logger.warning(f"[LAYOUT-ENUM] {prefix}{name}{extra}")
                        # Determine children
                        kids = []
                        if hasattr(ctrl, 'controls') and getattr(ctrl, 'controls'):
                            kids = list(getattr(ctrl, 'controls'))  # type: ignore[arg-type]
                        elif hasattr(ctrl, 'content') and getattr(ctrl, 'content'):
                            kids = [getattr(ctrl, 'content')]
                        for k in kids[:40]:
                            _deep_enum(k, depth + 1, max_depth)
                    except Exception as _enum_err:  # noqa: BLE001
                        logger.warning(f"[LAYOUT-ENUM] error depth={depth}: {_enum_err}")
                logger.warning('[LAYOUT-ENUM] ---- BEGIN ----')
                _deep_enum(main_content)
                logger.warning('[LAYOUT-ENUM] ---- END ----')
        except Exception as _layout_err:  # noqa: BLE001
            logger.warning(f"[LAYOUT] layout diagnostics failed: {_layout_err}")

    # Additional runtime diagnostics: enumerate immediate child counts for early visibility
    try:  # pragma: no cover - diagnostics
        logger.warning(
            "[DASHBOARD_DIAG] Constructed container: child(main_content)=%s, test_marker=%s",
            isinstance(main_content, ft.Control), bool(test_marker_control)
        )
    except Exception:  # noqa: BLE001
        pass

    # Create the main dashboard container
    dashboard_container = ft.Container(
        content=main_content,
        expand=True,
        padding=ft.padding.symmetric(horizontal=20, vertical=16)
    )

    def setup_subscriptions() -> None:
        """Setup subscriptions and initial data loading after view is added to page."""
        nonlocal refresh_task, _stop_polling

        # Simplified immediate data loading - avoid complex async dependencies
        try:
            logger.debug("[DASHBOARD_SETUP] Starting immediate data loading")
            update_all_displays()
            _update_operations_panels()
            logger.debug("[DASHBOARD_SETUP] Initial data loaded successfully")
        except Exception as e:
            logger.warning(f"[DASHBOARD_SETUP] Initial data load failed: {e}")
            # Continue anyway - dashboard should still be visible

        # Optional deferred async loading for dynamic updates (non-blocking)
        async def _optional_async_updates() -> None:
            try:
                await asyncio.sleep(1.0)  # Wait for UI to settle
                logger.debug("[DASHBOARD_SETUP] Starting optional async updates")
                await _update_all_displays_async('setup')
            except Exception as e:
                logger.debug(f"[DASHBOARD_SETUP] Optional async updates failed: {e}")

        # Start optional async updates (don't wait for them)
        try:
            page.run_task(_optional_async_updates)
        except Exception as e:
            logger.debug(f"[DASHBOARD_SETUP] Failed to start async updates: {e}")

        # Dashboard is already visible - no need for fade-in since we start with opacity=1.0
        try:
            logger.debug(
                f"[DASHBOARD_DIAG] Dashboard opacity is already: {getattr(dashboard_container, 'opacity', 'n/a')}"
            )
            # Trigger update to ensure any pending changes are reflected
            dashboard_container.update()
        except Exception as _update_err:  # noqa: BLE001
            logger.warning(f"[DASHBOARD_DIAG] Dashboard update failed: {_update_err}")

        _update_refresh_countdown_display()

        # Start lightweight periodic refresh in background using constants (optimized for stability)
        async def _poll_loop() -> None:
            nonlocal _stop_polling, countdown_remaining
            operations_update_counter = 0
            consecutive_failures = 0
            try:
                while not _stop_polling:
                    countdown_remaining = POLLING_INTERVAL
                    while countdown_remaining > 0 and not _stop_polling:
                        if not auto_refresh_enabled:
                            countdown_remaining = POLLING_INTERVAL
                            _update_refresh_countdown_display()
                            await asyncio.sleep(2)  # Longer sleep when disabled
                            continue
                        _update_refresh_countdown_display()
                        await asyncio.sleep(1)
                        countdown_remaining -= 1

                    if _stop_polling or not auto_refresh_enabled:
                        continue

                    # Fetch & update asynchronously with failure protection
                    try:
                        # Use simpler sync updates to avoid async complexities that might hang
                        update_all_displays()
                        # Only update operations panels every other cycle to reduce load
                        operations_update_counter += 1
                        if operations_update_counter % OPERATIONS_UPDATE_CYCLE == 0:
                            _update_operations_panels()
                        countdown_remaining = POLLING_INTERVAL
                        _update_refresh_countdown_display()
                        consecutive_failures = 0  # Reset failure counter on success
                    except Exception as e:
                        logger.debug(f"Update failed: {e}")
                        consecutive_failures += 1
                        if consecutive_failures > 3:
                            logger.warning(f"Multiple consecutive failures ({consecutive_failures}), slowing down polling")
                            await asyncio.sleep(5)  # Slow down on repeated failures
            except Exception as e:
                logger.debug(f"Polling loop terminated: {e}")

        # Start the polling loop after initial setup
        try:
            refresh_task = page.run_task(_poll_loop)
        except Exception as e:
            logger.debug(f"Failed to start polling task: {e}")

    def dispose() -> None:
        """Clean up subscriptions and resources."""
        nonlocal _stop_polling, refresh_task
        logger.warning("[DASHBOARD] Disposing dashboard view")
        _stop_polling = True

        # Properly cancel the refresh task
        if refresh_task:
            try:
                refresh_task.cancel()
                logger.debug("Dashboard refresh task cancelled")
            except Exception as e:
                logger.debug(f"Error cancelling refresh task: {e}")
            refresh_task = None

    # Immediate initial data load as fallback - don't rely entirely on setup_subscriptions
    try:
        logger.debug("[DASHBOARD_IMMEDIATE] Loading initial data for immediate display")
        update_all_displays()
        logger.debug("[DASHBOARD_IMMEDIATE] Initial data loaded successfully")
    except Exception as e:
        logger.warning(f"[DASHBOARD_IMMEDIATE] Initial data load failed: {e}")

    return dashboard_container, dispose, setup_subscriptions
