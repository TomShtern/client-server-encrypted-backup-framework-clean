#!/usr/bin/env python3
"""Enhanced UTF-8 / Unicode helper utilities for the CyberBackup Framework.

Core Goals:
1. Provide a stable UTF-8 environment that propagates to subprocesses (C++ client).
2. Offer safe printing that works with emojis / Hebrew on Windows without crashes.
3. Enhanced bidirectional text handling with optional python-bidi integration.
4. Rich console output with optional rich library integration.
5. Proper text width calculations with optional wcwidth integration.
6. Simple file helpers guaranteeing UTF-8 (errors='replace') to avoid charmap issues.
7. Diagnostics for environment verification.

🎯 **AUTOMATIC ENHANCEMENT**: Just importing this module automatically enables enhanced
functionality when optional libraries are installed. No configuration needed!

Optional Library Integrations (automatically detected and used when available):

📦 **python-bidi** (pip install python-bidi):
   - Enables proper Unicode Bidirectional Algorithm for Hebrew/Arabic text
   - Automatic fallback to simple segmentation when not available
   - Used in: process_bidirectional_text(), rtl_print()

📦 **rich** (pip install rich):
   - Enhanced console output with better Unicode handling
   - Improved emoji and special character display
   - Used in: safe_print(), formatting functions
   - Automatic fallback to direct buffer writing when not available

📦 **wcwidth** (pip install wcwidth):
   - Proper text width calculation for Unicode characters
   - Accurate alignment for tables and formatted output
   - Used in: get_text_width(), pad_text(), truncate_text(), format_table_row()
   - Automatic fallback to len() when not available

Quick start (recommended):

        import Shared.utils.utf8_solution as utf8

        # ensure initialization (idempotent, safe). optional but recommended
        utf8.ensure_initialized()

        # start C++ client (env/encodings handled automatically)
        proc = utf8.Popen_utf8([str(client_exe), "--batch"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

Core usage examples:

        # Basic import (silent init) + enhanced safe print
        import Shared.utils.utf8_solution as utf8
        utf8.safe_print("🎉 Hello 🌍 שלום עולם ✅")  # Uses rich when available

        # Enhanced bidirectional text (uses python-bidi when available)
        utf8.rtl_print("שלום עולם Hello")  # Proper BiDi rendering

        # Text width and alignment (uses wcwidth when available)
        width = utf8.get_text_width("🎉 שלום 🌍")  # Accurate width calculation
        padded = utf8.pad_text("Hello", 10, align='center')  # "  Hello   "
        
        # Table formatting with proper alignment
        utf8.format_table_row(["Name", "🎉 Status", "שלום"], [10, 15, 12])

Enhanced Installation (for full functionality):

        pip install python-bidi rich wcwidth

When to call what (short):
    - Import early (before spawning child processes): usually enough.
    - Call `ensure_initialized()` if you want an explicit guarantee.
    - Use `Popen_utf8` / `run_utf8` to get safe defaults (encoding='utf-8', errors='replace').
    - If you pass a custom env to subprocess, merge it with `utf8.get_env(existing_env)`.
    - Use formatting functions for aligned output: `pad_text()`, `format_table_row()`, etc.

Helper: `ensure_initialized(verify_child=False)` — call this just before starting the
C++ client if you want an explicit, idempotent initialization check. Use
`verify_child=True` to spawn a short child Python process to confirm the
environment variables propagate to child processes (best effort, optional).
"""


import contextlib
import logging
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

# Optional libraries for enhanced functionality (graceful fallback if not available)
# These libraries provide enhanced features but are not required for basic functionality

# python-bidi: Proper Unicode BiDi algorithm implementation
try:
    from bidi.algorithm import get_display
    HAS_BIDI = True
except ImportError:
    get_display = None
    HAS_BIDI = False

# rich: Enhanced console output, better unicode handling, formatting
try:
    from rich.console import Console
    from rich.text import Text
    from rich import print as rich_print
    HAS_RICH = True
    # Create a console instance for internal use
    _rich_console = Console(force_terminal=True, legacy_windows=False)
except ImportError:
    Console = None
    Text = None
    rich_print = None
    HAS_RICH = False
    _rich_console = None

# wcwidth: Proper text width calculation for alignment
try:
    import wcwidth
    HAS_WCWIDTH = True
except ImportError:
    wcwidth = None
    HAS_WCWIDTH = False

