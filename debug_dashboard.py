# Setup path
import os
import sys
import traceback

import flet as ft

sys.path.insert(0, os.getcwd())

try:
    from FletV2.views.dashboard import create_dashboard_view

    print("Import successful")

    page = ft.Page(None, None)  # Mock page? Or just None if not used in init?
    # Flet 0.21+ Page ctor might behave differently.
    # We just want to call create_dashboard_view.
    # It takes (server_bridge, page, ...)

    # We might need a real page or a mock.
    class MockPage:
        def run_task(self, coro):
            pass

        @property
        def pubsub(self):
            return None

    page = MockPage()

    print("Creating dashboard view...")
    content, cleanup, load = create_dashboard_view(None, page, None)
    print("Dashboard created successfully!")

except Exception:
    print("CRITICAL FAILURE:")
    traceback.print_exc()
