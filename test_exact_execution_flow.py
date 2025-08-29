#!/usr/bin/env python3
"""
Detailed test script to debug the exact execution flow
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_exact_execution_flow():
    """Test the exact execution flow"""
    print("Testing exact execution flow...")
    
    try:
        import flet as ft
        from flet_server_gui.ui.widgets.buttons import ActionButtonFactory, ButtonConfig
        from flet_server_gui.components.base_component import BaseComponent
        from flet_server_gui.actions.client_actions import ClientActions
        from flet_server_gui.components.client_action_handlers import ClientActionHandlers
        
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
                    
        # Create a mock base component (using the real one this time)
        class MockToastManager:
            def show_error(self, message):
                print(f"[TOAST ERROR] {message}")
                
            def show_success(self, message):
                print(f"[TOAST SUCCESS] {message}")
                
        class MockDialogSystem:
            async def show_confirmation_async(self, title, message):
                print(f"[DIALOG CONFIRMATION] {title}: {message}")
                return True  # Simulate user confirming
                
            def show_info_dialog(self, title, message):
                print(f"[DIALOG INFO] {title}: {message}")
                
            def show_custom_dialog(self, title, content, actions):
                print(f"[DIALOG CUSTOM] {title}")
                
        mock_page = MockPage()
        mock_toast_manager = MockToastManager()
        mock_dialog_system = MockDialogSystem()
        
        # Create a real base component
        class RealBaseComponent(BaseComponent):
            def __init__(self):
                super().__init__(mock_page, mock_dialog_system, mock_toast_manager)
                
        mock_component = RealBaseComponent()
        mock_server_bridge = None  # We won't actually use this
        
        # Create button factory
        button_factory = ActionButtonFactory(mock_component, mock_server_bridge, mock_page)
        
        # Create and set action handlers (this is what the real views do)
        client_action_handlers = ClientActionHandlers(mock_server_bridge, mock_dialog_system, mock_toast_manager, mock_page)
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
        
        # Get the action instance and method
        action_instance = button_factory.actions[config.action_class]
        action_method = getattr(action_instance, config.action_method)
        
        print(f"Action instance: {action_instance}")
        print(f"Action method: {action_method}")
        
        # Test calling the method directly with params
        print("Testing direct method call...")
        try:
            # This should work
            import asyncio
            async def test_direct_call():
                try:
                    result = await action_method(**params)
                    print(f"[DIRECT CALL SUCCESS] {result}")
                except Exception as e:
                    print(f"[DIRECT CALL ERROR] {e}")
                    import traceback
                    traceback.print_exc()
            
            asyncio.run(test_direct_call())
        except Exception as e:
            print(f"[DIRECT CALL SETUP ERROR] {e}")
        
        # Test creating the lambda action
        print("Testing lambda action creation...")
        method_params = params
        action = lambda: action_method(**method_params)
        print(f"Lambda action created: {action}")
        
        # Test calling the lambda action
        print("Testing lambda action call...")
        try:
            # This should work
            import asyncio
            async def test_lambda_call():
                try:
                    result = await action()
                    print(f"[LAMBDA CALL SUCCESS] {result}")
                except Exception as e:
                    print(f"[LAMBDA CALL ERROR] {e}")
                    import traceback
                    traceback.print_exc()
            
            asyncio.run(test_lambda_call())
        except Exception as e:
            print(f"[LAMBDA CALL SETUP ERROR] {e}")
            
        print("[DEBUG] Exact execution flow test completed")
        
    except Exception as e:
        print(f"[FAIL] Exact execution flow test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_exact_execution_flow()