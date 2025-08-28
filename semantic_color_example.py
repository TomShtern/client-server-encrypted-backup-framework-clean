"""
Example: Semantic Color System Integration

This example demonstrates how to integrate the semantic color management system
into existing Flet components to replace hardcoded colors.
"""

import flet as ft
from flet_server_gui.core.semantic_colors import (
    get_status_color,
    get_ui_state_color, 
    get_text_color,
    get_surface_color,
    get_toast_colors,
    LegacyColorReplacements
)


def create_status_dashboard_old():
    """OLD WAY: Using hardcoded colors (before semantic color system)"""
    return ft.Column([
        ft.Text("Status Dashboard", size=24, color=ft.Colors.ON_SURFACE),
        
        # Status cards with hardcoded colors
        ft.Row([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600),
                        ft.Text("Success", color=ft.Colors.GREEN_600),
                        ft.Text("72 transfers completed", color=ft.Colors.ON_SURFACE)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20
                ),
                bgcolor=ft.Colors.SURFACE
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.ERROR_OUTLINE, color=ft.Colors.RED_600),
                        ft.Text("Errors", color=ft.Colors.RED_600), 
                        ft.Text("2 failed transfers", color=ft.Colors.ON_SURFACE)
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20
                ),
                bgcolor=ft.Colors.SURFACE
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.WARNING_OUTLINED, color=ft.Colors.ORANGE_600),
                        ft.Text("Warnings", color=ft.Colors.ORANGE_600),
                        ft.Text("5 retries needed", color=ft.Colors.ON_SURFACE) 
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20
                ),
                bgcolor=ft.Colors.SURFACE
            )
        ]),
        
        # Action buttons with hardcoded colors
        ft.Row([
            ft.ElevatedButton(
                "Start Server", 
                bgcolor=ft.Colors.GREEN_600,
                color=ft.Colors.WHITE
            ),
            ft.ElevatedButton(
                "Stop Server",
                bgcolor=ft.Colors.RED_600, 
                color=ft.Colors.WHITE
            ),
            ft.OutlinedButton(
                "Refresh",
                style=ft.ButtonStyle(color=ft.Colors.BLUE_600)
            )
        ])
    ])


def create_status_dashboard_new():
    """NEW WAY: Using semantic color system (recommended)"""
    return ft.Column([
        ft.Text("Status Dashboard", size=24, color=get_text_color("primary")),
        
        # Status cards with semantic colors
        ft.Row([
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.CHECK_CIRCLE, color=get_status_color("success")),
                        ft.Text("Success", color=get_status_color("success")),
                        ft.Text("72 transfers completed", color=get_text_color("primary"))
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20
                ),
                bgcolor=get_surface_color("card")
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.ERROR_OUTLINE, color=get_status_color("error")),
                        ft.Text("Errors", color=get_status_color("error")), 
                        ft.Text("2 failed transfers", color=get_text_color("primary"))
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20
                ),
                bgcolor=get_surface_color("card")
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.WARNING_OUTLINED, color=get_status_color("warning")),
                        ft.Text("Warnings", color=get_status_color("warning")),
                        ft.Text("5 retries needed", color=get_text_color("primary")) 
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    padding=20
                ),
                bgcolor=get_surface_color("card")
            )
        ]),
        
        # Action buttons with semantic colors
        ft.Row([
            ft.ElevatedButton(
                "Start Server", 
                bgcolor=get_status_color("success"),
                color=get_text_color("inverse")
            ),
            ft.ElevatedButton(
                "Stop Server",
                bgcolor=get_status_color("error"), 
                color=get_text_color("inverse")
            ),
            ft.OutlinedButton(
                "Refresh",
                style=ft.ButtonStyle(color=get_status_color("info"))
            )
        ])
    ])


def create_interactive_table_old():
    """OLD WAY: Table with hardcoded hover/selection colors"""
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Client", color=ft.Colors.ON_SURFACE)),
            ft.DataColumn(ft.Text("Status", color=ft.Colors.ON_SURFACE)),
            ft.DataColumn(ft.Text("Files", color=ft.Colors.ON_SURFACE)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("client-001")),
                    ft.DataCell(ft.Icon(ft.icons.CHECK_CIRCLE, color=ft.Colors.GREEN_600)),
                    ft.DataCell(ft.Text("15")),
                ],
                # Hardcoded hover color
                on_select_changed=lambda e: print("Selected"),
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("client-002")),
                    ft.DataCell(ft.Icon(ft.icons.ERROR_OUTLINE, color=ft.Colors.RED_600)),
                    ft.DataCell(ft.Text("8")),
                ],
                on_select_changed=lambda e: print("Selected"),
            ),
        ]
    )


def create_interactive_table_new():
    """NEW WAY: Table with semantic hover/selection colors"""
    return ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Client", color=get_text_color("primary"))),
            ft.DataColumn(ft.Text("Status", color=get_text_color("primary"))),
            ft.DataColumn(ft.Text("Files", color=get_text_color("primary"))),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("client-001")),
                    ft.DataCell(ft.Icon(ft.icons.CHECK_CIRCLE, color=get_status_color("success"))),
                    ft.DataCell(ft.Text("15")),
                ],
                on_select_changed=lambda e: print("Selected"),
            ),
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("client-002")),
                    ft.DataCell(ft.Icon(ft.icons.ERROR_OUTLINE, color=get_status_color("error"))),
                    ft.DataCell(ft.Text("8")),
                ],
                on_select_changed=lambda e: print("Selected"),
            ),
        ]
    )


