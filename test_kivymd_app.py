# -*- coding: utf-8 -*-
"""
test_kivymd_app.py - Test script for the KivyMD application skeleton
Tests basic functionality and Material Design 3 Expressive theming
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import UTF-8 solution FIRST to fix encoding issues
try:
    import Shared.utils.utf8_solution
    print("[INFO] UTF-8 solution loaded successfully")
except ImportError:
    print("[WARNING] UTF-8 solution not available - encoding issues may occur")

def test_basic_imports():
    """Test that all KivyMD imports work correctly"""
    print("[TEST] Testing KivyMD imports...")
    
    try:
        from kivymd.app import MDApp
        from kivymd.uix.screen import MDScreen
        from kivymd.uix.label import MDLabel
        from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
        print("[OK] Basic KivyMD imports successful")
        return True
    except ImportError as e:
        print(f"[X] KivyMD import failed: {e}")
        return False

def test_theme_system():
    """Test the Material Design 3 Expressive theme system"""
    print("[TEST] Testing MD3 Expressive theme system...")
    
    try:
        from kivymd_gui.themes.custom_theme import CustomTheme
        
        # Test predefined themes
        themes = CustomTheme.THEMES
        print(f"[OK] Found {len(themes)} predefined themes: {list(themes.keys())}")
        
        # Test expressive styles
        expressive_styles = CustomTheme.EXPRESSIVE_STYLES
        print(f"[OK] Found {len(expressive_styles)} expressive styles: {list(expressive_styles.keys())}")
        
        # Test color harmonies
        harmonies = CustomTheme.COLOR_HARMONIES
        print(f"[OK] Found {len(harmonies)} color harmonies: {list(harmonies.keys())}")
        
        # Test dynamic theme generation
        dynamic_theme = CustomTheme.generate_expressive_theme_from_seed(
            "#FF5722", "complementary", "expressive"
        )
        print(f"[OK] Dynamic theme generation successful")
        print(f"    Primary: {dynamic_theme.get('primary', 'N/A')}")
        print(f"    Secondary: {dynamic_theme.get('secondary', 'N/A')}")
        print(f"    Harmony: {dynamic_theme.get('_harmony_type', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"[X] Theme system test failed: {e}")
        return False

def test_config_loading():
    """Test configuration loading"""
    print("[TEST] Testing configuration loading...")
    
    try:
        import json
        with open("kivymd_gui/config.json", "r") as f:
            config = json.load(f)
        
        # Check for expressive theming config
        expressive_config = config.get("app", {}).get("expressive_theming", {})
        print(f"[OK] Configuration loaded successfully")
        print(f"    Expressive theming enabled: {expressive_config.get('enable_dynamic', False)}")
        print(f"    Available harmonies: {len(expressive_config.get('available_harmonies', []))}")
        print(f"    Default harmony: {expressive_config.get('harmony', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"[X] Configuration test failed: {e}")
        return False

def test_screen_imports():
    """Test that screen implementations can be imported"""
    print("[TEST] Testing screen imports...")
    
    try:
        from kivymd_gui.screens.dashboard import DashboardScreen
        from kivymd_gui.screens.clients import ClientsScreen
        from kivymd_gui.screens.settings import SettingsScreen
        
        print("[OK] All screen imports successful")
        return True
    except Exception as e:
        print(f"[X] Screen import failed: {e}")
        return False

def test_server_integration():
    """Test server integration bridge"""
    print("[TEST] Testing server integration...")
    
    try:
        from kivymd_gui.utils.server_integration import ServerIntegrationBridge
        
        # Test creating bridge
        bridge = ServerIntegrationBridge()
        print("[OK] Server integration bridge created successfully")
        
        # Test basic methods
        server_info = bridge.get_server_info()
        print(f"[OK] Server info retrieved: {len(server_info)} fields")
        
        return True
    except Exception as e:
        print(f"[X] Server integration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results"""
    print("="*60)
    print("KivyMD Application Skeleton Tests")
    print("Material Design 3 Expressive Theme System")
    print("="*60)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("MD3 Expressive Theme System", test_theme_system),
        ("Configuration Loading", test_config_loading),
        ("Screen Imports", test_screen_imports),
        ("Server Integration", test_server_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print()
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[X] {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "OK PASS" if result else "X FAIL"
        print(f"{status:<8} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n** All tests passed! KivyMD application skeleton is ready.")
        print("   You can now run the main application with:")
        print("   python kivymd_gui/main.py")
    else:
        print(f"\n** {total - passed} tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)