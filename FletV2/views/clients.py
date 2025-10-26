#!/usr/bin/env python3
"""
Simplified Clients View - The Flet Way
~350 lines instead of 956 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, AlertDialog, and TextField.
Clean client management with server integration and graceful fallbacks.
"""

import contextlib
import os
import sys
import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

# Ensure repository and package roots are on sys.path for runtime resolution
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import flet as ft

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

from FletV2.utils.async_helpers import create_async_fetch_function, run_sync_in_executor, safe_server_call
from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.state_manager import StateManager
from FletV2.utils.ui_components import AppCard, create_status_pill
from FletV2.utils.user_feedback import show_error_message, show_success_message
from FletV2.utils.ui_builders import (
    create_action_button,
    create_filter_dropdown,
    create_metric_card,
    create_search_bar,
    create_view_header,
)

logger = get_logger(__name__)

# ==============================================================================
# MAIN VIEW
# All logic is organized within create_clients_view as nested functions
# ==============================================================================

# Note: Helper builders moved to FletV2.utils.ui_builders module


def create_clients_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    _state_manager: StateManager | None
) -> Any:
    """Simple clients view using Flet's built-in components."""
    logger.info("Creating simplified clients view")

    state_manager: StateManager | None = _state_manager
    state_subscription_callback: Callable[[Any, Any], None] | None = None

    # Simple state management
    search_query = ""
    status_filter = "all"
    clients_data = []

    # Create async fetch function using proven pattern from async_helpers
    _fetch_clients_async = create_async_fetch_function('get_clients', empty_default=[])

    # Load client data from server or use mock
    async def load_clients_data(*, broadcast: bool | None = None) -> None:
        """Load client data with loading indicator and proper error handling."""
        try:
            # Show loading indicator
            loading_ring.visible = True
            loading_ring.update()

            should_broadcast = state_manager is not None if broadcast is None else broadcast

            new_clients = await _fetch_clients_async(server_bridge)
            apply_clients_data(new_clients, broadcast=should_broadcast)

        except Exception as e:
            logger.error(f"Error loading clients: {e}")
            show_error_message(page, f"Failed to load clients: {e}")

        finally:
            # Hide loading indicator
            loading_ring.visible = False
            loading_ring.update()

    # Create DataTable using Flet's built-in functionality with enhanced header
    clients_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Last Seen")),
            ft.DataColumn(ft.Text("Files")),
            ft.DataColumn(ft.Text("Actions")),
        ],
        rows=[],
        heading_row_color="#212121",  # Enhanced darker header as specified in document
        border_radius=12,
        expand=True
    )

    def get_status_type(status: str) -> str:
        """Map client status to status pill type."""
        status_mapping = {
            "connected": "success",     # Green - active connections
            "disconnected": "error",   # Red - failed connections
            "connecting": "warning",   # Orange - in progress
            "registered": "registered", # Purple - enrolled but not connected
            "offline": "offline",       # Brown - offline clients
            "error": "error",          # Red - error state
            "unknown": "unknown"        # Light Blue Grey - unknown states
        }
        return status_mapping.get(status.lower(), "default")

    def filter_clients() -> list[dict[str, Any]]:
        """Filter clients based on search and status."""
        filtered = clients_data.copy()

        # Apply search filter
        if search_query.strip():
            query = search_query.lower()
            filtered = [
                client for client in filtered
                if (query in str(client.get("id", "")).lower() or
                    query in str(client.get("name", "")).lower() or
                    query in str(client.get("status", "")).lower())
            ]

        # Apply status filter
        if status_filter != "all":
            filtered = [
                client for client in filtered
                if str(client.get("status", "")).lower() == status_filter.lower()
            ]

        return filtered

    def update_table() -> None:
        """Update table using Flet's simple patterns."""
        filtered_clients = filter_clients()
        if clients_table.rows:
            clients_table.rows.clear()

        for client in filtered_clients:
            status = client.get("status", "Unknown")

            if clients_table.rows is not None:
                clients_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(client.get("id", "")))),
                        ft.DataCell(ft.Text(str(client.get("name", "")))),
                        ft.DataCell(create_status_pill(status, get_status_type(status))),
                        ft.DataCell(ft.Text(str(client.get("last_seen", "")))),
                        ft.DataCell(ft.Text(str(client.get("files_count", 0)))),
                        ft.DataCell(
                            ft.PopupMenuButton(
                                icon=ft.Icons.MORE_VERT,
                                items=[
                                    ft.PopupMenuItem(text="View Details", icon=ft.Icons.INFO,
                                                   on_click=lambda _e, c=client: view_client_details(c)),
                                    ft.PopupMenuItem(text="Edit", icon=ft.Icons.EDIT,
                                                   on_click=lambda _e, c=client: edit_client(c)),
                                    ft.PopupMenuItem(text="Disconnect", icon=ft.Icons.LOGOUT,
                                                   on_click=lambda _e, c=client: disconnect_client(c)),
                                    ft.PopupMenuItem(text="Delete", icon=ft.Icons.DELETE,
                                                   on_click=lambda _e, c=client: delete_client(c)),
                                ]
                            )
                        )
                    ]
                )
            )

        clients_table.update()

    # Reactive metric values for stat cards
    total_clients_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
    total_clients_value.semantics_label = "Total clients count"
    connected_clients_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
    connected_clients_value.semantics_label = "Connected clients count"
    disconnected_clients_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
    disconnected_clients_value.semantics_label = "Disconnected clients count"
    total_files_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
    total_files_value.semantics_label = "Total files across clients"

    def update_stats() -> None:
        """Recompute metric card values from current client data."""
        totals = len(clients_data)
        connected = len([client for client in clients_data if str(client.get('status', '')).lower() == 'connected'])
        disconnected = len([client for client in clients_data if str(client.get('status', '')).lower() == 'disconnected'])
        files_total = sum(int(client.get('files_count', 0) or 0) for client in clients_data)

        total_clients_value.value = str(totals)
        connected_clients_value.value = str(connected)
        disconnected_clients_value.value = str(disconnected)
        total_files_value.value = str(files_total)

        for control in (
            total_clients_value,
            connected_clients_value,
            disconnected_clients_value,
            total_files_value,
        ):
            with contextlib.suppress(Exception):
                control.update()

    def apply_clients_data(new_clients: list[dict[str, Any]] | None, *, broadcast: bool = False, source: str = "clients_view") -> None:
        """Centralized handler for client data updates with optional state broadcast."""
        nonlocal clients_data

        normalized: list[dict[str, Any]] = []
        if new_clients:
            for item in new_clients:
                normalized.append(dict(item) if isinstance(item, dict) else item)

        clients_data = normalized
        update_stats()
        update_table()

        if broadcast and state_manager is not None:
            with contextlib.suppress(Exception):
                state_manager.update(
                    "clients",
                    [dict(item) if isinstance(item, dict) else item for item in normalized],
                    source=source,
                )

    if state_manager is not None:
        def _handle_state_clients(new_value, _old_value) -> None:
            if isinstance(new_value, list):
                apply_clients_data(new_value, broadcast=False, source="state_manager")

        state_subscription_callback = _handle_state_clients
        state_manager.subscribe("clients", state_subscription_callback)

    # Client action handlers
    def view_client_details(client: dict[str, Any]) -> None:
        """View client details using AlertDialog."""
        details_dialog = ft.AlertDialog(
            title=ft.Text("Client Details"),
            content=ft.Column([
                ft.Text(f"ID: {client.get('id', 'N/A')}"),
                ft.Text(f"Name: {client.get('name', 'N/A')}"),
                ft.Row([
                    ft.Text("Status: "),
                    create_status_pill(client.get('status', 'Unknown'), get_status_type(client.get('status', 'Unknown')))
                ], spacing=8),
                ft.Text(f"Last Seen: {client.get('last_seen', 'N/A')}"),
                ft.Text(f"Files: {client.get('files_count', 'N/A')}"),
                ft.Text(f"IP Address: {client.get('ip_address', 'N/A')}"),
            ], height=200, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Close", on_click=lambda _e: page.close(details_dialog))
            ],
        )
        page.open(details_dialog)

    def disconnect_client(client: dict[str, Any]) -> None:
        """Disconnect client with confirmation."""

        async def confirm_disconnect_async(_e: ft.ControlEvent) -> None:
            if not server_bridge:
                show_error_message(page, "Server not connected. Please start the backup server.")
                page.close(confirm_dialog)
                return

            client_id = client.get('id')
            if not client_id or not isinstance(client_id, str):
                show_error_message(page, "Invalid client ID")
                page.close(confirm_dialog)
                return

            result = await run_sync_in_executor(safe_server_call, server_bridge, 'disconnect_client', client_id)

            if result.get('success'):
                show_success_message(page, f"Client {client.get('name')} disconnected")
                await load_clients_data()
            else:
                show_error_message(page, f"Failed to disconnect: {result.get('error', 'Unknown error')}")

            page.close(confirm_dialog)

        async def confirm_disconnect(event: ft.ControlEvent) -> None:
            try:
                # Show loading indicator
                loading_ring.visible = True
                loading_ring.update()

                if hasattr(page, "run_task"):
                    await page.run_task(confirm_disconnect_async, event)
                else:
                    await confirm_disconnect_async(event)
            finally:
                # Hide loading indicator
                loading_ring.visible = False
                loading_ring.update()

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Disconnect"),
            content=ft.Text(f"Are you sure you want to disconnect {client.get('name', 'this client')}?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: page.close(confirm_dialog)),
                ft.FilledButton("Disconnect", on_click=confirm_disconnect),
            ],
        )
        page.open(confirm_dialog)

    def delete_client(client: dict[str, Any]) -> None:
        """Delete client with confirmation."""

        async def confirm_delete_async(_e: ft.ControlEvent) -> None:
            if not server_bridge:
                show_error_message(page, "Server not connected. Please start the backup server.")
                page.close(delete_dialog)
                return

            client_id = client.get('id')
            if not client_id or not isinstance(client_id, str):
                show_error_message(page, "Invalid client ID")
                page.close(delete_dialog)
                return

            result = await run_sync_in_executor(safe_server_call, server_bridge, 'delete_client', client_id)

            if result.get('success'):
                show_success_message(page, f"Client {client.get('name')} deleted")
                await load_clients_data()
            else:
                show_error_message(page, f"Failed to delete: {result.get('error', 'Unknown error')}")

            page.close(delete_dialog)

        async def confirm_delete(event: ft.ControlEvent) -> None:
            try:
                # Show loading indicator
                loading_ring.visible = True
                loading_ring.update()

                if hasattr(page, "run_task"):
                    await page.run_task(confirm_delete_async, event)
                else:
                    await confirm_delete_async(event)
            finally:
                # Hide loading indicator
                loading_ring.visible = False
                loading_ring.update()

        delete_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(f"Are you sure you want to delete {client.get('name', 'this client')}?\n\nThis action cannot be undone."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: page.close(delete_dialog)),
                ft.FilledButton("Delete", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED)),
            ],
        )
        page.open(delete_dialog)

    def add_client() -> None:
        """Add new client dialog."""
        name_field = ft.TextField(label="Client Name", hint_text="Enter client name")
        ip_field = ft.TextField(label="IP Address", hint_text="Enter IP address")
        status_dropdown = ft.Dropdown(
            label="Status",
            value="Disconnected",
            options=[
                ft.dropdown.Option("Connected"),
                ft.dropdown.Option("Disconnected"),
                ft.dropdown.Option("Connecting"),
            ]
        )

        async def save_client_async(_e: ft.ControlEvent) -> None:
            if not name_field.value or not name_field.value.strip():
                show_error_message(page, "Client name is required")
                return

            new_client = {
                "id": f"client-{str(uuid.uuid4())[:8]}",
                "name": name_field.value.strip(),
                "ip_address": ip_field.value.strip() if ip_field.value else "Unknown",
                "status": status_dropdown.value,
                "files_count": 0,
                "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            if not server_bridge:
                show_error_message(page, "Server not connected. Please start the backup server.")
                return

            result = await run_sync_in_executor(safe_server_call, server_bridge, 'add_client', new_client)

            if result.get('success'):
                show_success_message(page, f"Client {new_client['name']} added")
                await load_clients_data()
                page.close(add_dialog)
            else:
                show_error_message(page, f"Failed to add client: {result.get('error', 'Unknown error')}")

        async def save_client(event: ft.ControlEvent) -> None:
            try:
                # Show loading indicator
                loading_ring.visible = True
                loading_ring.update()

                if hasattr(page, "run_task"):
                    await page.run_task(save_client_async, event)
                else:
                    await save_client_async(event)
            finally:
                # Hide loading indicator
                loading_ring.visible = False
                loading_ring.update()

        add_dialog = ft.AlertDialog(
            title=ft.Text("Add New Client"),
            content=ft.Column([name_field, ip_field, status_dropdown], height=200, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: page.close(add_dialog)),
                ft.FilledButton("Add", on_click=save_client),
            ],
        )
        page.open(add_dialog)

    def edit_client(client: dict[str, Any]) -> None:
        """Edit existing client dialog."""
        name_field = ft.TextField(label="Client Name", value=client.get('name', ''), hint_text="Enter client name")
        ip_field = ft.TextField(label="IP Address", value=client.get('ip_address', ''), hint_text="Enter IP address")
        status_dropdown = ft.Dropdown(
            label="Status",
            value=client.get('status', 'Disconnected'),
            options=[
                ft.dropdown.Option("Connected"),
                ft.dropdown.Option("Disconnected"),
                ft.dropdown.Option("Connecting"),
            ]
        )

        async def save_changes_async(_e: ft.ControlEvent) -> None:
            if not name_field.value or not name_field.value.strip():
                show_error_message(page, "Client name is required")
                return

            updated_client = {
                **client,  # Keep existing fields
                "name": name_field.value.strip(),
                "ip_address": ip_field.value.strip() if ip_field.value else client.get('ip_address', 'Unknown'),
                "status": status_dropdown.value,
                "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            if not server_bridge:
                show_error_message(page, "Server not connected. Please start the backup server.")
                return

            client_id = updated_client.get('id') or client.get('id')
            if client_id is None:
                show_error_message(page, "Selected client has no ID; cannot update.")
                return

            result = await run_sync_in_executor(safe_server_call, server_bridge, 'update_client', str(client_id), {"name": updated_client["name"]})

            if result.get('success'):
                show_success_message(page, f"Client {updated_client['name']} updated")
                await load_clients_data()
                page.close(edit_dialog)
            else:
                show_error_message(page, f"Failed to update client: {result.get('error', 'Unknown error')}")

        async def save_changes(event: ft.ControlEvent) -> None:
            try:
                # Show loading indicator
                loading_ring.visible = True
                loading_ring.update()

                if hasattr(page, "run_task"):
                    await page.run_task(save_changes_async, event)
                else:
                    await save_changes_async(event)
            finally:
                # Hide loading indicator
                loading_ring.visible = False
                loading_ring.update()

        edit_dialog = ft.AlertDialog(
            title=ft.Text(f"Edit Client: {client.get('name', 'Unknown')}"),
            content=ft.Column([name_field, ip_field, status_dropdown], height=200, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: page.close(edit_dialog)),
                ft.FilledButton("Save", on_click=save_changes),
            ],
        )
        page.open(edit_dialog)

    # Search and filter handlers
    def on_search_change(e: ft.ControlEvent) -> None:
        """Handle search input."""
        nonlocal search_query
        search_query = e.control.value
        update_table()

    def on_status_filter_change(e: ft.ControlEvent) -> None:
        """Handle status filter change."""
        nonlocal status_filter
        status_filter = e.control.value
        update_table()

    async def refresh_clients(_e: ft.ControlEvent) -> None:
        """Refresh clients list."""
        try:
            # Show loading indicator
            loading_ring.visible = True
            loading_ring.update()

            # Load data
            await load_clients_data()
            show_success_message(page, "Clients refreshed")

        finally:
            # Hide loading indicator
            loading_ring.visible = False
            loading_ring.update()

    # Loading indicators
    loading_ring = ft.ProgressRing(width=20, height=20, visible=False)

    # Create UI components
    search_field = create_search_bar(
        on_search_change,
        placeholder="Search clients…",
    )

    status_filter_dropdown = create_filter_dropdown(
        "Status",
        [
            ("all", "All"),
            ("connected", "Connected"),
            ("disconnected", "Disconnected"),
            ("connecting", "Connecting"),
        ],
        on_status_filter_change,
        value=status_filter,
        width=200,
    )

    refresh_button = create_action_button("Refresh", refresh_clients, icon=ft.Icons.REFRESH, primary=False)

    filters_row = ft.ResponsiveRow(
        controls=[
            ft.Container(content=search_field, col={"xs": 12, "sm": 8, "md": 6, "lg": 5}),
            ft.Container(content=status_filter_dropdown, col={"xs": 12, "sm": 4, "md": 3, "lg": 2}),
            ft.Container(
                content=ft.Row(
                    [
                        refresh_button,
                        loading_ring,
                    ],
                    spacing=8,
                ),
                col={"xs": 12, "sm": 12, "md": 3, "lg": 2},
                alignment=ft.alignment.center_left,
            ),
        ],
        spacing=12,
        run_spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    # Client stats using simple metric cards
    # Responsive stats row for all screen sizes
    stats_row = ft.ResponsiveRow([
        ft.Column([create_metric_card("Total Clients", total_clients_value, ft.Icons.PEOPLE, "Total clients metric")],
                 col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([create_metric_card("Connected", connected_clients_value, ft.Icons.WIFI, "Connected clients metric")],
                 col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([create_metric_card("Disconnected", disconnected_clients_value, ft.Icons.WIFI_OFF, "Disconnected clients metric")],
                 col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([create_metric_card("Total Files", total_files_value, ft.Icons.FOLDER, "Total client files metric")],
                 col={"sm": 12, "md": 6, "lg": 3}),
    ])

    stats_section = AppCard(stats_row, title="At a glance")
    filters_section = AppCard(filters_row, title="Filters")
    table_section = AppCard(clients_table, title="Clients")
    table_section.expand = True

    header_actions = [
        create_action_button("Add client", lambda _: add_client(), icon=ft.Icons.PERSON_ADD),
        refresh_button,
    ]

    header = create_view_header(
        "Client management",
        icon=ft.Icons.PEOPLE_ALT_OUTLINED,
        description="Manage registered backup clients and their connection status.",
        actions=header_actions,
    )

    main_column = ft.Column(
        [
            header,
            stats_section,
            filters_section,
            table_section,
        ],
        spacing=16,
        expand=True,
        scroll=ft.ScrollMode.AUTO,
    )

    main_layout = ft.Container(
        content=main_column,
        padding=ft.padding.symmetric(horizontal=20, vertical=16),
        expand=True,
    )

    async def setup_subscriptions() -> None:
        """Setup subscriptions and initial data loading after view is added to page."""
        existing_clients: list[dict[str, Any]] = []
        if state_manager is not None:
            with contextlib.suppress(Exception):
                state_value = state_manager.get("clients", [])
                if isinstance(state_value, list):
                    existing_clients = state_value

        if existing_clients:
            apply_clients_data(existing_clients, broadcast=False, source="state_manager_init")
        else:
            await load_clients_data()

    def dispose() -> None:
        """Clean up subscriptions and resources."""
        nonlocal state_subscription_callback
        logger.debug("Disposing clients view")
        if state_manager is not None and state_subscription_callback is not None:
            with contextlib.suppress(Exception):
                state_manager.unsubscribe("clients", state_subscription_callback)
            state_subscription_callback = None

    return main_layout, dispose, setup_subscriptions
