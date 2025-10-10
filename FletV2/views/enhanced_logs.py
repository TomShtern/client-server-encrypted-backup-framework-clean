#!/usr/bin/env python3
"""
Ultra-Enhanced Neomorphic Logs View - MD3/Material You 3 Design
Flet 0.28.3 Compatible

Design Philosophy:
- True neomorphic design with dual shadow system (light + dark)
- Distinct color coding: Red (error), Green (success), Yellow (warning),
  Blue (info), Orange (critical), Purple (special)
- Material 3 principles with surface tones and elevation
- Clean, professional, and modern aesthetic
- Subtle visual differentiation through shadows, borders, and opacity
"""

import os
import sys
import logging
import contextlib
from datetime import datetime
import asyncio
import json
from typing import Any, Callable, Optional

import flet as ft

# Path setup
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import Shared.utils.utf8_solution as _  # noqa: F401

# --------------------------------------------------------------------------------------
# NEOMORPHIC SHADOW SYSTEM
# True neomorphism requires dual shadows: one light (top-left) and one dark (bottom-right)
# This creates the "soft UI" effect where elements appear to extrude from or press into the surface
# --------------------------------------------------------------------------------------

class NeomorphicShadows:
    """Professional neomorphic shadow system with elevation levels"""

    @staticmethod
    def get_card_shadows(elevation: str = "medium") -> list[ft.BoxShadow]:
        """
        Get neomorphic shadows for cards based on elevation level.
        Neomorphism uses dual shadows to create depth perception.
        """
        if elevation == "low":
            return [
                # Light shadow (top-left) - simulates light source
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
                    offset=ft.Offset(-2, -2),
                ),
                # Dark shadow (bottom-right) - creates depth
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=10,
                    color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                    offset=ft.Offset(2, 2),
                ),
            ]
        elif elevation == "medium":
            return [
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.10, ft.Colors.WHITE),
                    offset=ft.Offset(-3, -3),
                ),
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=15,
                    color=ft.Colors.with_opacity(0.20, ft.Colors.BLACK),
                    offset=ft.Offset(3, 3),
                ),
            ]
        else:  # high
            return [
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
                    offset=ft.Offset(-4, -4),
                ),
                ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=20,
                    color=ft.Colors.with_opacity(0.25, ft.Colors.BLACK),
                    offset=ft.Offset(4, 4),
                ),
            ]

    @staticmethod
    def get_hover_shadows() -> list[ft.BoxShadow]:
        """Enhanced shadows for hover state - more pronounced elevation"""
        return [
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=18,
                color=ft.Colors.with_opacity(0.12, ft.Colors.WHITE),
                offset=ft.Offset(-4, -4),
            ),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=18,
                color=ft.Colors.with_opacity(0.22, ft.Colors.BLACK),
                offset=ft.Offset(4, 4),
            ),
        ]

    @staticmethod
    def get_pressed_shadows() -> list[ft.BoxShadow]:
        """Inset shadows for pressed state - appears pressed into surface"""
        return [
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.15, ft.Colors.BLACK),
                offset=ft.Offset(2, 2),
            ),
        ]

    @staticmethod
    def get_button_shadows() -> list[ft.BoxShadow]:
        """Neomorphic button shadows"""
        return [
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.08, ft.Colors.WHITE),
                offset=ft.Offset(-2, -2),
            ),
            ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.Colors.with_opacity(0.18, ft.Colors.BLACK),
                offset=ft.Offset(2, 2),
            ),
        ]

# --------------------------------------------------------------------------------------
# MD3 COLOR POLYFILLS
# Ensuring all Material 3 color tokens are available in Flet 0.28.x
# --------------------------------------------------------------------------------------

def _ensure_color_attr(attr_name: str, fallback_factory: Callable[[], str]) -> None:
    """Safely add missing color attributes to ft.Colors"""
    try:
        if not hasattr(ft.Colors, attr_name):
            setattr(ft.Colors, attr_name, fallback_factory())
    except Exception:
        with contextlib.suppress(Exception):
            setattr(ft.Colors, attr_name, getattr(ft.Colors, "SURFACE", "#121212"))

# Material 3 surface container colors
_ensure_color_attr(
    "SURFACE_CONTAINER_LOW",
    lambda: ft.Colors.with_opacity(0.06, getattr(ft.Colors, "SURFACE", "#121212")),
)
_ensure_color_attr(
    "SURFACE_CONTAINER",
    lambda: ft.Colors.with_opacity(0.10, getattr(ft.Colors, "SURFACE", "#121212")),
)
_ensure_color_attr(
    "SURFACE_CONTAINER_HIGH",
    lambda: ft.Colors.with_opacity(0.14, getattr(ft.Colors, "SURFACE", "#121212")),
)
_ensure_color_attr(
    "SURFACE_CONTAINER_HIGHEST",
    lambda: ft.Colors.with_opacity(0.16, getattr(ft.Colors, "SURFACE", "#121212")),
)
_ensure_color_attr(
    "ON_SURFACE_VARIANT",
    lambda: ft.Colors.with_opacity(0.70, getattr(ft.Colors, "ON_SURFACE", "#FFFFFF")),
)
_ensure_color_attr(
    "OUTLINE",
    lambda: ft.Colors.with_opacity(0.12, getattr(ft.Colors, "ON_SURFACE", "#FFFFFF")),
)
_ensure_color_attr(
    "OUTLINE_VARIANT",
    lambda: ft.Colors.with_opacity(0.06, getattr(ft.Colors, "ON_SURFACE", "#FFFFFF")),
)

