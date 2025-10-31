# FletV2 Architecture Documentation

## Overview

This document provides a comprehensive technical overview of the FletV2 desktop GUI component, focusing on architecture patterns, system design, and implementation details for developers and AI coding agents.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FletV2 Desktop GUI                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │   Views     │  │ Components  │  │   Utils     │  │  Theme   │ │
│  │             │  │             │  │             │  │          │ │
│  │ Dashboard   │  │ Filter      │  │ Server      │  │ Unified  │ │
│  │ Clients     │  │ Controls    │  │ Bridge      │  │ Theme    │ │
│  │ Database    │  │ Search      │  │ UI          │  │ System   │ │
│  │ Files       │  │ Components  │  │ Components  │  │          │ │
│  │ Logs        │  │             │  │ Async       │  │          │ │
│  │ Settings    │  │             │  │ Helpers     │  │          │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                     ServerBridge Pattern                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              BackupServer Integration                       │ │
│  │                                                             │ │
│  │  • Direct Python method calls (no network overhead)        │ │
│  │  • Structured responses: {success, data, error}            │ │
│  │  • Async/await patterns for UI responsiveness              │ │
│  │  • Error handling with user feedback                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                    Network Protocol Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              C++ Client Communication                       │ │
│  │                                                             │ │
│  │  • Binary protocol with Boost.Asio                          │ │
│  │  • RSA-1024 key exchange + AES-256-CBC encryption          │ │
│  │  • CRC32 verification for data integrity                    │ │
│  │  • Port 1256 network listener                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Core Design Patterns

### 1. View-Based Architecture

Each major feature is implemented as an independent view following a consistent pattern:

```python
def create_feature_view(
    server_bridge: Any,
    page: ft.Page,
    state_manager: Any,
    navigate_callback: Callable[[str], None] | None = None
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    """
    Standard view creation pattern.

    Returns:
        (view_control, dispose_function, setup_function)
    """

    # 1. Initialize local state
    local_state = {}
    disposed = False

    # 2. Build UI components
    content = build_view_content()

    # 3. Setup async data loading
    async def setup():
        """Initialize data and bind events after UI attachment."""
        await load_initial_data()
        setup_event_handlers()

    # 4. Cleanup resources
    def dispose():
        """Dispose view and cleanup resources."""
        nonlocal disposed
        disposed = True
        cleanup_background_tasks()
        unbind_event_handlers()

    return content, dispose, setup
```

**Benefits:**
- Separation of concerns between UI, data, and logic
- Consistent lifecycle management
- Easy testing and mocking
- Modular architecture enables feature additions

### 2. ServerBridge Communication Pattern

Direct communication with the backup server without network overhead:

```python
class ServerBridge:
    """Clean API surface for server communication."""

    def __init__(self, real_server=None):
        self.real_server = real_server

    def get_dashboard_summary(self) -> dict:
        """Get dashboard summary data.

        Returns:
            {'success': bool, 'data': Any, 'error': str}
        """
        if not self.real_server:
            return {'success': False, 'data': None, 'error': 'Server not connected'}

        try:
            data = self.real_server.get_dashboard_summary()
            return {'success': True, 'data': data, 'error': None}
        except Exception as e:
            return {'success': False, 'data': None, 'error': str(e)}

# Usage in views
async def fetch_dashboard_data(server_bridge):
    result = await _call_bridge(server_bridge, "get_dashboard_summary")
    if result.get("success"):
        return result.get("data")
    else:
        raise Exception(result.get("error"))
```

**Benefits:**
- Eliminates network overhead for direct integration
- Consistent error handling
- Easy mocking for testing
- Clean separation of concerns

### 3. Async Operation Pattern

Non-blocking UI operations using thread pool execution:

```python
from FletV2.utils.async_helpers import run_sync_in_executor

async def perform_server_operation(server_bridge, operation_name, *args):
    """Perform server operation without blocking UI thread."""

    # Wrap synchronous server call
    def operation():
        method = getattr(server_bridge, operation_name)
        return method(*args)

    try:
        # Execute in thread pool
        result = await run_sync_in_executor(operation)

        # Handle structured response
        if isinstance(result, dict):
            if result.get("success"):
                return result.get("data")
            else:
                raise Exception(result.get("error"))
        else:
            return result

    except Exception as e:
        # User-friendly error handling
        show_error_message(page, f"Operation failed: {e}")
        raise
```

**Benefits:**
- UI remains responsive during long operations
- Consistent error handling
- Progress indicators during operations
- Thread-safe server communication

