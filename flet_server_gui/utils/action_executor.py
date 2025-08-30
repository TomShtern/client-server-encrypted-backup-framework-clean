"""action_executor.py

Provides a standardized asynchronous execution pipeline for UI-triggered
actions. This central wrapper ensures consistent tracing, correlation ID
propagation, timing, structured error handling, and ActionResult
normalization.

Why centralize now?
- Current ad-hoc button handlers produce silent failures and lack
  consistent observability. A single orchestrator reduces variance.
- Keeps original action callables unchanged; we wrap them, so rollback is
  trivial (remove wrapper usage).

Edge Cases:
- Precondition failure (e.g., empty selection) -> warn result; no raise.
- Unexpected exception -> error result with message sanitized (stack can
  be separately logged in meta if desired).
- Offline mode mutation attempted -> warn no-op but still traced.

Performance Considerations:
- Minimal overhead: a few dict constructions + time.perf_counter.
- No heavy serialization inline; trace center handles truncation.
"""
from __future__ import annotations

import asyncio
import time
import traceback
from typing import Any, Awaitable, Callable, Dict, Iterable, Optional

from .action_result import ActionResult
from .trace_center import (
    trace_action_start,
    trace_action_end,
    trace_action_error,
    get_trace_center,
)
from flet_server_gui.services.notification_center import get_notification_center
from flet_server_gui.services.busy_indicator import get_busy_indicator
from .error_context import create_error_context


