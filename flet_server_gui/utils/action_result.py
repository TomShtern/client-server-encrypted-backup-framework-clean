"""action_result.py

Unified ActionResult implementation aligned with docs/action_result_contract.md.

Replaces prior minimal (status, code, message) schema with richer, yet
parsable structure enabling:
 - Consistent notification & severity mapping
 - Bulk/partial operation summarization
 - Selection + timing telemetry
 - Progressive migration (legacy adapters still accepted)

Backward Compatibility: existing imports remain; legacy fields (status)
still populated, mapping contract `code` & `severity` appropriately.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Optional, List
import time
from flet_server_gui.utils.trace_center import get_trace_center


@dataclass(slots=True)
class ActionResult:
    """Richer unified result object.

    Primary Contract Fields (authoritative):
        code, success, message, severity, data, selection, count,
        duration_ms, error_code, meta, timestamp

    Back-compat Fields:
        status (maps to success|warn|error for existing trace consumers)
        correlation_id
    """

    # Back-compat tri-state for existing pipeline ('success','warn','error')
    # Required (no defaults) first
    status: str
    code: str
    message: str
    success: bool = False
    severity: str = "info"  # success|info|warning|error
    correlation_id: str = ""
    data: Optional[Dict[str, Any]] = None
    duration_ms: int = 0
    selection: Optional[List[str]] = None
    count: Optional[int] = None
    error_code: Optional[str] = None
    details: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: time.strftime('%Y-%m-%dT%H:%M:%S'))

    # ---------- Factory helpers ----------
    @classmethod
    def _build(
        cls,
        *,
        code: str,
        message: str,
        success: bool,
        severity: str,
    correlation_id: str,
    status: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        selection: Optional[List[str]] = None,
        count: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
        duration_ms: int = 0,
    ) -> "ActionResult":
        # Derive legacy status default
        if status is None:
            if success:
                status = "success"
            elif severity == "warning":
                status = "warn"
            else:
                status = "error"
        if selection and count is None:
            count = len(selection)
        return cls(
            status=status,
            code=code,
            message=message,
            success=success,
            severity=severity,
            data=data,
            correlation_id=correlation_id,
            duration_ms=duration_ms,
            selection=selection,
            count=count,
            error_code=error_code,
            details=details,
            meta=meta or {},
        )

    @classmethod
    def make_success(cls, *, code: str, message: str, correlation_id: str, data: Optional[Dict[str, Any]] = None, selection=None, meta=None, duration_ms: int = 0) -> "ActionResult":
        return cls._build(code=code, message=message, success=True, severity="success", correlation_id=correlation_id, data=data, selection=selection, meta=meta, duration_ms=duration_ms)

    @classmethod
    def make_info(cls, *, code: str, message: str, correlation_id: str, data: Optional[Dict[str, Any]] = None, selection=None, meta=None, duration_ms: int = 0) -> "ActionResult":
        return cls._build(code=code, message=message, success=True, severity="info", correlation_id=correlation_id, data=data, selection=selection, meta=meta, duration_ms=duration_ms)

    @classmethod
    def make_warn(cls, *, code: str, message: str, correlation_id: str, data: Optional[Dict[str, Any]] = None, selection=None, meta=None, duration_ms: int = 0) -> "ActionResult":
        return cls._build(code=code, message=message, success=False, severity="warning", correlation_id=correlation_id, data=data, selection=selection, meta=meta, duration_ms=duration_ms)

    @classmethod
    def make_partial(cls, *, code: str, message: str, correlation_id: str, failed: List[Dict[str, Any]], data: Optional[Dict[str, Any]] = None, selection=None, meta=None, duration_ms: int = 0) -> "ActionResult":
        m = meta or {}
        m.update({"partial_failures": failed, "failed_count": len(failed)})
        return cls._build(code=code, message=message, success=False, severity="warning", correlation_id=correlation_id, data=data, selection=selection, meta=m, duration_ms=duration_ms, status="warn")

    @classmethod
    def make_error(cls, *, code: str, message: str, correlation_id: str, error_code: str | None = None, details: str | None = None, data: Optional[Dict[str, Any]] = None, selection=None, meta=None, duration_ms: int = 0) -> "ActionResult":
        return cls._build(code=code, message=message, success=False, severity="error", correlation_id=correlation_id, data=data, selection=selection, meta=meta, duration_ms=duration_ms, error_code=error_code, details=details)

    @classmethod
    def make_cancelled(cls, *, correlation_id: str, message: str = "Cancelled by user", selection=None, meta=None, duration_ms: int = 0) -> "ActionResult":
        return cls._build(code="CANCELLED", message=message, success=False, severity="info", correlation_id=correlation_id, selection=selection, meta=meta, duration_ms=duration_ms, status="warn")

    @classmethod
    def make_retrying(cls, *, code: str, message: str, attempt: int, max_attempts: int, correlation_id: str, selection=None, meta=None) -> "ActionResult":
        m = meta or {}
        m.update({"attempt": attempt, "max_attempts": max_attempts})
        return cls._build(code=code, message=message, success=False, severity="info", correlation_id=correlation_id, selection=selection, meta=m, status="warn")

    # Legacy compatibility wrappers (existing call sites use old signature)
    @classmethod
    def legacy_success(cls, code: str, message: str, correlation_id: str, *, data: Optional[Dict[str, Any]] = None, duration_ms: int = 0):  # noqa: D401
        return cls.make_success(code=code, message=message, correlation_id=correlation_id, data=data, duration_ms=duration_ms)

    @classmethod
    def legacy_warn(cls, code: str, message: str, correlation_id: str, *, data: Optional[Dict[str, Any]] = None, duration_ms: int = 0):
        return cls.make_warn(code=code, message=message, correlation_id=correlation_id, data=data, duration_ms=duration_ms)

    @classmethod
    def legacy_error(cls, code: str, message: str, correlation_id: str, *, data: Optional[Dict[str, Any]] = None, duration_ms: int = 0):
        return cls.make_error(code=code, message=message, correlation_id=correlation_id, data=data, duration_ms=duration_ms)

    # Broad compatibility helpers for older call sites expecting simplified factories
    @classmethod
    def success_result(cls, data: Any = None, metadata: Optional[Dict[str, Any]] = None):  # type: ignore[override]
        cid = get_trace_center().new_correlation_id()
        payload = data if isinstance(data, dict) else ({"value": data} if data is not None else None)
        return cls.make_success(code="OK", message="Success", correlation_id=cid, data=payload, meta=metadata or {})

    @classmethod
    def error_result(cls, error_message: str, error_code: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):  # type: ignore[override]
        cid = get_trace_center().new_correlation_id()
        return cls.make_error(code=error_code or "ERROR", message=error_message, correlation_id=cid, error_code=error_code, meta=metadata or {})

    # Simple factory methods for common use cases
    @classmethod
    def error(cls, *, code: str, message: str, correlation_id: Optional[str] = None, error_code: Optional[str] = None) -> "ActionResult":
        """Simple error factory method"""
        cid = correlation_id or get_trace_center().new_correlation_id()
        return cls.make_error(code=code, message=message, correlation_id=cid, error_code=error_code)
    
    @classmethod
    def success(cls, *, code: str, message: str, correlation_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> "ActionResult":
        """Simple success factory method"""
        cid = correlation_id or get_trace_center().new_correlation_id()
        return cls.make_success(code=code, message=message, correlation_id=cid, data=data)
    
    @classmethod
    def info(cls, *, code: str, message: str, correlation_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> "ActionResult":
        """Simple info factory method"""
        cid = correlation_id or get_trace_center().new_correlation_id()
        return cls.make_info(code=code, message=message, correlation_id=cid, data=data)
    
    @classmethod
    def warn(cls, *, code: str, message: str, correlation_id: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> "ActionResult":
        """Simple warning factory method"""
        cid = correlation_id or get_trace_center().new_correlation_id()
        return cls.make_warn(code=code, message=message, correlation_id=cid, data=data)
    
    @classmethod
    def cancelled(cls, *, code: str = "CANCELLED", message: str = "Cancelled by user", correlation_id: Optional[str] = None) -> "ActionResult":
        """Simple cancelled factory method"""
        cid = correlation_id or get_trace_center().new_correlation_id()
        return cls.make_cancelled(correlation_id=cid, message=message)
    
    @classmethod
    def partial(cls, *, code: str, message: str, correlation_id: Optional[str] = None, failed: List[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> "ActionResult":
        """Simple partial factory method"""
        cid = correlation_id or get_trace_center().new_correlation_id()
        return cls.make_partial(code=code, message=message, correlation_id=cid, failed=failed or [], data=data)

    def to_dict(self) -> Dict[str, Any]:  # noqa: D401
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionResult":
        """Create ActionResult from dict (best-effort for tests/serialization)."""
        return cls(
            status=data.get("status", "success" if data.get("success", False) else "error"),
            code=data.get("code", "UNKNOWN"),
            message=data.get("message", ""),
            success=data.get("success", False),
            severity=data.get("severity", "info"),
            data=data.get("data"),
            correlation_id=data.get("correlation_id", "n/a"),
            duration_ms=data.get("duration_ms", 0),
            selection=data.get("selection"),
            count=data.get("count"),
            error_code=data.get("error_code"),
            details=data.get("details"),
            meta=data.get("meta", {}),
            timestamp=data.get("timestamp", time.strftime('%Y-%m-%dT%H:%M:%S')),
        )


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
    return ActionResult.make_success(
        code="GENERIC_OK",
        message="Operation completed",
        correlation_id=correlation_id,
        data={"result": result} if result is not None else None,
        duration_ms=duration_ms,
    )