### 4. Unified Theme System Pattern

Single source of truth for styling with Material Design 3:

```python
# Theme setup with Windows integration
def setup_sophisticated_theme(page: ft.Page, theme_mode: str = "system"):
    """Setup enhanced theme with Windows 11 integration."""

    # Windows 11 theme detection
    windows_theme_provider = setup_windows_11_integration(page)

    # Display scaling for 4K monitors
    display_scaler = setup_display_scaling(page)

    # Base Flet theme
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True,
        text_theme=ft.TextTheme(
            headline_large=ft.TextStyle(size=32, weight=ft.FontWeight.W_700),
            body_large=ft.TextStyle(size=16, weight=ft.FontWeight.W_400),
        ),
    )

    # Store references for later use
    setattr(page, "_windows_theme_provider", windows_theme_provider)
    setattr(page, "_display_scaler", display_scaler)

# Enhanced components with gradients and animations
def create_enhanced_card(content: ft.Control, gradient_background: str = "surface"):
    """Create card with gradient backgrounds and hover effects."""
    gradient = create_gradient(gradient_background)

    return ft.Container(
        content=content,
        bgcolor=ft.Colors.SURFACE,
        border_radius=16,
        gradient=gradient,
        shadow=ft.BoxShadow(
            blur_radius=6,
            color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
        ),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )
```

**Benefits:**
- Consistent visual design across the application
- Framework harmony with Flet 0.28.3
- Enhanced visual quality beyond vanilla Material Design 3
- Easy theme customization and extension

## Component Architecture

### View Components

#### Dashboard View (`views/dashboard.py`)
- **Purpose**: System overview, metrics, and real-time monitoring
- **Features**: Live metrics, activity feed, server status
- **Data Sources**: ServerBridge dashboard methods
- **Key Methods**:
  - `create_dashboard_view()`: Main view creation
  - `_fetch_snapshot()`: Data collection and transformation
  - `_build_metric_block()`: UI component building

#### Clients View (`views/clients.py`)
- **Purpose**: Client management and monitoring
- **Features**: Client list, connection status, management operations
- **Data Sources**: ServerBridge client methods
- **Key Methods**:
  - `create_clients_view()`: Main view creation
  - `load_clients_data()`: Data fetching and caching
  - `handle_client_action()`: CRUD operations

#### Database View (`views/database_pro.py`)
- **Purpose**: Database management with full CRUD operations
- **Features**: Table browser, data editing, export functionality
- **Data Sources**: ServerBridge database methods
- **Key Methods**:
  - `create_database_view()`: Main view creation
  - `load_table_data()`: Data pagination and filtering
  - `perform_crud_operation()`: Database operations

### Utility Components

#### ServerBridge (`utils/server_bridge.py`)
```python
class ServerBridge:
    """Communication layer between GUI and backup server."""

    # Dashboard methods
    def get_dashboard_summary(self) -> dict
    def get_performance_metrics(self) -> dict
    def get_server_statistics(self) -> dict

    # Client management
    def get_clients(self) -> dict
    def get_client_details(self, client_id: str) -> dict
    def disconnect_client(self, client_id: str) -> dict

    # Database operations
    def get_table_names(self) -> dict
    def get_table_data(self, table_name: str, limit: int = 100) -> dict
    def add_table_record(self, table_name: str, record: dict) -> dict
    def update_table_record(self, table_name: str, record: dict) -> dict
    def delete_table_record(self, table_name: str, record_id: Any) -> dict

    # File management
    def get_files_list(self, path: str = "") -> dict
    def get_file_details(self, file_id: str) -> dict
    def delete_file(self, file_id: str) -> dict
```

#### UI Components (`utils/ui_components.py`)
```python
# Core UI building blocks
def create_action_button(text: str, on_click, icon=None, primary=True) -> ft.ElevatedButton
def create_search_bar(on_change, placeholder="Search...") -> ft.TextField
def create_filter_dropdown(label: str, options: list, on_change) -> ft.Dropdown
def create_status_pill(status: str, variant: str = "filled") -> ft.Container

# Enhanced components
def create_pulsing_status_indicator(status: str, text: str) -> ft.Container
def AppCard(content: ft.Control, elevation: int = 2) -> ft.Container
def create_loading_indicator(text: str = "Loading...") -> ft.Container
```

#### Async Helpers (`utils/async_helpers.py`)
```python
async def run_sync_in_executor(func: Callable, *args) -> Any:
    """Execute synchronous function in thread pool."""

async def create_async_fetch_function(method_name: str, empty_default=None):
    """Create async fetch function for server methods."""

async def safe_server_call(bridge, method_name: str, *args) -> dict:
    """Safely call server method with error handling."""
```

