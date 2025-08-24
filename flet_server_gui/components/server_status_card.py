#!/usr/bin/env python3
"""
Server Status Card Component
Material Design 3 card showing server status, uptime, and connection info.
"""

import flet as ft
import asyncio
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flet_server_gui.utils.server_bridge import ServerBridge, ServerInfo


class ServerStatusCard:
    """Server status card with real-time updates and self-updating uptime"""
    
    def __init__(self, server_bridge: "ServerBridge", page: ft.Page):
        self.server_bridge = server_bridge
        self.page = page
        self.server_info = None
        self._is_running = False
        self._uptime_task = None # Task reference for the uptime ticker
        self._ticker_started = False # Flag to ensure ticker starts only once

        # UI components with Refs for dynamic updates
        self.status_chip = ft.Ref[ft.Chip]()
        self.status_icon = ft.Ref[ft.Icon]()
        self.address_text = ft.Ref[ft.Text]()
        self.uptime_text = ft.Ref[ft.Text]()
        self.clients_text = ft.Ref[ft.Text]()

    def build(self) -> ft.Card:
        """Build the server status card with fully responsive layout"""
        header_row = ft.Row([
            ft.Row([
                ft.Icon(ref=self.status_icon, name=ft.Icons.RADIO_BUTTON_OFF, size=20),
                ft.Text("Server Status", style=ft.TextThemeStyle.TITLE_LARGE)
            ], spacing=12),
            ft.Chip(ref=self.status_chip, label=ft.Text("OFFLINE", weight=ft.FontWeight.BOLD), elevation=0)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        details_column = ft.Column([
            ft.Text(ref=self.address_text, value="Address: N/A", style=ft.TextThemeStyle.BODY_MEDIUM),
            ft.Text(f"Port: {getattr(self.server_info, 'port', 'N/A') if self.server_info else 'N/A'}", style=ft.TextThemeStyle.BODY_MEDIUM),
            ft.Text(ref=self.uptime_text, value="Uptime: 00:00:00", style=ft.TextThemeStyle.BODY_MEDIUM),
            ft.Text(ref=self.clients_text, value="Connected: 0 clients", style=ft.TextThemeStyle.BODY_MEDIUM)
        ], spacing=8)
        
        # Use responsive layout with adaptive container
        from ..layouts.responsive_utils import ResponsiveBuilder
        from ..layouts.breakpoint_manager import BreakpointManager
        
        # Get current screen width (default to 1200 if not available)
        screen_width = getattr(self.page, 'window_width', 1200) or 1200
        
        # Create fully responsive container without any hardcoded dimensions
        card_content = ResponsiveBuilder.create_adaptive_container(
            content=ft.Column([header_row, ft.Divider(), details_column], spacing=16),
            responsive_padding=True,
            responsive_margin=True,
            expand=True
        )
        
        # Use responsive card creation
        return ResponsiveBuilder.create_responsive_card(
            content=card_content,
            elevation=1,
            expand=True
        )

    def update_status(self, server_info):
        """Update the status card with new server information."""
        if not self.status_chip.current:
            return

        self.server_info = server_info
        self._is_running = getattr(server_info, 'running', False)

        if self._is_running:
            self.status_chip.current.label.value = "ONLINE"
            # Use theme colors for status indication
            if hasattr(self.page.theme, 'color_scheme'):
                self.status_chip.current.bgcolor = self.page.theme.color_scheme.primary_container
                self.status_chip.current.label.color = self.page.theme.color_scheme.on_primary_container
            self.status_icon.current.name = ft.Icons.RADIO_BUTTON_CHECKED
            self.status_icon.current.color = ft.Colors.GREEN if not hasattr(self.page.theme, 'color_scheme') else self.page.theme.color_scheme.primary
            self.address_text.current.value = f"Address: {getattr(server_info, 'host', 'N/A')}:{getattr(server_info, 'port', 'N/A')}"
            self.clients_text.current.value = f"Connected: {getattr(server_info, 'connected_clients', 0)} clients"
        else:
            self.status_chip.current.label.value = "OFFLINE"
            # Use theme colors for status indication
            if hasattr(self.page.theme, 'color_scheme'):
                self.status_chip.current.bgcolor = self.page.theme.color_scheme.secondary_container
                self.status_chip.current.label.color = self.page.theme.color_scheme.on_secondary_container
            self.status_icon.current.name = ft.Icons.RADIO_BUTTON_OFF
            self.status_icon.current.color = ft.Colors.GREY if not hasattr(self.page.theme, 'color_scheme') else self.page.theme.color_scheme.outline
            self.address_text.current.value = "Address: N/A"
            self.uptime_text.current.value = "Uptime: 00:00:00"
            self.clients_text.current.value = "Connected: 0 clients"
            
        self.page.update()

    async def uptime_ticker(self):
        """A dedicated task to update the uptime every second."""
        while True:
            if self._is_running and getattr(self.server_info, 'uptime_start', None) and self.uptime_text.current:
                uptime = datetime.now() - self.server_info.uptime_start
                hours, remainder = divmod(int(uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                self.uptime_text.current.value = f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
                try:
                    await self.page.update_async()
                except Exception:
                    pass
            await asyncio.sleep(1)

    async def update_real_time(self):
        """Update status with real-time data from server bridge and start ticker if needed."""
        if not self._ticker_started:
            asyncio.create_task(self.uptime_ticker())
            self._ticker_started = True

        server_info = await self.server_bridge.get_server_status()
        self.update_status(server_info)