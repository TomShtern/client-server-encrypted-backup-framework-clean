# Centralized Error Boundary System

## Overview

The Centralized Error Boundary System provides comprehensive error handling for the CyberBackup Framework's Flet GUI application. It catches unhandled exceptions in UI callbacks and presents them through professional, user-friendly error dialogs while maintaining detailed technical information for debugging.

## Key Features

### 🛡️ **Error Protection**
- Catches unhandled exceptions in UI callbacks
- Prevents application crashes from uncaught errors
- Graceful degradation when errors occur
- Multiple usage patterns (decorators, context managers, automatic)

### 🎨 **Professional UI**
- User-friendly error messages (non-technical language)
- Material Design 3 styled error dialogs
- Collapsible technical details section
- Copy-to-clipboard functionality
- Theme-aware styling

### 🔍 **Developer Experience**
- Detailed stack traces with local variables
- Correlation IDs for error tracking
- Integration with existing logging systems
- Custom error reporting callbacks
- Comprehensive error context information

### 🏗️ **Architecture Integration**
- Seamless integration with existing ActionExecutor
- Automatic protection for BaseActionHandler
- Global error boundary singleton
- Custom error handler registration

## Components

### 1. ErrorContext (`utils/error_context.py`)

Captures comprehensive error information for both users and developers:

```python
from flet_server_gui.utils.error_context import create_error_context

try:
    risky_operation()
except Exception as e:
    context = create_error_context(
        exception=e,
        operation="File Processing",
        component="FileManager",
        user_message="Failed to process the selected file"
    )
```

**Features:**
- Automatic user-friendly message generation
- Stack trace capture with local variables
- Error severity classification (critical, error, warning)
- Correlation ID generation
- Clipboard-friendly formatting

### 2. ErrorDialog (`components/error_dialog.py`)

Professional error dialog with Material Design 3 styling:

```python
from flet_server_gui.components.error_dialog import show_error_dialog

show_error_dialog(page, error_context, on_report=handle_error_report)
```

**Features:**
- Collapsible technical details
- Copy to clipboard functionality
- Custom error reporting integration
- Theme-aware styling
- Progressive disclosure design

### 3. ErrorBoundary (`components/error_boundary.py`)

Central error boundary for catching and handling exceptions:

```python
from flet_server_gui.components.error_boundary import ErrorBoundary

# Initialize error boundary
boundary = ErrorBoundary(page)

# Usage patterns:
# 1. Decorator
@boundary.safe_callback
def on_button_click(e):
    risky_operation()

# 2. Context manager
async with boundary.protect("Data Loading"):
    await load_data()

# 3. Wrapper
safe_callback = boundary.wrap_callback(callback, "File Operation")
```

## Usage Patterns

### Global Error Boundary (Recommended)

Initialize once at application startup:

```python
from flet_server_gui.components.error_boundary import GlobalErrorBoundary

def main(page: ft.Page):
    # Initialize global error boundary
    error_boundary = GlobalErrorBoundary.initialize(page)
    
    # Optional: Set up error reporting
    error_boundary.set_error_report_callback(send_error_report)
    
    # Create your app
    create_app(page)

# Use global decorators
from flet_server_gui.components.error_boundary import safe_callback

@safe_callback
async def on_button_click(e):
    await process_data()
```

### BaseActionHandler Integration (Automatic)

Error boundary is automatically integrated with BaseActionHandler:

```python
class MyActionHandler(BaseActionHandler):
    def __init__(self, server_bridge, dialog_system, toast_manager, page):
        super().__init__(server_bridge, dialog_system, toast_manager, page)
        # Error boundary is automatically set up
    
    def create_ui(self):
        # Create safe button callbacks
        button = ft.ElevatedButton(
            text="Process Data",
            on_click=self.create_safe_callback(self.process_data, "Data Processing")
        )
        return button
    
    @self.safe_callback("Data Processing")
    async def process_data(self, e):
        # This method is automatically protected
        await self.business_logic.process_data()
```

### Manual Error Handling

For specific error handling needs:

```python
from flet_server_gui.utils.error_context import create_error_context
from flet_server_gui.components.error_dialog import show_error_dialog

async def risky_operation(page):
    try:
        await complex_async_operation()
    except Exception as e:
        error_context = create_error_context(
            exception=e,
            operation="Complex Operation",
            user_message="The operation could not be completed"
        )
        show_error_dialog(page, error_context)
```

