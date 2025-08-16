# gui_integration.py
# pyright: reportMissingImports=false, reportUnknownMemberType=false, reportOptionalMemberAccess=false
# GUI Integration Module
# Extracted from monolithic server.py for better modularity

import os
import sys
import threading
import logging
from typing import Optional, Dict, Any, TYPE_CHECKING, Callable, Protocol

# UTF-8 support for international characters and emojis
try:
    import Shared.utils.utf8_solution  # 🚀 UTF-8 support enabled automatically
except ImportError:
    # Fallback for when running from within python_server directory
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    import Shared.utils.utf8_solution  # 🚀 UTF-8 support enabled automatically

if TYPE_CHECKING:
    from python_server.server_gui import ServerGUI

# Use Any-based runtime annotations to keep static analyzer happy without
# introducing heavyweight Protocols that complicate imports.

logger = logging.getLogger(__name__)

class GUIManager:
    """
    Manages GUI integration for the backup server.
    Handles GUI initialization, updates, and cleanup with graceful degradation.
    """
    
    def __init__(self, server_instance: Any = None):
        """Initialize the GUI manager.

        Keeps GUI optional so server can run headless. GUI imports are attempted
        but failures fall back to console-only operation.
        """
        self.server_instance = server_instance

        # Use Any for runtime to avoid circular import/type issues
        self.gui: Optional[Any] = None
        self.gui_ready = threading.Event()  # Event to signal GUI is fully initialized
        self.data_loaded = threading.Event()  # Event to signal that initial data is loaded
        self.gui_lock = threading.Lock()

        # Try to import GUI components
        # Check environment variable to disable GUI
        gui_disabled = os.environ.get('CYBERBACKUP_DISABLE_GUI', '').lower() in ('1', 'true', 'yes')

        if gui_disabled:
            logger.info("GUI disabled via CYBERBACKUP_DISABLE_GUI environment variable")
            self.ServerGUI = None
            self.gui_available = False
            return

        # Attempt imports; leave ServerGUI as None on failure and continue headless
        try:
            from python_server.server_gui import ServerGUI  # type: ignore
            self.ServerGUI = ServerGUI
            self.gui_available = True
            logger.info("GUI components available for initialization")
        except Exception:
            try:
                from server_gui import ServerGUI  # type: ignore
                self.ServerGUI = ServerGUI
                self.gui_available = True
                logger.info("GUI components available for initialization (fallback import)")
            except Exception as e:
                logger.info(f"GUI components not available: {e}")
                self.ServerGUI = None
                self.gui_available = False
    
    def initialize_gui(self) -> bool:
        """
        Initialize the GUI in a separate thread to avoid blocking server startup.

        Returns:
            True if GUI initialization started successfully, False otherwise
        """
        if not self.gui_available or self.ServerGUI is None:
            logger.info("GUI components not available, running in console mode")
            self.gui_ready.set()  # Signal ready immediately for console mode
            return False

        def init_gui():
            try:
                with self.gui_lock:
                    if self.ServerGUI is not None:
                        # type: ignore[call-arg]
                        # runtime assignment: instantiate the GUI class if available
                        self.gui = self.ServerGUI(server_instance=self.server_instance)  # type: ignore
                        logger.info("[GUI] Calling ServerGUI.initialize() (threaded)")
                        # initialize() may not be present on partial mocks; guard at runtime
                        gui_initialized = False
                        try:
                            gui_obj: Any = self.gui  # hint for static analyzers
                            gui_initialized = bool(getattr(gui_obj, 'initialize', lambda: False)())
                        except Exception:
                            gui_initialized = False
                        logger.info(f"[GUI] ServerGUI.initialize() returned {gui_initialized}")
                    else:
                        logger.warning("ServerGUI is None, cannot initialize GUI")
                        gui_initialized = False

                if gui_initialized:
                    logger.info("Server GUI initialized successfully")
                    self.gui_ready.set()
                else:
                    logger.warning("Server GUI initialization failed, continuing without GUI")
                    with self.gui_lock:
                        self.gui = None
                    self.gui_ready.set()
            except Exception as e:
                logger.warning(f"Failed to initialize server GUI: {e}, continuing without GUI")
                with self.gui_lock:
                    self.gui = None
                self.gui_ready.set()

        try:
            logger.info("[GUI] Spawning GUI initializer thread ...")
            gui_thread = threading.Thread(target=init_gui, daemon=True, name="GUIInitializer")
            gui_thread.start()
            logger.info("[GUI] GUI initializer thread started")
            logger.info("GUI initialization started in background")
            return True
        except Exception as e:
            logger.warning(f"Failed to start GUI thread: {e}, continuing without GUI")
            return False
    
    def is_gui_ready(self) -> bool:
        """Check if GUI is fully initialized and ready for interaction."""
        return self.gui_ready.is_set()

    def signal_data_loaded(self):
        """Signal that the initial data from the server has been loaded."""
        self.data_loaded.set()

    def _execute_gui_action(self, action: Callable[..., Any], *args: Any, **kwargs: Any) -> bool:
        """A helper to safely execute actions on the GUI thread."""
        if not self.is_gui_ready():
            return False
        with self.gui_lock:
            if self.gui is not None:
                try:
                    action(*args, **kwargs)
                    return True
                except Exception as e:
                    logger.error(f"Failed to execute GUI action: {e}", exc_info=True)
                    return False
            return False

    def update_server_status(self, running: bool, address: str, port: int):
        if self.is_gui_ready() and self.gui:
            self._execute_gui_action(self.gui.update_server_status, running, address, port)

    def update_client_stats(self, stats_data: Optional[Dict[str, Any]] = None) -> None:
        if self.is_gui_ready() and self.gui:
            self.data_loaded.wait(timeout=5.0)  # Wait for data to be loaded
            if stats_data is None:
                stats_data = {'connected': 0, 'total': 0, 'active_transfers': 0}
            self._execute_gui_action(self.gui.update_client_stats, stats_data)

    def update_transfer_stats(self, bytes_transferred: int = 0, last_activity: str = "") -> None:
        if self.is_gui_ready() and self.gui:
            stats_data = {
                'bytes_transferred': bytes_transferred,
                'last_activity': last_activity
            }
            self._execute_gui_action(self.gui.update_transfer_stats, stats_data)

    def update_maintenance_stats(self, stats: Dict[str, Any]) -> None:
        if self.is_gui_ready() and self.gui:
            self._execute_gui_action(self.gui.update_maintenance_stats, stats)

    def show_error(self, error_message: str) -> None:
        if self.is_gui_ready() and self.gui is not None and hasattr(self.gui, 'show_error'):
            show_error_method = getattr(self.gui, 'show_error', None)
            if callable(show_error_method):
                self._execute_gui_action(show_error_method, error_message)

    def show_success(self, success_message: str) -> None:
        if self.is_gui_ready() and self.gui is not None and hasattr(self.gui, 'show_success'):
            show_success_method = getattr(self.gui, 'show_success', None)
            if callable(show_success_method):
                self._execute_gui_action(show_success_method, success_message)

    def queue_update(self, update_type: str, data: Any) -> None:
        """Queue an update for the GUI to process safely."""
        if not self.is_gui_ready():
            return
        
        with self.gui_lock:
            if self.gui is not None and hasattr(self.gui, 'update_queue') and self.gui.update_queue is not None:
                self.gui.update_queue.put((update_type, data))

    def is_gui_running(self) -> bool:
        """Check if the GUI is currently running."""
        if self.gui is None:
            return False
        # Check if the GUI thread is alive, or if the root window exists
        gui_thread_alive = bool(self.gui.gui_thread and self.gui.gui_thread.is_alive()) if self.gui.gui_thread else False
        root_window_exists = bool(hasattr(self.gui, 'root') and self.gui.root and 
                                 hasattr(self.gui.root, 'winfo_exists') and self.gui.root.winfo_exists())
        return gui_thread_alive or root_window_exists

    def shutdown(self):
        """Shutdown the GUI gracefully."""
        if not self.is_gui_ready():
            logger.info("GUI not ready or not enabled, no shutdown needed")
            return

        logger.info("Shutting down GUI...")
        
        # Check if GUI exists before attempting to call shutdown
        with self.gui_lock:
            if self.gui is not None and hasattr(self.gui, 'shutdown'):
                self._execute_gui_action(self.gui.shutdown)
            else:
                logger.info("GUI object is None or doesn't have shutdown method")
        
        with self.gui_lock:
            self.gui = None
        self.gui_ready.clear()
        logger.info("GUI shutdown completed successfully")