"""Lightweight performance instrumentation utilities.

Provides minimal overhead timing & metric aggregation for manual benchmarking
aligned with Plan Phase F (QA & Metrics).

Usage:
    from utils.perf_metrics import PerfTimer, record_metric, get_metrics, reset_metrics
    with PerfTimer("files.update_table_display"):
        update_table_display()

Design constraints:
- No external deps
- Thread-safe via simple Lock
- Stores only aggregate stats (count, total_ms, max_ms, last_ms)
- Accessors return shallow copy to avoid accidental mutation
"""
from __future__ import annotations
import time
import threading
from typing import Dict, Any

__all__ = ["PerfTimer", "record_metric", "get_metrics", "reset_metrics"]

_metrics_lock = threading.Lock()
_metrics: Dict[str, Dict[str, Any]] = {}

def record_metric(name: str, elapsed_ms: float) -> None:
    with _metrics_lock:
        m = _metrics.setdefault(name, {"count": 0, "total_ms": 0.0, "max_ms": 0.0, "last_ms": 0.0})
        m["count"] += 1
        m["total_ms"] += elapsed_ms
        m["last_ms"] = elapsed_ms
        if elapsed_ms > m["max_ms"]:
            m["max_ms"] = elapsed_ms

def get_metrics() -> Dict[str, Dict[str, Any]]:
    with _metrics_lock:
        # Shallow copy to ensure caller cannot mutate internal state directly
        return {k: v.copy() for k, v in _metrics.items()}

def reset_metrics(pattern: str | None = None) -> None:
    with _metrics_lock:
        if pattern is None:
            _metrics.clear()
        else:
            for k in list(_metrics.keys()):
                if pattern in k:
                    _metrics.pop(k, None)

class PerfTimer:
    """Context manager & optional decorator for timing blocks.

    Example:
        with PerfTimer("files.load"):
            await load_files_data_async()
    """
    __slots__ = ("name", "start")

    def __init__(self, name: str):
        self.name = name
        self.start = 0.0

    def __enter__(self):  # type: ignore[override]
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):  # type: ignore[override]
        elapsed_ms = (time.perf_counter() - self.start) * 1000.0
        record_metric(self.name, elapsed_ms)
        # Don't suppress exceptions
        return False
