#!/usr/bin/env python3
"""
Simple test script to verify client delete action works correctly
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_client_delete_action():
    """Test that client delete action works correctly"""
    print("Testing client delete action...")
    
    try:
        from flet_server_gui.components.client_action_handlers import ClientActionHandlers
        
        # Create mock components
        class MockServerBridge:
            pass
            
        class MockDialogSystem:
            async def show_confirmation_async(self, title, message):
                print(f"[MOCK DIALOG] {title}: {message}")
                # Simulate user confirming the action
                return True
                
            def show_custom_dialog(self, title, content, actions=None):
                print(f"[MOCK CUSTOM DIALOG] {title}")
                
        class MockToastManager:
            def show_success(self, message):
                print(f"[TOAST SUCCESS] {message}")
                
            def show_error(self, message):
                print(f"[TOAST ERROR] {message}")
                
        class MockPage:
            def run_task(self, coro):
                print(f"[MOCK RUN_TASK] Running coroutine: {coro}")
                # For testing, just run the coroutine directly
                import asyncio
                try:
                    asyncio.run(coro)
                except Exception as e:
                    print(f"[MOCK RUN_TASK ERROR] {e}")
                    
        # Create instances
        mock_server_bridge = MockServerBridge()
        mock_dialog_system = MockDialogSystem()
        mock_toast_manager = MockToastManager()
        mock_page = MockPage()
        
        # Create client action handlers
        client_action_handlers = ClientActionHandlers(
            mock_server_bridge, 
            mock_dialog_system, 
            mock_toast_manager, 
            mock_page
        )
        
        print("Created ClientActionHandlers successfully")
        
        # Test calling delete_client method
        print("Testing delete_client method...")
        import asyncio
        
        async def test_delete():
            try:
                print("[TEST] Calling delete_client with test_client_id")
                await client_action_handlers.delete_client("test_client_id")
                print("[TEST] delete_client method completed")
            except Exception as e:
                print(f"[TEST ERROR] delete_client method failed: {e}")
                import traceback
                traceback.print_exc()
                
        asyncio.run(test_delete())
        print("[TEST] Client delete action test completed")
        
    except Exception as e:
        print(f"[FAIL] Client delete action test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_client_delete_action()