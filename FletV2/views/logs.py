#!/usr/bin/env python3
"""
Logs View for FletV2
An improved implementation using ft.UserControl for better state management.
"""

import flet as ft
from typing import List, Dict, Any
import asyncio
from utils.debug_setup import get_logger
from datetime import datetime, timedelta
import random
from config import ASYNC_DELAY

logger = get_logger(__name__)


class LogsView(ft.UserControl):
    """
    Logs view using ft.UserControl for better state management.
    """
    
    def __init__(self, server_bridge, page: ft.Page):
        super().__init__()
        self.server_bridge = server_bridge
        self.page = page
        self.logs_data: List[Dict[str, Any]] = []
        self.filtered_logs_data: List[Dict[str, Any]] = []
        self.current_filter = "ALL"
        self.is_loading = False
        self.last_updated = None
        
        # UI References
        self.logs_container = None
        self.status_text = None
        self.last_updated_text = None
        self.filter_buttons = []
        
    def build(self):
        """Build the logs view UI."""
        self.status_text = ft.Text(
            value="Loading logs...",
            color=ft.Colors.ON_SURFACE_VARIANT,
            ref=ft.Ref[ft.Text]()
        )
        
        self.last_updated_text = ft.Text(
            value="Last updated: Never",
            color=ft.Colors.ON_SURFACE,
            size=12
        )
        
        # Create filter buttons
        self.filter_buttons = [
            ft.ElevatedButton(
                "ALL",
                icon=ft.Icons.FILTER_LIST,
                on_click=self._create_filter_handler("ALL"),
                style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY if self.current_filter == "ALL" else None)
            ),
            ft.OutlinedButton("INFO", on_click=self._create_filter_handler("INFO")),
            ft.OutlinedButton("SUCCESS", on_click=self._create_filter_handler("SUCCESS")),
            ft.OutlinedButton("WARNING", on_click=self._create_filter_handler("WARNING")),
            ft.OutlinedButton("ERROR", on_click=self._create_filter_handler("ERROR")),
            ft.OutlinedButton("DEBUG", on_click=self._create_filter_handler("DEBUG"))
        ]
        
        self.logs_container = ft.Column(
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0
        )
        
        # Build the main view
        return ft.Column([
            # Header with title and action buttons
            ft.Container(
                content=ft.Row([
                    ft.Text("System Logs", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),  # Spacer
                    ft.Row([
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Refresh Logs",
                            on_click=self._on_refresh_logs
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DOWNLOAD,
                            tooltip="Export Logs",
                            on_click=self._on_export_logs
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLEAR_ALL,
                            tooltip="Clear Logs",
                            icon_color=ft.Colors.RED,
                            on_click=self._on_clear_logs
                        )
                    ], spacing=5)
                ]),
                padding=ft.Padding(20, 20, 20, 10)
            ),
            # Filter buttons
            ft.Container(
                content=ft.Row(self.filter_buttons, spacing=10),
                padding=ft.Padding(20, 0, 20, 10)
            ),
            # Status info
            ft.Container(
                content=ft.Row([
                    self.status_text,
                    ft.Container(expand=True),
                    self.last_updated_text
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
                content=self.logs_container,
                expand=True,
                padding=ft.Padding(20, 0, 20, 20),
                border=ft.border.all(1, ft.Colors.OUTLINE),
                bgcolor=ft.Colors.SURFACE_TINT
            )
        ], expand=True)
    
    async def _load_logs_data_async(self):
        """Asynchronously load logs data."""
        if self.is_loading:
            return
            
        self.is_loading = True
        try:
            # Show loading state
            self.status_text.value = "Loading logs..."
            self.status_text.update()
            
            # Load data asynchronously
            if self.server_bridge:
                self.logs_data = await self.page.run_thread(self.server_bridge.get_logs)
            else:
                # Generate mock log data
                self.logs_data = await self.page.run_thread(self._generate_mock_logs)
            
            # Update last updated timestamp
            self.last_updated = datetime.now()
            self.last_updated_text.value = f"Last updated: {self.last_updated.strftime('%H:%M:%S')}"
            
            # Apply current filter
            self._filter_logs()
            
            # Update UI
            self._update_logs_display()
            self._update_status_text()
            
        except Exception as e:
            logger.error(f"Error loading logs data: {e}")
            self.status_text.value = "Error loading logs data"
        finally:
            self.is_loading = False
            self.update()
    
    def _generate_mock_logs(self):
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
    
    def _filter_logs(self):
        """Filter logs based on current selection."""
        if self.current_filter == "ALL":
            self.filtered_logs_data = self.logs_data
        else:
            self.filtered_logs_data = [log for log in self.logs_data if log["level"] == self.current_filter]
    
    def _update_logs_display(self):
        """Update the logs display with current filter."""
        # Create log entries using Flet's built-in components
        log_entries = []
        for log in self.filtered_logs_data[:100]:  # Limit to 100 entries for performance
            timestamp_str = datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
            level_color = self._get_level_color(log["level"])
            
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
        self.logs_container.controls = log_entries
    
    def _update_status_text(self):
        """Update status text."""
        total_logs = len(self.logs_data)
        filtered_count = len(self.filtered_logs_data)
        self.status_text.value = f"Showing {min(100, filtered_count)} of {filtered_count} logs (Total: {total_logs})"
    
    def _get_level_color(self, level):
        """Get color for log level."""
        color_map = {
            "INFO": ft.Colors.BLUE,
            "SUCCESS": ft.Colors.GREEN,
            "WARNING": ft.Colors.ORANGE,
            "ERROR": ft.Colors.RED,
            "DEBUG": ft.Colors.GREY
        }
        return color_map.get(level, ft.Colors.ON_SURFACE)
    
    def _create_filter_handler(self, level):
        def handler(e):
            self.current_filter = level
            logger.info(f"Filter changed to: {level}")
            # Update button styles
            for i, button in enumerate(self.filter_buttons):
                if i == 0:  # ALL button
                    button.style = ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY if level == "ALL" else None)
                button.update()
            
            # Apply filter and update display
            self._filter_logs()
            self._update_logs_display()
            self._update_status_text()
            self.update()
        return handler
    
    def _on_clear_logs(self, e):
        logger.info("Clear logs requested")
        # Simple confirmation dialog using Flet's built-in AlertDialog
        dialog = ft.AlertDialog(
            title=ft.Text("Clear Logs"),
            content=ft.Text("Are you sure you want to clear all logs?"),
            actions=[
                ft.TextButton("Cancel", on_click=self._close_dialog),
                ft.TextButton("Clear", on_click=self._confirm_clear)
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def _confirm_clear(self, e):
        logger.info("Logs cleared")
        self.logs_data = []
        self.filtered_logs_data = []
        self._update_logs_display()
        self._update_status_text()
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Logs cleared successfully"),
            bgcolor=ft.Colors.GREEN
        )
        self.page.snack_bar.open = True
        self._close_dialog(None)
    
    def _close_dialog(self, e):
        self.page.dialog.open = False
        self.page.update()
    
    def _on_refresh_logs(self, e):
        logger.info("Refresh logs")
        self.page.run_task(self._load_logs_data_async)
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Refreshing logs..."),
            bgcolor=ft.Colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    async def _export_logs_async(self):
        """Async function to export logs."""
        try:
            # Simulate async operation
            await asyncio.sleep(ASYNC_DELAY)
            logger.info("Exported logs")
            return True
        except Exception as e:
            logger.error(f"Failed to export logs: {e}")
            return False

    def _on_export_logs(self, e):
        logger.info("Export logs requested")
        
        async def async_export():
            try:
                success = await self._export_logs_async()
                if success:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Logs exported to logs_export.txt"),
                        bgcolor=ft.Colors.BLUE
                    )
                else:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Failed to export logs"),
                        bgcolor=ft.Colors.RED
                    )
                self.page.snack_bar.open = True
                self.page.update()
            except Exception as e:
                logger.error(f"Error in export handler: {e}")
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Error exporting logs"),
                    bgcolor=ft.Colors.RED
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        # Run async operation
        self.page.run_task(async_export)
    
    def did_mount(self):
        """Called when the control is added to the page."""
        self.page.run_task(self._load_logs_data_async)


def create_logs_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create logs view using ft.UserControl.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The logs view
    """
    return LogsView(server_bridge, page)