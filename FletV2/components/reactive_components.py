#!/usr/bin/env python3
"""
Reactive component examples using Flet 0.80.0's @ft.component decorator.

These components automatically re-render when the app_state properties they
depend on change. No manual control.update() calls needed!

This is the modern Flet 0.80.0 pattern replacing manual state management.
"""

from __future__ import annotations

import flet as ft
from FletV2.utils.observable_state import app_state


@ft.component
def LoadingIndicator():
    """Show loading indicator based on app_state.loading_states."""
    # This component automatically re-renders when app_state.loading_states changes
    if any(app_state.loading_states.values()):
        return ft.Column(
            [
                ft.ProgressRing(),
                ft.Text("Loading...", size=14, color=ft.Colors.GREY_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        )
    return ft.Container()  # Empty when not loading


@ft.component
def ToastNotification():
    """Display toast notification based on app_state.toast_message."""
    if not app_state.toast_message:
        return ft.Container()  # Hidden when no message

    # Color based on level
    color_map = {
        "success": ft.Colors.GREEN,
        "warning": ft.Colors.ORANGE,
        "error": ft.Colors.RED,
        "info": ft.Colors.BLUE,
    }
    bg_color = color_map.get(app_state.toast_level, ft.Colors.BLUE)

    return ft.Container(
        content=ft.Text(
            app_state.toast_message,
            color=ft.Colors.WHITE,
            size=14,
        ),
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        bgcolor=bg_color,
        border_radius=8,
        margin=ft.margin.all(8),
    )


@ft.component
def ClientsList():
    """
    Reactive clients list - automatically updates when app_state.clients changes.

    ✨ Key Insight: This component watches app_state.clients. When set_clients()
    is called anywhere in the app, this component automatically re-renders without
    any explicit update() calls.
    """

    if app_state.is_loading("clients"):
        return ft.Column(
            [
                ft.ProgressRing(),
                ft.Text("Loading clients...", color=ft.Colors.GREY_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            padding=ft.Padding.all(20),
        )

    if app_state.get_error("clients"):
        return ft.Container(
            content=ft.Text(
                f"Error: {app_state.get_error('clients')}",
                color=ft.Colors.ERROR,
            ),
            padding=ft.Padding.all(20),
        )

    if not app_state.clients:
        return ft.Container(
            content=ft.Text(
                "No clients found",
                color=ft.Colors.GREY_500,
                size=14,
            ),
            padding=ft.Padding.all(20),
            alignment=ft.Alignment.CENTER,
        )

    return ft.ListView(
        controls=[
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text(client.get("name", "Unknown")),
                subtitle=ft.Text(client.get("id", "")[:16] + "..."),
                on_click=lambda e, cid=client.get("id"): app_state.set_selected_client(cid),
            )
            for client in app_state.clients
        ],
        item_extent=60,
        expand=True,
    )


@ft.component
def FilesList():
    """Reactive files list - automatically updates when app_state.files changes."""

    if app_state.is_loading("files"):
        return ft.Column(
            [
                ft.ProgressRing(),
                ft.Text("Loading files...", color=ft.Colors.GREY_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            padding=ft.Padding.all(20),
        )

    if app_state.get_error("files"):
        return ft.Container(
            content=ft.Text(
                f"Error: {app_state.get_error('files')}",
                color=ft.Colors.ERROR,
            ),
            padding=ft.Padding.all(20),
        )

    if not app_state.files:
        return ft.Container(
            content=ft.Text(
                "No files found",
                color=ft.Colors.GREY_500,
                size=14,
            ),
            padding=ft.Padding.all(20),
            alignment=ft.Alignment.CENTER,
        )

    return ft.ListView(
        controls=[
            ft.ListTile(
                leading=ft.Icon(ft.Icons.DESCRIPTION),
                title=ft.Text(file.get("name", "Unknown")),
                subtitle=ft.Text(f"{file.get('size', 0)} bytes"),
                on_click=lambda e, fid=file.get("id"): app_state.set_selected_file(fid),
            )
            for file in app_state.files
        ],
        item_extent=60,
        expand=True,
    )


@ft.component
def SearchableClientsList():
    """
    Example of local state with hooks combined with global observable state.

    Uses ft.use_state() for local search query, watches app_state.clients for updates.
    """
    search_query, set_search_query = ft.use_state("")

    # Filter clients based on search
    filtered_clients = [
        c for c in app_state.clients
        if search_query.lower() in c.get("name", "").lower()
    ]

    return ft.Column(
        [
            ft.TextField(
                label="Search clients",
                value=search_query,
                on_change=lambda e: set_search_query(e.control.value),
                prefix_icon=ft.Icons.SEARCH,
            ),
            ft.ListView(
                controls=[
                    ft.ListTile(
                        title=ft.Text(c.get("name", "Unknown")),
                        subtitle=ft.Text(c.get("id", "")[:16] + "..."),
                    )
                    for c in filtered_clients
                ],
                item_extent=50,
                expand=True,
            ) if filtered_clients else ft.Container(
                content=ft.Text("No matches", color=ft.Colors.GREY_500),
                padding=ft.Padding.all(20),
            ),
        ],
        spacing=8,
        expand=True,
    )


@ft.component
def ServerStatusBadge():
    """
    Status badge that automatically updates when app_state.server_status changes.

    ✨ Example of a simple reactive component with conditional styling.
    """
    color_map = {
        "connected": ft.Colors.GREEN,
        "disconnected": ft.Colors.GREY,
        "error": ft.Colors.RED,
        "unknown": ft.Colors.AMBER,
    }
    color = color_map.get(app_state.server_status, ft.Colors.GREY)

    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(
                    ft.Icons.CIRCLE,
                    size=12,
                    color=color,
                ),
                ft.Text(
                    app_state.server_status.upper(),
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=color,
                ),
            ],
            spacing=4,
        ),
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        bgcolor=ft.Colors.with_opacity(0.1, color),
        border_radius=12,
        border=ft.border.all(1, color),
    )


@ft.component
def DataMetricsCard(title: str, value: int | str, icon: str = ft.Icons.TRENDING_UP):
    """
    Reusable metrics card component.

    Example of a parameterized component that stays simple while watching
    global state.
    """
    return ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(icon, size=24, color=ft.Colors.PRIMARY),
                            ft.Text(title, size=12, color=ft.Colors.GREY_500),
                        ],
                        spacing=8,
                    ),
                    ft.Text(
                        str(value),
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE,
                    ),
                ],
                spacing=8,
            ),
            padding=ft.Padding.all(16),
        ),
    )


