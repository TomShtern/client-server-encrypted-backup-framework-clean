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

## 🏗️ System Architecture Overview

This is a **production-grade 5-layer encrypted backup system** with hybrid web-to-native-desktop architecture:

```
Web UI → Flask API Bridge → C++ Client (subprocess) → Python Server → Flet Desktop GUI
  ↓           ↓                    ↓                     ↓                     ↓
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
```

#### C++
```bash
# Build: cmake with vcpkg toolchain
cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake" && cmake --build build --config Release

# Format: clang-format -i file.cpp (Google style, 100 cols, 4-space indent)
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
- **Error Handling**: Try/except with specific exceptions, log errors with context
- **Async**: Use async/await for I/O operations, avoid blocking calls
- **Indentation**: Correct any unexpected indentation issues by ensuring code blocks are properly scoped. Run linters (e.g., `ruff check .`) to verify code style.

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
- **Data Source**: **ALWAYS USE REAL DATA FROM THE SERVER/DATABASE!** You can, optionally, add also a fallback to placeholder. Use real data from the python server and the sqlite3. If real data is unavailable, display 'No real data' or a simple 'loren ipsum' instead of mock data. **NEVER use mock data.**

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
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
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
import contextlib
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
    items = ft.Column(scroll=ft.ScrollMode.AUTO)
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

### Error Handling & Feedback
Use robust try/except with logging and Snackbar messages via `utils.user_feedback`.

#### StateManager Integration
```python
from utils.state_manager import StateManager

def create_dashboard_view(page: ft.Page, server_bridge: ServerBridge, state_manager: StateManager) -> ft.Control:
    """Create dashboard view with reactive state management."""

    # Subscribe to state changes
    def on_progress_update(progress_data):
        """Handle progress updates from state manager."""
        progress_bar.value = progress_data.get('percentage', 0) / 100
        progress_text.value = progress_data.get('message', '')
        page.update()

    # Subscribe to progress updates
    state_manager.subscribe_settings('progress', on_progress_update)

    def start_operation(e):
        """Start operation and update state."""
        # Update state - triggers reactive updates
        state_manager.set_progress({
            'percentage': 0,
            'message': 'Starting operation...'
        })
    # Perform operation

    # UI components that react to state changes
    progress_bar = ft.ProgressBar(value=0)
    progress_text = ft.Text('')

    return ft.Container(
        content=ft.Column([
            ft.Text("Dashboard", size=24, weight=ft.FontWeight.BOLD),
            progress_bar,
            progress_text,
            themed_button("Start", on_click=start_operation)
        ])
    )
```

#### Reactive UI Updates
```python
def create_reactive_component(state_manager: StateManager) -> ft.Control:
    """Create component that reacts to state changes."""
    local_data = {}
    def on_data_change(new_data):
        """Handle data changes from state manager."""
        nonlocal local_data
        local_data = new_data
        update_display()

    def update_display():
        """Update UI with current data."""
        data_container.controls = [
            create_data_row(item) for item in local_data.values()
        ]
        page.update()

    # Subscribe to data changes
    state_manager.subscribe_settings('data', on_data_change)

    data_container = ft.Column()
    return data_container
```

#### StateManager Anti-Patterns (AVOID)
```python
def bad_update_pattern(e):
    # Avoid scattered page.update() calls and prefer control.update() when possible
    button.text = "Loading..."
    page.update()  # Scattered calls
    # ... more code ...
    page.update()  # More scattered calls

# ❌ WRONG: No state synchronization
def bad_state_management():
    # Local variables not synced with global state
    local_counter = 0  # Gets out of sync
    # No reactive updates when state changes elsewhere
```

### UI Component Patterns

**CRITICAL**: Use themed UI components for consistent styling and maintainability.

#### Themed Component Usage
```python
from utils.ui_components import themed_card, themed_button, create_info_card

def create_dashboard_cards() -> ft.Control:
    """Create dashboard using themed components."""

    # Primary action button
    start_button = themed_button(
        text="Start Backup",
        on_click=handle_start_backup,
        icon=ft.Icons.PLAY_ARROW,
        variant="primary"
    )

    # Secondary action button
    settings_button = themed_button(
        text="Settings",
        on_click=handle_open_settings,
        icon=ft.Icons.SETTINGS,
        variant="secondary"
    )

    # Destructive action button
    stop_button = themed_button(
        text="Stop Server",
        on_click=handle_stop_server,
        icon=ft.Icons.STOP,
        variant="destructive"
    )

    # Information card
    status_card = themed_card(
        title="Server Status",
        content=ft.Column([
            ft.Text("Uptime: 2h 15m"),
            ft.Text("Connections: 3")
        ]),
        variant="info"
    )

    # Success card
    backup_card = themed_card(
        title="Last Backup",
        content=ft.Text("Completed successfully at 14:30"),
        variant="success"
    )

    return ft.Container(
        content=ft.Column([
            ft.Row([status_card, backup_card])
        ])
    )