# --------------------------------------------------------------------------------------
# PROFESSIONAL COLOR SYSTEM
# Distinct, vibrant colors for each log level with excellent contrast
# --------------------------------------------------------------------------------------

class LogColorSystem:
    """
    Professional color system with distinct, recognizable colors.
    Each level has a primary color, background tint, and semantic meaning.
    """

    # Color definitions optimized for both dark and light themes
    COLORS = {
        "DEBUG": {
            "primary": "#94A3B8",      # Slate gray - neutral, technical
            "secondary": "#CBD5E1",
            "bg_light": "#F8FAFC",
            "bg_dark": "#1E293B",
            "icon": ft.Icons.BUG_REPORT_ROUNDED,
            "label": "DEBUG",
            "description": "Debug information",
        },
        "INFO": {
            "primary": "#3B82F6",      # Bright blue - informational, clear
            "secondary": "#60A5FA",
            "bg_light": "#EFF6FF",
            "bg_dark": "#1E3A8A",
            "icon": ft.Icons.INFO_ROUNDED,
            "label": "INFO",
            "description": "General information",
        },
        "SUCCESS": {
            "primary": "#10B981",      # Emerald green - positive, successful
            "secondary": "#34D399",
            "bg_light": "#ECFDF5",
            "bg_dark": "#064E3B",
            "icon": ft.Icons.CHECK_CIRCLE_ROUNDED,
            "label": "SUCCESS",
            "description": "Successful operation",
        },
        "WARNING": {
            "primary": "#EAB308",      # Yellow - caution, attention needed
            "secondary": "#FDE047",
            "bg_light": "#FEFCE8",
            "bg_dark": "#713F12",
            "icon": ft.Icons.WARNING_ROUNDED,
            "label": "WARNING",
            "description": "Warning - review needed",
        },
        "IMPORTANT": {
            "primary": "#F97316",      # Orange - important warning, urgent
            "secondary": "#FB923C",
            "bg_light": "#FFF7ED",
            "bg_dark": "#7C2D12",
            "icon": ft.Icons.PRIORITY_HIGH_ROUNDED,
            "label": "IMPORTANT",
            "description": "Important warning",
        },
        "ERROR": {
            "primary": "#EF4444",      # Red - error, failure
            "secondary": "#F87171",
            "bg_light": "#FEF2F2",
            "bg_dark": "#7F1D1D",
            "icon": ft.Icons.ERROR_ROUNDED,
            "label": "ERROR",
            "description": "Error occurred",
        },
        "CRITICAL": {
            "primary": "#DC2626",      # Deep red - critical, severe
            "secondary": "#EF4444",
            "bg_light": "#FEE2E2",
            "bg_dark": "#991B1B",
            "icon": ft.Icons.DANGEROUS_ROUNDED,
            "label": "CRITICAL",
            "description": "Critical failure",
        },
        "SPECIAL": {
            "primary": "#A855F7",      # Purple - special events, unique
            "secondary": "#C084FC",
            "bg_light": "#FAF5FF",
            "bg_dark": "#581C87",
            "icon": ft.Icons.STARS_ROUNDED,
            "label": "SPECIAL",
            "description": "Special event",
        },
    }

    @staticmethod
    def get_level_config(level: str) -> dict:
        """Get complete color configuration for a log level"""
        return LogColorSystem.COLORS.get(level, LogColorSystem.COLORS["INFO"])

    @staticmethod
    def get_surface_tint(color: str, opacity: float = 0.05) -> str:
        """Create subtle surface tint for neomorphic backgrounds"""
        return ft.Colors.with_opacity(opacity, color)

    @staticmethod
    def get_border_color(color: str, opacity: float = 0.15) -> str:
        """Create border color with appropriate opacity"""
        return ft.Colors.with_opacity(opacity, color)

# --------------------------------------------------------------------------------------
# FLET LOG CAPTURE SYSTEM
# Enhanced logging handler with precise timestamp formatting
# --------------------------------------------------------------------------------------

