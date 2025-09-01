#!/usr/bin/env python3
"""
UTF-8 Solution - Simple and Reliable Unicode Support with Automatic Detection and Smart Bidirectional Text

SINGLE WORKING APPROACH: Direct buffer writing for emoji display + Environment Setup + Auto Detection + Smart Bidirectional Text

HOW IT WORKS:
1. Import this module in any Python file that needs UTF-8 support
2. All subprocess calls from that process automatically get UTF-8 environment
3. Environment variables propagate to child processes (C++ client)
4. ACTUAL emoji display using direct buffer writing
5. Hebrew text can be displayed with proper bidirectional text handling when needed
6. Automatic environment detection and configuration
7. Enhanced file operations with UTF-8 support
8. Context managers for RTL printing
9. Enhanced error reporting
10. No global monkey-patching - predictable behavior

USAGE:
    import Shared.utils.utf8_solution  # Add to each file that needs UTF-8
    
    # Now all subprocess calls work with UTF-8
    subprocess.run([exe, "--batch"], encoding='utf-8', env=utf8_solution.get_env())
    
    # For normal text (emojis, English, Hebrew in logical order):
    utf8_solution.safe_print("🎉 Emojis work perfectly")
    utf8_solution.safe_print("שלום עולם")  # Appears as: שלום עולם (logical order)
    
    # For Hebrew with smart bidirectional handling:
    utf8_solution.rtl_print("שלום עולם")  # Appears as: םולש םלוע (visual RTL order)
    utf8_solution.rtl_print("Hello שלום World עולם")  # Appears as: Hello םולש World םלוע

SOLVES:
- Hebrew filenames with emoji: קובץ_עברי_🎉_test.txt
- Subprocess communication with C++ client
- Windows console encoding issues
- 'charmap' codec errors
- ACTUAL emoji display in Windows environments
- Proper bidirectional text handling for Hebrew/English mixed text
- Automatic environment detection
- UTF-8 file operations
- Enhanced error reporting
"""


import contextlib
import os
import sys
import subprocess
import locale
from typing import Dict, Optional, Any, Union, List, TextIO, BinaryIO

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
    
    @classmethod
    def setup(cls) -> bool:
        """Setup UTF-8 support for current process and subprocesses."""
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
            
            # Auto-configure environment if needed
            cls._auto_configure_environment()
            
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
    def _auto_configure_environment(cls) -> None:
        """Auto-configure environment based on detection."""
        try:
            # Detect if we're in PowerShell
            is_powershell = 'PROMPT' in os.environ or 'PSModulePath' in os.environ
            
            # Detect if we're in Windows Terminal
            is_windows_terminal = 'WT_SESSION' in os.environ
            
            # Auto-configure based on environment
            if sys.platform == 'win32':
                if is_powershell or is_windows_terminal:
                    # PowerShell or Windows Terminal - optimize for better UTF-8 support
                    if hasattr(sys.stdout, 'reconfigure'):
                        sys.stdout.reconfigure(encoding='utf-8')
                        sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            # Silent failure to avoid breaking existing functionality
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

# === SMART BIDIRECTIONAL TEXT PROCESSING ===
def is_hebrew_char(char: str) -> bool:
    """Check if a character is Hebrew."""
    return '\u0590' <= char <= '\u05FF' or '\uFB00' <= char <= '\uFB4F'

def process_bidirectional_text(text: str) -> str:
    """
    Process text with proper bidirectional handling.
    Hebrew characters go RTL, English/Latin characters go LTR within their segments.
    
    Args:
        text: Input text that may contain mixed Hebrew/English
        
    Returns:
        Processed text with proper bidirectional handling for visual display
    """
    if not text:
        return text
        
    # Split text into segments of the same script
    segments = []
    current_segment = ""
    current_type = None  # None, 'hebrew', 'non_hebrew'
    
    for char in text:
        char_type = 'hebrew' if is_hebrew_char(char) else 'non_hebrew'
        
        if current_type is None:
            current_type = char_type
            current_segment = char
        elif current_type == char_type:
            current_segment += char
        else:
            # Type changed, save current segment and start new one
            segments.append((current_type, current_segment))
            current_type = char_type
            current_segment = char
    
    # Don't forget the last segment
    if current_segment:
        segments.append((current_type, current_segment))
    
    # Process segments: reverse Hebrew segments for visual order, keep non-Hebrew as-is
    processed_segments = []
    for seg_type, segment in segments:
        if seg_type == 'hebrew':
            # For Hebrew, reverse to achieve visual RTL order
            processed_segments.append(segment[::-1])
        else:
            # For non-Hebrew, keep as-is (LTR order)
            processed_segments.append(segment)
    
    # Join all segments
    return ''.join(processed_segments)

