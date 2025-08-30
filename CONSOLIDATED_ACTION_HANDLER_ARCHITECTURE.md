# Consolidated Action Handler Architecture

## Overview

This document describes the consolidated action handler architecture implemented in the CyberBackup Framework's Flet GUI. The consolidation eliminated over 650 lines of duplicate boilerplate code while standardizing patterns across all action handlers.

## Architecture Components

### Core Classes

#### 1. BaseActionHandler
**Location**: `flet_server_gui/components/base_action_handler.py`

The foundational base class that all action handlers inherit from. Provides standardized patterns for:
- Action execution with busy indicators
- Error handling and toast notifications  
- Confirmation dialog integration
- Data change callback management
- Correlation ID generation for traceability

**Key Methods**:
```python
async def execute_action(self, action_func, *args, **kwargs) -> ActionResult
```

#### 2. ActionExecutor  
**Location**: `flet_server_gui/utils/action_executor.py`

Enhanced unified async wrapper that handles:
- Busy indicator management
- Confirmation dialogs with customizable messages
- Toast notifications for all result types
- Data change callback triggers
- Correlation ID tracking

**Key Methods**:
```python
async def run_with_confirmation(self, action_func, *args, **kwargs) -> ActionResult
async def run(self, action_func, *args, **kwargs) -> ActionResult
```

#### 3. ActionResult
**Location**: `flet_server_gui/utils/action_result.py`

Unified result object for all action operations with factory methods:
```python
# Factory methods for clean API usage
ActionResult.success(message, data=None)
ActionResult.error(message, error=None)
ActionResult.info(message, data=None)
ActionResult.warn(message, data=None)
ActionResult.cancelled(message)
ActionResult.partial(message, data=None)
```

### Business Logic Classes

#### 4. DatabaseActions
**Location**: `flet_server_gui/actions/database_actions.py`

Pure business logic for database operations (250+ lines):
- `backup_database()` - Create database backups with timestamping
- `optimize_database()` - Run VACUUM and REINDEX operations
- `analyze_database()` - Gather table statistics  
- `execute_sql_query()` - Safe SQL execution with validation

#### 5. LogActions
**Location**: `flet_server_gui/actions/log_actions.py`

Pure business logic for log management (300+ lines):
- `export_logs()` - Export filtered logs to CSV/JSON
- `clear_logs()` - Clear logs with backup options
- `filter_logs()` - Apply level/date/content filters
- `search_logs()` - Full-text search with regex support
- `refresh_logs()` - Reload log data from sources

#### 6. ClientActions  
**Location**: `flet_server_gui/actions/client_actions.py`

Pure business logic for client management:
- `view_client_details()` - Retrieve client connection info
- `disconnect_client()` - Safely disconnect clients
- `get_client_statistics()` - Generate connection statistics

### UI Integration Layer

#### 7. Handler Classes
All inherit from `BaseActionHandler` and focus purely on UI integration:

**ClientActionHandlers** (`client_action_handlers.py`):
- UI event handling for client management
- Confirmation dialog integration  
- Data binding and display updates

**DatabaseActionHandlers** (`database_action_handlers.py`):
- Database UI controls and feedback
- Progress indicators for long operations
- Result display and error reporting

**LogActionHandlers** (`log_action_handlers.py`):
- Log viewer UI management
- Filter and search interface integration
- Export dialog and file picker integration

## Architecture Benefits

### Code Reduction
- **Total Reduction**: 650+ lines of duplicate boilerplate eliminated
- **Client Handlers**: 200+ lines removed
- **Database Handlers**: 300+ lines removed  
- **Log Handlers**: 150+ lines removed

### Standardization
- Consistent error handling patterns across all handlers
- Unified confirmation dialog behavior
- Standardized toast notification timing and styling
- Common data change callback mechanisms

### Maintainability
- Single source of truth for common action patterns
- Reduced cognitive load for developers
- Clear separation between UI and business logic
- Easier testing with mocked dependencies

### Extensibility
- Simple inheritance model for new action handlers
- Standardized factory methods for ActionResult creation
- Pluggable confirmation dialog system
- Flexible data change callback registration

## Usage Patterns

### Creating New Action Handlers

1. **Inherit from BaseActionHandler**:
```python
from flet_server_gui.components.base_action_handler import BaseActionHandler

class NewActionHandlers(BaseActionHandler):
    def __init__(self, page):
        super().__init__(page)
        # Handler-specific initialization
```

2. **Use execute_action() for all operations**:
```python
async def handle_action(self):
    return await self.execute_action(
        self.business_logic.some_operation,
        param1="value",
        confirmation_message="Are you sure?"
    )
```

3. **Create corresponding business logic class**:
```python
# In actions/new_actions.py
class NewActions:
    async def some_operation(self, param1: str) -> ActionResult:
        try:
            # Business logic here
            return ActionResult.success("Operation completed")
        except Exception as e:
            return ActionResult.error(f"Operation failed: {e}")
```

