# UTF-8 Solution Documentation

## 🎯 One-Import Unicode Solution

Just add `import Shared.utils.utf8_solution as utf8` to any file and get perfect Unicode support with automatic enhancements!

## Quick Start

### Basic Usage
```python
import Shared.utils.utf8_solution as utf8

# Enhanced printing (uses rich when available)
utf8.safe_print("🎉 Hello 🌍 שלום עולם ✅")

# Enhanced RTL processing (uses python-bidi when available) 
utf8.rtl_print("שלום עולם Hello")

# Enhanced subprocess operations
proc = utf8.Popen_utf8(["client.exe", "--batch"])
result = utf8.run_utf8(["some_command"])

# Enhanced file operations
content = utf8.read_file("config.txt")
utf8.write_file("output.txt", "Content with 🎉 emojis")
```

### Enhanced Features (with optional libraries)
```python
import Shared.utils.utf8_solution as utf8

# Accurate text width (uses wcwidth when available)
width = utf8.get_text_width("🎉 שלום 🌍")

# Perfect text alignment  
padded = utf8.pad_text("Hello", 10, align='center')
short = utf8.truncate_text("Long text...", 10)

# Professional table formatting
row = utf8.format_table_row(["Name", "Status"], [20, 15])

# Smart text wrapping
lines = utf8.wrap_text("Long text with 🎉 emojis", 20)
```

## Installation

### Basic (Required)
The module works automatically when imported - no installation needed!

### Enhanced (Optional)
Add to your installation:
```bash
pip install -r requirements.txt
```

The requirements.txt includes these optional enhancements:
- `python-bidi` - Full Unicode BiDi Algorithm for Hebrew/Arabic text
- `rich` - Enhanced console output with colors and formatting
- `wcwidth` - Accurate Unicode character width calculation

## Features

### 🎯 Core Functions (Always Available)

| Function | Purpose | Example |
|----------|---------|---------|
| `safe_print()` | Enhanced Unicode printing | `utf8.safe_print("🎉 שלום ✅")` |
| `rtl_print()` | RTL text processing | `utf8.rtl_print("שלום עולם")` |
| `Popen_utf8()` | UTF-8 subprocess.Popen | `utf8.Popen_utf8(["cmd"])` |
| `run_utf8()` | UTF-8 subprocess.run | `utf8.run_utf8(["cmd"])` |
| `read_file()` | UTF-8 file reading | `utf8.read_file("file.txt")` |
| `write_file()` | UTF-8 file writing | `utf8.write_file("file.txt", "content")` |

### 🎨 Enhanced Functions (Available with optional libraries)

| Function | Purpose | Requires | Example |
|----------|---------|----------|---------|
| `get_text_width()` | Unicode width calculation | wcwidth | `utf8.get_text_width("🎉 שלום")` |
| `pad_text()` | Unicode-aware padding | wcwidth | `utf8.pad_text("Hello", 10)` |
| `truncate_text()` | Unicode-aware truncation | wcwidth | `utf8.truncate_text("Long text", 10)` |
| `format_table_row()` | Table formatting | wcwidth | `utf8.format_table_row(cols, widths)` |
| `wrap_text()` | Unicode-aware wrapping | wcwidth | `utf8.wrap_text("text", 20)` |
| `process_bidirectional_text()` | BiDi processing | python-bidi | `utf8.process_bidirectional_text("שלום Hello")` |

### 🚀 Automatic Enhancements

| Library | Enhancement | Fallback |
|---------|-------------|----------|
| **rich** | Enhanced console output with colors | Direct buffer writing |
| **python-bidi** | Full Unicode BiDi Algorithm | Simple Hebrew segmentation |
| **wcwidth** | Accurate Unicode width calculation | Character count (len) |

## Framework Integration

### In API Server Files
```python
import Shared.utils.utf8_solution as utf8

# Enhanced logging
utf8.safe_print("🚀 [bold green]Server starting[/bold green] on port 9090")

# Status tables
data = [["Component", "Status"], ["API", "✅ Running"]]
for row in data:
    utf8.safe_print(utf8.format_table_row(row, [15, 15]))
```

### In Backup Executor
```python
import Shared.utils.utf8_solution as utf8

def log_progress(filename: str, progress: int):
    display_name = utf8.truncate_text(filename, 30)
    bar = "█" * (progress // 5)
    utf8.safe_print(f"📤 {display_name}: [green]{bar}[/green] {progress}%")
```

### In Python Server
```python
import Shared.utils.utf8_solution as utf8

def log_connection(client_addr: str):
    utf8.safe_print(f"🔗 [bold]Client connected:[/bold] {client_addr}")

def display_file_info(filename: str, size: int):
    display_name = utf8.truncate_text(filename, 40)
    utf8.safe_print(f"📄 File: {display_name} ([blue]{size/1024/1024:.1f} MB[/blue])")
```

