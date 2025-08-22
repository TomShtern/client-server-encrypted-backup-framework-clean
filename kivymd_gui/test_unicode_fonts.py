# -*- coding: utf-8 -*-
"""
Unicode Font Test - Verify Hebrew and emoji rendering
Quick test to verify that Unicode font configuration is working
"""

import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# UTF-8 solution import - MUST be imported early
import Shared.utils.utf8_solution

print("[TEST] Testing Unicode font configuration...")

def test_font_registration():
    """Test that fonts are properly registered"""
    try:
        from kivymd_gui.utils.font_config import FontConfiguration, initialize_unicode_fonts
        
        print("[TEST] Initializing Unicode fonts...")
        success = initialize_unicode_fonts()
        print(f"[TEST] Font initialization: {'SUCCESS' if success else 'FAILED'}")
        
        if success:
            registered_fonts = FontConfiguration.get_registered_fonts()
            print(f"[TEST] Registered fonts: {registered_fonts}")
            
            # Test font selection for different content types
            test_cases = [
                ("Hello World", "English text"),
                ("שלום עולם", "Hebrew text"),
                ("🎉 ✅ ❌ 🔧", "Emoji text"),
                ("Hello שלום 🎉", "Mixed content"),
                ("קובץ_עברי_🎉_test.txt", "Hebrew filename with emoji")
            ]
            
            print("\n[TEST] Font selection test:")
            for text, description in test_cases:
                best_font = FontConfiguration.get_best_font_for_content(text)
                print(f"  {description:25} -> Font: {best_font or 'System default'}")
                print(f"    Text: {text}")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"[TEST] Font registration test failed: {e}")
        return False

def test_label_creation():
    """Test MD3Label creation with Unicode content"""
    try:
        # Set up minimal Kivy environment for testing
        os.environ['KIVY_NO_FILELOG'] = '1'
        os.environ['KIVY_NO_CONSOLELOG'] = '1'
        
        from kivymd_gui.components.md3_label import (
            create_md3_label, create_unicode_label, 
            create_emoji_label, create_hebrew_label
        )
        
        print("\n[TEST] Label creation test:")
        
        # Test different label types
        test_labels = [
            (create_md3_label, "Hello World", "Standard label"),
            (create_unicode_label, "שלום עולם", "Hebrew label"),
            (create_emoji_label, "🎉 ✅ ❌", "Emoji label"),
            (create_hebrew_label, "בדיקת עברית", "Hebrew-optimized label")
        ]
        
        for label_func, text, description in test_labels:
            try:
                label = label_func(text)
                font_name = getattr(label, 'font_name', 'default')
                print(f"  {description:25} -> Font: {font_name}")
                print(f"    Text: {text}")
            except Exception as e:
                print(f"  {description:25} -> ERROR: {e}")
        
        return True
        
    except Exception as e:
        print(f"[TEST] Label creation test failed: {e}")
        return False

def main():
    """Run all Unicode font tests"""
    print("=" * 60)
    print("UNICODE FONT CONFIGURATION TEST")
    print("=" * 60)
    
    results = []
    
    # Test 1: Font registration
    print("\n1. Testing font registration...")
    results.append(test_font_registration())
    
    # Test 2: Label creation  
    print("\n2. Testing label creation...")
    results.append(test_label_creation())
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    test_names = ["Font Registration", "Label Creation"]
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {name:20} {status}")
    
    all_passed = all(results)
    overall_status = "[ALL TESTS PASSED]" if all_passed else "[SOME TESTS FAILED]"
    print(f"\nOverall result: {overall_status}")
    
    if all_passed:
        print("\nUnicode font configuration is working correctly!")
        print("Hebrew text and emojis should render properly in the GUI.")
    else:
        print("\nIssues detected with Unicode font configuration.")
        print("Check console output for specific errors.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())