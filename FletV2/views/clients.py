#!/usr/bin/env python3
"""
Simplified Clients View - The Flet Way
~350 lines instead of 956 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, AlertDialog, and TextField.
Clean client management with server integration and graceful fallbacks.
"""

import flet as ft
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_components import themed_card, themed_button, themed_metric_card, create_status_pill
from utils.user_feedback import show_success_message, show_error_message

logger = get_logger(__name__)


def create_clients_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    _state_manager: StateManager
) -> ft.Control:
    """Simple clients view using Flet's built-in components."""
    logger.info("Creating simplified clients view")

    # Simple state management
    search_query = ""
    status_filter = "all"
    clients_data = []

    # Mock client data for demonstration
    def get_mock_clients() -> List[Dict[str, Any]]:
        """Simple mock client data generator."""
        return [
            {"id": "client-001", "name": "Desktop-PC-01", "status": "Connected",
             "last_seen": "2025-01-17 14:30:25", "files_count": 15, "ip_address": "192.168.1.100"},
            {"id": "client-002", "name": "Laptop-User-02", "status": "Disconnected",
             "last_seen": "2025-01-17 13:45:10", "files_count": 8, "ip_address": "192.168.1.101"},
            {"id": "client-003", "name": "Server-Backup-03", "status": "Connecting",
             "last_seen": "2025-01-17 14:35:18", "files_count": 42, "ip_address": "192.168.1.102"},
            {"id": "client-004", "name": "Mobile-Device-04", "status": "Connected",
             "last_seen": "2025-01-17 14:36:22", "files_count": 23, "ip_address": "192.168.1.103"},
            {"id": "client-005", "name": "WorkStation-05", "status": "Disconnected",
             "last_seen": "2025-01-17 12:20:45", "files_count": 67, "ip_address": "192.168.1.104"},
        ]

    # Load client data from server or use mock
    def load_clients_data():
        """Load client data using server bridge or mock."""
        nonlocal clients_data

        if server_bridge:
            try:
                result = server_bridge.get_clients()
                if result.get('success'):
                    clients_data = result.get('data', [])
                else:
                    clients_data = get_mock_clients()
            except Exception:
                clients_data = get_mock_clients()
        else:
            clients_data = get_mock_clients()

        update_table()

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

    def filter_clients():
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

    def update_table():
        """Update table using Flet's simple patterns."""
        filtered_clients = filter_clients()
        clients_table.rows.clear()

        for client in filtered_clients:
            status = client.get("status", "Unknown")

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

    # Client action handlers
    def view_client_details(client: Dict[str, Any]):
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

    def disconnect_client(client: Dict[str, Any]):
        """Disconnect client with confirmation."""
        def confirm_disconnect(_e):
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
                # Mock success
                show_success_message(page, f"Client {client.get('name')} disconnected (mock mode)")
                load_clients_data()

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

    def delete_client(client: Dict[str, Any]):
        """Delete client with confirmation."""
        def confirm_delete(_e):
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
                # Mock success - remove from local data
                global clients_data
                clients_data = [c for c in clients_data if c.get('id') != client.get('id')]
                show_success_message(page, f"Client {client.get('name')} deleted (mock mode)")
                update_table()

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

    def add_client():
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

        def save_client(_e):
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
                # Mock success - add to local data
                global clients_data
                clients_data.append(new_client)
                show_success_message(page, f"Client {new_client['name']} added (mock mode)")
                update_table()

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

    # Search and filter handlers
    def on_search_change(e):
        """Handle search input."""
        nonlocal search_query
        search_query = e.control.value
        update_table()

    def on_status_filter_change(e):
        """Handle status filter change."""
        nonlocal status_filter
        status_filter = e.control.value
        update_table()

    def refresh_clients(_e):
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
    stats_row = ft.Row([
        themed_metric_card("Total Clients", str(len(clients_data)), ft.Icons.PEOPLE),
        themed_metric_card("Connected", str(len([c for c in clients_data if c.get('status', '').lower() == 'connected'])), ft.Icons.WIFI),
        themed_metric_card("Disconnected", str(len([c for c in clients_data if c.get('status', '').lower() == 'disconnected'])), ft.Icons.WIFI_OFF),
        themed_metric_card("Total Files", str(sum(c.get('files_count', 0) for c in clients_data)), ft.Icons.FOLDER),
    ], spacing=10)

    # Enhanced table with layered card design
    table_card = themed_card(clients_table, "Clients", page)

    # Main layout
    main_content = ft.Column([
        ft.Text("Client Management", size=28, weight=ft.FontWeight.BOLD),
        stats_row,
        actions_row,
        table_card
    ], expand=True, spacing=20)

    # Create the main container with theme support
    clients_container = themed_card(main_content, None, page)  # No title since we have one in content

    def setup_subscriptions():
        """Setup subscriptions and initial data loading after view is added to page."""
        load_clients_data()

    def dispose():
        """Clean up subscriptions and resources."""
        logger.debug("Disposing clients view")
        # No subscriptions to clean up currently

    return clients_container, dispose, setup_subscriptions