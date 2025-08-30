"""runtime_context.py

Holds shared *read-mostly* runtime context values (offline mode, server
capabilities) without relying on hidden feature flags. This centralizes
what would otherwise become scattered booleans. Explicit modification
occurs via public functions intentionally named for agent discoverability.

Initialization Strategy:
- Passive detection tries a lightweight server probe (import + attribute
  check or socket attempt—here simplified to import attempt placeholder).
- If unavailable, context sets `offline_mode=True`.
- A future Settings page can call `set_offline_mode(True/False)` to allow
  user override only when server actually available; when not available,
  toggle shows enforced offline state.

Thread Safety:
- RLock guards context mutation; reads inexpensive.

Edge Cases:
- Probe failures do not throw—they log a trace event and default offline.
- Multiple initialization calls idempotent.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import threading

from .trace_center import get_trace_center


@dataclass(slots=True)
class RuntimeContext:
    offline_mode: bool
    server_available: bool
    build_info: str


class _RuntimeContextHolder:
    _instance: Optional[RuntimeContext] = None
    _lock = threading.RLock()

    @classmethod
    def init(cls) -> RuntimeContext:
        with cls._lock:
            if cls._instance is not None:
                return cls._instance
            server_available = _probe_server_availability()
            offline_mode = not server_available
            cls._instance = RuntimeContext(
                offline_mode=offline_mode,
                server_available=server_available,
                build_info="gui"  # Placeholder; could embed git hash / version
            )
            get_trace_center().emit(type="RUNTIME_CONTEXT", level="INFO", message="Runtime context initialized", meta={
                "offline_mode": cls._instance.offline_mode,
                "server_available": cls._instance.server_available,
            })
            return cls._instance

    @classmethod
    def get(cls) -> RuntimeContext:
        return cls.init() if cls._instance is None else cls._instance

    @classmethod
    def set_offline_mode(cls, value: bool) -> RuntimeContext:
        with cls._lock:
            ctx = cls.get()
            # If server not available, force True regardless of requested value
            forced = (not ctx.server_available)
            new_val = True if forced else value
            if new_val != ctx.offline_mode:
                ctx.offline_mode = new_val
                get_trace_center().emit(type="RUNTIME_CONTEXT", level="INFO", message="Offline mode changed", meta={"offline_mode": new_val, "forced": forced})
            return ctx


def _probe_server_availability() -> bool:
    # Placeholder: Real implementation could attempt import or socket connect.
    try:
        # from some_module import BackupServer  # Example placeholder
        return False  # Assume unavailable in current dev stage.
    except Exception:
        return False


# Public API

def get_runtime_context() -> RuntimeContext:
    return _RuntimeContextHolder.get()


def set_offline_mode(value: bool) -> RuntimeContext:
    return _RuntimeContextHolder.set_offline_mode(value)
