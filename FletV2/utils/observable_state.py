#!/usr/bin/env python3
"""
Observable state management for Flet 0.80.0.

This module provides reactive state management using Flet's @ft.observable decorator.
State changes automatically trigger UI re-renders without manual control.update() calls.

This is a modern replacement for SimpleState, providing:
- Automatic UI updates on state changes
- Cleaner, more declarative code
- Better performance through optimized re-renders
- Type-safe mutations with clear interfaces
"""

from __future__ import annotations

import flet as ft
from typing import Any


@ft.observable
class AppState:
    """
    Global application state with reactive updates.

    When any property changes, components watching these properties
    automatically re-render through Flet's observable mechanism.

    ✨ Key Insight: No need to call control.update() or page.update()!
    Just set the property and Flet handles the rest.
    """

    def __init__(self):
        # Data state
        self.clients: list = []
        self.files: list = []
        self.logs_data: list = []
        self.analytics_data: dict = {}
        self.database_records: dict = {}

        # UI state
        self.loading_states: dict = {}  # {"clients": True, "files": False, ...}
        self.error_states: dict = {}    # {"clients": "Connection error", ...}
        self.current_view: str = "dashboard"
        self.selected_client_id: str | None = None
        self.selected_file_id: str | None = None
        self.search_query: str = ""

        # Server state
        self.server_status: str = "unknown"  # "connected", "disconnected", "error"
        self.connection_status: bool = False
        self.database_info: dict = {}
        self.server_stats: dict = {}

        # Toast/notification state
        self.toast_message: str = ""
        self.toast_level: str = "info"  # "info", "success", "warning", "error"

    # ───────────────────────────────────────────────────────────────
    # Data mutations (trigger re-renders)
    # ───────────────────────────────────────────────────────────────

    def set_clients(self, clients: list) -> None:
        """Update client list - automatically triggers re-render of ClientsList component."""
        self.clients = clients
        self.clear_error("clients")

    def set_files(self, files: list) -> None:
        """Update file list - automatically triggers re-render of FilesList component."""
        self.files = files
        self.clear_error("files")

    def set_logs_data(self, logs: list) -> None:
        """Update log entries - automatically triggers re-render of LogsView component."""
        self.logs_data = logs
        self.clear_error("logs")

    def set_analytics_data(self, data: dict) -> None:
        """Update analytics metrics - automatically triggers re-render of AnalyticsView."""
        self.analytics_data = data
        self.clear_error("analytics")

    def set_database_records(self, table_name: str, records: dict) -> None:
        """Update database records for a specific table."""
        new_records = {**self.database_records, table_name: records}
        self.database_records = new_records
        self.clear_error(f"db_{table_name}")

    # ───────────────────────────────────────────────────────────────
    # UI state mutations
    # ───────────────────────────────────────────────────────────────

    def set_loading(self, key: str, loading: bool) -> None:
        """Set loading state for a data fetch operation."""
        new_states = {**self.loading_states, key: loading}
        self.loading_states = new_states

    def is_loading(self, key: str) -> bool:
        """Check if a specific operation is loading."""
        return self.loading_states.get(key, False)

    def set_error(self, key: str, error: str | None) -> None:
        """Set error message for a failed operation."""
        if error:
            new_errors = {**self.error_states, key: error}
            self.error_states = new_errors
        else:
            self.clear_error(key)

    def clear_error(self, key: str) -> None:
        """Clear error for a specific operation."""
        if key in self.error_states:
            new_errors = {k: v for k, v in self.error_states.items() if k != key}
            self.error_states = new_errors

    def get_error(self, key: str) -> str | None:
        """Get error message for a specific operation."""
        return self.error_states.get(key)

    def set_current_view(self, view_name: str) -> None:
        """Change the current view being displayed."""
        self.current_view = view_name

    def set_selected_client(self, client_id: str | None) -> None:
        """Select a client for detailed view."""
        self.selected_client_id = client_id

    def set_selected_file(self, file_id: str | None) -> None:
        """Select a file for detailed view."""
        self.selected_file_id = file_id

    def set_search_query(self, query: str) -> None:
        """Update search query - components can filter based on this."""
        self.search_query = query

    # ───────────────────────────────────────────────────────────────
    # Server state mutations
    # ───────────────────────────────────────────────────────────────

    def set_server_status(self, status: str) -> None:
        """Update server connection status."""
        self.server_status = status
        self.connection_status = status == "connected"

    def set_database_info(self, info: dict) -> None:
        """Update database information."""
        self.database_info = info

    def set_server_stats(self, stats: dict) -> None:
        """Update server statistics."""
        self.server_stats = stats

    # ───────────────────────────────────────────────────────────────
    # Notification state
    # ───────────────────────────────────────────────────────────────

    def show_toast(self, message: str, level: str = "info") -> None:
        """
        Show a temporary notification toast.

        Args:
            message: Toast message text
            level: "info", "success", "warning", or "error"
        """
        self.toast_message = message
        self.toast_level = level

    def show_success(self, message: str) -> None:
        """Show success toast."""
        self.show_toast(message, "success")

    def show_warning(self, message: str) -> None:
        """Show warning toast."""
        self.show_toast(message, "warning")

    def show_error(self, message: str) -> None:
        """Show error toast."""
        self.show_toast(message, "error")

    def clear_toast(self) -> None:
        """Clear the current toast."""
        self.toast_message = ""

    # ───────────────────────────────────────────────────────────────
    # Utility methods
    # ───────────────────────────────────────────────────────────────

    def reset_all(self) -> None:
        """Reset all state to initial values (useful for logout)."""
        self.__init__()

    def to_dict(self) -> dict[str, Any]:
        """Export state as dictionary (useful for debugging/logging)."""
        return {
            "clients": self.clients,
            "files": self.files,
            "logs_data": self.logs_data,
            "analytics_data": self.analytics_data,
            "database_records": self.database_records,
            "loading_states": self.loading_states,
            "error_states": self.error_states,
            "current_view": self.current_view,
            "selected_client_id": self.selected_client_id,
            "selected_file_id": self.selected_file_id,
            "search_query": self.search_query,
            "server_status": self.server_status,
            "connection_status": self.connection_status,
            "database_info": self.database_info,
            "server_stats": self.server_stats,
        }


# Global singleton instance
app_state = AppState()


def get_app_state() -> AppState:
    """Get the global application state instance."""
    return app_state
