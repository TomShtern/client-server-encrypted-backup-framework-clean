#!/usr/bin/env python3
"""
Launch script for FletV2 with modularized experimental views.

This script launches the FletV2 application using the modularized experimental views
that implement the improved architecture patterns.
"""

import os
import sys

import flet as ft

# Add the FletV2 directory to the path
flet_v2_root = os.path.dirname(os.path.abspath(__file__))
if flet_v2_root not in sys.path:
    sys.path.insert(0, flet_v2_root)

# Import the modularized main application (the experimental version)
from main_exp import main as modularized_main


def main(page: ft.Page) -> None:
    """Main entry point that uses the modularized experimental views."""
    modularized_main(page)

if __name__ == "__main__":
    # Launch the modularized application
    print("🌐 Launching FletV2 with modularized experimental views...")
    try:
        ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8550)
    except OSError as e:
        print(f"Port 8550 in use ({e}), trying 8551...")
        try:
            ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8551)
        except OSError as e2:
            print(f"Port 8551 in use ({e2}), trying 8552...")
            ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8552)
    except Exception as e:
        print(f"❌ FATAL ERROR starting modularized Flet app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
