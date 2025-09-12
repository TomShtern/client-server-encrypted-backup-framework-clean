#!/usr/bin/env python3
"""
Enhanced Logging Utilities for FletV2
Provides more detailed and informative logging for debugging purposes.
"""

import logging
import functools
import inspect
from typing import Any, Callable, Optional
from utils.debug_setup import get_logger

# Get the base logger
base_logger = get_logger(__name__)


def log_method_call(func: Callable) -> Callable:
    """
    Decorator to automatically log method calls with parameters.
    
    Args:
        func: Function to decorate
        
    Returns:
        Wrapped function with logging
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Get class name if this is a method
            if args and hasattr(args[0], '__class__'):
                class_name = args[0].__class__.__name__
                method_name = f"{class_name}.{func.__name__}"
            else:
                method_name = func.__name__
            
            # Log method entry with parameters (but don't log sensitive data)
            params = []
            for i, arg in enumerate(args[1:], 1):  # Skip self
                if i <= 3:  # Only log first few args to avoid clutter
                    param_str = str(arg)[:50] + "..." if len(str(arg)) > 50 else str(arg)
                    params.append(f"arg{i}={param_str}")
            
            for key, value in list(kwargs.items())[:3]:  # Only log first few kwargs
                if not any(sensitive in key.lower() for sensitive in ['password', 'secret', 'key', 'token']):
                    value_str = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                    params.append(f"{key}={value_str}")
            
            param_str = ", ".join(params) if params else "no parameters"
            base_logger.info(f"Calling {method_name}({param_str})")
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Log successful completion
            result_str = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            base_logger.info(f"Completed {method_name} -> {result_str}")
            
            return result
        except Exception as e:
            # Log the exception with full context
            if args and hasattr(args[0], '__class__'):
                class_name = args[0].__class__.__name__
                method_name = f"{class_name}.{func.__name__}"
            else:
                method_name = func.__name__
            
            base_logger.error(f"Exception in {method_name}: {str(e)}", exc_info=True)
            raise
    
    return wrapper


def log_async_operation(operation_name: str, details: str = ""):
    """
    Log the start of an async operation with contextual details.
    
    Args:
        operation_name: Name of the operation
        details: Additional contextual details
    """
    message = f"Starting async operation: {operation_name}"
    if details:
        message += f" ({details})"
    base_logger.info(message)


def log_async_completion(operation_name: str, result: Any = None, duration: Optional[float] = None):
    """
    Log the completion of an async operation.
    
    Args:
        operation_name: Name of the operation
        result: Result of the operation (if applicable)
        duration: Duration of the operation in seconds (if measured)
    """
    message = f"Completed async operation: {operation_name}"
    if duration is not None:
        message += f" in {duration:.2f}s"
    if result is not None:
        result_str = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
        message += f" -> {result_str}"
    base_logger.info(message)


def log_user_action(action: str, user: str = "Unknown", details: str = ""):
    """
    Log user actions for audit trail.
    
    Args:
        action: Description of the user action
        user: User identifier (if available)
        details: Additional details about the action
    """
    message = f"User action: {action} by {user}"
    if details:
        message += f" ({details})"
    base_logger.info(message)


def log_data_change(change_type: str, item_type: str, item_id: str, details: str = ""):
    """
    Log data changes for tracking modifications.
    
    Args:
        change_type: Type of change (CREATE, UPDATE, DELETE, READ)
        item_type: Type of item being changed
        item_id: Identifier of the item
        details: Additional details about the change
    """
    message = f"Data {change_type}: {item_type}[{item_id}]"
    if details:
        message += f" ({details})"
    base_logger.info(message)


def log_performance_metric(metric_name: str, value: Any, unit: str = "", context: str = ""):
    """
    Log performance metrics for monitoring.
    
    Args:
        metric_name: Name of the metric
        value: Value of the metric
        unit: Unit of measurement
        context: Contextual information
    """
    message = f"Performance metric: {metric_name} = {value}{unit}"
    if context:
        message += f" [{context}]"
    base_logger.info(message)


def log_error_with_context(error: Exception, context: str = "", stack_level: int = 1):
    """
    Log errors with additional contextual information.
    
    Args:
        error: Exception that occurred
        context: Additional context about where the error happened
        stack_level: How many levels up the stack to report (for helper functions)
    """
    # Get caller information
    frame = inspect.currentframe()
    for _ in range(stack_level):
        frame = frame.f_back
    caller_info = f"{frame.f_code.co_filename}:{frame.f_lineno}"
    
    message = f"Error in {caller_info}: {str(error)}"
    if context:
        message += f" [Context: {context}]"
    base_logger.error(message, exc_info=True)


def log_network_request(method: str, url: str, status_code: Optional[int] = None, duration: Optional[float] = None):
    """
    Log network requests for monitoring connectivity.
    
    Args:
        method: HTTP method
        url: Request URL
        status_code: Response status code (if available)
        duration: Request duration in seconds (if measured)
    """
    message = f"Network request: {method} {url}"
    if status_code is not None:
        message += f" -> {status_code}"
    if duration is not None:
        message += f" ({duration:.2f}s)"
    base_logger.info(message)


def log_resource_usage(resource_type: str, usage: Any, limit: Any = None, context: str = ""):
    """
    Log resource usage for monitoring system health.
    
    Args:
        resource_type: Type of resource (MEMORY, CPU, DISK, etc.)
        usage: Current usage value
        limit: Usage limit (if applicable)
        context: Contextual information
    """
    message = f"Resource usage: {resource_type} = {usage}"
    if limit is not None:
        message += f" / {limit}"
        if isinstance(usage, (int, float)) and isinstance(limit, (int, float)) and limit > 0:
            percentage = (usage / limit) * 100
            message += f" ({percentage:.1f}%)"
    if context:
        message += f" [{context}]"
    base_logger.info(message)