### Reusable Components

#### Filter Controls (`components/filter_controls.py`)
```python
def create_advanced_filter_panel(
    filters: dict,
    on_filter_change: Callable[[dict], None]
) -> ft.Container:
    """Create advanced filtering panel."""

def create_quick_filter_buttons(
    filter_options: list,
    on_selection_change: Callable[[str], None]
) -> ft.Row:
    """Create quick filter buttons."""
```

#### Global Search (`components/global_search.py`)
```python
class GlobalSearchManager:
    """Manage global search across all views."""

    def __init__(self, server_bridge):
        self.server_bridge = server_bridge
        self.search_history = []

    async def perform_search(self, query: str, scope: str = "all") -> dict:
        """Perform global search across all data sources."""

    def add_to_history(self, query: str):
        """Add search query to history."""
```

## Data Flow Architecture

### 1. Data Loading Flow

```
View Creation → Setup Function → Async Data Fetch → UI Update
     ↓               ↓                ↓              ↓
build_view() → setup() → _call_bridge() → update_display()
```

```python
# Example: Dashboard data loading
async def setup():
    """Load dashboard data after UI attachment."""
    try:
        # Fetch data from server
        snapshot = await _fetch_snapshot(server_bridge)

        # Update UI with data
        _apply_snapshot_to_ui(snapshot)

        # Start periodic refresh
        _start_periodic_update()

    except Exception as e:
        show_error_message(page, f"Failed to load dashboard: {e}")
```

### 2. User Action Flow

```
User Interaction → Event Handler → Async Operation → Server Call → UI Update
      ↓                ↓              ↓              ↓           ↓
  click_button → on_click → perform_action() → server_call() → refresh_ui()
```

```python
# Example: Client disconnection
async def disconnect_client(client_id: str):
    """Handle client disconnection."""
    try:
        # Show loading state
        update_client_status(client_id, "disconnecting")

        # Perform server operation
        result = await _call_bridge(server_bridge, "disconnect_client", client_id)

        if result.get("success"):
            # Update UI
            remove_client_from_list(client_id)
            show_success_message("Client disconnected successfully")
        else:
            # Handle error
            show_error_message(result.get("error"))

    except Exception as e:
        show_error_message(f"Failed to disconnect client: {e}")
```

### 3. Real-time Update Flow

```
Server Event → Bridge Method → GUI Notification → UI Update
     ↓             ↓              ↓              ↓
  event occurs → notify_gui() → on_update() → refresh_view()
```

```python
# Real-time updates using periodic polling
async def start_periodic_updates():
    """Start periodic data refresh."""
    while not disposed:
        try:
            # Fetch latest data
            current_data = await _fetch_snapshot(server_bridge)

            # Check for changes
            if has_data_changed(current_data, previous_data):
                # Update UI
                _apply_snapshot_to_ui(current_data)
                previous_data = current_data

        except Exception as e:
            logger.error(f"Update failed: {e}")

        # Wait before next update
        await asyncio.sleep(UPDATE_INTERVAL)
```

## State Management

### Application State

```python
class FletV2App:
    def __init__(self, page: ft.Page, server_bridge=None):
        self.page = page
        self.server_bridge = server_bridge
        self.current_view = None
        self.view_state = {}
        self.navigation_history = []

    def navigate_to(self, view_name: str):
        """Navigate to specified view."""
        # Save current state
        if self.current_view:
            self.view_state[self.current_view] = self._capture_view_state()

        # Load new view
        view_control, dispose, setup = self._create_view(view_name)
        self._display_view(view_control)

        # Setup new view
        self.page.run_task(setup)

        # Update navigation
        self.current_view = view_name
        self.navigation_history.append(view_name)
```

### View State Management

```python
def capture_view_state():
    """Capture current view state for restoration."""
    return {
        'scroll_position': get_scroll_position(),
        'filter_settings': get_current_filters(),
        'selected_items': get_selected_items(),
        'search_query': get_search_query(),
        'view_mode': get_view_mode()
    }

def restore_view_state(state: dict):
    """Restore view state from captured data."""
    set_scroll_position(state.get('scroll_position', 0))
    set_filters(state.get('filter_settings', {}))
    set_selected_items(state.get('selected_items', []))
    set_search_query(state.get('search_query', ''))
    set_view_mode(state.get('view_mode', 'table'))
```

