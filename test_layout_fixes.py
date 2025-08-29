#!/usr/bin/env python3
"""
Test script to verify layout fixes
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_layout_fixes():
    """Test that layout fixes are working correctly"""
    print("Testing layout fixes...")
    
    # Test importing the components
    try:
        from flet_server_gui.components.client_table_renderer import ClientTableRenderer
        from flet_server_gui.components.file_table_renderer import FileTableRenderer
        from flet_server_gui.views.clients import ClientsView
        from flet_server_gui.views.files import FilesView
        from flet_server_gui.views.database import DatabaseView
        print("[PASS] All components imported successfully")
    except Exception as e:
        print(f"[FAIL] Import error: {e}")
        return False
    
    # Test that the fixes are applied
    try:
        # Check that ClientTableRenderer has the fixed get_table_container method
        import inspect
        client_renderer_source = inspect.getsource(ClientTableRenderer.get_table_container)
        if "clip_behavior=ft.ClipBehavior.NONE" in client_renderer_source:
            print("[PASS] Client table renderer layout fixes applied")
        else:
            print("[FAIL] Client table renderer layout fixes not applied")
            
        # Check that FileTableRenderer has the fixed get_table_container method
        file_renderer_source = inspect.getsource(FileTableRenderer.get_table_container)
        if "clip_behavior=ft.ClipBehavior.NONE" in file_renderer_source:
            print("[PASS] File table renderer layout fixes applied")
        else:
            print("[FAIL] File table renderer layout fixes not applied")
            
    except Exception as e:
        print(f"[FAIL] Layout fix verification error: {e}")
        return False
        
    print("Layout fixes test completed")
    return True

if __name__ == "__main__":
    test_layout_fixes()