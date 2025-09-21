#!/usr/bin/env python3
"""
Async Error Handling Helpers for FletV2
Consolidates repeated error handling patterns found across view files.

USAGE EXAMPLES:

Before (repeated pattern in views):
    if server_bridge:
        try:
            result = server_bridge.delete_client(client_id)
            if result.get('success'):
                show_success_message(page, f"Client {client.get('name')} deleted")
                load_clients_data()
            else:
                show_error_message(page, f"Failed to delete: {result.get('error', 'Unknown error')}")
        except Exception as ex:
            show_error_message(page, f"Error: {ex}")

After (using async_helpers):
    result = safe_server_call(server_bridge, 'delete_client', client_id)
    if handle_server_result(page, result, f"Client {client.get('name')} deleted", "Delete failed"):
        load_clients_data()

Or with context manager:
    with SafeOperation(page, "Delete failed") as op:
        result = safe_server_call(server_bridge, 'delete_client', client_id)
        if safe_get(result, 'success'):
            op.mark_success(f"Client {client.get('name')} deleted")
            load_clients_data()

Data loading pattern:
    # Before
    if server_bridge:
        try:
            result = server_bridge.get_clients()
            if result.get('success'):
                clients_data = result.get('data', [])
            else:
                clients_data = get_mock_clients()
        except Exception:
            clients_data = get_mock_clients()
    else:
        clients_data = get_mock_clients()

    # After
    clients_data = safe_load_data(server_bridge, 'get_clients', get_mock_clients())
"""

import flet as ft
from typing import Callable, Any, Optional, Awaitable
from functools import wraps
from utils.debug_setup import get_logger
from utils.user_feedback import show_success_message, show_error_message

logger = get_logger(__name__)


def async_event_handler(
    success_message: Optional[str] = None,
    error_message: str = "Operation failed",
    log_context: Optional[str] = None
):
    """
    Decorator for async event handlers that provides standardized error handling and user feedback.
    
    Args:
        success_message: Message to show on success (optional)
        error_message: Base error message prefix
        log_context: Context for logging (defaults to function name)
    
    Returns:
        Decorated async function with error handling
        
    Example:
        @async_event_handler("File downloaded successfully", "Download failed")
        async def on_download_file(e: ft.ControlEvent) -> None:
            await download_operation()
    """
    def decorator(func: Callable[[Any], Awaitable[Any]]):
        @wraps(func)
        async def wrapper(e: ft.ControlEvent) -> Any:
            page = getattr(e, 'page', None) or getattr(e.control, 'page', None)
            context = log_context or func.__name__
            
            try:
                result = await func(e)
                
                if success_message and page:
                    show_success_message(page, success_message)
                
                logger.debug(f"Event handler '{context}' completed successfully")
                return result
                
            except Exception as ex:
                error_detail = f"{error_message}: {str(ex)}"
                logger.error(f"Event handler '{context}' failed: {ex}", exc_info=True)
                
                if page:
                    show_error_message(page, error_detail)
                
                return None
        
        return wrapper
    return decorator


async def safe_async_operation(
    operation: Callable[[], Awaitable[Any]], 
    page: ft.Page,
    success_message: Optional[str] = None,
    error_message: str = "Operation failed",
    context: Optional[str] = None
) -> Optional[Any]:
    """
    Execute an async operation with standardized error handling and user feedback.
    
    Args:
        operation: Async function to execute
        page: Flet page for user feedback
        success_message: Message to show on success (optional)
        error_message: Base error message prefix
        context: Context for logging
    
    Returns:
        Result of operation or None if failed
        
    Example:
        result = await safe_async_operation(
            lambda: fetch_data(),
            page,
            "Data loaded successfully",
            "Failed to load data",
            "fetch_operation"
        )
    """
    try:
        result = await operation()
        
        if success_message:
            show_success_message(page, success_message)
        
        if context:
            logger.debug(f"Safe async operation '{context}' completed successfully")
            
        return result
        
    except Exception as ex:
        error_detail = f"{error_message}: {str(ex)}"
        log_context = context or "async_operation"
        
        logger.error(f"Safe async operation '{log_context}' failed: {ex}", exc_info=True)
        show_error_message(page, error_detail)

        return None


