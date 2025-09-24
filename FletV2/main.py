#!/usr/bin/env python3
"""
FletV2 - Clean Desktop Application - Properly implemented Flet desktop application following best practices.

This demonstrates the clean architecture:
- Uses Flet built-ins exclusively (no framework fighting)
- Simple NavigationRail.on_change callback (no complex routing)
- Proper theme.py integration
- Server bridge with fallback
- UTF-8 support
- Resizable desktop app configuration
"""

# CRITICAL: Ensure FletV2 root is on sys.path BEFORE any other imports
import os
import sys

# Idempotent bootstrap: ensure both the FletV2 package root and the repository root
# are on sys.path so runtime imports like `utils.*` and `Shared.*` resolve whether
# the app is launched from the repo root, FletV2 folder, or elsewhere.
_here = os.path.abspath(__file__)
_base = os.path.dirname(_here)
# If this file is directly in FletV2/, _base will be the FletV2 folder
if os.path.basename(_base) == "FletV2":
    flet_v2_root = _base
else:
    # File may be in a subfolder of FletV2; the parent of the file's dir is FletV2
    flet_v2_root = os.path.dirname(_base)

# Repo root is the parent of the FletV2 root
repo_root = os.path.dirname(flet_v2_root)

# Insert flet_v2_root first so `import utils` resolves to FletV2/utils
if flet_v2_root not in sys.path:
    sys.path.insert(0, flet_v2_root)

# Ensure the repo root is available for sibling packages (Shared, python_server, api_server)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Best-effort: Also ensure the project root (one level up from this file) is present
project_root = os.path.dirname(_here)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Standard library imports
import asyncio
import contextlib
from typing import Any, Callable, Dict, Optional, Set, Tuple, cast

# Third-party imports
import flet as ft

# (Path setup handled above)

# Local imports - utilities first
try:
    from utils.debug_setup import setup_terminal_debugging  # noqa: E402
