#!/usr/bin/env python3
"""
Basic GUI Functionality Test - Comprehensive Verification Suite

This test verifies the core GUI functionality works without requiring server infrastructure.
It focuses on basic functionality verification - import integrity, view creation, theme system,
navigation utilities, and UTF-8 support.

Test Categories:
1. Import Chain Integrity - Are there broken imports from deleted files?
2. View Creation - Can each view actually be instantiated?
3. Theme System - Does theme.py load properly?
4. Navigation Utilities - Do our extracted utilities work?
5. UTF-8 Support - Is UTF-8 functional with sample text?

This test reports specific failures rather than just "success/failure" to identify
exactly what broke during our architectural changes.
"""

import sys
import os
import traceback
from typing import Dict, List, Tuple, Any, Optional
import importlib.util

# Add project root to Python path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "flet_server_gui"))

class TestResult:
    """Simple test result container"""
    def __init__(self, name: str, success: bool, message: str = "", error: Optional[Exception] = None):
        self.name = name
        self.success = success
        self.message = message
        self.error = error
        self.details = []
    
    def add_detail(self, detail: str):
        """Add detailed information to the test result"""
        self.details.append(detail)

class BasicGUITester:
    """Comprehensive basic GUI functionality tester"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.flet_available = False
        
    def log_result(self, name: str, success: bool, message: str = "", error: Optional[Exception] = None) -> TestResult:
        """Log a test result"""
        result = TestResult(name, success, message, error)
        self.results.append(result)
        return result
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all basic GUI functionality tests"""
        print("=" * 60)
        print("BASIC GUI FUNCTIONALITY TEST - Comprehensive Verification")
        print("=" * 60)
        
        # Phase 1: Core Infrastructure Tests
        print("\n[PHASE 1] Core Infrastructure Tests")
        self.test_flet_availability()
        self.test_utf8_support()
        self.test_project_structure()
        
        # Phase 2: Import Chain Integrity Tests
        print("\n[PHASE 2] Import Chain Integrity Tests")
        self.test_theme_imports()
        self.test_utility_imports()
        self.test_main_simplified_imports()
        
        # Phase 3: Component Creation Tests (only if Flet is available)
        if self.flet_available:
            print("\n[PHASE 3] Component Creation Tests")
            self.test_theme_system()
            self.test_navigation_utilities()
            self.test_view_creation()
            self.test_main_app_creation()
        else:
            print("\n[PHASE 3] Skipped (Flet not available)")
            
        # Phase 4: Integration Tests
        print("\n[PHASE 4] Integration Tests")
        self.test_utf8_with_gui()
        self.test_error_handling()
        
        # Generate comprehensive report
        return self._generate_report()
    
    def test_flet_availability(self):
        """Test if Flet is available and properly installed"""
        try:
            import flet as ft
            self.flet_available = True
            result = self.log_result("Flet Import", True, f"Flet version available: {getattr(ft, '__version__', 'unknown')}")
            result.add_detail(f"Flet module path: {ft.__file__}")
            
            # Test core Flet components we rely on
            test_components = [
                'Page', 'Row', 'Column', 'Container', 'NavigationRail', 
                'Card', 'Text', 'ResponsiveRow', 'Colors', 'Icons', 'Theme'
            ]
            missing_components = []
            for component in test_components:
                if not hasattr(ft, component):
                    missing_components.append(component)
            
            if missing_components:
                result.add_detail(f"Missing components: {missing_components}")
                result.success = False
                result.message = f"Core components missing: {missing_components}"
            else:
                result.add_detail("All core components available")
                
        except ImportError as e:
            self.flet_available = False
            result = self.log_result("Flet Import", False, f"Flet not available: {e}", e)
            result.add_detail("Install with: pip install flet")
        except Exception as e:
            self.flet_available = False
            result = self.log_result("Flet Import", False, f"Unexpected Flet error: {e}", e)
    
    def test_utf8_support(self):
        """Test UTF-8 support functionality"""
        try:
            # Test basic UTF-8 import
            import Shared.utils.utf8_solution as utf8
            result = self.log_result("UTF-8 Module Import", True, "UTF-8 solution module imported successfully")
            
            # Test UTF-8 functionality
            test_strings = [
                "Basic ASCII text",
                "Hebrew text",
                "שלום עולם",  # Hebrew: Hello World
                "Mixed: Hello שלום World"
            ]
            
            failures = []
            for test_str in test_strings:
                try:
                    # Test encoding/decoding cycle
                    encoded = test_str.encode('utf-8')
                    decoded = encoded.decode('utf-8')
                    if test_str != decoded:
                        failures.append(f"Round-trip failed for: {test_str[:20]}")
                except Exception as e:
                    failures.append(f"Failed processing: {test_str[:20]} - {e}")
            
            if failures:
                utf8_result = self.log_result("UTF-8 Functionality", False, f"UTF-8 processing failed: {len(failures)} failures")
                for failure in failures:
                    utf8_result.add_detail(failure)
            else:
                utf8_result = self.log_result("UTF-8 Functionality", True, "All UTF-8 test strings processed successfully")
                utf8_result.add_detail(f"Tested {len(test_strings)} different string types")
            
            # Test UTF-8 environment setup
            try:
                utf8.ensure_initialized()
                env_result = self.log_result("UTF-8 Environment", True, "UTF-8 environment initialized successfully")
            except Exception as e:
                env_result = self.log_result("UTF-8 Environment", False, f"UTF-8 environment setup failed: {e}", e)
                
        except ImportError as e:
            result = self.log_result("UTF-8 Module Import", False, f"Cannot import UTF-8 solution: {e}", e)
        except Exception as e:
            result = self.log_result("UTF-8 Module Import", False, f"Unexpected UTF-8 error: {e}", e)
    
    def test_project_structure(self):
        """Test that expected project files and directories exist"""
        expected_paths = [
            "flet_server_gui/main_simplified.py",
            "flet_server_gui/theme.py",
            "flet_server_gui/utils/navigation_enums.py",
            "flet_server_gui/utils/simple_navigation.py",
            "flet_server_gui/utils/accessibility_helpers.py",
            "flet_server_gui/utils/simple_server_bridge.py",
            "Shared/utils/utf8_solution.py"
        ]
        
        missing_files = []
        existing_files = []
        
        for path in expected_paths:
            full_path = os.path.join(project_root, path)
            if os.path.exists(full_path):
                existing_files.append(path)
            else:
                missing_files.append(path)
        
        if missing_files:
            result = self.log_result("Project Structure", False, f"Missing {len(missing_files)} expected files")
            for missing in missing_files:
                result.add_detail(f"Missing: {missing}")
        else:
            result = self.log_result("Project Structure", True, "All expected files present")
            
        result.add_detail(f"Found {len(existing_files)} of {len(expected_paths)} expected files")
    
    def test_theme_imports(self):
        """Test theme.py imports and functionality"""
        try:
            sys.path.insert(0, os.path.join(project_root, "flet_server_gui"))
            import theme
            
            result = self.log_result("Theme Module Import", True, "theme.py imported successfully")
            
            # Check theme functions
            required_functions = [
                'setup_default_theme', 'toggle_theme_mode', 'apply_theme_to_page',
                'get_current_theme_colors'
            ]
            
            missing_functions = []
            for func_name in required_functions:
                if not hasattr(theme, func_name):
                    missing_functions.append(func_name)
            
            if missing_functions:
                result.add_detail(f"Missing functions: {missing_functions}")
                func_result = self.log_result("Theme Functions", False, f"Missing {len(missing_functions)} theme functions")
            else:
                func_result = self.log_result("Theme Functions", True, "All theme functions available")
            
            # Check theme data
            if hasattr(theme, 'THEMES') and isinstance(theme.THEMES, dict):
                themes_result = self.log_result("Theme Data", True, f"Found {len(theme.THEMES)} themes")
                themes_result.add_detail(f"Available themes: {list(theme.THEMES.keys())}")
            else:
                themes_result = self.log_result("Theme Data", False, "THEMES dictionary not found or invalid")
                
        except ImportError as e:
            result = self.log_result("Theme Module Import", False, f"Cannot import theme: {e}", e)
        except Exception as e:
            result = self.log_result("Theme Module Import", False, f"Unexpected theme error: {e}", e)
    
    def test_utility_imports(self):
        """Test utility module imports"""
        utility_modules = [
            ("navigation_enums", "flet_server_gui.utils.navigation_enums"),
            ("simple_navigation", "flet_server_gui.utils.simple_navigation"),
            ("accessibility_helpers", "flet_server_gui.utils.accessibility_helpers"),
            ("simple_server_bridge", "flet_server_gui.utils.simple_server_bridge")
        ]
        
        for name, module_path in utility_modules:
            try:
                # Add flet_server_gui/utils to Python path for imports
                utils_path = os.path.join(project_root, "flet_server_gui", "utils")
                if utils_path not in sys.path:
                    sys.path.insert(0, utils_path)
                
                # Try to import the module
                spec = importlib.util.spec_from_file_location(
                    name, 
                    os.path.join(project_root, module_path.replace('.', os.sep) + '.py')
                )
                if spec is None or spec.loader is None:
                    result = self.log_result(f"Utility Import: {name}", False, f"Cannot find module spec: {module_path}")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                result = self.log_result(f"Utility Import: {name}", True, f"Successfully imported {name}")
                
                # Check for expected functions/classes
                if name == "navigation_enums" and hasattr(module, 'NavigationView'):
                    result.add_detail("NavigationView enum found")
                elif name == "simple_navigation":
                    expected_funcs = ['SimpleNavigationState', 'create_simple_navigation_rail']
                    found_funcs = [f for f in expected_funcs if hasattr(module, f)]
                    result.add_detail(f"Found functions: {found_funcs}")
                elif name == "accessibility_helpers" and hasattr(module, 'ensure_windowed_compatibility'):
                    result.add_detail("ensure_windowed_compatibility function found")
                elif name == "simple_server_bridge" and hasattr(module, 'SimpleServerBridge'):
                    result.add_detail("SimpleServerBridge class found")
                    
            except ImportError as e:
                result = self.log_result(f"Utility Import: {name}", False, f"Import failed: {e}", e)
            except Exception as e:
                result = self.log_result(f"Utility Import: {name}", False, f"Unexpected error: {e}", e)
    
    def test_main_simplified_imports(self):
        """Test main_simplified.py can import all its dependencies"""
        if not self.flet_available:
            self.log_result("Main Simplified Import", False, "Skipped - Flet not available")
            return
            
        try:
            # Add flet_server_gui and utils to Python path
            flet_gui_path = os.path.join(project_root, "flet_server_gui")
            utils_path = os.path.join(project_root, "flet_server_gui", "utils")
            if flet_gui_path not in sys.path:
                sys.path.insert(0, flet_gui_path)
            if utils_path not in sys.path:
                sys.path.insert(0, utils_path)
                
            # Test importing main_simplified without running it
            main_path = os.path.join(project_root, "flet_server_gui", "main_simplified.py")
            spec = importlib.util.spec_from_file_location("main_simplified_test", main_path)
            
            if spec is None or spec.loader is None:
                result = self.log_result("Main Simplified Import", False, "Cannot find main_simplified.py")
                return
            
            # Create module
            module = importlib.util.module_from_spec(spec)
            
            try:
                spec.loader.exec_module(module)
                result = self.log_result("Main Simplified Import", True, "main_simplified.py imports successful")
                
                # Check if main classes are available
                if hasattr(module, 'SimpleDesktopApp'):
                    result.add_detail("SimpleDesktopApp class found")
                if hasattr(module, 'main'):
                    result.add_detail("main function found")
                    
            except Exception as exec_error:
                # If execution fails, try to at least check if it's just a runtime issue
                result = self.log_result("Main Simplified Import", False, f"Module execution failed: {exec_error}", exec_error)
                result.add_detail("This may be a runtime issue rather than import issue")
                    
        except ImportError as e:
            result = self.log_result("Main Simplified Import", False, f"Import dependencies failed: {e}", e)
            result.add_detail("Check for missing utility modules or broken import paths")
        except Exception as e:
            result = self.log_result("Main Simplified Import", False, f"Unexpected error: {e}", e)
    
    def test_theme_system(self):
        """Test theme system functionality with actual Flet objects"""
        try:
            import flet as ft
            import theme
            
            # Create a mock page for testing
            class MockPage:
                def __init__(self):
                    self.theme = None
                    self.dark_theme = None
                    self.theme_mode = None
                    self.update_called = False
                
                def update(self):
                    self.update_called = True
            
            mock_page = MockPage()
            
            # Test theme setup
            try:
                theme.setup_default_theme(mock_page)
                if mock_page.theme is not None:
                    setup_result = self.log_result("Theme Setup", True, "Default theme setup successful")
                    setup_result.add_detail(f"Theme mode set to: {mock_page.theme_mode}")
                else:
                    setup_result = self.log_result("Theme Setup", False, "Theme not set after setup")
            except Exception as e:
                setup_result = self.log_result("Theme Setup", False, f"Theme setup failed: {e}", e)
            
            # Test theme toggling
            try:
                original_mode = mock_page.theme_mode
                theme.toggle_theme_mode(mock_page)
                if mock_page.theme_mode != original_mode or mock_page.update_called:
                    toggle_result = self.log_result("Theme Toggle", True, "Theme mode toggle successful")
                    toggle_result.add_detail(f"Theme mode changed: {original_mode} → {mock_page.theme_mode}")
                else:
                    toggle_result = self.log_result("Theme Toggle", False, "Theme mode not changed after toggle")
            except Exception as e:
                toggle_result = self.log_result("Theme Toggle", False, f"Theme toggle failed: {e}", e)
            
            # Test color retrieval
            try:
                colors = theme.get_current_theme_colors(mock_page)
                if isinstance(colors, dict) and len(colors) > 0:
                    color_result = self.log_result("Theme Colors", True, f"Retrieved {len(colors)} color definitions")
                    color_result.add_detail(f"Available colors: {list(colors.keys())[:5]}...")  # Show first 5
                else:
                    color_result = self.log_result("Theme Colors", False, "No colors returned or invalid format")
            except Exception as e:
                color_result = self.log_result("Theme Colors", False, f"Color retrieval failed: {e}", e)
                
        except ImportError as e:
            result = self.log_result("Theme System", False, f"Cannot import required modules: {e}", e)
        except Exception as e:
            result = self.log_result("Theme System", False, f"Unexpected theme system error: {e}", e)
    
    def test_navigation_utilities(self):
        """Test navigation utility functions"""
        if not self.flet_available:
            self.log_result("Navigation Utilities", False, "Skipped - Flet not available")
            return
            
        try:
            # Import navigation utilities
            from flet_server_gui.utils.navigation_enums import NavigationView
            from flet_server_gui.utils.simple_navigation import SimpleNavigationState, create_simple_navigation_rail
            
            # Test NavigationView enum
            try:
                views = [view.value for view in NavigationView]
                enum_result = self.log_result("Navigation Enum", True, f"NavigationView enum has {len(views)} views")
                enum_result.add_detail(f"Views: {views}")
            except Exception as e:
                enum_result = self.log_result("Navigation Enum", False, f"NavigationView enum failed: {e}", e)
            
            # Test SimpleNavigationState
            try:
                nav_state = SimpleNavigationState()
                nav_state.set_current_view(NavigationView.DASHBOARD.value)
                if nav_state.get_current_view() == NavigationView.DASHBOARD.value:
                    state_result = self.log_result("Navigation State", True, "SimpleNavigationState works correctly")
                else:
                    state_result = self.log_result("Navigation State", False, "Navigation state not updated correctly")
            except Exception as e:
                state_result = self.log_result("Navigation State", False, f"Navigation state failed: {e}", e)
            
            # Test navigation rail creation (mock callback)
            try:
                def mock_callback(view_name: str):
                    pass
                    
                nav_rail = create_simple_navigation_rail(
                    nav_state=SimpleNavigationState(),
                    on_change_callback=mock_callback,
                    extended=False
                )
                
                if nav_rail is not None:
                    rail_result = self.log_result("Navigation Rail", True, "Navigation rail created successfully")
                    rail_result.add_detail(f"Rail type: {type(nav_rail).__name__}")
                else:
                    rail_result = self.log_result("Navigation Rail", False, "Navigation rail creation returned None")
            except Exception as e:
                rail_result = self.log_result("Navigation Rail", False, f"Navigation rail creation failed: {e}", e)
                
        except ImportError as e:
            result = self.log_result("Navigation Utilities", False, f"Cannot import navigation utilities: {e}", e)
        except Exception as e:
            result = self.log_result("Navigation Utilities", False, f"Unexpected navigation error: {e}", e)
    
    def test_view_creation(self):
        """Test that individual view creation methods work"""
        if not self.flet_available:
            self.log_result("View Creation", False, "Skipped - Flet not available")
            return
            
        try:
            import flet as ft
            from flet_server_gui.main_simplified import SimpleDesktopApp
            
            # Create a minimal mock page
            class MockPage:
                def __init__(self):
                    self.window_min_width = None
                    self.window_min_height = None
                    self.window_resizable = None
                    self.title = None
                    self.padding = None
                    self.theme = None
                    self.theme_mode = None
                
                def update(self):
                    pass
                    
                def add(self, control):
                    pass
            
            mock_page = MockPage()
            
            # Create app instance for testing view methods
            app = SimpleDesktopApp(mock_page)
            
            # Test individual view creation methods
            view_methods = [
                ("Dashboard", "_create_dashboard_view"),
                ("Clients", "_create_clients_view"), 
                ("Files", "_create_files_view"),
                ("Database", "_create_database_view"),
                ("Analytics", "_create_analytics_view"),
                ("Logs", "_create_logs_view"),
                ("Settings", "_create_settings_view"),
                ("Error", "_create_error_view")
            ]
            
            successful_views = []
            failed_views = []
            
            for view_name, method_name in view_methods:
                try:
                    if hasattr(app, method_name):
                        if method_name == "_create_error_view":
                            # Error view requires a parameter
                            view = getattr(app, method_name)("Test error message")
                        else:
                            view = getattr(app, method_name)()
                        
                        if view is not None:
                            successful_views.append(view_name)
                        else:
                            failed_views.append(f"{view_name} (returned None)")
                    else:
                        failed_views.append(f"{view_name} (method not found)")
                except Exception as e:
                    failed_views.append(f"{view_name} ({str(e)[:50]})")
            
            if failed_views:
                result = self.log_result("View Creation", False, f"Failed to create {len(failed_views)} views")
                for failure in failed_views:
                    result.add_detail(f"Failed: {failure}")
            else:
                result = self.log_result("View Creation", True, f"Successfully created all {len(successful_views)} views")
                
            result.add_detail(f"Successful: {successful_views}")
                
        except ImportError as e:
            result = self.log_result("View Creation", False, f"Cannot import required modules: {e}", e)
        except Exception as e:
            result = self.log_result("View Creation", False, f"Unexpected view creation error: {e}", e)
    
    def test_main_app_creation(self):
        """Test that the main SimpleDesktopApp can be instantiated"""
        if not self.flet_available:
            self.log_result("Main App Creation", False, "Skipped - Flet not available")
            return
            
        try:
            import flet as ft
            from flet_server_gui.main_simplified import SimpleDesktopApp
            
            # Create a minimal mock page that satisfies the constructor
            class MockPage:
                def __init__(self):
                    self.window_min_width = None
                    self.window_min_height = None
                    self.window_resizable = None
                    self.title = None
                    self.padding = None
                    self.theme = None
                    self.theme_mode = None
                    self.on_connect = None
                
                def update(self):
                    pass
                    
                def add(self, control):
                    pass
            
            mock_page = MockPage()
            
            # Test app creation
            try:
                app = SimpleDesktopApp(mock_page)
                
                if app is not None:
                    result = self.log_result("Main App Creation", True, "SimpleDesktopApp created successfully")
                    
                    # Check key properties
                    if hasattr(app, 'expand') and app.expand:
                        result.add_detail("App has expand=True (good for desktop)")
                    if hasattr(app, 'controls') and len(app.controls) > 0:
                        result.add_detail(f"App has {len(app.controls)} controls")
                    if hasattr(app, 'nav_rail'):
                        result.add_detail("Navigation rail initialized")
                    if hasattr(app, 'content_area'):
                        result.add_detail("Content area initialized")
                else:
                    result = self.log_result("Main App Creation", False, "App creation returned None")
                    
            except Exception as e:
                result = self.log_result("Main App Creation", False, f"App creation failed: {e}", e)
                result.add_detail(f"Error type: {type(e).__name__}")
                
        except ImportError as e:
            result = self.log_result("Main App Creation", False, f"Cannot import SimpleDesktopApp: {e}", e)
        except Exception as e:
            result = self.log_result("Main App Creation", False, f"Unexpected app creation error: {e}", e)
    
    def test_utf8_with_gui(self):
        """Test UTF-8 functionality in GUI context"""
        try:
            import Shared.utils.utf8_solution as utf8
            
            # Test UTF-8 with GUI-relevant strings
            gui_test_strings = [
                "Server Management",
                "Analytics Dashboard", 
                "File Browser",
                "Settings",
                "שלום Server Status",  # Mixed Hebrew/English (Hebrew: Hello)
                "Connected [OK] | Disconnected [ERROR]"
            ]
            
            failures = []
            successes = []
            
            for test_str in gui_test_strings:
                try:
                    # Test safe_print functionality (core GUI use case)
                    utf8.safe_print(test_str)
                    successes.append(test_str[:20])
                except Exception as e:
                    failures.append(f"{test_str[:20]} - {str(e)[:30]}")
            
            if failures:
                result = self.log_result("UTF-8 with GUI", False, f"GUI UTF-8 failed for {len(failures)} strings")
                for failure in failures[:3]:  # Show first 3 failures
                    result.add_detail(f"Failed: {failure}")
            else:
                result = self.log_result("UTF-8 with GUI", True, f"GUI UTF-8 successful for all {len(successes)} test strings")
                
        except ImportError as e:
            result = self.log_result("UTF-8 with GUI", False, f"Cannot import UTF-8 module: {e}", e)
        except Exception as e:
            result = self.log_result("UTF-8 with GUI", False, f"Unexpected UTF-8 GUI error: {e}", e)
    
    def test_error_handling(self):
        """Test error handling and fallback mechanisms"""
        try:
            # Test fallback when server bridge is not available
            from flet_server_gui.utils.simple_server_bridge import SimpleServerBridge
            
            try:
                bridge = SimpleServerBridge()
                bridge_result = self.log_result("Error Handling: Bridge Fallback", True, "SimpleServerBridge fallback works")
            except Exception as e:
                bridge_result = self.log_result("Error Handling: Bridge Fallback", False, f"Bridge fallback failed: {e}", e)
            
            # Test theme fallback behavior
            if self.flet_available:
                import theme
                import flet as ft
                
                # Test with invalid theme
                class MockPage:
                    def __init__(self):
                        self.theme = None
                        self.theme_mode = None
                    def update(self):
                        pass
                
                try:
                    mock_page = MockPage()
                    # This should not crash even with a minimal mock page
                    colors = theme.get_current_theme_colors(mock_page)
                    theme_result = self.log_result("Error Handling: Theme Fallback", True, "Theme fallback works")
                    theme_result.add_detail(f"Got {len(colors)} fallback colors")
                except Exception as e:
                    theme_result = self.log_result("Error Handling: Theme Fallback", False, f"Theme fallback failed: {e}", e)
                    
        except ImportError as e:
            result = self.log_result("Error Handling", False, f"Cannot test error handling: {e}", e)
        except Exception as e:
            result = self.log_result("Error Handling", False, f"Unexpected error handling test error: {e}", e)
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        
        print(f"\n{'='*60}")
        print("TEST RESULTS SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} [PASS]")
        print(f"Failed: {failed_tests} [FAIL]")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n[FAILED TESTS] ({failed_tests}):")
            print("-" * 40)
            for result in self.results:
                if not result.success:
                    print(f"[FAIL] {result.name}")
                    print(f"   Error: {result.message}")
                    if result.error:
                        print(f"   Exception: {type(result.error).__name__}: {result.error}")
                    for detail in result.details:
                        print(f"   Detail: {detail}")
                    print()
        
        if passed_tests > 0:
            print(f"\n[PASSED TESTS] ({passed_tests}):")
            print("-" * 40)
            for result in self.results:
                if result.success:
                    print(f"[PASS] {result.name}")
                    if result.message:
                        print(f"   {result.message}")
                    for detail in result.details[:2]:  # Show first 2 details
                        print(f"   {detail}")
                    if len(result.details) > 2:
                        print(f"   ... and {len(result.details)-2} more details")
        
        # Critical issues summary
        critical_issues = []
        for result in self.results:
            if not result.success and any(keyword in result.name.lower() for keyword in ['import', 'flet', 'theme']):
                critical_issues.append(result.name)
        
        if critical_issues:
            print(f"\n[CRITICAL ISSUES] REQUIRING IMMEDIATE ATTENTION:")
            print("-" * 50)
            for issue in critical_issues:
                print(f"[CRITICAL] {issue}")
        
        # Recommendations
        print(f"\n[RECOMMENDATIONS]:")
        print("-" * 20)
        if not self.flet_available:
            print("* Install Flet: pip install flet")
        if failed_tests > 0:
            print("* Fix import chain issues before proceeding with development")
            print("* Check file paths and module structure")
        if passed_tests == total_tests:
            print("* All basic functionality tests pass! [SUCCESS]")
            print("* Ready for server integration testing")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests, 
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100,
            'results': self.results,
            'critical_issues': critical_issues,
            'flet_available': self.flet_available
        }

def main():
    """Run the comprehensive basic GUI functionality test"""
    tester = BasicGUITester()
    report = tester.run_all_tests()
    
    # Return appropriate exit code
    if report['failed_tests'] > 0:
        print(f"\n[FAIL] Test suite failed with {report['failed_tests']} failures")
        return 1
    else:
        print(f"\n[SUCCESS] All {report['total_tests']} tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())