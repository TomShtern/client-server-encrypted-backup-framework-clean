"""
Minimal diagnostic to find what import in main.py causes ft.run() to hang.
"""

import sys
import os

# Path setup from main.py
here_path = os.path.abspath(__file__)
base_dir = os.path.dirname(here_path)
parent_dir = os.path.dirname(base_dir)

if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

print("[STEP 1] Testing basic ft.run() with NO extra imports...")

import flet as ft  # noqa: E402 - Intentional delayed import for diagnostics


def simple_main(page: ft.Page):
    page.title = "Test"
    page.add(ft.Text("Working!"))


try:
    print("  Calling ft.run()...")
    ft.run(simple_main)
    print("  ft.run() returned")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n[STEP 2] Adding utf8_solution import...")
try:
    from Shared.filesystem.utf8_solution import utf8

    print("  utf8_solution imported")
    utf8.ensure_initialized()
    print("  utf8_solution initialized")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\n[STEP 3] Testing ft.run() with utf8_solution loaded...")


def test2(page: ft.Page):
    page.title = "Test 2"
    page.add(ft.Text("Still working!"))


try:
    print("  Calling ft.run()...")
    ft.run(test2)
    print("  ft.run() returned")
except Exception as e:
    print(f"  ERROR: {e}")

print("\n[STEP 4] Adding FletV2 components import...")
try:
    from FletV2.components.breadcrumb import BreadcrumbFactory  # noqa: F401 - Testing import side effects

    print("  breadcrumb imported")
except Exception as e:
    print(f"  ERROR: {e}")
    import traceback

    traceback.print_exc()

print("\n[STEP 5] Testing ft.run() with components loaded...")


def test3(page: ft.Page):
    page.title = "Test 3"
    page.add(ft.Text("Components loaded!"))


try:
    print("  Calling ft.run()...")
    ft.run(test3)
    print("  ft.run() returned")
except Exception as e:
    print(f"  ERROR: {e}")

print("\nDone with diagnostic tests")
