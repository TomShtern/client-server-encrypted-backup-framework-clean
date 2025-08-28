#!/usr/bin/env python3
"""
M3 Component Factory Integration Example
=======================================

This example shows how to integrate the new M3 Component Factory
with your existing button factory and component systems.

Usage:
    python flet_server_gui/integration_example_m3.py
"""

import flet as ft
from ui.m3_components import get_m3_factory, M3ButtonConfig, M3CardConfig, ComponentStyle
from ui.widgets.buttons import ActionButtonFactory, ButtonConfig


def create_comparison_demo():
    """Create a demo comparing existing and M3 components"""
    
    # Get the M3 factory
    m3_factory = get_m3_factory()
    
    # Get existing action button factory
    action_factory = ActionButtonFactory()
    
    def on_click_handler(e):
        print(f"Button clicked: {e.control.text}")
    
    # Create comparison components
    components = []
    
    # === Button Comparison ===
    components.append(ft.Text("Button Comparison", style=ft.TextThemeStyle.HEADLINE_MEDIUM))
    components.append(ft.Divider())
    
    # M3 Buttons
    m3_buttons = ft.Row([
        m3_factory.create_button(
            style="filled",
            text="M3 Filled",
            icon=ft.Icons.STAR,
            on_click=on_click_handler
        ),
        m3_factory.create_button(
            style="outlined", 
            text="M3 Outlined",
            icon=ft.Icons.FAVORITE,
            on_click=on_click_handler
        ),
        m3_factory.create_button(
            style="elevated",
            text="M3 Elevated",
            icon=ft.Icons.SETTINGS,
            on_click=on_click_handler
        ),
    ], spacing=10)
    
    components.append(ft.Text("M3 Component Factory Buttons:", weight=ft.FontWeight.BOLD))
    components.append(m3_buttons)
    
    # Standard Flet buttons for comparison
    standard_buttons = ft.Row([
        ft.FilledButton("Standard Filled", icon=ft.Icons.STAR, on_click=on_click_handler),
        ft.OutlinedButton("Standard Outlined", icon=ft.Icons.FAVORITE, on_click=on_click_handler),
        ft.ElevatedButton("Standard Elevated", icon=ft.Icons.SETTINGS, on_click=on_click_handler),
    ], spacing=10)
    
    components.append(ft.Text("Standard Flet Buttons:", weight=ft.FontWeight.BOLD))
    components.append(standard_buttons)
    
    # === Card Comparison ===
    components.append(ft.Text("Card Comparison", style=ft.TextThemeStyle.HEADLINE_MEDIUM))
    components.append(ft.Divider())
    
    # M3 Cards
    m3_cards = ft.Row([
        m3_factory.create_card(
            style="elevated",
            title="M3 Elevated Card",
            subtitle="With proper M3 styling",
            content=ft.Text("This card follows Material Design 3 specifications.")
        ),
        m3_factory.create_card(
            style="filled",
            title="M3 Filled Card", 
            subtitle="Surface variant background",
            content=ft.Text("This card uses M3 filled card styling.")
        ),
        m3_factory.create_card(
            style="outlined",
            title="M3 Outlined Card",
            subtitle="With border outline",
            content=ft.Text("This card has M3 outlined styling.")
        ),
    ], spacing=10, expand=True)
    
    components.append(ft.Text("M3 Component Factory Cards:", weight=ft.FontWeight.BOLD))
    components.append(m3_cards)
    
    # Standard Flet card for comparison
    standard_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Standard Flet Card", weight=ft.FontWeight.BOLD),
                ft.Text("Without M3 specific styling"),
                ft.Text("Uses default Flet card appearance.")
            ]),
            padding=16
        )
    )
    
    components.append(ft.Text("Standard Flet Card:", weight=ft.FontWeight.BOLD))
    components.append(standard_card)
    
    # === Input Components ===
    components.append(ft.Text("Input Component Examples", style=ft.TextThemeStyle.HEADLINE_MEDIUM))
    components.append(ft.Divider())
    
    input_components = ft.Column([
        m3_factory.create_text_field(
            label="M3 Text Field",
            hint_text="Enter your text here..."
        ),
        m3_factory.create_dropdown(
            label="M3 Dropdown",
            options=[
                ft.dropdown.Option("Option 1"),
                ft.dropdown.Option("Option 2"),
                ft.dropdown.Option("Option 3"),
            ]
        ),
        ft.Row([
            m3_factory.create_checkbox(label="M3 Checkbox", value=True),
            m3_factory.create_switch(label="M3 Switch", value=False),
        ]),
    ], spacing=10)
    
    components.append(input_components)
    
    return ft.Column(components, spacing=15, scroll=ft.ScrollMode.AUTO)


def main(page: ft.Page):
    """Main demo application"""
    page.title = "M3 Component Factory Integration Example"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    
    # Create theme toggle
    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
        else:
            page.theme_mode = ft.ThemeMode.DARK
        page.update()
    
    # Header with theme toggle
    header = ft.Row([
        ft.Text(
            "M3 Component Factory Integration",
            style=ft.TextThemeStyle.HEADLINE_LARGE,
            expand=True
        ),
        ft.IconButton(
            icon=ft.Icons.BRIGHTNESS_6,
            tooltip="Toggle Theme",
            on_click=toggle_theme
        )
    ])
    
    # Usage instructions
    instructions = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Text("Integration Usage:", weight=ft.FontWeight.BOLD),
                ft.Text("• Import: from ui.m3_components import get_m3_factory"),
                ft.Text("• Factory: factory = get_m3_factory()"),
                ft.Text("• Buttons: factory.create_button('filled', 'Text', icon=ft.Icons.STAR)"),
                ft.Text("• Cards: factory.create_card('elevated', title='Title', content=content)"),
                ft.Text("• Inputs: factory.create_text_field('Label', hint_text='Hint')"),
                ft.Text("• Theme Integration: Automatically uses your existing theme system"),
                ft.Text("• Responsive: All components support responsive design"),
            ], spacing=5),
            padding=16
        )
    )
    
    # Add all content
    page.add(
        ft.Column([
            header,
            ft.Divider(),
            instructions,
            ft.Divider(),
            create_comparison_demo()
        ])
    )


if __name__ == "__main__":
    print("🎨 M3 Component Factory Integration Example")
    print("📱 This demo shows how to integrate M3 components with existing systems")
    print("🔧 All components are theme-aware and responsive")
    print("✨ Toggle theme to see Material Design 3 color adaptation")
    
    try:
        ft.app(target=main, port=8889)
        print("✅ Integration example completed successfully!")
    except Exception as e:
        print(f"❌ Integration example failed: {e}")
        print("💡 Make sure the M3 component factory is properly set up")