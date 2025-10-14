#!/usr/bin/env python3
"""
Simplified UI Components for FletV2 - The Flet Way
~200 lines instead of 2,170 lines of framework fighting!

Core Principle: Use Flet's built-in components with proper theming.
Let Flet do the heavy lifting. We compose, not reinvent.
"""

from collections.abc import Callable
from typing import Any
import contextlib

import flet as ft
from theme import get_design_tokens

# ==============================================================================
# FRAMEWORK-HARMONIOUS COMPONENTS - Using Flet's Native Power
# ==============================================================================

def create_professional_card(title: str, content: ft.Control) -> ft.Card:
    """Professional card with proper spacing and sizing - no more cramped layouts!"""
    card_content = ft.Column([
        ft.Container(
            content=ft.Text(
                title,
                size=18,  # Larger title for better hierarchy
                weight=ft.FontWeight.W_600,
                color=ft.Colors.ON_SURFACE
            ),
            margin=ft.Margin(0, 0, 0, 12)  # Space below title
        ),
        ft.Container(
            content=content,
            expand=True  # Let content expand to fill available space
        )
    ], spacing=0, expand=True)

    return ft.Card(
        content=ft.Container(
            content=card_content,
            padding=ft.Padding(28, 24, 28, 24),  # More generous padding
            border_radius=16,
            expand=True
        ),
        elevation=6,  # Moderate elevation
        surface_tint_color=ft.Colors.SURFACE_TINT,
        expand=True  # Card expands to fill column space
    )


def create_beautiful_card(title: str, content: ft.Control, accent_color: str | None = None) -> ft.Container:
    """Visually stunning card with depth and polish matching the reference design."""
    # Beautiful dark theme colors
    BEAUTIFUL_DARK_PALETTE = {
        "surface": "#1E293B",         # Card backgrounds with subtle warmth
        "surface_bright": "#334155",  # Elevated elements
        "text_primary": "#F8FAFC",    # Crisp white text
        "text_secondary": "#CBD5E1",  # Subtle gray text
    }

    return ft.Container(
        content=ft.Column([
            ft.Text(
                title,
                size=16,
                weight=ft.FontWeight.W_600,
                color=BEAUTIFUL_DARK_PALETTE["text_primary"]
            ),
            content
        ], spacing=16),
        padding=ft.Padding(24, 20, 24, 20),  # Generous, balanced padding
        bgcolor=BEAUTIFUL_DARK_PALETTE["surface"],
        border_radius=16,  # Rounded for modern feel
        # Beautiful layered shadow for depth
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            offset=ft.Offset(0, 8),
            color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
            blur_style=ft.ShadowBlurStyle.OUTER
        ),
        # Subtle border for definition
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
        # Smooth hover animation
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )


def create_simple_bar_chart(data_points: list, labels: list, colors: list) -> ft.BarChart:
    """Create a simple bar chart for data visualization."""
    # Create bar groups from data
    bar_groups = []
    bar_groups.extend(
        ft.BarChartGroup(
            x=i,
            bar_rods=[
                ft.BarChartRod(
                    to_y=value,
                    color=color,
                    width=20,
                    border_radius=4,
                )
            ],
        )
        for i, (value, label, color) in enumerate(
            zip(data_points, labels, colors, strict=False)
        )
    )
    return ft.BarChart(
        bar_groups=bar_groups,
        width=400,
        height=200,
        interactive=True,
        bgcolor=ft.Colors.TRANSPARENT,
        border=ft.border.all(1, ft.Colors.OUTLINE)
    )


def create_simple_pie_chart(sections: list) -> ft.PieChart:
    """Create a simple pie chart for data visualization."""
    pie_sections = [
        ft.PieChartSection(
            value=section["value"],
            color=section["color"],
            title=section["title"],
            radius=section.get("radius", 80),
            badge=ft.Text(f"{section['value']}%", size=10, color=ft.Colors.WHITE)
        )
        for section in sections
    ]

    return ft.PieChart(
        sections=pie_sections,
        width=180,
        height=180,
        sections_space=2
    )

