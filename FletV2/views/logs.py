#!/usr/bin/env python3
"""
Logs View - Dual-Tab System with Enhanced Visual Design
Tab 1: System Logs (server_bridge.get_logs())
Tab 2: Flet Logs (framework error capture)

Features:
- Color-coded level badges with icons
- Gradient borders on search field
- Animated filter chips with hover effects
- Neumorphic shadows and glassmorphic accents
- Server integration with fallback data
"""

import os
import sys
import logging
from datetime import datetime
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

# Import theme constants
try:
    from FletV2.theme import PRONOUNCED_NEUMORPHIC_SHADOWS, MODERATE_NEUMORPHIC_SHADOWS
except ImportError:
    PRONOUNCED_NEUMORPHIC_SHADOWS = []
    MODERATE_NEUMORPHIC_SHADOWS = []


# ========================================================================================
# FLET LOG CAPTURE SYSTEM
# ========================================================================================

class FletLogCapture(logging.Handler):
    """Custom logging handler to capture Flet framework logs."""

    def __init__(self):
        super().__init__()
        self.logs = []
        self.max_logs = 100  # Keep last 100 logs

    def emit(self, record):
        """Capture log record and format it."""
        try:
            self.logs.insert(0, {
                "time": datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
                "level": record.levelname,
                "component": record.name,
                "message": self.format(record)
            })
            # Limit to max_logs
            if len(self.logs) > self.max_logs:
                self.logs = self.logs[:self.max_logs]
        except Exception:
            pass  # Ignore errors in logging


# Global Flet log capture instance
_flet_log_capture = FletLogCapture()


def setup_flet_log_capture():
    """Setup Flet log capture if not already configured."""
    if not any(isinstance(h, FletLogCapture) for h in logging.root.handlers):
        _flet_log_capture.setLevel(logging.DEBUG)
        _flet_log_capture.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))
        logging.root.addHandler(_flet_log_capture)


# ========================================================================================
# LOG DATA PROVIDERS
# ========================================================================================

def get_system_logs(server_bridge: Any | None) -> list[dict]:
    """Get system logs from server or fallback data."""
    if server_bridge and hasattr(server_bridge, 'get_logs'):
        try:
            logs = server_bridge.get_logs()
            if logs and isinstance(logs, list):
                return logs
        except Exception:
            pass

    # Fallback sample logs
    return [
        {"time": "18:48:54", "level": "INFO", "component": "MainThread", "message": "=== BACKUP-SERVER LOGGING INITIALIZED ==="},
        {"time": "18:48:54", "level": "INFO", "component": "MainThread", "message": "Console Level: INFO"},
        {"time": "18:48:54", "level": "INFO", "component": "MainThread", "message": "File Level: DEBUG"},
        {"time": "18:48:54", "level": "INFO", "component": "MainThread", "message": "Log File: logs/backup-server_20250930_184854.log"},
        {"time": "18:48:54", "level": "INFO", "component": "GUI", "message": "[GUI] Embedded GUI disable flag value: '1'"},
        {"time": "18:48:54", "level": "INFO", "component": "GUI", "message": "[GUI] Integrated Server GUI disabled via CYBERBACKUP_DISABLE_INTEGRATED_GUI=1"},
        {"time": "18:48:56", "level": "INFO", "component": "FletV2App", "message": "State manager initialized"},
        {"time": "18:48:56", "level": "INFO", "component": "FletV2App", "message": "Navigation rail created"},
        {"time": "18:48:57", "level": "WARNING", "component": "dashboard", "message": "Failed to unsubscribe from state manager"},
        {"time": "18:48:57", "level": "INFO", "component": "FletV2App", "message": "Successfully updated content area with dashboard"},
    ]


def get_flet_logs() -> list[dict]:
    """Get captured Flet framework logs."""
    return _flet_log_capture.logs if _flet_log_capture.logs else [
        {"time": datetime.now().strftime("%H:%M:%S"), "level": "INFO", "component": "FletLogCapture", "message": "No Flet logs captured yet"}
    ]


# ========================================================================================
# VISUAL COMPONENTS
# ========================================================================================

# Level configuration
LEVEL_CONFIG = {
    "ERROR": {"color": ft.Colors.RED_500, "icon": ft.Icons.ERROR, "name": "ERROR"},
    "WARNING": {"color": ft.Colors.AMBER_500, "icon": ft.Icons.WARNING_AMBER, "name": "WARNING"},
    "INFO": {"color": ft.Colors.BLUE_500, "icon": ft.Icons.INFO, "name": "INFO"},
    "DEBUG": {"color": ft.Colors.GREY_500, "icon": ft.Icons.BUG_REPORT, "name": "DEBUG"},
}


