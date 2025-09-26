#!/usr/bin/env python3
"""Integration tests for Database view with ServerBridge (mock-backed)."""

import os
import sys
import unittest

# Ensure FletV2 root is on sys.path for `utils`, `views`, etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import flet as ft

os.environ.setdefault("FLET_V2_DEBUG", "false")

from tests.integration_utils import FakePage, find_control_by_type
from utils.server_bridge import create_server_bridge
from utils.state_manager import StateManager
from views.database import create_database_view


class TestDatabaseIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.page: ft.Page = FakePage()  # type: ignore[assignment]
        self.bridge = create_server_bridge()
        self.state_manager = StateManager(self.page, self.bridge)

    def test_database_view_loads_clients_table(self):
        view, dispose, setup = create_database_view(self.bridge, self.page, self.state_manager)
        self.assertIsInstance(view, ft.Control)
        setup()

        # Attempt to use bridge to fetch table data (mock DB supplies data for known tables)
        data_result = self.bridge.get_table_data("clients")
        self.assertTrue(data_result.get("success", False))
        data = data_result.get("data", [])
        self.assertIsInstance(data, list)

        table = find_control_by_type(view, ft.DataTable)
        if table is not None:
            self.assertGreaterEqual(len(table.rows), 1)

        dispose()


if __name__ == "__main__":
    unittest.main()