def create_toast_notification_old(message: str, toast_type: str):
    """OLD WAY: Toast with hardcoded colors"""
    color_map = {
        "success": ft.Colors.GREEN_600,
        "error": ft.Colors.RED_600,
        "warning": ft.Colors.ORANGE_600,
        "info": ft.Colors.BLUE_600,
    }
    
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.INFO, color=color_map.get(toast_type, ft.Colors.GREY_600)),
            ft.Text(message, color=ft.Colors.ON_SURFACE)
        ]),
        bgcolor=ft.Colors.SURFACE,
        border=ft.border.all(1, color_map.get(toast_type, ft.Colors.GREY_600)),
        border_radius=8,
        padding=10
    )


def create_toast_notification_new(message: str, toast_type: str):
    """NEW WAY: Toast with semantic colors"""
    toast_colors = get_toast_colors(toast_type)
    
    return ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.INFO, color=toast_colors["icon"]),
            ft.Text(message, color=toast_colors["text"])
        ]),
        bgcolor=toast_colors["background"],
        border=ft.border.all(1, toast_colors["border"]),
        border_radius=8,
        padding=10
    )


def create_theme_aware_component():
    """Example of theme-aware component"""
    def create_button_for_theme(theme_mode: str):
        return ft.ElevatedButton(
            f"{theme_mode.title()} Theme Button",
            bgcolor=get_ui_state_color("button", "default", theme_mode),
            color=get_text_color("inverse", theme_mode)
        )
    
    return ft.Column([
        ft.Text("Theme-Aware Components:", size=18, color=get_text_color("primary")),
        ft.Row([
            create_button_for_theme("light"),
            create_button_for_theme("dark")
        ]),
        
        # Performance indicators with semantic colors
        ft.Text("Performance Levels:", size=18, color=get_text_color("primary")),
        ft.Row([
            ft.Container(
                content=ft.Text("Excellent", color=get_text_color("inverse")),
                bgcolor=get_status_color("success"),
                padding=8,
                border_radius=4
            ),
            ft.Container(
                content=ft.Text("Average", color=get_text_color("inverse")),
                bgcolor=get_status_color("warning"), 
                padding=8,
                border_radius=4
            ),
            ft.Container(
                content=ft.Text("Poor", color=get_text_color("inverse")),
                bgcolor=get_status_color("error"),
                padding=8,
                border_radius=4
            )
        ])
    ])


def create_legacy_replacement_example():
    """Example using legacy replacement methods for quick migration"""
    return ft.Column([
        ft.Text("Legacy Replacement Example:", size=18, color=get_text_color("primary")),
        
        # Using legacy replacements for quick migration
        ft.Row([
            ft.Container(
                content=ft.Text("Success", color=get_text_color("inverse")),
                bgcolor=LegacyColorReplacements.GREEN_600(),
                padding=10
            ),
            ft.Container(
                content=ft.Text("Error", color=get_text_color("inverse")),
                bgcolor=LegacyColorReplacements.RED_600(),
                padding=10
            ),
            ft.Container(
                content=ft.Text("Warning", color=get_text_color("inverse")),
                bgcolor=LegacyColorReplacements.ORANGE_600(),
                padding=10
            ),
            ft.Container(
                content=ft.Text("Info", color=get_text_color("inverse")),
                bgcolor=LegacyColorReplacements.BLUE_600(),
                padding=10
            )
        ])
    ])


def main(page: ft.Page):
    """Main function to demonstrate the semantic color system"""
    page.title = "Semantic Color System Examples"
    page.scroll = ft.ScrollMode.AUTO
    
    page.add(
        ft.Text("Semantic Color System Integration Examples", 
                size=24, 
                weight=ft.FontWeight.BOLD,
                color=get_text_color("primary")),
        
        ft.Divider(color=get_ui_state_color("row", "alternate")),
        
        ft.Text("Status Dashboard Comparison:", 
                size=18, 
                weight=ft.FontWeight.W_500,
                color=get_text_color("primary")),
        
        ft.ExpansionTile(
            title=ft.Text("NEW: Semantic Colors", color=get_status_color("success")),
            controls=[create_status_dashboard_new()]
        ),
        
        ft.ExpansionTile(
            title=ft.Text("OLD: Hardcoded Colors", color=get_status_color("error")),
            controls=[create_status_dashboard_old()]
        ),
        
        ft.Divider(color=get_ui_state_color("row", "alternate")),
        
        create_theme_aware_component(),
        
        ft.Divider(color=get_ui_state_color("row", "alternate")),
        
        create_legacy_replacement_example(),
        
        ft.Divider(color=get_ui_state_color("row", "alternate")),
        
        ft.Text("Toast Notifications:", size=18, color=get_text_color("primary")),
        ft.Column([
            create_toast_notification_new("Success message", "success"),
            create_toast_notification_new("Error occurred", "error"),
            create_toast_notification_new("Warning notice", "warning"),
            create_toast_notification_new("Information", "info"),
        ], spacing=10)
    )


if __name__ == "__main__":
    # This example requires flet to be installed
    # Run with: python semantic_color_example.py
    try:
        ft.app(target=main)
    except ImportError:
        print("This example requires 'flet' to be installed.")
        print("Install with: pip install flet")
        print("Or run from the flet_venv virtual environment.")