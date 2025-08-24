"""
Logs View for Flet Server GUI
Real-time server log viewer with advanced filtering and management
"""

import flet as ft
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
from ..services.log_service import LogService, LogEntry

logger = logging.getLogger(__name__)

class LogsView:
    """
    Real-time log viewer with advanced filtering and search capabilities.
    NO mock data - displays actual server logs with live updates.
    """
    
    def __init__(self, page: ft.Page, dialog_system, toast_manager):
        """Initialize with real log service"""
        self.page = page
        self.dialog_system = dialog_system
        self.toast_manager = toast_manager
        self.log_service = LogService()
        
        # UI state
        self.auto_scroll = True
        self.filter_level = "ALL"
        self.filter_component = "ALL"
        self.search_query = ""
        self.max_displayed_logs = 500
        
        # UI components
        self.log_list = ft.ListView(spacing=2, padding=10, auto_scroll=True, expand=True)
        self.log_counter = ft.Text("0 entries", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        self.monitoring_status = ft.Text("●", color=ft.Colors.RED, size=16)
        
        # Filter controls
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
        
        # Defer monitoring start until page is ready
        # self._start_monitoring()
        
        logger.info("✅ Logs view initialized with real log service")
    
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
            ft.Text("Real-time server log monitoring", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
        ])
        
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Server Logs",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PRIMARY
                ),
                ft.Text(
                    "Real-time server log monitoring and analysis",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT
                ),
                ft.Divider(height=20),
                controls_bar,
                settings_row,
                ft.Divider(),
                ft.Container(
                    content=self.log_list,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=8,
                    expand=True
                )
            ]),
            padding=20,
            expand=True
        )
    
    def _start_monitoring(self):
        """Start log monitoring service"""
        if self.log_service.start_monitoring():
            self.monitoring_status.color = ft.Colors.GREEN
            self.monitoring_status.value = "●"
            
            # Add callback for real-time updates
            self.log_service.add_update_callback(self._on_log_update)
            
            # Load initial logs
            self._refresh_logs(None)
            
            # Start periodic UI updates
            self._schedule_ui_updates()
        else:
            self.monitoring_status.color = ft.Colors.RED
            self.monitoring_status.value = "●"
            self.toast_manager.show_warning("No log files found for monitoring")
    
    def _schedule_ui_updates(self):
        """Schedule periodic UI updates for real-time log display"""
        async def update_loop():
            while self.log_service.monitoring_active:
                try:
                    # Get pending updates
                    pending_updates = self.log_service.get_pending_updates()
                    if pending_updates:
                        self._process_pending_updates(pending_updates)
                    
                    # Update stats
                    self._update_stats()
                    
                    await asyncio.sleep(1)  # Update every second
                except Exception as e:
                    logger.error(f"❌ Error in UI update loop: {e}")
                    await asyncio.sleep(5)
        
        # Start the update loop
        # Use the page's event loop if available, otherwise create task
        try:
            if hasattr(self.page, 'session') and self.page.session:
                # We're in a page session, can create task directly
                asyncio.create_task(update_loop())
            else:
                # Defer task creation until event loop is available
                async def delayed_start():
                    await asyncio.sleep(0.1)  # Small delay to allow page setup
                    asyncio.create_task(update_loop())
                
                # Just run the loop directly for now to avoid event loop issues
                # asyncio.create_task(delayed_start())
                pass  # Skip auto-start for now to avoid event loop issues
        except RuntimeError:
            # No event loop running, defer task creation
            pass
    
    def _process_pending_updates(self, updates: List[LogEntry]):
        """Process pending log updates and update UI"""
        for entry in updates:
            if self._should_display_entry(entry):
                self._add_log_entry_to_ui(entry)
        
        # Limit displayed entries
        if len(self.log_list.controls) > self.max_displayed_logs:
            excess = len(self.log_list.controls) - self.max_displayed_logs
            self.log_list.controls = self.log_list.controls[excess:]
        
        # Update page
        self.page.update()
    
    def _should_display_entry(self, entry: LogEntry) -> bool:
        """Check if log entry should be displayed based on current filters"""
        # Level filter
        if self.filter_level != "ALL" and entry.level.upper() != self.filter_level:
            return False
        
        # Component filter
        if self.filter_component != "ALL" and entry.component != self.filter_component:
            return False
        
        # Search filter
        if self.search_query:
            query = self.search_query.lower()
            if (query not in entry.message.lower() and 
                query not in entry.component.lower()):
                return False
        
        return True
    
    def _add_log_entry_to_ui(self, entry: LogEntry):
        """Add a log entry to the UI list"""
        # Color based on log level
        level_colors = {
            'DEBUG': ft.Colors.BLUE_GREY,
            'INFO': ft.Colors.BLUE,
            'WARNING': ft.Colors.ORANGE,
            'ERROR': ft.Colors.RED,
            'CRITICAL': ft.Colors.PURPLE
        }
        
        level_color = level_colors.get(entry.level.upper(), ft.Colors.ON_SURFACE)
        
        # Format timestamp
        time_str = entry.timestamp.strftime("%H:%M:%S")
        
        log_row = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Text(time_str, size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                    width=60
                ),
                ft.Container(
                    content=ft.Text(
                        entry.level,
                        size=10,
                        color=level_color,
                        weight=ft.FontWeight.BOLD
                    ),
                    width=60
                ),
                ft.Container(
                    content=ft.Text(entry.component, size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                    width=80
                ),
                ft.Expanded(
                    child=ft.Text(
                        entry.message,
                        size=12,
                        color=ft.Colors.ON_SURFACE,
                        overflow=ft.TextOverflow.ELLIPSIS
                    )
                )
            ]),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_radius=4,
            bgcolor=ft.Colors.SURFACE_VARIANT if entry.level.upper() in ['WARNING', 'ERROR', 'CRITICAL'] else None,
            data=entry.id
        )
        
        self.log_list.controls.append(log_row)
    
    def _on_log_update(self, entry: LogEntry):
        """Callback for real-time log updates"""
        # This runs in a background thread, so we queue the update
        pass  # Actual processing happens in _schedule_ui_updates
    
    def _toggle_monitoring(self, e):
        """Toggle log monitoring on/off"""
        if self.log_service.monitoring_active:
            self.log_service.stop_monitoring()
            self.monitoring_status.color = ft.Colors.RED
            self.monitoring_status.value = "●"
            e.control.text = "Start Monitoring"
            e.control.icon = ft.icons.play_arrow
            self.toast_manager.show_info("Log monitoring stopped")
        else:
            if self.log_service.start_monitoring():
                self.monitoring_status.color = ft.Colors.GREEN
                self.monitoring_status.value = "●"
                e.control.text = "Stop Monitoring"
                e.control.icon = ft.icons.stop
                self.toast_manager.show_success("Log monitoring started")
                self._schedule_ui_updates()
            else:
                self.toast_manager.show_error("Failed to start log monitoring")
        
        self.page.update()
    
    def _refresh_logs(self, e):
        """Refresh the log display"""
        try:
            # Clear current display
            self.log_list.controls.clear()
            
            # Get recent logs
            recent_logs = self.log_service.get_recent_logs(limit=self.max_displayed_logs)
            
            # Update component filter options
            self._update_component_filter(recent_logs)
            
            # Add filtered logs to UI
            displayed_count = 0
            for entry in reversed(recent_logs):  # Show newest first
                if self._should_display_entry(entry):
                    self._add_log_entry_to_ui(entry)
                    displayed_count += 1
            
            self._update_stats()
            self.page.update()
            
            logger.info(f"✅ Logs refreshed - displaying {displayed_count} entries")
            
        except Exception as e:
            logger.error(f"❌ Error refreshing logs: {e}")
            self.toast_manager.show_error("Failed to refresh logs")
    
    def _update_component_filter(self, logs: List[LogEntry]):
        """Update component filter dropdown with available components"""
        components = set(["ALL"])
        for log in logs:
            components.add(log.component)
        
        # Update dropdown options
        self.component_filter.options = [
            ft.dropdown.Option(comp) for comp in sorted(components)
        ]
        
        # Reset to ALL if current selection no longer exists
        if self.component_filter.value not in components:
            self.component_filter.value = "ALL"
    
    def _update_stats(self):
        """Update log statistics display"""
        stats = self.log_service.get_log_stats()
        self.log_counter.value = f"{stats['total_entries']} total, {len(self.log_list.controls)} displayed"
    
    def _on_filter_changed(self, e):
        """Handle filter changes"""
        self.filter_level = self.level_filter.value
        self.filter_component = self.component_filter.value
        self._refresh_logs(None)
    
    def _on_search_changed(self, e):
        """Handle search query changes"""
        self.search_query = self.search_field.value
        # Add small delay to avoid excessive updates
        self.page.run_task(self._delayed_search)
    
    async def _delayed_search(self):
        """Delayed search to avoid excessive updates"""
        await asyncio.sleep(0.5)  # 500ms delay
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
        self.log_list.controls.clear()
        self.log_counter.value = "0 entries displayed"
        self.page.update()
        self.toast_manager.show_info("Log display cleared")
    
    def _export_logs(self, e):
        """Export logs to file"""
        try:
            # Simple filename - could be enhanced with file picker
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"server_logs_export_{timestamp}.txt"
            
            # Get current logs based on filters
            logs = self.log_service.get_recent_logs()
            filtered_logs = [log for log in logs if self._should_display_entry(log)]
            
            # Export filtered logs
            if filtered_logs:
                # Write to file manually to include filter info
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"# Server Logs Export - {datetime.now().isoformat()}\n")
                    f.write(f"# Filters: Level={self.filter_level}, Component={self.filter_component}\n")
                    f.write(f"# Search: {self.search_query or 'None'}\n")
                    f.write(f"# Total entries: {len(filtered_logs)}\n\n")
                    
                    for entry in sorted(filtered_logs, key=lambda x: x.timestamp):
                        f.write(f"{entry.timestamp.isoformat()} - {entry.level} - {entry.component} - {entry.message}\n")
                
                self.dialog_system.show_success_dialog(
                    title="Export Successful",
                    message=f"Logs exported to {filename}\n{len(filtered_logs)} entries exported"
                )
                logger.info(f"✅ Logs exported to {filename}")
            else:
                self.toast_manager.show_warning("No logs to export with current filters")
                
        except Exception as e:
            logger.error(f"❌ Error exporting logs: {e}")
            self.dialog_system.show_error_dialog(
                title="Export Failed",
                message="An error occurred while exporting logs. Check logs for details."
            )