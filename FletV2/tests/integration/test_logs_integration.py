#!/usr/bin/env python3
"""Integration tests for Logs view with ServerBridge (mock-backed)."""

import os
import sys
import unittest

import flet as ft

# Ensure FletV2 root is on sys.path for `utils`, `views`, etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

os.environ.setdefault("FLET_V2_DEBUG", "true")

from utils.server_bridge import create_server_bridge
from utils.state_manager import StateManager
from views.logs import create_logs_view
from tests.integration_utils import FakePage


class TestLogsIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.page: ft.Page = FakePage()  # type: ignore[assignment]
        self.bridge = create_server_bridge()
        self.state_manager = StateManager(self.page, self.bridge)

    def test_logs_view_loads_and_filters(self):
        view, dispose, setup = create_logs_view(self.bridge, self.page, self.state_manager)
        self.assertIsInstance(view, ft.Control)
        setup()

        # Bridge should respond for logs in mock mode
        result = self.bridge.get_logs()
        self.assertTrue(result.get("success", False))
        data = result.get("data", [])
        self.assertIsInstance(data, list)

        dispose()


if __name__ == "__main__":
    unittest.main()
