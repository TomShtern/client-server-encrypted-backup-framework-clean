#!/usr/bin/env python3
"""
Enhanced Theme System Test and Demonstration
Comprehensive testing of the enhanced theme system with all features.
"""

import flet as ft
from theme_enhanced import (
    setup_enhanced_theme,
    create_gradient_button,
    create_enhanced_card,
    create_metric_card_enhanced,
    create_status_badge_enhanced,
    create_section_header_enhanced,
    create_gradient_text,
    create_rich_gradient_text,
    GRADIENTS,
    ENHANCED_COLOR_SCHEMES,
    toggle_theme_mode
)

def main(page: ft.Page):
    page.title = "Enhanced Theme System Test"
    page.scroll = ft.ScrollMode.AUTO
    page.padding = ft.padding.all(20)

    # Setup enhanced theme
    setup_enhanced_theme(page)

    # Test data
    metrics_data = [
        {
            "title": "Active Users",
            "value": "1,234",
            "change": "+12.5%",
            "icon": ft.Icons.PEOPLE,
            "color_type": "success",
            "trend": "up"
        },
        {
            "title": "Server Load",
            "value": "67%",
            "change": "-5.2%",
            "icon": ft.Icons.SERVER,
            "color_type": "warning",
            "trend": "down"
        },
        {
            "title": "Failed Requests",
            "value": "23",
            "change": "+2",
            "icon": ft.Icons.ERROR,
            "color_type": "error",
            "trend": "up"
        },
        {
            "title": "Response Time",
            "value": "124ms",
            "change": "0%",
            "icon": ft.Icons.SPEED,
            "color_type": "primary",
            "trend": "neutral"
        }
    ]

    # Build UI sections
    sections = []

    # 1. Theme Toggle Section
    sections.append(
        create_section_header_enhanced(
            "Theme Controls",
            "Test theme switching and color schemes",
            action_button=create_gradient_button(
                "Toggle Theme",
                on_click=lambda e: toggle_theme_mode(page),
                gradient_type="secondary",
                icon=ft.Icons.PALETTE
            ),
            gradient_type="primary"
        )
    )

    # 2. Gradient Text Section
    sections.append(
        create_section_header_enhanced(
            "Enhanced Typography",
            "Gradient text effects and rich formatting"
        )
    )

    sections.append(
        ft.Row([
            create_gradient_text("Primary Gradient", "primary", size=28),
            create_gradient_text("Success Gradient", "success", size=28),
            create_gradient_text("Warning Gradient", "warning", size=28),
            create_gradient_text("Error Gradient", "error", size=28),
        ], wrap=True, spacing=20)
    )

    # Rich text example
    sections.append(
        create_rich_gradient_text([
            ft.TextSpan("This is rich text with "),
            ft.TextSpan(
                "gradient effects",
                style=ft.TextStyle(
                    foreground=ft.Paint(
                        gradient=GRADIENTS["primary"],
                        style=ft.PaintingStyle.FILL,
                    ),
                    weight=ft.FontWeight.BOLD
                )
            ),
            ft.TextSpan(" and "),
            ft.TextSpan(
                "multiple styles",
                style=ft.TextStyle(
                    color=ft.Colors.PURPLE,
                    weight=ft.FontWeight.W_500,
                    italic=True
                )
            ),
            ft.TextSpan(" in a single component.")
        ])
    )

    # 3. Button Variants Section
    sections.append(
        create_section_header_enhanced(
            "Enhanced Buttons",
            "Multi-state animations and gradient styling"
        )
    )

    button_variants = []
    gradient_types = ["primary", "secondary", "success", "warning", "error"]
    variants = ["filled", "outlined", "text"]

    for variant in variants:
        row_buttons = []
        for gradient_type in gradient_types:
            row_buttons.append(
                create_gradient_button(
                    f"{gradient_type.title()} {variant.title()}",
                    gradient_type=gradient_type,
                    variant=variant,
                    icon=ft.Icons.STAR,
                    on_click=lambda e, gt=gradient_type, v=variant: print(f"Clicked {gt} {v}")
                )
            )
        button_variants.append(ft.Row(row_buttons, spacing=10, wrap=True))

    sections.extend(button_variants)

    # 4. Enhanced Cards Section
    sections.append(
        create_section_header_enhanced(
            "Enhanced Cards",
            "Nested themes and gradient backgrounds"
        )
    )

    # Test different card configurations
    test_cards = []

    # Card with gradient background
    test_cards.append(
        create_enhanced_card(
            content=ft.Column([
                ft.Text("Gradient Background Card", weight=ft.FontWeight.BOLD),
                ft.Text("This card uses a gradient background instead of solid color."),
                ft.Row([
                    create_gradient_button("Action", gradient_type="primary", variant="text"),
                    create_gradient_button("Cancel", gradient_type="error", variant="text")
                ], spacing=10)
            ], spacing=12),
            gradient_background="primary",
            hover_effect=True
        )
    )

    # Card with nested theme
    test_cards.append(
        create_enhanced_card(
            content=ft.Column([
                ft.Text("Accent Theme Card", weight=ft.FontWeight.BOLD),
                ft.Text("This card uses a nested accent theme."),
                ft.FilledButton("Themed Button")
            ], spacing=12),
            theme_variant="accent",
            hover_effect=True
        )
    )

    # Surface variant card
    test_cards.append(
        create_enhanced_card(
            content=ft.Column([
                ft.Text("Surface Variant Card", weight=ft.FontWeight.BOLD),
                ft.Text("This card uses surface variant theming for subtle appearance."),
            ], spacing=12),
            theme_variant="surface",
            hover_effect=True
        )
    )

    sections.append(ft.Row(test_cards, spacing=15, wrap=True))

    # 5. Enhanced Metrics Section
    sections.append(
        create_section_header_enhanced(
            "Enhanced Metrics Dashboard",
            "Animated metric cards with trend indicators"
        )
    )

    metrics_row = []
    for metric in metrics_data:
        metrics_row.append(
            create_metric_card_enhanced(**metric)
        )

    sections.append(ft.Row(metrics_row, spacing=15, wrap=True))

    # 6. Status Badges Section
    sections.append(
        create_section_header_enhanced(
            "Enhanced Status Badges",
            "Gradient badges with icons and animations"
        )
    )

    badge_variants = ["filled", "outlined", "gradient"]
    status_types = ["Active", "Pending", "Error", "Offline", "Success"]

    badge_rows = []
    for variant in badge_variants:
        badges = []
        for status in status_types:
            badges.append(create_status_badge_enhanced(status, variant))
        badge_rows.append(
            ft.Container(
                content=ft.Row(badges, spacing=10, wrap=True),
                padding=ft.padding.all(10),
                bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SURFACE_VARIANT),
                border_radius=8,
                margin=ft.margin.only(bottom=10)
            )
        )

    sections.extend(badge_rows)

    # 7. Interactive Demo Section
    sections.append(
        create_section_header_enhanced(
            "Interactive Demo",
            "Click buttons to test interactions"
        )
    )

    # Demo counter
    counter_text = ft.Text("Click count: 0", size=20, weight=ft.FontWeight.BOLD)

    def increment_counter(e):
        current = int(counter_text.value.split(": ")[1])
        counter_text.value = f"Click count: {current + 1}"
        counter_text.update()

    demo_content = ft.Column([
        counter_text,
        ft.Row([
            create_gradient_button(
                "Increment",
                on_click=increment_counter,
                gradient_type="success",
                icon=ft.Icons.ADD
            ),
            create_gradient_button(
                "Reset",
                on_click=lambda e: setattr(counter_text, 'value', 'Click count: 0') or counter_text.update(),
                gradient_type="warning",
                icon=ft.Icons.REFRESH
            )
        ], spacing=10),
        ft.Text("Notice the smooth animations and hover effects!",
                style=ft.TextThemeStyle.BODY_MEDIUM,
                color=ft.Colors.ON_SURFACE_VARIANT)
    ], spacing=20)

    sections.append(create_enhanced_card(demo_content, elevation=6))

    # 8. Performance Test Section
    sections.append(
        create_section_header_enhanced(
            "Performance Test",
            "Multiple animated components to test performance"
        )
    )

    performance_cards = []
    for i in range(10):
        performance_cards.append(
            create_enhanced_card(
                content=ft.Text(f"Card {i+1}", weight=ft.FontWeight.BOLD),
                gradient_background=gradient_types[i % len(gradient_types)],
                hover_effect=True
            )
        )

    sections.append(ft.Container(
        content=ft.Row(performance_cards, spacing=10, wrap=True),
        padding=ft.padding.all(20),
        bgcolor=ft.Colors.with_opacity(0.02, ft.Colors.SURFACE_VARIANT),
        border_radius=12
    ))

    # Add all sections to page
    page.add(
        ft.Column(sections, spacing=30, scroll=ft.ScrollMode.AUTO)
    )

if __name__ == "__main__":
    ft.app(target=main)