#!/usr/bin/env python3
"""
Control Panel Card Component
Material Design 3 card with server control buttons and actions.
"""

import flet as ft
import asyncio
from typing import TYPE_CHECKING
from flet_server_gui.utils.server_bridge import ServerBridge

if TYPE_CHECKING:
    from flet_server_gui.main import ServerGUIApp


class ControlPanelCard:
    """Control panel card with server management buttons"""
    
    def __init__(self, server_bridge: ServerBridge, app: "ServerGUIApp"):
        self.server_bridge = server_bridge
        self.app = app
        self.server_running = False

        # --- Control References --- #
        self.start_button_ref = ft.Ref[ft.FilledButton]()
        self.stop_button_ref = ft.Ref[ft.FilledButton]()
        self.restart_button_ref = ft.Ref[ft.OutlinedButton]()
        self.operation_status_ref = ft.Ref[ft.Row]()
        self.operation_text_ref = ft.Ref[ft.Text]()

    def build(self) -> ft.Card:
        """Build the control panel card"""
        
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.CONSTRUCTION),
            ft.Text("Control Panel", style=ft.TextThemeStyle.TITLE_LARGE)
        ], spacing=12)
        
        # Primary actions using semantic M3 buttons
        primary_actions = ft.Row([
            ft.FilledButton(
                ref=self.start_button_ref,
                text="Start Server",
                icon=ft.Icons.PLAY_ARROW,
                on_click=self.start_server,
                # Add animation for button interactions
                animate_scale=100
            ),
            ft.FilledButton(
                ref=self.stop_button_ref,
                text="Stop Server", 
                icon=ft.Icons.STOP,
                on_click=self.stop_server,
                disabled=True,
                animate_scale=100
            )
        ], spacing=12)
        
        # Secondary actions  
        secondary_actions = ft.Row([
            ft.OutlinedButton(
                ref=self.restart_button_ref,
                text="Restart",
                icon=ft.Icons.REFRESH,
                on_click=self.restart_server,
                disabled=True,
                animate_scale=100
            )
        ], spacing=12)
        
        # Operation status (now controlled by Ref)
        operation_status = ft.Row([
            ft.ProgressRing(width=20, height=20, stroke_width=2),
            ft.Text(ref=self.operation_text_ref, style=ft.TextThemeStyle.BODY_SMALL)
        ], ref=self.operation_status_ref, spacing=8, visible=False)
        
        # Mock mode indicator
        mock_indicator = None
        if self.server_bridge.is_mock_mode():
            mock_indicator = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.DEVELOPER_MODE, size=16),
                    ft.Text("Mock Mode", style=ft.TextThemeStyle.LABEL_SMALL)
                ], spacing=4),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=4
            )
        
        # Card content
        content_items = [header, ft.Divider(), primary_actions, secondary_actions]
        if mock_indicator:
            content_items.append(mock_indicator)
        content_items.append(operation_status)
        
        card_content = ft.Container(
            content=ft.Column(content_items, spacing=16),
            padding=ft.padding.all(20),
            width=350
        )
        
        return ft.Card(
            content=card_content,
            elevation=1
        )
    
    def update_button_states(self, server_running: bool):
        """Update button states based on server status using Refs."""
        self.server_running = server_running
        if self.start_button_ref.current:
            self.start_button_ref.current.disabled = server_running
            self.stop_button_ref.current.disabled = not server_running
            self.restart_button_ref.current.disabled = not server_running
            
            # Add visual feedback for button state changes using theme colors
            if hasattr(self.app.page.theme, 'color_scheme'):
                if server_running:
                    # Use secondary color for stop button when server is running with animation
                    self.stop_button_ref.current.style = ft.ButtonStyle(
                        bgcolor=self.app.page.theme.color_scheme.secondary,
                        color=self.app.page.theme.color_scheme.on_secondary
                    )
                    # Add subtle pulse animation when button becomes active
                    self.stop_button_ref.current.scale = ft.transform.Scale(1)
                    self.stop_button_ref.current.animate_scale = ft.Animation(150, ft.AnimationCurve.ELASTIC_OUT)
                    self.app.page.update()
                    self.stop_button_ref.current.scale = ft.transform.Scale(1.02)
                    self.app.page.update()
                    self.stop_button_ref.current.scale = ft.transform.Scale(1)
                    self.app.page.update()
                else:
                    self.stop_button_ref.current.style = None
            self.app.page.update()
    
    def show_operation_status(self, message: str):
        """Show operation status using Refs for direct access."""
        if self.operation_status_ref.current:
            self.operation_text_ref.current.value = message
            self.operation_status_ref.current.visible = True
            self.page.update()

    def hide_operation_status(self):
        """Hide operation status using Refs."""
        if self.operation_status_ref.current:
            self.operation_status_ref.current.visible = False
            self.page.update()

    @property
    def page(self) -> ft.Page:
        return self.app.page

    async def start_server(self, e):
        """Start the server"""
        self.show_operation_status("Starting server...")
        try:
            success = await self.server_bridge.start_server()
            if success:
                self.update_button_states(True)
                await self.app.show_notification("Server started successfully")
                self.app.activity_log.add_entry("Control", "Server started by user", "SUCCESS")
            else:
                await self.app.show_notification("Failed to start server", is_error=True)
                self.app.activity_log.add_entry("Control", "Failed to start server", "ERROR")
        except Exception as ex:
            await self.app.show_notification(f"Error starting server: {str(ex)}", is_error=True)
            self.app.activity_log.add_entry("Control", f"Start error: {str(ex)}", "ERROR")
        finally:
            self.hide_operation_status()
    
    async def stop_server(self, e):
        """Stop the server"""
        self.show_operation_status("Stopping server...")
        try:
            success = await self.server_bridge.stop_server()
            if success:
                self.update_button_states(False)
                await self.app.show_notification("Server stopped successfully")
                self.app.activity_log.add_entry("Control", "Server stopped by user", "INFO")
            else:
                await self.app.show_notification("Failed to stop server", is_error=True)
                self.app.activity_log.add_entry("Control", "Failed to stop server", "ERROR")
        except Exception as ex:
            await self.app.show_notification(f"Error stopping server: {str(ex)}", is_error=True)
            self.app.activity_log.add_entry("Control", f"Stop error: {str(ex)}", "ERROR")
        finally:
            self.hide_operation_status()
    
    async def restart_server(self, e):
        """Restart the server"""
        self.show_operation_status("Restarting server...")
        try:
            success = await self.server_bridge.restart_server()
            if success:
                self.update_button_states(True)
                await self.app.show_notification("Server restarted successfully")
                self.app.activity_log.add_entry("Control", "Server restarted by user", "SUCCESS")
            else:
                await self.app.show_notification("Failed to restart server", is_error=True)
                self.app.activity_log.add_entry("Control", "Failed to restart server", "ERROR")
        except Exception as ex:
            await self.app.show_notification(f"Error restarting server: {str(ex)}", is_error=True)
            self.app.activity_log.add_entry("Control", f"Restart error: {str(ex)}", "ERROR")
        finally:
            self.hide_operation_status()