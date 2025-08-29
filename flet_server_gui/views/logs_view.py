#!/usr/bin/env python3
"""
Logs View for Flet Server GUI
Real-time server log viewer with advanced filtering and management
"""

import flet as ft
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

# Existing imports
from flet_server_gui.services.log_service import LogService, LogEntry
from flet_server_gui.components.base_component import BaseComponent
from flet_server_gui.components.log_action_handlers import LogActionHandlers
from flet_server_gui.core.semantic_colors import get_status_color

# Enhanced components imports
from flet_server_gui.ui.widgets import (
    EnhancedButton,
    EnhancedCard,
    EnhancedTable,
    EnhancedWidget,
    EnhancedButtonConfig,
    ButtonVariant,
    CardVariant,
    TableSize,
    WidgetSize,
    WidgetType
)

# Layout fixes imports
from flet_server_gui.ui.layouts.responsive_fixes import ResponsiveLayoutFixes
# Unified theme system - consolidated theme functionality
from flet_server_gui.ui.unified_theme_system import ThemeConsistencyManager, TOKENS


logger = logging.getLogger(__name__)

class LogsView(BaseComponent):
    """
    Real-time log viewer with advanced filtering and search capabilities.
    NO mock data - displays actual server logs with live updates.
    """
    
    def __init__(self, page: ft.Page, dialog_system, toast_manager):
        """Initialize with real log service"""
        # Initialize parent BaseComponent
        super().__init__(page, dialog_system, toast_manager)
        
        # Initialize theme consistency manager
        self.theme_manager = ThemeConsistencyManager(page)
        
        self.page = page
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.log_service = LogService()
        self._ui_update_task = None
        
        # Flag to prevent callbacks during initialization
        self.initialized = False
        
        # Initialize action handlers
        self.action_handlers = LogActionHandlers(self.log_service, dialog_system, toast_manager, page)
        self.action_handlers.set_data_changed_callback(self._refresh_logs)
        self.action_handlers.parent_view = self
        
        # UI state
        self.auto_scroll = True
        self.filter_level = "ALL"
        self.filter_component = "ALL"
        self.search_query = ""
        self.max_displayed_logs = 500
        
        # UI components - Apply responsive layout fixes
        self.log_list = ft.ListView(spacing=2, padding=10, auto_scroll=True, expand=True)
        self.log_counter = ft.Text("0 entries", size=12)
        self.monitoring_status = ft.Text("●", color=get_status_color("error"), size=16)
        
        # Apply hitbox alignment fixes
        self.monitoring_status = ResponsiveLayoutFixes.fix_hitbox_alignment(self.monitoring_status)
        
        # Filter controls - Apply responsive layout fixes
        self.level_filter = ft.Dropdown(
            label="Level",
            value="ALL",
            options=[
                ft.dropdown.Option("ALL"),
                ft.dropdown.Option("DEBUG"),
                ft.dropdown.Option("INFO"),
                ft.dropdown.Option("WARNING"),
                ft.dropdown.Option("ERROR"),
                ft.dropdown.Option("CRITICAL")
            ],
            on_change=self._on_filter_changed,
            width=120
        )
        
        self.component_filter = ft.Dropdown(
            label="Component",
            value="ALL",
            options=[ft.dropdown.Option("ALL")],
            on_change=self._on_filter_changed,
            width=150
        )
        
        self.search_field = ft.TextField(
            label="Search logs",
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_changed,
            width=300
        )
        
        # Apply clipping fixes to filter controls
        self.level_filter = ResponsiveLayoutFixes.create_clipping_safe_container(
            self.level_filter
        )
        
        self.component_filter = ResponsiveLayoutFixes.create_clipping_safe_container(
            self.component_filter
        )
        
        self.search_field = ResponsiveLayoutFixes.create_clipping_safe_container(
            self.search_field
        )
        
        # Set initialized flag after everything is set up
        self.initialized = True
        
        logger.info("✅ Logs view initialized with real log service")

    def start(self):
        """Start log monitoring and UI updates."""
        if not self.log_service.monitoring_active:
            if self.log_service.start_monitoring():
                self.monitoring_status.color = get_status_color("success")
                self.monitoring_status.value = "●"
                if self._ui_update_task is None:
                    self._ui_update_task = self.page.run_task(self._ui_update_loop)
                self._refresh_logs(None)
            else:
                self.toast_manager.show_warning("No log files found for monitoring")

    def stop(self):
        """Stop log monitoring and UI updates."""
        self.log_service.stop_monitoring()
        if self._ui_update_task:
            self._ui_update_task.cancel()
            self._ui_update_task = None
        self.monitoring_status.color = get_status_color("error")

    def create_logs_view(self) -> ft.Container:
        """Create the main logs view with real-time updates"""
        
        # Controls bar
        controls_bar = ft.Row([
            ft.ElevatedButton(
                text="Start Monitoring" if not self.log_service.monitoring_active else "Stop Monitoring",
                icon=ft.Icons.PLAY_ARROW if not self.log_service.monitoring_active else ft.Icons.STOP,
                on_click=self._toggle_monitoring
            ),
            ft.VerticalDivider(width=1),
            self.level_filter,
            self.component_filter,
            self.search_field,
            ft.VerticalDivider(width=1),
            ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Refresh logs",
                on_click=self._refresh_logs
            ),
            ft.IconButton(
                icon=ft.Icons.CLEAR,
                tooltip="Clear display",
                on_click=self._clear_display
            ),
            ft.IconButton(
                icon=ft.Icons.DOWNLOAD,
                tooltip="Export logs",
                on_click=self._export_logs
            ),
            ft.Container(expand=1),
            ft.Row([
                self.monitoring_status,
                ft.Text("Live", size=12),
                ft.VerticalDivider(width=5),
                self.log_counter
            ])
        ])
        
        # Settings row
        settings_row = ft.Row([
            ft.Switch(
                label="Auto-scroll",
                value=self.auto_scroll,
                on_change=self._toggle_auto_scroll
            ),
            ft.TextField(
                label="Max entries",
                value=str(self.max_displayed_logs),
                width=120,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=self._on_max_entries_changed
            ),
            ft.Container(expand=1),
            ft.Text("Real-time server log monitoring", size=12, color=TOKENS['outline'])
        ])
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Server Logs",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=TOKENS['primary']
                ),
                ft.Text(
                    "Real-time server log monitoring and analysis",
                    size=14,
                    color=TOKENS['outline']
                ),
                ft.Divider(height=20),
                controls_bar,
                settings_row,
                ft.Divider(),
                ft.Container(
                    content=self.log_list,
                    # Let theme handle border color automatically,
                    border_radius=8,
                    expand=True
                )
            ]),
            padding=20,
            expand=True
        )
    
    async def _ui_update_loop(self):
        """Periodically fetch and display new log entries."""
        while True:
            try:
                if self.log_service.monitoring_active:
                    pending_updates = self.log_service.get_pending_updates()
                    if pending_updates:
                        self._process_pending_updates(pending_updates)
                    self._update_stats()
                await asyncio.sleep(1)  # Update every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in UI update loop: {e}")
                await asyncio.sleep(5)
    
    def _process_pending_updates(self, updates: List[LogEntry]):
        """Process pending log updates and update UI"""
        for entry in updates:
            if self._should_display_entry(entry):
                self._add_log_entry_to_ui(entry)
        
        if len(self.log_list.controls) > self.max_displayed_logs:
            excess = len(self.log_list.controls) - self.max_displayed_logs
            self.log_list.controls = self.log_list.controls[excess:]
        
        self.page.update()
    
    def _should_display_entry(self, entry: LogEntry) -> bool:
        """Check if log entry should be displayed based on current filters"""
        if self.filter_level != "ALL" and entry.level.upper() != self.filter_level:
            return False
        
        if self.filter_component != "ALL" and entry.component != self.filter_component:
            return False
        
        if self.search_query:
            query = self.search_query.lower()
            if (query not in entry.message.lower() and 
                query not in entry.component.lower()):
                return False
        
        return True
    
    def _add_log_entry_to_ui(self, entry: LogEntry):
        """Add a log entry to the UI list"""
        # Use semantic color system for log level colors
        level_color_map = {
            'DEBUG': "info",
            'INFO': "info",
            'WARNING': "warning",
            'ERROR': "error",
            'CRITICAL': "error"
        }
        semantic_level = level_color_map.get(entry.level.upper(), "neutral")
        level_color = get_status_color(semantic_level)
        time_str = entry.timestamp.strftime("%H:%M:%S")
        
        log_row = ft.Container(
            content=ft.Row([
                ft.Container(content=ft.Text(time_str, size=10), width=60),
                ft.Container(content=ft.Text(entry.level, size=10, weight=ft.FontWeight.BOLD), width=60),
                ft.Container(content=ft.Text(entry.component, size=10), width=80),
                ft.Expanded(child=ft.Text(entry.message, size=12, overflow=ft.TextOverflow.ELLIPSIS))
            ]),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=4,
            bgcolor=get_status_color("warning") if entry.level.upper() == 'WARNING' else get_status_color("error") if entry.level.upper() in ['ERROR', 'CRITICAL'] else None,
            data=entry.id
        )
        self.log_list.controls.append(log_row)
    
    def _toggle_monitoring(self, e):
        """Toggle log monitoring on/off"""
        if self.log_service.monitoring_active:
            self.stop()
            e.control.text = "Start Monitoring"
            e.control.icon = ft.Icons.PLAY_ARROW
            self.toast_manager.show_info("Log monitoring stopped")
        else:
            self.start()
            e.control.text = "Stop Monitoring"
            e.control.icon = ft.Icons.STOP
            self.toast_manager.show_success("Log monitoring started")
        self.page.update()
    
    def _refresh_logs(self, e):
        """Refresh the log display"""
        # Only refresh if the view is fully initialized
        if hasattr(self, 'initialized') and self.initialized:
            try:
                # Use page.run_task if available, otherwise check for event loop
                if hasattr(self.page, 'run_task'):
                    self.page.run_task(self.action_handlers.refresh_logs)
                else:
                    # Check if we're in an async context
                    try:
                        loop = asyncio.get_running_loop()
                        if loop.is_running():
                            asyncio.create_task(self.action_handlers.refresh_logs())
                    except RuntimeError:
                        # No event loop running, skip refresh
                        pass
            except Exception:
                # General exception handling
                pass
    
    def _update_component_filter(self, logs: List[LogEntry]):
        """Update component filter dropdown with available components"""
        components = set(["ALL"])
        for log in logs:
            components.add(log.component)
        
        self.component_filter.options = [ft.dropdown.Option(comp) for comp in sorted(components)]
        if self.component_filter.value not in components:
            self.component_filter.value = "ALL"
    
    def _update_stats(self):
        """Update log statistics display"""
        stats = self.log_service.get_log_stats()
        self.log_counter.value = f"{stats['total_entries']} total, {len(self.log_list.controls)} displayed"
    
    def _on_filter_changed(self, e):
        """Handle filter changes"""
        # Check if level_filter and component_filter are properly initialized
        if hasattr(self.level_filter, 'value'):
            self.filter_level = self.level_filter.value
        if hasattr(self.component_filter, 'value'):
            self.filter_component = self.component_filter.value
        self._refresh_logs(None)
    
    def _on_search_changed(self, e):
        """Handle search query changes"""
        self.search_query = self.search_field.value
        # Use page.run_task if available, otherwise check for event loop
        if hasattr(self.page, 'run_task'):
            self.page.run_task(self._delayed_search)
        else:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    asyncio.create_task(self._delayed_search())
            except RuntimeError:
                # No event loop running, skip operation
                pass
    
    async def _delayed_search(self):
        """Delayed search to avoid excessive updates"""
        await asyncio.sleep(0.5)
        self._refresh_logs(None)
    
    def _toggle_auto_scroll(self, e):
        """Toggle auto-scroll behavior"""
        self.auto_scroll = e.control.value
        self.log_list.auto_scroll = self.auto_scroll
        self.page.update()
    
    def _on_max_entries_changed(self, e):
        """Handle max entries limit change"""
        try:
            new_max = int(e.control.value)
            if 50 <= new_max <= 10000:
                self.max_displayed_logs = new_max
                self._refresh_logs(None)
            else:
                e.control.value = str(self.max_displayed_logs)
                self.toast_manager.show_warning("Max entries must be between 50 and 10000")
        except ValueError:
            e.control.value = str(self.max_displayed_logs)
            self.toast_manager.show_error("Invalid number for max entries")
        self.page.update()
    
    def _clear_display(self, e):
        """Clear the log display"""
        # Use page.run_task if available, otherwise check for event loop
        if hasattr(self.page, 'run_task'):
            self.page.run_task(self.action_handlers.clear_logs)
        else:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    asyncio.create_task(self.action_handlers.clear_logs())
            except RuntimeError:
                # No event loop running, skip operation
                pass
    
    def _export_logs(self, e):
        """Export logs to file"""
        # Use page.run_task if available, otherwise check for event loop
        if hasattr(self.page, 'run_task'):
            # Create a wrapper function to pass the parameters
            async def export_logs_wrapper():
                await self.action_handlers.export_logs(
                    self.filter_level, 
                    self.filter_component, 
                    self.search_query
                )
            self.page.run_task(export_logs_wrapper)
        else:
            # Check if we're in an async context
            try:
                loop = asyncio.get_running_loop()
                if loop.is_running():
                    asyncio.create_task(self.action_handlers.export_logs(
                        self.filter_level, 
                        self.filter_component, 
                        self.search_query
                    ))
            except RuntimeError:
                # No event loop running, skip operation
                pass
