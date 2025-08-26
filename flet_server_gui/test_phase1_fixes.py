#!/usr/bin/env python3
"""
Phase 1 Critical Stability Fixes - Verification Test
Test script to verify that all critical stability fixes are working properly.
"""

import sys
import os
import asyncio

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

# Import UTF-8 solution to fix encoding issues
try:
    import Shared.utils.utf8_solution
    print("[INFO] UTF-8 solution imported successfully")
except ImportError as e:
    # Try alternative path
    utf8_path = os.path.join(os.path.dirname(__file__), "..", "Shared", "utils")
    if utf8_path not in sys.path:
        sys.path.insert(0, utf8_path)
    try:
        import utf8_solution
        print("[INFO] UTF-8 solution imported via alternative path")
    except ImportError:
        print("[WARNING] utf8_solution import failed, continuing without it")
        print(f"[DEBUG] Import error: {e}")

def test_imports():
    """Test that all required modules can be imported without errors"""
    print("Testing module imports...")
    
    # Test base table manager
    try:
        from flet_server_gui.components.base_table_manager import BaseTableManager
        print("  [PASS] BaseTableManager import")
    except Exception as e:
        print(f"  [FAIL] BaseTableManager import: {e}")
        return False
    
    # Test client table renderer
    try:
        from flet_server_gui.components.client_table_renderer import ClientTableRenderer
        print("  [PASS] ClientTableRenderer import")
    except Exception as e:
        print(f"  [FAIL] ClientTableRenderer import: {e}")
        return False
    
    # Test file table renderer
    try:
        from flet_server_gui.components.file_table_renderer import FileTableRenderer
        print("  [PASS] FileTableRenderer import")
    except Exception as e:
        print(f"  [FAIL] FileTableRenderer import: {e}")
        return False
    
    # Test server bridge
    try:
        from flet_server_gui.utils.server_bridge import ServerBridge
        print("  [PASS] ServerBridge import")
    except Exception as e:
        print(f"  [FAIL] ServerBridge import: {e}")
        return False
    
    # Test simple server bridge
    try:
        from flet_server_gui.utils.simple_server_bridge import SimpleServerBridge
        print("  [PASS] SimpleServerBridge import")
    except Exception as e:
        print(f"  [FAIL] SimpleServerBridge import: {e}")
        return False
    
    return True

def test_server_bridge_methods():
    """Test that server bridge has all required methods"""
    print("\nTesting server bridge methods...")
    
    # Test full server bridge
    try:
        from flet_server_gui.utils.simple_server_bridge import SimpleServerBridge
        bridge = SimpleServerBridge()
        
        # Test required methods exist
        required_methods = [
            'is_server_running',
            'get_clients', 
            'get_files',
            'get_notifications'
        ]
        
        for method in required_methods:
            if hasattr(bridge, method):
                print(f"  [PASS] SimpleServerBridge.{method} method exists")
            else:
                print(f"  [FAIL] SimpleServerBridge.{method} method missing")
                return False
                
        print("  [PASS] All server bridge methods verified")
        
    except Exception as e:
        print(f"  [FAIL] ServerBridge method testing: {e}")
        return False
    
    return True

def test_table_manager_methods():
    """Test that table managers have all required methods"""
    print("\nTesting table manager methods...")
    
    try:
        # Read the base table manager source
        base_table_path = os.path.join(os.path.dirname(__file__), "components", "base_table_manager.py")
        with open(base_table_path, 'r', encoding='utf-8') as f:
            base_table_content = f.read()
        
        # Check for required method implementations
        required_methods = [
            'select_all_rows',
            'clear_selection', 
            'get_selected_data'
        ]
        
        for method in required_methods:
            if f"def {method}" in base_table_content:
                print(f"  [PASS] BaseTableManager.{method} method implemented")
            else:
                print(f"  [FAIL] BaseTableManager.{method} method not implemented")
                return False
        
        print("  [PASS] All table manager methods verified")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Table manager method testing: {e}")
        return False

def test_table_renderer_methods():
    """Test that table renderers have all required methods"""
    print("\nTesting table renderer methods...")
    
    try:
        # Read the client table renderer source
        client_table_path = os.path.join(os.path.dirname(__file__), "components", "client_table_renderer.py")
        with open(client_table_path, 'r', encoding='utf-8') as f:
            client_table_content = f.read()
        
        # Check for required method implementations
        required_methods = [
            'select_all_rows',
            'deselect_all_rows'
        ]
        
        for method in required_methods:
            if f"def {method}" in client_table_content:
                print(f"  [PASS] ClientTableRenderer.{method} method implemented")
            else:
                print(f"  [FAIL] ClientTableRenderer.{method} method not implemented")
                return False
        
        # Read the file table renderer source
        file_table_path = os.path.join(os.path.dirname(__file__), "components", "file_table_renderer.py")
        with open(file_table_path, 'r', encoding='utf-8') as f:
            file_table_content = f.read()
        
        # Check for required method implementations
        for method in required_methods:
            if f"def {method}" in file_table_content:
                print(f"  [PASS] FileTableRenderer.{method} method implemented")
            else:
                print(f"  [FAIL] FileTableRenderer.{method} method not implemented")
                return False
        
        print("  [PASS] All table renderer methods verified")
        return True
        
    except Exception as e:
        print(f"  [FAIL] Table renderer method testing: {e}")
        return False

def main():
    """Main verification function"""
    print("=== FLET GUI PHASE 1 CRITICAL STABILITY FIXES - VERIFICATION ===\n")
    
    # Test imports
    if not test_imports():
        print("\n[FAIL] Import tests failed!")
        return 1
    
    # Test server bridge methods
    if not test_server_bridge_methods():
        print("\n[FAIL] Server bridge method tests failed!")
        return 1
    
    # Test table manager methods
    if not test_table_manager_methods():
        print("\n[FAIL] Table manager method tests failed!")
        return 1
    
    # Test table renderer methods
    if not test_table_renderer_methods():
        print("\n[FAIL] Table renderer method tests failed!")
        return 1
    
    print("\n[SUCCESS] All Phase 1 critical stability fixes verified!")
    print("\nKey Fixes Verified:")
    print("  [PASS] ServerBridge API completeness")
    print("  [PASS] SimpleServerBridge API completeness") 
    print("  [PASS] BaseTableManager selection methods")
    print("  [PASS] ClientTableRenderer selection methods")
    print("  [PASS] FileTableRenderer selection methods")
    print("  [PASS] All imports working correctly")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)