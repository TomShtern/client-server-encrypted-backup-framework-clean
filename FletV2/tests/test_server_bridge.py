#!/usr/bin/env python3
"""
Unit tests for the server bridge modules.
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

try:  # pragma: no cover - only for environment without flet
    import flet  # noqa: F401
except Exception:  # noqa: BLE001
    flet = None  # type: ignore

# Set debug mode to enable mock data
os.environ['FLET_V2_DEBUG'] = 'true'

# Add the FletV2 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.server_bridge import ServerBridge, create_server_bridge  # create_server_bridge retained for backward compat


class TestServerBridgeNoMock(unittest.TestCase):
    """Tests for ServerBridge in no-mock (disconnected) mode."""

    def setUp(self):
        with patch('utils.server_bridge.logger'):
            self.bridge = ServerBridge()  # No real server

    def test_initialization_disconnected(self):
        if flet is None:
            self.skipTest("Skipping test: flet dependency not installed")
        self.assertIsInstance(self.bridge, ServerBridge)
        self.assertFalse(self.bridge.is_connected(), "Bridge without real server should be disconnected")

    def test_get_clients_empty(self):
        self.assertEqual(self.bridge.get_clients(), [], "Expected empty client list without real server")

    def test_get_files_empty(self):
        self.assertEqual(self.bridge.get_files(), [], "Expected empty file list without real server")

    def test_database_info_failure(self):
        getter = getattr(self.bridge, 'get_database_info', None)
        if getter is None:
            self.skipTest("ServerBridge.get_database_info not implemented in this build")
        info = getter()  # type: ignore[call-arg]
        # Without real server expect failure structure
        self.assertIsInstance(info, dict)
        self.assertIn('success', info)
        self.assertFalse(info['success'])

    def test_factory_returns_disconnected(self):
        with patch('utils.server_bridge.logger'):
            bridge = create_server_bridge()  # disconnected bridge
        self.assertFalse(bridge.is_connected(), "Factory without real server should yield disconnected bridge")

    def test_real_server_delegation(self):
        if flet is None:
            self.skipTest("Skipping test: flet dependency not installed")
        mock_real = Mock()
        mock_real.is_connected.return_value = True
        mock_real.get_clients = Mock(return_value=[{'id': '1', 'name': 'Real', 'last_seen': 'now', 'files_count': 0}])
        bridge = ServerBridge(real_server=mock_real)
        self.assertTrue(bridge.is_connected())
        clients = bridge.get_clients()
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]['name'], 'Real')


if __name__ == '__main__':
    unittest.main()
