# UTF-8 Solution Documentation

## Overview
The UTF-8 Solution provides comprehensive Unicode support for the Client-Server Encrypted Backup Framework, enabling proper display of emojis, Hebrew text, and other Unicode characters in Windows console environments with automatic environment detection and smart bidirectional text processing.

## Features
- ✅ **Emoji Display**: Proper display of all Unicode emojis
- ✅ **Hebrew Support**: Support for Hebrew text in both logical and visual RTL order
- ✅ **UTF-8 Encoding**: Automatic UTF-8 encoding for all subprocess operations
- ✅ **Error Prevention**: Eliminates UnicodeEncodeError exceptions
- ✅ **Backward Compatibility**: Maintains compatibility with existing code
- ✅ **Simple Integration**: Single import provides all functionality
- ✅ **Automatic Environment Detection**: Auto-detects PowerShell/Windows Terminal and configures appropriately
- ✅ **Smart Bidirectional Text Processing**: Intelligently handles mixed Hebrew/English text
- ✅ **Enhanced File Operations**: UTF-8 enabled file I/O functions
- ✅ **Context Managers**: Clean context manager approach for RTL printing
- ✅ **Enhanced Error Reporting**: Detailed environment diagnosis capabilities

## Installation
No installation required. The solution is part of the framework.

## Usage

### Basic Import
```python
import Shared.utils.utf8_solution
```

Simply importing the module automatically:
- Sets up UTF-8 environment variables
- Configures console for UTF-8 support
- Enables emoji display in subprocesses
- Automatically detects and configures PowerShell/Windows Terminal environments

### Safe Printing
For normal text, emojis, and Hebrew in logical order:
```python
import Shared.utils.utf8_solution as utf8

# Emojis display correctly
utf8.safe_print("🎉 Party Popper")
utf8.safe_print("✅ Check Mark")
utf8.safe_print("❌ Cross Mark")

# Hebrew in logical order
utf8.safe_print("שלום עולם")

# Mixed content
utf8.safe_print("Hello 🌍 שלום עולם ✅")
```

### Smart Bidirectional Text Printing
For Hebrew text with proper bidirectional handling:
```python
import Shared.utils.utf8_solution as utf8

# Hebrew displayed in visual RTL order with smart processing
utf8.rtl_print("שלום עולם")     # Displays as: םולש םלוע
utf8.rtl_print("בדיקה ✅")      # Displays as: הקידב ✅
utf8.rtl_print("טעות ❌")      # Displays as: תועט ❌

# Mixed Hebrew/English text with intelligent bidirectional processing
utf8.rtl_print("Hello שלום World עולם")  # Displays as: Hello םולש World םלוע
utf8.rtl_print("בדיקה test ✅")           # Displays as: הקידב test ✅
```

### Subprocess Operations
All subprocess operations automatically use UTF-8 encoding:
```python
import Shared.utils.utf8_solution as utf8

# UTF-8 enabled subprocess.run
result = utf8.run_utf8(["some_command"])

# UTF-8 enabled subprocess.Popen
process = utf8.Popen_utf8(["some_command"])

# Get UTF-8 environment for custom subprocess calls
env = utf8.get_env()
```

### Enhanced File Operations
UTF-8 enabled file operations:
```python
import Shared.utils.utf8_solution as utf8

# Write UTF-8 file
success = utf8.write_file("output.txt", "Hello 🌍 שלום עולם ✅")
if success:
    print("File written successfully")

# Read UTF-8 file
content = utf8.read_file("test.txt")
if content:
    utf8.safe_print(f"File content: {content}")

# Enhanced open function
with utf8.open_utf8("data.txt", "r") as f:
    data = f.read()
```

### Context Managers for RTL
Clean context manager approach for RTL printing:
```python
import Shared.utils.utf8_solution as utf8

# Context manager for temporary RTL printing
with utf8.rtl_context() as rtl:
    rtl.print("שלום עולם")              # Displays as: םולש םלוע
    rtl.print("Hello שלום World עולם")   # Displays as: Hello םולש World םלוע
    rtl.print("בדיקה test ✅")           # Displays as: הקידב test ✅
```

### Enhanced Error Reporting
Detailed environment diagnosis for troubleshooting:
```python
import Shared.utils.utf8_solution as utf8

# Get detailed environment diagnosis
diagnosis = utf8.diagnose_utf8_environment()
utf8.safe_print(f"Platform: {diagnosis['platform']}")
utf8.safe_print(f"UTF-8 test: {diagnosis['utf8_test']}")

# Enhanced safe print with optional diagnostics
utf8.enhanced_safe_print("Hello 🌍", show_diagnostics=True)
```

## Functions

### `safe_print(message: str) -> None`
Safely prints messages with proper UTF-8 encoding and emoji support.

**Parameters:**
- `message`: The message to print

**Usage:**
```python
utf8.safe_print("🎉 This will display correctly")
utf8.safe_print("שלום עולם")  # Hebrew in logical order
```

**Note:** For Hebrew in RTL visual order, use `rtl_print()` instead.

### `rtl_print(message: str) -> None`
Prints text with smart bidirectional text handling.

This function processes text with proper bidirectional handling:
- Hebrew characters are reversed for visual RTL order
- English/Latin characters remain in LTR order
- Mixed text is handled properly with each script in its natural direction

**Parameters:**
- `message`: Text to display in RTL visual order

**Usage:**
```python
utf8.rtl_print("שלום עולם")     # Displays as: םולש םלוע
utf8.rtl_print("Hello שלום")    # Displays as: Hello םולש
```

