#!/usr/bin/env python3
"""
Minimal test to check dashboard import and basic structure.
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

try:
    # Just try to import the dashboard module
    print("🔄 Attempting to import dashboard module...")
    from FletV2.views import dashboard
    print("✅ Successfully imported dashboard module")

    # Check if create_dashboard_view function exists
    if hasattr(dashboard, 'create_dashboard_view'):
        print("✅ create_dashboard_view function exists")
        print(f"   - Function: {dashboard.create_dashboard_view}")
    else:
        print("❌ create_dashboard_view function not found")

    # Check what other functions exist
    functions = [name for name in dir(dashboard) if not name.startswith('_')]
    print(f"📋 Available functions in dashboard module: {functions}")

except Exception as e:
    print(f"❌ Error during import: {e}")
    import traceback
    traceback.print_exc()