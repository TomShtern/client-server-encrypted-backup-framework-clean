"""test_utils_phase1_smoke.py

Lightweight smoke tests for newly introduced Phase 1 utility modules:
- ActionResult creation & dict conversion
- TraceCenter emit / export behavior
- RuntimeContext initialization & offline toggle semantics
- ActionExecutor pipeline happy path, empty selection, offline mutation

These are *not* full pytest formal tests yet; they can be executed ad-hoc:
    python -m flet_server_gui.test_utils_phase1_smoke

They print succinct summaries to avoid log flood.
"""
from __future__ import annotations

import asyncio
from typing import List

from flet_server_gui.utils.action_result import ActionResult
from flet_server_gui.utils.trace_center import get_trace_center, trace_action_start, trace_action_end
from flet_server_gui.utils.runtime_context import get_runtime_context, set_offline_mode
from flet_server_gui.utils.action_executor import get_action_executor


def _print(header: str, value):  # Simple consistent output helper
    print(f"[SMOKE] {header}: {value}")


def test_action_result() -> None:
    ar = ActionResult.make_success("TEST_OK", "Worked", correlation_id="abc123", data={"x": 1})
    assert ar.status == "success"
    assert ar.to_dict()["code"] == "TEST_OK"
    _print("ActionResult", ar.to_dict())


def test_trace_center() -> None:
    tc = get_trace_center()
    cid = trace_action_start("demo")
    trace_action_end("demo", cid, "success", 5)
    recent = tc.export_recent(limit=5)
    assert any(ev["type"] == "ACTION_END" for ev in recent)
    _print("TraceEvents", recent[-2:])


def test_runtime_context() -> None:
    ctx = get_runtime_context()
    _print("RuntimeContext.initial", ctx)
    set_offline_mode(True)
    ctx2 = get_runtime_context()
    _print("RuntimeContext.after_toggle", ctx2)


async def _demo_action():
    return {"value": 42}


async def _demo_fail():
    raise RuntimeError("Boom")


async def _run_executor_cases():
    ex = get_action_executor()
    # Happy path
    res1 = await ex.run(action_name="demo", action_coro=_demo_action)
    _print("Executor.demo", res1.to_dict())
    # Error path
    res2 = await ex.run(action_name="demo_fail", action_coro=_demo_fail)
    _print("Executor.demo_fail", res2.to_dict())
    # Selection required path
    res3 = await ex.run(action_name="needs_selection", action_coro=_demo_action, require_selection=True, selection_provider=lambda: [])
    _print("Executor.no_selection", res3.to_dict())
    # Offline mutation no-op
    set_offline_mode(True)
    res4 = await ex.run(action_name="mutate_offline", action_coro=_demo_action, mutate=True)
    _print("Executor.mutate_offline", res4.to_dict())


def run_all() -> None:
    test_action_result()
    test_trace_center()
    test_runtime_context()
    asyncio.run(_run_executor_cases())
    print("[SMOKE] Completed Phase1 utility smoke tests")


if __name__ == "__main__":  # Manual execution
    run_all()
