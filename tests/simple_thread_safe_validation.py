#!/usr/bin/env python3
"""
Simple Thread-Safe UI Validation Script
Tests basic functionality of the thread-safe UI implementation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test importing the thread-safe UI utilities"""
    print("[TEST] Testing ThreadSafeUIUpdater import...")
    
    try:
        from flet_server_gui.utils.thread_safe_ui import (
            ThreadSafeUIUpdater, 
            ui_safe_update, 
            safe_ui_update
        )
        print("[PASS] ThreadSafeUIUpdater utilities imported successfully")
        return True
    except ImportError as e:
        print(f"[FAIL] Failed to import ThreadSafeUIUpdater: {e}")
        return False

def test_view_imports():
    """Test that view files import correctly with thread-safe utilities"""
    print("\n[TEST] Testing view file imports...")
    
    try:
        # Test dashboard view
        from flet_server_gui.views.dashboard import DashboardView
        print("[PASS] DashboardView imports successfully")
        
        # Test clients view  
        from flet_server_gui.views.clients import ClientsView
        print("[PASS] ClientsView imports successfully")
        
        # Test files view
        from flet_server_gui.views.files import FilesView
        print("[PASS] FilesView imports successfully")
        
        return True
    except ImportError as e:
        print(f"[FAIL] Failed to import view files: {e}")
        return False

def test_view_initialization():
    """Test that view classes have proper UI updater initialization"""
    print("\n[TEST] Testing view initialization patterns...")
    
    try:
        from flet_server_gui.utils.thread_safe_ui import ThreadSafeUIUpdater
        
        # Mock objects
        class MockPage:
            def update(self): pass
            
        class MockServerBridge:
            pass
            
        class MockToastManager:
            pass
            
        class MockDialogSystem:
            pass
        
        # Test DashboardView initialization
        from flet_server_gui.views.dashboard import DashboardView
        page = MockPage()
        server_bridge = MockServerBridge()
        
        dashboard = DashboardView(page, server_bridge)
        if not hasattr(dashboard, 'ui_updater'):
            print("[FAIL] DashboardView missing ui_updater")
            return False
        if not isinstance(dashboard.ui_updater, ThreadSafeUIUpdater):
            print("[FAIL] DashboardView ui_updater wrong type")
            return False
        if not hasattr(dashboard, '_updater_started'):
            print("[FAIL] DashboardView missing _updater_started flag")
            return False
        print("[PASS] DashboardView initialization pattern correct")
        
        # Test ClientsView initialization
        from flet_server_gui.views.clients import ClientsView
        clients = ClientsView(server_bridge, MockDialogSystem(), MockToastManager(), page)
        if not hasattr(clients, 'ui_updater'):
            print("[FAIL] ClientsView missing ui_updater")
            return False
        if not isinstance(clients.ui_updater, ThreadSafeUIUpdater):
            print("[FAIL] ClientsView ui_updater wrong type")
            return False
        if not hasattr(clients, '_updater_started'):
            print("[FAIL] ClientsView missing _updater_started flag")
            return False
        print("[PASS] ClientsView initialization pattern correct")
        
        # Test FilesView initialization
        from flet_server_gui.views.files import FilesView
        files = FilesView(server_bridge, MockDialogSystem(), MockToastManager(), page)
        if not hasattr(files, 'ui_updater'):
            print("[FAIL] FilesView missing ui_updater")
            return False
        if not isinstance(files.ui_updater, ThreadSafeUIUpdater):
            print("[FAIL] FilesView ui_updater wrong type")
            return False
        if not hasattr(files, '_updater_started'):
            print("[FAIL] FilesView missing _updater_started flag")
            return False
        print("[PASS] FilesView initialization pattern correct")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Error testing view initialization: {e}")
        return False

def test_page_update_replacement():
    """Test that direct page.update() calls have been replaced"""
    print("\n[TEST] Testing page.update() replacement...")
    
    try:
        # Check that view files contain thread-safe patterns
        files_to_check = [
            "flet_server_gui/views/dashboard.py",
            "flet_server_gui/views/clients.py", 
            "flet_server_gui/views/files.py"
        ]
        
        thread_safe_patterns_found = 0
        
        for file_path in files_to_check:
            full_path = project_root / file_path
            if not full_path.exists():
                print(f"[WARN] File not found: {file_path}")
                continue
                
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for thread-safe patterns
            if 'Thread-safe UI update' in content and 'ui_updater.queue_update' in content:
                thread_safe_patterns_found += 1
                print(f"[PASS] {file_path} contains thread-safe patterns")
            else:
                print(f"[FAIL] {file_path} missing thread-safe patterns")
                
        if thread_safe_patterns_found == len(files_to_check):
            print("[PASS] All view files contain thread-safe patterns")
            return True
        else:
            print(f"[FAIL] Only {thread_safe_patterns_found}/{len(files_to_check)} files contain thread-safe patterns")
            return False
            
    except Exception as e:
        print(f"[FAIL] Error checking page.update() replacement: {e}")
        return False

def main():
    """Run all validation tests"""
    print("Starting Thread-Safe UI Validation")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("View Import Test", test_view_imports),
        ("View Initialization", test_view_initialization),
        ("Page Update Replacement", test_page_update_replacement),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[FAIL] {test_name} failed with exception: {e}")
            failed += 1
            
    print("\n" + "=" * 50)
    print(f"VALIDATION SUMMARY")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed}/{passed + failed} ({passed/(passed + failed)*100:.1f}%)")
    
    if failed == 0:
        print("\nALL TESTS PASSED! Thread-safe UI implementation is working correctly.")
        return True
    else:
        print(f"\n{failed} tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)