#!/usr/bin/env python3
"""
Test script to verify action handlers are working correctly
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_action_handlers():
    """Test that action handlers work correctly"""
    print("Testing action handlers...")
    
    try:
        from flet_server_gui.components.client_action_handlers import ClientActionHandlers
        from flet_server_gui.components.base_component import BaseComponent
        
        # Create mock components
        class MockPage:
            def __init__(self):
                self.controls = []
                
            def update(self):
                print("[DEBUG] Page.update() called")
                
        class MockDialogSystem:
            def show_info_dialog(self, title, message):
                print(f"[INFO DIALOG] {title}: {message}")
                
            def show_error_dialog(self, title, message):
                print(f"[ERROR DIALOG] {title}: {message}")
                
            def show_custom_dialog(self, title, content, actions):
                print(f"[CUSTOM DIALOG] {title}")
                
            async def show_confirmation_async(self, title, message):
                print(f"[CONFIRMATION] {title}: {message}")
                return True  # Simulate user confirming
                
        class MockToastManager:
            def show_success(self, message):
                print(f"[TOAST SUCCESS] {message}")
                
            def show_error(self, message):
                print(f"[TOAST ERROR] {message}")
                
            def show_warning(self, message):
                print(f"[TOAST WARNING] {message}")
                
            def show_info(self, message):
                print(f"[TOAST INFO] {message}")
                
        class MockServerBridge:
            pass
            
        # Create instances
        mock_page = MockPage()
        mock_dialog_system = MockDialogSystem()
        mock_toast_manager = MockToastManager()
        mock_server_bridge = MockServerBridge()
        
        # Create client action handlers
        client_action_handlers = ClientActionHandlers(
            mock_server_bridge, 
            mock_dialog_system, 
            mock_toast_manager, 
            mock_page
        )
        
        print("Created ClientActionHandlers successfully")
        
        # Test calling a method
        print("Testing delete_client method...")
        try:
            # This should work - it's an async method
            import asyncio
            async def test_delete():
                try:
                    await client_action_handlers.delete_client("test_client_id")
                    print("[SUCCESS] delete_client method called successfully")
                except Exception as e:
                    print(f"[ERROR] delete_client method failed: {e}")
                    import traceback
                    traceback.print_exc()
                    
            asyncio.run(test_delete())
        except Exception as e:
            print(f"[ERROR] Testing delete_client failed: {e}")
            
        print("Action handler test completed")
        
    except Exception as e:
        print(f"[FAIL] Action handler test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_action_handlers()