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

# Standard library imports
import asyncio
import builtins
import contextlib
import inspect
import logging
import os
import sys
import time  # For optional startup profiling
from collections.abc import Callable
from typing import Any

# Third-party imports
import flet as ft

from FletV2.components.breadcrumb import (
    BreadcrumbFactory,
    BreadcrumbNavigation,
    setup_breadcrumb_navigation,
)
from FletV2.components.global_search import create_global_search_bar

# Import global shortcuts system for desktop navigation
from FletV2.utils.global_shortcuts import GlobalShortcutManager, create_standard_application_shortcuts


def _bootstrap_paths() -> tuple[str, str, str, str]:
    """Ensure repo directories are registered on sys.path for local imports."""
    here_path = os.path.abspath(__file__)
    base_dir = os.path.dirname(here_path)
    parent_dir = os.path.dirname(base_dir)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    if os.path.basename(base_dir) == "FletV2":
        flet_root = base_dir
    else:
        flet_root = os.path.dirname(base_dir)

    repository_root = os.path.dirname(flet_root)
    if flet_root not in sys.path:
        sys.path.insert(0, flet_root)
    if repository_root not in sys.path:
        sys.path.insert(0, repository_root)

    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    return here_path, flet_root, repository_root, base_dir


_here, flet_v2_root, repo_root, project_root = _bootstrap_paths()

# ALWAYS import UTF-8 solution FIRST to fix encoding issues
# This MUST be imported before any subprocess or console operations
try:
    import Shared.utils.utf8_solution as _utf8_solution

    # Ensure initialization for side effects
    _utf8_solution.ensure_initialized()
except ImportError as e:
    print(f"WARNING: Could not import UTF-8 solution: {e}")
    # Set basic UTF-8 environment as fallback
    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

# Flet 0.28.3 has native FilterChip support - no polyfill needed
# Legacy FilterChip polyfill moved to archive/legacy_filter_chip_polyfill.py on 2025-10-28

# (Path setup handled above)

# Local imports - utilities first
try:
    from .utils.debug_setup import setup_terminal_debugging
