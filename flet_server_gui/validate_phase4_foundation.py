"""
Phase 4 Foundation Validation Test
=================================

This script validates that the Phase 4 Material Design 3 consolidation foundation
has been properly set up and all new core modules can be imported successfully.

Run this script to verify:
1. Core directory structure is correct
2. New consolidation files can be imported
3. Basic functionality is accessible
4. No import errors or conflicts
"""

import sys
import os
import traceback
from pathlib import Path

# Add the flet_server_gui directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir.parent))

def test_imports():
    """Test all Phase 4 consolidation imports"""
    print("[TEST] Testing Phase 4 Foundation Imports...")
    
    tests = [
        # Core module imports
        ("Core Theme System", "flet_server_gui.core.theme_system", [
            "MaterialDesign3ThemeSystem", "theme_system", "get_theme_system",
            "ColorTokens", "TypographyTokens", "SpacingTokens", "ElevationTokens"
        ]),
        
        ("Core Design Tokens", "flet_server_gui.core.design_tokens", [
            "ColorRole", "TypographyRole", "LIGHT_COLOR_TOKENS", "DARK_COLOR_TOKENS",
            "TYPOGRAPHY_TOKENS", "SPACING_TOKENS", "ELEVATION_TOKENS",
            "get_color_token", "get_typography_token"
        ]),
        
        ("Core Responsive Layout", "flet_server_gui.core.responsive_layout", [
            "ResponsiveLayoutSystem", "BreakpointSize", "DeviceType", "Breakpoint",
            "responsive_layout_system", "get_responsive_layout_system"
        ]),
        
        ("Core Module Combined", "flet_server_gui.core", [
            "MaterialDesign3ThemeSystem", "ResponsiveLayoutSystem", "ColorRole",
            "theme_system", "responsive_layout_system"
        ])
    ]
    
    results = []
    
    for test_name, module_name, expected_attrs in tests:
        try:
            print(f"  [MODULE] Testing {test_name}...")
            module = __import__(module_name, fromlist=expected_attrs)
            
            missing_attrs = []
            for attr in expected_attrs:
                if not hasattr(module, attr):
                    missing_attrs.append(attr)
            
            if missing_attrs:
                print(f"    [FAIL] Missing attributes: {missing_attrs}")
                results.append((test_name, False, f"Missing: {missing_attrs}"))
            else:
                print(f"    [PASS] All attributes available")
                results.append((test_name, True, "All imports successful"))
                
        except ImportError as e:
            print(f"    [FAIL] Import error: {e}")
            results.append((test_name, False, f"Import error: {e}"))
        except Exception as e:
            print(f"    [FAIL] Unexpected error: {e}")
            results.append((test_name, False, f"Unexpected error: {e}"))
    
    return results


def test_basic_functionality():
    """Test basic functionality of Phase 4 systems"""
    print("\n[FUNC] Testing Basic Functionality...")
    
    results = []
    
    try:
        # Test theme system creation
        print("  [THEME] Testing theme system initialization...")
        from flet_server_gui.core import MaterialDesign3ThemeSystem, theme_system
        
        # Create new theme system
        custom_theme = MaterialDesign3ThemeSystem()
        print("    [PASS] Theme system creation - PASS")
        
        # Test global instance access
        global_theme = theme_system
        print("    [PASS] Global theme instance access - PASS")
        
        results.append(("Theme System", True, "Basic functionality working"))
        
    except Exception as e:
        print(f"    [FAIL] Theme system test failed: {e}")
        results.append(("Theme System", False, f"Error: {e}"))
    
    try:
        # Test responsive layout system
        print("  [RESPONSIVE] Testing responsive layout system...")
        from flet_server_gui.core import ResponsiveLayoutSystem, responsive_layout_system
        
        # Create new responsive system
        custom_responsive = ResponsiveLayoutSystem()
        print("    [PASS] Responsive system creation - PASS")
        
        # Test breakpoint detection
        breakpoint = custom_responsive.get_breakpoint_for_width(800)
        print(f"    [PASS] Breakpoint detection - PASS (width=800 -> {breakpoint.name})")
        
        results.append(("Responsive System", True, "Basic functionality working"))
        
    except Exception as e:
        print(f"    [FAIL] Responsive system test failed: {e}")
        results.append(("Responsive System", False, f"Error: {e}"))
    
    try:
        # Test design tokens access
        print("  [TOKENS] Testing design tokens access...")
        from flet_server_gui.core import get_color_token, get_typography_token, ColorRole, TypographyRole
        
        # Test color token access
        primary_color = get_color_token(ColorRole.PRIMARY)
        print(f"    [PASS] Color token access - PASS (primary: {primary_color})")
        
        # Test typography token access
        body_style = get_typography_token(TypographyRole.BODY_MEDIUM)
        print(f"    [PASS] Typography token access - PASS (body style keys: {list(body_style.keys())})")
        
        results.append(("Design Tokens", True, "Token access working"))
        
    except Exception as e:
        print(f"    [FAIL] Design tokens test failed: {e}")
        results.append(("Design Tokens", False, f"Error: {e}"))
    
    return results


def test_file_structure():
    """Test that the Phase 4 file structure is correct"""
    print("\n[FILES] Testing File Structure...")
    
    expected_files = [
        "core/__init__.py",
        "core/theme_system.py",
        "core/design_tokens.py", 
        "core/responsive_layout.py",
        "core/client_management.py",
        "core/file_management.py",
        "core/server_operations.py",
        "core/system_integration.py"
    ]
    
    results = []
    base_path = Path(__file__).parent
    
    for file_path in expected_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"  [EXISTS] {file_path}")
            results.append((file_path, True, "File exists"))
        else:
            print(f"  [MISSING] {file_path}")
            results.append((file_path, False, "File missing"))
    
    return results


def main():
    """Main validation function"""
    print("=" * 60)
    print("Phase 4 Material Design 3 Consolidation Foundation Test")
    print("=" * 60)
    
    all_results = []
    
    # Test file structure
    structure_results = test_file_structure()
    all_results.extend(structure_results)
    
    # Test imports
    import_results = test_imports()
    all_results.extend(import_results)
    
    # Test basic functionality  
    functionality_results = test_basic_functionality()
    all_results.extend(functionality_results)
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in all_results if success)
    total = len(all_results)
    
    print(f"[PASS] Passed: {passed}/{total}")
    print(f"[FAIL] Failed: {total - passed}/{total}")
    
    if total - passed > 0:
        print(f"\n[FAILED TESTS]:")
        for name, success, message in all_results:
            if not success:
                print(f"  - {name}: {message}")
    
    success_rate = (passed / total) * 100
    print(f"\n[SUCCESS RATE] {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("[READY] Phase 4 foundation is ready for consolidation!")
    elif success_rate >= 75:
        print("[WARNING] Phase 4 foundation mostly ready, minor issues to resolve")
    else:
        print("[ERROR] Phase 4 foundation needs attention before proceeding")
    
    return success_rate >= 90


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] {e}")
        traceback.print_exc()
        sys.exit(1)