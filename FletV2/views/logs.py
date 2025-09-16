#!/usr/bin/env python3
"""
Simplified Logs View - The Flet Way
~200 lines instead of 1,802 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, TextField, and FilePicker.
Let Flet handle the complexity. We compose, not reinvent.
"""

import flet as ft
from typing import List, Dict, Any, Optional
import json
import csv
import tempfile
from datetime import datetime, timedelta
import random

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_components import themed_card, themed_button
from utils.user_feedback import show_success_message

logger = get_logger(__name__)


def create_logs_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    state_manager: StateManager
) -> ft.Control:
    """Simple logs view using Flet's built-in components."""
    logger.info("Creating simplified logs view")

    # Simple state management (no complex nested functions!)
    logs_data: List[Dict[str, Any]] = []
    filtered_logs = []
    search_query = ""
    level_filter = "ALL"

    # Generate mock logs (simplified)
    def get_mock_logs() -> List[Dict[str, Any]]:
        """Simple mock log generation - no over-engineering!"""
        levels = ["INFO", "ERROR", "WARNING", "DEBUG"]
        components = ["Server", "Client", "Database", "Network"]

        logs = []
        for i in range(100):
            time_offset = timedelta(hours=random.randint(0, 24))
            log_time = datetime.now() - time_offset

            logs.append({
                "id": i + 1,
                "timestamp": log_time.strftime("%H:%M:%S"),
                "level": random.choice(levels),
                "component": random.choice(components),
                "message": f"Log message {i + 1} - System operation completed"
            })

        return sorted(logs, key=lambda x: x["id"], reverse=True)

    # Load logs data
    def load_logs():
        """Load logs using server bridge or mock data."""
        nonlocal logs_data, filtered_logs

        if server_bridge:
            try:
                result = server_bridge.get_logs()
                if result.get('success'):
                    logs_data = result.get('data', [])
                else:
                    logs_data = get_mock_logs()
            except Exception:
                logs_data = get_mock_logs()
        else:
            logs_data = get_mock_logs()

        filtered_logs = logs_data.copy()
        update_table()

    # Filter logs (simple & clean)
    def apply_filters():
        """Simple filtering using Python built-ins."""
        nonlocal filtered_logs

        filtered_logs = logs_data.copy()

        # Level filter
        if level_filter != "ALL":
            filtered_logs = [log for log in filtered_logs if log["level"] == level_filter]

        # Search filter
        if search_query.strip():
            query = search_query.lower()
            filtered_logs = [
                log for log in filtered_logs
                if query in log["message"].lower() or query in log["component"].lower()
            ]

        update_table()

    # UI Components using Flet built-ins
    def get_level_color(level: str) -> str:
        """Simple level color mapping."""
        colors = {
            "ERROR": ft.Colors.RED,
            "WARNING": ft.Colors.ORANGE,
            "INFO": ft.Colors.BLUE,
            "DEBUG": ft.Colors.GREY
        }
        return colors.get(level, ft.Colors.GREY)

    # Create data table using Flet's built-in styling
    logs_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Time")),
            ft.DataColumn(ft.Text("Level")),
            ft.DataColumn(ft.Text("Component")),
            ft.DataColumn(ft.Text("Message")),
        ],
        rows=[],
        heading_row_color=ft.Colors.SURFACE_VARIANT,
        border_radius=12,
        expand=True
    )

    def update_table():
        """Update table using Flet's simple row creation."""
        logs_table.rows.clear()

        for log in filtered_logs[:50]:  # Simple pagination - show first 50
            logs_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(log["timestamp"], size=12)),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(log["level"], size=10, color=ft.Colors.WHITE),
                                padding=ft.Padding(4, 2, 4, 2),
                                bgcolor=get_level_color(log["level"]),
                                border_radius=4
                            )
                        ),
                        ft.DataCell(ft.Text(log["component"], size=12)),
                        ft.DataCell(ft.Text(log["message"], size=12)),
                    ]
                )
            )

        if hasattr(logs_table, 'update'):
            logs_table.update()

    # Search functionality (simple TextField)
    def on_search_change(e):
        """Simple search handler."""
        nonlocal search_query
        search_query = e.control.value
        apply_filters()

    search_field = ft.TextField(
        label="Search logs",
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_search_change,
        width=300
    )

    # Level filter (simple Dropdown)
    def on_level_filter_change(e):
        """Simple level filter handler."""
        nonlocal level_filter
        level_filter = e.control.value
        apply_filters()

    level_dropdown = ft.Dropdown(
        label="Filter by level",
        value="ALL",
        options=[
            ft.dropdown.Option("ALL"),
            ft.dropdown.Option("ERROR"),
            ft.dropdown.Option("WARNING"),
            ft.dropdown.Option("INFO"),
            ft.dropdown.Option("DEBUG"),
        ],
        on_change=on_level_filter_change,
        width=150
    )

    # Statistics (simple display)
    stats_text = ft.Text("", size=14)

    def update_stats():
        """Simple stats calculation."""
        total = len(filtered_logs)
        errors = len([log for log in filtered_logs if log["level"] == "ERROR"])
        warnings = len([log for log in filtered_logs if log["level"] == "WARNING"])

        stats_text.value = f"Total: {total} | Errors: {errors} | Warnings: {warnings}"
        if hasattr(stats_text, 'update'):
            stats_text.update()

    # Export functionality (using Flet's FilePicker)
    def save_logs_as_json(e: ft.FilePickerResultEvent):
        """Simple JSON export using FilePicker."""
        if e.path:
            try:
                with open(e.path, 'w') as f:
                    json.dump(filtered_logs, f, indent=2)
                show_success_message(page, f"Logs exported to {e.path}")
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Export failed: {ex}"))
                page.snack_bar.open = True
                page.update()

    file_picker = ft.FilePicker(on_result=save_logs_as_json)
    page.overlay.append(file_picker)

    def export_logs(e):
        """Export logs using Flet's FilePicker."""
        file_picker.save_file(
            dialog_title="Export Logs",
            file_name=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"]
        )

    # Refresh functionality
    def refresh_logs(e):
        """Simple refresh handler."""
        load_logs()
        update_stats()
        show_success_message(page, "Logs refreshed")

    # Action buttons using simplified components
    actions_row = ft.Row([
        themed_button("Refresh", refresh_logs, "filled", ft.Icons.REFRESH),
        themed_button("Export", export_logs, "outlined", ft.Icons.DOWNLOAD),
        ft.Container(expand=True),  # Spacer
        stats_text
    ], spacing=10)

    # Filters row
    filters_row = ft.Row([
        search_field,
        level_dropdown,
    ], spacing=10)

    # Main layout using Flet's simple Column
    main_content = ft.Column([
        ft.Text("System Logs", size=28, weight=ft.FontWeight.BOLD),
        filters_row,
        actions_row,
        ft.Container(
            content=logs_table,
            expand=True,
            padding=10,
            border_radius=12,
            bgcolor=ft.Colors.SURFACE
        )
    ], expand=True, spacing=20)

    # Initialize data
    load_logs()
    update_stats()

    # Override apply_filters to update stats
    original_apply_filters = apply_filters
    def apply_filters():
        original_apply_filters()
        update_stats()

    return themed_card(main_content, "Logs Management")