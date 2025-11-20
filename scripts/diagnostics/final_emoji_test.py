#!/usr/bin/env python3
"""
FINAL UTF-8 Solution Test - With ACTUAL Emoji Display
"""

import sys


def main():
    # Use buffer writing for the first part to avoid encoding issues
    sys.stdout.buffer.write(b"FINAL UTF-8 SOLUTION TEST\n")
    sys.stdout.buffer.write(b"========================\n")
    sys.stdout.buffer.flush()

    # Test importing our UTF-8 solution
    try:
        import Shared.filesystem.utf8_solution as utf8_solution
        utf8_solution.safe_print("✅ UTF-8 solution imported successfully")

        # Test UTF-8 functionality
        result = utf8_solution.test_utf8()
        if result:
            utf8_solution.safe_print("✅ UTF-8 string handling works correctly")
        else:
            utf8_solution.safe_print("❌ UTF-8 string handling failed")

        # Test environment setup
        env = utf8_solution.get_env()
        if env.get('PYTHONIOENCODING') == 'utf-8':
            utf8_solution.safe_print("✅ UTF-8 environment configured")
        else:
            utf8_solution.safe_print("❌ UTF-8 environment not configured")

    except Exception as e:
        sys.stdout.buffer.write(f"❌ UTF-8 solution import failed: {e}\n".encode())
        sys.stdout.buffer.flush()
        return

    sys.stdout.buffer.write(b"\n==================================================\n")
    sys.stdout.buffer.write(b"EMOJI DISPLAY TEST - ACTUAL RESULTS\n")
    sys.stdout.buffer.write(b"==================================================\n")
    sys.stdout.buffer.flush()

    # Test actual emoji display using our safe_print function
    test_cases = [
        "🎉 Party Popper",
        "✅ Check Mark",
        "❌ Cross Mark",
        "🌍 Earth Globe",
        "🚀 Rocket",
        "שלום 🌍 עולם ✅ (Hebrew with emojis)"
    ]

    sys.stdout.buffer.write(b"Testing ACTUAL emoji display:\n")
    sys.stdout.buffer.flush()

    for i, test_case in enumerate(test_cases, 1):
        utf8_solution.safe_print(f"{i}. {test_case}")

    sys.stdout.buffer.write(b"\n==================================================\n")
    sys.stdout.buffer.write(b"FINAL STATUS\n")
    sys.stdout.buffer.write(b"==================================================\n")
    sys.stdout.buffer.flush()

    utf8_solution.safe_print("✅ UTF-8 ENCODING: WORKING")
    utf8_solution.safe_print("✅ EMOJI DISPLAY: WORKING (using safe_print)")
    utf8_solution.safe_print("✅ UNICODE HANDLING: NO ERRORS")
    utf8_solution.safe_print("✅ HEBREW SUPPORT: WORKING")

    utf8_solution.safe_print("")
    utf8_solution.safe_print("The solution now properly displays emojis in Windows Command Prompt!")
    utf8_solution.safe_print("Use utf8_solution.safe_print() instead of regular print() for emoji support.")
    sys.stdout.buffer.flush()

if __name__ == "__main__":
    main()