class FletLogCapture(logging.Handler):
    """
    Enhanced logging handler that captures Flet framework logs.
    Maintains a rolling buffer with timestamps and metadata.
    """

    def __init__(self):
        super().__init__()
        self.logs = []
        self.max_logs = 250  # Generous buffer for debugging

    def emit(self, record):
        """Capture log record with enhanced formatting"""
        with contextlib.suppress(Exception):
            # Format timestamp with milliseconds for precise timing
            timestamp = datetime.fromtimestamp(record.created)
            time_str = timestamp.strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds

            self.logs.insert(0, {
                "time": time_str,
                "level": record.levelname,
                "component": record.name,
                "message": self.format(record),
                "timestamp": record.created,
                "full_datetime": timestamp.isoformat(),
            })

            # Maintain buffer size
            if len(self.logs) > self.max_logs:
                self.logs = self.logs[:self.max_logs]


# Initialize global log capture
_flet_log_capture = FletLogCapture()
_flet_log_capture.setFormatter(logging.Formatter('%(message)s'))

# Attach to root logger (check to avoid duplicates on hot reload)
_root_logger = logging.getLogger()
if not any(isinstance(h, FletLogCapture) for h in _root_logger.handlers):
    _root_logger.addHandler(_flet_log_capture)

# --------------------------------------------------------------------------------------
# DATA FETCHING
# --------------------------------------------------------------------------------------

def get_system_logs(server_bridge: Any | None) -> list[dict]:
    """Fetch system logs from server bridge with error handling"""
    if not server_bridge:
        return []
    try:
        result = server_bridge.get_logs()
        if isinstance(result, dict) and result.get('success'):
            return result.get('data', [])
        return []
    except Exception:
        return []

# --------------------------------------------------------------------------------------
# MAIN VIEW CREATION
# --------------------------------------------------------------------------------------

