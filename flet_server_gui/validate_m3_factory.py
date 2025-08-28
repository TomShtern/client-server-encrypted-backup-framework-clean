#!/usr/bin/env python3
"""
Material Design 3 Component Factory Validation
==============================================

This script validates that the M3 component factory integrates properly
with the existing theme system and all imports work correctly.

Usage:
    python flet_server_gui/validate_m3_factory.py
"""

import sys
import traceback
from typing import Dict, List, Any


def safe_print(message: str):
    """Safe printing function for console output"""
    try:
        print(message)
    except UnicodeEncodeError:
        clean_msg = ''.join(char if ord(char) < 128 else '?' for char in message)
        print(clean_msg)


def test_imports() -> Dict[str, bool]:
    """Test all required imports"""
    results = {}
    
    safe_print("🔍 Testing imports...")
    
    # Test core imports
    try:
        import flet as ft
        results["flet"] = True
        safe_print("✅ Flet imported successfully")
    except Exception as e:
        results["flet"] = False
        safe_print(f"❌ Flet import failed: {e}")
    
    # Test theme system imports
    try:
        from core.theme_system import get_theme_system, ThemeMode, MaterialDesign3ThemeSystem
        results["theme_system"] = True
        safe_print("✅ Theme system imported successfully")
    except Exception as e:
        results["theme_system"] = False
        safe_print(f"❌ Theme system import failed: {e}")
    
    # Test design tokens imports
    try:
        from core.design_tokens import (
            ColorRole, TypographyRole, get_color_token, get_typography_token,
            get_spacing_token, get_elevation_token, BUTTON_TOKENS, CARD_TOKENS
        )
        results["design_tokens"] = True
        safe_print("✅ Design tokens imported successfully")
    except Exception as e:
        results["design_tokens"] = False
        safe_print(f"❌ Design tokens import failed: {e}")
    
    # Test M3 component factory imports
    try:
        from ui.m3_components import (
            M3ComponentFactory, ComponentStyle, StateLayer,
            M3ComponentConfig, M3ButtonConfig, M3CardConfig,
            get_m3_factory, create_m3_button, create_m3_card
        )
        results["m3_components"] = True
        safe_print("✅ M3 component factory imported successfully")
    except Exception as e:
        results["m3_components"] = False
        safe_print(f"❌ M3 component factory import failed: {e}")
        safe_print(f"   Traceback: {traceback.format_exc()}")
    
    return results


def test_factory_creation() -> Dict[str, bool]:
    """Test M3 component factory creation and basic functionality"""
    results = {}
    
    safe_print("\n🏭 Testing factory creation...")
    
    try:
        from ui.m3_components import get_m3_factory, ComponentStyle
        
        # Get factory instance
        factory = get_m3_factory()
        results["factory_creation"] = True
        safe_print("✅ M3ComponentFactory instance created successfully")
        
        # Test theme system integration
        theme_system = factory.theme_system
        if theme_system is not None:
            results["theme_integration"] = True
            safe_print("✅ Theme system integration working")
        else:
            results["theme_integration"] = False
            safe_print("❌ Theme system integration failed")
        
        # Test component style enum
        styles = [ComponentStyle.FILLED, ComponentStyle.OUTLINED, ComponentStyle.TEXT]
        results["component_styles"] = True
        safe_print("✅ Component style enums accessible")
        
    except Exception as e:
        results["factory_creation"] = False
        results["theme_integration"] = False
        results["component_styles"] = False
        safe_print(f"❌ Factory creation failed: {e}")
        safe_print(f"   Traceback: {traceback.format_exc()}")
    
    return results


def test_component_creation() -> Dict[str, bool]:
    """Test basic component creation without requiring full Flet app"""
    results = {}
    
    safe_print("\n🎨 Testing component creation...")
    
    try:
        from ui.m3_components import get_m3_factory, M3ButtonConfig, M3CardConfig, ComponentStyle
        import flet as ft
        
        factory = get_m3_factory()
        
        # Test button creation
        try:
            button = factory.create_button(
                style="filled",
                text="Test Button",
                icon=ft.Icons.STAR
            )
            results["button_creation"] = True
            safe_print("✅ Button creation successful")
        except Exception as e:
            results["button_creation"] = False
            safe_print(f"❌ Button creation failed: {e}")
        
        # Test card creation
        try:
            card = factory.create_card(
                style="elevated",
                title="Test Card",
                content=ft.Text("Test content")
            )
            results["card_creation"] = True
            safe_print("✅ Card creation successful")
        except Exception as e:
            results["card_creation"] = False
            safe_print(f"❌ Card creation failed: {e}")
        
        # Test input component creation
        try:
            text_field = factory.create_text_field(
                label="Test Field",
                hint_text="Enter text..."
            )
            results["input_creation"] = True
            safe_print("✅ Input component creation successful")
        except Exception as e:
            results["input_creation"] = False
            safe_print(f"❌ Input component creation failed: {e}")
        
        # Test convenience functions
        try:
            from ui.m3_components import create_m3_button, create_m3_card, create_m3_text_field
            
            conv_button = create_m3_button("outlined", "Convenience Button")
            conv_card = create_m3_card("filled", ft.Text("Convenience Card"))
            conv_field = create_m3_text_field("Convenience Field")
            
            results["convenience_functions"] = True
            safe_print("✅ Convenience functions working")
        except Exception as e:
            results["convenience_functions"] = False
            safe_print(f"❌ Convenience functions failed: {e}")
        
    except Exception as e:
        results["button_creation"] = False
        results["card_creation"] = False
        results["input_creation"] = False
        results["convenience_functions"] = False
        safe_print(f"❌ Component creation test setup failed: {e}")
    
    return results