logger = logging.getLogger(__name__)


class UTF8Support:
    """Simple UTF-8 environment support for subprocess operations.

    Public API surface purposely tiny: ``setup`` (implicit via ``get_env``),
    ``get_env``, ``restore_console``. All other helpers are internal.
    """
    
    _initialized: bool = False
    _original_console_cp: Optional[int] = None
    _original_console_output_cp: Optional[int] = None
    
    @classmethod
    def setup(cls) -> bool:
        """Setup UTF-8 support for current process and subprocesses.

        Returns True if initialization completed or already done. Returns False
        only for expected environment limitations (never raises) to avoid
        breaking caller import paths.
        """
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
        except (OSError, AttributeError, RuntimeError) as e:
            # Expected benign environment/terminal limitation
            logger.debug("UTF8Support.setup benign failure: %s", e)
            return False
        except Exception as e:  # noqa: BLE001 (want to log unexpected issue once)
            logger.exception("Unexpected UTF8Support.setup failure: %s", e)
            return False
    
    @classmethod
    def _setup_windows_console(cls) -> None:
        """Configure Windows console for UTF-8 (best effort, Windows only)."""
        if sys.platform != 'win32' or ctypes is None or not hasattr(ctypes, 'windll'):
            return

        try:
            kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
            cls._original_console_cp = kernel32.GetConsoleCP()
            cls._original_console_output_cp = kernel32.GetConsoleOutputCP()

            if kernel32.GetConsoleCP() != 65001:
                kernel32.SetConsoleCP(65001)
            if kernel32.GetConsoleOutputCP() != 65001:
                kernel32.SetConsoleOutputCP(65001)

            # Enable virtual terminal processing (not critical if fails)
            try:
                STD_OUTPUT_HANDLE = -11
                ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
                handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
                mode = ctypes.c_ulong()
                if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                    kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
            except Exception:  # noqa: BLE001
                pass
        except (AttributeError, OSError) as e:
            logger.debug("Windows console setup skipped: %s", e)
            cls._original_console_cp = None
            cls._original_console_output_cp = None

    @classmethod
    def _fix_console_streams(cls) -> None:
        """Attempt to reconfigure stdout/stderr to UTF-8 (non-fatal)."""
        try:
            if hasattr(sys.stdout, 'reconfigure') and hasattr(sys.stderr, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
                sys.stderr.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
            pass

    @classmethod
    def _auto_configure_environment(cls) -> None:
        """Lightweight heuristics for terminals (PowerShell / Windows Terminal)."""
        try:
            if sys.platform == 'win32' and (
                'PSModulePath' in os.environ or 'WT_SESSION' in os.environ
            ) and hasattr(sys.stdout, 'reconfigure') and hasattr(sys.stderr, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
                sys.stderr.reconfigure(encoding='utf-8')  # type: ignore[attr-defined]
        except Exception:  # noqa: BLE001
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
        """Restore original console code pages (best effort)."""
        if (
            sys.platform == 'win32'
            and ctypes is not None
            and cls._original_console_cp is not None
            and hasattr(ctypes, 'windll')
        ):
            with contextlib.suppress(AttributeError, OSError):
                kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
                kernel32.SetConsoleCP(cls._original_console_cp)
                if cls._original_console_output_cp is not None:
                    kernel32.SetConsoleOutputCP(cls._original_console_output_cp)

# === SMART BIDIRECTIONAL TEXT PROCESSING ===
def is_hebrew_char(char: str) -> bool:
    """Check if a character is Hebrew."""
    return '\u0590' <= char <= '\u05FF' or '\uFB00' <= char <= '\uFB4F'

def process_bidirectional_text(text: str) -> str:
    """
    Process text with proper bidirectional handling.
    
    When python-bidi is available, uses the proper Unicode BiDi algorithm for
    accurate text processing. Falls back to simple Hebrew/English segmentation
    when the library is not available.
    
    Args:
        text: Input text that may contain mixed Hebrew/English
        
    Returns:
        Processed text with proper bidirectional handling for visual display
    """
    if not text:
        return text
        
    # Use python-bidi for proper Unicode BiDi algorithm if available
    if HAS_BIDI and get_display is not None:
        try:
            # The get_display function implements the full Unicode BiDi algorithm
            return get_display(text)
        except Exception as e:
            logger.debug("bidi.get_display failed, falling back to simple algorithm: %s", e)
            # Fall through to simple algorithm
    
    # Fallback: Simple segmentation approach (original implementation)
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
    """Enhanced Unicode print with automatic rich integration when available.

    When rich is available, uses rich console for superior Unicode handling.
    Falls back to direct buffer writing when rich is not available.
    Never raises exceptions - graceful degradation in all cases.
    
    Args:
        message: Text to print (may contain emojis, Hebrew, etc.)
    """
    # Primary path: use rich console when available for best Unicode support
    if HAS_RICH and _rich_console is not None:
        try:
            _rich_console.print(message)
            return
        except Exception as e:
            logger.debug("rich console print failed, falling back: %s", e)
            # Fall through to buffer writing
    
    # Fallback path: direct buffer writing (original implementation)
    line = f"{message}\n"
    buf = getattr(sys.stdout, 'buffer', None)
    # Primary path: write UTF-8 bytes directly
    try:
        if buf is not None:
            buf.write(line.encode('utf-8'))
            buf.flush()
            return
        # Fallback: text write (already a Unicode-capable wrapper)
        sys.stdout.write(line)
        sys.stdout.flush()
        return
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Attempt ASCII replacement then retry
        try:
            safe_line = f"{message.encode('ascii', errors='replace').decode('ascii')}\n"
            if buf is not None:
                buf.write(safe_line.encode('utf-8'))
                buf.flush()
            else:
                sys.stdout.write(safe_line)
                sys.stdout.flush()
            return
        except Exception:  # noqa: BLE001
            pass
    except Exception:  # noqa: BLE001
        pass

    # Ultimate silent fallback
    try:
        err_buf = getattr(sys.stderr, 'buffer', None)
        if err_buf is not None:
            err_buf.write(b"UTF-8 safe_print failure\n")
            err_buf.flush()
        else:
            sys.stderr.write("UTF-8 safe_print failure\n")
            sys.stderr.flush()
    except Exception:  # noqa: BLE001
        pass

def rtl_print(message: str) -> None:
    """Print message after best‑effort Hebrew visual ordering.

    Falls back to the original message if processing fails.
    """
    try:
        safe_print(process_bidirectional_text(message))
    except Exception as e:  # noqa: BLE001
        logger.debug("rtl_print processing error: %s", e)
        safe_print(message)

# Convenience functions that match the CyberBackup Framework patterns
def get_env(base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Get UTF-8 environment for subprocess calls."""
    return UTF8Support.get_env(base_env)


def ensure_initialized(verify_child: bool = False, timeout: int = 5) -> bool:
    """Ensure module initialization and optionally verify env propagation.

    Args:
        verify_child: If True, spawn a short child Python process to verify
                      that PYTHONUTF8 is visible to children. This is optional
                      and useful for troubleshooting only.
        timeout: child process timeout in seconds.

    Returns:
        True if initialization succeeded (and child verification passed when
        requested), False otherwise.
    """
    ok = UTF8Support.setup()
    if not ok:
        return False

    if not verify_child:
        return True

    # Best-effort child verification: run `python -c 'import os; print(os.environ.get("PYTHONUTF8"))'`
    try:
        proc = run_utf8([sys.executable, '-c', 'import os,sys; print(os.environ.get("PYTHONUTF8", "")); sys.stdout.flush()'], timeout=timeout)
        out = getattr(proc, 'stdout', None)
        return out is not None and out.strip() == '1'
    except Exception:
        return False

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

def Popen_utf8(cmd: Union[str, List[str]], **kwargs: Any) -> subprocess.Popen[str]:
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

# === TEXT WIDTH AND FORMATTING FUNCTIONS ===
def get_text_width(text: str) -> int:
    """Get the display width of text, accounting for Unicode characters.
    
    Uses wcwidth when available for accurate width calculation of Unicode
    characters including emojis and wide characters. Falls back to len()
    when wcwidth is not available.
    
    Args:
        text: Text to measure
        
    Returns:
        Display width of the text
        
    Usage:
        width = utf8.get_text_width("🎉 שלום 🌍")  # Accurate width with wcwidth
        width = utf8.get_text_width("Hello")       # Works without wcwidth too
    """
    if not text:
        return 0
        
    if HAS_WCWIDTH and wcwidth is not None:
        try:
            # Use wcwidth for accurate Unicode width calculation
            total_width = 0
            for char in text:
                char_width = wcwidth.wcwidth(char)
                if char_width is None:
                    # Control characters and some Unicode have None width
                    char_width = 0
                elif char_width < 0:
                    # Some characters have negative width (combining chars)
                    char_width = 0
                total_width += char_width
            return total_width
        except Exception as e:
            logger.debug("wcwidth calculation failed, falling back to len(): %s", e)
            # Fall through to len() fallback
    
    # Fallback: use character count (not always accurate for Unicode)
    return len(text)

def pad_text(text: str, width: int, align: str = 'left', fill_char: str = ' ') -> str:
    """Pad text to specified width with proper Unicode width handling.
    
    Uses wcwidth when available for accurate padding of Unicode text.
    Supports left, right, and center alignment.
    
    Args:
        text: Text to pad
        width: Target width
        align: Alignment ('left', 'right', 'center')
        fill_char: Character to use for padding
        
    Returns:
        Padded text
        
    Usage:
        padded = utf8.pad_text("Hello", 10, align='center')  # "  Hello   "
        padded = utf8.pad_text("🎉", 5, align='right')       # "   🎉"
    """
    if not text:
        return fill_char * width
        
    text_width = get_text_width(text)
    
    if text_width >= width:
        return text
    
    padding_needed = width - text_width
    
    if align == 'right':
        return fill_char * padding_needed + text
    elif align == 'center':
        left_padding = padding_needed // 2
        right_padding = padding_needed - left_padding
        return fill_char * left_padding + text + fill_char * right_padding
    else:  # left alignment (default)
        return text + fill_char * padding_needed

def truncate_text(text: str, width: int, suffix: str = '...') -> str:
    """Truncate text to specified width with proper Unicode width handling.
    
    Uses wcwidth when available for accurate truncation of Unicode text.
    Adds suffix when text is truncated.
    
    Args:
        text: Text to truncate
        width: Maximum width
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text
        
    Usage:
        short = utf8.truncate_text("Hello World 🌍", 10)  # "Hello W..."
        short = utf8.truncate_text("שלום עולם", 8)        # "שלום..."
    """
    if not text:
        return text
        
    text_width = get_text_width(text)
    
    if text_width <= width:
        return text
    
    suffix_width = get_text_width(suffix)
    target_width = width - suffix_width
    
    if target_width <= 0:
        return suffix[:width] if width > 0 else ''
    
    # Find the truncation point
    current_width = 0
    truncate_pos = 0
    
    for i, char in enumerate(text):
        char_width = get_text_width(char)
        if current_width + char_width > target_width:
            break
        current_width += char_width
        truncate_pos = i + 1
    
    return text[:truncate_pos] + suffix

def format_table_row(columns: List[str], widths: List[int], sep: str = ' | ', align: str = 'left') -> str:
    """Format a table row with proper Unicode width alignment.
    
    Uses wcwidth when available for accurate column alignment with Unicode text.
    
    Args:
        columns: List of column texts
        widths: List of column widths
        sep: Column separator
        align: Default alignment for all columns
        
    Returns:
        Formatted table row
        
    Usage:
        row = utf8.format_table_row(["Name", "🎉 Status", "שלום"], [10, 15, 12])
        # "Name      | 🎉 Status     | שלום        "
    """
    if len(columns) != len(widths):
        # Adjust to match lengths
        min_len = min(len(columns), len(widths))
        columns = columns[:min_len]
        widths = widths[:min_len]
    
    formatted_columns = []
    for column, width in zip(columns, widths):
        formatted_columns.append(pad_text(column, width, align=align))
    
    return sep.join(formatted_columns)

def wrap_text(text: str, width: int, indent: str = '', subsequent_indent: str = '') -> List[str]:
    """Wrap text to specified width with proper Unicode width handling.
    
    Uses wcwidth when available for accurate text wrapping with Unicode characters.
    
    Args:
        text: Text to wrap
        width: Maximum line width
        indent: Indent for first line
        subsequent_indent: Indent for continuation lines
        
    Returns:
        List of wrapped lines
        
    Usage:
        lines = utf8.wrap_text("Hello World 🌍 שלום עולם", 10)
        for line in lines:
            utf8.safe_print(line)
    """
    if not text:
        return ['']
    
    # Simple word-based wrapping with Unicode width awareness
    words = text.split()
    lines = []
    current_line = indent
    current_width = get_text_width(current_line)
    
    for word in words:
        word_width = get_text_width(word)
        space_width = get_text_width(' ')
        
        # Check if adding this word would exceed width
        needed_width = word_width
        if current_line.strip():  # If there's already content, add space
            needed_width += space_width
        
        if current_width + needed_width <= width:
            # Word fits on current line
            if current_line.strip():
                current_line += ' '
                current_width += space_width
            current_line += word
            current_width += word_width
        else:
            # Word doesn't fit, start new line
            if current_line.strip():
                lines.append(current_line)
            current_line = subsequent_indent + word
            current_width = get_text_width(current_line)
    
    # Add the last line if it has content
    if current_line.strip():
        lines.append(current_line)
    
    return lines if lines else ['']

# === CONTEXT MANAGERS ===
########################################
# Removed RTLContext / rtl_context helper (unused in code base). Keeping file
# lean; reintroduce only if genuine multi-call scoping semantics needed.
########################################

# === ENHANCED ERROR REPORTING ===
def diagnose_utf8_environment() -> Dict[str, Any]:
    """
    Provide detailed UTF-8 environment diagnosis including optional library status.
    
    This function returns detailed information about the current UTF-8
    environment configuration and optional library availability for debugging.
    
    Returns:
        Dictionary with environment diagnosis information including library status
        
    Usage:
        diagnosis = utf8.diagnose_utf8_environment()
        utf8.safe_print(f"UTF-8 test: {diagnosis['utf8_test']}")
        utf8.safe_print(f"Rich available: {diagnosis['optional_libraries']['rich']}")
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
        },
        # Optional library availability status
        'optional_libraries': {
            'python-bidi': HAS_BIDI,
            'rich': HAS_RICH,
            'wcwidth': HAS_WCWIDTH
        },
        'enhancements_active': {
            'bidirectional_text': HAS_BIDI,
            'rich_console_output': HAS_RICH,
            'unicode_width_calculation': HAS_WCWIDTH
        }
    }
    
    try:
        diagnosis['utf8_test'] = test_utf8()
        env = get_env()
        diagnosis['utf8_environment'] = {
            'PYTHONUTF8': env.get('PYTHONUTF8', 'NOT SET'),
            'PYTHONIOENCODING': env.get('PYTHONIOENCODING', 'NOT SET')
        }
        
        # Test optional library functionality
        if HAS_BIDI:
            try:
                test_bidi = process_bidirectional_text("שלום Hello")
                diagnosis['bidi_test'] = {'success': True, 'result': test_bidi}
            except Exception as e:
                diagnosis['bidi_test'] = {'success': False, 'error': str(e)}
        
        if HAS_WCWIDTH:
            try:
                test_width = get_text_width("🎉 שלום 🌍")
                diagnosis['wcwidth_test'] = {'success': True, 'width': test_width}
            except Exception as e:
                diagnosis['wcwidth_test'] = {'success': False, 'error': str(e)}
                
    except Exception as e:
        diagnosis['utf8_test_error'] = str(e)
    
    return diagnosis

########################################
# Removed enhanced_safe_print_with_emoji (no external references, cosmetic).
########################################

# Export key functions for CyberBackup Framework usage
__all__ = [
    'get_env',          # Subprocess environment helper
    'run_utf8',         # UTF-8 enabled subprocess.run wrapper
    'Popen_utf8',       # UTF-8 enabled subprocess.Popen wrapper
    'test_utf8',        # Simple UTF-8 round trip test
    'UTF8Support',      # Environment support class
    'safe_print',       # Enhanced Unicode printing with rich integration
    'rtl_print',        # Best-effort Hebrew visual ordering print
    'open_utf8',        # UTF-8 aware open()
    'read_file',        # UTF-8 read helper
    'write_file',       # UTF-8 write helper
    'diagnose_utf8_environment',  # Diagnostics
    'ensure_initialized',
    # Text width and formatting functions (wcwidth integration)
    'get_text_width',   # Unicode-aware text width calculation
    'pad_text',         # Unicode-aware text padding
    'truncate_text',    # Unicode-aware text truncation
    'format_table_row', # Table row formatting with alignment
    'wrap_text',        # Unicode-aware text wrapping
    # Bidirectional text processing
    'process_bidirectional_text',  # BiDi text processing (bidi integration)
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