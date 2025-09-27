#!/usr/bin/env python3
"""
Test script to check if hero_metrics_section is included in dashboard.
"""

import os
import sys

# Add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
repo_root = os.path.dirname(parent_dir)

for path in (parent_dir, repo_root):
    if path not in sys.path:
        sys.path.insert(0, path)

# Set debug environment
os.environ['FLET_DASHBOARD_DEBUG'] = '1'
os.environ['FLET_DASHBOARD_DIAG_LAYOUT'] = '1'
os.environ['FLET_DASHBOARD_TEST_MARKER'] = '1'

try:
    from FletV2.views.dashboard import create_dashboard_view
    print("✅ Successfully imported create_dashboard_view")

    # Mock page and dependencies
    class MockPage:
        def update(self): pass
        def run_task(self, coro): pass

    class MockServerBridge:
        pass

    class MockStateManager:
        pass

    mock_page = MockPage()
    mock_server_bridge = MockServerBridge()
    mock_state_manager = MockStateManager()

    # Try to create the dashboard
    print("🔄 Attempting to create dashboard...")
    result = create_dashboard_view(mock_server_bridge, mock_page, mock_state_manager)
    print("✅ Dashboard creation completed")

    if isinstance(result, tuple) and len(result) == 3:
        dashboard_container, dispose_func, setup_func = result
        print("✅ Dashboard tuple structure is correct")

        # Check if dashboard_container has content
        if hasattr(dashboard_container, 'content'):
            main_content = dashboard_container.content
            print(f"✅ Dashboard container has content: {type(main_content)}")

            if hasattr(main_content, 'controls'):
                controls = main_content.controls
                print(f"✅ Main content has {len(controls)} controls")

                # Check if hero_metrics_section is in the controls
                hero_found = False
                for i, control in enumerate(controls):
                    if hasattr(control, '__class__') and 'ResponsiveRow' in str(control.__class__):
                        print(f"✅ Found ResponsiveRow at index {i} - likely hero_metrics_section")
                        hero_found = True
                        break

                if hero_found:
                    print("✅ Hero metrics section appears to be included in the layout")
                else:
                    print("❌ Hero metrics section not found in controls")
                    print("Controls types:", [type(c).__name__ for c in controls[:10]])
            else:
                print("❌ Main content has no controls attribute")
        else:
            print("❌ Dashboard container has no content attribute")
    else:
        print(f"❌ Unexpected return type: {result}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()