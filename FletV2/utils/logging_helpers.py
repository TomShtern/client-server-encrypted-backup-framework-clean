#!/usr/bin/env python3
"""
Centralized Logging Utilities for FletV2
Standardized logging patterns with context and performance tracking.
"""

import time
import functools
from typing import Any, Optional, Callable
from utils.debug_setup import get_logger

# Get the base logger
logger = get_logger(__name__)


def log_error(
    error: Exception, 
    context: str, 
    additional_info: Optional[str] = None,
    include_traceback: bool = True
) -> None:
    """
    Centralized error logging with consistent format and context.
    
    Args:
        error: The exception that occurred
        context: Context where the error happened (function name, operation, etc.)
        additional_info: Additional context information
        include_traceback: Whether to include full traceback
        
    Example:
        try:
            risky_operation()
        except Exception as e:
            log_error(e, "risky_operation", "Processing client data")
    """
    error_msg = f"Error in {context}: {str(error)}"
    
    if additional_info:
        error_msg += f" | Additional info: {additional_info}"
    
    if include_traceback:
        logger.error(error_msg, exc_info=True)
    else:
        logger.error(error_msg)


def log_operation(
    operation_name: str,
    details: Optional[str] = None,
    level: str = "info"
) -> None:
    """
    Log an operation with consistent formatting.
    
    Args:
        operation_name: Name of the operation
        details: Optional additional details
        level: Log level (debug, info, warning, error)
        
    Example:
        log_operation("file_download", "Downloaded client_data.csv", "info")
    """
    message = f"Operation: {operation_name}"
    if details:
        message += f" | {details}"
    
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)


def log_performance(func: Callable) -> Callable:
    """
    Decorator to log function execution time for performance monitoring.
    
    Args:
        func: Function to monitor
        
    Returns:
        Decorated function with performance logging
        
    Example:
        @log_performance
        def expensive_operation():
            # Complex operation
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        function_name = func.__name__
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > 1.0:  # Log slow operations (>1 second)
                logger.warning(f"Slow operation: {function_name} took {execution_time:.2f}s")
            elif execution_time > 0.1:  # Log moderate operations (>100ms)
                logger.info(f"Performance: {function_name} took {execution_time:.3f}s")
            else:
                logger.debug(f"Performance: {function_name} took {execution_time:.3f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            log_error(e, function_name, f"Failed after {execution_time:.3f}s")
            raise
    
    return wrapper


def log_user_action(
    action: str, 
    user_context: Optional[str] = None,
    success: bool = True,
    details: Optional[str] = None
) -> None:
    """
    Log user actions for audit and debugging purposes.
    
    Args:
        action: The action performed by the user
        user_context: Context about the user or session
        success: Whether the action was successful
        details: Additional details about the action
        
    Example:
        log_user_action("file_download", "main_view", True, "client_data.csv")
    """
    status = "SUCCESS" if success else "FAILED"
    message = f"User Action [{status}]: {action}"
    
    if user_context:
        message += f" | Context: {user_context}"
    
    if details:
        message += f" | Details: {details}"
    
    if success:
        logger.info(message)
    else:
        logger.warning(message)


def log_state_change(
    state_key: str,
    old_value: Any,
    new_value: Any,
    context: Optional[str] = None
) -> None:
    """
    Log state changes for debugging state management.
    
    Args:
        state_key: The key that changed
        old_value: Previous value
        new_value: New value
        context: Context where the change occurred
        
    Example:
        log_state_change("selected_client", None, "client_123", "dashboard_view")
    """
    message = f"State Change: {state_key} | {old_value} → {new_value}"
    
    if context:
        message += f" | Context: {context}"
    
    logger.debug(message)


class OperationLogger:
    """
    Context manager for logging operations with automatic timing and error handling.
    
    Example:
        with OperationLogger("database_query", "Fetching client list"):
            clients = fetch_clients()
    """
    
    def __init__(self, operation_name: str, description: Optional[str] = None):
        self.operation_name = operation_name
        self.description = description
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        message = f"Starting operation: {self.operation_name}"
        if self.description:
            message += f" | {self.description}"
        logger.debug(message)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        
        if exc_type is None:
            # Operation succeeded
            message = f"Completed operation: {self.operation_name} ({execution_time:.3f}s)"
            if self.description:
                message += f" | {self.description}"
            logger.debug(message)
        else:
            # Operation failed
            log_error(exc_val, self.operation_name, f"Failed after {execution_time:.3f}s")
        
        return False  # Don't suppress exceptions