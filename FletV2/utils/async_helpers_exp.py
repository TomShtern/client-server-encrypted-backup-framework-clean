"""
Async Helpers for FletV2 - Universal patterns for async/sync integration.

This module provides universal patterns for:
- Async/sync integration using run_in_executor
- Fetch operations with loading states
- Debounced async functions
"""

import asyncio
from typing import Any, Callable, Awaitable
import flet as ft


async def run_sync_in_executor(func, *args, **kwargs):
    """
    Run synchronous function in thread pool executor.
    
    Args:
        func: Synchronous function to execute
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Result of the function execution
    """
    loop = asyncio.get_running_loop()
    if kwargs:
        # If kwargs are provided, create a wrapper function
        def wrapper():
            return func(*args, **kwargs)
        return await loop.run_in_executor(None, wrapper)
    else:
        # If no kwargs, call directly
        return await loop.run_in_executor(None, func, *args)


async def fetch_with_loading(
    bridge_method,
    *args,
    loading_control=None,
    error_control=None,
    on_success=None,
    on_error=None
):
    """
    Universal async fetch pattern with loading states and error handling.
    
    Args:
        bridge_method: The server bridge method to call
        *args: Arguments to pass to the bridge method
        loading_control: Control to show/hide loading state
        error_control: Control to display error messages
        on_success: Callback function to call on success with the result data
        on_error: Callback function to call on error with the error message
        
    Returns:
        Result data on success, None on failure
    """
    if loading_control:
        loading_control.visible = True
        loading_control.update()

    try:
        result = await run_sync_in_executor(bridge_method, *args)

        if result.get('success'):
            if on_success:
                on_success(result['data'])
            return result['data']
        else:
            error_msg = result.get('error', 'Unknown error')
            if error_control:
                error_control.value = error_msg
                error_control.visible = True
            if on_error:
                on_error(error_msg)
            return None

    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        if error_control:
            error_control.value = error_msg
            error_control.visible = True
        if on_error:
            on_error(error_msg)
        return None

    finally:
        if loading_control:
            loading_control.visible = False
            if hasattr(loading_control, 'update'):
                loading_control.update()


def debounce(wait_seconds=0.5):
    """
    Decorator for debouncing async functions.
    
    Args:
        wait_seconds: Number of seconds to wait before executing the function
        
    Returns:
        Decorated function that is debounced
    """
    def decorator(func: Callable[..., Awaitable[Any]]):
        timer = None

        async def debounced(*args, **kwargs):
            nonlocal timer

            if timer:
                timer.cancel()

            async def run():
                await asyncio.sleep(wait_seconds)
                await func(*args, **kwargs)

            timer = asyncio.create_task(run())
            try:
                await timer
            except asyncio.CancelledError:
                pass  # Task was cancelled by another call

        return debounced
    return decorator