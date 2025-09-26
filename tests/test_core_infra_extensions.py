from flet_server_gui.utils.action_result import ActionResult, timed_execution
from flet_server_gui.utils.trace_center import TraceCenter, get_trace_center


def test_action_result_factories_basic():
    cid = get_trace_center().new_correlation_id()
    r1 = ActionResult.make_success(code="FILE_SAVED", message="Saved", correlation_id=cid)
    r2 = ActionResult.make_error(code="E_FAIL", message="Boom", correlation_id=cid, error_code="E_FAIL")
    r3 = ActionResult.make_warn(code="EDGE", message="Warned", correlation_id=cid)
    r4 = ActionResult.make_partial(code="PART", message="Partial", correlation_id=cid, failed=[{"id":1},{"id":2}])
    assert r1.success and r1.status == "success" and r1.severity == "success"
    assert not r2.success and r2.severity == "error" and r2.error_code == "E_FAIL"
    assert r3.status == "warn" and r3.severity == "warning"
    assert r4.meta.get("failed_count") == 2 and r4.status == "warn" and r4.severity == "warning"


def test_action_result_legacy_helpers():
    ok = ActionResult.success_result({"answer":42})
    err = ActionResult.error_result("nope", "X")
    assert ok.success and ok.data["answer"] == 42
    assert not err.success and err.error_code == "X"


def test_timed_execution_wraps_data():
    cid = get_trace_center().new_correlation_id()
    def work():
        return 5
    res = timed_execution(work, correlation_id=cid)
    assert res.success and res.duration_ms >= 0 and res.data["result"] == 5


def test_timed_execution_enriches_action_result():
    cid = get_trace_center().new_correlation_id()
    def work():
        return ActionResult.make_success(code="FAST", message="done", correlation_id=cid)
    res = timed_execution(work, correlation_id=cid)
    assert res.code == "FAST" and res.duration_ms >= 0


def test_trace_center_emit_and_filter():
    tc = get_trace_center()
    tc.clear()
    cid = tc.emit(type="TEST", level="INFO", message="hello", meta={"a":1})
    tc.emit(type="OTHER", level="DEBUG")
    filtered = tc.export_recent(filter_type="TEST")
    assert len(filtered) == 1 and filtered[0]["message"] == "hello"
    by_cid = tc.export_recent(correlation_id=cid)
    assert all(e["correlation_id"] == cid for e in by_cid)


def test_trace_center_ring_buffer_bounds():
    tc = TraceCenter.get()
    tc.clear()
    # push more than max default (600) to ensure trimming
    for i in range(650):
        tc.emit(type="SPAM", level="DEBUG", message=str(i))
    events = tc.export_recent(limit=1000)
    assert len(events) <= 600  # bounded
    assert events[-1]["message"] == "649"


def test_trace_center_meta_truncation(monkeypatch):
    tc = get_trace_center()
    tc.clear()
    huge = {"blob":"x" * 20000}
    cid = tc.emit(type="BIG", level="INFO", meta=huge)
    rec = tc.export_recent(correlation_id=cid)[0]
    assert rec["meta"] == {"truncated": True}


def test_retrying_and_cancelled():
    tc = get_trace_center()
    cid = tc.new_correlation_id()
    retry = ActionResult.make_retrying(code="RET", message="again", attempt=2, max_attempts=5, correlation_id=cid)
    cancel = ActionResult.make_cancelled(correlation_id=cid)
    assert retry.meta.get("attempt") == 2 and not retry.success and retry.status == "warn"
    assert cancel.code == "CANCELLED" and cancel.status == "warn"


def test_action_result_from_dict_roundtrip():
    original = ActionResult.make_success(code="ROUND", message="trip", correlation_id=get_trace_center().new_correlation_id(), data={"v":1})
    d = original.to_dict()
    clone = ActionResult.from_dict(d)
    assert clone.code == original.code and clone.data == original.data and clone.success
