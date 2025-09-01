#!/usr/bin/env python3
"""
Enhanced UTF-8 Solution with Proper Console Encoding Fix
"""

import sys
import os
import ctypes
from typing import Dict, Optional

def fix_console_encoding():
    """Forcefully fix console encoding to UTF-8."""
    try:
        # Force stdout and stderr to use UTF-8 encoding
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        else:
            # Fallback for older Python versions
            sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
            
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(encoding='utf-8')
        else:
            # Fallback for older Python versions
            sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)
            
        return True
    except Exception as e:
        print(f"Failed to fix console encoding: {e}")
        return False

def enhanced_utf8_setup():
    """Enhanced UTF-8 setup with console encoding fix."""
    # Set environment variables
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Fix console encoding
    success = fix_console_encoding()
    
    # Set Windows console code page if on Windows
    if sys.platform == 'win32':
        try:
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleCP(65001)
            kernel32.SetConsoleOutputCP(65001)
        except Exception:
            pass  # Continue even if this fails
            
    return success

def test_emoji_display():
    """Test if emojis can be displayed."""
    test_string = "🎉✅❌🌍🚀"
    try:
        print(f"Emoji test: {test_string}")
        return True
    except Exception as e:
        print(f"Emoji display failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing enhanced UTF-8 solution...")
    print(f"Initial stdout encoding: {sys.stdout.encoding}")
    print(f"Initial stderr encoding: {sys.stderr.encoding}")
    
    # Apply enhanced UTF-8 setup
    success = enhanced_utf8_setup()
    print(f"UTF-8 setup result: {success}")
    
    print(f"New stdout encoding: {sys.stdout.encoding}")
    print(f"New stderr encoding: {sys.stderr.encoding}")
    
    # Test emoji display
    test_emoji_display()