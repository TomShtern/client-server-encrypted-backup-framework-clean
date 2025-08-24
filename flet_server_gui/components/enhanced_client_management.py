#!/usr/bin/env python3
"""
Enhanced Client Management Component
Material Design 3 component with detailed client information and advanced filtering.
"""

import flet as ft
from typing import List, Dict, Optional, Callable
from flet_server_gui.components.enhanced_components import (
    EnhancedDataTable,
    EnhancedTextField,
    EnhancedChip,
    create_enhanced_button,
    create_enhanced_icon_button
)
from flet_server_gui.components.dialogs import create_confirmation_dialog, create_input_dialog


def create_enhanced_client_management(clients_data: List[Dict] = None, page: ft.Page = None) -> ft.Control:
    """Create enhanced client management component"""
    clients_data = clients_data or []
    
    # Callback functions for button actions
    def _on_add_client(e):
        """Handle add client button click"""
        print("Add client clicked")
        # In a real implementation, this would show an add client dialog
        if page:
            from flet_server_gui.components.dialogs import create_toast_notification
            toast = create_toast_notification(
                message="Add client functionality would be implemented here",
                bgcolor=ft.Colors.SECONDARY_CONTAINER
            )
            toast.show(page)

    def _on_refresh_client_list(e):
        """Handle refresh client list button click"""
        print("Refresh client list clicked")
        # In a real implementation, this would refresh the client list from the server
        if page:
            from flet_server_gui.components.dialogs import create_toast_notification
            toast = create_toast_notification(
                message="Client list refreshed",
                bgcolor=ft.Colors.PRIMARY_CONTAINER
            )
            toast.show(page)

    def _on_view_client_details(client_data):
        """Handle view client details button click"""
        def handler(e):
            print(f"View details for {client_data.get('client_id')}")
            # In a real implementation, this would show client details
            if page:
                from flet_server_gui.components.dialogs import create_toast_notification
                toast = create_toast_notification(
                    message=f"Viewing details for {client_data.get('client_id')}",
                    bgcolor=ft.Colors.PRIMARY_CONTAINER
                )
                toast.show(page)
        return handler

    def _on_disconnect_client(client_data):
        """Handle disconnect client button click"""
        def handler(e):
            print(f"Disconnect {client_data.get('client_id')}")
            # In a real implementation, this would disconnect the client
            if page:
                from flet_server_gui.components.dialogs import create_toast_notification
                toast = create_toast_notification(
                    message=f"Disconnected {client_data.get('client_id')}",
                    bgcolor=ft.Colors.SECONDARY_CONTAINER
                )
                toast.show(page)
        return handler

    # Header with title and actions
    header = ft.Row([
        ft.Text("Client Management", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
        ft.Container(expand=True),
        create_enhanced_button(
            text="Add Client",
            icon=ft.Icons.ADD,
            on_click=_on_add_client
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    # Filter controls
    # Search field
    search_field = EnhancedTextField(
        label="Search clients...",
        icon=ft.Icons.SEARCH,
        expand=True
    )
    
    # Status filter chips
    status_chips = ft.Row([
        EnhancedChip(
            label=ft.Text("All"),
            selected=True
        ),
        EnhancedChip(
            label=ft.Text("Online")
        ),
        EnhancedChip(
            label=ft.Text("Offline")
        ),
        EnhancedChip(
            label=ft.Text("Active")
        )
    ], spacing=8)
    
    # Refresh button
    refresh_button = create_enhanced_icon_button(
        icon=ft.Icons.REFRESH,
        tooltip="Refresh client list",
        on_click=_on_refresh_client_list
    )
    
    filter_row = ft.Column([
        ft.Row([
            search_field,
            refresh_button
        ], spacing=12),
        status_chips
    ], spacing=12)
    
    # Client table
    columns = [
        ft.DataColumn(ft.Text("")),
        ft.DataColumn(ft.Text("Client ID")),
        ft.DataColumn(ft.Text("IP Address")),
        ft.DataColumn(ft.Text("Status")),
        ft.DataColumn(ft.Text("Connected Since")),
        ft.DataColumn(ft.Text("Last Activity")),
        ft.DataColumn(ft.Text("Actions"))
    ]
    
    rows = []
    for client in clients_data:
        status_color = "green" if client.get("status") == "online" else "red" if client.get("status") == "offline" else "orange"
        
        row = ft.DataRow(
            cells=[
                ft.DataCell(ft.Checkbox()),
                ft.DataCell(ft.Text(client.get("client_id", "N/A"))),
                ft.DataCell(ft.Text(client.get("ip", "N/A"))),
                ft.DataCell(
                    ft.Chip(
                        label=ft.Text(client.get("status", "Unknown")),
                        color=status_color
                    )
                ),
                ft.DataCell(ft.Text(client.get("connected", "N/A"))),
                ft.DataCell(ft.Text(client.get("activity", "N/A"))),
                ft.DataCell(
                    ft.Row([
                        create_enhanced_icon_button(
                            icon=ft.Icons.VISIBILITY,
                            tooltip="View details",
                            on_click=_on_view_client_details(client)
                        ),
                        create_enhanced_icon_button(
                            icon=ft.Icons.CLOSE,
                            tooltip="Disconnect",
                            on_click=_on_disconnect_client(client)
                        )
                    ], spacing=4)
                )
            ]
        )
        rows.append(row)
    
    client_table = EnhancedDataTable(
        columns=columns,
        rows=rows,
        sortable=True,
        striped_rows=True,
        hover_highlight=True
    )
    
    # Wrap table in a scrollable container
    table_container = ft.Container(
        content=client_table,
        padding=20,
        border_radius=8,
        expand=True
    )
    
    return ft.Column([
        header,
        ft.Divider(),
        filter_row,
        ft.Divider(),
        table_container,
    ], spacing=20, expand=True, scroll=ft.ScrollMode.ADAPTIVE)