def test_theme_integration() -> Dict[str, bool]:
    """Test theme system integration"""
    results = {}
    
    safe_print("\n🎨 Testing theme integration...")
    
    try:
        from ui.m3_components import get_m3_factory
        from core.theme_system import ThemeMode
        from core.design_tokens import ColorRole, get_color_token
        
        factory = get_m3_factory()
        
        # Test color resolution
        try:
            primary_light = factory._resolve_color(ColorRole.PRIMARY, is_dark=False)
            primary_dark = factory._resolve_color(ColorRole.PRIMARY, is_dark=True)
            results["color_resolution"] = True
            safe_print("✅ Color resolution working")
            safe_print(f"   Light primary: {primary_light}")
            safe_print(f"   Dark primary: {primary_dark}")
        except Exception as e:
            results["color_resolution"] = False
            safe_print(f"❌ Color resolution failed: {e}")
        
        # Test theme switching
        try:
            factory.theme_system.switch_theme(ThemeMode.LIGHT)
            factory.theme_system.switch_theme(ThemeMode.DARK)
            results["theme_switching"] = True
            safe_print("✅ Theme switching working")
        except Exception as e:
            results["theme_switching"] = False
            safe_print(f"❌ Theme switching failed: {e}")
        
        # Test typography integration
        try:
            from core.design_tokens import TypographyRole, get_typography_token
            typography = get_typography_token(TypographyRole.BODY_LARGE)
            results["typography_integration"] = True
            safe_print("✅ Typography integration working")
            safe_print(f"   Body large size: {typography.get('font_size')}")
        except Exception as e:
            results["typography_integration"] = False
            safe_print(f"❌ Typography integration failed: {e}")
        
    except Exception as e:
        results["color_resolution"] = False
        results["theme_switching"] = False
        results["typography_integration"] = False
        safe_print(f"❌ Theme integration test setup failed: {e}")
    
    return results


def print_summary(all_results: Dict[str, Dict[str, bool]]):
    """Print validation summary"""
    safe_print("\n" + "="*60)
    safe_print("📊 VALIDATION SUMMARY")
    safe_print("="*60)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        safe_print(f"\n📂 {category.replace('_', ' ').title()}:")
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            safe_print(f"   {test_name.replace('_', ' ').title()}: {status}")
            total_tests += 1
            if passed:
                passed_tests += 1
    
    safe_print(f"\n📈 Overall Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        safe_print("🎉 ALL TESTS PASSED! M3 Component Factory is ready for use.")
    elif passed_tests >= total_tests * 0.8:
        safe_print("⚠️ Most tests passed. Minor issues may exist but factory should work.")
    else:
        safe_print("❌ Major issues detected. Factory may not work properly.")
    
    # Integration advice
    safe_print("\n💡 Integration Notes:")
    safe_print("• Use get_m3_factory() to get the global factory instance")
    safe_print("• Use convenience functions (create_m3_button, etc.) for quick component creation")
    safe_print("• Factory automatically integrates with existing theme system")
    safe_print("• All components follow Material Design 3 specifications")
    safe_print("• Responsive design is enabled by default")


def main():
    """Run all validation tests"""
    safe_print("🚀 Material Design 3 Component Factory Validation")
    safe_print("=" * 60)
    
    all_results = {}
    
    # Run all test suites
    all_results["imports"] = test_imports()
    all_results["factory_creation"] = test_factory_creation()
    all_results["component_creation"] = test_component_creation()
    all_results["theme_integration"] = test_theme_integration()
    
    # Print summary
    print_summary(all_results)
    
    # Return success status
    total_tests = sum(len(results) for results in all_results.values())
    passed_tests = sum(sum(results.values()) for results in all_results.values())
    
    return passed_tests == total_tests


if __name__ == "__main__":
    try:
        success = main()
        exit_code = 0 if success else 1
        safe_print(f"\n🏁 Validation completed with exit code: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        safe_print(f"\n💥 Validation failed with exception: {e}")
        safe_print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)