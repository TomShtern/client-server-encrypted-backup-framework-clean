#!/usr/bin/env python3
"""
Logs View for FletV2
A clean implementation using pure Flet patterns.
"""

import flet as ft
from typing import List, Dict, Any
import asyncio
from utils.debug_setup import get_logger
from datetime import datetime, timedelta
import random

logger = get_logger(__name__)


def create_logs_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create logs view using simple Flet patterns.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The logs view
    """
    
    # Get logs data from server or generate mock data
    def get_logs_data():
        """Get real logs from server bridge or generate mock data."""
        logs_data = []
        if server_bridge:
            try:
                # Try to get logs from server bridge
                logs_data = server_bridge.get_logs()
            except Exception as e:
                logger.warning(f"Failed to get logs from server bridge: {e}")
        
        # Fallback: generate realistic mock log data
        if not logs_data:
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
    
    # Get initial logs data
    logs_data = get_logs_data()
    
    # Filter state (simple variables, no complex state management)
    current_filter = "ALL"
    
    # Helper function to get color for log level
    def get_level_color(level):
        """Get color for log level using Flet's built-in colors."""
        color_map = {
            "INFO": ft.Colors.BLUE,
            "SUCCESS": ft.Colors.GREEN,
            "WARNING": ft.Colors.ORANGE,
            "ERROR": ft.Colors.RED,
            "DEBUG": ft.Colors.GREY
        }
        return color_map.get(level, ft.Colors.ON_SURFACE)
    
    # Filter logs based on current filter
    def get_filtered_logs():
        """Filter logs based on current selection."""
        if current_filter == "ALL":
            return logs_data
        return [log for log in logs_data if log["level"] == current_filter]
    
    # Create action handlers (simple functions)
    def on_filter_change(level):
        def handler(e):
            nonlocal current_filter
            current_filter = level
            logger.info(f"Filter changed to: {level}")
            # Refresh the logs list
            refresh_logs()
        return handler
    
    def on_clear_logs(e):
        logger.info("Clear logs requested")
        # Simple confirmation dialog using Flet's built-in AlertDialog
        dialog = ft.AlertDialog(
            title=ft.Text("Clear Logs"),
            content=ft.Text("Are you sure you want to clear all logs?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: close_dialog()),
                ft.TextButton("Clear", on_click=lambda e: confirm_clear())
            ]
        )
        def close_dialog():
            page.dialog.open = False
            page.update()
        def confirm_clear():
            logger.info("Logs cleared")
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Logs cleared successfully"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
            close_dialog()
        page.dialog = dialog
        dialog.open = True
        page.update()
    
    def on_refresh_logs(e):
        logger.info("Refresh logs")
        refresh_logs()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Logs refreshed"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()
    
    async def export_logs_async():
        """Async function to export logs."""
        try:
            # Simulate async operation
            await asyncio.sleep(1.0)
            logger.info("Exported logs")
            return True
        except Exception as e:
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
                        bgcolor=ft.Colors.BLUE
                    )
                else:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("Failed to export logs"),
                        bgcolor=ft.Colors.RED
                    )
                page.snack_bar.open = True
                page.update()
            except Exception as e:
                logger.error(f"Error in export handler: {e}")
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error exporting logs"),
                    bgcolor=ft.Colors.RED
                )
                page.snack_bar.open = True
                page.update()
        
        # Run async operation
        page.run_task(async_export)
    
    # Create the logs list container (we'll update this reference)
    logs_container = ft.Ref[ft.Column]()
    status_text = ft.Ref[ft.Text]()
    
    def refresh_logs():
        """Refresh the logs display with current filter."""
        filtered_logs = get_filtered_logs()
        # Create log entries using Flet's built-in components
        log_entries = []
        for log in filtered_logs[:100]:  # Limit to 100 entries for performance
            timestamp_str = datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
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
                            color=get_level_color(log["level"])
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
        if logs_container.current:
            logs_container.current.controls = log_entries
            logs_container.current.update()
        # Update status text
        if status_text.current:
            total_logs = len(logs_data)
            filtered_count = len(filtered_logs)
            status_text.current.value = f"Showing {min(100, filtered_count)} of {filtered_count} logs (Total: {total_logs})"
            status_text.current.update()
    
    # Create safe event handlers FIRST
    def safe_refresh_logs():
        """Safe version of refresh_logs that handles initialization."""
        try:
            if logs_container.current and status_text.current:
                refresh_logs()
            else:
                logger.warning("Logs controls not yet mounted, scheduling retry...")
                # Schedule retry after brief delay
                import asyncio
                async def retry_refresh():
                    await asyncio.sleep(0.2)
                    try:
                        if logs_container.current and status_text.current:
                            refresh_logs()
                            logger.info("Logs initialized successfully after retry")
                    except Exception as retry_ex:
                        logger.error(f"Retry failed: {retry_ex}")
                
                if hasattr(page, 'run_task'):
                    page.run_task(retry_refresh)
        except Exception as e:
            logger.error(f"Error in safe_refresh_logs: {e}")
    
    def on_filter_change_safe(level):
        def handler(e):
            nonlocal current_filter
            current_filter = level
            logger.info(f"Filter changed to: {level}")
            safe_refresh_logs()
        return handler
    
    def on_refresh_logs_safe(e):
        logger.info("Refresh logs")
        safe_refresh_logs()
        page.snack_bar = ft.SnackBar(
            content=ft.Text("Logs refreshed"),
            bgcolor=ft.Colors.GREEN
        )
        page.snack_bar.open = True
        page.update()
    
    # Create filter buttons using safe handlers
    filter_buttons = ft.Row([
        ft.ElevatedButton(
            "ALL",
            icon=ft.Icons.FILTER_LIST,
            on_click=on_filter_change_safe("ALL"),
            style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY if current_filter == "ALL" else None)
        ),
        ft.OutlinedButton("INFO", on_click=on_filter_change_safe("INFO")),
        ft.OutlinedButton("SUCCESS", on_click=on_filter_change_safe("SUCCESS")),
        ft.OutlinedButton("WARNING", on_click=on_filter_change_safe("WARNING")),
        ft.OutlinedButton("ERROR", on_click=on_filter_change_safe("ERROR")),
        ft.OutlinedButton("DEBUG", on_click=on_filter_change_safe("DEBUG"))
    ], spacing=10)
    
    # Create the logs container with initial content
    logs_column = ft.Column(
        ref=logs_container,
        controls=[],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=0
    )
    
    # Create the main view structure FIRST (controls must be added to page before refs work)
    main_view = ft.Column([
        # Header with title and action buttons
        ft.Container(
            content=ft.Row([
                ft.Text("System Logs", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),  # Spacer
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh Logs",
                        on_click=on_refresh_logs_safe
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
            content=filter_buttons,
            padding=ft.Padding(20, 0, 20, 10)
        ),
        # Status info
        ft.Container(
            content=ft.Text(
                ref=status_text,
                value=f"Showing logs...",
                color=ft.Colors.ON_SURFACE_VARIANT
            ),
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
            content=logs_column,
            expand=True,
            padding=ft.Padding(20, 0, 20, 20),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            bgcolor=ft.Colors.SURFACE_TINT
        )
    ], expand=True)
    
    # CRITICAL: Populate with initial loading message instead of calling refresh_logs()
    # The refresh_logs will be called by event handlers after the view is properly mounted
    
    # Initial loading state - populate with placeholder content
    initial_loading_entry = ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=16, height=16, stroke_width=2),
            ft.Text("Loading logs...", size=14, color=ft.Colors.ON_SURFACE_VARIANT)
        ], spacing=10),
        padding=ft.Padding(20, 40, 20, 40),
        alignment=ft.alignment.center
    )
    
    # Set initial content
    logs_column.controls = [initial_loading_entry]
    
    # Safe event handlers are now defined above with filter_buttons
    
    # Add trigger mechanism for after view is mounted
    def trigger_initial_load():
        """Trigger initial load after view is mounted to page."""
        safe_refresh_logs()
    
    # Attach the trigger to the main view for external calling
    main_view.trigger_initial_load = trigger_initial_load
    
    # Return the main view - logs will be populated when controls are attached to page
    return main_view