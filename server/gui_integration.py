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
    
    def __init__(self):
        """Initialize the GUI manager."""
        self.gui = None
        self.gui_enabled = False
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
        
        try:
            # Start GUI initialization in a separate thread
            def init_gui():
                try:
                    with self.gui_lock:
                        self.gui = self.ServerGUI()
                        self.gui_enabled = self.gui.initialize()
                        
                    if self.gui_enabled:
                        logger.info("Server GUI initialized successfully")
                        self.update_gui_status("Server Started", "Backup server is running and ready")
                    else:
                        logger.warning("Server GUI initialization failed, continuing without GUI")
                        
                except Exception as e:
                    logger.warning(f"Failed to initialize server GUI: {e}, continuing without GUI")
                    with self.gui_lock:
                        self.gui = None
                        self.gui_enabled = False
            
            # Start GUI in background thread
            gui_thread = threading.Thread(target=init_gui, daemon=True, name="GUIInitializer")
            gui_thread.start()
            
            # Don't wait for GUI - let server start immediately
            logger.info("GUI initialization started in background")
            return True
            
        except Exception as e:
            logger.warning(f"Failed to start GUI thread: {e}, continuing without GUI")
            return False
    
    def is_gui_enabled(self) -> bool:
        """
        Check if GUI is currently enabled and available.
        
        Returns:
            True if GUI is enabled, False otherwise
        """
        with self.gui_lock:
            return self.gui_enabled and self.gui is not None
    
    def update_gui_status(self, status: str, details: str = "") -> bool:
        """
        Update the GUI with server status information.
        
        Args:
            status: Status message to display
            details: Additional details about the status
            
        Returns:
            True if update succeeded, False otherwise
        """
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'update_status'):
                    self.gui.update_status(status, details)
                    logger.debug(f"GUI status updated: {status} - {details}")
                    return True
                else:
                    logger.debug("GUI update_status method not available")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update GUI status: {e}")
            return False
    
    def update_gui_client_count(self, count: int) -> bool:
        """
        Update the GUI with current client count.
        
        Args:
            count: Number of connected clients
            
        Returns:
            True if update succeeded, False otherwise
        """
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'update_client_count'):
                    self.gui.update_client_count(count)
                    logger.debug(f"GUI client count updated: {count}")
                    return True
                else:
                    logger.debug("GUI update_client_count method not available")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update GUI client count: {e}")
            return False
    
    def update_gui_transfer_stats(self, stats: Dict[str, Any]) -> bool:
        """
        Update the GUI with file transfer statistics.
        
        Args:
            stats: Dictionary containing transfer statistics
            
        Returns:
            True if update succeeded, False otherwise
        """
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'update_transfer_stats'):
                    self.gui.update_transfer_stats(stats)
                    logger.debug(f"GUI transfer stats updated")
                    return True
                else:
                    logger.debug("GUI update_transfer_stats method not available")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update GUI transfer stats: {e}")
            return False
    
    def show_gui_notification(self, title: str, message: str, notification_type: str = "info") -> bool:
        """
        Show a notification in the GUI.
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification (info, warning, error, success)
            
        Returns:
            True if notification was shown, False otherwise
        """
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'show_notification'):
                    self.gui.show_notification(title, message, notification_type)
                    logger.debug(f"GUI notification shown: {title} - {message}")
                    return True
                else:
                    logger.debug("GUI show_notification method not available")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to show GUI notification: {e}")
            return False
    
    def update_gui_error(self, error_message: str) -> bool:
        """
        Update the GUI with error information.
        
        Args:
            error_message: Error message to display
            
        Returns:
            True if update succeeded, False otherwise
        """
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'update_error'):
                    self.gui.update_error(error_message)
                    logger.debug(f"GUI error updated: {error_message}")
                    return True
                else:
                    logger.debug("GUI update_error method not available")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update GUI error: {e}")
            return False
    
    def update_gui_log(self, log_entry: str, log_level: str = "info") -> bool:
        """
        Add a log entry to the GUI.
        
        Args:
            log_entry: Log message to add
            log_level: Level of the log entry (debug, info, warning, error)
            
        Returns:
            True if log was added, False otherwise
        """
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'add_log_entry'):
                    self.gui.add_log_entry(log_entry, log_level)
                    logger.debug(f"GUI log entry added: {log_entry}")
                    return True
                else:
                    logger.debug("GUI add_log_entry method not available")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to add GUI log entry: {e}")
            return False
    
    def update_gui_server_info(self, port: int, client_count: int, uptime: int) -> bool:
        """
        Update the GUI with comprehensive server information.
        
        Args:
            port: Server port number
            client_count: Number of connected clients
            uptime: Server uptime in seconds
            
        Returns:
            True if update succeeded, False otherwise
        """
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'update_server_info'):
                    self.gui.update_server_info(port, client_count, uptime)
                    logger.debug(f"GUI server info updated: port={port}, clients={client_count}, uptime={uptime}")
                    return True
                else:
                    logger.debug("GUI update_server_info method not available")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update GUI server info: {e}")
            return False
    
    def refresh_gui(self) -> bool:
        """
        Refresh the GUI display.
        
        Returns:
            True if refresh succeeded, False otherwise
        """
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'refresh'):
                    self.gui.refresh()
                    logger.debug("GUI refreshed")
                    return True
                else:
                    logger.debug("GUI refresh method not available")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to refresh GUI: {e}")
            return False
    
    def shutdown_gui(self):
        """
        Shutdown the GUI gracefully.
        """
        if not self.is_gui_enabled():
            logger.info("GUI not enabled, no cleanup needed")
            return
        
        try:
            with self.gui_lock:
                if self.gui:
                    logger.info("Shutting down GUI...")
                    
                    # Update GUI with shutdown status
                    if hasattr(self.gui, 'update_status'):
                        self.gui.update_status("Server Shutting Down", "Backup server is stopping...")
                    
                    # Call GUI shutdown method if available
                    if hasattr(self.gui, 'shutdown'):
                        self.gui.shutdown()
                    
                    # Clean up GUI reference
                    self.gui = None
                    self.gui_enabled = False
                    
                    logger.info("GUI shutdown completed successfully")
                else:
                    logger.debug("No GUI instance to shutdown")
                    
        except Exception as e:
            logger.error(f"Error during GUI shutdown: {e}")
            # Ensure cleanup even if shutdown fails
            with self.gui_lock:
                self.gui = None
                self.gui_enabled = False
    
    def get_gui_status(self) -> Dict[str, Any]:
        """
        Get current GUI status information.
        
        Returns:
            Dictionary containing GUI status information
        """
        with self.gui_lock:
            return {
                'available': self.gui_available,
                'enabled': self.gui_enabled,
                'initialized': self.gui is not None,
                'class_available': self.ServerGUI is not None
            }
    
    def handle_gui_error(self, error: Exception, context: str = ""):
        """
        Handle GUI-related errors with appropriate logging and fallback.
        
        Args:
            error: The exception that occurred
            context: Additional context about when the error occurred
        """
        error_msg = f"GUI error{f' in {context}' if context else ''}: {error}"
        logger.error(error_msg)
        
        # Show notification about GUI error if possible
        self.show_gui_notification(
            "GUI Error", 
            f"GUI operation failed{f' ({context})' if context else ''}", 
            "error"
        )
        
        # Consider disabling GUI if errors are frequent
        # This could be enhanced with error counting and automatic disabling
        
    def update_gui_maintenance_stats(self, stats: Dict[str, Any]) -> bool:
        """
        Update the GUI with maintenance operation statistics.
        
        Args:
            stats: Dictionary containing maintenance statistics
            
        Returns:
            True if update succeeded, False otherwise
        """
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'update_maintenance_stats'):
                    self.gui.update_maintenance_stats(stats)
                    logger.debug("GUI maintenance stats updated")
                    return True
                else:
                    # Fallback to status update if specific method not available
                    if hasattr(self.gui, 'update_status'):
                        status_msg = f"Maintenance: {stats.get('description', 'Completed')}"
                        self.gui.update_status(status_msg, f"Operations: {stats.get('operations', 0)}")
                        return True
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update GUI maintenance stats: {e}")
            return False

    def update_server_status(self, running: bool, address: str, port: int) -> bool:
        """Update the GUI with server status information."""
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'update_server_status'):
                    self.gui.update_server_status(running, address, port)
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update GUI server status: {e}")
            return False

    def update_client_stats(self, connected: int = 0, total: int = 0, active_transfers: int = 0) -> bool:
        """Update the GUI with client statistics."""
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'update_client_stats'):
                    self.gui.update_client_stats(connected, total, active_transfers)
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update GUI client stats: {e}")
            return False

    def force_status_update(self, running: bool, address: str, port: int, active_clients: int, total_clients: int) -> bool:
        """Force a GUI status update with all parameters."""
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'force_status_update'):
                    self.gui.force_status_update(running, address, port, active_clients, total_clients)
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to force GUI status update: {e}")
            return False

    def update_transfer_stats(self, bytes_transferred: int = 0, last_activity: str = "") -> bool:
        """Update the GUI with transfer statistics."""
        if not self.is_gui_enabled():
            return False
        
        try:
            with self.gui_lock:
                if self.gui and hasattr(self.gui, 'update_transfer_stats'):
                    self.gui.update_transfer_stats(bytes_transferred, last_activity)
                    return True
                return False
        except Exception as e:
            logger.error(f"Failed to update GUI transfer stats: {e}")
            return False

    def show_error(self, error_message: str) -> bool:
        """Show an error message in the GUI."""
        return self.update_gui_error(error_message)

    def show_success(self, success_message: str) -> bool:
        """Show a success message in the GUI."""
        return self.show_gui_notification("Success", success_message, "success")