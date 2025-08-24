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
from flet_server_gui.components.real_database_view import RealDatabaseView
from flet_server_gui.components.analytics_view import AnalyticsView
from flet_server_gui.components.enhanced_stats_card import EnhancedStatsCard
from flet_server_gui.components.real_time_charts import RealTimeCharts
from flet_server_gui.components.quick_actions import QuickActions
from flet_server_gui.components.enhanced_client_management import create_enhanced_client_management
from flet_server_gui.components.real_data_clients import RealDataClientsView, RealDataStatsCard
from flet_server_gui.components.real_data_files import RealDataFilesView, FileTypeBreakdownCard
from flet_server_gui.components.comprehensive_client_management import ComprehensiveClientManagement
from flet_server_gui.components.comprehensive_file_management import ComprehensiveFileManagement
from flet_server_gui.components.dialog_system import DialogSystem, ToastManager
from flet_server_gui.utils.theme_manager import ThemeManager
from flet_server_gui.utils.server_bridge import ServerBridge, MockClient
from flet_server_gui.views.settings_view import SettingsView
from flet_server_gui.views.logs_view import LogsView


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
        
        # Initialize dialog and notification systems
        self.dialog_system = DialogSystem(page)
        self.toast_manager = ToastManager(page)
        
        # NOW initialize components that depend on the theme
        self.status_card = ServerStatusCard(self.server_bridge, page)
        self.client_stats_card = ClientStatsCard(self.server_bridge, page)
        self.control_panel = ControlPanelCard(self.server_bridge, self)
        self.activity_log = ActivityLogCard()
        self.files_view = FilesView(self.server_bridge)
        self.database_view = RealDatabaseView(self.server_bridge)
        self.analytics_view = AnalyticsView(self.server_bridge)
        self.enhanced_stats_card = EnhancedStatsCard()
        self.real_time_charts = RealTimeCharts()
        self.quick_actions = QuickActions(
            on_backup_now=self._on_backup_now,
            on_clear_logs=self._on_clear_logs,
            on_restart_services=self._on_restart_services,
            on_view_clients=self._on_view_clients,
            on_manage_files=self._on_manage_files
        )
        
        # Comprehensive components with dialog integration
        self.comprehensive_client_management = ComprehensiveClientManagement(
            self.server_bridge, 
            self._show_dialog
        )
        self.comprehensive_file_management = ComprehensiveFileManagement(
            self.server_bridge, 
            self._show_dialog
        )
        
        # Settings view with real configuration management
        self.settings_view = SettingsView(page, self.dialog_system, self.toast_manager)
        
        # Logs view with real-time server log monitoring
        self.logs_view = LogsView(page, self.dialog_system, self.toast_manager)
        
        # Legacy simple components (for dashboard stats)
        self.real_data_stats = RealDataStatsCard(self.server_bridge)
        self.file_type_breakdown = FileTypeBreakdownCard(self.server_bridge)
        
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
        asyncio.create_task(self.chart_update_loop())
    
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
                ft.IconButton(ft.Icons.NOTIFICATIONS, tooltip="Notifications", on_click=self._on_notifications),
                ft.IconButton(ft.Icons.HELP, tooltip="Help", on_click=self._on_help),
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
                    ft.Column(col={"sm": 12, "md": 12, "lg": 4}, controls=[self.real_data_stats.build()]),
                    ft.Column(col={"sm": 12, "md": 12, "lg": 6}, controls=[self.enhanced_stats_card]),
                    ft.Column(col={"sm": 12, "md": 12, "lg": 6}, controls=[self.real_time_charts]),
                    ft.Column(col={"sm": 12, "md": 12, "lg": 12}, controls=[self.quick_actions]),
                    ft.Column(col=12, controls=[self.activity_log.build()]),
                ],
                spacing=20,
            )
        ], spacing=24, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    
    def get_clients_view(self) -> ft.Control:
        """Get the comprehensive clients management view"""
        clients_control = self.comprehensive_client_management.build()
        # Load data immediately
        self.comprehensive_client_management.did_mount()
        return clients_control
    
    def get_files_view(self) -> ft.Control:
        """Get the comprehensive files management view"""
        files_control = self.comprehensive_file_management.build()
        # Load data immediately
        self.comprehensive_file_management.did_mount()
        return files_control
    
    def get_database_view(self) -> ft.Control:
        """Get the real database management view"""
        return self.database_view.build()
    
    def get_analytics_view(self) -> ft.Control:
        """Get the analytics and reporting view"""
        return self.analytics_view.build()
    
    def get_logs_view(self) -> ft.Control:
        """Get the comprehensive real-time logs view"""
        return self.logs_view.create_logs_view()
    
    def get_settings_view(self) -> ft.Control:
        """Get the comprehensive settings view with real configuration management"""
        return self.settings_view.create_settings_view()

    def _on_backup_now(self, e):
        """Handle backup now action"""
        self.activity_log.add_entry("Quick Actions", "Backup initiated", "INFO")
        # In a real implementation, this would trigger a backup
        # For now, we'll just show a notification
        self._show_notification_sync("Backup started")

    def _on_clear_logs(self, e):
        """Handle clear logs action"""
        self.activity_log.clear_log()
        self._show_notification_sync("Logs cleared")

    def _on_restart_services(self, e):
        """Handle restart services action"""
        self.activity_log.add_entry("Quick Actions", "Services restart initiated", "INFO")
        # In a real implementation, this would restart services
        # For now, we'll just show a notification
        self._show_notification_sync("Services restart initiated")

    def _on_view_clients(self, e):
        """Handle view clients action"""
        self.switch_view("clients")

    def _on_manage_files(self, e):
        """Handle manage files action"""
        self.switch_view("files")

    def _get_sample_clients(self):
        """Get sample client data for demonstration"""
        import datetime
        return [
            {
                "client_id": "client_001",
                "ip": "192.168.1.101",
                "status": "online",
                "connected": "2025-08-23 10:30:16",
                "activity": "2025-08-23 10:45:22"
            },
            {
                "client_id": "client_002",
                "ip": "192.168.1.102",
                "status": "offline",
                "connected": "2025-08-22 09:15:33",
                "activity": "2025-08-22 14:22:18"
            },
            {
                "client_id": "client_003",
                "ip": "192.168.1.103",
                "status": "active",
                "connected": "2025-08-23 08:45:12",
                "activity": "2025-08-23 10:40:05"
            },
            {
                "client_id": "client_004",
                "ip": "192.168.1.104",
                "status": "online",
                "connected": "2025-08-23 07:30:45",
                "activity": "2025-08-23 10:35:30"
            },
            {
                "client_id": "client_005",
                "ip": "192.168.1.105",
                "status": "offline",
                "connected": "2025-08-21 16:22:18",
                "activity": "2025-08-21 18:45:33"
            }
        ]

    async def chart_update_loop(self):
        """Loop to update real-time charts"""
        while True:
            try:
                if self.current_view == "dashboard":
                    await self.real_time_charts.update_charts()
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                print(f"Chart update error: {e}")
                await asyncio.sleep(5)

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

    def _on_export_logs(self, e):
        """Handle export logs button click"""
        self._show_notification_sync("Logs exported successfully")

    def _on_clear_logs_view(self, e):
        """Handle clear logs button click"""
        self._show_notification_sync("Logs cleared")

    def _on_notifications(self, e):
        """Handle notifications button click"""
        self._show_notification_sync("No new notifications")

    def _on_help(self, e):
        """Handle help button click"""
        self._show_notification_sync("Help documentation would be shown here")
    
    async def show_notification(self, message: str, is_error: bool = False):
        """Async method to show notification."""
        self._show_notification_sync(message, is_error)
    
    def _show_dialog(self, dialog_type: str, title: str, message: str, **kwargs):
        """Show dialog using the dialog system - bridge method for comprehensive components"""
        if dialog_type == "info":
            self.dialog_system.show_info_dialog(title, message, kwargs.get('on_close'))
        elif dialog_type == "success":
            self.dialog_system.show_success_dialog(title, message, kwargs.get('on_close'))
        elif dialog_type == "error":
            self.dialog_system.show_error_dialog(title, message, kwargs.get('on_close'))
        elif dialog_type == "warning":
            self.dialog_system.show_warning_dialog(title, message, kwargs.get('on_close'))
        elif dialog_type == "confirmation":
            self.dialog_system.show_confirmation_dialog(
                title, message,
                kwargs.get('on_confirm', lambda: None),
                kwargs.get('on_cancel'),
                kwargs.get('confirm_text', 'Confirm'),
                kwargs.get('cancel_text', 'Cancel'),
                kwargs.get('danger', False)
            )
        elif dialog_type == "input":
            self.dialog_system.show_input_dialog(
                title, message,
                kwargs.get('on_submit', lambda x: None),
                kwargs.get('on_cancel'),
                kwargs.get('placeholder', ''),
                kwargs.get('initial_value', ''),
                kwargs.get('multiline', False)
            )
        elif dialog_type == "progress":
            return self.dialog_system.show_progress_dialog(
                title, message,
                kwargs.get('progress_value'),
                kwargs.get('cancelable', True),
                kwargs.get('on_cancel')
            )
        elif dialog_type == "custom":
            self.dialog_system.show_custom_dialog(
                title, 
                kwargs.get('content'),
                kwargs.get('actions'),
                kwargs.get('modal', True),
                kwargs.get('scrollable', False)
            )
    
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