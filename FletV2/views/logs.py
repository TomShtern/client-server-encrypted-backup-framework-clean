#!/usr/bin/env python3
"""
Logs View - Clean and Simple
Shows system logs with filtering and search.
"""

import os
import sys
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

def create_logs_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None
) -> tuple[ft.Control, Callable[[], None], Callable[[], None]]:
    """Create logs view with DataTable."""

    # Sample logs data
    sample_logs = [
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

    # Level colors
    level_colors = {
        "ERROR": ft.Colors.RED_500,
        "WARNING": ft.Colors.AMBER_500,
        "INFO": ft.Colors.BLUE_500,
        "DEBUG": ft.Colors.GREY_500,
    }

    # Level icons
    level_icons = {
        "ERROR": ft.Icons.ERROR,
        "WARNING": ft.Icons.WARNING_AMBER,
        "INFO": ft.Icons.INFO,
        "DEBUG": ft.Icons.BUG_REPORT,
    }

    # Create DataTable
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Time", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Level", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Component", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Message", weight=ft.FontWeight.BOLD)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(log["time"], size=12)),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(
                                    level_icons.get(log["level"], ft.Icons.INFO),
                                    size=16,
                                    color=level_colors.get(log["level"], ft.Colors.GREY_500)
                                ),
                                ft.Text(log["level"], size=12, weight=ft.FontWeight.W_600)
                            ], spacing=4, tight=True),
                        )
                    ),
                    ft.DataCell(ft.Text(log["component"], size=12)),
                    ft.DataCell(ft.Text(log["message"], size=12)),
                ]
            )
            for log in sample_logs
        ],
        border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
        border_radius=8,
        horizontal_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.06, ft.Colors.OUTLINE)),
        heading_row_color=ft.Colors.with_opacity(0.05, ft.Colors.SURFACE),
    )

    # Search field
    search_field = ft.TextField(
        label="Search logs",
        prefix_icon=ft.Icons.SEARCH,
        border_radius=12,
        width=300,
    )

    # Filter chips
    filter_chips = ft.Row([
        ft.FilledButton("ALL", icon=ft.Icons.SELECT_ALL, style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_500)),
        ft.OutlinedButton("INFO", icon=ft.Icons.INFO),
        ft.OutlinedButton("ERROR", icon=ft.Icons.ERROR),
        ft.OutlinedButton("WARNING", icon=ft.Icons.WARNING_AMBER),
        ft.OutlinedButton("DEBUG", icon=ft.Icons.BUG_REPORT),
    ], spacing=8)

    # Action buttons
    action_buttons = ft.Row([
        ft.FilledTonalButton("Refresh", icon=ft.Icons.REFRESH),
        ft.OutlinedButton("Export", icon=ft.Icons.DOWNLOAD),
    ], spacing=8)

    # Main content
    content = ft.Column([
        # Header
        ft.Row([
            ft.Text("System Logs", size=28, weight=ft.FontWeight.BOLD),
            action_buttons,
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

        # Filter bar
        ft.Container(
            content=ft.Column([
                ft.Row([search_field, filter_chips], spacing=16, wrap=True),
            ], spacing=12),
            padding=16,
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SURFACE),
        ),

        # Logs table
        ft.Container(
            content=ft.Column([
                data_table,
            ], scroll=ft.ScrollMode.AUTO),
            padding=16,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            expand=True,
        ),
    ], spacing=20, expand=True)

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