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
import contextlib
import os
import sys
import time  # For optional startup profiling
from collections.abc import Callable
from typing import Any, cast

# Third-party imports
import flet as ft


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

if not hasattr(ft, "FilterChip"):
    class FilterChip(ft.Container):  # sourcery skip: remove-unnecessary-cast, remove-unnecessary-try-except
        def __init__(
            self,
            label: str = "",
            selected: bool = False,
            on_selected: Callable[[ft.ControlEvent], None] | None = None,
            **kwargs: Any,
        ) -> None:
            self.label = label
            self.selected = selected
            self.on_selected = on_selected
            self._button = ft.ElevatedButton(
                text=label,
                on_click=self._handle_click,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16)),
            )
            super().__init__(
                content=self._button,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                **kwargs,
            )
            self._refresh_style()

        def _handle_click(self, e: ft.ControlEvent) -> None:
            with contextlib.suppress(Exception):
                if callable(self.on_selected):
                    ev = type("Evt", (), {"control": self})()
                    self.on_selected(ev)

        def _refresh_style(self) -> None:
            with contextlib.suppress(Exception):
                if self.selected:
                    self._button.bgcolor = ft.Colors.PRIMARY
                    self._button.color = ft.Colors.ON_PRIMARY
                else:
                    self._button.bgcolor = None
                    self._button.color = None
                self._button.update()

        def update(self, *args: Any, **kwargs: Any) -> None:
            self._refresh_style()
            try:
                super().update(*args, **kwargs)
            except Exception:
                with contextlib.suppress(Exception):
                    self._button.update()

    ft.FilterChip = cast(Any, FilterChip)  # type: ignore[attr-defined]

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
os.environ.setdefault("PYTHONUTF8", "1")

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
    from .theme import setup_modern_theme, toggle_theme_mode  # type: ignore[import-not-found]
except ImportError as _theme_rel_err:  # pragma: no cover - fallback path
    try:
        # Fallback to absolute import when running as a script inside FletV2 directory
        from theme import setup_modern_theme, toggle_theme_mode  # type: ignore[import-not-found]
    except ImportError as _theme_abs_err:
        print(f"Warning: Could not import theme module: {_theme_rel_err}; {_theme_abs_err}")
        # Create minimal fallbacks so the app can still start
        def setup_modern_theme(page):  # type: ignore[no-redef]
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

    # Add project_root to sys.path BEFORE import to ensure python_server module is found
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.info(f"Added project root to sys.path: {project_root}")

    # Set environment variable BEFORE importing BackupServer to ensure proper initialization
    os.environ['BACKUP_DATABASE_PATH'] = main_db_path
    logger.info(f"Set BACKUP_DATABASE_PATH environment variable to: {main_db_path}")

    # Import the BackupServer AFTER setting environment variables and path
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
    # Removed legacy BRIDGE_TYPE constant (deprecated). Single runtime variable 'bridge_type' retained.
    logger.info("✅ Real BackupServer initialized successfully and verified")

except ImportError as e:
    logger.error(f"Could not import BackupServer - check if python_server is available: {e}")
    logger.warning(
        "Real server unavailable. Set FLET_GUI_ONLY_MODE=1 for limited GUI-only mode or fix import."
    )
    real_server_instance = None
except FileNotFoundError as e:
    logger.error(f"Database file not found: {e}")
    logger.warning(
        "Real server startup blocked by missing database. Provide database or set FLET_GUI_ONLY_MODE=1."
    )
    real_server_instance = None
