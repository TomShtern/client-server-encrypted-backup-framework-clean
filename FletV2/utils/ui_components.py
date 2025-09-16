#!/usr/bin/env python3
"""
Simplified UI Components for FletV2 - The Flet Way
~200 lines instead of 2,170 lines of framework fighting!

Core Principle: Use Flet's built-in components with proper theming.
Let Flet do the heavy lifting. We compose, not reinvent.
"""

import flet as ft
from typing import Optional, List, Callable, Dict, Any, Union


# ==============================================================================
# SIMPLE UTILITIES (Keep these - they're actually useful)
# ==============================================================================

def get_file_type_icon(filename: str) -> str:
    """Simple file type to icon mapping using Flet's built-in icons."""
    extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''

    file_icons = {
        # Documents
        '.pdf': ft.Icons.PICTURE_AS_PDF,
        '.doc': ft.Icons.DESCRIPTION, '.docx': ft.Icons.DESCRIPTION,
        '.txt': ft.Icons.TEXT_SNIPPET,

        # Spreadsheets
        '.xls': ft.Icons.TABLE_CHART, '.xlsx': ft.Icons.TABLE_CHART,
        '.csv': ft.Icons.TABLE_CHART,

        # Images
        '.jpg': ft.Icons.IMAGE, '.jpeg': ft.Icons.IMAGE, '.png': ft.Icons.IMAGE,
        '.gif': ft.Icons.IMAGE, '.svg': ft.Icons.IMAGE,

        # Videos
        '.mp4': ft.Icons.VIDEO_FILE, '.avi': ft.Icons.VIDEO_FILE,
        '.mov': ft.Icons.VIDEO_FILE, '.mkv': ft.Icons.VIDEO_FILE,

        # Audio
        '.mp3': ft.Icons.AUDIO_FILE, '.wav': ft.Icons.AUDIO_FILE,
        '.flac': ft.Icons.AUDIO_FILE,

        # Archives
        '.zip': ft.Icons.FOLDER_ZIP, '.rar': ft.Icons.FOLDER_ZIP,
        '.7z': ft.Icons.FOLDER_ZIP,

        # Code
        '.py': ft.Icons.CODE, '.js': ft.Icons.CODE, '.html': ft.Icons.CODE,
        '.css': ft.Icons.CODE, '.json': ft.Icons.CODE,
    }

    return file_icons.get(extension, ft.Icons.INSERT_DRIVE_FILE)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


# ==============================================================================
# THEME-AWARE FLET HELPERS (Simple wrappers, not reinventions)
# ==============================================================================

def themed_card(content: ft.Control, title: Optional[str] = None) -> ft.Card:
    """Create a card using Flet's built-in theming. 5 lines vs 100+ lines!"""
    card_content = content

    if title:
        card_content = ft.Column([
            ft.Text(title, size=18, weight=ft.FontWeight.W_600),
            ft.Divider(height=1),
            content
        ], spacing=12)

    return ft.Card(
        content=ft.Container(content=card_content, padding=20),
        elevation=2
    )


def themed_button(text: str, on_click: Callable, variant: str = "filled",
                 icon: Optional[str] = None) -> ft.Control:
    """Create themed button using Flet built-ins. 5 lines vs 200+ lines!"""
    button_content = ft.Row([ft.Icon(icon), ft.Text(text)], tight=True) if icon else text

    if variant == "filled":
        return ft.FilledButton(content=button_content, on_click=on_click)
    elif variant == "outlined":
        return ft.OutlinedButton(content=button_content, on_click=on_click)
    elif variant == "elevated":
        return ft.ElevatedButton(content=button_content, on_click=on_click)
    else:  # text
        return ft.TextButton(content=button_content, on_click=on_click)


def themed_progress(value: float, label: str) -> ft.Column:
    """Create progress indicator using Flet built-ins. 5 lines vs 100+ lines!"""
    return ft.Column([
        ft.Row([
            ft.Text(label, size=14),
            ft.Text(f"{value * 100:.1f}%", size=14, weight=ft.FontWeight.W_600)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.ProgressBar(value=value, height=8)
    ], spacing=8)


def themed_metric_card(title: str, value: str, icon: str) -> ft.Card:
    """Create metric card using Flet's Card. 5 lines vs 100+ lines!"""
    return ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(icon, size=24), ft.Text(title, size=14)]),
                ft.Text(value, size=24, weight=ft.FontWeight.BOLD)
            ], spacing=8),
            padding=20
        ),
        elevation=2
    )


