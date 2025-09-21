#!/usr/bin/env python3
"""
Simplified Logs View - The Flet Way
~200 lines instead of 1,802 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, TextField, and FilePicker.
Let Flet handle the complexity. We compose, not reinvent.
"""

# Explicit imports instead of star import for better static analysis
import flet as ft
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, timedelta
import json
import asyncio
import aiofiles
import random

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_components import themed_card, themed_button, create_status_pill
from utils.user_feedback import show_success_message, show_error_message

logger = get_logger(__name__)


def create_logs_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    _state_manager: Optional[StateManager] = None
) -> Any:
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
    def load_logs() -> None:
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
    def apply_filters() -> None:
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

    def get_status_type(level: str) -> str:
        """Map log level to status pill type."""
        level_mapping = {
            "error": "error",        # Red for errors
            "warning": "warning",    # Orange for warnings
            "info": "info",          # Blue for info
            "debug": "debug"         # Blue Grey for debug
        }
        return level_mapping.get(level.lower(), "default")

    def get_card_background_color(level: str) -> str:
        """Get transparent background color for log cards based on level."""
        level_backgrounds = {
            "ERROR": "rgba(200, 40, 40, 0.1)",    # Transparent red
            "WARNING": "rgba(239, 108, 0, 0.1)",  # Transparent orange
            "INFO": "rgba(2, 136, 209, 0.1)",     # Transparent blue
            "DEBUG": "rgba(66, 66, 66, 0.1)"      # Transparent grey
        }
        return level_backgrounds.get(level, "rgba(66, 66, 66, 0.1)")

    def create_filter_chip(text: str, icon: str, is_selected: bool, on_click) -> ft.Container:
        """Create filter chip with icon and selection state."""
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=16),
                ft.Text(text, size=12, weight=ft.FontWeight.BOLD)
            ], spacing=4, tight=True),
            padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            bgcolor=ft.Colors.PRIMARY if is_selected else ft.Colors.SURFACE,
            border=ft.border.all(2, ft.Colors.PRIMARY if is_selected else ft.Colors.OUTLINE),
            border_radius=16,
            on_click=on_click
        )

    # Create ListView for card-based log display
    logs_listview = ft.ListView(
        expand=True,
        spacing=8,
        padding=ft.padding.all(8)
    )

    def create_log_card(log: Dict[str, Any]) -> ft.Container:
        """Create individual card for each log entry."""
        level = log["level"]

        return ft.Container(
            content=ft.Row([
                # Status pill on the left
                create_status_pill(level, get_status_type(level)),

                # Log content
                ft.Column([
                    ft.Row([
                        ft.Text(log["timestamp"], size=12, weight=ft.FontWeight.BOLD),
                        ft.Text(f"[{log['component']}]", size=12, color=ft.Colors.ON_SURFACE),
                    ], spacing=8),
                    ft.Text(log["message"], size=13, max_lines=2)
                ], spacing=4, expand=True)
            ], spacing=12),

            padding=16,
            bgcolor=get_card_background_color(level),
            border_radius=8,
            border=ft.border.all(1, ft.Colors.OUTLINE)
        )

    def update_table() -> None:
        """Update ListView with log cards."""
        logs_listview.controls.clear()

        for log in filtered_logs[:50]:  # Simple pagination - show first 50
            logs_listview.controls.append(create_log_card(log))

        if hasattr(logs_listview, 'update') and hasattr(logs_listview, 'page') and logs_listview.page:
            try:
                logs_listview.update()
            except Exception as e:
                logger.warning(f"ListView update failed - this may prevent navigation: {e}")
                # Try to re-attach the ListView if it got detached
                try:
                    if logs_listview.page is None:
                        logger.error("ListView lost page reference - navigation may be broken")
                except Exception:
                    logger.error("ListView is in an invalid state - navigation may be broken")

    # Search functionality (simple TextField)
    def on_search_change(e: ft.ControlEvent) -> None:
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

    # Filter chips with icons
    def on_filter_click(filter_level: str) -> Callable[[ft.ControlEvent], None]:
        """Handle filter chip click."""
        def handler(e: ft.ControlEvent) -> None:
            nonlocal level_filter
            level_filter = filter_level
            apply_filters()
            update_filter_chips()
        return handler

    filter_chips_row = ft.Row(spacing=8)

    def update_filter_chips() -> None:
        """Update filter chips with selection state."""
        filter_chips_row.controls = [
            create_filter_chip("ALL", ft.Icons.LIST, level_filter == "ALL", on_filter_click("ALL")),
            create_filter_chip("INFO", ft.Icons.INFO, level_filter == "INFO", on_filter_click("INFO")),
            create_filter_chip("ERROR", ft.Icons.ERROR, level_filter == "ERROR", on_filter_click("ERROR")),
            create_filter_chip("WARNING", ft.Icons.WARNING, level_filter == "WARNING", on_filter_click("WARNING")),
            create_filter_chip("DEBUG", ft.Icons.BUG_REPORT, level_filter == "DEBUG", on_filter_click("DEBUG")),
        ]
        if hasattr(filter_chips_row, 'update') and hasattr(filter_chips_row, 'page') and filter_chips_row.page:
            try:
                filter_chips_row.update()
            except Exception as e:
                logger.warning(f"Filter chips update failed - this may prevent navigation: {e}")
                # Try to re-attach if it got detached
                try:
                    if filter_chips_row.page is None:
                        logger.error("Filter chips lost page reference - navigation may be broken")
                except Exception:
                    logger.error("Filter chips are in an invalid state - navigation may be broken")

    # Initialize filter chips (defer update until after page attachment)
    filter_chips_row.controls = [
        create_filter_chip("ALL", ft.Icons.LIST, level_filter == "ALL", on_filter_click("ALL")),
        create_filter_chip("INFO", ft.Icons.INFO, level_filter == "INFO", on_filter_click("INFO")),
        create_filter_chip("ERROR", ft.Icons.ERROR, level_filter == "ERROR", on_filter_click("ERROR")),
        create_filter_chip("WARNING", ft.Icons.WARNING, level_filter == "WARNING", on_filter_click("WARNING")),
        create_filter_chip("DEBUG", ft.Icons.BUG_REPORT, level_filter == "DEBUG", on_filter_click("DEBUG")),
    ]

    # Statistics (simple display)
    stats_text = ft.Text("", size=14)

    def update_stats() -> None:
        """Simple stats calculation."""
        total = len(filtered_logs)
        errors = len([log for log in filtered_logs if log["level"] == "ERROR"])
        warnings = len([log for log in filtered_logs if log["level"] == "WARNING"])

        stats_text.value = f"Total: {total} | Errors: {errors} | Warnings: {warnings}"
        if hasattr(stats_text, 'update') and hasattr(stats_text, 'page') and stats_text.page:
            try:
                stats_text.update()
            except Exception as e:
                logger.warning(f"Stats text update failed - this may prevent navigation: {e}")
                # Try to re-attach if it got detached
                try:
                    if stats_text.page is None:
                        logger.error("Stats text lost page reference - navigation may be broken")
                except Exception:
                    logger.error("Stats text is in an invalid state - navigation may be broken")

    # Export functionality (using Flet's FilePicker)
    async def save_logs_as_json(e: ft.FilePickerResultEvent) -> None:
        """Simple JSON export using FilePicker."""
        if e.path:
            try:
                async with aiofiles.open(e.path, 'w') as f:
                    await f.write(json.dumps(filtered_logs, indent=2))
                show_success_message(page, f"Logs exported to {e.path}")
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Export failed: {ex}"))
                page.snack_bar.open = True
                page.update()

    file_picker = ft.FilePicker(on_result=save_logs_as_json)
    page.overlay.append(file_picker)

    def export_logs(e: ft.ControlEvent) -> None:
        """Export logs using Flet's FilePicker."""
        file_picker.save_file(
            dialog_title="Export Logs",
            file_name=f"logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["json"]
        )

    # Refresh functionality
    def refresh_logs(e: ft.ControlEvent) -> None:
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

    # Enhanced filter controls with responsive design
    filters_section = ft.Column([
        ft.ResponsiveRow([
            ft.Column([search_field], col={"sm": 12, "md": 12, "lg": 12})
        ]),
        ft.Container(height=8),  # Spacing
        filter_chips_row
    ], spacing=8)

    # Enhanced logs display with layered card design
    logs_card = themed_card(logs_listview, "System Logs", page)

    # Main layout with enhanced styling and responsive design
    main_content = ft.Column([
        ft.Text("Logs Management", size=28, weight=ft.FontWeight.BOLD),
        # Make filters section responsive
        ft.ResponsiveRow([
            ft.Column([filters_section], col={"sm": 12, "md": 12, "lg": 12})
        ]),
        actions_row,
        logs_card
    ], expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)

    # Create the main container with theme support
    logs_container = themed_card(main_content, None, page)  # No title since we have one in content

    def setup_subscriptions() -> None:
        """Setup subscriptions and initial data loading after view is added to page."""
        load_logs()
        update_stats()

        # Update filter chips now that view is attached to page
        update_filter_chips()

        # Override apply_filters to update stats
        nonlocal apply_filters
        original_apply_filters = apply_filters
        def apply_filters() -> None:
            original_apply_filters()
            update_stats()

    def dispose() -> None:
        """Clean up subscriptions and resources."""
        logger.debug("Disposing logs view")
        # Remove FilePicker from page overlay
        try:
            if file_picker in page.overlay:
                page.overlay.remove(file_picker)
                logger.debug("FilePicker removed from page overlay")
            else:
                logger.debug("FilePicker was not in page overlay during disposal")
        except Exception as e:
            logger.warning(f"Failed to remove FilePicker from page overlay: {e}")

        # Clear any lingering references
        try:
            logs_listview.controls.clear()
            filter_chips_row.controls.clear()
            logger.debug("Cleared logs view controls")
        except Exception as e:
            logger.warning(f"Failed to clear logs view controls: {e}")

        # Force update of page overlay to ensure FilePicker is really gone
        try:
            if hasattr(page, 'update') and page.update:
                page.update()
                logger.debug("Updated page after logs view disposal")
        except Exception as e:
            logger.warning(f"Failed to update page after logs view disposal: {e}")

    return logs_container, dispose, setup_subscriptions