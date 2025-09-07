#!/usr/bin/env python3
"""
View Rebuild Approach Test - Complete DataTable Recreation
This tests the "nuclear option" - rebuilding the entire DataTable on every interaction.
"""

import flet as ft

# Global state for testing
button_clicks = {"count": 0}
current_clients_data = [
    {"client_id": "client_001", "address": "192.168.1.101:5432", "status": "connected"},
    {"client_id": "client_002", "address": "192.168.1.102:5433", "status": "registered"},
    {"client_id": "client_003", "address": "192.168.1.103:5434", "status": "offline"}
]

def view_details_clicked(e):
    """Handler that will work because table is rebuilt fresh each time"""
    button_clicks["count"] += 1
    client_id = e.control.data if hasattr(e.control, 'data') else "Unknown"
    print(f"VIEW DETAILS CLICKED! Client: {client_id}, Count: {button_clicks['count']}")
    
    # Get page reference and show snack bar
    page = e.control.page if hasattr(e.control, 'page') else None
    if page:
        page.snack_bar = ft.SnackBar(ft.Text(f"View Details: {client_id} (click #{button_clicks['count']})"))
        page.snack_bar.open = True
        page.update()
    
    # CRITICAL: Rebuild the entire table after action
    rebuild_table(page)

def disconnect_clicked(e):
    """Handler that will work because table is rebuilt fresh each time"""
    button_clicks["count"] += 1
    client_id = e.control.data if hasattr(e.control, 'data') else "Unknown"
    print(f"DISCONNECT CLICKED! Client: {client_id}, Count: {button_clicks['count']}")
    
    # Get page reference and show snack bar
    page = e.control.page if hasattr(e.control, 'page') else None
    if page:
        page.snack_bar = ft.SnackBar(ft.Text(f"Disconnect: {client_id} (click #{button_clicks['count']})"))
        page.snack_bar.open = True
        page.update()
    
    # CRITICAL: Rebuild the entire table after action
    rebuild_table(page)

def create_fresh_datatable():
    """Create a completely fresh DataTable with working buttons"""
    print("Creating fresh DataTable...")
    
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Client ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Address", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
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
                        on_click=view_details_clicked  # Fresh handler reference
                    ),
                    ft.IconButton(
                        icon=ft.Icons.POWER_OFF,
                        tooltip="Disconnect",
                        icon_size=16,
                        icon_color=ft.Colors.RED,
                        data=client["client_id"],
                        on_click=disconnect_clicked  # Fresh handler reference
                    )
                ], spacing=5))
            ]) for client in current_clients_data
        ],
        heading_row_color=ft.Colors.SURFACE,
        data_row_min_height=50,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8
    )

# Global reference to table container
table_container_ref = ft.Ref[ft.Container]()

def rebuild_table(page):
    """Rebuild the entire table - the nuclear option"""
    print("REBUILDING ENTIRE TABLE...")
    
    # Create completely fresh DataTable
    fresh_table = create_fresh_datatable()
    
    # Replace the content entirely
    if table_container_ref.current:
        table_container_ref.current.content = ft.Column([fresh_table], scroll=ft.ScrollMode.AUTO)
        table_container_ref.current.update()
        print("Table rebuilt successfully!")

def main(page: ft.Page):
    page.title = "View Rebuild Approach Test"
    
    # Initial table
    initial_table = create_fresh_datatable()
    
    # Container to hold the table (will be replaced)
    table_container = ft.Container(
        ref=table_container_ref,
        content=ft.Column([initial_table], scroll=ft.ScrollMode.AUTO),
        expand=True,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8,
        padding=10
    )
    
    page.add(
        ft.Text("View Rebuild Approach Test", size=20, weight=ft.FontWeight.BOLD),
        ft.Text(f"Total button clicks: {button_clicks['count']}", size=14),
        ft.Text("Each button click rebuilds the ENTIRE table", size=12, color=ft.Colors.GREY),
        ft.Divider(),
        table_container
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)