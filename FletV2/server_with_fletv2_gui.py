#!/usr/bin/env python3
"""
BackupServer with FletV2 GUI Integration

This script demonstrates how FletV2Manager completely replaces the old ServerGUI.
Instead of the BackupServer using GUIManager (tkinter), it now uses FletV2Manager (Flet).

Usage:
    python server_with_fletv2_gui.py

Integration Pattern:
    OLD: BackupServer.__init__() → self.gui_manager = GUIManager(self)
    NEW: BackupServer.__init__() → self.gui_manager = FletV2Manager(self)
"""

import os
import sys
import logging
from pathlib import Path

# Set up environment for proper imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(parent_dir))

# Essential UTF-8 support
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import UTF-8 solution if available
try:
    import Shared.utils.utf8_solution as _
except ImportError:
    pass

# Import the BackupServer
try:
    from python_server.server.server import BackupServer
    BACKUP_SERVER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import BackupServer: {e}")
    print("Running with mock server for demonstration")
    BACKUP_SERVER_AVAILABLE = False
    BackupServer = None

# Import our FletV2Manager
from fletv2_gui_manager import FletV2Manager, is_gui_disabled

class BackupServerWithFletV2:
    """
    BackupServer with FletV2 GUI integration.

    This class demonstrates how to integrate FletV2Manager into BackupServer
    to completely replace the old tkinter ServerGUI.
    """

    def __init__(self, disable_gui=False):
        """Initialize BackupServer with FletV2 GUI."""
        self.logger = logging.getLogger("BackupServerWithFletV2")

        # Initialize the actual BackupServer
        if BACKUP_SERVER_AVAILABLE and BackupServer:
            self.logger.info("Initializing production BackupServer...")
            self.backup_server = BackupServer()

            # CRITICAL: Replace the old GUIManager with FletV2Manager
            if not disable_gui and not is_gui_disabled():
                self.logger.info("Replacing old GUI with FletV2Manager...")

                # Replace the GUI manager
                self.backup_server.gui_manager = FletV2Manager(self.backup_server)

                # Initialize the FletV2 GUI
                if self.backup_server.gui_manager.initialize():
                    self.logger.info("✅ FletV2 GUI successfully replaced old ServerGUI")
                else:
                    self.logger.error("❌ Failed to initialize FletV2 GUI")
            else:
                self.logger.info("GUI disabled - running headless")
                self.backup_server.gui_manager = None

        else:
            self.logger.warning("BackupServer not available - using mock")
            self.backup_server = MockBackupServer()

            # Still create FletV2Manager for demonstration
            if not disable_gui:
                self.backup_server.gui_manager = FletV2Manager(self.backup_server)
                self.backup_server.gui_manager.initialize()

    def start(self):
        """Start the BackupServer with FletV2 GUI."""
        try:
            self.logger.info("Starting BackupServer with FletV2 GUI...")

            # Start the server (this will now use FletV2 as its GUI)
            if hasattr(self.backup_server, 'start'):
                self.backup_server.start()
            else:
                self.logger.info("Mock server - simulating startup")
                self._simulate_server_activity()

        except KeyboardInterrupt:
            self.logger.info("Shutdown requested")
            self.shutdown()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            self.shutdown()

    def shutdown(self):
        """Shutdown server and GUI."""
        try:
            self.logger.info("Shutting down BackupServer and FletV2 GUI...")

            # Shutdown GUI first
            if self.backup_server and self.backup_server.gui_manager:
                self.backup_server.gui_manager.shutdown()

            # Shutdown server
            if hasattr(self.backup_server, 'shutdown'):
                self.backup_server.shutdown()

            self.logger.info("Shutdown complete")

        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")

    def _simulate_server_activity(self):
        """Simulate server activity for demonstration."""
        import time
        import threading

        def update_loop():
            """Simulate real-time updates that the GUI would receive."""
            connected_clients = 0
            bytes_transferred = 0

            while True:
                try:
                    # Simulate changing values
                    connected_clients = (connected_clients + 1) % 10
                    bytes_transferred += 1024

                    # Send updates to GUI (same as real server would)
                    if self.backup_server and self.backup_server.gui_manager:
                        gui = self.backup_server.gui_manager

                        # Update server status
                        gui.update_server_status(
                            running=True,
                            address='localhost',
                            port=1256,
                            uptime=f"{int(time.time()) % 3600:02d}:00:00"
                        )

                        # Update client stats
                        gui.update_client_stats(
                            connected=connected_clients,
                            total_registered=17,  # From real database
                            active_transfers=connected_clients // 2
                        )

                        # Update transfer stats
                        gui.update_transfer_stats(
                            bytes_transferred=bytes_transferred,
                            transfer_rate=1024.0,
                            last_activity="Just now"
                        )

                        # Update maintenance stats
                        gui.update_maintenance_stats(
                            last_cleanup="Today",
                            files_cleaned=5,
                            clients_cleaned=2
                        )

                    time.sleep(2)  # Update every 2 seconds

                except Exception as e:
                    self.logger.error(f"Update loop error: {e}")
                    break

        # Start update thread
        update_thread = threading.Thread(target=update_loop, daemon=True)
        update_thread.start()

        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


class MockBackupServer:
    """Mock BackupServer for demonstration when real server not available."""

    def __init__(self):
        self.gui_manager = None
        self.logger = logging.getLogger("MockBackupServer")

    def start(self):
        self.logger.info("Mock server started")

    def shutdown(self):
        self.logger.info("Mock server shutdown")


def setup_logging():
    """Set up logging for the demonstration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point."""
    setup_logging()
    logger = logging.getLogger("Main")

    logger.info("=" * 60)
    logger.info("BackupServer with FletV2 GUI Integration Demo")
    logger.info("=" * 60)
    logger.info("")
    logger.info("This demonstrates FletV2 completely replacing the old ServerGUI")
    logger.info("Integration pattern: BackupServer.gui_manager = FletV2Manager(server)")
    logger.info("")

    try:
        # Create and start server with FletV2 GUI
        server = BackupServerWithFletV2(disable_gui=False)
        server.start()

    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
    finally:
        logger.info("Application terminated")


if __name__ == "__main__":
    main()