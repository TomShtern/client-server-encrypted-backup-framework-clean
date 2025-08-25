#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flet Material Design 3 Server GUI - Main Application
Desktop application for managing the encrypted backup server.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import utf8_solution to fix encoding issues
try:
    import Shared.utils.utf8_solution
    print("[INFO] UTF-8 solution imported successfully")
except ImportError as e:
    # Try alternative path
    utf8_path = os.path.join(os.path.dirname(__file__), "..", "Shared", "utils")
    if utf8_path not in sys.path:
        sys.path.insert(0, utf8_path)
    try:
        import utf8_solution
        print("[INFO] UTF-8 solution imported via alternative path")
    except ImportError:
        print("[WARNING] utf8_solution import failed, continuing without it")
        print(f"[DEBUG] Import error: {e}")
import flet as ft
import asyncio
from datetime import datetime
from typing import Callable

from flet_server_gui.components.server_status_card import ServerStatusCard
from flet_server_gui.components.client_stats_card import ClientStatsCard  
from flet_server_gui.components.control_panel_card import ControlPanelCard
from flet_server_gui.components.activity_log_card import ActivityLogCard
from flet_server_gui.components.navigation import NavigationManager
from flet_server_gui.components.real_database_view import RealDatabaseView
from flet_server_gui.components.enhanced_performance_charts import EnhancedPerformanceCharts
from flet_server_gui.components.enhanced_stats_card import EnhancedStatsCard
from flet_server_gui.components.quick_actions import QuickActions
from flet_server_gui.components.real_data_clients import RealDataStatsCard
from flet_server_gui.components.comprehensive_client_management import ComprehensiveClientManagement
from flet_server_gui.components.comprehensive_file_management import ComprehensiveFileManagement
from flet_server_gui.components.dialog_system import DialogSystem, ToastManager
from flet_server_gui.utils.theme_manager import ThemeManager
from flet_server_gui.utils.server_bridge import ServerBridge
from flet_server_gui.views.settings_view import SettingsView
from flet_server_gui.views.logs_view import LogsView
from flet_server_gui.actions import FileActions