def create_logs_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Any]]:
    """
    Create ultra-enhanced neomorphic logs view with MD3 styling.

    Returns:
        - Main UI container
        - Dispose function for cleanup
        - Setup function for initialization
    """

    # ---------------------------------------------
    # Level Mapping and Configuration
    # ---------------------------------------------

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
            "NOTICE": "SPECIAL",
            "EVENT": "SPECIAL",
            "DEBUG": "DEBUG",
            "INFO": "INFO",
            "ERROR": "ERROR",
        }

        return level_map.get(r, "INFO" if r not in LogColorSystem.COLORS else r)

    # ---------------------------------------------
    # Neomorphic Card Builder
    # This is the heart of the visual design - creates beautiful, elevated log cards
    # ---------------------------------------------

    def build_log_card(log: dict, index: int) -> ft.Control:
        """
        Build a professional neomorphic log card.

        Design features:
        - Dual shadows for neomorphic depth
        - Color-coded level indicator strip
        - Icon with circular background
        - Clean typography hierarchy
        - Hover animations
        - Subtle color tinting based on log level
        """

        # Extract log data safely
        time_s = str(log.get("time", ""))
        level = map_level(log.get("level"))
        comp = str(log.get("component", ""))
        msg = str(log.get("message", ""))

        # Get color configuration for this level
        color_config = LogColorSystem.get_level_config(level)
        primary_color = color_config["primary"]

        # ===== LEFT ACCENT STRIP =====
        # Colored vertical strip that provides immediate visual identification
        accent_strip = ft.Container(
            width=5,
            height=None,  # Full height of card
            bgcolor=primary_color,
            border_radius=ft.border_radius.only(top_left=10, bottom_left=10),
        )

        # ===== ICON CONTAINER =====
        # Circular icon with subtle background matching the log level
        icon_circle = ft.Container(
            content=ft.Icon(
                color_config["icon"],
                size=20,
                color=primary_color,
            ),
            width=40,
            height=40,
            bgcolor=LogColorSystem.get_surface_tint(primary_color, 0.12),
            border_radius=20,
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
                size=10,
                weight=ft.FontWeight.W_700,
                color=primary_color,
            ),
            bgcolor=LogColorSystem.get_surface_tint(primary_color, 0.15),
            padding=ft.padding.symmetric(horizontal=10, vertical=4),
            border_radius=12,
            border=ft.border.all(
                1,
                LogColorSystem.get_border_color(primary_color, 0.2)
            ),
        )

        # ===== MESSAGE TEXT =====
        # Main log message with selectable text
        message_text = ft.Text(
            msg or "(empty message)",
            size=13,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.ON_SURFACE,
            max_lines=3,
            overflow=ft.TextOverflow.ELLIPSIS,
            selectable=True,
        )

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
                            size=11,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        ),
                        ft.Text(
                            comp,
                            size=11,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            weight=ft.FontWeight.W_500,
                        ),
                    ], spacing=4, tight=True),
                    bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.ON_SURFACE_VARIANT),
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    border_radius=6,
                )
            )

        if time_s:
            # Timestamp with clock icon
            metadata_items.append(
                ft.Row([
                    ft.Icon(
                        ft.Icons.ACCESS_TIME_ROUNDED,
                        size=11,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    ),
                    ft.Text(
                        time_s,
                        size=11,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        weight=ft.FontWeight.W_400,
                    ),
                ], spacing=4, tight=True)
            )

        # ===== CARD CONTENT LAYOUT =====
        card_content = ft.Row([
            accent_strip,
            ft.Container(width=16),  # Spacing
            icon_circle,
            ft.Container(width=14),  # Spacing
            # Main content column
            ft.Column([
                message_text,
                ft.Container(height=8),  # Vertical spacing
                ft.Row([
                    *metadata_items,
                    ft.Container(expand=True),  # Push badge to right
                    level_badge,
                ], spacing=8),
            ], spacing=0, expand=True),
            ft.Container(width=16),  # Right padding
        ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        # ===== MAIN CARD CONTAINER =====
        # Neomorphic container with dual shadows and subtle background tint
        card_container = ft.Container(
            content=card_content,
            padding=ft.padding.only(top=14, bottom=14, right=0, left=0),
            border_radius=12,
            # Subtle background tint based on log level
            bgcolor=LogColorSystem.get_surface_tint(primary_color, 0.02),
            # Soft border for definition
            border=ft.border.all(
                1,
                LogColorSystem.get_border_color(primary_color, 0.08)
            ),
            # Neomorphic shadows - the key to the soft UI effect
            shadow=NeomorphicShadows.get_card_shadows("medium" if index < 3 else "low"),
            # Smooth animations for interactions
            animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

        # Hover interaction handler
        def on_card_hover(e: ft.ControlEvent):
            """Enhanced hover effect with scale and shadow changes"""
            is_hovering = e.data == "true"

            if is_hovering:
                card_container.shadow = NeomorphicShadows.get_hover_shadows()
                card_container.scale = 1.015
                card_container.bgcolor = LogColorSystem.get_surface_tint(primary_color, 0.04)
            else:
                card_container.shadow = NeomorphicShadows.get_card_shadows("medium" if index < 3 else "low")
                card_container.scale = 1.0
                card_container.bgcolor = LogColorSystem.get_surface_tint(primary_color, 0.02)

            card_container.update()

        card_container.on_hover = on_card_hover

        return card_container

    # ---------------------------------------------
    # Empty State Component
    # ---------------------------------------------

    def create_empty_state(tab_name: str) -> ft.Control:
        """
        Create professional empty state with neomorphic design.
        Shows when no logs are available.
        """

        icon_map = {
            "System Logs": ft.Icons.DESKTOP_WINDOWS_ROUNDED,
            "Flet Logs": ft.Icons.CODE_ROUNDED,
        }

        # Neomorphic icon container
        icon_container = ft.Container(
            content=ft.Icon(
                icon_map.get(tab_name, ft.Icons.INBOX_ROUNDED),
                size=56,
                color=ft.Colors.ON_SURFACE_VARIANT,
            ),
            width=100,
            height=100,
            bgcolor=ft.Colors.SURFACE,
            border_radius=50,
            alignment=ft.alignment.center,
            shadow=NeomorphicShadows.get_card_shadows("medium"),
        )

        return ft.Container(
            content=ft.Column([
                icon_container,
                ft.Container(height=16),
                ft.Text(
                    f"No {tab_name} Available",
                    size=18,
                    weight=ft.FontWeight.W_600,
                    color=ft.Colors.ON_SURFACE,
                ),
                ft.Text(
                    "Logs will appear here when available",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    weight=ft.FontWeight.W_400,
                ),
                ft.Container(height=20),
                # Neomorphic refresh button
                ft.Container(
                    content=ft.TextButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.REFRESH_ROUNDED, size=18),
                            ft.Text("Refresh", size=14, weight=ft.FontWeight.W_600),
                        ], spacing=8, tight=True),
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(horizontal=24, vertical=12),
                            shape=ft.RoundedRectangleBorder(radius=24),
                            bgcolor=ft.Colors.SURFACE,
                        ),
                        on_click=lambda _: on_refresh_click(_),
                    ),
                    shadow=NeomorphicShadows.get_button_shadows(),
                    border_radius=24,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
            padding=80,
            alignment=ft.alignment.center,
            expand=True,
        )

    # ---------------------------------------------
    # Loading Overlay Component
    # ---------------------------------------------

    def create_loading_overlay() -> ft.Container:
        """Professional loading overlay with neomorphic design"""
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.ProgressRing(
                        width=40,
                        height=40,
                        stroke_width=4,
                        color=ft.Colors.PRIMARY,
                    ),
                    width=80,
                    height=80,
                    bgcolor=ft.Colors.SURFACE,
                    border_radius=40,
                    alignment=ft.alignment.center,
                    shadow=NeomorphicShadows.get_card_shadows("high"),
                ),
                ft.Container(height=16),
                ft.Text(
                    "Loading logs...",
                    size=14,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                    weight=ft.FontWeight.W_500,
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.96, ft.Colors.SURFACE),
            alignment=ft.alignment.center,
            visible=False,
            padding=50,
            border_radius=16,
            shadow=NeomorphicShadows.get_card_shadows("high"),
        )

    # ---------------------------------------------
    # UI State and References
    # ---------------------------------------------

    system_list_ref: ft.Ref[ft.ListView] = ft.Ref()
    flet_list_ref: ft.Ref[ft.ListView] = ft.Ref()
    system_loading_ref: ft.Ref[ft.Container] = ft.Ref()
    flet_loading_ref: ft.Ref[ft.Container] = ft.Ref()

    system_logs_data: list[dict] = []
    flet_logs_data: list[dict] = []

    # Create list views
    def make_listview(ref: ft.Ref[ft.ListView]) -> ft.ListView:
        return ft.ListView(
            ref=ref,
            spacing=12,  # Increased spacing for neomorphic effect
            padding=ft.padding.all(4),
            auto_scroll=False,
            controls=[],
            expand=True,
        )

    # Create loading overlays
    system_loading = create_loading_overlay()
    system_loading.ref = system_loading_ref

    flet_loading = create_loading_overlay()
    flet_loading.ref = flet_loading_ref

    # Create stacks for each tab
    system_stack = ft.Stack([
        make_listview(system_list_ref),
        system_loading,
    ], expand=True)

    flet_stack = ft.Stack([
        make_listview(flet_list_ref),
        flet_loading,
    ], expand=True)

    # ---------------------------------------------
    # Filter System
    # Neomorphic filter chips for log level selection
    # ---------------------------------------------

    selected_levels: set[str] = set()  # Empty means show all
    _chip_refs: dict[str, ft.Chip] = {}

    def _build_filter_chip(level_name: str) -> ft.Chip:
        """Build neomorphic filter chip with level-specific styling"""
        config = LogColorSystem.get_level_config(level_name)

        chip = ft.Chip(
            label=ft.Text(
                config["label"],
                size=11,
                weight=ft.FontWeight.W_700,
            ),
            selected=(level_name in selected_levels),
            on_select=lambda e, n=level_name: _on_toggle_level(n, e.control.selected),
            leading=ft.Icon(config["icon"], size=15),
            bgcolor=LogColorSystem.get_surface_tint(config["primary"], 0.08),
            selected_color=LogColorSystem.get_surface_tint(config["primary"], 0.20),
            label_padding=ft.padding.symmetric(horizontal=8, vertical=6),
            # Note: Chip doesn't support border in Flet 0.28.3
        )

        _chip_refs[level_name] = chip
        return chip

    def _on_toggle_level(level_name: str, is_selected: bool):
        """Handle filter chip toggle"""
        nonlocal selected_levels

        if is_selected:
            selected_levels.add(level_name)
        else:
            selected_levels.discard(level_name)

        # Update chip appearance
        chip = _chip_refs.get(level_name)
        if chip:
            config = LogColorSystem.get_level_config(level_name)
            chip.selected = is_selected
            chip.bgcolor = LogColorSystem.get_surface_tint(
                config["primary"],
                0.20 if is_selected else 0.08
            )
            # Update icon color
            if chip.leading:
                chip.leading.color = config["primary"]
            chip.update()

        # Refresh lists with new filter
        _refresh_lists_by_filter()

    def _passes_filter(log: dict) -> bool:
        """Check if log passes current filter"""
        if not selected_levels:
            return True
        return map_level(log.get("level")) in selected_levels

    def _render_list(lst_ref: ft.Ref[ft.ListView], data: list[dict], tab_name: str):
        """Render log list with filtering"""
        if not lst_ref.current:
            return

        # CRITICAL: Check if control is attached to page before updating
        # The ref might be populated before the control is in the page tree
        if not hasattr(lst_ref.current, 'page') or lst_ref.current.page is None:
            return

        if not data:
            # Show empty state
            lst_ref.current.controls = [create_empty_state(tab_name)]
        else:
            # Filter data
            filtered_data = [row for row in data if _passes_filter(row)]

            if not filtered_data:
                # Show "no matches" state
                lst_ref.current.controls = [
                    ft.Container(
                        content=ft.Column([
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.FILTER_LIST_OFF_ROUNDED,
                                    size=48,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                ),
                                width=80,
                                height=80,
                                bgcolor=ft.Colors.SURFACE,
                                border_radius=40,
                                alignment=ft.alignment.center,
                                shadow=NeomorphicShadows.get_card_shadows("medium"),
                            ),
                            ft.Container(height=16),
                            ft.Text(
                                "No logs match the selected filters",
                                size=15,
                                color=ft.Colors.ON_SURFACE,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                "Try adjusting your filter selection",
                                size=13,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        padding=60,
                        alignment=ft.alignment.center,
                    )
                ]
            else:
                # Render log cards
                lst_ref.current.controls = [
                    build_log_card(row, idx) for idx, row in enumerate(filtered_data)
                ]

        lst_ref.current.update()

    def _refresh_lists_by_filter():
        """Refresh both lists with current filter settings"""
        _render_list(system_list_ref, system_logs_data, "System Logs")
        _render_list(flet_list_ref, flet_logs_data, "Flet Logs")

    # ---------------------------------------------
    # Tab System
    # Custom neomorphic tab bar
    # ---------------------------------------------

    active_tab_index = 0

    def _create_tab_button(label: str, icon: str, idx: int, is_active: bool) -> ft.Container:
        """Create neomorphic tab button"""
        # Color configuration based on active state
        if is_active:
            text_color = ft.Colors.PRIMARY
            icon_color = ft.Colors.PRIMARY
            bg_color = LogColorSystem.get_surface_tint(ft.Colors.PRIMARY, 0.12)
            border_color = LogColorSystem.get_border_color(ft.Colors.PRIMARY, 0.3)
            shadows = NeomorphicShadows.get_pressed_shadows()
        else:
            text_color = ft.Colors.ON_SURFACE_VARIANT
            icon_color = ft.Colors.ON_SURFACE_VARIANT
            bg_color = ft.Colors.SURFACE
            border_color = ft.Colors.OUTLINE_VARIANT
            shadows = NeomorphicShadows.get_button_shadows()

        button_content = ft.Row([
            ft.Icon(icon, size=18, color=icon_color),
            ft.Text(
                label,
                size=14,
                weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_500,
                color=text_color
            ),
        ], spacing=10, tight=True)

        return ft.Container(
            content=button_content,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=12,
            bgcolor=bg_color,
            border=ft.border.all(1, border_color),
            shadow=shadows,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_click=lambda _: _on_tab_click(idx),
            ink=True,
        )

    tabbar_row_ref: ft.Ref[ft.Row] = ft.Ref()
    content_host_ref: ft.Ref[ft.Container] = ft.Ref()

    def _render_tabbar():
        """Render tab bar with current active tab"""
        if not tabbar_row_ref.current:
            return

        # CRITICAL: Check if control is attached to page before updating
        if not hasattr(tabbar_row_ref.current, 'page') or tabbar_row_ref.current.page is None:
            return

        tabbar_row_ref.current.controls = [
            _create_tab_button("System Logs", ft.Icons.ARTICLE_ROUNDED, 0, active_tab_index == 0),
            _create_tab_button("Flet Logs", ft.Icons.CODE_ROUNDED, 1, active_tab_index == 1),
        ]
        tabbar_row_ref.current.update()

    def _render_active_content():
        """Render content for active tab"""
        if not content_host_ref.current:
            return

        # CRITICAL: Check if control is attached to page before updating
        if not hasattr(content_host_ref.current, 'page') or content_host_ref.current.page is None:
            return

        content_host_ref.current.content = (
            system_stack if active_tab_index == 0 else flet_stack
        )
        content_host_ref.current.update()

    def _on_tab_click(idx: int):
        """Handle tab click"""
        nonlocal active_tab_index
        if idx == active_tab_index:
            return

        active_tab_index = idx
        _render_tabbar()
        _render_active_content()

    # ---------------------------------------------
    # Action Functions
    # ---------------------------------------------

    _system_first_load = True
    _flet_first_load = True

    async def refresh_system_logs(show_toast: bool = False, show_spinner: bool = False):
        """Refresh system logs from server"""
        nonlocal _system_first_load

        if system_loading_ref.current and (show_spinner or _system_first_load):
            # CRITICAL: Only update if attached to page
            if hasattr(system_loading_ref.current, 'page') and system_loading_ref.current.page:
                system_loading_ref.current.visible = True
                system_loading_ref.current.update()

        # Fetch logs
        logs = get_system_logs(server_bridge)

        # Normalize log format
        safe_logs: list[dict] = []
        for item in logs:
            if isinstance(item, dict):
                safe_logs.append({
                    "time": item.get("time") or item.get("timestamp") or "",
                    "level": item.get("level") or item.get("severity") or "INFO",
                    "component": item.get("component") or item.get("module") or "",
                    "message": item.get("message") or item.get("msg") or "",
                })
            else:
                safe_logs.append({
                    "time": "",
                    "level": "INFO",
                    "component": "",
                    "message": str(item)
                })

        nonlocal system_logs_data
        system_logs_data = safe_logs
        _render_list(system_list_ref, system_logs_data, "System Logs")

        if system_loading_ref.current and (show_spinner or _system_first_load):
            # CRITICAL: Only update if attached to page
            if hasattr(system_loading_ref.current, 'page') and system_loading_ref.current.page:
                system_loading_ref.current.visible = False
                system_loading_ref.current.update()

        _system_first_load = False

        if show_toast:
            _show_toast(page, "System logs refreshed", "success")

    async def refresh_flet_logs(show_toast: bool = False, show_spinner: bool = False):
        """Refresh Flet logs from capture handler"""
        nonlocal _flet_first_load

        if flet_loading_ref.current and (show_spinner or _flet_first_load):
            # CRITICAL: Only update if attached to page
            if hasattr(flet_loading_ref.current, 'page') and flet_loading_ref.current.page:
                flet_loading_ref.current.visible = True
                flet_loading_ref.current.update()

        nonlocal flet_logs_data
        flet_logs_data = _flet_log_capture.logs.copy() if _flet_log_capture.logs else []
        _render_list(flet_list_ref, flet_logs_data, "Flet Logs")

        if flet_loading_ref.current and (show_spinner or _flet_first_load):
            # CRITICAL: Only update if attached to page
            if hasattr(flet_loading_ref.current, 'page') and flet_loading_ref.current.page:
                flet_loading_ref.current.visible = False
                flet_loading_ref.current.update()

        _flet_first_load = False

        if show_toast:
            _show_toast(page, "Flet logs refreshed", "success")

    def on_refresh_click(_: ft.ControlEvent):
        """Handle refresh button click"""
        if active_tab_index == 0:
            page.run_task(refresh_system_logs(show_toast=True, show_spinner=True))
        else:
            page.run_task(refresh_flet_logs(show_toast=True, show_spinner=True))

    def on_export_click(_: ft.ControlEvent):
        """Export logs to JSON file"""
        try:
            export_dir = os.path.join(_repo_root, "logs_exports")
            os.makedirs(export_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            payload = {
                "exported_at": timestamp,
                "export_datetime": datetime.now().isoformat(),
                "system_logs": system_logs_data,
                "flet_logs": flet_logs_data or _flet_log_capture.logs.copy(),
            }

            filepath = os.path.join(export_dir, f"logs_{timestamp}.json")

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)

            _show_toast(page, f"Exported to {filepath}", "success")
        except Exception as e:
            _show_toast(page, f"Export failed: {str(e)}", "error")

    async def on_clear_flet_click(_: ft.ControlEvent):
        """Clear Flet logs"""
        try:
            _flet_log_capture.logs.clear()
            await refresh_flet_logs(show_toast=False)
            _show_toast(page, "Cleared Flet logs", "success")
        except Exception as e:
            _show_toast(page, f"Clear failed: {str(e)}", "error")

    # ---------------------------------------------
    # Toast Notifications
    # ---------------------------------------------

    def _show_toast(pg: ft.Page, message: str, toast_type: str = "info"):
        """Show toast notification with appropriate styling"""
        try:
            # Color based on type
            if toast_type == "error":
                bg_color = ft.Colors.ERROR_CONTAINER
                text_color = ft.Colors.ON_ERROR_CONTAINER
                icon = ft.Icons.ERROR_OUTLINE_ROUNDED
            elif toast_type == "success":
                bg_color = LogColorSystem.get_surface_tint("#10B981", 0.9)
                text_color = ft.Colors.ON_PRIMARY_CONTAINER
                icon = ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED
            else:
                bg_color = ft.Colors.SURFACE_CONTAINER_HIGHEST
                text_color = ft.Colors.ON_SURFACE
                icon = ft.Icons.INFO_OUTLINE_ROUNDED

            pg.snack_bar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(icon, color=text_color, size=20),
                    ft.Text(message, color=text_color, size=14),
                ], spacing=12),
                bgcolor=bg_color,
                show_close_icon=True,
                close_icon_color=text_color,
                duration=3000,
            )
            pg.snack_bar.open = True
            pg.update()
        except Exception:
            pass

    # ---------------------------------------------
    # Action Buttons
    # Neomorphic buttons with proper styling
    # ---------------------------------------------

    def _create_neomorphic_button(
        text: str,
        icon: str,
        on_click: Callable,
        style_type: str = "tonal"
    ) -> ft.Container:
        """Create neomorphic button"""

        if style_type == "tonal":
            bg_color = ft.Colors.SECONDARY_CONTAINER
            text_color = ft.Colors.ON_SECONDARY_CONTAINER
        else:  # outlined
            bg_color = ft.Colors.SURFACE
            text_color = ft.Colors.PRIMARY

        button_content = ft.Row([
            ft.Icon(icon, size=18, color=text_color),
            ft.Text(text, size=14, weight=ft.FontWeight.W_600, color=text_color),
        ], spacing=8, tight=True)

        return ft.Container(
            content=button_content,
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border_radius=12,
            bgcolor=bg_color,
            border=ft.border.all(
                1,
                ft.Colors.OUTLINE_VARIANT if style_type == "outlined" else ft.Colors.TRANSPARENT
            ),
            shadow=NeomorphicShadows.get_button_shadows(),
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            on_click=on_click,
            ink=True,
        )

    # Auto-refresh switch
    auto_refresh_switch = ft.Switch(
        label="Auto-refresh",
        value=True,
        label_style=ft.TextStyle(size=14, weight=ft.FontWeight.W_500),
    )

    # Action buttons row
    action_buttons = ft.Row([
        _create_neomorphic_button(
            "Refresh",
            ft.Icons.REFRESH_ROUNDED,
            on_refresh_click,
            "tonal"
        ),
        _create_neomorphic_button(
            "Export",
            ft.Icons.DOWNLOAD_ROUNDED,
            on_export_click,
            "outlined"
        ),
        _create_neomorphic_button(
            "Clear Flet Logs",
            ft.Icons.DELETE_SWEEP_ROUNDED,
            on_clear_flet_click,
            "outlined"
        ),
    ], spacing=12, wrap=True)

    # ---------------------------------------------
    # Header Section
    # ---------------------------------------------

    # Neomorphic header icon
    header_icon = ft.Container(
        content=ft.Icon(
            ft.Icons.ARTICLE_ROUNDED,
            size=32,
            color=ft.Colors.PRIMARY,
        ),
        width=56,
        height=56,
        bgcolor=ft.Colors.SURFACE,
        border_radius=16,
        alignment=ft.alignment.center,
        shadow=NeomorphicShadows.get_card_shadows("medium"),
    )

    header_row = ft.Row([
        ft.Row([
            header_icon,
            ft.Container(width=16),
            ft.Text(
                "Logs",
                size=32,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.ON_SURFACE,
            ),
        ], spacing=0),
        ft.Row([
            auto_refresh_switch,
            ft.Container(width=16),
            action_buttons,
        ], spacing=0, wrap=True),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True)

    # ---------------------------------------------
    # Filter Row
    # ---------------------------------------------

    filter_chips = ft.Row([
        _build_filter_chip("INFO"),
        _build_filter_chip("SUCCESS"),
        _build_filter_chip("WARNING"),
        _build_filter_chip("IMPORTANT"),
        _build_filter_chip("ERROR"),
        _build_filter_chip("CRITICAL"),
        _build_filter_chip("SPECIAL"),
        _build_filter_chip("DEBUG"),
    ], scroll="auto", spacing=10)

    filter_container = ft.Container(
        content=filter_chips,
        padding=ft.padding.symmetric(vertical=8),
    )

    # ---------------------------------------------
    # Tab Bar and Content
    # ---------------------------------------------

    tabbar = ft.Row(ref=tabbar_row_ref, spacing=12)
    content_host = ft.Container(
        ref=content_host_ref,
        expand=True,
        bgcolor=ft.Colors.TRANSPARENT,
    )

    # ---------------------------------------------
    # Main Layout
    # ---------------------------------------------

    main_content = ft.Column([
        ft.Container(content=header_row, padding=ft.padding.only(bottom=20)),
        filter_container,
        ft.Container(content=tabbar, padding=ft.padding.symmetric(vertical=12)),
        content_host,
    ], spacing=0, expand=True)

    # Main container with padding
    main_container = ft.Container(
        content=main_content,
        padding=28,
        expand=True,
        bgcolor=ft.Colors.SURFACE,
    )

    # ---------------------------------------------
    # Lifecycle Management
    # ---------------------------------------------

    _live_task: Optional[asyncio.Task] = None

    def dispose():
        """Cleanup function"""
        nonlocal _live_task
        if _live_task and not _live_task.done():
            _live_task.cancel()
        _live_task = None

    async def _auto_refresh_loop():
        """Background task for auto-refresh"""
        try:
            while True:
                # Only refresh if auto-refresh is enabled
                if auto_refresh_switch.value:
                    if active_tab_index == 0:
                        await refresh_system_logs(show_toast=False, show_spinner=False)
                    else:
                        await refresh_flet_logs(show_toast=False, show_spinner=False)

                await asyncio.sleep(2.0)  # Refresh every 2 seconds
        except asyncio.CancelledError:
            return
        except Exception:
            # Don't crash on background errors
            return

    async def setup_subscriptions():
        """Initialize view"""
        nonlocal _live_task

        # CRITICAL FIX: Wait for refs to be fully initialized
        # Flet needs time to attach controls to page tree and populate refs
        # Without this delay, ListView.update() fails with "Control must be added to the page first"
        await asyncio.sleep(0.3)

        # Additional safety: Wait for refs to be populated
        max_wait = 20  # 2 seconds max wait
        wait_count = 0
        while wait_count < max_wait:
            if (tabbar_row_ref.current and content_host_ref.current and
                system_list_ref.current and flet_list_ref.current):
                break
            await asyncio.sleep(0.1)
            wait_count += 1

        # Render initial UI
        _render_tabbar()
        _render_active_content()

        # Load initial data
        await refresh_system_logs(show_toast=False, show_spinner=True)
        await refresh_flet_logs(show_toast=False, show_spinner=True)

        # Start auto-refresh loop
        try:
            _live_task = asyncio.create_task(_auto_refresh_loop())
        except Exception:
            _live_task = None

    return main_container, dispose, setup_subscriptions