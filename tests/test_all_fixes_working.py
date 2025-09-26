#!/usr/bin/env python3
"""
Comprehensive test to verify all fixes are working together
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_all_fixes_working():
    """Test that all fixes are working together"""
    print("Testing all fixes working together...")

    try:
        import flet as ft
        from flet_server_gui.components.base_component import BaseComponent
        from flet_server_gui.components.client_table_renderer import ClientTableRenderer
        from flet_server_gui.components.file_table_renderer import FileTableRenderer
        from flet_server_gui.ui.widgets.buttons import ActionButtonFactory

        class MockPage:
            def __init__(self):
                self.run_task_called = False

            def run_task(self, *args, **kwargs):
                self.run_task_called = True
                print(f"[DEBUG] run_task called with args: {args}")

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

        class MockButtonFactory:
            def __init__(self):
                self.mock_page = MockPage()
                self.mock_component = MockBaseComponent()
                self.mock_server_bridge = MockServerBridge()
                self.button_factory = ActionButtonFactory(self.mock_component, self.mock_server_bridge, self.mock_page)

            def create_action_button(self, config_key, get_selected_items):
                return self.button_factory.create_action_button(config_key, get_selected_items)

        # Test 1: Button factory creates buttons with proper click handlers
        print("Test 1: Button factory creates buttons with proper click handlers")
        mock_button_factory = MockButtonFactory()

        def get_selected_client():
            return ["test_client_id"]

        client_button = mock_button_factory.create_action_button(
            "client_view_details",
            get_selected_client
        )

        if isinstance(client_button, ft.Container) and client_button.on_click:
            print("[PASS] Client button has proper click handler")
        else:
            print("[FAIL] Client button does not have proper click handler")
            return False

        # Test 2: Client table renderer creates action buttons properly
        print("Test 2: Client table renderer creates action buttons properly")
        class MockClient:
            client_id = "test_client"

        client_renderer = ClientTableRenderer(None, mock_button_factory, None)
        mock_client = MockClient()

        buttons_row = client_renderer._create_client_action_buttons(mock_client)
        if isinstance(buttons_row, ft.Row) and len(buttons_row.controls) > 0:
            print("[PASS] Client action buttons created properly")
        else:
            print("[FAIL] Client action buttons not created properly")
            return False

        # Test 3: File table renderer creates action buttons properly
        print("Test 3: File table renderer creates action buttons properly")
        class MockFile:
            filename = "test_file.txt"

        file_renderer = FileTableRenderer(None, mock_button_factory, None)
        mock_file = MockFile()

        file_buttons_row = file_renderer._create_file_action_buttons(mock_file)
        if isinstance(file_buttons_row, ft.Row) and len(file_buttons_row.controls) > 0:
            print("[PASS] File action buttons created properly")
        else:
            print("[FAIL] File action buttons not created properly")
            return False

        # Test 4: Lambda closure capture is working
        print("Test 4: Lambda closure capture is working")
        # Create multiple clients and verify each gets the right client_id
        class MockClient1:
            client_id = "client_1"

        class MockClient2:
            client_id = "client_2"

        mock_client1 = MockClient1()
        mock_client2 = MockClient2()

        buttons_row1 = client_renderer._create_client_action_buttons(mock_client1)
        buttons_row2 = client_renderer._create_client_action_buttons(mock_client2)

        # Get the getter functions from the buttons
        button1 = buttons_row1.controls[0]  # View details button
        button2 = buttons_row2.controls[0]  # View details button

        # Extract the getter functions (this is a bit tricky since they're wrapped)
        getter1 = button1.on_click.__closure__[0].cell_contents.__closure__[1].cell_contents
        getter2 = button2.on_click.__closure__[0].cell_contents.__closure__[1].cell_contents

        # Call the getters and check the results
        result1 = getter1()
        result2 = getter2()

        if result1 == ["client_1"] and result2 == ["client_2"]:
            print("[PASS] Lambda closure capture is working")
        else:
            print(f"[FAIL] Lambda closure capture not working - got {result1} and {result2}")
            return False

        print("[SUCCESS] All fixes are working together properly!")
        return True

    except Exception as e:
        print(f"[FAIL] Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_all_fixes_working()