def safe_server_call(server_bridge, method_name: str, *args, **kwargs) -> dict:
    """
    Safe server bridge method call with standardized error handling.
    Consolidates the repeated pattern found across view files.

    Args:
        server_bridge: Server bridge instance (can be None)
        method_name: Name of the method to call
        *args, **kwargs: Arguments to pass to the method

    Returns:
        Dict with standardized format: {'success': bool, 'data': Any, 'error': str}
    """
    if not server_bridge:
        return {'success': False, 'error': 'No server bridge available', 'data': None}

    try:
        method = getattr(server_bridge, method_name, None)
        if not method:
            return {'success': False, 'error': f'Method {method_name} not found', 'data': None}

        result = method(*args, **kwargs)

        # Normalize result to standard format
        if isinstance(result, dict):
            return result
        else:
            return {'success': bool(result), 'data': result, 'error': None}

    except Exception as e:
        logger.debug(f"Server call {method_name} failed: {e}")
        return {'success': False, 'error': str(e), 'data': None}


def safe_get(data: dict, key: str, default: Any = None) -> Any:
    """
    Safe dictionary access with logging for debugging.
    Replaces repeated result.get('success'), result.get('error') patterns.

    Args:
        data: Dictionary to access
        key: Key to retrieve
        default: Default value if key not found

    Returns:
        Value from dictionary or default
    """
    if not isinstance(data, dict):
        logger.debug(f"Expected dict, got {type(data)} when accessing key '{key}'")
        return default

    return data.get(key, default)


def handle_server_result(page: ft.Page, result: dict, success_msg: str,
                        error_prefix: str = "Operation failed") -> bool:
    """
    Handle server operation result with user feedback.
    Consolidates the repeated success/error checking pattern.

    Args:
        page: Flet page for user feedback
        result: Server operation result dict
        success_msg: Message to show on success
        error_prefix: Prefix for error messages

    Returns:
        bool: True if operation was successful
    """
    if safe_get(result, 'success', False):
        show_success_message(page, success_msg)
        return True
    else:
        error = safe_get(result, 'error', 'Unknown error')
        show_error_message(page, f"{error_prefix}: {error}")
        return False


def safe_load_data(server_bridge, method_name: str, fallback_data: Any, *args, **kwargs) -> Any:
    """
    Safe data loading with automatic fallback to mock data.
    Consolidates the repeated pattern of server call with fallback.

    Args:
        server_bridge: Server bridge instance
        method_name: Method name to call
        fallback_data: Fallback data if server call fails
        *args, **kwargs: Arguments for server method

    Returns:
        Data from server or fallback
    """
    if server_bridge:
        try:
            result = safe_server_call(server_bridge, method_name, *args, **kwargs)
            if safe_get(result, 'success', False):
                return safe_get(result, 'data', fallback_data)
            else:
                return fallback_data
        except Exception:
            return fallback_data
    else:
        return fallback_data


def validate_required_field(field_value: str, field_name: str, page: ft.Page) -> bool:
    """
    Validate required form field with user feedback.
    Consolidates repeated validation pattern.

    Args:
        field_value: Value to validate
        field_name: Name of field for error message
        page: Flet page for user feedback

    Returns:
        bool: True if field is valid
    """
    if not field_value or not field_value.strip():
        show_error_message(page, f"{field_name} is required")
        return False
    return True


class SafeOperation:
    """
    Context manager for safe operations with user feedback.
    Simplifies try/catch blocks with automatic error handling.

    Example:
        with SafeOperation(page, "Delete failed") as op:
            result = server_bridge.delete_client(client_id)
            if result.get('success'):
                op.mark_success("Client deleted successfully")
    """

    def __init__(self, page: ft.Page, error_prefix: str = "Operation failed"):
        self.page = page
        self.error_prefix = error_prefix
        self.success = False

    def __enter__(self) -> 'SafeOperation':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            error_msg = f"{self.error_prefix}: {str(exc_val)}"
            show_error_message(self.page, error_msg)
            logger.debug(f"SafeOperation failed: {exc_val}")
        return True  # Suppress exception

    def mark_success(self, message: str) -> None:
        """Mark operation as successful with message."""
        self.success = True
        show_success_message(self.page, message)