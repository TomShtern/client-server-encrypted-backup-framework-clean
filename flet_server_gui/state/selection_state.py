"""Selection State Service

Centralized publisher/subscriber selection tracking for tables.
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time  # Import time for timestamping
from typing import Callable, Dict, List, Set, Optional, Any, Tuple
import asyncio
from flet_server_gui.utils.trace_center import get_trace_center

SelectionListener = Callable[[str, List[str]], None]

@dataclass
class TableSelection:
    table_id: str
    selected_ids: Set[str] = field(default_factory=set)
    last_updated: float = 0.0

class SelectionState:
    """Global selection registry for all data tables.
    Thread-safe for async UI usage via internal lock.
    """
    def __init__(self):
        self._selections: Dict[str, TableSelection] = {}
        self._listeners: Dict[str, List[SelectionListener]] = {}
        self._lock = asyncio.Lock()

    def update_selection(self, table_id: str, ids: List[str]):
        # Synchronous variant for simple test usage
        sel = self._selections.get(table_id) or TableSelection(table_id=table_id)
        new_set = set(ids)
        if prev := set(sel.selected_ids):
            added = list(new_set - prev)
            removed = list(prev - new_set)
        else:
            # First assignment: treat entire set as added, none removed
            added = list(new_set)
            removed = []
        sel.selected_ids = new_set
        sel.last_updated = time.time()
        self._selections[table_id] = sel
        get_trace_center().emit(
            type="SELECTION",
            level="INFO",
            message="selection updated",
            meta={
                "table": table_id,
                "count": len(ids),
                "added": added,
                "removed": removed,
            },
        )
        listeners = list(self._listeners.get(table_id, []))
        for listener in listeners:
            try:
                listener(table_id, ids)
            except Exception as e:  # noqa: BLE001
                get_trace_center().emit(type="SELECTION_LISTENER_ERROR", level="ERROR", message=str(e), meta={"table": table_id})

    def clear(self, table_id: str):
        self.update_selection(table_id, [])

    def select_all(self, table_id: str, all_ids: List[str]):
        self.update_selection(table_id, all_ids)

    def get_selected(self, table_id: str) -> List[str]:
        return list(self._selections.get(table_id, TableSelection(table_id)).selected_ids)

    def subscribe(self, table_id: str, listener: SelectionListener):
        self._listeners.setdefault(table_id, []).append(listener)

    def unsubscribe(self, table_id: str, listener: SelectionListener):
        if table_id in self._listeners:
            self._listeners[table_id] = [l for l in self._listeners[table_id] if l != listener]
            if not self._listeners[table_id]:
                del self._listeners[table_id]

# Global singleton accessor
selection_state = SelectionState()
