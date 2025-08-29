#!/usr/bin/env python3
"""
Test script to verify action button functionality
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_action_button_functionality():
    """Test that action button functionality is working correctly"""
    print("Testing action button functionality...")
    
    # Test importing the components
    try:
        from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
        from flet_server_gui.components.base_component import BaseComponent
        print("[PASS] Button factory and base component imported successfully")
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False
    
    # Test that the button factory has the correct configuration
    try:
        # Check that BUTTON_CONFIGS contains the expected keys
        button_configs = ActionButtonFactory.BUTTON_CONFIGS
        required_configs = [
            'client_export', 'client_import', 'client_disconnect_bulk', 'client_delete_bulk',
            'client_disconnect', 'client_delete', 'client_view_details', 'client_view_files',
            'database_backup', 'database_optimize', 'database_analyze', 'database_execute_query',
            'file_download_bulk', 'file_verify_bulk', 'file_export_list', 'file_upload',
            'file_cleanup', 'file_download', 'file_verify', 'file_delete', 
            'file_view_details', 'file_preview'
        ]
        
        missing_configs = [config for config in required_configs if config not in button_configs]
        if not missing_configs:
            print("[PASS] All required button configurations found")
        else:
            print(f"[FAIL] Missing button configurations: {missing_configs}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Button configuration test error: {e}")
        return False
        
    # Test that the button factory can create action buttons
    try:
        # Create a mock base component
        class MockBaseComponent(BaseComponent):
            def __init__(self):
                pass
                
        mock_component = MockBaseComponent()
        
        # Create a mock server bridge
        class MockServerBridge:
            pass
            
        mock_server_bridge = MockServerBridge()
        
        # Create a mock page
        class MockPage:
            pass
            
        mock_page = MockPage()
        
        # Create button factory
        button_factory = ActionButtonFactory(mock_component, mock_server_bridge, mock_page)
        
        # Test creating a client action button
        def get_selected_clients():
            return ["client1", "client2"]
            
        client_button = button_factory.create_action_button(
            "client_disconnect_bulk",
            get_selected_clients
        )
        
        if client_button:
            print("[PASS] Client action button created successfully")
        else:
            print("[FAIL] Client action button creation failed")
            return False
            
        # Test creating a file action button
        def get_selected_files():
            return ["file1.txt", "file2.pdf"]
            
        file_button = button_factory.create_action_button(
            "file_download_bulk",
            get_selected_files
        )
        
        if file_button:
            print("[PASS] File action button created successfully")
        else:
            print("[FAIL] File action button creation failed")
            return False
            
    except Exception as e:
        print(f"[FAIL] Button creation test error: {e}")
        return False
        
    print("Action button functionality test completed")
    return True

if __name__ == "__main__":
    test_action_button_functionality()