#!/usr/bin/env python3
"""
Test script for simple navigation rail system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import flet as ft
from flet_server_gui.utils.simple_navigation import SimpleNavigationState, create_simple_navigation_rail

def switch_view(view_name: str):
    print(f"Switching to view: {view_name}")

def main(page: ft.Page):
    page.title = "Simple Navigation Rail Test"
    page.window_width = 1000
    page.window_height = 700
    
    # Create simple navigation state
    nav_state = SimpleNavigationState()
    
    # Create simple navigation rail
    nav_rail = create_simple_navigation_rail(
        nav_state,
        switch_view,
        extended=False
    )
    
    # Create simple content
    content = ft.Container(
        content=ft.Text("Main Content Area", size=20),
        padding=20,
        expand=True
    )
    
    # Create layout
    layout = ft.Row([
        nav_rail,
        ft.VerticalDivider(width=1),
        content
    ], expand=True, spacing=0)
    
    page.add(layout)

if __name__ == "__main__":
    print("Starting Navigation Rail Test...")
    ft.app(target=main)