except Exception as e:
    logger.error(f"Failed to initialize BackupServer: {e}")
    logger.warning(
        "Real server initialization failed. Use FLET_GUI_ONLY_MODE=1 for GUI-only diagnostics if needed."
    )
    real_server_instance = None

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
        print("🚀🚀🚀 FletV2App __init__ called 🚀🚀🚀")
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
                    logger.error(
                        "CRITICAL: Real server integration failed - this may indicate compatibility issues"
                    )
                    # Don't fall back to placeholder since ServerBridge now requires real server
                    raise test_error
            else:
                # No real server available - check for GUI-only mode
                gui_only_mode = os.environ.get('FLET_GUI_ONLY_MODE', '0') == '1'
                if gui_only_mode:
                    logger.warning("⚠️ Starting in GUI-only mode without server bridge")
                    logger.warning("GUI will be functional but data operations will show empty states")
                    self.server_bridge = None
                    bridge_type = "GUI-Only Mode (No Server)"
                    real_server_available = False
                else:
                    logger.error("❌ No real server available - ServerBridge requires real server instance")
                    logger.error(
                        "Set FLET_GUI_ONLY_MODE=1 to start GUI without server, or provide a real "
                        "server instance"
                    )
                    raise RuntimeError(
                        "ServerBridge requires real server instance. Use FLET_GUI_ONLY_MODE=1 for "
                        "GUI-only mode."
                    )
        except Exception as bridge_ex:
            logger.error(f"❌ Server bridge initialization failed: {bridge_ex}")
            logger.error("Application cannot continue without properly configured server bridge")
            raise bridge_ex

        logger.info(f"Final server bridge configuration: {bridge_type}")
        logger.info(f"Real server available: {real_server_available}")

        # Initialize state manager for reactive UI updates - after server bridge is ready
        self._initialize_state_manager()
        self._profile_mark('state_manager:initialized')

        # Comment 12: Track current view dispose function for proper StateManager cleanup
        self._current_view_dispose: Callable[[], None] | None = None
        self._current_view_name: str | None = None

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

        # Add dashboard loading management flags
        self._dashboard_loading = False
        self._dashboard_loaded = False

        # Dashboard will be loaded after page connection to ensure AnimatedSwitcher is attached
        logger.info("Dashboard will be loaded after page connection is established")

        # If integrated GUI embedding is disabled (browser-only mode), some environments may not
        # trigger page.on_connect before the process exits. Proactively load the dashboard to
        # replace the placeholder immediately in that mode.
        proactive_disabled = os.environ.get('FLET_DISABLE_PROACTIVE_LOAD') == '1'
        if os.environ.get('CYBERBACKUP_DISABLE_INTEGRATED_GUI') == '1' and not proactive_disabled:
            try:
                logger.info("Integrated GUI disabled - proactively loading dashboard view immediately")
                print("🚀🚀🚀 MAIN APP: LOADING DASHBOARD PROACTIVELY 🚀🚀🚀")
                async def _proactive_load_dashboard() -> None:
                    try:
                        await asyncio.sleep(0.1)
                        if not self._dashboard_loading and not self._dashboard_loaded:
                            self._dashboard_loading = True
                            self._load_view("dashboard", force_reload=False)
                            self._dashboard_loaded = True
                            print("🚀🚀🚀 MAIN APP: DASHBOARD LOAD CALLED 🚀🚀🚀")
                    except Exception as immediate_err:
                        logger.error(f"Immediate dashboard load failed in proactive task: {immediate_err}")
                        print(f"🚀🚀🚀 MAIN APP: DASHBOARD LOAD FAILED: {immediate_err} 🚀🚀🚀")
                    finally:
                        self._dashboard_loading = False

                # Run the async task
                self.page.run_task(_proactive_load_dashboard)
            except Exception as e:
                logger.error(f"Proactive dashboard loading failed: {e}")

        # Post-update adjustments handled in _post_content_update

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
        logger.info(f"🔄 Starting view loading for: {view_name}")

        # Comment 12: Dispose of current view before loading new one
        self._dispose_current_view(view_name)

        # Get view configuration
        module_name, function_name, actual_view_name = self._get_view_config(view_name)
        logger.info(f"📦 View config - module: {module_name}, function: {function_name}")

        # Dynamic import and view creation
        try:
            logger.debug(f"Attempting dynamic import for view module '{module_name}'")
            module = __import__(module_name, fromlist=[function_name])
            logger.info(f"✅ Successfully imported module: {module_name}")

            if not hasattr(module, function_name):
                raise AttributeError(f"Module '{module_name}' missing '{function_name}'")
            view_function = getattr(module, function_name)
            logger.info(f"✅ Successfully got view function: {function_name}")

            content, dispose_func = self._create_enhanced_view(view_function, actual_view_name)
            logger.info(f"✅ Successfully created view content, type: {type(content)}")
        except Exception as e:
            logger.error(f"❌ Error during view creation for {view_name}: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Special handling: if dashboard fails, attempt stub
            if view_name != "dashboard":
                raise
            try:
                logger.warning("Attempting fallback stub dashboard due to failure")
                from views.dashboard_stub import create_dashboard_stub  # type: ignore[import-not-found]
                stub_content = create_dashboard_stub(self.page)
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
        animated_switcher = self.content_area.content
        return self._update_content_area(animated_switcher, content, view_name)

    def _update_content_area(self, animated_switcher, content, view_name: str) -> bool:
        """Safely update the content area with simplified view loading"""
        # Store reference for diagnostics that need to inspect attachment state later
        self._animated_switcher = animated_switcher
        try:
            # Unique and stable key for AnimatedSwitcher
            content.key = f"{view_name}_view_{int(time.time() * 1000)}"

            # Single, atomic content update
            if isinstance(animated_switcher, ft.AnimatedSwitcher):
                animated_switcher.content = content
                animated_switcher.transition = ft.AnimatedSwitcherTransition.FADE
                animated_switcher.update()

            # Post-update visibility and subscription management
            self._post_content_update(content, view_name)

            logger.info(f"Successfully updated content area with {view_name}")
            return True
        except Exception as e:
            logger.error(f"Content area update failed for {view_name}: {e}")
            return False
        finally:
            self._loading_view = False

    def _post_content_update(self, content: Any, view_name: str) -> None:
        """Handle visibility and subscription setup after content update."""
        if content is None:
            return

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
                                pass

                    if depth >= max_depth:
                        return

                    try:
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
                    except Exception:
                        pass

                _force_visible_recursive(content, 0, 10)

                try:
                    if hasattr(self, 'page') and self.page is not None:
                        with contextlib.suppress(Exception):
                            self.page.update()
                except Exception:
                    pass

                logger.info('[DASH_FIX] Forced nested dashboard controls visible (aggressive)')
            except Exception as vis_err:
                logger.debug(f"Failed forcing dashboard opacity: {vis_err}")

        # Schedule subscription setup once control is attached to the page
        setup_cb = getattr(content, '_setup_subscriptions', None)
        if not callable(setup_cb):
            logger.debug(
                f"Skipping subscription setup for {view_name}: _setup_subscriptions is not callable "
                f"(type={type(setup_cb).__name__})"
            )
            return

        try:
            if hasattr(self.page, 'run_task'):
                async def _wait_and_setup() -> None:
                    try:
                        timeout = 2.0
                        interval = 0.05
                        waited = 0.0
                        attached = False
                        while waited < timeout:
                            try:
                                if hasattr(content, 'page') and content.page:
                                    attached = True
                                    break

                                if hasattr(self, 'content_area') and self.content_area:
                                    container = self.content_area
                                    if hasattr(container, 'content') and container.content:
                                        inner = container.content
                                        if hasattr(inner, 'page') and inner.page:
                                            attached = True
                                            break

                                animated = getattr(self, '_animated_switcher', None)
                                if animated and hasattr(animated, 'page') and animated.page:
                                    attached = True
                                    break
                            except Exception:
                                pass
                            await asyncio.sleep(interval)
                            waited += interval

                        if not attached:
                            logger.warning(
                                "Setup subscriptions: content not attached after %ss, proceeding anyway",
                                timeout,
                            )

                        try:
                            if asyncio.iscoroutinefunction(setup_cb):
                                await setup_cb()
                            else:
                                result = setup_cb()
                                if asyncio.iscoroutine(result):
                                    await result
                            logger.debug(f"Set up subscriptions for {view_name} view")
                            logger.warning(
                                "[CONTENT_DIAG] _setup_subscriptions executed for %s (waiter)",
                                view_name,
                            )
                        except Exception as setup_error:
                            logger.warning(f"Subscription setup failed in waiter: {setup_error}")
                    except Exception as outer_error:
                        logger.warning(f"Subscription waiter failed: {outer_error}")

                self.page.run_task(_wait_and_setup)
        except Exception as sub_error:
            logger.warning(f"Failed to schedule subscription setup for {view_name}: {sub_error}")

    def _extract_content_and_dispose(
        self,
        result_t: tuple[Any, ...],
    ) -> tuple[Any, Callable[[], None] | None]:
        """Extract content and dispose function from result tuple."""
        content = result_t[0]
        dispose_func = cast(Callable[[], None] | None, result_t[1])
        return content, dispose_func

    def _diagnose_dashboard_content(self, content: Any) -> None:
        """Centralized dashboard diagnostics (removed duplication)."""
        try:
            ctrl = content
            desc = type(ctrl).__name__
            has_controls = hasattr(ctrl, 'controls') and bool(ctrl.controls)
            if hasattr(ctrl, 'controls'):
                children_count = len(ctrl.controls)
            elif hasattr(ctrl, 'content') and ctrl.content:
                children_count = 1
            else:
                children_count = 0
            logger.warning(
                "[DASH_DBG] dashboard content type=%s has_controls=%s children_count=%s",
                desc,
                has_controls,
                children_count,
            )
        except Exception as _dbg_err:
            logger.warning(f"[DASH_DBG] inspection failed: {_dbg_err}")

    def _process_view_result_tuple(
        self,
        result_t: tuple[Any, ...],
        view_name: str,
    ) -> tuple[Any, Callable[[], None] | None]:
        """Process view result tuple (deduplicated)."""
        length = len(result_t)
        if length not in (2, 3):
            logger.error(f"Unexpected tuple length {length} for {view_name}")
            return self._create_error_view(f"Invalid tuple length for {view_name}"), lambda: None

        content, dispose_func = self._extract_content_and_dispose(result_t)
        if length == 3:
            setup_func = cast(Callable[..., Any], result_t[2])
            content._setup_subscriptions = setup_func  # type: ignore[attr-defined]

        if view_name == 'dashboard':
            self._diagnose_dashboard_content(content)

        logger.debug("Successfully processed %s-tuple for %s", length, view_name)
        return content, dispose_func

    def _create_enhanced_view(
        self, view_function: Callable[..., Any], view_name: str
    ) -> tuple[Any, Callable[[], None] | None]:
        """Create view with state manager integration - now required for all views."""
        try:
            # Lightweight per-view cache to avoid reconstructing heavy views (dashboard) repeatedly
            # Only enabled for views explicitly marked safe for reuse (currently: dashboard) to
            # prevent stale state issues on views requiring fresh data bindings.
            if not hasattr(self, "_view_cache"):
                # view_name -> (content, dispose_func)
                self._view_cache = {}
            cache_enabled = (view_name == "dashboard")
            if cache_enabled and view_name in self._view_cache:
                cached_content, cached_dispose = self._view_cache[view_name]
                with contextlib.suppress(Exception):
                    logger.warning(
                        "[VIEW_CACHE] Reusing cached %s view (no reconstruction) type=%s disposed=%s",
                        view_name, type(cached_content).__name__, cached_dispose is None
                    )
                    if os.environ.get('FLET_DASHBOARD_CONTENT_DEBUG') == '1' and view_name == 'dashboard':
                        # Lightweight cache integrity check
                        has_children = hasattr(cached_content, 'controls') and bool(cached_content.controls)
                        logger.warning(
                            "[VIEW_CACHE] Cached dashboard control integrity: has_children=%s opacity=%s",
                            has_children,
                            getattr(cached_content, 'opacity', None),
                        )
                return cached_content, cached_dispose
            # All views now require state_manager as per Phase 2 refactor
            result = view_function(self.server_bridge, self.page, self.state_manager)
            logger.debug(f"View function returned: {type(result)} for {view_name}")

            # Comment 12: Check if view returned dispose function and subscription setup (new pattern)
            if isinstance(result, tuple):
                result_t = cast(tuple[Any, ...], result)
                logger.debug(f"Tuple length: {len(result_t)} for {view_name}")
                return self._process_view_result_tuple(result_t, view_name)

            logger.debug(f"Non-tuple result for {view_name}, creating auto-dispose")
            # Backward compatibility: create auto-dispose function
            # Track subscriptions for automatic cleanup
            dispose_func = self._create_auto_dispose_for_view(view_name)
            # Store in cache if eligible
            if cache_enabled:
                with contextlib.suppress(Exception):
                    self._view_cache[view_name] = (result, dispose_func)
                    logger.debug(
                        "[VIEW_CACHE] Stored %s view in cache (type=%s)",
                        view_name,
                        type(result).__name__,
                    )
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
                self.navigate_to("dashboard")
            except Exception as nav_error:
                logger.error(f"Navigation error: {nav_error}")

        return ft.Column([
            ft.Text(error_message, size=16, color=ft.Colors.RED),
            ft.ElevatedButton("Return to Dashboard", on_click=_on_return_button_click)
        ], spacing=10)

    def _load_view(self, view_name: str, force_reload: bool = False) -> bool:
        """Load view with simplified and thread-safe mechanism."""
        # Prevent multiple simultaneous view loads
        if self._loading_view:
            logger.warning(f"View load in progress. Skipping '{view_name}' request.")
            return False

        # Check if view reload is necessary
        if not force_reload and view_name == getattr(self, '_current_view_name', None):
            logger.debug(f"Skipping reload for view '{view_name}' (already current)")
            return True

        try:
            self._loading_view = True
            result = self._perform_view_loading(view_name)
            return result
        except Exception as e:
            logger.error(f"Failed to load view {view_name}: {e}")
            return False
        finally:
            self._loading_view = False


async def main(page: ft.Page, backup_server) -> None:
    """Main Flet application entry point."""
    app = FletV2App(page, backup_server)
    await app.initialize()


def run_application():
    """Initialize and run the FletV2 application."""
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

    # Use browser mode for faster development
    print("FletV2 is starting in browser mode for faster development")

    # Launch async Flet app in browser mode with real server
    async def main_with_server(page: ft.Page) -> None:
        await main(page, backup_server)

    # Dynamically resolve a free port starting from preferred 8550 with robust IPv4 + IPv6 checks
    def _is_port_free(port: int) -> bool:
        import socket as _sock
        sockets: list[tuple[_sock.socket, str]] = []
        try:
            for family in (getattr(_sock, 'AF_INET', None), getattr(_sock, 'AF_INET6', None)):
                if family is None:
                    continue
                try:
                    s = _sock.socket(family, _sock.SOCK_STREAM)
                    s.setsockopt(_sock.SOL_SOCKET, _sock.SO_REUSEADDR, 1)
                    bind_addr = ('::', port, 0, 0) if family == _sock.AF_INET6 else ('0.0.0.0', port)
                    s.bind(bind_addr)
                    sockets.append((s, 'ipv6' if family == _sock.AF_INET6 else 'ipv4'))
                except OSError:
                    # Any bind failure indicates port in use
                    return False
            return True
        finally:
            for s, _ in sockets:
                with contextlib.suppress(Exception):
                    s.close()

    _preferred_port = 8550
    _port_candidate = None
    for candidate in range(_preferred_port, _preferred_port + 25):
        if _is_port_free(candidate):
            _port_candidate = candidate
            break
    if _port_candidate is None:
        print("Warning: Could not find free port in preferred range; letting OS choose")
        _port_candidate = 0  # OS-assigned ephemeral port
    elif _port_candidate != _preferred_port:
        print(f"Info: Preferred port {_preferred_port} in use; using {_port_candidate} instead")

    try:
        asyncio.run(
            ft.app_async(
                target=main_with_server,
                view=ft.AppView.WEB_BROWSER,
                port=_port_candidate,
            )
        )  # type: ignore[attr-defined]
    except OSError as bind_err:  # Port race condition fallback
        print(f"Port {_port_candidate} bind failed ({bind_err}); retrying with ephemeral port")
        asyncio.run(
            ft.app_async(
                target=main_with_server,
                view=ft.AppView.WEB_BROWSER,
                port=0,
            )
        )  # type: ignore[attr-defined]
    except ImportError as imp_err:
        # FastAPI / pydantic_core compatibility issue (often on bleeding-edge Python versions)
        err_text = str(imp_err)
        if 'pydantic_core' in err_text or 'fastapi' in err_text:
            print("Browser mode failed due to FastAPI/Pydantic import issue; falling back to native app view")
            try:
                asyncio.run(
                    ft.app_async(
                        target=main_with_server,
                        view=ft.AppView.FLET_APP,
                        port=_port_candidate,
                    )
                )  # type: ignore[attr-defined]
            except Exception as fallback_err:
                import traceback as _tb
                print("Native app view fallback failed:", fallback_err)
                print(_tb.format_exc())
                print("Attempting minimal fallback view (no specific AppView)")
                try:
                    asyncio.run(
                        ft.app_async(
                            target=main_with_server,
                            port=_port_candidate,
                        )
                    )  # type: ignore[attr-defined]
                except Exception as minimal_err:
                    print("Minimal fallback also failed, aborting startup:", minimal_err)
                    print(_tb.format_exc())
                    raise
        else:
            # If ImportError wasn't the known FastAPI/pydantic issue, re-raise to surface original problem
            raise


if __name__ == "__main__":
    run_application()