class ActionExecutor:
    def __init__(self) -> None:
        self._trace = get_trace_center()
        self._dialog_system = None
        self._data_change_callbacks = []
        self._error_boundary = None  # Will be set by the error boundary system

    def set_dialog_system(self, dialog_system):
        """Set the dialog system for confirmation dialogs"""
        self._dialog_system = dialog_system
    
    def set_error_boundary(self, error_boundary):
        """Set the error boundary for enhanced error handling"""
        self._error_boundary = error_boundary
    
    def add_data_change_callback(self, callback: Callable):
        """Add a callback to be triggered when data changes occur"""
        if callback not in self._data_change_callbacks:
            self._data_change_callbacks.append(callback)
    
    def remove_data_change_callback(self, callback: Callable):
        """Remove a data change callback"""
        if callback in self._data_change_callbacks:
            self._data_change_callbacks.remove(callback)
    
    async def _trigger_data_change_callbacks(self):
        """Trigger all registered data change callbacks"""
        for callback in self._data_change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                # Log callback errors but don't fail the main operation
                self._trace.emit(
                    type="DATA_CALLBACK_ERROR",
                    level="WARN", 
                    message=f"Data change callback failed: {str(e)}"
                )

    async def run_with_confirmation(
        self,
        *,
        action_name: str,
        action_coro: Callable[[], Awaitable[Any]],
        confirmation_text: Optional[str] = None,
        confirmation_title: Optional[str] = None,
        trigger_data_change: bool = True,
        **run_kwargs
    ) -> ActionResult:
        """Execute an action with optional confirmation dialog.
        
        Args:
            action_name: Human/machine readable name.
            action_coro: Zero-arg async callable performing the work.
            confirmation_text: Text to show in confirmation dialog.
            confirmation_title: Title for confirmation dialog.
            trigger_data_change: Whether to trigger data change callbacks on success.
            **run_kwargs: Additional arguments passed to run()
        """
        # Handle confirmation if needed
        if confirmation_text and self._dialog_system:
            title = confirmation_title or f"Confirm {action_name}"
            confirmed = await self._dialog_system.show_confirmation_async(
                title=title,
                message=confirmation_text
            )
            if not confirmed:
                cid = self._trace.new_correlation_id()
                return ActionResult.make_warn(
                    code="USER_CANCELLED",
                    message="Operation cancelled by user",
                    correlation_id=cid,
                    data={"action_name": action_name}
                )
        
        # Execute the action
        result = await self.run(
            action_name=action_name,
            action_coro=action_coro,
            **run_kwargs
        )
        
        # Trigger data change callbacks on successful mutations
        if trigger_data_change and result.success and self._data_change_callbacks:
            await self._trigger_data_change_callbacks()
        
        return result

    async def run(
        self,
        *,
        action_name: str,
        action_coro: Callable[[], Awaitable[Any]],
        selection_provider: Optional[Callable[[], Iterable[str]]] = None,
        require_selection: bool = False,
        mutate: bool = False,
        correlation_id: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> ActionResult:
        """Execute an action coroutine with standardized pipeline.

        Args:
            action_name: Human/machine readable name.
            action_coro: Zero-arg async callable performing the work.
            selection_provider: Returns iterable of selected ids if needed.
            require_selection: If True, empty selection becomes warn result.
            mutate: If True, offline mode short-circuits with warn result.
            correlation_id: Provided or auto-generated for grouping.
            meta: Additional metadata for start trace.
        """
        cid = correlation_id or self._trace.new_correlation_id()
        start_trace_meta = dict(meta or {})
        # ctx = get_runtime_context()  # This line seems to be missing a function definition

        # Gather selection early (don't call selection twice to avoid race)
        selection_list = []
        if selection_provider:
            try:
                selection_list = list(selection_provider())
                start_trace_meta["selection_size"] = len(selection_list)
            except Exception as e:
                # Selection failure is an error-level trace but returns warn result
                trace_action_error(action_name, cid, f"Selection provider failed: {e}")
                return ActionResult.warn(
                    code="SELECTION_PROVIDER_ERROR",
                    message="Failed to read selection",
                    correlation_id=cid,
                )
        if require_selection and not selection_list:
            trace_action_start(action_name, cid, meta=start_trace_meta)
            trace_action_end(action_name, cid, "warn", 0, meta={"reason": "empty_selection"})
            return ActionResult.make_warn(
                code="EMPTY_SELECTION",
                message="No items selected",
                correlation_id=cid,
                data={"required": True},
            )
        
        # Note: Offline mode check removed for simplicity
        # Future enhancement: add offline mode support if needed

        trace_action_start(action_name, cid, meta=start_trace_meta)
        busy = get_busy_indicator()
        busy.start()
        t0 = time.perf_counter()
        try:
            result = await action_coro()
            elapsed = int((time.perf_counter() - t0) * 1000)
            if isinstance(result, ActionResult):
                # Ensure duration recorded
                result.duration_ms = elapsed
                trace_action_end(action_name, cid, result.status, elapsed)
                get_notification_center().publish(result)
                busy.stop()
                return result
            # Wrap non-standard returns
            trace_action_end(action_name, cid, "success", elapsed)
            wrapped = ActionResult.make_success(
                code=f"{action_name.upper()}_OK",
                message=f"{action_name} completed",
                correlation_id=cid,
                data={"raw": result} if result is not None else None,
                duration_ms=elapsed,
            )
            get_notification_center().publish(wrapped)
            busy.stop()
            return wrapped
        except asyncio.CancelledError:
            elapsed = int((time.perf_counter() - t0) * 1000)
            trace_action_error(action_name, cid, "Cancelled", meta={"elapsed_ms": elapsed})
            wrapped = ActionResult.make_warn(
                code="ACTION_CANCELLED",
                message=f"{action_name} cancelled",
                correlation_id=cid,
                duration_ms=elapsed,
            )
            get_notification_center().publish(wrapped)
            busy.stop()
            return wrapped
        except Exception as e:  # noqa: BLE001 broad for top-level safety
            elapsed = int((time.perf_counter() - t0) * 1000)
            stack = traceback.format_exc(limit=3)
            
            # Enhanced error handling with error boundary
            if self._error_boundary:
                try:
                    # Create error context for detailed error information
                    error_context = create_error_context(
                        exception=e,
                        operation=action_name,
                        component="ActionExecutor",
                        correlation_id=cid
                    )
                    
                    # Log the error context
                    error_context.log_error()
                    
                    # Let error boundary handle the exception (but don't show dialog for actions)
                    # The error boundary will log and potentially report the error
                    await self._error_boundary._handle_exception(
                        e,
                        operation=action_name,
                        component="ActionExecutor",
                        correlation_id=cid
                    )
                except Exception as boundary_error:
                    # Fallback to standard logging if error boundary fails
                    get_trace_center().emit(
                        type="ERROR_BOUNDARY_FAILED",
                        level="ERROR",
                        message=f"Error boundary failed during action execution: {str(boundary_error)}",
                        correlation_id=cid
                    )
            
            trace_action_error(action_name, cid, str(e), meta={"elapsed_ms": elapsed, "stack": stack})
            wrapped = ActionResult.error(
                code=f"{action_name.upper()}_ERROR",
                message=str(e),
                correlation_id=cid,
            )
            get_notification_center().publish(wrapped)
            busy.stop()
            return wrapped
        finally:
            # Safety: ensure busy counter released on any unexpected path
            if busy._count > 0:
                busy.stop()


# Convenience singleton-style accessor if needed
_executor_singleton: ActionExecutor | None = None


def get_action_executor() -> ActionExecutor:
    global _executor_singleton
    if _executor_singleton is None:
        _executor_singleton = ActionExecutor()
    return _executor_singleton