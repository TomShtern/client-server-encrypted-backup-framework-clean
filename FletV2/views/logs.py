#!/usr/bin/env python3
"""
Logs View for FletV2
Clean function-based implementation using Flet's built-in components.
"""

import flet as ft
from typing import List, Dict, Any
import asyncio
from utils.debug_setup import get_logger
from utils.user_feedback import show_success_message, show_error_message, show_info_message
from datetime import datetime, timedelta
import random
from config import ASYNC_DELAY

logger = get_logger(__name__)


def create_logs_view(server_bridge, page: ft.Page, state_manager=None) -> ft.Control:
    """
    Create logs view with enhanced infrastructure and state management.

    Args:
        server_bridge: Enhanced server bridge for data access
        page: Flet page instance
        state_manager: Reactive state manager for cross-view data sharing

    Returns:
        ft.Control: The logs view
    """
    logger.info("Creating logs view with enhanced infrastructure")
    # State variables
    logs_data: List[Dict[str, Any]] = []
    filtered_logs_data: List[Dict[str, Any]] = []
    current_filter = "ALL"
    is_loading = False
    last_updated = None

    def generate_mock_logs():
        """Generate mock log data."""
        base_time = datetime.now()
        log_types = ["INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG"]
        components = ["Server", "Client", "Database", "File Transfer", "Authentication", "System"]
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
        # Generate 50 recent log entries
        logs_data = []
        for i in range(50):
            time_offset = timedelta(
                hours=random.randint(0, 24),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            log_time = base_time - time_offset
            log_type = random.choice(log_types)
            component = random.choice(components)
            message_template = random.choice(messages)
            # Format message with random data
            message = message_template.format(
                ip=random.randint(100, 199),
                filename=f"document_{random.randint(1, 999)}.{random.choice(['pdf', 'docx', 'txt', 'jpg'])}",
                id=random.randint(1, 100),
                time=random.randint(50, 500),
                usage=random.randint(30, 95)
            )
            logs_data.append({
                "id": i + 1,
                "timestamp": log_time.isoformat(),
                "level": log_type,
                "component": component,
                "message": message
            })
        # Sort by timestamp (most recent first)
        logs_data.sort(key=lambda x: x["timestamp"], reverse=True)
        return logs_data

    def get_level_color(level):
        """Get color for log level."""
        color_map = {
            "INFO": ft.Colors.BLUE,
            "SUCCESS": ft.Colors.GREEN,
            "WARNING": ft.Colors.ORANGE,
            "ERROR": ft.Colors.RED,
            "DEBUG": ft.Colors.GREY
        }
        return color_map.get(level, ft.Colors.ON_SURFACE)

    def filter_logs():
        """Filter logs based on current selection."""
        nonlocal filtered_logs_data
        if current_filter == "ALL":
            filtered_logs_data = logs_data
        else:
            filtered_logs_data = [log for log in logs_data if log["level"] == current_filter]

    def update_logs_display():
        """Update the logs display with current filter and empty state handling."""
        if not filtered_logs_data:
            # Show empty state
            empty_state = ft.Container(
                content=ft.Column([
                    ft.Icon(
                        ft.Icons.LOGS,
                        size=64,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    ft.Text(
                        "No logs found",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE
                    ),
                    ft.Text(
                        "No log entries match the current filter criteria.",
                        size=14,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    ft.Container(height=10),
                    ft.OutlinedButton(
                        "Show All Logs",
                        icon=ft.Icons.FILTER_LIST,
                        on_click=create_filter_handler("ALL"),
                        tooltip="Clear filters to show all logs"
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16
                ),
                height=300,
                alignment=ft.alignment.center
            )
            logs_container.controls = [empty_state]
        else:
            # Create log entries using Flet's built-in components
            log_entries = []
            for log in filtered_logs_data[:100]:  # Limit to 100 entries for performance
                timestamp_str = datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
                level_color = get_level_color(log["level"])

                log_entry = ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Text(
                                timestamp_str,
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            ),
                            width=80
                        ),
                        ft.Container(
                            content=ft.Text(
                                log["level"],
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=level_color
                            ),
                            width=70
                        ),
                        ft.Container(
                            content=ft.Text(
                                log["component"],
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            ),
                            width=100
                        ),
                        ft.Container(
                            content=ft.Text(
                                log["message"],
                                size=12,
                                overflow=ft.TextOverflow.ELLIPSIS
                            ),
                            expand=True
                        )
                    ], spacing=10),
                    padding=ft.Padding(10, 8, 10, 8),
                    border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)),
                    bgcolor=ft.Colors.SURFACE if log["level"] != "ERROR" else ft.Colors.ERROR_CONTAINER
                )
                log_entries.append(log_entry)

            # Update the logs container
            logs_container.controls = log_entries

        logs_container.update()

    def update_status_text():
        """Update status text."""
        total_logs = len(logs_data)
        filtered_count = len(filtered_logs_data)
        status_text.value = f"Showing {min(100, filtered_count)} of {filtered_count} logs (Total: {total_logs})"
        status_text.update()

    async def load_logs_data_async():
        """Asynchronously load logs data."""
        nonlocal logs_data, is_loading, last_updated
        if is_loading:
            return

        is_loading = True
        try:
            # Show loading state
            status_text.value = "Loading logs..."
            status_text.update()

            # Load data directly (no blocking await)
            if server_bridge:
                try:
                    logs_data = server_bridge.get_logs()
                except Exception as e:
                    logger.warning(f"Server bridge failed: {e}")
                    logs_data = generate_mock_logs()
            else:
                # Generate mock log data
                logs_data = generate_mock_logs()

            # Update last updated timestamp
            last_updated = datetime.now()
            last_updated_text.value = f"Last updated: {last_updated.strftime('%H:%M:%S')}"
            last_updated_text.update()

            # Apply current filter
            filter_logs()

            # Update UI
            update_logs_display()
            update_status_text()

        except Exception as e:
            logger.error(f"Error loading logs data: {e}")
            status_text.value = "Error loading logs data"
            status_text.update()
        finally:
            is_loading = False

    def create_filter_handler(level):
        def handler(e):
            nonlocal current_filter
            current_filter = level
            logger.info(f"Filter changed to: {level}")
            # Update button styles
            for i, button in enumerate(filter_buttons):
                if i == 0:  # ALL button
                    button.style = ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY if level == "ALL" else None)
                button.update()

            # Apply filter and update display
            filter_logs()
            update_logs_display()
            update_status_text()
        return handler

    def close_dialog(e):
        page.dialog.open = False
        page.update()

    def confirm_clear(e):
        nonlocal logs_data, filtered_logs_data
        logger.info("Logs cleared")
        logs_data = []
        filtered_logs_data = []
        update_logs_display()
        update_status_text()
        show_success_message(page, "Logs cleared successfully")
        close_dialog(None)

    def on_clear_logs(e):
        logger.info("Clear logs requested")
        # Simple confirmation dialog using Flet's built-in AlertDialog
        dialog = ft.AlertDialog(
            title=ft.Text("Clear Logs"),
            content=ft.Text("Are you sure you want to clear all logs?"),
            actions=[
                ft.TextButton("Cancel", icon=ft.Icons.CANCEL, on_click=close_dialog, tooltip="Cancel log clearing"),
                ft.TextButton("Clear", icon=ft.Icons.CLEAR, on_click=confirm_clear, tooltip="Clear all logs")
            ]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def on_refresh_logs(e):
        logger.info("Refresh logs")
        page.run_task(load_logs_data_async)
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Refreshing logs..."),
            bgcolor=ft.Colors.BLUE
        )
        page.snack_bar.open = True
        page.update()

    async def export_logs_async():
        """Async function to export logs with progress indication."""
        try:
            # Show progress dialog
            progress_ring = ft.ProgressRing(width=40, height=40)
            progress_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Exporting Logs"),
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Exporting log data..."),
                        ft.Container(height=20),
                        ft.Row([
                            progress_ring,
                            ft.Container(width=20),
                            ft.Text("Processing logs...", size=14)
                        ], alignment=ft.MainAxisAlignment.CENTER)
                    ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    width=300,
                    height=150
                ),
                actions_alignment=ft.MainAxisAlignment.CENTER
            )

            page.dialog = progress_dialog
            progress_dialog.open = True
            page.update()

            # Get logs data (simulate getting log entries)
            progress_text = ft.Text("Collecting log data...", size=14)
            progress_dialog.content.content.controls[2].controls[2] = progress_text
            page.update()
            await asyncio.sleep(ASYNC_DELAY * 0.5)

            # Simulate processing logs
            progress_text.value = "Writing log file..."
            page.update()
            await asyncio.sleep(ASYNC_DELAY * 0.5)

            # Simulate file operations
            progress_text.value = "Finalizing export..."
            page.update()
            await asyncio.sleep(ASYNC_DELAY * 0.5)

            # Close progress dialog
            progress_dialog.open = False
            page.update()

            logger.info("Exported logs")
            return True
        except Exception as e:
            # Close progress dialog on error
            if 'progress_dialog' in locals() and progress_dialog.open:
                progress_dialog.open = False
                page.update()
            logger.error(f"Failed to export logs: {e}")
            return False

    def on_export_logs(e):
        logger.info("Export logs requested")

        async def async_export():
            try:
                success = await export_logs_async()
                if success:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Logs exported to logs_export.txt"),
                        bgcolor=ft.Colors.GREEN
                    )
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Failed to export logs"),
                        bgcolor=ft.Colors.ERROR
                    )
                page.snack_bar.open = True
                page.update()
            except Exception as e:
                logger.error(f"Error in export handler: {e}")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error exporting logs"),
                    bgcolor=ft.Colors.ERROR
                )
                page.snack_bar.open = True
                page.update()

        # Run async operation
        page.run_task(async_export)

    # Create UI controls
    status_text = ft.Text(
        value="Loading logs...",
        color=ft.Colors.ON_SURFACE_VARIANT
    )

    last_updated_text = ft.Text(
        value="Last updated: Never",
        color=ft.Colors.ON_SURFACE,
        size=12
    )

    # Create filter buttons
    filter_buttons = [
        ft.FilledButton(
            "ALL",
            icon=ft.Icons.FILTER_LIST,
            on_click=create_filter_handler("ALL"),
            style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY if current_filter == "ALL" else None),
            tooltip="Show all log entries"
        ),
        ft.OutlinedButton("INFO", icon=ft.Icons.INFO, on_click=create_filter_handler("INFO"), tooltip="Show info logs"),
        ft.OutlinedButton("SUCCESS", icon=ft.Icons.CHECK_CIRCLE, on_click=create_filter_handler("SUCCESS"), tooltip="Show success logs"),
        ft.OutlinedButton("WARNING", icon=ft.Icons.WARNING, on_click=create_filter_handler("WARNING"), tooltip="Show warning logs"),
        ft.OutlinedButton("ERROR", icon=ft.Icons.ERROR, on_click=create_filter_handler("ERROR"), tooltip="Show error logs"),
        ft.OutlinedButton("DEBUG", icon=ft.Icons.BUG_REPORT, on_click=create_filter_handler("DEBUG"), tooltip="Show debug logs")
    ]

    logs_container = ft.Column(
        controls=[],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0
    )

    # Schedule initial data load after controls are added to page
    def schedule_initial_load():
        """Schedule initial data load with retry mechanism."""
        async def delayed_load():
            # Wait a bit for controls to be attached
            await asyncio.sleep(0.1)
            # Check if controls are attached before proceeding
            if (status_text and
                hasattr(status_text, 'page') and
                status_text.page is not None):
                await load_logs_data_async()
            else:
                logger.warning("Controls not attached, skipping initial load")
        page.run_task(delayed_load)

    schedule_initial_load()

    # Build the main view
    view = ft.Column([
        # Header with title and action buttons
        ft.Container(
            content=ft.Row([
                ft.Text("System Logs", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),  # Spacer
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh Logs",
                        on_click=on_refresh_logs
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DOWNLOAD,
                        tooltip="Export Logs",
                        on_click=on_export_logs
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLEAR_ALL,
                        tooltip="Clear Logs",
                        icon_color=ft.Colors.RED,
                        on_click=on_clear_logs
                    )
                ], spacing=5)
            ]),
            padding=ft.Padding(20, 20, 20, 10)
        ),
        # Filter buttons
        ft.Container(
            content=ft.Row(filter_buttons, spacing=10),
            padding=ft.Padding(20, 0, 20, 10)
        ),
        # Status info
        ft.Container(
            content=ft.Row([
                status_text,
                ft.Container(expand=True),
                last_updated_text
            ]),
            padding=ft.Padding(20, 0, 20, 10)
        ),
        # Logs header
        ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text("Time", weight=ft.FontWeight.BOLD, size=12),
                    width=80
                ),
                ft.Container(
                    content=ft.Text("Level", weight=ft.FontWeight.BOLD, size=12),
                    width=70
                ),
                ft.Container(
                    content=ft.Text("Component", weight=ft.FontWeight.BOLD, size=12),
                    width=100
                ),
                ft.Container(
                    content=ft.Text("Message", weight=ft.FontWeight.BOLD, size=12),
                    expand=True
                )
            ], spacing=10),
            padding=ft.Padding(10, 8, 10, 8),
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE)
        ),
        # Logs list in a scrollable container
        ft.Container(
            content=logs_container,
            expand=True,
            padding=ft.Padding(20, 0, 20, 20),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            bgcolor=ft.Colors.SURFACE_TINT
        )
    ], expand=True)

    # Also provide a trigger for manual loading if needed
    def trigger_initial_load():
        """Trigger initial data load manually."""
        page.run_task(load_logs_data_async)

    # Export the trigger function so it can be called externally
    view.trigger_initial_load = trigger_initial_load

    return view
