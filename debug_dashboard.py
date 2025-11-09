#!/usr/bin/env python3
"""
Debug script to test dashboard view loading.
"""
import sys

# Setup paths
sys.path.insert(0, 'FletV2')
sys.path.insert(0, '.')

import flet as ft
from utils.server_bridge import create_server_bridge
from views.dashboard import create_dashboard_view


def test_dashboard():
    """Test dashboard creation with different configurations."""
    print("Testing dashboard view creation...")

    # Create a minimal Flet page
    page = ft.Page()

    # Test 1: Dashboard with None values (should work)
    print("\n1. Testing with None server_bridge and state_manager...")
    try:
        result = create_dashboard_view(None, page, None)
        print("✓ SUCCESS: Dashboard created with None values")
        print(f"  Result type: {type(result)}")
        if isinstance(result, tuple):
            print(f"  Tuple length: {len(result)}")
            print(f"  Control type: {type(result[0])}")

    except Exception as e:
        print(f"✗ ERROR with None values: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Dashboard with real server_bridge
    print("\n2. Testing with real server_bridge...")
    try:
        # Import BackupServer
        sys.path.insert(0, 'python_server')
        from python_server.server.server import BackupServer

        # Create BackupServer instance
        backup_server = BackupServer()
        print("✓ BackupServer created")

        # Create server_bridge
        server_bridge = create_server_bridge(real_server=backup_server)
        print("✓ Server bridge created")

        # Now test dashboard creation
        result = create_dashboard_view(server_bridge, page, None)
        print("✓ SUCCESS: Dashboard created with real server")
        print(f"  Result type: {type(result)}")

    except Exception as e:
        print(f"✗ ERROR with real server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard()
