#!/usr/bin/env python3
"""
Detailed test script to debug button parameter passing
"""

import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_parameter_passing():
    """Test parameter passing in detail"""
    print("Testing parameter passing in detail...")

    try:
        import flet as ft
        from flet_server_gui.components.base_component import BaseComponent
        from flet_server_gui.components.client_action_handlers import ClientActionHandlers
        from flet_server_gui.ui.widgets.buttons import ActionButtonFactory, ButtonConfig

        # Create a simple mock page
        class MockPage:
            def __init__(self):
                self.controls = []
                self.window_min_width = None
                self.window_min_height = None
                self.update_called = False

            def update(self):
                self.update_called = True
                print("[DEBUG] Page.update() called")

            def run_task(self, coro, *args, **kwargs):
                print(f"[DEBUG] run_task called with coro: {coro}, args: {args}, kwargs: {kwargs}")
                # For testing, just call the coroutine directly
                import asyncio
                try:
                    asyncio.run(coro)
                except Exception as e:
                    print(f"[DEBUG] run_task exception: {e}")

        # Create a mock base component
        class MockBaseComponent(BaseComponent):
            def __init__(self, page):
                self.page = page
                self.error_shown = False
                self.confirmation_executed = False
                self.toast_manager = None
                self.dialog_system = None

            async def _show_error(self, message):
                self.error_shown = True
                print(f"[ERROR] {message}")

            async def _show_success(self, message):
                print(f"[SUCCESS] {message}")

            async def execute_with_confirmation(self, action, confirmation_text, success_message, operation_name):
                self.confirmation_executed = True
                print(f"[CONFIRMATION] {confirmation_text}")
                print(f"[SUCCESS] {success_message}")
                print(f"[OPERATION] {operation_name}")

                # Try to execute the action
                try:
                    if callable(action):
                        result = action()
                        if hasattr(result, '__await__'):
                            result = await result
                        print(f"[ACTION RESULT] {result}")
                        return True
                    else:
                        print("[ACTION] Action is not callable")
                        return False
                except Exception as e:
                    print(f"[ACTION ERROR] {e}")
                    return False

            async def execute_bulk_action(self, action, selected_items, item_type, action_name):
                print(f"[BULK ACTION] action: {action}, selected_items: {selected_items}, item_type: {item_type}, action_name: {action_name}")
                try:
                    if callable(action):
                        result = action(selected_items)
                        if hasattr(result, '__await__'):
                            result = await result
                        print(f"[BULK ACTION RESULT] {result}")
                        return True
                    else:
                        print("[BULK ACTION] Action is not callable")
                        return False
                except Exception as e:
                    print(f"[BULK ACTION ERROR] {e}")
                    return False

        class MockServerBridge:
            pass

        class MockDialogSystem:
            pass

        # Create instances
        mock_page = MockPage()
        mock_component = MockBaseComponent(mock_page)
        mock_server_bridge = MockServerBridge()
        mock_dialog_system = MockDialogSystem()

        # Create button factory
        button_factory = ActionButtonFactory(mock_component, mock_server_bridge, mock_page)

        # Create and set action handlers (this is what the real views do)
        client_action_handlers = ClientActionHandlers(mock_server_bridge, mock_dialog_system, None, mock_page)
        button_factory.actions["ClientActionHandlers"] = client_action_handlers

        # Test the parameter preparation directly
        config = ButtonConfig(
            text="View Details",
            icon=ft.Icons.INFO,
            tooltip="View detailed client information",
            action_class="ClientActionHandlers",
            action_method="view_client_details",
            confirmation_text="View details for client {item}?",
            success_message="Client details loaded",
            progress_message="Loading client details...",
            requires_selection=False,
            operation_type="single",
            action_key="client_view_details"
        )

        selected_items = ["test_client_id"]
        additional_params = None

        print("Testing parameter preparation...")
        params = button_factory._prepare_method_params(config, selected_items, additional_params)
        print(f"Prepared params: {params}")

        # Check if client_id is in params
        if "client_id" in params:
            print(f"[SUCCESS] client_id found in params: {params['client_id']}")
        else:
            print("[ERROR] client_id not found in params")

        # Test creating and clicking a client view details button
        def get_selected_client():
            return ["test_client_id"]

        print("Creating client view details button...")
        button = button_factory.create_action_button(
            "client_view_details",
            get_selected_client
        )

        print(f"Button type: {type(button)}")
        print(f"Button on_click: {button.on_click}")

        # Simulate clicking the button
        print("Simulating button click...")
        if button.on_click:
            # Create a mock event
            class MockEvent:
                def __init__(self):
                    self.data = None
                    self.control = button

            mock_event = MockEvent()

            # Call the click handler
            try:
                button.on_click(mock_event)
                print("[SUCCESS] Button click handler executed")
            except Exception as e:
                print(f"[ERROR] Button click handler failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("[ERROR] Button has no click handler")

        print("[DEBUG] Parameter passing test completed")

    except Exception as e:
        print(f"[FAIL] Parameter passing test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_parameter_passing()
