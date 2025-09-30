#!/usr/bin/env python3
"""
Simplified Clients View - The Flet Way
~350 lines instead of 956 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, AlertDialog, and TextField.
Clean client management with server integration and graceful fallbacks.
"""

import asyncio
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

from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.state_manager import StateManager
from FletV2.utils.ui_components import create_status_pill, themed_button, themed_card
from FletV2.utils.user_feedback import show_error_message, show_success_message

logger = get_logger(__name__)

# ==============================================================================
# Helper builders
# ==============================================================================


def _build_metric_card(title: str, value_control: Any, icon: str, card_description: str):
    """Create a reusable metric card wrapper."""
    card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, size=24), ft.Text(title, size=14)]),
                value_control,
            ], spacing=8),
            padding=20,
        ),
        elevation=2,
    )
    card.is_semantic_container = True  # Semantic accessibility for card (using card_description parameter for context)
    return card



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

    def _fetch_clients_sync() -> list[dict[str, Any]]:
        """Retrieve clients synchronously from real server only."""
        if not server_bridge:
            logger.error("Server bridge not available - cannot fetch clients")
            return []

        try:
            result = server_bridge.get_clients()
            if isinstance(result, list):
                return result
            if isinstance(result, dict) and result.get("success"):
                data = result.get("data", [])
                return data if isinstance(data, list) else []
        except Exception as ex:
            logger.error(f"Failed to fetch clients from server: {ex}")
            return []

        logger.warning("Server returned unexpected response format")
        return []

    async def _fetch_clients_async() -> list[dict[str, Any]]:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _fetch_clients_sync)

    # Load client data from server or use mock
    def load_clients_data(*, broadcast: bool | None = None) -> None:
        """Load client data using optional async scheduling to avoid blocking UI."""
        should_broadcast = state_manager is not None if broadcast is None else broadcast

        async def _load_and_apply() -> None:
            new_clients = await _fetch_clients_async()
            apply_clients_data(new_clients, broadcast=should_broadcast)

        if hasattr(page, "run_task"):
            page.run_task(_load_and_apply)
        else:
            apply_clients_data(_fetch_clients_sync(), broadcast=should_broadcast)

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
        def confirm_disconnect(_e: ft.ControlEvent) -> None:
            if server_bridge:
                client_id = client.get('id')
                if not client_id or not isinstance(client_id, str):
                    show_error_message(page, "Invalid client ID")
                    return
                try:
                    result = server_bridge.disconnect_client(client_id)
                    if result.get('success'):
                        show_success_message(page, f"Client {client.get('name')} disconnected")
                        load_clients_data()
                    else:
                        show_error_message(page, f"Failed to disconnect: {result.get('error', 'Unknown error')}")
                except Exception as ex:
                    show_error_message(page, f"Error: {ex}")
            else:
                # No server connection
                show_error_message(page, "Server not connected. Please start the backup server.")
                return

            page.close(confirm_dialog)

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
        def confirm_delete(_e: ft.ControlEvent) -> None:
            nonlocal clients_data
            if server_bridge:
                client_id = client.get('id')
                if not client_id or not isinstance(client_id, str):
                    show_error_message(page, "Invalid client ID")
                    return
                try:
                    result = server_bridge.delete_client(client_id)
                    if result.get('success'):
                        show_success_message(page, f"Client {client.get('name')} deleted")
                        load_clients_data()
                    else:
                        show_error_message(page, f"Failed to delete: {result.get('error', 'Unknown error')}")
                except Exception as ex:
                    show_error_message(page, f"Error: {ex}")
            else:
                # No server connection
                show_error_message(page, "Server not connected. Please start the backup server.")
                return

            page.close(delete_dialog)

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
        nonlocal clients_data
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

        def save_client(_e: ft.ControlEvent) -> None:
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

            if server_bridge:
                try:
                    result = server_bridge.add_client(new_client)
                    if result.get('success'):
                        show_success_message(page, f"Client {new_client['name']} added")
                        load_clients_data()
                    else:
                        show_error_message(page, f"Failed to add client: {result.get('error', 'Unknown error')}")
                except Exception as ex:
                    show_error_message(page, f"Error: {ex}")
            else:
                # No server connection
                show_error_message(page, "Server not connected. Please start the backup server.")
                return

            page.close(add_dialog)

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
        nonlocal clients_data
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

        def save_changes(_e: ft.ControlEvent) -> None:
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

            if server_bridge:
                try:
                    result = server_bridge.update_client(client.get('id'), updated_client)
                    if result.get('success'):
                        show_success_message(page, f"Client {updated_client['name']} updated")
                        load_clients_data()
                    else:
                        show_error_message(page, f"Failed to update client: {result.get('error', 'Unknown error')}")
                except Exception as ex:
                    show_error_message(page, f"Error: {ex}")
            else:
                # No server connection
                show_error_message(page, "Server not connected. Please start the backup server.")
                return

            page.close(edit_dialog)

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

    def refresh_clients(_e: ft.ControlEvent) -> None:
        """Refresh clients list."""
        load_clients_data()
        show_success_message(page, "Clients refreshed")

    # Create UI components
    search_field = ft.TextField(
        label="Search clients",
        prefix_icon=ft.Icons.SEARCH,
        on_change=on_search_change,
        width=300
    )

    status_filter_dropdown = ft.Dropdown(
        label="Filter by Status",
        value="all",
        options=[
            ft.dropdown.Option("all", "All"),
            ft.dropdown.Option("connected", "Connected"),
            ft.dropdown.Option("disconnected", "Disconnected"),
            ft.dropdown.Option("connecting", "Connecting"),
        ],
        on_change=on_status_filter_change,
        width=150
    )

    # Actions row
    actions_row = ft.Row([
        search_field,
        status_filter_dropdown,
        ft.Container(expand=True),  # Spacer
        themed_button("Add Client", lambda _e: add_client(), "filled", ft.Icons.ADD),
        themed_button("Refresh", refresh_clients, "outlined", ft.Icons.REFRESH),
    ], spacing=10)

    # Client stats using simple metric cards
    # Responsive stats row for all screen sizes
    stats_row = ft.ResponsiveRow([
        ft.Column([_build_metric_card("Total Clients", total_clients_value, ft.Icons.PEOPLE, "Total clients metric")],
                 col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([_build_metric_card("Connected", connected_clients_value, ft.Icons.WIFI, "Connected clients metric")],
                 col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([_build_metric_card("Disconnected", disconnected_clients_value, ft.Icons.WIFI_OFF, "Disconnected clients metric")],
                 col={"sm": 12, "md": 6, "lg": 3}),
        ft.Column([_build_metric_card("Total Files", total_files_value, ft.Icons.FOLDER, "Total client files metric")],
                 col={"sm": 12, "md": 6, "lg": 3}),
    ])

    # Enhanced table with layered card design
    table_card = themed_card(clients_table, "Clients", page)

    # Main layout with scrollbar for long client lists
    main_content = ft.Column([
        ft.Text("Client Management", size=28, weight=ft.FontWeight.BOLD),
        stats_row,
        actions_row,
        table_card
    ], expand=True, spacing=20, scroll=ft.ScrollMode.AUTO)

    # Create the main container with theme support
    clients_container = themed_card(main_content, None, page)  # No title since we have one in content

    def setup_subscriptions() -> None:
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
            load_clients_data()

    def dispose() -> None:
        """Clean up subscriptions and resources."""
        nonlocal state_subscription_callback
        logger.debug("Disposing clients view")
        if state_manager is not None and state_subscription_callback is not None:
            with contextlib.suppress(Exception):
                state_manager.unsubscribe("clients", state_subscription_callback)
            state_subscription_callback = None

    return clients_container, dispose, setup_subscriptions