except ImportError:
    # Silent fallback for import issues - create minimal debug setup with matching signature
    import logging
    from typing import Optional

    def setup_terminal_debugging(log_level: int = logging.INFO, logger_name: Optional[str] = None) -> logging.Logger:
        logger = logging.getLogger(logger_name or __name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        logger.setLevel(log_level)
        return logger

# ALWAYS import this in any Python file that deals with subprocess or console I/O
# Import for side effects (UTF-8 configuration)
import Shared.utils.utf8_solution as _  # noqa: F401,E402

# Initialize logging and environment BEFORE any logger usage
logger = setup_terminal_debugging(logger_name="FletV2.main")
os.environ.setdefault("PYTHONUTF8", "1")

# Local imports - application modules
try:
    from theme import setup_modern_theme, toggle_theme_mode  # noqa: E402
except ImportError as e:
    print(f"Warning: Could not import theme module: {e}")
    # Create minimal fallbacks
    def setup_modern_theme(page): pass
    def toggle_theme_mode(page): pass

try:
    from utils.server_bridge import create_server_bridge  # noqa: E402
except ImportError as e:
    print(f"Error: Could not import server_bridge: {e}")
    # Mock data support has been removed - server bridge requires real server
    def create_server_bridge(real_server: Any | None = None) -> Any:  # type: ignore[override]
        if real_server is None:
            raise ValueError("ServerBridge requires a real server instance. Mock data support has been removed.")
        raise ImportError(f"ServerBridge module not available: {e}")

# Exported runtime flags for tests and integration checks
REAL_SERVER_AVAILABLE = False
BRIDGE_TYPE = "Placeholder Data Development Mode"

# Try to import and initialize the real BackupServer
real_server_instance = None
try:
    # Disable BackupServer's embedded GUI to prevent conflicts with FletV2 GUI
    os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'
    os.environ['CYBERBACKUP_DISABLE_GUI'] = '1'
    logger.info("Disabled BackupServer embedded GUI to prevent conflicts")

    # Use __file__ for reliable path resolution instead of os.getcwd()
    fletv2_root = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(fletv2_root)
    main_db_path = os.path.join(project_root, "defensive.db")

    # Set environment variable BEFORE importing BackupServer to ensure proper initialization
    os.environ['BACKUP_DATABASE_PATH'] = main_db_path
    logger.info(f"Set BACKUP_DATABASE_PATH environment variable to: {main_db_path}")

    # Import the BackupServer AFTER setting environment variables
    from python_server.server.server import BackupServer
    logger.info("BackupServer class imported successfully")

    # Check if the main database exists and has data
    if os.path.exists(main_db_path):
        import sqlite3
        conn = sqlite3.connect(main_db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM clients")
            client_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM files")
            file_count = cursor.fetchone()[0]
            logger.info(f"Main database contains {client_count} clients and {file_count} files")
        except Exception as db_error:
            logger.warning(f"Database query failed: {db_error}")
        finally:
            conn.close()
    else:
        logger.error(f"CRITICAL: Main database file not found: {main_db_path}")
        logger.error("Application will start in placeholder mode")
        raise FileNotFoundError(f"Database file not found: {main_db_path}")

    # Initialize the real server instance
    logger.info("Initializing BackupServer instance...")
    real_server_instance = BackupServer()

    # Validate that the server is using the correct database
    actual_db_path = getattr(real_server_instance.db_manager, 'db_name', 'Unknown')
    logger.info(f"BackupServer initialized with database: {actual_db_path}")

    # Comprehensive database connection test
    if hasattr(real_server_instance.db_manager, 'execute'):
        try:
            # Test client count
            clients_result = real_server_instance.db_manager.execute(
                "SELECT COUNT(*) FROM clients", fetchone=True
            )
            client_count = clients_result[0] if clients_result else 0

            # Test files count
            files_result = real_server_instance.db_manager.execute(
                "SELECT COUNT(*) FROM files", fetchone=True
            )
            file_count = files_result[0] if files_result else 0

            logger.info(f"Database connection test successful: {client_count} clients, {file_count} files")

            # Validate database integrity
            integrity_result = real_server_instance.db_manager.execute(
                "PRAGMA integrity_check", fetchone=True
            )
            if integrity_result and integrity_result[0] == 'ok':
                logger.info("Database integrity check passed")
            else:
                logger.warning(f"Database integrity check result: {integrity_result}")

        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise e

    # Test server methods compatibility
    try:
        if hasattr(real_server_instance, 'get_clients'):
            logger.info("Server has get_clients method - compatible with ServerBridge")
        else:
            logger.warning("Server missing get_clients method - may have compatibility issues")
    except Exception as e:
        logger.warning(f"Server method test failed: {e}")

    REAL_SERVER_AVAILABLE = True
    BRIDGE_TYPE = "Real Server Production Mode"
    logger.info("✅ Real BackupServer initialized successfully and verified")

except ImportError as e:
    logger.error(f"Could not import BackupServer - check if python_server is available: {e}")
    logger.info("Starting in placeholder mode - all GUI features will work with mock data")
    real_server_instance = None
except FileNotFoundError as e:
    logger.error(f"Database file not found: {e}")
    logger.info("Starting in placeholder mode - create a database file to enable real server mode")
    real_server_instance = None
except Exception as e:
    logger.error(f"Failed to initialize BackupServer: {e}")
    logger.info("Starting in placeholder mode due to server initialization failure")
    real_server_instance = None

# Direct server integration support (no adapter layer needed)
# The BackupServer has built-in ServerBridge compatibility
real_server_available = REAL_SERVER_AVAILABLE  # Will be set to True when server is injected
create_fletv2_server = None  # Legacy - not needed for direct integration

# Ensure project root is in path for direct execution
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Application bridge type - will be updated when real server is injected
bridge_type = "Placeholder Data Development Mode"
logger.info("🧪 Using placeholder data for development (real server can be injected)")


class FletV2App(ft.Row):
    """
    Clean FletV2 desktop app using pure Flet patterns.

    This demonstrates maximum framework harmony:
    - NavigationRail.on_change for navigation (no custom managers)
    - Container(expand=True) for responsive layout
    - Simple view switching with direct function calls
    - Uses theme.py for styling
    """

    def __init__(self, page: ft.Page, real_server: Optional[Any] = None) -> None:
        super().__init__()
        self.page: ft.Page = page  # Ensure page is never None
        self.expand = True

        # Type annotations for key attributes
        self.server_bridge: Any = None
        self.state_manager: Optional[Any] = None
        self.content_area: ft.Container = ft.Container()
        self.nav_rail: ft.Container = ft.Container()
        self.nav_rail_extended: bool = True
        self._loaded_views: Dict[str, ft.Control] = {}
        self._background_tasks: Set[Any] = set()

        # Initialize server bridge - prefer real server instance
        global bridge_type, real_server_available, real_server_instance
        try:
            if real_server is not None:
                # Direct server injection (from integrated startup script)
                logger.info("🎯 Using directly provided real server (direct injection)")
                self.server_bridge = create_server_bridge(real_server=real_server)
                bridge_type = "Direct BackupServer Integration"
                real_server_available = True
                logger.info("✅ Direct BackupServer integration activated!")
            elif real_server_instance is not None:
                # Use the real server instance we created at startup
                logger.info("🎯 Using global real server instance")
                self.server_bridge = create_server_bridge(real_server=real_server_instance)
                bridge_type = "Real BackupServer Integration"
                real_server_available = True
                logger.info("✅ Real BackupServer integration activated!")

                # Test server bridge functionality immediately
                try:
                    test_result = self.server_bridge.get_clients()
                    if isinstance(test_result, list):
                        logger.info(f"Server bridge test successful: {len(test_result)} clients accessible")
                    elif isinstance(test_result, dict) and test_result.get('success'):
                        client_count = len(test_result.get('data', []))
                        logger.info(f"Server bridge test successful: {client_count} clients accessible")
                    else:
                        logger.warning(f"Server bridge test returned unexpected format: {type(test_result)}")
                except Exception as test_error:
                    logger.error(f"Server bridge test failed: {test_error}")
                    logger.error("CRITICAL: Real server integration failed - this may indicate compatibility issues")
                    # Don't fall back to placeholder since ServerBridge now requires real server
                    raise test_error
            else:
                # No real server available - ServerBridge now requires real server instance
                logger.error("❌ No real server available - ServerBridge requires real server instance")
                logger.error("Application cannot start without a real server instance")
                raise RuntimeError("ServerBridge requires real server instance. Mock data support has been removed.")
        except Exception as bridge_ex:
            logger.error(f"❌ Server bridge initialization failed: {bridge_ex}")
            logger.error("Application cannot continue without properly configured server bridge")
            raise bridge_ex

        logger.info(f"Final server bridge configuration: {bridge_type}")
        logger.info(f"Real server available: {real_server_available}")

        # Initialize state manager for reactive UI updates - after server bridge is ready
        self._initialize_state_manager()

        # Comment 12: Track current view dispose function for proper StateManager cleanup
        self._current_view_dispose: Optional[Callable[[], None]] = None
        self._current_view_name: Optional[str] = None

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
                                    color=ft.Colors.ON_SURFACE
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

    def _initialize_state_manager(self) -> None:
        """Initialize state manager with server bridge integration for reactive UI updates"""
        try:
            from utils.state_manager import create_state_manager
            # Pass server_bridge for enhanced server-mediated operations
            self.state_manager = create_state_manager(self.page, self.server_bridge)

            # Set up cross-view reactive updates
            self._setup_cross_view_reactivity()

            logger.info("State manager initialized with server bridge integration and cross-view reactivity")
        except ImportError:
            logger.warning("State manager not available, UI updates will be manual")
            self.state_manager = None
        except Exception as e:
            logger.error(f"Failed to initialize state manager: {e}")
            self.state_manager = None

    def _setup_cross_view_reactivity(self) -> None:
        """Set up global state listeners for cross-view reactive updates"""
        if not self.state_manager:
            return

        # Global listener for all state changes
        def global_state_change_handler(key: str, new_value: Any, old_value: Any) -> None:
            """Handle state changes that affect multiple views"""
            try:
                # Update navigation indicators based on state
                if key in {"connection_status"}:
                    self._update_connection_indicator(new_value)
                elif key == "server_status":
                    self._update_server_status_indicator(new_value)
                elif key == "notifications":
                    self._handle_notifications_update(new_value)
                elif key in {"clients", "files", "database_info"}:
                    # Data changes that might affect multiple views
                    self._handle_data_update(key, new_value)

                logger.debug(f"Cross-view reactive update: {key}")

            except Exception as e:
                logger.error(f"Global state change handler failed: {e}")

        # Subscribe to global state changes
        self.state_manager.subscribe_global(global_state_change_handler)

        # Set up specific cross-view subscriptions
        self._setup_view_specific_subscriptions()

    def _setup_view_specific_subscriptions(self) -> None:
        """Set up view-specific cross-view subscriptions"""
        if not self.state_manager:
            return

        # Example: When clients change, update any client-related displays
        self.state_manager.subscribe("clients", self._on_clients_changed)

        # When server status changes, update relevant views
        self.state_manager.subscribe("server_status", self._on_server_status_changed)

        # When files change, update file-related displays
        self.state_manager.subscribe("files", self._on_files_changed)

    def _create_status_chip(self, label: str, icon_name: str, color_name: str) -> ft.Chip:
        """Create a status chip with safe icon and color resolution."""
        try:
            # Safe icon resolution with proper fallback
            icon = (getattr(ft.Icons, icon_name, None) or
                   getattr(ft.Icons, f"{icon_name}_ROUNDED", None) or
                   ft.Icons.INFO)

            # Safe color resolution
            color = getattr(ft.Colors, color_name, ft.Colors.PRIMARY)

            return ft.Chip(
                label=ft.Text(label, size=11),
                leading=ft.Icon(icon, size=14),
                bgcolor=ft.Colors.with_opacity(0.12, color),
                color=color,
                height=28,
            )
        except Exception:
            # Fallback chip
            return ft.Chip(label=ft.Text(label, size=11), height=28)

    def _update_connection_indicator(self, status: str) -> None:
        """Update connection status indicator in navigation"""
        # This could update a visual indicator in the navigation rail
        logger.debug(f"Connection status: {status}")

    def _update_server_status_indicator(self, status: dict[str, Any]) -> None:
        """Update server status indicator"""
        # This could update server status displays across views
        logger.debug(f"Server status: {status}")

    def _handle_notifications_update(self, notifications: list[Any]) -> None:
        """Handle notifications display updates"""
        # This could show/hide notification indicators
        logger.debug(f"Notifications: {len(notifications)} items")

    def _handle_data_update(self, data_type: str, new_data: Any) -> None:
        """Handle data updates that affect multiple views"""
        # This could trigger view refreshes or update counters
        data_count = len(new_data) if isinstance(new_data, list) else 'N/A'
        logger.debug(f"Data update received: {data_type} with {data_count} items")

    def _on_clients_changed(self, new_clients: Any, old_clients: Any) -> None:
        """Handle clients data changes"""
        # Could update client count displays, refresh client-dependent views
        is_both_lists = isinstance(new_clients, list) and isinstance(old_clients, list)
        if is_both_lists and len(new_clients) != len(old_clients):
                logger.info(f"Client count changed: {len(old_clients)} -> {len(new_clients)}")

    def _on_server_status_changed(self, new_status: Any, old_status: Any) -> None:
        """Handle server status changes"""
        # Could update server indicators, enable/disable buttons
        if isinstance(new_status, dict):
            old_running = (old_status or {}).get('server_running')
            new_running = new_status.get('server_running')
            if new_running != old_running:
                logger.info(f"Server running state changed: {new_running}")

    def _on_files_changed(self, new_files: Any, old_files: Any) -> None:
        """Handle files data changes"""
        # Could update file count displays, refresh file-dependent views
        if isinstance(new_files, list) and isinstance(old_files, list) and len(new_files) != len(old_files):
            logger.info(f"Files count changed: {len(old_files)} -> {len(new_files)}")

    def _on_page_connect(self, e: ft.ControlEvent) -> None:
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
        except Exception as fallback_error:
            logger.error(f"Error view display failed: {fallback_error}")
            # Last resort
            with contextlib.suppress(Exception):
                self.page.update()
        # Window settings - Updated to requested size 1730x1425
        if hasattr(self.page, 'window_min_width'):
            self.page.window_min_width = 1200  # Slightly larger minimum for better UX
        if hasattr(self.page, 'window_min_height'):
            self.page.window_min_height = 900
        if hasattr(self.page, 'window_width'):
            self.page.window_width = 1730  # User requested size
        if hasattr(self.page, 'window_height'):
            self.page.window_height = 1425  # User requested size
        if hasattr(self.page, 'window_resizable'):
            self.page.window_resizable = True
        self.page.title = "Backup Server Management"

        # Apply 2025 modern theme with vibrant colors and enhanced effects
        setup_modern_theme(self.page)

        # Add performance optimizations - Visual Density for reduced spacing
        if getattr(self.page, "theme", None):
            # Guard against None to satisfy type checker
            self.page.theme.visual_density = ft.VisualDensity.COMPACT

        # Set desktop-appropriate padding (reduced for more content space)
        self.page.padding = ft.Padding(0, 0, 0, 0)

        # Set up keyboard shortcuts
        if hasattr(self.page, 'on_keyboard_event'):
            self.page.on_keyboard_event = self._on_keyboard_event

    def _on_keyboard_event(self, e: ft.KeyboardEvent) -> None:
        """Handle keyboard shortcuts for navigation and actions."""
        # Only handle key down events
        if e.key not in ["R", "D", "C", "F", "B", "A", "L", "S"]:
            return

        # Check for Ctrl modifier
        if not (hasattr(e, 'ctrl') and e.ctrl):
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

    def _refresh_current_view(self) -> None:
        """Refresh the currently active view."""
        # Access NavigationRail through container content
        nav_rail_control = self.nav_rail.content
        if hasattr(nav_rail_control, 'selected_index'):
            current_index = nav_rail_control.selected_index
            view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]
            if current_index is not None and current_index < len(view_names):
                current_view = view_names[current_index]
                logger.info(f"Refreshing view: {current_view}")
                self._load_view(current_view)

    def _switch_to_view(self, index: int) -> None:
        """Switch to a specific view by index."""
        # Access NavigationRail through container content
        nav_rail_control = self.nav_rail.content
        # Bound index to available destinations
        with contextlib.suppress(Exception):
            if hasattr(nav_rail_control, 'destinations'):
                total = len(nav_rail_control.destinations or [])
                if total and (index < 0 or index >= total):
                    index = 0

        if hasattr(nav_rail_control, 'selected_index'):
            nav_rail_control.selected_index = index
        # Ensure the visual selection indicator updates immediately (control + container)
        with contextlib.suppress(Exception):
            if hasattr(nav_rail_control, 'update'):
                nav_rail_control.update()
        with contextlib.suppress(Exception):
            self.nav_rail.update()
        # Trigger the standard change handler to load the view
        placeholder_event = type('Event', (), {'control': nav_rail_control})()
        self._on_navigation_change(placeholder_event)

    def _create_navigation_rail(self) -> ft.Container:
        """Create enhanced collapsible navigation rail with modern 2025 UI styling."""
        return ft.Container(
            content=ft.NavigationRail(
                selected_index=0,
                label_type=ft.NavigationRailLabelType.ALL,
                group_alignment=-0.8,
                min_width=68,  # Collapsed width (icons only)
                min_extended_width=240,  # Extended width (2025 standard)
                extended=self.nav_rail_extended,  # Collapsible functionality
                bgcolor=ft.Colors.with_opacity(0.98, ft.Colors.SURFACE),
                indicator_color=ft.Colors.with_opacity(0.2, ft.Colors.PRIMARY),
                indicator_shape=ft.RoundedRectangleBorder(radius=24),
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
                            color=ft.Colors.ON_SURFACE,
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

    def _toggle_navigation_rail(self, e: Optional[ft.ControlEvent] = None) -> None:
        """Toggle navigation rail with modern UI feedback and optimized performance animations."""
        self.nav_rail_extended = not self.nav_rail_extended

        # Update the navigation rail extended state
        nav_rail_control = self.nav_rail.content
        if hasattr(nav_rail_control, 'extended'):
            nav_rail_control.extended = self.nav_rail_extended

        # Update the toggle button with modern floating action button styling
        toggle_btn: Any = None
        if hasattr(nav_rail_control, 'leading') and hasattr(nav_rail_control.leading, 'content'):
            toggle_btn = cast(Any, nav_rail_control.leading.content)
            with contextlib.suppress(Exception):
                toggle_btn.icon = (
                    ft.Icons.MENU_ROUNDED if self.nav_rail_extended else ft.Icons.MENU_OPEN_ROUNDED
                )

        # Add modern scale/rotation animation feedback for better UX (only if button resolved)
        if toggle_btn:
            with contextlib.suppress(Exception):
                toggle_btn.scale = 0.95
                toggle_btn.animate_scale = ft.Animation(80, ft.AnimationCurve.EASE_OUT)
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
        if hasattr(self.page, 'overlay'):
            self.page.overlay.append(nav_snack)
            nav_snack.open = True
            self.page.update()

        # Reset scale after animation for smooth feel
        async def reset_scale_async() -> None:
            try:
                await asyncio.sleep(0.08)
                if toggle_btn:
                    toggle_btn.scale = 1.0
                    toggle_btn.animate_scale = ft.Animation(80, ft.AnimationCurve.EASE_OUT)
                    with contextlib.suppress(Exception):
                        toggle_btn.update()
            except Exception as e:
                logger.debug(f"Scale reset completed: {e}")

        # Use asyncio for proper async timing (replaces threading.Timer)
        if hasattr(self.page, 'run_task'):
            self.page.run_task(reset_scale_async)

        state_text = 'extended' if self.nav_rail_extended else 'collapsed'
        logger.info(f"Navigation rail {state_text} with modern UI feedback")

    def _on_navigation_change(self, e: ft.ControlEvent) -> None:
        """Optimized navigation callback with lazy loading."""
        # Map index to view names
        view_names = ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]

        # Safe access to selected_index
        selected_index = 0  # Default to dashboard
        has_control = hasattr(e, 'control') and hasattr(e.control, 'selected_index')
        if has_control and e.control.selected_index is not None:
            selected_index = e.control.selected_index

        selected_view = view_names[selected_index] if selected_index < len(view_names) else "dashboard"

        logger.info(f"Navigation switching to: {selected_view} (optimized)")

        # Performance: Skip loading indicator for faster transitions
        # Load view with lazy loading optimization
        self._load_view(selected_view)

    async def _on_theme_toggle(self, e: ft.ControlEvent) -> None:
        """Handle theme toggle button click with modern UI animations and feedback."""
        try:
            toggle_theme_mode(self.page)

            # Add modern animation feedback to the toggle button
            toggle_btn = e.control
            if hasattr(toggle_btn, 'icon'):
                _ = toggle_btn.icon  # Track for visual feedback

            if hasattr(toggle_btn, 'scale'):
                toggle_btn.scale = 0.85
            if hasattr(toggle_btn, 'animate_scale'):
                toggle_btn.animate_scale = ft.Animation(100, ft.AnimationCurve.EASE_OUT_BACK)
            if hasattr(toggle_btn, 'update'):
                toggle_btn.update()

            # Modern theme feedback with enhanced SnackBar
            is_dark = (hasattr(self.page, 'theme_mode')
                      and self.page.theme_mode == ft.ThemeMode.DARK)
            current_theme = "Dark" if is_dark else "Light"
            snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(
                        ft.Icons.BRIGHTNESS_6_ROUNDED if current_theme == "Dark" else ft.Icons.BRIGHTNESS_6,
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
            if hasattr(self.page, 'overlay'):
                self.page.overlay.append(snack_bar)
                snack_bar.open = True
                self.page.update()

            # Reset scale after animation using asyncio.sleep for proper timing
            await asyncio.sleep(0.1)  # 100ms delay

            def reset_scale() -> None:
                try:
                    if hasattr(toggle_btn, 'scale'):
                        toggle_btn.scale = 1.0
                    if hasattr(toggle_btn, 'animate_scale'):
                        toggle_btn.animate_scale = ft.Animation(120, ft.AnimationCurve.EASE_OUT_BACK)
                    if hasattr(toggle_btn, 'update'):
                        toggle_btn.update()
                except Exception as scale_error:
                    logger.debug(f"Theme toggle scale reset: {scale_error}")

            reset_scale()

            logger.info(f"Theme toggled to {current_theme} with modern UI feedback")

        except Exception as ex:  # use different name to avoid shadowing parameter type
            logger.error(f"Theme toggle failed: {ex}")
            # Use dynamic attribute lookup for Icons and Colors to avoid static analyzer errors
            _Icons = getattr(ft, "Icons", None)
            _Colors = getattr(ft, "Colors", None)
            icon_data = None
            icon_color = None
            if _Icons:
                icon_data = (getattr(_Icons, "ERROR_OUTLINED", None) or
                           getattr(_Icons, "ERROR", None) or
                           getattr(_Icons, "WARNING", None))
            if _Colors:
                icon_color = getattr(_Colors, "ON_ERROR", None) or getattr(_Colors, "ERROR", None)

            error_snack = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(icon_data, size=16, color=icon_color),
                    ft.Text("Theme toggle failed", color=icon_color, size=14),
                ], spacing=8),
                bgcolor=(getattr(_Colors, "ERROR", None) if _Colors is not None else None),
                duration=3000,
                behavior=ft.SnackBarBehavior.FLOATING,
            )
            if hasattr(self.page, 'overlay'):
                self.page.overlay.append(error_snack)
                error_snack.open = True
                self.page.update()

    def _show_loading_indicator(self) -> None:
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
                                # Create status chips with clean helper method
                                ft.Row([
                                    self._create_status_chip("Optimized", "SPEED", "GREEN"),
                                    self._create_status_chip("Secure", "SECURITY", "BLUE"),
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
            if hasattr(animated_switcher, 'content'):
                animated_switcher.content = loading_content

            # Defensive update for loading indicator with modern error handling
            try:
                # Use getattr to safely access controls (Page may not expose controls in some runtimes)
                if getattr(self.page, 'controls', None):
                    if hasattr(animated_switcher, 'update'):
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
            with contextlib.suppress(Exception):
                simple_loading = ft.Container(
                    content=ft.ProgressRing(width=24, height=24),
                    expand=True,
                    alignment=ft.alignment.center
                )
                if hasattr(self.content_area.content, 'content'):
                    self.content_area.content.content = simple_loading
                if hasattr(self.content_area.content, 'update'):
                    self.content_area.content.update()

    def _set_animation_for_view(self, view_name: str) -> None:
        """Dynamically set animation type and parameters based on view for enhanced UX."""
        animated_switcher = self.content_area.content
        if animated_switcher is None:
            return

        # Different animation styles for different views
        if view_name == "dashboard":
            # Dashboard: Scale with bounce for welcoming feel
            if hasattr(animated_switcher, 'transition'):
                animated_switcher.transition = ft.AnimatedSwitcherTransition.SCALE
            if hasattr(animated_switcher, 'duration'):
                animated_switcher.duration = 450
            if hasattr(animated_switcher, 'reverse_duration'):
                animated_switcher.reverse_duration = 350
            if hasattr(animated_switcher, 'switch_in_curve'):
                animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT_BACK
            if hasattr(animated_switcher, 'switch_out_curve'):
                animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN_OUT

        elif view_name == "clients":
            # Clients: Slide from right for data flow feel
            if hasattr(animated_switcher, 'transition'):
                animated_switcher.transition = ft.AnimatedSwitcherTransition.SCALE
            if hasattr(animated_switcher, 'duration'):
                animated_switcher.duration = 400
            if hasattr(animated_switcher, 'reverse_duration'):
                animated_switcher.reverse_duration = 300
            if hasattr(animated_switcher, 'switch_in_curve'):
                animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT_CUBIC
            if hasattr(animated_switcher, 'switch_out_curve'):
                animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN_CUBIC

        elif view_name == "files":
            # Files: Fade with elastic for file browsing feel
            if hasattr(animated_switcher, 'transition'):
                animated_switcher.transition = ft.AnimatedSwitcherTransition.FADE
            if hasattr(animated_switcher, 'duration'):
                animated_switcher.duration = 350
            if hasattr(animated_switcher, 'reverse_duration'):
                animated_switcher.reverse_duration = 250
            if hasattr(animated_switcher, 'switch_in_curve'):
                animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT
            if hasattr(animated_switcher, 'switch_out_curve'):
                animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN

        elif view_name == "database":
            # Database: Scale with smooth curves for data stability
            if hasattr(animated_switcher, 'transition'):
                animated_switcher.transition = ft.AnimatedSwitcherTransition.SCALE
            if hasattr(animated_switcher, 'duration'):
                animated_switcher.duration = 500
            if hasattr(animated_switcher, 'reverse_duration'):
                animated_switcher.reverse_duration = 400
            if hasattr(animated_switcher, 'switch_in_curve'):
                animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT_QUART
            if hasattr(animated_switcher, 'switch_out_curve'):
                animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN_QUART

        elif view_name == "analytics":
            # Analytics: Scale with bounce for dynamic data visualization
            if hasattr(animated_switcher, 'transition'):
                animated_switcher.transition = ft.AnimatedSwitcherTransition.SCALE
            if hasattr(animated_switcher, 'duration'):
                animated_switcher.duration = 420
            if hasattr(animated_switcher, 'reverse_duration'):
                animated_switcher.reverse_duration = 320
            if hasattr(animated_switcher, 'switch_in_curve'):
                animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT_BACK
            if hasattr(animated_switcher, 'switch_out_curve'):
                animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN_BACK

        elif view_name == "logs":
            # Logs: Fade for quick transitions in log viewing
            if hasattr(animated_switcher, 'transition'):
                animated_switcher.transition = ft.AnimatedSwitcherTransition.FADE
            if hasattr(animated_switcher, 'duration'):
                animated_switcher.duration = 300
            if hasattr(animated_switcher, 'reverse_duration'):
                animated_switcher.reverse_duration = 200
            if hasattr(animated_switcher, 'switch_in_curve'):
                animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT
            if hasattr(animated_switcher, 'switch_out_curve'):
                animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN

        elif view_name == "settings":
            # Settings: Scale with smooth transition for configuration feel
            if hasattr(animated_switcher, 'transition'):
                animated_switcher.transition = ft.AnimatedSwitcherTransition.SCALE
            if hasattr(animated_switcher, 'duration'):
                animated_switcher.duration = 380
            if hasattr(animated_switcher, 'reverse_duration'):
                animated_switcher.reverse_duration = 280
            if hasattr(animated_switcher, 'switch_in_curve'):
                animated_switcher.switch_in_curve = ft.AnimationCurve.EASE_OUT_CUBIC
            if hasattr(animated_switcher, 'switch_out_curve'):
                animated_switcher.switch_out_curve = ft.AnimationCurve.EASE_IN_CUBIC

        # Safe logging of animation settings
        transition = getattr(animated_switcher, 'transition', 'unknown')
        duration = getattr(animated_switcher, 'duration', 'unknown')
        logger.debug(f"Set animation for {view_name}: {transition}, duration={duration}ms")

    def _get_view_config(self, view_name: str) -> Tuple[str, str, str]:
        """Get view configuration for the specified view name."""
        view_configs = {
            "dashboard": ("views.dashboard", "create_dashboard_view"),
            "clients": ("views.clients", "create_clients_view"),
            "files": ("views.files", "create_files_view"),
            "database": ("views.database", "create_database_view"),
            "analytics": ("views.analytics", "create_analytics_view"),
            "logs": ("views.logs", "create_logs_view"),
            "settings": ("views.settings", "create_settings_view"),
        }

        # Get view configuration or use dashboard as fallback
        module_name, function_name = view_configs.get(view_name, view_configs["dashboard"])
        actual_view_name = view_name if view_name in view_configs else "dashboard"
        return module_name, function_name, actual_view_name

    def _update_content_area(self, animated_switcher: Any, content: Any, view_name: str) -> bool:
        """Update content area with error handling and fallback strategies."""
        if hasattr(animated_switcher, 'content'):
            animated_switcher.content = content
        update_success = False

        # Smart update - check if control is attached to page before updating
        try:
            # Verify AnimatedSwitcher is properly attached to page
            if hasattr(animated_switcher, 'page') and animated_switcher.page:
                if hasattr(animated_switcher, 'update'):
                    animated_switcher.update()
                update_success = True
                logger.info(f"Successfully loaded {view_name} view")
            else:
                # Control not yet attached, use page update as fallback
                logger.debug("AnimatedSwitcher not yet attached to page, using page update")
                self.page.update()  # type: ignore[call-arg]
                update_success = True
                logger.info(f"Successfully loaded {view_name} view (page update fallback)")
        except Exception as update_error:
            logger.warning(f"AnimatedSwitcher update failed for {view_name}: {update_error}")
            try:
                self.page.update()  # type: ignore[call-arg]
                update_success = True
                logger.info(f"Successfully loaded {view_name} view (page update fallback)")
            except Exception as fallback_error:
                logger.error(f"Page update also failed for {view_name}: {fallback_error}")
                update_success = False

        if not update_success:
            logger.error(f"Failed to load {view_name} view - UI update failed")
            return False

        # Set up subscriptions after view is added to page and updated
        # (prevents "Control must be added to page first" error)
        if hasattr(content, '_setup_subscriptions'):
            setup_cb = getattr(content, '_setup_subscriptions', None)
            # Only proceed if the attribute is callable; skip falsy/non-callable values (e.g., 0)
            if callable(setup_cb):
                try:
                    # Use page.run_task to defer subscription setup to next event loop iteration
                    # This ensures all controls are properly attached to the page hierarchy
                    async def setup_subs() -> None:
                        try:
                            # If the setup callback is defined as a coroutine function, await it directly
                            if asyncio.iscoroutinefunction(setup_cb):
                                await setup_cb()
                            else:
                                # Call the setup function; if it returns a coroutine, await that
                                result = setup_cb()
                                if asyncio.iscoroutine(result):
                                    await result
                            logger.debug(f"Set up subscriptions for {view_name} view")
                        except Exception as sub_error:
                            logger.warning(f"Failed to set up subscriptions for {view_name}: {sub_error}")

                    if hasattr(self.page, 'run_task'):
                        self.page.run_task(setup_subs)
                except Exception as sub_error:
                    logger.warning(f"Failed to schedule subscription setup for {view_name}: {sub_error}")
            else:
                logger.debug(
                    f"Skipping subscription setup for {view_name}: _setup_subscriptions is not callable "
                    f"(type={type(setup_cb).__name__})"
                )

        return True

    def _dispose_current_view(self, new_view_name: str) -> None:
        """Dispose of the current view before loading a new one."""
        if self._current_view_dispose and new_view_name != self._current_view_name:
            try:
                self._current_view_dispose()
                logger.debug(f"Disposed of previous view: {self._current_view_name}")
            except Exception as e:
                logger.warning(f"Failed to dispose previous view {self._current_view_name}: {e}")
            self._current_view_dispose = None
            self._current_view_name = None

    def _perform_view_loading(self, view_name: str) -> bool:
        """Perform the core view loading logic."""
        # Comment 12: Dispose of current view before loading new one
        self._dispose_current_view(view_name)

        # Get view configuration
        module_name, function_name, actual_view_name = self._get_view_config(view_name)

        # Dynamic import and view creation
        module = __import__(module_name, fromlist=[function_name])
        view_function = getattr(module, function_name)
        content, dispose_func = self._create_enhanced_view(view_function, actual_view_name)

        # Store dispose function for cleanup (Comment 12)
        self._current_view_dispose = dispose_func
        self._current_view_name = view_name

        self._set_animation_for_view(actual_view_name)

        # Update content area using AnimatedSwitcher for smooth transitions
        animated_switcher = self.content_area.content
        return self._update_content_area(animated_switcher, content, view_name)

    def _load_view(self, view_name: str) -> bool:
        """Load view with enhanced infrastructure support and dynamic animated transitions."""
        try:
            update_success = self._perform_view_loading(view_name)

            if not update_success:
                logger.error(f"View loading failed for {view_name} - falling back to error view")
                # Clean up if update failed
                if self._current_view_dispose:
                    try:
                        self._current_view_dispose()
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to cleanup after failed view load: {cleanup_error}")
                self._current_view_dispose = None
                self._current_view_name = None
                return False

            return True

        except Exception as e:
            logger.error(f"Failed to load view {view_name}: {e}")
            # Simple error fallback
            try:
                animated_switcher = self.content_area.content
                error_view = self._create_error_view(str(e))
                if hasattr(animated_switcher, 'content'):
                    animated_switcher.content = error_view  # type: ignore[attr-defined]
                    with contextlib.suppress(Exception):
                        animated_switcher.update()  # type: ignore[call-arg]
                    logger.warning(f"Showing error view for {view_name}")
                else:
                    # Fallback: replace entire content area content
                    self.content_area.content = error_view
                    self.content_area.update()
            except Exception as fallback_error:
                logger.error(f"Error view display failed: {fallback_error}")
                # Last resort
                with contextlib.suppress(Exception):
                    self.page.update()  # type: ignore[call-arg]
            return False

    def _extract_content_and_dispose(self, result_t: Tuple[Any, ...]) -> Tuple[Any, Optional[Callable[[], None]]]:
        """Extract content and dispose function from result tuple."""
        content = result_t[0]
        dispose_func = cast(Optional[Callable[[], None]], result_t[1])
        return content, dispose_func

    def _process_view_result_tuple(self, result_t: Tuple[Any, ...], view_name: str) -> Tuple[Any, Optional[Callable[[], None]]]:
        """Process view result tuple and extract content and dispose function."""
        if len(result_t) == 3:
            content, dispose_func = self._extract_content_and_dispose(result_t)
            setup_subscriptions_func = cast(Callable[..., Any], result_t[2])
            # Store setup function for later execution
            content._setup_subscriptions = setup_subscriptions_func
            logger.debug(f"Successfully processed 3-tuple for {view_name}")
            return content, dispose_func
        elif len(result_t) == 2:
            content, dispose_func = self._extract_content_and_dispose(result_t)
            logger.debug(f"Successfully processed 2-tuple for {view_name}")
            return content, dispose_func
        else:
            logger.error(f"Unexpected tuple length {len(result_t)} for {view_name}")
            return self._create_error_view(f"Invalid tuple length for {view_name}"), lambda: None

    def _create_enhanced_view(
        self, view_function: Callable[..., Any], view_name: str
    ) -> Tuple[Any, Optional[Callable[[], None]]]:
        """Create view with state manager integration - now required for all views."""
        try:
            # All views now require state_manager as per Phase 2 refactor
            result = view_function(self.server_bridge, self.page, self.state_manager)
            logger.debug(f"View function returned: {type(result)} for {view_name}")

            # Comment 12: Check if view returned dispose function and subscription setup (new pattern)
            if isinstance(result, tuple):
                result_t = cast(Tuple[Any, ...], result)
                logger.debug(f"Tuple length: {len(result_t)} for {view_name}")
                return self._process_view_result_tuple(result_t, view_name)
            else:
                logger.debug(f"Non-tuple result for {view_name}, creating auto-dispose")
                # Backward compatibility: create auto-dispose function
                # Track subscriptions for automatic cleanup
                dispose_func = self._create_auto_dispose_for_view(view_name)
                return result, dispose_func

        except Exception as e:
            logger.error(f"View creation failed for {view_name}: {e}")
            return self._create_error_view(f"Failed to create {view_name} view: {e}"), lambda: None

    def _create_auto_dispose_for_view(self, view_name: str) -> Callable[[], None]:
        """Create auto-dispose function for views that don't implement dispose (Comment 12)."""
        # For now, return a no-op function since automatic tracking would be complex
        # This allows views to be enhanced incrementally
        def auto_dispose() -> None:
            logger.debug(f"Auto-dispose called for view: {view_name} (no-op)")
        return auto_dispose

    def _create_error_view(self, error_message: str) -> ft.Control:
        """Simple error view for fallback."""
        def _on_return_button_click(e: ft.ControlEvent) -> None:
            # Explicit typed handler to satisfy static analysis
            try:
                self._load_view("dashboard")
            except Exception:
                logger.exception("Failed to switch to dashboard from error view")

        return ft.Container(
            content=ft.Column([
                ft.Text("Error", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ERROR),
                ft.Text(f"An error occurred: {error_message}", size=16),
                ft.ElevatedButton(
                    "Return to Dashboard",
                    on_click=_on_return_button_click
                )
            ], spacing=20),
            padding=20,
            expand=True
        )


# Simple application entry point
async def main(page: ft.Page, real_server: Optional[Any] = None) -> None:
    """Simple main function - supports optional real server injection."""
    def on_window_event(e: ft.ControlEvent) -> None:
        """Handle window events to force sizing."""
        if hasattr(e, 'data') and e.data in ("focus", "ready"):
            _p = cast(Any, page)
            with contextlib.suppress(Exception):
                _p.window_width = 1730
                _p.window_height = 1425
                _p.window_center = True
            page.update()  # type: ignore[call-arg]
            width = getattr(page, 'window_width', 'unknown')
            height = getattr(page, 'window_height', 'unknown')
            logger.info(f"Window resized via event: {width}x{height}")

    try:
        # Set up window event handler
        _p = cast(Any, page)
        with contextlib.suppress(Exception):
            _p.on_window_event = on_window_event

        # Initial window configuration
        with contextlib.suppress(Exception):
            _p.window_width = 1730
            _p.window_height = 1425
            _p.window_min_width = 1200
            _p.window_min_height = 900
            _p.window_resizable = True
            _p.window_center = True
        page.title = "Backup Server Management"

        # Create and add the simple desktop app with optional real server injection
        app = FletV2App(page, real_server=real_server)
        # Expose app instance on page for programmatic navigation from views (lightweight glue)
        with contextlib.suppress(Exception):
            if hasattr(page, '__dict__'):
                _p.app_ref = app  # type: ignore[attr-defined]

        # Add placeholder mode banner if in placeholder mode - import at point of use to avoid unused import warnings
        try:
            from utils.placeholder_mode_indicator import create_placeholder_mode_banner  # type: ignore[import-not-found]
            placeholder_banner = cast(ft.Control, cast(Any, create_placeholder_mode_banner)(app.server_bridge))
        except (ImportError, AttributeError):
            logger.warning("Placeholder mode indicator not available, continuing without banner")
            placeholder_banner = ft.Container(height=0)  # Empty container as fallback

        # Create main layout with banner and app
        main_layout = ft.Column([
            placeholder_banner,
            ft.Container(content=app, expand=True)
        ], spacing=0, expand=True)

        page.add(main_layout)

        # Additional attempts to force window size
        await asyncio.sleep(0.2)
        with contextlib.suppress(Exception):
            _p.window_width = 1730
            _p.window_height = 1425
        page.update()  # type: ignore[call-arg]

        width = getattr(page, 'window_width', 'unknown')
        height = getattr(page, 'window_height', 'unknown')
        logger.info(f"Window configured multiple attempts: {width}x{height}")

        logger.info(f"FletV2 App started - {bridge_type} active")

    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)
        # Simple error fallback
        error_text = ft.Text(f"Failed to start: {e}", color=ft.Colors.ERROR)
        page.add(error_text)

        # Show error in snackbar as well
        if hasattr(page, '__dict__'):  # Check if we can set attributes
            _p = cast(Any, page)
            _p.snack_bar = ft.SnackBar(
                content=ft.Text(f"Application failed to start: {str(e)}"),
                bgcolor=ft.Colors.RED,
                duration=3000
            )
            with contextlib.suppress(Exception):
                _p.snack_bar.open = True
        page.update()  # type: ignore[call-arg]


if __name__ == "__main__":
    # Simple launch - let Flet handle the complexity
    # Run in web mode for UI analysis
    import os as _os
    _port = int(_os.getenv("FLET_SERVER_PORT", "8000"))
    # Proactively check if the desired port is available; if not, use an ephemeral port.
    def _port_available(port: int) -> bool:
        import socket
        # Check IPv4
        try:
            s4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s4.bind(("0.0.0.0", port))
            s4.close()
        except OSError:
            return False
        # Check IPv6 if supported
        try:
            s6 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            s6.bind(("::", port))
            s6.close()
        except OSError:
            return False
        return True

    # Initialize real server for standalone mode
    backup_server = None
    if REAL_SERVER_AVAILABLE and real_server_instance is not None:
        # Use the existing real server instance
        backup_server = real_server_instance
        logger.info("✅ Using existing BackupServer instance for standalone mode")
    elif REAL_SERVER_AVAILABLE:
        try:
            # Create new BackupServer instance if needed
            backup_server = BackupServer()
            logger.info("✅ Created new BackupServer instance for standalone mode")
        except Exception as e:
            logger.error(f"❌ Failed to create BackupServer for standalone mode: {e}")
            backup_server = None
    else:
        logger.error("❌ Real server not available, application cannot run without server integration")
        logger.error("Please check that the python_server module is available and the database file exists")
        raise RuntimeError("Application requires real server integration")

    # Use desktop app mode to avoid FastAPI/pydantic dependencies
    print("FletV2 is starting in desktop mode (FLET_APP)")

    # Launch async Flet app in desktop mode with real server
    async def main_with_server(page: ft.Page) -> None:
        await main(page, backup_server)

    asyncio.run(ft.app_async(target=main_with_server, view=ft.AppView.FLET_APP))  # type: ignore[attr-defined]
