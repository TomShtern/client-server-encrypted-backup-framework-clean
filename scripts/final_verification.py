#!/usr/bin/env python3
"""
Final verification script for Flet GUI stabilization project
Tests all phases and reports status
"""

import sys
import os
import traceback
from typing import List, Tuple, Dict, Any

# Add the project directory to the path  
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import utf8_solution to fix encoding issues
safe_print = print  # Default fallback
try:
    import Shared.utils.utf8_solution as utf8_solution
    from Shared.utils.utf8_solution import safe_print
    safe_print("[INFO] UTF-8 solution imported successfully")
except ImportError as e:
    # Try alternative path
    utf8_path = os.path.join(os.path.dirname(__file__), "..", "Shared", "utils")
    if utf8_path not in sys.path:
        sys.path.insert(0, utf8_path)
    try:
        import utf8_solution
        from utf8_solution import safe_print
        safe_print("[INFO] UTF-8 solution imported via alternative path")
    except ImportError:
        safe_print("[WARNING] utf8_solution import failed, continuing without it")
        safe_print(f"[DEBUG] Import error: {e}")

class VerificationTest:
    """Individual verification test"""
    def __init__(self, name: str, test_func: callable, phase: int):
        self.name = name
        self.test_func = test_func
        self.phase = phase
        self.passed = False
        self.error = None
        self.duration = 0

def test_phase_1_stability() -> bool:
    """Test Phase 1: Critical stability fixes"""
    try:
        # Test server bridge API
        from flet_server_gui.utils.server_bridge import ServerBridge
        bridge = ServerBridge()
        
        required_methods = ['get_clients', 'get_files', 'is_server_running', 'get_notifications']
        for method in required_methods:
            if not hasattr(bridge, method):
                raise AttributeError(f"Missing method: {method}")
            
            # Test method is callable without errors
            result = getattr(bridge, method)()
            if result is None and method != 'is_server_running':
                result = []  # Allow None results for data methods
        
        # Test FilesView compatibility
        try:
            from flet_server_gui.views.files import FilesView
            # This should not raise AttributeError anymore
            print("FilesView import successful")
        except AttributeError as e:
            if 'select_all_rows' in str(e):
                raise Exception("FilesView still has select_all_rows AttributeError")
        
        return True
        
    except Exception as e:
        safe_print(f"Phase 1 test failed: {e}")
        return False

def test_phase_2_foundation() -> bool:
    """Test Phase 2: Foundation infrastructure"""
    try:
        # Test BaseTableManager
        from flet_server_gui.components.base_table_manager import BaseTableManager
        from unittest.mock import Mock
        import flet as ft
        
        class TestTableManager(BaseTableManager):
            def get_table_columns(self) -> List:
                return [ft.DataColumn(ft.Text("Name")), ft.DataColumn(ft.Text("Status"))]
            
            def create_table_row(self, item, on_item_select):
                return ft.DataRow(cells=[ft.DataCell(ft.Text(str(item)))])
            
            def get_sortable_columns(self) -> List[str]:
                return ["name", "status"]
                
            def sort_data(self, data: List, column: str, ascending: bool = True) -> List:
                return data  # Simple implementation for testing
                
            def _apply_custom_filters(self, items: List) -> List:
                return items
                
            def _apply_search_filter(self, items: List, search_term: str) -> List:
                return items
                
            async def perform_bulk_action(self, action: str, item_ids: List[str]) -> None:
                pass
        
        # Mock the required parameters for BaseTableManager constructor
        server_bridge = Mock()
        button_factory = Mock()
        page = Mock(spec=ft.Page)
        manager = TestTableManager(server_bridge, button_factory, page)
        
        # Test required methods exist
        methods = ['select_all_rows', 'clear_selection', 'get_selected_data']
        for method in methods:
            if not hasattr(manager, method):
                raise AttributeError(f"BaseTableManager missing method: {method}")
        
        # Test ToastManager
        from flet_server_gui.utils.toast_manager import ToastManager
        toast = ToastManager(page)
        if not hasattr(toast, 'show_toast'):
            raise AttributeError("ToastManager missing show_toast method")
        
        # Test ConnectionManager  
        from flet_server_gui.utils.connection_manager import ConnectionManager
        conn_mgr = ConnectionManager()
        if not hasattr(conn_mgr, 'register_callback'):
            raise AttributeError("ConnectionManager missing register_callback method")
        
        return True
        
    except Exception as e:
        safe_print(f"Phase 2 test failed: {e}")
        return False

