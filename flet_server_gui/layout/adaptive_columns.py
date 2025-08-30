"""Adaptive Column Visibility System

Determines which columns to show based on available width using priority & minimum widths.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Callable
from flet_server_gui.utils.trace_center import get_trace_center

@dataclass(order=True)
class ColumnSpec:
    priority: int
    id: str = field(compare=False)
    title: str = field(compare=False)
    min_width: int = field(compare=False, default=120)
    always_visible: bool = field(compare=False, default=False)
    collapse_group: Optional[str] = field(compare=False, default=None)  # group that can collapse into a summary column
    summary_of: Optional[List[str]] = field(compare=False, default=None)  # if this column summarizes others

@dataclass
class LayoutDecision:
    visible: List[str]
    hidden: List[str]
    width_used: int
    width_available: int

class AdaptiveColumnManager:
    def __init__(self, specs: List[ColumnSpec]):
        # Sort specs: always_visible first preserving their relative order, then by priority asc
        self.specs = specs
        self._sorted = sorted(specs, key=lambda s: (not s.always_visible, s.priority))

    def compute(self, available_width: int, per_column_padding: int = 24) -> LayoutDecision:
        width_used = 0
        visible = []
        hidden = []
        for spec in self._sorted:
            needed = spec.min_width + per_column_padding
            if spec.always_visible or width_used + needed <= available_width or not visible:
                visible.append(spec.id)
                width_used += needed
            else:
                hidden.append(spec.id)
        get_trace_center().emit(
            type="LAYOUT_COLUMNS",
            level="DEBUG",
            message="layout computed",
            meta={"available": available_width, "used": width_used, "visible": visible, "hidden": hidden},
        )
        return LayoutDecision(
            visible=visible,
            hidden=hidden,
            width_used=width_used,
            width_available=available_width,
        )

    def get_spec(self, col_id: str) -> Optional[ColumnSpec]:
        return next((s for s in self.specs if s.id == col_id), None)

    # Backwards compatibility alias requested by tests
    def compute_visible(self, available_width: int) -> List[ColumnSpec]:
        decision = self.compute(available_width)
        # Return full spec objects for visible columns
        return [self.get_spec(cid) for cid in decision.visible if self.get_spec(cid)]

# Example usage helper
def example_specs() -> List[ColumnSpec]:
    return [
        ColumnSpec(id="status", title="Status", priority=0, min_width=90, always_visible=True),
        ColumnSpec(id="name", title="Name", priority=1, min_width=160, always_visible=True),
        ColumnSpec(id="ip", title="IP", priority=2, min_width=140),
        ColumnSpec(id="last_seen", title="Last Seen", priority=3, min_width=160),
        ColumnSpec(id="files", title="Files", priority=4, min_width=100),
        ColumnSpec(id="size", title="Total Size", priority=5, min_width=140),
    ]
