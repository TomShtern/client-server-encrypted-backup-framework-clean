#!/usr/bin/env python3
"""
Notifications Panel - Notification management system

Purpose: Manage and display system notifications
Logic: Notification storage, filtering, actions
UI: Slide-out panel with notification cards
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from flet_server_gui.core.theme_compatibility import TOKENS


class NotificationType(Enum):
    """Notification categories"""
    SYSTEM = "system"
    SECURITY = "security"
    BACKUP = "backup"
    CLIENT = "client"
    MAINTENANCE = "maintenance"
    WARNING = "warning"
    INFO = "info"


class NotificationPriority(Enum):
    """Notification priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


@dataclass
class NotificationItem:
    """Individual notification item"""
    id: str
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    timestamp: datetime = field(default_factory=datetime.now)
    read: bool = False
    actions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class NotificationsPanel(ft.NavigationDrawer):
    """Slide-out notifications panel with Material Design 3 styling"""
    
    def __init__(self, 
                 notifications: Optional[List[NotificationItem]] = None,
                 on_notification_click: Optional[Callable] = None,
                 on_action_click: Optional[Callable] = None):
        super().__init__()
        self.notifications = notifications or []
        self.on_notification_click = on_notification_click
        self.on_action_click = on_action_click
        self.position = ft.NavigationDrawerPosition.END
        self.bgcolor = TOKENS['surface']
        self.elevation = 16
        
        # Priority styling
        self._priority_colors = {
            NotificationPriority.CRITICAL: TOKENS['error'],
            NotificationPriority.HIGH: TOKENS['tertiary'],
            NotificationPriority.NORMAL: TOKENS['primary'],
            NotificationPriority.LOW: TOKENS['outline']
        }
        
        self._type_icons = {
            NotificationType.SYSTEM: ft.Icons.COMPUTER,
            NotificationType.SECURITY: ft.Icons.SECURITY,
            NotificationType.BACKUP: ft.Icons.BACKUP,
            NotificationType.CLIENT: ft.Icons.PEOPLE,
            NotificationType.MAINTENANCE: ft.Icons.BUILD,
            NotificationType.WARNING: ft.Icons.WARNING_AMBER,
            NotificationType.INFO: ft.Icons.INFO
        }
        
        # Build the component
        self._build_component()
    
    def _build_component(self):
        """Build notifications panel UI"""
        # Create notification list
        self._notification_list = ft.ListView(
            expand=True,
            spacing=8,
            padding=ft.padding.all(16)
        )
        
        # Populate with existing notifications
        for notification in self.notifications:
            self._notification_list.controls.append(
                self._create_notification_card(notification)
            )
        
        # Create header with clear button
        header = ft.Container(
            content=ft.Row([
                ft.Text("Notifications", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.IconButton(
                    icon=ft.Icons.CLEAR_ALL,
                    tooltip="Clear all notifications",
                    on_click=self._clear_all_notifications
                )
            ]),
            padding=ft.padding.symmetric(horizontal=16, vertical=8)
        )
        
        # Create empty state
        empty_state = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.NOTIFICATIONS_NONE, size=48, color=TOKENS['outline']),
                ft.Text("No notifications", size=16, color=TOKENS['outline']),
                ft.Text("You're all caught up!", size=14, color=TOKENS['outline'])
            ], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8),
            expand=True,
            alignment=ft.alignment.center
        )
        
        # Create main content
        main_content = ft.Column([
            header,
            ft.Divider(),
            self._notification_list if self.notifications else empty_state
        ], expand=True)
        
        # Set content
        self.content = main_content
    
    def _create_notification_card(self, notification: NotificationItem) -> ft.Container:
        """Create a notification card"""
        # Priority indicator
        priority_color = self._priority_colors.get(notification.priority, TOKENS['outline'])
        priority_indicator = ft.Container(
            width=4,
            bgcolor=priority_color,
            border_radius=ft.border_radius.all(2)
        )

        # Icon
        icon = ft.Icon(
            self._type_icons.get(notification.type, ft.Icons.NOTIFICATIONS),
            size=20,
            color=priority_color
        )

        # Title and message
        title = ft.Text(
            notification.title,
            size=14,
            weight=ft.FontWeight.NORMAL if notification.read else ft.FontWeight.BOLD,
            color=TOKENS['outline'] if notification.read else TOKENS['on_background']
        )

        message = ft.Text(
            notification.message,
            size=12,
            color=TOKENS['outline'],
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS
        )

        # Timestamp
        timestamp = ft.Text(
            self._format_timestamp(notification.timestamp),
            size=10,
            color=TOKENS['outline']
        )

        # Action buttons
        action_buttons = []
        if notification.actions:
            for action in notification.actions[:2]:  # Limit to 2 actions
                btn = ft.TextButton(
                    text=action,
                    on_click=lambda e, a=action, nid=notification.id: self._handle_action_click(nid, a)
                )
                action_buttons.append(btn)

        # Main content
        content_column = ft.Column([
            ft.Row([
                title,
                ft.Container(expand=True),
                timestamp
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            message,
            ft.Row(action_buttons, spacing=8) if action_buttons else ft.Container()
        ], spacing=4)

        return ft.Container(
            content=ft.Row(
                [
                    priority_indicator,
                    ft.Container(
                        content=ft.Row(
                            [icon, ft.Container(content_column, expand=True)],
                            spacing=12,
                        ),
                        padding=ft.padding.all(12),
                        expand=True,
                    ),
                ],
                spacing=0,
            ),
            border_radius=8,
            bgcolor=(
                TOKENS['surface'] if notification.read else TOKENS['surface_variant']
            ),
            ink=True,
            on_click=lambda e, nid=notification.id: self._handle_notification_click(
                nid
            ),
        )
    
    def add_notification(self, notification: NotificationItem):
        """Add a new notification"""
        self.notifications.insert(0, notification)  # Add to top
        
        # Limit to 100 notifications
        if len(self.notifications) > 100:
            self.notifications = self.notifications[:100]
        
        # Update UI
        self._notification_list.controls.clear()
        for notif in self.notifications:
            self._notification_list.controls.append(
                self._create_notification_card(notif)
            )
        self._safe_update()
    
    def mark_as_read(self, notification_id: str):
        """Mark notification as read"""
        for notification in self.notifications:
            if notification.id == notification_id:
                notification.read = True
                # Update UI
                self._notification_list.controls.clear()
                for notif in self.notifications:
                    self._notification_list.controls.append(
                        self._create_notification_card(notif)
                    )
                self._safe_update()
                break
    
    def remove_notification(self, notification_id: str):
        """Remove notification"""
        self.notifications = [n for n in self.notifications if n.id != notification_id]
        
        # Update UI
        self._notification_list.controls.clear()
        for notif in self.notifications:
            self._notification_list.controls.append(
                self._create_notification_card(notif)
            )
        self._safe_update()
    
    def clear_all_notifications(self):
        """Clear all notifications"""
        self.notifications.clear()
        
        # Update UI
        self._notification_list.controls.clear()
        self._safe_update()
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        return len([n for n in self.notifications if not n.read])
    
    def show(self):
        """Show notifications panel"""
        self.open = True
        self._safe_update()
    
    def hide(self):
        """Hide notifications panel"""
        self.open = False
        self._safe_update()
    
    def _handle_notification_click(self, notification_id: str):
        """Handle notification click"""
        # Mark as read
        self.mark_as_read(notification_id)
        
        # Call callback
        if self.on_notification_click:
            self.on_notification_click(notification_id)
    
    def _handle_action_click(self, notification_id: str, action: str):
        """Handle action button click"""
        if self.on_action_click:
            self.on_action_click(notification_id, action)
    
    def _clear_all_notifications(self, e):
        """Handle clear all button click"""
        self.clear_all_notifications()
    
    def _safe_update(self):
        """Safely update the component if attached to a page"""
        try:
            if hasattr(self, 'page') and self.page:
                self.update()
        except (AttributeError, AssertionError):
            # Control not attached to page, skip update
            pass
    
    def _format_timestamp(self, timestamp: datetime) -> str:
        """Format timestamp for display"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours}h ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"


# Factory functions for easy creation
def create_notifications_panel(notifications: Optional[List[NotificationItem]] = None,
                              on_notification_click: Optional[Callable] = None,
                              on_action_click: Optional[Callable] = None) -> NotificationsPanel:
    """Create a notifications panel"""
    return NotificationsPanel(notifications, on_notification_click, on_action_click)


def create_notification(title: str, 
                       message: str, 
                       type: NotificationType = NotificationType.INFO,
                       priority: NotificationPriority = NotificationPriority.NORMAL,
                       actions: Optional[List[str]] = None) -> NotificationItem:
    """Create a notification item"""
    return NotificationItem(
        id=f"notif_{datetime.now().timestamp()}",
        title=title,
        message=message,
        type=type,
        priority=priority,
        actions=actions or []
    )