### Using ActionResult Factory Methods

```python
# Success with data
return ActionResult.success("Backup completed", {"backup_file": filepath})

# Error with exception details  
return ActionResult.error("Database connection failed", error=exc)

# Warning for partial results
return ActionResult.warn("Some files skipped during export")

# Information messages
return ActionResult.info("Cache refreshed from server")

# User cancellation
return ActionResult.cancelled("Operation cancelled by user")

# Partial success
return ActionResult.partial("Export completed with warnings", {"exported": 100})
```

### Confirmation Dialogs

The `execute_action()` method automatically handles confirmation dialogs:

```python
# Simple confirmation
await self.execute_action(
    dangerous_operation,
    confirmation_message="This will delete all data. Continue?"
)

# Custom confirmation with details
await self.execute_action(
    batch_operation,
    confirmation_message="Process 150 files?",
    confirmation_details="This may take several minutes"
)
```

### Data Change Callbacks

Handlers automatically trigger data change callbacks:

```python
# Register callback in component initialization
self.action_executor.register_data_change_callback(
    "database_changed", 
    self.refresh_database_view
)

# Callbacks are automatically triggered after successful actions
# No manual callback invocation needed
```

## Testing Strategy

### Integration Testing
- **File**: `test_consolidation_integration.py`
- **Coverage**: All imports, inheritance, method signatures, module exports
- **Results**: 50 test cases, all passing

### End-to-End Testing  
- **File**: `test_e2e_action_execution.py`
- **Coverage**: Complete execution pipeline with mocked dependencies
- **Results**: 13 test scenarios, all passing

### Test Command
```powershell
# Activate virtual environment
& .\.venv\Scripts\Activate.ps1

# Run integration tests
python test_consolidation_integration.py

# Run end-to-end tests  
python test_e2e_action_execution.py
```

## Migration Guide

### For Existing Handlers

1. **Update inheritance**:
```python
# Before
class SomeHandlers:
    def __init__(self, page):
        self.page = page
        self.action_executor = ActionExecutor(page)

# After  
class SomeHandlers(BaseActionHandler):
    def __init__(self, page):
        super().__init__(page)
```

2. **Replace action patterns**:
```python
# Before - Manual error handling
async def some_action(self):
    try:
        self.action_executor.show_busy_indicator()
        result = await business_logic()
        if result.success:
            self.action_executor.show_toast("Success!")
        else:
            self.action_executor.show_toast("Error!", error=True)
    finally:
        self.action_executor.hide_busy_indicator()

# After - Standardized execution
async def some_action(self):
    return await self.execute_action(business_logic)
```

3. **Extract business logic**:
   - Move all non-UI logic to separate action classes
   - Keep UI event handling in handler classes
   - Use ActionResult factory methods for clean APIs

### For New Features

1. Create business logic class in `actions/` directory
2. Create handler class inheriting from `BaseActionHandler`  
3. Use `execute_action()` for all operations
4. Register data change callbacks as needed
5. Add tests for both business logic and UI integration

## Best Practices

### Business Logic Classes
- Keep pure functions without UI dependencies
- Return ActionResult objects with appropriate factory methods
- Handle all expected exceptions and error conditions
- Use type hints for better IDE support

### Handler Classes
- Focus only on UI event handling and data binding
- Use `execute_action()` for all business operations
- Avoid duplicating error handling logic
- Register appropriate data change callbacks

### ActionResult Usage
- Use factory methods instead of constructor
- Include helpful error messages for debugging
- Attach relevant data for success results
- Use appropriate result types (success, error, warn, etc.)

### Testing
- Mock business logic classes for handler tests
- Test business logic independently of UI
- Use integration tests to verify complete flows
- Validate all error conditions and edge cases

## Performance Considerations

### Async Operations
- All actions run asynchronously to prevent UI blocking
- Busy indicators provide user feedback during operations
- Data change callbacks update UI after completion

### Memory Management
- ActionResult objects are lightweight and short-lived
- Business logic classes are stateless where possible
- Handler classes maintain minimal state

### Error Recovery
- Graceful degradation for non-critical failures
- Detailed error logging with correlation IDs
- User-friendly error messages in toast notifications

## Future Enhancements

### Planned Improvements
- Enhanced confirmation dialog templates
- Progress tracking for long-running operations
- Undo/redo capability for reversible actions
- Action history and audit logging

### Extension Points
- Custom ActionResult types for specific domains
- Pluggable confirmation dialog providers
- Advanced data change notification patterns
- Action composition and workflow support

## Conclusion

The consolidated action handler architecture provides a robust, maintainable foundation for the CyberBackup Framework's GUI. By eliminating duplicate code and standardizing patterns, it reduces development time and improves code quality while maintaining full backward compatibility.

For questions or issues with this architecture, refer to the test files or examine existing handler implementations for usage examples.
