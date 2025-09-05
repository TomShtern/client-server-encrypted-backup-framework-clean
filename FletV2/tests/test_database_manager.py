#!/usr/bin/env python3
"""
Unit tests for the database manager module.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import sqlite3

# Add the FletV2 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.database_manager import FletDatabaseManager, create_database_manager


class TestFletDatabaseManager(unittest.TestCase):
    """Test cases for the FletDatabaseManager."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.db_manager = FletDatabaseManager("MockaBase.db")

    def test_initialization(self):
        """Test that the database manager initializes correctly."""
        self.assertIsInstance(self.db_manager, FletDatabaseManager)
        self.assertEqual(self.db_manager.database_path, "MockaBase.db")
        self.assertIsNone(self.db_manager.connection)

    @patch('utils.database_manager.sqlite3.connect')
    def test_connect_success(self, mock_connect):
        """Test successful database connection."""
        mock_connection = Mock()
        mock_connect.return_value = mock_connection
        
        # Create a temporary database manager with a path that exists
        with patch('utils.database_manager.os.path.exists', return_value=True):
            db_manager = FletDatabaseManager("MockaBase.db")
            result = db_manager.connect()
        
        self.assertTrue(result)
        mock_connect.assert_called_once_with("MockaBase.db")
        self.assertEqual(db_manager.connection, mock_connection)

    @patch('utils.database_manager.sqlite3.connect')
    def test_connect_failure(self, mock_connect):
        """Test failed database connection."""
        mock_connect.side_effect = Exception("Connection failed")
        
        result = self.db_manager.connect()
        
        self.assertFalse(result)
        self.assertIsNone(self.db_manager.connection)

    @patch('utils.database_manager.os.path.exists')
    def test_get_table_names_no_connection(self, mock_exists):
        """Test getting table names with no connection."""
        mock_exists.return_value = True
        
        tables = self.db_manager.get_table_names()
        
        self.assertEqual(tables, [])

    @patch('utils.database_manager.os.path.exists')
    def test_get_table_data_no_connection(self, mock_exists):
        """Test getting table data with no connection."""
        mock_exists.return_value = True
        
        data = self.db_manager.get_table_data("clients")
        
        self.assertEqual(data, {"columns": [], "rows": []})

    @patch('utils.database_manager.os.path.exists')
    def test_get_database_stats_no_connection(self, mock_exists):
        """Test getting database stats with no connection."""
        mock_exists.return_value = True
        
        stats = self.db_manager.get_database_stats()
        
        self.assertEqual(stats, {})

    @patch('utils.database_manager.os.path.exists')
    def test_get_clients_no_connection(self, mock_exists):
        """Test getting clients with no connection."""
        mock_exists.return_value = True
        
        clients = self.db_manager.get_clients()
        
        self.assertEqual(clients, [])

    @patch('utils.database_manager.os.path.exists')
    def test_get_files_no_connection(self, mock_exists):
        """Test getting files with no connection."""
        mock_exists.return_value = True
        
        files = self.db_manager.get_files()
        
        self.assertEqual(files, [])

    @patch('utils.database_manager.os.path.exists')
    def test_update_row_no_connection(self, mock_exists):
        """Test updating a row with no connection."""
        mock_exists.return_value = True
        
        result = self.db_manager.update_row("clients", "123", {"name": "test"})
        
        self.assertFalse(result)

    @patch('utils.database_manager.os.path.exists')
    def test_delete_row_no_connection(self, mock_exists):
        """Test deleting a row with no connection."""
        mock_exists.return_value = True
        
        result = self.db_manager.delete_row("clients", "123")
        
        self.assertFalse(result)

    def test_create_database_manager_factory(self):
        """Test the factory function."""
        with patch('utils.database_manager.logger'):
            db_manager = create_database_manager(":memory:")
            self.assertIsInstance(db_manager, FletDatabaseManager)


if __name__ == '__main__':
    unittest.main()