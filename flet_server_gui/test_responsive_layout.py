#!/usr/bin/env python3
"""
Test script to verify responsive layout and button functionality
"""
import flet as ft
import sys
import os

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

# Import utf8_solution to fix encoding issues
try:
    import Shared.utils.utf8_solution
    print("[INFO] UTF-8 solution imported successfully")
except ImportError as e:
    # Try alternative path
    utf8_path = os.path.join(os.path.dirname(__file__), "..", "Shared", "utils")
    if utf8_path not in sys.path:
        sys.path.insert(0, utf8_path)
    try:
        import utf8_solution
        print("[INFO] UTF-8 solution imported via alternative path")
    except ImportError:
        print("[WARNING] utf8_solution import failed, continuing without it")
        print(f"[DEBUG] Import error: {e}")

from flet_server_gui.layout.responsive import BreakpointManager
from flet_server_gui.layout.responsive import ResponsiveBuilder


def test_breakpoint_detection():
    """Test breakpoint detection at different screen widths"""
    test_cases = [
        (300, "xs"),
        (576, "sm"),
        (768, "md"),
        (992, "lg"),
        (1200, "xl"),
        (1400, "xxl"),
        (2000, "xxl")
    ]
    
    print("Testing breakpoint detection...")
    for width, expected in test_cases:
        current_breakpoint = BreakpointManager.get_current_breakpoint(width)
        status = "[PASS]" if current_breakpoint.value == expected else "[FAIL]"
        print(f"  {status} Width {width}px -> {current_breakpoint.value} (expected: {expected})")
    print()


def test_responsive_spacing():
    """Test responsive spacing calculations"""
    print("Testing responsive spacing...")
    widths = [300, 576, 768, 992, 1200, 1400]
    sizes = ["small", "medium", "large", "xlarge"]
    
    for width in widths:
        print(f"  Width {width}px:")
        for size in sizes:
            spacing = BreakpointManager.get_responsive_spacing(width, size)
            print(f"    {size}: {spacing}px")
    print()


def test_column_configurations():
    """Test column configurations for different breakpoints"""
    print("Testing column configurations...")
    breakpoints = [Breakpoint.XS, Breakpoint.SM, 
                  Breakpoint.MD, Breakpoint.LG,
                  Breakpoint.XL, Breakpoint.XXL]
    
    for bp in breakpoints:
        config = BreakpointManager.get_column_config(bp)
        print(f"  {bp.value}: {config}")
    print()


def main(page: ft.Page):
    """Main test application"""
    page.title = "Responsive Layout Test"
    page.window_width = 1200
    page.window_height = 800
    
    # Test responsive components
    test_breakpoint_detection()
    test_responsive_spacing()
    test_column_configurations()
    
    # Create a test layout
    def on_resize(e):
        width = page.window_width or 800
        height = page.window_height or 600
        breakpoint = BreakpointManager.get_current_breakpoint(width)
        
        status_text.value = f"Screen: {width}x{height}px - Breakpoint: {breakpoint.value}"
        page.update()
    
    page.on_resized = on_resize
    
    status_text = ft.Text("Resize the window to test responsive behavior")
    
    # Create responsive row with test components
    test_components = [
        ft.Container(
            content=ft.Text("Column 1", size=20),
            bgcolor=TOKENS['primary'],
            padding=20,
            expand=True
        ),
        ft.Container(
            content=ft.Text("Column 2", size=20),
            bgcolor=TOKENS['secondary'],
            padding=20,
            expand=True
        ),
        ft.Container(
            content=ft.Text("Column 3", size=20),
            bgcolor=TOKENS['secondary'],
            padding=20,
            expand=True
        )
    ]
    
    responsive_row = ResponsiveBuilder.create_responsive_row(test_components)
    
    page.add(
        ft.Column([
            ft.Text("Responsive Layout Test", size=30, weight=ft.FontWeight.BOLD),
            status_text,
            ft.Divider(),
            responsive_row
        ], expand=True)
    )
    
    # Trigger initial resize
    on_resize(None)


if __name__ == "__main__":
    print("Running responsive layout tests...")
    ft.app(target=main)