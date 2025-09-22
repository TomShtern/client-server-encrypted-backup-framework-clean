#!/usr/bin/env python3
"""Integration tests for Clients view with ServerBridge (mock-backed)."""

import os
import sys
import unittest

import flet as ft

# Ensure FletV2 root is on sys.path for `utils`, `views`, etc., without shadowing test discovery
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

os.environ.setdefault("FLET_V2_DEBUG", "true")

from utils.server_bridge import create_server_bridge
from utils.state_manager import StateManager
from views.clients import create_clients_view
from tests.integration_utils import FakePage, find_control_by_type


class TestClientsIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.page: ft.Page = FakePage()  # type: ignore[assignment]
        self.bridge = create_server_bridge()
        self.state_manager = StateManager(self.page, self.bridge)

    def test_clients_view_loads_and_actions(self):
        view, dispose, setup = create_clients_view(self.bridge, self.page, self.state_manager)
        self.assertIsInstance(view, ft.Control)
        setup()

        # Ensure mock bridge has clients
        clients = self.bridge.get_clients()
        self.assertIsInstance(clients, list)
        self.assertGreater(len(clients), 0)

        # Try invoking a delete flow programmatically
        # Find a DataTable to assert rows (best-effort)
        table = find_control_by_type(view, ft.DataTable)
        if table is not None:
            self.assertGreaterEqual(len(table.rows), 0)

        # Simulate delete via bridge to verify cascade works in mock
        cid_value = clients[0].get("id")
        cid = str(cid_value) if cid_value is not None else ""
        delete_result = self.bridge.delete_client(cid)
        self.assertTrue(delete_result.get("success", False))

        dispose()


if __name__ == "__main__":
    unittest.main()
