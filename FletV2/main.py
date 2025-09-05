#!/usr/bin/env python3
"""
FletV2 - Clean Desktop Application
A properly implemented Flet desktop application following best practices.

This demonstrates the clean architecture:
- Uses Flet built-ins exclusively (no framework fighting)
- Simple NavigationRail.on_change callback (no complex routing)
- Proper theme.py integration
- Server bridge with fallback
- UTF-8 support
- Resizable desktop app configuration
"""

import flet as ft
import asyncio
import sys
import os

# Set up terminal debugging FIRST (before any other imports)
from utils.debug_setup import setup_terminal_debugging, get_logger
logger = setup_terminal_debugging(logger_name="FletV2.main")

# Auto-enable UTF-8 for all subprocess operations
import sys
import os
# Add parent directory to path for Shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import Shared.utils.utf8_solution

# Add project root to Python path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

# Use our custom theme system  
from theme import setup_default_theme, toggle_theme_mode

# Server bridge with fallback - MOCK BRIDGE PRIORITY FOR DEVELOPMENT
# To use the real bridge, comment out the MockServerBridge import.
USE_MOCK_BRIDGE = True

try:
    if USE_MOCK_BRIDGE:
        from utils.mock_server_bridge import MockServerBridge as ServerBridge
        BRIDGE_TYPE = "MockServerBridge (Development)"
        logger.info("Using MockServerBridge for standalone development.")
    else:
        raise ImportError("Skipping mock bridge to try real implementations.")
except (ImportError, ModuleNotFoundError):
    try:
        from utils.server_bridge import ModularServerBridge as ServerBridge
        BRIDGE_TYPE = "Full ModularServerBridge"
    except Exception as e:
        logger.warning(f"Failed to import ModularServerBridge: {e}")
        try:
            from utils.simple_server_bridge import SimpleServerBridge as ServerBridge
            BRIDGE_TYPE = "SimpleServerBridge (Fallback)"
        except Exception as e2:
            logger.error(f"Failed to import any server bridge: {e2}")
            ServerBridge = None
            BRIDGE_TYPE = "No Server Bridge"


