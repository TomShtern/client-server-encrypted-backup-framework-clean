import asyncio
import sys
from pathlib import Path

# Ensure project root on sys.path for flet_server_gui package
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flet_server_gui.utils.trace_center import get_trace_center
from flet_server_gui.utils.action_result import ActionResult
from flet_server_gui.utils.action_executor import get_action_executor

# NOTE: This is a lightweight integration-like test focusing on the ActionExecutor
# wiring rather than full Flet UI event loop. We directly invoke _handle_button_click
# via the executor to simulate several button actions and then assert trace events.

# We assume TraceCenter already initialized; ensure file logging target directory exists.

def test_multiple_button_actions_trace_capture(monkeypatch):
    trace = get_trace_center()
    # Start with a clean in-memory buffer using public API
    trace.clear()

    # Prepare dummy async actions
    async def ok_action():
        await asyncio.sleep(0)
        return ActionResult.success(code="OK", message="done")

    async def warn_action():
        await asyncio.sleep(0)
        return ActionResult.warn(code="WARN", message="caution")

    async def error_action():
        await asyncio.sleep(0)
        raise RuntimeError("boom")

    execu = get_action_executor()

    async def run_all():
        await execu.run(action_name="ok_btn", action_coro=ok_action)
        await execu.run(action_name="warn_btn", action_coro=warn_action)
        await execu.run(action_name="err_btn", action_coro=error_action)

    asyncio.run(run_all())

    events = [e for e in trace.export_recent(limit=100) if e["type"] in {"ACTION_START", "ACTION_END", "ACTION_ERROR"}]
    # We expect at least one start per action and an error for the failing action
    starts = [e for e in events if e["type"] == "ACTION_START"]
    assert len(starts) >= 3, "Expected three ACTION_START events"
    assert any(e["type"] == "ACTION_ERROR" for e in events), "Missing error event"
