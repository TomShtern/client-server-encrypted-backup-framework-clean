from flet_server_gui.services.busy_indicator import get_busy_indicator
from flet_server_gui.state.selection_state import SelectionState
from flet_server_gui.utils.trace_center import get_trace_center, trace_action_end, trace_action_start


def test_action_trace_pairing_and_correlation_uniqueness():
    tc = get_trace_center(); tc.clear()
    cids = set()
    for i in range(5):
        cid = trace_action_start(f"op{i}")
        cids.add(cid)
        trace_action_end(f"op{i}", cid, "success", 10)
    events = tc.export_recent()
    starts = [e for e in events if e['type']=='ACTION_START']
    ends = [e for e in events if e['type']=='ACTION_END']
    assert len(starts)==5 and len(ends)==5
    # Correlation pairing
    start_ids = sorted(e['correlation_id'] for e in starts)
    end_ids = sorted(e['correlation_id'] for e in ends)
    assert start_ids == end_ids
    assert len(cids) == 5  # uniqueness


def test_selection_diff_meta():
    tc = get_trace_center(); tc.clear()
    state = SelectionState()
    state.update_selection('files', ['a','b'])
    state.update_selection('files', ['b','c'])  # added c, removed a
    events = [e for e in tc.export_recent() if e['type']=='SELECTION']
    assert len(events) == 2
    first, second = events
    # First event should show both a and b added
    assert set(first['meta']['added'])=={'a','b'} and first['meta']['removed']==[]
    assert set(second['meta']['added'])=={'c'} and set(second['meta']['removed'])=={'a'}


def test_busy_indicator_context_manager():
    tc = get_trace_center(); tc.clear()
    busy = get_busy_indicator()
    # ensure clean
    while busy.is_busy():
        busy.stop()
    with busy.active():
        assert busy.is_busy()
    assert not busy.is_busy()
