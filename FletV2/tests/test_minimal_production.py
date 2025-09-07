#!/usr/bin/env python3
"""
Minimal Production Test - Bypass All Complex Infrastructure
This tests whether the complex infrastructure is preventing button serialization.
"""

import flet as ft

# Module-level handlers (working pattern)
def view_details_clicked(e):
    print(f"VIEW DETAILS CLICKED! Data: {e.control.data}")
    page = e.control.page
    if page:
        page.snack_bar = ft.SnackBar(ft.Text(f"View Details: {e.control.data}"))
        page.snack_bar.open = True
        page.update()

def disconnect_clicked(e):
    print(f"DISCONNECT CLICKED! Data: {e.control.data}")
    page = e.control.page
    if page:
        page.snack_bar = ft.SnackBar(ft.Text(f"Disconnect: {e.control.data}"))
        page.snack_bar.open = True
        page.update()

def main(page: ft.Page):
    page.title = "Minimal Production Test - No Infrastructure"
    
    # Simple mock data (no StateManager, no EnhancedServerBridge)
    clients = [
        {"client_id": "test_001", "address": "192.168.1.101", "status": "connected"},
        {"client_id": "test_002", "address": "192.168.1.102", "status": "offline"}
    ]
    
    # Create DataTable EXACTLY like the working simple test
    # BUT with production-like structure
    datatable = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Client ID")),
            ft.DataColumn(ft.Text("Address")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Actions"))
        ],
        rows=[
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(client["client_id"])),
                ft.DataCell(ft.Text(client["address"])),
                ft.DataCell(ft.Text(client["status"])),
                ft.DataCell(ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.INFO,
                        tooltip="View Details",
                        icon_size=16,
                        data=client["client_id"],
                        on_click=view_details_clicked
                    ),
                    ft.IconButton(
                        icon=ft.Icons.POWER_OFF,
                        tooltip="Disconnect",
                        icon_size=16,
                        icon_color=ft.Colors.RED,
                        data=client["client_id"],
                        on_click=disconnect_clicked
                    )
                ], spacing=5))
            ]) for client in clients
        ],
        heading_row_color=ft.Colors.SURFACE,
        data_row_min_height=50,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8
    )
    
    page.add(
        ft.Text("Minimal Production Test", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("No StateManager, no EnhancedServerBridge, no refs", size=14),
        ft.Divider(),
        datatable
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)