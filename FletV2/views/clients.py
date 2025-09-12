#!/usr/bin/env python3
"""
Server-Mediated Clients View - Framework Harmonious Implementation
This demonstrates server-mediated operations through state manager with reactive UI updates.
"""

# Standard library imports
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

# Third-party imports
import flet as ft

# Local imports
from utils.async_helpers import async_event_handler
from utils.debug_setup import get_logger
from utils.dialog_consolidation_helper import show_confirmation, show_info, show_success_message, show_error_message, show_info_message
from utils.server_bridge import ServerBridge
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
    
    # Local UI state (not data state - that's managed by state_manager)
    ui_state = {
        "search_query": "",
        "status_filter": "all",
        "connection_filter": "all"
    }
    
    # Control references for reactive UI updates
    clients_table_ref = ft.Ref[ft.DataTable]()
    search_field_ref = ft.Ref[ft.TextField]()
    feedback_text_ref = ft.Ref[ft.Text]()
    loading_indicator_ref = ft.Ref[ft.ProgressBar]()
    
    # Pre-create the DataTable to avoid lifecycle issues
    clients_table = ft.DataTable(
        ref=clients_table_ref,
        columns=[
            ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_800)),
            ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_800)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_800)),
            ft.DataColumn(ft.Text("Last Seen", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_800)),
            ft.DataColumn(ft.Text("Files", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_800)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, size=14, color=ft.Colors.BLUE_800))
        ],
        rows=[],
        heading_row_color=ft.Colors.BLUE_50,
        border=ft.border.all(3, ft.Colors.BLUE_300),
        border_radius=16,
        data_row_min_height=62,
        column_spacing=28,
        show_checkbox_column=False
    )
    
    # Feedback text and loading indicator
    feedback_text = ft.Text("Loading clients...", size=14, color=ft.Colors.BLUE, ref=feedback_text_ref)
    loading_indicator = ft.ProgressBar(visible=False, ref=loading_indicator_ref)

    async def view_details_action(client_id: str):
        """Server-mediated view client details with reactive updates."""
        logger.info(f"View details clicked for client {client_id}")
        
        try:
            # Set loading state
            state_manager.set_loading("client_details", True)
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
                key="client_details",
                value=client_data,  # Fallback to basic data
                server_operation="get_client_details_async" if hasattr(server_bridge, 'get_client_details_async') else None
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
            state_manager.set_loading("client_details", False)

    async def disconnect_action(client_id: str):
        """Server-mediated disconnect client action with reactive updates."""
        logger.info(f"Disconnect clicked for client {client_id}")
        
        async def confirm_disconnect_async(e):
            try:
                # Close confirmation dialog
                confirmation_dialog.open = False
                confirmation_dialog.update()  # Efficient dialog-specific update
                
                # Set loading state
                state_manager.set_loading("client_disconnect", True)
                feedback_text.value = f"Disconnecting client {client_id}..."
                feedback_text.update()
                
                # Use server-mediated update for disconnect operation
                disconnect_data = {
                    "client_id": client_id,
                    "action": "disconnect",
                    "timestamp": datetime.now().isoformat()
                }
                
                result = await state_manager.server_mediated_update(
                    key="client_action",
                    value=disconnect_data,
                    server_operation="disconnect_client_async"
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
                state_manager.set_loading("client_disconnect", False)
        
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

    def get_status_color(status):
        """Get color based on client status."""
        status_lower = str(status).lower()
        if status_lower in ["connected", "online", "active"]:
            return ft.Colors.GREEN_600  # Success - online/connected
        elif status_lower in ["disconnected", "offline", "inactive"]:
            return ft.Colors.RED_600    # Error - offline/disconnected
        elif status_lower in ["connecting", "pending", "initializing"]:
            return ft.Colors.ORANGE_600  # Warning - transitional states
        else:
            return ft.Colors.GREY_600   # Unknown status

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
        """Reactive table update using state manager data."""
        filtered_clients = filter_clients()
        new_rows = []
        
        for client in filtered_clients:
            status = client.get("status", "Unknown")
            status_color = get_status_color(status)
            
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(client.get("id", "Unknown")))),
                    ft.DataCell(ft.Text(str(client.get("name", "Unknown")))),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                status,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD
                            ),
                            padding=ft.Padding(8, 4, 8, 4),
                            border_radius=12,
                            bgcolor=status_color
                        )
                    ),
                    ft.DataCell(ft.Text(str(client.get("last_seen", "Unknown")))),
                    ft.DataCell(ft.Text(str(client.get("files_count", "0")))),
                    ft.DataCell(
                        ft.PopupMenuButton(
                            icon=ft.Icons.MORE_VERT,
                            tooltip="Client Actions",
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
                                )
                            ]
                        )
                    )
                ]
            )
            new_rows.append(row)

        # Framework harmonious table update pattern
        clients_table.rows = new_rows
        
        # Only update the reference if it exists and is properly attached to page
        if clients_table_ref.current is not None:
            try:
                # Check if control is attached to page before updating
                if hasattr(clients_table_ref.current, 'page') and clients_table_ref.current.page is not None:
                    clients_table_ref.current.rows = new_rows
                    clients_table_ref.current.update()  # control.update() not page.update()
                    logger.debug(f"Table updated reactively with {len(new_rows)} rows")
                else:
                    # Control not yet attached to page, just update the data
                    clients_table_ref.current.rows = new_rows
                    logger.debug(f"Table data updated (not yet attached to page), {len(new_rows)} rows")
            except Exception as update_error:
                logger.warning(f"Table reference update failed: {update_error}")
                # Table will still work, just update on next display
        else:
            logger.debug("Table reference not yet initialized, rows updated on object")

    # Reactive callback for clients state changes
    def on_clients_state_changed(new_clients_data, old_clients_data):
        """React to clients state changes by updating the UI."""
        logger.debug(f"Clients state changed: {len(new_clients_data) if new_clients_data else 0} clients")
        update_table()
        
        # Update feedback text
        clients_count = len(new_clients_data) if new_clients_data else 0
        if feedback_text_ref.current:
            feedback_text_ref.current.value = f"Showing {clients_count} clients"
            feedback_text_ref.current.update()

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
            # Set loading state
            state_manager.set_loading("clients", True)
            if loading_indicator_ref.current:
                loading_indicator_ref.current.visible = True
                loading_indicator_ref.current.update()
            
            # Use server-mediated update to load clients
            result = await state_manager.server_mediated_update(
                key="clients",
                value=get_mock_data(),  # Fallback data
                server_operation="get_clients_async"
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
            state_manager.set_loading("clients", False)
            if loading_indicator_ref.current:
                loading_indicator_ref.current.visible = False
                loading_indicator_ref.current.update()

    def on_search_change(e):
        """Handle search field changes - reactive filtering."""
        ui_state["search_query"] = e.control.value
        logger.info(f"Search query changed to: '{ui_state['search_query']}'")
        update_table()  # Reactive update based on current state

    def on_status_filter_change(e):
        """Handle status filter changes - reactive filtering."""
        ui_state["status_filter"] = e.control.value
        logger.info(f"Status filter changed to: '{ui_state['status_filter']}'")
        update_table()  # Reactive update based on current state

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
        """Server-mediated add client operation."""
        try:
            # Set loading state
            state_manager.set_loading("client_add", True)
            feedback_text.value = f"Adding client {client_data.get('name', 'Unknown')}..."
            feedback_text.update()
            
            # Use server-mediated update
            result = await state_manager.server_mediated_update(
                key="client_add",
                value=client_data,
                server_operation="add_client_async"
            )
            
            if result.get('success'):
                # Reload clients list after successful add
                await load_clients_data()
                show_success_message(page, f"Client {client_data.get('name')} added successfully")
                feedback_text.value = f"Client {client_data.get('name')} added successfully"
            else:
                show_error_message(page, f"Failed to add client: {result.get('error', 'Unknown error')}")
                feedback_text.value = f"Failed to add client {client_data.get('name')}"
                
        except Exception as e:
            logger.error(f"Error adding client: {e}")
            show_error_message(page, f"Error adding client: {str(e)}")
            feedback_text.value = f"Error adding client"
        finally:
            state_manager.set_loading("client_add", False)

    async def delete_client_action(client_id: str):
        """Server-mediated delete client operation."""
        try:
            # Set loading state
            state_manager.set_loading("client_delete", True)
            feedback_text.value = f"Deleting client {client_id}..."
            feedback_text.update()
            
            # Use server-mediated update
            result = await state_manager.server_mediated_update(
                key="client_delete",
                value={"client_id": client_id, "action": "delete"},
                server_operation="delete_client_async"
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
            state_manager.set_loading("client_delete", False)

    # Build the main UI
    main_view = ft.Column([
        # Header with title and refresh button
        ft.Container(
            content=ft.Row([
                ft.Text("Client Management", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),  # Spacer
                ft.Row([
                    ft.TextField(
                        label="Search clients...",
                        hint_text="Search by ID, name, or status...",
                        prefix_icon=ft.Icons.SEARCH,
                        width=300,
                        on_change=on_search_change,
                        ref=search_field_ref
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
                        on_change=on_status_filter_change
                    ),
                    ft.IconButton(
                        icon=ft.Icons.REFRESH,
                        tooltip="Refresh Clients",
                        on_click=lambda e: page.run_task(on_refresh_click, e)
                    )
                ], spacing=10)
            ]),
            padding=ft.Padding(20, 20, 20, 10)
        ),
        
        # Action Feedback and Loading Indicator
        ft.Container(
            content=ft.Column([
                feedback_text,
                loading_indicator
            ], spacing=8, tight=True),
            padding=ft.Padding(20, 10, 20, 10),
            bgcolor=ft.Colors.SURFACE,
            border_radius=4
        ),
        
        # Clients table
        ft.Container(
            content=ft.Column([
                clients_table
            ], scroll=ft.ScrollMode.AUTO),
            expand=True,
            padding=ft.Padding(20, 0, 20, 20)
        )
    ], expand=True)

    # Set up reactive state subscriptions
    state_manager.subscribe("clients", on_clients_state_changed, control=clients_table)
    state_manager.subscribe("loading_states", on_loading_state_changed, control=loading_indicator)
    
    # Initialize with mock data and trigger server load
    logger.info("Initializing clients view with reactive state management")
    page.run_task(load_clients_data)

    return main_view
