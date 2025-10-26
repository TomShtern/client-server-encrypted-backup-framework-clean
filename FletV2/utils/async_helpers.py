#!/usr/bin/env python3
"""
Async/sync coordination utilities - SIMPLIFIED (Phase 1 cleanup).

This module contains only the proven patterns actually used by views.
Removed 8 unused functions that were designed theoretically but never adopted.

Kept functions:
- run_sync_in_executor: Used in 100% of views for server bridge calls
- safe_server_call: Used in 100% of views for structured error handling
- debounce: Used in settings.py for autosave
- create_async_fetch_function: NEW - extracted from working view patterns
"""

from __future__ import annotations

import asyncio
import contextlib
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import Any, TypeVar

from FletV2.utils.debug_setup import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


async def run_sync_in_executor(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Execute a synchronous callable without blocking the Flet event loop.

    This is the CRITICAL function that prevents UI freezes. All synchronous
    server_bridge methods MUST be called through this function from async code.

    Args:
        func: Synchronous function to execute
        *args, **kwargs: Arguments to pass to the function

    Returns:
        Result of the function call

    Example:
        # CORRECT - prevents freeze
        result = await run_sync_in_executor(safe_server_call, bridge, 'get_clients')

        # WRONG - causes permanent freeze
        result = await bridge.get_clients()  # If bridge.get_clients is sync
    """
    loop = asyncio.get_running_loop()

    try:
        if kwargs:
            def _wrapper() -> T:
                return func(*args, **kwargs)
            return await loop.run_in_executor(None, _wrapper)

        return await loop.run_in_executor(None, func, *args)

    except RuntimeError as exc:
        message = str(exc)
        if "cannot schedule new futures after shutdown" in message or "Event loop is closed" in message:
            raise asyncio.CancelledError(message) from exc
        raise


def safe_server_call(server_bridge, method_name: str, *args, **kwargs) -> dict:
    """
    Safe server bridge method call with standardized error handling.

    This is the UNIVERSAL PATTERN for calling server_bridge methods.
    Returns structured format used across all views.

    Args:
        server_bridge: Server bridge instance (can be None)
        method_name: Name of the method to call
        *args, **kwargs: Arguments to pass to the method

    Returns:
        Dict with standardized format: {'success': bool, 'data': Any, 'error': str}

    Example:
        # Always returns structured format
        result = safe_server_call(bridge, 'get_clients')
        if result.get('success'):
            clients = result.get('data', [])
        else:
            error = result.get('error', 'Unknown error')
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


def debounce(wait: float):
    """
    Debounce decorator for async functions.

    Delays execution until after 'wait' seconds have elapsed since the last invocation.
    Used for expensive operations that shouldn't execute on every keystroke.

    Args:
        wait: Time in seconds to wait before executing (e.g., 0.5 for 500ms)

    Returns:
        Decorated function that will be debounced

    Example:
        @debounce(1.5)
        async def autosave_settings():
            await persist_to_disk()

        # Function will only execute 1.5s after the last call
        await autosave_settings()  # Cancelled
        await autosave_settings()  # Cancelled
        await autosave_settings()  # Executes after 1.5s
    """
    def decorator(func: Callable[..., Awaitable[Any]]):
        # Store the pending task for cancellation
        pending_task: asyncio.Task | None = None

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal pending_task

            # Cancel any pending execution
            if pending_task and not pending_task.done():
                pending_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await pending_task

            # Schedule new execution after delay
            async def delayed_execution():
                await asyncio.sleep(wait)
                return await func(*args, **kwargs)

            pending_task = asyncio.create_task(delayed_execution())
            return await pending_task

        return wrapper
    return decorator


def create_async_fetch_function(
    method_name: str,
    normalizer: Callable[[Any], Any] | None = None,
    empty_default: Any = None
) -> Callable[[Any], Awaitable[Any]]:
    """
    Create an async fetch function following the proven pattern from working views.

    This is the EXACT pattern extracted from clients.py, files.py, analytics.py, etc.
    Consolidates the duplicated async fetch logic into a reusable factory.

    Args:
        method_name: Name of the server_bridge method to call (e.g., 'get_clients')
        normalizer: Optional function to transform/normalize the data
        empty_default: Value to return if fetch fails or bridge is None (default: None)

    Returns:
        Async function that fetches data from server_bridge

    Example:
        # Create fetch function (replaces 15 lines of duplicated code)
        fetch_clients = create_async_fetch_function('get_clients', empty_default=[])

        # Use it
        clients = await fetch_clients(server_bridge)

        # With normalization
        def normalize_analytics(data):
            return AnalyticsData(**data) if data else AnalyticsData()

        fetch_analytics = create_async_fetch_function(
            'get_analytics_data',
            normalizer=normalize_analytics,
            empty_default=AnalyticsData()
        )
        analytics = await fetch_analytics(server_bridge)
    """
    async def fetch_async(bridge: Any) -> Any:
        if not bridge:
            logger.debug(f"{method_name}: No server bridge available")
            return empty_default if empty_default is not None else None

        result = await run_sync_in_executor(safe_server_call, bridge, method_name)

        if not result.get('success'):
            error = result.get('error', 'Unknown error')
            logger.debug(f"{method_name} fetch failed: {error}")
            return empty_default if empty_default is not None else None

        data = result.get('data')

        if normalizer:
            try:
                return normalizer(data)
            except Exception as e:
                logger.error(f"{method_name} normalization failed: {e}")
                return empty_default if empty_default is not None else None

        return data

    return fetch_async
