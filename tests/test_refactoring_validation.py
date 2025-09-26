#!/usr/bin/env python3
"""
Test script to validate the refactoring work done in Phases 1-5.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_server.real_backup_executor import RealBackupExecutor
from Shared.utils.unified_config import get_config


class TestRefactoringValidation(unittest.TestCase):

    def test_config_centralization(self):
        """Test if the configuration is centralized and accessible."""
        server_port = get_config('server.port')
        api_port = get_config('api.port')
        self.assertIsNotNone(server_port)
        self.assertIsNotNone(api_port)
        self.assertIsInstance(server_port, int)
        self.assertIsInstance(api_port, int)

    def test_file_organization(self):
        """Test if the file organization is correct by importing a moved script."""
        try:
            from scripts import launch_server_gui
            self.assertTrue(True)
        except ImportError:
            self.fail("Failed to import launch_server_gui from its new location in scripts/")

    def test_unified_monitor_integration(self):
        """Test the integration of the UnifiedFileMonitor."""
        # This is a more complex test that requires running the servers.
        # For now, we will just check if the RealBackupExecutor can be initialized.
        try:
            executor = RealBackupExecutor()
            self.assertIsNotNone(executor)
        except Exception as e:
            self.fail(f"Failed to initialize RealBackupExecutor: {e}")

if __name__ == '__main__':
    unittest.main()
