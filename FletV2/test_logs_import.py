#!/usr/bin/env python3
"""Test script to verify logs view imports and components work."""
import sys
import traceback

print("=" * 60)
print("Testing Logs View Components")
print("=" * 60)

# Test 1: Import flet
print("\n1. Testing Flet import...")
try:
    import flet as ft
    print("   ✅ Flet imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import Flet: {e}")
    sys.exit(1)

# Test 2: Check for required controls
print("\n2. Checking required Flet controls...")
required_controls = [
    'ProgressRing',
    'SegmentedButton',
    'Segment',
    'TextSpan',
    'TextStyle',
    'AnimatedSwitcher',
    'Stack',
    'IconButton',
]

missing = []
for control in required_controls:
    if hasattr(ft, control):
        print(f"   ✅ {control} exists")
    else:
        print(f"   ❌ {control} MISSING!")
        missing.append(control)

if missing:
    print(f"\n   ⚠️  Missing controls: {', '.join(missing)}")
    print("   This Flet version may be too old!")
    sys.exit(1)

# Test 3: Import logs view
print("\n3. Testing logs view import...")
try:
    from views.logs import create_logs_view
    print("   ✅ Logs view imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import logs view:")
    print(f"   Error: {type(e).__name__}: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check for syntax errors in the module
print("\n4. Checking module structure...")
try:
    import views.logs as logs_module
    print(f"   ✅ Module loaded, size: {len(dir(logs_module))} attributes")
except Exception as e:
    print(f"   ❌ Module error: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nIf the GUI still doesn't load, check the browser console (F12)")
print("for runtime errors during view creation.")