class FletV2App(ft.Row):
    """
    Clean FletV2 desktop app using pure Flet patterns.
    
    This demonstrates maximum framework harmony:
    - NavigationRail.on_change for navigation (no custom managers)
    - Container(expand=True) for responsive layout
    - Simple view switching with direct function calls
    - Uses theme.py for styling
    """
    
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        
        # Configure desktop window
        self._configure_desktop_window()
        
        # Initialize server bridge with fallback asynchronously
        self.server_bridge = None
        page.run_task(self._initialize_server_bridge_async)
        
        # Create content area
        self.content_area = ft.Container(expand=True)
        
        # Create navigation rail (using simple approach)
        self.nav_rail = self._create_navigation_rail()
        
        # Build layout: NavigationRail + content area (pure Flet pattern)
        self.controls = [
            self.nav_rail,
            ft.VerticalDivider(width=1),
            self.content_area
        ]
        
        # Initial view will be loaded after the control is added to the page
        # Set up page connection handler to load initial view
        logger.info("Setting up page connection handler")
        page.on_connect = self._on_page_connect
        logger.info("Page connection handler set")
    
    async def _initialize_server_bridge_async(self):
        """Asynchronously initialize server bridge to prevent UI blocking."""
        try:
            if ServerBridge:
                # Use MockBridge directly if it's the selected type
                if BRIDGE_TYPE == "MockServerBridge (Development)":
                    self.server_bridge = ServerBridge()
                # For other bridges, attempt connection
                elif BRIDGE_TYPE == "Full ModularServerBridge":
                    self.server_bridge = ServerBridge(host="127.0.0.1", port=1256)
                    # Test connection asynchronously ONLY for real bridge
                    self.page.run_thread(self.server_bridge._test_connection)
                else:
                    # For SimpleServerBridge or others, init directly
                    self.server_bridge = ServerBridge()
                logger.info(f"Server bridge initialized: {BRIDGE_TYPE}")
            else:
                self.server_bridge = None
                logger.warning("No server bridge available")
        except Exception as e:
            logger.warning(f"Server bridge failed, falling back to mock: {e}")
            from utils.mock_server_bridge import MockServerBridge
            self.server_bridge = MockServerBridge()
        # Bridge initialization complete
    
    def _on_page_connect(self, e):
        """Called when page is connected - safe to load initial view."""
        logger.info("Page connected - loading initial dashboard view")
        self._load_view("dashboard")
        logger.info("Initial dashboard view loaded")
    
    def _configure_desktop_window(self):
        """Configure window for desktop application."""
        # Window settings
        self.page.window_min_width = 1024
        self.page.window_min_height = 768
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_resizable = True
        self.page.title = "Backup Server Management"
        
        # Apply theme from theme.py (source of truth)
        setup_default_theme(self.page)
        
        # Set desktop-appropriate padding
        self.page.padding = ft.Padding(0, 0, 0, 0)
    
    def _create_navigation_rail(self):
        """Create simple navigation rail."""
        return ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            group_alignment=-0.9,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Dashboard",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE_OUTLINE,
                    selected_icon=ft.Icons.PEOPLE,
                    label="Clients",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FOLDER_OUTLINED,
                    selected_icon=ft.Icons.FOLDER,
                    label="Files",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.STORAGE_OUTLINED,
                    selected_icon=ft.Icons.STORAGE,
                    label="Database",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.AUTO_GRAPH_OUTLINED,
                    selected_icon=ft.Icons.AUTO_GRAPH,
                    label="Analytics",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ARTICLE_OUTLINED,
                    selected_icon=ft.Icons.ARTICLE,
                    label="Logs",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings",
                ),
            ],
            on_change=self._on_navigation_change,
        )
    
    def _on_navigation_change(self, e):
        """Simple navigation callback - no complex routing."""
        # Map index to view names
        view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]
        selected_view = view_names[e.control.selected_index] if e.control.selected_index < len(view_names) else "dashboard"
        
        logger.info(f"Navigation switching to: {selected_view}")
        self._load_view(selected_view)
    
    def _load_view(self, view_name: str):
        """Load view using simple function calls - no complex view managers."""
        try:
            # Simple view switching with direct function calls
            if view_name == "dashboard":
                # Import and create dashboard view
                from views.dashboard import create_dashboard_view
                content = create_dashboard_view(self.server_bridge, self.page)
            elif view_name == "clients":
                # Import and create clients view
                from views.clients import create_clients_view
                content = create_clients_view(self.server_bridge, self.page)
            elif view_name == "files":
                # Import and create files view
                from views.files import create_files_view
                content = create_files_view(self.server_bridge, self.page)
            elif view_name == "database":
                # Import and create database view
                from views.database import create_database_view
                content = create_database_view(self.server_bridge, self.page)
            elif view_name == "analytics":
                # Import and create analytics view
                from views.analytics import create_analytics_view
                content = create_analytics_view(self.server_bridge, self.page)
            elif view_name == "logs":
                # Import and create logs view
                from views.logs import create_logs_view
                content = create_logs_view(self.server_bridge, self.page)
            elif view_name == "settings":
                # Import and create settings view
                from views.settings import create_settings_view
                content = create_settings_view(self.server_bridge, self.page)
            else:
                # Import and create dashboard view as fallback
                from views.dashboard import create_dashboard_view
                content = create_dashboard_view(self.server_bridge, self.page)
            
            # Update content area (simple assignment, no complex managers)
            self.content_area.content = content
            # Only update if the control is attached to the page
            if self.page and hasattr(self.content_area, 'page') and self.content_area.page:
                self.content_area.update()
                
                # CRITICAL: Trigger initial load for views that need it (after mounting)
                # First check if content has trigger_initial_load method
                if hasattr(content, 'trigger_initial_load') and callable(content.trigger_initial_load):
                    try:
                        content.trigger_initial_load()
                        logger.info(f"Triggered initial load for {view_name} view")
                    except Exception as init_ex:
                        logger.warning(f"Initial load trigger failed for {view_name}: {init_ex}")
                # Also check if there's a specific trigger method for dashboard
                elif view_name == "dashboard" and hasattr(content, 'trigger_initial_load'):
                    try:
                        content.trigger_initial_load()
                        logger.info(f"Triggered initial load for {view_name} view (fallback)")
                    except Exception as init_ex:
                        logger.warning(f"Initial load trigger failed for {view_name}: {init_ex}")
            
        except Exception as e:
            logger.error(f"Failed to load view {view_name}: {e}", exc_info=True)
            # Fallback to simple error view
            self.content_area.content = self._create_error_view(str(e))
            # Only update if the control is attached to the page
            if self.page and hasattr(self.content_area, 'page') and self.content_area.page:
                self.content_area.update()
    
    def _create_error_view(self, error_message: str) -> ft.Control:
        """Simple error view for fallback."""
        return ft.Container(
            content=ft.Column([
                ft.Text("Error", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ERROR),
                ft.Text(f"An error occurred: {error_message}", size=16),
                ft.ElevatedButton(
                    "Return to Dashboard",
                    on_click=lambda _: self._load_view("dashboard")
                )
            ], spacing=20),
            padding=20,
            expand=True
        )


# Simple application entry point
def main(page: ft.Page):
    """Simple main function - no complex initialization."""
    try:
        # Create and add the simple desktop app
        app = FletV2App(page)
        page.add(app)
        
        logger.info(f"FletV2 App started - {BRIDGE_TYPE} active")
        
    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)
        # Simple error fallback
        error_text = ft.Text(f"Failed to start: {e}", color=ft.Colors.ERROR)
        page.add(error_text)
        
        # Show error in snackbar as well
        page.snack_bar = ft.SnackBar(
            content=ft.Text(f"Application failed to start: {str(e)}"),
            bgcolor=ft.Colors.RED
        )
        page.snack_bar.open = True
        page.update()


if __name__ == "__main__":
    # Simple launch - let Flet handle the complexity
    ft.app(target=main, view=ft.AppView.FLET_APP)