## Error Handling Strategy

### Structured Error Responses

All server communication returns structured responses:

```python
def server_method() -> dict:
    """Standard server method pattern."""
    try:
        # Perform operation
        result = perform_operation()

        # Return success response
        return {
            'success': True,
            'data': result,
            'error': None
        }

    except SpecificError as e:
        # Handle known errors
        return {
            'success': False,
            'data': None,
            'error': f"Operation failed: {str(e)}"
        }

    except Exception as e:
        # Handle unexpected errors
        logger.exception("Unexpected error in server method")
        return {
            'success': False,
            'data': None,
            'error': "An unexpected error occurred"
        }
```

### User-Friendly Error Display

```python
def show_error_message(page: ft.Page, message: str, duration: int = 5):
    """Display user-friendly error message."""
    snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.Colors.ERROR_CONTAINER,
        action="Dismiss",
        duration=duration * 1000
    )
    page.snack_bar = snack_bar
    snack_bar.open = True
    page.update()

def show_success_message(page: ft.Page, message: str, duration: int = 3):
    """Display success message."""
    snack_bar = ft.SnackBar(
        content=ft.Text(message),
        bgcolor=ft.Colors.SUCCESS_CONTAINER,
        action="OK",
        duration=duration * 1000
    )
    page.snack_bar = snack_bar
    snack_bar.open = True
    page.update()
```

## Performance Optimization

### 1. Async Operation Patterns

```python
# Non-blocking server calls
async def fetch_data_nonblocking():
    """Fetch data without blocking UI."""
    def blocking_operation():
        return server_bridge.get_data()

    return await run_sync_in_executor(blocking_operation)

# Batch operations
async def batch_update(items: list):
    """Perform batch updates efficiently."""
    def batch_operation():
        results = []
        for item in items:
            result = server_bridge.update_item(item)
            results.append(result)
        return results

    return await run_sync_in_executor(batch_operation)
```

### 2. UI Optimization

```python
# Efficient list updates
def update_list_efficiently(new_data: list, existing_list: ft.Column):
    """Update list with minimal UI rebuild."""
    # Calculate differences
    changes = calculate_list_diff(existing_list.controls, new_data)

    # Apply minimal changes
    for change in changes:
        if change.type == 'add':
            existing_list.controls.append(change.item)
        elif change.type == 'remove':
            existing_list.controls.remove(change.item)
        elif change.type == 'update':
            existing_list.controls[change.index] = change.new_item
```

### 3. Memory Management

```python
# Proper cleanup
def dispose_view():
    """Dispose view and cleanup resources."""
    # Cancel background tasks
    for task in background_tasks:
        if not task.done():
            task.cancel()

    # Clear references
    server_bridge = None
    page = None

    # Clear UI references
    for control in ui_controls:
        control.parent = None

# Resource pooling
class ConnectionPool:
    """Manage database connections efficiently."""

    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connections = queue.Queue(maxsize=max_connections)
        self._initialize_pool()

    def get_connection(self):
        """Get connection from pool."""
        return self.connections.get(timeout=30)

    def return_connection(self, conn):
        """Return connection to pool."""
        self.connections.put(conn)
```

## Security Considerations

### 1. Input Validation

```python
def validate_user_input(input_text: str) -> str:
    """Validate and sanitize user input."""
    # Remove potentially harmful content
    sanitized = html.escape(input_text.strip())

    # Validate length
    if len(sanitized) > MAX_INPUT_LENGTH:
        raise ValueError("Input too long")

    # Validate characters
    if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', sanitized):
        raise ValueError("Invalid characters in input")

    return sanitized

# Usage in input handlers
def on_text_change(e):
    """Handle text input with validation."""
    try:
        validated_text = validate_user_input(e.control.value)
        process_input(validated_text)
    except ValueError as ve:
        show_error_message(page, f"Invalid input: {ve}")
```

### 2. Secure Communication

```python
# ServerBridge with authentication
class SecureServerBridge(ServerBridge):
    """ServerBridge with security features."""

    def __init__(self, real_server, auth_token):
        super().__init__(real_server)
        self.auth_token = auth_token

    def _authenticated_call(self, method_name: str, *args):
        """Make authenticated call to server."""
        # Add authentication headers
        headers = {'Authorization': f'Bearer {self.auth_token}'}

        # Make secure call
        return self.real_server.make_secure_call(method_name, args, headers)
```

## Testing Strategy

### 1. Unit Testing

