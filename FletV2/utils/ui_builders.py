"""
UI Builders for FletV2 - Common UI patterns and components.

This module provides standardized building blocks for:
- Search bars
- Filter dropdowns
- Action buttons
- Confirmation dialogs
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft


def create_search_bar(
    on_change,
    *,
    placeholder: str = "Search…",
    expand: bool = True,
    width: int | None = None,
    prefix_icon: str = ft.Icons.SEARCH,
    suggestions: list[str] | None = None,
    on_submit: Callable[[str], None] | None = None,
    on_tap: Callable[[ft.ControlEvent], None] | None = None,
):
    """
    Create a native Material Design 3 SearchBar with enhanced features.

    Replaces the custom TextField-based search with Flet's native SearchBar
    for better accessibility, Material Design 3 compliance, and native functionality.

    Args:
        on_change: Function to call when search query changes
        placeholder: Placeholder text for the search bar
        expand: Whether the search bar should expand to fill available space
        width: Fixed width for the search bar (ignored if expand=True)
        prefix_icon: Icon to display before the search text
        suggestions: List of search suggestions for auto-completion
        on_submit: Function to call when user submits search (Enter/Click)
        on_tap: Function to call when search bar is tapped

    Returns:
        ft.SearchBar: Native search bar with Material Design 3 styling

    Example:
        def handle_search(query: str):
            print(f"Searching: {query}")

        search_bar = create_search_bar(
            on_change=handle_search,
            placeholder="Search files...",
            suggestions=["report.pdf", "data.xlsx", "presentation.pptx"],
            on_submit=lambda q: print(f"Submit: {q}")
        )
    """

    # Create search suggestions if provided
    suggestion_tiles = []
    if suggestions:
        for suggestion in suggestions:
            suggestion_tiles.append(
                ft.SearchBarTile(
                    value=suggestion,
                    text=ft.Text(suggestion),
                    on_select=lambda _, s=suggestion: (
                        setattr(search_bar, 'value', s),
                        on_change(s) if on_change else None,
                        search_bar.update()
                    )
                )
            )

    # Create the native SearchBar with Material Design 3 styling
    search_bar = ft.SearchBar(
        bar_hint_text=placeholder,
        bar_leading=ft.Icon(
            prefix_icon,
            color=ft.Colors.PRIMARY,
            size=20,
        ),
        view_elevation=4,
        view_surface_tint_color=ft.Colors.SURFACE,
        view_header_height=56,
        bar_overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.PRIMARY),
        bar_surface_tint_color=ft.Colors.SURFACE,
        bar_padding=ft.padding.symmetric(horizontal=16),
        on_tap=on_tap,
        on_submit=lambda e: on_submit(e.control.value) if on_submit else None,
        on_change=lambda e: on_change(e.control.value) if on_change else None,
        controls=suggestion_tiles,
        expand=expand if width is None else False,
        width=width,
    )

    # Enhanced styling with Material Design 3 shadow and border radius
    search_bar.bar_bgcolor = ft.Colors.SURFACE
    search_bar.bar_shape = ft.RoundedRectangleBorder(radius=16)
    search_bar.bar_border_side = ft.BorderSide(1, ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE))

    return search_bar


def create_filter_chip(
    text: str,
    selected: bool = False,
    on_select: Callable[[str, bool], None] | None = None,
    *,
    icon: str | None = None,
    bg_color: str | None = None,
    text_color: str | None = None,
    padding: ft.Padding | None = None,
) -> ft.FilterChip:
    """
    Create a native Material Design 3 FilterChip with enhanced features.

    Replaces custom filter implementations with Flet's native FilterChip
    for better accessibility, Material Design 3 compliance, and native functionality.

    Args:
        text: Text label for the filter chip
        selected: Whether the chip is currently selected
        on_select: Function called when chip selection changes (receives text and selected state)
        icon: Optional icon to display before the text
        bg_color: Optional background color override
        text_color: Optional text color override
        padding: Optional custom padding

    Returns:
        ft.FilterChip: Native filter chip with Material Design 3 styling

    Example:
        def handle_filter(filter_name: str, is_selected: bool):
            print(f"Filter {filter_name} selected: {is_selected}")

        chip = create_filter_chip(
            text="Active",
            on_select=handle_filter,
            icon=ft.Icons.CHECK_CIRCLE
        )
    """

    # Set default padding if not provided
    if padding is None:
        padding = ft.padding.symmetric(horizontal=12, vertical=6)

    # Create the native FilterChip with Material Design 3 styling
    chip = ft.FilterChip(
        label=text,
        selected=selected,
        on_select=lambda e: on_select(text, e.control.selected) if on_select else None,
        label_style=ft.TextStyle(
            size=12,
            color=text_color or ft.Colors.ON_SURFACE,
            weight=ft.FontWeight.W_500,
        ),
        padding=padding,
        bg_color=bg_color,
        icon=icon,
        elevation=1,
        shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.SHADOW),
    )

    return chip


def create_status_chip(
    icon: str,
    text_control: ft.Control,
    bg_color: str,
    text_color: str,
) -> ft.Container:
    """
    Create a native Material Design 3 status chip for displaying metrics.

    Replaces custom _pill helper with proper Material Design 3 styling
    using native Container component with enhanced accessibility and styling.

    Args:
        icon: Icon name to display
        text_control: Text control showing the value
        bg_color: Background color for the chip
        text_color: Text color for the chip

    Returns:
        ft.Container: Styled status chip with Material Design 3 compliance

    Example:
        uptime_text = ft.Text("24h 15m", size=12)
        chip = create_status_chip(
            icon=ft.Icons.HOURGLASS_BOTTOM,
            text_control=uptime_text,
            bg_color=ft.Colors.PRIMARY,
            text_color=ft.Colors.ON_PRIMARY
        )
    """

    return ft.Container(
        content=ft.Row(
            [
                ft.Icon(
                    icon,
                    size=14,
                    color=text_color,
                ),
                text_control,
            ],
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(horizontal=12, vertical=6),
        bgcolor=ft.Colors.with_opacity(0.12, bg_color),
        border=ft.border.all(1, ft.Colors.with_opacity(0.24, bg_color)),
        border_radius=16,  # Material Design 3 recommends 16px for chips
        shadow=ft.BoxShadow(
            spread_radius=1,
            blur_radius=2,
            color=ft.Colors.with_opacity(0.1, ft.Colors.SHADOW),
            offset=ft.Offset(0, 1),
        ),
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )


def create_filter_dropdown(
    label: str,
    options,
    on_change,
    *,
    value=None,
    width: int | None = 200,
    expand: bool = False,
):
    """Create a standardized dropdown styled for filter toolbars."""

    dropdown_options: list[ft.dropdown.Option] = []
    for option in options:
        if isinstance(option, ft.dropdown.Option):
            dropdown_options.append(option)
        elif isinstance(option, tuple):
            if len(option) == 2:
                dropdown_options.append(ft.dropdown.Option(option[0], option[1]))
            else:
                dropdown_options.append(ft.dropdown.Option(option[0]))
        else:
            dropdown_options.append(ft.dropdown.Option(option))

    return ft.Dropdown(
        label=label,
        value=value,
        options=dropdown_options,
        on_change=on_change,
        border=ft.InputBorder.OUTLINE,
        border_radius=12,
        filled=True,
        fill_color=ft.Colors.SURFACE,
        focused_border_color=ft.Colors.PRIMARY,
        content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
        width=None if expand else width,
        expand=expand,
    )


def create_action_button(text, on_click, icon=None, primary=True):
    """Create a consistent action button that respects the active theme."""

    button_cls = ft.FilledButton if primary else ft.OutlinedButton

    return button_cls(
        text=text,
        icon=icon,
        on_click=on_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            padding=ft.Padding(16, 10, 16, 10),
        ),
    )


def create_view_header(
    title: str,
    *,
    icon: str | None = None,
    description: str | None = None,
    actions: list[ft.Control] | None = None,
) -> ft.Control:
    """Compose a compact, responsive header for top-of-view toolbars."""

    leading_controls: list[ft.Control] = []
    if icon:
        leading_controls.append(
            ft.Icon(icon, size=26, color=ft.Colors.PRIMARY)
        )
    leading_controls.append(
        ft.Text(title, size=26, weight=ft.FontWeight.BOLD)
    )

    title_row = ft.Row(
        [
            ft.Row(
                leading_controls,
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(expand=True),
            *(actions or []),
        ],
        spacing=16,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        wrap=False,
    )

    header_controls: list[ft.Control] = [title_row]
    if description:
        header_controls.append(
            ft.Text(
                description,
                size=14,
                color=ft.Colors.ON_SURFACE_VARIANT,
            )
        )

    return ft.Container(
        content=ft.Column(header_controls, spacing=4),
        padding=ft.padding.only(bottom=12),
    )


def create_info_row(
    icon: str,
    label: str,
    value: str | ft.Control,
    *,
    label_size: int = 12,
    value_size: int = 14,
) -> ft.Row:
    """Create standardized info row with icon, label, and value.

    Used consistently across all dashboard/detail views for metadata display.
    Pattern: [Icon] Label
                    Value

    Args:
        icon: Material icon name (e.g., ft.Icons.HUB)
        label: Label text (e.g., "Connections")
        value: Value text or Control (e.g., "42" or ft.Text(...))
        label_size: Size of label text (default: 12)
        value_size: Size of value text (default: 14)

    Returns:
        Properly styled Row with icon, label column, and value

    Example:
        >>> create_info_row(ft.Icons.HUB, "Connections", "5")
        >>> create_info_row(ft.Icons.STORAGE, "DB response", db_value_text)
    """
    if isinstance(value, str):
        value_control = ft.Text(
            value,
            size=value_size,
            weight=ft.FontWeight.W_600,
            color=ft.Colors.ON_SURFACE
        )
    else:
        value_control = value

    return ft.Row(
        [
            ft.Icon(icon, size=18, color=ft.Colors.ON_SURFACE_VARIANT),
            ft.Column(
                [
                    ft.Text(label, size=label_size, color=ft.Colors.ON_SURFACE_VARIANT),
                    value_control,
                ],
                spacing=2,
                tight=True,
            ),
        ],
        spacing=10,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def create_confirmation_dialog(title, message, on_confirm, on_cancel):
    """
    Create standardized confirmation dialog.

    Args:
        title: Title of the dialog
        message: Message to display in the dialog
        on_confirm: Function to call if user confirms
        on_cancel: Function to call if user cancels

    Returns:
        AlertDialog configured as a confirmation dialog
    """
    return ft.AlertDialog(
        title=ft.Text(title),
        content=ft.Text(message),
        actions=[
            ft.TextButton("Cancel", on_click=on_cancel),
            ft.TextButton("Confirm", on_click=on_confirm)
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )


def create_metric_card(
    title: str,
    value_control: ft.Control,
    icon: str,
    description: str = "",
) -> ft.Card:
    """
    Create a metric card matching the EXACT pattern from clients.py and files.py.

    This is the duplicated code from:
    - clients.py:67-80
    - files.py:65-77

    Now consolidated into a single reusable function.

    Args:
        title: Card title
        value_control: Control displaying the value (e.g., ft.Text("42"))
        icon: Material icon name (e.g., ft.Icons.PEOPLE)
        description: Optional description for accessibility

    Returns:
        Configured Card with metric display

    Example:
        total_value = ft.Text("0", size=28, weight=ft.FontWeight.BOLD)
        card = create_metric_card("Total Clients", total_value, ft.Icons.PEOPLE)
    """
    card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(icon, size=24),
                    ft.Text(title, size=14, weight=ft.FontWeight.W_500),
                ], spacing=8),
                value_control,
            ], spacing=8, tight=True),
            padding=20,
        ),
        elevation=2,
    )
    card.is_semantic_container = True  # Accessibility
    return card


# ============================================================================
# Legacy badge helpers migrated from ui_helpers.py (kept for future reuse)
# ============================================================================

_STATUS_COLOR_MAP = {
    "verified": ft.Colors.GREEN_600,
    "complete": ft.Colors.GREEN_600,
    "pending": ft.Colors.ORANGE_600,
    "received": ft.Colors.BLUE_600,
    "unverified": ft.Colors.RED_600,
    "stored": ft.Colors.PURPLE_600,
    "archived": ft.Colors.BROWN_600,
    "empty": ft.Colors.GREY_500,
}


def get_status_color(status: str) -> str:
    """Resolve semantic status into a Material color."""

    key = status.lower() if isinstance(status, str) else f"{status}".lower()
    return _STATUS_COLOR_MAP.get(key, ft.Colors.GREY_400)


def create_status_badge(text: str, status: str) -> ft.Control:
    """Create a compact pill badge for statuses."""

    color = get_status_color(status)
    return ft.Container(
        content=ft.Text(text, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        border_radius=12,
        bgcolor=color,
        border=ft.border.all(1, color),
    )


_LEVEL_COLOR_FG = {
    "INFO": ft.Colors.BLUE,
    "SUCCESS": ft.Colors.GREEN,
    "WARNING": ft.Colors.ORANGE,
    "ERROR": ft.Colors.RED,
    "DEBUG": ft.Colors.GREY,
}


def get_level_colors(level: str) -> tuple[str, str]:
    """Return foreground/background colors for log levels."""

    fg = _LEVEL_COLOR_FG.get(level.upper(), ft.Colors.ON_SURFACE)
    bg = ft.Colors.with_opacity(0.08, fg)
    return fg, bg


def create_log_level_badge(level: str) -> ft.Control:
    """Create a badge control for log levels with consistent styling."""

    fg, bg = get_level_colors(level)
    return ft.Container(
        content=ft.Text(level, size=10, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        padding=ft.padding.symmetric(horizontal=8, vertical=4),
        bgcolor=fg,
        border_radius=12,
        border=ft.border.all(1, fg),
        alignment=ft.alignment.center,
    )


def get_striped_row_color(index: int) -> str | None:
    """Return alternating row color for striped tables."""

    return ft.Colors.GREEN_50 if index % 2 == 0 else None
