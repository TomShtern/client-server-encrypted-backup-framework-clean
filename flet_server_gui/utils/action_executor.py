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
from .runtime_context import get_runtime_context

# Type aliases
AsyncCallable = Callable[[], Awaitable[Any]]
SelectionProvider = Callable[[], Iterable[str]]


class ActionExecutor:
    """High-level orchestrator for action execution.

    Typical usage:
        executor = ActionExecutor()
        await executor.run(
            action_name="delete_client",
            action_coro=lambda: client_actions.delete_client(client_id),
            selection_provider=current_selection,
        )
    """

    def __init__(self) -> None:
        self._trace = get_trace_center()

    async def run(
        self,
        *,
        action_name: str,
        action_coro: AsyncCallable,
        selection_provider: Optional[SelectionProvider] = None,
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
        ctx = get_runtime_context()

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
            return ActionResult.warn(
                code="EMPTY_SELECTION",
                message="No items selected",
                correlation_id=cid,
                data={"required": True},
            )
        if mutate and ctx.offline_mode:
            trace_action_start(action_name, cid, meta=start_trace_meta)
            trace_action_end(action_name, cid, "warn", 0, meta={"reason": "offline_noop"})
            return ActionResult.warn(
                code="OFFLINE_NOOP",
                message="Offline mode: mutation skipped",
                correlation_id=cid,
                data={"offline_mode": True},
            )

        trace_action_start(action_name, cid, meta=start_trace_meta)
        t0 = time.perf_counter()
        try:
            result = await action_coro()
            elapsed = int((time.perf_counter() - t0) * 1000)
            if isinstance(result, ActionResult):
                # Ensure duration recorded
                result.duration_ms = elapsed
                trace_action_end(action_name, cid, result.status, elapsed)
                return result
            # Wrap non-standard returns
            trace_action_end(action_name, cid, "success", elapsed)
            return ActionResult.success(
                code=f"{action_name.upper()}_OK",
                message=f"{action_name} completed",
                correlation_id=cid,
                data={"raw": result} if result is not None else None,
                duration_ms=elapsed,
            )
        except asyncio.CancelledError:
            elapsed = int((time.perf_counter() - t0) * 1000)
            trace_action_error(action_name, cid, "Cancelled", meta={"elapsed_ms": elapsed})
            return ActionResult.warn(
                code="ACTION_CANCELLED",
                message=f"{action_name} cancelled",
                correlation_id=cid,
                duration_ms=elapsed,
            )
        except Exception as e:  # noqa: BLE001 broad for top-level safety
            elapsed = int((time.perf_counter() - t0) * 1000)
            stack = traceback.format_exc(limit=3)
            trace_action_error(action_name, cid, str(e), meta={"elapsed_ms": elapsed, "stack": stack})
            return ActionResult.error(
                code=f"{action_name.upper()}_ERROR",
                message=str(e),
                correlation_id=cid,
                data={"stack": stack},
                duration_ms=elapsed,
            )


# Convenience singleton-style accessor if needed
_executor_singleton: ActionExecutor | None = None


def get_action_executor() -> ActionExecutor:
    global _executor_singleton
    if _executor_singleton is None:
        _executor_singleton = ActionExecutor()
    return _executor_singleton