def create_stunning_circular_progress(percentage: float, title: str, color_type: str = "primary") -> ft.Container:
    """Perfect circular progress indicators - maintaining aspect ratio!"""
    # Use vibrant colors that really stand out
    color_map = {
        "primary": "#3B82F6",    # Bright blue
        "secondary": "#8B5CF6",  # Purple
        "success": "#10B981",    # Green
        "warning": "#F59E0B",    # Orange - perfect for memory
        "error": "#EF4444"       # Red
    }

    color = color_map.get(color_type, "#3B82F6")

    # Create a perfectly square container to maintain circle shape
    ring_size = 160  # Single size variable for perfect circles

    return ft.Container(
        content=ft.Stack([
            # Perfect circular progress ring - no stretching!
            ft.ProgressRing(
                value=percentage / 100,
                stroke_width=12,  # Proportional stroke width
                color=color,
                width=ring_size,
                height=ring_size  # Exact same as width for perfect circle
            ),
            # Center text overlay
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        f"{percentage:.0f}%",
                        size=28,  # Proportional to ring size
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_SURFACE,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        title,
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        text_align=ft.TextAlign.CENTER,
                        weight=ft.FontWeight.W_500
                    )
                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                width=ring_size,
                height=ring_size
            )
        ]),
        width=ring_size + 40,   # Ring size + padding
        height=ring_size + 40,  # Exact same for perfect square container
        alignment=ft.alignment.center,
        padding=20  # Equal padding on all sides
    )

def create_elegant_button(text: str, icon: str, on_click, button_type: str = "filled") -> ft.Control:
    """Elegant button using Flet's built-in buttons - Framework Harmony!"""
    button_content = ft.Row([
        ft.Icon(icon, size=18),
        ft.Text(text, size=14, weight=ft.FontWeight.W_500)
    ], spacing=8, tight=True)

    # Use Flet's native button types - let the framework handle styling!
    if button_type == "filled":
        return ft.FilledButton(content=button_content, on_click=on_click)
    elif button_type == "elevated":
        return ft.ElevatedButton(content=button_content, on_click=on_click)
    elif button_type == "outlined":
        return ft.OutlinedButton(content=button_content, on_click=on_click)
    else:
        return ft.TextButton(content=button_content, on_click=on_click)


def create_beautiful_action_button(text: str, icon: str, on_click, color_type: str = "primary") -> ft.Container:
    """Beautifully styled action button with visual polish matching the reference design."""
    # Color mapping for different button types
    color_map = {
        "primary": "#3B82F6",      # Vibrant blue
        "success": "#10B981",      # Fresh green for START SERVER
        "error": "#EF4444",        # Clear red for STOP SERVER
        "warning": "#F59E0B",      # Warm orange for BACKUP
        "secondary": "#6B7280"     # Gray for REFRESH
    }

    base_color = color_map.get(color_type, color_map["primary"])

    # Create the button with enhanced styling
    button = ft.ElevatedButton(
        content=ft.Row([
            ft.Icon(icon, size=18, color=ft.Colors.WHITE),
            ft.Text(text, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE)
        ], spacing=8, tight=True),
        on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor=base_color,
            overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            elevation={
                ft.ControlState.DEFAULT: 6,
                ft.ControlState.HOVERED: 8,
                ft.ControlState.PRESSED: 2,
            },
            animation_duration=150,
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(20, 12, 20, 12)
        )
    )

    # Add container with shadow for additional depth
    return ft.Container(
        content=button,
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=12,
            offset=ft.Offset(0, 4),
            color=ft.Colors.with_opacity(0.25, base_color)
        ),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
    )


def create_action_buttons_row(on_start_server, on_stop_server, on_backup, on_refresh) -> ft.Row:
    """Create the beautiful action buttons row matching the reference design."""
    return ft.Row([
        create_beautiful_action_button("START SERVER", ft.Icons.PLAY_ARROW, on_start_server, "success"),
        create_beautiful_action_button("STOP SERVER", ft.Icons.STOP, on_stop_server, "error"),
        create_beautiful_action_button("BACKUP", ft.Icons.BACKUP, on_backup, "warning"),
        create_beautiful_action_button("REFRESH", ft.Icons.REFRESH, on_refresh, "secondary")
    ], spacing=16)

