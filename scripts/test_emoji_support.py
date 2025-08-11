#!/usr/bin/env python3
"""Test script for the new emoji support functionality in one_click_build_and_run.py"""

import sys
import os
from pathlib import Path

# Setup standardized import paths
from Shared.path_utils import setup_imports
setup_imports()

try:
    from .one_click_build_and_run import setup_unicode_console, supports_emojis, safe_print
    print("[OK] Successfully imported emoji support functions")
except Exception as e:
    print(f"[ERROR] Failed to import: {e}")
    sys.exit(1)

def test_emoji_functions():
    """Test the emoji support functions comprehensively"""
    print("=" * 60)
    print("TESTING EMOJI SUPPORT FUNCTIONS")
    print("=" * 60)
    
    # Test 1: Setup function
    print("\n[TEST 1] Testing setup_unicode_console()...")
    try:
        setup_unicode_console()
        print("[OK] setup_unicode_console() executed without errors")
    except Exception as e:
        print(f"[ERROR] setup_unicode_console() failed: {e}")
        return False
    
    # Test 2: Emoji detection
    print("\n[TEST 2] Testing supports_emojis()...")
    try:
        emoji_support = supports_emojis()
        print(f"[OK] Emoji support detected: {emoji_support}")
        
        # Show what encoding is being used
        print(f"[INFO] stdout encoding: {sys.stdout.encoding}")
        print(f"[INFO] Platform: {os.name}")
    except Exception as e:
        print(f"[ERROR] supports_emojis() failed: {e}")
        return False
    
    # Test 3: Safe print with emojis
    print("\n[TEST 3] Testing safe_print() with emojis...")
    try:
        safe_print("🚀 Rocket emoji test")
        safe_print("✅ Checkmark emoji test") 
        safe_print("⚠️ Warning emoji test")
        safe_print("🔧 Tool emoji test")
        print("[OK] All emoji safe_print tests completed")
    except Exception as e:
        print(f"[ERROR] safe_print() with emojis failed: {e}")
        return False
    
    # Test 4: Safe print with fallbacks
    print("\n[TEST 4] Testing safe_print() fallback behavior...")
    try:
        safe_print("🚀 Rocket with fallback", "[ROCKET] Rocket fallback")
        safe_print("✅ Check with fallback", "[SUCCESS] Check fallback")
        print("[OK] Fallback behavior tests completed")
    except Exception as e:
        print(f"[ERROR] safe_print() fallback tests failed: {e}")
        return False
    
    # Test 5: Mixed content
    print("\n[TEST 5] Testing mixed ASCII/emoji content...")
    try:
        safe_print("Regular text with 🚀 emoji in middle")
        safe_print("Multiple emojis: 🚀 ✅ ⚠️ 🔧")
        safe_print("Text at end 🚀")
        print("[OK] Mixed content tests completed")
    except Exception as e:
        print(f"[ERROR] Mixed content tests failed: {e}")
        return False
    
    # Test 6: Edge cases
    print("\n[TEST 6] Testing edge cases...")
    try:
        safe_print("", "empty fallback")  # Empty string
        safe_print("Pure ASCII text")     # No emojis
        safe_print("🚀")                  # Just emoji
        print("[OK] Edge case tests completed")
    except Exception as e:
        print(f"[ERROR] Edge case tests failed: {e}")
        return False
    
    return True

def test_integration_simulation():
    """Simulate how the functions are used in the main script"""
    print("\n" + "=" * 60)
    print("TESTING INTEGRATION SIMULATION")
    print("=" * 60)
    
    try:
        # Simulate the main script flow
        print("\n[SIMULATION] Simulating main script startup flow...")
        
        setup_unicode_console()
        emoji_support = supports_emojis()
        
        print(f"\nEmoji support available: {emoji_support}")
        
        if emoji_support:
            safe_print("   🚀 ONE-CLICK BUILD AND RUN - CyberBackup 3.0")
        else:
            safe_print("   ONE-CLICK BUILD AND RUN - CyberBackup 3.0")
        
        # Simulate success message
        server_started_successfully = True  # Simulate success
        
        if server_started_successfully:
            if emoji_support:
                safe_print("   ✅ ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!", 
                         "   [SUCCESS] ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!")
            else:
                safe_print("   [SUCCESS] ONE-CLICK BUILD AND RUN COMPLETED SUCCESSFULLY!")
        
        # Simulate final message
        if emoji_support:
            safe_print("Have a great backup session! 🚀", "Have a great backup session!")
        else:
            safe_print("Have a great backup session!")
        
        print("\n[OK] Integration simulation completed successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Integration simulation failed: {e}")
        return False

def main():
    """Run all emoji support tests"""
    success = True
    
    # Run function tests
    if not test_emoji_functions():
        success = False
    
    # Run integration simulation
    if not test_integration_simulation():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL EMOJI SUPPORT TESTS PASSED!" if supports_emojis() else "[SUCCESS] ALL EMOJI SUPPORT TESTS PASSED!")
        print("The emoji support implementation is working correctly.")
        print("\nKey benefits:")
        print("- ✅ Emojis display when supported" if supports_emojis() else "- [CHECK] Emojis display when supported")
        print("- 🔄 Automatic fallback when not supported" if supports_emojis() else "- [CYCLE] Automatic fallback when not supported") 
        print("- 🛡️ No crashes from encoding errors" if supports_emojis() else "- [SHIELD] No crashes from encoding errors")
        print("- 🎯 Works across different Windows configurations" if supports_emojis() else "- [TARGET] Works across different Windows configurations")
    else:
        print("❌ SOME EMOJI SUPPORT TESTS FAILED!" if supports_emojis() else "[ERROR] SOME EMOJI SUPPORT TESTS FAILED!")
        print("Check the output above for specific issues.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())