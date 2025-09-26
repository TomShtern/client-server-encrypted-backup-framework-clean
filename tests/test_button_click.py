#!/usr/bin/env python3
"""
Test script to verify button click handler is properly set
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_button_click_handler():
    """Test that button click handler is properly set"""
    print("Testing button click handler...")

    try:
        import flet as ft
        from flet_server_gui.components.base_component import BaseComponent
        from flet_server_gui.ui.widgets.buttons import ActionButtonFactory

        class MockPage:
            def __init__(self):
                self.run_task_called = False

            def run_task(self, *args, **kwargs):
                self.run_task_called = True
                print(f"[DEBUG] run_task called with args: {args}, kwargs: {kwargs}")

        class MockBaseComponent(BaseComponent):
            def __init__(self):
                self.error_shown = False
                self.confirmation_executed = False

            async def _show_error(self, message):
                self.error_shown = True
                print(f"[ERROR] {message}")

            async def execute_with_confirmation(self, action, confirmation_text, success_message, operation_name):
                self.confirmation_executed = True
                print(f"[CONFIRMATION] {confirmation_text}")
                print(f"[SUCCESS] {success_message}")
                print(f"[OPERATION] {operation_name}")
                return True

        class MockServerBridge:
            pass

        # Create instances
        mock_page = MockPage()
        mock_component = MockBaseComponent()
        mock_server_bridge = MockServerBridge()

        # Create button factory
        button_factory = ActionButtonFactory(mock_component, mock_server_bridge, mock_page)

        # Test creating a client view details button
        def get_selected_client():
            return ["test_client_id"]

        print("Creating client view details button...")
        button = button_factory.create_action_button(
            "client_view_details",
            get_selected_client
        )

        print(f"Button type: {type(button)}")
        print(f"Button on_click: {button.on_click}")

        # Check if it's a container and has the right structure
        if isinstance(button, ft.Container):
            print("[INFO] Button is wrapped in Container (expected)")
            # Check if the container has an on_click handler
            if button.on_click:
                print("[PASS] Container has on_click handler")
            else:
                print("[FAIL] Container does not have on_click handler")
        else:
            print("[FAIL] Button is not wrapped in Container")

        print("[DEBUG] Button click handler test completed")

    except Exception as e:
        print(f"[FAIL] Button click handler test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_button_click_handler()
