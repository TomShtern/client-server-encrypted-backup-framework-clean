"""
Reusable LogCard component for Flet applications
Flet 0.28.3 Compatible
"""

from collections.abc import Callable
from typing import Any

import flet as ft

from FletV2.utils.logging.color_system import LogColorSystem
from FletV2.utils.ui.neomorphism import NeomorphicShadows


class LogCard(ft.Container):
    """
    Reusable neomorphic log card component.

    Design features:
    - Dual shadows for neomorphic depth
    - Color-coded level indicator strip
    - Icon with circular background
    - Clean typography hierarchy
    - Hover animations
    - Subtle color tinting based on log level
    """

    def __init__(
        self,
        log: dict,
        index: int = 0,
        is_compact: bool = False,
        search_query: str = "",
        on_click: Callable[[Any], None] | None = None,
        page: ft.Page | None = None,  # Add page reference for theme awareness
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        # Store page reference
        self.page = page        # Extract log data safely
        time_s = str(log.get("time", ""))
        level = self.map_level(log.get("level"))
        comp = str(log.get("component", ""))
        msg = str(log.get("message", ""))

        # Get color configuration for this level
        color_config = LogColorSystem.get_level_config(level)
        primary_color = color_config["primary"]

        # Determine if compact mode is active
        self.is_compact = is_compact

        # ===== LEFT ACCENT STRIP =====
        # Colored vertical strip that provides immediate visual identification
        accent_strip = ft.Container(
            width=5,
            height=None,  # Full height of card
            bgcolor=primary_color,
            border_radius=ft.border_radius.only(top_left=8 if is_compact else 10, bottom_left=8 if is_compact else 10),
        )

        # ===== ICON CONTAINER =====
        # Circular icon with subtle background matching the log level
        icon_size = 16 if is_compact else 20
        icon_circle_size = 30 if is_compact else 40
        icon_circle = ft.Container(
            content=ft.Icon(
                color_config["icon"],
                size=icon_size,
                color=primary_color,
            ),
            width=icon_circle_size,
            height=icon_circle_size,
            bgcolor=LogColorSystem.get_surface_tint(primary_color, 0.12),
            border_radius=icon_circle_size/2,
            alignment=ft.alignment.center,
            # Subtle neomorphic shadow on icon container
            shadow=[
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=6,
                    color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK),
                    offset=ft.Offset(1, 1),
                ),
            ],
        )

        # ===== LEVEL BADGE =====
        # Small pill showing the log level
        level_badge = ft.Container(
            content=ft.Text(
                color_config["label"],
                size=9 if is_compact else 10,
                weight=ft.FontWeight.W_700,
                color=primary_color,
            ),
            bgcolor=LogColorSystem.get_surface_tint(primary_color, 0.15),
            padding=ft.padding.symmetric(
                horizontal=8 if is_compact else 10,
                vertical=3 if is_compact else 4
            ),
            border_radius=10 if is_compact else 12,
            border=ft.border.all(
                1,
                LogColorSystem.get_border_color(primary_color, 0.2)
            ),
        )

        # ===== MESSAGE TEXT =====
        # Main log message with selectable text and search highlighting
        message_text = self.highlight_text(msg, search_query, is_compact)

        # ===== METADATA ROW =====
        # Component and timestamp information
        metadata_items = []

        if comp:
            # Component pill with subtle background
            metadata_items.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            ft.Icons.WIDGETS_ROUNDED,
                            size=10 if is_compact else 11,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        ),
                        ft.Text(
                            comp,
                            size=10 if is_compact else 11,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            weight=ft.FontWeight.W_500,
                        ),
                    ], spacing=3 if is_compact else 4, tight=True),
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE_VARIANT),
                    padding=ft.padding.symmetric(
                        horizontal=6 if is_compact else 8,
                        vertical=2 if is_compact else 3
                    ),
                    border_radius=5 if is_compact else 6,
                )
            )

        if time_s:
            # Timestamp with clock icon
            time_icon_size = 10 if is_compact else 11
            time_text_size = 10 if is_compact else 11
            time_spacing = 3 if is_compact else 4
            metadata_items.append(
                ft.Row([
                    ft.Icon(
                        ft.Icons.ACCESS_TIME_ROUNDED,
                        size=time_icon_size,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    ft.Text(
                        time_s,
                        size=time_text_size,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        weight=ft.FontWeight.W_400,
                    ),
                ], spacing=time_spacing, tight=True)
            )

        # ===== CARD CONTENT LAYOUT =====
        horizontal_spacing = 10 if is_compact else 16
        vertical_spacing = 4 if is_compact else 8
        icon_spacing = 10 if is_compact else 14

        card_content = ft.Row([
            accent_strip,
            ft.Container(width=horizontal_spacing),  # Spacing
            icon_circle,
            ft.Container(width=icon_spacing),  # Spacing
            # Main content column
            ft.Column([
                message_text,
                ft.Container(height=vertical_spacing),  # Vertical spacing
                ft.Row([
                    *metadata_items,
                    ft.Container(expand=True),  # Push badge to right
                    level_badge,
                ], spacing=4 if is_compact else 8),
            ], spacing=0, expand=True),
            ft.Container(width=horizontal_spacing),  # Right padding
        ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # ===== MAIN CARD CONTAINER =====
        # Neomorphic container with dual shadows and subtle background tint
        card_padding = ft.padding.only(
            top=10 if is_compact else 14,
            bottom=10 if is_compact else 14,
            right=0,
            left=0
        )

        # Set container properties
        self.content = card_content
        self.padding = card_padding
        self.border_radius = 10 if is_compact else 12
        # Subtle background tint based on log level
        self.bgcolor = LogColorSystem.get_surface_tint(primary_color, 0.02)
        # Soft border for definition
        self.border = ft.border.all(
            1,
            LogColorSystem.get_border_color(primary_color, 0.08)
        )

        # Neomorphic shadows - the key to the soft UI effect
        # Use page reference if available for theme-aware shadows
        if page:
            self.shadow = NeomorphicShadows.get_card_shadows("medium" if index < 3 else "low", page)
        else:
            self.shadow = NeomorphicShadows.get_card_shadows("medium" if index < 3 else "low")

        # Smooth animations for interactions
        self.animate = ft.Animation(250, ft.AnimationCurve.EASE_OUT)
        self.animate_scale = ft.Animation(200, ft.AnimationCurve.EASE_OUT)

        # Event handlers
        if on_click:
            # GestureDetector to handle taps for showing log details
            # Note: Since LogCard extends ft.Container, we set up hover effects directly
            # Click handling is managed through the on_click parameter
            self.on_click = on_click

        # Hover interaction handler
        def on_card_hover(e: ft.ControlEvent):
            """Enhanced hover effect with scale and shadow changes"""
            is_hovering = e.data == "true"

            if is_hovering:
                # Use page reference if available
                if self.page:
                    self.shadow = NeomorphicShadows.get_hover_shadows(self.page)
                else:
                    self.shadow = NeomorphicShadows.get_hover_shadows()
                self.scale = 1.015
                self.bgcolor = LogColorSystem.get_surface_tint(primary_color, 0.04)
            else:
                if self.page:
                    self.shadow = NeomorphicShadows.get_card_shadows("medium" if index < 3 else "low", self.page)
                else:
                    self.shadow = NeomorphicShadows.get_card_shadows("medium" if index < 3 else "low")
                self.scale = 1.0
                self.bgcolor = LogColorSystem.get_surface_tint(primary_color, 0.02)

            # Only update if control is attached to page
            if self.page:
                self.update()

        self.on_hover = on_card_hover

    @staticmethod
    def map_level(raw: str | None) -> str:
        """
        Map various log level strings to canonical levels.
        Handles common aliases and variations.
        """
        if not raw:
            return "INFO"

        r = str(raw).strip().upper()

        # Mapping dictionary for all common variations
        level_map = {
            "WARN": "WARNING",
            "WARNING": "WARNING",
            "CRIT": "CRITICAL",
            "CRITICAL": "CRITICAL",
            "FATAL": "CRITICAL",
            "OK": "SUCCESS",
            "SUCCESS": "SUCCESS",
            "IMPORTANT": "IMPORTANT",
            "ALERT": "IMPORTANT",
            "SPECIAL": "SPECIAL",
            "DEBUG": "DEBUG",
            "INFO": "INFO",
            "ERROR": "ERROR",
        }

        return level_map.get(r, "INFO" if r not in LogColorSystem.COLORS else r)

    @staticmethod
    def highlight_text(text: str, search_query: str, is_compact: bool = False) -> ft.Control:
        """Create text with highlighted search matches using spans"""
        # Determine font size based on compact mode
        font_size = 12 if is_compact else 13
        # Remove max_lines limitation to show full log content

        if not search_query or not text:
            return ft.Text(
                text or "(empty message)",
                size=font_size,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.ON_SURFACE,
                selectable=True,
            )

        # Find all occurrences of the search query in the text
        search_lower = search_query.lower()
        text_lower = text.lower()
        parts = []
        last_end = 0

        # Find all matches
        start = 0
        while start < len(text_lower):
            pos = text_lower.find(search_lower, start)
            if pos == -1:
                break
            # Add text before match
            if pos > last_end:
                parts.append(text[last_end:pos])
            # Add matched text
            parts.append(text[pos:pos+len(search_query)])
            last_end = pos + len(search_query)
            start = pos + 1

        # Add remaining text
        if last_end < len(text):
            parts.append(text[last_end:])

        # Create spans
        spans = []
        for part in parts:
            if part.lower() == search_query.lower():
                # This is a match, highlight it
                spans.append(
                    ft.TextSpan(
                        part,
                        ft.TextStyle(
                            bgcolor=ft.Colors.YELLOW_200,
                            color=ft.Colors.BLACK,
                            weight=ft.FontWeight.BOLD
                        )
                    )
                )
            else:
                # This is normal text
                spans.append(ft.TextSpan(part))

        return ft.Text(
            spans=spans,
            size=font_size,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.ON_SURFACE,
            selectable=True,
        )
