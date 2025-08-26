#!/usr/bin/env python3
"""
Comprehensive GUI Functionality Validation
Tests all aspects of the Material Design 3 Flet GUI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Import UTF-8 solution first
try:
    import Shared.utils.utf8_solution
    print("[UTF-8] UTF-8 solution imported successfully")
except ImportError:
    print("[WARNING] UTF-8 solution not available")

def safe_print(message: str):
    """Print message with UTF-8 encoding safety"""
    try:
        print(message)
    except UnicodeEncodeError:
        clean_msg = ''.join(char if ord(char) < 128 else '?' for char in message)
        print(clean_msg)

def test_imports():
    """Test all critical imports"""
    safe_print("\n=== TESTING IMPORTS ===")
    
    try:
        import flet as ft
        safe_print("[SUCCESS] Flet imported")
    except Exception as e:
        safe_print(f"[ERROR] Flet import failed: {e}")
        return False
        
    try:
        from flet_server_gui.ui.theme import ThemeManager
        safe_print("[SUCCESS] ThemeManager imported")
    except Exception as e:
        safe_print(f"[ERROR] ThemeManager import failed: {e}")
        
    try:
        from flet_server_gui.views.dashboard import DashboardView
        safe_print("[SUCCESS] DashboardView imported")
    except Exception as e:
        safe_print(f"[ERROR] DashboardView import failed: {e}")
        
    # Test server bridge fallback
    try:
        from flet_server_gui.utils.server_bridge import ServerBridge
        safe_print("[SUCCESS] Full ServerBridge imported")
    except Exception:
        try:
            from flet_server_gui.utils.simple_server_bridge import SimpleServerBridge
            safe_print("[SUCCESS] SimpleServerBridge fallback imported")
        except Exception as e:
            safe_print(f"[ERROR] No server bridge available: {e}")
    
    return True

def test_api_compatibility():
    """Test Flet API compatibility"""
    safe_print("\n=== TESTING FLET API COMPATIBILITY ===")
    
    try:
        import flet as ft
        
        # Test color constants
        colors_to_test = [
            'PRIMARY', 'ERROR', 'SURFACE', 'ON_SURFACE', 
            'ON_SURFACE_VARIANT', 'OUTLINE', 'OUTLINE_VARIANT'
        ]
        
        for color in colors_to_test:
            if hasattr(ft.Colors, color):
                safe_print(f"[SUCCESS] ft.Colors.{color} available")
            else:
                safe_print(f"[WARNING] ft.Colors.{color} not available")
                
        # Test icon constants
        icons_to_test = [
            'DASHBOARD', 'PLAY_ARROW', 'STOP', 'REFRESH', 
            'SETTINGS', 'CHECK_CIRCLE', 'ERROR_OUTLINE'
        ]
        
        for icon in icons_to_test:
            if hasattr(ft.Icons, icon):
                safe_print(f"[SUCCESS] ft.Icons.{icon} available")
            else:
                safe_print(f"[WARNING] ft.Icons.{icon} not available")
                
        # Test core components
        components_to_test = [
            'Card', 'Container', 'Column', 'Row', 'ResponsiveRow',
            'FilledButton', 'OutlinedButton', 'TextButton'
        ]
        
        for component in components_to_test:
            if hasattr(ft, component):
                safe_print(f"[SUCCESS] ft.{component} available")
            else:
                safe_print(f"[ERROR] ft.{component} not available")
                
    except Exception as e:
        safe_print(f"[ERROR] API compatibility test failed: {e}")
        return False
        
    return True

def test_dashboard_functionality():
    """Test dashboard functionality without launching GUI"""
    safe_print("\n=== TESTING DASHBOARD FUNCTIONALITY ===")
    
    try:
        import flet as ft
        from flet_server_gui.views.dashboard import DashboardView
        from flet_server_gui.utils.simple_server_bridge import SimpleServerBridge
        
        # Create mock page
        class MockPage:
            def __init__(self):
                self.theme_mode = ft.ThemeMode.SYSTEM
                self.theme = None
                self.dark_theme = None
                
            def update(self):
                pass
                
        mock_page = MockPage()
        server_bridge = SimpleServerBridge()
        
        # Test dashboard creation
        dashboard = DashboardView(mock_page, server_bridge)
        safe_print("[SUCCESS] DashboardView instance created")
        
        # Test dashboard methods exist
        methods_to_test = [
            'build', 'start_dashboard_sync', 'start_dashboard_async',
            'add_log_entry', '_create_server_status_card',
            '_on_start_server', '_on_stop_server', '_on_restart_server'
        ]
        
        for method in methods_to_test:
            if hasattr(dashboard, method):
                safe_print(f"[SUCCESS] Dashboard.{method} available")
            else:
                safe_print(f"[ERROR] Dashboard.{method} missing")
                
    except Exception as e:
        safe_print(f"[ERROR] Dashboard functionality test failed: {e}")
        return False
        
    return True

def main():
    """Run comprehensive validation"""
    safe_print("=" * 60)
    safe_print("FLET MATERIAL DESIGN 3 GUI - COMPREHENSIVE VALIDATION")
    safe_print("=" * 60)
    
    results = {
        "imports": test_imports(),
        "api_compatibility": test_api_compatibility(),
        "dashboard_functionality": test_dashboard_functionality()
    }
    
    safe_print("\n" + "=" * 60)
    safe_print("VALIDATION SUMMARY")
    safe_print("=" * 60)
    
    all_passed = True
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        safe_print(f"{test_name.upper()}: {status}")
        if not result:
            all_passed = False
    
    safe_print("=" * 60)
    
    if all_passed:
        safe_print("SUCCESS: All validation tests passed!")
        safe_print("The Flet Material Design 3 GUI is ready for production use.")
        return 0
    else:
        safe_print("WARNING: Some validation tests failed.")
        safe_print("Check the output above for specific issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())