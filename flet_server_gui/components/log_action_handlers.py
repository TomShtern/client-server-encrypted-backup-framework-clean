#!/usr/bin/env python3
"""
Log Action Handlers Component
Handles all log-related actions including export, clear, and filtering operations.
"""

import flet as ft
import asyncio
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from ..services.log_service import LogService, LogEntry
from ..utils.action_result import ActionResult
from ..utils.trace_center import get_trace_center
from ..actions import LogActions
from .base_action_handler import BaseActionHandler, UIActionMixin

logger = logging.getLogger(__name__)


class LogActionHandlers(BaseActionHandler, UIActionMixin):
    """Handles all log-related actions and operations"""
    
    def __init__(self, log_service: LogService, dialog_system, toast_manager, page: ft.Page):
        # Initialize base handler with common dependencies
        super().__init__(log_service, dialog_system, toast_manager, page)
        
        # Initialize log actions
        self.log_service = log_service
        self.log_actions = LogActions(log_service)
    
    async def export_logs(self, filter_level: str = "ALL", filter_component: str = "ALL", search_query: str = "") -> ActionResult:
        """Export logs with confirmation."""
        return await self.execute_action(
            action_name="Export Logs",
            action_coro=self.log_actions.export_logs(filter_level, filter_component, search_query),
            confirmation_text="Are you sure you want to export the logs? This will create a text file with the current log entries.",
            confirmation_title="Confirm Log Export",
            require_selection=False,
            trigger_data_change=False,
            success_message="Logs exported successfully"
        )
    
    async def clear_logs(self) -> ActionResult:
        """Clear logs with confirmation."""
        return await self.execute_action(
            action_name="Clear Logs",
            action_coro=self.log_actions.clear_logs(),
            confirmation_text="Are you sure you want to clear the log display? This will remove all currently displayed logs but will not affect the actual log files.",
            confirmation_title="Confirm Clear Logs", 
            require_selection=False,
            trigger_data_change=True,
            success_message="Log display cleared"
        )
    
    async def refresh_logs(self) -> ActionResult:
        """Refresh log view"""
        return await self.execute_action(
            action_name="Refresh Logs",
            action_coro=self._refresh_logs_action(),
            require_selection=False,
            trigger_data_change=True,
            success_message="Logs refreshed"
        )
    
    async def _refresh_logs_action(self):
        """Action implementation for refreshing logs"""
        # No actual backend operation needed, just trigger data refresh
        return {"refreshed": True}
    
    async def filter_logs(self, filter_level: str = "ALL", filter_component: str = "ALL", search_query: str = "") -> ActionResult:
        """Filter logs by level, component, and search query"""
        return await self.execute_action(
            action_name="Filter Logs",
            action_coro=self.log_actions.filter_logs(filter_level, filter_component, search_query),
            require_selection=False,
            trigger_data_change=True,
            success_message="Logs filtered successfully"
        )
    
    async def search_logs(self, search_query: str) -> ActionResult:
        """Search logs by query"""
        return await self.execute_action(
            action_name="Search Logs",
            action_coro=self.log_actions.search_logs(search_query),
            require_selection=False,
            trigger_data_change=True,
            success_message="Log search completed"
        )
