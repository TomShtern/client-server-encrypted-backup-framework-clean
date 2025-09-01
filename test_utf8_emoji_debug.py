#!/usr/bin/env python3
"""
Comprehensive UTF-8 Emoji Display Test
"""

import sys
import os
import ctypes

# Add project root to path if needed
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_console_settings():
    """Check current console settings."""
    print("=== Console Settings Check ===")
    print(f"Platform: {sys.platform}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"Filesystem encoding: {sys.getfilesystemencoding()}")
    print(f"Stdout encoding: {sys.stdout.encoding}")
    print(f"Stderr encoding: {sys.stderr.encoding}")
    
    # Check Windows console settings if on Windows
    if sys.platform == 'win32':
        try:
            kernel32 = ctypes.windll.kernel32
            console_cp = kernel32.GetConsoleCP()
            console_output_cp = kernel32.GetConsoleOutputCP()
            print(f"Console Input Code Page: {console_cp}")
            print(f"Console Output Code Page: {console_output_cp}")
        except Exception as e:
            print(f"Error checking console code pages: {e}")

def test_direct_print():
    """Test direct printing of emojis."""
    print("\n=== Direct Print Test ===")
    test_string = "🎉✅❌🌍🚀"
    try:
        print(f"Direct print: {test_string}")
        print("SUCCESS: Direct print worked")
    except Exception as e:
        print(f"FAILED: Direct print error: {e}")

def test_utf8_solution():
    """Test the UTF-8 solution."""
    print("\n=== UTF-8 Solution Test ===")
    
    try:
        import Shared.utils.utf8_solution as utf8_solution
        print("✅ UTF-8 solution imported successfully")
        
        # Check if setup worked
        result = utf8_solution.test_utf8()
        print(f"UTF-8 test result: {result}")
        
        # Test safe print
        utf8_solution.safe_print("Safe print test: 🎉✅❌🌍🚀")
        
        # Try enhanced safe print
        try:
            utf8_solution.enhanced_safe_print("Enhanced safe print test: 🎉✅❌🌍🚀")
        except Exception as e:
            print(f"Enhanced safe print error: {e}")
            
        return True
    except Exception as e:
        print(f"UTF-8 solution test failed: {e}")
        return False

def force_utf8_console():
    """Force UTF-8 console settings."""
    print("\n=== Force UTF-8 Console ===")
    
    if sys.platform == 'win32':
        try:
            kernel32 = ctypes.windll.kernel32
            # Force set UTF-8 code page
            result1 = kernel32.SetConsoleCP(65001)
            result2 = kernel32.SetConsoleOutputCP(65001)
            print(f"SetConsoleCP result: {result1}")
            print(f"SetConsoleOutputCP result: {result2}")
            
            # Check if it worked
            console_cp = kernel32.GetConsoleCP()
            console_output_cp = kernel32.GetConsoleOutputCP()
            print(f"New Console Input Code Page: {console_cp}")
            print(f"New Console Output Code Page: {console_output_cp}")
        except Exception as e:
            print(f"Error forcing UTF-8 console: {e}")

def test_with_forced_utf8():
    """Test emoji display after forcing UTF-8."""
    print("\n=== Test After Forcing UTF-8 ===")
    test_string = "🎉✅❌🌍🚀"
    try:
        print(f"After forcing UTF-8: {test_string}")
        print("SUCCESS: Emoji display after forcing UTF-8")
    except Exception as e:
        print(f"FAILED: Still can't display emojis: {e}")

if __name__ == "__main__":
    print("Starting Comprehensive UTF-8 Emoji Test...")
    
    check_console_settings()
    test_direct_print()
    test_utf8_solution()
    force_utf8_console()
    test_with_forced_utf8()
    
    print("\n=== Test Complete ===")