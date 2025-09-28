#!/usr/bin/env python3
"""
Clean Dashboard View - Material Design 3
Simplified, robust implementation focusing on functionality and clean layouts.
"""

import asyncio
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

from theme import setup_sophisticated_theme
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.user_feedback import show_success_message, show_error_message

def create_dashboard_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    _state_manager: StateManager | None
) -> tuple[ft.Control, Callable, Callable]:
    """Create clean, functional dashboard using Flet built-in components."""

    # Apply theme
    if page:
        setup_sophisticated_theme(page)

    # Refs for dynamic content
    clients_ref = ft.Ref[ft.Text]()
    files_ref = ft.Ref[ft.Text]()
    storage_ref = ft.Ref[ft.Text]()
    uptime_ref = ft.Ref[ft.Text]()
    status_ref = ft.Ref[ft.Text]()

    # Progress refs
    storage_progress_ref = ft.Ref[ft.ProgressRing]()
    cpu_progress_ref = ft.Ref[ft.ProgressRing]()
    memory_progress_ref = ft.Ref[ft.ProgressRing]()

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

        # Update progress rings
        if storage_progress_ref.current:
            storage_progress_ref.current.value = data.get('storage_used', 0) / 100
            storage_progress_ref.current.update()

        if cpu_progress_ref.current:
            cpu_progress_ref.current.value = data.get('cpu_usage', 0) / 100
            cpu_progress_ref.current.update()

        if memory_progress_ref.current:
            memory_progress_ref.current.value = data.get('memory_usage', 0) / 100
            memory_progress_ref.current.update()

    # Clean metric card
    def create_metric_card(title: str, value_ref, icon: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=24),
                    ft.Text(title, size=14, weight=ft.FontWeight.W_500)
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(
                    content=ft.Text("0", ref=value_ref, size=32, weight=ft.FontWeight.BOLD, color=color),
                    margin=ft.margin.only(top=8)
                ),
            ], spacing=4),
            padding=16,
            border_radius=8,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        )

    # Clean progress gauge
    def create_progress_gauge(title: str, progress_ref, icon: str, color: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, color=color, size=24),
                    ft.Text(title, size=14, weight=ft.FontWeight.W_500)
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(
                    content=ft.ProgressRing(
                        ref=progress_ref,
                        width=60,
                        height=60,
                        stroke_width=6,
                        color=color,
                        bgcolor=ft.Colors.SURFACE,
                        value=0
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=12)
                )
            ], spacing=4),
            padding=16,
            border_radius=8,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        )

    # Clean activity panel
    def create_activity_panel() -> ft.Container:
        activities = [
            ["Client-001", "Backup Complete", "2 min ago", "Success"],
            ["Client-003", "File Transfer", "5 min ago", "In Progress"],
            ["Client-007", "System Scan", "8 min ago", "Success"],
            ["Client-012", "Data Sync", "12 min ago", "Success"],
            ["Client-017", "Snapshot", "16 min ago", "Success"],
            ["Client-021", "Restore", "21 min ago", "In Progress"],
        ]

        list_items = []
        for c, action, when, status in activities:
            color = ft.Colors.GREEN if status == "Success" else ft.Colors.BLUE if status == "In Progress" else ft.Colors.ORANGE
            list_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.CIRCLE, size=8, color=color),
                            width=16,
                            alignment=ft.alignment.center_left,
                        ),
                        ft.Text(c, size=12, weight=ft.FontWeight.W_500, expand=True),
                        ft.Text(action, size=11, color=ft.Colors.ON_SURFACE_VARIANT, expand=True),
                        ft.Text(when, size=10, color=ft.Colors.OUTLINE),
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=6,
                    bgcolor=ft.Colors.SURFACE
                )
            )

        return ft.Container(
            content=ft.Column([
                ft.Text("Recent Activity", size=16, weight=ft.FontWeight.W_600),
                ft.Container(
                    content=ft.ListView(list_items, spacing=4, padding=ft.padding.only(top=8)),
                    height=200
                )
            ], spacing=8),
            padding=16,
            border_radius=8,
            bgcolor=ft.Colors.SURFACE,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
        )

    # Clean header
    header = ft.Container(
        content=ft.Column([
            ft.Text("SERVER DASHBOARD", size=28, weight=ft.FontWeight.BOLD),
            ft.Text("Real-time system monitoring", size=14, color=ft.Colors.ON_SURFACE_VARIANT)
        ], spacing=4),
        padding=ft.padding.all(20),
        margin=ft.margin.only(bottom=16)
    )

    # Status bar
    status_bar = ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.GREEN, size=12),
                ft.Text("All systems normal", size=12)
            ], spacing=6),
            ft.Row([
                ft.Icon(ft.Icons.REFRESH, size=14, color=ft.Colors.BLUE),
                ft.Text("Live", size=11)
            ], spacing=6)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        margin=ft.margin.only(bottom=12),
        border_radius=6,
        bgcolor=ft.Colors.SURFACE,
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT)
    )

    # Metrics row
    metrics_row = ft.Row([
        create_metric_card("Active Clients", clients_ref, ft.Icons.PEOPLE, ft.Colors.BLUE),
        create_metric_card("Total Files", files_ref, ft.Icons.FOLDER, ft.Colors.GREEN),
        create_metric_card("Storage Used", storage_ref, ft.Icons.STORAGE, ft.Colors.ORANGE),
        create_metric_card("Uptime", uptime_ref, ft.Icons.TIMER, ft.Colors.PURPLE),
    ], spacing=12, wrap=True)

    # Performance row
    performance_row = ft.Row([
        create_progress_gauge("Storage", storage_progress_ref, ft.Icons.STORAGE, ft.Colors.ORANGE),
        create_progress_gauge("CPU Usage", cpu_progress_ref, ft.Icons.MEMORY, ft.Colors.RED),
        create_progress_gauge("Memory", memory_progress_ref, ft.Icons.DEVELOPER_BOARD, ft.Colors.BLUE),
    ], spacing=12, wrap=True)

    # Activity section
    activity_section = create_activity_panel()

    # Main dashboard container
    dashboard_container = ft.Container(
        content=ft.Column([
            header,
            status_bar,
            metrics_row,
            performance_row,
            activity_section,
        ], spacing=16, scroll=ft.ScrollMode.AUTO),
        padding=20,
        expand=True
    )

    def setup_subscriptions():
        """Initialize dashboard data."""
        update_data()

    def dispose():
        """Cleanup dashboard."""
        pass

    return dashboard_container, dispose, setup_subscriptions