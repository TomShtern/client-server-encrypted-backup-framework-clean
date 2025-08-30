"""Notification Center
Aggregates ActionResult events and notifies subscribers (e.g., toast manager, status bar).
"""
from __future__ import annotations
from typing import Callable, List
from flet_server_gui.utils.action_result import ActionResult
from flet_server_gui.utils.trace_center import get_trace_center

NotificationListener = Callable[[ActionResult], None]

class NotificationCenter:
    def __init__(self):
        self._listeners: List[NotificationListener] = []

    def subscribe(self, listener: NotificationListener):
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: NotificationListener):
        self._listeners = [l for l in self._listeners if l != listener]

    def publish(self, result: ActionResult):
        # Trace emission
        get_trace_center().emit(
            type="ACTION_RESULT",
            level=result.severity.upper(),
            message=result.message,
            meta={
                "code": result.code,
                "success": result.success,
                "severity": result.severity,
                "duration_ms": result.duration_ms,
                "count": result.count,
                "selection_size": len(result.selection) if result.selection else 0,
            },
            correlation_id=result.correlation_id,
        )
        for listener in list(self._listeners):
            try:
                listener(result)
            except Exception as e:
                get_trace_center().emit(type="NOTIFICATION_ERROR", level="ERROR", message=str(e))

# Global singleton
_notification_center: NotificationCenter | None = None

def get_notification_center() -> NotificationCenter:
    global _notification_center
    if _notification_center is None:
        _notification_center = NotificationCenter()
    return _notification_center
