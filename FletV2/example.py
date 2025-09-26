#!/usr/bin/env python3
"""
Example script demonstrating FletV2 framework usage.
"""

import os
import sys

# Add the FletV2 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

import contextlib
from typing import Any, cast

import flet as ft
from theme import setup_modern_theme as setup_default_theme
from utils.server_bridge import create_server_bridge
from views.clients import create_clients_view
from views.dashboard import create_dashboard_view


def main(page: ft.Page):
    """Main application function."""
    # Configure the page
    page.title = "FletV2 Example"
    # Page layout attributes may not be statically known to the type checker; set at runtime
    _p = cast(Any, page)
    with contextlib.suppress(Exception):
        _p.window_width = 1200
        _p.window_height = 800

    # Set up theme
    setup_default_theme(page)

    # Create server bridge
    server_bridge = create_server_bridge()

    # Create views (call factories and unwrap tuple results if present)
    dashboard_result = cast(Any, create_dashboard_view)(server_bridge, page, None)
    if isinstance(dashboard_result, tuple):
        dashboard_view = dashboard_result[0]
    else:
        dashboard_view = dashboard_result

    clients_result = cast(Any, create_clients_view)(server_bridge, page, None)
    if isinstance(clients_result, tuple):
        clients_view = clients_result[0]
    else:
        clients_view = clients_result

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
