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

logger = logging.getLogger(__name__)


class LogActionHandlers:
    """Handles all log-related actions and operations"""
    
    def __init__(self, log_service: LogService, dialog_system, toast_manager, page: ft.Page):
        self.log_service = log_service
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.page = page
        
        # Callbacks for parent component
        self.on_data_changed: Optional[Callable] = None
    
    def set_data_changed_callback(self, callback: Callable):
        """Set callback for when data changes and refresh is needed"""
        self.on_data_changed = callback
        self.callback_initialized = True
    
    async def export_logs(self, filter_level: str = "ALL", filter_component: str = "ALL", search_query: str = "") -> bool:
        """Export logs with confirmation"""
        def confirm_export():
            self._close_dialog()
            # Use page.run_task if available, otherwise check for event loop
            if hasattr(self.page, 'run_task'):
                # Create a wrapper function to pass the parameters
                async def perform_export_wrapper():
                    await self._perform_export(filter_level, filter_component, search_query)
                self.page.run_task(perform_export_wrapper)
            else:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_export(filter_level, filter_component, search_query))
                except RuntimeError:
                    # No event loop running, skip async task creation
                    pass
        
        # Show confirmation dialog
        if self.dialog_system:
            confirmed = await self.dialog_system.show_confirmation_async(
                title="Confirm Log Export",
                message="Are you sure you want to export the logs? This will create a text file with the current log entries."
            )
            if confirmed:
                confirm_export()
        else:
            confirm_export()
    
    async def _perform_export(self, filter_level: str, filter_component: str, search_query: str) -> bool:
        """Actually perform the log export"""
        try:
            # Show progress dialog
            self.dialog_system.show_info_dialog(
                title="Exporting Logs",
                message="Exporting logs to file..."
            )
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"server_logs_export_{timestamp}.txt"
            logs = self.log_service.get_recent_logs()
            
            # Apply filters
            filtered_logs = logs
            if filter_level != "ALL":
                filtered_logs = [log for log in filtered_logs if log.level == filter_level]
            if filter_component != "ALL":
                filtered_logs = [log for log in filtered_logs if log.component == filter_component]
            if search_query:
                filtered_logs = [log for log in filtered_logs if search_query.lower() in log.message.lower()]
            
            if filtered_logs:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# Server Logs Export - {datetime.now().isoformat()}\\n")
                    f.write(f"# Filters: Level={filter_level}, Component={filter_component}\\n")
                    f.write(f"# Search: {search_query or 'None'}\\n")
                    f.write(f"# Total entries: {len(filtered_logs)}\\n\\n")
                    for entry in sorted(filtered_logs, key=lambda x: x.timestamp):
                        f.write(f"{entry.timestamp.isoformat()} - {entry.level} - {entry.component} - {entry.message}\\n")
                
                # Close progress dialog
                self._close_dialog()
                
                self.toast_manager.show_success(f"Logs exported to {filename}")
                logger.info(f"✅ Logs exported to {filename}")
                return True
            else:
                # Close progress dialog
                self._close_dialog()
                
                self.toast_manager.show_warning("No logs to export with current filters")
                return False
                
        except Exception as e:
            # Close progress dialog
            self._close_dialog()
            
            logger.error(f"❌ Error exporting logs: {e}")
            self.toast_manager.show_error(f"Error exporting logs: {str(e)}")
            return False
    
    async def clear_logs(self) -> bool:
        """Clear logs with confirmation"""
        def confirm_clear():
            self._close_dialog()
            # Use page.run_task if available, otherwise check for event loop
            if hasattr(self.page, 'run_task'):
                self.page.run_task(self._perform_clear)
            else:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        asyncio.create_task(self._perform_clear())
                except RuntimeError:
                    # No event loop running, skip async task creation
                    pass
        
        # Show confirmation dialog
        if self.dialog_system:
            confirmed = await self.dialog_system.show_confirmation_async(
                title="Confirm Clear Logs",
                message="Are you sure you want to clear the log display? This will remove all currently displayed logs but will not affect the actual log files."
            )
            if confirmed:
                confirm_clear()
        else:
            confirm_clear()
    
    async def _perform_clear(self) -> bool:
        """Actually perform the log clear"""
        try:
            # Clear the UI display
            if hasattr(self, 'parent_view') and hasattr(self.parent_view, 'log_list'):
                self.parent_view.log_list.controls.clear()
                self.parent_view.log_list.update()
            
            self.toast_manager.show_success("Log display cleared")
            return True
            
        except Exception as e:
            self.toast_manager.show_error(f"Error clearing logs: {str(e)}")
            return False
    
    async def refresh_logs(self) -> bool:
        """Refresh log view"""
        try:
            if self.on_data_changed:
                await self.on_data_changed()
            self.toast_manager.show_success("Logs refreshed")
            return True
        except Exception as e:
            self.toast_manager.show_error(f"Refresh failed: {str(e)}")
            return False
    
    def _close_dialog(self):
        """Close the current dialog"""
        if self.dialog_system and hasattr(self.dialog_system, 'current_dialog'):
            if self.dialog_system.current_dialog:
                self.dialog_system.current_dialog.open = False
                self.page.update()
