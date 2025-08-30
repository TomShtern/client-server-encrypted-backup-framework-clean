"""Central Confirmation Service

Provides standard confirmation flow returning unified ActionResult (cancelled or proceed token).
"""
from __future__ import annotations
from typing import Optional
from flet_server_gui.utils.action_result import ActionResult
from flet_server_gui.utils.trace_center import get_trace_center

class ConfirmationService:
    def __init__(self, dialog_system):
        self.dialog_system = dialog_system

    async def confirm(self, *, title: str, message: str, proceed_code: str, proceed_message: str, cancel_message: str = "Cancelled"):
        cid = get_trace_center().new_correlation_id()
        if not self.dialog_system:
            return ActionResult.make_info(code=proceed_code, message=proceed_message, correlation_id=cid)
        confirmed = await self.dialog_system.show_confirmation_async(title=title, message=message)
        if confirmed:
            return ActionResult.make_info(code=proceed_code, message=proceed_message, correlation_id=cid)
        return ActionResult.make_cancelled(correlation_id=cid, message=cancel_message)
