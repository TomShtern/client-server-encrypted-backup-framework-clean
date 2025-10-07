#!/usr/bin/env python3
"""
Production Button Fix Test - Apply Working Pattern to Production-Like Code
This tests the exact working minimal test pattern in a production-like environment.
"""


import flet as ft


def main(page: ft.Page):
    page.title = "Production Button Fix Test"

    # Simulate our production data
    mock_clients_data = [
        {"client_id": "client_001", "address": "192.168.1.101:5432", "status": "connected"},
        {"client_id": "client_002", "address": "192.168.1.102:5433", "status": "registered"},
        {"client_id": "client_003", "address": "192.168.1.103:5434", "status": "offline"}
    ]

    # CRITICAL: Define handlers at the RIGHT SCOPE (same level as DataTable)
    def view_details_clicked(e):
        client_id = e.control.data if hasattr(e.control, 'data') else "Unknown"
        print(f"VIEW DETAILS CLICKED! Client: {client_id}")
        page.snack_bar = ft.SnackBar(ft.Text(f"View Details clicked for: {client_id}"))
        page.snack_bar.open = True
        page.update()

    def disconnect_clicked(e):
        client_id = e.control.data if hasattr(e.control, 'data') else "Unknown"
        print(f"DISCONNECT CLICKED! Client: {client_id}")
        page.snack_bar = ft.SnackBar(ft.Text(f"Disconnect clicked for: {client_id}"))
        page.snack_bar.open = True
        page.update()

    # Create DataTable with the EXACT working pattern from minimal test
    def create_data_rows() -> list[ft.DataRow]:
        """Create DataTable rows with working button pattern"""
        rows = []

        for client in mock_clients_data:
            row = ft.DataRow(cells=[
                ft.DataCell(ft.Text(client["client_id"])),
                ft.DataCell(ft.Text(client["address"])),
                ft.DataCell(ft.Text(client["status"])),
                ft.DataCell(
                    ft.Row([
                        # EXACT working pattern from minimal test
                        ft.IconButton(
                            icon=ft.Icons.INFO,
                            tooltip="View Details",
                            icon_size=16,
                            data=client["client_id"],  # Store client ID in data
                            on_click=view_details_clicked  # Direct function reference
                        ),
                        ft.IconButton(
                            icon=ft.Icons.POWER_OFF,
                            tooltip="Disconnect",
                            icon_size=16,
                            icon_color=ft.Colors.RED,
                            data=client["client_id"],  # Store client ID in data
                            on_click=disconnect_clicked  # Direct function reference
                        )
                    ], spacing=5)
                )
            ])
            rows.append(row)

        return rows

    # Create DataTable with buttons at creation time (working pattern)
    clients_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Client ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Address", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
        ],
        rows=create_data_rows(),  # Buttons included at creation time
        heading_row_color=ft.Colors.SURFACE,
        data_row_min_height=50,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8
    )

    page.add(
        ft.Text("Production Button Fix Test", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Testing exact working pattern from minimal test", size=14),
        ft.Divider(),
        ft.Container(
            content=ft.Column([
                clients_table
            ], scroll="auto"),
            expand=True,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=8,
            padding=10
        )
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
