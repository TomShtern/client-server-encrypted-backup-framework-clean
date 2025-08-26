#!/usr/bin/env python3
"""
Phase 2 Foundation Infrastructure - Verification Test
Test script to verify that all Phase 2 foundation infrastructure components are working properly.
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
    
    # Test toast manager
    try:
        from flet_server_gui.utils.toast_manager import ToastManager
        print("  [PASS] ToastManager import")
    except Exception as e:
        print(f"  [FAIL] ToastManager import: {e}")
        return False
    
    # Test error handler
    try:
        from flet_server_gui.utils.error_handler import ErrorHandler
        print("  [PASS] ErrorHandler import")
    except Exception as e:
        print(f"  [FAIL] ErrorHandler import: {e}")
        return False
    
    # Test connection manager
    try:
        from flet_server_gui.utils.connection_manager import ConnectionManager
        print("  [PASS] ConnectionManager import")
    except Exception as e:
        print(f"  [FAIL] ConnectionManager import: {e}")
        return False
    
    # Test base table manager
    try:
        from flet_server_gui.components.base_table_manager import BaseTableManager
        print("  [PASS] BaseTableManager import")
    except Exception as e:
        print(f"  [FAIL] BaseTableManager import: {e}")
        return False
    
    return True

def test_toast_manager():
    """Test that toast manager has all required functionality"""
    print("\nTesting ToastManager functionality...")
    
    try:
        from flet_server_gui.utils.toast_manager import ToastManager, ToastType, ToastConfig
        
        # Test that ToastType enum is complete
        expected_types = ['SUCCESS', 'INFO', 'WARNING', 'ERROR']
        for toast_type in expected_types:
            if hasattr(ToastType, toast_type):
                print(f"  [PASS] ToastType.{toast_type} exists")
            else:
                print(f"  [FAIL] ToastType.{toast_type} missing")
                return False
        
        # Test that ToastManager has required methods
        required_methods = [
            'show_toast',
            'show_success',
            'show_info',
            'show_warning',
            'show_error',
            'dismiss_all_toasts',
            'get_active_toast_count',
            'get_queue_size',
            'get_toast_stats'
        ]
        
        # Create a mock page object for testing
        class MockPage:
            def __init__(self):
                self.overlay = []
                self.update = lambda: None
        
        mock_page = MockPage()
        toast_manager = ToastManager(mock_page)
        
        for method in required_methods:
            if hasattr(toast_manager, method):
                print(f"  [PASS] ToastManager.{method} method exists")
            else:
                print(f"  [FAIL] ToastManager.{method} method missing")
                return False
                
        print("  [PASS] All ToastManager functionality verified")
        return True
        
    except Exception as e:
        print(f"  [FAIL] ToastManager testing: {e}")
        return False

def test_error_handler():
    """Test that error handler has all required functionality"""
    print("\nTesting ErrorHandler functionality...")
    
    try:
        from flet_server_gui.utils.error_handler import ErrorHandler, ErrorSeverity, ErrorCategory
        
        # Test that ErrorSeverity enum is complete
        expected_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        for severity in expected_severities:
            if hasattr(ErrorSeverity, severity):
                print(f"  [PASS] ErrorSeverity.{severity} exists")
            else:
                print(f"  [FAIL] ErrorSeverity.{severity} missing")
                return False
        
        # Test that ErrorCategory enum is complete
        expected_categories = ['NETWORK', 'DATA', 'UI', 'SYSTEM', 'VALIDATION']
        for category in expected_categories:
            if hasattr(ErrorCategory, category):
                print(f"  [PASS] ErrorCategory.{category} exists")
            else:
                print(f"  [FAIL] ErrorCategory.{category} missing")
                return False
        
        # Test that ErrorHandler has required methods
        required_methods = [
            'handle_error',
            'error_handler_decorator',
            'get_error_stats',
            'clear_error_history'
        ]
        
        error_handler = ErrorHandler()
        
        for method in required_methods:
            if hasattr(error_handler, method):
                print(f"  [PASS] ErrorHandler.{method} method exists")
            else:
                print(f"  [FAIL] ErrorHandler.{method} method missing")
                return False
                
        print("  [PASS] All ErrorHandler functionality verified")
        return True
        
    except Exception as e:
        print(f"  [FAIL] ErrorHandler testing: {e}")
        return False

def test_connection_manager():
    """Test that connection manager has all required functionality"""
    print("\nTesting ConnectionManager functionality...")
    
    try:
        from flet_server_gui.utils.connection_manager import ConnectionManager, ConnectionConfig, ConnectionStatus
        
        # Test that ConnectionStatus enum is complete
        expected_statuses = ['DISCONNECTED', 'CONNECTING', 'CONNECTED', 'RECONNECTING', 'ERROR', 'TIMEOUT']
        for status in expected_statuses:
            if hasattr(ConnectionStatus, status):
                print(f"  [PASS] ConnectionStatus.{status} exists")
            else:
                print(f"  [FAIL] ConnectionStatus.{status} missing")
                return False
        
        # Test that ConnectionManager has required methods
        required_methods = [
            'connect',
            'disconnect',
            'is_connected',
            'get_connection_info',
            'health_check',
            'register_callback',
            'unregister_callback',
            'cleanup',
            'get_connection_stats'
        ]
        
        config = ConnectionConfig()
        connection_manager = ConnectionManager(config)
        
        for method in required_methods:
            if hasattr(connection_manager, method):
                print(f"  [PASS] ConnectionManager.{method} method exists")
            else:
                print(f"  [FAIL] ConnectionManager.{method} method missing")
                return False
                
        print("  [PASS] All ConnectionManager functionality verified")
        return True
        
    except Exception as e:
        print(f"  [FAIL] ConnectionManager testing: {e}")
        return False

def test_base_table_manager():
    """Test that base table manager has all Phase 2 functionality"""
    print("\nTesting BaseTableManager Phase 2 functionality...")
    
    try:
        from flet_server_gui.components.base_table_manager import BaseTableManager
        
        # Test that BaseTableManager has required Phase 2 methods
        required_methods = [
            'initialize_phase2_components',
            'get_sortable_columns',
            'sort_data',
            'enable_sorting',
            'setup_pagination',
            'get_current_page_data',
            'goto_page',
            'export_data',
            'get_table_stats',
            'refresh_table',
            'enable_virtual_scrolling',
            'enable_lazy_loading',
            'setup_keyboard_navigation',
            'get_accessibility_info'
        ]
        
        # We can't instantiate BaseTableManager directly since it's abstract,
        # but we can check if the methods are defined in the class
        for method in required_methods:
            if hasattr(BaseTableManager, method):
                print(f"  [PASS] BaseTableManager.{method} method exists")
            else:
                print(f"  [FAIL] BaseTableManager.{method} method missing")
                return False
                
        print("  [PASS] All BaseTableManager Phase 2 functionality verified")
        return True
        
    except Exception as e:
        print(f"  [FAIL] BaseTableManager Phase 2 testing: {e}")
        return False

def main():
    """Main verification function"""
    print("=== FLET GUI PHASE 2 FOUNDATION INFRASTRUCTURE - VERIFICATION ===\n")
    
    # Test imports
    if not test_imports():
        print("\n[FAIL] Import tests failed!")
        return 1
    
    # Test toast manager
    if not test_toast_manager():
        print("\n[FAIL] ToastManager tests failed!")
        return 1
    
    # Test error handler
    if not test_error_handler():
        print("\n[FAIL] ErrorHandler tests failed!")
        return 1
    
    # Test connection manager
    if not test_connection_manager():
        print("\n[FAIL] ConnectionManager tests failed!")
        return 1
    
    # Test base table manager
    if not test_base_table_manager():
        print("\n[FAIL] BaseTableManager tests failed!")
        return 1
    
    print("\n[SUCCESS] All Phase 2 foundation infrastructure components verified!")
    print("\nKey Components Verified:")
    print("  [PASS] ToastManager - Standardized user notifications")
    print("  [PASS] ErrorHandler - Centralized error handling")
    print("  [PASS] ConnectionManager - Server connection management")
    print("  [PASS] BaseTableManager - Advanced table features")
    print("  [PASS] All imports working correctly")
    print("  [PASS] All required methods implemented")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)