def create_level_badge(level: str) -> ft.Container:
    """Create color-coded level badge with icon."""
    config = LEVEL_CONFIG.get(level, LEVEL_CONFIG["INFO"])

    return ft.Container(
        content=ft.Row([
            ft.Icon(config["icon"], size=16, color=config["color"]),
            ft.Text(config["name"], size=12, weight=ft.FontWeight.W_600, color=config["color"])
        ], spacing=4, tight=True),
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.1, config["color"]),
    )


def create_gradient_search_field(on_change=None) -> ft.Container:
    """Create search field with gradient border effect."""
    search_field = ft.TextField(
        label="Search logs",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=12,
        width=300,
        on_change=on_change,
        border_color=ft.Colors.OUTLINE,
        focused_border_color=ft.Colors.BLUE_500,
        focused_border_width=2,
    )

    return ft.Container(
        content=search_field,
        border_radius=12,
        border=ft.border.all(2, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_500)),
        padding=0,
    )


def create_animated_filter_chip(label: str, icon: str, is_active: bool, on_click) -> ft.Container:
    """Create animated filter chip with hover effects."""

    chip = ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=16, color=ft.Colors.WHITE if is_active else None),
            ft.Text(label, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE if is_active else None)
        ], spacing=6, tight=True),
        padding=ft.padding.symmetric(horizontal=12, vertical=8),
        border_radius=20,
        bgcolor=LEVEL_CONFIG.get(label, {}).get("color", ft.Colors.BLUE_500) if is_active else ft.Colors.with_opacity(0.05, ft.Colors.SURFACE),
        border=ft.border.all(1, ft.Colors.OUTLINE) if not is_active else None,
        animate_scale=ft.Animation(180, ft.AnimationCurve.EASE_OUT_CUBIC),
        on_click=on_click,
        ink=True,
    )

    # Hover effect
    def on_hover(e):
        chip.scale = 1.05 if e.data == "true" else 1.0
        chip.update()

    chip.on_hover = on_hover

    return chip


def create_logs_table(logs: list[dict]) -> ft.DataTable:
    """Create logs DataTable with enhanced styling."""

    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.BOLD, size=13)),
            ft.DataColumn(ft.Text("Level", weight=ft.FontWeight.BOLD, size=13)),
            ft.DataColumn(ft.Text("Component", weight=ft.FontWeight.BOLD, size=13)),
            ft.DataColumn(ft.Text("Message", weight=ft.FontWeight.BOLD, size=13)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(log.get("time", ""), size=12, font_family="Courier New")),
                    ft.DataCell(create_level_badge(log.get("level", "INFO"))),
                    ft.DataCell(ft.Text(log.get("component", ""), size=12, weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text(log.get("message", ""), size=12, max_lines=2)),
                ]
            )
            for log in logs
        ],
        border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
        border_radius=12,
        horizontal_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.06, ft.Colors.OUTLINE)),
        heading_row_color=ft.Colors.with_opacity(0.05, ft.Colors.SURFACE),
        heading_row_height=48,
        data_row_min_height=56,
        data_row_max_height=80,
    )


# ========================================================================================
# MAIN VIEW CREATION
# ========================================================================================