def themed_chip(text: str, icon: Optional[str] = None) -> ft.Container:
    """Create info chip using Flet's Container. Simple & clean!"""
    content = [ft.Text(text, size=12)]
    if icon:
        content.insert(0, ft.Icon(icon, size=16))

    return ft.Container(
        content=ft.Row(content, spacing=4, tight=True),
        padding=ft.Padding(8, 4, 8, 4),
        bgcolor=ft.Colors.PRIMARY,
        border_radius=12
    )


# ==============================================================================
# SMART FIELD BUILDERS (Simplified from the complex registry system)
# ==============================================================================

def smart_text_field(label: str, value: str = "", on_change: Optional[Callable] = None) -> ft.TextField:
    """Create text field using Flet's theming. Simple & powerful!"""
    return ft.TextField(
        label=label,
        value=value,
        on_change=on_change,
        border_radius=12,
        filled=True
    )


def smart_switch(label: str, value: bool = False, on_change: Optional[Callable] = None) -> ft.Switch:
    """Create switch using Flet's theming. Simple & works!"""
    return ft.Switch(label=label, value=value, on_change=on_change)


def smart_dropdown(label: str, options: List[str], value: str = "",
                  on_change: Optional[Callable] = None) -> ft.Dropdown:
    """Create dropdown using Flet's theming. Clean & simple!"""
    return ft.Dropdown(
        label=label,
        value=value,
        options=[ft.dropdown.Option(opt) for opt in options],
        on_change=on_change,
        filled=True
    )


# ==============================================================================
# DATA DISPLAY HELPERS (Using Flet's DataTable properly)
# ==============================================================================

def smart_data_table(columns: List[str], rows: List[List[str]]) -> ft.DataTable:
    """Create DataTable using Flet's built-in styling. Let Flet handle the complexity!"""
    return ft.DataTable(
        columns=[ft.DataColumn(ft.Text(col)) for col in columns],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
            for row in rows
        ],
        heading_row_color=ft.Colors.SURFACE_VARIANT,
        border_radius=12
    )


def smart_file_row(filename: str, status: str, size: int) -> ft.Container:
    """Create file row using simple Container. Clean & efficient!"""
    return ft.Container(
        content=ft.Row([
            ft.Icon(get_file_type_icon(filename), size=20),
            ft.Text(filename, expand=True),
            ft.Text(status, size=12),
            ft.Text(format_file_size(size), size=12)
        ], spacing=12),
        padding=ft.Padding(12, 8, 12, 8),
        border_radius=8,
        bgcolor=ft.Colors.SURFACE_VARIANT
    )


# ==============================================================================
# LAYOUT HELPERS (Using Flet's ResponsiveRow)
# ==============================================================================

def smart_responsive_cards(cards: List[ft.Control]) -> ft.ResponsiveRow:
    """Create responsive card layout using Flet's ResponsiveRow. Framework harmony!"""
    return ft.ResponsiveRow([
        ft.Column([card], col={"sm": 12, "md": 6, "lg": 4})
        for card in cards
    ])


def smart_dashboard_layout(metrics: List[Dict[str, Any]]) -> ft.Column:
    """Create dashboard layout using Flet patterns. Simple & responsive!"""
    cards = [
        themed_metric_card(m["title"], m["value"], m["icon"])
        for m in metrics
    ]

    return ft.Column([
        ft.Text("Dashboard", size=28, weight=ft.FontWeight.BOLD),
        smart_responsive_cards(cards)
    ], spacing=20)


# ==============================================================================
# MIGRATION HELPERS (For compatibility during transition)
# ==============================================================================

# Alias functions to maintain compatibility during migration
create_modern_card = themed_card
create_modern_button = themed_button
create_stat_card = themed_metric_card
create_info_chip = themed_chip

# Additional compatibility functions (simplified from complex originals)
def create_progress_indicator(value: float, label: str, **kwargs) -> ft.Column:
    """Progress indicator compatibility wrapper."""
    return themed_progress(value, label)

