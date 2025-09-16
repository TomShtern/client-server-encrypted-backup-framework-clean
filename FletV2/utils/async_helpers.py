#!/usr/bin/env python3
"""
Async Event Handler Utilities for FletV2
Provides reusable patterns for async event handling with built-in error management.
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
        async def on_download_file(e):
            await download_operation()
    """
    def decorator(func: Callable[[Any], Awaitable[Any]]):
        @wraps(func)
        async def wrapper(e):
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