```

#### Custom Component Creation
```python
def create_metric_card(title: str, value: str, trend: str, icon: str) -> ft.Control:
    """Create a metric card with consistent styling."""
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(icon, size=24, color=ft.Colors.PRIMARY),
                ft.Text(title, size=14, weight=ft.FontWeight.W_500)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text(value, size=28, weight=ft.FontWeight.BOLD),
            ft.Text(trend, size=12, color=ft.Colors.GREEN if "up" in trend.lower() else ft.Colors.RED)
        ]),
        padding=20,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=4,
            color=ft.Colors.with_opacity(0.1, ft.Colors.SHADOW),
            offset=ft.Offset(0, 2)
        )
    )
```

#### ListView for Large Datasets
```python
def create_data_list(items: List[Dict[str, Any]]) -> ft.Control:
    """Create efficient list for large datasets."""
    return ft.Container(
        content=ft.ListView(
            controls=[
                create_list_item(item) for item in items
            ],
            expand=True,
            spacing=8,
            semantic_child_count=len(items)  # Performance optimization
        ),
        height=400  # Fixed height for virtualization
    )

def create_list_item(item: Dict[str, Any]]) -> ft.Control:
    """Create individual list item."""
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.FILE_PRESENT, size=20),
            ft.Column([
                ft.Text(item['name'], weight=ft.FontWeight.W_500),
                ft.Text(f"Size: {item['size']}", size=12, color=ft.Colors.OUTLINE)
            ], expand=True),
            ft.Text(item['date'], size=12, color=ft.Colors.OUTLINE)
        ]),
        padding=12,
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_VARIANT,
    )
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
        show_error_message(page, "Operation timed out. Please try again.")

    except Exception as ex:
        logger.error(f"Async operation failed: {ex}", exc_info=True)
        show_error_message(page, f"Operation failed: {str(ex)}")

    finally:
        # Always restore UI state
        button.disabled = False
        button.text = "Start Operation"
        page.update()
```

#### Error Boundary Pattern
```python
def create_safe_component(component_factory, fallback_content=None):
    """Create component with error boundary."""
    try:
        return component_factory()
    except Exception as ex:
        logger.error(f"Component creation failed: {ex}", exc_info=True)

        # Return fallback content
        if fallback_content is None:
            fallback_content = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ERROR, color=ft.Colors.ERROR, size=48),
                    ft.Text("Component failed to load", color=ft.Colors.ERROR),
                    ft.Text(str(ex), size=12, color=ft.Colors.OUTLINE)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=20,
                border=ft.border.all(1, ft.Colors.ERROR),
                border_radius=8
            )

        return fallback_content
```

#### Error Handling Anti-Patterns (AVOID)
```python
# ❌ WRONG: Silent error handling
def bad_error_handling():
    try:
        risky_operation()
    except:
        pass  # Never do this - errors disappear

# ❌ WRONG: Generic exception handling
def bad_generic_catch():
    try:
        operation()
    except Exception as ex:
        print(f"Error: {ex}")  # No logging, no user feedback

# ❌ WRONG: UI updates in exception handlers
def bad_ui_in_catch():
    try:
        operation()
    except Exception as ex:
        button.text = "Error!"  # UI updates in catch block
        page.update()  # Can cause more errors
```

### Configuration Management Patterns

**CRITICAL**: Use centralized configuration management with environment variables and validation.

#### Configuration Loading
```python
#!/usr/bin/env python3
"""
Configuration and Constants for FletV2.
"""

import os
from pathlib import Path
from contextlib import suppress
from contextlib import suppress

# Load environment variables from .env file if it exists
with suppress(ImportError):
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()

# Debug mode - controls visibility of mock data and debug features
DEBUG_MODE = os.environ.get('FLET_V_DEBUG', 'false').lower() == 'true'

# Secure secret handling from environment variables
GITHUB_PERSONAL_ACCESS_TOKEN = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN')
SERVER_API_KEY = os.environ.get('SERVER_API_KEY')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

