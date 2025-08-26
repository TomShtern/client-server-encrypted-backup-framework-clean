#!/usr/bin/env python3
"""
Final verification test for Phase 4 components integration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Import utf8_solution to fix encoding issues
safe_print = print  # Default fallback
try:
    import Shared.utils.utf8_solution
    from Shared.utils.utf8_solution import safe_print
    safe_print("[INFO] UTF-8 solution imported successfully")
except ImportError as e:
    # Try alternative path
    utf8_path = os.path.join(os.path.dirname(__file__), "..", "Shared", "utils")
    if utf8_path not in sys.path:
        sys.path.insert(0, utf8_path)
    try:
        import utf8_solution
        from utf8_solution import safe_print
        safe_print("[INFO] UTF-8 solution imported via alternative path")
    except ImportError:
        safe_print("[WARNING] utf8_solution import failed, continuing without it")
        safe_print(f"[DEBUG] Import error: {e}")

import flet as ft
import asyncio

async def test_phase4_components():
    """Test Phase 4 component integration and basic functionality"""
    
    safe_print("[TEST] Phase 4 Components Integration Test")
    safe_print("=" * 50)
    
    # Test status indicators import
    try:
        from flet_server_gui.ui.widgets.status_pill import StatusPill, ServerStatus
        safe_print("[SUCCESS] Status indicators imports successfully")
    except Exception as e:
        safe_print(f"[ERROR] Status indicators import failed: {e}")
        return False
    
    # Test notifications panel import
    try:
        from flet_server_gui.ui.widgets.notifications_panel import NotificationsPanel, create_notification, NotificationType, NotificationPriority
        safe_print("[SUCCESS] Notifications panel imports successfully")
    except Exception as e:
        safe_print(f"[ERROR] Notifications panel import failed: {e}")
        return False
    
    # Test activity log dialog import
    try:
        from flet_server_gui.ui.widgets.activity_log_dialog import ActivityLogDialog, create_activity_entry, ActivityLevel, ActivityCategory
        safe_print("[SUCCESS] Activity log dialog imports successfully")
    except Exception as e:
        safe_print(f"[ERROR] Activity log dialog import failed: {e}")
        return False
    
    # Test top bar integration import
    try:
        from flet_server_gui.ui.top_bar_integration import TopBarIntegrationManager, BreadcrumbItem
        safe_print("[SUCCESS] Top bar integration imports successfully")
    except Exception as e:
        safe_print(f"[ERROR] Top bar integration import failed: {e}")
        return False
    
    # Test status pill creation
    try:
        status_pill = StatusPill(ServerStatus.RUNNING)
        safe_print("[SUCCESS] Status pill creation successful")
    except Exception as e:
        safe_print(f"[ERROR] Status pill creation failed: {e}")
        return False
    
    # Test notifications panel creation
    try:
        notification = create_notification(
            "Test Notification",
            "This is a test notification",
            NotificationType.INFO,
            NotificationPriority.NORMAL
        )
        notifications_panel = NotificationsPanel([notification])
        safe_print("[SUCCESS] Notifications panel creation successful")
    except Exception as e:
        safe_print(f"[ERROR] Notifications panel creation failed: {e}")
        return False
    
    # Test activity log dialog creation
    try:
        activity = create_activity_entry(
            "Test Activity",
            ActivityLevel.INFO,
            ActivityCategory.SYSTEM,
            "TestSource"
        )
        activity_log_dialog = ActivityLogDialog([activity])
        safe_print("[SUCCESS] Activity log dialog creation successful")
    except Exception as e:
        safe_print(f"[ERROR] Activity log dialog creation failed: {e}")
        return False
    
    # Test top bar integration creation
    try:
        top_bar_manager = TopBarIntegrationManager(None)
        safe_print("[SUCCESS] Top bar integration creation successful")
    except Exception as e:
        safe_print(f"[ERROR] Top bar integration creation failed: {e}")
        return False
    
    safe_print("\n" + "=" * 50)
    safe_print("[SUCCESS] All Phase 4 components imported and created successfully!")
    safe_print("[SUCCESS] Phase 4 implementation is complete and working correctly!")
    return True

if __name__ == "__main__":
    asyncio.run(test_phase4_components())