except ImportError:
    # Silent fallback for import issues - create minimal debug setup with matching signature
    import logging
    # Optional already imported at top

    def setup_terminal_debugging(
        log_level: int = logging.INFO,
        logger_name: str | None = None,
    ) -> logging.Logger:
        logger = logging.getLogger(logger_name or __name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(handler)
        logger.setLevel(log_level)
        return logger

# UTF-8 solution already imported at the top of the file

# Initialize logging and environment BEFORE any logger usage
logger = setup_terminal_debugging(logger_name="FletV2.main")
_VERBOSE_DIAGNOSTICS = os.getenv("FLET_V2_VERBOSE", "").strip().lower() in {"1", "true", "yes"}
_VERBOSE_NAV_LOGS = (
    _VERBOSE_DIAGNOSTICS or
    os.getenv("FLET_V2_VERBOSE_NAV", "").strip().lower() in {"1", "true", "yes"}
)
os.environ.setdefault("PYTHONUTF8", "1")

_ORIGINAL_PRINT = builtins.print


def _diagnostic_print(*args: Any, **kwargs: Any) -> None:
    """Route legacy print-based diagnostics through the logger."""

    sep = kwargs.get("sep", " ")
    message = sep.join(str(arg) for arg in args)

    if _VERBOSE_DIAGNOSTICS:
        _ORIGINAL_PRINT(*args, **kwargs)
    else:
        logger.debug(message)


print = _diagnostic_print  # type: ignore[assignment]

# Install global exception handlers early so any silent crashes are surfaced.
def _install_global_exception_handlers() -> None:  # pragma: no cover - diagnostic utility
    try:
        previous_hook = sys.excepthook
    except Exception:
        previous_hook = None  # type: ignore[assignment]

    def _excepthook(exc_type, exc, tb):  # type: ignore[override]
        with contextlib.suppress(Exception):
            logger.critical("UNCAUGHT EXCEPTION (sys.excepthook)", exc_info=(exc_type, exc, tb))
        if previous_hook and previous_hook is not sys.excepthook:  # avoid recursion
            with contextlib.suppress(Exception):
                previous_hook(exc_type, exc, tb)  # type: ignore[misc]

    try:
        sys.excepthook = _excepthook  # type: ignore[assignment]
    except Exception:
        logger.warning("Failed to install sys.excepthook override")

    # Asyncio loop exception handler - fix Python 3.13 compatibility
    try:
        # Use get_running_loop() for Python 3.13 compatibility
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, skip loop exception handler setup
            loop = None

        def _loop_exception_handler(loop_obj, context):  # type: ignore[no-untyped-def]
            with contextlib.suppress(Exception):
                msg = context.get("message") or "Asyncio loop exception"
                logger.critical(f"ASYNCIO LOOP EXCEPTION: {msg}", exc_info=context.get("exception"))

        if loop:  # Only set handler if we have a running loop
            loop.set_exception_handler(_loop_exception_handler)
    except Exception as _loop_err:
        logger.warning(f"Failed to set asyncio loop exception handler: {_loop_err}")

_install_global_exception_handlers()

# Local imports - application modules
try:
    # Prefer package-relative import
    from .theme import setup_sophisticated_theme  # type: ignore[import-not-found]
except ImportError as _theme_rel_err:  # pragma: no cover - fallback path
    try:
        # Fallback to absolute import when running as a script inside FletV2 directory
        from theme import setup_sophisticated_theme  # type: ignore[import-not-found]
    except ImportError as _theme_abs_err:
        print(f"Warning: Could not import theme module: {_theme_rel_err}; {_theme_abs_err}")
        # Create minimal fallbacks so the app can still start
        def setup_sophisticated_theme(page):  # type: ignore[no-redef]
            return None

        def toggle_theme_mode(page):  # type: ignore[no-redef]
            return None

try:
    # Primary: package-relative import (works when launched via `python -m FletV2.main`)
    from .utils.server_bridge import create_server_bridge  # type: ignore[import-not-found]
except ImportError as _rel_err:  # pragma: no cover - fallback path
    try:
        # Fallback: absolute import (works when running `python FletV2/main.py` directly)
        from utils.server_bridge import create_server_bridge  # type: ignore[import-not-found]
    except ImportError as _abs_err:
        # Final explicit path-based fallback to avoid package context issues
        try:
            import importlib.util as _importlib_util
            _srv_path = os.path.join(flet_v2_root, 'utils', 'server_bridge.py')
            if os.path.isfile(_srv_path):
                _spec = _importlib_util.spec_from_file_location('fletv2_server_bridge_fallback', _srv_path)
                if _spec and _spec.loader:  # type: ignore[truthy-bool]
                    _mod = _importlib_util.module_from_spec(_spec)  # type: ignore[arg-type]
                    _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
                    if hasattr(_mod, 'create_server_bridge'):
                        create_server_bridge = _mod.create_server_bridge  # type: ignore[assignment]
                    else:
                        raise ImportError('create_server_bridge symbol missing in loaded module')
            else:
                raise ImportError(f'server_bridge.py not found at expected path: {_srv_path}')
        except Exception as _path_err:
            combined_err = f"{_rel_err}; {_abs_err}; {_path_err}"
            print(f"Error: Could not import server_bridge: {combined_err}")
            server_bridge_error = str(combined_err)
            def create_server_bridge(real_server: Any | None = None) -> Any:  # type: ignore[override]
                if real_server is None:
                    raise ValueError(
                        "ServerBridge requires a real server instance. "
                        "Mock data support has been removed."
                    )
                raise ImportError(f"ServerBridge module not available: {server_bridge_error}")

# Final safety net: dynamic import attempt if create_server_bridge still missing
if 'create_server_bridge' not in globals():  # pragma: no cover - rare path
    try:
        import importlib
        _mod = importlib.import_module('utils.server_bridge')
        if hasattr(_mod, 'create_server_bridge'):
            create_server_bridge = _mod.create_server_bridge  # type: ignore[assignment]
            print("Info: Loaded create_server_bridge via dynamic import fallback")
    except Exception as _dyn_err:
        print(f"Error: Dynamic import of server_bridge failed: {_dyn_err}")

# Exported runtime flags for tests and integration checks (real server required unless GUI-only override)
REAL_SERVER_AVAILABLE = False

# CRITICAL: Do NOT initialize BackupServer at module load time
# BackupServer sets up signal handlers which can only run in main thread
# Server initialization must happen via start_with_server.py launcher
real_server_instance = None

# Prepare environment for potential server integration (but don't create instance yet)
os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'
os.environ['CYBERBACKUP_DISABLE_GUI'] = '1'
logger.info("Disabled BackupServer embedded GUI to prevent conflicts")

# Set up paths and environment for server IF it gets initialized later
fletv2_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(fletv2_root)
main_db_path = os.path.join(project_root, "defensive.db")

# Add project_root to sys.path for python_server module
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    logger.info(f"Added project root to sys.path: {project_root}")

# Set database path environment variable (used if BackupServer is created)
os.environ['BACKUP_DATABASE_PATH'] = main_db_path
logger.info(f"Set BACKUP_DATABASE_PATH environment variable to: {main_db_path}")

# Log the server mode
logger.info("""
=======================================================================
FletV2 GUI Initialization Mode:
- Standalone Mode: Use 'flet run main.py' for GUI development (no server)
- Integrated Mode: Use 'python start_with_server.py' for full functionality
- Server instance will be passed via FletV2App constructor if available
=======================================================================
""")

# Direct server integration support (no adapter layer needed)
# The BackupServer has built-in ServerBridge compatibility
real_server_available = REAL_SERVER_AVAILABLE  # Will be True if server initialized above
create_fletv2_server = None  # Legacy - not needed for direct integration

# Ensure project root is in path for direct execution
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# bridge_type resolved later during server bridge initialization
bridge_type = "Unknown"


class AsyncManager:
    """
    Centralized async task lifecycle management for Flet applications.

    Provides cooperative cancellation and proper cleanup for background tasks
    to prevent UI freezing during navigation.
    """

    def __init__(self):
        self._cancelled: bool = False
        self._tasks: set[asyncio.Task] = set()
        self._view_name: str | None = None

    def set_view(self, view_name: str) -> None:
        """Associate this manager with a specific view."""
        self._view_name = view_name

    def cancel_all(self) -> None:
        """Cancel all registered tasks cooperatively."""
        self._cancelled = True
        logger.info(f"[ASYNC_MANAGER] Cancelling all tasks for view: {self._view_name}")

        # Cancel all tasks
        for task in list(self._tasks):
            if not task.done():
                task.cancel()

        # Clear the task set
        self._tasks.clear()

    def is_cancelled(self) -> bool:
        """Check if operations should be cancelled."""
        return self._cancelled

    def register_task(self, task: asyncio.Task) -> None:
        """Register a task for cleanup."""
        self._tasks.add(task)

        # Auto-remove task when done
        def cleanup(task_future: asyncio.Task) -> None:
            self._tasks.discard(task)

        task.add_done_callback(cleanup)

    async def run_cancellable(self, coro, *args, **kwargs):
        """Run a coroutine with cancellation support."""
        if self._cancelled:
            return None

        task = asyncio.create_task(coro(*args, **kwargs))
        self.register_task(task)

        try:
            return await task
        except asyncio.CancelledError:
            logger.debug(f"[ASYNC_MANAGER] Task cancelled for view: {self._view_name}")
            return None

    def safe_update(self, control: ft.Control) -> None:
        """Safely update a control, preventing updates from cancelled tasks."""
        if not self._cancelled and hasattr(control, 'page'):
            try:
                control.update()
            except Exception as e:
                logger.debug(f"[ASYNC_MANAGER] Failed to update control: {e}")


class FletV2App(ft.Row):
    """
    Clean FletV2 desktop app using pure Flet patterns.

    This demonstrates maximum framework harmony:
    - NavigationRail.on_change for navigation (no custom managers)
    - Container(expand=True) for responsive layout
    - Simple view switching with direct function calls
    - Uses theme.py for styling
    """

    def __init__(self, page: ft.Page, real_server: Any | None = None) -> None:
        super().__init__()
        if _VERBOSE_DIAGNOSTICS:
            logger.debug("FletV2App __init__ called")
        self.page: ft.Page = page  # Ensure page is never None
        self.expand = True

        # Type annotations for key attributes
        self.server_bridge: Any = None
        self.state_manager: Any | None = None
        self.content_area: ft.Container = ft.Container()
        self.nav_rail: ft.Container = ft.Container()
        self.nav_rail_extended: bool = True
        self._loaded_views: dict[str, ft.Control] = {}
        self._background_tasks: set[Any] = set()
        self._loading_view: bool = False  # Guard against concurrent view loads
        self._startup_profile: list[tuple[str, float]] = []
        # Track last view loading error for diagnostics UI
        self._last_view_error: str | None = None
        # Ensure initial view is loaded exactly once to avoid duplicate dashboard instances
        self._initial_view_loaded: bool = False

        # Async task management
        self.async_manager: AsyncManager = AsyncManager()

        # Desktop navigation components
        self.global_shortcut_manager: GlobalShortcutManager | None = None
        self.breadcrumb_navigation: BreadcrumbNavigation | None = None
        self.global_search = None

        # Startup profiling helpers (opt-in via FLET_STARTUP_PROFILER=1)
        def _profile_enabled() -> bool:
            return os.environ.get('FLET_STARTUP_PROFILER') == '1'

        def _mark(label: str) -> None:
            if _profile_enabled():
                self._startup_profile.append((label, time.perf_counter()))

        self._profile_enabled = _profile_enabled  # type: ignore[attr-defined]
        self._profile_mark = _mark  # type: ignore[attr-defined]
        self._profile_mark('init:start')

        # Initialize server bridge - prefer real server instance
        global bridge_type, real_server_available, real_server_instance
        try:
            if real_server is not None:
                # Direct server injection (from integrated startup script like start_with_server.py)
                logger.info("🎯 Using directly provided real server (direct injection)")
                self.server_bridge = create_server_bridge(real_server=real_server)
                bridge_type = "Direct BackupServer Integration"
                real_server_available = True
                logger.info("✅ Direct BackupServer integration activated!")

                # Test server bridge functionality
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
                    logger.warning("Server integration may have compatibility issues")
            else:
                # No real server available - default to GUI-only standalone mode
                logger.warning("⚠️ Starting in GUI-only standalone mode without server bridge")
                logger.warning("GUI will be functional but data operations will show empty states")
                logger.warning("Use 'python start_with_server.py' for full server integration")
                self.server_bridge = None
                bridge_type = "GUI-Only Standalone Mode (No Server)"
                real_server_available = False
        except Exception as bridge_ex:
            logger.error(f"❌ Server bridge initialization failed: {bridge_ex}")
            logger.warning("Falling back to GUI-only mode")
            self.server_bridge = None
            bridge_type = "GUI-Only Mode (Server Init Failed)"
            real_server_available = False

        logger.info(f"Final server bridge configuration: {bridge_type}")
        logger.info(f"Real server available: {real_server_available}")

        # Initialize enhanced state manager for reactive updates and inter-view coordination
        self._initialize_state_manager()
        if _VERBOSE_DIAGNOSTICS:
            logger.debug("State manager initialized for reactive updates")
        self._profile_mark('state_manager:initialized')

        # Comment 12: Track current view dispose function for proper StateManager cleanup
        self._current_view_dispose: Callable[[], None] | None = None
        self._current_view_name: str | None = None
        self._current_setup_task: asyncio.Task | None = None  # Track setup task for cancellation

        # Create optimized content area with modern Material Design 3 styling and fast transitions
        self._animated_switcher = ft.AnimatedSwitcher(
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
            expand=True,
        )

        self._breadcrumb_strip = ft.Container(visible=False, expand=False)

        content_column = ft.Column(
            controls=[
                self._breadcrumb_strip,
                ft.Container(content=self._animated_switcher, expand=True),
            ],
            spacing=16,
            expand=True,
        )

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
            content=content_column,
        )

        # Create navigation rail (using simple approach with collapsible functionality)
        print("🔧 About to create navigation rail...")
        self.nav_rail_extended = True  # Track extended state
        self.nav_rail = self._create_navigation_rail()
        print("✅ Navigation rail created")

        # Build layout: NavigationRail + content area (pure Flet pattern)
        self.controls = [
            self.nav_rail,
            ft.VerticalDivider(width=1, color=ft.Colors.with_opacity(0.12, ft.Colors.OUTLINE)),
            self.content_area
        ]

        # Set up page connection handler to load initial view (guarded)
        logger.info("Setting up page connection handler")
        def _guarded_on_connect(e: ft.ControlEvent) -> None:
            try:
                # Prevent duplicate loads: only navigate here if initialize() hasn't done it
                if not self._initial_view_loaded and not getattr(self, "_initialized", False):
                    logger.info("Page connected - loading initial dashboard view (guarded)")
                    self.navigate_to("dashboard")
                    # Mark to prevent any further on_connect-triggered loads
                    self._initial_view_loaded = True
            except Exception as connect_error:
                logger.error(f"Page connect error: {connect_error}")
        page.on_connect = _guarded_on_connect

        # Add disconnect cleanup to release resources and return DB connections
        def _on_disconnect(e: ft.ControlEvent | None = None):
            try:
                logger.info("Page disconnect detected - disposing app resources")
                self.dispose()
            except Exception as disconnect_err:
                logger.warning(f"Page disconnect cleanup error: {disconnect_err}")
        page.on_disconnect = _on_disconnect

        # Add dashboard loading management flags
        self._dashboard_loading = False
        self._dashboard_loaded = False

        # Dashboard will be loaded after page connection to ensure AnimatedSwitcher is attached
        logger.info("Dashboard will be loaded after page connection is established")

        # DISABLED: Proactive loading causing multiple instantiation issues
        # The page.on_connect handler will load the dashboard properly
        logger.info("Proactive dashboard loading disabled - using page.on_connect instead")

        # Post-update adjustments handled in _post_content_update

    def _initialize_state_manager(self) -> None:
        """Initialize simplified state management using Flet-native patterns."""
        if self.state_manager is not None:
            return  # Already initialized

        try:
            # Use Flet-native simple state management (replaces 1,036-line StateManager)
            from FletV2.utils.simple_state import create_simple_state
            self.state_manager = create_simple_state(self.page, self.server_bridge)
            logger.info("✅ Simple state manager initialized (Flet-native approach)")
        except ImportError as e:
            logger.warning(f"Could not import simple state manager: {e}")
            self.state_manager = None
        except Exception as e:
            print(f"🔴 [CRITICAL] Exception during state manager init: {e}")
            import traceback
            print(f"🔴 [CRITICAL] Traceback: {traceback.format_exc()}")
            raise

    def dispose(self) -> None:
        """Clean up resources when app is disposed."""
        try:
            logger.info("🧹 Disposing FletV2App resources...")

            # Dispose current view
            if self._current_view_dispose:
                try:
                    self._current_view_dispose()
                    logger.debug("Disposed current view")
                except Exception as e:
                    logger.warning(f"Error disposing current view: {e}")

            # Cancel background tasks
            for task in self._background_tasks:
                try:
                    if hasattr(task, 'cancel'):
                        task.cancel()
                except Exception as e:
                    logger.debug(f"Error canceling background task: {e}")
            self._background_tasks.clear()

            # Clear loaded views
            self._loaded_views.clear()

            # ✅ ELIMINATED: StateManager cleanup - no longer needed
            # Simple state patterns are self-cleaning and framework-native

            logger.info("✅ FletV2App resources disposed successfully")
        except Exception as e:
            logger.error(f"Error during FletV2App disposal: {e}")

    def _get_view_config(self, view_name: str) -> tuple[str, str, str]:
        """Get view configuration for dynamic import."""
        view_configs = {
            "dashboard": ("views.dashboard", "create_dashboard_view", "dashboard"),
            "clients": ("views.clients", "create_clients_view", "clients"),
            "files": ("views.files", "create_files_view", "files"),
            "database": (
                "views.database_pro", "create_database_view", "database"
            ),  # Professional view with full CRUD operations
            "analytics": ("views.analytics", "create_analytics_view", "analytics"),
            "logs": ("views.enhanced_logs", "create_logs_view", "logs"),
            "settings": ("views.settings", "create_settings_view", "settings"),
            "experimental": ("views.experimental", "create_experimental_view", "experimental"),
        }
        return view_configs.get(view_name, ("views.dashboard", "create_dashboard_view", "dashboard"))

    def _set_animation_for_view(self, view_name: str) -> None:
        """Set animation for view transitions."""
        try:
            if isinstance(self._animated_switcher, ft.AnimatedSwitcher):
                self._animated_switcher.transition = ft.AnimatedSwitcherTransition.FADE
                self._animated_switcher.duration = 200
        except Exception as e:
            logger.debug(f"Failed to set animation for {view_name}: {e}")

    def navigate_to(self, view_name: str) -> None:
        """Navigate to a specific view and sync navigation rail."""

        if not view_name:
            return

        if _VERBOSE_NAV_LOGS:
            logger.debug("navigate_to(%s) invoked (current=%s)", view_name, self._current_view_name)

        # CRITICAL FIX: Prevent navigating to the same view twice (causes setup cancellation)
        if view_name == self._current_view_name:
            if _VERBOSE_NAV_LOGS:
                logger.debug("Navigation to %s skipped; already active", view_name)
            return

        logger.info("View change requested: %s", view_name)

        # Update navigation rail selected index
        view_names = [
            "dashboard", "clients", "files", "database",
            "analytics", "logs", "settings", "experimental"
        ]
        if view_name in view_names and hasattr(self, "_nav_rail_control") and self._nav_rail_control:
            new_index = view_names.index(view_name)
            self._nav_rail_control.selected_index = new_index
            try:
                self._nav_rail_control.update()
            except Exception as rail_err:
                logger.warning("Navigation rail update failed: %s", rail_err)
            else:
                if _VERBOSE_NAV_LOGS:
                    logger.debug("Navigation rail updated to index %s", new_index)
        elif _VERBOSE_NAV_LOGS:
            logger.debug("Navigation rail not available or view missing: %s", view_name)

        self._perform_view_loading(view_name)
        if _VERBOSE_NAV_LOGS:
            logger.debug("Completed navigation to %s", view_name)

    def _create_navigation_rail(self) -> ft.NavigationRail:
        """Create native navigation rail using Flet's built-in features.

        Simplified from ~180 lines to ~90 lines by:
        - Using ft.NavigationRail directly (no container wrapper)
        - Native extended property (no custom width management)
        - Built-in animation (no custom animate property)
        - Standard styling (no manual shadows/borders)
        - Framework-harmonious patterns (work WITH Flet, not against it)
        """
        def on_nav_change(e: ft.ControlEvent) -> None:
            """Handle navigation changes using Flet's native on_change."""
            try:
                selected_index = e.control.selected_index
                view_names = [
                    "dashboard", "clients", "files", "database",
                    "analytics", "logs", "settings", "experimental"
                ]
                if 0 <= selected_index < len(view_names):
                    view_name = view_names[selected_index]
                    self.navigate_to(view_name)
                    # Update breadcrumbs for desktop navigation
                    self._update_breadcrumbs(view_name)
            except Exception as nav_error:
                logger.error(f"Navigation error: {nav_error}")

        def toggle_rail(e: ft.ControlEvent) -> None:
            """Toggle rail using Flet's native extended property."""
            try:
                self.nav_rail_extended = not self.nav_rail_extended
                rail.extended = self.nav_rail_extended

                # Update toggle button icon
                rail.leading.icon = ft.Icons.MENU_OPEN if self.nav_rail_extended else ft.Icons.MENU
                rail.leading.tooltip = "Collapse sidebar" if self.nav_rail_extended else "Expand sidebar"

                rail.update()
                state_text = 'expanded' if self.nav_rail_extended else 'collapsed'
                logger.info(f"Navigation rail {state_text}")
            except Exception as toggle_error:
                logger.error(f"Toggle rail error: {toggle_error}")

        # Native NavigationRail - let Flet handle the complexity
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            extended=self.nav_rail_extended,
            on_change=on_nav_change,
            # Flet manages width automatically when extended=True/False
            min_width=56,
            min_extended_width=168,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.DASHBOARD_OUTLINED,
                    selected_icon=ft.Icons.DASHBOARD,
                    label="Dashboard"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PEOPLE_OUTLINED,
                    selected_icon=ft.Icons.PEOPLE,
                    label="Clients"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.FOLDER_OUTLINED,
                    selected_icon=ft.Icons.FOLDER,
                    label="Files"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.STORAGE_OUTLINED,
                    selected_icon=ft.Icons.STORAGE,
                    label="Database"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ANALYTICS_OUTLINED,
                    selected_icon=ft.Icons.ANALYTICS,
                    label="Analytics"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.LIST_ALT_OUTLINED,
                    selected_icon=ft.Icons.LIST_ALT,
                    label="Logs"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Settings"
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.SCIENCE_OUTLINED,
                    selected_icon=ft.Icons.SCIENCE,
                    label="Experimental"
                ),
            ],
            # Enhanced theme integration using native Flet styling
            bgcolor=ft.Colors.SURFACE,
            indicator_color=ft.Colors.with_opacity(0.15, ft.Colors.PRIMARY),
            indicator_shape=ft.RoundedRectangleBorder(radius=12),
            selected_label_text_style=ft.TextStyle(
                size=13,
                weight=ft.FontWeight.W_600,
                color=ft.Colors.PRIMARY
            ),
            unselected_label_text_style=ft.TextStyle(
                size=12,
                weight=ft.FontWeight.W_400,
                color=ft.Colors.with_opacity(0.7, ft.Colors.ON_SURFACE)
            ),
            # Native leading area for toggle button
            leading=ft.IconButton(
                icon=ft.Icons.MENU_OPEN if self.nav_rail_extended else ft.Icons.MENU,
                tooltip="Collapse sidebar" if self.nav_rail_extended else "Expand sidebar",
                on_click=toggle_rail,
                icon_color=ft.Colors.PRIMARY
            )
        )

        # Store reference for programmatic navigation
        self._nav_rail_control = rail
        return rail

    def _on_page_connect(self, e: ft.ControlEvent) -> None:
        """Handle page connection event."""
        try:
            logger.info("Page connected - loading initial dashboard view")
            self.navigate_to("dashboard")
        except Exception as connect_error:
            logger.error(f"Page connect error: {connect_error}")

    def _update_breadcrumbs(self, view_name: str) -> None:
        """Update breadcrumbs based on current view"""
        if not self.breadcrumb_navigation:
            return

        try:
            # Create breadcrumb items for different views
            if view_name == "database":
                from FletV2.components.breadcrumb import BreadcrumbItem
                items = BreadcrumbFactory.create_database_breadcrumb()
            elif view_name == "files":
                from FletV2.components.breadcrumb import BreadcrumbItem
                items = BreadcrumbFactory.create_file_breadcrumb([])
            elif view_name == "logs":
                from FletV2.components.breadcrumb import BreadcrumbItem
                items = BreadcrumbFactory.create_log_breadcrumb()
            elif view_name == "settings":
                from FletV2.components.breadcrumb import BreadcrumbItem
                items = BreadcrumbFactory.create_settings_breadcrumb()
            else:
                # Default breadcrumb for other views
                from FletV2.components.breadcrumb import BreadcrumbItem
                items = [
                    BreadcrumbItem(
                        label=view_name.title(),
                        icon=ft.Icons.DASHBOARD if view_name == "dashboard" else ft.Icons.INFO,
                        is_current=True
                    )
                ]

            self.breadcrumb_navigation.set_items(items)
            if self._breadcrumb_strip:
                self._breadcrumb_strip.visible = True
                if getattr(self._breadcrumb_strip, "page", None):
                    self._breadcrumb_strip.update()

        except Exception as e:
            logger.error(f"Failed to update breadcrumbs: {e}")

    def _setup_desktop_navigation(self) -> None:
        """Setup desktop navigation features - global shortcuts, breadcrumbs, search"""
        try:
            logger.info("Setting up desktop navigation features")

            # Initialize global shortcut manager
            self.global_shortcut_manager = GlobalShortcutManager(self.page)

            # Create view navigator function for shortcuts
            def view_navigator(view_name: str) -> None:
                """Navigate to a specific view"""
                allowed_views = [
                    "dashboard", "clients", "files", "database",
                    "analytics", "logs", "settings"
                ]
                if view_name in allowed_views:
                    self.navigate_to(view_name)

            # Setup standard application shortcuts
            create_standard_application_shortcuts(
                self.global_shortcut_manager,
                view_navigator=view_navigator
            )

            # Initialize breadcrumb navigation
            self.breadcrumb_navigation = BreadcrumbNavigation(
                on_navigation=lambda destination: logger.info(f"Breadcrumb navigation to: {destination}")
            )

            breadcrumb_container = setup_breadcrumb_navigation(
                self.page,
                self.breadcrumb_navigation,
                self.navigate_to,
            )
            self._breadcrumb_strip.content = breadcrumb_container
            self._breadcrumb_strip.visible = True
            if getattr(self._breadcrumb_strip, "page", None):
                self._breadcrumb_strip.update()

            # Initialize global search
            self.global_search = create_global_search_bar()

            # Add desktop navigation components to page overlay
            if self.global_search:
                self.page.overlay.append(self.global_search)

            # Prime breadcrumb trail with the current or default view
            current_view = self._current_view_name or "dashboard"
            self._update_breadcrumbs(current_view)

            logger.info("✅ Desktop navigation features initialized successfully")

        except Exception as e:
            logger.error(f"Failed to setup desktop navigation: {e}")
            print(f"❌ Desktop navigation setup failed: {e}")

    async def initialize(self) -> None:
        """Initialize the application."""
        print("🔴 [CRITICAL DEBUG] initialize() method ENTERED")
        try:
            print("🔴 [DEBUG] About to call logger.info()")
            logger.info("🚀 FletV2 application initialization started")
            print("🔴 [DEBUG] logger.info() completed")

            print("🔴 [DEBUG] Checking _initialized flag")
            if getattr(self, '_initialized', False):
                logger.debug("initialize() called more than once; ignoring subsequent call")
                return
            print("🔴 [DEBUG] _initialized check passed")

            loop = asyncio.get_running_loop()
            if not getattr(self, "_loop_exception_handler_installed", False):
                previous_handler = loop.get_exception_handler()

                def _loop_handler(loop_obj: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
                    exc = context.get("exception")
                    message = context.get("message", "")

                    error_text = str(exc) if exc else message

                    if "cannot schedule new futures after shutdown" in error_text:
                        logger.debug("Suppressed executor shutdown noise during shutdown")
                        return

                    if isinstance(exc, asyncio.CancelledError):
                        # Routine cancellation at shutdown - ignore silently
                        return

                    if isinstance(exc, RuntimeError) and "Event loop is closed" in error_text:
                        logger.debug("Suppressed executor shutdown noise during shutdown")
                        return

                    if previous_handler is not None:
                        previous_handler(loop_obj, context)
                    else:
                        loop_obj.default_exception_handler(context)

                loop.set_exception_handler(_loop_handler)
                self._loop_exception_handler_installed = True

            print("🔴 [DEBUG] About to call setup_sophisticated_theme()")
            # Apply theme with Windows 11 integration
            setup_sophisticated_theme(self.page)
            print("🔴 [DEBUG] setup_sophisticated_theme() completed")
            logger.debug("Theme setup complete")

            print("🔴 [DEBUG] About to add app to page")
            # Add the app to the page
            self.page.add(self)
            print("🔴 [DEBUG] self.page.add(self) completed")

            print("🔴 [DEBUG] Setting page properties")
            # Set page properties
            self.page.title = "FletV2 - Encrypted Backup Framework"
            self.page.auto_update = True  # Enable automatic UI updates for better performance
            print("🔴 [DEBUG] page.title set")
            print("🔴 [DEBUG] page.auto_update enabled")

            # Window properties only work in FLET_APP mode, not WEB_BROWSER
            try:
                if hasattr(self.page, 'window') and self.page.window:
                    self.page.window.width = 1200
                    self.page.window.height = 800
                    self.page.window.min_width = 800
                    self.page.window.min_height = 600
                    print("🔴 [DEBUG] window properties set")
                else:
                    print("🔴 [DEBUG] page.window not available (running in web mode)")
            except Exception as win_err:
                logger.debug(f"Could not set window properties (web mode?): {win_err}")
                print(f"🔴 [DEBUG] window property error: {win_err}")

            print("🔴 [DEBUG] About to call page.update()")
            # Update the page
            self.page.update()
            print("🔴 [DEBUG] page.update() completed")

            # Initialize desktop navigation features
            self._setup_desktop_navigation()
            print("🔴 [DEBUG] Desktop navigation setup completed")

            self._initialized = True
            print("🔴 [DEBUG] _initialized flag set to True")

            logger.info("✅ FletV2 application initialized successfully")
            print("🔴 [DEBUG] About to load dashboard")

            # Load initial dashboard view. Mark as loaded to prevent on_connect from loading again.
            try:
                logger.info("📊 Loading initial dashboard view...")
                print("🔴 [DEBUG] Calling navigate_to('dashboard')")
                self.navigate_to("dashboard")
                print("🔴 [DEBUG] navigate_to returned")
                logger.info("✅ Dashboard navigation completed")
                # Guard: mark that initial view is loaded to avoid duplicate loads via on_connect
                self._initial_view_loaded = True
            except Exception as dash_err:
                print(f"🔴 [DEBUG] Dashboard navigation raised exception: {dash_err}")
                logger.error(f"❌ Failed to load dashboard: {dash_err}")
                import traceback
                logger.error(f"Dashboard load traceback: {traceback.format_exc()}")
                print(f"🔴 [DEBUG] Traceback: {traceback.format_exc()}")

            print("🔴 [DEBUG] End of initialize() method reached")

            # Optional internal navigation smoke test
            if os.environ.get("FLET_NAV_SMOKE") == '1':
                with contextlib.suppress(Exception):
                    self.page.run_task(self._run_nav_smoke_test)
        except Exception as e:
            logger.error(f"❌ Application initialization failed: {e}")
            raise

    def _dispose_current_view(self, new_view_name: str) -> None:
        """Dispose of the current view before loading a new one using AsyncManager."""
        if new_view_name != self._current_view_name:
            logger.info(f"[DISPOSE] Disposing view '{self._current_view_name}' → '{new_view_name}'")

            # 1. Cancel async tasks FIRST using AsyncManager
            self.async_manager.cancel_all()

            # 2. Cancel the individual setup task if it exists
            setup_task = self._current_setup_task
            if setup_task and not setup_task.done():
                print(f"🟥 [DISPOSE] Cancelling setup task for '{self._current_view_name}'")
                logger.info(f"[DISPOSE] Cancelling setup task for view: {self._current_view_name}")
                setup_task.cancel()
            self._current_setup_task = None

            # 3. Call view's dispose function synchronously
            if self._current_view_dispose:
                try:
                    self._current_view_dispose()
                    logger.debug(f"[DISPOSE] Successfully disposed view: {self._current_view_name}")
                except Exception as e:
                    logger.warning(
                    f"[DISPOSE] Failed to dispose previous view "
                    f"{self._current_view_name}: {e}"
                )
                finally:
                    self._current_view_dispose = None
                    self._current_view_name = None

    def _perform_view_loading(self, view_name: str) -> bool:
        """Perform the core view loading logic."""
        print(f"🚨🚨🚨 _perform_view_loading ENTERED for '{view_name}' 🚨🚨🚨")
        logger.info(f"🔄 Loading view: {view_name} (previous: {self._current_view_name})")

        # Comment 12: Dispose of current view before loading new one
        self._dispose_current_view(view_name)

        # IMPORTANT: Reset and associate AsyncManager with new view
        self.async_manager = AsyncManager()  # Fresh manager for each view
        self.async_manager.set_view(view_name)

        # Get view configuration
        module_name, function_name, actual_view_name = self._get_view_config(view_name)
        logger.debug(f"View config - module: {module_name}, function: {function_name}")

        # Dynamic import and view creation
        try:
            print(f"🔴 [IMPORT] About to import module '{module_name}' for view '{view_name}'")
            logger.debug(f"Importing view module '{module_name}'")
            module = __import__(module_name, fromlist=[function_name])
            print(f"🔴 [IMPORT] Module imported successfully: {module}")

            print(f"🔴 [IMPORT] Checking if module has function '{function_name}'")
            if not hasattr(module, function_name):
                raise AttributeError(f"Module '{module_name}' missing '{function_name}'")
            view_function = getattr(module, function_name)
            print(f"🔴 [IMPORT] Got view function: {view_function}")

            # Call the view function directly with required arguments
            # Dashboard needs navigate_callback for hero card clicks
            print(f"🔴 [CALL] About to call view function for '{view_name}'")
            signature = inspect.signature(view_function)
            call_kwargs: dict[str, Any] = {}
            if "server_bridge" in signature.parameters:
                call_kwargs["server_bridge"] = self.server_bridge
            if "page" in signature.parameters:
                call_kwargs["page"] = self.page
            if "_state_manager" in signature.parameters:
                call_kwargs["_state_manager"] = self.state_manager
            elif "state_manager" in signature.parameters:
                call_kwargs["state_manager"] = self.state_manager
            if "navigate_callback" in signature.parameters:
                call_kwargs["navigate_callback"] = self.navigate_to
            if "async_manager" in signature.parameters:
                call_kwargs["async_manager"] = self.async_manager

            result = view_function(**call_kwargs)
            print(f"🔴 [CALL] View function returned: {type(result)}")

            # DEBUG: Log result structure
            is_tuple = isinstance(result, tuple)
            length = len(result) if is_tuple else 'N/A'
            logger.info(
                f"🔍 [{view_name.upper()}] Result type: {type(result)}, "
                f"is tuple: {is_tuple}, len: {length}"
            )
            if isinstance(result, tuple) and len(result) >= 2:
                result2_callable = (
                    callable(result[2]) if len(result) > 2 else 'N/A'
                )
                logger.info(
                    f"🔍 [{view_name.upper()}] result[0] type: {type(result[0])}, "
                    f"result[1] callable: {callable(result[1])}, "
                    f"result[2] exists: {len(result) > 2}, "
                    f"result[2] callable: {result2_callable}"
                )

            # Handle different return types: tuple (content, dispose, setup) or just content
            if isinstance(result, tuple) and len(result) >= 2:
                content = result[0]
                dispose_func = result[1] if len(result) > 1 else lambda: None
                setup_func = result[2] if len(result) > 2 else None
                # Store setup function to be called AFTER content is added to page
                self._current_view_setup = setup_func
                setup_callable = callable(setup_func) if setup_func else False
                logger.info(
                    f"🔍 [{view_name.upper()}] Stored setup_func: {setup_func}, "
                    f"callable: {setup_callable}"
                )
            else:
                content = result
                dispose_func = lambda: None  # noqa: E731
                self._current_view_setup = None
            logger.info(f"✅ View content created for '{view_name}'")
            print(f"🟣 [PERFORM_VIEW] logger.info executed successfully for '{view_name}'")
        except Exception as e:
            print(f"🔴 [ERROR] Exception caught for view '{view_name}': {e}")
            print(f"🔴 [ERROR] Exception type: {type(e)}")
            logger.error(f"❌ Error loading view '{view_name}': {e}")
            import traceback
            tb_str = traceback.format_exc()
            print(f"🔴 [ERROR] Traceback:\n{tb_str}")
            logger.error(f"Full traceback: {tb_str}")
            # Store last error for UI diagnostics
            self._last_view_error = f"{view_name}: {e}"
            # Special handling: if dashboard fails, attempt stub
            if view_name != "dashboard":
                # Provide inline error diagnostics UI instead of raising to avoid blank screen
                error_details = getattr(e, 'args', [''])[0]
                error_tb = traceback.format_exc(limit=5)
                logger.warning(f"Rendering inline error panel for failed view '{view_name}'")
                content = ft.Container(
                    content=ft.Column([
                        ft.Text(
                            f"❌ Failed to load view: {view_name}",
                            size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ERROR
                        ),
                        ft.Text(str(error_details), size=14, color=ft.Colors.ERROR),
                        ft.Text("Traceback (truncated):", size=12, weight=ft.FontWeight.W_600),
                        ft.Text(error_tb, selectable=True, size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Divider(),
                        ft.Text(
                            "This is a diagnostics panel. Navigate to another view to continue.",
                            size=12, color=ft.Colors.ON_SURFACE_VARIANT
                        )
                    ], spacing=8, scroll=ft.ScrollMode.ALWAYS),
                    padding=20,
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ERROR),
                    border=ft.border.all(1, ft.Colors.with_opacity(0.4, ft.Colors.ERROR)),
                    border_radius=12,
                )
                dispose_func = lambda: None  # noqa: E731
            else:
                # For dashboard keep existing stub fallback path
                # (original logic continues below)
                pass
            try:
                logger.warning("Attempting fallback stub dashboard due to failure")
                stub_content = None
                try:
                    from views.dashboard_stub import create_dashboard_stub  # type: ignore[import-not-found]
                    stub_content = create_dashboard_stub(self.page)
                except ModuleNotFoundError:
                    logger.debug("Dashboard stub module not found; using inline fallback UI")
                    stub_content = self._create_inline_dashboard_stub()

                if stub_content is None:
                    raise RuntimeError("Dashboard stub unavailable")

                content = stub_content
                dispose_func = lambda: None  # noqa: E731
                logger.info("Loaded dashboard stub successfully")
            except Exception as stub_err:
                logger.error(f"Dashboard stub load failed: {stub_err}")
                raise

        # Store dispose function for cleanup (Comment 12)
        self._current_view_dispose = dispose_func
        self._current_view_name = view_name

        self._set_animation_for_view(actual_view_name)

        # Update content area using AnimatedSwitcher for smooth transitions
        animated_switcher = self._animated_switcher
        return self._update_content_area(animated_switcher, content, view_name)

    def _update_content_area(self, animated_switcher, content, view_name: str) -> bool:
        """Safely update the content area with simplified view loading"""
        print(f"🔵 [UPDATE_CONTENT] ENTERED for view '{view_name}'")
        # Store reference for diagnostics that need to inspect attachment state later
        self._animated_switcher = animated_switcher
        try:
            print("🔵 [UPDATE_CONTENT] About to set content.key")
            # Unique and stable key for AnimatedSwitcher
            content.key = f"{view_name}_view_{int(time.time() * 1000)}"
            print("🔵 [UPDATE_CONTENT] Key set successfully")

            # Single, atomic content update
            if isinstance(animated_switcher, ft.AnimatedSwitcher):
                print("🔵 [UPDATE_CONTENT] AnimatedSwitcher detected, updating content")
                animated_switcher.content = content
                print("🔵 [UPDATE_CONTENT] Content assigned, setting transition")
                animated_switcher.transition = ft.AnimatedSwitcherTransition.FADE
                print("🔵 [UPDATE_CONTENT] About to call animated_switcher.update()")
                animated_switcher.update()
                print("🔵 [UPDATE_CONTENT] animated_switcher.update() completed")

            # Post-update visibility and subscription management
            print("🔵 [UPDATE_CONTENT] About to call _post_content_update")
            self._post_content_update(content, view_name)
            print("🔵 [UPDATE_CONTENT] _post_content_update completed")

            print(f"🟣 [UPDATE_CONTENT] About to call logger.info for '{view_name}'")
            logger.info(f"Successfully updated content area with {view_name}")
            print("🟣 [UPDATE_CONTENT] logger.info completed, about to return True")
            return True
        except Exception as e:
            print(f"🔴 [UPDATE_CONTENT] EXCEPTION CAUGHT: {e}")
            import traceback
            print(f"🔴 [UPDATE_CONTENT] Traceback:\n{traceback.format_exc()}")
            logger.error(f"Content area update failed for {view_name}: {e}")
            return False
        finally:
            self._loading_view = False

    def _post_content_update(self, content: Any, view_name: str) -> None:
        """Handle visibility and subscription setup after content update."""
        if content is None:
            return

        # Call setup function asynchronously (AFTER content is rendered)
        has_setup = hasattr(self, '_current_view_setup')
        setup_value = getattr(self, '_current_view_setup', 'NO_ATTR')
        setup_callable = (
            callable(getattr(self, '_current_view_setup', None))
            if has_setup else False
        )
        logger.info(
            f"[POST_UPDATE] Checking setup for {view_name}, "
            f"has attr: {has_setup}, value: {setup_value}, "
            f"callable: {setup_callable}"
        )
        setup_check = (
            hasattr(self, '_current_view_setup') and
            self._current_view_setup and
            callable(self._current_view_setup)
        )
        logger.info(f"[POST_UPDATE] setup_check result for {view_name}: {setup_check}")
        if setup_check:
            setup_func = self._current_view_setup
            self._current_view_setup = None  # Clear immediately to prevent double-calling

            task_holder: dict[str, asyncio.Task | None] = {"task": None}

            async def delayed_setup():
                """Delay setup until controls are fully attached to page tree."""
                try:
                    # Wait for AnimatedSwitcher transition to complete (160ms) + safety margin
                    await asyncio.sleep(0.25)  # Let Flet complete rendering and transition

                    # Check cancellation after sleep - prevents race conditions
                    if self.async_manager.is_cancelled():
                        logger.debug(f"[SETUP_TASK] Setup cancelled after sleep for '{view_name}'")
                        return

                    logger.info(f"Calling delayed setup function for {view_name}")

                    # Guard against None/non-callable and handle both sync and async functions
                    if setup_func and callable(setup_func):
                        try:
                            # Run setup function with cancellation support
                            if asyncio.iscoroutinefunction(setup_func):
                                await self.async_manager.run_cancellable(setup_func)
                            else:
                                # For sync functions, check cancellation before calling
                                if not self.async_manager.is_cancelled():
                                    setup_func()
                        except asyncio.CancelledError:
                            print(f"🟦 [SETUP_TASK] Setup cancelled for '{view_name}'")
                            logger.info(f"Setup cancelled for {view_name}")
                            raise  # Re-raise to properly cancel the task
                        except Exception as setup_err:
                            logger.warning(f"Setup function execution failed: {setup_err}")
                    else:
                        logger.debug("No setup_func to execute (None or not callable); skipping")
                except asyncio.CancelledError:
                    print(f"🟦 [SETUP_TASK] Delayed setup cancelled during sleep for '{view_name}'")
                    raise  # Re-raise to properly cancel the task
                except Exception as setup_err:
                    logger.warning(f"Setup function failed for {view_name}: {setup_err}")
                finally:
                    # Clear task reference when done (successfully or cancelled)
                    if (
                        task_holder["task"] is not None
                        and self._current_setup_task is task_holder["task"]
                    ):
                        print(f"🟦 [SETUP_TASK] Clearing setup task reference for '{view_name}'")
                        self._current_setup_task = None

            # Run setup asynchronously using page.run_task() and track for cancellation
            try:
                task = self.page.run_task(delayed_setup)
                task_holder["task"] = task
                self._current_setup_task = task
                print(f"🟦 [SETUP_TASK] Created setup task for '{view_name}': {task}")
            except Exception as e:
                logger.warning(f"Failed to schedule setup task for {view_name}: {e}")

        # Force visibility if dashboard content remains hidden
        if view_name == 'dashboard':
            try:
                if getattr(content, 'opacity', 1.0) == 0.0:
                    logger.warning("Dashboard opacity still 0 after update; forcing to 1.0")
                    content.opacity = 1.0
                    with contextlib.suppress(Exception):
                        content.update()

                def _force_visible_recursive(ctrl, depth: int = 0, max_depth: int = 10) -> None:
                    if ctrl is None:
                        return

                    # Prefer contextlib.suppress for concise suppressed-exception blocks
                    with contextlib.suppress(Exception):
                        if hasattr(ctrl, 'visible') and ctrl.visible is False:
                            ctrl.visible = True

                    with contextlib.suppress(Exception):
                        if hasattr(ctrl, 'opacity') and ctrl.opacity is not None and ctrl.opacity != 1.0:
                            ctrl.opacity = 1.0

                    with contextlib.suppress(Exception):
                        if hasattr(ctrl, 'update'):
                            try:
                                ctrl.update()
                            except Exception:
                                # Keep inner safety for update() call failures
                                pass

                    if depth >= max_depth:
                        return

                    # Suppress errors across recursive descent (safer and clearer than a bare try/except)
                    with contextlib.suppress(Exception):
                        if hasattr(ctrl, 'controls') and ctrl.controls:
                            for child in list(ctrl.controls):
                                _force_visible_recursive(child, depth + 1, max_depth)

                        if hasattr(ctrl, 'content') and ctrl.content:
                            _force_visible_recursive(ctrl.content, depth + 1, max_depth)

                        if hasattr(ctrl, 'rows') and ctrl.rows:
                            for child in list(ctrl.rows):
                                _force_visible_recursive(child, depth + 1, max_depth)

                        if hasattr(ctrl, 'columns') and ctrl.columns:
                            for child in list(ctrl.columns):
                                _force_visible_recursive(child, depth + 1, max_depth)

                _force_visible_recursive(content, 0, 10)

                # Use contextlib.suppress for page.update safety
                with contextlib.suppress(Exception):
                    if hasattr(self, 'page') and self.page is not None:
                        self.page.update()

                logger.info('[DASH_FIX] Forced nested dashboard controls visible (aggressive)')
            except Exception as vis_err:
                logger.debug(f"Failed forcing dashboard opacity: {vis_err}")

        # Note: Subscription setup is handled by delayed_setup() above (lines 987-1005)
        # The setup_func from the view's return tuple is called after transition completes


    async def _run_nav_smoke_test(self) -> None:
        """Cycle through all views to surface hidden loading errors.

        Triggered only when env var FLET_NAV_SMOKE=1.
        """
        if getattr(self, '_nav_smoke_test_running', False):  # Guard
            return
        self._nav_smoke_test_running = True
        view_names = [
            "dashboard", "clients", "files", "database",
            "analytics", "logs", "settings", "experimental"
        ]
        logger.info("[SMOKE] Starting navigation smoke test across %d views", len(view_names))
        errors: list[str] = []
        for name in view_names:
            try:
                logger.info(f"[SMOKE] Navigating to {name} ...")
                self.navigate_to(name)
                await asyncio.sleep(0.35)  # Allow rendering & setup
                if self._last_view_error and self._last_view_error.startswith(name):
                    errors.append(self._last_view_error)
            except Exception as nav_err:
                err_msg = f"{name}: {nav_err}"
                errors.append(err_msg)
                logger.error(f"[SMOKE] Error navigating to {name}: {nav_err}")
        if errors:
            logger.warning("[SMOKE] Completed with %d view errors", len(errors))
            for e in errors:
                logger.warning(f"[SMOKE][ERROR] {e}")
        else:
            logger.info("[SMOKE] All views loaded without detected errors")
        self._nav_smoke_test_running = False

    def _create_inline_dashboard_stub(self) -> ft.Control:
        """Provide a minimal dashboard fallback when the external stub module is archived."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.DASHBOARD, color=ft.Colors.PRIMARY, size=28),
                            ft.Text("Dashboard Stub Active", size=22, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=10,
                    ),
                    ft.Text(
                        "The dashboard failed to load. Review logs for details.",
                        size=13,
                        color=ft.Colors.ON_SURFACE,
                    ),
                    ft.Text(
                        "Once the issue is resolved, restart or navigate back to reload the dashboard.",
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=20,
            expand=True,
        )


if __name__ == "__main__":
    import sys

    import flet as ft

    def main(page: ft.Page) -> None:
        """Main entry point for GUI-only mode (no server integration)."""
        try:
            logger.info("🚀 Launching FletV2 in GUI-only mode (no server)")
            # Create app without server bridge (will use placeholder data)
            app = FletV2App(page, real_server=None)
            page.run_task(app.initialize)
        except Exception as e:
            print(f"❌ FATAL ERROR in main(): {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # Launch in web browser mode with port fallback
    try:
        print("🌐 Attempting to start Flet app on port 8550...")
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
    except OSError as e:
        logger.warning(f"Port 8550 in use ({e}), trying 8551...")
        try:
            ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8551)
        except OSError as e2:
            logger.warning(f"Port 8551 in use ({e2}), trying 8552...")
            ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8552)
    except Exception as e:
        print(f"❌ FATAL ERROR starting Flet app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