### Simple Error Dialogs

For quick error notifications:

```python
from flet_server_gui.components.error_dialog import show_simple_error

show_simple_error(
    page,
    "Could not save the file",
    "Save Error",
    "File path: /path/to/file.txt"
)
```

## Configuration

### Error Boundary Settings

```python
boundary = ErrorBoundary(page)

# Configure behavior
boundary.auto_show_dialog = True      # Show error dialogs automatically
boundary.capture_locals = False      # Capture local variables (use for debugging)
boundary.log_errors = True           # Log errors to trace center

# Add custom error handlers
def custom_handler(error_context):
    # Custom error processing
    if error_context.severity == "critical":
        send_alert_to_admin(error_context)
    return False  # Continue with default handling

boundary.add_error_handler(custom_handler)
```

### Error Reporting Integration

```python
def error_report_callback(error_context):
    """Send error reports to external service."""
    report = {
        "error_type": error_context.error_type,
        "message": error_context.error_message,
        "operation": error_context.operation,
        "correlation_id": error_context.correlation_id,
        "timestamp": error_context.timestamp,
        "stack_trace": error_context.stack_trace
    }
    send_to_error_service(report)

boundary.set_error_report_callback(error_report_callback)
```

## Error Types and User Messages

The system automatically generates user-friendly messages for common error types:

| Exception Type | User-Friendly Message |
|---|---|
| `FileNotFoundError` | "The requested file could not be found." |
| `PermissionError` | "Permission denied. Please check file permissions." |
| `ConnectionError` | "Unable to connect to the server. Please check your connection." |
| `TimeoutError` | "The operation timed out. Please try again." |
| `ValueError` | "Invalid input provided. Please check your data." |
| `RuntimeError` | "An unexpected error occurred during processing." |

### Error Severity Classification

| Severity | Exception Types | Behavior |
|---|---|---|
| `critical` | `MemoryError`, `SystemExit`, `SystemError` | High-priority reporting |
| `warning` | `UserWarning`, `DeprecationWarning` | Lower priority |
| `error` | Most other exceptions | Standard error handling |

## Integration with Existing Systems

### ActionExecutor Integration

The ErrorBoundary integrates seamlessly with the existing ActionExecutor:

```python
# ActionExecutor automatically uses error boundary if available
class ActionExecutor:
    def set_error_boundary(self, error_boundary):
        self._error_boundary = error_boundary
    
    async def run(self, action_name, action_coro, **kwargs):
        try:
            # Execute action
            result = await action_coro()
        except Exception as e:
            # Enhanced error handling with error boundary
            if self._error_boundary:
                error_context = create_error_context(e, operation=action_name)
                await self._error_boundary._handle_exception(e, ...)
```

### BaseActionHandler Integration

All action handlers automatically get error boundary protection:

```python
class BaseActionHandler:
    def __init__(self, server_bridge, dialog_system, toast_manager, page):
        # ... existing initialization ...
        
        # Set up error boundary
        self.error_boundary = ErrorBoundary(page)
        self.action_executor.set_error_boundary(self.error_boundary)
        
        # Configure for action handlers
        self.error_boundary.auto_show_dialog = False  # Actions use ActionResult
        self.error_boundary.log_errors = True
```

## Testing

### Running Tests

```powershell
# Basic functionality tests
python test_error_boundary_simple.py

# Interactive demo (requires Flet)
python error_boundary_demo.py
```

### Test Coverage

- **ErrorContext**: Exception capture, message generation, severity classification
- **ErrorFormatter**: User/developer message formatting
- **ErrorDialog**: UI functionality, copy to clipboard
- **ErrorBoundary**: Decorator patterns, context managers, integration
- **BaseActionHandler**: Automatic integration, safe callbacks

## Examples

### Complete Example Application

```python
import flet as ft
from flet_server_gui.components.error_boundary import GlobalErrorBoundary
from flet_server_gui.components.base_action_handler import BaseActionHandler

class MyActionHandler(BaseActionHandler):
    def __init__(self, server_bridge, dialog_system, toast_manager, page):
        super().__init__(server_bridge, dialog_system, toast_manager, page)
    
    def create_ui(self):
        return ft.Column([
            ft.ElevatedButton(
                text="Safe Operation",
                on_click=self.create_safe_callback(self.safe_operation, "Safe Operation")
            ),
            ft.ElevatedButton(
                text="Risky Operation", 
                on_click=self.create_safe_callback(self.risky_operation, "Risky Operation")
            )
        ])
    
    async def safe_operation(self, e):
        # This will complete successfully
        self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Operation completed!")))
    
    async def risky_operation(self, e):
        # This will trigger the error boundary
        raise ValueError("Something went wrong in the risky operation")

def main(page: ft.Page):
    page.title = "Error Boundary Example"
    
    # Initialize global error boundary
    error_boundary = GlobalErrorBoundary.initialize(page)
    
    # Create action handler
    handler = MyActionHandler(None, None, None, page)
    
    # Add UI
    page.add(handler.create_ui())

ft.app(target=main)
```

