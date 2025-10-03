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
```bash
# Lint: ruff check . (line-length=110, rules: E,F,W,B,I)
ruff check .

# Format: ruff format .
ruff format .

# Type Check: mypy . (strict mode, Python 3.13.5)
mypy .

# Lint: pylint (configuration via .pylintrc)
pylint

# Test All: pytest tests/
pytest tests/

# Test Single: pytest tests/test_specific_file.py::TestClass::test_method -v
pytest tests/test_specific_file.py::TestClass::test_method -v

# Test Integration: pytest tests/integration/ -v
pytest tests tests/integration/ -v

# Compile all Python files
python -m compileall FletV2/main.py
```

#### C++
```bash
# Build: cmake with vcpkg toolchain
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake" && cmake --build build --config Release

# Format: clang-format -i file.cpp (Google style, 100 cols, 4-space indent, Google style)
clang-format -i file.cpp
```

#### Full System
```bash
# One-Click Build+Run: python scripts/one_click_build_and_run.py
python scripts/one_click_build_and_run.py
```

### Code Style Guidelines

#### Python
- **Imports**: Standard library first, then third-party, then local (alphabetical within groups)
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants
- **Types**: Use type hints, strict mypy compliance
- **Line Length**: 110 characters max
- **Error Handling**: Try/except with specific exceptions, log errors with context. Use `contextlib.suppress(Exception)` for concise suppressed-exception blocks.
- **Async**: Use async/await for I/O operations, avoid blocking calls
- **Indentation**: Correct any unexpected indentation issues by ensuring code blocks are properly scoped. Run linters (e.g., `ruff check .`) to verify code style.
- **Sourcery**: Apply only safe, behavior‑preserving refactors (inline immediately-returned vars, simplify empty list comparisons, remove unnecessary casts, safe list comprehension/extend substitutions) and explicitly justify skipping higher‑risk “extract-method” or structural changes that could drop comments or subtly alter flow. Address all sourcery warnings in the `#file:main.py`.
- **Problems View**: The Problems view in VS Code groups problems by source (e.g., extensions, linters) in tree view mode. Multiple groups can appear for the same file if multiple tools are enabled. Use the `problems.defaultViewMode` setting to switch to table view for a flat list. Pylance (Microsoft's Python language server) groups its findings by type in the Problems panel:
    1. **Syntax Errors** - Parse/compilation issues
    2. **Type Errors** - Type checking violations
    3. **Import Issues** - Module resolution problems
    4. **Code Analysis** - Potential bugs or improvements
    5. **Information** - Hints and suggestions

#### C++
- **Style**: Google C++ style with clang-format
- **Indentation**: 4 spaces, no tabs
- **Braces**: Attach to function/class, new line for control statements
- **Pointers**: Left-aligned (*)
- **Includes**: Group by type, alphabetical within groups

#### General
- **Flet GUI Transition Delay**:  Increase the transition delay in `main.py` line 990 to `await asyncio.sleep(0.25)` (250ms) to provide a safe margin after the 160ms animated switcher transition. This prevents setup functions from running before the transition finishes, which can cause crashes.
- **Flet Code**:
  - **Code Location**: The first statement in a function should be the docstring. Having code before the docstring makes the docstring a regular string literal, not documentation.
  - **`_initialized`**: The `_initialized` guard in `FletV2App` should be checked to prevent multiple initializations.
- **Flet Version**: Ensure you are doing things with Flet 0.28.3 idioms in mind. Always avoid costume complex long solutions where there is a Flet native better and simpler way. Use context7 if you are not sure about something, it has instructions for everything.
- **Ruff**: When addressing Ruff issues, ensure you are not breaking the code and not removing functionality, and make sure to not create more problems than you solve.
- **Context7 MCP Usage**: Use context7 MCP more than a few times. When working with Flet, reference the official docs from context7 about version 0.28.3. **Create `Flet_Snnipets.md` to document Flet methods, features, built-in behaviors, anti-patterns, and recovery tips. The total length of the new markdown doc should be shorter than 500 LOC, ideally around 200-350 LOC.** When working with Flet, reference the official docs from context7 about version 0.28.3.
- **Configuration Search**: When asked to find a configuration value (e.g., a timeout), use workspace grep to locate the exact string and its assigned value.
- **settings.local.json**: Ensure the `settings.local.json` file does not contain any duplicate entries in the `"allow"` array.
- **Emergency GUI**: When fixing issues in `emergency_gui.py` related to missing imports or dependencies, define a simple, self-contained stub for the missing function directly in the file. This creates a basic control that matches the expected return signature (e.g., `dashboard_control, dispose_func, setup_func`), ensuring the code runs without external dependencies.
- **Qwen Code Configuration**:
  - `contentGenerator.timeout`: This key is not present in your repository files, but it is referenced repeatedly in Qwen Code issues and the Qwen Code docs as the configuration property to increase the streaming/setup timeout for content generation (i.e., streaming responses).
  - Place a settings file at either:
    - Project-level: `<project-root>/.qwen/settings.json`
    - User-level: `%USERPROFILE%\.qwen.settings.json` (on Windows; equivalently `~/.qwen/.settings.json`)
  - The timeout is a request timeout for the content generator (the CLI’s model/API calls).
  - Units: milliseconds (the settings schema says "Request timeout in milliseconds.").
  - Semantics: the maximum wall‑clock time allowed for a single generation request to complete. If a request exceeds this time the client will abort/consider it failed. It’s a total request timeout, not a per‑token inactivity timeout.
  - Value behavior:
    - Any positive integer = timeout in milliseconds (e.g., 30000 = 30 seconds).
    - `0` (or omitted/undefined depending on implementation) — effectively disables the timeout (no client‑side abort).
  - Interaction with `maxRetries`: if a request times out, the client may retry up to `contentGenerator.maxRetries` times (so a short timeout + retries can cause multiple fast retry attempts).
  - Practical recommendation: pick a reasonable timeout for your network and model latency (30_000–60_000 ms is common). If you want no client-side cutoff, keep `0`.
- **Flet GUI Startup**: The Flet GUI should start successfully and run in browser mode by default. If port 8550 is already in use, the application will use port 8551 or 8552. The GUI should be fully operational for managing the encrypted backup system.
- **GUI Access**: The Flet GUI is accessible via a web browser. The application typically runs on port 8550 by default and will use ports 8551/8552 if port 8550 is in use. Navigate to `http://localhost:8550` (or 8551/8552 if port 8550 is in use) to access the GUI.
- **GUI-Only Mode**: When running in GUI-only mode, ensure the `backup_server` parameter is set to `None` when calling `main.main(page, backup_server=None)` to trigger Lorem ipsum placeholder data. The Flet GUI should start successfully and run in browser mode by default. If port 8550 is already in use, the application will use port 8551.
- **Navigation Bar Styling**: When improving the navigation bar's design, adhere to the following specifications:
  - **Layout**:
    - Position: fixed left column (vertical), full-height of app.
    - Width: expanded 260 px, collapsed 72 px.
    - Padding: 16px vertical inside container, 12px horizontal for items.
    - Item spacing: 10 px vertical gap between nav items.
    - Icon size: 22 px for list icons; active icon 24 px with subtle scale animation.
    - Label typography: 14 px medium (FontWeight W_500), single-line ellipsis.
    - Secondary text (badges/labels): 11 px, uppercase, color token outline.
  - **Visuals**:
    - Background: Surface variant slightly elevated. Example token: ft.Colors.SURFACE_VARIANT (dark) with linear gradient subtle top-left to bottom-right or box shadow inner glow (use BoxShadow with small blur).
    - Border radius: 10 px for the container; nav items: 8 px.
    - Active item: Elevated card (bgcolor = ft.Colors.SURFACE_HIGHLIGHT or custom token), left accent bar: 4 px solid accent color (Primary/TINT).
    - Hover: Slight lighten of bg (increase alpha) and soft outer glow ring (BoxShadow with color primary, opacity 0.08). Animated transitions: 120-180ms ease-out.
  - **Icon & label alignment**:
    - Row: icon left, label right.
    - When collapsed: only icon visible, icons centered in a circular container (48x48).
    - Tooltip: show label on hover when collapsed (Flet Tooltip wrapper).
  - **Interactions and behavior**:
    - Collapse/expand button at bottom (arrow icon). Animated width transition (use control.update with small task that animates).
    - Non-blocking: Keep nav z-index low, no modal behavior. Content area should have left padding equal to nav width (update on collapse).
    - Keyboard navigation: items reachable via Tab; add semantic attributes (aria-like text via tooltip and accessible_text on Buttons).
    - Touch targets: min 44x44 px for each item to be mobile-friendly.
  - **Animations**:
    - Hover elevation: 160ms easing.
    - Active selection ripple: use small scale + opacity overlay.
    - Collapse/expand animation: 220ms linear.
  - **Colors (dark theme tokens - map to Flet)**:
    - Surface: ft.Colors.SURFACE (dark).
    - Surface variant / card: ft.Colors.SURFACE_VARIANT.
    - Primary accent: ft.Colors.PRIMARY (or ft.Colors.BLUE_500).
    - Text primary: ft.Colors.ON_SURFACE.
    - Muted: ft.Colors.OUTLINE or ft.Colors.OUTLINE_VARIANT.
    - Danger/destructive: ft.Colors.ERROR.
  - **Accessibility**:
    - Provide tooltips for collapsed state.
    - Use descriptive icons + accessible_text on buttons.
    - Ensure contrast ratios — primary text on surface should meet 4.5:1 where possible.
- **Blank Gray Screens on Analytics and Logs Pages**: If encountering blank gray screens on the analytics and logs pages, investigate the following:
  - **Structural Issues**: The Flet Specialist's extensive modifications may have introduced structural problems preventing proper content rendering.
  - **Ref-Based Updates**: Ensure complex ref-based updates are functioning correctly.
  - **Loading Overlays**: Verify that loading overlays are not blocking content. Ensure overlays are hidden (visible=False and opacity=0) when not loading.
  - **Container/Stack Structure**: Check for issues with the container and stack structures.
  - **Async Loading**: Investigate potential async loading problems with skeleton placeholders.
  - **Overlay or Stack ordering**: A loading overlay may be placed on top of the content and left visible or opaque, blocking user content (most common cause when views show a gray surface only). Ensure that the content is the first child and the overlay is the last child in a Stack (Stack renders children in order; last on top). Example: ensure `Stack(children=[content_container, overlay])` so the overlay is placed above the content only when needed. Toggle the overlay child `visible` and `opacity` instead of only toggling a top-level `visible` flag.
  - **Controls Visibility**: Controls may be set to visible=False or opacity=0 and never re-enabled, possibly via refs or async loading code that never completes or fails silently.
  - **Refs and Deferred Updates**: Code may be updating controls before they are attached, or using controls reference wrongly (e.g., expecting .controls to exist when it's None), so nothing gets added to the UI. Ensure that after any `.controls` modification you call `.update()` on that parent control. Ensure the ref is not None before using; add a small wait (`page.run_task`) to populate after attachment or add safe guards like `if ref.current is None: skip update and log a warning, then schedule a retry`. Wrap dynamic control population in a small function and call it with `page.run_task` or schedule via `page.add_post_frame_frame_callback` equivalent (Flet has `page.add_auto_close`? If not, call `page.update` after adding).
  - **Layout Structure**: Using Container vs Column vs Stack incorrectly may cause scroll or layout to be collapsed to zero height.
  - **Suppressed Exceptions**: Exceptions swallowed by `with contextlib.suppress(Exception)` in critical places, may be hiding the real error (a later AI/engineer should disable suppression to see the real stacktrace while debugging). Replace broad `contextlib.suppress(Exception)` with `logging.exception` to capture real errors during debug.
  - **Logs View Attachment Diagnostic**: Add a small diagnostic log + `page.update` in `logs.py`s `setup_subscriptions` to verify that the Logs view is attaching correctly.
- **Embedded GUI**: To enable the embedded GUI set `CYBERBACKUP_DISABLE_INTEGRATED_GUI=0`. The server checks the environment flag incorrectly; the condition should treat only `'1'` as disable.
- **Data Type Handling in Logs View**: When handling data in the logs view, especially data received from the server, ensure that variables declared as lists are not inadvertently reassigned to dictionaries. Use temporary variables to inspect the server response and normalize the data into a consistent list format before further processing. This avoids static type checker errors and ensures that list operations are performed on valid list objects.
- **Flet GUI Startup**: The Flet GUI is now running! The GUI should now be accessible in the web browser. The application is running with:
  - Embedded GUI disabled (as expected for FletV2)
  - Logging initialized with console and file output
  - The server is ready to accept connections
  The Flet GUI should open automatically in the default web browser. If it doesn't appear, you can typically access it at `http://localhost:8550` (or ports 8551/8552 if 8550 is occupied).
- **FletV2 Analysis**: Before making any changes to `FletV2`, analyze the folder for issues, problems, flaws, wrongs, anti-patterns, and bad practices using context7 MCP for up-to-date official context, documentation, and information to verify that all is going the way it should be going.
- **Database Connection Management**: When updating client information in the database, ensure proper handling of connection acquisition and release, especially when using connection pooling. Mirror the pattern used in the `execute` method for connection management. Add checks for whether connection pooling is enabled (`self.use_pool` and `self.connection_pool`). Use manual connection management (get, use, return) when pooling is enabled, and a direct `sqlite3.connect` context manager when pooling is disabled. Ensure the connection is committed and returned properly to avoid resource leaks or database locks.
- **Codacy Instructions**: When working with `codacy.instructions.md`, ensure that the instructions do not contain references to files or folders that do not exist in the repository (e.g., `#file:AI-Context` or `#file:important_docs`). Remove such references to avoid "File not found" errors. **Ignore the two warnings in codacy instructions. Address the remaining issues. Figure out what caused them to show suddenly and fix them. Make sure you are not braking the code. Ensure functionality stays the same or better. Think harder and check if you solved the problems. If you introduce problems, you must figure out what you did that caused it and fix it.**
- **File and Folder References**: In this project's documentation convention, the syntax `#file:` is used to reference both individual files and folders (e.g., `#file:AI-Context` for the AI-Context folder). There isn't a separate `#folder:` keyword.
- **Pylance AI-Assisted Code Actions**: This refers to the configuration settings for AI-powered code actions in the Python extension (Pylance) for Visual Studio Code. It controls various automated code improvements, such as generating docstrings, adding missing imports, organizing imports, and suggesting type annotations. Each key (e.g., `"generateDocstring": true`) enables or disables specific AI-assisted features. Adjust these settings to customize how the extension assists with code editing. Refer to the VS Code Python extension documentation for more details.
  - **Available Keys and Their Effects**
    - `"generateDocstring"`: Automatically generates docstrings for functions, classes, and methods.
    - `"implementAbstractClasses"`: Suggests implementations for abstract methods in subclasses.
    - `"generateSymbol"`: Creates stubs for referenced but missing symbols (e.g., undefined functions or classes).
    - `"convertFormatString"`: Converts old-style string formatting (e.g., `%` or `.format()`) to f-strings.
    - `"addMissingImports"`: Suggests and adds missing import statements based on code usage.
    - `"organizeImports"`: Sorts and removes unused imports.
    - `"suggestTypeAnnotations"`: Proposes type hints for variables, parameters, and return types.
    - `"fixTypeErrors"`: Automatically fixes detected type errors (use cautiously, as it may introduce changes).
  - **Optional/Advanced Keys (Not in your current config)**
    - `"autoApplyEdits"`: If supported, applies edits automatically without confirmation (set to `false` for manual review).
    - `"fixLintIssues"`: Auto-fixes common linting issues (e.g., style violations).
    - `"applyRefactorings"`: Enables AI-driven code refactorings (e.g., renaming, extracting methods).
  - **Usage Tips**
    - Start with conservative settings (like your current ones) to avoid unwanted changes.
    - Enable `"fixTypeErrors"` only after reviewing suggestions, as it can alter code.
    - These actions appear as lightbulb icons in the editor or via quick fixes (Ctrl+.).
    - For more details, check the Pylance documentation or VS Code Python extension settings. If you enable aggressive options, test your code thoroughly to ensure no regressions.
- **Server Issues**: When addressing the issues outlined in `#file:Server_Issues_01.10.2025.md` and the `#file:server.py`, focus on resolving all identified problems and flaws within the server component of the system. When addressing issues in `server.py`, use context7 and sequential thinking tools. When addressing issues outlined in `#file:Server_Issues_01.10.2025.md`, ensure every problem is covered and ready for prioritization before starting implementation. Search for the `update_row` method.
- **Error Handling**: If new problems or errors arise after recent changes, immediately investigate the cause and fix them, ensuring that the system's functionality remains the same or improves. **Make sure you are not breaking the code.** Ensure functionality stays the same or better. Think harder and check if you solved the problems. If you introduce problems, you **must** figure out what you did that caused it and fix it.
- **Pylance**: When addressing Pylance issues, ensure that the code remains unbroken and that no new problems are introduced. **Don't assume anything, always make sure.**
- **Sourcery**: Apply only safe, behavior‑preserving refactors (inline immediately-returned vars, simplify empty list comparisons, remove unnecessary casts, safe list comprehension/extend substitutions) and explicitly justify skipping higher‑risk “extract-method” or structural changes that could drop comments or subtly alter flow.
- **Task Prioritization from Server Issues Document**: When addressing server issues, prioritize based on the summary in `#file:Server_Issues_01.10.2025.md`. High/Medium-High priority tasks should be addressed first.
- **Server Issues Document Editing**: User has delegated the following responsibilities to the AI regarding the `#file:Server_Issues_01.10.2025.md` document:
  - **Duplicate Removal**: Remove duplicate entries from the document.
  - **Re-numbering**: Re-number items in the document to maintain sequential order after duplicate removal.
  - **Completed Items**: Move items marked with a green checkmark (✅) to a "Completed items" section at the bottom of the document.
  - **Reordering**: Reorder the uncompleted items and renumber them, updating small sections as needed.
- **Issue Prioritization**: When reordering issues in `#file:Server_Issues_01.10.2025.md`, order them from the easiest and most impactful to apply (top) to the hardest and least impactful (bottom). Ensure that the text of each issue is preserved exactly.
- **Database Parameter Handling**: When calling the `execute` method in `database.py`, do not include the `return_cursor` parameter. The method returns a cursor by default, and specifying `return_cursor` is unnecessary and incorrect.
- **VS Code Release Notes**: To view the release notes of the latest VS Code update:
  1. Use the "Show release notes" command in VS Code (open the Command Palette with Ctrl + Shift + P and run Show release notes) to view the latest update notes inside the editor.
  2. Or view them online at https://code.visualstudio.com/updates.
- **Flet GUI Integration Troubleshooting**: When integrating the Python server and SQLite3 database into the FletV2 GUI and encountering issues such as broken navigation or views not displaying:
  - Use ultrathink to systematically analyze the issues and identify the root causes.
  - Prioritize fixing the problems while ensuring not to introduce further issues or break existing functionality. The system was working before the integration, so focus on changes made during the integration process.
  - Employ all appropriate tools to diagnose and resolve the issues effectively.
- **VS Code Language Server**: Be aware that VS Code language server analysis might show errors from temporary chat editing buffers that are not present in the actual saved files. Always verify the actual saved file for errors.
- **Virtual Environment**: When working in the `flet_venv` virtual environment, ensure that the environment is activated before running any Python scripts.
- **Flet GUI State**: When the Flet GUI shows loaded data briefly before breaking and exhibiting navigation and glitching issues, use ultrathink to find the root cause and fix it without introducing new problems.
- **Playwright MCP**: When using Playwright MCP, run the Flet GUI in webview mode to take screenshots and automatically verify fixes.
- **Context7 MCP**: When unsure about anything Flet-related, use context7 MCP to get official, up-to-date context. If context7 does not provide an answer, perform web searches.
- **Running `main.py`**: When running `main.py` directly, ensure the file has an `if __name__ == "__main__":` block to actually call `main()` or start the app. Use `ft.app(target=main)` inside the `if __name__ == "__main__":` block.
- **Async Setup Functions**: When calling `setup_func()` for a view, check if it's an async coroutine. If it is, use `await setup_func()` to ensure it's properly awaited.
- **Flet Launch Verification**: After launching the Flet app, verify that the Flet backend server process is running and that the WebSocket endpoint is available. Check for WebSocket connection failures in the browser console.
- **Environment Flags Check**: When launching the Flet GUI, check the environment flags `CYBERBACKUP_DISABLE_GUI` and `INTEGRATED_GUI` to ensure they are correctly configured and not interfering with Flet's internal spawning when using WEB_BROWSER mode.
- **Lazy Server Initialization**: When using lazy server initialization, ensure that the `BackupServer` instance is created in the main thread to avoid `ValueError: signal only works in main thread of the main interpreter`.
- **GUI-Only Standalone Mode**: Be aware that the GUI may start in GUI-only standalone mode without the server bridge if `main.py` is run directly. In this mode, data operations will show empty states. Use `python start_with_server.py` for full server integration.
- **Embedded GUI Conflicts**: The embedded GUI in `BackupServer` should be disabled to prevent conflicts when running the Flet GUI with the server integration.
- **Inline Diagnostics Panel**: Implement an inline diagnostics panel for non-dashboard view load failures in `main.py` to prevent blank/gray screens. Track the most recent view loading error using the `_last_view_error` attribute.
- **Navigation Smoke Test**: Implement a navigation smoke test that automatically cycles through every view and logs success or any captured errors. To run the smoke test, launch the app with the environment variable `FLET_NAV_SMOKE=1`.
- **Dashboard Update Guard**: When updating the dashboard, add a guard to prevent updating controls that aren't yet attached to the page. This prevents errors during the initial data refresh.
- **Dashboard Loading**: The dashboard view should load correctly after the GUI initializes. If the dashboard is not loading, ensure that the `navigate_to("dashboard")` call is present at the end of the `initialize()` method and that the `initialize()` method is being called successfully. Debug output should be added to the `_perform_view_loading` method to identify any issues during view switching. Sentry SDK initialization should be disabled temporarily to rule out any crashes during module import.
- **`setup_func` Callability**: When calling `setup_func()` , add a defensive guard ensuring `setup_func` is callable before invoking it. If in an async context, handle coroutine functions while keeping changes minimal and avoiding alterations to existing behavior.
- **Database View Glitches**: If the app starts having fatal glitches after navigating to the database page, ensure that `database_table.update()` is not called before the table is attached to the page.
- **Problematic Charts**: Be aware that the analytics view has chart components (`LineChart`, `BarChart`, `PieChart`) that are complex Flet controls and may cause issues. If the analytics page is broken, these may be the cause. Replace them with simpler UI primitives if necessary.
- **Initial `state_manager.py` Errors**: If the application hangs during state manager initialization, check for corrupted Python code or syntax errors in the `state_manager.py` file, particularly within the docstring.
- **Circular Import Deadlocks**: Circular import deadlocks can occur when the `setup_terminal_debugging()` function, called at module import time in `state_manager.py`, triggers an import of the dashboard module, which then imports `state_manager` again. To prevent this, avoid calling `setup_terminal_debugging()` at the module level in `state_manager.py`.
- **Analytics Page Issues**: If the analytics page breaks the GUI, it's likely due to issues with the Flet chart components (`LineChart`, `BarChart`, `PieChart`). Replace them with simpler UI primitives if necessary.
- **Navigation and View Loading**: If navigation breaks and views don't load, check for async/await issues in setup functions, and ensure the Flet app is properly initialized and the server bridge is connected. Ensure `page.on_connect` is being called, and if not, call `navigate_to("dashboard")` directly after initialization. The `initialize()` method should be called successfully.
- **Database Page Issues**: If the database page breaks the GUI, it's likely due to issues with the `ft.DataTable` component. Replace `ft.DataTable` with a simpler `ListView` of `Cards`.
- **Analyze Before Changing**: Before making any changes, analyze the code for potential issues and use ultrathink to identify the root cause of problems before attempting fixes.
- **Avoid Assumptions**: Before making changes, ensure a thorough understanding of the code and the problem to be solved. Don't assume anything, verify everything.
- **Flet Component Instability**: Be aware that complex Flet components like `ft.DataTable`, `LineChart`, `BarChart`, and `PieChart` might be unstable in Flet version 0.28.3 and can cause browser crashes. If encountering issues with these components, consider replacing them with simpler UI primitives.
- **Database View Blocking**: Avoid making synchronous server calls during view construction. Instead, use placeholder data and load data asynchronously after the view is attached.
- **Database View Async Data Loading**: When implementing asynchronous data loading in database and analytics views, ensure that the data is fetched and loaded after the view is attached, preventing UI blocking and improving responsiveness. Initialize with placeholder data to provide immediate feedback to the user.
- **Flet GUI Launch in Webview Mode**: Use Playwright MCP to launch the Flet GUI in webview mode to take screenshots and automatically verify fixes.
- **Debug Prints Preservation**: Save the important debug prints that will help in the future for similar problems, but remove excessive debug statements that clutter the code.
- **Docstring Position**: Ensure that the docstring is the first statement after the function definition to avoid parsing errors.
- **Module-Level Code**: Avoid calling functions with potential side effects, especially those that might trigger imports, at the module level. These calls can lead to circular import deadlocks.
- **Asynchronous Data Loading**: When facing issues with UI freezing or crashing, particularly in the database and analytics pages, the root cause is often synchronous calls to the server bridge during view construction.
  - **Solution**: Apply an asynchronous data loading pattern:
    1.  **Fast View Construction**: Construct the view quickly with placeholder data.
    2.  **Lazy Data Loading**: After the view is attached (typically within `setup_subscriptions`), initiate an asynchronous call to fetch the actual data.
    3.  **Defensive Updates**: Ensure that updates to the UI are performed only after verifying that the relevant controls are attached to the page.
- **Flet Component Instability**: Certain Flet components, including `ft.DataTable`, `LineChart`, `BarChart`, and `PieChart`, may be unstable in version 0.28.3 and can cause browser crashes. If encountering issues with these components, consider replacing them with simpler UI primitives such as `ListView` or `Card`.
- **View Loading Issues**: When debugging issues with view loading, start by checking if the `page.on_connect` handler is being called. If it is not, ensure that the `navigate_to()` method is called directly after initialization. Add debug output to the `_perform_view_loading` method to identify any issues during view switching. Temporarily disable Sentry SDK initialization to rule out any crashes during module import.
- **Circular Import Deadlocks**: Circular import deadlocks can occur when the `setup_terminal_debugging()` function, called at module import time in `state_manager.py`, triggers an import of the dashboard module, which then imports `state_manager` again. To prevent this, avoid calling `setup_terminal_debugging()` at the module level in `state_manager.py`.
- **Fault Isolation**: When debugging complex issues, isolate the fault by commenting out sections of code, especially during view construction. Use incremental development to identify the minimum amount of code that is necessary to cause the error.
- **Log Analysis**: When analyzing logs, be aware that VS Code language server analysis might show errors from temporary chat editing buffers that are not present in the actual saved files. Always verify the actual saved file for errors.
- **`backup_server` Parameter**: If encountering errors related to the `backup_server` parameter in the `main` function, verify the following:
  1.  **Import Path**: Ensure the correct `main` function is being imported.
  2.  **Function Signature**: Confirm the `main` function signature includes the `backup_server` parameter: `def main(page: ft.Page, backup_server: BackupServer | None = None) -> None:`.
  3.  **Static Analysis Cache**: Clear any static analysis caches that might be using outdated information.
  4. **Parameter Recognition**: If the static analysis tool does not recognize the `backup_server` parameter, review recent changes to the `main` function signature and check for import issues.
  5. **Dynamic Parameter Handling**: To avoid static analysis errors when the `main` function signature might differ, use dynamic import and runtime inspection to call the function. Build a `kwargs` dictionary and call `main_func(page, **kwargs)`. Provide a module-level fallback (e.g., `INJECTED_BACKUP_SERVER`) for older signatures.
- **Thorough Testing**: After applying fixes, ensure the fixes are actually applied at runtime by clearing Python's module cache, terminating old processes, and clearing the browser cache. Add diagnostic logging to verify code execution.
- **GUI Transition Race Condition**: The database and analytics page crashes can be caused by a race condition between the `AnimatedSwitcher` transition and the execution of setup functions. Increase the `asyncio.sleep()` duration to `0.25` seconds to provide a safe margin after the 160ms transition.
- **Flet GUI Launch**: Ensure that when launching the Flet GUI, the `PYTHONNOUSERSITE` environment variable is set to `1` to prevent package conflicts.
- **Web Browser Mode**: When running the Flet GUI in web browser mode, protect against crashes by wrapping window property settings with try-except blocks.
- **Race Conditions**: Be aware of race conditions where code may be called during Flet's `AnimatedSwitcher` transitions.
- **GUI Transition Race Condition (REVISED)**:
  - **Problem:** The database and analytics page crashes were caused by a race condition where setup functions ran before the `AnimatedSwitcher` transition completed (160ms).
  - **Solution:** Increased the `asyncio.sleep()` duration to `0.