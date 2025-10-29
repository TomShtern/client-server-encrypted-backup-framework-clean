#!/usr/bin/env python3
"""Compatibility async helper utilities for legacy experimental tests.

This module re-introduces the public surface that older `_exp` test suites
expect while delegating to the production-ready helpers that ship with the
modern GUI implementation.  The goal is to keep historical tests passing
without maintaining a forked implementation of the async patterns.
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Awaitable, Callable

# Project requirement – must be first import for reliable UTF-8 I/O on Windows.
import Shared.utils.utf8_solution as _  # noqa: F401

from FletV2.utils.async_helpers import (
    run_sync_in_executor as _base_run_sync_in_executor,
    safe_server_call,
)
from FletV2.utils.debug_setup import get_logger

logger = get_logger(__name__)


def _toggle_visibility(control: Any | None, visible: bool) -> None:
    if not control:
        return
    try:
        setattr(control, "visible", visible)
        if getattr(control, "page", None) and hasattr(control, "update"):
            control.update()
    except Exception:  # pragma: no cover - UI best-effort
        logger.debug("fetch_with_loading: failed to update control visibility", exc_info=True)


async def _execute_operation(
    operation: Callable[..., Any] | Awaitable[Any],
    operation_args: tuple[Any, ...],
    operation_kwargs: dict[str, Any],
) -> Any:
    if inspect.isawaitable(operation):
        return await operation  # type: ignore[return-value]
    if inspect.iscoroutinefunction(operation):
        return await operation(*operation_args, **operation_kwargs)
    return await _base_run_sync_in_executor(operation, *operation_args, **operation_kwargs)


def _normalise_result(raw_result: Any) -> tuple[bool, Any, Any]:
    if isinstance(raw_result, dict) and "success" in raw_result:
        success = bool(raw_result.get("success"))
        return success, raw_result.get("data"), raw_result.get("error")
    return True, raw_result, None


async def fetch_with_loading(
    operation: Callable[..., Any] | Awaitable[Any],
    *operation_args: Any,
    loading_control: Any | None = None,
    error_control: Any | None = None,
    on_success: Callable[[Any], None] | None = None,
    on_error: Callable[[Any], None] | None = None,
    **operation_kwargs: Any,
) -> Any:
    """Execute a potentially blocking operation while managing loading/error UI.

    This helper mirrors the behaviour of the historical experimental module:
    - `loading_control.visible` is toggled before/after execution
    - `error_control.visible` is cleared on success and re-enabled on failure
    - results shaped like ``{"success": bool, "data": Any, "error": str}``
      are normalised; other return types are passed through untouched
    - optional callbacks receive the normalised payload or error message

    Args:
        operation: Callable or awaiting object to execute
        *operation_args, **operation_kwargs: Parameters forwarded to `operation`
        loading_control: Flet control with a ``visible`` attribute (optional)
        error_control: Flet control to surface errors (optional)
        on_success: Callback invoked with the extracted data on success
        on_error: Callback invoked with the error string/exception on failure

    Returns:
        The extracted data payload on success, or ``None`` when the operation
        reports failure.
    """

    _toggle_visibility(loading_control, True)
    _toggle_visibility(error_control, False)

    try:
        raw_result = await _execute_operation(operation, operation_args, operation_kwargs)
    except Exception as exc:  # pragma: no cover - defensive guard
        logger.debug("fetch_with_loading: operation raised %s", exc)
        if on_error:
            on_error(exc)
        _toggle_visibility(error_control, True)
        return None
    finally:
        _toggle_visibility(loading_control, False)

    success, payload, error_message = _normalise_result(raw_result)
    if success:
        if on_success:
            on_success(payload)
        return payload

    if on_error:
        on_error(error_message)
    _toggle_visibility(error_control, True)
    return None

async def run_sync_in_executor(func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Legacy wrapper that unwraps structured server responses on success.

    The historical experimental helpers expected ``run_sync_in_executor`` to
    return the data payload directly when the synchronous function yielded a
    ``{"success": bool, "data": ...}`` structure.  Modern code paths operate
    on the structured response instead.  This shim preserves the legacy
    contract for the tests that still import this module while delegating the
    heavy lifting to the production helper.
    """

    result = await _base_run_sync_in_executor(func, *args, **kwargs)

    if isinstance(result, dict) and result.get("success") and "data" in result:
        return result.get("data")
    return result


__all__ = ["run_sync_in_executor", "safe_server_call", "fetch_with_loading"]
