---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

---
description: AI rules derived by SpecStory from the project AI interaction history
---

---
description: AI rules derived by SpecStory from the project AI interaction history
---

---
description: AI rules derived by SpecStory from the project AI interaction history
---

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

    def setup():
        """Initialize data loading, event handlers."""
        pass

    return view_control, dispose, setup
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
    bgcolor=ft.Colors.SURFACE_VARIANT,
    bgcolor=ft.Colors.SURFACE # Replaced SURFACE_VARIANT with SURFACE
    border_radius=8,
    padding=10,
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

# FletV2 GUI with Real Server (RECOMMENDED - PowerShell Launcher)
cd FletV2 && .\start_with_server.ps1

# FletV2 GUI with Real Server (Alternative - Direct Python)
cd FletV2 && python start_with_server.py  # May fail if user site-packages conflict

# GUI-Only Mode (Mock Data)
cd FletV2 && python main.py
```

**CRITICAL**: Always use `start_with_server.ps1` (PowerShell launcher) to avoid pydantic import errors. The `.ps1` launcher sets `PYTHONNOUSERSITE=1` BEFORE Python starts and uses the `-s` flag to prevent user site-packages interference. Setting environment variables from within Python (`os.environ['PYTHONNOUSERSITE'] = '1'`) is **too late** and will NOT work.

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

**CRITICAL - ALWAYS LAUNCH WITH SERVER**:
The Flet GUI must always be launched with the server.

**CRITICAL - USE POWERSHELL LAUNCHER**:
```powershell
# RECOMMENDED: PowerShell launcher with proper environment isolation
cd FletV2
.\start_with_server.ps1
```

**Why the PowerShell launcher is required**:
- Sets `PYTHONNOUSERSITE=1` as environment variable **BEFORE** Python starts
- Uses Python `-s` flag for additional user site-packages isolation
- Prevents pydantic/pydantic-core import errors from user's global packages

**Alternative (Manual - for debugging only)**:
```powershell
$env:PYTHONNOUSERSITE = "1"
cd FletV2
..\flet_venv\Scripts\python.exe -s start_with_server.py
```

**NEVER use** (will fail with pydantic import errors):
```python
# ❌ WRONG - Setting environment variables from within Python is TOO LATE
os.environ['PYTHONNOUSERSITE'] = '1'  # Already in running process, doesn't affect imports!
```

**Technical Details**:
```python
# FletV2/start_with_server.py pattern (managed by PowerShell launcher)
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
7. **Flet GUI Launch:** Failing to use the PowerShell launcher (`start_with_server.ps1`) results in `pydantic` import errors.
8. **Flet App Still Stuck Loading:** The port is already in use from the previous session. The app is trying to start but can't bind to the port because the old instance is still running. Ensure the previous instance is fully closed.
9. **Launching Flet GUI without Server:** The Flet GUI must always be launched with the server.
10. **GUI Disconnect:** The GUI disconnects if the database view triggers a disconnect, likely due to an update-before-attachment or a blocking call.

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
- **`ft.Column` DOES support the `scroll` property in Flet 0.28.3**
  - Use string values for the `scroll` property:
    -  `scroll="auto"`
    -  `scroll="always"`
  -  Do NOT use `ft.ScrollMode.AUTO` or `ft.ScrollMode.ALWAYS`

### Database Best Practices
- Use `db_manager.get_connection()` context manager (never raw `sqlite3.connect()`)
- All timestamps use `time.monotonic()` (not `time.time()`)
- Connection pooling is enabled by default
- Execute queries via `db_manager.execute()` wrapper

### Known Issues & Workarounds
- **Flet DataTable/Charts:** Complex components (`ft.DataTable`, `LineChart`, `BarChart`, `PieChart`) may crash in Flet 0.28.3. Replace with simpler primitives (`ListView`, `Card`) if issues occur. **The `database_simple.py` view was rewritten to use a `ListView` instead of `DataTable` to avoid UI freezes.**
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

### Flet GUI Icon Replacement
- In the database view, `ft.Icons.DATABASE` is not available in the current Flet version. Replace with `ft.Icons.DATABASE` with `ft.Icons.DATASET`.

