#!/usr/bin/env python3
"""
Client Statistics Card Component
Material Design 3 card showing client connection stats and metrics.
"""

import flet as ft
from flet_server_gui.utils.server_bridge import ServerBridge, ServerInfo

class ClientStatsCard:
    """Client statistics card with connection metrics"""
    
    def __init__(self, server_bridge: ServerBridge, page: ft.Page):
        self.server_bridge = server_bridge
        self.page = page
        
        # UI components with Refs for dynamic updates
        self.connected_count = ft.Ref[ft.Text]()
        self.total_count = ft.Ref[ft.Text]()
        self.transfers_count = ft.Ref[ft.Text]()
        self.connection_indicator = ft.Ref[ft.Icon]()

    def build(self) -> ft.Card:
        """Build the client statistics card, letting the theme handle colors."""
        header = ft.Row([
            ft.Icon(ref=self.connection_indicator, name=ft.Icons.PEOPLE_ALT, size=24),
            ft.Text("Client Statistics", style=ft.TextThemeStyle.TITLE_LARGE)
        ], spacing=12)
        
        primary_metric = ft.Container(
            content=ft.Column([
                ft.Text(ref=self.connected_count, value="0", style=ft.TextThemeStyle.DISPLAY_MEDIUM, weight=ft.FontWeight.BOLD),
                ft.Text("Connected", style=ft.TextThemeStyle.LABEL_LARGE)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            padding=ft.padding.all(12),
            border_radius=12
        )
        
        secondary_metrics = ft.Row([
            ft.Column([
                ft.Text(ref=self.total_count, value="0", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("Total Registered", style=ft.TextThemeStyle.BODY_MEDIUM)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
            ft.VerticalDivider(),
            ft.Column([
                ft.Text(ref=self.transfers_count, value="0", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("Active Transfers", style=ft.TextThemeStyle.BODY_MEDIUM)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4)
        ], alignment=ft.MainAxisAlignment.SPACE_AROUND, expand=True)
        
        card_content = ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                primary_metric,
                secondary_metrics
            ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=ft.padding.all(20),
            width=400,
            border_radius=12
        )
        
        return ft.Card(content=card_content, elevation=1)

    def update_stats(self, server_info: ServerInfo):
        """Update statistics with new data."""
        if not self.connected_count.current:
            return
        
        self.connected_count.current.value = str(server_info.connected_clients)
        self.total_count.current.value = str(server_info.total_clients)
        self.transfers_count.current.value = str(server_info.active_transfers)
        
        # Enhanced icon animation for client count changes
        if hasattr(self.page.theme, 'color_scheme'):
            if server_info.connected_clients > 0:
                # Animate icon color change
                self.connection_indicator.current.color = self.page.theme.color_scheme.primary
                
                # Add pulse animation for new connections
                if hasattr(self.connected_count.current, '_last_value'):
                    if int(server_info.connected_clients) > int(self.connected_count.current._last_value):
                        # Pulse animation
                        original_scale = getattr(self.connection_indicator.current, 'scale', ft.Scale(1))
                        self.connection_indicator.current.scale = ft.Scale(1.3)
                        self.page.update()
                        self.connection_indicator.current.scale = original_scale
                        self.page.update()
                        
                self.connected_count.current._last_value = str(server_info.connected_clients)
            else:
                self.connection_indicator.current.color = self.page.theme.color_scheme.outline
        else:
            self.connection_indicator.current.color = ft.Colors.BLUE if server_info.connected_clients > 0 else ft.Colors.GREY
            
        self.page.update()

    async def update_real_time(self):
        """Update stats with real-time data from server bridge"""
        server_info = await self.server_bridge.get_server_status()
        self.update_stats(server_info)