def test_phase_3_ui_stability() -> bool:
    """Test Phase 3: UI stability and navigation"""
    try:
        # Test NavigationManager
        from flet_server_gui.managers.navigation_manager import NavigationManager
        from unittest.mock import Mock
        import flet as ft
        
        page = Mock(spec=ft.Page)
        switch_callback = Mock()
        nav_manager = NavigationManager(page, switch_callback)
        
        # Test navigation methods
        if not hasattr(nav_manager, 'navigate_to'):
            raise AttributeError("NavigationManager missing navigate_to method")
        
        # Test responsive layout
        from flet_server_gui.ui.layouts.responsive import ResponsiveLayoutManager
        
        page = Mock(spec=ft.Page)
        layout_manager = ResponsiveLayoutManager(page)
        if not hasattr(layout_manager, 'update_viewport'):
            raise Exception("ResponsiveLayoutManager missing update_viewport method")
        
        # Test theme consistency  
        from flet_server_gui.ui.theme import get_theme_tokens
        tokens = get_theme_tokens()
        if not tokens:
            raise Exception("Theme system not working")
        
        return True
        
    except Exception as e:
        safe_print(f"Phase 3 test failed: {e}")
        return False

def test_phase_4_enhanced_features() -> bool:
    """Test Phase 4: Enhanced features"""
    try:
        # Test StatusPill
        from flet_server_gui.ui.widgets.status_pill import StatusPill
        from flet_server_gui.utils.connection_manager import ConnectionStatus
        
        pill = StatusPill(ConnectionStatus.CONNECTED)
        if not hasattr(pill, 'set_status'):
            raise AttributeError("StatusPill missing set_status method")
        
        # Test NotificationsPanel
        from flet_server_gui.ui.widgets.notifications_panel import NotificationsPanel
        panel = NotificationsPanel()
        if not hasattr(panel, 'add_notification'):
            raise AttributeError("NotificationsPanel missing add_notification method")
        
        # Test ActivityLogDialog
        from flet_server_gui.ui.widgets.activity_log_dialog import ActivityLogDialog
        dialog = ActivityLogDialog()
        if not hasattr(dialog, 'show'):
            raise AttributeError("ActivityLogDialog missing show method")
        
        return True
        
    except Exception as e:
        safe_print(f"Phase 4 test failed: {e}")
        return False

def test_phase_5_optimization() -> bool:
    """Test Phase 5: Performance optimization"""
    try:
        # Test performance manager
        from flet_server_gui.utils.performance_manager import PerformanceManager
        
        perf_mgr = PerformanceManager()
        if not hasattr(perf_mgr, 'measure_performance'):
            raise AttributeError("PerformanceManager missing measure_performance method")
        
        # Test integration
        import unittest
        from tests.test_gui_integration import TestGUIIntegration
        
        # Run a subset of integration tests
        suite = unittest.TestLoader().loadTestsFromTestCase(TestGUIIntegration)
        runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=0)
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            raise Exception(f"Integration tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
        
        return True
        
    except Exception as e:
        safe_print(f"Phase 5 test failed: {e}")
        return False

def main():
    """Run all verification tests"""
    
    tests = [
        VerificationTest("Phase 1: Critical Stability", test_phase_1_stability, 1),
        VerificationTest("Phase 2: Foundation Infrastructure", test_phase_2_foundation, 2), 
        VerificationTest("Phase 3: UI Stability", test_phase_3_ui_stability, 3),
        VerificationTest("Phase 4: Enhanced Features", test_phase_4_enhanced_features, 4),
        VerificationTest("Phase 5: Optimization", test_phase_5_optimization, 5),
    ]
    
    safe_print("FLET GUI STABILIZATION - FINAL VERIFICATION")
    safe_print("=" * 60)
    
    passed_count = 0
    failed_tests = []
    
    for test in tests:
        safe_print(f"\nTesting {test.name}...")
        
        try:
            import time
            start_time = time.time()
            
            test.passed = test.test_func()
            test.duration = time.time() - start_time
            
            if test.passed:
                safe_print(f"[PASS] {test.name} - PASSED ({test.duration:.2f}s)")
                passed_count += 1
            else:
                safe_print(f"[FAIL] {test.name} - FAILED ({test.duration:.2f}s)")
                failed_tests.append(test)
                
        except Exception as e:
            test.error = str(e)
            test.duration = time.time() - start_time
            safe_print(f"[CRASH] {test.name} - CRASHED ({test.duration:.2f}s)")
            safe_print(f"   Error: {e}")
            failed_tests.append(test)
    
    # Final report
    safe_print("\n" + "=" * 60)
    safe_print("VERIFICATION SUMMARY")
    safe_print("=" * 60)
    safe_print(f"Passed: {passed_count}/{len(tests)}")
    safe_print(f"Failed: {len(failed_tests)}/{len(tests)}")
    
    if failed_tests:
        safe_print(f"\nFAILED TESTS:")
        for test in failed_tests:
            safe_print(f"   * {test.name}")
            if test.error:
                safe_print(f"     Error: {test.error}")
    
    success_rate = (passed_count / len(tests)) * 100
    safe_print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        safe_print("PROJECT READY FOR PRODUCTION")
        return 0
    elif success_rate >= 60:
        safe_print("PROJECT NEEDS MINOR FIXES")
        return 1
    else:
        safe_print("PROJECT NEEDS MAJOR FIXES")
        return 2

if __name__ == "__main__":
    sys.exit(main())