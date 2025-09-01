# UTF-8 Solution Documentation

## Overview
The UTF-8 Solution provides comprehensive Unicode support for the Client-Server Encrypted Backup Framework, enabling proper display of emojis, Hebrew text, and other Unicode characters in Windows console environments.

## Features
- ✅ **Emoji Display**: Proper display of all Unicode emojis
- ✅ **Hebrew Support**: Support for Hebrew text in both logical and visual RTL order
- ✅ **UTF-8 Encoding**: Automatic UTF-8 encoding for all subprocess operations
- ✅ **Error Prevention**: Eliminates UnicodeEncodeError exceptions
- ✅ **Backward Compatibility**: Maintains compatibility with existing code
- ✅ **Simple Integration**: Single import provides all functionality

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

### RTL Hebrew Printing
For Hebrew text in visual RTL order:
```python
import Shared.utils.utf8_solution as utf8

# Hebrew displayed in visual RTL order
utf8.rtl_print("שלום עולם")     # Appears as: םלוע םולש
utf8.rtl_print("בדיקה ✅")      # Appears as: ✅ הקידב
utf8.rtl_print("טעות ❌")      # Appears as: ❌ תועט
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

### `rtl_print(message: str) -> None`
Prints Hebrew text in visual RTL order by reversing the string.

**Parameters:**
- `message`: Hebrew text to display in RTL order

**Usage:**
```python
utf8.rtl_print("שלום עולם")  # Displays as: םלוע םולש
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

## Environment Variables
The solution automatically sets:
- `PYTHONIOENCODING=utf-8`
- `PYTHONUTF8=1`

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
4. Providing string reversal for RTL Hebrew display
5. Ensuring proper encoding for subprocess operations

## Troubleshooting
If emojis or Hebrew text don't display correctly:
1. Ensure you're using `utf8.safe_print()` instead of regular `print()`
2. For Hebrew RTL, use `utf8.rtl_print()`
3. In PowerShell, set `[Console]::OutputEncoding = [Text.Encoding]::UTF8`
4. In Command Prompt, run `chcp 65001` before executing Python scripts

## Version
Current version supports:
- ✅ Emoji display in Windows console environments
- ✅ Hebrew text in logical order
- ✅ Hebrew text in visual RTL order
- ✅ Automatic UTF-8 environment setup
- ✅ Subprocess UTF-8 integration