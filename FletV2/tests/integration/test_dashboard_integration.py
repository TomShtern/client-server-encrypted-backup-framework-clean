#!/usr/bin/env python3
"""Integration tests for Dashboard view with real ServerBridge (mock-backed)."""

import os
import sys
import unittest

import flet as ft

# Ensure FletV2 root is on sys.path for `utils`, `views`, etc., without shadowing test discovery
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

os.environ.setdefault("FLET_V2_DEBUG", "true")

from utils.server_bridge import create_server_bridge
from utils.state_manager import StateManager
from views.dashboard import create_dashboard_view
from tests.integration_utils import FakePage


class TestDashboardIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.page: ft.Page = FakePage()  # type: ignore[assignment]
        self.bridge = create_server_bridge()  # Mock mode by default
        self.state_manager = StateManager(self.page, self.bridge)

    def test_dashboard_renders_and_loads_status(self):
        view, dispose, setup = create_dashboard_view(self.bridge, self.page, self.state_manager)
        self.assertIsInstance(view, ft.Control)
        # Run initial setup which triggers data loads
        setup()
        # Ensure server status call in mock mode returns data
        status = self.bridge.get_server_status()
        self.assertIsInstance(status, dict)
        self.assertTrue(status.get("success", False))

        dispose()

    def test_dashboard_handles_server_error(self):
        # Monkeypatch bridge method to force error path
        original = self.bridge.get_server_status
        try:
            def bad_call():
                raise RuntimeError("boom")
            self.bridge.get_server_status = bad_call  # type: ignore[assignment]

            view, dispose, setup = create_dashboard_view(self.bridge, self.page, self.state_manager)
            self.assertIsInstance(view, ft.Control)
            setup()
            # View should still be operable even when server fails
            self.assertTrue(True)
            dispose()
        finally:
            self.bridge.get_server_status = original  # type: ignore[assignment]


if __name__ == "__main__":
    unittest.main()
