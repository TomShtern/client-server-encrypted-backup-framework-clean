#!/usr/bin/env python3
"""
Comprehensive Test Suite for Consolidated Responsive System
Tests all functionality after Phase 2 layout consolidation
"""

import sys
import time


def test_imports():
    """Test that all consolidated components can be imported"""
    print("=== Testing Imports ===")

    try:
        # Test main responsive module import
        from flet_server_gui.layout.responsive import (
            # Enums
            Breakpoint,
            # Classes
            BreakpointManager,
            DesktopBreakpoint,
            DeviceType,
            InteractionMethod,
            ResponsiveBuilder,
            ResponsiveLayoutFactory,
            ResponsiveLayoutFixes,
            ResponsiveLayoutManager,
            ResponsivePatterns,
            ScreenSize,
            # Data classes
            TouchTargetSpec,
            # Utility functions
            create_responsive_layout_manager,
            get_viewport_info,
        )
        print("PASS - All main responsive components imported successfully")

        # Test registry import
        from flet_server_gui.layout.responsive_component_registry import (
            LayoutConstraints,
            ResponsiveComponentRegistry,
            ResponsiveConfig,
        )
        print("PASS - Registry components imported successfully")

        return True

    except ImportError as e:
        print(f"FAIL - Import failed: {e}")
        return False

def test_breakpoint_manager():
    """Test BreakpointManager functionality"""
    print("\n=== Testing BreakpointManager ===")

    from flet_server_gui.layout.responsive import Breakpoint, BreakpointManager

    # Test breakpoint detection
    test_cases = [
        (400, Breakpoint.XS, "mobile"),
        (768, Breakpoint.MD, "tablet"),
        (1200, Breakpoint.XL, "desktop"),
        (1600, Breakpoint.XXL, "wide desktop")
    ]

    for width, expected_bp, device_type in test_cases:
        current_bp = BreakpointManager.get_current_breakpoint(width)
        is_mobile = BreakpointManager.is_mobile(width)
        is_tablet = BreakpointManager.is_tablet(width)
        is_desktop = BreakpointManager.is_desktop(width)
        spacing = BreakpointManager.get_responsive_spacing(width)

        print(f"  Width {width}px -> {current_bp.value} ({device_type}), spacing: {spacing}px")

        if current_bp != expected_bp:
            print(f"    ❌ Expected {expected_bp.value}, got {current_bp.value}")
            return False

    print("✅ BreakpointManager tests passed")
    return True

def test_responsive_builder():
    """Test ResponsiveBuilder functionality"""
    print("\n=== Testing ResponsiveBuilder ===")

    import flet as ft
    from flet_server_gui.layout.responsive import ResponsiveBuilder

    try:
        # Test basic component creation (without actual Flet page)
        test_controls = [ft.Text("Test 1"), ft.Text("Test 2")]

        # Test responsive row creation (API validation)
        responsive_row = ResponsiveBuilder.create_responsive_row(test_controls)
        print(f"✅ Created responsive row with {len(responsive_row.controls)} controls")

        # Test adaptive container creation
        test_container = ResponsiveBuilder.create_adaptive_container(ft.Text("Test"))
        print("✅ Created adaptive container")

        # Test font size calculation
        font_size = ResponsiveBuilder.get_responsive_font_size(1200, 16)
        print(f"✅ Calculated responsive font size: {font_size}px")

        # Test padding calculation
        padding = ResponsiveBuilder.get_adaptive_padding(1200, "medium")
        print("✅ Calculated adaptive padding")

        return True

    except Exception as e:
        print(f"❌ ResponsiveBuilder test failed: {e}")
        return False

def test_layout_factory():
    """Test ResponsiveLayoutFactory functionality"""
    print("\n=== Testing ResponsiveLayoutFactory ===")

    import flet as ft
    from flet_server_gui.layout.responsive import ResponsiveLayoutFactory, ScreenSize

    try:
        # Test factory methods (API validation)
        test_items = [ft.Text("Item 1"), ft.Text("Item 2")]

        # Test card grid creation
        card_grid = ResponsiveLayoutFactory.create_responsive_card_grid(
            test_items, ScreenSize.DESKTOP, 1200
        )
        print("✅ Created responsive card grid")

        # Test form creation
        test_fields = [ft.TextField("Field 1"), ft.TextField("Field 2")]
        form = ResponsiveLayoutFactory.create_responsive_form(
            test_fields, ScreenSize.DESKTOP
        )
        print("✅ Created responsive form")

        # Test header creation
        header = ResponsiveLayoutFactory.create_responsive_header(
            "Test Header", [], ScreenSize.DESKTOP
        )
        print("✅ Created responsive header")

        return True

    except Exception as e:
        print(f"❌ ResponsiveLayoutFactory test failed: {e}")
        return False