# Real server configuration
REAL_SERVER_URL = os.environ.get('REAL_SERVER_URL')  # e.g., https://backup.example.com/api
BACKUP_SERVER_TOKEN = os.environ.get('BACKUP_SERVER_TOKEN') or os.environ.get('BACKUP_SERVER_API_KEY')
REQUEST_TIMEOUT = float(os.environ.get('REQUEST_TIMEOUT', '10'))
VERIFY_TLS = os.environ.get('VERIFY_TLS', 'true').lower() == 'true'

# Optional: Validate critical secrets in debug mode
if DEBUG_MODE:
    if not GITHUB_PERSONAL_ACCESS_TOKEN:
        print("Warning: GITHUB_PERSONAL_ACCESS_TOKEN not set")
    if not SERVER_API_KEY:
        print("Warning: SERVER_API_KEY not set")
    if not DATABASE_PASSWORD:
        print("Warning: DATABASE_PASSWORD not set")
    if not REAL_SERVER_URL:
        print("Info: REAL_SERVER_URL not set - running in mock mode unless a real server is injected")
    if REAL_SERVER_URL and not REAL_SERVER_URL.startswith(('https://', 'http://')):
        print("Warning: REAL_SERVER_URL should start with https:// or http://")
    if not BACKUP_SERVER_TOKEN:
        print("Info: BACKUP_SERVER_TOKEN not set - endpoints requiring auth will fail in real mode")

# Mock data visibility - when False, mock data is only used when server is unavailable
SHOW_MOCK_DATA = DEBUG_MODE

# Async operation delays for simulation
ASYNC_DELAY = 0.5  # seconds

# Server connection timeout
CONNECTION_TIMEOUT = 30  # seconds
```

#### Environment Variable Validation
```python
def validate_environment():
    """Validate required environment variables and provide helpful errors."""
    required_vars = {
        'FLET_V_DEBUG': 'Controls debug mode and mock data visibility',
        'REAL_SERVER_URL': 'URL for production server integration',
        'BACKUP_SERVER_TOKEN': 'Authentication token for server API'
    }

    missing_vars = []
    for var, description in required_vars.items():
        if not os.environ.get(var):
            missing_vars.append(f"{var}: {description}")

    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var_info in missing_vars:
            print(f"   - {var_info}")
        print("\nCreate a .env file or set these environment variables.")

    return len(missing_vars) == 0
```

#### Configuration Anti-Patterns (AVOID)
```python
# ❌ WRONG: Hardcoded configuration values
API_URL = "http://localhost:8000"  # Don't hardcode!

# ❌ WRONG: No environment variable loading
DEBUG = True  # No way to change in production

# ❌ WRONG: No validation of required config
# Missing validation leads to runtime errors
```

### Testing Patterns

**CRITICAL**: Follow proper testing patterns for reliable and maintainable tests.

#### Unit Test Structure
```python
#!/usr/bin/env python3
"""
Unit tests for the server bridge modules.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch

# Set debug mode to enable mock data
os.environ['FLET_V_DEBUG'] = 'true'

# Add the FletV2 directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.server_bridge import ServerBridge, create_server_bridge


class TestSimpleServerBridge(unittest.TestCase):
    """Test cases for the simple bridge interface (now unified ServerBridge)."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        with patch('utils.server_bridge.logger'):
            self.bridge = ServerBridge()

    def test_initialization(self):
        """Test that the bridge initializes correctly."""
        self.assertIsInstance(self.bridge, ServerBridge)
        self.assertTrue(self.bridge.is_connected())

    def test_get_clients(self):
        """Test getting client data."""
        clients = self.bridge.get_clients()
        self.assertIsInstance(clients, list)
        self.assertGreater(len(clients), 0)

        # Check structure of first client
        if clients:
            client = clients[0]  # clients is a list, accessing first element
            required_keys = ['client_id', 'address', 'status', 'connected_at', 'last_activity']
            for (key) in required_keys:
                self.assertIn(key, client)

    def test_get_files(self):
        """Test getting file data."""
        files = self.bridge.get_files()
        self.assertIsInstance(files, list)

        # Add mocking for ServerBridge to resolve type mismatch errors when testing views

#### Mocking

When mocking `ServerBridge` in tests, use `unittest.mock.Mock` with `spec=ServerBridge` to ensure type compatibility:

```python
    from utils.server_bridge import ServerBridge
    from unittest.mock.Mock import Mock