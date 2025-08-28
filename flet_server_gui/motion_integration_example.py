#!/usr/bin/env python3
"""
Motion System Integration Example
Shows how to integrate M3 Motion System with existing Flet GUI components.
"""

import flet as ft
import asyncio
from typing import Optional
from .ui.theme_m3 import TOKENS

# Import the motion system
from flet_server_gui.ui.motion_system import (
    M3MotionSystem,
    M3Duration,
    M3EasingCurves,
    M3MotionTokens,
    create_motion_system
)

# Import existing components (examples)
try:
    from flet_server_gui.ui.widgets.cards import ServerStatusCard, ClientStatsCard
    from flet_server_gui.ui.widgets.buttons import ActionButtonFactory
    from flet_server_gui.ui.theme import ThemeManager
    HAS_COMPONENTS = True
except ImportError:
    HAS_COMPONENTS = False
    print("[INFO] Some components not available - using mock components")


class MotionEnabledDashboard:
    """
    Example dashboard with Motion System integration.
    Shows how to enhance existing components with M3 animations.
    """
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.motion_system = create_motion_system(page)
        
        # Initialize theme
        if HAS_COMPONENTS:
            self.theme_manager = ThemeManager(page)
            self.theme_manager.apply_theme()
        
        # Dashboard components
        self.server_card = None
        self.client_cards = []
        self.action_buttons = []
        self.notification_area = None
        
    def create_enhanced_dashboard(self) -> ft.Control:
        """Create a dashboard with motion-enhanced components."""
        
        # Header with animated title
        header = self._create_animated_header()
        
        # Status cards with hover effects
        status_row = self._create_status_cards()
        
        # Action buttons with press feedback
        actions_section = self._create_action_buttons()
        
        # Activity log with smooth updates
        activity_section = self._create_activity_log()
        
        # Notification area for toasts
        self.notification_area = ft.Container(height=100)  # Space for notifications
        
        # Main layout
        main_content = ft.Column([
            header,
            ft.Divider(height=20),
            status_row,
            ft.Divider(height=20),
            actions_section,
            ft.Divider(height=20),
            activity_section,
            self.notification_area
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO
        )
        
        # Apply initial entrance animation to the whole dashboard
        self.motion_system.fade_in(main_content, duration=M3Duration.LONG1)
        
        return ft.Container(
            content=main_content,
            padding=20,
            expand=True
        )
    
    def _create_animated_header(self) -> ft.Control:
        """Create header with animated elements."""
        
        # Title with typewriter effect simulation
        title = ft.Text(
            "Enhanced Server Dashboard",
            style=ft.TextThemeStyle.HEADLINE_LARGE,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        # Status indicator that pulses
        status_indicator = ft.Row([
            ft.Icon(ft.Icons.CIRCLE, color=TOKENS["secondary"], size=12),
            ft.Text("System Online", style=ft.TextThemeStyle.BODY_SMALL)
        ], spacing=5, alignment=ft.MainAxisAlignment.CENTER)
        
        # Apply subtle pulse animation to status
        async def pulse_status():
            while True:
                try:
                    self.motion_system.success_pulse(status_indicator)
                    await asyncio.sleep(5)  # Pulse every 5 seconds
                except Exception:
                    break
        
        # Start pulsing in background
        asyncio.create_task(pulse_status())
        
        # Animated slide-in for header elements
        self.motion_system.slide_down(title, duration=M3Duration.MEDIUM4)
        
        return ft.Column([title, status_indicator], 
                        alignment=ft.MainAxisAlignment.CENTER, spacing=10)
    
    def _create_status_cards(self) -> ft.Control:
        """Create status cards with hover effects."""
        
        # Mock server status card
        server_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.SERVER, size=24, color=TOKENS["primary"]),
                        ft.Text("Server Status", style=ft.TextThemeStyle.TITLE_MEDIUM)
                    ], spacing=10),
                    ft.Text("Running", style=ft.TextThemeStyle.BODY_LARGE, 
                           color=TOKENS["secondary"]),
                    ft.Text("Port 1256 ג€¢ 5 connections", 
                           style=ft.TextThemeStyle.BODY_SMALL)
                ], spacing=8),
                padding=16,
                width=200
            ),
            elevation=2
        )
        
        # Mock client stats card
        client_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.DEVICES, size=24, color=TOKENS["secondary"]),
                        ft.Text("Active Clients", style=ft.TextThemeStyle.TITLE_MEDIUM)
                    ], spacing=10),
                    ft.Text("17", style=ft.TextThemeStyle.HEADLINE_MEDIUM, 
                           color=TOKENS["primary"]),
                    ft.Text("Last activity: 2 min ago", 
                           style=ft.TextThemeStyle.BODY_SMALL)
                ], spacing=8),
                padding=16,
                width=200
            ),
            elevation=2
        )
        
        # Mock files card
        files_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.FOLDER, size=24, color=TOKENS["tertiary"]),
                        ft.Text("Files Processed", style=ft.TextThemeStyle.TITLE_MEDIUM)
                    ], spacing=10),
                    ft.Text("1,247", style=ft.TextThemeStyle.HEADLINE_MEDIUM,
                           color=TOKENS["primary"]),
                    ft.Text("Total size: 2.3 GB", 
                           style=ft.TextThemeStyle.BODY_SMALL)
                ], spacing=8),
                padding=16,
                width=200
            ),
            elevation=2
        )
        
        cards = [server_card, client_card, files_card]
        self.client_cards = cards
        
        # Apply hover effects to all cards
        for card in cards:
            self.motion_system.card_hover_effect(
                card, 
                elevation_increase=3,
                scale_factor=1.02
            )
        
        # Staggered entrance animation
        self.motion_system.list_item_interactions(
            cards,
            stagger_delay=100,
            entrance_direction="up"
        )
        
        return ft.ResponsiveRow([
            ft.Column([card], col={"sm": 12, "md": 4}, expand=True) 
            for card in cards
        ])
    
    def _create_action_buttons(self) -> ft.Control:
        """Create action buttons with motion feedback."""
        
        # Action buttons with different styles
        start_button = ft.FilledButton(
            text="Start Server",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_start_server,
            style=ft.ButtonStyle(bgcolor=TOKENS["secondary"])
        )
        
        stop_button = ft.FilledButton(
            text="Stop Server",
            icon=ft.Icons.STOP,
            on_click=self._on_stop_server,
            style=ft.ButtonStyle(bgcolor=TOKENS["error"])
        )
        
        restart_button = ft.OutlinedButton(
            text="Restart",
            icon=ft.Icons.REFRESH,
            on_click=self._on_restart_server
        )
        
        settings_button = ft.TextButton(
            text="Settings",
            icon=ft.Icons.SETTINGS,
            on_click=self._on_open_settings
        )
        
        buttons = [start_button, stop_button, restart_button, settings_button]
        self.action_buttons = buttons
        
        # Apply motion effects to buttons
        for button in buttons:
            self.motion_system.button_press_feedback(button)
            self.motion_system.button_hover_effect(button, scale_factor=1.05)
        
        return ft.Column([
            ft.Text("Server Controls", style=ft.TextThemeStyle.TITLE_SMALL),
            ft.Row(buttons, alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        ], spacing=10)
    
    def _create_activity_log(self) -> ft.Control:
        """Create activity log with smooth item additions."""
        
        # Initial log entries
        log_entries = [
            ("System", "Server started successfully", "success"),
            ("Client", "New client connected: 192.168.1.100", "info"),
            ("File", "backup_data.zip processed (2.1 MB)", "info"),
            ("System", "Database cleanup completed", "success"),
        ]
        
        # Create log items
        log_items = []
        for source, message, level in log_entries:
            icon_map = {
                "success": (ft.Icons.CHECK_CIRCLE, TOKENS["secondary"]),
                "info": (ft.Icons.INFO, TOKENS["primary"]),
                "error": (ft.Icons.ERROR, TOKENS["error"]),
                "warning": (ft.Icons.WARNING, TOKENS["secondary"])
            }
            
            icon, color = icon_map.get(level, (ft.Icons.INFO, TOKENS["primary"]))
            
            log_item = ft.ListTile(
                leading=ft.Icon(icon, color=color, size=16),
                title=ft.Text(f"[{source}] {message}", 
                             style=ft.TextThemeStyle.BODY_SMALL),
                dense=True
            )
            log_items.append(log_item)
        
        # Log container
        log_container = ft.Container(
            content=ft.Column(
                controls=log_items,
                spacing=2,
                scroll=ft.ScrollMode.AUTO
            ),
            height=200,
            border=ft.border.all(1, TOKENS['outline']),
            border_radius=8,
            padding=8
        )
        
        # Animate log items in
        self.motion_system.list_item_interactions(
            log_items,
            stagger_delay=50,
            entrance_direction="up"
        )
        
        return ft.Column([
            ft.Text("Activity Log", style=ft.TextThemeStyle.TITLE_SMALL),
            log_container
        ], spacing=10)
    
    # Button event handlers with motion feedback
    async def _on_start_server(self, e):
        """Handle start server with success feedback."""
        # Simulate server start
        await asyncio.sleep(0.5)
        
        # Show success notification
        self._show_toast("Server started successfully!", "success")
        
        # Update status indicator with pulse
        # In real implementation, this would update actual server status
    
    async def _on_stop_server(self, e):
        """Handle stop server with confirmation."""
        # Show warning shake first
        if self.server_card:
            self.motion_system.error_shake(self.action_buttons[1])  # Stop button
        
        # Simulate server stop
        await asyncio.sleep(0.5)
        self._show_toast("Server stopped", "warning")
    
    async def _on_restart_server(self, e):
        """Handle restart with visual feedback."""
        # Show loading state
        self._show_toast("Restarting server...", "info")
        
        # Simulate restart delay
        await asyncio.sleep(1.0)
        
        # Show completion
        self._show_toast("Server restarted successfully!", "success")
    
    def _on_open_settings(self, e):
        """Handle settings with transition."""
        # In real implementation, this would navigate to settings
        # For demo, just show a modal dialog
        
        dialog_content = ft.Container(
            content=ft.Column([
                ft.Text("Settings", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("Settings panel would appear here"),
                ft.Row([
                    ft.TextButton("Cancel", on_click=lambda e: self.page.close(settings_dialog)),
                    ft.FilledButton("Save", on_click=lambda e: self.page.close(settings_dialog))
                ], alignment=ft.MainAxisAlignment.END, spacing=10)
            ], spacing=20),
            padding=20,
            width=400
        )
        
        settings_dialog = ft.AlertDialog(
            content=dialog_content,
            shape=ft.RoundedRectangleBorder(radius=12)
        )
        
        # Apply dialog animation
        self.motion_system.dialog_appearance(settings_dialog, entrance_style="scale_fade")
        
        self.page.open(settings_dialog)
    
    def _show_toast(self, message: str, level: str = "info"):
        """Show animated toast notification."""
        
        # Color mapping
        colors = {
            "success": TOKENS["secondary"],
            "error": TOKENS["error"],
            "warning": TOKENS["secondary"],
            "info": TOKENS["primary"]
        }
        
        # Icon mapping  
        icons = {
            "success": ft.Icons.CHECK_CIRCLE,
            "error": ft.Icons.ERROR,
            "warning": ft.Icons.WARNING,
            "info": ft.Icons.INFO
        }
        
        toast = ft.Container(
            content=ft.Row([
                ft.Icon(icons.get(level, ft.Icons.INFO), color=TOKENS['on_primary'], size=20),
                ft.Text(message, color=TOKENS['on_primary'], style=ft.TextThemeStyle.BODY_MEDIUM)
            ], spacing=10),
            bgcolor=colors.get(level, TOKENS["primary"]),
            border_radius=8,
            padding=ft.padding.all(16),
            margin=ft.margin.only(bottom=10)
        )
        
        # Add to notification area
        if not hasattr(self.notification_area, 'content'):
            self.notification_area.content = ft.Column([], spacing=5)
        
        self.notification_area.content.controls.append(toast)
        self.page.update()
        
        # Animate toast
        self.motion_system.toast_notification(
            toast,
            slide_from="bottom",
            auto_dismiss_after=3.0,
            on_dismiss=lambda: self._remove_toast(toast)
        )
    
    def _remove_toast(self, toast: ft.Control):
        """Remove toast from notification area."""
        try:
            if (hasattr(self.notification_area, 'content') and 
                hasattr(self.notification_area.content, 'controls')):
                
                if toast in self.notification_area.content.controls:
                    self.notification_area.content.controls.remove(toast)
                    self.page.update()
        except Exception as e:
            print(f"[WARNING] Could not remove toast: {e}")


def main(page: ft.Page):
    """Main application demonstrating Motion System integration."""
    
    # Page setup
    page.title = "Motion System Integration Example"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    
    # Material Design 3
    page.theme = ft.Theme(use_material3=True)
    page.dark_theme = ft.Theme(use_material3=True)
    
    # Create enhanced dashboard
    dashboard = MotionEnabledDashboard(page)
    dashboard_ui = dashboard.create_enhanced_dashboard()
    
    page.add(dashboard_ui)


if __name__ == "__main__":
    ft.app(target=main, view=ft.WEB_BROWSER, port=8081)