def create_status_indicator(status: str, text: str) -> ft.Container:
    """Status indicator using Flet's semantic colors - Framework Harmony!"""
    # Use Flet's semantic colors instead of hardcoded colors
    status_colors = {
        "excellent": ft.Colors.GREEN,
        "good": ft.Colors.GREEN_700,
        "warning": ft.Colors.ORANGE,
        "critical": ft.Colors.RED,
        "info": ft.Colors.BLUE,
        "neutral": ft.Colors.GREY
    }

    color = status_colors.get(status, ft.Colors.GREY)

    return ft.Container(
        content=ft.Row([
            # Simple animated dot
            ft.Container(
                width=12,
                height=12,
                border_radius=6,
                bgcolor=color,
                animate=True  # Simple animation - let Flet handle it!
            ),
            ft.Text(text, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE)
        ], spacing=8),
        padding=ft.Padding(12, 8, 12, 8),
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.1, color),
        border=ft.border.all(1, ft.Colors.with_opacity(0.3, color))
    )


def create_pulsing_status_indicator(status: str, text: str) -> ft.Container:
    """Beautiful status indicator with pulsing animation matching the reference design."""
    # Use vibrant colors that match the dark theme
    status_colors = {
        "excellent": "#10B981",    # Fresh green
        "good": "#059669",         # Deeper success green
        "warning": "#F59E0B",      # Warm orange
        "critical": "#EF4444",     # Clear red
        "info": "#3B82F6",        # Trustworthy blue
        "neutral": "#6B7280"       # Professional gray
    }

    color = status_colors.get(status, status_colors["neutral"])

    # Create pulsing dot with animation
    pulsing_dot = ft.Container(
        width=12,
        height=12,
        border_radius=6,
        bgcolor=color,
        animate=ft.Animation(1500, ft.AnimationCurve.EASE_IN_OUT),
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=8,
            color=ft.Colors.with_opacity(0.4, color)
        )
    )

    return ft.Container(
        content=ft.Row([
            pulsing_dot,
            ft.Text(
                text,
                size=14,
                weight=ft.FontWeight.W_500,
                color="#F8FAFC"  # Crisp white text for dark theme
            )
        ], spacing=8),
        padding=ft.Padding(12, 8, 12, 8),
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.1, color),
        border=ft.border.all(1, ft.Colors.with_opacity(0.2, color))
    )

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

def themed_card(content: ft.Control, title: str | None = None, page: ft.Page | None = None) -> ft.Card:
    """
    Enhanced card with layered depth and old design styling.
    Hybrid approach: visually appealing colors that adapt to light/dark themes.
    """
    card_content = content

    if title:
        card_content = ft.Column([
            ft.Text(title, size=18, weight=ft.FontWeight.W_600),
            ft.Divider(height=1, color=ft.Colors.OUTLINE),
            content
        ], spacing=12)

    # Enhanced approach: Let Flet handle theming but add layered depth through elevation and borders
    # This gives us the visual depth without hardcoded colors that break in light theme

    return ft.Card(
        content=ft.Container(
            content=card_content,
            padding=16,  # Consistent internal padding as specified
            border=ft.border.all(1, ft.Colors.OUTLINE),  # Theme-aware border
            border_radius=8,  # Rounded corners as specified
        ),
        elevation=6,  # Enhanced elevation for layered depth
        surface_tint_color=ft.Colors.TRANSPARENT  # Prevent Material 3 tinting, keep theme colors
    )


def themed_button(text: str, on_click: Callable, variant: str = "filled",
                 icon: str | None = None) -> ft.Control:
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


def themed_chip(text: str, icon: str | None = None) -> ft.Container:
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


def create_status_pill(text: str, status_type: str) -> ft.Container:
    """
    Create compact status pills following old design specifications.
    Status types: 'success', 'error', 'warning', 'info', 'default'
    Optimized for smaller, more refined appearance.
    """
    # Expanded status colors with distinct colors for each state
    status_colors = {
        'success': "#2E7D32",   # Green - as specified in document
        'error': "#C62828",     # Red - as specified in document
        'warning': "#EF6C00",   # Orange - as specified in document
        'info': "#0288D1",      # Blue - as specified in document
        'registered': "#7B1FA2", # Purple - for registered/enrolled states
        'offline': "#5D4037",   # Brown - for offline/disconnected states
        'queued': "#F57C00",    # Amber - for pending/queued operations
        'debug': "#546E7A",     # Blue Grey - for debug/development info
        'unknown': "#78909C",   # Light Blue Grey - for unknown states
        'default': "#424242"    # Dark Grey - fallback only
    }

    return ft.Container(
        content=ft.Text(
            text,
            color=ft.Colors.WHITE,          # White text as specified
            size=10,                        # Smaller text for more refined appearance
            weight=ft.FontWeight.BOLD       # Bold text as specified
        ),
        bgcolor=status_colors.get(status_type.lower(), status_colors['default']),
        border_radius=8,                    # Slightly smaller radius for compact look
        padding=ft.Padding(left=6, right=6, top=2, bottom=2),  # More compact padding
        alignment=ft.alignment.center,      # Center the text
        width=None,                         # Let it size naturally to content
        height=20                           # Fixed height for consistency
    )


