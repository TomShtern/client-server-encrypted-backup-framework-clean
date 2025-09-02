#!/usr/bin/env python3
"""
Quick Actions Component
Material Design 3 component with shortcut buttons for common server operations.
"""

import flet as ft
from typing import Callable, Optional
from flet_server_gui.components.enhanced_components import (
    create_enhanced_button,
    create_enhanced_icon_button,
    EnhancedCard
)


class QuickActions(EnhancedCard):
    """Quick actions component with shortcut buttons for common operations"""
    
    def __init__(self, 
                 page: ft.Page,
                 on_backup_now: Optional[Callable] = None,
                 on_clear_logs: Optional[Callable] = None,
                 on_restart_services: Optional[Callable] = None,
                 on_view_clients: Optional[Callable] = None,
                 on_manage_files: Optional[Callable] = None,
                 animate_duration: int = 200,
                 **kwargs):
        self.page = page
        self.on_backup_now = on_backup_now
        self.on_clear_logs = on_clear_logs
        self.on_restart_services = on_restart_services
        self.on_view_clients = on_view_clients
        self.on_manage_files = on_manage_files
        
        # Create the main content
        content = self._build_content()
        
        super().__init__(
            content=content,
            animate_duration=animate_duration,
            **kwargs
        )
    
    def _build_content(self) -> ft.Control:
        """Build the quick actions content"""
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.FLASH_ON, size=24),
            ft.Text("Quick Actions", style=ft.TextThemeStyle.TITLE_LARGE),
        ], spacing=12)
        
        # Action buttons grid
        actions_grid = ft.ResponsiveRow([
            # Row 1
            ft.Column([
                create_enhanced_button(
                    text="Backup Now",
                    icon=ft.Icons.CLOUD_UPLOAD,
                    on_click=self._on_backup_now,
                    width=180
                )
            ], col={"sm": 6, "md": 4}),
            
            ft.Column([
                create_enhanced_button(
                    text="Clear Logs",
                    icon=ft.Icons.CLEAR_ALL,
                    on_click=self._on_clear_logs,
                    width=180
                )
            ], col={"sm": 6, "md": 4}),
            
            ft.Column([
                create_enhanced_button(
                    text="Restart Services",
                    icon=ft.Icons.RESTART_ALT,
                    on_click=self._on_restart_services,
                    width=180
                )
            ], col={"sm": 6, "md": 4}),
            
            # Row 2
            ft.Column([
                create_enhanced_button(
                    text="View Clients",
                    icon=ft.Icons.PEOPLE,
                    on_click=self._on_view_clients,
                    width=180
                )
            ], col={"sm": 6, "md": 4}),
            
            ft.Column([
                create_enhanced_button(
                    text="Manage Files",
                    icon=ft.Icons.FOLDER,
                    on_click=self._on_manage_files,
                    width=180
                )
            ], col={"sm": 6, "md": 4}),
            
            ft.Column([
                create_enhanced_button(
                    text="Settings",
                    icon=ft.Icons.SETTINGS,
                    on_click=self._on_settings,
                    width=180
                )
            ], col={"sm": 6, "md": 4}),
        ], spacing=16)
        
        return ft.Container(
            content=ft.Column([
                header,
                ft.Divider(),
                actions_grid
            ], spacing=16),
            padding=ft.padding.all(20)
        )
    
    def _on_backup_now(self, e):
        """Handle backup now action"""
        if self.on_backup_now:
            # Show confirmation dialog using DialogSystem
            from flet_server_gui.ui.dialogs import DialogSystem
            dialog_system = DialogSystem(self.page)
            dialog_system.show_confirmation_dialog(
                title="Start Backup",
                message="Are you sure you want to start a backup now?",
                on_confirm=lambda: self.on_backup_now(e),
                on_cancel=None
            )
    
    def _on_clear_logs(self, e):
        """Handle clear logs action"""
        if self.on_clear_logs:
            # Show confirmation dialog using DialogSystem
            from flet_server_gui.ui.dialogs import DialogSystem
            dialog_system = DialogSystem(self.page)
            dialog_system.show_confirmation_dialog(
                title="Clear Logs",
                message="Are you sure you want to clear all logs?",
                on_confirm=lambda: self.on_clear_logs(e),
                on_cancel=None
            )
    
    def _on_restart_services(self, e):
        """Handle restart services action"""
        if self.on_restart_services:
            # Show confirmation dialog using DialogSystem
            from flet_server_gui.ui.dialogs import DialogSystem
            dialog_system = DialogSystem(self.page)
            dialog_system.show_confirmation_dialog(
                title="Restart Services",
                message="Are you sure you want to restart all services?",
                on_confirm=lambda: self.on_restart_services(e),
                on_cancel=None
            )
    
    def _on_view_clients(self, e):
        """Handle view clients action"""
        if self.on_view_clients:
            self.on_view_clients(e)
    
    def _on_manage_files(self, e):
        """Handle manage files action"""
        if self.on_manage_files:
            self.on_manage_files(e)
    
    def _on_settings(self, e):
        """Handle settings action"""
        # Show settings dialog using ToastManager
        from flet_server_gui.managers.toast_manager import ToastManager
        toast_manager = ToastManager(self.page)
        toast_manager.show_info("Settings dialog would open here")


# Factory function
def create_quick_actions(**kwargs) -> QuickActions:
    """Create quick actions component"""
    return QuickActions(**kwargs)