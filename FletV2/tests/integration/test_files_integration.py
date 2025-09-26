#!/usr/bin/env python3
"""Integration tests for Files view with ServerBridge (mock-backed)."""

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
from views.files import create_files_view


class TestFilesIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.page: ft.Page = FakePage()  # type: ignore[assignment]
        self.bridge = create_server_bridge()
        self.state_manager = StateManager(self.page, self.bridge)

    def test_files_view_loads_and_delete(self):
        view, dispose, setup = create_files_view(self.bridge, self.page, self.state_manager)
        self.assertIsInstance(view, ft.Control)
        setup()

        files = self.bridge.get_files()
        self.assertIsInstance(files, list)
        self.assertGreater(len(files), 0)

        table = find_control_by_type(view, ft.DataTable)
        if table is not None:
            self.assertGreaterEqual(len(table.rows), 0)

        fid_value = files[0].get("id")
        fid = str(fid_value) if fid_value is not None else ""
        delete_result = self.bridge.delete_file(fid)
        self.assertTrue(delete_result.get("success", False))

        dispose()


if __name__ == "__main__":
    unittest.main()
