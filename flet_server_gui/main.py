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
from datetime import datetime
from typing import Callable

# Use only working components to avoid complex import chains
from flet_server_gui.components.control_panel_card import ControlPanelCard
from flet_server_gui.components.quick_actions import QuickActions
from flet_server_gui.ui.navigation import NavigationManager
from flet_server_gui.ui.dialogs import DialogSystem, ToastManager
from flet_server_gui.ui.theme import ThemeManager
from flet_server_gui.ui.layouts.responsive_fixes import apply_layout_fixes
# Import new Phase 4 components
from flet_server_gui.ui.widgets.status_pill import StatusPill, ServerStatus
from flet_server_gui.ui.widgets.notifications_panel import NotificationsPanel, create_notification, NotificationType, NotificationPriority
from flet_server_gui.ui.widgets.activity_log_dialog import ActivityLogDialog, create_activity_entry, ActivityLevel, ActivityCategory
from flet_server_gui.ui.theme_m3 import TOKENS

# Robust server bridge with fallback
try:
    from flet_server_gui.utils.server_bridge import ServerBridge
    BRIDGE_TYPE = "Full ModularServerBridge" 
    print(f"[SUCCESS] Using {BRIDGE_TYPE}")
except Exception as e:
    print(f"[WARNING] Full ServerBridge unavailable ({e}), using SimpleServerBridge")
    from flet_server_gui.utils.simple_server_bridge import SimpleServerBridge as ServerBridge
    BRIDGE_TYPE = "SimpleServerBridge (Fallback)"
    print(f"[INFO] Using {BRIDGE_TYPE}")
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
        
        # Resource management
        self._background_tasks = set()  # Track all async tasks for cleanup
        self._monitor_task = None  # Main monitor task reference
        self._is_shutting_down = False  # Prevent new tasks during shutdown

        # Apply theme and configure page FIRST
        self.setup_application()
        
        # Initialize dialog and notification systems
        self.dialog_system = DialogSystem(page)
        self.toast_manager = ToastManager(page)
        
        # Initialize Phase 4 components - Status pill should be OFFLINE and not clickable
        from flet_server_gui.ui.widgets.status_pill import StatusPillConfig
        status_pill_config = StatusPillConfig(clickable=False)  # Not clickable
        self.status_pill = StatusPill(ServerStatus.STOPPED, config=status_pill_config)  # OFFLINE by default
        self.notifications_panel = NotificationsPanel()
        self.activity_log_dialog = ActivityLogDialog()
        
        # Initialize action handlers
        self.file_actions = FileActions(self.server_bridge)

        # NOW initialize working components 
        self.control_panel = ControlPanelCard(self.server_bridge, self.page, self.show_notification, self.add_log_entry)
        self.quick_actions = QuickActions(
            page=page,
            on_backup_now=self._on_backup_now,
            on_clear_logs=self._on_clear_logs,
            on_restart_services=self._on_restart_services,
            on_view_clients=self._on_view_clients,
            on_manage_files=self._on_manage_files
        )
        
        # Initialize view objects with robust error handling
        self.dashboard_view = self._safe_init_view(
            "Dashboard", "flet_server_gui.views.dashboard", "DashboardView", 
            page, self.server_bridge
        )
        
        self.clients_view = self._safe_init_view(
            "Clients", "flet_server_gui.views.clients", "ClientsView",
            self.server_bridge, self.dialog_system, self.toast_manager, page
        )
        
        self.files_view = self._safe_init_view(
            "Files", "flet_server_gui.views.files", "FilesView",
            self.server_bridge, self.dialog_system, self.toast_manager, page
        )
        
        self.database_view = self._safe_init_view(
            "Database", "flet_server_gui.views.database", "DatabaseView",
            self.server_bridge, self.dialog_system, self.toast_manager, page
        )
        
        self.analytics_view = self._safe_init_view(
            "Analytics", "flet_server_gui.views.analytics", "AnalyticsView",
            page, self.server_bridge, self.dialog_system, self.toast_manager
        )
        
        # Handle pre-imported views (SettingsView and LogsView)
        self.settings_view = self._safe_init_preloaded_view(
            "Settings", SettingsView, page, self.dialog_system, self.toast_manager
        )
        
        self.logs_view = self._safe_init_preloaded_view(
            "Logs", LogsView, page, self.dialog_system, self.toast_manager
        )
        # Navigation manager will be initialized after content_area is created in build_ui

        self.build_ui()
        
        # Add sample notifications and activities for demonstration
        self._add_sample_data()
        
        self.page.window_to_front = True
        self.page.on_connect = self._on_page_connect
        self.page.on_close = self._on_page_close
    
    def _safe_init_view(self, view_name: str, module_path: str, class_name: str, *args):
        """
        Safely import and initialize a view with detailed error diagnostics.
        
        Args:
            view_name: Human-readable name for logging (e.g., "Dashboard")
            module_path: Module path for import (e.g., "flet_server_gui.views.dashboard")
            class_name: Class name to import (e.g., "DashboardView")
            *args: Arguments to pass to the view constructor
            
        Returns:
            View instance if successful, None if failed
        """
        view_instance = None
        
        # Debug: Print current working directory and Python path
        import os
        safe_print(f"[DEBUG] Current working directory: {os.getcwd()}")
        import sys
        safe_print(f"[DEBUG] Python path (first 5 entries): {sys.path[:5]}")
        
        # Step 1: Try to import the module
        try:
            import importlib
            safe_print(f"[DEBUG] Attempting to import module: {module_path}")
            module = importlib.import_module(module_path)
            safe_print(f"[SUCCESS] {view_name} module imported successfully from {module_path}")
        except ImportError as e:
            safe_print(f"[ERROR] {view_name} import failed: Module '{module_path}' not found")
            safe_print(f"[DEBUG] Import error details: {e}")
            import traceback
            safe_print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
            return None
        except Exception as e:
            safe_print(f"[ERROR] {view_name} import failed: Unexpected error importing '{module_path}'")
            safe_print(f"[DEBUG] Error details: {e}")
            import traceback
            safe_print(f"[DEBUG] Full traceback: {traceback.format_exc()}")
            return None
            
        # Step 2: Try to get the class from the module
        try:
            view_class = getattr(module, class_name)
            safe_print(f"[SUCCESS] {view_name} class '{class_name}' found in module")
        except AttributeError as e:
            safe_print(f"[ERROR] {view_name} class not found: '{class_name}' not in '{module_path}'")
            safe_print(f"[DEBUG] Available classes: {[name for name in dir(module) if not name.startswith('_')]}")
            return None
        except Exception as e:
            safe_print(f"[ERROR] {view_name} class access failed: Unexpected error accessing '{class_name}'")
            safe_print(f"[DEBUG] Error details: {e}")
            return None
        
        # Step 3: Try to initialize the view
        try:
            view_instance = view_class(*args)
            safe_print(f"[SUCCESS] {view_name} view initialized successfully")
        except TypeError as e:
            safe_print(f"[ERROR] {view_name} initialization failed: Invalid arguments for constructor")
            safe_print(f"[DEBUG] Constructor error: {e}")
            safe_print(f"[DEBUG] Provided args: {len(args)} arguments")
            return None
        except Exception as e:
            safe_print(f"[ERROR] {view_name} initialization failed: Runtime error during construction")
            safe_print(f"[DEBUG] Runtime error: {e}")
            return None
        
        return view_instance
    
    def _safe_init_preloaded_view(self, view_name: str, view_class, *args):
        """
        Safely initialize a pre-imported view class with detailed error diagnostics.
        
        Args:
            view_name: Human-readable name for logging (e.g., "Settings")
            view_class: Pre-imported class (could be None if import failed)
            *args: Arguments to pass to the view constructor
        
        Returns:
            View instance if successful, None if failed
        """
        if view_class is None:
            safe_print(f"[WARNING] {view_name} view not available: Class was not imported successfully")
            safe_print(f"[INFO] {view_name} will show 'not available' message to users")
            return None
        
        try:
            view_instance = view_class(*args)
            safe_print(f"[SUCCESS] {view_name} view initialized successfully from pre-imported class")
            return view_instance
        except TypeError as e:
            safe_print(f"[ERROR] {view_name} initialization failed: Invalid arguments for constructor")
            safe_print(f"[DEBUG] Constructor error: {e}")
            safe_print(f"[DEBUG] Provided args: {len(args)} arguments")
            return None
        except Exception as e:
            safe_print(f"[ERROR] {view_name} initialization failed: Runtime error during construction")
            safe_print(f"[DEBUG] Runtime error: {e}")
            return None
    
    def _track_task(self, task: asyncio.Task) -> asyncio.Task:
        """Track an async task for cleanup."""
        if not self._is_shutting_down:
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
        return task
    
    async def _cancel_all_tasks(self):
        """Cancel all background tasks gracefully."""
        self._is_shutting_down = True
        
        # Cancel main monitor task first
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                safe_print(f"[WARNING] Error cancelling monitor task: {e}")
        
        # Cancel all other background tasks
        if self._background_tasks:
            safe_print(f"[INFO] Cancelling {len(self._background_tasks)} background tasks...")
            for task in list(self._background_tasks):
                if not task.done():
                    task.cancel()
            
            # Wait for tasks to complete cancellation
            if self._background_tasks:
                await asyncio.gather(*self._background_tasks, return_exceptions=True)
            
            self._background_tasks.clear()
    
    def _cleanup_view_resources(self, view_instance):
        """Clean up resources for a view instance."""
        if not view_instance:
            return
        
        # Call dispose if available
        if hasattr(view_instance, 'dispose'):
            try:
                view_instance.dispose()
            except Exception as e:
                safe_print(f"[WARNING] Error disposing view: {e}")
        
        # Call cleanup if available
        if hasattr(view_instance, 'cleanup'):
            try:
                view_instance.cleanup()
            except Exception as e:
                safe_print(f"[WARNING] Error cleaning up view: {e}")
        
        # Call stop if available
        if hasattr(view_instance, 'stop'):
            try:
                view_instance.stop()
            except Exception as e:
                safe_print(f"[WARNING] Error stopping view: {e}")
    
    async def dispose(self):
        """Dispose of all application resources."""
        safe_print("[INFO] Disposing application resources...")
        
        # Clean up current view
        self._cleanup_view_resources(self.active_view_instance)
        
        # Clean up all view instances
        for view in [self.dashboard_view, self.clients_view, self.files_view, 
                    self.database_view, self.analytics_view, self.settings_view, self.logs_view]:
            self._cleanup_view_resources(view)
        
        # Cancel all background tasks
        await self._cancel_all_tasks()
        
        # Clean up server bridge
        if hasattr(self.server_bridge, 'cleanup'):
            try:
                self.server_bridge.cleanup()
            except Exception as e:
                safe_print(f"[WARNING] Error cleaning up server bridge: {e}")
        
        safe_print("[INFO] Application disposed successfully")
    
    async def _on_page_close(self, e):
        """Handle application close event."""
        await self.dispose()
    
    async def _on_page_connect(self, e):
        """Start background tasks when the page is connected."""
        if self._is_shutting_down:
            return
        
        # Start main monitor loop with tracking
        self._monitor_task = self._track_task(asyncio.create_task(self.monitor_loop()))
        
        # Initialize dashboard if it's the current view
        if self.current_view == "dashboard" and self.dashboard_view:
            self.dashboard_view.start_dashboard_sync()  # Sync initialization
            # Track dashboard async tasks
            if hasattr(self.dashboard_view, 'start_dashboard_async'):
                self._track_task(asyncio.create_task(self.dashboard_view.start_dashboard_async()))
    
    def setup_application(self):
        """Configure the desktop application and apply the theme."""
        self.page.title = "Encrypted Backup Server - Control Panel"
        
        # Adaptive window sizing - use percentage of screen or reasonable defaults
        # Remove hardcoded dimensions to allow natural sizing
        self.page.window_width = None  # Let Flet determine optimal width
        self.page.window_height = None  # Let Flet determine optimal height
        
        # More reasonable minimum sizes for standard screens
        self.page.window_min_width = 1024  # Minimum for proper layout
        self.page.window_min_height = 768   # Standard 4:3 aspect ratio
        self.page.window_resizable = True
        
        # Set preferred window size on first launch
        self.page.window_width = 1200  # Reasonable default that works on most screens
        self.page.window_height = 800   # Balanced height for content
        
        self.theme_manager.apply_theme()
        
        # Reduced padding for better space utilization
        self.page.padding = ft.padding.all(12)
        self.page.spacing = 0
        
        # Apply layout fixes for clipping and hitbox issues
        apply_layout_fixes(self.page)
        
        # Apply theme consistency
        self.theme_manager.apply_consistency()
        
        # Register window resize handler for responsive behavior
        self.page.on_window_event = self.handle_window_resize
        
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

        # Initialize status pill as OFFLINE since we're not connected to a server
        self.status_pill.set_status(ServerStatus.STOPPED)  # OFFLINE status

        app_bar = ft.AppBar(
            title=ft.Text("Server Control Panel", weight=ft.FontWeight.W_500),
            leading=self.hamburger_button,
            actions=[
                self.status_pill,  # Status pill is not clickable
                ft.IconButton(ft.Icons.NOTIFICATIONS, tooltip="Notifications", on_click=self._on_notifications),
                self.theme_toggle_button,
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
        
        # Responsive main layout with proper expand behavior
        self.main_layout = ft.Row([
            # Navigation rail container
            ft.Container(
                content=self.nav_rail,
                width=None,  # Let nav rail determine its own width
                expand=False  # Don't expand the navigation area
            ),
            # Divider
            ft.VerticalDivider(width=1),
            # Content area with responsive container
            ft.Container(
                content=self.content_area,
                padding=ft.padding.symmetric(horizontal=16, vertical=12),  # Reduced padding
                expand=True,  # This should expand to fill available space
                clip_behavior=ft.ClipBehavior.NONE,  # Prevent content clipping
                # Ensure content area can scroll if needed
                alignment=ft.alignment.top_left
            )
        ], 
        expand=True,  # Main row expands to fill page
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.START  # Align to top
        )
        
        self.page.appbar = app_bar
        self.page.add(self.main_layout)
        
        # Remove redundant minimum size settings - already set in setup_application()
        # The responsive layout will handle sizing automatically
    
    def toggle_navigation(self, e):
        """Toggle navigation rail visibility with responsive behavior"""
        self.nav_rail_visible = not self.nav_rail_visible
        self.nav_rail.visible = self.nav_rail_visible
        self.hamburger_button.icon = ft.Icons.MENU if self.nav_rail_visible else ft.Icons.MENU_OPEN
        
        # Update content area padding based on nav rail visibility
        if hasattr(self, 'main_layout') and len(self.main_layout.controls) >= 3:
            content_container = self.main_layout.controls[2]  # Content area container
            if self.nav_rail_visible:
                content_container.padding = ft.padding.symmetric(horizontal=16, vertical=12)
            else:
                # More space when nav rail is hidden
                content_container.padding = ft.padding.symmetric(horizontal=24, vertical=12)
        
        self.page.update()
    
    def handle_window_resize(self, e=None):
        """Handle window resize events to ensure responsive layout with MD3 desktop breakpoints"""
        if not hasattr(self, 'page') or not self.page:
            return
            
        # Get current window dimensions
        window_width = getattr(self.page, 'window_width', 1200)
        window_height = getattr(self.page, 'window_height', 800)
        
        # Import breakpoint system
        from flet_server_gui.ui.layouts.md3_desktop_breakpoints import MD3DesktopBreakpoints, DesktopBreakpoint
        
        # Determine current breakpoint
        breakpoint = MD3DesktopBreakpoints.get_breakpoint(window_width)
        
        # Auto-hide navigation on very small screens (windowed mode)
        if window_width and window_width < 1024 and self.nav_rail_visible:
            # Auto-collapse navigation on small screens
            self.nav_rail.extended = False
            self.nav_rail.label_type = ft.NavigationRailLabelType.SELECTED
            self.hamburger_button.icon = ft.Icons.MENU_OPEN
            
            # Update content area for more space
            if hasattr(self, 'main_layout') and len(self.main_layout.controls) >= 3:
                content_container = self.main_layout.controls[2]
                content_container.padding = ft.padding.symmetric(horizontal=12, vertical=8)
        elif window_width and window_width >= 1024 and not self.nav_rail.extended:
            # Restore navigation on larger screens
            self.nav_rail.extended = True
            self.nav_rail.label_type = ft.NavigationRailLabelType.ALL
            self.hamburger_button.icon = ft.Icons.MENU
            
            # Update content area padding
            if hasattr(self, 'main_layout') and len(self.main_layout.controls) >= 3:
                content_container = self.main_layout.controls[2]
                content_container.padding = ft.padding.symmetric(horizontal=16, vertical=12)
        
        # Update layout
        self.page.update()
    
    def get_dashboard_view(self) -> ft.Control:
        """Create and return the dashboard view."""
        if self.dashboard_view:
            try:
                dashboard_content = self.dashboard_view.build()
                if dashboard_content:
                    # Dashboard async tasks will be started via _on_page_connect
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
        
        # Create compact status cards optimized for windowed mode
        server_status_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Server Status", style=ft.TextThemeStyle.TITLE_SMALL, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Status:", size=12),
                                ft.Container(expand=True),
                                ft.Text("Offline", color=TOKENS['error'], size=12, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Row([
                                ft.Text("Port:", size=12),
                                ft.Container(expand=True),
                                ft.Text("1256", size=12)
                            ])
                        ], spacing=4),
                        margin=ft.margin.only(top=8)
                    )
                ], spacing=4),
                padding=16,  # Reduced padding for more compact layout
                height=100,  # Fixed height for consistency
                alignment=ft.alignment.top_left
            ),
            elevation=2
        )
        
        stats_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Statistics", style=ft.TextThemeStyle.TITLE_SMALL, weight=ft.FontWeight.BOLD),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Clients:", size=12),
                                ft.Container(expand=True),
                                ft.Text("0", size=12, weight=ft.FontWeight.BOLD)
                            ]),
                            ft.Row([
                                ft.Text("Files:", size=12),
                                ft.Container(expand=True),
                                ft.Text("0", size=12, weight=ft.FontWeight.BOLD)
                            ])
                        ], spacing=4),
                        margin=ft.margin.only(top=8)
                    )
                ], spacing=4),
                padding=16,  # Reduced padding for more compact layout
                height=100,  # Fixed height for consistency
                alignment=ft.alignment.top_left
            ),
            elevation=2
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Server Dashboard", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Divider(),
                
                # Status row with improved responsive breakpoints
                ft.ResponsiveRow([
                    ft.Container(
                        content=server_status_card,
                        col={"xs": 12, "sm": 6, "md": 4, "lg": 4},
                        expand=True
                    ),
                    ft.Container(
                        content=stats_card,
                        col={"xs": 12, "sm": 6, "md": 4, "lg": 4},
                        expand=True
                    ),
                    ft.Container(
                        content=self.control_panel.build(),
                        col={"xs": 12, "sm": 12, "md": 4, "lg": 4},
                        expand=True
                    )
                ], spacing=12, run_spacing=12),
                
                ft.Container(height=12),  # Reduced spacing
                
                # Quick actions row with better breakpoints
                ft.ResponsiveRow([
                    ft.Container(
                        content=self.quick_actions,
                        col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                        expand=True
                    ),
                    ft.Container(
                        content=ft.Card(
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text("Activity Log", style=ft.TextThemeStyle.TITLE_MEDIUM),
                                    ft.Divider(),
                                    ft.Container(
                                        content=ft.Column([
                                            ft.Text("System started", style=ft.TextThemeStyle.BODY_SMALL),
                                            ft.Text("GUI initialized", style=ft.TextThemeStyle.BODY_SMALL),
                                        ], spacing=4),
                                        height=60,  # Fixed height for consistency
                                        alignment=ft.alignment.top_left
                                    ),
                                    ft.Container(
                                        content=ft.FilledButton(
                                            "View Full Logs",
                                            icon=ft.Icons.HISTORY,
                                            on_click=lambda _: self.switch_view("logs")
                                        ),
                                        alignment=ft.alignment.center,
                                        margin=ft.margin.only(top=8)
                                    )
                                ], spacing=8),
                                padding=16  # Reduced padding
                            ),
                            elevation=2
                        ),
                        col={"xs": 12, "sm": 12, "md": 6, "lg": 6},
                        expand=True
                    )
                ], spacing=12, run_spacing=12)
            ], spacing=16, scroll=ft.ScrollMode.AUTO, expand=True),
            expand=True,
            padding=ft.padding.all(8),  # Outer padding for the dashboard
            clip_behavior=ft.ClipBehavior.NONE
        )
    
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
        if self._is_shutting_down:
            return
            
        self.add_log_entry("Quick Actions", "Cleanup job initiated", "INFO")
        try:
            result = await self.server_bridge.cleanup_old_files_by_age(days_threshold=30)
            if result and result.get('success'):
                cleaned_count = result.get('cleaned_files', 0)
                await self.show_notification(f"Cleanup successful: {cleaned_count} old files removed.")
                self.add_log_entry("Cleanup", f"Removed {cleaned_count} old files", "SUCCESS")
                
                # Add notification to panel
                notification = create_notification(
                    "Backup Completed",
                    f"Cleanup successful: {cleaned_count} old files removed.",
                    NotificationType.BACKUP,
                    NotificationPriority.NORMAL,
                    ["View Details"]
                )
                self.notifications_panel.add_notification(notification)
            else:
                await self.show_notification("Cleanup failed", is_error=True)
                self.add_log_entry("Cleanup", "Cleanup operation failed", "ERROR")
        except Exception as ex:
            await self.show_notification(f"Cleanup error: {str(ex)}", is_error=True)
            self.add_log_entry("Cleanup", f"Error: {str(ex)}", "ERROR")

    async def _on_clear_logs(self, e):
        """Handle clear logs action."""
        if self._is_shutting_down:
            return
            
        if (self.current_view == "dashboard" and 
            self.dashboard_view and 
            hasattr(self.dashboard_view, '_clear_activity_log')):
            self.dashboard_view._clear_activity_log(e)
        else:
            self.add_log_entry("System", "Activity log cleared", "INFO")

    async def _on_restart_services(self, e):
        """Handle restart services action."""
        if self._is_shutting_down:
            return
            
        if hasattr(self.control_panel, 'restart_server'):
            await self.control_panel.restart_server(e)
        else:
            self.add_log_entry("System", "Restart requested", "INFO")
            await self.show_notification("Service restart initiated")

    def _on_view_clients(self, e):
        self.switch_view("clients")

    def _on_manage_files(self, e):
        self.switch_view("files")

    def switch_view(self, view_name: str):
        """Switch to a different view, managing component lifecycles."""
        if self.current_view == view_name:
            return

        # Clean up the current view properly
        self._cleanup_view_resources(self.active_view_instance)

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
            
            # Sync navigation state
            if hasattr(self, 'navigation') and self.navigation:
                self.navigation.sync_navigation_state(view_name)
                
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
        # Show notifications panel
        self.notifications_panel.show()

    def _on_help(self, e):
        """Handle help button click."""
        self.dialog_system.show_info_dialog(
            "About",
            "Encrypted Backup Server - Control Panel\nVersion: 1.0.0\nDeveloped with Flet and Material Design 3."
        )
    
    def _show_activity_log(self, e):
        """Show activity log dialog."""
        self.activity_log_dialog.show(self.page)
    
    def _add_sample_data(self):
        """Add sample notifications and activities for demonstration."""
        # Add sample notifications
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
        notif3 = create_notification(
            "System Update",
            "New version available for download",
            NotificationType.MAINTENANCE,
            NotificationPriority.LOW,
            ["Download", "Dismiss"]
        )
        
        self.notifications_panel.add_notification(notif1)
        self.notifications_panel.add_notification(notif2)
        self.notifications_panel.add_notification(notif3)
        
        # Add sample activities
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
        activity3 = create_activity_entry(
            "Backup job completed",
            ActivityLevel.SUCCESS,
            ActivityCategory.BACKUP,
            "BackupService"
        )
        activity4 = create_activity_entry(
            "Warning: Disk space low",
            ActivityLevel.WARNING,
            ActivityCategory.SYSTEM,
            "SystemMonitor"
        )
        
        self.activity_log_dialog.add_activity(activity1)
        self.activity_log_dialog.add_activity(activity2)
        self.activity_log_dialog.add_activity(activity3)
        self.activity_log_dialog.add_activity(activity4)
    
    async def show_notification(self, message: str, is_error: bool = False):
        """Async method to show notification."""
        if self._is_shutting_down:
            return
            
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
    
    def add_log_entry(self, source: str, message: str, level: str = "INFO"):
        """Add entry to the activity log"""
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
        activity_category = ActivityCategory.SYSTEM  # Default category
        
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
        if (self.current_view == "dashboard" and 
            self.dashboard_view and 
            hasattr(self.dashboard_view, 'add_log_entry')):
            self.dashboard_view.add_log_entry(source, message, level)
        else:
            # Fallback to console
            safe_print(f"[LOG] {source}: {message} ({level})")
    
    async def monitor_loop(self):
        """Main monitoring loop with proper resource management and meaningful functionality."""
        safe_print("[INFO] Starting application monitor loop...")
        monitor_interval = 5  # Reasonable 5-second interval
        
        while not self._is_shutting_down:
            try:
                # Check if we should continue monitoring
                if self._is_shutting_down:
                    break
                
                # Monitor server status
                try:
                    if hasattr(self.server_bridge, 'get_server_status'):
                        server_status = await self.server_bridge.get_server_status()
                        if server_status and hasattr(self, 'status_pill'):
                            # Update status pill based on server status
                            if server_status.get('running', False):
                                self.status_pill.set_status(ServerStatus.RUNNING)
                            else:
                                self.status_pill.set_status(ServerStatus.STOPPED)
                except Exception as e:
                    safe_print(f"[DEBUG] Server status check failed: {e}")
                
                # Update current view if it has monitor methods
                if self.current_view == "dashboard" and self.dashboard_view:
                    if hasattr(self.dashboard_view, 'update_metrics'):
                        try:
                            await self.dashboard_view.update_metrics()
                        except Exception as e:
                            safe_print(f"[DEBUG] Dashboard metrics update failed: {e}")
                
                elif self.current_view == "analytics" and self.analytics_view:
                    if hasattr(self.analytics_view, 'refresh_data'):
                        try:
                            await self.analytics_view.refresh_data()
                        except Exception as e:
                            safe_print(f"[DEBUG] Analytics refresh failed: {e}")
                
                # Monitor system resources (basic)
                try:
                    import psutil
                    cpu_percent = psutil.cpu_percent(interval=None)
                    memory = psutil.virtual_memory()
                    
                    # Log warnings if resources are high
                    if cpu_percent > 80:
                        safe_print(f"[WARNING] High CPU usage: {cpu_percent:.1f}%")
                    if memory.percent > 85:
                        safe_print(f"[WARNING] High memory usage: {memory.percent:.1f}%")
                        
                except ImportError:
                    # psutil not available, skip resource monitoring
                    pass
                except Exception as e:
                    safe_print(f"[DEBUG] Resource monitoring failed: {e}")
                
                # Wait for next cycle, but check for shutdown
                for _ in range(monitor_interval):
                    if self._is_shutting_down:
                        break
                    await asyncio.sleep(1)
                    
            except asyncio.CancelledError:
                safe_print("[INFO] Monitor loop cancelled")
                break
            except Exception as e:
                safe_print(f"[ERROR] Monitor loop error: {e}")
                # Use longer delay on errors
                for _ in range(10):
                    if self._is_shutting_down:
                        break
                    await asyncio.sleep(1)
        
        safe_print("[INFO] Monitor loop stopped")

def main(page: ft.Page):
    app = ServerGUIApp(page)

if __name__ == "__main__":
    print("Starting Encrypted Backup Server GUI...")
    ft.app(target=main, assets_dir="assets")
