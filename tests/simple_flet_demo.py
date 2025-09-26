#!/usr/bin/env python3
"""
Simple Flet Demo - Desktop Server Dashboard

This shows how simple Flet can be compared to your 2,268-line KivyMD dashboard.
No complex threading, no text rendering issues, just clean Material Design 3.
"""


import flet as ft


class SimpleServerDashboard:
    def __init__(self, page: ft.Page):
        self.page = page
        self.server_running = False
        self.setup_page()
        self.build_dashboard()

    def setup_page(self):
        """Configure the desktop window"""
        self.page.title = "Server Dashboard - Flet Demo"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = 600
        self.page.window_height = 500
        self.page.padding = 20

        # Material Design 3
        self.page.theme = ft.Theme(use_material3=True)

    def build_dashboard(self):
        """Build the simple dashboard"""

        # Header
        header = ft.Text("Encrypted Backup Server", style="headlineLarge")

        # Status card
        self.status_text = ft.Text("Status: OFFLINE", style="titleMedium")
        self.status_chip = ft.Chip(
            label=ft.Text("OFFLINE"),
            bgcolor=ft.Colors.ERROR_CONTAINER
        )

        status_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Server Status", style="titleLarge"),
                        self.status_chip
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(),
                    self.status_text,
                    ft.Text("Port: 1256", style="bodyMedium"),
                    ft.Text("Hebrew Test: שלום עולם", style="bodyMedium")  # Unicode test
                ]),
                padding=20
            ),
            width=500
        )

        # Control buttons
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

        controls_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("Server Controls", style="titleLarge"),
                    ft.Divider(),
                    ft.Row([self.start_btn, self.stop_btn], spacing=20)
                ]),
                padding=20
            ),
            width=500
        )

        # Add everything to page
        self.page.add(
            ft.Column([
                header,
                ft.Divider(),
                status_card,
                controls_card,
                ft.Text("Click buttons to test server control!", style="bodySmall")
            ], spacing=20)
        )

    def start_server(self, e):
        """Start server simulation"""
        self.server_running = True
        self.update_status()
        print("Server started!")

    def stop_server(self, e):
        """Stop server simulation"""
        self.server_running = False
        self.update_status()
        print("Server stopped!")

    def update_status(self):
        """Update UI based on server status"""
        if self.server_running:
            # Server online
            self.status_text.value = "Status: RUNNING"
            self.status_chip.label.value = "ONLINE"
            self.status_chip.bgcolor = ft.Colors.PRIMARY_CONTAINER
            self.start_btn.disabled = True
            self.stop_btn.disabled = False
        else:
            # Server offline
            self.status_text.value = "Status: OFFLINE"
            self.status_chip.label.value = "OFFLINE"
            self.status_chip.bgcolor = ft.Colors.ERROR_CONTAINER
            self.start_btn.disabled = False
            self.stop_btn.disabled = True

        # Update the page
        self.page.update()

def main(page: ft.Page):
    """Main app entry point"""
    SimpleServerDashboard(page)

if __name__ == "__main__":
    print("Starting Simple Flet Demo...")
    print("Desktop window will open...")

    # Launch desktop app
    ft.app(target=main)
