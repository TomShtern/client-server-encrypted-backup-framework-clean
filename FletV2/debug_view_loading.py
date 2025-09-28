#!/usr/bin/env python3
"""
Debug script to test view loading step by step.
This will help identify where the dashboard loading is failing.
"""

import os
import sys

# Add the FletV2 directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
fletv2_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, fletv2_dir)

import flet as ft
import Shared.utils.utf8_solution as _  # noqa: F401


def test_step(description, test_func):
    """Helper function to run a test step with consistent error handling."""
    print(f"\n{description}")
    try:
        result = test_func()
        print(f"   ✅ {result}")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_view_loading():
    """Test the view loading process step by step."""
    print("=== FletV2 View Loading Debug Test ===\n")

    # Step 1: Test server bridge creation
    def step1():
        from utils.server_bridge import create_server_bridge
        server_bridge = create_server_bridge()
        return f"Server bridge created: {type(server_bridge)}, Is connected: {server_bridge.is_connected()}"

    if not test_step("1. Testing server bridge creation...", step1):
        return False

    # Create server bridge for other steps
    from utils.server_bridge import create_server_bridge
    server_bridge = create_server_bridge()

    # Step 2: Mock page creation (moved earlier to support state manager)
    print("\n2. Creating mock page...")
    try:
        class MockPage:
            def __init__(self):
                self.update = lambda: print("   📝 Mock page.update() called")
                self.run_task = lambda f: print(f"   📝 Mock page.run_task() called with {f}")

        mock_page = MockPage()
        print("   ✅ Mock page created")
    except Exception as e:
        print(f"   ❌ Mock page failed: {e}")
        return False

    # Step 3: Test state manager creation (now with mock_page)
    def step3():
        from utils.state_manager import create_state_manager
        state_manager = create_state_manager(mock_page)  # type: ignore
        return f"State manager created: {type(state_manager)}"

    if not test_step("3. Testing state manager creation...", step3):
        return False

    # Create state manager for other steps
    from utils.state_manager import create_state_manager
    state_manager = create_state_manager(mock_page)  # type: ignore

    # Step 4: Test dashboard view import
    def step4():
        from views.dashboard import create_dashboard_view
        return "Dashboard view imported successfully"

    if not test_step("4. Testing dashboard view import...", step4):
        return False

    # Import dashboard view for step 5
    from views.dashboard import create_dashboard_view

    # Step 5: Test view creation
    print("\n5. Testing dashboard view creation...")
    try:
        view_content, dispose_func, setup_func = create_dashboard_view(server_bridge, mock_page, state_manager)  # type: ignore
        print(f"   ✅ Dashboard view created: {type(view_content)}")
        print(f"   ✅ Dispose function: {type(dispose_func)}")
        print(f"   ✅ Setup function: {type(setup_func)}")
        print(f"   ✅ Has controls: {hasattr(view_content, 'controls')}")
        if hasattr(view_content, 'controls'):
            controls = getattr(view_content, 'controls', [])
            print(f"   ✅ Number of controls: {len(controls) if controls else 0}")
        print(f"   ✅ View is expandable: {getattr(view_content, 'expand', False)}")

        # Test if it's a valid Flet control
        print(f"   ✅ Is Flet control: {isinstance(view_content, ft.Control)}")

        # Test setup function
        print("   📝 Testing setup function...")
        setup_func()
        print("   ✅ Setup function executed successfully")

        return True
    except Exception as e:
        print(f"   ❌ Dashboard view creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_view_loading()

    print(f"\n=== Test Result: {'PASSED' if success else 'FAILED'} ===")
    if not success:
        print("❌ View loading has issues. Check the errors above.")
        exit(1)
    else:
        print("✅ All view loading tests passed!")
        print("   The issue might be in the main app initialization or AnimatedSwitcher update process.")
        exit(0)