#!/usr/bin/env python3
"""
Debug Button Tracing Test Script

This script tests button execution tracing by triggering various button actions
and monitoring the console output to identify where execution fails.
"""

# Import UTF-8 solution for Unicode handling
import Shared.utils.utf8_solution

import sys
import os
import asyncio
from typing import List

# Add project root to path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

try:
    from flet_server_gui.ui.widgets.buttons import ActionButtonFactory, ButtonConfig
    from flet_server_gui.actions.client_actions import ClientActions
    from flet_server_gui.utils.server_bridge import ModularServerBridge
    from flet_server_gui.components.base_component import BaseComponent
    import flet as ft
    IMPORTS_OK = True
    print("[TRACE_TEST] OK All imports successful")
except Exception as e:
    print(f"[TRACE_TEST] FAIL Import failed: {e}")
    IMPORTS_OK = False

class MockBaseComponent(BaseComponent):
    """Mock base component for testing"""
    
    def __init__(self):
        self.server_bridge = None
        self.page = None
        
    async def _show_error(self, message: str):
        print(f"[TRACE_TEST] ERROR: {message}")
        
    async def _show_success(self, message: str):
        print(f"[TRACE_TEST] SUCCESS: {message}")
        
    async def execute_with_confirmation(self, action, confirmation_text, success_message, operation_name):
        print(f"[TRACE_TEST] CONFIRMATION: {confirmation_text}")
        print(f"[TRACE_TEST] Executing action: {operation_name}")
        try:
            result = await action()
            print(f"[TRACE_TEST] Action result: {result}")
            if result:
                print(f"[TRACE_TEST] {success_message}")
            return result
        except Exception as e:
            print(f"[TRACE_TEST] Action failed: {e}")
            return False

class MockPage:
    """Mock Flet page for testing"""
    
    def __init__(self):
        pass
        
    def run_task(self, coroutine):
        """Mock run_task that executes immediately"""
        print(f"[TRACE_TEST] Running async task")
        return asyncio.create_task(coroutine)
        
    def update(self):
        print(f"[TRACE_TEST] Page update called")

async def test_button_execution():
    """Test button execution with tracing"""
    
    print("[TRACE_TEST] ========== BUTTON TRACING TEST ==========")
    
    if not IMPORTS_OK:
        print("[TRACE_TEST] FAIL Cannot run test - imports failed")
        return
    
    try:
        print("[TRACE_TEST] Setting up test environment...")
        
        # Create mock server bridge
        print("[TRACE_TEST] Creating server bridge...")
        server_bridge = ModularServerBridge()
        
        # Create mock base component
        print("[TRACE_TEST] Creating base component...")
        base_component = MockBaseComponent()
        base_component.server_bridge = server_bridge
        
        # Create mock page
        print("[TRACE_TEST] Creating page...")
        page = MockPage()
        base_component.page = page
        
        # Create button factory
        print("[TRACE_TEST] Creating button factory...")
        button_factory = ActionButtonFactory(base_component, server_bridge, page)
        
        # Mock selected items function
        def get_selected_items() -> List[str]:
            return ["test_client_1", "test_client_2"]
        
        print("[TRACE_TEST] Testing client export button...")
        
        # Test client export button (should not require selection)
        export_button = button_factory.create_action_button(
            config_key="client_export",
            get_selected_items=get_selected_items
        )
        
        print("[TRACE_TEST] Created export button successfully")
        print(f"[TRACE_TEST] Button type: {type(export_button)}")
        
        # Simulate button click
        print("[TRACE_TEST] Simulating button click...")
        class MockClickEvent:
            def __init__(self):
                self.control = export_button
        
        mock_event = MockClickEvent()
        
        # Get the button's click handler and execute it
        if hasattr(export_button, 'on_click') and export_button.on_click:
            print("[TRACE_TEST] Executing button click handler...")
            try:
                # The click handler is async, so we need to wait for completion
                export_button.on_click(mock_event)
                
                # Wait a moment for async tasks to complete
                await asyncio.sleep(2)
                
                print("[TRACE_TEST] Button click handler completed")
            except Exception as e:
                print(f"[TRACE_TEST] FAIL Button click handler failed: {e}")
                import traceback
                print(f"[TRACE_TEST] Traceback: {traceback.format_exc()}")
        else:
            print("[TRACE_TEST] FAIL Button has no click handler")
        
        print("[TRACE_TEST] ========== TEST COMPLETE ==========")
        
    except Exception as e:
        print(f"[TRACE_TEST] FAIL Test setup failed: {e}")
        import traceback
        print(f"[TRACE_TEST] Traceback: {traceback.format_exc()}")

async def test_individual_action():
    """Test individual action execution without UI"""
    
    print("[TRACE_TEST] ========== INDIVIDUAL ACTION TEST ==========")
    
    try:
        print("[TRACE_TEST] Creating server bridge...")
        server_bridge = ModularServerBridge()
        
        print("[TRACE_TEST] Creating client actions...")
        client_actions = ClientActions(server_bridge)
        
        print("[TRACE_TEST] Testing export_clients action...")
        result = await client_actions.export_clients([], 'csv')
        
        print(f"[TRACE_TEST] Action result: {result}")
        print(f"[TRACE_TEST] Result type: {type(result)}")
        
        if hasattr(result, 'success'):
            print(f"[TRACE_TEST] ActionResult.success: {result.success}")
            if hasattr(result, 'data'):
                print(f"[TRACE_TEST] ActionResult.data: {len(result.data) if result.data else 0} characters")
        
        print("[TRACE_TEST] ========== INDIVIDUAL ACTION TEST COMPLETE ==========")
        
    except Exception as e:
        print(f"[TRACE_TEST] FAIL Individual action test failed: {e}")
        import traceback
        print(f"[TRACE_TEST] Traceback: {traceback.format_exc()}")

def main():
    """Main test function"""
    print("[TRACE_TEST] Starting button execution tracing test...")
    
    try:
        # Test individual action first
        asyncio.run(test_individual_action())
        
        print("\n" + "="*50 + "\n")
        
        # Then test full button execution
        asyncio.run(test_button_execution())
        
    except Exception as e:
        print(f"[TRACE_TEST] ✗ Main test failed: {e}")
        import traceback
        print(f"[TRACE_TEST] Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    main()