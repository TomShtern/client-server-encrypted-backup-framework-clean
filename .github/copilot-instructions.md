---
description: AI Development Guide for Client-Server Encrypted Backup Framework
globs: *
---

# Client-Server Encrypted Backup Framework - AI Agent Guide

## 🎯 Quick Start: What You Need to Know

This is a **production-grade 5-layer encrypted backup system** implementing RSA-1024 + AES-256-CBC encryption with a hybrid architecture.

### Architecture & Data Flow

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Web UI     │────→│ Flask API Bridge │────→│ RealBackupExecutor  │
│ (Browser)   │     │   (Port 9090)    │     │ (Process Manager)   │
└─────────────┘     └──────────────────┘     └─────────────────────┘
                                                        ↓
                                                 Creates transfer.info
                                                        ↓
┌─────────────────────────────────────────────────────┴─────────────┐
│ C++ Client (EncryptedBackupClient.exe --batch mode)               │
│ • Reads transfer.info (server:port, username, filepath)           │
│ • RSA-1024 key exchange → AES-256-CBC file encryption             │
│ • Custom binary protocol (23-byte header + payload)               │
│ • CRC32 verification                                               │
└─────────────────────────────────────────────────────┬─────────────┘
                                                        ↓
                                              TCP Connection (Port 1256)
                                                        ↓
┌─────────────────────────────────────────────────────┴─────────────┐
│ Python Backup Server (Multi-threaded TCP Server)                  │
│ • Custom binary protocol handler (protocol.py)                    │
│ • Stores: received_files/ + SQLite3 (defensive.db)                │
│ • Connection pooling with monitoring                               │
└─────────────────────────────────────────────────────┬─────────────┘
                                                        ↓
                                              Direct Instance Reference
                                                        ↓
┌─────────────────────────────────────────────────────┴─────────────┐
│ FletV2 Desktop GUI (Material Design 3 + Flet 0.28.3)              │
│ • ServerBridge: Data format converter (BackupServer ↔ FletV2)     │
│ • Views return: (control, dispose_func, setup_func)                │
│ • Theme: Material 3 + Neumorphism (40%) + Glassmorphism (20%)     │
└────────────────────────────────────────────────────────────────────┘
```

### Critical Integration Points

1. **`transfer.info` File** (C++ Client Configuration)
   ```
   127.0.0.1:1256              # Line 1: Server address:port
   TestUser                     # Line 2: Username
   C:\path\to\file.txt         # Line 3: File path to backup
   ```

2. **ServerBridge Pattern** (`FletV2/utils/server_bridge.py`)
   - **NOT an API client** - delegates directly to BackupServer instance
   - Converts data formats: `convert_backupserver_client_to_fletv2()`
   - Returns: `{'success': bool, 'data': Any, 'error': str}`

3. **Environment Flags** (Control integration modes)
   ```python
   CYBERBACKUP_DISABLE_INTEGRATED_GUI=1  # Disable BackupServer's embedded GUI
   CYBERBACKUP_DISABLE_GUI=1             # Use FletV2 GUI instead
   PYTHONNOUSERSITE=1                    # Prevent package conflicts
   ```

### Component Directory Structure

```
Client/cpp/              # C++ client source (client.cpp, main.cpp, WebServerBackend.cpp)
python_server/server/    # TCP server (server.py, protocol.py, database.py)
api_server/              # Flask bridge (cyberbackup_api_server.py, real_backup_executor.py)
FletV2/                  # Desktop GUI (main.py, views/, utils/, theme.py)
Shared/                  # Cross-component utilities (utf8_solution, logging, observability)
vcpkg/                   # C++ dependency manager (Boost, Crypto++)
scripts/                 # Build automation (one_click_build_and_run.py)
```

## ⚡ Critical Development Patterns

### 1. UTF-8 Initialization (ALWAYS FIRST!)

**MUST** be the first import in any Python entry point:

```python
# main.py, server.py, or any entry point
import Shared.utils.utf8_solution as _utf8
_utf8.ensure_initialized()

# NOW safe to import other modules
import flet as ft
from python_server.server.server import BackupServer
```

**Why:** Windows subprocess communication requires UTF-8 console setup before ANY other code runs.

### 2. FletV2 View Pattern

All views follow this signature:

```python
def create_*_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None,
    navigate_callback: Callable[[str], None] | None = None
) -> tuple[ft.Control, Callable, Callable]:
    """Returns (view_control, dispose_function, setup_function)."""

    # Create UI controls with refs for targeted updates
    content_ref = ft.Ref[ft.Column]()

    view_control = ft.Container(...)

    def dispose():
        """Cleanup subscriptions, cancel tasks."""
        pass

    def setup_subscriptions():
        """Initialize data loading, event handlers."""
        pass

    return view_control, dispose, setup_subscriptions
