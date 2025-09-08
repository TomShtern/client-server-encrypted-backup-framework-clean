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

# Use our modern 2025 theme system with enhanced visuals
from theme import setup_modern_theme, toggle_theme_mode

# Import the unified server bridge with built-in mock fallback
from utils.server_bridge import ServerBridge, create_server_bridge
BRIDGE_TYPE = "Unified Server Bridge (with built-in mock fallback)"
logger.info("Using Unified Server Bridge with built-in mock fallback.")


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
        
        # Initialize server bridge synchronously for immediate availability
        self.server_bridge = create_server_bridge()  # Direct synchronous initialization
        logger.info(f"Server bridge initialized: {BRIDGE_TYPE}")
        
        # Create enhanced content area with sophisticated animated transitions
        self.content_area = ft.Container(
            expand=True,
            padding=ft.Padding(20, 16, 20, 16),  # Reduced padding for more content space
            border_radius=ft.BorderRadius(12, 0, 0, 12),  # Slightly smaller radius
            bgcolor=ft.Colors.with_opacity(0.015, ft.Colors.PRIMARY),  # More subtle background
            # Add modern visual depth with subtle shadow
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT),  # Faster, more efficient
            animate_opacity=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
            content=ft.AnimatedSwitcher(
                content=ft.Container(  # Start with empty container instead of None
                    content=ft.Text("Loading...", size=16),
                    padding=20,
                    expand=True
                ),
                transition=ft.AnimatedSwitcherTransition.SCALE,  # Enhanced scale transition
                duration=400,  # Slightly longer for more noticeable effect
                reverse_duration=300,
                switch_in_curve=ft.AnimationCurve.EASE_OUT_BACK,  # Bouncy entrance
                switch_out_curve=ft.AnimationCurve.EASE_IN,  # Smooth exit
                expand=True
            )
        )
        
        # Create navigation rail (using simple approach with collapsible functionality)
        self.nav_rail_extended = True  # Track extended state
        self.nav_rail = self._create_navigation_rail()
        
        # Build layout: NavigationRail + content area (pure Flet pattern)
        self.controls = [
            self.nav_rail,
            ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            self.content_area
        ]
        
        # Set up page connection handler to load initial view
        logger.info("Setting up page connection handler")
        page.on_connect = self._on_page_connect
        
        # Load dashboard immediately instead of waiting for page connection
        logger.info("Loading initial dashboard view immediately")
        try:
            self._load_view("dashboard")
            logger.info("Initial dashboard view loaded successfully")
        except Exception as ex:
            logger.error(f"Failed to load initial dashboard view: {ex}", exc_info=True)
            # Fallback: show error in content area
            try:
                self.content_area.content.content = ft.Container(
                    content=ft.Text(f"Failed to load dashboard: {ex}", color=ft.Colors.ERROR),
                    padding=20,
                    expand=True
                )
                self.content_area.content.update()
            except Exception as fallback_ex:
                logger.error(f"Even fallback failed: {fallback_ex}")
    
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
    
    def _on_page_connect(self, e):
        """Called when page is connected - handle reconnection scenarios."""
        logger.info("Page connected event received")
        # Dashboard is already loaded in constructor, but we can refresh if needed
        try:
            # Check if we need to refresh the current view
            animated_switcher = self.content_area.content
            if hasattr(animated_switcher, 'content') and animated_switcher.content:
                current_content = animated_switcher.content
                if hasattr(current_content, '_on_page_connect'):
                    current_content._on_page_connect()
                    logger.info("Current view page connect callback executed")
        except Exception as callback_error:
            logger.debug(f"Could not call view page connect callback: {callback_error}")
    
    def _configure_desktop_window(self):
        """Configure window for desktop application."""
        # Window settings - Updated to requested size 1730x1425
        self.page.window_min_width = 1200  # Slightly larger minimum for better UX
        self.page.window_min_height = 900
        self.page.window_width = 1730      # User requested size
        self.page.window_height = 1425     # User requested size
        self.page.window_resizable = True
        self.page.title = "Backup Server Management"
        
        # Apply 2025 modern theme with vibrant colors and enhanced effects
        setup_modern_theme(self.page)
        
        # Add performance optimizations - Visual Density for reduced spacing
        self.page.theme.visual_density = ft.VisualDensity.COMPACT
        
        # Set desktop-appropriate padding (reduced for more content space)
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
        # Access NavigationRail through container content
        nav_rail_control = self.nav_rail.content
        current_index = nav_rail_control.selected_index
        view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]
        if current_index < len(view_names):
            current_view = view_names[current_index]
            logger.info(f"Refreshing view: {current_view}")
            self._load_view(current_view)
    
    def _switch_to_view(self, index: int):
        """Switch to a specific view by index."""
        # Access NavigationRail through container content
        nav_rail_control = self.nav_rail.content
        nav_rail_control.selected_index = index
        self._on_navigation_change(type('Event', (), {'control': nav_rail_control})())
    
    def _create_navigation_rail(self):
        """Create enhanced collapsible navigation rail with modern 2025 UI styling."""
        return ft.Container(
            content=ft.NavigationRail(
                selected_index=0,
                label_type=ft.NavigationRailLabelType.ALL,
                group_alignment=-0.8,
                min_width=68,  # Collapsed width (icons only)
                min_extended_width=240,  # Extended width (2025 standard)
                extended=self.nav_rail_extended,  # Collapsible functionality
                bgcolor=ft.Colors.with_opacity(0.98, ft.Colors.SURFACE),  # Enhanced transparency
                indicator_color=ft.Colors.with_opacity(0.15, ft.Colors.PRIMARY),  # More vibrant indicator
                indicator_shape=ft.RoundedRectangleBorder(radius=20),  # More modern rounding
                elevation=4,  # Enhanced depth for 2025 layering
                destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icon(
                        ft.Icons.DASHBOARD,
                        color=ft.Colors.PRIMARY,
                        size=24
                    ),
                    label="Dashboard"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE_OUTLINE,
                    selected_icon=ft.Icon(
                        ft.Icons.PEOPLE,
                        color=ft.Colors.PRIMARY,
                        size=24
                    ),
                    label="Clients"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FOLDER_OUTLINED,
                    selected_icon=ft.Icon(
                        ft.Icons.FOLDER,
                        color=ft.Colors.PRIMARY,
                        size=24
                    ),
                    label="Files"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.STORAGE_OUTLINED,
                    selected_icon=ft.Icon(
                        ft.Icons.STORAGE,
                        color=ft.Colors.PRIMARY,
                        size=24
                    ),
                    label="Database"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.AUTO_GRAPH_OUTLINED,
                    selected_icon=ft.Icon(
                        ft.Icons.AUTO_GRAPH,
                        color=ft.Colors.PRIMARY,
                        size=24
                    ),
                    label="Analytics"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ARTICLE_OUTLINED,
                    selected_icon=ft.Icon(
                        ft.Icons.ARTICLE,
                        color=ft.Colors.PRIMARY,
                        size=24
                    ),
                    label="Logs"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icon(
                        ft.Icons.SETTINGS,
                        color=ft.Colors.PRIMARY,
                        size=24
                    ),
                    label="Settings"
                ),
                ],
                on_change=self._on_navigation_change,
                leading=ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.MENU_ROUNDED if self.nav_rail_extended else ft.Icons.MENU_OPEN_ROUNDED,
                        icon_size=24,
                        tooltip="Toggle Navigation Menu",
                        on_click=self._toggle_navigation_rail,
                        style=ft.ButtonStyle(
                            color=ft.Colors.PRIMARY,
                            shape=ft.RoundedRectangleBorder(radius=14),
                            overlay_color={
                                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                                ft.ControlState.PRESSED: ft.Colors.with_opacity(0.15, ft.Colors.PRIMARY)
                            },
                            padding=ft.Padding(8, 8, 8, 8)
                        )
                    ),
                    padding=ft.Padding(8, 16, 8, 8),
                    animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT)  # Shorter animation
                ),
                trailing=ft.Container(
                    content=ft.IconButton(
                        icon=ft.Icons.BRIGHTNESS_6_ROUNDED,
                        icon_size=22,
                        tooltip="Toggle Dark/Light Theme",
                        on_click=self._on_theme_toggle,
                        style=ft.ButtonStyle(
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            shape=ft.RoundedRectangleBorder(radius=14),
                            overlay_color={
                                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY),
                                ft.ControlState.PRESSED: ft.Colors.with_opacity(0.12, ft.Colors.PRIMARY)
                            },
                            padding=ft.Padding(8, 8, 8, 8)
                        )
                    ),
                    padding=ft.Padding(8, 8, 8, 16),
                    animate=ft.Animation(100, ft.AnimationCurve.EASE_OUT)  # Shorter animation
                )
            ),
            # Enhanced modern depth with 2025 design standards - layering effect
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=24,  # Enhanced blur for modern depth
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),  # Stronger shadow
                offset=ft.Offset(4, 0),  # Slightly more offset for depth
            ),
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),  # Shorter but smooth collapse animation
            border_radius=ft.BorderRadius(0, 16, 16, 0),  # Modern rounded corners
        )

    def _toggle_navigation_rail(self, e=None):
        """Toggle navigation rail between extended and collapsed states with enhanced smooth animation."""
        self.nav_rail_extended = not self.nav_rail_extended
        
        # Update the navigation rail extended state
        nav_rail_control = self.nav_rail.content
        nav_rail_control.extended = self.nav_rail_extended
        
        # Update the toggle icon with smooth rotation animation
        toggle_btn = nav_rail_control.leading.content
        toggle_btn.icon = ft.Icons.MENU_ROUNDED if self.nav_rail_extended else ft.Icons.MENU_OPEN_ROUNDED
        
        # Add subtle rotation animation to the toggle button
        toggle_btn.rotate = ft.Rotate(0.5 if self.nav_rail_extended else 0)
        toggle_btn.animate_rotation = ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        
        # Smooth animation for the navigation rail with enhanced curves
        self.nav_rail.animate = ft.Animation(250, ft.AnimationCurve.EASE_OUT_CUBIC)
        self.nav_rail.update()
        
        logger.info(f"Navigation rail {'extended' if self.nav_rail_extended else 'collapsed'} with enhanced animation")

    def _on_navigation_change(self, e):
        """Enhanced navigation callback with loading indicator and smooth transitions."""
        # Map index to view names
        view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]
        selected_view = view_names[e.control.selected_index] if e.control.selected_index < len(view_names) else "dashboard"
        
        logger.info(f"Navigation switching to: {selected_view} with enhanced animation")
        
        # Show subtle loading indicator during transition
        self._show_loading_indicator()
        
        # Load view with enhanced animation
        self._load_view(selected_view)
    
    async def _on_theme_toggle(self, e):
        """Handle theme toggle button click with smooth animation."""
        try:
            from theme import toggle_theme_mode
            toggle_theme_mode(self.page)
            
            # Add subtle animation feedback to the toggle button
            toggle_btn = e.control
            original_icon = toggle_btn.icon
            
            # Quick scale animation for visual feedback
            toggle_btn.scale = 0.9
            toggle_btn.animate_scale = ft.Animation(100, ft.AnimationCurve.EASE_OUT)
            toggle_btn.update()
            
            # Reset scale after animation using asyncio.sleep for proper timing
            import asyncio
            await asyncio.sleep(0.1)  # 100ms delay
            
            def reset_scale():
                toggle_btn.scale = 1.0
                toggle_btn.animate_scale = ft.Animation(100, ft.AnimationCurve.EASE_OUT)
                toggle_btn.update()
            
            reset_scale()
            
            logger.info("Theme toggled successfully with animation feedback")
            
        except Exception as ex:
            logger.error(f"Failed to toggle theme: {ex}", exc_info=True)
            # Show error feedback
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Failed to toggle theme: {ex}"),
                bgcolor=ft.Colors.ERROR,
                duration=3000
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def _show_loading_indicator(self):
        """Show subtle loading indicator during view transitions."""
        try:
            # Create a subtle loading overlay
            loading_content = ft.Container(
                content=ft.Column([
                    ft.Container(height=40),  # Spacer
                    ft.ProgressRing(
                        width=32,
                        height=32,
                        stroke_width=3,
                        color=ft.Colors.PRIMARY,
                        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY)
                    ),
                    ft.Container(height=16),  # Spacer
                    ft.Text(
                        "Loading...",
                        size=14,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER
                    )
                ], 
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
                ),
                padding=20,
                expand=True
            )
            
            # Temporarily show loading indicator
            animated_switcher = self.content_area.content
            animated_switcher.content = loading_content
            
            # Defensive update for loading indicator
            try:
                if hasattr(self.page, 'controls') and self.page.controls:
                    animated_switcher.update()
                else:
                    logger.debug("Page not ready for loading indicator update")
            except Exception as update_error:
                logger.debug(f"Loading indicator update failed: {update_error}")
                # Don't fail the entire operation for loading indicator
            
        except Exception as e:
            logger.debug(f"Could not show loading indicator: {e}")
            # Continue without loading indicator if it fails
    
    def _set_animation_for_view(self, view_name: str):
        """Dynamically set animation type and parameters based on view for enhanced UX."""
        animated_switcher = self.content_area.content
        
        # Different animation styles for different views
        if view_name == "dashboard":
            # Dashboard: Scale with bounce for welcoming feel
            animated_switcher.transition = ft.AnimatedSwitcherTransition.SCALE
            animated_switcher.duration = 450
            animated_switcher.reverse_duration = 350
            animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT_BACK
            animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN_OUT
            
        elif view_name == "clients":
            # Clients: Slide from right for data flow feel
            animated_switcher.transition = ft.AnimatedSwitcherTransition.SCALE
            animated_switcher.duration = 400
            animated_switcher.reverse_duration = 300
            animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT_CUBIC
            animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN_CUBIC
            
        elif view_name == "files":
            # Files: Fade with elastic for file browsing feel
            animated_switcher.transition = ft.AnimatedSwitcherTransition.FADE
            animated_switcher.duration = 350
            animated_switcher.reverse_duration = 250
            animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT
            animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN
            
        elif view_name == "database":
            # Database: Scale with smooth curves for data stability
            animated_switcher.transition = ft.AnimatedSwitcherTransition.SCALE
            animated_switcher.duration = 500
            animated_switcher.reverse_duration = 400
            animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT_QUART
            animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN_QUART
            
        elif view_name == "analytics":
            # Analytics: Scale with bounce for dynamic data visualization
            animated_switcher.transition = ft.AnimatedSwitcherTransition.SCALE
            animated_switcher.duration = 420
            animated_switcher.reverse_duration = 320
            animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT_BACK
            animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN_BACK
            
        elif view_name == "logs":
            # Logs: Fade for quick transitions in log viewing
            animated_switcher.transition = ft.AnimatedSwitcherTransition.FADE
            animated_switcher.duration = 300
            animated_switcher.reverse_duration = 200
            animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT
            animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN
            
        elif view_name == "settings":
            # Settings: Scale with smooth transition for configuration feel
            animated_switcher.transition = ft.AnimatedSwitcherTransition.SCALE
            animated_switcher.duration = 380
            animated_switcher.reverse_duration = 280
            animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT_CUBIC
            animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN_CUBIC
        
        logger.debug(f"Set animation for {view_name}: {animated_switcher.transition}, duration={animated_switcher.duration}ms")
    
    def _load_view(self, view_name: str):
        """Load view with enhanced infrastructure support and dynamic animated transitions."""
        try:
            # Enhanced view loading with state manager integration
            if view_name == "dashboard":
                # Import and create dashboard view with enhanced infrastructure
                from views.dashboard import create_dashboard_view
                content = self._create_enhanced_view(create_dashboard_view, view_name)
                self._set_animation_for_view("dashboard")
            elif view_name == "clients":
                # Import and create clients view
                from views.clients import create_clients_view
                content = self._create_enhanced_view(create_clients_view, view_name)
                self._set_animation_for_view("clients")
            elif view_name == "files":
                # Import and create files view
                from views.files import create_files_view
                content = self._create_enhanced_view(create_files_view, view_name)
                self._set_animation_for_view("files")
            elif view_name == "database":
                # Import and create database view
                from views.database import create_database_view
                content = self._create_enhanced_view(create_database_view, view_name)
                self._set_animation_for_view("database")
            elif view_name == "analytics":
                # Import and create analytics view
                from views.analytics import create_analytics_view
                content = self._create_enhanced_view(create_analytics_view, view_name)
                self._set_animation_for_view("analytics")
            elif view_name == "logs":
                # Import and create logs view
                from views.logs import create_logs_view
                content = self._create_enhanced_view(create_logs_view, view_name)
                self._set_animation_for_view("logs")
            elif view_name == "settings":
                # Import and create settings view
                from views.settings import create_settings_view
                content = self._create_enhanced_view(create_settings_view, view_name)
                self._set_animation_for_view("settings")
            else:
                # Import and create dashboard view as fallback
                from views.dashboard import create_dashboard_view
                content = self._create_enhanced_view(create_dashboard_view, "dashboard")
                self._set_animation_for_view("dashboard")
            
            # Update content area using AnimatedSwitcher for smooth transitions
            animated_switcher = self.content_area.content
            animated_switcher.content = content

            # Smart update - check if control is attached to page before updating
            try:
                # Verify AnimatedSwitcher is properly attached to page
                if hasattr(animated_switcher, 'page') and animated_switcher.page is not None:
                    animated_switcher.update()
                    logger.info(f"Successfully loaded {view_name} view")
                else:
                    # Control not yet attached, use page update as fallback
                    logger.debug("AnimatedSwitcher not yet attached to page, using page update")
                    self.page.update()
                    logger.info(f"Successfully loaded {view_name} view (page update fallback)")
            except Exception as update_error:
                logger.warning(f"AnimatedSwitcher update failed, using page update: {update_error}")
                try:
                    self.page.update()
                    logger.info(f"Successfully loaded {view_name} view (page update fallback)")
                except Exception as fallback_error:
                    logger.error(f"Page update also failed: {fallback_error}")
            
        except Exception as e:
            logger.error(f"Failed to load view {view_name}: {e}")
            # Simple error fallback
            try:
                animated_switcher = self.content_area.content
                animated_switcher.content = self._create_error_view(str(e))
                animated_switcher.update()
            except Exception as fallback_error:
                logger.error(f"Error view display failed: {fallback_error}")
                # Last resort
                try:
                    self.page.update()
                except Exception:
                    pass
    
    def _create_enhanced_view(self, view_function, view_name: str):
        """Create view with simplified synchronous approach for better performance."""
        try:
            # Simple synchronous view creation - no complex async handling
            try:
                # Try with state_manager first
                result = view_function(self.server_bridge, self.page, state_manager=self.state_manager)
            except TypeError:
                # Fallback without state_manager
                result = view_function(self.server_bridge, self.page)

            # Return the result directly - no async detection or placeholder logic
            return result

        except Exception as e:
            logger.error(f"View creation failed for {view_name}: {e}")
            return self._create_error_view(f"Failed to create {view_name} view: {e}")
    
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
async def main(page: ft.Page):
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
    asyncio.run(ft.app_async(target=main, view=ft.AppView.FLET_APP))