## API Reference

### Core Functions

#### `safe_print(message: str) -> None`
Enhanced Unicode printing with automatic rich integration.
- Uses rich console when available for superior Unicode handling
- Falls back to direct buffer writing when rich not available
- Never raises exceptions - graceful degradation in all cases

#### `rtl_print(message: str) -> None`
Print message with enhanced RTL processing.
- Uses python-bidi when available for full Unicode BiDi Algorithm
- Falls back to simple Hebrew segmentation when not available
- Handles mixed Hebrew/English text properly

#### `Popen_utf8(cmd, **kwargs) -> subprocess.Popen[str]`
UTF-8 enabled subprocess.Popen wrapper.
- Automatically sets encoding='utf-8', text=True, errors='replace'
- Sets UTF-8 environment variables for child processes
- Compatible with existing subprocess.Popen usage

#### `run_utf8(cmd, **kwargs) -> subprocess.CompletedProcess`
UTF-8 enabled subprocess.run wrapper.
- Same automatic UTF-8 handling as Popen_utf8
- Returns standard subprocess.CompletedProcess object

### Enhanced Functions

#### `get_text_width(text: str) -> int`
Get display width of text with Unicode awareness.
- Uses wcwidth for accurate calculation when available
- Falls back to len() when wcwidth not installed
- Handles emojis, wide characters, combining characters

#### `pad_text(text: str, width: int, align: str = 'left') -> str`
Pad text with proper Unicode width handling.
- Supports 'left', 'right', 'center' alignment
- Uses accurate width calculation from get_text_width()
- Customizable fill character

#### `format_table_row(columns: List[str], widths: List[int]) -> str`
Format table row with Unicode alignment.
- Properly aligns Unicode text in columns
- Handles mixed-script content correctly
- Customizable separator and alignment

### Diagnostics

#### `diagnose_utf8_environment() -> Dict[str, Any]`
Get detailed environment and library status.
- Shows available optional libraries
- Tests UTF-8 functionality
- Provides debugging information

#### `ensure_initialized(verify_child: bool = False) -> bool`
Ensure UTF-8 environment initialization.
- Idempotent - safe to call multiple times
- Optional child process verification
- Returns success status

## Best Practices

### For AI Agents & Developers
```python
# 1. Always import at top of files
import Shared.utils.utf8_solution as utf8

# 2. Replace print() with utf8.safe_print()
utf8.safe_print("Message with 🎉 emojis and שלום Hebrew")

# 3. Use UTF-8 subprocess wrappers
result = utf8.run_utf8(["command"])
proc = utf8.Popen_utf8(["command"], stdout=subprocess.PIPE)

# 4. Use formatting functions for alignment
row = utf8.format_table_row(["Col1", "Col2"], [10, 15])
padded = utf8.pad_text("Text", 20, align='center')

# 5. Use UTF-8 file helpers
content = utf8.read_file("config.txt")
utf8.write_file("output.txt", "Unicode content 🎉")
```

### Error Handling
```python
# The module handles errors gracefully - no try/catch needed
utf8.safe_print("🎉 This never fails")

# But you can still check status if needed
if utf8.ensure_initialized():
    utf8.safe_print("✅ UTF-8 environment ready")
```

### Diagnostics
```python
# Check what enhancements are available
diagnosis = utf8.diagnose_utf8_environment()
libraries = diagnosis['optional_libraries']

print(f"Rich available: {libraries['rich']}")
print(f"BiDi available: {libraries['python-bidi']}")  
print(f"wcwidth available: {libraries['wcwidth']}")
```

## Testing

Run the comprehensive test:
```bash
python Shared/utils/test_utf8_solution.py
```

This tests all functionality with and without optional libraries.

## Troubleshooting

### Common Issues

**Issue**: Unicode characters not displaying correctly
**Solution**: Check terminal support and install optional libraries
```bash
pip install rich python-bidi wcwidth
```

**Issue**: Rich markup not working
**Solution**: Ensure rich is installed and markup is valid
```python
# Check if rich is available
import Shared.utils.utf8_solution as utf8
diagnosis = utf8.diagnose_utf8_environment()
print(diagnosis['optional_libraries']['rich'])
```

**Issue**: Text alignment incorrect
**Solution**: Install wcwidth for accurate Unicode width calculation
```bash
pip install wcwidth
```

## Summary

The UTF-8 solution provides:
- ✅ **Perfect Unicode support** with just one import
- ✅ **Automatic enhancements** when optional libraries installed
- ✅ **Graceful fallbacks** when libraries not available
- ✅ **Zero configuration** required
- ✅ **Production ready** with robust error handling

Just import and use - everything works automatically! 🎉