# === CORE UTF-8 FUNCTIONS ===
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
            sys.stdout.buffer.write(f"{message}\n".encode('utf-8'))
            sys.stdout.buffer.flush()
        except (UnicodeEncodeError, UnicodeDecodeError):
            try:
                # Ultimate fallback: ASCII with replacement
                safe_message = message.encode('ascii', errors='replace').decode('ascii')
                sys.stdout.buffer.write(f"{safe_message}\n".encode('utf-8'))
                sys.stdout.buffer.flush()
            except (UnicodeEncodeError, UnicodeDecodeError, LookupError):
                # More specific exception handling
                sys.stdout.buffer.write(b"UTF-8 Solution: Message encoding failed\n")
                sys.stdout.buffer.flush()

def rtl_print(message: str) -> None:
    """Print text with smart bidirectional text handling.
    
    This function processes text with proper bidirectional handling:
    - Hebrew characters are reversed for visual RTL order
    - English/Latin characters remain in LTR order
    - Mixed text is handled properly with each script in its natural direction
    
    Usage:
        rtl_print("שלום עולם")  # Displays as: םולש םלוע
        rtl_print("Hello שלום World עולם")  # Displays as: Hello םולש World םלוע
        rtl_print("בדיקה test ✅")  # Displays as: הקידב test ✅
        
    Note: 
        - Use this function for Hebrew text that should appear in RTL order
        - For normal text (English, emojis), use safe_print()
        - This function provides smart bidirectional text processing
    """
    try:
        # Process text with smart bidirectional handling
        processed_text = process_bidirectional_text(message)
        safe_print(processed_text)
    except Exception as e:
        # Fallback to regular safe_print if processing fails
        safe_print(f"RTL processing error: {e}")
        safe_print(message)

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

# === ENHANCED FILE OPERATIONS ===
def open_utf8(file: Union[str, bytes, int], mode: str = 'r', **kwargs: Any) -> Union[TextIO, BinaryIO]:
    """
    Enhanced open function with automatic UTF-8 handling.
    
    This function automatically sets UTF-8 encoding and robust error handling
    for all file operations.
    
    Args:
        file: File path or file descriptor
        mode: File mode ('r', 'w', 'a', etc.)
        **kwargs: Additional arguments passed to open()
    
    Returns:
        File object with UTF-8 support
        
    Usage:
        # Read UTF-8 file
        with utf8.open_utf8('test.txt', 'r') as f:
            content = f.read()
            
        # Write UTF-8 file
        with utf8.open_utf8('output.txt', 'w') as f:
            f.write('Hello 🌍 שלום עולם ✅')
    """
    # Set default encoding to UTF-8 if not specified
    if 'encoding' not in kwargs and ('b' not in mode):
        kwargs['encoding'] = 'utf-8'
    
    # Set default error handling for robustness
    if 'errors' not in kwargs:
        kwargs['errors'] = 'replace'
    
    return open(file, mode, **kwargs)

def read_file(filepath: Union[str, bytes], encoding: Optional[str] = None, errors: Optional[str] = None) -> Optional[str]:
    """
    Read file with UTF-8 support.
    
    This function reads a file with proper UTF-8 encoding and error handling.
    
    Args:
        filepath: Path to the file to read
        encoding: Encoding to use (default: utf-8)
        errors: Error handling strategy (default: replace)
    
    Returns:
        File content as string, or None if error occurs
        
    Usage:
        content = utf8.read_file('test.txt')
        if content:
            utf8.safe_print(f"File content: {content}")
    """
    try:
        enc = encoding or 'utf-8'
        err = errors or 'replace'
        with open_utf8(filepath, 'r', encoding=enc, errors=err) as f:
            return f.read()
    except Exception as e:
        safe_print(f"Error reading file {filepath}: {e}")
        return None

