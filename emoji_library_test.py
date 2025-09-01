#!/usr/bin/env python3
"""
Emoji Display Test using emoji library
"""

import sys
import os
import emoji

# Add project root to path if needed
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def setup_utf8():
    """Setup UTF-8 encoding for proper emoji display."""
    try:
        # Set environment variables
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
        
        # Configure stdout/stderr for UTF-8
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
            
        print("UTF-8 encoding setup completed")
        return True
    except Exception as e:
        print(f"Error setting up UTF-8: {e}")
        return False

def test_emoji_library():
    """Test emoji display using the emoji library."""
    print("\n=== Emoji Library Test ===")
    
    # Test with emoji aliases
    emoji_tests = [
        ":party_popper: Party Popper",
        ":check_mark: Check Mark",
        ":cross_mark: Cross Mark",
        ":earth_globe: Earth Globe",
        ":rocket: Rocket",
        "Hello :earth_globe: World :check_mark:"
    ]
    
    for test in emoji_tests:
        emojized = emoji.emojize(test)
        try:
            print(f"Test: {emojized}")
        except Exception as e:
            print(f"Error displaying emoji: {e}")
            # Try with error handling
            safe_text = emojized.encode('utf-8', errors='replace').decode('utf-8')
            print(f"Safe: {safe_text}")

def test_direct_emojis():
    """Test direct emoji characters."""
    print("\n=== Direct Emoji Test ===")
    
    direct_emojis = [
        "🎉 Party Popper",
        "✅ Check Mark",
        "❌ Cross Mark",
        "🌍 Earth Globe",
        "🚀 Rocket",
        "שלום 🌍 עולם ✅"
    ]
    
    for text in direct_emojis:
        try:
            print(f"Direct: {text}")
        except Exception as e:
            print(f"Error with direct emoji: {e}")
            # Try with error handling
            safe_text = text.encode('utf-8', errors='replace').decode('utf-8')
            print(f"Safe direct: {safe_text}")

def test_utf8_solution_integration():
    """Test integration with our UTF-8 solution."""
    print("\n=== UTF-8 Solution Integration Test ===")
    
    try:
        import Shared.utils.utf8_solution as utf8_solution
        print("✅ UTF-8 solution imported successfully")
        
        # Test safe print with emojis
        test_strings = [
            "🎉 Party Popper",
            "✅ Check Mark",
            "❌ Cross Mark",
            "🌍 Earth Globe",
            "🚀 Rocket",
            "שלום 🌍 עולם ✅"
        ]
        
        for text in test_strings:
            utf8_solution.safe_print(f"Safe print: {text}")
            
    except Exception as e:
        print(f"❌ UTF-8 solution integration failed: {e}")

def main():
    """Main test function."""
    print("Emoji Display Test with UTF-8 Support")
    print("====================================")
    
    # Setup UTF-8
    setup_utf8()
    
    # Test different approaches
    test_emoji_library()
    test_direct_emojis()
    test_utf8_solution_integration()
    
    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    main()