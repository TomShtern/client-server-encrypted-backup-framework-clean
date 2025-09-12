#!/usr/bin/env python3
"""
Example script demonstrating FletV2 framework usage.
"""

import sys
import os

# Add the FletV2 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

import flet as ft
from theme import setup_default_theme
from utils.server_bridge import create_server_bridge
from views.dashboard import create_dashboard_view
from views.clients import create_clients_view


def main(page: ft.Page):
    """Main application function."""
    # Configure the page
    page.title = "FletV2 Example"
    page.window_width = 1200
    page.window_height = 800

    # Set up theme
    setup_default_theme(page)

    # Create server bridge
    server_bridge = create_server_bridge()

    # Create views
    dashboard_view = create_dashboard_view(server_bridge, page)
    clients_view = create_clients_view(server_bridge, page)

    # Create navigation
    def on_nav_change(e):
        if e.control.selected_index == 0:
            content_area.content = dashboard_view
        else:
            content_area.content = clients_view
        content_area.update()

    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        min_extended_width=400,
        group_alignment=-0.9,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PEOPLE_OUTLINE,
                selected_icon=ft.Icons.PEOPLE,
                label="Clients",
            ),
        ],
        on_change=on_nav_change,
    )

    content_area = ft.Container(
        content=dashboard_view,
        expand=True
    )

    # Create main layout
    app = ft.Row(
        controls=[
            nav_rail,
            ft.VerticalDivider(width=1),
            content_area
        ],
        expand=True
    )

    page.add(app)


if __name__ == "__main__":
    ft.app(target=main)