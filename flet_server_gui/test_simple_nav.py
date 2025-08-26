#!/usr/bin/env python3
"""
Simple test to check navigation rail rendering
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import flet as ft

def main(page: ft.Page):
    page.title = "Navigation Rail Test"
    page.window_width = 800
    page.window_height = 600
    
    # Create simple navigation rail with known good colors
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=100,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.DASHBOARD_OUTLINED,
                selected_icon=ft.Icons.DASHBOARD,
                label="Dashboard"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.PEOPLE_OUTLINE,
                selected_icon=ft.Icons.PEOPLE,
                label="Clients"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.FOLDER_OUTLINED,
                selected_icon=ft.Icons.FOLDER,
                label="Files"
            ),
        ],
        bgcolor=ft.Colors.SURFACE,  # This might be causing the issue
        on_change=lambda e: print(f"Selected index: {e.control.selected_index}")
    )
    
    # Create simple content
    content = ft.Container(
        content=ft.Text("Main Content", size=30),
        alignment=ft.alignment.center,
        expand=True
    )
    
    # Create layout
    layout = ft.Row([
        nav_rail,
        ft.VerticalDivider(width=1),
        content
    ], expand=True)
    
    page.add(layout)

if __name__ == "__main__":
    print("Starting simple navigation rail test...")
    ft.app(target=main)