#!/usr/bin/env python3
"""
Standardized Responsive Layouts for FletV2
Provides consistent responsive layout patterns across all views.

This eliminates inconsistencies and provides a unified responsive design system.
"""

import flet as ft
from typing import List, Dict, Any, Optional


# Standardized responsive breakpoints
RESPONSIVE_BREAKPOINTS = {
    "xs": {"sm": 12, "md": 12, "lg": 12},  # Full width on all screens
    "sm": {"sm": 12, "md": 6, "lg": 4},    # Half width on medium+, third on large
    "md": {"sm": 12, "md": 6, "lg": 3},    # Half width on medium+, quarter on large
    "lg": {"sm": 6, "md": 4, "lg": 3},     # Half on small, third on medium, quarter on large
    "xl": {"sm": 6, "md": 3, "lg": 2},     # Half on small, quarter on medium+, sixth on large
}


def create_responsive_card(
    content: ft.Control,
    size: str = "md",
    title: Optional[str] = None,
    padding: int = 20,
    elevation: int = 2
) -> ft.Column:
    """
    Create a responsive card with consistent styling.
    
    Args:
        content: Content to put in the card
        size: Responsive size key from RESPONSIVE_BREAKPOINTS
        title: Optional title for the card
        padding: Internal padding for the card
        elevation: Card elevation/shadow
    
    Returns:
        Column with responsive card
    """
    card_content = []
    
    if title:
        card_content.append(
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD)
        )
        card_content.append(ft.Divider(height=10))
    
    card_content.append(content)
    
    return ft.Column([
        ft.Card(
            content=ft.Container(
                content=ft.Column(card_content, spacing=10),
                padding=padding
            ),
            elevation=elevation
        )
    ], col=RESPONSIVE_BREAKPOINTS.get(size, RESPONSIVE_BREAKPOINTS["md"]))


def create_metrics_row(metrics: List[Dict[str, Any]], card_size: str = "lg") -> ft.ResponsiveRow:
    """
    Create a responsive row of metric cards.
    
    Args:
        metrics: List of metric dictionaries with keys: title, value, icon, color
        card_size: Size category for responsive behavior
    
    Returns:
        ResponsiveRow with metric cards
    """
    cards = []
    
    for metric in metrics:
        title = metric.get("title", "Metric")
        value = metric.get("value", "0")
        icon = metric.get("icon", ft.Icons.INFO)
        color = metric.get("color", ft.Colors.PRIMARY)
        
        card_content = ft.Row([
            ft.Icon(icon, color=color, size=24),
            ft.Column([
                ft.Text(str(value), size=24, weight=ft.FontWeight.BOLD, color=color),
                ft.Text(title, size=12, color=ft.Colors.ON_SURFACE)
            ], spacing=2, expand=True)
        ], alignment=ft.MainAxisAlignment.START)
        
        cards.append(create_responsive_card(card_content, card_size))
    
    return ft.ResponsiveRow(cards)


def create_data_table_container(
    table: ft.DataTable,
    title: str = "Data",
    search_field: Optional[ft.TextField] = None,
    action_buttons: Optional[List[ft.Control]] = None,
    status_text: Optional[ft.Text] = None
) -> ft.Container:
    """
    Create a standardized data table container with consistent layout.
    
    Args:
        table: The data table control
        title: Title for the table section
        search_field: Optional search field
        action_buttons: Optional list of action buttons
        status_text: Optional status text
    
    Returns:
        Container with standardized table layout
    """
    header_controls = [ft.Text(title, size=20, weight=ft.FontWeight.BOLD)]
    
    if search_field or action_buttons:
        row_controls = []
        if search_field:
            row_controls.append(ft.Container(search_field, expand=True))
        if action_buttons:
            row_controls.extend(action_buttons)
        
        header_controls.append(
            ft.Row(row_controls, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )
    
    content = [
        ft.Column(header_controls, spacing=15),
        ft.Divider(),
        ft.Container(
            table,
            expand=True,
            padding=ft.Padding(0, 10, 0, 0)
        )
    ]
    
    if status_text:
        content.append(status_text)
    
    return ft.Container(
        content=ft.Column(content, expand=True, scroll=ft.ScrollMode.AUTO),
        padding=20,
        expand=True
    )


def create_settings_section(
    title: str,
    controls: List[ft.Control],
    description: Optional[str] = None
) -> ft.Card:
    """
    Create a standardized settings section.
    
    Args:
        title: Section title
        controls: List of setting controls
        description: Optional description text
    
    Returns:
        Card with standardized settings layout
    """
    content = [
        ft.Text(title, size=18, weight=ft.FontWeight.BOLD),
    ]
    
    if description:
        content.append(
            ft.Text(description, size=12, color=ft.Colors.ON_SURFACE, italic=True)
        )
    
    content.append(ft.Divider())
    content.extend(controls)
    
    return ft.Card(
        content=ft.Container(
            content=ft.Column(content, spacing=15),
            padding=20
        )
    )


def create_action_bar(
    primary_actions: List[ft.Control],
    secondary_actions: Optional[List[ft.Control]] = None,
    status_control: Optional[ft.Control] = None
) -> ft.Container:
    """
    Create a standardized action bar.
    
    Args:
        primary_actions: Main action buttons (left side)
        secondary_actions: Secondary actions (right side)
        status_control: Status indicator (center)
    
    Returns:
        Container with action bar layout
    """
    left_section = ft.Row(primary_actions, spacing=10) if primary_actions else ft.Container()
    center_section = status_control if status_control else ft.Container()
    right_section = ft.Row(secondary_actions, spacing=10) if secondary_actions else ft.Container()
    
    return ft.Container(
        content=ft.Row([
            left_section,
            ft.Container(center_section, expand=True),
            right_section
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.Padding(20, 10, 20, 10),
        bgcolor=ft.Colors.SURFACE,
        border=ft.Border(
            bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)
        )
    )


# Standard spacing and padding values
SPACING = {
    "xs": 5,
    "sm": 10,
    "md": 15,
    "lg": 20,
    "xl": 30
}

PADDING = {
    "xs": ft.Padding(5, 5, 5, 5),
    "sm": ft.Padding(10, 10, 10, 10),
    "md": ft.Padding(15, 15, 15, 15),
    "lg": ft.Padding(20, 20, 20, 20),
    "xl": ft.Padding(30, 30, 30, 30)
}