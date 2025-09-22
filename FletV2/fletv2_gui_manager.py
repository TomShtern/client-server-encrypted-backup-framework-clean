#!/usr/bin/env python3
"""
FletV2 GUI Manager - Complete Replacement for ServerGUI

This module provides the FletV2Manager class that replaces the old tkinter-based
ServerGUI integration, providing the exact same functionality but with modern Flet.

Integration Pattern:
    BackupServer.__init__() → self.gui_manager = FletV2Manager(self)
"""

import asyncio
import threading
import queue
import logging
from typing import Optional, Any, Dict
import flet as ft
from pathlib import Path
import sys
import os

# Add current directory to path for local imports
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import FletV2 main application
try:
    from main import FletV2App
except ImportError as e:
    print(f"Error importing FletV2App: {e}")
    FletV2App = None

class FletV2Manager:
    """
    FletV2 GUI Manager - Direct replacement for the old GUIManager.

    This class provides the exact same interface as the old GUIManager but uses
    FletV2 instead of tkinter ServerGUI. It integrates directly with BackupServer
    and provides real-time updates and server control functionality.
    """

    def __init__(self, server_instance):
        """Initialize FletV2Manager with server instance."""
        self.server = server_instance
        self.logger = logging.getLogger("FletV2Manager")

        # Threading and communication
        self.gui_thread = None
        self.update_queue = queue.Queue()
        self.running = False

        # FletV2 app instance
        self.flet_app = None
        self.page = None

        # Real-time data storage (same as old GUI)
        self.server_status = {
            'running': False,
            'address': 'localhost',
            'port': 1256,
            'uptime': '00:00:00'
        }

        self.client_stats = {
            'connected': 0,
            'total_registered': 0,
            'active_transfers': 0
        }

        self.transfer_stats = {
            'bytes_transferred': 0,
            'transfer_rate': 0,
            'last_activity': 'Never'
        }

        self.maintenance_stats = {
            'last_cleanup': 'Never',
            'files_cleaned': 0,
            'clients_cleaned': 0
        }

        self.logger.info("FletV2Manager initialized")

    def initialize(self):
        """Initialize the FletV2 GUI - called by BackupServer."""
        try:
            self.logger.info("FletV2Manager initialized for main thread GUI...")
            self.running = True

            # FletV2Manager now works as a bridge - actual GUI runs in main thread
            # This method just prepares the manager for server integration
            self.logger.info("FletV2Manager ready for main thread integration")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize FletV2Manager: {e}")
            return False

    def _run_flet_gui(self):
        """Run FletV2 application in thread - same pattern as old GUI."""
        try:
            # FletV2 main function with server integration
            async def flet_main(page: ft.Page):
                self.page = page
                page.title = "BackupServer - FletV2 Interface"
                page.window.width = 1200
                page.window.height = 800

                # Create FletV2App with server integration
                if FletV2App:
                    self.flet_app = FletV2App(page, real_server=self.server)
                    page.add(self.flet_app)
                else:
                    # Fallback if FletV2App not available
                    page.add(ft.Text("FletV2 GUI - Server Integration Active"))

                # Start update processing
                self._start_update_processor()

                await page.update_async()

            # Run FletV2 (same as old GUI runs tkinter mainloop)
            ft.app(target=flet_main, view=ft.AppView.FLET_APP)

        except Exception as e:
            self.logger.error(f"FletV2 GUI error: {e}")

    def _start_update_processor(self):
        """Start processing updates from server - same as old GUI."""
        async def process_updates():
            while self.running:
                try:
                    # Process queued updates (same pattern as old GUI)
                    while not self.update_queue.empty():
                        update_type, data = self.update_queue.get_nowait()
                        await self._handle_update(update_type, data)

                    await asyncio.sleep(0.1)  # 100ms update cycle
                except Exception as e:
                    self.logger.error(f"Update processor error: {e}")

        # Start update processor if we have a page
        if self.page:
            self.page.run_task(process_updates)

    async def _handle_update(self, update_type: str, data: Dict[str, Any]):
        """Handle real-time updates from server."""
        try:
            if update_type == 'server_status':
                self.server_status.update(data)
                await self._update_server_status_display()

            elif update_type == 'client_stats':
                self.client_stats.update(data)
                await self._update_client_stats_display()

            elif update_type == 'transfer_stats':
                self.transfer_stats.update(data)
                await self._update_transfer_stats_display()

            elif update_type == 'maintenance_stats':
                self.maintenance_stats.update(data)
                await self._update_maintenance_stats_display()

        except Exception as e:
            self.logger.error(f"Failed to handle update {update_type}: {e}")

    async def _update_server_status_display(self):
        """Update server status in FletV2 interface."""
        if self.flet_app and hasattr(self.flet_app, 'update_server_status'):
            await self.flet_app.update_server_status(self.server_status)

    async def _update_client_stats_display(self):
        """Update client statistics in FletV2 interface."""
        if self.flet_app and hasattr(self.flet_app, 'update_client_stats'):
            await self.flet_app.update_client_stats(self.client_stats)

    async def _update_transfer_stats_display(self):
        """Update transfer statistics in FletV2 interface."""
        if self.flet_app and hasattr(self.flet_app, 'update_transfer_stats'):
            await self.flet_app.update_transfer_stats(self.transfer_stats)

    async def _update_maintenance_stats_display(self):
        """Update maintenance statistics in FletV2 interface."""
        if self.flet_app and hasattr(self.flet_app, 'update_maintenance_stats'):
            await self.flet_app.update_maintenance_stats(self.maintenance_stats)

    # ============================================================================
    # SERVER INTEGRATION METHODS (Same interface as old GUIManager)
    # ============================================================================

    def queue_update(self, update_type: str, data: Dict[str, Any]):
        """Queue an update for the GUI - same method as old GUIManager."""
        try:
            self.update_queue.put((update_type, data))
        except Exception as e:
            self.logger.error(f"Failed to queue update: {e}")

    def update_server_status(self, running: bool, address: str, port: int, uptime: str):
        """Update server status - same method as old GUIManager."""
        self.queue_update('server_status', {
            'running': running,
            'address': address,
            'port': port,
            'uptime': uptime
        })

    def update_client_stats(self, connected: int, total_registered: int, active_transfers: int):
        """Update client statistics - same method as old GUIManager."""
        self.queue_update('client_stats', {
            'connected': connected,
            'total_registered': total_registered,
            'active_transfers': active_transfers
        })

    def update_transfer_stats(self, bytes_transferred: int, transfer_rate: float, last_activity: str):
        """Update transfer statistics - same method as old GUIManager."""
        self.queue_update('transfer_stats', {
            'bytes_transferred': bytes_transferred,
            'transfer_rate': transfer_rate,
            'last_activity': last_activity
        })

    def update_maintenance_stats(self, last_cleanup: str, files_cleaned: int, clients_cleaned: int):
        """Update maintenance statistics - same method as old GUIManager."""
        self.queue_update('maintenance_stats', {
            'last_cleanup': last_cleanup,
            'files_cleaned': files_cleaned,
            'clients_cleaned': clients_cleaned
        })

    def get_server_updates(self):
        """Get all pending updates for the GUI - called from main thread."""
        updates = []
        try:
            while not self.update_queue.empty():
                updates.append(self.update_queue.get_nowait())
        except queue.Empty:
            pass
        return updates

    def get_current_state(self):
        """Get current server state - called from main thread."""
        return {
            'server_status': self.server_status.copy(),
            'client_stats': self.client_stats.copy(),
            'transfer_stats': self.transfer_stats.copy(),
            'maintenance_stats': self.maintenance_stats.copy()
        }

    def shutdown(self):
        """Shutdown FletV2 GUI - same method as old GUIManager."""
        try:
            self.logger.info("Shutting down FletV2Manager...")
            self.running = False

            # Clear update queue
            while not self.update_queue.empty():
                try:
                    self.update_queue.get_nowait()
                except queue.Empty:
                    break

            self.logger.info("FletV2Manager shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during FletV2Manager shutdown: {e}")

    # ============================================================================
    # SERVER CONTROL METHODS (For FletV2 to control server)
    # ============================================================================

    def start_server(self):
        """Start the server - called from FletV2 controls."""
        if self.server and hasattr(self.server, 'start'):
            threading.Thread(target=self.server.start, daemon=True).start()

    def stop_server(self):
        """Stop the server - called from FletV2 controls."""
        if self.server and hasattr(self.server, 'stop'):
            threading.Thread(target=self.server.stop, daemon=True).start()

    def restart_server(self):
        """Restart the server - called from FletV2 controls."""
        def restart():
            self.stop_server()
            import time
            time.sleep(2)
            self.start_server()

        threading.Thread(target=restart, daemon=True).start()

    def backup_database(self):
        """Backup database - called from FletV2 controls."""
        if self.server and hasattr(self.server, 'backup_database'):
            threading.Thread(target=self.server.backup_database, daemon=True).start()

    def save_settings(self, settings: Dict[str, Any]):
        """Save server settings - called from FletV2 controls."""
        if self.server and hasattr(self.server, 'save_settings'):
            self.server.save_settings(settings)


# ============================================================================
# INTEGRATION HELPER FUNCTIONS
# ============================================================================

def create_fletv2_manager(server_instance):
    """Create FletV2Manager instance - replacement for GUIManager creation."""
    return FletV2Manager(server_instance)

def is_gui_disabled():
    """Check if GUI should be disabled - same logic as old GUI."""
    return os.environ.get('CYBERBACKUP_DISABLE_GUI', '').lower() in ('true', '1', 'yes')