#!/usr/bin/env python3
"""
Debug script to check action handler calls
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def debug_action_handlers():
    """Debug action handler calls"""
    print("Debugging action handler calls...")
    
    try:
        # Import the components
        from flet_server_gui.ui.widgets.buttons import ActionButtonFactory, ButtonConfig
        from flet_server_gui.components.base_component import BaseComponent
        
        # Create mock components
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
        
        print(f"Button created: {button}")
        
        # Simulate button click
        class MockEvent:
            pass
            
        mock_event = MockEvent()
        print("Simulating button click...")
        button.on_click(mock_event)
        
        print(f"run_task_called: {mock_page.run_task_called}")
        print(f"error_shown: {mock_component.error_shown}")
        print(f"confirmation_executed: {mock_component.confirmation_executed}")
        
        print("[DEBUG] Action handler test completed")
        
    except Exception as e:
        print(f"[FAIL] Action handler debug error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_action_handlers()