def create_logs_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None
) -> tuple[ft.Control, Callable[[], None], Callable[[], None]]:
    """Create logs view with two tabs (System Logs and Flet Logs)."""

    # Setup Flet log capture
    setup_flet_log_capture()

    # State
    system_logs = get_system_logs(server_bridge)
    flet_logs = get_flet_logs()
    current_filter = "ALL"
    search_query = ""

    # Refs for updates
    system_table_ref = ft.Ref[ft.DataTable]()
    flet_table_ref = ft.Ref[ft.DataTable]()
    filter_chips_ref = ft.Ref[ft.Row]()

    # ========================================================================================
    # FILTER LOGIC
    # ========================================================================================

    def filter_logs(logs: list[dict]) -> list[dict]:
        """Apply current filter and search to logs."""
        filtered = logs

        # Apply level filter
        if current_filter != "ALL":
            filtered = [log for log in filtered if log.get("level", "") == current_filter]

        # Apply search filter
        if search_query:
            query_lower = search_query.lower()
            filtered = [
                log for log in filtered
                if query_lower in log.get("message", "").lower()
                or query_lower in log.get("component", "").lower()
            ]

        return filtered

    def update_tables():
        """Update both tables with filtered data."""
        if system_table_ref.current:
            filtered_system = filter_logs(system_logs)
            system_table_ref.current.rows = [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(log.get("time", ""), size=12, font_family="Courier New")),
                    ft.DataCell(create_level_badge(log.get("level", "INFO"))),
                    ft.DataCell(ft.Text(log.get("component", ""), size=12, weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text(log.get("message", ""), size=12, max_lines=2)),
                ])
                for log in filtered_system
            ]
            system_table_ref.current.update()

        if flet_table_ref.current:
            filtered_flet = filter_logs(flet_logs)
            flet_table_ref.current.rows = [
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(log.get("time", ""), size=12, font_family="Courier New")),
                    ft.DataCell(create_level_badge(log.get("level", "INFO"))),
                    ft.DataCell(ft.Text(log.get("component", ""), size=12, weight=ft.FontWeight.W_500)),
                    ft.DataCell(ft.Text(log.get("message", ""), size=12, max_lines=2)),
                ])
                for log in filtered_flet
            ]
            flet_table_ref.current.update()

    def on_filter_change(level: str):
        """Handle filter chip click."""
        nonlocal current_filter
        current_filter = level
        update_tables()

        # Update chip visuals
        if filter_chips_ref.current:
            filter_chips_ref.current.controls = create_filter_chips()
            filter_chips_ref.current.update()

    def on_search_change(e):
        """Handle search field change."""
        nonlocal search_query
        search_query = e.control.value
        update_tables()

    def on_refresh(e):
        """Refresh logs from server."""
        nonlocal system_logs, flet_logs
        system_logs = get_system_logs(server_bridge)
        flet_logs = get_flet_logs()
        update_tables()

    # ========================================================================================
    # UI COMPONENTS
    # ========================================================================================

    def create_filter_chips() -> list[ft.Control]:
        """Create filter chips with current state."""
        return [
            create_animated_filter_chip("ALL", ft.Icons.SELECT_ALL, current_filter == "ALL", lambda e: on_filter_change("ALL")),
            create_animated_filter_chip("INFO", ft.Icons.INFO, current_filter == "INFO", lambda e: on_filter_change("INFO")),
            create_animated_filter_chip("ERROR", ft.Icons.ERROR, current_filter == "ERROR", lambda e: on_filter_change("ERROR")),
            create_animated_filter_chip("WARNING", ft.Icons.WARNING_AMBER, current_filter == "WARNING", lambda e: on_filter_change("WARNING")),
            create_animated_filter_chip("DEBUG", ft.Icons.BUG_REPORT, current_filter == "DEBUG", lambda e: on_filter_change("DEBUG")),
        ]

    filter_chips_row = ft.Row(
        ref=filter_chips_ref,
        controls=create_filter_chips(),
        spacing=8,
        wrap=True
    )

    # Action buttons with neumorphic shadows
    action_buttons = ft.Row([
        ft.Container(
            content=ft.FilledTonalButton("Refresh", icon=ft.Icons.REFRESH, on_click=on_refresh),
            shadow=MODERATE_NEUMORPHIC_SHADOWS,
            border_radius=12,
        ),
        ft.Container(
            content=ft.OutlinedButton("Export", icon=ft.Icons.DOWNLOAD),
            shadow=MODERATE_NEUMORPHIC_SHADOWS,
            border_radius=12,
        ),
    ], spacing=12)

    # Filter bar
    filter_bar = ft.Container(
        content=ft.Column([
            ft.Row([
                create_gradient_search_field(on_change=on_search_change),
                filter_chips_row
            ], spacing=16, wrap=True, alignment=ft.MainAxisAlignment.START),
        ], spacing=12),
        padding=16,
        border_radius=12,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SURFACE),
        shadow=PRONOUNCED_NEUMORPHIC_SHADOWS,
    )

    # System Logs Tab
    system_logs_table = create_logs_table(filter_logs(system_logs))
    system_logs_table.ref = system_table_ref

    system_logs_content = ft.Container(
        content=ft.Column([
            system_logs_table,
        ], scroll=ft.ScrollMode.AUTO, spacing=0),
        padding=16,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE,
        shadow=MODERATE_NEUMORPHIC_SHADOWS,
        expand=True,
    )

    # Flet Logs Tab
    flet_logs_table = create_logs_table(filter_logs(flet_logs))
    flet_logs_table.ref = flet_table_ref

    flet_logs_content = ft.Container(
        content=ft.Column([
            flet_logs_table,
        ], scroll=ft.ScrollMode.AUTO, spacing=0),
        padding=16,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE,
        shadow=MODERATE_NEUMORPHIC_SHADOWS,
        expand=True,
    )

    # Tabs system
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="System Logs",
                icon=ft.Icons.ARTICLE,
                content=system_logs_content,
            ),
            ft.Tab(
                text="Flet Logs",
                icon=ft.Icons.CODE,
                content=flet_logs_content,
            ),
        ],
        expand=True,
    )

    # Main content
    content = ft.Column([
        # Header
        ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.ARTICLE, size=32, color=ft.Colors.PRIMARY),
                ft.Text("Logs", size=28, weight=ft.FontWeight.BOLD),
            ], spacing=12),
            action_buttons,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

        # Filter bar
        filter_bar,

        # Tabs
        tabs,
    ], spacing=20, expand=True)

    main_container = ft.Container(
        content=content,
        padding=24,
        expand=True,
    )

    # ========================================================================================
    # LIFECYCLE
    # ========================================================================================

    def dispose():
        """Cleanup resources."""
        pass

    def setup_subscriptions():
        """Setup state subscriptions."""
        pass

    return main_container, dispose, setup_subscriptions
