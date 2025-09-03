import asyncio

from flet_server_gui.services.notification_center import NotificationCenter
from flet_server_gui.services.busy_indicator import get_busy_indicator
from flet_server_gui.services.confirmation_service import ConfirmationService
from flet_server_gui.state.selection_state import SelectionState
from flet_server_gui.components.adaptive_columns import AdaptiveColumnManager, ColumnSpec
from flet_server_gui.utils.action_result import ActionResult


class DummyDialogSystem:
    def __init__(self, confirm=True):
        self._confirm = confirm
    async def show_confirmation_async(self, title: str, message: str):  # mimic real signature
        return self._confirm


def test_notification_center_publish_subscribe():
    nc = NotificationCenter()
    received = []
    def handler(result: ActionResult):
        received.append(result.code)
    nc.subscribe(handler)
    ar = ActionResult.make_success(code="TEST_OK", message="done", correlation_id="cid1")
    nc.publish(ar)
    assert received == ["TEST_OK"]


def test_busy_indicator_refcount():
    bi = get_busy_indicator()
    assert not bi.is_busy()
    token1 = bi.start()  # Start busy indicator
    assert bi.is_busy()
    token2 = bi.start()  # Start another busy indicator
    assert bi.is_busy()
    bi.stop()  # Stop busy indicator without token
    assert bi.is_busy()  # still busy due to token2
    bi.stop()  # Stop busy indicator without token
    assert not bi.is_busy()


def test_confirmation_service_proceed_cancel():
    # proceed path
    ds_yes = DummyDialogSystem(confirm=True)
    cs_yes = ConfirmationService(ds_yes)
    r_yes = asyncio.run(cs_yes.confirm(title="T", message="M", proceed_code="X_START", proceed_message="go", cancel_message="no"))
    assert r_yes.code == "X_START"
    # cancel path
    ds_no = DummyDialogSystem(confirm=False)
    cs_no = ConfirmationService(ds_no)
    r_no = asyncio.run(cs_no.confirm(title="T", message="M", proceed_code="X_START", proceed_message="go", cancel_message="no"))
    assert r_no.code == "CANCELLED"


def test_selection_state_basic():
    ss = SelectionState()
    events = []
    def listener(table, ids):
        events.append((table, tuple(ids)))
    ss.subscribe("files", listener)
    ss.update_selection("files", ["a","b"])  # set
    ss.update_selection("files", ["b","c"])  # change
    ss.clear("files")  # clear
    assert events[0][1] == ("a","b")
    assert events[1][1] == ("b","c")
    assert events[2][1] == tuple()


def test_adaptive_column_manager():
    mgr = AdaptiveColumnManager([
        ColumnSpec(id="id", title="ID", min_width=100, priority=1),
        ColumnSpec(id="name", title="Name", min_width=120, priority=2),
        ColumnSpec(id="status", title="Status", min_width=160, priority=3),
    ])
    # enough width -> all
    vis_all = mgr.compute_visible(600)
    assert {c.id for c in vis_all} == {"id","name","status"}
    # restricted width -> drop highest priority number first (status)
    vis_small = mgr.compute_visible(250)
    ids_small = [c.id for c in vis_small]
    assert "status" not in ids_small and "id" in ids_small
