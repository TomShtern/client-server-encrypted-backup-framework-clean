#!/usr/bin/env python3
"""
Test script for Phase 4 components
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import flet as ft
from flet_server_gui.ui.widgets.status_pill import StatusPill, ServerStatus, create_hero_status_pill
from flet_server_gui.ui.widgets.notifications_panel import NotificationsPanel, create_notification, NotificationType, NotificationPriority
from flet_server_gui.ui.widgets.activity_log_dialog import ActivityLogDialog, create_activity_entry, ActivityLevel, ActivityCategory


def test_status_pill(page: ft.Page):
    """Test status pill component"""
    # Create status pills
    status_pill = StatusPill(ServerStatus.RUNNING)
    hero_pill = create_hero_status_pill(ServerStatus.STARTING)
    compact_pill = StatusPill(ServerStatus.ERROR)
    
    def on_status_click(e):
        print("Status pill clicked!")
    
    status_pill.on_click = on_status_click
    hero_pill.on_click = on_status_click
    compact_pill.on_click = on_status_click
    
    # Create test layout
    page.add(
        ft.AppBar(title=ft.Text("Status Pill Test")),
        ft.Column([
            ft.Text("Status Pills Test", size=20, weight=ft.FontWeight.BOLD),
            ft.Row([
                ft.Text("Normal:"),
                status_pill
            ]),
            ft.Row([
                ft.Text("Hero:"),
                hero_pill
            ]),
            ft.Row([
                ft.Text("Compact:"),
                compact_pill
            ]),
            ft.ElevatedButton("Change Status", on_click=lambda e: status_pill.set_status(ServerStatus.ERROR)),
            ft.ElevatedButton("Pulse Animation", on_click=lambda e: status_pill.pulse())
        ], spacing=20)
    )


def test_notifications_panel(page: ft.Page):
    """Test notifications panel component"""
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
        ),
        create_notification(
            "System Update",
            "New version available for download",
            NotificationType.MAINTENANCE,
            NotificationPriority.LOW,
            ["Download", "Dismiss"]
        )
    ]
    
    # Create notifications panel
    panel = NotificationsPanel(notifications)
    
    def on_notification_click(notification_id):
        print(f"Notification clicked: {notification_id}")
    
    def on_action_click(notification_id, action):
        print(f"Action '{action}' clicked for notification: {notification_id}")
        panel.mark_as_read(notification_id)
    
    panel.on_notification_click = on_notification_click
    panel.on_action_click = on_action_click
    
    # Create test layout
    page.add(
        ft.AppBar(title=ft.Text("Notifications Panel Test")),
        ft.Column([
            ft.Text("Notifications Panel Test", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Show Panel", on_click=lambda e: panel.show()),
            ft.ElevatedButton("Add Notification", on_click=lambda e: panel.add_notification(
                create_notification(
                    "New Notification",
                    "This is a dynamically added notification",
                    NotificationType.INFO,
                    NotificationPriority.NORMAL
                )
            )),
            ft.ElevatedButton("Clear All", on_click=lambda e: panel.clear_all_notifications())
        ], spacing=20)
    )
    
    # Add panel to page overlay
    page.overlay.append(panel)


def test_activity_log_dialog(page: ft.Page):
    """Test activity log dialog component"""
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
        ),
        create_activity_entry(
            "Backup job completed",
            ActivityLevel.SUCCESS,
            ActivityCategory.BACKUP,
            "BackupService"
        ),
        create_activity_entry(
            "Warning: Disk space low",
            ActivityLevel.WARNING,
            ActivityCategory.SYSTEM,
            "SystemMonitor"
        )
    ]
    
    # Create activity log dialog
    dialog = ActivityLogDialog(activities)
    
    def on_close():
        print("Activity log dialog closed")
    
    dialog.on_close = on_close
    
    # Create test layout
    page.add(
        ft.AppBar(title=ft.Text("Activity Log Dialog Test")),
        ft.Column([
            ft.Text("Activity Log Dialog Test", size=20, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("Show Dialog", on_click=lambda e: dialog.show()),
            ft.ElevatedButton("Add Activity", on_click=lambda e: dialog.add_activity(
                create_activity_entry(
                    "Test activity added",
                    ActivityLevel.INFO,
                    ActivityCategory.SYSTEM,
                    "TestSource"
                )
            )),
            ft.Text(f"Total activities: {dialog.get_activity_count()}"),
            ft.Text(f"Error count: {dialog.get_error_count()}")
        ], spacing=20)
    )


def main(page: ft.Page):
    """Main test function"""
    page.title = "Phase 4 Components Test"
    page.window_width = 800
    page.window_height = 600
    
    # Test all components
    test_status_pill(page)
    test_notifications_panel(page)
    test_activity_log_dialog(page)


if __name__ == "__main__":
    print("Starting Phase 4 Components Test...")
    ft.app(target=main)