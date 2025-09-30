#!/usr/bin/env python3
"""
Logs View - Dual-Tab System with Pronounced Neumorphic Design
Tab 1: System Logs (server integration)
Tab 2: Flet Framework Logs (live capture)
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

# Import neumorphic shadows from theme (using relative import to avoid circular imports)
try:
    from theme import PRONOUNCED_NEUMORPHIC_SHADOWS, MODERATE_NEUMORPHIC_SHADOWS
except ImportError:
    PRONOUNCED_NEUMORPHIC_SHADOWS = []
    MODERATE_NEUMORPHIC_SHADOWS = []


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
_flet_log_capture.setFormatter(logging.Formatter('%(message)s'))

# Attach to root logger to capture all logs
logging.getLogger().addHandler(_flet_log_capture)


# ======================================================================================
# DATA FETCHING
# ======================================================================================

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
        {"time": "18:48:54", "level": "INFO", "component": "GUI", "message": "[GUI] Embedded GUI disable flag value: '1'"},
        {"time": "18:48:56", "level": "INFO", "component": "FletV2App", "message": "State manager initialized"},
        {"time": "18:48:56", "level": "INFO", "component": "FletV2App", "message": "Navigation rail created"},
        {"time": "18:48:57", "level": "WARNING", "component": "dashboard", "message": "Failed to unsubscribe from state manager"},
        {"time": "18:48:57", "level": "ERROR", "component": "dashboard", "message": "Control lifecycle error detected"},
        {"time": "18:48:58", "level": "DEBUG", "component": "analytics", "message": "Analytics view loaded successfully"},
        {"time": "18:48:58", "level": "INFO", "component": "logs", "message": "Logs view initialized with dual-tab system"},
    ]


# ======================================================================================
# UI CREATION
# ======================================================================================

def create_logs_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None
) -> tuple[ft.Control, Callable[[], None], Callable[[], None]]:
    """Create logs view with dual-tab system and neumorphic design."""

    # Level configuration
    LEVEL_CONFIG = {
        "ERROR": {"color": ft.Colors.RED_500, "icon": ft.Icons.ERROR},
        "WARNING": {"color": ft.Colors.AMBER_500, "icon": ft.Icons.WARNING_AMBER},
        "INFO": {"color": ft.Colors.BLUE_500, "icon": ft.Icons.INFO},
        "DEBUG": {"color": ft.Colors.GREY_500, "icon": ft.Icons.BUG_REPORT},
    }

    def create_log_table(logs: list[dict], table_key: str) -> ft.DataTable:
        """Create a data table for logs with color-coded level badges."""
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
                        ft.DataCell(ft.Text(log.get("time", ""), size=12)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Row([
                                    ft.Icon(
                                        LEVEL_CONFIG.get(log.get("level", "INFO"), {}).get("icon", ft.Icons.INFO),
                                        size=16,
                                        color=LEVEL_CONFIG.get(log.get("level", "INFO"), {}).get("color", ft.Colors.BLUE_500)
                                    ),
                                    ft.Text(
                                        log.get("level", "INFO"),
                                        size=12,
                                        weight=ft.FontWeight.W_600,
                                        color=LEVEL_CONFIG.get(log.get("level", "INFO"), {}).get("color", ft.Colors.BLUE_500)
                                    )
                                ], spacing=6, tight=True),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=12,
                                bgcolor=ft.Colors.with_opacity(0.1, LEVEL_CONFIG.get(log.get("level", "INFO"), {}).get("color", ft.Colors.BLUE_500))
                            )
                        ),
                        ft.DataCell(ft.Text(log.get("component", ""), size=12)),
                        ft.DataCell(ft.Text(log.get("message", ""), size=12)),
                    ]
                )
                for log in logs
            ],
            border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            border_radius=12,
            horizontal_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.06, ft.Colors.OUTLINE)),
            heading_row_color=ft.Colors.with_opacity(0.08, ft.Colors.SURFACE),
            data_row_max_height=60,
        )

    # Fetch system logs
    system_logs = get_system_logs(server_bridge)

    # Create system logs tab content
    system_logs_table = create_log_table(system_logs, "system_logs")
    system_logs_content = ft.Container(
        content=ft.Column([
            system_logs_table,
        ], scroll=ft.ScrollMode.AUTO, expand=True),
        padding=20,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE,
        shadow=MODERATE_NEUMORPHIC_SHADOWS,
        expand=True,
    )

    # Create Flet logs tab content
    def get_flet_logs():
        """Get logs from the Flet log capture handler."""
        return _flet_log_capture.logs if _flet_log_capture.logs else [
            {"time": datetime.now().strftime("%H:%M:%S"), "level": "INFO", "component": "flet", "message": "Flet framework initialized successfully"},
            {"time": datetime.now().strftime("%H:%M:%S"), "level": "DEBUG", "component": "flet.page", "message": "Page created with Material Design 3 theme"},
        ]

    flet_logs_table = create_log_table(get_flet_logs(), "flet_logs")
    flet_logs_content = ft.Container(
        content=ft.Column([
            flet_logs_table,
        ], scroll=ft.ScrollMode.AUTO, expand=True),
        padding=20,
        border_radius=16,
        bgcolor=ft.Colors.SURFACE,
        shadow=MODERATE_NEUMORPHIC_SHADOWS,
        expand=True,
    )

    # Create tabs
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        indicator_color=ft.Colors.PRIMARY,
        label_color=ft.Colors.PRIMARY,
        unselected_label_color=ft.Colors.ON_SURFACE_VARIANT,
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

    # Action buttons with neumorphic styling
    action_buttons = ft.Row([
        ft.FilledTonalButton(
            "Refresh",
            icon=ft.Icons.REFRESH,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
            )
        ),
        ft.OutlinedButton(
            "Export",
            icon=ft.Icons.DOWNLOAD,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
            )
        ),
        ft.OutlinedButton(
            "Clear Flet Logs",
            icon=ft.Icons.DELETE_SWEEP,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
            )
        ),
    ], spacing=12)

    # Main content with pronounced neumorphism
    content = ft.Column([
        # Header with icon and buttons
        ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.ARTICLE, size=36, color=ft.Colors.PRIMARY),
                    ft.Text("Logs", size=32, weight=ft.FontWeight.BOLD),
                ], spacing=12),
                action_buttons,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.only(bottom=16),
        ),

        # Tabs container with pronounced neumorphism
        ft.Container(
            content=tabs,
            border_radius=16,
            shadow=PRONOUNCED_NEUMORPHIC_SHADOWS,  # Big neumorphism!
            bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
            padding=12,
            expand=True,
        ),
    ], spacing=24, expand=True)

    main_container = ft.Container(
        content=content,
        padding=24,
        expand=True,
    )

    def dispose():
        """Cleanup."""
        pass

    def setup_subscriptions():
        """Setup."""
        pass

    return main_container, dispose, setup_subscriptions
