#!/usr/bin/env python3
"""
FletV2 - Clean Desktop Ap    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.expand = True

        # Performance optimization: lazy view loading
        self._loaded_views = {}  # Cache for loaded views
        self._background_tasks = set()  # Track background tasks

        # Window configuration moved to main() function for proper timing

        # Initialize state manager with performance optimizations
        self.state_manager = None
        self._initialize_state_manager()

        # Initialize server bridge synchronously for immediate availability
        self.server_bridge = create_server_bridge()  # Direct synchronous initialization
        logger.info(f"Server bridge initialized: {BRIDGE_TYPE}")

        # Create optimized content area with fast transitions for better performanceerly implemented Flet desktop application following best practices.

This demonstrates the clean architecture:
- Uses Flet built-ins exclusively (no framework fighting)
- Simple NavigationRail.on_change callback (no complex routing)
- Proper theme.py integration
- Server bridge with fallback
- UTF-8 support
- Resizable desktop app configuration
"""

# Standard library imports
import asyncio
import os
import sys

# Third-party imports
import flet as ft

# Local imports - utilities first
from utils.debug_setup import setup_terminal_debugging, get_logger
try:
    from utils import utf8_patch  # noqa: F401 (side effects only)
except ImportError:
    pass  # Non-fatal; continue without extra patch

# Local imports - application modules
from theme import setup_modern_theme, toggle_theme_mode
from utils.server_bridge import ServerBridge, create_server_bridge
from utils.mock_mode_indicator import create_mock_mode_banner, add_mock_indicator_to_snackbar_message

# Initialize logging and environment
logger = setup_terminal_debugging(logger_name="FletV2.main")
os.environ.setdefault("PYTHONUTF8", "1")

