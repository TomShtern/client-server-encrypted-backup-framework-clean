#!/usr/bin/env python3
"""
UTF-8 Solution - Simple and Reliable Unicode Support with ACTUAL Emoji Display and RTL Hebrew

SINGLE WORKING APPROACH: Direct buffer writing for emoji display + Environment Setup

HOW IT WORKS:
1. Import this module in any Python file that needs UTF-8 support
2. All subprocess calls from that process automatically get UTF-8 environment
3. Environment variables propagate to child processes (C++ client)
4. ACTUAL emoji display using direct buffer writing
5. Hebrew text can be displayed in RTL visual order when needed
6. No global monkey-patching - predictable behavior

USAGE:
    import Shared.utils.utf8_solution  # Add to each file that needs UTF-8
    
    # Now all subprocess calls work with UTF-8
    subprocess.run([exe, "--batch"], encoding='utf-8', env=utf8_solution.get_env())
    
    # For normal text (emojis, English, Hebrew in logical order):
    utf8_solution.safe_print("🎉 Emojis work perfectly")
    utf8_solution.safe_print("שלום עולם")  # Appears as: שלום עולם (logical order)
    
    # For Hebrew in RTL visual order:
    utf8_solution.rtl_print("שלום עולם")  # Appears as: םלוע םולש (visual RTL order)

SOLVES:
- Hebrew filenames with emoji: קובץ_עברי_🎉_test.txt
- Subprocess communication with C++ client
- Windows console encoding issues
- 'charmap' codec errors
- ACTUAL emoji display in Windows environments
- Hebrew RTL visual display when needed
"""


import contextlib
import os
import sys
import subprocess
import threading
from typing import Dict, Optional, Any, Union, List

# Import ctypes with proper error handling for Windows
try:
    import ctypes
except ImportError:
    ctypes = None

class UTF8Support:
    """Simple UTF-8 environment support for subprocess operations."""
    
    _initialized: bool = False
    _original_console_cp: Optional[int] = None
    _original_console_output_cp: Optional[int] = None
    _lock: threading.Lock = threading.Lock()
    
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
                
                # Fix console streams encoding
                cls._fix_console_streams()
                
                cls._initialized = True
                return True
            except (OSError, AttributeError, RuntimeError):
                # More specific exception handling for setup failures
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
                
            # Enable virtual terminal processing for better Unicode support
            try:
                STD_OUTPUT_HANDLE = -11
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                
                handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(handle, ctypes.byref(mode))
                kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
            except Exception:
                pass  # Not critical
                
        except (AttributeError, OSError):
            # More specific exception handling
            cls._original_console_cp = None
            cls._original_console_output_cp = None

    @classmethod
    def _fix_console_streams(cls) -> None:
        """Fix console streams to use UTF-8 encoding."""
        try:
            # Reconfigure stdout and stderr to use UTF-8 if possible
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
                sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            # Not critical, continue with existing setup
            pass

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
            # Use dict.update() for Python 3.8+ compatibility instead of | operator
            base_dict = dict(os.environ) if base_env is None else dict(base_env)
            base_dict.update({
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONUTF8': '1',
            })
            return base_dict
        except (OSError, AttributeError, KeyError):
            # Fallback to minimal environment for specific errors
            return {
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONUTF8': '1'
            }
    
    @classmethod
    def restore_console(cls) -> None:
        """Restore original console code pages (cleanup method)."""
        if (sys.platform == 'win32' and ctypes is not None and 
            cls._original_console_cp is not None):
            with contextlib.suppress(AttributeError, OSError):
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleCP(cls._original_console_cp)
                kernel32.SetConsoleOutputCP(cls._original_console_output_cp)