```

### 3. Binary Protocol Structure

```python
# Request Header (23 bytes)
client_id    = bytes[0:16]   # 16-byte UUID (BLOB format)
version      = bytes[16]     # 1 byte (must match SERVER_VERSION)
code         = bytes[17:19]  # 2 bytes little-endian (REQ_REGISTER, REQ_SEND_FILE, etc.)
payload_size = bytes[19:23]  # 4 bytes little-endian

# Response Header (7 bytes)
version      = bytes[0]      # 1 byte
code         = bytes[1:3]    # 2 bytes (RESP_REG_OK, RESP_FILE_CRC, etc.)
payload_size = bytes[3:7]    # 4 bytes
```

See `python_server/server/protocol.py` for codes and parsing functions.

### 4. Database Connection Pattern

```python
# Use DatabaseManager's pooling - DO NOT create raw sqlite3 connections
with db_manager.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT ...")
    results = cursor.fetchall()
    conn.commit()  # If modifying data
# Connection automatically returned to pool
```

**Critical:** Uses `time.monotonic()` for timestamps (not `time.time()`), and returns connections to pool.

### 5. Theme System Usage

```python
from theme import (
    PRONOUNCED_NEUMORPHIC_SHADOWS,  # 40-45% intensity (buttons, cards)
    MODERATE_NEUMORPHIC_SHADOWS,    # 30% intensity (secondary elements)
    SUBTLE_NEUMORPHIC_SHADOWS,      # 20% intensity (backgrounds)
    GLASS_STRONG, GLASS_MODERATE, GLASS_SUBTLE,  # Glassmorphism configs
    create_glassmorphic_container,
    create_hover_animation
)

# Neumorphic card
card = ft.Container(
    content=...,
    shadow=PRONOUNCED_NEUMORPHIC_SHADOWS,
    border_radius=12,
    bgcolor=ft.Colors.SURFACE_VARIANT
)

# Glassmorphic overlay
overlay = create_glassmorphic_container(
    content=...,
    config=GLASS_MODERATE,  # {'blur': 12, 'bg_opacity': 0.10, 'border_opacity': 0.15}
    border_radius=16
)
```

**Performance:** Use pre-computed constants (zero allocation) over function calls in hot paths.

## 🔧 Build, Lint & Test Commands

### Python Development

```bash
# Lint & Format
ruff check .              # Line length: 110, rules: E,F,W,B,I
ruff format .             # Auto-format code
pylint                    # Configuration via .pylintrc

# Type Checking
mypy .                    # Strict mode, Python 3.13.5

# Testing
pytest tests/                                           # Run all tests
pytest tests/test_file.py::TestClass::test_method -v  # Single test
pytest tests/integration/ -v                           # Integration tests

# Verify Imports
python -m compileall FletV2/main.py
```

### C++ Development

```bash
# Build with vcpkg (REQUIRED)
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake"
cmake --build build --config Release

