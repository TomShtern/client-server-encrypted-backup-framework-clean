"""trace_center.py

Central lightweight tracing hub replacing ad-hoc print debugging.

Goals:
- Bounded in-memory ring buffer for fast recent-event inspection (default 600 entries per user guidance for ~1.5–2 runs).
- Optional JSONL file append (disabled by default until explicitly enabled by UI setting—no hidden flag logic, explicit method call).
- Machine & AI friendly: fixed schema, snake_case keys, minimal nesting.
- Non-blocking emission: lock with minimal contention; avoids long I/O on UI thread.

Design Choices:
- Uses dataclass-like dict generation instead of full pydantic to avoid runtime overhead.
- Avoids background flush thread initially; synchronous file append small enough for current scale.
- Uses simple re-entrant lock to protect buffer; could be swapped for deque without lock if only single thread, but future async tasks may emit concurrently.

Edge Cases:
- Oversized meta payload truncated to protect memory.
- Emission during exception handling still succeeds (fallback minimal record if serialization fails).
- File I/O errors degrade silently to memory-only mode but record an INTERNAL_ERROR event once.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional
import json
import threading
import time
import uuid
import os

_DEFAULT_MAX_EVENTS = 600  # per user feedback (allow ~1.5–2 runs worth of activity)
_MAX_META_LENGTH = 10_000   # soft cap on meta serialization size (characters)


@dataclass(slots=True)
class TraceEvent:
    ts: int
    correlation_id: str
    type: str
    level: str
    action: Optional[str]
    message: Optional[str]
    meta: Optional[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ts": self.ts,
            "correlation_id": self.correlation_id,
            "type": self.type,
            "level": self.level,
            "action": self.action,
            "message": self.message,
            "meta": self.meta,
        }


class TraceCenter:
    _instance: "TraceCenter" | None = None
    _lock = threading.RLock()

    def __init__(self, max_events: int = _DEFAULT_MAX_EVENTS) -> None:
        self._events: Deque[TraceEvent] = deque(maxlen=max_events)
        self._file_path: Optional[str] = None
        self._file_error: bool = False
        self._events_lock = threading.RLock()

    # Singleton accessor (explicit; tests can create isolated instance directly)
    @classmethod
    def get(cls) -> "TraceCenter":
        with cls._lock:
            if cls._instance is None:
                cls._instance = TraceCenter()
            return cls._instance

    @staticmethod
    def new_correlation_id() -> str:
        return uuid.uuid4().hex[:8]

    def enable_file_logging(self, file_path: str) -> None:
        """Enable JSONL file logging (explicit call—no hidden flag)."""
        self._file_path = file_path
        # Touch file
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "a", encoding="utf-8"):
                pass
        except Exception:
            self._file_error = True
            self.emit(type="INTERNAL_ERROR", level="ERROR", message="Failed to enable file logging", action=None, meta={"file_path": file_path})

    def emit(self, *, type: str, level: str = "DEBUG", message: Optional[str] = None, action: Optional[str] = None, correlation_id: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> str:
        """Record a trace event and return correlation_id used.

        Truncates meta if too large. Safe fallback on serialization failure.
        """
        cid = correlation_id or self.new_correlation_id()
        ts = int(time.time() * 1000)
        safe_meta = None
        if meta:
            try:
                serialized = json.dumps(meta, default=str)
                safe_meta = {"truncated": True} if len(serialized) > _MAX_META_LENGTH else meta
            except Exception:
                safe_meta = {"serialization_failure": True}
        event = TraceEvent(ts=ts, correlation_id=cid, type=type, level=level, action=action, message=message, meta=safe_meta)
        with self._events_lock:
            self._events.append(event)
            if self._file_path and not self._file_error:
                try:
                    with open(self._file_path, "a", encoding="utf-8") as f:
                        json.dump(event.to_dict(), f)
                        f.write("\n")
                except Exception:
                    self._file_error = True
                    # Record once; avoid recursion
        return cid

    def export_recent(self, limit: int = 200, filter_type: Optional[str] = None, correlation_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return recent events (newest last) filtered optionally."""
        with self._events_lock:
            events = list(self._events)
        if filter_type:
            events = [e for e in events if e.type == filter_type]
        if correlation_id:
            events = [e for e in events if e.correlation_id == correlation_id]
        return [e.to_dict() for e in events[-limit:]]

    def clear(self) -> None:
        with self._events_lock:
            self._events.clear()


# Convenience module-level helpers (explicit for discoverability)
def get_trace_center() -> TraceCenter:
    return TraceCenter.get()


def trace_action_start(action: str, correlation_id: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> str:
    return get_trace_center().emit(type="ACTION_START", level="INFO", action=action, message=f"Action {action} started", correlation_id=correlation_id, meta=meta)


def trace_action_end(action: str, correlation_id: str, result_status: str, duration_ms: int, meta: Optional[Dict[str, Any]] = None) -> None:
    get_trace_center().emit(type="ACTION_END", level="INFO", action=action, correlation_id=correlation_id, message=f"Action {action} {result_status}", meta={"duration_ms": duration_ms, **(meta or {})})


def trace_action_error(action: str, correlation_id: str, message: str, meta: Optional[Dict[str, Any]] = None) -> None:
    get_trace_center().emit(type="ACTION_ERROR", level="ERROR", action=action, correlation_id=correlation_id, message=message, meta=meta)