### `run_utf8(cmd, **kwargs)`
UTF-8 enabled wrapper for `subprocess.run()`.

**Parameters:**
- `cmd`: Command to run
- `**kwargs`: Additional arguments passed to `subprocess.run()`

**Returns:**
- `subprocess.CompletedProcess` instance

### `Popen_utf8(cmd, **kwargs)`
UTF-8 enabled wrapper for `subprocess.Popen()`.

**Parameters:**
- `cmd`: Command to run
- `**kwargs`: Additional arguments passed to `subprocess.Popen()`

**Returns:**
- `subprocess.Popen` instance

### `get_env(base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]`
Gets environment with UTF-8 settings for subprocess calls.

**Parameters:**
- `base_env`: Base environment dictionary (optional)

**Returns:**
- Environment dictionary with UTF-8 configuration

### `test_utf8() -> bool`
Tests UTF-8 capability with Hebrew and emoji characters.

**Returns:**
- `True` if UTF-8 is working correctly, `False` otherwise

### `open_utf8(file, mode='r', **kwargs)`
Enhanced open function with automatic UTF-8 handling.

**Parameters:**
- `file`: File path or file descriptor
- `mode`: File mode ('r', 'w', 'a', etc.)
- `**kwargs`: Additional arguments passed to `open()`

**Returns:**
- File object with UTF-8 support

### `read_file(filepath, encoding=None, errors=None) -> Optional[str]`
Read file with UTF-8 support.

**Parameters:**
- `filepath`: Path to the file to read
- `encoding`: Encoding to use (default: utf-8)
- `errors`: Error handling strategy (default: replace)

**Returns:**
- File content as string, or `None` if error occurs

### `write_file(filepath, content, encoding=None, errors=None) -> bool`
Write file with UTF-8 support.

**Parameters:**
- `filepath`: Path to the file to write
- `content`: Content to write
- `encoding`: Encoding to use (default: utf-8)
- `errors`: Error handling strategy (default: replace)

**Returns:**
- `True` if successful, `False` if error occurs

### `rtl_context() -> RTLContext`
Context manager for temporary RTL printing.

**Returns:**
- `RTLContext` instance for RTL printing within a context

**Usage:**
```python
with utf8.rtl_context() as rtl:
    rtl.print("שלום עולם")
```

### `diagnose_utf8_environment() -> Dict[str, Any]`
Provide detailed UTF-8 environment diagnosis.

**Returns:**
- Dictionary with environment diagnosis information

### `enhanced_safe_print(message: str, show_diagnostics: bool = False) -> None`
Enhanced safe print with optional diagnostics.

**Parameters:**
- `message`: The message to print
- `show_diagnostics`: Whether to show environment diagnosis

## Environment Variables
The solution automatically sets:
- `PYTHONIOENCODING=utf-8`
- `PYTHONUTF8=1`

## Smart Bidirectional Text Processing

The enhanced UTF-8 solution implements intelligent bidirectional text processing that:

1. **Segments text by script type** - Identifies Hebrew vs. Latin/English segments
2. **Processes Hebrew segments** - Reverses Hebrew text for proper RTL visual order  
3. **Preserves Latin/English segments** - Keeps English/Latin text in natural LTR order
4. **Handles mixed text efficiently** - Processes only when script changes occur
5. **Maintains emoji integrity** - Emojis remain unchanged regardless of surrounding text

**Example processing:**
```
Input:  "Hello שלום World עולם"
Processing:
  - Segment 1: "Hello " (Latin - keep as-is)
  - Segment 2: "שלום" (Hebrew - reverse to "םולש")  
  - Segment 3: " World " (Latin - keep as-is)
  - Segment 4: "עולם" (Hebrew - reverse to "םלוע")
Output: "Hello םולש World םלוע"
```

## Supported Environments
- ✅ Windows Command Prompt
- ✅ PowerShell 5.1
- ✅ PowerShell 7
- ✅ Windows Terminal
- ✅ Linux terminals
- ✅ macOS terminals

## Technical Implementation
The solution works by:
1. Setting proper environment variables for UTF-8 support
2. Configuring Windows console code page to UTF-8 (65001)
3. Using direct buffer writing for emoji display
4. Implementing smart bidirectional text processing for Hebrew/English mixed text
5. Ensuring proper encoding for subprocess operations
6. Automatically detecting PowerShell/Windows Terminal environments
7. Providing enhanced file I/O operations with UTF-8 support
8. Offering context managers for clean RTL printing

## Troubleshooting
If emojis or Hebrew text don't display correctly:
1. Ensure you're using `utf8.safe_print()` instead of regular `print()`
2. For Hebrew RTL, use `utf8.rtl_print()` for smart bidirectional processing
3. In PowerShell, set `[Console]::OutputEncoding = [Text.Encoding]::UTF8`
4. In Command Prompt, run `chcp 65001` before executing Python scripts

## Version
Current version supports:
- ✅ Emoji display in Windows console environments
- ✅ Hebrew text in logical order
- ✅ Hebrew text in visual RTL order with smart bidirectional processing
- ✅ Automatic UTF-8 environment setup
- ✅ Subprocess UTF-8 integration
- ✅ Enhanced file operations with UTF-8 support
- ✅ Context managers for RTL printing
- ✅ Enhanced error reporting with environment diagnosis
- ✅ Automatic environment detection (PowerShell/Windows Terminal)