#!/usr/bin/env python3
"""
Console Encoding Checker

This script checks your current console encoding and provides solutions
to change from cp1255 to UTF-8.
"""

import locale
import os
import subprocess
import sys


def check_current_encoding():
    """Check and display current encoding settings."""
    print("=== Current Encoding Status ===")

    # Python encoding settings
    print(f"Python default encoding: {sys.getdefaultencoding()}")
    print(f"Python filesystem encoding: {sys.getfilesystemencoding()}")
    print(f"Python stdout encoding: {sys.stdout.encoding}")
    print(f"Python stderr encoding: {sys.stderr.encoding}")

    # Environment variables
    print(f"PYTHONIOENCODING: {os.environ.get('PYTHONIOENCODING', 'Not set')}")

    # System locale
    try:
        system_locale = locale.getpreferredencoding()
        print(f"System preferred encoding: {system_locale}")
    except:
        print("System preferred encoding: Unable to determine")

    # Windows code page (if available)
    try:
        result = subprocess.run(['chcp'], capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"Windows code page: {result.stdout.strip()}")
        else:
            print("Windows code page: Unable to determine")
    except:
        print("Windows code page: Not available (not Windows or chcp not found)")

def test_emoji_support():
    """Test if current console can handle emojis."""
    print("\n=== Emoji Support Test ===")

    test_emojis = ['🎉', '✅', '❌', '⚠️', '🔧']
    hebrew_text = 'בדיקה'

    try:
        print("Testing emoji output:")
        for emoji in test_emojis:
            print(f"  {emoji} - OK")

        print(f"Testing Hebrew text: {hebrew_text}")
        print("✅ Console supports Unicode correctly")
        return True

    except UnicodeEncodeError as e:
        print(f"❌ Console encoding error: {e}")
        print("🔧 Your console cannot display Unicode characters")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def provide_solutions():
    """Provide specific solutions based on current encoding."""
    print("\n=== Solutions to Enable UTF-8 ===")

    current_stdout = sys.stdout.encoding.lower()

    if 'cp1255' in current_stdout:
        print("🔍 DETECTED: CP1255 (Hebrew) encoding")
        print("\n💡 RECOMMENDED SOLUTIONS:")

        print("\n1. 🏆 BEST: Enable Windows UTF-8 Beta (System-wide)")
        print("   - Press Win+I → Time & Language → Language & Region")
        print("   - Administrative language settings → Change system locale")
        print("   - Check 'Beta: Use Unicode UTF-8 for worldwide language support'")
        print("   - Restart computer")

        print("\n2. 🚀 QUICK: Change code page for current session")
        print("   - Run: chcp 65001")
        print("   - Then: set PYTHONIOENCODING=utf-8")

        print("\n3. 📝 BATCH FILE: Create startup script")
        print("   - Create run_backup_utf8.bat:")
        print("   - Add: @echo off")
        print("   - Add: chcp 65001 >nul")
        print("   - Add: set PYTHONIOENCODING=utf-8")
        print("   - Add: python scripts/fixed_launcher.py")

    elif 'utf-8' in current_stdout or 'utf8' in current_stdout:
        print("✅ GREAT: UTF-8 encoding already enabled")
        print("   Your console should handle Unicode correctly")

    else:
        print(f"⚠️ UNKNOWN ENCODING: {current_stdout}")
        print("   Try enabling UTF-8 with: set PYTHONIOENCODING=utf-8")

def test_subprocess_encoding():
    """Test subprocess encoding behavior."""
    print("\n=== Subprocess Encoding Test ===")

    # Test subprocess without UTF-8 environment
    test_script = '''
print("🎉 Subprocess emoji test")
print("Hebrew: בדיקה")
'''

    try:
        # Test without UTF-8 environment
        result1 = subprocess.run(
            [sys.executable, '-c', test_script],
            capture_output=True,
            text=True,
            timeout=5
        )

        without_utf8_ok = result1.returncode == 0 and 'UnicodeDecodeError' not in result1.stderr
        print(f"Without UTF-8 env: {'✅ OK' if without_utf8_ok else '❌ ENCODING ERROR'}")

        # Test with UTF-8 environment
        utf8_env = os.environ.copy()
        utf8_env['PYTHONIOENCODING'] = 'utf-8'

        result2 = subprocess.run(
            [sys.executable, '-c', test_script],
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=utf8_env,
            timeout=5
        )

        with_utf8_ok = result2.returncode == 0 and 'UnicodeDecodeError' not in result2.stderr
        print(f"With UTF-8 env: {'✅ OK' if with_utf8_ok else '❌ STILL ERROR'}")

        if not without_utf8_ok and with_utf8_ok:
            print("✅ Our project UTF-8 fix is working!")
        elif without_utf8_ok:
            print("✅ System already supports UTF-8")
        else:
            print("❌ UTF-8 fix may need system-level changes")

    except Exception as e:
        print(f"❌ Subprocess test failed: {e}")

def main():
    """Run complete encoding analysis."""
    print("Console Encoding Analysis")
    print("=" * 50)

    check_current_encoding()
    emoji_support = test_emoji_support()
    test_subprocess_encoding()
    provide_solutions()

    print(f"\n{'=' * 50}")
    if emoji_support:
        print("🎉 Your console supports Unicode!")
        print("✅ The backup system should work correctly")
    else:
        print("⚠️ Your console has encoding limitations")
        print("🔧 Follow the solutions above to enable UTF-8")
    print("=" * 50)

if __name__ == "__main__":
    main()