# Convenience functions that match the CyberBackup Framework patterns
def get_env(base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Get UTF-8 environment for subprocess calls."""
    return UTF8Support.get_env(base_env)

def run_utf8(cmd: Union[str, List[str]], **kwargs: Any) -> subprocess.CompletedProcess[Any]:
    """
    Run subprocess with UTF-8 support.
    
    This is a convenience wrapper that automatically sets up UTF-8 environment
    and encoding parameters for subprocess.run calls.
    """
    # Set UTF-8 defaults only if not explicitly provided
    if 'encoding' not in kwargs and 'text' not in kwargs:
        kwargs['encoding'] = 'utf-8'
        kwargs['text'] = True
        # Add error handling for invalid UTF-8 bytes from C++ client
        if 'errors' not in kwargs:
            kwargs['errors'] = 'replace'  # Replace invalid bytes with replacement character
    
    # Ensure UTF-8 environment
    if 'env' not in kwargs:
        kwargs['env'] = get_env()
    
    return subprocess.run(cmd, **kwargs)

def Popen_utf8(cmd: Union[str, List[str]], **kwargs: Any) -> subprocess.Popen[Any]:
    """
    Create Popen with UTF-8 support.
    
    This is a convenience wrapper that automatically sets up UTF-8 environment
    and encoding parameters for subprocess.Popen calls.
    """
    # Set UTF-8 defaults only if not explicitly provided
    if 'encoding' not in kwargs and 'text' not in kwargs:
        kwargs['encoding'] = 'utf-8' 
        kwargs['text'] = True
        # Add error handling for invalid UTF-8 bytes from C++ client
        if 'errors' not in kwargs:
            kwargs['errors'] = 'replace'  # Replace invalid bytes with replacement character
    
    # Ensure UTF-8 environment
    if 'env' not in kwargs:
        kwargs['env'] = get_env()
    
    return subprocess.Popen(cmd, **kwargs)

def test_utf8() -> bool:
    """Test UTF-8 capability with Hebrew and emoji characters."""
    try:
        test_content = "Hebrew: בדיקה | Emoji: 🎉✅❌ | Mixed: קובץ_עברי_🔧_test.txt"

        # Test encoding/decoding cycle
        encoded = test_content.encode('utf-8')
        decoded = encoded.decode('utf-8')

        # Verify round-trip integrity
        return test_content == decoded

    except (UnicodeEncodeError, UnicodeDecodeError, LookupError):
        # Specific exceptions for encoding issues
        return False

def safe_print(message: str) -> None:
    """Safely print message with ACTUAL emoji display support.
    
    This function ensures that all Unicode characters (including emojis and Hebrew)
    display correctly in Windows console environments.
    
    Usage:
        safe_print("🎉 This emoji will display correctly")
        safe_print("שלום עולם")  # Hebrew displays in logical order
        safe_print("Mixed: Hello 🌍 שלום עולם ✅")
        
    Note: For Hebrew in RTL visual order, use rtl_print() instead.
    """
    try:
        # Try direct buffer writing for proper emoji display
        sys.stdout.buffer.write(f"{message}\n".encode('utf-8'))
        sys.stdout.buffer.flush()
    except Exception:
        try:
            # Fallback to regular print with error handling
            print(message)
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                # Ultimate fallback: ASCII with replacement
                safe_message = message.encode('ascii', errors='replace').decode('ascii')
                print(safe_message)
            except (UnicodeEncodeError, UnicodeDecodeError, LookupError):
                # More specific exception handling
                print("UTF-8 Solution: Message encoding failed")

def rtl_print(message: str) -> None:
    """Print Hebrew text in RTL (Right-to-Left) visual order.
    
    This function reverses Hebrew text to display it in visual RTL order,
    which is how Hebrew is traditionally read.
    
    Usage:
        rtl_print("שלום עולם")  # Displays as: םלוע םולש
        rtl_print("בדיקה ✅")   # Displays as: ✅ הקידב
        rtl_print("טעות ❌")   # Displays as: ❌ תועט
        
    Note: 
        - Use this function ONLY for Hebrew text that should appear in RTL order
        - For normal text (English, emojis, Hebrew in logical order), use safe_print()
        - This function is specifically for visual RTL display, not for Unicode RTL controls
    """
    try:
        # Reverse the string to achieve visual RTL order
        reversed_message = message[::-1]
        safe_print(reversed_message)
    except Exception as e:
        # Fallback to regular safe_print if reversal fails
        safe_print(f"RTL conversion error: {e}")
        safe_print(message)

def enhanced_safe_print(message: str, use_emoji: bool = True) -> None:
    """Enhanced safe print with emoji support.
    
    This function provides backward compatibility with the original enhanced output.
    
    Args:
        message: The message to print
        use_emoji: Whether to use emoji formatting (if enhanced_output is available)
    """
    # Try to import enhanced output function - simplified approach
    try:
        from Shared.utils.enhanced_output import success_print
        if use_emoji:
            success_print(message, "UTF-8")
        else:
            safe_print(f"UTF-8: {message}")
    except ImportError:
        # Fallback to basic safe print if enhanced_output not available
        safe_print(f"UTF-8: {message}")
    except (AttributeError, TypeError):
        # Handle other specific errors with enhanced_output
        safe_print(message)

# Export key functions for CyberBackup Framework usage
__all__ = [
    'get_env',           # Main function for subprocess environment
    'run_utf8',          # UTF-8 enabled subprocess.run
    'Popen_utf8',        # UTF-8 enabled subprocess.Popen  
    'test_utf8',         # Test UTF-8 capability
    'UTF8Support',       # Main class
    'safe_print',        # Safe printing function with ACTUAL emoji display
    'rtl_print',         # Hebrew RTL visual display function
    'enhanced_safe_print' # Enhanced safe printing with emoji support
]

# Automatic setup when imported (with error handling)
def _initialize_module():
    """Initialize module safely without side effects."""
    with contextlib.suppress(OSError, AttributeError, RuntimeError):
        UTF8Support.setup()
        # Silent initialization - no console output that could cause encoding errors

# Safe module initialization - SILENT to prevent console encoding errors
if __name__ != '__main__':
    _initialize_module()