## Best Practices

### 1. Use Global Error Boundary
Initialize the global error boundary at application startup for consistent error handling across all components.

### 2. Protect UI Callbacks
Always protect UI callbacks (button clicks, menu selections) with error boundaries to prevent application crashes.

### 3. Provide Context
Include operation names and component information when creating error contexts for better debugging.

### 4. Configure Appropriately
- Set `auto_show_dialog=False` for action handlers (they use ActionResult)
- Set `capture_locals=True` only during debugging (privacy/performance)
- Always enable `log_errors=True` for production

### 5. Custom Error Messages
Provide user-friendly error messages for domain-specific operations:

```python
try:
    backup_database()
except Exception as e:
    context = create_error_context(
        e,
        operation="Database Backup",
        user_message="Failed to create database backup. Please check disk space and permissions."
    )
```

### 6. Error Reporting
Set up error reporting callbacks to track errors in production:

```python
def report_error(error_context):
    if error_context.severity in ["critical", "error"]:
        send_to_monitoring_service(error_context.to_dict())

boundary.set_error_report_callback(report_error)
```

## Migration Guide

### From Manual Error Handling

**Before:**
```python
async def on_button_click(e):
    try:
        await risky_operation()
        page.show_snack_bar(ft.SnackBar(content=ft.Text("Success!")))
    except Exception as ex:
        page.show_snack_bar(ft.SnackBar(
            content=ft.Text(f"Error: {str(ex)}"),
            bgcolor=ft.colors.ERROR
        ))
```

**After:**
```python
@safe_callback
async def on_button_click(e):
    await risky_operation()
    page.show_snack_bar(ft.SnackBar(content=ft.Text("Success!")))
```

### From ActionExecutor Only

**Before:**
```python
result = await self.action_executor.run(
    action_name="backup_database",
    action_coro=lambda: backup_database(),
)
```

**After:**
```python
# No changes needed - ActionExecutor automatically integrates with error boundary
result = await self.action_executor.run(
    action_name="backup_database", 
    action_coro=lambda: backup_database(),
)
# Now includes enhanced error context and reporting
```

## Performance Considerations

- **Low Overhead**: Error boundary adds minimal performance overhead
- **Memory Efficient**: Error contexts are lightweight and short-lived
- **Async Safe**: All error handling is async-compatible
- **Local Variables**: Only capture when explicitly enabled (debugging)

## Security Considerations

- **Sanitized Output**: Local variables are sanitized before display
- **Correlation IDs**: Enable error tracking without exposing sensitive data
- **User Messages**: Technical details hidden by default
- **Copy Protection**: Users can copy technical details but not sensitive data

## Troubleshooting

### Common Issues

1. **Error Boundary Not Working**
   - Ensure GlobalErrorBoundary.initialize() is called
   - Check that callbacks are wrapped with @safe_callback or create_safe_callback()

2. **No Error Dialogs Showing**
   - Check auto_show_dialog setting
   - Verify dialog system is properly initialized

3. **Missing Error Context**
   - Ensure error_context import is available
   - Check that create_error_context is called with valid exception

4. **Integration Issues**
   - Verify BaseActionHandler inheritance
   - Check that error_boundary is set on ActionExecutor

## Future Enhancements

### Planned Features
- Enhanced error analytics and reporting
- Error replay and debugging tools
- Custom error dialog templates
- Integration with external monitoring services
- Automated error recovery mechanisms

## Conclusion

The Centralized Error Boundary System provides a robust, professional error handling solution for the CyberBackup Framework. It significantly improves both user experience (through friendly error messages) and developer experience (through detailed error context and debugging information).

By implementing consistent error handling patterns across the entire application, it reduces development time, improves code quality, and enhances application reliability.

For questions or issues with the error boundary system, refer to the test files and demo application for usage examples.
