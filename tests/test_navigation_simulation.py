#!/usr/bin/env python3
"""
Navigation Simulation Test
Tests the navigation functionality of the Flet GUI without manual interaction.
Identifies which view switches work and which fail, and reports specific issues.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import asyncio
import time
import traceback
from typing import Any

# Import the main app and required components
try:
    import flet as ft
    from flet_server_gui.managers.view_manager import ViewManager
    from flet_server_gui.ui.dialogs import DialogSystem, ToastManager
    from flet_server_gui.utils.navigation_enums import (
        NAVIGATION_ITEMS,
        NavigationView,
        get_index_by_view,
        get_view_by_index,
    )
    from flet_server_gui.utils.simple_navigation import SimpleNavigationState, navigate_programmatically

    # Server bridge
    from flet_server_gui.utils.simple_server_bridge import SimpleServerBridge
    from flet_server_gui.views.analytics import AnalyticsView
    from flet_server_gui.views.clients import ClientsView

    # Import all views to test them individually
    from flet_server_gui.views.dashboard import DashboardView
    from flet_server_gui.views.database import DatabaseView
    from flet_server_gui.views.files import FilesView
    from flet_server_gui.views.logs_view import LogsView
    from flet_server_gui.views.settings_view import SettingsView

    print("✅ All imports successful")

except ImportError as e:
    print(f"❌ Import error: {e}")
    traceback.print_exc()
    sys.exit(1)


class NavigationTestResults:
    """Container for navigation test results."""

    def __init__(self):
        self.test_results: dict[str, dict[str, Any]] = {}
        self.overall_success = True
        self.critical_errors: list[str] = []

    def add_test_result(self, view_name: str, success: bool, error_msg: str = "", build_method: str = ""):
        """Add a test result for a specific view."""
        self.test_results[view_name] = {
            "success": success,
            "error": error_msg,
            "build_method": build_method,
            "timestamp": time.time()
        }
        if not success:
            self.overall_success = False

    def add_critical_error(self, error_msg: str):
        """Add a critical system error."""
        self.critical_errors.append(error_msg)
        self.overall_success = False

    def print_summary(self):
        """Print comprehensive test results."""
        print("\n" + "="*70)
        print("🧪 NAVIGATION TEST RESULTS SUMMARY")
        print("="*70)

        if self.critical_errors:
            print("\n🚨 CRITICAL ERRORS (System Issues):")
            for error in self.critical_errors:
                print(f"   ❌ {error}")

        print(f"\n📊 OVERALL SUCCESS: {'✅ PASS' if self.overall_success else '❌ FAIL'}")
        print(f"📈 SUCCESS RATE: {sum(1 for r in self.test_results.values() if r['success'])}/{len(self.test_results)} views")

        print("\n📋 DETAILED VIEW TEST RESULTS:")
        print("-" * 70)

        for view_name, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"   {status:<8} | {view_name.upper():<12} | Method: {result['build_method']}")
            if result["error"]:
                print(f"            └─ Error: {result['error']}")

        print("\n🔍 ANALYSIS:")
        failing_views = [name for name, result in self.test_results.items() if not result["success"]]
        if failing_views:
            print(f"   🔴 Failed views: {', '.join(failing_views)}")
        else:
            print("   🟢 All views can be built successfully")

        build_methods = {}
        for view_name, result in self.test_results.items():
            method = result["build_method"]
            if method not in build_methods:
                build_methods[method] = []
            build_methods[method].append(view_name)

        print("\n📚 BUILD METHODS ANALYSIS:")
        for method, views in build_methods.items():
            print(f"   {method}: {', '.join(views)}")


class MockPage:
    """Mock Flet page for testing without actual GUI."""

    def __init__(self):
        self.title = ""
        self.window_width = 1280
        self.window_height = 800
        self.window_min_width = 1024
        self.window_min_height = 768
        self.window_resizable = True
        self.padding = None
        self.spacing = 0
        self.appbar = None
        self.controls = []
        self.on_window_event = None
        self.window_to_front = True
        self.on_connect = None
        self.on_close = None
        self.update_count = 0

    def update(self):
        """Mock update method."""
        self.update_count += 1

    def add(self, control):
        """Mock add method."""
        self.controls.append(control)


class NavigationTester:
    """Test navigation functionality programmatically."""

    def __init__(self):
        self.results = NavigationTestResults()
        self.mock_page = MockPage()
        self.server_bridge = None
        self.dialog_system = None
        self.toast_manager = None

    def setup_test_environment(self):
        """Setup test environment with mocked dependencies."""
        try:
            print("🔧 Setting up test environment...")

            # Create server bridge
            self.server_bridge = SimpleServerBridge()
            print("   ✅ Server bridge created")

            # Create dialog and toast systems
            # These might fail with mock page, so wrap in try-catch
            try:
                self.dialog_system = DialogSystem(self.mock_page)
                self.toast_manager = ToastManager(self.mock_page)
                print("   ✅ Dialog and toast systems created")
            except Exception as e:
                print(f"   ⚠️ Dialog/toast system creation failed (expected): {e}")
                self.dialog_system = None
                self.toast_manager = None

            return True

        except Exception as e:
            error_msg = f"Failed to setup test environment: {e}"
            self.results.add_critical_error(error_msg)
            print(f"❌ {error_msg}")
            return False

    def test_view_instantiation(self):
        """Test if all view classes can be instantiated."""
        print("\n🏗️ Testing view instantiation...")

        view_classes = [
            ("dashboard", DashboardView, [self.mock_page, self.server_bridge]),
            ("clients", ClientsView, [self.server_bridge, self.dialog_system, self.toast_manager, self.mock_page]),
            ("files", FilesView, [self.server_bridge, self.dialog_system, self.toast_manager, self.mock_page]),
            ("database", DatabaseView, [self.server_bridge, self.dialog_system, self.toast_manager, self.mock_page]),
            ("analytics", AnalyticsView, [self.mock_page, self.server_bridge, self.dialog_system, self.toast_manager]),
            ("settings", SettingsView, [self.mock_page, self.dialog_system, self.toast_manager]),
            ("logs", LogsView, [self.mock_page, self.dialog_system, self.toast_manager]),
        ]

        instantiated_views = {}

        for view_name, view_class, args in view_classes:
            try:
                # Filter out None arguments
                filtered_args = [arg for arg in args if arg is not None]
                view_instance = view_class(*filtered_args)
                instantiated_views[view_name] = view_instance
                print(f"   ✅ {view_name.upper()}: Instantiated successfully")

            except Exception as e:
                error_msg = f"Failed to instantiate: {e}"
                self.results.add_test_result(view_name, False, error_msg, "instantiation_failed")
                print(f"   ❌ {view_name.upper()}: {error_msg}")
                instantiated_views[view_name] = None

        return instantiated_views

    def test_view_build_methods(self, instantiated_views: dict[str, Any]):
        """Test if views can build their content."""
        print("\n🔨 Testing view build methods...")

        for view_name, view_instance in instantiated_views.items():
            if view_instance is None:
                continue

            # Determine which build method to use
            build_method = "unknown"
            content = None
            success = False
            error_msg = ""

            try:
                if view_name == "settings" and hasattr(view_instance, 'create_settings_view'):
                    build_method = "create_settings_view"
                    content = view_instance.create_settings_view()
                elif view_name == "logs" and hasattr(view_instance, 'create_logs_view'):
                    build_method = "create_logs_view"
                    content = view_instance.create_logs_view()
                elif hasattr(view_instance, 'build'):
                    build_method = "build"
                    content = view_instance.build()
                else:
                    build_method = "direct_instance"
                    content = view_instance

                # Check if content was created
                if content is not None:
                    success = True
                    print(f"   ✅ {view_name.upper()}: Content built via {build_method}")
                else:
                    error_msg = f"Build method {build_method} returned None"
                    print(f"   ❌ {view_name.upper()}: {error_msg}")

            except Exception as e:
                error_msg = f"Build method {build_method} failed: {e}"
                print(f"   ❌ {view_name.upper()}: {error_msg}")

            self.results.add_test_result(view_name, success, error_msg, build_method)

    def test_view_manager_integration(self, instantiated_views: dict[str, Any]):
        """Test ViewManager with the instantiated views."""
        print("\n⚙️ Testing ViewManager integration...")

        try:
            # Create mock content area
            content_area = ft.AnimatedSwitcher(
                content=ft.Text("Loading..."),
                transition=ft.AnimatedSwitcherTransition.FADE,
                duration=200
            )

            # Create ViewManager
            view_manager = ViewManager(self.mock_page, content_area)
            print("   ✅ ViewManager created successfully")

            # Register all views
            for view_name, view_instance in instantiated_views.items():
                if view_instance is not None:
                    view_manager.register_view(view_name, view_instance)
                    print(f"   ✅ Registered {view_name} with ViewManager")

            # Test view switching
            print("\n🔄 Testing view switches...")
            initial_content = content_area.content

            for view_name in instantiated_views.keys():
                if instantiated_views[view_name] is None:
                    continue

                try:
                    print(f"   🔄 Switching to {view_name}...")
                    success = view_manager.switch_view(view_name)

                    if success:
                        current_view = view_manager.get_current_view()
                        if current_view == view_name:
                            print(f"      ✅ Switch successful - current view: {current_view}")
                            print(f"      📊 Page updates: {self.mock_page.update_count}")

                            # Check if content actually changed
                            if content_area.content != initial_content:
                                print("      ✅ Content area updated")
                            else:
                                print("      ⚠️ Content area unchanged")
                        else:
                            print(f"      ❌ View state mismatch: expected {view_name}, got {current_view}")
                    else:
                        print("      ❌ Switch failed")

                except Exception as e:
                    print(f"      ❌ Switch error: {e}")

            return view_manager

        except Exception as e:
            error_msg = f"ViewManager integration failed: {e}"
            self.results.add_critical_error(error_msg)
            print(f"   ❌ {error_msg}")
            return None

    def test_navigation_state_integration(self, view_manager):
        """Test SimpleNavigationState integration."""
        print("\n🧭 Testing NavigationState integration...")

        try:
            # Create navigation state
            nav_state = SimpleNavigationState()
            print("   ✅ NavigationState created")

            # Set navigation state in view manager
            if view_manager:
                view_manager.set_navigation_state(nav_state)
                print("   ✅ NavigationState linked to ViewManager")

                # Test navigation state updates
                for view_name in ["dashboard", "clients", "files", "database", "analytics", "logs", "settings"]:
                    try:
                        nav_state.update_current_view(view_name)
                        current = nav_state.get_current_view()
                        if current == view_name:
                            print(f"   ✅ NavigationState update: {view_name}")
                        else:
                            print(f"   ❌ NavigationState mismatch: expected {view_name}, got {current}")
                    except Exception as e:
                        print(f"   ❌ NavigationState update failed for {view_name}: {e}")

        except Exception as e:
            error_msg = f"NavigationState integration failed: {e}"
            self.results.add_critical_error(error_msg)
            print(f"   ❌ {error_msg}")

    def test_navigation_enumeration(self):
        """Test navigation constants and enumeration."""
        print("\n📋 Testing navigation enumeration...")

        try:
            print(f"   📊 Available views: {len(NAVIGATION_ITEMS)}")

            for i, item in enumerate(NAVIGATION_ITEMS):
                view_name = item["view"]
                label = item["label"]

                # Test view name lookup
                index_by_view = get_index_by_view(view_name)
                view_by_index = get_view_by_index(i)

                if index_by_view == i and view_by_index == view_name:
                    print(f"   ✅ {i}: {label} ({view_name}) - lookups work")
                else:
                    print(f"   ❌ {i}: {label} ({view_name}) - lookup mismatch")

        except Exception as e:
            error_msg = f"Navigation enumeration failed: {e}"
            self.results.add_critical_error(error_msg)
            print(f"   ❌ {error_msg}")

    async def run_all_tests(self):
        """Run all navigation tests."""
        print("🚀 Starting Navigation Tests...")
        print("="*70)

        # Test 1: Setup
        if not self.setup_test_environment():
            return self.results

        # Test 2: Navigation enumeration
        self.test_navigation_enumeration()

        # Test 3: View instantiation
        instantiated_views = self.test_view_instantiation()

        # Test 4: View build methods
        self.test_view_build_methods(instantiated_views)

        # Test 5: ViewManager integration
        view_manager = self.test_view_manager_integration(instantiated_views)

        # Test 6: NavigationState integration
        self.test_navigation_state_integration(view_manager)

        return self.results


async def main():
    """Main test execution."""
    print("🧪 NAVIGATION SIMULATION TEST")
    print("Testing Flet GUI navigation without manual interaction")
    print("="*70)

    tester = NavigationTester()
    results = await tester.run_all_tests()
    results.print_summary()

    if results.overall_success:
        print("\n🎉 All tests passed! Navigation should work correctly.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Navigation may have issues.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        traceback.print_exc()
        sys.exit(1)
