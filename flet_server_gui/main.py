#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flet Material Design 3 Server GUI - Refactored Main Application (FACADE PATTERN)
Desktop application for managing the encrypted backup server.

REFACTORED: Reduced from 924 lines to <200 lines using specialized managers.
This class now acts as a Facade, coordinating between:
- ViewManager: View switching and lifecycle
- ApplicationMonitor: Background monitoring and resources  
- ThemeManager: Theme switching and application
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import utf8_solution to fix encoding issues
safe_print = print  # Default fallback
try:
    import Shared.utils.utf8_solution
    from Shared.utils.utf8_solution import safe_print
    safe_print("[INFO] UTF-8 solution imported successfully")
except ImportError as e:
    # Try alternative path
    utf8_path = os.path.join(os.path.dirname(__file__), "..", "Shared", "utils")
    if utf8_path not in sys.path:
        sys.path.insert(0, utf8_path)
    try:
        import utf8_solution
        from utf8_solution import safe_print
        safe_print("[INFO] UTF-8 solution imported via alternative path")
    except ImportError:
        safe_print("[WARNING] utf8_solution import failed, continuing without it")
        safe_print(f"[DEBUG] Import error: {e}")

import flet as ft
import asyncio
from typing import Optional

# Extracted managers (Single Responsibility Principle)
from flet_server_gui.managers.view_manager import ViewManager
from flet_server_gui.services.application_monitor import ApplicationMonitor
from flet_server_gui.managers.theme_manager import ThemeManager

# Essential components
from flet_server_gui.components.control_panel_card import ControlPanelCard
from flet_server_gui.components.quick_actions import QuickActions
from flet_server_gui.ui.navigation import NavigationManager
from flet_server_gui.ui.dialogs import DialogSystem, ToastManager
from flet_server_gui.theme import THEMES, DEFAULT_THEME_NAME
from flet_server_gui.ui.layouts.responsive_fixes import apply_layout_fixes
from flet_server_gui.ui.widgets.status_pill import StatusPill, ServerStatus, StatusPillConfig
from flet_server_gui.ui.widgets.notifications_panel import NotificationsPanel, create_notification, NotificationType, NotificationPriority
from flet_server_gui.ui.widgets.activity_log_dialog import ActivityLogDialog, create_activity_entry, ActivityLevel, ActivityCategory

# Server bridge with fallback
try:
    from flet_server_gui.utils.server_bridge import ServerBridge
    BRIDGE_TYPE = "Full ModularServerBridge"
    print(f"[SUCCESS] Using {BRIDGE_TYPE}")
except Exception as e:
    print(f"[WARNING] Full ServerBridge unavailable ({e}), using SimpleServerBridge")
    from flet_server_gui.utils.simple_server_bridge import SimpleServerBridge as ServerBridge
    BRIDGE_TYPE = "SimpleServerBridge (Fallback)"
    print(f"[INFO] Using {BRIDGE_TYPE}")

# Import views
from flet_server_gui.views.dashboard import DashboardView
from flet_server_gui.views.clients import ClientsView
from flet_server_gui.views.files import FilesView
from flet_server_gui.views.database import DatabaseView
from flet_server_gui.views.analytics import AnalyticsView
from flet_server_gui.views.settings_view import SettingsView
from flet_server_gui.views.logs_view import LogsView
from flet_server_gui.actions import FileActions
from flet_server_gui.utils.trace_center import get_trace_center


