#!/usr/bin/env python3
"""
Unit tests for the server bridge modules.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Set debug mode to enable mock data
os.environ['FLET_V2_DEBUG'] = 'true'

# Add the FletV2 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.server_bridge import ServerBridge, create_server_bridge


class TestSimpleServerBridge(unittest.TestCase):
    """Test cases for the simple bridge interface (now unified ServerBridge)."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        with patch('utils.server_bridge.logger'):
            self.bridge = ServerBridge()

    def test_initialization(self):
        """Test that the bridge initializes correctly."""
        self.assertIsInstance(self.bridge, ServerBridge)
        self.assertTrue(self.bridge.is_connected())

    def test_get_clients(self):
        """Test getting client data."""
        clients = self.bridge.get_clients()
        self.assertIsInstance(clients, list)
        self.assertGreater(len(clients), 0)

        # Check structure of first client
        if clients:
            client = clients[0]  # clients is a list, accessing first element
            required_keys = ['client_id', 'address', 'status', 'connected_at', 'last_activity']
            for key in required_keys:
                self.assertIn(key, client)

    def test_get_files(self):
        """Test getting file data."""
        files = self.bridge.get_files()
        self.assertIsInstance(files, list)

        # Check structure of first file
        if files:
            file_data = files[0]  # files is a list, accessing first element
            required_keys = ['file_id', 'filename', 'size', 'uploaded_at', 'client_id']
            for key in required_keys:
                self.assertIn(key, file_data)

    def test_get_database_info(self):
        """Test getting database information."""
        db_info = self.bridge.get_database_info()
        self.assertIsInstance(db_info, dict)

        required_keys = ['status', 'tables', 'records', 'size']
        for key in required_keys:
            self.assertIn(key, db_info)

    def test_disconnect_client(self):
        """Test disconnecting a client."""
        result = self.bridge.disconnect_client("client_001")
        self.assertTrue(result)

    def test_delete_client(self):
        """Test deleting a client."""
        result = self.bridge.delete_client("client_001")
        self.assertTrue(result)

    def test_is_connected(self):
        """Test checking connection status."""
        result = self.bridge.is_connected()
        self.assertTrue(result)

    def test_create_simple_server_bridge_factory(self):
        """Test the factory function."""
        with patch('utils.simple_server_bridge.logger'):
            bridge = create_server_bridge()
            self.assertIsInstance(bridge, ServerBridge)


if __name__ == '__main__':
    unittest.main()