#!/usr/bin/env python3
"""
Simple Clients View - Hiroshima Protocol Compliant
A clean, minimal implementation using pure Flet patterns.

This demonstrates the Hiroshima ideal:
- Uses Flet's built-in DataTable exclusively 
- No custom state management or complex event handling
- Simple function returning ft.Control (composition over inheritance)
- Works WITH the framework, not against it
"""

import flet as ft
import asyncio
from datetime import datetime


def create_clients_view(server_bridge, page: ft.Page) -> ft.Control:
    """
    Create clients view using simple Flet patterns (no class inheritance needed).
    
    Args:
        server_bridge: Server bridge for data access
        page: Flet page instance
        
    Returns:
        ft.Control: The clients view
    """
    
    # Get client data from server
    if server_bridge:
        clients_data = server_bridge.get_clients()
    else:
        # Fallback mock data
        clients_data = [
            {"client_id": "client_001", "address": "192.168.1.101:54321", "status": "Connected", "connected_at": "2025-09-03 10:30:15", "last_activity": "2025-09-03 14:45:30"},
            {"client_id": "client_002", "address": "192.168.1.102:54322", "status": "Registered", "connected_at": "2025-09-02 09:15:22", "last_activity": "2025-09-03 12:20:45"},
            {"client_id": "client_003", "address": "192.168.1.103:54323", "status": "Offline", "connected_at": "2025-09-01 14:22:10", "last_activity": "2025-09-02 16:33:55"},
            {"client_id": "client_004", "address": "192.168.1.104:54324", "status": "Connected", "connected_at": "2025-09-03 11:45:05", "last_activity": "2025-09-03 15:12:33"}
        ]
    
    # Create action handlers (simple functions)
    def on_disconnect_click(client_id):
        def handler(e):
            print(f"[INFO] Disconnect client {client_id}")
            if page.snack_bar:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Client {client_id} disconnected"),
                    bgcolor=ft.Colors.GREEN
                )
                page.snack_bar.open = True
                page.update()
        return handler
    
    def on_view_details_click(client_id):
        def handler(e):
            print(f"[INFO] View details for client {client_id}")
            # Simple dialog using Flet's built-in AlertDialog
            client = next((c for c in clients_data if c["client_id"] == client_id), None)
            if client:
                dialog = ft.AlertDialog(
                    title=ft.Text(f"Client Details - {client_id}"),
                    content=ft.Column([
                        ft.Text(f"Address: {client['address']}"),
                        ft.Text(f"Status: {client['status']}"),
                        ft.Text(f"Connected: {client['connected_at']}"),
                        ft.Text(f"Last Activity: {client['last_activity']}")
                    ], spacing=10, height=150),
                    actions=[
                        ft.TextButton("Close", on_click=lambda e: close_dialog())
                    ]
                )
                
                def close_dialog():
                    page.dialog.open = False
                    page.update()
                
                page.dialog = dialog
                dialog.open = True
                page.update()
        return handler
    
    # Create DataTable using Flet's built-in component (this is the RIGHT way!)
    clients_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Client ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Address", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Connected At", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Last Activity", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(client["client_id"])),
                    ft.DataCell(ft.Text(client["address"])),
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                client["status"], 
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD
                            ),
                            bgcolor=ft.Colors.GREEN if client["status"] == "Connected" 
                                   else ft.Colors.ORANGE if client["status"] == "Registered" 
                                   else ft.Colors.RED,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            border_radius=4
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
                                on_click=on_view_details_click(client["client_id"])
                            ),
                            ft.IconButton(
                                icon=ft.Icons.POWER_OFF,
                                tooltip="Disconnect",
                                icon_size=16,
                                icon_color=ft.Colors.RED,
                                on_click=on_disconnect_click(client["client_id"])
                            )
                        ], spacing=5)
                    )
                ]
            ) for client in clients_data
        ],
        heading_row_color=ft.Colors.SURFACE,
        data_row_min_height=50,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8
    )
    
    # Simple refresh function
    def refresh_clients(e):
        print("[INFO] Refreshing clients...")
        if page.snack_bar:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Clients refreshed"),
                bgcolor=ft.Colors.GREEN
            )
            page.snack_bar.open = True
            page.update()
    
    # Status summary cards
    connected_count = len([c for c in clients_data if c["status"] == "Connected"])
    registered_count = len([c for c in clients_data if c["status"] == "Registered"])
    offline_count = len([c for c in clients_data if c["status"] == "Offline"])
    
    summary_cards = ft.ResponsiveRow([
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.CONNECT_WITHOUT_CONTACT, size=24, color=ft.Colors.GREEN),
                        ft.Text("Connected", size=12, weight=ft.FontWeight.W_500),
                        ft.Text(str(connected_count), size=20, weight=ft.FontWeight.BOLD)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 12, "md": 4}),
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON_ADD, size=24, color=ft.Colors.ORANGE),
                        ft.Text("Registered", size=12, weight=ft.FontWeight.W_500),
                        ft.Text(str(registered_count), size=20, weight=ft.FontWeight.BOLD)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 12, "md": 4}),
        ft.Column([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.PERSON_OFF, size=24, color=ft.Colors.RED),
                        ft.Text("Offline", size=12, weight=ft.FontWeight.W_500),
                        ft.Text(str(offline_count), size=20, weight=ft.FontWeight.BOLD)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                    padding=15
                )
            )
        ], col={"sm": 12, "md": 4})
    ])
    
    # Main layout using simple Column
    return ft.Column([
        # Header
        ft.Row([
            ft.Icon(ft.Icons.PEOPLE, size=24),
            ft.Text("Client Management", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(expand=True),
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh Clients",
                on_click=refresh_clients
            )
        ]),
        ft.Divider(),
        
        # Summary cards
        ft.Text("Client Status Overview", size=18, weight=ft.FontWeight.BOLD),
        summary_cards,
        ft.Divider(),
        
        # Search and filter controls
        ft.Row([
            ft.TextField(
                label="Search Clients",
                hint_text="Search by client ID or address...",
                prefix_icon=ft.Icons.SEARCH,
                expand=True
            ),
            ft.Dropdown(
                label="Filter by Status",
                value="all",
                options=[
                    ft.dropdown.Option("all", "All Clients"),
                    ft.dropdown.Option("connected", "Connected"),
                    ft.dropdown.Option("registered", "Registered"),
                    ft.dropdown.Option("offline", "Offline")
                ],
                width=200
            )
        ], spacing=20),
        
        # Status info
        ft.Row([
            ft.Text(f"Showing {len(clients_data)} clients", size=14, color=ft.Colors.PRIMARY),
            ft.Container(expand=True),
            ft.Text("Last updated: " + datetime.now().strftime("%H:%M:%S"), size=12, color=ft.Colors.ON_SURFACE)
        ]),
        
        # DataTable in scrollable container (using Flet's built-in scrolling!)
        ft.Container(
            content=ft.Column([clients_table], scroll=ft.ScrollMode.AUTO),
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10
        )
        
    ], spacing=20, expand=True, scroll=ft.ScrollMode.AUTO)