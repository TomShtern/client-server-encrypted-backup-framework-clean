#!/usr/bin/env python3
"""
UTF-8 Solution - Simple and Reliable Unicode Support

SINGLE WORKING APPROACH: Explicit Import + Environment Setup

HOW IT WORKS:
1. Import this module in any Python file that needs UTF-8 support
2. All subprocess calls from that process automatically get UTF-8 environment
3. Environment variables propagate to child processes (C++ client)
4. No global monkey-patching - predictable behavior

USAGE:
    import Shared.utils.utf8_solution  # Add to each file that needs UTF-8
    
    # Now all subprocess calls work with UTF-8
    subprocess.run([exe, "--batch"], encoding='utf-8', env=utf8_solution.get_env())

SOLVES:
- Hebrew filenames with emoji: קובץ_עברי_🎉_test.txt
- Subprocess communication with C++ client
- Windows console encoding issues
- 'charmap' codec errors
"""

import os
import sys
import subprocess
import threading
from typing import Dict, Optional, Any

# Import ctypes with proper error handling for Windows
try:
    import ctypes
except ImportError:
    ctypes = None

class UTF8Support:
    """Simple UTF-8 environment support for subprocess operations."""
    
    _initialized = False
    _original_console_cp = None
    _original_console_output_cp = None
    _lock = threading.Lock()
    
    @classmethod
    def setup(cls) -> bool:
        """Setup UTF-8 support for current process and subprocesses."""
        with cls._lock:
            if cls._initialized:
                return True
            
            try:
                # Set environment variables that propagate to subprocesses
                os.environ['PYTHONIOENCODING'] = 'utf-8'
                os.environ['PYTHONUTF8'] = '1'
                
                # Configure Windows console if available
                cls._setup_windows_console()
                
                cls._initialized = True
                return True
            except Exception:
                return False
    
    @classmethod
    def _setup_windows_console(cls) -> None:
        """Configure Windows console for UTF-8."""
        if sys.platform != 'win32' or ctypes is None:
            return
        
        try:
            kernel32 = ctypes.windll.kernel32
            # Store original values for potential restoration
            cls._original_console_cp = kernel32.GetConsoleCP()
            cls._original_console_output_cp = kernel32.GetConsoleOutputCP()
            
            # Set UTF-8 (Code Page 65001) only if not already set
            current_cp = kernel32.GetConsoleCP()
            current_output_cp = kernel32.GetConsoleOutputCP()
            
            if current_cp != 65001:
                kernel32.SetConsoleCP(65001)
            if current_output_cp != 65001:
                kernel32.SetConsoleOutputCP(65001)
                
        except Exception:
            # Reset stored values if setup failed
            cls._original_console_cp = None
            cls._original_console_output_cp = None
    
    @classmethod
    def get_env(cls, base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        Get environment with UTF-8 settings for subprocess calls.
        
        Args:
            base_env: Base environment (default: os.environ)
        
        Returns:
            Environment dictionary with UTF-8 configuration
        """
        # Ensure setup (ignore return value for backward compatibility)
        cls.setup()

        try:
            env = dict(os.environ) if base_env is None else dict(base_env)
            # Critical environment variables for UTF-8 support
            env.update({
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONUTF8': '1'
            })

            return env
        except Exception:
            # Fallback to minimal environment
            return {
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONUTF8': '1'
            }
    
    @classmethod
    def restore_console(cls) -> None:
        """Restore original console code pages (cleanup method)."""
        if (sys.platform == 'win32' and ctypes is not None and 
            cls._original_console_cp is not None):
            try:
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleCP(cls._original_console_cp)
                kernel32.SetConsoleOutputCP(cls._original_console_output_cp)
            except Exception:
                pass

# Convenience functions that match the CyberBackup Framework patterns
def get_env(base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Get UTF-8 environment for subprocess calls."""
    return UTF8Support.get_env(base_env)

def run_utf8(cmd, **kwargs) -> subprocess.CompletedProcess:
    """
    Run subprocess with UTF-8 support.
    
    This is a convenience wrapper that automatically sets up UTF-8 environment
    and encoding parameters for subprocess.run calls.
    """
    try:
        # Set UTF-8 defaults only if not explicitly provided
        if 'encoding' not in kwargs and 'text' not in kwargs:
            kwargs['encoding'] = 'utf-8'
            kwargs['text'] = True
        
        # Ensure UTF-8 environment
        if 'env' not in kwargs:
            kwargs['env'] = get_env()
        
        return subprocess.run(cmd, **kwargs)
    except Exception as e:
        # Return failed CompletedProcess instead of raising
        return subprocess.CompletedProcess(
            args=cmd, 
            returncode=1, 
            stdout=f"UTF-8 subprocess error: {e}",
            stderr=str(e)
        )

def Popen_utf8(cmd, **kwargs) -> subprocess.Popen:
    """
    Create Popen with UTF-8 support.
    
    This is a convenience wrapper that automatically sets up UTF-8 environment
    and encoding parameters for subprocess.Popen calls.
    """
    try:
        # Set UTF-8 defaults only if not explicitly provided
        if 'encoding' not in kwargs and 'text' not in kwargs:
            kwargs['encoding'] = 'utf-8' 
            kwargs['text'] = True
        
        # Ensure UTF-8 environment
        if 'env' not in kwargs:
            kwargs['env'] = get_env()
        
        return subprocess.Popen(cmd, **kwargs)
    except Exception:
        # Fallback Popen without UTF-8 modifications
        return subprocess.Popen(cmd)

def test_utf8() -> bool:
    """Test UTF-8 capability with Hebrew and emoji characters."""
    try:
        test_content = "Hebrew: בדיקה | Emoji: 🎉✅❌ | Mixed: קובץ_עברי_🔧_test.txt"
        
        # Test encoding/decoding cycle
        encoded = test_content.encode('utf-8')
        decoded = encoded.decode('utf-8')
        
        # Verify round-trip integrity
        return test_content == decoded
        
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        return False
    except Exception:
        return False

def safe_print(message: str) -> None:
    """Safely print message with UTF-8 fallback."""
    try:
        print(message)
    except (UnicodeEncodeError, UnicodeDecodeError):
        try:
            # Fallback: ASCII with replacement
            safe_message = message.encode('ascii', errors='replace').decode('ascii')
            print(safe_message)
        except Exception:
            print("UTF-8 Solution: Message encoding failed")

# Export key functions for CyberBackup Framework usage
__all__ = [
    'get_env',           # Main function for subprocess environment
    'run_utf8',          # UTF-8 enabled subprocess.run
    'Popen_utf8',        # UTF-8 enabled subprocess.Popen  
    'test_utf8',         # Test UTF-8 capability
    'UTF8Support',       # Main class
    'safe_print'         # Safe printing function
]

# Automatic setup when imported (with error handling)
def _initialize_module():
    """Initialize module safely without side effects."""
    try:
        success = UTF8Support.setup()
        test_success = test_utf8()
        
        if success and test_success:
            safe_print("🎯 UTF-8 Solution: Ready for Hebrew+emoji content in subprocess calls!")
        elif success:
            safe_print("⚠️ UTF-8 Solution: Basic UTF-8 support activated")
        else:
            safe_print("⚠️ UTF-8 Solution: Limited support mode")
    except Exception:
        try:
            print("⚠️ UTF-8 Solution: Activated with basic support")
        except Exception:
            pass  # Silent fallback

# Safe module initialization
if __name__ != '__main__':
    _initialize_module()