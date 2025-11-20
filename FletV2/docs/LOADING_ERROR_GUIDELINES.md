# Standardized Loading and Error Pattern Guidelines

This document outlines the proper usage of loading and error patterns across all FletV2 views to ensure consistency and maintainability.

## Loading States

### Core Loading Components
The `utils/loading_states.py` module provides the following standardized loading components:

1. `create_loading_indicator(message="Loading...")` - Creates a standard loading indicator UI
2. `create_error_display(error_message)` - Creates a standard error display UI
3. `create_empty_state(title, message, icon=ft.icons.INBOX_OUTLINED)` - Creates a standard empty state UI

### Usage Pattern for Async Operations

```python
async def fetch_data_async(bridge, loading_control=None, error_control=None):
    """Example pattern for async operations with loading states."""
    # Show loading state
    if loading_control:
        loading_control.visible = True
        loading_control.update()  # Use control.update instead of page.update
    
    try:
        # Perform the async operation using run_sync_in_executor for sync bridge methods
        result = await run_sync_in_executor(bridge.get_some_data)
        
        if result.get('success'):
            # Handle success - update UI with data
            return result['data']
        else:
            # Handle error case - show error message
            if error_control:
                error_control.content = create_error_display(result.get('error', 'Unknown error'))
                error_control.visible = True
                error_control.update()
            return None
            
    except Exception as e:
        # Handle exception case - show error message
        if error_control:
            error_control.content = create_error_display(f"Exception: {str(e)}")
            error_control.visible = True
            error_control.update()
        return None
        
    finally:
        # Always hide loading indicator
        if loading_control:
            loading_control.visible = False
            loading_control.update()
```

### Loading State Best Practices

1. **Use Control Updates**: Always use `control.update()` instead of `page.update()` for better performance
2. **Proper Error Handling**: Wrap in try/catch blocks to handle both sync and async errors
3. **Hide Loading States**: Always ensure loading indicators are hidden in finally blocks
4. **Consistent Messages**: Use consistent loading messages across all views

## Error Handling Patterns

### Snackbar Notifications

The `utils/loading_states.py` module provides standardized snackbar notifications:

1. `show_snackbar(page, message, bgcolor=None)` - Show standard snackbar
2. `show_error_snackbar(page, error_message)` - Show error snackbar with red theme
3. `show_success_snackbar(page, message)` - Show success snackbar with green theme

### Error Display Components

For inline error display, use:

- `create_error_display(error_message)` for major errors on the page
- `show_error_snackbar(page, message)` for minor errors that don't need to disrupt the UI flow

## Integration with Experimental Views

### Enhanced Logs View
- Use `create_loading_indicator` for initial data loading
- Use `create_error_display` if data fetching fails
- Use `show_error_snackbar` for export failures
- Use `show_success_snackbar` for successful operations

### Database Pro View
- Use `create_loading_indicator` when switching tables or fetching data
- Use `create_error_display` if database connection fails
- Use `show_error_snackbar` for individual record operation failures
- Use `show_success_snackbar` for successful record operations

### Dashboard View
- Use `create_loading_indicator` in specific containers rather than `page.update()`
- Use `create_error_display` if server connection fails
- Use `show_error_snackbar` for minor notification errors
- Use `show_success_snackbar` for successful operations

## Implementation Checklist

For each view, verify:
- [ ] Loading indicators use `create_loading_indicator()` from utils
- [ ] Error displays use `create_error_display()` from utils
- [ ] Empty states use `create_empty_state()` from utils
- [ ] Success notifications use `show_success_snackbar()` from utils
- [ ] Error notifications use `show_error_snackbar()` from utils
- [ ] Loading states are hidden with `control.update()` not `page.update()`
- [ ] All async operations are wrapped with try/catch blocks
- [ ] Loading indicators are always hidden in finally blocks

## Performance Considerations

1. Use `control.update()` instead of `page.update()` for better performance
2. Only update the specific controls that change, not the entire page
3. Use refs to target specific controls when possible
4. Avoid unnecessary updates in loops or frequently called functions