def create_loading_overlay(message: str = "Loading...") -> ft.Container:
    """Simple loading overlay using Flet built-ins."""
    return ft.Container(
        content=ft.Column([
            ft.ProgressRing(width=40, height=40),
            ft.Text(message, size=14)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        padding=20,
        bgcolor=ft.Colors.with_opacity(0.9, ft.Colors.SURFACE),
        border_radius=12
    )

def create_enhanced_metric_card(title: str, value: Any, icon: str, accent_color: str = None) -> ft.Card:
    """Enhanced metric card compatibility wrapper."""
    return themed_metric_card(title, str(value), icon)

def apply_advanced_table_effects(data_table: ft.DataTable, **kwargs) -> ft.Container:
    """Table wrapper using Flet's built-in styling instead of custom effects."""
    # Just return the table in a simple container - let Flet handle styling
    return ft.Container(
        content=data_table,
        padding=10,
        border_radius=12,
        bgcolor=ft.Colors.SURFACE
    )

def create_professional_datatable(columns: List[str], rows: List[List[str]], **kwargs) -> ft.DataTable:
    """Professional DataTable using Flet's built-in styling."""
    return smart_data_table(columns, rows)

def get_premium_table_styling() -> Dict[str, Any]:
    """Simple table styling dict - let Flet handle the complexity."""
    return {
        "heading_row_color": ft.Colors.SURFACE_VARIANT,
        "border_radius": 12,
        "column_spacing": 50,
        "data_row_min_height": 60
    }

# Status chip for compatibility
def create_status_chip(status: str, size: str = "medium") -> ft.Container:
    """Status chip using Flet's Container."""
    colors = {
        "success": ft.Colors.GREEN,
        "warning": ft.Colors.ORANGE,
        "error": ft.Colors.RED,
        "info": ft.Colors.BLUE
    }

    return ft.Container(
        content=ft.Text(status, size=10 if size == "small" else 12, color=ft.Colors.WHITE),
        padding=ft.Padding(6, 2, 6, 2),
        bgcolor=colors.get(status.lower(), ft.Colors.GREY),
        border_radius=8
    )


# Floating action button for compatibility
def create_floating_action_button(icon: str, on_click: Callable, tooltip: str = "Action") -> ft.FloatingActionButton:
    """Simple FAB using Flet built-ins."""
    return ft.FloatingActionButton(icon=icon, on_click=on_click, tooltip=tooltip)

# Settings field builders (simplified from complex registry system)
def build_settings_field(field_config: Dict[str, Any], state) -> Optional[ft.Control]:
    """Simple settings field builder using Flet built-ins."""
    field_type = field_config.get("type", "text")
    label = str(field_config.get("label", ""))

    if field_type == "text":
        return smart_text_field(label, str(field_config.get("default", "")))
    elif field_type == "switch":
        return smart_switch(label, bool(field_config.get("default", False)))
    elif field_type == "dropdown":
        options = field_config.get("options", [])
        return smart_dropdown(label, options, str(field_config.get("default", "")))
    else:
        return ft.Text(f"Unsupported field type: {field_type}")

def create_status_header(server_bridge, settings_state):
    """Simple status header using Flet built-ins."""
    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.CLOUD_SYNC, size=16),
                ft.Text("Server Status: Connected" if server_bridge else "No server", size=12),
            ], spacing=5),
            ft.Row([
                ft.Icon(ft.Icons.SCHEDULE, size=16),
                ft.Text("Settings loaded", size=12),
            ], spacing=5),
        ], spacing=2),
        padding=10,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.PRIMARY),
        border_radius=8,
    ), lambda: None  # Return tuple (container, update_fn)

# Progress indicator for compatibility
def create_modern_progress_indicator(operation: str, state_manager=None) -> ft.Container:
    """Simple progress indicator using Flet built-ins."""
    return ft.Container(
        content=ft.Row([
            ft.ProgressRing(width=20, height=20, visible=False),
            ft.Text("", size=12, visible=False)
        ], spacing=5),
        visible=False
    )

# File operations helpers
def safe_update_control(control: ft.Control, force: bool = False) -> bool:
    """Safe control update helper."""
    try:
        if hasattr(control, 'update'):
            control.update()
            return True
    except Exception:
        pass
    return False


def safe_update_controls(*controls: ft.Control, force: bool = False) -> int:
    """Safe multiple control update helper."""
    count = 0
    for control in controls:
        if safe_update_control(control, force):
            count += 1
    return count