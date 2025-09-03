#!/usr/bin/env python3
"""
Test script to verify GUI initialization
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_gui_initialization():
    """Test that GUI components can be initialized without errors"""
    print("Testing GUI initialization...")
    
    try:
        # Test importing the main GUI components
        from flet_server_gui.views.clients import ClientsView
        from flet_server_gui.views.files import FilesView
        from flet_server_gui.views.database import DatabaseView
        print("[PASS] All GUI view components imported successfully")
    except Exception as e:
        print(f"[FAIL] GUI component import error: {e}")
        return False
    
    # Test that the selection handlers have the correct signature
    try:
        import inspect
        
        # Check ClientsView _on_client_selected method signature
        clients_signature = inspect.signature(ClientsView._on_client_selected)
        if 'e' in clients_signature.parameters:
            print("[PASS] ClientsView selection handler has correct signature")
        else:
            print("[FAIL] ClientsView selection handler has incorrect signature")
            return False
            
        # Check FilesView _on_file_selected method signature
        files_signature = inspect.signature(FilesView._on_file_selected)
        if 'e' in files_signature.parameters:
            print("[PASS] FilesView selection handler has correct signature")
        else:
            print("[FAIL] FilesView selection handler has incorrect signature")
            return False
            
    except Exception as e:
        print(f"[FAIL] Selection handler signature test error: {e}")
        return False
        
    print("GUI initialization test completed")
    return True

if __name__ == "__main__":
    test_gui_initialization()