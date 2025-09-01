#!/usr/bin/env python3
"""
Ultimate UTF-8 Solution with Windows Console Fix
"""

import sys
import os
import ctypes
from typing import Dict, Optional

def setup_windows_console():
    """Setup Windows console for proper UTF-8 emoji support."""
    if sys.platform != 'win32':
        return True
        
    try:
        # Enable virtual terminal processing for better Unicode support
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleCP(65001)
        kernel32.SetConsoleOutputCP(65001)
        
        # Try to enable virtual terminal processing
        try:
            STD_OUTPUT_HANDLE = -11
            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            
            handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
        except Exception:
            pass  # Not critical
            
        return True
    except Exception:
        return False

def fix_console_streams():
    """Fix console streams to use UTF-8 encoding."""
    try:
        # Reconfigure stdout and stderr to use UTF-8
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        else:
            # For older Python versions
            sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
            sys.stderr = open(sys.stderr.fileno(), mode='w', encoding='utf-8', buffering=1)
            
        return True
    except Exception as e:
        print(f"Failed to fix console streams: {e}")
        return False

def ultimate_utf8_setup():
    """Ultimate UTF-8 setup with all possible fixes."""
    # Set environment variables
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Setup Windows console
    setup_windows_console()
    
    # Fix console streams
    return fix_console_streams()

def test_emoji_display():
    """Test emoji display with proper error handling."""
    test_string = "🎉✅❌🌍🚀"
    try:
        print(f"Emoji test: {test_string}")
        return True
    except Exception as e:
        print(f"Emoji display failed: {e}")
        # Try with error handling
        try:
            safe_string = test_string.encode('utf-8', errors='replace').decode('utf-8')
            print(f"Safe emoji test: {safe_string}")
            return True
        except Exception:
            return False

def check_system_info():
    """Check system information for debugging."""
    print("=== System Information ===")
    print(f"Platform: {sys.platform}")
    print(f"Python version: {sys.version}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    print(f"Filesystem encoding: {sys.getfilesystemencoding()}")
    print(f"Stdout encoding: {getattr(sys.stdout, 'encoding', 'Unknown')}")
    print(f"Stderr encoding: {getattr(sys.stderr, 'encoding', 'Unknown')}")
    
    if sys.platform == 'win32':
        try:
            kernel32 = ctypes.windll.kernel32
            console_cp = kernel32.GetConsoleCP()
            console_output_cp = kernel32.GetConsoleOutputCP()
            print(f"Console Input Code Page: {console_cp}")
            print(f"Console Output Code Page: {console_output_cp}")
        except Exception as e:
            print(f"Error checking console code pages: {e}")

if __name__ == "__main__":
    print("Ultimate UTF-8 Solution Test")
    check_system_info()
    
    print("\n=== Applying Ultimate UTF-8 Setup ===")
    success = ultimate_utf8_setup()
    print(f"Setup result: {success}")
    
    print("\n=== After Setup ===")
    check_system_info()
    
    print("\n=== Testing Emoji Display ===")
    test_emoji_display()
    
    print("\n=== Test Complete ===")