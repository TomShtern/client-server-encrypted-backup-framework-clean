# AGENTS.md - Development Guidelines for AI Coding Agents

## Project Overview

This is a **5-layer encrypted backup system** with hybrid web-to-native-desktop architecture:

```
Web UI → Flask API Bridge → C++ Client (subprocess) → Python Server → Flet Desktop GUI
  ↓           ↓                    ↓                     ↓                     ↓
HTTP      RealBackupExecutor    --batch mode       Custom Binary       Material Design 3
requests  process management   + transfer.info     Custom Binary TCP   Server Management
```

**Critical Components**:
- **C++ Client**: Production-ready executable with RSA/AES encryption, CRC verification, and --batch mode for subprocess integration
- **Flask API Bridge**: HTTP API server (port 9090) coordinating between web UI and native client
- **Python Server**: Multi-threaded TCP server (port 1256) with file storage in `received_files/`
- **Flet Desktop GUI**: Material Design 3 server management interface with modular architecture
- **SQLite3 Database**: Client and file tracking storage

## Build/Lint/Test Commands

### Python
- **Lint**: `ruff check .` (line-length=110, rules: E,F,W,B,I)
- **Format**: `ruff format .`
- **Type Check**: `mypy .` (strict mode, Python 3.13.5)
- **Test All**: `pytest tests/`
- **Test Single**: `pytest tests/test_specific_file.py::TestClass::test_method -v`
- **Test Integration**: `pytest tests/integration/ -v`

### C++
- **Build**: `cmake -B build -DCMAKE_TOOLCHAIN_FILE="vcpkg/scripts/buildsystems/vcpkg.cmake" && cmake --build build --config Release`
- **Format**: `clang-format -i file.cpp` (Google style, 100 cols, 4-space indent)

### Full System
- **One-Click Build+Run**: `python scripts/one_click_build_and_run.py`

## Code Style Guidelines

### Python
- **Imports**: Standard library first, then third-party, then local (alphabetical within groups)
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants
- **Types**: Use type hints, strict mypy compliance
- **Line Length**: 110 characters max
- **Error Handling**: Try/except with specific exceptions, log errors with context
- **Async**: Use async/await for I/O operations, avoid blocking calls

### C++
- **Style**: Google C++ style with clang-format
- **Indentation**: 4 spaces, no tabs
- **Braces**: Attach to function/class, new line for control statements
- **Pointers**: Left-aligned (*)
- **Includes**: Group by type, alphabetical within groups

### General
- **UTF-8**: Import `Shared.utils.utf8_solution` in files with subprocess/console I/O
- **Logging**: Use logger instead of print() for debugging
- **File Size**: Keep files under 650 lines, decompose larger files
- **Framework Harmony**: Prefer Flet built-ins over custom solutions

## AI Assistant Rules

### Copilot Instructions
See `.github/copilot-instructions-updated.md` for comprehensive development guidelines including:
- 5-layer encrypted backup architecture
- Flet Material Design 3 patterns
- Integration testing protocols
- Anti-patterns to avoid

### Key Principles
- **FletV2 First**: Use `FletV2/` directory exclusively (modern implementation)
- **Single Responsibility**: Components <300 lines, focused on one purpose
- **Async Patterns**: Use `page.run_task()` for background operations
- **Theme System**: Use TOKENS instead of hardcoded colors
- **Verification**: Check `received_files/` for actual transfers (not exit codes)

### Testing Strategy
- Integration tests verify end-to-end flows
- Component tests isolate Flet UI elements
- Always verify file presence in `received_files/` directory
- Test responsive layouts on 800x600 minimum window size

## Core Integration Patterns

### Subprocess Management (CRITICAL)
```python
# Flask API → RealBackupExecutor → C++ client (with --batch flag)
# File Lifecycle: SynchronizedFileManager prevents race conditions
self.backup_process = subprocess.Popen(
    [self.client_exe, "--batch"],  # --batch prevents hanging in subprocess
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    cwd=os.path.dirname(os.path.abspath(self.client_exe)),  # CRITICAL: Working directory
    env=Shared.utils.utf8_solution.get_env()  # UTF-8 environment
)
```

### File Transfer Verification (CRITICAL)
Always verify file transfers by checking actual files in `received_files/` directory:
- Compare file sizes
- Compare SHA256 hashes
- Verify network activity on port 1256

### Configuration Generation Pattern
```python
# transfer.info must be generated per operation (3-line format)
def _generate_transfer_info(self, server_ip, server_port, username, file_path):
    with open("transfer.info", 'w') as f:
        f.write(f"{server_ip}:{server_port}\n")  # Line 1: server endpoint
        f.write(f"{username}\n")                 # Line 2: username  
        f.write(f"{file_path}\n")                # Line 3: absolute file path
```

### Flet Async Task Management Patterns
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

## Flet Component Development Best Practices

### Creating Flet-Style Components

When creating UI components for Flet, follow these best practices:

#### 1. Single Inheritance Pattern
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

