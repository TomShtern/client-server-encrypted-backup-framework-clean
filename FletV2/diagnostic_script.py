"""
Diagnostic script to pinpoint Flet hang issue.
Tests different Flet launch modes to isolate the problem.
"""

import sys

print("=" * 70)
print("Flet Diagnostic Script")
print("=" * 70)

print("\n[Step 1] Testing Flet import...")
try:
    import flet as ft

    print(f"✓ Flet {ft.__version__} imported successfully")
except Exception as e:
    print(f"✗ Flet import failed: {e}")
    sys.exit(1)

print("\n[Step 2] Testing synchronous function (should work)...")


def test_sync(page: ft.Page):
    print("  → test_sync() called")
    page.title = "Test"
    page.add(ft.Text("Sync test"))


try:
    print("  → Calling ft.app with sync function...")
    ft.app(target=test_sync, view=ft.AppView.FLET_APP)
    print("  ✓ ft.app() returned")
except Exception as e:
    print(f"  ✗ ft.app() failed: {e}")

print("\n[Step 3] Testing ft.run with sync function...")
try:
    print("  → Calling ft.run with sync function...")
    ft.run(test_sync, view=ft.AppView.FLET_APP)
    print("  ✓ ft.run() returned")
except Exception as e:
    print(f"  ✗ ft.run() failed: {e}")

print("\n[Step 4] Testing ft.run with async function...")


async def test_async(page: ft.Page):
    print("  → test_async() called")
    page.title = "Test Async"
    page.add(ft.Text("Async test"))


try:
    print("  → Calling ft.run with async function...")
    ft.run(test_async, view=ft.AppView.FLET_APP)
    print("  ✓ ft.run() returned")
except Exception as e:
    print(f"  ✗ ft.run() failed: {e}")

print("\n[Step 5] Testing WEB_BROWSER view (the failing mode)...")


async def test_web(page: ft.Page):
    print("  → test_web() called")
    page.title = "Web Test"
    page.add(ft.Text("Web browser mode"))


try:
    print("  → Calling ft.run with WEB_BROWSER view...")
    ft.run(test_web, view=ft.AppView.WEB_BROWSER, port=9999)
    print("  ✓ ft.run() returned")
except Exception as e:
    print(f"  ✗ ft.run() failed: {e}")

print("\n[Step 6] Testing with specific port 8550...")
try:
    print("  → Calling ft.run on port 8550...")
    ft.run(test_web, view=ft.AppView.WEB_BROWSER, port=8550)
    print("  ✓ ft.run() returned")
except Exception as e:
    print(f"  ✗ ft.run() failed: {e}")

print("\n" + "=" * 70)
print("Diagnostic complete")
print("=" * 70)
