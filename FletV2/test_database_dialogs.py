#!/usr/bin/env python3
"""
Test script for database dialog functionality.
Run this to verify that edit and delete dialogs work properly.
"""

import flet as ft
import sys
import os

# Add the FletV2 directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from views.database import create_database_view
from utils.server_bridge import create_server_bridge
from utils.state_manager import StateManager

def main(page: ft.Page):
    """Test the database view dialogs."""
    page.title = "Database Dialog Test"
    page.window_width = 1200
    page.window_height = 800
    
    # Create test infrastructure
    server_bridge = create_server_bridge()  # Will use mock data
    state_manager = StateManager(page)
    
    # Create database view
    database_view = create_database_view(server_bridge, page, state_manager)
    
    # Add header
    page.add(
        ft.Text("Database Dialog Test", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Click the three-dot menu on any row to test edit/delete dialogs", size=14),
        ft.Divider(),
        database_view
    )

if __name__ == "__main__":
    print("Starting database dialog test...")
    print("- Click on the three-dot menu (⋮) on any row")
    print("- Select 'Edit Row' to test the edit dialog")
    print("- Select 'Delete Row' to test the delete confirmation dialog")
    print("- Check the console for dialog event logs")
    
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)