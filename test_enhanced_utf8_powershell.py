#!/usr/bin/env python3
"""
Enhanced UTF-8 Solution for PowerShell 7 with Proper Emoji Display
"""

import sys
import os
import subprocess
import ctypes
from typing import Dict, Optional, Any, Union, List

def setup_powershell_utf8():
    """Setup proper UTF-8 support for PowerShell 7."""
    try:
        # Set environment variables for UTF-8
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        os.environ['PYTHONUTF8'] = '1'
        
        # On Windows, set code page to UTF-8
        if sys.platform == 'win32':
            # Set console code page to UTF-8 (65001)
            subprocess.run(['chcp', '65001'], capture_output=True, shell=True)
            
        # Configure stdout/stderr for UTF-8
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
            
        return True
    except Exception as e:
        print(f"Error setting up UTF-8: {e}")
        return False

def print_with_emoji_fix(message: str):
    """Print function with emoji fix for PowerShell 7."""
    try:
        # Try direct print first
        print(message)
    except UnicodeEncodeError:
        # Fallback with error handling
        try:
            safe_message = message.encode('utf-8', errors='replace').decode('utf-8')
            print(safe_message)
        except Exception:
            print("Emoji display issue - UTF-8 encoding problem")

def test_emoji_display():
    """Test emoji display in PowerShell 7."""
    print("=== Enhanced UTF-8 Emoji Test ===")
    
    # Test different emoji formats
    emojis = [
        "🎉 Party Popper",
        "✅ Check Mark",
        "❌ Cross Mark", 
        "🌍 Earth Globe",
        "🚀 Rocket",
        "שלום 🌍 שלום ✅"  # Hebrew with emojis
    ]
    
    for emoji in emojis:
        print_with_emoji_fix(f"Test: {emoji}")
    
    print("\n=== Test Complete ===")
    print("If you see question marks or boxes above:")
    print("1. Make sure you're using PowerShell 7")
    print("2. Try running in Windows Terminal")
    print("3. Check that your console font supports emojis")

def get_utf8_env() -> Dict[str, str]:
    """Get environment with UTF-8 settings."""
    env = dict(os.environ)
    env.update({
        'PYTHONIOENCODING': 'utf-8',
        'PYTHONUTF8': '1'
    })
    return env

if __name__ == "__main__":
    print("Setting up enhanced UTF-8 support...")
    setup_powershell_utf8()
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Default encoding: {sys.getdefaultencoding()}")
    
    test_emoji_display()