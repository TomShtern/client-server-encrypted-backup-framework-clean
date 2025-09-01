#!/usr/bin/env python3
"""
Simple UTF-8 Solution Test
"""

import sys
import os

# Add project root to path if needed
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_utf8_solution():
    """Test the UTF-8 solution import and basic functionality."""
    print("Testing UTF-8 solution...")
    
    try:
        # Import the UTF-8 solution
        import Shared.utils.utf8_solution as utf8_solution
        utf8_solution.safe_print("✅ UTF-8 solution imported successfully")
        
        # Test basic functionality
        result = utf8_solution.test_utf8()
        utf8_solution.safe_print(f"✅ UTF-8 test function result: {result}")
        
        # Test environment setup
        env = utf8_solution.get_env()
        utf8_solution.safe_print(f"✅ PYTHONUTF8 in environment: {env.get('PYTHONUTF8', 'NOT SET')}")
        utf8_solution.safe_print(f"✅ PYTHONIOENCODING in environment: {env.get('PYTHONIOENCODING', 'NOT SET')}")
        
        # Test safe print with Unicode
        utf8_solution.safe_print("✅ Safe print with Unicode: Hello 🌍, שלום עולם!")
        
        # Test Hebrew and emoji handling
        test_string = "Hebrew: בדיקה | Emoji: 🎉✅❌ | Mixed: קובץ_עברי_🔧_test.txt"
        utf8_solution.safe_print(f"✅ Test string: {test_string}")
        
        # Try encoding/decoding
        try:
            encoded = test_string.encode('utf-8')
            decoded = encoded.decode('utf-8')
            if test_string == decoded:
                utf8_solution.safe_print("✅ UTF-8 encode/decode cycle successful")
            else:
                utf8_solution.safe_print("❌ UTF-8 encode/decode cycle failed")
                return False
        except Exception as e:
            utf8_solution.safe_print(f"❌ UTF-8 encode/decode error: {e}")
            return False
            
        return result
        
    except ImportError as e:
        print(f"❌ Failed to import UTF-8 solution: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing UTF-8 solution: {e}")
        return False

if __name__ == "__main__":
    print("Starting UTF-8 solution test...")
    print(f"Python version: {sys.version}")
    print(f"System encoding: {sys.getdefaultencoding()}")
    print(f"File system encoding: {sys.getfilesystemencoding()}")
    
    # Import UTF-8 solution early to set up environment
    try:
        import Shared.utils.utf8_solution
        print("UTF-8 solution initialized")
    except Exception as e:
        print(f"Failed to initialize UTF-8 solution: {e}")
    
    success = test_utf8_solution()
    
    if success:
        Shared.utils.utf8_solution.safe_print("\n🎉 All UTF-8 solution tests passed!")
        sys.exit(0)
    else:
        Shared.utils.utf8_solution.safe_print("\n💥 UTF-8 solution tests failed!")
        sys.exit(1)