# Ensure project root is in path for direct execution
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Application constants
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

        # Window configuration moved to main() function for proper timing

        # Initialize state manager for reactive UI updates
        self.state_manager = None
        self._initialize_state_manager()

        # Initialize server bridge synchronously for immediate availability
        self.server_bridge = create_server_bridge()  # Direct synchronous initialization
        logger.info(f"Server bridge initialized: {BRIDGE_TYPE}")

        # Create optimized content area with modern Material Design 3 styling and fast transitions
        self.content_area = ft.Container(
            expand=True,
            padding=ft.Padding(24, 20, 24, 20),  # Material Design 3 spacing standards
            border_radius=ft.BorderRadius(16, 0, 0, 16),  # Modern rounded corners on content side
            bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.SURFACE),  # Modern surface hierarchy compatible
            # Enhanced shadow for modern depth without performance impact
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            animate=ft.Animation(140, ft.AnimationCurve.EASE_OUT_CUBIC),  # Modern animation curve
            animate_opacity=ft.Animation(100, ft.AnimationCurve.EASE_OUT),
            content=ft.AnimatedSwitcher(
                content=ft.Card(  # Modern card-based loading state
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.ProgressRing(
                                    width=24,
                                    height=24,
                                    stroke_width=3,
                                    color=ft.Colors.PRIMARY,
                                ),
                                ft.Text(
                                    "Loading Application...",
                                    size=16,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.ON_SURFACE_VARIANT
                                ),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
                            ft.Chip(
                                label=ft.Text("Encrypted Backup Framework", size=12),
                                bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                                color=ft.Colors.PRIMARY,
                                height=32,
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
                        padding=24,
                        expand=True,
                        alignment=ft.alignment.center
                    ),
                    elevation=2,
                    shadow_color=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                    surface_tint_color=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
                ),
                transition=ft.AnimatedSwitcherTransition.FADE,  # Optimal performance transition
                duration=160,  # Balanced for smoothness and speed
                reverse_duration=100,
                switch_in_curve=ft.AnimationCurve.EASE_OUT_CUBIC,  # Modern curves
                switch_out_curve=ft.AnimationCurve.EASE_IN_CUBIC,
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
        """Create enhanced collapsible navigation rail with modern 2025 UI styling and performance optimizations."""
        return ft.Container(
            content=ft.NavigationRail(
                selected_index=0,
                label_type=ft.NavigationRailLabelType.ALL,
                group_alignment=-0.8,
                min_width=68,  # Collapsed width (icons only)
                min_extended_width=240,  # Extended width (2025 standard)
                extended=self.nav_rail_extended,  # Collapsible functionality
                bgcolor=ft.Colors.with_opacity(0.98, ft.Colors.SURFACE),  # Material Design 3 compatible surface
                indicator_color=ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY),  # Enhanced visibility with optimal opacity
                indicator_shape=ft.RoundedRectangleBorder(radius=24),  # Material Design 3 rounded corners
                elevation=6,  # Enhanced depth for modern layering without performance impact
                destinations=[
                # Dashboard with modern badge indicator
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.DASHBOARD_OUTLINED,
                        size=22,
                        badge=ft.Badge(small_size=8, bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.GREEN))
                    ),
                    selected_icon=ft.Icon(
                        ft.Icons.DASHBOARD,
                        color=ft.Colors.PRIMARY,
                        size=24,
                        badge=ft.Badge(small_size=10, bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.GREEN))
                    ),
                    label="Dashboard"
                ),
                # Clients with adaptive status badge
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.PEOPLE_OUTLINE,
                        size=22,
                        badge=ft.Badge(small_size=8, bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.BLUE))
                    ),
                    selected_icon=ft.Icon(
                        ft.Icons.PEOPLE,
                        color=ft.Colors.PRIMARY,
                        size=24,
                        badge=ft.Badge(small_size=10, bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.BLUE))
                    ),
                    label="Clients"
                ),
                # Files with modern folder indication
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.FOLDER_OUTLINED, size=22),
                    selected_icon=ft.Icon(
                        ft.Icons.FOLDER,
                        color=ft.Colors.PRIMARY,
                        size=24
                    ),
                    label="Files"
                ),
                # Database with enhanced storage visual
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.STORAGE_OUTLINED, size=22),
                    selected_icon=ft.Icon(
                        ft.Icons.STORAGE,
                        color=ft.Colors.PRIMARY,
                        size=24
                    ),
                    label="Database"
                ),
                # Analytics with modern graph styling
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.AUTO_GRAPH_OUTLINED, size=22),
                    selected_icon=ft.Icon(
                        ft.Icons.AUTO_GRAPH,
                        color=ft.Colors.PRIMARY,
                        size=24
                    ),
                    label="Analytics"
                ),
                # Logs with activity indicator
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.ARTICLE_OUTLINED,
                        size=22,
                        badge=ft.Badge(small_size=8, bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.ORANGE))
                    ),
                    selected_icon=ft.Icon(
                        ft.Icons.ARTICLE,
                        color=ft.Colors.PRIMARY,
                        size=24,
                        badge=ft.Badge(small_size=10, bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.ORANGE))
                    ),
                    label="Logs"
                ),
                # Settings with modern gear icon
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.SETTINGS_OUTLINED, size=22),
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
                    content=ft.FloatingActionButton(
                        icon=ft.Icons.MENU_ROUNDED if self.nav_rail_extended else ft.Icons.MENU_OPEN_ROUNDED,
                        mini=True,
                        tooltip="Toggle Navigation Menu",
                        on_click=self._toggle_navigation_rail,
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
            # Enhanced depth with optimized performance - reduced shadow for speed
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,  # Reduced blur for better performance
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(2, 0),  # Reduced offset for less rendering cost
            ),
            animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT),  # Much faster collapse animation
            border_radius=ft.BorderRadius(0, 12, 12, 0),  # Smaller radius for speed
        )

    def _toggle_navigation_rail(self, e=None):
        """Toggle navigation rail with modern UI feedback and optimized performance animations."""
        self.nav_rail_extended = not self.nav_rail_extended

        # Update the navigation rail extended state
        nav_rail_control = self.nav_rail.content
        nav_rail_control.extended = self.nav_rail_extended

        # Update the toggle button with modern floating action button styling
        toggle_btn = nav_rail_control.leading.content
        toggle_btn.icon = ft.Icons.MENU_ROUNDED if self.nav_rail_extended else ft.Icons.MENU_OPEN_ROUNDED

        # Add modern scale animation feedback for better UX
        toggle_btn.scale = 0.95
        toggle_btn.animate_scale = ft.Animation(80, ft.AnimationCurve.EASE_OUT)

        # Modern rotation animation with cubic curves
        toggle_btn.rotate = ft.Rotate(0.25 if self.nav_rail_extended else 0)
        toggle_btn.animate_rotation = ft.Animation(140, ft.AnimationCurve.EASE_OUT_CUBIC)

        # Optimized animation for the navigation rail with modern curves
        self.nav_rail.animate = ft.Animation(160, ft.AnimationCurve.EASE_OUT_CUBIC)
        self.nav_rail.update()

        # Show modern SnackBar feedback for better UX
        nav_snack = ft.SnackBar(
            content=ft.Row([
                ft.Icon(
                    ft.Icons.MENU_OPEN if self.nav_rail_extended else ft.Icons.MENU,
                    size=16,
                    color=ft.Colors.ON_INVERSE_SURFACE
                ),
                ft.Text(
                    f"Navigation {'expanded' if self.nav_rail_extended else 'collapsed'}",
                    color=ft.Colors.ON_INVERSE_SURFACE,
                    size=14
                ),
            ], spacing=8),
            bgcolor=ft.Colors.INVERSE_SURFACE,
            duration=1500,
            behavior=ft.SnackBarBehavior.FLOATING,
            margin=ft.Margin(20, 0, 20, 20),
            shape=ft.RoundedRectangleBorder(radius=12),
            elevation=3,
        )
        self.page.overlay.append(nav_snack)
        nav_snack.open = True
        self.page.update()

        # Reset scale after animation for smooth feel
        import time
        import threading

        def reset_scale():
            try:
                toggle_btn.scale = 1.0
                toggle_btn.animate_scale = ft.Animation(80, ft.AnimationCurve.EASE_OUT)
                toggle_btn.update()
            except Exception as e:
                logger.debug(f"Scale reset completed: {e}")

        # Use threading timer for proper async timing (more reliable than page timer)
        threading.Timer(0.08, reset_scale).start()

        logger.info(f"Navigation rail {'extended' if self.nav_rail_extended else 'collapsed'} with modern UI feedback")

    def _on_navigation_change(self, e):
        """Optimized navigation callback with lazy loading."""
        # Map index to view names
        view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]
        selected_view = view_names[e.control.selected_index] if e.control.selected_index < len(view_names) else "dashboard"

        logger.info(f"Navigation switching to: {selected_view} (optimized)")

        # Performance: Skip loading indicator for faster transitions
        # Load view with lazy loading optimization
        self._load_view(selected_view)

    async def _on_theme_toggle(self, e):
        """Handle theme toggle button click with modern UI animations and feedback."""
        try:
            from theme import toggle_theme_mode
            toggle_theme_mode(self.page)

            # Add modern animation feedback to the toggle button
            toggle_btn = e.control
            original_icon = toggle_btn.icon

            # Modern bounce-scale animation for visual feedback
            toggle_btn.scale = 0.85
            toggle_btn.animate_scale = ft.Animation(100, ft.AnimationCurve.EASE_OUT_BACK)
            toggle_btn.update()

            # Modern theme feedback with enhanced SnackBar
            current_theme = "Dark" if self.page.theme_mode == ft.ThemeMode.DARK else "Light"
            snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(
                        ft.Icons.DARK_MODE if current_theme == "Dark" else ft.Icons.LIGHT_MODE,
                        size=16,
                        color=ft.Colors.ON_INVERSE_SURFACE
                    ),
                    ft.Text(
                        f"Switched to {current_theme} theme",
                        color=ft.Colors.ON_INVERSE_SURFACE,
                        size=14,
                        weight=ft.FontWeight.W_500
                    ),
                ], spacing=8),
                bgcolor=ft.Colors.INVERSE_SURFACE,
                duration=2000,
                behavior=ft.SnackBarBehavior.FLOATING,
                margin=ft.Margin(20, 0, 20, 20),
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=4,
            )
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()

            # Reset scale after animation using asyncio.sleep for proper timing
            import asyncio
            await asyncio.sleep(0.1)  # 100ms delay

            def reset_scale():
                try:
                    toggle_btn.scale = 1.0
                    toggle_btn.animate_scale = ft.Animation(120, ft.AnimationCurve.EASE_OUT_BACK)
                    toggle_btn.update()
                except Exception as scale_error:
                    logger.debug(f"Theme toggle scale reset: {scale_error}")

            reset_scale()

            logger.info(f"Theme toggled to {current_theme} with modern UI feedback")

        except Exception as e:
            logger.error(f"Theme toggle failed: {e}")
            # Show error feedback with modern SnackBar
            error_snack = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(ft.Icons.ERROR_OUTLINE, size=16, color=ft.Colors.ON_ERROR),
                    ft.Text("Theme toggle failed", color=ft.Colors.ON_ERROR, size=14),
                ], spacing=8),
                bgcolor=ft.Colors.ERROR,
                duration=3000,
                behavior=ft.SnackBarBehavior.FLOATING,
            )
            self.page.overlay.append(error_snack)
            error_snack.open = True
            self.page.update()

    def _show_loading_indicator(self):
        """Show modern loading indicator with enhanced UI components during view transitions."""
        try:
            # Create a modern loading overlay with cards and visual enhancements
            loading_content = ft.Container(
                content=ft.Column([
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.ProgressRing(
                                        width=28,
                                        height=28,
                                        stroke_width=3,
                                        color=ft.Colors.PRIMARY,
                                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.PRIMARY)
                                    ),
                                    ft.Text(
                                        "Loading View...",
                                        size=15,
                                        weight=ft.FontWeight.W_500,
                                        color=ft.Colors.ON_SURFACE
                                    )
                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
                                ft.Row([
                                    ft.Chip(
                                        label=ft.Text("Optimized", size=11),
                                        leading=ft.Icon(ft.Icons.SPEED, size=14),
                                        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.GREEN),
                                        color=ft.Colors.GREEN,
                                        height=28,
                                    ),
                                    ft.Chip(
                                        label=ft.Text("Secure", size=11),
                                        leading=ft.Icon(ft.Icons.SECURITY, size=14),
                                        bgcolor=ft.Colors.with_opacity(0.12, ft.Colors.BLUE),
                                        color=ft.Colors.BLUE,
                                        height=28,
                                    ),
                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=16),
                            padding=24,
                            alignment=ft.alignment.center
                        ),
                        elevation=2,
                        shadow_color=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
                        surface_tint_color=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0
                ),
                padding=32,
                expand=True,
                alignment=ft.alignment.center
            )

            # Temporarily show loading indicator
            animated_switcher = self.content_area.content
            animated_switcher.content = loading_content

            # Defensive update for loading indicator with modern error handling
            try:
                if hasattr(self.page, 'controls') and self.page.controls:
                    animated_switcher.update()
                    logger.debug("Modern loading indicator updated via AnimatedSwitcher")
                else:
                    logger.debug("Page not ready for loading indicator update")
            except Exception as update_error:
                logger.debug(f"Loading indicator update failed, gracefully continuing: {update_error}")
                # Don't fail the entire operation for loading indicator

        except Exception as e:
            logger.debug(f"Could not show modern loading indicator: {e}")
            # Fallback to simple loading if modern version fails
            try:
                simple_loading = ft.Container(
                    content=ft.ProgressRing(width=24, height=24),
                    expand=True,
                    alignment=ft.alignment.center
                )
                self.content_area.content.content = simple_loading
                self.content_area.content.update()
            except:
                pass  # Continue without loading indicator if all attempts fail

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
    def on_window_event(e):
        """Handle window events to force sizing."""
        if e.data == "focus" or e.data == "ready":
            page.window_width = 1730
            page.window_height = 1425
            page.window_center = True
            page.update()
            logger.info(f"Window resized via event: {page.window_width}x{page.window_height}")

    try:
        # Set up window event handler
        page.on_window_event = on_window_event

        # Initial window configuration
        page.window_width = 1730
        page.window_height = 1425
        page.window_min_width = 1200
        page.window_min_height = 900
        page.window_resizable = True
        page.window_center = True
        page.title = "Backup Server Management"

        # Create and add the simple desktop app with mock mode banner
        app = FletV2App(page)

        # Add mock mode banner if in mock mode
        from utils.mock_mode_indicator import create_mock_mode_banner
        mock_banner = create_mock_mode_banner(app.server_bridge)

        # Create main layout with banner and app
        main_layout = ft.Column([
            mock_banner,
            ft.Container(content=app, expand=True)
        ], spacing=0, expand=True)

        page.add(main_layout)

        # Additional attempts to force window size
        await asyncio.sleep(0.2)
        page.window_width = 1730
        page.window_height = 1425
        page.update()

        logger.info(f"Window configured multiple attempts: {page.window_width}x{page.window_height}")

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