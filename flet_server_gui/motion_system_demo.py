#!/usr/bin/env python3
"""
Material Design 3 Motion System Demo
Demonstrates the M3 Motion System capabilities with interactive examples.
"""

import flet as ft
import asyncio
from flet_server_gui.ui.motion_system import (
    M3MotionSystem, 
    MotionAnimation, 
    MotionDuration, 
    MotionEasing
)
from .ui.theme_m3 import TOKENS


class MotionSystemDemo:
    def __init__(self, page: ft.Page):
        self.page = page
        self.motion_system = create_motion_system(page)
        
        # Demo components
        self.demo_card = None
        self.demo_button = None
        self.list_items = []
        self.current_content = None
    
    def create_demo_ui(self) -> ft.Control:
        """Create the demo interface."""
        
        # Title
        title = ft.Text(
            "Material Design 3 Motion System Demo",
            style=ft.TextThemeStyle.HEADLINE_MEDIUM,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        # Demo card for animations
        self.demo_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.ANIMATION, size=48, color=TOKENS['primary']),
                    ft.Text("Demo Card", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    ft.Text("Hover over me or click buttons below", 
                           style=ft.TextThemeStyle.BODY_SMALL)
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
                padding=20,
                alignment=ft.alignment.center
            ),
            elevation=2,
            width=200,
            height=150
        )
        
        # Apply hover effect to demo card
        self.motion_system.card_hover_effect(self.demo_card)
        
        # Demo button
        self.demo_button = ft.FilledButton(
            text="Click Me!",
            icon=ft.Icons.TOUCH_APP,
            on_click=lambda e: None  # Will be enhanced with motion
        )
        
        # Apply button press feedback
        self.motion_system.button_press_feedback(self.demo_button)
        self.motion_system.button_hover_effect(self.demo_button)
        
        # Control buttons
        control_buttons = self._create_control_buttons()
        
        # Transition demo area
        transition_demo = self._create_transition_demo()
        
        # List animation demo
        list_demo = self._create_list_demo()
        
        # Main layout
        main_content = ft.Column([
            title,
            ft.Divider(height=20),
            
            # Card and button demo section
            ft.Row([
                ft.Column([
                    ft.Text("Interactive Elements", 
                           style=ft.TextThemeStyle.TITLE_SMALL),
                    self.demo_card,
                    self.demo_button
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                
                ft.VerticalDivider(width=40),
                
                ft.Column([
                    ft.Text("Animation Controls", 
                           style=ft.TextThemeStyle.TITLE_SMALL),
                    *control_buttons
                ], alignment=ft.MainAxisAlignment.START, spacing=8)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            
            ft.Divider(height=30),
            transition_demo,
            ft.Divider(height=30),
            list_demo
        ], 
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        scroll=ft.ScrollMode.AUTO
        )
        
        return ft.Container(
            content=main_content,
            padding=20,
            expand=True
        )
    
    def _create_control_buttons(self) -> list:
        """Create control buttons for triggering animations."""
        
        buttons = [
            # Basic animations
            ft.OutlinedButton(
                text="Fade In",
                icon=ft.Icons.VISIBILITY,
                on_click=self._on_fade_in
            ),
            ft.OutlinedButton(
                text="Fade Out",
                icon=ft.Icons.VISIBILITY_OFF,
                on_click=self._on_fade_out
            ),
            ft.OutlinedButton(
                text="Slide Up",
                icon=ft.Icons.KEYBOARD_ARROW_UP,
                on_click=self._on_slide_up
            ),
            ft.OutlinedButton(
                text="Slide Down", 
                icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                on_click=self._on_slide_down
            ),
            
            # Feedback animations
            ft.OutlinedButton(
                text="Success Pulse",
                icon=ft.Icons.CHECK_CIRCLE,
                on_click=self._on_success_pulse,
                style=ft.ButtonStyle(color=TOKENS['secondary'])
            ),
            ft.OutlinedButton(
                text="Error Shake",
                icon=ft.Icons.ERROR,
                on_click=self._on_error_shake,
                style=ft.ButtonStyle(color=TOKENS['error'])
            ),
            
            # Toast demo
            ft.OutlinedButton(
                text="Show Toast",
                icon=ft.Icons.NOTIFICATIONS,
                on_click=self._on_show_toast
            ),
        ]
        
        # Apply motion effects to control buttons
        for button in buttons:
            self.motion_system.button_hover_effect(button, scale_factor=1.03)
        
        return buttons
    
    def _create_transition_demo(self) -> ft.Control:
        """Create transition pattern demo."""
        
        # Content containers
        content_a = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOOKS_ONE, size=64, color=TOKENS['primary']),
                ft.Text("Content A", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("This is the first content panel")
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            bgcolor=TOKENS['surface_variant'],
            border_radius=12,
            padding=20,
            width=300,
            height=200,
            alignment=ft.alignment.center
        )
        
        content_b = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.LOOKS_TWO, size=64, color=TOKENS['secondary']),
                ft.Text("Content B", style=ft.TextThemeStyle.HEADLINE_SMALL),
                ft.Text("This is the second content panel")
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            bgcolor=TOKENS['surface_variant'],
            border_radius=12,
            padding=20,
            width=300,
            height=200,
            alignment=ft.alignment.center
        )
        
        # Start with content A visible
        self.current_content = content_a
        content_b.visible = False
        
        # Transition buttons
        transition_buttons = ft.Row([
            ft.FilledButton(
                text="Fade Through",
                icon=ft.Icons.SWAP_HORIZ,
                on_click=lambda e: self._transition_fade_through(content_a, content_b)
            ),
            ft.FilledButton(
                text="Shared Axis X", 
                icon=ft.Icons.ARROW_FORWARD,
                on_click=lambda e: self._transition_shared_axis_x(content_a, content_b)
            ),
            ft.FilledButton(
                text="Container Transform",
                icon=ft.Icons.TRANSFORM,
                on_click=lambda e: self._transition_container_transform(content_a, content_b)
            )
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        
        # Apply hover effects to transition buttons
        for button in transition_buttons.controls:
            self.motion_system.button_hover_effect(button)
        
        return ft.Column([
            ft.Text("Transition Patterns", style=ft.TextThemeStyle.TITLE_SMALL),
            ft.Stack([content_a, content_b]),
            transition_buttons
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
    
    def _create_list_demo(self) -> ft.Control:
        """Create list animation demo."""
        
        # Create list items
        self.list_items = []
        for i in range(6):
            item = ft.ListTile(
                leading=ft.Icon(ft.Icons.STAR, color=TOKENS['tertiary']),
                title=ft.Text(f"List Item {i+1}"),
                subtitle=ft.Text(f"Description for item {i+1}"),
                bgcolor=TOKENS['surface_variant'],
                border_radius=8
            )
            self.list_items.append(item)
        
        # List container
        list_container = ft.Column(
            controls=self.list_items,
            spacing=5,
            height=300,
            scroll=ft.ScrollMode.AUTO
        )
        
        # List control buttons
        list_buttons = ft.Row([
            ft.FilledButton(
                text="Animate In",
                icon=ft.Icons.PLAY_ARROW,
                on_click=self._on_animate_list_in
            ),
            ft.FilledButton(
                text="Reset List",
                icon=ft.Icons.REFRESH,
                on_click=self._on_reset_list
            )
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        
        # Apply hover effects
        for button in list_buttons.controls:
            self.motion_system.button_hover_effect(button)
        
        return ft.Column([
            ft.Text("List Animations", style=ft.TextThemeStyle.TITLE_SMALL),
            list_container,
            list_buttons
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=15)
    
    # Animation event handlers
    def _on_fade_in(self, e):
        """Handle fade in animation."""
        self.motion_system.fade_in(self.demo_card, duration=M3Duration.MEDIUM2)
    
    def _on_fade_out(self, e):
        """Handle fade out animation.""" 
        self.motion_system.fade_out(self.demo_card, duration=M3Duration.MEDIUM2)
    
    def _on_slide_up(self, e):
        """Handle slide up animation."""
        self.motion_system.slide_up(self.demo_card, duration=M3Duration.MEDIUM2)
    
    def _on_slide_down(self, e):
        """Handle slide down animation."""
        self.motion_system.slide_down(self.demo_card, duration=M3Duration.MEDIUM2)
    
    def _on_success_pulse(self, e):
        """Handle success pulse animation."""
        self.motion_system.success_pulse(self.demo_card)
    
    def _on_error_shake(self, e):
        """Handle error shake animation."""
        self.motion_system.error_shake(self.demo_card)
    
    def _on_show_toast(self, e):
        """Show toast notification."""
        toast = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.INFO, color=TOKENS['on_primary']),
                ft.Text("This is a toast notification!", color=TOKENS['on_primary'])
            ], spacing=10),
            bgcolor=TOKENS['surface'],
            border_radius=8,
            padding=ft.padding.all(12),
            margin=ft.margin.only(bottom=20, left=20, right=20)
        )
        
        # Add toast to page overlay
        self.page.overlay.append(toast)
        self.page.update()
        
        # Animate toast
        self.motion_system.toast_notification(
            toast, 
            slide_from="bottom",
            auto_dismiss_after=3.0,
            on_dismiss=lambda: (
                self.page.overlay.remove(toast),
                self.page.update()
            )
        )
    
    def _transition_fade_through(self, content_a, content_b):
        """Demonstrate fade through transition."""
        current = self.current_content
        next_content = content_b if current == content_a else content_a
        
        def on_complete():
            current.visible = False
            next_content.visible = True
            self.current_content = next_content
            self.page.update()
        
        M3TransitionPatterns.fade_through(
            current, next_content, 
            duration=M3Duration.MEDIUM4.value,
            on_complete=on_complete
        )
    
    def _transition_shared_axis_x(self, content_a, content_b):
        """Demonstrate shared axis X transition."""
        current = self.current_content
        next_content = content_b if current == content_a else content_a
        
        # Hide current and show next
        current.visible = False
        next_content.visible = True
        self.current_content = next_content
        self.page.update()
        
        # Animate next content in
        M3TransitionPatterns.shared_axis_x(
            next_content,
            direction="forward" if next_content == content_b else "backward",
            duration=M3Duration.LONG2.value
        )
    
    def _transition_container_transform(self, content_a, content_b):
        """Demonstrate container transform."""
        current = self.current_content
        next_content = content_b if current == content_a else content_a
        
        def on_complete():
            current.visible = False
            next_content.visible = True
            self.current_content = next_content
            self.page.update()
        
        next_content.visible = True
        self.page.update()
        
        M3TransitionPatterns.container_transform(
            current, next_content,
            duration=M3Duration.LONG2.value,
            on_complete=on_complete
        )
    
    def _on_animate_list_in(self, e):
        """Animate list items with staggered entrance."""
        self.motion_system.list_item_interactions(
            self.list_items,
            stagger_delay=75,
            entrance_direction="up"
        )
    
    def _on_reset_list(self, e):
        """Reset list items to initial state."""
        for item in self.list_items:
            item.opacity = 0
            item.offset = ft.transform.Offset(0, 0.5)
        self.page.update()


def main(page: ft.Page):
    """Main demo application."""
    
    # Page configuration
    page.title = "Material Design 3 Motion System Demo"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 0
    page.scroll = ft.ScrollMode.AUTO
    
    # Enable Material Design 3
    page.theme = ft.Theme(use_material3=True)
    page.dark_theme = ft.Theme(use_material3=True)
    
    # Create demo
    demo = MotionSystemDemo(page)
    demo_ui = demo.create_demo_ui()
    
    # Add to page
    page.add(demo_ui)
    
    # Initial animation - fade in the whole UI
    demo.motion_system.fade_in(demo_ui, duration=M3Duration.LONG1)


if __name__ == "__main__":
    # Run demo application
    ft.app(target=main, view=ft.WEB_BROWSER, port=8080)