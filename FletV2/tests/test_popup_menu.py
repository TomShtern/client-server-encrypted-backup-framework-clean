#!/usr/bin/env python3
"""
PopupMenuButton Solution - Native Flet Context Menu
This uses Flet's built-in PopupMenuButton for proper context menus.
"""

import flet as ft

# Global state for testing
action_count = {"count": 0}
feedback_text = ft.Text("No actions yet - try the menu buttons", size=14, color=ft.Colors.BLUE)

def view_details_action(client_id, page):
    """View details action via popup menu"""
    action_count["count"] += 1
    print(f"VIEW DETAILS ACTION! Client: {client_id}, Count: {action_count['count']}")

    feedback_text.value = f"VIEW DETAILS for {client_id} (action #{action_count['count']})"
    feedback_text.update()

    page.snack_bar = ft.SnackBar(ft.Text(f"View Details: {client_id}"))
    page.snack_bar.open = True
    page.update()

def disconnect_action(client_id, page):
    """Disconnect action via popup menu"""
    action_count["count"] += 1
    print(f"DISCONNECT ACTION! Client: {client_id}, Count: {action_count['count']}")

    feedback_text.value = f"DISCONNECT for {client_id} (action #{action_count['count']})"
    feedback_text.update()

    page.snack_bar = ft.SnackBar(ft.Text(f"Disconnect: {client_id}"))
    page.snack_bar.open = True
    page.update()

def create_popup_menu_row(client, page):
    """Create DataRow with PopupMenuButton"""

    def on_view_details(e):
        view_details_action(client["client_id"], page)

    def on_disconnect(e):
        disconnect_action(client["client_id"], page)

    return ft.DataRow(cells=[
        ft.DataCell(ft.Text(client["client_id"])),
        ft.DataCell(ft.Text(client["address"])),
        ft.DataCell(ft.Text(client["status"])),
        ft.DataCell(
            ft.PopupMenuButton(
                icon=ft.Icons.MORE_VERT,
                tooltip="Actions",
                items=[
                    ft.PopupMenuItem(
                        text="View Details",
                        icon=ft.Icons.INFO,
                        on_click=on_view_details
                    ),
                    ft.PopupMenuItem(
                        text="Disconnect",
                        icon=ft.Icons.POWER_OFF,
                        on_click=on_disconnect
                    )
                ]
            )
        )
    ])

def main(page: ft.Page):
    page.title = "PopupMenuButton Solution Test"

    # Mock clients data
    clients = [
        {"client_id": "client_001", "address": "192.168.1.101:5432", "status": "connected"},
        {"client_id": "client_002", "address": "192.168.1.102:5433", "status": "registered"},
        {"client_id": "client_003", "address": "192.168.1.103:5434", "status": "offline"}
    ]

    # Create DataTable with PopupMenuButton
    datatable = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Client ID", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Address", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Status", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD))
        ],
        rows=[create_popup_menu_row(client, page) for client in clients],
        heading_row_color=ft.Colors.SURFACE,
        data_row_min_height=50,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=8
    )

    page.add(
        ft.Text("PopupMenuButton Solution Test", size=20, weight=ft.FontWeight.BOLD),
        ft.Text("Click the ⋮ (3 dots) button in each row for actions", size=14),

        # Feedback text
        ft.Container(
            content=feedback_text,
            padding=ft.padding.all(10),
            bgcolor=ft.Colors.SURFACE,
            border_radius=4
        ),

        ft.Divider(),
        datatable
    )

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.FLET_APP)
