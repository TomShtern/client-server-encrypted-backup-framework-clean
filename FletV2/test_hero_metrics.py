#!/usr/bin/env python3
"""
Test script to check if hero_metrics_section is included in dashboard.
"""

import os
import sys
from unittest.mock import Mock

import flet as ft

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
    from utils.server_bridge import create_server_bridge
    from utils.state_manager import create_state_manager
    print("✅ Successfully imported create_dashboard_view and real components")

    # Mock page with proper spec (UI component, not data)
    mock_page = Mock(spec=ft.Page)

    # Use real server_bridge and state_manager (no mock data)
    try:
        server_bridge = create_server_bridge()
        state_manager = create_state_manager() # type: ignore
        print("✅ Using real server_bridge and state_manager")
    except Exception as e:
        print(f"❌ Failed to create real components: {e}")
        print("No real data available - cannot run test")
        sys.exit(1)

    # Try to create the dashboard (correct argument order: page, server_bridge, state_manager)
    print("🔄 Attempting to create dashboard...")
    result = create_dashboard_view(mock_page, server_bridge, state_manager)  # type: ignore
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