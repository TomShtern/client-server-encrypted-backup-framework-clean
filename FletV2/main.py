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

# Auto-enable UTF-8 for all subprocess operations
import sys
import os
# Add parent directory to path for Shared imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import Shared.utils.utf8_solution

# Add project root to Python path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

# Use our clean utilities
from theme import setup_default_theme, toggle_theme_mode

# Server bridge with fallback
try:
    from utils.server_bridge import ModularServerBridge as ServerBridge
    BRIDGE_TYPE = "Full ModularServerBridge"
except Exception:
    from utils.simple_server_bridge import SimpleServerBridge as ServerBridge
    BRIDGE_TYPE = "SimpleServerBridge (Fallback)"


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
        
        # Initialize server bridge with fallback
        try:
            self.server_bridge = ServerBridge()
            print(f"[SUCCESS] Server bridge initialized: {BRIDGE_TYPE}")
        except Exception as e:
            print(f"[WARNING] Server bridge failed, using mock: {e}")
            self.server_bridge = None
        
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
        page.on_connect = self._on_page_connect
    
    def _on_page_connect(self, e):
        """Called when page is connected - safe to load initial view."""
        self._load_view("dashboard")
    
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
        
        print(f"[NAVIGATION] Switching to: {selected_view}")
        self._load_view(selected_view)
    
    def _load_view(self, view_name: str):
        """Load view using simple function calls - no complex view managers."""
        try:
            # Simple view switching with direct function calls
            if view_name == "dashboard":
                content = self._create_dashboard_view()
            elif view_name == "clients":
                # Import and create clients view
                from views.clients import create_clients_view
                content = create_clients_view(self.server_bridge, self.page)
            elif view_name == "files":
                content = self._create_files_view()
            elif view_name == "database":
                # Import and create database view
                from views.database import create_database_view
                content = create_database_view(self.server_bridge, self.page)
            elif view_name == "analytics":
                # Import and create analytics view
                from views.analytics import create_analytics_view
                content = create_analytics_view(self.server_bridge, self.page)
            elif view_name == "logs":
                content = self._create_logs_view()
            elif view_name == "settings":
                # Import and create settings view
                from views.settings import create_settings_view
                content = create_settings_view(self.server_bridge, self.page)
            else:
                content = self._create_dashboard_view()
            
            # Update content area (simple assignment, no complex managers)
            self.content_area.content = content
            # Only update if the control is attached to the page
            if self.page and hasattr(self.content_area, 'page') and self.content_area.page:
                self.content_area.update()
            
        except Exception as e:
            print(f"[ERROR] Failed to load view {view_name}: {e}")
            # Fallback to simple error view
            self.content_area.content = self._create_error_view(str(e))
            # Only update if the control is attached to the page
            if self.page and hasattr(self.content_area, 'page') and self.content_area.page:
                self.content_area.update()
    
    def _create_dashboard_view(self) -> ft.Control:
        """Simple dashboard view - uses Flet built-ins only."""
        # Get server status (with fallback)
        server_status = "Running" if self.server_bridge else "Unavailable"
        status_color = ft.Colors.GREEN if self.server_bridge else ft.Colors.ORANGE
        
        return ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),  # Spacer
                    ft.IconButton(
                        icon=ft.Icons.DARK_MODE,
                        tooltip="Toggle theme",
                        on_click=lambda _: toggle_theme_mode(self.page)
                    )
                ]),
                padding=ft.Padding(20, 20, 20, 10)
            ),
            
            # Status cards using simple ResponsiveRow
            ft.ResponsiveRow([
                ft.Column([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Server Status", weight=ft.FontWeight.BOLD),
                                ft.Text(server_status, color=status_color, size=16)
                            ], spacing=8),
                            padding=20
                        ),
                        expand=True
                    )
                ], col={"sm": 12, "md": 4}, expand=True),
                
                ft.Column([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("Bridge Type", weight=ft.FontWeight.BOLD),
                                ft.Text(BRIDGE_TYPE, size=12)
                            ], spacing=8),
                            padding=20
                        ),
                        expand=True
                    )
                ], col={"sm": 12, "md": 4}, expand=True),
                
                ft.Column([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("System", weight=ft.FontWeight.BOLD),
                                ft.Text("Desktop App", size=16)
                            ], spacing=8),
                            padding=20
                        ),
                        expand=True
                    )
                ], col={"sm": 12, "md": 4}, expand=True)
            ])
        ], expand=True, scroll=ft.ScrollMode.AUTO)
    
    def _create_files_view(self) -> ft.Control:
        """Simple files view."""
        return ft.Container(
            content=ft.Column([
                ft.Text("File Management", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Transferred files and file operations.", size=16),
                ft.Card(
                    content=ft.Container(
                        content=ft.Text("File browser functionality will be integrated here."),
                        padding=20
                    ),
                    expand=True
                )
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def _create_database_view(self) -> ft.Control:
        """Simple database view."""
        return ft.Container(
            content=ft.Column([
                ft.Text("Database Operations", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Database queries and management.", size=16),
                ft.Card(
                    content=ft.Container(
                        content=ft.Text("Database interface will be integrated here."),
                        padding=20
                    ),
                    expand=True
                )
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def _create_analytics_view(self) -> ft.Control:
        """Simple analytics view."""
        return ft.Container(
            content=ft.Column([
                ft.Text("Analytics & Performance", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("System performance metrics and charts.", size=16),
                ft.Card(
                    content=ft.Container(
                        content=ft.Text("Performance charts will be integrated here."),
                        padding=20
                    ),
                    expand=True
                )
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def _create_logs_view(self) -> ft.Control:
        """Simple logs view."""
        return ft.Container(
            content=ft.Column([
                ft.Text("System Logs", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Real-time system and transfer logs.", size=16),
                ft.Card(
                    content=ft.Container(
                        content=ft.Text("Log monitoring will be integrated here."),
                        padding=20
                    ),
                    expand=True
                )
            ], spacing=20),
            padding=20,
            expand=True
        )
    
    def _create_settings_view(self) -> ft.Control:
        """Simple settings view."""
        return ft.Container(
            content=ft.Column([
                ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Application configuration and preferences.", size=16),
                ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("Theme Settings", weight=ft.FontWeight.BOLD),
                            ft.ElevatedButton(
                                "Toggle Dark/Light Mode",
                                on_click=lambda _: toggle_theme_mode(self.page)
                            ),
                            ft.Divider(),
                            ft.Text("Server Settings", weight=ft.FontWeight.BOLD),
                            ft.Text("Server configuration options will be available here.")
                        ], spacing=12),
                        padding=20
                    ),
                    expand=True
                )
            ], spacing=20),
            padding=20,
            expand=True
        )
    
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
        
        print(f"[SUCCESS] FletV2 App started - {BRIDGE_TYPE} active")
        
    except Exception as e:
        print(f"[ERROR] Failed to start application: {e}")
        # Simple error fallback
        page.add(ft.Text(f"Failed to start: {e}", color=ft.Colors.ERROR))


if __name__ == "__main__":
    # Simple launch - let Flet handle the complexity
    ft.app(target=main, view=ft.AppView.FLET_APP)