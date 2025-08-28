#!/usr/bin/env python3
"""
Material Design 3 Component Factory Demo
========================================

This demo showcases the M3 component factory functionality and validates
integration with the existing theme system.

Usage:
    python flet_server_gui/demo_m3_components.py
"""

import flet as ft
import asyncio
from ui.m3_components import (
    M3ComponentFactory, ComponentStyle, M3ButtonConfig, M3CardConfig,
    get_m3_factory, create_m3_button, create_m3_card, create_m3_text_field
)
from core.theme_system import ThemeMode, get_theme_system


def main(page: ft.Page):
    """Demo application main function"""
    page.title = "Material Design 3 Component Factory Demo"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Get the M3 factory instance
    factory = get_m3_factory()
    
    def create_button_showcase():
        """Create showcase of all button types"""
        buttons = []
        
        # Button click handler
        def on_button_click(e):
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Clicked {e.control.text} button!"),
                    action="OK"
                )
            )
        
        # Create all button styles
        styles = [
            ("filled", "Filled Button"),
            ("outlined", "Outlined Button"),
            ("text", "Text Button"),
            ("elevated", "Elevated Button"),
            ("tonal", "Tonal Button")
        ]
        
        for style, text in styles:
            button = factory.create_button(
                style=style,
                text=text,
                icon=ft.Icons.STAR,
                on_click=on_button_click
            )
            buttons.append(button)
        
        # Create buttons with different configurations
        config_button = factory.create_button(
            style="filled",
            config=M3ButtonConfig(
                style=ComponentStyle.FILLED,
                text="Custom Config Button",
                icon=ft.Icons.SETTINGS,
                size="large",
                full_width=False,
                on_click=on_button_click
            )
        )
        buttons.append(config_button)
        
        return ft.Column(
            [
                ft.Text("Button Showcase", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Text("All Material Design 3 button variants", style=ft.TextThemeStyle.BODY_MEDIUM),
                ft.Divider(),
                *buttons,
            ],
            spacing=10
        )
    
    def create_card_showcase():
        """Create showcase of all card types"""
        cards = []
        
        # Card click handler
        def on_card_click(e):
            page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Card clicked!"))
            )
        
        # Sample content for cards
        sample_content = ft.Column([
            ft.Text("Card Content", weight=ft.FontWeight.BOLD),
            ft.Text("This is some sample content inside the card."),
            ft.Text("Material Design 3 cards support rich content.")
        ])
        
        # Create all card styles
        styles = [
            ("elevated", "Elevated Card"),
            ("filled", "Filled Card"), 
            ("outlined", "Outlined Card")
        ]
        
        for style, title in styles:
            card = factory.create_card(
                style=style,
                title=title,
                subtitle=f"This is a {style} card example",
                content=ft.Text("Sample card content with proper M3 styling."),
                config=M3CardConfig(
                    style=ComponentStyle(f"{style}_card"),
                    clickable=True,
                    on_click=on_card_click,
                    actions=[
                        factory.create_button("text", "Action 1", on_click=on_card_click),
                        factory.create_button("text", "Action 2", on_click=on_card_click)
                    ]
                )
            )
            cards.append(card)
        
        return ft.Column(
            [
                ft.Text("Card Showcase", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Text("All Material Design 3 card variants", style=ft.TextThemeStyle.BODY_MEDIUM),
                ft.Divider(),
                *cards,
            ],
            spacing=10
        )
    
    def create_input_showcase():
        """Create showcase of input components"""
        inputs = []
        
        # Text field
        text_field = factory.create_text_field(
            label="M3 Text Field",
            hint_text="Enter some text here..."
        )
        inputs.append(text_field)
        
        # Dropdown
        dropdown = factory.create_dropdown(
            label="M3 Dropdown",
            options=[
                ft.dropdown.Option("Option 1"),
                ft.dropdown.Option("Option 2"),
                ft.dropdown.Option("Option 3"),
            ]
        )
        inputs.append(dropdown)
        
        # Checkbox
        checkbox = factory.create_checkbox(
            label="M3 Checkbox",
            value=True
        )
        inputs.append(checkbox)
        
        # Switch
        switch = factory.create_switch(
            label="M3 Switch",
            value=False
        )
        inputs.append(switch)
        
        return ft.Column(
            [
                ft.Text("Input Component Showcase", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Text("Material Design 3 input components", style=ft.TextThemeStyle.BODY_MEDIUM),
                ft.Divider(),
                *inputs,
            ],
            spacing=10
        )
    
    def create_data_display_showcase():
        """Create showcase of data display components"""
        # Sample data table
        columns = [
            ft.DataColumn(ft.Text("Name")),
            ft.DataColumn(ft.Text("Age")),
            ft.DataColumn(ft.Text("City")),
        ]
        
        rows = [
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("John Doe")),
                ft.DataCell(ft.Text("25")),
                ft.DataCell(ft.Text("New York")),
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("Jane Smith")),
                ft.DataCell(ft.Text("30")),
                ft.DataCell(ft.Text("London")),
            ]),
            ft.DataRow(cells=[
                ft.DataCell(ft.Text("Bob Wilson")),
                ft.DataCell(ft.Text("35")),
                ft.DataCell(ft.Text("Tokyo")),
            ]),
        ]
        
        table = factory.create_data_table(columns, rows)
        
        # List tiles
        list_tiles = [
            factory.create_list_tile(
                title="List Item 1",
                subtitle="This is a subtitle",
                leading=ft.Icon(ft.Icons.PERSON),
                trailing=ft.Icon(ft.Icons.ARROW_FORWARD_IOS)
            ),
            factory.create_list_tile(
                title="List Item 2", 
                subtitle="Another subtitle",
                leading=ft.Icon(ft.Icons.SETTINGS),
                trailing=ft.Icon(ft.Icons.ARROW_FORWARD_IOS)
            ),
        ]
        
        return ft.Column(
            [
                ft.Text("Data Display Showcase", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
                ft.Text("Material Design 3 data components", style=ft.TextThemeStyle.BODY_MEDIUM),
                ft.Divider(),
                ft.Text("Data Table:", weight=ft.FontWeight.BOLD),
                table,
                ft.Text("List Tiles:", weight=ft.FontWeight.BOLD),
                *list_tiles,
            ],
            spacing=10
        )
    
    def toggle_theme(e):
        """Toggle between light and dark theme"""
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            get_theme_system().switch_theme(ThemeMode.LIGHT)
        else:
            page.theme_mode = ft.ThemeMode.DARK
            get_theme_system().switch_theme(ThemeMode.DARK)
        page.update()
    
    # Create theme toggle button
    theme_toggle = ft.IconButton(
        icon=ft.Icons.BRIGHTNESS_6,
        tooltip="Toggle Theme",
        on_click=toggle_theme
    )
    
    # Create the main layout
    page.add(
        ft.Column([
            # Header
            ft.Row([
                ft.Text(
                    "Material Design 3 Component Factory Demo",
                    style=ft.TextThemeStyle.HEADLINE_LARGE,
                    expand=True
                ),
                theme_toggle
            ]),
            ft.Divider(),
            
            # Component showcases
            ft.ResponsiveRow([
                ft.Column([
                    create_button_showcase(),
                    ft.Divider(),
                    create_input_showcase(),
                ], col={"sm": 12, "md": 6}, expand=True),
                
                ft.Column([
                    create_card_showcase(),
                    ft.Divider(), 
                    create_data_display_showcase(),
                ], col={"sm": 12, "md": 6}, expand=True),
            ]),
            
            # Footer
            ft.Divider(),
            ft.Text(
                "This demo showcases the M3ComponentFactory integration with the existing theme system.",
                style=ft.TextThemeStyle.BODY_SMALL,
                text_align=ft.TextAlign.CENTER
            )
        ])
    )


if __name__ == "__main__":
    print("🎨 Starting Material Design 3 Component Factory Demo...")
    print("📱 This demo showcases all M3 components with theme integration")
    print("🔧 Components are fully integrated with the existing theme system")
    print("✨ Toggle between light and dark themes to see M3 color adaptation")
    
    try:
        ft.app(target=main, port=8888)
        print("✅ Demo completed successfully!")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("💡 Make sure all dependencies are installed and the theme system is working")