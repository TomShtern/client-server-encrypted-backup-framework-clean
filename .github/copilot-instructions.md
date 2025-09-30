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

# Client-Server Encrypted Backup Framework - AI Development Guide

This AI Development Guide should be read in conjunction with the `#file:AI-Context` folder (for extremely important documentation, data, information, and rules) and the `#file:important_docs` folder (for important information and documentation).

## 🏗️ System Architecture Overview

This is a **production-grade 5-layer encrypted backup system** with hybrid web-to-native-desktop architecture:

```
Web UI → Flask API Bridge → C++ Client (subprocess) → Python Server → Flet Desktop GUI
  ↓           ↓                    ↓                     ↓
HTTP      RealBackupExecutor    --batch mode       Custom Binary TCP   Material Design 3
requests  process management   + transfer.info     Custom Binary TCP   Server Management
```

**Critical Components**:
- **C++ Client**: Production executable with RSA/AES encryption, CRC verification, and `--batch` mode for subprocess integration
- **Flask API Bridge**: HTTP API server (port 9090) coordinating between web UI and native client
- **Python Server**: Multi-threaded TCP server (port 1256) with file storage in `received_files/`
- **Flet Desktop GUI**: Material Design 3 server management interface with modular architecture
- **SQLite3 Database**: Client and file tracking storage

### Build/Lint/Test Commands

