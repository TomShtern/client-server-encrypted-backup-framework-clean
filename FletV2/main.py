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

# Unified Server Bridge with direct function calls and mock fallback
try:
    from utils.server_bridge import ServerBridge, create_server_bridge
    BRIDGE_TYPE = "Unified Server Bridge (Direct Function Calls)"
    logger.info("Using Unified Server Bridge with direct function calls and mock fallback.")
except Exception as e:
    logger.error(f"Failed to import unified server bridge: {e}")
    # Fallback to simple bridge if available
    try:
        from utils.simple_server_bridge import SimpleServerBridge as ServerBridge
        BRIDGE_TYPE = "Simple Server Bridge (Emergency Fallback)"
        logger.warning("Using emergency fallback: Simple Server Bridge")
    except Exception as e2:
        logger.error(f"Simple server bridge also failed: {e2}")
        # Import mock bridge as absolute last resort
        try:
            from utils.mock_server_bridge import MockServerBridge as ServerBridge
            BRIDGE_TYPE = "MockServerBridge (Emergency Fallback)"
            logger.warning("Using mock server bridge as final fallback")
        except Exception as e3:
            logger.critical(f"Even mock bridge failed: {e3}")
            logger.critical("Creating minimal fallback bridge")
            
            # Create minimal working bridge class
            class MinimalServerBridge:
                def __init__(self): pass
                def get_clients(self): return []
                def get_files(self): return []
                def get_server_status(self): return {"server_running": False, "error": "No bridge available"}
                def delete_client(self, client_id): return False
                def delete_file(self, file_id): return False
                
            ServerBridge = MinimalServerBridge
            BRIDGE_TYPE = "Minimal Fallback Bridge"


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
        
        # Initialize state manager for reactive UI updates
        self.state_manager = None
        self._initialize_state_manager()
        
        # Initialize server bridge with state integration asynchronously
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
        
        # Also ensure initial view loads after control is fully initialized
        # Use a small delay to ensure all controls are ready
        page.run_task(self._delayed_initial_load)
        logger.info("Page connection handler set")
    
    def _initialize_state_manager(self):
        """Initialize state manager for reactive UI updates"""
        try:
            from utils.state_manager import create_state_manager
            self.state_manager = create_state_manager(self.page)
            logger.info("State manager initialized successfully")
        except ImportError:
            logger.warning("State manager not available, UI updates will be manual")
            self.state_manager = None
        except Exception as e:
            logger.error(f"Failed to initialize state manager: {e}")
            self.state_manager = None
    
    async def _initialize_server_bridge_async(self):
        """Asynchronously initialize unified server bridge."""
        try:
            if ServerBridge:
                # For development: Initialize with no real server (fallback mode)
                # For production: Pass real server instance
                # Example production usage:
                # from python_server.server import BackupServer
                # real_server = BackupServer()
                # self.server_bridge = ServerBridge(real_server)
                
                # Development mode: No real server, uses mock data
                self.server_bridge = ServerBridge()  # Fallback mode
                
                # Connect state manager if available
                if self.state_manager:
                    # State manager integration will be handled by the bridge
                    logger.info("State manager available for bridge integration")
                
                logger.info(f"Unified server bridge initialized: {BRIDGE_TYPE}")
                logger.info("Bridge running in FALLBACK mode - using mock data for development")
            else:
                self.server_bridge = None
                logger.warning("No server bridge available")
                
        except Exception as e:
            logger.error(f"Server bridge initialization failed: {e}")
            # Emergency fallback to mock bridge if available
            try:
                from utils.mock_server_bridge import MockServerBridge
                self.server_bridge = MockServerBridge()
                logger.info("Using emergency mock bridge fallback")
            except Exception as fallback_e:
                logger.critical(f"Even mock bridge fallback failed: {fallback_e}")
                self.server_bridge = None
    
    def _on_page_connect(self, e):
        """Called when page is connected - safe to load initial view."""
        logger.info("Page connected - loading initial dashboard view")
        self._load_view("dashboard")
        logger.info("Initial dashboard view loaded")
    
    async def _delayed_initial_load(self):
        """Delayed initial load to ensure all controls are ready."""
        # Small delay to ensure UI is fully initialized
        await asyncio.sleep(0.1)
        
        # Ensure dashboard is selected and loaded
        if self.nav_rail.selected_index == 0 and self.content_area.content is None:
            logger.info("Delayed initial load - ensuring dashboard is loaded")
            self._load_view("dashboard")
            # Force update of content area
            if self.content_area.page:
                self.content_area.update()
        
        logger.info("Delayed initial load completed")
    
    def _configure_desktop_window(self):
        """Configure window for desktop application."""
        # Window settings - Updated to requested size 1730x1425
        self.page.window_min_width = 1200  # Slightly larger minimum for better UX
        self.page.window_min_height = 900
        self.page.window_width = 1730      # User requested size
        self.page.window_height = 1425     # User requested size
        self.page.window_resizable = True
        self.page.title = "Backup Server Management"
        
        # Apply theme from theme.py (source of truth)
        setup_default_theme(self.page)
        
        # Set desktop-appropriate padding
        self.page.padding = ft.Padding(0, 0, 0, 0)
        
        # Set up keyboard shortcuts
        self.page.on_keyboard_event = self._on_keyboard_event
    
    def _on_keyboard_event(self, e: ft.KeyboardEvent):
        """Handle keyboard shortcuts for navigation and actions."""
        # Only handle key down events
        if e.key not in ["R", "D", "C", "F", "B", "A", "L", "S"]:
            return
            
        # Check for Ctrl modifier
        if not e.ctrl:
            return
            
        # Handle shortcuts
        if e.key == "R":
            # Ctrl+R: Refresh current view
            logger.info("Keyboard shortcut: Refresh current view")
            self._refresh_current_view()
        elif e.key == "D":
            # Ctrl+D: Switch to dashboard
            logger.info("Keyboard shortcut: Switch to dashboard")
            self._switch_to_view(0)
        elif e.key == "C":
            # Ctrl+C: Switch to clients
            logger.info("Keyboard shortcut: Switch to clients")
            self._switch_to_view(1)
        elif e.key == "F":
            # Ctrl+F: Switch to files
            logger.info("Keyboard shortcut: Switch to files")
            self._switch_to_view(2)
        elif e.key == "B":
            # Ctrl+B: Switch to database
            logger.info("Keyboard shortcut: Switch to database")
            self._switch_to_view(3)
        elif e.key == "A":
            # Ctrl+A: Switch to analytics
            logger.info("Keyboard shortcut: Switch to analytics")
            self._switch_to_view(4)
        elif e.key == "L":
            # Ctrl+L: Switch to logs
            logger.info("Keyboard shortcut: Switch to logs")
            self._switch_to_view(5)
        elif e.key == "S":
            # Ctrl+S: Switch to settings
            logger.info("Keyboard shortcut: Switch to settings")
            self._switch_to_view(6)
    
    def _refresh_current_view(self):
        """Refresh the currently active view."""
        # Fixed: self.navigation_rail -> self.nav_rail (attribute name consistency)
        current_index = self.nav_rail.selected_index
        view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]
        if current_index < len(view_names):
            current_view = view_names[current_index]
            logger.info(f"Refreshing view: {current_view}")
            self._load_view(current_view)
    
    def _switch_to_view(self, index: int):
        """Switch to a specific view by index."""
        # Fixed: self.navigation_rail -> self.nav_rail (attribute name consistency) 
        self.nav_rail.selected_index = index
        self._on_navigation_change(type('Event', (), {'control': self.nav_rail})())
    
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
            trailing=ft.IconButton(
                icon=ft.Icons.BRIGHTNESS_6,
                tooltip="Toggle Theme",
                on_click=self._on_theme_toggle,
            ),
        )
    
    def _on_navigation_change(self, e):
        """Simple navigation callback - no complex routing."""
        # Map index to view names
        view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]
        selected_view = view_names[e.control.selected_index] if e.control.selected_index < len(view_names) else "dashboard"
        
        logger.info(f"Navigation switching to: {selected_view}")
        self._load_view(selected_view)
    
    def _on_theme_toggle(self, e):
        """Handle theme toggle button click."""
        from theme import toggle_theme_mode
        toggle_theme_mode(self.page)
        logger.info("Theme toggled")
    
    def _load_view(self, view_name: str):
        """Load view with enhanced infrastructure support and backward compatibility."""
        try:
            # Enhanced view loading with state manager integration
            if view_name == "dashboard":
                # Import and create dashboard view with enhanced infrastructure
                from views.dashboard import create_dashboard_view
                content = self._create_enhanced_view(create_dashboard_view, view_name)
            elif view_name == "clients":
                # Import and create clients view
                from views.clients import create_clients_view
                content = self._create_enhanced_view(create_clients_view, view_name)
            elif view_name == "files":
                # Import and create files view
                from views.files import create_files_view
                content = self._create_enhanced_view(create_files_view, view_name)
            elif view_name == "database":
                # Import and create database view
                from views.database import create_database_view
                content = self._create_enhanced_view(create_database_view, view_name)
            elif view_name == "analytics":
                # Import and create analytics view
                from views.analytics import create_analytics_view
                content = self._create_enhanced_view(create_analytics_view, view_name)
            elif view_name == "logs":
                # Import and create logs view
                from views.logs import create_logs_view
                content = self._create_enhanced_view(create_logs_view, view_name)
            elif view_name == "settings":
                # Import and create settings view
                from views.settings import create_settings_view
                content = self._create_enhanced_view(create_settings_view, view_name)
            else:
                # Import and create dashboard view as fallback
                from views.dashboard import create_dashboard_view
                content = self._create_enhanced_view(create_dashboard_view, "dashboard")
            
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
    
    def _create_enhanced_view(self, view_function, view_name: str):
        """Create view with enhanced infrastructure support and backward compatibility."""
        import inspect
        
        try:
            # Get function signature to determine parameter support
            signature = inspect.signature(view_function)
            param_names = list(signature.parameters.keys())
            
            # Update current view in state manager
            if self.state_manager:
                # Use run_task for async state update
                async def update_current_view():
                    await self.state_manager.update_state("current_view", view_name)
                self.page.run_task(update_current_view)
            
            # Enhanced view creation: Try passing state_manager if function supports it
            if len(param_names) >= 3 and 'state_manager' in param_names:
                # Enhanced view with state manager support
                logger.debug(f"Creating enhanced {view_name} view with state manager")
                return view_function(self.server_bridge, self.page, state_manager=self.state_manager)
            else:
                # Legacy view - backward compatibility
                logger.debug(f"Creating legacy {view_name} view without state manager")
                return view_function(self.server_bridge, self.page)
                
        except Exception as e:
            logger.error(f"Enhanced view creation failed for {view_name}: {e}", exc_info=True)
            # Fallback to basic view creation
            try:
                return view_function(self.server_bridge, self.page)
            except Exception as fallback_e:
                logger.error(f"Even basic view creation failed for {view_name}: {fallback_e}", exc_info=True)
                return self._create_error_view(f"Failed to create {view_name} view: {fallback_e}")
    
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
            bgcolor=ft.Colors.RED,
            duration=3000
        )
        page.snack_bar.open = True
        page.update()


if __name__ == "__main__":
    # Simple launch - let Flet handle the complexity
    ft.app(target=main, view=ft.AppView.FLET_APP)