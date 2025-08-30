"""Busy Indicator Service
Simple reference-counted global busy overlay controller.
"""
from __future__ import annotations
from typing import Optional, Callable
from flet_server_gui.utils.trace_center import get_trace_center
from contextlib import contextmanager

class BusyIndicatorService:
    def __init__(self, show_cb: Optional[Callable[[], None]] = None, hide_cb: Optional[Callable[[], None]] = None):
        self._count = 0
        self._show_cb = show_cb
        self._hide_cb = hide_cb

    def attach(self, show_cb: Callable[[], None], hide_cb: Callable[[], None]):
        self._show_cb = show_cb
        self._hide_cb = hide_cb

    def start(self):
        self._count += 1
        if self._count == 1 and self._show_cb:
            self._show_cb()
            get_trace_center().emit(type="BUSY", level="INFO", message="busy started")

    def stop(self):
        if self._count > 0:
            self._count -= 1
            if self._count == 0 and self._hide_cb:
                self._hide_cb()
                get_trace_center().emit(type="BUSY", level="INFO", message="busy ended")
        else:
            # Underflow protection: never go negative, emit diagnostic trace once per call
            get_trace_center().emit(type="BUSY_UNDERFLOW", level="WARN", message="stop() called with count already zero")

    # Test helper / convenience
    def is_busy(self) -> bool:
        return self._count > 0

    @contextmanager
    def active(self):
        """Context manager to automatically balance start/stop.

        Usage:
            with get_busy_indicator().active():
                ... do work ...
        Guarantees no underflow even if an exception occurs.
        """
        self.start()
        try:
            yield
        finally:
            self.stop()

# Global singleton
_busy: BusyIndicatorService | None = None

def get_busy_indicator() -> BusyIndicatorService:
    global _busy
    if _busy is None:
        _busy = BusyIndicatorService()
    return _busy
