#!/usr/bin/env python3
"""
Thread-Safe UI Validation Script
Tests that all thread-safe UI update patterns work correctly across the Flet GUI.

This script validates:
1. ThreadSafeUIUpdater utility functionality
2. Integration with view files (dashboard.py, clients.py, files.py)
3. Proper fallback mechanisms
4. Background thread safety

Usage:
    python validate_thread_safe_ui.py
"""

import asyncio
import sys
import threading
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_thread_safe_ui_import():
    """Test importing the thread-safe UI utilities"""
    print("[TEST] Testing ThreadSafeUIUpdater import...")
    
    try:
        from flet_server_gui.utils.thread_safe_ui import (
            ThreadSafeUIUpdater, 
            ui_safe_update, 
            safe_ui_update,
            create_safe_callback,
            safe_control_update,
            safe_controls_update
        )
        print("[PASS] ThreadSafeUIUpdater utilities imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import ThreadSafeUIUpdater: {e}")
        return False

def test_view_imports():
    """Test that view files import thread-safe utilities correctly"""
    print("\n🔍 Testing view file imports...")
    
    try:
        # Test dashboard view
        from flet_server_gui.views.dashboard import DashboardView
        print("✅ DashboardView imports successfully")
        
        # Test clients view  
        from flet_server_gui.views.clients import ClientsView
        print("✅ ClientsView imports successfully")
        
        # Test files view
        from flet_server_gui.views.files import FilesView
        print("✅ FilesView imports successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import view files: {e}")
        return False

def test_mock_page_interaction():
    """Test ThreadSafeUIUpdater with mock page object"""
    print("\n🔍 Testing ThreadSafeUIUpdater functionality...")
    
    try:
        from flet_server_gui.utils.thread_safe_ui import ThreadSafeUIUpdater
        
        # Mock page object
        class MockPage:
            def __init__(self):
                self.update_count = 0
                
            def update(self):
                self.update_count += 1
                
        async def test_updater():
            page = MockPage()
            updater = ThreadSafeUIUpdater(page)
            
            # Test initialization
            assert not updater.is_running()
            assert updater.queue_size() == 0
            
            # Test starting
            await updater.start()
            assert updater.is_running()
            
            # Test queueing updates
            update_executed = False
            def test_update():
                nonlocal update_executed
                update_executed = True
                
            updater.queue_update(test_update)
            
            # Wait for update to be processed
            await asyncio.sleep(0.1)
            
            # Test stopping
            await updater.stop()
            assert not updater.is_running()
            
            return update_executed and page.update_count > 0
            
        # Run the async test
        result = asyncio.run(test_updater())
        
        if result:
            print("✅ ThreadSafeUIUpdater functionality works correctly")
            return True
        else:
            print("❌ ThreadSafeUIUpdater functionality test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ThreadSafeUIUpdater: {e}")
        return False

def test_decorator_pattern():
    """Test the ui_safe_update decorator"""
    print("\n🔍 Testing ui_safe_update decorator...")
    
    try:
        from flet_server_gui.utils.thread_safe_ui import ui_safe_update, ThreadSafeUIUpdater
        
        class MockPage:
            def __init__(self):
                self.update_count = 0
                
            def update(self):
                self.update_count += 1
        
        class TestView:
            def __init__(self, page):
                self.page = page
                self.ui_updater = ThreadSafeUIUpdater(page)
                self.test_value = 0
                
            @ui_safe_update
            def update_test_value(self, value):
                self.test_value = value
                
        async def test_decorator():
            page = MockPage()
            view = TestView(page)
            
            # Test fallback (updater not started)
            view.update_test_value(42)
            assert view.test_value == 42
            assert page.update_count > 0
            
            # Test with updater running
            await view.ui_updater.start()
            old_update_count = page.update_count
            
            view.update_test_value(84)
            
            # Wait for queued update
            await asyncio.sleep(0.1)
            
            await view.ui_updater.stop()
            
            return view.test_value == 84 and page.update_count > old_update_count
            
        result = asyncio.run(test_decorator())
        
        if result:
            print("✅ ui_safe_update decorator works correctly")
            return True
        else:
            print("❌ ui_safe_update decorator test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing ui_safe_update decorator: {e}")
        return False