```python
# Test view creation
def test_dashboard_view_creation():
    """Test dashboard view creation returns correct types."""
    page = ft.Page()
    server_bridge = Mock()

    view, dispose, setup = create_dashboard_view(server_bridge, page, None)

    assert isinstance(view, ft.Control)
    assert callable(dispose)
    assert callable(setup)

# Test server bridge
def test_server_bridge_error_handling():
    """Test server bridge error handling."""
    server_bridge = ServerBridge(real_server=None)

    result = server_bridge.get_dashboard_summary()

    assert result['success'] is False
    assert result['error'] == 'Server not connected'
```

### 2. Integration Testing

```python
# Test complete user workflows
async def test_client_management_workflow():
    """Test complete client management workflow."""
    page = ft.Page()
    mock_server = Mock()
    server_bridge = ServerBridge(mock_server)

    # Create view
    view, dispose, setup = create_clients_view(server_bridge, page, None)

    # Setup view
    await setup()

    # Perform actions
    await add_test_client()
    await edit_client()
    await delete_client()

    # Verify results
    assert mock_server.add_client.called
    assert mock_server.update_client.called
    assert mock_server.delete_client.called
```

### 3. Performance Testing

```python
# Test UI responsiveness
async def test_ui_responsiveness():
    """Test UI remains responsive during heavy operations."""
    start_time = time.time()

    # Simulate heavy operation
    await perform_heavy_operation()

    end_time = time.time()
    operation_time = end_time - start_time

    # UI should remain responsive (update within 100ms)
    assert operation_time < 0.1

    # Verify UI still updates
    assert ui_controls_are_responsive()
```

## Deployment Architecture

### 1. Development Environment

```bash
# Local development setup
cd FletV2
python -m venv ../flet_venv
../flet_venv/Scripts/activate
pip install -r requirements.txt

# Run in development mode
export FLET_DEBUG=1
python main.py
```

### 2. Production Deployment

```bash
# Build standalone executable
flet build windows --project-name "CyberBackup GUI"

# Or create distribution package
python setup.py sdist bdist_wheel
```

### 3. Configuration Management

```python
# Configuration loader
class ConfigManager:
    """Manage application configuration."""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()

    def get(self, key: str, default=None):
        """Get configuration value."""
        return self.config.get(key, default)
```

## Future Enhancements

### 1. Plugin Architecture

```python
# Plugin system for extensibility
class PluginManager:
    """Manage plugins for FletV2."""

    def __init__(self):
        self.plugins = {}

    def register_plugin(self, name: str, plugin_class):
        """Register a plugin."""
        self.plugins[name] = plugin_class

    def load_plugin(self, name: str):
        """Load and initialize plugin."""
        if name in self.plugins:
            return self.plugins[name]()
        raise PluginNotFoundError(f"Plugin {name} not found")
```

### 2. Advanced Theming

```python
# Theme customization system
class ThemeCustomizer:
    """Allow runtime theme customization."""

    def __init__(self, base_theme):
        self.base_theme = base_theme
        self.customizations = {}

    def add_color_override(self, color_name: str, color_value: str):
        """Add custom color override."""
        self.customizations[color_name] = color_value

    def create_custom_theme(self) -> ft.Theme:
        """Create theme with customizations."""
        custom_theme = copy.deepcopy(self.base_theme)

        for color_name, color_value in self.customizations.items():
            setattr(custom_theme.color_scheme, color_name, color_value)

        return custom_theme
```

### 3. Real-time Collaboration

```python
# Multi-user collaboration features
class CollaborationManager:
    """Manage real-time collaboration features."""

    def __init__(self, server_bridge):
        self.server_bridge = server_bridge
        self.active_users = {}
        self.collaboration_channel = None

    async def join_collaboration_session(self, session_id: str):
        """Join a collaboration session."""
        # Connect to real-time channel
        self.collaboration_channel = await self.server_bridge.join_session(session_id)

        # Listen for updates
        self.collaboration_channel.on('user_update', self._handle_user_update)
        self.collaboration_channel.on('data_update', self._handle_data_update)
```

## Conclusion

The FletV2 architecture provides a robust, scalable, and maintainable foundation for the CyberBackup desktop GUI. Key architectural decisions include:

- **View-based modularity** for separation of concerns
- **ServerBridge pattern** for clean server communication
- **Async-first design** for responsive user experience
- **Unified theming** for consistent visual design
- **Comprehensive error handling** for reliability
- **Performance optimization** for efficient operation

This architecture enables rapid development, easy testing, and straightforward maintenance while providing a rich, responsive user experience.