# ==============================================================================
# SMART FIELD BUILDERS (Simplified from the complex registry system)
# ==============================================================================

def smart_text_field(label: str, value: str = "", on_change: Callable | None = None) -> ft.TextField:
    """Create text field using Flet's theming. Simple & powerful!"""
    return ft.TextField(
        label=label,
        value=value,
        on_change=on_change,
        border_radius=12,
        filled=True
    )


def smart_switch(label: str, value: bool = False, on_change: Callable | None = None) -> ft.Switch:
    """Create switch using Flet's theming. Simple & works!"""
    return ft.Switch(label=label, value=value, on_change=on_change)


def smart_dropdown(label: str, options: list[str], value: str = "",
                  on_change: Callable | None = None) -> ft.Dropdown:
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

def smart_data_table(columns: list[str], rows: list[list[str]]) -> ft.DataTable:
    """Create DataTable using Flet's built-in styling. Let Flet handle the complexity!"""
    return ft.DataTable(
        columns=[ft.DataColumn(ft.Text(col)) for col in columns],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
            for row in rows
        ],
        heading_row_color=ft.Colors.SURFACE,
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
        bgcolor=ft.Colors.SURFACE
    )


# ==============================================================================
# LAYOUT HELPERS (Using Flet's ResponsiveRow)
# ==============================================================================

def smart_responsive_cards(cards: list[ft.Control]) -> ft.ResponsiveRow:
    """Create responsive card layout using Flet's ResponsiveRow. Framework harmony!"""
    return ft.ResponsiveRow([
        ft.Column([card], col={"sm": 12, "md": 6, "lg": 4})
        for card in cards
    ])


def smart_dashboard_layout(metrics: list[dict[str, Any]]) -> ft.Column:
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

def create_enhanced_metric_card(title: str, value: Any, icon: str, accent_color: str | None = None) -> ft.Card:
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

def create_professional_datatable(columns: list[str], rows: list[list[str]], **kwargs) -> ft.DataTable:
    """Professional DataTable using Flet's built-in styling."""
    return smart_data_table(columns, rows)

def get_premium_table_styling() -> dict[str, Any]:
    """Simple table styling dict - let Flet handle the complexity."""
    return {
        "heading_row_color": ft.Colors.SURFACE,
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
def build_settings_field(field_config: dict[str, Any], state) -> ft.Control | None:
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
    with contextlib.suppress(Exception):
        if hasattr(control, 'update'):
            control.update()
            return True
    return False


def safe_update_controls(*controls: ft.Control, force: bool = False) -> int:
    """Safe multiple control update helper."""
    return sum(safe_update_control(control, force) for control in controls)

# ======================================================================
# PHASE 1: STANDARDIZED COMPONENT PRIMITIVES (additive, non-breaking)
# ======================================================================

_TOKENS = get_design_tokens()
_SP = _TOKENS["spacing"]
_RD = _TOKENS["radii"]


def AppCard(
    content: ft.Control,
    title: str | None = None,
    actions: list[ft.Control] | None = None,
    padding: int | None = None,
    tooltip: str | None = None,
    expand_content: bool = True,
) -> ft.Container:
    """Unified card: subtle border + elevation, consistent padding & radius.

    When expand_content=True, the card will allocate remaining vertical space to its body
    so that children like Tabs can render properly. We do this by wrapping the body in
    a Container(expand=True) to make it an expanding child inside the card's Column.
    """
    body = ft.Container(content=content, expand=True) if expand_content else content
    header_controls: list[ft.Control] = []
    if title is not None or actions:
        header_controls.extend(
            (
                ft.Row(
                    [
                        ft.Text(
                            title or "", size=16, weight=ft.FontWeight.W_600
                        ),
                        ft.Container(expand=True),
                        *(actions or []),
                    ]
                ),
                ft.Divider(height=1, color=ft.Colors.OUTLINE),
            )
        )
    return ft.Container(
        content=ft.Column([
            *header_controls,
            body
        ], spacing=_SP["lg"], expand=expand_content, scroll=(ft.ScrollMode.AUTO if expand_content else None)),
        # Key fix: when expand_content is True, allow this card to expand within parent layouts (e.g., Column)
        # so children like Tabs (with expand=True) actually receive vertical space.
        expand=1 if expand_content else None,
        padding=ft.padding.all(padding if padding is not None else _SP["xl"]),
        border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
        border_radius=_RD["lg"],
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=14,
            offset=ft.Offset(0, 6),
            color=ft.Colors.with_opacity(0.16, ft.Colors.SURFACE_TINT),
        ),
        bgcolor=ft.Colors.SURFACE,
        # Micro-interactions
        animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
        on_hover=lambda e: (setattr(e.control, 'scale', 1.01 if e.data == 'true' else 1.0), e.control.update()),
        tooltip=tooltip,
    )