def test_background_thread_safety():
    """Test thread safety with actual background threads"""
    print("\n🔍 Testing background thread safety...")
    
    try:
        from flet_server_gui.utils.thread_safe_ui import ThreadSafeUIUpdater
        
        class MockPage:
            def __init__(self):
                self.update_count = 0
                self.updates_from_background = 0
                
            def update(self):
                self.update_count += 1
                # Check if called from background thread
                if threading.current_thread() != threading.main_thread():
                    self.updates_from_background += 1
        
        async def test_thread_safety():
            page = MockPage()
            updater = ThreadSafeUIUpdater(page)
            await updater.start()
            
            # Function to be called from background thread
            def background_update():
                updater.queue_update(lambda: None)
                
            # Start multiple background threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=background_update)
                threads.append(thread)
                thread.start()
                
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
                
            # Wait for updates to be processed
            await asyncio.sleep(0.2)
            
            await updater.stop()
            
            # Verify that page.update() was called from main thread only
            return page.update_count >= 5 and page.updates_from_background == 0
            
        result = asyncio.run(test_thread_safety())
        
        if result:
            print("✅ Background thread safety works correctly")
            return True
        else:
            print("❌ Background thread safety test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing background thread safety: {e}")
        return False

def test_view_initialization_patterns():
    """Test that view classes have proper UI updater initialization"""
    print("\n🔍 Testing view initialization patterns...")
    
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
        assert hasattr(dashboard, 'ui_updater'), "DashboardView missing ui_updater"
        assert isinstance(dashboard.ui_updater, ThreadSafeUIUpdater), "DashboardView ui_updater wrong type"
        assert hasattr(dashboard, '_updater_started'), "DashboardView missing _updater_started flag"
        print("✅ DashboardView initialization pattern correct")
        
        # Test ClientsView initialization
        from flet_server_gui.views.clients import ClientsView
        clients = ClientsView(server_bridge, MockDialogSystem(), MockToastManager(), page)
        assert hasattr(clients, 'ui_updater'), "ClientsView missing ui_updater"
        assert isinstance(clients.ui_updater, ThreadSafeUIUpdater), "ClientsView ui_updater wrong type"
        assert hasattr(clients, '_updater_started'), "ClientsView missing _updater_started flag"
        print("✅ ClientsView initialization pattern correct")
        
        # Test FilesView initialization
        from flet_server_gui.views.files import FilesView
        files = FilesView(server_bridge, MockDialogSystem(), MockToastManager(), page)
        assert hasattr(files, 'ui_updater'), "FilesView missing ui_updater"
        assert isinstance(files.ui_updater, ThreadSafeUIUpdater), "FilesView ui_updater wrong type"
        assert hasattr(files, '_updater_started'), "FilesView missing _updater_started flag"
        print("✅ FilesView initialization pattern correct")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing view initialization: {e}")
        return False

def test_page_update_replacement():
    """Test that direct page.update() calls have been replaced"""
    print("\n🔍 Testing page.update() replacement...")
    
    try:
        # Check that view files don't contain unprotected page.update() calls
        files_to_check = [
            "flet_server_gui/views/dashboard.py",
            "flet_server_gui/views/clients.py", 
            "flet_server_gui/views/files.py"
        ]
        
        unprotected_calls = []
        
        for file_path in files_to_check:
            full_path = project_root / file_path
            if not full_path.exists():
                print(f"⚠️  File not found: {file_path}")
                continue
                
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                # Look for direct page.update() calls
                if 'self.page.update()' in line:
                    # Check if it's protected by thread-safe pattern
                    context_start = max(0, line_num - 5)
                    context_end = min(len(lines), line_num + 2)
                    context = ''.join(lines[context_start:context_end])
                    
                    if 'Thread-safe UI update' not in context and 'ui_updater.queue_update' not in context:
                        unprotected_calls.append(f"{file_path}:{line_num}")
                        
        if unprotected_calls:
            print(f"❌ Found unprotected page.update() calls:")
            for call in unprotected_calls:
                print(f"   - {call}")
            return False
        else:
            print("✅ All page.update() calls are properly protected")
            return True
            
    except Exception as e:
        print(f"❌ Error checking page.update() replacement: {e}")
        return False

def main():
    """Run all validation tests"""
    print("Starting Thread-Safe UI Validation")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_thread_safe_ui_import),
        ("View Import Test", test_view_imports),
        ("Mock Page Interaction", test_mock_page_interaction),
        ("Decorator Pattern", test_decorator_pattern),
        ("Background Thread Safety", test_background_thread_safety),
        ("View Initialization", test_view_initialization_patterns),
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
            print(f"❌ {test_name} failed with exception: {e}")
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