# -*- coding: utf-8 -*-
"""
test_kivymd_minimal.py - Minimal test for components that don't require KivyMD
Tests configuration, theme system logic, and server integration without GUI dependencies
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
        print(f"    App title: {config.get('app', {}).get('title', 'N/A')}")
        print(f"    Material style: {config.get('app', {}).get('material_style', 'N/A')}")
        print(f"    Expressive theming enabled: {expressive_config.get('enable_dynamic', False)}")
        print(f"    Available harmonies: {len(expressive_config.get('available_harmonies', []))}")
        print(f"    Default harmony: {expressive_config.get('harmony', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"[X] Configuration test failed: {e}")
        return False

def test_theme_logic():
    """Test the Material Design 3 Expressive theme logic (without KivyMD)"""
    print("[TEST] Testing MD3 Expressive theme logic...")
    
    try:
        # Mock theme manager for testing
        class MockThemeManager:
            def __init__(self):
                self.theme_style = None
                self.primary_palette = None
                self.material_style = None
        
        # Import theme class
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
        
        # Test color conversion functions
        rgb_result = CustomTheme._rgb_to_hsl(0.5, 0.7, 0.9)
        print(f"[OK] RGB to HSL conversion: {rgb_result}")
        
        hex_result = CustomTheme._hsl_to_hex(240, 0.8, 0.6)
        print(f"[OK] HSL to hex conversion: {hex_result}")
        
        # Test dynamic theme generation
        dynamic_theme = CustomTheme.generate_expressive_theme_from_seed(
            "#FF5722", "complementary", "expressive"
        )
        print(f"[OK] Dynamic theme generation successful")
        print(f"    Primary: {dynamic_theme.get('primary', 'N/A')}")
        print(f"    Secondary: {dynamic_theme.get('secondary', 'N/A')}")
        print(f"    Harmony: {dynamic_theme.get('_harmony_type', 'N/A')}")
        print(f"    Expressive style: {dynamic_theme.get('_expressive_style', 'N/A')}")
        
        # Test theme application with mock
        mock_manager = MockThemeManager()
        CustomTheme.apply_theme(mock_manager, "Blue", "Dark")
        print(f"[OK] Theme application successful")
        print(f"    Applied style: {mock_manager.theme_style}")
        print(f"    Applied palette: {mock_manager.primary_palette}")
        print(f"    Material style: {mock_manager.material_style}")
        
        return True
    except Exception as e:
        print(f"[X] Theme logic test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_project_structure():
    """Test that project structure is correct"""
    print("[TEST] Testing project structure...")
    
    try:
        expected_files = [
            "kivymd_gui/main.py",
            "kivymd_gui/config.json",
            "kivymd_gui/themes/custom_theme.py",
            "kivymd_gui/screens/dashboard.py",
            "kivymd_gui/screens/clients.py", 
            "kivymd_gui/screens/settings.py",
            "kivymd_gui/utils/server_integration.py",
            "requirements.txt"
        ]
        
        missing_files = []
        for file_path in expected_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"[X] Missing files: {missing_files}")
            return False
        
        print(f"[OK] All {len(expected_files)} expected files found")
        
        # Check directories
        expected_dirs = [
            "kivymd_gui/screens",
            "kivymd_gui/themes",
            "kivymd_gui/utils",
            "kivymd_gui/components",
            "kivymd_gui/models",
            "kivymd_gui/assets"
        ]
        
        missing_dirs = []
        for dir_path in expected_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            print(f"[WARNING] Missing directories: {missing_dirs}")
        else:
            print(f"[OK] All {len(expected_dirs)} expected directories found")
        
        return True
    except Exception as e:
        print(f"[X] Project structure test failed: {e}")
        return False

def test_utf8_solution():
    """Test UTF-8 solution functionality"""
    print("[TEST] Testing UTF-8 solution...")
    
    try:
        # Test Unicode string handling
        test_strings = [
            "Regular ASCII text",
            "Hebrew text: שלום עולם",
            "Emojis: 🚀 📊 ⚙️ ✅",
            "Mixed: Server Status ✓ Running 🔥"
        ]
        
        for test_str in test_strings:
            try:
                # Try to print - this would fail without UTF-8 solution
                encoded = test_str.encode('utf-8').decode('utf-8')
                print(f"[OK] UTF-8 handling successful: {test_str[:30]}...")
            except UnicodeError as e:
                print(f"[X] UTF-8 handling failed for: {test_str[:30]}... - {e}")
                return False
        
        print("[OK] UTF-8 solution working correctly")
        return True
    except Exception as e:
        print(f"[X] UTF-8 solution test failed: {e}")
        return False

def run_minimal_tests():
    """Run tests that don't require KivyMD"""
    print("="*60)
    print("KivyMD Minimal Tests (No GUI Dependencies)")
    print("Material Design 3 Expressive Theme System")
    print("="*60)
    
    tests = [
        ("UTF-8 Solution", test_utf8_solution),
        ("Project Structure", test_project_structure),
        ("Configuration Loading", test_config_loading),
        ("MD3 Theme Logic", test_theme_logic)
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
        print("\n** All minimal tests passed!")
        print("   Core components are working correctly.")
        print("   To test full KivyMD functionality:")
        print("   1. Activate your kivy_venv environment")
        print("   2. Run: python kivymd_gui/main.py")
    else:
        print(f"\n** {total - passed} tests failed. Please check the implementation.")
    
    print("\nNext Steps:")
    print("1. Test in KivyMD environment: kivy_venv\\Scripts\\activate")
    print("2. Install requirements: pip install -r requirements.txt")
    print("3. Run main app: python kivymd_gui/main.py")
    
    return passed == total

if __name__ == "__main__":
    success = run_minimal_tests()
    sys.exit(0 if success else 1)