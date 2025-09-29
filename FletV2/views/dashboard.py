#!/usr/bin/env python3
"""
Simple Dashboard with Basic Controls
Focusing on functionality over complex styling
"""

import os
import sys
from datetime import datetime
from typing import Any, Callable

# Path setup
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import flet as ft
import Shared.utils.utf8_solution as _  # noqa: F401

def create_dashboard_view(
    server_bridge: Any | None,
    page: ft.Page,
    _state_manager: Any | None
) -> tuple[ft.Control, Callable, Callable]:
    """Create a simple, functional dashboard using basic Flet components."""

    # Refs for dynamic content
    clients_ref = ft.Ref[ft.Text]()
    files_ref = ft.Ref[ft.Text]()
    storage_ref = ft.Ref[ft.Text]()
    uptime_ref = ft.Ref[ft.Text]()

    # Progress refs
    storage_progress_ref = ft.Ref[ft.ProgressBar]()
    cpu_progress_ref = ft.Ref[ft.ProgressBar]()
    memory_progress_ref = ft.Ref[ft.ProgressBar]()

    # Get server data
    def get_server_data():
        if server_bridge:
            try:
                result = server_bridge.get_system_status()
                if result.get('success'):
                    return result.get('data', {})
            except Exception:
                pass

        # Fallback data
        return {
            'clients': 8,
            'files': 1247,
            'storage_used': 68,
            'uptime': '2d 14h',
            'cpu_usage': 25,
            'memory_usage': 42
        }

    # Update dashboard data safely
    def update_data():
        data = get_server_data()

        # Update text values
        if clients_ref.current:
            clients_ref.current.value = str(data.get('clients', 0))
            clients_ref.current.update()

        if files_ref.current:
            files_ref.current.value = str(data.get('files', 0))
            files_ref.current.update()

        if storage_ref.current:
            storage_ref.current.value = f"{data.get('storage_used', 0)}%"
            storage_ref.current.update()

        if uptime_ref.current:
            uptime_ref.current.value = data.get('uptime', 'N/A')
            uptime_ref.current.update()

        # Update progress bars
        if storage_progress_ref.current:
            storage_progress_ref.current.value = data.get('storage_used', 0) / 100
            storage_progress_ref.current.update()

        if cpu_progress_ref.current:
            cpu_progress_ref.current.value = data.get('cpu_usage', 0) / 100
            cpu_progress_ref.current.update()

        if memory_progress_ref.current:
            memory_progress_ref.current.value = data.get('memory_usage', 0) / 100
            memory_progress_ref.current.update()

    # Simple metric card
    def create_metric_card(title: str, value_ref, icon: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color),
                    ft.Text(title)
                ]),
                ft.Text("0", ref=value_ref),
                ft.ProgressBar(value=0, color=color)
            ], spacing=10),
            padding=10,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            width=200,
            height=150
        )

    # Simple header
    header = ft.Container(
        content=ft.Row([
            ft.Text(
                "SERVER DASHBOARD",
                size=24,
                weight=ft.FontWeight.BOLD
            ),
            ft.IconButton(ft.Icons.REFRESH, on_click=lambda _: update_data())
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=10,
        border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE))
    )

    # Metrics row
    metrics_row = ft.Row([
        create_metric_card("Active Clients", clients_ref, ft.Icons.PEOPLE, ft.Colors.BLUE),
        create_metric_card("Total Files", files_ref, ft.Icons.FOLDER_COPY, ft.Colors.GREEN),
        create_metric_card("Storage Used", storage_ref, ft.Icons.STORAGE, ft.Colors.ORANGE),
        create_metric_card("System Uptime", uptime_ref, ft.Icons.SCHEDULE, ft.Colors.PURPLE),
    ], spacing=10, wrap=True)

    # Performance row
    performance_row = ft.Row([
        ft.Container(
            content=ft.Column([
                ft.Text("Storage Usage"),
                ft.ProgressBar(ref=storage_progress_ref, value=0, color=ft.Colors.ORANGE)
            ]),
            width=200,
            padding=10
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("CPU Performance"),
                ft.ProgressBar(ref=cpu_progress_ref, value=0, color=ft.Colors.RED)
            ]),
            width=200,
            padding=10
        ),
        ft.Container(
            content=ft.Column([
                ft.Text("Memory Usage"),
                ft.ProgressBar(ref=memory_progress_ref, value=0, color=ft.Colors.BLUE)
            ]),
            width=200,
            padding=10
        )
    ], spacing=10, wrap=True)

    # Recent activity (simplified)
    def create_activity_item(client: str, action: str, status: str):
        return ft.ListTile(
            title=ft.Text(client),
            subtitle=ft.Text(f"{action} - {status}")
        )

    activities = [
        create_activity_item("Client-001", "Backup", "Complete"),
        create_activity_item("Client-003", "File Transfer", "In Progress"),
        create_activity_item("Client-007", "System Scan", "Complete")
    ]

    activity_list = ft.ListView(controls=activities, spacing=10, width=600)

    # Main dashboard container
    dashboard_container = ft.Column([
        header,
        ft.Text("System Metrics", size=18, weight=ft.FontWeight.BOLD),
        metrics_row,
        ft.Text("Performance", size=18, weight=ft.FontWeight.BOLD),
        performance_row,
        ft.Text("Recent Activity", size=18, weight=ft.FontWeight.BOLD),
        activity_list
    ], spacing=10, scroll=ft.ScrollMode.AUTO)

    def setup_subscriptions():
        """Initialize dashboard data."""
        update_data()

    def dispose():
        """Cleanup dashboard."""
        pass

    return dashboard_container, dispose, setup_subscriptions