# Format (Google style, 100 cols, 4-space indent)
clang-format -i Client/cpp/*.cpp

# Dependencies (if build fails)
vcpkg\vcpkg.exe install boost-iostreams:x64-windows
```

### Full System Launch

```bash
# One-Click Build + Run Everything
python scripts/one_click_build_and_run.py

# FletV2 GUI with Real Server
cd FletV2 && python start_with_server.py

# GUI-Only Mode (Mock Data)
cd FletV2 && python main.py
```

## 📋 Code Style Guidelines

### Python Conventions
- **Imports:** Standard library → third-party → local (alphabetical within groups)
- **Naming:** `snake_case` (vars/funcs), `PascalCase` (classes), `UPPER_CASE` (constants)
- **Types:** Type hints required, strict mypy compliance
- **Line Length:** 110 characters max
- **Error Handling:** Specific exceptions, log with context. Use `contextlib.suppress(Exception)` sparingly
- **Async:** Prefer `async/await` for I/O; avoid blocking calls

### C++ Conventions
- **Style:** Google C++ style with clang-format
- **Indentation:** 4 spaces, no tabs
- **Braces:** Attach to function/class, new line for control statements
- **Pointers:** Left-aligned (`*ptr`, not `* ptr`)

## 🔌 Component Integration Patterns

### Launching FletV2 with Real Server

```python
# FletV2/start_with_server.py pattern
os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'  # Disable server's GUI
os.environ['PYTHONNOUSERSITE'] = '1'                    # Prevent package conflicts

from python_server.server.server import BackupServer
server_instance = BackupServer()  # Create in MAIN thread (signal handlers)

ft.app(target=lambda page: main.main(page, backup_server=server_instance))
```

### Subprocess C++ Client Integration

```python
# api_server/real_backup_executor.py pattern
# 1. Write transfer.info
with open('transfer.info', 'w', encoding='utf-8') as f:
    f.write(f"{server_ip}:{server_port}\n{username}\n{file_path}\n")

# 2. Launch client in --batch mode
from Shared.utils.utf8_solution import Popen_utf8
process = Popen_utf8([
    'build/Release/EncryptedBackupClient.exe',
    '--batch'  # Uses transfer.info, no GUI
])
```

### ServerBridge Data Conversion

```python
# FletV2/utils/server_bridge.py pattern
def convert_backupserver_client_to_fletv2(client_data: dict) -> dict:
    """Convert BackupServer's BLOB UUIDs and timestamps to FletV2 format."""
    return {
        'id': blob_to_uuid_string(client_data['id']),           # bytes → str
        'name': client_data.get('name', 'Unknown'),
        'registered': format_timestamp(client_data['last_seen']), # monotonic → readable
        'is_active': client_data.get('is_active', False)
    }
```

## ⚠️ Common Pitfalls

1. **UTF-8 Not First:** Importing other modules before `utf8_solution.ensure_initialized()` breaks subprocess handling
2. **Wrong Timestamp:** Using `time.time()` instead of `time.monotonic()` in database code breaks connection pooling
3. **Direct sqlite3:** Creating connections without `db_manager.get_connection()` bypasses pooling
4. **View Setup Timing:** Calling `setup_func()` before view is attached to page causes null reference errors
5. **Environment Flags:** Missing `CYBERBACKUP_DISABLE_INTEGRATED_GUI=1` launches duplicate GUIs
6. **transfer.info Format:** C++ client expects exactly 3 lines (server:port, username, filepath)

## 📁 Key Files Reference

- **Architecture Entry Points:**
  - `scripts/one_click_build_and_run.py` - Full system orchestration
  - `FletV2/main.py` - GUI application entry
  - `python_server/server/server.py` - Backup server (TCP port 1256)
  - `api_server/cyberbackup_api_server.py` - Flask bridge (HTTP port 9090)

- **Critical Modules:**
  - `python_server/server/protocol.py` - Binary protocol codes and parsing
  - `python_server/server/database.py` - Connection pooling and schema
  - `FletV2/utils/server_bridge.py` - Data format conversion
  - `FletV2/theme.py` - Tri-style design system
  - `Shared/utils/utf8_solution.py` - UTF-8 initialization (import first!)

- **Build Configuration:**
  - `CMakeLists.txt` - C++ build configuration (vcpkg toolchain required)
  - `vcpkg.json` - C++ dependencies (Boost, Crypto++)
  - `pyproject.toml` - Python project metadata
  - `ruff.toml` - Python linting configuration

---

## 📝 Additional Project-Specific Notes

### Flet 0.28.3 Conventions
- Use Flet's native components over custom implementations
- Consult context7 MCP for up-to-date Flet documentation
- Views should return `(control, dispose_func, setup_func)` tuple
- Call `setup_func()` **after** view is attached to page
- Handle async setup functions: check `inspect.iscoroutinefunction(setup_func)` before calling

### Database Best Practices
- Use `db_manager.get_connection()` context manager (never raw `sqlite3.connect()`)
- All timestamps use `time.monotonic()` (not `time.time()`)
- Connection pooling is enabled by default
- Execute queries via `db_manager.execute()` wrapper

### Known Issues & Workarounds
- **Flet DataTable/Charts:** Complex components (`ft.DataTable`, `LineChart`, `BarChart`, `PieChart`) may crash in Flet 0.28.3. Replace with simpler primitives (`ListView`, `Card`) if issues occur
- **View Loading Race:** Add 250ms delay (`await asyncio.sleep(0.25)`) after `AnimatedSwitcher` transitions to prevent setup functions running before transition completes
- **Async Data Loading:** Load data asynchronously in `setup_subscriptions()`, not during view construction, to prevent UI blocking
- **Circular Imports:** Avoid calling imports at module level in `state_manager.py` to prevent deadlocks

### Environment Variables
```bash
CYBERBACKUP_DISABLE_INTEGRATED_GUI=1  # Disable embedded GUI in BackupServer
CYBERBACKUP_DISABLE_GUI=1             # Use FletV2 GUI instead of server's GUI
PYTHONNOUSERSITE=1                    # Prevent package conflicts
FLET_NAV_SMOKE=1                      # Enable navigation smoke test
FLET_DASHBOARD_DEBUG=1                # Enable dashboard debugging
```

### Troubleshooting Quick Reference
- **Blank/gray views:** Check loading overlay visibility, ref attachments, and stack ordering
- **View not loading:** Verify `setup_func()` is called after view attachment
- **Database errors:** Ensure connection pooling pattern is followed
- **Import errors:** Check UTF-8 initialization is first import
- **Subprocess failures:** Verify `transfer.info` format (3 lines: server:port, username, filepath)
