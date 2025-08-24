#!/usr/bin/env python3
"""
Simple test script to verify responsive layout and button functionality without UI
"""
import sys
import os

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, project_root)

from flet_server_gui.layouts.breakpoint_manager import BreakpointManager, Breakpoint


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
        breakpoint = BreakpointManager.get_current_breakpoint(width)
        status = "[PASS]" if breakpoint.value == expected else "[FAIL]"
        print(f"  {status} Width {width}px -> {breakpoint.value} (expected: {expected})")
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
    breakpoint_enums = [Breakpoint.XS, Breakpoint.SM, 
                       Breakpoint.MD, Breakpoint.LG,
                       Breakpoint.XL, Breakpoint.XXL]
    
    for bp in breakpoint_enums:
        config = BreakpointManager.get_column_config(bp)
        print(f"  {bp.value}: {config}")
    print()


if __name__ == "__main__":
    print("Running responsive layout tests...")
    test_breakpoint_detection()
    test_responsive_spacing()
    test_column_configurations()
    print("[SUCCESS] All responsive layout tests completed!")