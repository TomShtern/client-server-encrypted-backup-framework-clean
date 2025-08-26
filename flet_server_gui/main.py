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

# Use only working components to avoid complex import chains
from flet_server_gui.components.control_panel_card import ControlPanelCard
from flet_server_gui.components.quick_actions import QuickActions
from flet_server_gui.ui.navigation import NavigationManager
from flet_server_gui.ui.dialogs import DialogSystem, ToastManager
from flet_server_gui.ui.theme import ThemeManager
from flet_server_gui.utils.server_bridge import ServerBridge
# Direct import to avoid __init__.py issues
try:
    from flet_server_gui.views.settings_view import SettingsView
except ImportError:
    SettingsView = None
try:
    from flet_server_gui.views.logs_view import LogsView
except ImportError:
    LogsView = None
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

        # NOW initialize working components 
        self.control_panel = ControlPanelCard(self.server_bridge, self.page, self.show_notification, None)
        self.quick_actions = QuickActions(
            page=page,
            on_backup_now=self._on_backup_now,
            on_clear_logs=self._on_clear_logs,
            on_restart_services=self._on_restart_services,
            on_view_clients=self._on_view_clients,
            on_manage_files=self._on_manage_files
        )
        
        # Initialize view objects
        try:
            from flet_server_gui.views.dashboard import DashboardView
            self.dashboard_view = DashboardView(page, self.server_bridge)
        except Exception as e:
            print(f"[WARNING] Dashboard view import failed: {e}")
            self.dashboard_view = None
            
        try:
            from flet_server_gui.views.clients import ClientsView
            self.clients_view = ClientsView(self.server_bridge, self.dialog_system, self.toast_manager, page)
        except Exception as e:
            print(f"[WARNING] Clients view import failed: {e}")
            self.clients_view = None
            
        try:
            from flet_server_gui.views.files import FilesView
            self.files_view = FilesView(self.server_bridge, self.dialog_system, self.toast_manager, page)
        except Exception as e:
            print(f"[WARNING] Files view import failed: {e}")
            self.files_view = None
            
        try:
            from flet_server_gui.views.database import DatabaseView
            self.database_view = DatabaseView(self.server_bridge, self.dialog_system, self.toast_manager, page)
        except Exception as e:
            print(f"[WARNING] Database view import failed: {e}")
            self.database_view = None
            
        try:
            from flet_server_gui.views.analytics import AnalyticsView
            self.analytics_view = AnalyticsView(page)
        except Exception as e:
            print(f"[WARNING] Analytics view import failed: {e}")
            self.analytics_view = None
            
        if SettingsView:
            self.settings_view = SettingsView(page, self.dialog_system, self.toast_manager)
        else:
            self.settings_view = None
        if LogsView:
            self.logs_view = LogsView(page, self.dialog_system, self.toast_manager)
        else:
            self.logs_view = None
        # Navigation manager will be initialized after content_area is created in build_ui

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
            duration=200,
            reverse_duration=150,
            switch_in_curve=ft.AnimationCurve.EASE_OUT,
            switch_out_curve=ft.AnimationCurve.EASE_OUT,
        )

        # Initialize navigation manager after content_area is created
        self.navigation = NavigationManager(self.page, self.switch_view, self.content_area)
        
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
        """Create and return the dashboard view."""
        if self.dashboard_view:
            try:
                dashboard_content = self.dashboard_view.build()
                if dashboard_content:
                    # Start the dashboard's real-time updates and welcome messages
                    self.dashboard_view.start_dashboard()
                    return dashboard_content
                else:
                    # Fallback to simplified dashboard if build returns None
                    return self._build_simplified_dashboard()
            except Exception as e:
                print(f"[ERROR] Failed to build dashboard view: {e}")
                return ft.Container(
                    content=ft.Text(f"Dashboard view error: {str(e)}",
                                   style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                   text_align=ft.TextAlign.CENTER),
                    padding=40,
                    alignment=ft.alignment.center
                )
        else:
            # Fallback to simplified dashboard if view not available
            return self._build_simplified_dashboard()
    
    def _build_simplified_dashboard(self) -> ft.Control:
        """Build a simplified dashboard when full dashboard is not available."""
        return ft.Column([
            ft.Text("Dashboard", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
            ft.Divider(),
            ft.ResponsiveRow(
                controls=[
                    ft.Column(col={"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6}, controls=[self.control_panel.build()]),  
                    ft.Column(col={"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6}, controls=[ft.Card(
                        content=ft.Container(
                            content=ft.Text("Additional components will be restored once import issues are resolved.",
                                           style=ft.TextThemeStyle.BODY_LARGE,
                                           text_align=ft.TextAlign.CENTER),
                            padding=40
                        )
                    )]),
                ],
                spacing=16,
            ),
            ft.Container(height=16),
            ft.ResponsiveRow(
                controls=[
                    ft.Column(col={"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6}, controls=[self.quick_actions]),
                    ft.Column(col={"xs": 12, "sm": 12, "md": 6, "lg": 6, "xl": 6}, controls=[ft.Card(
                        content=ft.Container(
                            content=ft.Text("Server statistics will be shown here.",
                                           style=ft.TextThemeStyle.BODY_LARGE,
                                           text_align=ft.TextAlign.CENTER),
                            padding=40
                        )
                    )]),
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
        """Create and return the clients view."""
        if self.clients_view:
            try:
                return self.clients_view.build()
            except Exception as e:
                print(f"[ERROR] Failed to build clients view: {e}")
                return ft.Container(
                    content=ft.Text(f"Clients view error: {str(e)}",
                                   style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                   text_align=ft.TextAlign.CENTER),
                    padding=40,
                    alignment=ft.alignment.center
                )
        else:
            return ft.Container(
                content=ft.Text("Clients view not available",
                               style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                               text_align=ft.TextAlign.CENTER),
                padding=40,
                alignment=ft.alignment.center
            )
    
    def get_files_view(self) -> ft.Control:
        """Create and return the files view."""
        if self.files_view:
            try:
                return self.files_view.build()
            except Exception as e:
                print(f"[ERROR] Failed to build files view: {e}")
                return ft.Container(
                    content=ft.Text(f"Files view error: {str(e)}",
                                   style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                   text_align=ft.TextAlign.CENTER),
                    padding=40,
                    alignment=ft.alignment.center
                )
        else:
            return ft.Container(
                content=ft.Text("Files view not available",
                               style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                               text_align=ft.TextAlign.CENTER),
                padding=40,
                alignment=ft.alignment.center
            )
    
    def get_database_view(self) -> ft.Control:
        """Create and return the database view."""
        if self.database_view:
            try:
                return self.database_view.build()
            except Exception as e:
                print(f"[ERROR] Failed to build database view: {e}")
                return ft.Container(
                    content=ft.Text(f"Database view error: {str(e)}",
                                   style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                   text_align=ft.TextAlign.CENTER),
                    padding=40,
                    alignment=ft.alignment.center
                )
        else:
            return ft.Container(
                content=ft.Text("Database view not available",
                               style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                               text_align=ft.TextAlign.CENTER),
                padding=40,
                alignment=ft.alignment.center
            )
    
    def get_analytics_view(self) -> ft.Control:
        """Create and return the analytics view."""
        if self.analytics_view:
            try:
                return self.analytics_view.build()
            except Exception as e:
                print(f"[ERROR] Failed to build analytics view: {e}")
                return ft.Container(
                    content=ft.Text(f"Analytics view error: {str(e)}",
                                   style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                   text_align=ft.TextAlign.CENTER),
                    padding=40,
                    alignment=ft.alignment.center
                )
        else:
            return ft.Container(
                content=ft.Text("Analytics view not available",
                               style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                               text_align=ft.TextAlign.CENTER),
                padding=40,
                alignment=ft.alignment.center
            )
    
    def get_logs_view(self) -> ft.Control:
        if self.logs_view:
            return self.logs_view
        else:
            return ft.Container(
                content=ft.Text("Logs view - Import issues being resolved",
                               style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                               text_align=ft.TextAlign.CENTER),
                padding=40,
                alignment=ft.alignment.center
            )
    
    def get_settings_view(self) -> ft.Control:
        if self.settings_view:
            return self.settings_view.create_settings_view()
        else:
            return ft.Container(
                content=ft.Text("Settings view - Import issues being resolved",
                               style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                               text_align=ft.TextAlign.CENTER),
                padding=40,
                alignment=ft.alignment.center
            )

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
        
        view_builder = view_map.get(view_name, self.get_dashboard_view)
        
        try:
            new_content_instance = view_builder()
            
            # Special handling for view classes vs created controls
            if view_name == "logs" and self.logs_view:
                self.active_view_instance = self.logs_view
                new_content = self.logs_view.create_logs_view()
            else:
                self.active_view_instance = new_content_instance
                new_content = new_content_instance

            # Ensure new_content is not None
            if new_content is None:
                new_content = ft.Container(
                    content=ft.Text(f"View '{view_name}' is not available", 
                                   style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                                   text_align=ft.TextAlign.CENTER),
                    padding=40,
                    alignment=ft.alignment.center,
                    expand=True
                )

            # Start the new view if it has a start method
            if hasattr(self.active_view_instance, 'start'):
                self.active_view_instance.start()

            self.content_area.content = new_content
            self.page.update()
        except Exception as e:
            print(f"[ERROR] Failed to switch to view '{view_name}': {e}")
            error_content = ft.Container(
                content=ft.Text(f"Error loading view '{view_name}': {str(e)}", 
                               style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                               text_align=ft.TextAlign.CENTER),
                padding=40,
                alignment=ft.alignment.center,
                expand=True
            )
            self.content_area.content = error_content
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
                    # Real-time updates will be restored when imports are fixed
                    pass
                elif self.current_view == "analytics":
                    # This view manages its own updates, so we don't call it here.
                    pass
                await asyncio.sleep(2)
            except Exception as e:
                print(f"Monitor loop error: {e}")
                await asyncio.sleep(5)

def main(page: ft.Page):
    app = ServerGUIApp(page)

if __name__ == "__main__":
    print("Starting Encrypted Backup Server GUI...")
    ft.app(target=main, assets_dir="assets")
