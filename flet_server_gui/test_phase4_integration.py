#!/usr/bin/env python3
"""
Simple test application to verify Phase 4 components work in a Flet app
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import flet as ft
from flet_server_gui.ui.widgets.status_pill import StatusPill, ServerStatus, create_hero_status_pill
from flet_server_gui.ui.widgets.notifications_panel import NotificationsPanel, create_notification, NotificationType, NotificationPriority
from flet_server_gui.ui.widgets.activity_log_dialog import ActivityLogDialog, create_activity_entry, ActivityLevel, ActivityCategory
from flet_server_gui.core.theme_compatibility import TOKENS


def main(page: ft.Page):
    page.title = "Phase 4 Components Test"
    page.window_width = 800
    page.window_height = 600
    
    # Create status pills
    status_pill = StatusPill(ServerStatus.RUNNING)
    
    def on_status_click(e):
        page.snack_bar = ft.SnackBar(content=ft.Text("Status pill clicked!"))
        page.snack_bar.open = True
        page.update()
    
    status_pill.on_click = on_status_click
    
    # Create sample notifications
    notifications = [
        create_notification(
            "Backup Completed",
            "Daily backup completed successfully with 0 errors.",
            NotificationType.BACKUP,
            NotificationPriority.NORMAL,
            ["View Details", "Dismiss"]
        ),
        create_notification(
            "Security Alert",
            "Failed login attempt detected from IP 192.168.1.100",
            NotificationType.SECURITY,
            NotificationPriority.HIGH,
            ["Block IP", "Dismiss"]
        )
    ]
    
    # Create notifications panel
    panel = NotificationsPanel(notifications)
    
    # Create sample activities
    activities = [
        create_activity_entry(
            "Server started successfully",
            ActivityLevel.SUCCESS,
            ActivityCategory.SYSTEM,
            "ServerManager"
        ),
        create_activity_entry(
            "Client connected: Client-001",
            ActivityLevel.INFO,
            ActivityCategory.CLIENT,
            "ClientManager"
        )
    ]
    
    # Create activity log dialog
    dialog = ActivityLogDialog(activities)
    
    # Create test controls
    def show_notifications(e):
        panel.show()
    
    def show_activity_log(e):
        dialog.show(page)
    
    def change_status(e):
        status_pill.set_status(ServerStatus.ERROR)
    
    def pulse_status(e):
        status_pill.pulse()
    
    # Add components to page
    page.add(
        ft.AppBar(title=ft.Text("Phase 4 Components Test")),
        ft.Column([
            ft.Text("Phase 4 Components Integration Test", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Text("Status:"),
                status_pill
            ]),
            ft.Row([
                ft.ElevatedButton("Show Notifications", on_click=show_notifications),
                ft.ElevatedButton("Show Activity Log", on_click=show_activity_log),
                ft.ElevatedButton("Change Status", on_click=change_status),
                ft.ElevatedButton("Pulse Status", on_click=pulse_status)
            ], spacing=10),
            ft.Text("All Phase 4 components are working correctly!", size=16, color=TOKENS['secondary'])
        ], spacing=20)
    )
    
    # Add panel to page overlay
    page.overlay.append(panel)
    page.update()


if __name__ == "__main__":
    print("Starting Phase 4 Components Test...")
    ft.app(target=main)