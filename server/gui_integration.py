# gui_integration.py
# GUI Integration Module
# Extracted from monolithic server.py for better modularity

import threading
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GUIManager:
    """
    Manages GUI integration for the backup server.
    Handles GUI initialization, updates, and cleanup with graceful degradation.
    """
    
    def __init__(self, server_instance=None):
        """Initialize the GUI manager."""
        self.server_instance = server_instance
        self.gui = None
        self.gui_ready = threading.Event() # Event to signal GUI is fully initialized
        self.gui_lock = threading.Lock()
        
        # Try to import GUI components
        try:
            from ServerGUI import ServerGUI
            self.ServerGUI = ServerGUI
            self.gui_available = True
            logger.info("GUI components available for initialization")
        except ImportError as e:
            logger.info(f"GUI components not available: {e}")
            self.ServerGUI = None
            self.gui_available = False
    
    def initialize_gui(self) -> bool:
        """
        Initialize the GUI in a separate thread to avoid blocking server startup.
        
        Returns:
            True if GUI initialization started successfully, False otherwise
        """
        if not self.gui_available:
            logger.info("GUI components not available, running in console mode")
            return False
        
        def init_gui():
            try:
                with self.gui_lock:
                    # Pass the server_instance to the GUI
                    self.gui = self.ServerGUI(server_instance=self.server_instance)
                    gui_initialized = self.gui.initialize()
                
                if gui_initialized:
                    logger.info("Server GUI initialized successfully")
                    self.gui_ready.set() # Signal that the GUI is ready for updates
                else:
                    logger.warning("Server GUI initialization failed, continuing without GUI")
                    with self.gui_lock:
                        self.gui = None
                    self.gui_ready.set() # Signal completion even if GUI failed
            except Exception as e:
                logger.warning(f"Failed to initialize server GUI: {e}, continuing without GUI")
                with self.gui_lock:
                    self.gui = None
                self.gui_ready.set() # Signal completion even if GUI failed with exception
        
        try:
            gui_thread = threading.Thread(target=init_gui, daemon=True, name="GUIInitializer")
            gui_thread.start()
            logger.info("GUI initialization started in background")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to start GUI thread: {e}, continuing without GUI")
            return False
    
    def is_gui_ready(self) -> bool:
        """Check if GUI is fully initialized and ready for interaction."""
        return self.gui_ready.is_set()

    def _execute_gui_action(self, action, *args, **kwargs):
        """A helper to safely execute actions on the GUI thread."""
        if not self.is_gui_ready():
            return False
        with self.gui_lock:
            if self.gui:
                try:
                    action(*args, **kwargs)
                    return True
                except Exception as e:
                    logger.error(f"Failed to execute GUI action: {e}", exc_info=True)
                    return False
        return False

    def update_server_status(self, running: bool, address: str, port: int):
        if self.is_gui_ready():
            self._execute_gui_action(self.gui.update_server_status, running, address, port)

    def update_client_stats(self, stats_data: dict = None):
        if self.is_gui_ready():
            if stats_data is None:
                stats_data = {'connected': 0, 'total': 0, 'active_transfers': 0}
            self._execute_gui_action(self.gui.update_client_stats, stats_data)

    def update_transfer_stats(self, bytes_transferred: int = 0, last_activity: str = ""):
        if self.is_gui_ready():
            self._execute_gui_action(self.gui.update_transfer_stats, bytes_transferred, last_activity)

    def update_maintenance_stats(self, stats: Dict[str, Any]):
        if self.is_gui_ready():
            self._execute_gui_action(self.gui.update_maintenance_stats, stats)

    def show_error(self, error_message: str):
        if self.is_gui_ready():
            self._execute_gui_action(self.gui.show_error, error_message)

    def show_success(self, success_message: str):
        if self.is_gui_ready():
            self._execute_gui_action(self.gui.show_success, success_message)

    def queue_update(self, update_type: str, data: Any):
        """Queue an update for the GUI to process safely."""
        if not self.is_gui_ready():
            return
        
        with self.gui_lock:
            if self.gui:
                self.gui.update_queue.put((update_type, data))

    def is_gui_running(self) -> bool:
        """Check if the GUI is currently running."""
        if not self.gui:
            return False
        # Check if the GUI thread is alive, or if the root window exists
        gui_thread_alive = self.gui.gui_thread and self.gui.gui_thread.is_alive()
        root_window_exists = self.gui.root and self.gui.root.winfo_exists()
        return gui_thread_alive or root_window_exists

    def shutdown(self):
        """Shutdown the GUI gracefully."""
        if not self.is_gui_ready():
            logger.info("GUI not ready or not enabled, no shutdown needed")
            return

        logger.info("Shutting down GUI...")
        self._execute_gui_action(self.gui.shutdown)
        with self.gui_lock:
            self.gui = None
        self.gui_ready.clear()
        logger.info("GUI shutdown completed successfully")