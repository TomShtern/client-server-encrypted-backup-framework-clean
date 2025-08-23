#!/usr/bin/env python3
"""
Enhanced Components Showcase Demo
Demonstrates all implemented enhanced UI components and interactions.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '.')

import flet as ft
from flet_server_gui.components.enhanced_components import *
from flet_server_gui.components.dialogs import *
from flet_server_gui.components.charts import *
from flet_server_gui.components.widgets import *


def main(page: ft.Page):
    page.title = "Enhanced Components Showcase"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Demo 1: Enhanced Buttons
    button_demo = ft.Column([
        ft.Text("Enhanced Buttons", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Advanced buttons with ripple effects and hover animations", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.Row([
            create_enhanced_button(
                text="Primary Button",
                icon=ft.Icons.PLAY_ARROW,
                on_click=lambda e: print("Primary button clicked!")
            ),
            create_enhanced_button(
                text="Secondary Button", 
                icon=ft.Icons.STOP,
                on_click=lambda e: print("Secondary button clicked!"),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.SECONDARY,
                    color=ft.Colors.ON_SECONDARY
                )
            ),
            create_enhanced_button(
                text="Tertiary Button",
                icon=ft.Icons.REFRESH,
                on_click=lambda e: print("Tertiary button clicked!"),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.TERTIARY,
                    color=ft.Colors.ON_TERTIARY
                )
            ),
        ], spacing=20, wrap=True)
    ], spacing=16)
    
    # Demo 2: Enhanced Icon Buttons
    icon_button_demo = ft.Column([
        ft.Text("Enhanced Icon Buttons", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Icon buttons with scale animations and hover effects", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.Row([
            create_enhanced_icon_button(
                icon=ft.Icons.ADD,
                tooltip="Add Item",
                on_click=lambda e: print("Add clicked!")
            ),
            create_enhanced_icon_button(
                icon=ft.Icons.EDIT,
                tooltip="Edit Item",
                on_click=lambda e: print("Edit clicked!")
            ),
            create_enhanced_icon_button(
                icon=ft.Icons.DELETE,
                tooltip="Delete Item",
                on_click=lambda e: print("Delete clicked!")
            ),
            create_enhanced_icon_button(
                icon=ft.Icons.SHARE,
                tooltip="Share Item",
                on_click=lambda e: print("Share clicked!")
            ),
        ], spacing=20)
    ], spacing=16)
    
    # Demo 3: Enhanced Chips
    chip_demo = ft.Column([
        ft.Text("Enhanced Chips", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Interactive chips with selection states and animations", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.Row([
            create_enhanced_chip(
                label="Filter 1",
                on_click=lambda e: print("Filter 1 clicked!"),
                selected=False
            ),
            create_enhanced_chip(
                label="Filter 2",
                on_click=lambda e: print("Filter 2 clicked!"),
                selected=True
            ),
            create_enhanced_chip(
                label="Filter 3",
                on_click=lambda e: print("Filter 3 clicked!"),
                selected=False
            ),
            create_enhanced_chip(
                label="Remove",
                on_click=lambda e: print("Remove clicked!")
            ),
        ], spacing=16, wrap=True)
    ], spacing=16)
    
    # Demo 4: Enhanced Text Fields
    text_field_demo = ft.Column([
        ft.Text("Enhanced Text Fields", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Text fields with floating labels and focus animations", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.Column([
            create_enhanced_text_field(
                label="Username",
                icon=ft.Icons.PERSON,
                hint_text="Enter your username"
            ),
            create_enhanced_text_field(
                label="Password",
                icon=ft.Icons.LOCK,
                password=True,
                hint_text="Enter your password"
            ),
            create_enhanced_text_field(
                label="Description",
                icon=ft.Icons.DESCRIPTION,
                multiline=True,
                hint_text="Enter a description..."
            ),
        ], spacing=16)
    ], spacing=16)
    
    # Demo 5: Enhanced Cards
    card_demo = ft.Column([
        ft.Text("Enhanced Cards", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Cards with hover effects and elevation animations", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.Row([
            create_enhanced_card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("Card Title", style=ft.TextThemeStyle.TITLE_LARGE),
                        ft.Text("This is an enhanced card with hover effects and smooth animations.", size=14),
                        ft.Row([
                            create_enhanced_button(text="Action 1", size=ComponentSize.S),
                            create_enhanced_button(text="Action 2", size=ComponentSize.S, style=ft.ButtonStyle(bgcolor=ft.Colors.SECONDARY, color=ft.Colors.ON_SECONDARY)),
                        ], spacing=12)
                    ], spacing=16),
                    padding=20
                ),
                elevation=2
            ),
            create_enhanced_card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.IMAGE, size=48, color=ft.Colors.PRIMARY),
                        ft.Text("Media Card", style=ft.TextThemeStyle.TITLE_LARGE),
                        ft.Text("Card with media content and interactive elements.", size=14),
                    ], spacing=16, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=20
                ),
                elevation=2
            ),
        ], spacing=20, wrap=True)
    ], spacing=16)
    
    # Demo 6: Charts
    chart_demo = ft.Column([
        ft.Text("Enhanced Charts", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Data visualization components with animations", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.Row([
            create_bar_chart(
                data=[
                    {"month": "Jan", "sales": 1200},
                    {"month": "Feb", "sales": 1900},
                    {"month": "Mar", "sales": 1500},
                    {"month": "Apr", "sales": 2200},
                    {"month": "May", "sales": 1800},
                ],
                x_field="month",
                y_field="sales",
                title="Monthly Sales"
            ),
            create_pie_chart(
                data=[
                    {"category": "Electronics", "value": 45},
                    {"category": "Clothing", "value": 30},
                    {"category": "Books", "value": 15},
                    {"category": "Other", "value": 10},
                ],
                label_field="category",
                value_field="value",
                title="Product Categories"
            ),
        ], spacing=20, wrap=True)
    ], spacing=16)
    
    # Demo 7: Widgets
    widget_demo = ft.Column([
        ft.Text("Dashboard Widgets", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Modular widgets with auto-refresh and collapse capabilities", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.ResponsiveRow([
            ft.Column([
                create_stat_widget(
                    title="Total Revenue",
                    value="$45,231",
                    unit="USD",
                    icon=ft.Icons.MONETIZATION_ON,
                    trend=12.5,
                    color=ft.Colors.GREEN,
                    size=WidgetSize.SMALL
                )
            ], col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([
                create_stat_widget(
                    title="Active Users",
                    value=1245,
                    icon=ft.Icons.PERSON,
                    trend=-2.3,
                    color=ft.Colors.PRIMARY,
                    size=WidgetSize.SMALL
                )
            ], col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([
                create_stat_widget(
                    title="Tasks Completed",
                    value=89,
                    unit="%",
                    icon=ft.Icons.CHECK_CIRCLE,
                    trend=5.7,
                    color=ft.Colors.SECONDARY,
                    size=WidgetSize.SMALL
                )
            ], col={"sm": 12, "md": 6, "lg": 3}),
            ft.Column([
                create_stat_widget(
                    title="Conversion Rate",
                    value=3.2,
                    unit="%",
                    icon=ft.Icons.TRENDING_UP,
                    trend=1.8,
                    color=ft.Colors.TERTIARY,
                    size=WidgetSize.SMALL
                )
            ], col={"sm": 12, "md": 6, "lg": 3}),
        ], spacing=20),
    ], spacing=16)
    
    # Demo 8: Dialogs
    def show_confirmation_dialog(e):
        dialog = create_confirmation_dialog(
            title="Confirm Action",
            message="Are you sure you want to perform this action?",
            on_confirm=lambda e: print("Confirmed!"),
            on_cancel=lambda e: print("Cancelled!")
        )
        dialog.show(page)
    
    def show_input_dialog(e):
        dialog = create_input_dialog(
            title="Enter Information",
            label="Please enter your name:",
            on_submit=lambda e, value: print(f"Submitted: {value}"),
            on_cancel=lambda e: print("Input cancelled")
        )
        dialog.show(page)
    
    def show_progress_dialog(e):
        dialog = create_progress_dialog(
            title="Processing...",
            message="Please wait while we process your request."
        )
        dialog.show(page)
        # Simulate processing
        import asyncio
        async def simulate_processing():
            await asyncio.sleep(3)
            dialog.open = False
            page.update()
            # Show success notification
            toast = create_toast_notification(
                message="Processing completed successfully!",
                bgcolor=ft.Colors.GREEN_CONTAINER,
                duration=2000
            )
            toast.show(page)
        asyncio.create_task(simulate_processing())
    
    def show_toast_notification(e):
        toast = create_toast_notification(
            message="This is a toast notification!",
            duration=3000
        )
        toast.show(page)
    
    dialog_demo = ft.Column([
        ft.Text("Enhanced Dialogs", size=24, weight=ft.FontWeight.BOLD),
        ft.Text("Advanced dialogs with animations and interactions", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.Row([
            create_enhanced_button(
                text="Show Confirmation",
                icon=ft.Icons.QUESTION_MARK,
                on_click=show_confirmation_dialog
            ),
            create_enhanced_button(
                text="Show Input Dialog",
                icon=ft.Icons.INPUT,
                on_click=show_input_dialog
            ),
            create_enhanced_button(
                text="Show Progress",
                icon=ft.Icons.HOURGLASS_EMPTY,
                on_click=show_progress_dialog
            ),
            create_enhanced_button(
                text="Show Toast",
                icon=ft.Icons.NOTIFICATIONS,
                on_click=show_toast_notification
            ),
        ], spacing=20, wrap=True)
    ], spacing=16)
    
    # Add all demos to page
    page.add(
        ft.Text("Flet Enhanced Components Showcase", size=32, weight=ft.FontWeight.BOLD),
        ft.Text("Demonstration of all implemented enhanced UI components and interactions", size=16, color=ft.Colors.ON_SURFACE_VARIANT),
        ft.Divider(),
        button_demo,
        ft.Divider(),
        icon_button_demo,
        ft.Divider(),
        chip_demo,
        ft.Divider(),
        text_field_demo,
        ft.Divider(),
        card_demo,
        ft.Divider(),
        chart_demo,
        ft.Divider(),
        widget_demo,
        ft.Divider(),
        dialog_demo,
        ft.Divider(),
        ft.Text(
            "This showcase demonstrates the implemented enhanced components following "
            "Material Design 3 principles with advanced animations and interactions. "
            "All components are designed for performance, accessibility, and consistent user experience.",
            size=14,
            color=ft.Colors.ON_SURFACE_VARIANT
        )
    )


if __name__ == "__main__":
    ft.app(target=main)