#!/usr/bin/env python3
"""
Test script to verify GUI integration fixes
"""

import sys
import os
import time
import pytest

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

missing_gui = None
try:
    from python_server.server_gui.ServerGUI import ServerGUI  # type: ignore
except Exception as e:  # pragma: no cover - environment dependent legacy GUI
    missing_gui = str(e)


@pytest.mark.skipif(missing_gui is not None, reason="ServerGUI legacy module not available in trim environment")
def test_server_gui_integration_smoke():
    class MockServer:
        def __init__(self):
            self.running = True
            self.host = "127.0.0.1"
            self.port = 1256
            self.clients = {}
            self.clients_by_name = {}
            self.network_server = None
            self.file_transfer_manager = None
            self.db_manager = self.MockDBManager()

        class MockDBManager:
            def get_all_clients(self):
                return [f"client_{i}" for i in range(5)]

        def start(self):
            self.running = True

        def stop(self):
            self.running = False

        def apply_settings(self, settings):
            pass

    gui = ServerGUI(MockServer())
    gui.update_server_status(True, "127.0.0.1", 1256)
    gui.update_client_stats({'connected': 3, 'total': 5, 'active_transfers': 1})
    gui.update_transfer_stats({'bytes_transferred': 1024000, 'rate_kbps': 150.5, 'last_activity': 'test_file.txt'})
    gui.sync_current_server_state()
    # No exception = pass