### Flet GUI Freezing Issues
- If the Flet GUI freezes upon navigating to the database page, especially when using `flet==0.28.3` and Python 3.13.5 on Windows 11, consider the following:
    - The `database_simple.py` view currently used might still have issues. **This issue was resolved by rewriting `database_simple.py` to use a `ListView` instead of `DataTable`.**
    - Consult context7 MCP for up-to-date Flet documentation and implementation best practices.
    - Investigate potential causes such as data loading issues, UI rendering problems, or database connection errors.
    - Consider using Playwright MCP tools for UI testing and debugging when appropriate.
- When debugging Flet GUI issues, launch the Flet GUI in hot reload in the browser.

### Resolved Issues & Actions Taken (2025-10-04)
- **Database View Freezing:** Resolved by replacing the DataTable with a ListView in `database_simple.py` to improve performance and prevent UI freezes during hot reload sessions. Furthermore, the three function calls `update_table_dropdown()`, `update_database_info_ui()`, and `refresh_records_list()` were moved from view creation to the `setup()` function to prevent UI update calls before the view is attached to the page.
- **Pylance Errors:** Addressed a spike in Pylance errors by reorganizing button wiring in `database_simple.py`, tightening server connection checks, and tweaking status/helper text handling. The errors were caused by event handlers being bound before their definitions and from optional `server_bridge` accesses that weren’t type-narrowed. A `get_active_bridge()` helper was added, along with stricter guards to ensure async bridge APIs are only called when the real server is present.
- **Codacy Analysis:** The `codacy_cli_analyze` MCP tool was unavailable. To enable it, double-check Copilot MCP settings (GitHub Settings → Copilot → Enable MCP servers). If the issue persists, contact Codacy support to reconnect the repository.
- **VS Code Settings Conflict:** Resolved a VS Code settings conflict by removing the workspace-level `"python.analysis.typeCheckingMode"` setting from `.vscode/settings.json`. Pyright's configuration (either in `pyrightconfig.json` or `pyproject.toml`) should be used to control type checking. If project-level overrides are necessary, configure type checking within `pyrightconfig.json` or the appropriate section in `pyproject.toml`.
- **Flet Launch Errors:** If you encounter errors like `cannot import name 'validate_core_schema' from 'pydantic_core'`, this indicates a dependency conflict or version incompatibility with the `pydantic` library. This can prevent the Flet GUI from launching. Ensure that your `pydantic` version is compatible with your Flet version.
- **Analytics View Error:** If the analytics page is not loading and shows an error like `Failed to load analytics data: Column Control must be added to the page first`, it suggests an issue with the asynchronous data loading or UI component initialization. Ensure that the necessary UI components are added to the page before attempting to load the data. Also, check for correct usage and placement of asynchronous calls.
- **DataTable Initialization:** Ensure that `DataTable` controls are initialized with at least one placeholder column to prevent errors when the view is first loaded.

### Server Retry Decorator
- The `retry` decorator in `server.py` has been updated to prevent raising `None` exceptions, which can cause static analysis errors. The decorator now ensures that if no exception is captured during retry attempts, a `RuntimeError` is raised with a clear message.

```python
def retry(max_attempts: int = 3, backoff_base: float = 0.5, exceptions: tuple = (Exception,)):
    """
    Decorator to retry a function on transient failures with exponential backoff.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: Exception | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # Don't retry on last attempt
                    if attempt == max_attempts:
                        break

                    # Record retry metric
                    metrics_collector.record_counter(
                        "database.retry.attempts",
                        tags={'function': func.__name__, 'attempt': str(attempt)}
                    )

                    # Calculate exponential backoff delay
                    delay = backoff_base * (2 ** (attempt - 1))

                    # Log retry attempt (use WARNING level per logging standards)
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    time.sleep(delay)

            # All retries exhausted, log error and re-raise
            logger.error(
                f"All {max_attempts} attempts failed for {func.__name__}: {last_exception}"
            )

            # Ensure we never attempt to raise None (static analyzers complain)
            if last_exception is None:
                raise RuntimeError(f"{func.__name__} failed after {max_attempts} attempts (no exception captured)")
            raise last_exception

        return wrapper
    return decorator
```

### Running Flet GUI with Server Instructions

