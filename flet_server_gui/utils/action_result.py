"""action_result.py

Provides the canonical ActionResult object used to unify outcomes of all
UI-triggered operations (button clicks, menu actions, background syncs).

Design Goals:
- Minimal but expressive schema for AI agent & human consumption.
- Stable keys (snake_case) for log / JSON serialization.
- Distinguish transport severity (warn/error) from status category.
- Correlation with tracing via correlation_id.

Trade-offs:
- Keeps status as coarse enum ('success','warn','error') instead of a
  richer lattice to stay parse-friendly.
- Optional code field allows domain-specific machine codes without
  enforcing a registry at this stage.

Edge Cases Considered:
- Unexpected exceptions -> error with fallback generic code.
- No-op in offline mode -> warn with explicit offline code.
- User precondition failure (e.g., no selection) -> warn.

Future Extensions:
- Optional "hints" list (not added yet to keep payload lean).
- Localization mapping (currently message is raw English).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import time


@dataclass(slots=True)
class ActionResult:
    """Represents the standardized outcome of an executed action.

    Fields:
        status:   'success' | 'warn' | 'error'
        code:     Machine-readable code (e.g., 'CLIENT_DELETE_OK').
        message:  Human-readable explanation.
        data:     Optional structured payload (must be JSON-serializable).
        correlation_id: Correlates with trace events.
        duration_ms: Execution duration.
    """
    status: str
    code: str
    message: str
    data: Optional[Dict[str, Any]]
    correlation_id: str
    duration_ms: int

    @classmethod
    def success(cls, code: str, message: str, correlation_id: str, *, data: Optional[Dict[str, Any]] = None, duration_ms: int = 0) -> "ActionResult":
        return cls("success", code, message, data, correlation_id, duration_ms)

    @classmethod
    def warn(cls, code: str, message: str, correlation_id: str, *, data: Optional[Dict[str, Any]] = None, duration_ms: int = 0) -> "ActionResult":
        return cls("warn", code, message, data, correlation_id, duration_ms)

    @classmethod
    def error(cls, code: str, message: str, correlation_id: str, *, data: Optional[Dict[str, Any]] = None, duration_ms: int = 0) -> "ActionResult":
        return cls("error", code, message, data, correlation_id, duration_ms)

    def to_dict(self) -> Dict[str, Any]:
        """Return dictionary form safe for JSON serialization."""
        return asdict(self)


def timed_execution(fn, *args, correlation_id: str, **kwargs) -> ActionResult:
    """Utility to time a callable returning ActionResult or raw data.

    If the callable returns ActionResult we enrich duration.
    If it returns dict/None we wrap into success result with generic code.
    Exceptions are not caught here (caller decides) to avoid double wrapping.
    """
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    duration_ms = int((time.perf_counter() - start) * 1000)
    if isinstance(result, ActionResult):
        result.duration_ms = duration_ms
        return result
    # Wrap generic success
    return ActionResult.success(
        code="GENERIC_OK",
        message="Operation completed",
        correlation_id=correlation_id,
        data={"result": result} if result is not None else None,
        duration_ms=duration_ms,
    )
