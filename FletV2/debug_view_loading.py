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

def test_view_loading():
    """Test the view loading process step by step."""
    print("=== FletV2 View Loading Debug Test ===\n")

    # Step 1: Test server bridge creation
    print("1. Testing server bridge creation...")
    try:
        from utils.server_bridge import create_server_bridge
        server_bridge = create_server_bridge()
        print(f"   ✅ Server bridge created: {type(server_bridge)}")
        print(f"   ✅ Is connected: {server_bridge.is_connected()}")
    except Exception as e:
        print(f"   ❌ Server bridge failed: {e}")
        return False

    # Step 2: Test state manager creation
    print("\n2. Testing state manager creation...")
    try:
        from utils.state_manager import create_state_manager
        state_manager = create_state_manager()
        print(f"   ✅ State manager created: {type(state_manager)}")
    except Exception as e:
        print(f"   ❌ State manager failed: {e}")
        return False

    # Step 3: Test dashboard view import
    print("\n3. Testing dashboard view import...")
    try:
        from views.dashboard import create_dashboard_view
        print("   ✅ Dashboard view imported successfully")
    except Exception as e:
        print(f"   ❌ Dashboard import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Mock page creation
    print("\n4. Creating mock page...")
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

    # Step 5: Test view creation
    print("\n5. Testing dashboard view creation...")
    try:
        view_content = create_dashboard_view(server_bridge, mock_page, state_manager)
        print(f"   ✅ Dashboard view created: {type(view_content)}")
        print(f"   ✅ Has controls: {hasattr(view_content, 'controls')}")
        if hasattr(view_content, 'controls'):
            controls = getattr(view_content, 'controls', [])
            print(f"   ✅ Number of controls: {len(controls) if controls else 0}")
        print(f"   ✅ View is expandable: {getattr(view_content, 'expand', False)}")

        # Test if it's a valid Flet control
        print(f"   ✅ Is Flet control: {isinstance(view_content, ft.Control)}")

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