#### Python
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
- **Sourcery**: Address all sourcery warnings in the `#file:main.py`.
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
- **UTF-8**: Import `Shared.utils.utf8_solution` in files with subprocess/console I/O
- **Logging**: Use logger instead of print() for debugging
- **File Size**: Keep files under 650 lines, decompose larger files
- **Framework Harmony**: Prefer Flet built-ins over custom solutions
- **Reasoning**: Apply sequential thinking MCP (Meta-Cognitive Programming) as much as possible to identify all problems/issues before attempting fixes. Use websearch and context7 MCP when you need up to date context and docs.
- **Proactivity**: The AI should be proactive in identifying and fixing issues, not just running tests without understanding the results. Use sequential thinking MCP every 5 tool calls to ensure a thorough understanding of the situation before proceeding with fixes.
- **System Integrity**: Make sure you are not breaking the system and removing functionality.
- **Problem Management**: Make sure to not cause more problems than you solve.
- **Data Source**: **ALWAYS USE REAL DATA FROM THE SERVER/DATABASE!** You can, optionally, add also a fallback to placeholder 'loren ipsum' instead of mock data. **NEVER use mock data.**
- **Bug Fixing**: When fixing errors, focus on syntax errors without changing functionality. Ensure that the code remains unbroken and that no new problems are introduced.
- **Code Quality**: Make sure there are no code/functions duplications and no redundencies.
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
    - User-level: `%USERPROFILE%\.qwen\settings.json` (on Windows; equivalently `~/.qwen/settings.json`)
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
  - **Refs and Deferred Updates**: Code may be updating controls before they are attached, or using controls reference wrongly (e.g., expecting .controls to exist when it's None), so nothing gets added to the UI. Ensure that after any `.controls` modification you call `.update()` on that parent control. Ensure the ref is not None before using; add a small wait (`page.run_task`) to populate after attachment or add safe guards like `if ref.current is None: skip update and log a warning, then schedule a retry`. Wrap dynamic control population in a small function and call it with `page.run_task` or schedule via `page.add_post_frame_callback` equivalent (Flet has `page.add_auto_close`? If not, call `page.update` after adding).
  - **Layout Structure**: Using Container vs Column vs Stack incorrectly may cause scroll or layout to be collapsed to zero height.
  - **Suppressed Exceptions**: Exceptions swallowed by `with contextlib.suppress(Exception)` in critical places, may be hiding the real error (a later AI/engineer should disable suppression to see the real stacktrace while debugging). Replace broad `contextlib.suppress(Exception)` with `logging.exception` to capture real errors during debug.
  - **Logs View Attachment Diagnostic**: Add a small diagnostic log + `page.update` in `logs.py`'s `setup_subscriptions` to verify that the Logs view is attaching correctly.
- **Embedded GUI**: To enable the embedded GUI set `CYBERBACKUP_DISABLE_INTEGRATED_GUI=0`. The server checks the environment flag incorrectly; the condition should treat only `'1'` as disable.
- **Data Type Handling in Logs View**: When handling data in the logs view, especially data received from the server, ensure that variables declared as lists are not inadvertently reassigned to dictionaries. Use temporary variables to inspect the server response and normalize the data into a consistent list format before further processing. This avoids static type checker errors and ensures that list operations are performed on valid list objects.
- **Flet GUI Startup**: The Flet GUI is now running! The GUI should now be accessible in the web browser. The application is running with:
  - Embedded GUI disabled (as expected for FletV2)
  - Logging initialized with console and file output
  - The server is ready to accept connections
  The Flet GUI should open automatically in the default web browser. If it doesn't appear, you can typically access it at `http://localhost:8550` (or ports 8551/8552 if 8550 is occupied).

### Key Principles
- **FletV2 First**: Use `FletV2/` directory exclusively (modern implementation)
- **Single Responsibility**: Components <300 lines, focused on one purpose
- **Async Patterns**: Use `page.run_task()` for background operations
- **Theme System**: Use TOKENS instead of hardcoded colors
- **Verification**: Check `received_files/` for actual transfers (not exit codes)
- **Avoid Assumptions**: Always check the current actual state and figure things out from there.
- **Reasoning**: Apply the highest reasoning, take your time.
- **System Integrity**: Make sure you are not breaking the system and removing functionality.
- **Problem Management**: Make sure you are not causing more problems than you are solving.
- **Code Removal**: Remove bad/unused/wrong/not appropriate/falty/duplicated/ redunded /unwanted/unnedded code, if this could be done without braking the system and not changing functionality.
- **Tri-Style Design**: Maintain the tri-style design (Material Design 3 + Neumorphism + Glassmorphism) when modifying the UI.

### Testing Strategy
- Integration tests verify end-to-end flows
- Component tests isolate Flet UI elements
- Always verify file presence in `received_files/` directory
- Test responsive layouts on 800x600 minimum window size

### Core Integration Patterns

#### Subprocess Management (CRITICAL)
```python
# Flask API → RealBackupExecutor → C++ client (with --batch flag)
# File Lifecycle: SynchronizedFileManager prevents race conditions
self.backup_process = subprocess.Popen(
    [self.client_exe, "--batch"],  # --batch prevents hanging in subprocess
    stdin=self.PIPE,
    stdout=self.PIPE,
    stderr=self.PIPE,
    text=True,
    cwd=os.path.dirname(os.path.abspath(__file__)),  # CRITICAL: Working directory
    env=Shared.utils.utf8_solution.get_env()  # UTF-8 environment
)
```

#### File Transfer Verification (CRITICAL)
Always verify file transfers by checking actual files in `received_files/` directory:
- Compare file sizes
- Compare SHA256 hashes
- Verify network activity on port 1256

#### Configuration Generation Pattern
```python
# transfer.info must be generated per operation (3-line format)
def _generate_transfer_info(self, server_ip, server_port, username, file_path):
    with open("transfer.info", 'w') as f:
        f.write(f"{server_ip}:{server_port}\n")  # Line 1: server endpoint
        f.write(f"{username}\n")                 # Line 2: username
        f.write(f"{file_path}\n")                # Line 3: absolute file path
```

---

# FletV2 Development Guide (Concise)

This AI Development Guide should be read in conjunction with the `#file:AI-Context` folder (for extremely important documentation, data, information, and rules) and the `#file:important_docs` folder (for important information and documentation).

This guide codifies the essential rules to generate high-quality, compatible, and efficient code for this repository, focused on the FletV2 application. It consolidates prior guidance into a single DRY reference.

CRITICAL: Work exclusively in `FletV2/`. The legacy `flet_server_gui/` is obsolete and kept only as a reference for anti-patterns to avoid. When in doubt, prefer Flet built-ins and patterns shown here. See `FletV2/important_docs/` for examples.

**CRITICAL**: Follow these exact import patterns to ensure proper module resolution and avoid import errors.

#### Parent Directory Path Management
```python
# Standard pattern for FletV2 files that need Shared imports
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
```

#### Import Organization (STRICT ORDER)
```python
# 1. Standard library imports (alphabetical)
import asyncio
import contextlib # ADDED: for contextlib.suppress
import logging
import os
import sys
from typing import Any, Callable, Dict, Optional, Set, Tuple, cast

import flet as ft

# 3. Local imports - utilities first
from utils.debug_setup import setup_terminal_debugging

# 4. ALWAYS import UTF-8 solution for subprocess/console I/O
import Shared.utils.utf8_solution as _  # noqa: F401,E402

# 5. Initialize logging BEFORE any logger usage
logger = setup_terminal_debugging(logger_name="module_name")

# 6. Local imports - application modules
from theme import setup_modern_theme
from utils.server_bridge import create_server_bridge
```

#### Import Anti-Patterns (AVOID)
```python
# ❌ WRONG: Star imports
from utils.server_bridge import *

# ❌ WRONG: Delayed UTF-8 import (causes encoding issues)
# Import at top level, not inside functions

# ❌ WRONG: Inconsistent sys.path management
# Always use the parent_dir pattern shown above

### Component Architecture Patterns

**CRITICAL**: Use function-based components that return `ft.Control`, not classes. This ensures composability and follows Flet best practices.

#### View Component Structure
```python
import flet as ft
from utils.ui_components import themed_button
from utils.user_feedback import show_error_message

def create_view(page: ft.Page, server_bridge, state_manager) -> ft.Control:
    # local state + handlers
    def on_refresh(e):
        try:
            data = server_bridge.get_data()
            items.controls = [ft.Text(d["title"]) for d in data]
            items.update()  # Prefer control.update() for perf
        except Exception as ex:
            show_error_message(page, f"Refresh failed: {ex}")

    refresh_btn = themed_button(text="Refresh", on_click=on_refresh, icon=ft.Icons.REFRESH)
    items = ft.Column(scroll=ft.ScrollMode=ft.ScrollMode.AUTO)
    return ft.Container(content=ft.Column([ft.Row([ft.Text("Example"), refresh_btn]), items]), padding=20)
```

#### Flet Component Development Best Practices

When creating UI components for Flet, follow these best practices:

##### 1. Single Inheritance Pattern
Always inherit from a single Flet control class:
```python
# ✅ CORRECT - Single inheritance
class EnhancedButton(ft.FilledButton):
    def __init__(self, text="", **kwargs):
        super().__init__(text=text, **kwargs)
        # Add custom functionality

# ❌ INCORRECT - Multiple inheritance
class BadButton(ft.FilledButton, ft.TextButton):
    def __init__(self, text="", **kwargs):
        super().__init__(text=text, **kwargs)
```

##### 2. Proper Initialization
Always call `super().__init__()` properly:
```python
class MyComponent(ft.Container):
    def __init__(self, content=None, **kwargs):
        # Pass Flet-native parameters to parent class
        super().__init__(content=content, **kwargs)

        # Set custom properties AFTER parent initialization
        self.custom_property = "value"
```

##### 3. Component Composition Over Complex Inheritance
Use composition when a single component isn't sufficient:
```python
class StatCard(ft.Card):
    def __init__(self, title, value, **kwargs):
        # Create content using Flet controls
        content = ft.Column([
            ft.Text(title, size=16, weight=ft.FontWeight.W_500),
            ft.Text(str(value), size=24, weight=ft.FontWeight.W_300)
        ])

        # Initialize parent with composed content
        super().__init__(content=content, **kwargs)
```

##### 4. Flet-Native Properties
Leverage Flet's built-in properties instead of custom implementations where possible:
```python
# ✅ CORRECT - Use Flet's built-in properties
class MyButton(ft.FilledButton):
    def __init__(self, text="", **kwargs):
        super().__init__(text=text, **kwargs)
        self.bgcolor = ft.Colors.PRIMARY  # Use Flet's color constants
        self.height = 40  # Direct property assignment

# ❌ INCORRECT - Custom property management
class MyButton:
    def __init__(self, text="", **kwargs):
        self._bgcolor = None
        self._height = None
        # Custom property management is unnecessary
```

##### 5. Event Handling Patterns
Use Flet's event system properly:
```python
class ClickableCard(ft.Card):
    def __init__(self, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.on_click = on_click  # Set event handler directly

    def handle_click(self, e):
        if self.on_click:
            self.on_click(e)
```

##### 6. State Management
Manage component state using Flet's update mechanism:
```python
class StatefulButton(ft.FilledButton):
    def __init__(self, text="", **kwargs):
        super().__init__(text=text, **kwargs)
        self._state = "enabled"

    def set_state(self, state):
        self._state = state
        if state == "loading":
            self.disabled = True
            self.text = "Loading..."
        elif state == "disabled":
            self.disabled = True
        else:
            self.disabled = False
            self.text = "Click me"
        self.update()  # Trigger UI update
```

### Async Programming Patterns

## ⚡ Async Programming

Never block the UI thread. Use `page.run_task()` and `run_in_executor()` for blocking work.
```python
# Minimal patterns
async def handle_backup_start(e):
    # Update UI immediately
    start_button.disabled = True
    start_button.text = "Starting..."
    page.update()

    try:
        # Run blocking operation in thread pool
        result = await asyncio.get_event_loop().run_in_executor(
            None, perform_backup_operation, backup_config
        )

        # Update UI with results
        show_success_message(page, f"Backup completed: {result}")
        update_backup_status(result)

    except Exception as ex:
        logger.error(f"Backup failed: {ex}")
        show_error_message(page, f"Backup failed: {str(ex)}")

    finally:
        # Always restore UI state
        start_button.disabled = False
        start_button.text = "Start Backup"
        page.update()
```

#### Background Tasks with page.run_task()
```python
# ✅ CORRECT: Use page.run_task() for background operations
def start_background_monitoring(e):
    """Start background monitoring task."""
    async def monitor_task():
        while monitoring_active:
            try:
                # Perform monitoring operation
                status = await server_bridge.get_status()
                update_monitoring_display(status)
                # Wait before next check
                await asyncio.sleep(5)

            except Exception as ex:
                logger.error(f"Monitoring error: {ex}")
                break

    # Start the background task
    page.run_task(monitor_task)
```

#### Threading for CPU-bound Operations
```python
import concurrent.futures

# ✅ CORRECT: Use ThreadPoolExecutor for CPU-bound work
def handle_data_processing(e):
    """Process large dataset without blocking UI."""
    async def process_async():
        def cpu_intensive_work():
            # CPU-bound processing here
            return process_large_dataset(data)

            result = await asyncio.get_event_loop().run_in_executor(None, cpu_intensive_work)

        display_results(result)
        page.update()

    page.run_task(process_async)
```

#### Async Anti-Patterns (AVOID)
```python
# ❌ WRONG: Blocking operations in async handlers
async def bad_handler(e):
    result = blocking_file_operation()  # Blocks event loop!
    await update_ui(result)  # Never reached

# ❌ WRONG: Incorrect async UI updates
async def bad_ui_update(e):
    await page.update_async()  # update_async() doesn't exist in Flet

# ❌ WRONG: Mixing sync and async incorrectly
def sync_function():
    asyncio.run(async_operation())  # Don't do this in event handlers
```

#### Flet Async Task Management Patterns
```python
# Pattern 1: Simple async method calls
# ❌ INCORRECT - Calling the coroutine instead of passing it
self.page.run_task(self.action_handlers.clear_logs())

# ✅ CORRECT - Pass the coroutine function itself
self.page.run_task(self.action_handlers.clear_logs)

# Pattern 2: Parameterized async method calls
# ❌ INCORRECT - Calling the coroutine with parameters
self.page.run_task(self.action_handlers.export_logs(filter_level, filter_component, search_query))

# ✅ CORRECT - Create a wrapper function to capture parameters
async def export_logs_wrapper():
    await self.action_handlers.export_logs(filter_level, filter_component, search_query)
self.page.run_task(export_logs_wrapper)
```

### Error Handling Patterns

**CRITICAL**: Implement proper error handling with user feedback and logging.

#### User Feedback with SnackBar
```python
from utils.user_feedback import show_success_message, show_error_message

def handle_operation(e):
    """Handle operation with proper error handling and user feedback."""
    try:
        # Perform operation
        result = perform_operation()

        # Show success message
        show_success_message(page, f"Operation completed successfully: {result}")

        # Update UI
        update_display(result)

    except ValueError as ex:
        # Handle validation errors
        logger.warning(f"Validation error: {ex}")
        show_error_message(page, f"Invalid input: {str(ex)}")

    except ConnectionError as ex:
        # Handle connection errors
        logger.error(f"Connection failed: {ex}")
        show_error_message(page, "Connection failed. Please check network settings.")

    except Exception as ex:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {ex}", exc_info=True)
        show_error_message(page, f"An unexpected error occurred: {str(ex)}")
```

#### Async Error Handling
```python
async def handle_async_operation(e):
    """Handle async operation with proper error handling."""
    # Update UI to show loading state
    button.disabled = True
    button.text = "Processing..."
    page.update()

    try:
        # Perform async operation
        result = await perform_async_operation()

        # Show success
        show_success_message(page, "Operation completed successfully")
        update_ui_with_result(result)

    except asyncio.TimeoutError:
        logger.error("Operation timed out")
        show_error_message(page, "Operation timed out. Please check your network connection or try again later.")

    except Exception as ex:
        logger.error(f"Operation failed: {ex}", exc_info=True)
        show_error_message(page, f"Operation failed: {str(ex)}")

    finally:
        # Restore UI state
        button.disabled = False
        button.text = "Start Operation"
        page.update()
```

#### contextlib.suppress Usage

Prefer `contextlib.suppress(Exception)` for concise suppressed-exception blocks. This improves code readability and addresses Sourcery warnings related to bare `try/except` blocks that simply pass.

Example:

```python
import contextlib

# Instead of:
try:
    some_operation()
except Exception:
    pass

# Use:
with contextlib.suppress(Exception):
    some_operation()
```

Apply this pattern when silencing expected and non-critical exceptions, particularly in UI update and subscription setup routines.

#### Recursive Visibility Fixer

When forcing visibility of nested dashboard controls, use `contextlib.suppress` within the recursive function to handle potential errors during property access and updates. This ensures that the process continues even if specific controls raise exceptions.

```python
import contextlib

def _force_visible_recursive(ctrl, depth: int = 0, max_depth: int = 10) -> None:
    if ctrl is None:
        return

    # Prefer contextlib.suppress for concise suppressed-exception blocks
    with contextlib.suppress(Exception):
        if hasattr(ctrl, 'visible') and ctrl.visible is False:
            ctrl.visible = True

    with contextlib.suppress(Exception):
        if hasattr(ctrl, 'opacity') and ctrl.opacity is not None and ctrl.opacity != 1.0:
            ctrl.opacity = 1.0

    with contextlib.suppress(Exception):
        if hasattr(ctrl, 'update'):
            try:
                ctrl.update()
            except Exception:
                # Keep the inner safety for update() call failures
                pass

    if depth >= max_depth:
        return

    # Suppress errors across recursive descent (safer and clearer than a bare try/except)
    with contextlib.suppress(Exception):
        if hasattr(ctrl, 'controls') and ctrl.controls:
            for child in list(ctrl.controls):
                _force_visible_recursive(child, depth + 1, max_depth)

        if hasattr(ctrl, 'content') and ctrl.content:
            _