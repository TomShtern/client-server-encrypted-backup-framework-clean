#!/usr/bin/env python3
"""
Clients View for FletV2
An improved implementation using ft.UserControl for better state management.
"""

import flet as ft
import asyncio
from typing import List, Dict, Any
from utils.debug_setup import get_logger
from utils.progress_utils import ProgressIndicator, show_async_operation_feedback, hide_async_operation_feedback
from utils.logging_enhancements import log_method_call, log_async_operation, log_async_completion, log_user_action
from config import DEFAULT_PAGE_SIZE, get_status_color

logger = get_logger(__name__)


class ClientsView(ft.UserControl):
    """
    Clients view using ft.UserControl for better state management.
    """
    
    def __init__(self, server_bridge, page: ft.Page):
        super().__init__()
        self.server_bridge = server_bridge
        self.page = page
        self.all_clients_data: List[Dict[str, Any]] = []
        self.filtered_clients_data: List[Dict[str, Any]] = []
        self.search_query = ""
        self.status_filter = "all"
        self.is_loading = False
        self.last_updated = None
        self.progress_indicator = None
        
        # UI References using ft.Ref for robust access
        self.clients_table_ref = ft.Ref[ft.DataTable]()
        self.status_text_ref = ft.Ref[ft.Text]()
        self.search_field_ref = ft.Ref[ft.TextField]()
        self.filter_dropdown_ref = ft.Ref[ft.Dropdown]()
        self.last_updated_text_ref = ft.Ref[ft.Text]()
        self.connected_count_text_ref = ft.Ref[ft.Text]()
        self.registered_count_text_ref = ft.Ref[ft.Text]()
        self.offline_count_text_ref = ft.Ref[ft.Text]()
        
    def build(self):
        """Build the clients view UI."""
        logger.info("Building ClientsView UI")
        return self._create_main_layout()
    
    def _create_main_layout(self) -> ft.Column:
        """Create the main layout for the clients view."""
        return ft.Column([
            self._create_header_section(),
            ft.Divider(),
            self._create_status_overview_section(),
            ft.Divider(),
            self._create_search_and_filter_section(),
            self._create_status_section(),
            self._create_clients_table_section()
        ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=20)
    
    def _create_header_section(self) -> ft.Container:
        """Create the header section with title and refresh button."""
        return ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.PEOPLE, size=24),
                ft.Text("Client Management", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    tooltip="Refresh Clients",
                    on_click=self._on_refresh_click
                )
            ]),
            padding=ft.Padding(20, 20, 20, 10)
        )
    
    def _create_status_overview_section(self) -> ft.Container:
        """Create the client status overview cards."""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Text("Client Status Overview", size=18, weight=ft.FontWeight.BOLD),
                    padding=ft.Padding(20, 0, 20, 10)
                ),
                ft.Container(
                    content=ft.ResponsiveRow([
                        self._create_status_card("Connected", ft.Icons.CONNECT_WITHOUT_CONTACT, ft.Colors.GREEN, 0, self.connected_count_text_ref),
                        self._create_status_card("Registered", ft.Icons.PERSON_ADD, ft.Colors.ORANGE, 0, self.registered_count_text_ref),
                        self._create_status_card("Offline", ft.Icons.PERSON_OFF, ft.Colors.RED, 0, self.offline_count_text_ref)
                    ]),
                    padding=ft.Padding(20, 0, 20, 10)
                )
            ]),
            padding=ft.Padding(0, 0, 0, 10)
        )
    
    def _create_status_card(self, title: str, icon: ft.Icons, color: str, count: int, text_ref: ft.Ref) -> ft.Column:
        """Create a status card for the overview."""
        return ft.Column([
            ft.Card(content=ft.Container(
                content=ft.Column([
                    ft.Icon(icon, size=24, color=color),
                    ft.Text(title, size=12, weight=ft.FontWeight.W_500),
                    ft.Text(str(count), size=20, weight=ft.FontWeight.BOLD, ref=text_ref)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                padding=15
            ))
        ], col={"sm": 12, "md": 4})
    
    def _create_search_and_filter_section(self) -> ft.Container:
        """Create the search and filter controls section."""
        search_field = ft.TextField(
            label="Search Clients",
            hint_text="Search by client ID or address...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            on_change=self._on_search_change,
            ref=self.search_field_ref
        )
        
        filter_dropdown = ft.Dropdown(
            label="Filter by Status",
            value="all",
            options=[
                ft.dropdown.Option("all", "All Clients"),
                ft.dropdown.Option("connected", "Connected"),
                ft.dropdown.Option("registered", "Registered"), 
                ft.dropdown.Option("offline", "Offline")
            ],
            width=200,
            on_change=self._on_filter_change,
            ref=self.filter_dropdown_ref
        )
        
        return ft.Container(
            content=ft.Row([
                search_field,
                filter_dropdown
            ], spacing=20),
            padding=ft.Padding(20, 0, 20, 10)
        )
    
    def _create_status_section(self) -> ft.Container:
        """Create the status text section."""
        status_text = ft.Text(
            value="Loading clients...",
            color=ft.Colors.PRIMARY,
            size=14,
            ref=self.status_text_ref
        )
        
        last_updated_text = ft.Text(
            value="Last updated: never",
            color=ft.Colors.ON_SURFACE,
            size=12,
            ref=self.last_updated_text_ref
        )
        
        return ft.Container(
            content=ft.Row([
                status_text,
                ft.Container(expand=True),
                last_updated_text
            ]),
            padding=ft.Padding(20, 0, 20, 10)
        )
    
    def _create_clients_table_section(self) -> ft.Container:
        """Create the clients table section."""
        clients_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Client ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Address", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Connected At", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Last Activity", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
            ],
            rows=[],
            heading_row_color=ft.Colors.SURFACE,
            data_row_min_height=50,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            ref=self.clients_table_ref
        )
        
        return ft.Container(
            content=ft.Column([clients_table], scroll=ft.ScrollMode.AUTO),
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10,
            margin=ft.Margin(20, 0, 20, 20)
        )
    
    @log_method_call
    async def _load_clients_data_async(self):
        """Asynchronously load clients data."""
        if self.is_loading:
            logger.info("Clients data load already in progress, skipping")
            return
            
        self.is_loading = True
        log_async_operation("Load Clients Data", "Starting client data retrieval")
        
        try:
            # Show progress indicator
            show_async_operation_feedback(self.page, "Loading clients")
            
            # Load data asynchronously
            if self.server_bridge:
                logger.info("Fetching clients from server bridge")
                self.all_clients_data = await self.page.run_thread(self.server_bridge.get_clients)
            else:
                # Fallback mock data
                logger.info("Using mock data for clients")
                await asyncio.sleep(0.5)  # Simulate network delay
                self.all_clients_data = self._generate_mock_clients_data()
            
            # Update last updated timestamp
            from datetime import datetime
            self.last_updated = datetime.now()
            self.last_updated_text_ref.current.value = f"Last updated: {self.last_updated.strftime('%H:%M:%S')}"
            
            # Update status counts
            self._update_status_counts()
            
            # Apply current filters
            self._filter_clients()
            
            # Update table
            self._update_table()
            self.status_text_ref.current.value = f"Showing {len(self.filtered_clients_data)} of {len(self.all_clients_data)} clients"
            
            log_async_completion("Load Clients Data", f"{len(self.all_clients_data)} clients loaded")
            
        except Exception as e:
            logger.error(f"Error loading clients data: {e}")
            self.status_text_ref.current.value = "Error loading clients data"
            log_async_completion("Load Clients Data", f"Failed with error: {str(e)}")
        finally:
            self.is_loading = False
            hide_async_operation_feedback(self.page)
            self.update()
    
    def _generate_mock_clients_data(self) -> List[Dict[str, Any]]:
        """Generate mock client data for testing."""
        from datetime import datetime, timedelta
        base_time = datetime.now()
        
        return [
            {"client_id": "client_001", "address": "192.168.1.101:54321", "status": "Connected", "connected_at": (base_time - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "last_activity": base_time.strftime("%Y-%m-%d %H:%M:%S")},
            {"client_id": "client_002", "address": "192.168.1.102:54322", "status": "Registered", "connected_at": (base_time - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"), "last_activity": (base_time - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")},
            {"client_id": "client_003", "address": "192.168.1.103:54323", "status": "Offline", "connected_at": (base_time - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"), "last_activity": (base_time - timedelta(days=1, hours=2)).strftime("%Y-%m-%d %H:%M:%S")},
            {"client_id": "client_004", "address": "192.168.1.104:54324", "status": "Connected", "connected_at": (base_time - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"), "last_activity": (base_time - timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")},
            {"client_id": "client_005", "address": "10.0.0.50:12345", "status": "Registered", "connected_at": (base_time - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"), "last_activity": (base_time - timedelta(days=1, hours=4)).strftime("%Y-%m-%d %H:%M:%S")}
        ]
    
    def _update_status_counts(self):
        """Update the status count cards."""
        try:
            connected_count = len([c for c in self.all_clients_data if c["status"] == "Connected"])
            registered_count = len([c for c in self.all_clients_data if c["status"] == "Registered"])  
            offline_count = len([c for c in self.all_clients_data if c["status"] == "Offline"])
            
            # Update card values using ft.Ref
            self.connected_count_text_ref.current.value = str(connected_count)
            self.registered_count_text_ref.current.value = str(registered_count)
            self.offline_count_text_ref.current.value = str(offline_count)
            
            # Update all refs
            self.connected_count_text_ref.current.update()
            self.registered_count_text_ref.current.update()
            self.offline_count_text_ref.current.update()
            
            logger.info(f"Status counts - Connected: {connected_count}, Registered: {registered_count}, Offline: {offline_count}")
            
        except Exception as e:
            logger.error(f"Error updating status counts: {e}")
    
    def _filter_clients(self):
        """Filter clients based on search query and status filter."""
        filtered = self.all_clients_data
        
        # Apply search filter
        if self.search_query.strip():
            query = self.search_query.lower().strip()
            filtered = [c for c in filtered if 
                       query in c["client_id"].lower() or 
                       query in c["address"].lower()]
        
        # Apply status filter
        if self.status_filter != "all":
            filtered = [c for c in filtered if c["status"].lower() == self.status_filter.lower()]
        
        self.filtered_clients_data = filtered
        logger.info(f"Filtered clients: {len(filtered)} of {len(self.all_clients_data)}")
    
    def _update_table(self):
        """Update the clients table with filtered data using ft.Ref."""
        try:
            # Create new table rows
            new_rows = []
            for client in self.filtered_clients_data:
                # Status color based on client status
                status_color_name = get_status_color(client["status"])
                status_color = getattr(ft.Colors, status_color_name, ft.Colors.ON_SURFACE)
                
                row = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(client["client_id"])),
                        ft.DataCell(ft.Text(client["address"])),
                        ft.DataCell(
                            ft.Container(
                                content=ft.Text(client["status"], color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
                                bgcolor=status_color,
                                border_radius=4,
                                padding=ft.Padding(8, 4, 8, 4)
                            )
                        ),
                        ft.DataCell(ft.Text(client["connected_at"])),
                        ft.DataCell(ft.Text(client["last_activity"])),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.INFO,
                                    tooltip="View Details",
                                    icon_size=16,
                                    on_click=self._create_view_details_handler(client["client_id"])
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.POWER_OFF,
                                    tooltip="Disconnect",
                                    icon_size=16,
                                    icon_color=ft.Colors.RED,
                                    on_click=self._create_disconnect_handler(client["client_id"])
                                )
                            ], spacing=5)
                        )
                    ]
                )
                new_rows.append(row)
            
            # Update table using ft.Ref
            self.clients_table_ref.current.rows = new_rows
            self.clients_table_ref.current.update()
            
        except Exception as e:
            logger.error(f"Error updating clients table: {e}")
    
    def _create_view_details_handler(self, client_id):
        """Create handler for viewing client details."""
        def handler(e):
            log_user_action("View Client Details", client_id)
            logger.info(f"Viewing details for client: {client_id}")
            # Create a dialog with client details
            client = next((c for c in self.all_clients_data if c["client_id"] == client_id), None)
            if client:
                dialog = ft.AlertDialog(
                    title=ft.Text(f"Client Details: {client_id}"),
                    content=ft.Column([
                        ft.Text(f"Address: {client['address']}"),
                        ft.Text(f"Status: {client['status']}"),
                        ft.Text(f"Connected At: {client['connected_at']}"),
                        ft.Text(f"Last Activity: {client['last_activity']}")
                    ], spacing=10, tight=True),
                    actions=[
                        ft.TextButton("Close", on_click=self._close_dialog)
                    ]
                )
                
                self.page.dialog = dialog
                dialog.open = True
                self.page.update()
        return handler
    
    def _create_disconnect_handler(self, client_id):
        """Create handler for disconnecting a client."""
        def handler(e):
            log_user_action("Disconnect Client", client_id)
            logger.info(f"Disconnecting client: {client_id}")
            # Find and update the client status
            for client in self.all_clients_data:
                if client["client_id"] == client_id:
                    client["status"] = "Offline"
                    break
            
            # Update the table display
            self._filter_clients()
            self._update_table()
            self._update_status_counts()
            
            # Show confirmation
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Client {client_id} disconnected"),
                bgcolor=ft.Colors.ORANGE
            )
            self.page.snack_bar.open = True
            self.page.update()
        return handler
    
    def _close_dialog(self, e):
        """Close the current dialog."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def _on_search_change(self, e):
        """Handle search query changes."""
        self.search_query = e.control.value
        logger.info(f"Search query changed to: '{self.search_query}'")
        self._filter_clients()
        self._update_table()
        self.status_text_ref.current.value = f"Showing {len(self.filtered_clients_data)} of {len(self.all_clients_data)} clients"
        self.status_text_ref.current.update()
    
    def _on_filter_change(self, e):
        """Handle status filter changes."""
        self.status_filter = e.control.value
        logger.info(f"Status filter changed to: {self.status_filter}")
        self._filter_clients()
        self._update_table()
        self.status_text_ref.current.value = f"Showing {len(self.filtered_clients_data)} of {len(self.all_clients_data)} clients"
        self.status_text_ref.current.update()
    
    def _on_refresh_click(self, e):
        """Handle refresh button click."""
        log_user_action("Refresh Clients")
        logger.info("Refreshing clients list...")
        self.page.run_task(self._load_clients_data_async)
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Refreshing clients list..."),
            bgcolor=ft.Colors.BLUE
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def did_mount(self):
        """Called when the control is added to the page."""
        logger.info("ClientsView mounted, loading initial data")
        self.page.run_task(self._load_clients_data_async)


def create_clients_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create clients view using ft.UserControl.
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The clients view
    """
    logger.info("Creating clients view")
    return ClientsView(server_bridge, page)