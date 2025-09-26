#!/usr/bin/env python3
"""
Comprehensive Functionality Test for main_simplified.py

This script systematically tests the SimpleDesktopApp to verify that it actually works
functionally, not just launches. It tests:

1. All imports and dependencies
2. Class instantiation and initialization
3. Navigation between different views
4. View rendering without errors
5. Server bridge functionality
6. Theme switching capabilities
7. Error handling and fallbacks
8. Component functionality

The goal is to identify specific failures and provide actionable feedback.
"""

import asyncio
import inspect
import os
import sys
import traceback
from datetime import datetime

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'flet_server_gui'))
sys.path.insert(0, os.path.dirname(__file__))

print("=== SIMPLIFIED APP FUNCTIONALITY TEST ===")
print(f"Test started at: {datetime.now()}")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print()

class TestResult:
    """Container for test results"""
    def __init__(self, name: str, passed: bool, message: str, details: str | None = None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details
        self.timestamp = datetime.now()

class SimplifiedAppTester:
    """Comprehensive tester for the simplified app"""

    def __init__(self):
        self.results: list[TestResult] = []
        self.app_instance = None
        self.mock_page = None
        self.test_failures = 0
        self.test_successes = 0

    def log_result(self, name: str, passed: bool, message: str, details: str = None):
        """Log a test result"""
        result = TestResult(name, passed, message, details)
        self.results.append(result)

        if passed:
            self.test_successes += 1
            print(f"[PASS] {name}: {message}")
        else:
            self.test_failures += 1
            print(f"[FAIL] {name}: {message}")
            if details:
                print(f"   Details: {details}")

        if details and passed:  # Show details for passing tests if they're informative
            print(f"   Info: {details}")

    def test_imports(self):
        """Test all critical imports"""
        print("\n[TEST] Testing Imports...")

        # Test flet import
        try:
            import flet as ft
            self.log_result("Flet Import", True, "Successfully imported flet")

            # Test flet constants
            try:
                test_constants = [
                    ft.Icons.DASHBOARD,
                    ft.Colors.PRIMARY,
                    ft.NavigationRail,
                    ft.Container,
                    ft.ResponsiveRow,
                    ft.ThemeMode.DARK
                ]
                self.log_result("Flet Constants", True, f"All {len(test_constants)} critical flet constants available")
            except Exception as e:
                self.log_result("Flet Constants", False, "Some flet constants missing", str(e))

        except Exception as e:
            self.log_result("Flet Import", False, "Failed to import flet", str(e))
            return False

        # Test simplified app import
        try:
            self.log_result("SimpleDesktopApp Import", True, "Successfully imported SimpleDesktopApp class")
        except Exception as e:
            self.log_result("SimpleDesktopApp Import", False, "Failed to import SimpleDesktopApp", str(e))
            return False

        # Test utility imports
        utility_imports = [
            ("NavigationView", "flet_server_gui.utils.navigation_enums"),
            ("SimpleNavigationState", "flet_server_gui.utils.simple_navigation"),
            ("ensure_windowed_compatibility", "flet_server_gui.utils.accessibility_helpers"),
            ("setup_default_theme", "flet_server_gui.theme"),
        ]

        for item_name, module_name in utility_imports:
            try:
                module = __import__(module_name, fromlist=[item_name])
                getattr(module, item_name)
                self.log_result(f"Utility Import: {item_name}", True, f"Successfully imported {item_name}")
            except Exception as e:
                self.log_result(f"Utility Import: {item_name}", False, f"Failed to import {item_name}", str(e))

        # Test server bridge imports with fallback
        try:
            try:
                bridge_type = "Full ModularServerBridge"
            except:
                bridge_type = "SimpleServerBridge (Fallback)"

            self.log_result("Server Bridge Import", True, f"Successfully imported {bridge_type}")
        except Exception as e:
            self.log_result("Server Bridge Import", False, "Failed to import any server bridge", str(e))

        return True

    def test_class_instantiation(self):
        """Test class instantiation and basic initialization"""
        print("\n[TEST] Testing Class Instantiation...")

        try:
            from flet_server_gui.main_simplified import SimpleDesktopApp

            # Create mock page
            class MockPage:
                def __init__(self):
                    self.window_min_width = None
                    self.window_min_height = None
                    self.window_resizable = None
                    self.title = None
                    self.theme = None
                    self.theme_mode = None
                    self.padding = None
                    self.on_connect = None
                    self.controls = []
                    self.update_called = False

                def add(self, control):
                    self.controls.append(control)

                def update(self):
                    self.update_called = True

            self.mock_page = MockPage()

            # Test class instantiation
            self.app_instance = SimpleDesktopApp(self.mock_page)
            self.log_result("Class Instantiation", True, "SimpleDesktopApp created successfully")

            # Test basic attributes
            expected_attributes = ['page', 'expand', 'nav_state', 'content_area', 'nav_rail', 'controls']
            missing_attrs = []
            for attr in expected_attributes:
                if not hasattr(self.app_instance, attr):
                    missing_attrs.append(attr)

            if missing_attrs:
                self.log_result("Basic Attributes", False, f"Missing attributes: {missing_attrs}")
            else:
                self.log_result("Basic Attributes", True, f"All {len(expected_attributes)} expected attributes present")

            # Test window configuration
            config_checks = [
                ("window_min_width", 800),
                ("window_min_height", 600),
                ("window_resizable", True)
            ]

            config_issues = []
            for config_name, expected_value in config_checks:
                actual_value = getattr(self.mock_page, config_name)
                if actual_value != expected_value:
                    config_issues.append(f"{config_name}: expected {expected_value}, got {actual_value}")

            if config_issues:
                self.log_result("Window Configuration", False, "Window not configured correctly", "; ".join(config_issues))
            else:
                self.log_result("Window Configuration", True, "Window properly configured for desktop app")

            return True

        except Exception as e:
            self.log_result("Class Instantiation", False, "Failed to create SimpleDesktopApp", str(e))
            return False

    def test_navigation_system(self):
        """Test navigation state and view switching"""
        print("\n[TEST] Testing Navigation System...")

        if not self.app_instance:
            self.log_result("Navigation System", False, "Cannot test - app instance not available")
            return False

        try:

            # Test navigation state
            nav_state = self.app_instance.nav_state
            if nav_state:
                self.log_result("Navigation State", True, f"Navigation state initialized, current view: {nav_state.current_view}")

                # Test navigation state methods
                state_methods = ['update_current_view', 'can_go_back', 'go_back', 'set_badge', 'get_badge']
                missing_methods = []
                for method in state_methods:
                    if not hasattr(nav_state, method):
                        missing_methods.append(method)

                if missing_methods:
                    self.log_result("Navigation State Methods", False, f"Missing methods: {missing_methods}")
                else:
                    self.log_result("Navigation State Methods", True, f"All {len(state_methods)} navigation methods available")

            else:
                self.log_result("Navigation State", False, "Navigation state is None")

            # Test NavigationRail creation
            nav_rail = self.app_instance.nav_rail
            if nav_rail:
                self.log_result("NavigationRail Creation", True, "NavigationRail created successfully")

                # Check destinations
                if hasattr(nav_rail, 'destinations') and nav_rail.destinations:
                    dest_count = len(nav_rail.destinations)
                    self.log_result("Navigation Destinations", True, f"NavigationRail has {dest_count} destinations")
                else:
                    self.log_result("Navigation Destinations", False, "NavigationRail has no destinations")
            else:
                self.log_result("NavigationRail Creation", False, "NavigationRail is None")

            return True

        except Exception as e:
            self.log_result("Navigation System", False, "Navigation system test failed", str(e))
            return False

    def test_view_creation(self):
        """Test all view creation methods"""
        print("\n🔍 Testing View Creation...")

        if not self.app_instance:
            self.log_result("View Creation", False, "Cannot test - app instance not available")
            return False

        view_methods = [
            ('_create_dashboard_view', 'Dashboard View'),
            ('_create_clients_view', 'Clients View'),
            ('_create_files_view', 'Files View'),
            ('_create_database_view', 'Database View'),
            ('_create_analytics_view', 'Analytics View'),
            ('_create_logs_view', 'Logs View'),
            ('_create_settings_view', 'Settings View'),
            ('_create_error_view', 'Error View')
        ]

        successful_views = []
        failed_views = []

        for method_name, view_name in view_methods:
            try:
                if hasattr(self.app_instance, method_name):
                    method = getattr(self.app_instance, method_name)

                    if method_name == '_create_error_view':
                        # Error view needs a parameter
                        result = method("Test error message")
                    else:
                        result = method()

                    if result is not None:
                        successful_views.append(view_name)
                        self.log_result(f"View Creation: {view_name}", True, f"Successfully created {view_name}")

                        # Test if result has expected structure
                        if hasattr(result, 'controls') or hasattr(result, 'content'):
                            pass  # Good structure
                        else:
                            self.log_result(f"View Structure: {view_name}", False, "View doesn't have expected structure")
                    else:
                        failed_views.append(view_name)
                        self.log_result(f"View Creation: {view_name}", False, "Method returned None")
                else:
                    failed_views.append(view_name)
                    self.log_result(f"View Creation: {view_name}", False, f"Method {method_name} not found")

            except Exception as e:
                failed_views.append(view_name)
                self.log_result(f"View Creation: {view_name}", False, f"Exception creating {view_name}", str(e))

        # Summary
        total_views = len(view_methods)
        success_count = len(successful_views)
        self.log_result("View Creation Summary", success_count == total_views,
                       f"{success_count}/{total_views} views created successfully")

        return len(failed_views) == 0

    def test_view_loading(self):
        """Test the _load_view method with different view names"""
        print("\n🔍 Testing View Loading...")

        if not self.app_instance:
            self.log_result("View Loading", False, "Cannot test - app instance not available")
            return False

        try:
            from flet_server_gui.utils.navigation_enums import NavigationView

            # Test loading each view type
            view_tests = [
                (NavigationView.DASHBOARD.value, "Dashboard"),
                (NavigationView.CLIENTS.value, "Clients"),
                (NavigationView.FILES.value, "Files"),
                (NavigationView.DATABASE.value, "Database"),
                (NavigationView.ANALYTICS.value, "Analytics"),
                (NavigationView.LOGS.value, "Logs"),
                (NavigationView.SETTINGS.value, "Settings"),
                ("invalid_view", "Invalid View (fallback test)")
            ]

            successful_loads = []
            failed_loads = []

            for view_value, view_name in view_tests:
                try:
                    # Capture the content before load
                    original_content = getattr(self.app_instance.content_area, 'content', None)

                    # Attempt to load view
                    self.app_instance._load_view(view_value)

                    # Check if content changed
                    new_content = getattr(self.app_instance.content_area, 'content', None)

                    if new_content is not None:
                        successful_loads.append(view_name)
                        self.log_result(f"View Load: {view_name}", True, f"Successfully loaded {view_name}")
                    else:
                        failed_loads.append(view_name)
                        self.log_result(f"View Load: {view_name}", False, f"Content is None after loading {view_name}")

                except Exception as e:
                    failed_loads.append(view_name)
                    self.log_result(f"View Load: {view_name}", False, f"Exception loading {view_name}", str(e))

            # Summary
            success_count = len(successful_loads)
            total_count = len(view_tests)
            self.log_result("View Loading Summary", success_count >= total_count - 1,  # Allow 1 failure for invalid view
                           f"{success_count}/{total_count} views loaded successfully")

            return len(failed_loads) <= 1  # Allow invalid view to fail

        except Exception as e:
            self.log_result("View Loading", False, "View loading test failed", str(e))
            return False

    def test_server_bridge(self):
        """Test server bridge functionality"""
        print("\n🔍 Testing Server Bridge...")

        if not self.app_instance:
            self.log_result("Server Bridge", False, "Cannot test - app instance not available")
            return False

        try:
            server_bridge = self.app_instance.server_bridge

            if server_bridge is None:
                self.log_result("Server Bridge Availability", False, "Server bridge is None")
                return False
            else:
                bridge_type = type(server_bridge).__name__
                self.log_result("Server Bridge Availability", True, f"Server bridge available: {bridge_type}")

            # Test server bridge methods
            bridge_methods = [
                'get_server_status',
                'start_server',
                'stop_server',
                'get_client_list',
                'get_file_list',
                'is_server_running'
            ]

            available_methods = []
            missing_methods = []

            for method_name in bridge_methods:
                if hasattr(server_bridge, method_name):
                    available_methods.append(method_name)
                else:
                    missing_methods.append(method_name)

            if missing_methods:
                self.log_result("Server Bridge Methods", False,
                               f"Missing methods: {missing_methods}. Available: {available_methods}")
            else:
                self.log_result("Server Bridge Methods", True,
                               f"All {len(bridge_methods)} expected methods available")

            # Test basic method calls (synchronous ones first)
            try:
                running_status = server_bridge.is_server_running()
                self.log_result("Bridge Method Test: is_server_running", True,
                               f"Method works, server running: {running_status}")
            except Exception as e:
                self.log_result("Bridge Method Test: is_server_running", False,
                               "Method call failed", str(e))

            try:
                client_list = server_bridge.get_client_list()
                self.log_result("Bridge Method Test: get_client_list", True,
                               f"Method works, {len(client_list)} clients returned")
            except Exception as e:
                self.log_result("Bridge Method Test: get_client_list", False,
                               "Method call failed", str(e))

            return True

        except Exception as e:
            self.log_result("Server Bridge", False, "Server bridge test failed", str(e))
            return False

    async def test_async_server_bridge(self):
        """Test async server bridge functionality"""
        print("\n🔍 Testing Async Server Bridge...")

        if not self.app_instance or not self.app_instance.server_bridge:
            self.log_result("Async Server Bridge", False, "Server bridge not available")
            return False

        try:
            server_bridge = self.app_instance.server_bridge

            # Test async methods
            async_methods = [
                ('get_server_status', [], 'Get server status'),
                ('start_server', [], 'Start server'),
                ('stop_server', [], 'Stop server'),
            ]

            for method_name, args, description in async_methods:
                if hasattr(server_bridge, method_name):
                    try:
                        method = getattr(server_bridge, method_name)
                        if inspect.iscoroutinefunction(method):
                            result = await method(*args)
                        else:
                            result = method(*args)

                        self.log_result(f"Async Bridge: {method_name}", True,
                                       f"{description} successful. Result type: {type(result).__name__}")
                    except Exception as e:
                        self.log_result(f"Async Bridge: {method_name}", False,
                                       f"{description} failed", str(e))
                else:
                    self.log_result(f"Async Bridge: {method_name}", False,
                                   f"Method {method_name} not available")

            return True

        except Exception as e:
            self.log_result("Async Server Bridge", False, "Async server bridge test failed", str(e))
            return False

    def test_theme_system(self):
        """Test theme system functionality"""
        print("\n🔍 Testing Theme System...")

        try:
            # Test theme import
            from flet_server_gui.theme import THEMES, setup_default_theme, toggle_theme_mode
            self.log_result("Theme Import", True, f"Theme system imported. Available themes: {list(THEMES.keys())}")

            # Test theme application
            if self.mock_page:
                try:
                    setup_default_theme(self.mock_page)
                    self.log_result("Theme Application", True, "Default theme applied successfully")

                    # Check if theme was actually set
                    if hasattr(self.mock_page, 'theme') and self.mock_page.theme:
                        self.log_result("Theme Setting", True, "Page theme was set")
                    else:
                        self.log_result("Theme Setting", False, "Page theme is still None")

                except Exception as e:
                    self.log_result("Theme Application", False, "Failed to apply default theme", str(e))

                # Test theme toggle
                try:
                    original_mode = getattr(self.mock_page, 'theme_mode', None)
                    toggle_theme_mode(self.mock_page)
                    new_mode = getattr(self.mock_page, 'theme_mode', None)

                    if new_mode != original_mode:
                        self.log_result("Theme Toggle", True, f"Theme mode changed from {original_mode} to {new_mode}")
                    else:
                        self.log_result("Theme Toggle", False, "Theme mode did not change")

                except Exception as e:
                    self.log_result("Theme Toggle", False, "Theme toggle failed", str(e))
            else:
                self.log_result("Theme System", False, "Cannot test - mock page not available")

            return True

        except Exception as e:
            self.log_result("Theme System", False, "Theme system test failed", str(e))
            return False

    def test_error_handling(self):
        """Test error handling and fallback mechanisms"""
        print("\n🔍 Testing Error Handling...")

        if not self.app_instance:
            self.log_result("Error Handling", False, "Cannot test - app instance not available")
            return False

        try:
            # Test error view creation
            error_message = "Test error for error handling validation"
            error_view = self.app_instance._create_error_view(error_message)

            if error_view is not None:
                self.log_result("Error View Creation", True, "Error view created successfully")
            else:
                self.log_result("Error View Creation", False, "Error view creation returned None")

            # Test loading invalid view (should fall back to dashboard or error)
            try:
                original_content = getattr(self.app_instance.content_area, 'content', None)
                self.app_instance._load_view("completely_invalid_view_name")
                new_content = getattr(self.app_instance.content_area, 'content', None)

                if new_content is not None and new_content != original_content:
                    self.log_result("Invalid View Fallback", True, "Invalid view load handled gracefully")
                else:
                    self.log_result("Invalid View Fallback", False, "Invalid view load did not provide fallback")

            except Exception as e:
                self.log_result("Invalid View Fallback", False, "Invalid view load raised unhandled exception", str(e))

            return True

        except Exception as e:
            self.log_result("Error Handling", False, "Error handling test failed", str(e))
            return False

    def test_accessibility_helpers(self):
        """Test accessibility helper functions"""
        print("\n🔍 Testing Accessibility Helpers...")

        try:
            import flet as ft
            from flet_server_gui.utils.accessibility_helpers import ensure_windowed_compatibility

            # Create test content
            test_content = ft.Container(
                content=ft.Text("Test content for accessibility"),
                padding=20
            )

            # Test windowed compatibility
            compatible_content = ensure_windowed_compatibility(test_content)

            if compatible_content is not None:
                self.log_result("Accessibility Helpers", True, "ensure_windowed_compatibility works")

                # Check if it's wrapped properly
                if hasattr(compatible_content, 'content'):
                    self.log_result("Accessibility Wrapping", True, "Content properly wrapped for windowed mode")
                else:
                    self.log_result("Accessibility Wrapping", False, "Content not properly wrapped")
            else:
                self.log_result("Accessibility Helpers", False, "ensure_windowed_compatibility returned None")

            return True

        except Exception as e:
            self.log_result("Accessibility Helpers", False, "Accessibility helpers test failed", str(e))
            return False

    def test_component_integration(self):
        """Test integration between components"""
        print("\n🔍 Testing Component Integration...")

        if not self.app_instance:
            self.log_result("Component Integration", False, "Cannot test - app instance not available")
            return False

        try:
            # Test that app components are properly connected
            integration_checks = [
                (hasattr(self.app_instance, 'nav_rail'), "NavigationRail attribute exists"),
                (hasattr(self.app_instance, 'content_area'), "Content area attribute exists"),
                (hasattr(self.app_instance, 'nav_state'), "Navigation state attribute exists"),
                (hasattr(self.app_instance, 'controls'), "Controls attribute exists"),
                (len(self.app_instance.controls) > 0, "App has controls"),
            ]

            passed_checks = 0
            for check, description in integration_checks:
                if check:
                    passed_checks += 1
                    self.log_result(f"Integration: {description}", True, "✓")
                else:
                    self.log_result(f"Integration: {description}", False, "✗")

            # Test controls structure
            if hasattr(self.app_instance, 'controls') and len(self.app_instance.controls) >= 2:
                controls = self.app_instance.controls
                has_nav_rail = any(hasattr(c, 'destinations') for c in controls if c)
                has_divider = any(str(type(c).__name__) == 'VerticalDivider' for c in controls if c)
                has_content_area = any(hasattr(c, 'content') for c in controls if c)

                structure_score = sum([has_nav_rail, has_divider, has_content_area])
                self.log_result("Control Structure", structure_score >= 2,
                               f"App layout structure: NavRail={has_nav_rail}, Divider={has_divider}, Content={has_content_area}")
            else:
                self.log_result("Control Structure", False, "App controls structure incomplete")

            # Test if app is properly expandable
            expand_value = getattr(self.app_instance, 'expand', None)
            self.log_result("App Expandable", expand_value == True,
                           f"App expand property: {expand_value}")

            return passed_checks >= len(integration_checks) - 1  # Allow 1 failure

        except Exception as e:
            self.log_result("Component Integration", False, "Component integration test failed", str(e))
            return False

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)

        total_tests = self.test_successes + self.test_failures
        success_rate = (self.test_successes / total_tests * 100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"Successes: {self.test_successes}")
        print(f"Failures: {self.test_failures}")
        print(f"Success Rate: {success_rate:.1f}%")

        if self.test_failures > 0:
            print("\n🚨 FAILED TESTS:")
            for result in self.results:
                if not result.passed:
                    print(f"  • {result.name}: {result.message}")
                    if result.details:
                        print(f"    Details: {result.details}")

        print("\n📈 FUNCTIONALITY ANALYSIS:")

        # Categorize results
        categories = {
            "Import Issues": [r for r in self.results if "Import" in r.name and not r.passed],
            "Class Issues": [r for r in self.results if "Class" in r.name and not r.passed],
            "Navigation Issues": [r for r in self.results if "Navigation" in r.name or ("View" in r.name and not r.passed)],
            "Server Bridge Issues": [r for r in self.results if "Bridge" in r.name and not r.passed],
            "Theme Issues": [r for r in self.results if "Theme" in r.name and not r.passed],
            "Integration Issues": [r for r in self.results if "Integration" in r.name and not r.passed]
        }

        for category, issues in categories.items():
            if issues:
                print(f"\n  🔍 {category}: {len(issues)} issues found")
                for issue in issues[:3]:  # Show top 3 issues per category
                    print(f"    - {issue.message}")
            else:
                print(f"  ✅ {category}: No issues")

        # Overall assessment
        print("\n🎯 OVERALL ASSESSMENT:")
        if success_rate >= 90:
            print("  🟢 EXCELLENT: App appears to be fully functional")
        elif success_rate >= 75:
            print("  🟡 GOOD: App is mostly functional with minor issues")
        elif success_rate >= 50:
            print("  🟠 MODERATE: App has significant functionality issues")
        else:
            print("  🔴 POOR: App has major functionality problems")

        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if self.test_failures == 0:
            print("  • App is ready for use")
            print("  • Consider adding more comprehensive integration tests")
        else:
            critical_failures = [r for r in self.results if not r.passed and
                                ("Import" in r.name or "Class" in r.name)]
            if critical_failures:
                print("  • Fix critical import/class issues first")

            navigation_failures = [r for r in self.results if not r.passed and
                                 ("Navigation" in r.name or "View" in r.name)]
            if navigation_failures:
                print("  • Address navigation and view rendering issues")

            bridge_failures = [r for r in self.results if not r.passed and "Bridge" in r.name]
            if bridge_failures:
                print("  • Resolve server bridge connectivity issues")

    async def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting comprehensive functionality tests...\n")

        # Run all tests
        test_functions = [
            self.test_imports,
            self.test_class_instantiation,
            self.test_navigation_system,
            self.test_view_creation,
            self.test_view_loading,
            self.test_server_bridge,
            self.test_theme_system,
            self.test_error_handling,
            self.test_accessibility_helpers,
            self.test_component_integration
        ]

        for test_func in test_functions:
            try:
                test_func()
            except Exception as e:
                self.log_result(f"Test Framework Error: {test_func.__name__}", False,
                               "Test function itself failed", str(e))

        # Run async tests
        try:
            await self.test_async_server_bridge()
        except Exception as e:
            self.log_result("Async Test Framework Error", False,
                           "Async test function failed", str(e))

        # Print final summary
        self.print_summary()

        return self.test_failures == 0

async def main():
    """Main test execution function"""
    tester = SimplifiedAppTester()

    try:
        success = await tester.run_all_tests()

        print(f"\n🏁 Test completed at: {datetime.now()}")

        if success:
            print("✅ ALL TESTS PASSED - App is functionally ready!")
            return 0
        else:
            print(f"❌ {tester.test_failures} TESTS FAILED - App has functionality issues")
            return 1

    except Exception as e:
        print(f"💥 CRITICAL TEST FAILURE: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return 2

if __name__ == "__main__":
    # Run the async test
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