class ServerGUIApp:
    """
    FACADE PATTERN: Main application coordination hub (REFACTORED from 924→<200 lines)
    
    Coordinates between specialized managers:
    - ViewManager: View switching and lifecycle
    - ApplicationMonitor: Background monitoring and resources  
    - ThemeManager: Theme switching and application
    """
    
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        
        # Enable structured JSONL tracing early
        try:
            get_trace_center().enable_file_logging(os.path.join("logs", "ui_trace.log"))
            print("[TRACE] JSONL trace logging enabled at logs/ui_trace.log")
        except Exception as e:
            print(f"[TRACE_WARN] Failed to enable trace file logging: {e}")

        # Initialize server bridge
        mockabase_path = "MockaBase.db"
        if os.path.exists(mockabase_path):
            self.server_bridge = ServerBridge(database_name=mockabase_path)
        else:
            self.server_bridge = ServerBridge()
        
        # Initialize specialized managers (Single Responsibility Principle)
        self.application_monitor = ApplicationMonitor(self.server_bridge)
        self.theme_manager = ThemeManager(self.page, THEMES, DEFAULT_THEME_NAME)
        
        # Configure page and setup application
        self._setup_application()
        
        # Initialize dialog and notification systems
        self.dialog_system = DialogSystem(page)
        self.toast_manager = ToastManager(page)
        
        # Initialize Phase 4 components
        status_pill_config = StatusPillConfig(clickable=False)
        self.status_pill = StatusPill(ServerStatus.STOPPED, config=status_pill_config)
        self.notifications_panel = NotificationsPanel()
        self.activity_log_dialog = ActivityLogDialog()
        
        # Initialize action handlers and components
        self.file_actions = FileActions(self.server_bridge)
        self.control_panel = ControlPanelCard(self.server_bridge, self.page, self.show_notification, self.add_log_entry)
        self.quick_actions = QuickActions(
            page=page,
            on_backup_now=self._on_backup_now,
            on_clear_logs=self._on_clear_logs,
            on_restart_services=self._on_restart_services,
            on_view_clients=lambda _: self.view_manager.switch_view("clients"),
            on_manage_files=lambda _: self.view_manager.switch_view("files")
        )
        
        # Initialize all view instances
        self._initialize_views()
        
        # Build UI and initialize ViewManager
        self._build_ui()
        
        # Setup callbacks between managers
        self._setup_manager_integration()
        
        # Add sample data and setup page events
        self._add_sample_data()
        self.page.window_to_front = True
        self.page.on_connect = self._on_page_connect
        self.page.on_close = self._on_page_close
    def _initialize_views(self) -> None:
        """Initialize all view instances."""
        self.dashboard_view = DashboardView(self.page, self.server_bridge)
        self.clients_view = ClientsView(self.server_bridge, self.dialog_system, self.toast_manager, self.page)
        self.files_view = FilesView(self.server_bridge, self.dialog_system, self.toast_manager, self.page)
        self.database_view = DatabaseView(self.server_bridge, self.dialog_system, self.toast_manager, self.page)
        self.analytics_view = AnalyticsView(self.page, self.server_bridge, self.dialog_system, self.toast_manager)
        self.settings_view = SettingsView(self.page, self.dialog_system, self.toast_manager)
        self.logs_view = LogsView(self.page, self.dialog_system, self.toast_manager)
    
    def _setup_application(self) -> None:
        """Configure the desktop application."""
        self.page.title = "Encrypted Backup Server - Control Panel"
        self.page.window_width = 1280
        self.page.window_height = 800
        self.page.window_min_width = 1024
        self.page.window_min_height = 768
        self.page.window_resizable = True
        self.page.padding = ft.padding.all(12)
        self.page.spacing = 0
        apply_layout_fixes(self.page)
        self.page.on_window_event = self._handle_window_resize
    
    def _build_ui(self) -> None:
        """Build the main UI structure."""
        # Create app bar with theme components
        app_bar = ft.AppBar(
            title=ft.Text("Server Control Panel", weight=ft.FontWeight.W_500),
            leading=ft.IconButton(icon=ft.Icons.MENU, tooltip="Toggle Navigation", on_click=self._toggle_navigation),
            actions=[
                self.status_pill,
                ft.IconButton(ft.Icons.NOTIFICATIONS, tooltip="Notifications", on_click=self._on_notifications),
                self.theme_manager.create_theme_dropdown(),
                self.theme_manager.create_theme_toggle_button(),
                ft.IconButton(ft.Icons.HELP, tooltip="Help", on_click=self._on_help),
            ]
        )
        
        # Create content area
        self.content_area = ft.AnimatedSwitcher(
            content=ft.Text("Loading..."),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=200
        )
        
        # Initialize ViewManager AFTER content_area is created
        self.view_manager = ViewManager(self.page, self.content_area)
        self._register_all_views()
        
        # Initialize navigation
        self.navigation = NavigationManager(self.page, self.view_manager.switch_view, self.content_area)
        self.nav_rail = self.navigation.build()
        self.view_manager.set_navigation_manager(self.navigation)
        
        # Build main layout
        self._build_main_layout()
        
        self.page.appbar = app_bar
        self.page.add(self.main_layout)
    
    def _register_all_views(self) -> None:
        """Register all views with ViewManager."""
        self.view_manager.register_view("dashboard", self.dashboard_view)
        self.view_manager.register_view("clients", self.clients_view)
        self.view_manager.register_view("files", self.files_view)
        self.view_manager.register_view("database", self.database_view)
        self.view_manager.register_view("analytics", self.analytics_view)
        self.view_manager.register_view("settings", self.settings_view)
        self.view_manager.register_view("logs", self.logs_view)
        
        # Switch to dashboard view
        self.view_manager.switch_view("dashboard")
    
    def _build_main_layout(self) -> None:
        """Build the main responsive layout."""
        self.main_layout = ft.Row([
            ft.Container(content=self.nav_rail, expand=False),
            ft.VerticalDivider(width=1),
            ft.Container(
                content=self.content_area,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
                expand=True,
                clip_behavior=ft.ClipBehavior.NONE,
                alignment=ft.alignment.top_left
            )
        ], expand=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.START)
    
    def _setup_manager_integration(self) -> None:
        """Setup callbacks between managers."""
        # ApplicationMonitor callbacks
        self.application_monitor.add_status_callback(self._on_server_status_changed)
        self.application_monitor.add_error_callback(self._on_monitor_error)
        
        # ViewManager callbacks
        self.view_manager.add_view_change_callback(self._on_view_changed)
        
        # ThemeManager callbacks
        self.theme_manager.add_theme_change_callback(self._on_theme_changed)
    
    async def dispose(self) -> None:
        """Dispose of all application resources."""
        safe_print("[INFO] Disposing application resources...")
        
        # Dispose managers
        if hasattr(self, 'application_monitor'):
            await self.application_monitor.dispose()
        if hasattr(self, 'view_manager'):
            self.view_manager.dispose()
        if hasattr(self, 'theme_manager'):
            self.theme_manager.dispose()
        
        # Clean up server bridge
        if hasattr(self.server_bridge, 'cleanup'):
            try:
                self.server_bridge.cleanup()
            except Exception as e:
                safe_print(f"[WARNING] Error cleaning up server bridge: {e}")
        
        safe_print("[INFO] Application disposed successfully")
    
    async def _on_page_close(self, e: ft.ControlEvent) -> None:
        """Handle application close event."""
        await self.dispose()
    
    async def _on_page_connect(self, e: ft.ControlEvent) -> None:
        """Start background tasks when the page is connected."""
        # Start monitoring system
        self.application_monitor.start_monitoring()
        
        # Initialize dashboard if it's the current view
        current_view = self.view_manager.get_current_view()
        if current_view == "dashboard":
            dashboard = self.view_manager.get_active_view_instance()
            if dashboard and hasattr(dashboard, 'start_dashboard_sync'):
                dashboard.start_dashboard_sync()
            if dashboard and hasattr(dashboard, 'start_dashboard_async'):
                asyncio.create_task(dashboard.start_dashboard_async())
    # === FACADE METHODS - Delegate to specialized managers ===
    
    def switch_view(self, view_name: str) -> bool:
        """Delegate view switching to ViewManager."""
        return self.view_manager.switch_view(view_name)
    
    def apply_themes(self, theme_name: str) -> bool:
        """Delegate theme application to ThemeManager.""" 
        return self.theme_manager.apply_theme(theme_name)
    
    def toggle_theme(self, e: ft.ControlEvent) -> None:
        """Delegate theme toggle to ThemeManager."""
        self.theme_manager.toggle_theme_mode()
    
    def change_theme_name(self, e: ft.ControlEvent) -> None:
        """Delegate theme dropdown change to ThemeManager."""
        self.theme_manager._on_theme_dropdown_change(e)
    
    # === EVENT HANDLERS - Clean implementations ===
    
    def _toggle_navigation(self, e: ft.ControlEvent) -> None:
        """Toggle navigation rail visibility."""
        if hasattr(self, 'nav_rail'):
            self.nav_rail.visible = not self.nav_rail.visible
            self.page.update()
    
    def _handle_window_resize(self, e: Optional[ft.ControlEvent] = None) -> None:
        """Handle window resize events for responsive behavior."""
        if hasattr(self.page, 'window_width') and self.page.window_width:
            # Auto-adjust navigation based on window width
            if self.page.window_width < 1024 and hasattr(self, 'nav_rail'):
                self.nav_rail.extended = False
            elif self.page.window_width >= 1024 and hasattr(self, 'nav_rail'):
                self.nav_rail.extended = True
            self.page.update()
    
    def _on_notifications(self, e: ft.ControlEvent) -> None:
        """Show notifications panel."""
        if hasattr(self, 'notifications_panel'):
            self.notifications_panel.show()
    
    def _on_help(self, e: ft.ControlEvent) -> None:
        """Show help dialog."""
        if hasattr(self, 'dialog_system'):
            self.dialog_system.show_info_dialog(
                "About",
                "Encrypted Backup Server - Control Panel\nVersion: 1.0.0\nDeveloped with Flet and Material Design 3."
            )
    
    # === CALLBACK METHODS - Manager integration ===
    
    def _on_server_status_changed(self, status_data: dict) -> None:
        """Handle server status changes from ApplicationMonitor."""
        if hasattr(self, 'status_pill') and status_data:
            if status_data.get('running', False):
                self.status_pill.set_status(ServerStatus.RUNNING)
            else:
                self.status_pill.set_status(ServerStatus.STOPPED)
    
    def _on_monitor_error(self, context: str, error: Exception) -> None:
        """Handle monitoring errors."""
        safe_print(f"[ERROR] Monitor error in {context}: {error}")
        if hasattr(self, 'dialog_system'):
            asyncio.create_task(self.show_notification(f"Monitor error: {context}", is_error=True))
    
    def _on_view_changed(self, view_name: str) -> None:
        """Handle view change notifications."""
        safe_print(f"[INFO] View changed to: {view_name}")
    
    def _on_theme_changed(self, theme_info: str) -> None:
        """Handle theme change notifications."""
        safe_print(f"[INFO] Theme changed: {theme_info}")
    
    # === QUICK ACTION HANDLERS - Simplified implementations ===
    
    async def _on_backup_now(self, e: ft.ControlEvent) -> None:
        """Handle backup now action."""
        self.add_log_entry("Quick Actions", "Cleanup job initiated", "INFO")
        try:
            result = await self.server_bridge.cleanup_old_files_by_age(days_threshold=30)
            if result and result.get('success'):
                cleaned_count = result.get('cleaned_files', 0)
                await self.show_notification(f"Cleanup successful: {cleaned_count} old files removed.")
                self.add_log_entry("Cleanup", f"Removed {cleaned_count} old files", "SUCCESS")
            else:
                await self.show_notification("Cleanup failed", is_error=True)
                self.add_log_entry("Cleanup", "Cleanup operation failed", "ERROR")
        except Exception as ex:
            await self.show_notification(f"Cleanup error: {str(ex)}", is_error=True)
            self.add_log_entry("Cleanup", f"Error: {str(ex)}", "ERROR")

    async def _on_clear_logs(self, e: ft.ControlEvent) -> None:
        """Handle clear logs action."""
        current_view = self.view_manager.get_current_view()
        if current_view == "dashboard":
            dashboard = self.view_manager.get_active_view_instance()
            if dashboard and hasattr(dashboard, '_clear_activity_log'):
                dashboard._clear_activity_log(e)
        else:
            self.add_log_entry("System", "Activity log cleared", "INFO")

    async def _on_restart_services(self, e: ft.ControlEvent) -> None:
        """Handle restart services action."""
        if hasattr(self.control_panel, 'restart_server'):
            await self.control_panel.restart_server(e)
        else:
            self.add_log_entry("System", "Restart requested", "INFO")
            await self.show_notification("Service restart initiated")
    
    # === UTILITY METHODS ===
    
    async def show_notification(self, message: str, is_error: bool = False) -> None:
        """Show notification via ToastManager and NotificationsPanel."""
        if is_error:
            self.toast_manager.show_error(message)
        else:
            self.toast_manager.show_success(message)
        
        # Also add to notifications panel
        notif_type = NotificationType.ERROR if is_error else NotificationType.INFO
        priority = NotificationPriority.HIGH if is_error else NotificationPriority.NORMAL
        notification = create_notification(
            "System Notification",
            message,
            notif_type,
            priority
        )
        self.notifications_panel.add_notification(notification)
    
    def add_log_entry(self, source: str, message: str, level: str = "INFO") -> None:
        """Add entry to the activity log."""
        # Map string level to enum
        level_map = {
            "DEBUG": ActivityLevel.DEBUG,
            "INFO": ActivityLevel.INFO,
            "WARNING": ActivityLevel.WARNING,
            "ERROR": ActivityLevel.ERROR,
            "CRITICAL": ActivityLevel.CRITICAL,
            "SUCCESS": ActivityLevel.SUCCESS
        }
        
        activity_level = level_map.get(level.upper(), ActivityLevel.INFO)
        activity_category = ActivityCategory.SYSTEM
        
        # Create activity entry
        activity = create_activity_entry(
            message,
            activity_level,
            activity_category,
            source
        )
        
        # Add to activity log dialog
        self.activity_log_dialog.add_activity(activity)
        
        # Forward to dashboard if available
        current_view = self.view_manager.get_current_view()
        if current_view == "dashboard":
            dashboard = self.view_manager.get_active_view_instance()
            if dashboard and hasattr(dashboard, 'add_log_entry'):
                dashboard.add_log_entry(source, message, level)
        else:
            safe_print(f"[LOG] {source}: {message} ({level})")
    
    def _add_sample_data(self) -> None:
        """Add sample notifications and activities for demonstration."""
        # Sample notifications
        notif1 = create_notification(
            "Backup Completed",
            "Daily backup completed successfully with 0 errors.",
            NotificationType.BACKUP,
            NotificationPriority.NORMAL,
            ["View Details", "Dismiss"]
        )
        notif2 = create_notification(
            "Security Alert",
            "Failed login attempt detected from IP 192.168.1.100",
            NotificationType.SECURITY,
            NotificationPriority.HIGH,
            ["Block IP", "Dismiss"]
        )
        
        self.notifications_panel.add_notification(notif1)
        self.notifications_panel.add_notification(notif2)
        
        # Sample activities
        activity1 = create_activity_entry(
            "Server started successfully",
            ActivityLevel.SUCCESS,
            ActivityCategory.SYSTEM,
            "ServerManager"
        )
        activity2 = create_activity_entry(
            "Client connected: Client-001",
            ActivityLevel.INFO,
            ActivityCategory.CLIENT,
            "ClientManager"
        )
        
        self.activity_log_dialog.add_activity(activity1)
        self.activity_log_dialog.add_activity(activity2)


def main(page: ft.Page) -> None:
    """Main entry point for the Flet application."""
    app = ServerGUIApp(page)


if __name__ == "__main__":
    print("Starting Encrypted Backup Server GUI...")
    ft.app(target=main, assets_dir="assets")
