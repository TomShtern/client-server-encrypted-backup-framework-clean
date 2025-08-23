#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flet Material Design 3 Server GUI - Main Application
Desktop application for managing the encrypted backup server.
"""

import Shared.utils.utf8_solution
import flet as ft
import asyncio
from datetime import datetime

from flet_server_gui.components.server_status_card import ServerStatusCard
from flet_server_gui.components.client_stats_card import ClientStatsCard  
from flet_server_gui.components.control_panel_card import ControlPanelCard
from flet_server_gui.components.activity_log_card import ActivityLogCard
from flet_server_gui.components.navigation import NavigationManager
from flet_server_gui.components.files_view import FilesView
from flet_server_gui.components.database_view import DatabaseView
from flet_server_gui.components.analytics_view import AnalyticsView
from flet_server_gui.utils.theme_manager import ThemeManager
from flet_server_gui.utils.server_bridge import ServerBridge, MockClient


class ServerGUIApp:
    """Main application class - Material Design 3 desktop server GUI"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.server_bridge = ServerBridge()
        self.theme_manager = ThemeManager(page)
        self.current_view = "dashboard"
        self.nav_rail_visible = True

        # Apply theme and configure page FIRST
        self.setup_application()
        
        # NOW initialize components that depend on the theme
        self.status_card = ServerStatusCard(self.server_bridge, page)
        self.client_stats_card = ClientStatsCard(self.server_bridge, page)
        self.control_panel = ControlPanelCard(self.server_bridge, self)
        self.activity_log = ActivityLogCard()
        self.files_view = FilesView(self.server_bridge)
        self.database_view = DatabaseView(self.server_bridge)
        self.analytics_view = AnalyticsView(self.server_bridge)
        self.navigation = NavigationManager(page, self.switch_view)
        
        self.activity_log.set_page(page)

        # Build the UI with the initialized components
        self.build_ui()
        
        # Schedule background tasks to start after the page is fully initialized
        self.page.window_to_front = True
        self.page.on_connect = self._on_page_connect
    
    async def _on_page_connect(self, e):
        """Start background tasks when the page is connected."""
        asyncio.create_task(self.monitor_loop())
    
    def setup_application(self):
        """Configure the desktop application and apply the theme."""
        self.page.title = "Encrypted Backup Server - Control Panel"
        self.page.window_width = 1280
        self.page.window_height = 820
        self.page.window_min_width = 900
        self.page.window_min_height = 700
        self.theme_manager.apply_theme()
        self.page.padding = 0
        self.page.spacing = 0
        
        # Store theme tokens for use in components
        self.theme_tokens = self.theme_manager.get_tokens()
    
    def build_ui(self):
        """Build the main UI structure with animations."""
        # Create hamburger menu button
        self.hamburger_button = ft.IconButton(
            icon=ft.Icons.MENU,
            tooltip="Toggle Navigation",
            on_click=self.toggle_navigation
        )
        
        self.theme_toggle_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle Theme (Light/Dark/System)",
            on_click=self.toggle_theme
        )

        app_bar = ft.AppBar(
            title=ft.Text("Server Control Panel", weight=ft.FontWeight.W_500),
            leading=self.hamburger_button,
            # Let the theme handle the background color automatically
            actions=[
                self.theme_toggle_button,
                ft.IconButton(ft.Icons.NOTIFICATIONS, tooltip="Notifications"),
                ft.IconButton(ft.Icons.HELP, tooltip="Help"),
            ]
        )
        
        self.content_area = ft.AnimatedSwitcher(
            content=self.get_dashboard_view(),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=300,
            expand=True
        )
        
        # Build the navigation rail now that the theme is set
        self.nav_rail = self.navigation.build()
        
        # Create main layout with collapsible navigation
        self.main_layout = ft.Row([
            self.nav_rail,
            ft.VerticalDivider(width=1),
            ft.Container(self.content_area, padding=ft.padding.all(20), expand=True)
        ], expand=True, spacing=0)
        
        self.page.appbar = app_bar
        self.page.add(self.main_layout)
    
    def toggle_navigation(self, e):
        """Toggle navigation rail visibility"""
        self.nav_rail_visible = not self.nav_rail_visible
        if self.nav_rail_visible:
            self.nav_rail.visible = True
            self.hamburger_button.icon = ft.Icons.MENU
        else:
            self.nav_rail.visible = False
            self.hamburger_button.icon = ft.Icons.MENU_OPEN
        self.page.update()
    
    def get_dashboard_view(self) -> ft.Control:
        return ft.Column([
            ft.Text("Dashboard", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Divider(),
            ft.ResponsiveRow(
                controls=[
                    ft.Column(col={"sm": 12, "md": 6, "lg": 4}, controls=[self.status_card.build()]),
                    ft.Column(col={"sm": 12, "md": 6, "lg": 4}, controls=[self.control_panel.build()]),
                    ft.Column(col={"sm": 12, "md": 12, "lg": 4}, controls=[self.client_stats_card.build()]),
                    ft.Column(col=12, controls=[self.activity_log.build()]),
                ],
                spacing=20,
            )
        ], spacing=24, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    def get_clients_view(self) -> ft.Control:
        clients = self.server_bridge.get_client_list()
        client_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Client ID")),
                ft.DataColumn(ft.Text("IP Address")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Connected Since"), numeric=True),
            ],
            rows=[
                ft.DataRow(cells=[
                    ft.DataCell(ft.Row([ft.Icon(ft.Icons.COMPUTER), ft.Text(c.client_id)])),
                    ft.DataCell(ft.Text(c.address)),
                    ft.DataCell(ft.Chip(ft.Text(c.status))),
                    ft.DataCell(ft.Text(c.connected_at.strftime("%Y-%m-%d %H:%M"))),
                ]) for c in clients
            ]
        )
        # Use a default color if theme is not fully loaded
        border_color = ft.Colors.OUTLINE if not self.page.theme or not self.page.theme.color_scheme else self.page.theme.color_scheme.outline
        return ft.Column([
            ft.Text("Client Management", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Divider(),
            ft.Text(f"{len(clients)} clients currently connected."),
            ft.Container(client_table, border=ft.border.all(1, border_color), border_radius=8, padding=10, expand=True)
        ], spacing=24, expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    
    def get_files_view(self) -> ft.Control:
        """Get the files management view"""
        return self.files_view.build()
    
    def get_database_view(self) -> ft.Control:
        """Get the database management view"""
        return self.database_view.build()
    
    def get_analytics_view(self) -> ft.Control:
        """Get the analytics and reporting view"""
        return self.analytics_view.build()
    
    def get_logs_view(self) -> ft.Control:
        """Get the logs view (placeholder)"""
        # Create a scrollable container for logs
        log_container = ft.Container(
            content=ft.Column([
                ft.Text("2025-08-23 10:30:15 [INFO] Server started successfully"),
                ft.Text("2025-08-23 10:30:16 [INFO] Client client_001 connected"),
                ft.Text("2025-08-23 10:30:22 [SUCCESS] File transfer completed"),
                ft.Text("2025-08-23 10:35:44 [WARNING] CRC mismatch detected"),
                ft.Text("2025-08-23 10:35:45 [INFO] Retrying transfer..."),
                ft.Text("2025-08-23 10:35:50 [SUCCESS] Transfer completed on retry"),
            ], spacing=8, scroll=ft.ScrollMode.AUTO),
            padding=10,
            height=300,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=4,
        )
        
        return ft.Column([
            ft.Text("Logs", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Divider(),
            ft.Text("Detailed server logs will be displayed here."),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Log Viewer", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.TextField(label="Filter logs...", icon=ft.Icons.SEARCH),
                        log_container,
                        ft.Row([
                            ft.FilledButton("Export Logs", icon=ft.Icons.DOWNLOAD),
                            ft.OutlinedButton("Clear Logs", icon=ft.Icons.CLEAR),
                        ], alignment=ft.MainAxisAlignment.END)
                    ], spacing=16),
                    padding=20,
                )
            )
        ], spacing=24, expand=True, scroll=ft.ScrollMode.ADAPTIVE)
    
    def get_settings_view(self) -> ft.Control:
        def on_setting_change(e, setting_name):
            # Show notification directly without async task
            self._show_notification_sync(f'{setting_name} updated to "{e.control.value}"')

        def on_save_settings(e):
            # Show notification directly without async task
            self._show_notification_sync("Settings saved!")

        return ft.Column([
            ft.Text("Settings", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Divider(),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Server Configuration", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        ft.TextField(label="Port", value="1256", on_change=lambda e: on_setting_change(e, "Port")),
                        ft.TextField(label="Max Clients", value="100", on_change=lambda e: on_setting_change(e, "Max Clients")),
                        ft.TextField(label="Backup Directory", value="./backups", on_change=lambda e: on_setting_change(e, "Backup Directory")),
                        ft.Switch(label="Auto-start server", value=True, on_change=lambda e: on_setting_change(e, "Auto-start")),
                        ft.Switch(label="Enable logging", value=True, on_change=lambda e: on_setting_change(e, "Enable logging")),
                        ft.Dropdown(
                            label="Log Level",
                            options=[
                                ft.dropdown.Option("DEBUG"),
                                ft.dropdown.Option("INFO"),
                                ft.dropdown.Option("WARNING"),
                                ft.dropdown.Option("ERROR"),
                            ],
                            value="INFO",
                            on_change=lambda e: on_setting_change(e, "Log Level")
                        ),
                        ft.FilledButton("Save Settings", icon=ft.Icons.SAVE, on_click=on_save_settings)
                    ], spacing=16),
                    padding=20
                ),
                width=500
            )
        ], spacing=24)

    def switch_view(self, view_name: str):
        """Switch to a different view with animation."""
        self.current_view = view_name
        view_map = {
            "dashboard": self.get_dashboard_view,
            "clients": self.get_clients_view,
            "files": self.get_files_view,
            "database": self.get_database_view,
            "analytics": self.get_analytics_view,
            "logs": self.get_logs_view,
            "settings": self.get_settings_view
        }
        
        # Add smooth transition animation
        if self.content_area:
            # Fade out current content
            self.content_area.opacity = 1
            self.content_area.animate_opacity = ft.Animation(150, ft.AnimationCurve.EASE_IN)
            self.page.update()
            self.content_area.opacity = 0
            self.page.update()
            
            # Update content
            new_content = view_map.get(view_name, self.get_dashboard_view)()
            self.content_area.content = new_content
            
            # Fade in new content
            self.content_area.opacity = 0
            self.content_area.animate_opacity = ft.Animation(150, ft.AnimationCurve.EASE_OUT)
            self.page.update()
            self.content_area.opacity = 1
            self.page.update()
            
        self.page.update()

    def toggle_theme(self, e):
        self.theme_manager.toggle_theme()
        mode = self.page.theme_mode
        if mode == ft.ThemeMode.DARK:
            self.theme_toggle_button.icon = ft.Icons.LIGHT_MODE
        elif mode == ft.ThemeMode.LIGHT:
            self.theme_toggle_button.icon = ft.Icons.WB_SUNNY
        else:
            self.theme_toggle_button.icon = ft.Icons.SETTINGS_BRIGHTNESS
        self.page.update()

    def _show_notification_sync(self, message: str, is_error: bool = False):
        """Helper method to show notification in sync context."""
        # Ensure theme is available
        if not self.page.theme or not self.page.theme.color_scheme:
            # Fallback to default colors if theme is not fully loaded
            bgcolor = ft.Colors.RED_100 if is_error else ft.Colors.BLUE_100
            content_color = ft.Colors.RED_900 if is_error else ft.Colors.BLUE_900
        else:
            color_scheme = self.page.theme.color_scheme
            bgcolor = color_scheme.error_container if is_error else color_scheme.secondary_container
            content_color = color_scheme.on_error_container if is_error else color_scheme.on_secondary_container
        
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message, color=content_color, weight=ft.FontWeight.BOLD), bgcolor=bgcolor, duration=3000)
        self.page.snack_bar.open = True
        self.page.update()
    
    async def show_notification(self, message: str, is_error: bool = False):
        """Async method to show notification."""
        self._show_notification_sync(message, is_error)
    
    async def monitor_loop(self):
        while True:
            try:
                if self.current_view == "dashboard":
                    await self.status_card.update_real_time()
                    await self.client_stats_card.update_real_time()
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Monitor loop error: {e}")
                self.activity_log.add_entry("Monitor", f"Loop error: {e}", "ERROR")
                await asyncio.sleep(5)

def main(page: ft.Page):
    app = ServerGUIApp(page)

if __name__ == "__main__":
    print("Starting Encrypted Backup Server GUI...")
    ft.app(target=main, assets_dir="assets")