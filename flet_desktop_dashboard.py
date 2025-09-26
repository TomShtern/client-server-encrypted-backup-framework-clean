#!/usr/bin/env python3
"""
Flet Desktop Dashboard for Encrypted Backup Server

Clean desktop application - no Unicode characters, no web mode.
Pure desktop GUI to replace your KivyMD dashboard.

Run with: python flet_desktop_dashboard.py
"""

import asyncio
from datetime import datetime

import flet as ft


class ServerStatusCard:
    """Simple server status card for desktop"""

    def __init__(self):
        self.running = False
        self.uptime_start = None

        # Status indicator
        self.status_chip = ft.Chip(
            label=ft.Text("OFFLINE"),
            bgcolor=ft.Colors.ERROR_CONTAINER
        )

        # Status details
        self.status_text = ft.Text("Status: Stopped", style="bodyLarge")
        self.address_text = ft.Text("Address: N/A", style="bodyMedium")
        self.uptime_text = ft.Text("Uptime: 00:00:00", style="bodyMedium")

    def build(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header
                    ft.Row([
                        ft.Text("Server Status", style="titleLarge"),
                        self.status_chip
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                    ft.Divider(),

                    # Details
                    self.status_text,
                    self.address_text,
                    self.uptime_text
                ], spacing=12),
                padding=20,
                width=350
            ),
            elevation=3
        )

    def update_status(self, running: bool):
        self.running = running

        if running:
            self.status_chip.label.value = "ONLINE"
            self.status_chip.bgcolor = ft.Colors.PRIMARY_CONTAINER
            self.status_text.value = "Status: Running"
            self.address_text.value = "Address: localhost:1256"
            if not self.uptime_start:
                self.uptime_start = datetime.now()
        else:
            self.status_chip.label.value = "OFFLINE"
            self.status_chip.bgcolor = ft.Colors.ERROR_CONTAINER
            self.status_text.value = "Status: Stopped"
            self.address_text.value = "Address: N/A"
            self.uptime_start = None

        # Update uptime
        if self.uptime_start and running:
            uptime = datetime.now() - self.uptime_start
            hours = int(uptime.total_seconds() // 3600)
            minutes = int((uptime.total_seconds() % 3600) // 60)
            seconds = int(uptime.total_seconds() % 60)
            self.uptime_text.value = f"Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            self.uptime_text.value = "Uptime: 00:00:00"

class ControlPanelCard:
    """Simple control panel"""

    def __init__(self, dashboard):
        self.dashboard = dashboard

        self.start_btn = ft.ElevatedButton(
            "Start Server",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self.start_server,
            style=ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY)
        )

        self.stop_btn = ft.ElevatedButton(
            "Stop Server",
            icon=ft.Icons.STOP,
            on_click=self.stop_server,
            style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR),
            disabled=True
        )

    def build(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Control Panel", style="titleLarge"),
                    ft.Divider(),

                    ft.Row([self.start_btn, self.stop_btn], spacing=12)
                ], spacing=16),
                padding=20,
                width=350
            )
        )

    def update_buttons(self, server_running: bool):
        self.start_btn.disabled = server_running
        self.stop_btn.disabled = not server_running

    def start_server(self, e):
        print("Starting server...")
        self.dashboard.server_running = True
        self.dashboard.update_cards()
        self.dashboard.add_log("User", "Server started")

    def stop_server(self, e):
        print("Stopping server...")
        self.dashboard.server_running = False
        self.dashboard.update_cards()
        self.dashboard.add_log("User", "Server stopped")

class ActivityLogCard:
    """Simple activity log"""

    def __init__(self):
        self.log_entries = []
        self.log_view = ft.Column(height=200, scroll=ft.ScrollMode.AUTO)

    def build(self):
        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Activity Log", style="titleLarge"),
                        ft.IconButton(
                            ft.Icons.CLEAR,
                            tooltip="Clear log",
                            on_click=self.clear_log
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                    ft.Divider(),
                    self.log_view
                ], spacing=12),
                padding=20,
                width=720
            )
        )

    def add_entry(self, source: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")

        entry = ft.Text(
            f"[{timestamp}] {source}: {message}",
            style="bodySmall"
        )

        self.log_entries.insert(0, entry)

        # Keep only last 20 entries
        if len(self.log_entries) > 20:
            self.log_entries = self.log_entries[:20]

        self.log_view.controls = self.log_entries

    def clear_log(self, e):
        self.log_entries.clear()
        self.log_view.controls = []
        self.add_entry("System", "Log cleared")

class DesktopDashboard:
    """Clean desktop dashboard"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.server_running = False

        # Create cards
        self.status_card = ServerStatusCard()
        self.control_card = ControlPanelCard(self)
        self.log_card = ActivityLogCard()

        self.setup_page()
        self.build_ui()

        # Start monitoring
        asyncio.create_task(self.monitor_loop())

    def setup_page(self):
        self.page.title = "Encrypted Backup Server"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = 800
        self.page.window_height = 600
        self.page.window_resizable = True

        # Material Design 3
        self.page.theme = ft.Theme(use_material3=True)

    def build_ui(self):
        # Header
        header = ft.Row([
            ft.Icon(ft.Icons.SECURITY, size=32),
            ft.Text("Encrypted Backup Server", style="headlineMedium"),
        ], spacing=16)

        # Top row - status and controls
        top_row = ft.Row([
            self.status_card.build(),
            self.control_card.build()
        ], spacing=20, alignment=ft.MainAxisAlignment.CENTER)

        # Bottom row - log
        bottom_row = ft.Row([
            self.log_card.build()
        ], alignment=ft.MainAxisAlignment.CENTER)

        # Main layout
        self.page.add(
            ft.Column([
                ft.Container(header, padding=ft.padding.all(20)),
                ft.Divider(),
                ft.Container(top_row, padding=ft.padding.symmetric(horizontal=20)),
                ft.Container(bottom_row, padding=ft.padding.all(20))
            ], spacing=0, expand=True)
        )

        # Initial setup
        self.add_log("System", "Desktop dashboard initialized")
        self.update_cards()

    def update_cards(self):
        self.status_card.update_status(self.server_running)
        self.control_card.update_buttons(self.server_running)
        self.page.update()

    def add_log(self, source: str, message: str):
        self.log_card.add_entry(source, message)
        self.page.update()

    async def monitor_loop(self):
        """Update uptime every second"""
        while True:
            try:
                if self.server_running:
                    self.status_card.update_status(True)
                    self.page.update()

                await asyncio.sleep(1)
            except Exception as e:
                print(f"Monitor error: {e}")
                await asyncio.sleep(5)

def main(page: ft.Page):
    """Desktop app entry point"""
    dashboard = DesktopDashboard(page)

if __name__ == "__main__":
    print("Starting Desktop Dashboard...")
    print("Window will open shortly...")

    # Run desktop app
    ft.app(target=main)