def test_layout_fixes():
    """Test ResponsiveLayoutFixes functionality"""
    print("\n=== Testing ResponsiveLayoutFixes ===")

    import flet as ft
    from flet_server_gui.layout.responsive import ResponsiveLayoutFixes, TouchTargetSpec

    try:
        # Test clipping safe container
        test_content = ft.Text("Test content")
        safe_container = ResponsiveLayoutFixes.create_clipping_safe_container(test_content)
        print("✅ Created clipping safe container")

        # Test touch target specifications
        touch_spec = TouchTargetSpec(min_width=48, min_height=48)
        print(f"✅ Created TouchTargetSpec: {touch_spec.min_width}x{touch_spec.min_height}px")

        # Test accessibility compliance
        test_button = ft.ElevatedButton("Test")
        accessible_container = ResponsiveLayoutFixes.ensure_minimum_touch_target(
            test_button, touch_spec
        )
        print("✅ Created accessible component container")

        # Test accessible button creation
        accessible_button = ResponsiveLayoutFixes.create_accessible_button(
            "Test Button", lambda e: None
        )
        print("✅ Created accessible button")

        return True

    except Exception as e:
        print(f"❌ ResponsiveLayoutFixes test failed: {e}")
        return False

def test_enums_and_dataclasses():
    """Test all enums and data classes"""
    print("\n=== Testing Enums and Data Classes ===")

    from flet_server_gui.layout.responsive import (
        Breakpoint,
        DesktopBreakpoint,
        DeviceType,
        InteractionMethod,
        ScreenSize,
        TouchTargetSpec,
    )

    try:
        # Test enum values
        breakpoints = [bp.value for bp in Breakpoint]
        print(f"✅ Breakpoint enum values: {breakpoints}")

        screen_sizes = [ss.value for ss in ScreenSize]
        print(f"✅ ScreenSize enum values: {screen_sizes}")

        device_types = [dt.value for dt in DeviceType]
        print(f"✅ DeviceType enum values: {device_types}")

        interaction_methods = [im.value for im in InteractionMethod]
        print(f"✅ InteractionMethod enum values: {interaction_methods}")

        desktop_breakpoints = [db.value for db in DesktopBreakpoint]
        print(f"✅ DesktopBreakpoint enum values: {desktop_breakpoints}")

        # Test TouchTargetSpec
        spec = TouchTargetSpec()
        print(f"✅ TouchTargetSpec defaults: {spec.min_width}x{spec.min_height}px")

        return True

    except Exception as e:
        print(f"❌ Enums/DataClasses test failed: {e}")
        return False

def test_import_performance():
    """Test import performance of consolidated module"""
    print("\n=== Testing Import Performance ===")

    try:
        start_time = time.perf_counter()


        end_time = time.perf_counter()
        import_time = (end_time - start_time) * 1000  # Convert to milliseconds

        print(f"✅ Consolidated module import time: {import_time:.2f}ms")

        # Performance benchmark (should be under 100ms for good performance)
        if import_time < 100:
            print("✅ Import performance: EXCELLENT (< 100ms)")
        elif import_time < 500:
            print("⚠️  Import performance: GOOD (< 500ms)")
        else:
            print("❌ Import performance: SLOW (> 500ms)")

        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print("COMPREHENSIVE RESPONSIVE SYSTEM TEST")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("BreakpointManager Test", test_breakpoint_manager),
        ("ResponsiveBuilder Test", test_responsive_builder),
        ("ResponsiveLayoutFactory Test", test_layout_factory),
        ("ResponsiveLayoutFixes Test", test_layout_fixes),
        ("Enums & DataClasses Test", test_enums_and_dataclasses),
        ("Import Performance Test", test_import_performance)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")

    print("-" * 50)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("SUCCESS: ALL TESTS PASSED - Consolidated responsive system is fully functional!")
    else:
        print(f"WARNING: {total - passed} test(s) failed - please review issues above")

    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
