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
            required_keys = ['id', 'name', 'status', 'last_seen']
            for key in required_keys:
                self.assertIn(key, client)

    def test_get_files(self):
        """Test getting file data."""
        files = self.bridge.get_files()
        self.assertIsInstance(files, list)

        # Check structure of first file
        if files:
            file_data = files[0]  # files is a list, accessing first element
            required_keys = ['id', 'name', 'size', 'client_id']
            for key in required_keys:
                self.assertIn(key, file_data)

    def test_get_database_info(self):
        """Test getting database information."""
        db_info_result = self.bridge.get_database_info()
        self.assertIsInstance(db_info_result, dict)
        
        # Check that it has the expected structure
        self.assertIn('success', db_info_result)
        self.assertIn('data', db_info_result)
        self.assertIn('error', db_info_result)
        
        # Check the data structure
        db_info = db_info_result['data']
        required_keys = ['status', 'tables', 'total_records', 'size']
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
        with patch('utils.server_bridge.logger'):
            bridge = create_server_bridge()
            self.assertIsInstance(bridge, ServerBridge)

    def test_mock_data_disabled_with_real_server(self):
        """Test that mock data is disabled when real server is provided."""
        # Create a mock real server with the required methods
        mock_real_server = Mock()
        mock_real_server.is_connected.return_value = True
        mock_real_server.get_clients = Mock(return_value=[])  # Real server returns list directly
        
        # Create bridge with real server
        bridge_with_real_server = ServerBridge(real_server=mock_real_server)
        
        # Verify that mock database is not used
        self.assertIsNone(bridge_with_real_server._mock_db)
        self.assertFalse(bridge_with_real_server._use_mock_data)
        
        # Test that methods return empty data instead of mock data
        result = bridge_with_real_server.get_all_clients_from_db()
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('data', result)
        self.assertIn('error', result)
        self.assertEqual(len(result['data']), 0)  # Should be empty, not mock data

    def test_mock_data_enabled_without_real_server(self):
        """Test that mock data is enabled when no real server is provided."""
        # Create bridge without real server (mock mode)
        bridge_mock_mode = ServerBridge()
        
        # Verify that mock database is used
        self.assertIsNotNone(bridge_mock_mode._mock_db)
        self.assertTrue(bridge_mock_mode._use_mock_data)
        
        # Test that methods return mock data
        clients = bridge_mock_mode.get_clients()
        self.assertIsInstance(clients, list)
        self.assertGreater(len(clients), 0)  # Should have mock data


if __name__ == '__main__':
    unittest.main()