# ───────────────────────────────────────────────────────────────────────
# USAGE PATTERNS
# ───────────────────────────────────────────────────────────────────────

"""
Pattern 1: Use reactive component in a view
───────────────────────────────────────────
def my_view(server_bridge, page):
    content = ft.Column([
        ClientsList(),  # Automatically updates when app_state.clients changes!
        FilesList(),    # Automatically updates when app_state.files changes!
    ])

    async def load_data():
        app_state.set_loading("clients", True)
        result = await run_sync_in_executor(server_bridge.get_clients)
        if result.get("success"):
            app_state.set_clients(result["data"])  # Triggers ClientsList re-render
        app_state.set_loading("clients", False)

    return content, lambda: None, load_data


Pattern 2: Local state with global state
─────────────────────────────────────────
@ft.component
def MyComponent():
    local_state, set_local_state = ft.use_state("")

    # Watch both local and global state
    def on_change(e):
        set_local_state(e.control.value)  # Local update
        # Global state automatically triggers re-renders of other components

    return ft.Column([
        ft.TextField(value=local_state, on_change=on_change),
        # Other components that watch app_state automatically update
    ])


Pattern 3: Use async hooks for data loading
───────────────────────────────────────────
@ft.component
def DataView():
    loading, set_loading = ft.use_state(True)

    async def load_data():
        set_loading(True)
        app_state.set_loading("data", True)

        # Fetch data
        result = await run_sync_in_executor(server_bridge.get_data)

        if result.get("success"):
            app_state.set_analytics_data(result["data"])
        else:
            app_state.set_error("data", result.get("error"))

        app_state.set_loading("data", False)
        set_loading(False)

    ft.use_effect(load_data, [])  # Run on mount

    if loading:
        return ft.ProgressRing()

    return ft.Column([
        DataMetricsCard("Clients", len(app_state.clients)),
        DataMetricsCard("Files", len(app_state.files)),
    ])
"""