To run the Flet GUI with the server, follow these steps:

1.  Ensure the BackupServer is running. The server should be listening for client connections on TCP port 1256.
2.  Launch the Flet GUI. It should automatically open in your default web browser. If it doesn't, you can access it at: `http://localhost:8570`.
3.  Verify the integration. The GUI should be fully integrated with the server, providing access to real-time metrics, client management, file browsing, and database operations.
4.  Check the status. Confirm that the server, GUI, and database are all running and connected.

```
- **Server Status**: ✅ Running (TCP port 1256 ready for client connections)
- **GUI Status**: ✅ Running (Web interface active)
- **Database**: ✅ Connected (clients accessible)
- **Dashboard**: ✅ Loaded successfully
```

The system is now fully operational with end-to-end encryption (RSA-1024 + AES-256-CBC).

To run the Flet GUI with the server on Windows:

1. Open the integrated terminal in VS Code (ensure it's set to PowerShell).
2. Navigate to the FletV2 directory:  
   `cd c:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework\FletV2`
3. Execute the PowerShell launcher:  
   `.\start_with_server.ps1`

This will start the server on TCP port 1256 and launch the GUI in your default web browser. If issues occur (e.g., pydantic import errors), ensure `PYTHONNOUSERSITE=1` is set and no previous instances are running. Close with Ctrl+C.

To stop the application, close the terminal or press `Ctrl+C` in the running terminal.

### Validating Flet GUI with Server is Running

The FletV2 GUI is now running with the real backup server connected. Here's the current status:

### System Status:
- ✅ **Server**: Running on TCP port 1256
- ✅ **GUI**: Running on HTTP port 8570  
- ✅ **Integration**: Real server connected with full CRUD operations
- ✅ **Database**: 17 clients accessible

### Access the GUI:
The GUI should automatically open in your default web browser at: **http://localhost:8570**

### What You Can Do:
- **Dashboard**: Verify live metrics and cards switch
- **Clients**: Manage registered backup clients  
- **Files**: Browse and manage backed up files
- **Database**: Use table selector to view rows; export if available
- **Analytics**: Confirm charts render after a few navigations
- **Settings**: Configure server and GUI settings

### Navigation:
Use the navigation rail on the left side to switch between different views. The system starts on the Dashboard by default.

If the browser doesn't open automatically, you can manually navigate to `http://localhost:8570` in your web browser.

The server will continue running in the background. To stop it, you can close the terminal or press `Ctrl+C` in the running PowerShell terminal.

### Next Steps & Troubleshooting (2025-10-06)

## Status
- GUI: http://localhost:8570 (opened in your browser)
- Server: Injected into Flet, real integration active
- Navigation: Dashboard, Files, Database, Analytics all loading without freezes
- Database: Connected (counts OK). “Size: N/A” just means size calculation isn’t wired yet

## Try this
- Dashboard: Verify live metrics and cards switch
- Files: Browse backed-up files (list and actions)
- Database: Use table selector to view rows; export if available
- Analytics: Confirm charts render after a few navigations

## Stop or restart
- VS Code: Terminal → “Run FletV2 with Server (PS1)” → Terminate Task
- PowerShell (force stop):
```powershell
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
```
- Relaunch (task is set up and preferred):
```powershell
# in VS Code: run task "Run FletV2 with Server (PS1)"
```

## If anything gets stuck
- Port busy: ensure previous instances are terminated, then relaunch
- Browser doesn’t open: navigate manually to http://localhost:8570

### New Errors & Troubleshooting (2025-10-06)

- **Flet Launch Errors:** If you encounter errors like `cannot import name 'validate_core_schema' from 'pydantic_core'`, this indicates a dependency conflict or version incompatibility with the `pydantic` library. This can prevent the Flet GUI from launching. Ensure that your `pydantic` version is compatible with your Flet version.
- **Database View Error:** If the Flet GUI shows an error related to `ft.Icons.DATABASE`, it indicates that the icon is not available in the current Flet version. Replace `ft.Icons.DATABASE` with `ft.Icons.DATASET`.
- **Analytics View Error:** If the analytics page is not loading and shows an error like `Failed to load analytics data: Column Control must be added to the page first`, it suggests an issue with the asynchronous data loading or UI component initialization. Ensure that the necessary UI components are added to the page before loading the data. Also, check for correct usage and placement of asynchronous calls.
- **Flet App Still Stuck Loading:** The port is already in use from the previous session. The app is trying to start but can't bind to the port because the old instance is still running. Ensure the previous instance is fully closed.
- **DataTable Initialization:** Ensure that `DataTable` controls are initialized with at least one placeholder column to prevent errors when the view is first loaded.

### Flet View Lifecycle Deadlock Pattern

Flet views follow a strict 3-phase lifecycle:
1. Creation: Build control tree (NO updates allowed)
2. Attachment: AnimatedSwitcher adds to page (160ms + 250ms delay)
3. Setup: ONLY NOW can you safely call control.update()

Think of it like construction: You can't paint a wall (update) before it's installed
(attached to page). The `setup` function pattern leverages Flet's lifecycle hooks to guarantee attachment
before updates, eliminating an entire class of freeze bugs. Always follow this checklist when creating new views:

```python
def create_new_view(server_bridge, page, state_manager=None):
    # ✅ DO: Create controls
    control = ft.Text("Hello")

    # ✅ DO: Set event handlers (not updates)
    button.on_click = my_handler

    # ❌ DON'T: Call .update() on controls
    # control.update()  # WRONG - causes freeze!

    # ❌ DON'T: Call functions that update controls
    # populate_list()   # WRONG if it calls .update()!

    async def setup():
        # ✅ DO: Update controls here (after page attachment)
        control.update()
        populate_list()  # Now safe!

    return view_container, dispose, setup
```

It's critical that Flet's async architecture requires controls to be in the page tree before updates. This isn't a bug—it's by design. The framework needs a reference to the page object to know WHERE to render updates. Without page attachment, there's no render target, causing the blocking wait.

### Database View Troubleshooting (2025-10-06)

- **Large Empty Gray Area:** If the `records_section` expands to fill available vertical space, ensure the `ft.Column` inside has `alignment=ft.MainAxisAlignment.START` in addition to `tight=True`. Verify no invisible widgets are present before the `records_listview` within the `ft.Stack`.
- **Long Text Strings Causing Large Record Cards:** Truncate the display of long string values within the `build_record_card` function, similar to how byte arrays are handled. Limit the length of the displayed string and add an ellipsis if it exceeds a certain character count.

## 📝 Additional Project-Specific Notes

- **Enhance, Don't Replace:** When instructed to update the analytics view, improve the existing one instead of creating a new one. This maintains consistency and avoids unnecessary duplication.

## 🛠️ Debugging & Tooling

### Updating Claude Code

To update the Claude Code CLI tool, use the following command in your terminal:

```bash
claude code --update
```

Alternatively, if installed via npm, you can use:

```bash
npm update -g @anthropic/claude-code
```

However, the built-in update command (`claude code --update`) is recommended.

### Node.js Architecture Troubleshooting

If you encounter an "Unsupported architecture: ia32" error when using Claude Code, it indicates that Node.js is running in 32-bit mode instead of 64-bit. Claude Code requires a 64-bit Node.js installation.

**To fix this issue:**

1.  **Uninstall current Node.js:**
    \- Go to Settings → Apps → Node.js → Uninstall
2.  **Download 64-bit Node.js:**
    \- Visit: [https://nodejs.org/](https://nodejs.org/)
    \- Download the **Windows Installer (.msi)** for **x64** (not x86)
    \- Install the LTS version (currently v22.x is fine)
3.  **Verify after installation:**
    \- Open a new terminal or PowerShell window.
    \- Run: `node -p "process.arch"`
    \- The output should be `x64`. If it still shows `ia32`, ensure you have completely uninstalled the previous version and installed the 64-bit version correctly.
4.  **Reinstall Claude Code**:

```powershell
npm uninstall -g @anthropic-ai/claude-code
npm install -g @anthropic-ai/claude-code
```

### Using `grep` in the Terminal

`grep` is a command-line utility for searching text patterns in files or input streams. It's powerful for finding specific strings.

## 🛠️ Debugging & Tooling
### Updating pip

To update pip, use the