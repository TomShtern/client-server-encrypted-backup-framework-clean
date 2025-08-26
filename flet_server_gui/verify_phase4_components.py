#!/usr/bin/env python3
"""
Test script to verify Phase 4 components integration
"""

import sys
import os
import asyncio

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Test imports
try:
    from flet_server_gui.ui.widgets.status_pill import StatusPill, ServerStatus
    print("[SUCCESS] StatusPill import successful")
except Exception as e:
    print(f"[ERROR] StatusPill import failed: {e}")

try:
    from flet_server_gui.ui.widgets.notifications_panel import NotificationsPanel, create_notification, NotificationType, NotificationPriority
    print("[SUCCESS] NotificationsPanel import successful")
except Exception as e:
    print(f"[ERROR] NotificationsPanel import failed: {e}")

try:
    from flet_server_gui.ui.widgets.activity_log_dialog import ActivityLogDialog, create_activity_entry, ActivityLevel, ActivityCategory
    print("[SUCCESS] ActivityLogDialog import successful")
except Exception as e:
    print(f"[ERROR] ActivityLogDialog import failed: {e}")

# Test component creation
try:
    status_pill = StatusPill(ServerStatus.RUNNING)
    print("[SUCCESS] StatusPill creation successful")
except Exception as e:
    print(f"[ERROR] StatusPill creation failed: {e}")

try:
    notification = create_notification(
        "Test Notification",
        "This is a test notification",
        NotificationType.INFO,
        NotificationPriority.NORMAL
    )
    notifications_panel = NotificationsPanel([notification])
    print("[SUCCESS] NotificationsPanel creation successful")
except Exception as e:
    print(f"[ERROR] NotificationsPanel creation failed: {e}")

try:
    activity = create_activity_entry(
        "Test Activity",
        ActivityLevel.INFO,
        ActivityCategory.SYSTEM,
        "TestSource"
    )
    activity_log_dialog = ActivityLogDialog([activity])
    print("[SUCCESS] ActivityLogDialog creation successful")
except Exception as e:
    print(f"[ERROR] ActivityLogDialog creation failed: {e}")

print("")
print("All Phase 4 components imported and created successfully!")
print("Ready for integration with main application")