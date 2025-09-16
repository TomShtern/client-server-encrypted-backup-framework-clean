#!/usr/bin/env python3
"""
Server-Mediated Clients View - Framework Harmonious Implementation
This demonstrates server-mediated operations through state manager with reactive UI updates.
"""

# Standard library imports
import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

# Third-party imports
import flet as ft

# Local imports
from utils.async_helpers import async_event_handler
from utils.debug_setup import get_logger
from utils.user_feedback import show_confirmation, show_info, show_success_message, show_error_message, show_info_message
from utils.server_bridge import ServerBridge
from config import get_status_color
from theme import setup_modern_theme, SHADOW_STYLES, DARK_SHADOW_STYLES
from utils.ui_components import create_modern_card, apply_advanced_table_effects, create_status_chip
from utils.state_manager import StateManager
from utils.server_mediated_operations import create_server_mediated_operations

logger = get_logger(__name__)

def create_clients_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    state_manager: StateManager
) -> ft.Control:
    """Create server-mediated clients view with reactive UI updates."""
    logger.info("Creating server-mediated clients view with reactive state management")

    # Comment 8: Add server availability status note
    server_status_note = None
    if not server_bridge:
        server_status_note = "Server unavailable—running in mock mode."

    # Local UI state (not data state - that's managed by state_manager)
    ui_state = {
        "search_query": "",
        "status_filter": "all",
        "connection_filter": "all"
    }

    # Control references for reactive UI updates
    search_field_ref = ft.Ref[ft.TextField]()
    feedback_text_ref = ft.Ref[ft.Text]()
    loading_indicator_ref = ft.Ref[ft.ProgressBar]()
    add_client_dialog_ref = ft.Ref[ft.AlertDialog]()
    clients_table_ref = ft.Ref[ft.DataTable]()

    # Professional DataTable with responsive design and modern appearance
    # Column width ratios: ID(10%), Name(25%), Status(15%), Last Seen(20%), Files(15%), Actions(15%)
    clients_table = ft.DataTable(
        ref=clients_table_ref,
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
            ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
            ft.DataColumn(ft.Text("Last Seen", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
            ft.DataColumn(ft.Text("Files", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.PRIMARY))
        ],
        rows=[],
        heading_row_color=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
        border=ft.border.all(3, ft.Colors.PRIMARY),
        border_radius=20,  # Modern appearance
        data_row_min_height=70,  # Comfortable desktop viewing
        show_checkbox_column=False,
        bgcolor=ft.Colors.SURFACE,
        divider_thickness=1
    )

    # Feedback text and loading indicator
    feedback_text = ft.Text("Loading clients...", size=14, color=ft.Colors.ON_SURFACE, ref=feedback_text_ref)
    loading_indicator = ft.ProgressBar(visible=False, ref=loading_indicator_ref)

    # Enhanced loading state management
    async def set_loading_state(operation: str, is_loading: bool):
        """Set loading state with proper UI feedback."""
        state_manager.set_loading(operation, is_loading)
        if loading_indicator_ref.current:
            loading_indicator_ref.current.visible = is_loading
            loading_indicator_ref.current.update()

    async def view_details_action(client_id: str):
        """Server-mediated view client details with reactive updates.

        Falls back to basic client data from state manager if server operation
        is unavailable. Server method availability is handled by StateManager.
        """
        logger.info(f"View details clicked for client {client_id}")

        try:
            # Enhanced loading state management
            await set_loading_state("client_details", True)
            feedback_text.value = f"Loading details for client {client_id}..."
            feedback_text.update()

            # Get client data from state
            clients_data = state_manager.get("clients", [])
            client_data = None
            for client in clients_data:
                if client.get("id") == client_id:
                    client_data = client
                    break

            if not client_data:
                show_error_message(page, f"Client {client_id} not found")
                return

            # Use server-mediated update to fetch detailed info
            result = await state_manager.server_mediated_update(
                "client_details",  # key
                client_data,       # value - fallback to basic data if server operation fails
                "get_client_details_async",  # server_operation
                client_id          # Pass client_id as argument
            )

            detailed_info = result.get('data') if result.get('success') else client_data

            # Create detailed view dialog
            details_content = ft.Column([
                ft.Text("Client Details", size=20, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text(f"ID: {detailed_info.get('id', 'N/A')}"),
                ft.Text(f"Name: {detailed_info.get('name', 'N/A')}"),
                ft.Text(f"Status: {detailed_info.get('status', 'N/A')}"),
                ft.Text(f"Last Seen: {detailed_info.get('last_seen', 'N/A')}"),
                ft.Text(f"Files Count: {detailed_info.get('files_count', 'N/A')}"),
                ft.Text(f"Total Size: {detailed_info.get('total_size', 'N/A')}"),
            ], tight=True, spacing=5)

            # Add server details if available
            if detailed_info.get('connection_time') or detailed_info.get('ip_address'):
                details_content.controls.extend([
                    ft.Divider(),
                    ft.Text("Server Information", weight=ft.FontWeight.BOLD),
                    ft.Text(f"Connection Time: {detailed_info.get('connection_time', 'N/A')}"),
                    ft.Text(f"IP Address: {detailed_info.get('ip_address', 'N/A')}"),
                    ft.Text(f"Protocol Version: {detailed_info.get('protocol_version', 'N/A')}"),
                ])

            # Show details dialog using consolidated helper
            show_info(
                page,
                f"Client {client_id} Details",
                details_content,
                width=400
            )

            feedback_text.value = f"Showing details for client {client_id}"
            feedback_text.update()

        except Exception as e:
            logger.error(f"Error showing client details: {e}")
            show_error_message(page, f"Error showing client details: {str(e)}")
        finally:
            await set_loading_state("client_details", False)

    async def disconnect_action(client_id: str):
        """Server-mediated disconnect client action with reactive updates.

        Falls back to local state updates if server operation is unavailable.
        Server method availability is handled by StateManager.
        """
        logger.info(f"Disconnect clicked for client {client_id}")

        async def confirm_disconnect_async(e):
            try:
                # Enhanced loading state management
                await set_loading_state("client_disconnect", True)
                feedback_text.value = f"Disconnecting client {client_id}..."
                feedback_text.update()

                # Use server-mediated update for disconnect operation
                disconnect_data = {
                    "client_id": client_id,
                    "action": "disconnect",
                    "timestamp": datetime.now().isoformat()
                }

                result = await state_manager.server_mediated_update(
                    "client_action",           # key
                    disconnect_data,           # value
                    "disconnect_client_async", # server_operation
                    client_id                  # Pass client_id as argument
                )

                if result.get('success'):
                    # Get updated clients list after disconnect
                    await load_clients_data()

                    # Update specific client in state
                    await state_manager.update_async("client_disconnected", {
                        "client_id": client_id,
                        "timestamp": datetime.now().isoformat()
                    })

                    show_success_message(page, f"Client {client_id} disconnected successfully")
                    feedback_text.value = f"Client {client_id} disconnected successfully"
                    logger.info(f"Client {client_id} successfully disconnected via server")
                else:
                    # Fallback: update local state directly if server operation fails
                    clients_data = state_manager.get("clients", [])
                    updated_clients = []

                    for client in clients_data:
                        if client.get("id") == client_id:
                            updated_client = client.copy()
                            updated_client["status"] = "Disconnected"
                            updated_client["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            updated_clients.append(updated_client)
                            logger.info(f"Client {client_id} disconnected (fallback mode)")
                        else:
                            updated_clients.append(client)

                    # Update clients state with modified data
                    await state_manager.update_async("clients", updated_clients, source="disconnect_fallback")

                    show_success_message(page, f"Client {client_id} disconnected successfully (fallback mode)")
                    feedback_text.value = f"Client {client_id} disconnected (fallback mode)"

            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
                show_error_message(page, f"Error disconnecting client: {str(e)}")
                feedback_text.value = f"Failed to disconnect client {client_id}"
            finally:
                await set_loading_state("client_disconnect", False)

        def confirm_disconnect(e):
            """Wrapper to run async disconnect in a task"""
            page.run_task(confirm_disconnect_async, e)

        # Show confirmation dialog using consolidated helper
        show_confirmation(
            page,
            "Confirm Disconnect",
            f"Are you sure you want to disconnect client {client_id}?\n\nThis action cannot be undone.",
            confirm_disconnect,
            confirm_text="Disconnect",
            is_destructive=True
        )

    # get_status_color function moved to utils/ui_patterns.py for reuse

    def filter_clients():
        """Filter clients based on search query and status filter - uses state manager data."""
        # Get clients from state manager instead of local variable
        clients_data = state_manager.get("clients", [])
        if not clients_data:
            return []

        filtered = clients_data.copy()

        # Apply search filter
        if ui_state["search_query"].strip():
            query_lower = ui_state["search_query"].lower()
            filtered = [
                client for client in filtered
                if (query_lower in str(client.get("id", "")).lower() or
                    query_lower in str(client.get("name", "")).lower() or
                    query_lower in str(client.get("status", "")).lower())
            ]

        # Apply status filter
        if ui_state["status_filter"] != "all":
            filtered = [
                client for client in filtered
                if str(client.get("status", "")).lower() == ui_state["status_filter"].lower()
            ]

        return filtered

    def update_table():
        """Professional DataTable update with clean styling."""
        filtered_clients = filter_clients()

        # Clear existing rows
        clients_table.rows.clear()

        # Populate DataTable rows with clean cell structure
        for client in filtered_clients:
            status = client.get("status", "Unknown")

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(client.get("id", "Unknown")), size=13)),
                    ft.DataCell(ft.Text(str(client.get("name", "Unknown")), size=13, weight=ft.FontWeight.W_500)),
                    ft.DataCell(create_status_chip(status)),
                    ft.DataCell(ft.Text(str(client.get("last_seen", "Unknown")), size=13)),
                    ft.DataCell(ft.Text(str(client.get("files_count", "0")), size=13)),
                    ft.DataCell(
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            tooltip="Client Actions",
                            icon_color=ft.Colors.PRIMARY,
                            items=[
                                ft.PopupMenuItem(
                                    text="View Details",
                                    icon=ft.Icons.INFO,
                                    on_click=lambda e, client_id=client.get("id"): page.run_task(view_details_action, client_id)
                                ),
                                ft.PopupMenuItem(
                                    text="Disconnect",
                                    icon=ft.Icons.LOGOUT,
                                    on_click=lambda e, client_id=client.get("id"): page.run_task(disconnect_action, client_id)
                                ),
                                ft.PopupMenuItem(
                                    text="Delete",
                                    icon=ft.Icons.DELETE,
                                    on_click=lambda e, client_id=client.get("id"): show_delete_confirmation(client_id)
                                )
                            ]
                        )
                    )
                ]
            )

            clients_table.rows.append(row)

        # Update DataTable efficiently with proper safety checks
        try:
            if clients_table_ref.current is not None and hasattr(clients_table_ref.current, 'page') and clients_table_ref.current.page is not None:
                clients_table_ref.current.update()
            elif hasattr(clients_table, 'page') and clients_table.page is not None:
                clients_table.update()
            else:
                logger.debug("Skipping DataTable update - control not attached to page yet")
        except Exception as e:
            logger.warning(f"Failed to update DataTable: {e}")
            # Skip update to prevent errors - the table will be updated when properly attached

        logger.debug(f"DataTable updated with {len(filtered_clients)} rows")

    async def update_table_async():
        """Async version of update_table for consistent async patterns."""
        # This is primarily a UI update function, so we just add async consistency
        # and allow other async operations to run during processing
        filtered_clients = filter_clients()

        # Clear existing rows
        clients_table.rows.clear()

        # Populate DataTable rows with clean cell structure
        for client in filtered_clients:
            status = client.get("status", "Unknown")

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(client.get("id", "Unknown")), size=13)),
                    ft.DataCell(ft.Text(str(client.get("name", "Unknown")), size=13, weight=ft.FontWeight.W_500)),
                    ft.DataCell(create_status_chip(status)),
                    ft.DataCell(ft.Text(str(client.get("last_seen", "Unknown")), size=13)),
                    ft.DataCell(ft.Text(str(client.get("files_count", "0")), size=13)),
                    ft.DataCell(
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            tooltip="Client Actions",
                            icon_color=ft.Colors.PRIMARY,
                            items=[
                                ft.PopupMenuItem(
                                    text="View Details",
                                    icon=ft.Icons.INFO,
                                    on_click=lambda e, client_id=client.get("id"): page.run_task(view_details_action, client_id)
                                ),
                                ft.PopupMenuItem(
                                    text="Disconnect",
                                    icon=ft.Icons.LOGOUT,
                                    on_click=lambda e, client_id=client.get("id"): page.run_task(disconnect_action, client_id)
                                ),
                                ft.PopupMenuItem(
                                    text="Delete",
                                    icon=ft.Icons.DELETE,
                                    on_click=lambda e, client_id=client.get("id"): show_delete_confirmation(client_id)
                                )
                            ]
                        )
                    )
                ]
            )

            clients_table.rows.append(row)
            # Allow other async operations to run during large table updates
            await asyncio.sleep(0)

        # Update DataTable efficiently with proper safety checks
        try:
            if clients_table_ref.current is not None and hasattr(clients_table_ref.current, 'page') and clients_table_ref.current.page is not None:
                clients_table_ref.current.update()
            elif hasattr(clients_table, 'page') and clients_table.page is not None:
                clients_table.update()
            else:
                logger.debug("Skipping DataTable update - control not attached to page yet")
        except Exception as e:
            logger.warning(f"Failed to update DataTable: {e}")
            # Skip update to prevent errors - the table will be updated when properly attached

        logger.debug(f"DataTable updated with {len(filtered_clients)} rows (async)")

    # Responsive update function for reactive UI updates
    def update_clients_display(new_clients_data, old_clients_data):
        """Reactive callback for clients state changes with responsive table update."""
        logger.debug(f"Clients state changed: {len(new_clients_data) if new_clients_data else 0} clients")
        # Use page.run_task for async version in sync callback context
        page.run_task(update_table_async)

        # Update feedback text
        clients_count = len(new_clients_data) if new_clients_data else 0
        if feedback_text_ref.current:
            feedback_text_ref.current.value = f"Showing {clients_count} clients"
            feedback_text_ref.current.update()
        else:
            # Fallback if reference is not available
            feedback_text.value = f"Showing {clients_count} clients"
            feedback_text.update()

    # Legacy callback for backward compatibility
    def on_clients_state_changed(new_clients_data, old_clients_data):
        """React to clients state changes by delegating to update_clients_display."""
        update_clients_display(new_clients_data, old_clients_data)

    def get_mock_data():
        """Generate mock client data for testing."""
        return [
            {
                "id": "client-001",
                "name": "Desktop-PC-01",
                "status": "Connected",
                "last_seen": "2025-09-07 17:05:23",
                "files_count": "15",
                "total_size": "2.4 MB"
            },
            {
                "id": "client-002",
                "name": "Laptop-User-02",
                "status": "Disconnected",
                "last_seen": "2025-09-07 16:30:15",
                "files_count": "8",
                "total_size": "1.1 MB"
            },
            {
                "id": "client-003",
                "name": "Server-Backup-03",
                "status": "Connecting",
                "last_seen": "2025-09-07 17:08:45",
                "files_count": "42",
                "total_size": "15.7 MB"
            },
            {
                "id": "client-004",
                "name": "Mobile-Device-04",
                "status": "Connected",
                "last_seen": "2025-09-07 17:10:12",
                "files_count": "23",
                "total_size": "5.8 MB"
            },
            {
                "id": "client-005",
                "name": "WorkStation-05",
                "status": "Disconnected",
                "last_seen": "2025-09-07 15:45:33",
                "files_count": "67",
                "total_size": "125.3 MB"
            },
            {
                "id": "client-006",
                "name": "Gaming-Rig-06",
                "status": "Connected",
                "last_seen": "2025-09-07 17:11:45",
                "files_count": "156",
                "total_size": "2.8 GB"
            },
            {
                "id": "client-007",
                "name": "Office-Terminal-07",
                "status": "Connecting",
                "last_seen": "2025-09-07 17:12:01",
                "files_count": "34",
                "total_size": "18.9 MB"
            },
            {
                "id": "client-008",
                "name": "Home-Server-08",
                "status": "Connected",
                "last_seen": "2025-09-07 17:07:28",
                "files_count": "892",
                "total_size": "15.2 GB"
            },
            {
                "id": "client-009",
                "name": "Tablet-Device-09",
                "status": "Disconnected",
                "last_seen": "2025-09-07 14:22:16",
                "files_count": "12",
                "total_size": "3.7 MB"
            },
            {
                "id": "client-010",
                "name": "Backup-Node-10",
                "status": "Connected",
                "last_seen": "2025-09-07 17:12:15",
                "files_count": "445",
                "total_size": "8.9 GB"
            }
        ]

    async def load_clients_data():
        """Server-mediated load client data with reactive state updates."""
        try:
            # Enhanced loading state management
            await set_loading_state("clients", True)

            # Use server-mediated update to load clients
            result = await state_manager.server_mediated_update(
                "clients",            # key
                get_mock_data(),      # value - fallback data
                "get_clients_async"   # server_operation - no additional arguments needed
            )

            if result.get('success'):
                logger.info(f"Clients loaded successfully via server: {len(result.get('data', []))} clients")
            else:
                logger.warning("Using fallback client data")

        except Exception as e:
            logger.error(f"Failed to load client data: {e}")
            # Ensure fallback data is available
            await state_manager.update_async("clients", get_mock_data(), source="error_fallback")
        finally:
            await set_loading_state("clients", False)

    async def on_search_change(e):
        """Handle search field changes - reactive filtering (async)."""
        ui_state["search_query"] = e.control.value
        logger.info(f"Search query changed to: '{ui_state['search_query']}'")
        await update_table_async()  # Reactive update based on current state

    async def on_status_filter_change(e):
        """Handle status filter changes - reactive filtering (async)."""
        ui_state["status_filter"] = e.control.value
        logger.info(f"Status filter changed to: '{ui_state['status_filter']}'")
        await update_table_async()  # Reactive update based on current state

    async def on_refresh_click(e):
        """Server-mediated refresh with loading state management."""
        logger.info("Refreshing clients list via server-mediated update")
        feedback_text.value = "Refreshing clients list..."
        feedback_text.update()

        await load_clients_data()
        show_info_message(page, "Clients list refreshed successfully")

    # Loading state change handler
    def on_loading_state_changed(new_loading_states, old_loading_states):
        """React to loading state changes."""
        is_loading = new_loading_states.get("clients", False)
        if loading_indicator_ref.current:
            loading_indicator_ref.current.visible = is_loading
            loading_indicator_ref.current.update()

    async def add_client_action(client_data: Dict[str, Any]):
        """Server-mediated add client operation with local fallback.

        Falls back to local state updates if server operation is unavailable.
        Server method availability is handled by StateManager.
        """
        try:
            # Enhanced loading state management
            await set_loading_state("client_add", True)
            feedback_text.value = f"Adding client {client_data.get('name', 'Unknown')}..."
            feedback_text.update()

            # Use server-mediated update with client_data as argument
            result = await state_manager.server_mediated_update(
                "client_add",     # key
                client_data,      # value
                "add_client_async", # server_operation
                client_data       # Pass client_data as argument
            )

            if result.get('success'):
                # Reload clients list after successful add
                await load_clients_data()
                show_success_message(page, f"Client {client_data.get('name')} added successfully")
                feedback_text.value = f"Client {client_data.get('name')} added successfully"
            else:
                # Local fallback: add to local state when server method is missing
                if "method not found" in str(result.get('error', '')).lower() or "not available" in str(result.get('error', '')).lower():
                    # Add to local state as fallback
                    clients_data = state_manager.get("clients", [])
                    updated_clients = clients_data.copy()
                    updated_clients.append(client_data)

                    # Update clients state with new client
                    await state_manager.update_async("clients", updated_clients, source="add_fallback")

                    show_success_message(page, f"Client {client_data.get('name')} added successfully (mock mode)")
                    feedback_text.value = f"Client {client_data.get('name')} added (mock mode)"
                    logger.info(f"Client {client_data.get('name')} added via local fallback")
                else:
                    show_error_message(page, f"Failed to add client: {result.get('error', 'Unknown error')}")
                    feedback_text.value = f"Failed to add client {client_data.get('name')}"

        except Exception as e:
            logger.error(f"Error adding client: {e}")
            show_error_message(page, f"Error adding client: {str(e)}")
            feedback_text.value = f"Error adding client"
        finally:
            await set_loading_state("client_add", False)

    async def delete_client_action(client_id: str):
        """Server-mediated delete client operation.

        Falls back to error handling if server operation is unavailable.
        Server method availability is handled by StateManager.
        """
        try:
            # Enhanced loading state management
            await set_loading_state("client_delete", True)
            feedback_text.value = f"Deleting client {client_id}..."
            feedback_text.update()

            # Use server-mediated update with delete_client (non-async) and client_id argument
            result = await state_manager.server_mediated_update(
                "client_delete",  # key
                {"client_id": client_id, "action": "delete"},  # value
                "delete_client",  # server_operation (non-async)
                client_id         # Pass client_id as argument
            )

            if result.get('success'):
                # Reload clients list after successful delete
                await load_clients_data()
                show_success_message(page, f"Client {client_id} deleted successfully")
                feedback_text.value = f"Client {client_id} deleted successfully"
            else:
                show_error_message(page, f"Failed to delete client: {result.get('error', 'Unknown error')}")
                feedback_text.value = f"Failed to delete client {client_id}"

        except Exception as e:
            logger.error(f"Error deleting client: {e}")
            show_error_message(page, f"Error deleting client: {str(e)}")
            feedback_text.value = f"Error deleting client"
        finally:
            await set_loading_state("client_delete", False)

    def show_delete_confirmation(client_id: str):
        """Show delete confirmation dialog for client."""
        async def confirm_delete_async(e):
            await delete_client_action(client_id)

        def confirm_delete(e):
            page.run_task(confirm_delete_async, e)

        show_confirmation(
            page,
            "Confirm Delete",
            f"Are you sure you want to delete client {client_id}?\n\nThis action cannot be undone and will permanently remove all client data.",
            confirm_delete,
            confirm_text="Delete",
            is_destructive=True
        )

    def show_add_client_dialog():
        """Show add client dialog with form fields."""
        name_field = ft.TextField(label="Client Name", hint_text="Enter client name")
        ip_field = ft.TextField(label="IP Address", hint_text="Enter IP address")
        status_dropdown = ft.Dropdown(
            label="Initial Status",
            value="Disconnected",
            options=[
                ft.dropdown.Option("Connected", "Connected"),
                ft.dropdown.Option("Disconnected", "Disconnected"),
                ft.dropdown.Option("Connecting", "Connecting")
            ]
        )

        async def submit_add_client(e):
            if not name_field.value or not name_field.value.strip():
                show_error_message(page, "Client name is required")
                return

            # Generate unique client ID
            client_id = f"client-{str(uuid.uuid4())[:8]}"

            client_data = {
                "id": client_id,
                "name": name_field.value.strip(),
                "ip_address": ip_field.value.strip() if ip_field.value else "Unknown",
                "status": status_dropdown.value,
                "files_count": "0",
                "total_size": "0 MB",
                "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # Close dialog
            if add_client_dialog_ref.current:
                add_client_dialog_ref.current.open = False
                add_client_dialog_ref.current.update()

            await add_client_action(client_data)

        def on_submit(e):
            page.run_task(submit_add_client, e)

        def on_cancel(e):
            if add_client_dialog_ref.current:
                add_client_dialog_ref.current.open = False
                add_client_dialog_ref.current.update()

        # Create and show dialog
        dialog = ft.AlertDialog(
            ref=add_client_dialog_ref,
            modal=True,
            title=ft.Text("Add New Client"),
            content=ft.Column([
                name_field,
                ip_field,
                status_dropdown
            ], tight=True, spacing=16),
            actions=[
                ft.TextButton("Cancel", on_click=on_cancel),
                ft.FilledButton("Add Client", on_click=on_submit)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        # Comment 1: Avoid page.update() after overlay.append()
        # Use dialog-specific update pattern for Flet 0.28.3 compatibility
        page.overlay.append(dialog)
        dialog.open = True
        try:
            if hasattr(dialog, 'page') and dialog.page is not None:
                dialog.update()  # Update dialog directly instead of full page
            else:
                page.update()  # Fallback to page update if dialog not attached
        except Exception as e:
            logger.warning(f"Dialog update failed: {e}, using page update fallback")
            page.update()

    # Responsive table container with sophisticated shadow
    def create_responsive_table_container():
        """Create responsive table container with proper scaling and modern styling."""
        return ft.Container(
            content=clients_table,
            expand=True,
            shadow=SHADOW_STYLES["elevated"],  # Sophisticated shadow from theme system
            bgcolor=ft.Colors.SURFACE,
            border_radius=20,  # Match table border radius
            padding=0  # No padding for table - let DataTable handle its own spacing
        )

    # Build the main UI with responsive layout
    main_view = ft.ResponsiveRow([
        ft.Column(
            [
                # Header section with responsive controls
                ft.ResponsiveRow([
                    ft.Column([
                        create_modern_card(
                            content=ft.Row([
                                ft.Text("Client Management", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                                ft.Container(expand=True),  # Spacer
                                ft.Row([
                                    ft.TextField(
                                        label="Search clients...",
                                        hint_text="Search by ID, name, or status...",
                                        prefix_icon=ft.Icons.SEARCH,
                                        width=300,
                                        on_change=on_search_change,
                                        ref=search_field_ref,
                                        border_color=ft.Colors.OUTLINE,
                                        focused_border_color=ft.Colors.PRIMARY
                                    ),
                                    ft.Dropdown(
                                        label="Status Filter",
                                        value="all",
                                        options=[
                                            ft.dropdown.Option("all", "All Statuses"),
                                            ft.dropdown.Option("connected", "Connected"),
                                            ft.dropdown.Option("disconnected", "Disconnected"),
                                            ft.dropdown.Option("connecting", "Connecting")
                                        ],
                                        width=150,
                                        on_change=on_status_filter_change,
                                        border_color=ft.Colors.OUTLINE,
                                        focused_border_color=ft.Colors.PRIMARY
                                    ),
                                    ft.FilledButton(
                                        "Add Client",
                                        icon=ft.Icons.ADD,
                                        on_click=lambda e: show_add_client_dialog(),
                                        bgcolor=ft.Colors.PRIMARY,
                                        color=ft.Colors.ON_PRIMARY
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.REFRESH,
                                        tooltip="Refresh Clients",
                                        on_click=lambda e: page.run_task(on_refresh_click, e),
                                        icon_color=ft.Colors.PRIMARY,
                                        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY)
                                    )
                                ], spacing=10)
                            ]),
                            elevation="soft",
                            padding=32,
                            return_type="container"
                        )
                    ], col={"sm": 12, "md": 12, "lg": 12})
                ]),

                # Feedback section with responsive padding
                ft.ResponsiveRow([
                    ft.Column([
                        create_modern_card(
                            content=ft.Column([
                                ft.Text(server_status_note, color=ft.Colors.ORANGE_600) if server_status_note else ft.Container(height=0),
                                feedback_text,
                                loading_indicator
                            ], spacing=8, tight=True),
                            elevation="soft",
                            padding=24,
                            return_type="container"
                        )
                    ], col={"sm": 12, "md": 12, "lg": 12})
                ]),

                # Responsive table section with proper scaling
                ft.ResponsiveRow([
                    ft.Column([
                        ft.Column(
                            controls=[create_responsive_table_container()],
                            scroll=ft.ScrollMode.AUTO,
                            expand=True
                        )
                    ], col={"sm": 12, "md": 12, "lg": 12}, expand=True)
                ])
            ],
            expand=True,
            spacing=20
        )
    ], col={"xs": 12, "sm": 12, "md": 12, "lg": 12}, expand=True)

    # Legacy layout structure for backward compatibility
    legacy_view = ft.Column([
        # Header with title and refresh button
        create_modern_card(
            content=ft.Row([
                ft.Text("Client Management", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                ft.Container(expand=True),  # Spacer
                ft.Row([
                    ft.TextField(
                        label="Search clients...",
                        hint_text="Search by ID, name, or status...",
                        prefix_icon=ft.Icons.SEARCH,
                        width=300,
                        on_change=on_search_change,
                        ref=search_field_ref,
                        border_color=ft.Colors.OUTLINE,
                        focused_border_color=ft.Colors.PRIMARY
                    ),
                    ft.Dropdown(
                        label="Status Filter",
                        value="all",
                        options=[
                            ft.dropdown.Option("all", "All Statuses"),
                            ft.dropdown.Option("connected", "Connected"),
                            ft.dropdown.Option("disconnected", "Disconnected"),
                            ft.dropdown.Option("connecting", "Connecting")
                        ],
                        width=150,
                        on_change=on_status_filter_change,
                        border_color=ft.Colors.OUTLINE,
                        focused_border_color=ft.Colors.PRIMARY
                    ),
                    ft.FilledButton(
                        "Add Client",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: show_add_client_dialog(),
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh Clients",
                        on_click=lambda e: page.run_task(on_refresh_click, e),
                        icon_color=ft.Colors.PRIMARY,
                        bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY)
                    )
                ], spacing=10)
            ]),
            elevation="soft",
            padding=32,
            return_type="container"
        ),

        # Action Feedback and Loading Indicator (wrapped in modern card)
        create_modern_card(
            content=ft.Column([
                ft.Text(server_status_note, color=ft.Colors.ORANGE_600) if server_status_note else ft.Container(height=0),
                feedback_text,
                loading_indicator
            ], spacing=8, tight=True),
            elevation="soft",
            padding=24,
            return_type="container"
        ),

        # Clients table - DataTable wrapped in scrollable column with modern card styling
        ft.Column(
            controls=[create_responsive_table_container()],
            scroll=ft.ScrollMode.AUTO,
            expand=True
        )
    ], expand=True)

    # Enhanced subscription setup with reactive updates
    async def setup_subscriptions():
        """Set up state subscriptions with enhanced reactive UI updates."""
        await asyncio.sleep(0.1)  # Small delay to ensure page attachment

        # Set up reactive subscriptions using both callback functions
        state_manager.subscribe("clients", update_clients_display, control=clients_table)
        state_manager.subscribe("loading_states", on_loading_state_changed, control=loading_indicator)

        # Create async wrapper for update_clients_display since it's synchronous
        async def async_update_clients_display(new_clients_data, old_clients_data):
            """Async wrapper for the synchronous update_clients_display function."""
            update_clients_display(new_clients_data, old_clients_data)

        # Add async subscription for real-time client updates if available
        try:
            state_manager.subscribe_async("clients", async_update_clients_display)
        except AttributeError:
            logger.debug("Async subscriptions not available, using standard subscriptions")

        # Trigger initial data load after subscriptions are safely set up
        await load_clients_data()

    # Start subscription setup in background
    page.run_task(setup_subscriptions)

    # Return responsive layout as primary, with fallback detection
    try:
        # Test if ResponsiveRow is properly supported
        test_responsive = ft.ResponsiveRow([ft.Container()])
        return main_view  # Use responsive layout
    except Exception as e:
        logger.warning(f"ResponsiveRow not fully supported, using legacy layout: {e}")
        return legacy_view  # Fallback to legacy layout