def AppButton(
    text: str,
    on_click: Callable,
    icon: str | None = None,
    variant: str = "primary",  # primary | tonal | outline | danger | success
) -> ft.Control:
    """Unified button with consistent shape, padding and states."""
    content = ft.Row([
        *( [ft.Icon(icon, size=16)] if icon else [] ),
        ft.Text(text, size=14, weight=ft.FontWeight.W_500),
    ], spacing=_SP["sm"], tight=True)

    shape = ft.RoundedRectangleBorder(radius=_RD["md"])  # Use 'md' radius for buttons
    padding = ft.padding.symmetric(horizontal=_SP["xl"], vertical=_SP["md"])

    if variant == "outline":
        return ft.OutlinedButton(content=content, on_click=on_click, style=ft.ButtonStyle(shape=shape, padding=padding))
    if variant == "tonal":
        return ft.FilledTonalButton(content=content, on_click=on_click, style=ft.ButtonStyle(shape=shape, padding=padding))
    if variant == "danger":
        return ft.FilledButton(content=content, on_click=on_click, style=ft.ButtonStyle(shape=shape, padding=padding, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE))
    if variant == "success":
        return ft.FilledButton(content=content, on_click=on_click, style=ft.ButtonStyle(shape=shape, padding=padding, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE))
    # default primary
    return ft.FilledButton(content=content, on_click=on_click, style=ft.ButtonStyle(shape=shape, padding=padding))


def SectionHeader(title: str, actions: list[ft.Control] | None = None) -> ft.Row:
    """Standard page section header with title and optional actions on the right."""
    return ft.Row([
        ft.Text(title, size=20, weight=ft.FontWeight.W_600),
        ft.Container(expand=True),
        *(actions or [])
    ])


def StatusPill(label: str, level: str = "info") -> ft.Container:
    """Compact status pill with standardized colors."""
    palette = {
        "success": ft.Colors.GREEN,
        "warning": ft.Colors.AMBER,
        "error": ft.Colors.RED,
        "info": ft.Colors.BLUE,
        "neutral": ft.Colors.GREY,
    }
    color = palette.get(level.lower(), palette["neutral"])
    return ft.Container(
        content=ft.Text(label, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600),
        padding=ft.padding.symmetric(horizontal=_SP["md"], vertical=2),
        bgcolor=color,
        border_radius=_RD["chip"],
    )


def DataTableWrapper(table: ft.DataTable) -> ft.Container:
    """Add standard padding, zebra possibility, and elevation around DataTable."""
    return ft.Container(
        content=table,
        padding=ft.padding.all(_SP["lg"]),
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=_RD["lg"],
        bgcolor=ft.Colors.SURFACE,
    )


def FilterBar(controls: list[ft.Control]) -> ft.Row:
    """Unified filter bar spacing and alignment."""
    return ft.Row(controls, spacing=_SP["lg"], alignment=ft.MainAxisAlignment.START)
