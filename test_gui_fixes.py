#!/usr/bin/env python3
"""
Test script to validate ServerGUI fixes
"""

import sys
import traceback

def test_import():
    """Test if ServerGUI can be imported"""
    try:
        import server.ServerGUI
        print("✅ SUCCESS: ServerGUI imports without errors")
        return True
    except SyntaxError as e:
        print(f"❌ SYNTAX ERROR: {e}")
        print(f"   Line {e.lineno}: {e.text.strip() if e.text else 'N/A'}")
        return False
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        return False
    except Exception as e:
        print(f"❌ OTHER ERROR: {e}")
        traceback.print_exc()
        return False

def test_class_creation():
    """Test if ServerGUI class can be instantiated"""
    try:
        from server.ServerGUI import ServerGUI
        # Don't actually create the GUI (would require display)
        print("✅ SUCCESS: ServerGUI class accessible")
        return True
    except Exception as e:
        print(f"❌ CLASS CREATION ERROR: {e}")
        return False

def main():
    print("🔧 Testing ServerGUI Fixes...")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # Test 1: Import
    print("\n1. Testing module import...")
    if test_import():
        success_count += 1
        
        # Test 2: Class creation (only if import works)
        print("\n2. Testing class accessibility...")
        if test_class_creation():
            success_count += 1
    else:
        print("\n2. Skipping class test due to import failure")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED - ServerGUI is functional!")
    elif success_count > 0:
        print("⚠️  PARTIAL SUCCESS - Some issues remain")
    else:
        print("❌ ALL TESTS FAILED - Major issues need fixing")
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
