#!/usr/bin/env python3
"""
Activity Log Card Component
Material Design 3 card showing server activity log with color-coded entries.
"""

import flet as ft
from datetime import datetime
from typing import List, Dict, Any, Optional


class ActivityLogCard:
    """Activity log card with real-time server activity"""
    
    def __init__(self):
        self.log_entries: List[Dict[str, Any]] = []
        self.max_entries = 50
        self.log_container = ft.Ref[ft.Column]()
        self.page: Optional[ft.Page] = None

    def build(self) -> ft.Card:
        """Build the activity log card with M3 compliance and theme integration"""
        header = ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.TIMELINE),
                ft.Text("Activity Log", style=ft.TextThemeStyle.TITLE_LARGE)
            ], spacing=12),
            ft.IconButton(
                icon=ft.Icons.CLEAR_ALL,
                tooltip="Clear activity log",
                on_click=self.clear_log,
                # Add animation for button interactions
                animate_scale=100
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        log_viewer = ft.Container(
            content=ft.Column(
                ref=self.log_container,
                scroll=ft.ScrollMode.ALWAYS,
                spacing=4,
                # Add a placeholder for when the log is empty
                controls=[ft.Text("No activity yet.", italic=True)]
            ),
            border_radius=8,
            padding=ft.padding.all(12),
            expand=True,
            height=280 # Set a fixed height for the log area
        )
        
        card_content = ft.Container(
            content=ft.Column([header, ft.Divider(), log_viewer], spacing=12, expand=True),
            padding=ft.padding.all(20)
        )
        
        return ft.Card(content=card_content, elevation=1, expand=True)

    def add_entry(self, source: str, message: str, level: str = "INFO"):
        """Add a new log entry with enhanced animation"""
        if not self.log_container.current or not self.page:
            return

        timestamp = datetime.now()
        entry_data = {"timestamp": timestamp, "source": source, "message": message, "level": level}
        
        self.log_entries.insert(0, entry_data)
        if len(self.log_entries) > self.max_entries:
            self.log_entries.pop()

        # Clear placeholder if it exists
        if len(self.log_container.current.controls) == 1 and isinstance(self.log_container.current.controls[0], ft.Text):
            # Animate out placeholder
            self.log_container.current.controls[0].opacity = 1
            self.log_container.current.controls[0].animate_opacity = 200
            self.page.update()
            self.log_container.current.controls[0].opacity = 0
            self.page.update()
            self.log_container.current.controls.clear()

        visual_entry = self.create_log_entry_visual(entry_data)
        
        # Enhanced entrance animation for new entries
        visual_entry.opacity = 0
        visual_entry.offset = ft.transform.Offset(0, 0.5)  # Start slightly below
        visual_entry.animate_opacity = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        visual_entry.animate_offset = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        
        self.log_container.current.controls.insert(0, visual_entry)
        self.page.update()
        
        # Animate in
        visual_entry.opacity = 1
        visual_entry.offset = ft.transform.Offset(0, 0)
        self.page.update()
        
        if len(self.log_container.current.controls) > self.max_entries:
            # Remove oldest entry with fade out animation
            oldest_entry = self.log_container.current.controls[-1]
            oldest_entry.opacity = 1
            oldest_entry.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_IN)
            self.page.update()
            oldest_entry.opacity = 0
            self.page.update()
            self.log_container.current.controls.pop()
        
        self.page.update()

    def create_log_entry_visual(self, entry_data: Dict[str, Any]) -> ft.Control:
        """Create visual representation of a log entry using theme colors."""
        # Handle case where theme or color scheme is not available
        if not self.page.theme or not self.page.theme.color_scheme:
            # Fallback to default colors
            level_colors = {
                "INFO": ft.Colors.GREY_600,
                "SUCCESS": ft.Colors.GREEN_600,
                "WARNING": ft.Colors.ORANGE_600,
                "ERROR": ft.Colors.RED_600
            }
            
            color_scheme = None
        else:
            color_scheme = self.page.theme.color_scheme
            level_colors = {
                "INFO": color_scheme.on_surface_variant,
                "SUCCESS": color_scheme.primary,
                "WARNING": color_scheme.tertiary,
                "ERROR": color_scheme.error
            }
        
        level_icons = {
            "INFO": ft.Icons.INFO_OUTLINE,
            "SUCCESS": ft.Icons.CHECK_CIRCLE_OUTLINE,
            "WARNING": ft.Icons.WARNING_AMBER,
            "ERROR": ft.Icons.ERROR_OUTLINE
        }
        
        level = entry_data["level"]
        color = level_colors.get(level, ft.Colors.GREY_600 if not color_scheme else color_scheme.on_surface_variant)
        icon = level_icons.get(level, ft.Icons.INFO_OUTLINE)
        
        time_str = entry_data["timestamp"].strftime("%H:%M:%S")
        
        # Use fallback colors for text if theme is not available
        if color_scheme:
            time_color = color_scheme.on_surface_variant
            message_color = color_scheme.on_surface
        else:
            time_color = ft.Colors.GREY_600
            message_color = ft.Colors.GREY_800
        
        # Create the visual entry with proper styling
        entry_row = ft.Row([
            ft.Icon(icon, color=color, size=16),
            ft.Text(f"[{time_str}]", style=ft.TextThemeStyle.BODY_SMALL, color=time_color, width=70),
            ft.Text(entry_data["source"], style=ft.TextThemeStyle.BODY_SMALL, weight=ft.FontWeight.BOLD, color=color, width=80),
            ft.Text(entry_data["message"], style=ft.TextThemeStyle.BODY_SMALL, color=message_color, expand=True)
        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
        
        # Add animation properties
        entry_row.opacity = 1
        entry_row.animate_opacity = 300
        
        return entry_row

    def clear_log(self, e=None):
        """Clear all log entries with enhanced animation"""
        self.log_entries.clear()
        if self.log_container.current:
            # Enhanced clear animation - fade out all entries
            if self.log_container.current.controls:
                # Animate all entries out
                for control in self.log_container.current.controls:
                    control.opacity = 1
                    control.animate_opacity = ft.Animation(200, ft.AnimationCurve.EASE_IN)
                self.page.update()
                
                for control in self.log_container.current.controls:
                    control.opacity = 0
                self.page.update()
                
                # Wait for animations to complete
                import time
                time.sleep(0.25)
            
            # Clear and add confirmation message
            self.log_container.current.controls.clear()
            confirmation = ft.Text("Log cleared.", italic=True, opacity=0)
            confirmation.animate_opacity = ft.Animation(300, ft.AnimationCurve.EASE_OUT)
            self.log_container.current.controls.append(confirmation)
            self.page.update()
            confirmation.opacity = 1
            self.page.update()
            
            # Add system entry with animation
            self.add_entry("System", "Activity log cleared", "INFO")
            self.page.update()

    def set_page(self, page: ft.Page):
        """Sets the page context for the component."""
        self.page = page
        # Initialize with a welcome message once the page is set
        self.add_entry("System", "Activity log initialized", "INFO")