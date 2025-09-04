#!/usr/bin/env python3
"""
HIROSHIMA IDEAL: Simplified Flet Desktop App

This demonstrates the clean architecture after Semi-Nuclear transformation:
- ~150 lines total (vs 1000+ in the original)
- Uses Flet built-ins exclusively (no framework fighting)
- Simple NavigationRail.on_change callback (no complex routing)
- Proper theme.py integration
- Server bridge with fallback
- UTF-8 support
- Resizable desktop app configuration

This is what the architecture looks like after eliminating overengineering.
"""

import flet as ft
import asyncio
import sys
import os
import traceback
from typing import Optional
from datetime import datetime

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
from utils.navigation_enums import NavigationView
from utils.simple_navigation import SimpleNavigationState, create_simple_navigation_rail
from utils.accessibility_helpers import ensure_windowed_compatibility
from theme import setup_default_theme, toggle_theme_mode

# Server bridge with fallback
try:
    from utils.server_bridge import ModularServerBridge as ServerBridge
    BRIDGE_TYPE = "Full ModularServerBridge"
except Exception:
    from utils.simple_server_bridge import SimpleServerBridge as ServerBridge
    BRIDGE_TYPE = "SimpleServerBridge (Fallback)"


class SimpleDesktopApp(ft.Row):
    """
    Hiroshima Ideal: Simple desktop app using pure Flet patterns.
    
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
        
        # Initialize navigation state (simple tracking, no complex managers)
        self.nav_state = SimpleNavigationState()
        
        # Initialize server bridge with fallback
        try:
            self.server_bridge = ServerBridge()
            print(f"[SUCCESS] Server bridge initialized: {BRIDGE_TYPE}")
        except Exception as e:
            print(f"[WARNING] Server bridge failed, using mock: {e}")
            self.server_bridge = None
        
        # Create content area
        self.content_area = ft.Container(expand=True)
        
        # Create navigation rail (using our clean utility)
        self.nav_rail = create_simple_navigation_rail(
            nav_state=self.nav_state,
            on_change_callback=self._on_navigation_change,
            extended=False
        )
        
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
        self._load_view(NavigationView.DASHBOARD.value)
    
    def _configure_desktop_window(self):
        """Configure window for desktop application."""
        # Window settings
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        self.page.window_resizable = True
        self.page.title = "Backup Server Management"
        
        # Apply theme from theme.py (source of truth)
        setup_default_theme(self.page)
        
        # Set desktop-appropriate padding
        self.page.padding = ft.Padding(0, 0, 0, 0)
    
    def _on_navigation_change(self, view_name: str):
        """Simple navigation callback - no complex routing."""
        print(f"[NAVIGATION] Switching to: {view_name}")
        self._load_view(view_name)
    
    def _load_view(self, view_name: str):
        """Load view using simple function calls - no complex view managers."""
        try:
            # Simple view switching with direct function calls
            if view_name == NavigationView.DASHBOARD.value:
                content = self._create_dashboard_view()
            elif view_name == NavigationView.CLIENTS.value:
                content = self._create_clients_view()
            elif view_name == NavigationView.FILES.value:
                content = self._create_files_view()
            elif view_name == NavigationView.DATABASE.value:
                content = self._create_database_view()
            elif view_name == NavigationView.ANALYTICS.value:
                content = self._create_analytics_view()
            elif view_name == NavigationView.LOGS.value:
                content = self._create_logs_view()
            elif view_name == NavigationView.SETTINGS.value:
                content = self._create_settings_view()
            else:
                content = self._create_dashboard_view()
            
            # Use accessibility helper to ensure windowed compatibility
            accessible_content = ensure_windowed_compatibility(content)
            
            # Update content area (simple assignment, no complex managers)
            self.content_area.content = accessible_content
            # Only update if the control is attached to the page
            if self.page and hasattr(self.content_area, 'page') and self.content_area.page:
                self.content_area.update()
            
        except Exception as e:
            error_details = f"[ERROR] Failed to load view {view_name}: {e}\n"
            error_details += f"[TYPE] {type(e)}\n"
            try:
                tb_str = traceback.format_exc()
                error_details += f"[TRACEBACK]\n{tb_str}"
            except Exception as tb_e:
                error_details += f"[TRACEBACK_ERROR] Could not format traceback: {tb_e}"

            print(error_details)  # Try printing to console
            
            # Write to a debug file as a reliable fallback
            with open("debug_error.log", "a") as f:
                f.write(f"---\n{{datetime.now()}}---\n{{error_details}}\n\n")

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
    
    def _create_clients_view(self) -> ft.Control:
        """Placeholder for clients view."""
        return ft.Container(
            content=ft.Column([
                ft.Text("Client Management", size=24, weight=ft.FontWeight.BOLD),
                ft.Text("Client view is under reconstruction.", size=16),
            ]),
            padding=20,
            expand=True
        )
    
    def _create_files_view(self) -> ft.Control:
        """Creates the 'Files' view using the new simplified implementation."""
        try:
            from FletV2.views.files import create_files_view
            return create_files_view()
        except Exception as e:
            print(f"[ERROR] Failed to create files view: {e}")
            return self._create_error_view(f"Failed to load Files view: {e}")
    
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
                    on_click=lambda _: self._load_view(NavigationView.DASHBOARD.value)
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
        app = SimpleDesktopApp(page)
        page.add(app)
        
        print(f"[SUCCESS] Hiroshima Ideal App started - {BRIDGE_TYPE} active")
        
    except Exception as e:
        print(f"[ERROR] Failed to start application: {e}")
        # Simple error fallback
        page.add(ft.Text(f"Failed to start: {e}", color=ft.Colors.ERROR))


if __name__ == "__main__":
    # Simple launch - let Flet handle the complexity
    ft.app(target=main, view=ft.AppView.FLET_APP)