#### 2. Proper Initialization
Always call `super().__init__()` properly:
```python
class MyComponent(ft.Container):
    def __init__(self, content=None, **kwargs):
        # Pass Flet-native parameters to parent class
        super().__init__(content=content, **kwargs)
        
        # Set custom properties AFTER parent initialization
        self.custom_property = "value"
```

#### 3. Component Composition Over Complex Inheritance
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

#### 4. Flet-Native Properties
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

#### 5. Event Handling Patterns
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

#### 6. State Management
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

## Flet Development Patterns

### View Creation Pattern (MANDATORY)
```python
def create_view_name(server_bridge, page: ft.Page, state_manager=None):
    """Create view using pure Flet patterns."""
    
    # Refs for precise updates (10x performance)
    loading_ref = ft.Ref[ft.ProgressRing]()
    table_ref = ft.Ref[ft.DataTable]()
    status_ref = ft.Ref[ft.Text]()

    # Data loading with fallback
    def get_data():
        if server_bridge:
            try:
                return server_bridge.get_data()
            except Exception:
                pass
        return {"fallback": "data"}

    # Complete async handler with error handling & loading states
    async def on_action(e):
        loading_ref.current.visible = True
        loading_ref.current.update()
        try:
            result = await state_manager.server_mediated_update(
                key="action_key", value={"data": "value"},
                server_operation="server_method", param1, param2
            )
            if result.get('success'):
                show_success_message(page, "Operation completed")
                await refresh_data()
            else:
                show_error_message(page, f"Failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            show_error_message(page, f"Error: {str(e)}")
        finally:
            loading_ref.current.visible = False
            loading_ref.current.update()

    # Data table with action buttons
    def create_action_buttons(item_id):
        return ft.Row([
            ft.IconButton(ft.Icons.EDIT, on_click=lambda e: edit_item(item_id)),
            ft.IconButton(ft.Icons.DELETE, on_click=lambda e: delete_item(item_id))
        ], spacing=5)

    data_table = ft.DataTable(
        ref=table_ref,
        columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Status")), ft.DataColumn(ft.Text("Actions"))],
        rows=[ft.DataRow(cells=[
            ft.DataCell(ft.Text(str(item.get('id', '')))),
            ft.DataCell(ft.Text(str(item.get('status', '')))),
            ft.DataCell(create_action_buttons(item.get('id')))
        ]) for item in get_data()]
    )

    # State manager subscription for reactive updates
    def update_table(new_data):
        if table_ref.current:
            table_ref.current.rows = [/* updated rows */]
            table_ref.current.update()

    state_manager.subscribe("data_key", update_table)

    # Complete responsive UI with all elements
    return ft.Column([
        # Header with status
        ft.Row([
            ft.Text("View Title", size=28, weight=ft.FontWeight.BOLD),
            ft.ProgressRing(ref=loading_ref, visible=False, width=20, height=20),
            ft.Text("Ready", ref=status_ref, size=12)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

        # Responsive content
        ft.ResponsiveRow([
            ft.Column([data_table], col={"sm": 12, "md": 8}),
            ft.Column([
                ft.FilledButton("Primary Action", on_click=on_action),
                ft.OutlinedButton("Secondary Action")
            ], col={"sm": 12, "md": 4})
        ]),
    ], expand=True, scroll=ft.ScrollMode.AUTO, spacing=20)
```

### Enhanced State Manager with Server Operations
```python
async def server_mediated_update(self, key: str, value: Any, server_operation: str = None, *args, **kwargs):
    if not server_operation or not self.server_bridge:
        await self.update_async(key, value, source="direct")
        return {'success': True, 'mode': 'direct'}

    server_method = getattr(self.server_bridge, server_operation, None)
    if not server_method:
        await self.update_async(key, value, source="server_fallback")
        return {'success': False, 'error': f'method {server_operation} not found'}

    try:
        result = await server_method(*args, **kwargs) if asyncio.iscoroutinefunction(server_method) else server_method(*args, **kwargs)
        if not isinstance(result, dict):
            result = {'success': bool(result), 'data': result}
        if result.get('success'):
            await self.update_async(key, result.get('data', value))
        return result
    except Exception as e:
        await self.update_async(key, value, source="server_error")
        return {'success': False, 'error': str(e)}
```

## Essential Configuration
```python
import Shared.utils.utf8_solution  # ALWAYS for subprocess/console I/O
from utils.server_bridge import create_server_bridge
from utils.state_manager import create_state_manager
from utils.user_feedback import show_success_message, show_error_message
```

## Launch Commands & Code Quality
```bash
# Development: cd FletV2 && flet run -r main.py
# Production: cd FletV2 && python main.py
```

**Code Quality Checklist:**
- [ ] Flet built-in solution used? [ ] File <500 lines? [ ] `control.update()` vs `page.update()`?
- [ ] Async patterns for long operations? [ ] Error handling with user feedback? [ ] UTF-8 import for subprocess?