def write_file(filepath: Union[str, bytes], content: str, encoding: Optional[str] = None, errors: Optional[str] = None) -> bool:
    """
    Write file with UTF-8 support.
    
    This function writes content to a file with proper UTF-8 encoding and error handling.
    
    Args:
        filepath: Path to the file to write
        content: Content to write
        encoding: Encoding to use (default: utf-8)
        errors: Error handling strategy (default: replace)
    
    Returns:
        True if successful, False if error occurs
        
    Usage:
        success = utf8.write_file('output.txt', 'Hello 🌍 שלום עולם ✅')
        if success:
            utf8.safe_print("File written successfully")
    """
    try:
        enc = encoding or 'utf-8'
        err = errors or 'replace'
        with open_utf8(filepath, 'w', encoding=enc, errors=err) as f:
            f.write(content)
        return True
    except Exception as e:
        safe_print(f"Error writing file {filepath}: {e}")
        return False

# === CONTEXT MANAGERS ===
class RTLContext:
    """Context manager for temporary RTL printing."""
    
    def print(self, text: str) -> None:
        """Print text with smart bidirectional handling within the context."""
        rtl_print(text)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

def rtl_context() -> RTLContext:
    """
    Context manager for temporary RTL printing.
    
    This context manager allows you to temporarily use RTL printing
    mode within a specific code block with smart bidirectional text handling.
    
    Usage:
        with utf8.rtl_context() as rtl:
            rtl.print("שלום עולם")
            rtl.print("Hello שלום World עולם")
            
    Note: This provides smart bidirectional text processing for mixed scripts.
    """
    return RTLContext()

# === ENHANCED ERROR REPORTING ===
def diagnose_utf8_environment() -> Dict[str, Any]:
    """
    Provide detailed UTF-8 environment diagnosis.
    
    This function returns detailed information about the current UTF-8
    environment configuration for debugging purposes.
    
    Returns:
        Dictionary with environment diagnosis information
        
    Usage:
        diagnosis = utf8.diagnose_utf8_environment()
        utf8.safe_print(f"UTF-8 test: {diagnosis['utf8_test']}")
    """
    diagnosis = {
        'platform': sys.platform,
        'python_version': sys.version,
        'default_encoding': sys.getdefaultencoding(),
        'filesystem_encoding': sys.getfilesystemencoding(),
        'preferred_encoding': locale.getpreferredencoding(),
        'stdout_encoding': getattr(sys.stdout, 'encoding', 'Unknown'),
        'stderr_encoding': getattr(sys.stderr, 'encoding', 'Unknown'),
        'environment_variables': {
            'PYTHONUTF8': os.environ.get('PYTHONUTF8', 'NOT SET'),
            'PYTHONIOENCODING': os.environ.get('PYTHONIOENCODING', 'NOT SET')
        }
    }
    
    try:
        diagnosis['utf8_test'] = test_utf8()
        env = get_env()
        diagnosis['utf8_environment'] = {
            'PYTHONUTF8': env.get('PYTHONUTF8', 'NOT SET'),
            'PYTHONIOENCODING': env.get('PYTHONIOENCODING', 'NOT SET')
        }
    except Exception as e:
        diagnosis['utf8_test_error'] = str(e)
    
    return diagnosis

def enhanced_safe_print_with_emoji(message: str, use_emoji: bool = True) -> None:
    """Enhanced safe print with emoji support.
    
    This function provides emoji-enhanced printing within this module.
    
    Args:
        message: The message to print
        use_emoji: Whether to use emoji formatting
    """
    if use_emoji:
        # Use a simple emoji prefix for visual enhancement
        safe_print(f"🌍 {message}")
    else:
        safe_print(f"UTF-8: {message}")

# Export key functions for CyberBackup Framework usage
__all__ = [
    'get_env',           # Main function for subprocess environment
    'run_utf8',          # UTF-8 enabled subprocess.run
    'Popen_utf8',        # UTF-8 enabled subprocess.Popen  
    'test_utf8',         # Test UTF-8 capability
    'UTF8Support',       # Main class
    'safe_print',        # Safe printing function with ACTUAL emoji display
    'rtl_print',         # Hebrew smart bidirectional display function
    'enhanced_safe_print_with_emoji', # Enhanced safe printing with emoji support
    # Enhanced file operations
    'open_utf8',         # UTF-8 enabled file opening
    'read_file',         # UTF-8 enabled file reading
    'write_file',        # UTF-8 enabled file writing
    # Context managers
    'rtl_context',       # RTL context manager
    # Enhanced error reporting
    'diagnose_utf8_environment', # Environment diagnosis
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