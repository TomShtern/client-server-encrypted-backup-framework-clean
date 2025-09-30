#!/usr/bin/env python3
"""
Start the FletV2 GUI in GUI-only mode with Lorem ipsum placeholder data.
This allows the interface to be demonstrated without requiring a real server.
"""

import os
import sys

# Enable GUI-only mode
os.environ['FLET_GUI_ONLY_MODE'] = '1'
os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'
os.environ['CYBERBACKUP_DISABLE_GUI'] = '1'

# Try bypassing AnimatedSwitcher to fix blank content area
os.environ['FLET_BYPASS_SWITCHER'] = '1'

# Enable debugging to see what's happening
os.environ['FLET_DASHBOARD_DEBUG'] = '1'
os.environ['FLET_DASHBOARD_CONTENT_DEBUG'] = '1'

# Optional: Disable heavy diagnostics
os.environ['FLET_DASHBOARD_TEST_MARKER'] = '0'
os.environ['FLET_DASHBOARD_PLACEHOLDER'] = '0'

print("Starting FletV2 GUI in demonstration mode...")
print("Using Lorem ipsum placeholder data")
print("GUI will be fully functional for interface demonstration")

# Import and run main
if __name__ == "__main__":
    import flet as ft
    import main

    # Run GUI-only mode with no server (triggering Lorem ipsum placeholder data)
    import asyncio

    async def gui_only_main(page):
        # FIX: Instantiate FletV2App directly instead of calling non-existent main.main()
        app = main.FletV2App(page, real_server=None)
        await app.initialize()

    ft.app(target=gui_only_main, view=ft.AppView.FLET_APP)