class ServerGUIApp:
    """Main application class - Material Design 3 desktop server GUI"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.server_bridge = ServerBridge()
        self.theme_manager = ThemeManager(page)
        self.current_view = "dashboard"
        self.active_view_instance = None
        self.nav_rail_visible = True

        # Apply theme and configure page FIRST
        self.setup_application()
        
        # Initialize dialog and notification systems
        self.dialog_system = DialogSystem(page)
        self.toast_manager = ToastManager(page)
        
        # Initialize action handlers
        self.file_actions = FileActions(self.server_bridge)

        # NOW initialize components that depend on the theme
        self.status_card = ServerStatusCard(self.server_bridge, page)
        self.client_stats_card = ClientStatsCard(self.server_bridge, page)
        self.activity_log = ActivityLogCard()
        self.control_panel = ControlPanelCard(self.server_bridge, self.page, self.show_notification, self.activity_log.add_entry)
        self.database_view = RealDatabaseView(self.server_bridge)
        self.analytics_view = EnhancedPerformanceCharts(self.server_bridge, page)
        self.enhanced_stats_card = EnhancedStatsCard()
        self.enhanced_stats_card.toast_manager = self.toast_manager
        self.quick_actions = QuickActions(
            page=page,
            on_backup_now=self._on_backup_now,
            on_clear_logs=self._on_clear_logs,
            on_restart_services=self._on_restart_services,
            on_view_clients=self._on_view_clients,
            on_manage_files=self._on_manage_files
        )
        
        self.comprehensive_client_management = ComprehensiveClientManagement(
            self.server_bridge, 
            self.dialog_system,
            self.toast_manager,
            self.page
        )
        self.comprehensive_file_management = ComprehensiveFileManagement(
            self.server_bridge, 
            self.dialog_system,
            self.toast_manager,
            self.page
        )
        
        self.settings_view = SettingsView(page, self.dialog_system, self.toast_manager)
        self.logs_view = LogsView(page, self.dialog_system, self.toast_manager)
        self.real_data_stats = RealDataStatsCard(self.server_bridge)
        self.navigation = NavigationManager(page, self.switch_view)
        
        self.activity_log.set_page(page)

        self.build_ui()
        
        self.page.window_to_front = True
        self.page.on_connect = self._on_page_connect
    
    async def _on_page_connect(self, e):
        """Start background tasks when the page is connected."""
        asyncio.create_task(self.monitor_loop())
    
    def setup_application(self):
        """Configure the desktop application and apply the theme."""
        self.page.title = "Encrypted Backup Server - Control Panel"
        self.page.window_width = 1400
        self.page.window_height = 900
        self.page.window_min_width = 1000
        self.page.window_min_height = 750
        self.page.window_resizable = True
        self.theme_manager.apply_theme()
        self.page.padding = ft.padding.all(20)
        self.page.spacing = 0
        
        self.theme_tokens = self.theme_manager.get_tokens()
    
    def build_ui(self):
        """Build the main UI structure with animations."""
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
            actions=[
                self.theme_toggle_button,
                ft.IconButton(ft.Icons.NOTIFICATIONS, tooltip="Notifications", on_click=self._on_notifications),
                ft.IconButton(ft.Icons.HELP, tooltip="Help", on_click=self._on_help),
            ]
        )
        
        initial_view = self.get_dashboard_view()
        self.active_view_instance = initial_view

        self.content_area = ft.AnimatedSwitcher(
            content=initial_view,
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=300,
            expand=True
        )
        
        self.nav_rail = self.navigation.build()
        
        self.main_layout = ft.Row([
            self.nav_rail,
            ft.VerticalDivider(width=1),
            ft.Container(
                content=self.content_area, 
                padding=ft.padding.all(20), 
                expand=True
            )
        ], expand=True, spacing=0)
        
        self.page.appbar = app_bar
        self.page.add(self.main_layout)
    
    def toggle_navigation(self, e):
        """Toggle navigation rail visibility"""
        self.nav_rail_visible = not self.nav_rail_visible
        self.nav_rail.visible = self.nav_rail_visible
        self.hamburger_button.icon = ft.Icons.MENU if self.nav_rail_visible else ft.Icons.MENU_OPEN
        self.page.update()
    
    def get_dashboard_view(self) -> ft.Control:
        """Simplified dashboard prioritizing core components."""
        return ft.Column([
            ft.Text("Dashboard", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Divider(),
            ft.ResponsiveRow(
                controls=[
                    ft.Column(col={"xs": 12, "sm": 12, "md": 6, "lg": 4, "xl": 4}, controls=[self.status_card.build()]),
                    ft.Column(col={"xs": 12, "sm": 12, "md": 6, "lg": 4, "xl": 4}, controls=[self.control_panel.build()]),  
                    ft.Column(col={"xs": 12, "sm": 12, "md": 12, "lg": 4, "xl": 4}, controls=[self.enhanced_stats_card]),
                ],
                spacing=16,
            ),
            ft.Container(height=16),
            ft.ResponsiveRow(
                controls=[
                    ft.Column(col={"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6}, controls=[self.real_data_stats.build()]),
                    ft.Column(col={"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6}, controls=[self.quick_actions]),
                ],
                spacing=16,
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Recent Activity", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.Text("View detailed logs in the Logs section", 
                           style=ft.TextThemeStyle.BODY_MEDIUM,
                           color=ft.Colors.OUTLINE),
                    ft.FilledButton(
                        "View Full Logs",
                        icon=ft.Icons.HISTORY,
                        on_click=lambda _: self.switch_view("logs")
                    )
                ]),
                padding=16,
                margin=ft.margin.only(top=16)
            )
        ], spacing=24, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    def get_clients_view(self) -> ft.Control:
        return self.comprehensive_client_management.build()
    
    def get_files_view(self) -> ft.Control:
        return self.comprehensive_file_management.build()
    
    def get_database_view(self) -> ft.Control:
        return self.database_view.build()
    
    def get_analytics_view(self) -> ft.Control:
        return self.analytics_view.create_enhanced_charts_view()
    
    def get_logs_view(self) -> ft.Control:
        return self.logs_view
    
    def get_settings_view(self) -> ft.Control:
        return self.settings_view.create_settings_view()

    async def _on_backup_now(self, e):
        """Handle backup now action by running the file cleanup job."""
        self.activity_log.add_entry("Quick Actions", "Cleanup job initiated", "INFO")
        result = await self.file_actions.cleanup_old_files(days_threshold=30)
        if result.success:
            cleaned_count = result.data.get('cleaned_files', 0)
            await self.show_notification(f"Cleanup successful: {cleaned_count} old files removed.")
        else:
            await self.show_notification(f"Cleanup failed: {result.error_message}", is_error=True)

    async def _on_clear_logs(self, e):
        """Handle clear logs action."""
        await self.activity_log.clear_log(e)

    async def _on_restart_services(self, e):
        """Handle restart services action."""
        await self.control_panel.restart_server(e)

    def _on_view_clients(self, e):
        self.switch_view("clients")

    def _on_manage_files(self, e):
        self.switch_view("files")

    def switch_view(self, view_name: str):
        """Switch to a different view, managing component lifecycles."""
        if self.current_view == view_name:
            return

        # Stop the current view if it has a stop method
        if self.active_view_instance and hasattr(self.active_view_instance, 'stop'):
            self.active_view_instance.stop()

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
        
        new_content_instance = view_map.get(view_name, self.get_dashboard_view)()
        
        # Special handling for view classes vs created controls
        if view_name == "logs":
            self.active_view_instance = self.logs_view
            new_content = self.logs_view.create_logs_view()
        else:
            self.active_view_instance = new_content_instance
            new_content = new_content_instance

        # Start the new view if it has a start method
        if hasattr(self.active_view_instance, 'start'):
            self.active_view_instance.start()

        self.content_area.content = new_content
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

    def _on_notifications(self, e):
        """Handle notifications button click."""
        self.dialog_system.show_info_dialog("Notifications", "No new notifications.")

    def _on_help(self, e):
        """Handle help button click."""
        self.dialog_system.show_info_dialog(
            "About",
            "Encrypted Backup Server - Control Panel\nVersion: 1.0.0\nDeveloped with Flet and Material Design 3."
        )
    
    async def show_notification(self, message: str, is_error: bool = False):
        """Async method to show notification."""
        if is_error:
            self.toast_manager.show_error(message)
        else:
            self.toast_manager.show_success(message)
    
    async def monitor_loop(self):
        while True:
            try:
                if self.current_view == "dashboard":
                    await self.status_card.update_real_time()
                    await self.client_stats_card.update_real_time()
                elif self.current_view == "analytics":
                    # This view manages its own updates, so we don't call it here.
                    pass
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
