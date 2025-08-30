import pytest
from flet_server_gui.services.busy_indicator import get_busy_indicator
from flet_server_gui.state.selection_state import SelectionState
from flet_server_gui.utils.trace_center import get_trace_center

def test_busy_indicator_underflow_and_nested():
    tc = get_trace_center(); tc.clear()
    busy = get_busy_indicator()
    # Ensure clean state
    while busy.is_busy():
        busy.stop()
    # Underflow call (should not crash and emit warning)
    busy.stop()
    events = tc.export_recent(filter_type="BUSY_UNDERFLOW")
    assert events and events[-1]["type"] == "BUSY_UNDERFLOW"
    # Nested start/stop sequence
    busy.start(); busy.start(); assert busy.is_busy()
    busy.stop(); assert busy.is_busy()  # still one active
    busy.stop(); assert not busy.is_busy()

def test_selection_state_multi_listener():
    tc = get_trace_center(); tc.clear()
    state = SelectionState()
    calls_a = []
    calls_b = []
    state.subscribe("files", lambda tid, ids: calls_a.append((tid, list(ids))))
    state.subscribe("files", lambda tid, ids: calls_b.append((tid, list(ids))))
    state.update_selection("files", ["a","b"])  # triggers both listeners
    assert calls_a and calls_b
    assert calls_a[0][1] == ["a","b"] and calls_b[0][1] == ["a","b"]
    # Clear selection
    state.clear("files")
    assert state.get_selected("files") == []
