---
description: AI rules derived by SpecStory from the project AI interaction history
globs: *
---

```markdown
---
description: AI rules derived by SpecStory from the project AI interaction history
---

---
description: AI rules derived by SpecStory from the project AI interaction history
---

---
description: AI rules derived by SpecStory from the project AI interaction history
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

def create_list_item(item: Dict[str, Any]) -> ft.Control:
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
        bgcolor=ft.Colors.SURFACE_VARIANT
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

# Load environment variables from .env file if it exists
with suppress(ImportError):
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()

# Debug mode - controls visibility of mock data and debug features
DEBUG_MODE = os.environ.get('FLET_V2_DEBUG', 'false').lower() == 'true'

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
        'FLET_V2_DEBUG': 'Controls debug mode and mock data visibility',
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
os.environ['FLET_V2_DEBUG'] = 'true'

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


if __name__ == '__main__':
    unittest.main()
```

#### Mocking Patterns
```python
import unittest
from unittest.mock import Mock, patch, MagicMock

class TestViewComponents(unittest.TestCase):
    """Test view components with proper mocking."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock Flet page
        self.mock_page = Mock()
        self.mock_page.update = Mock()

        # Mock server bridge
        self.mock_server_bridge = Mock()
        self.mock_server_bridge.get_clients.return_value = [
            {
                'client_id': 'test-1',
                'address': '192.168.1.100',
                'status': 'connected',
                'connected_at': '2025-01-01T10:00:00Z',
                'last_activity': '2025-01-01T10:30:00Z'
            }
        ]

        # Mock state manager
        self.mock_state_manager = Mock()

    @patch('utils.user_feedback.show_success_message')
    def test_successful_operation(self, mock_show_success):
        """Test successful operation with mocked dependencies."""
        # Arrange
        from views.clients import handle_client_action

        # Act
        handle_client_action(
            self.mock_page,
            self.mock_server_bridge,
            self.mock_state_manager
        )

        # Assert
        mock_show_success.assert_called_once()
        self.mock_page.update.assert_called()
```

#### Integration Test Patterns
```python
import pytest
import flet as ft
from utils.server_bridge import create_server_bridge
from utils.state_manager import StateManager

class TestDashboardIntegration:
    """Integration tests for dashboard functionality."""

    @pytest.fixture
    def setup_app(self):
        """Set up test application."""
        # Create test page
        page = ft.Page()
        server_bridge = create_server_bridge()
        state_manager = StateManager()

        return page, server_bridge, state_manager

    def test_dashboard_loads_data(self, setup_app):
        """Test that dashboard loads and displays data correctly."""
        page, server_bridge, state_manager = setup_app

        # Create dashboard view
        from views.dashboard import create_dashboard_view
        dashboard = create_dashboard_view(page, server_bridge, state_manager)

        # Verify structure
        assert isinstance(dashboard, ft.Container)
        assert len(dashboard.content.controls) > 0

        # Verify data loading
        clients = server_bridge.get_clients()
        assert len(clients) > 0

    def test_reactive_updates(self, setup_app):
        """Test that UI reacts to state changes."""
        page, server_bridge, state_manager = setup_app

        # Subscribe to state changes
        update_called = False
        def on_update(data):
            nonlocal update_called
            update_called = True

        state_manager.subscribe_settings('test', on_update)

        # Trigger state change
        state_manager.set_settings('test', {'value': 'new'})

        # Verify reactive update
        assert update_called
```

#### Testing Anti-Patterns (AVOID)
```python
# ❌ WRONG: Testing implementation details
def test_internal_method(self):
    # Don't test private methods directly
    bridge = ServerBridge()
    bridge._internal_method()  # Avoid testing private methods

# ❌ WRONG: No mocking of external dependencies
def test_with_real_network(self):
    # Don't make real network calls in unit tests
    result = make_http_request('http://real-api.com')  # Slow, unreliable

# ❌ WRONG: Testing without proper setup
def test_without_setup(self):
    # Missing setUp/tearDown
    page = ft.Page()  # No proper initialization
    # Test will be flaky
```

#### Comprehensive Integration Tests

To ensure the stability and functionality of the FletV2 application, the following integration tests are recommended:

- **View Integration Tests**: Each FletV2 view (Dashboard, Clients, Files, Database, Logs) should be tested to ensure they load correctly and display real server data.
- **Server Operation Tests**: Verify that server operations such as adding/deleting clients and file management work correctly through the GUI.
- **Error Handling Tests**: Implement tests for error handling and graceful degradation scenarios to ensure the application behaves predictably under various failure conditions. Ensure the application behaves predictably under various failure conditions.
- **Relevant Files**: `@views`, `@tests`, `@main.py`

To address the `ModuleNotFoundError: No module named 'utils'` errors in the integration tests, the following pattern MUST be followed:

- Add `sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))` to the beginning of each integration test file. This ensures that the `utils` module can be found.

#### Integration Test Example - Logs View

```python
#!/usr/bin/env python3
"""Integration tests for Logs view with ServerBridge (mock-backed)."""

import os
import sys
import unittest

import flet as ft

# Ensure FletV2 root is on sys.path for `utils`, `views`, etc.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

os.environ.setdefault("FLET_V2_DEBUG", "true")

from utils.server_bridge import create_server_bridge
from utils.state_manager import StateManager
from views.logs import create_logs_view
from tests.integration_utils import FakePage


class TestLogsIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.page: ft.Page = FakePage()  # type: ignore[assignment]
        self.bridge = create_server_bridge()
        self.state_manager = StateManager(self.page, self.bridge)

    def test_logs_view_loads_and_filters(self):
        view, dispose, setup = create_logs_view(self.bridge, self.page, self.state_manager)
        self.assertIsInstance(view, ft.Control)
        setup()

        # Bridge should respond for logs in mock mode
        result = self.bridge.get_logs()
        self.assertTrue(result.get("success", False))
        data = result.get("data", [])
        self.assertIsInstance(data, list)

        dispose()


if __name__ == "__main__":
    unittest.main()
```

#### Fix: ImportError "No module named 'utils.debug_setup'" when launching FletV2
```markdown
Problem
- The app crashes on startup with: No module named 'utils.debug_setup'.
- Cause: The sys.path bootstrap in one or more entry files points to the wrong directory level (it goes too far up), so Python can’t see FletV2/utils.

Why this happens
- The project uses an import like:
  from utils.debug_setup import setup_terminal_debugging
- This requires FletV2 (the folder that contains utils/) to be on sys.path before imports run.
- Some files use a “two-levels up” pattern:
  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  In top-level files (directly under FletV2/), that resolves to the repo root’s parent, dropping FletV2 from sys.path and breaking utils.* imports.

Resolution (precise steps)

1) Fix the sys.path setup in entry modules
- In every file directly under FletV2/ that imports utils.* (e.g., FletV2/main.py, FletV2/app.py, any launcher), replace the two-level pattern with this exact snippet at the very top (before any other imports):

```python
import os
import sys

# Ensure FletV2 root is on sys.path (works for files for files in FletV2/ and its subfolders)
_here = os.path.abspath(__file__)
_base = os.path.dirname(_here)
if os.path.basename(_base) == "FletV2":
    flet_v2_root = _base
else:
    flet_v2_root = os.path.dirname(_base)  # if file is in a subfolder

if flet_v2_root not in sys.path:
    sys.path.insert(0, flet_v2_root)

# Optional: enable Shared.* imports if Shared is a sibling of FletV2
repo_root = os.path.dirname(flet_v2_root)
if os.path.isdir(os.path.join(repo_root, "Shared")) and repo_root not in sys.path:
    sys.path.insert(0, repo_root)
```

- Do not remove the import order you already follow; keep the imports exactly as documented after this snippet.

2) Verify utils package structure
- Ensure these paths exist:
  - FletV2/utils/__init__.py (can be empty; ensures package import across environments)
  - FletV2/utils/debug_setup.py (must define setup_terminal_debugging)

If FletV2/utils/debug_setup.py is missing, create it with:

```python
# filepath: c:\Users\tom7s\Desktopp\Claude_Folder_2\Client_Server_Encrypted_Backup_Framework\FletV2\utils\debug_setup.py
import logging
import sys

def setup_terminal_debugging(logger_name: str = "app", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    if not logger.handlers:
        handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger
```

3) Keep the documented import order
- After the path snippet, follow the project’s strict import order, including:
  - from utils.debug_setup import setup_terminal_debugging
  - import Shared.utils.utf8_solution as _  # if you use Shared
  - logger = setup_terminal_debugging(logger_name="module_name")

4) Find and fix all affected files
- In VS Code, search for these to locate offenders:
  - Query: from utils.debug_setup
  - Query: os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
- Apply Step 1 to each file that’s directly under FletV2/ or that fails to import utils.*

5) Validate
- From the repo root in Terminal (Windows):
  - python -V  (ensure ≥ 3.9)
  - python .\FletV2\main.py  (or your actual launcher)
- Expected: App starts; no ImportError for utils.debug_setup.

Notes
- If your Shared package is located inside FletV2 (FletV2/Shared), you do not need the repo_root insertion; the snippet above supports both layouts safely.
- sys.path.insert(0, ...) ensures project imports win over similarly named external packages (like a pip-installed utils).
```

### Performance Optimization Patterns

**CRITICAL**: Use performance-optimized patterns for smooth UI and efficient data handling.

#### ListView