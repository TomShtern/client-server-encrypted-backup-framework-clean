#!/usr/bin/env python3
"""
Logs View - Neumorphic, MD3-styled dual tabs

- System Logs: fetched from server bridge
- Flet Logs: captured via logging.Handler (optional live updates)

Design goals:
- Neumorphic cards with subtle elevation (theme shadows)
- MD3 accents and color-coded log levels
- Efficient ListView rendering (avoid DataTable freezes in 0.28.3)
"""

import os
import sys
import logging
import contextlib
from datetime import datetime
import asyncio
import json
from typing import Any, Callable

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
# MD3 color token polyfills for Flet 0.28.x
# Some Material 3 colors like SURFACE_CONTAINER_LOW/HIGHEST may not exist in older
# Flet versions. Define graceful fallbacks so the view doesn't crash at runtime.
# --------------------------------------------------------------------------------------
def _ensure_color_attr(attr_name: str, fallback_factory: Callable[[], str]) -> None:
    try:
        if not hasattr(ft.Colors, attr_name):
            setattr(ft.Colors, attr_name, fallback_factory())
    except Exception:
        # Last-resort fallback to SURFACE
        with contextlib.suppress(Exception):
            setattr(ft.Colors, attr_name, getattr(ft.Colors, "SURFACE", "#121212"))

_ensure_color_attr(
    "SURFACE_CONTAINER_LOW",
    lambda: ft.Colors.with_opacity(0.06, getattr(ft.Colors, "SURFACE", "#121212")),
)
_ensure_color_attr(
    "SURFACE_CONTAINER_HIGHEST",
    lambda: ft.Colors.with_opacity(0.16, getattr(ft.Colors, "SURFACE", "#121212")),
)
_ensure_color_attr(
    "ON_SURFACE_VARIANT",
    # If missing, approximate with a dimmed ON_SURFACE (or SURFACE as last resort)
    lambda: ft.Colors.with_opacity(0.70, getattr(ft.Colors, "ON_SURFACE", getattr(ft.Colors, "SURFACE", "#FFFFFF"))),
)
_ensure_color_attr(
    "OUTLINE",
    # Approximate MD outline with 12% of on-surface
    lambda: ft.Colors.with_opacity(0.12, getattr(ft.Colors, "ON_SURFACE", getattr(ft.Colors, "SURFACE", "#FFFFFF"))),
)

# Import neumorphic shadows and glassmorphic configs from theme
try:
    from theme import (
        PRONOUNCED_NEUMORPHIC_SHADOWS,
        MODERATE_NEUMORPHIC_SHADOWS,
        SUBTLE_NEUMORPHIC_SHADOWS,
        INSET_NEUMORPHIC_SHADOWS,
        GLASS_STRONG,
        GLASS_MODERATE,
        GLASS_SUBTLE,
    )
except ImportError:
    PRONOUNCED_NEUMORPHIC_SHADOWS = []
    MODERATE_NEUMORPHIC_SHADOWS = []
    SUBTLE_NEUMORPHIC_SHADOWS = []
    INSET_NEUMORPHIC_SHADOWS = []
    GLASS_STRONG = {"blur": 15, "bg_opacity": 0.12, "border_opacity": 0.2}
    GLASS_MODERATE = {"blur": 12, "bg_opacity": 0.10, "border_opacity": 0.15}
    GLASS_SUBTLE = {"blur": 10, "bg_opacity": 0.08, "border_opacity": 0.12}


# ======================================================================================
# FLET LOG CAPTURE SYSTEM
# ======================================================================================

class FletLogCapture(logging.Handler):
    """Custom logging handler to capture Flet framework logs in real-time."""

    def __init__(self):
        super().__init__()
        self.logs = []
        self.max_logs = 100  # Keep last 100 logs

    def emit(self, record):
        """Capture log record and format it."""
        with contextlib.suppress(Exception):
            self.logs.insert(0, {
                "time": datetime.fromtimestamp(record.created).strftime("%H:%M:%S"),
                "level": record.levelname,
                "component": record.name,
                "message": self.format(record)
            })
            # Limit to max_logs
            if len(self.logs) > self.max_logs:
                self.logs = self.logs[:self.max_logs]


# Global Flet log capture instance
_flet_log_capture = FletLogCapture()
_flet_log_capture.setFormatter(logging.Formatter('%(message)s'))

# Attach to root logger to capture all logs (avoid duplicates on hot reload)
_root_logger = logging.getLogger()
if not any(isinstance(h, FletLogCapture) for h in _root_logger.handlers):
    _root_logger.addHandler(_flet_log_capture)


# ======================================================================================
# DATA FETCHING
# ======================================================================================

def get_system_logs(server_bridge: Any | None) -> list[dict]:
    """Get system logs from server or return empty list."""
    if not server_bridge:
        return []  # Return empty, not mock data
    try:
        result = server_bridge.get_logs()
        if isinstance(result, dict) and result.get('success'):
            return result.get('data', [])
        return []
    except Exception:
        return []


# ======================================================================================
# UI CREATION
# ======================================================================================

def create_logs_view(
    server_bridge: Any | None,
    page: ft.Page,
    state_manager: Any | None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Any]]:
    """Create logs view with dual-tab system and neumorphic design."""

    # ---------------------------------------------
    # Level config and helpers
    # ---------------------------------------------
    LEVELS = {
        # canonical level -> dict of styles
        "DEBUG": {
            "color": ft.Colors.GREY_500,
            "bg": ft.Colors.GREY_100,
            "icon": ft.Icons.BUG_REPORT,
            "label": "DEBUG",
        },
        "INFO": {
            "color": ft.Colors.BLUE_500,
            "bg": ft.Colors.BLUE_100,
            "icon": ft.Icons.INFO,
            "label": "INFO",
        },
        "SUCCESS": {
            "color": ft.Colors.GREEN_600,
            "bg": ft.Colors.GREEN_100,
            "icon": ft.Icons.CHECK_CIRCLE,
            "label": "SUCCESS",
        },
        "WARNING": {
            "color": ft.Colors.AMBER_600,
            "bg": ft.Colors.AMBER_100,
            "icon": ft.Icons.WARNING_AMBER,
            "label": "WARNING",
        },
        "IMPORTANT": {  # important warning / orange
            "color": ft.Colors.ORANGE_700,
            "bg": ft.Colors.ORANGE_100,
            "icon": ft.Icons.REPORT_GMAILERRORRED,
            "label": "IMPORTANT",
        },
        "ERROR": {
            "color": ft.Colors.RED_600,
            "bg": ft.Colors.RED_100,
            "icon": ft.Icons.ERROR,
            "label": "ERROR",
        },
        "CRITICAL": {
            "color": ft.Colors.DEEP_ORANGE_700,
            "bg": ft.Colors.DEEP_ORANGE_100,
            "icon": ft.Icons.ERROR_OUTLINE,
            "label": "CRITICAL",
        },
        "SPECIAL": {
            "color": ft.Colors.DEEP_PURPLE_500,
            "bg": ft.Colors.DEEP_PURPLE_100,
            "icon": ft.Icons.STARS,
            "label": "SPECIAL",
        },
        "EVENT": {
            "color": ft.Colors.PURPLE_500,
            "bg": ft.Colors.PURPLE_100,
            "icon": ft.Icons.EVENT,
            "label": "EVENT",
        },
    }

    def map_level(raw: str | None) -> str:
        if not raw:
            return "INFO"
        r = str(raw).strip().upper()
        # common aliases
        if r in {"WARN", "WARNING"}:  # prefer WARNING
            return "WARNING"
        if r in {"CRIT", "FATAL"}:  # critical
            return "CRITICAL"
        if r in {"OK", "SUCCESS"}:  # success
            return "SUCCESS"
        if r in {"IMPORTANT", "ALERT"}:  # orange
            return "IMPORTANT"
        if r in {"SPECIAL", "NOTICE", "EVENT"}:  # purple family
            return "SPECIAL"
        return r if r in LEVELS else "INFO"

    def level_styles(level: str) -> dict:
        l = LEVELS.get(level, LEVELS["INFO"])
        # subtle surface tint using opacity
        tint = ft.Colors.with_opacity(0.08, l["color"])  # subtle card tint
        accent = l["color"]
        return {
            "tint": tint,
            "accent": accent,
            "icon": l["icon"],
            "label": l["label"],
        }

    # ---------------------------------------------
    # UI State & Refs (MUST BE BEFORE FUNCTIONS THAT USE THEM)
    # ---------------------------------------------
    system_list_ref: ft.Ref[ft.ListView] = ft.Ref()
    flet_list_ref: ft.Ref[ft.ListView] = ft.Ref()
    system_loading_ref: ft.Ref[ft.Container] = ft.Ref()
    flet_loading_ref: ft.Ref[ft.Container] = ft.Ref()
    stats_card_ref: ft.Ref[ft.Container] = ft.Ref()
    search_field_ref: ft.Ref[ft.TextField] = ft.Ref()

    # stores
    system_logs_data: list[dict] = []
    flet_logs_data: list[dict] = []

    # Search state
    search_query: str = ""

    # Density state
    density_presets = {
        "compact": {"padding": 8, "spacing": 6, "font_size": 12, "label": "Compact"},
        "normal": {"padding": 14, "spacing": 10, "font_size": 14, "label": "Normal"},
        "comfortable": {"padding": 18, "spacing": 14, "font_size": 16, "label": "Comfortable"},
    }
    current_density_mode: str = "normal"
    current_density = density_presets[current_density_mode]

    # Expansion state
    expanded_cards: set[str] = set()  # Track which cards are expanded

    # Filter chips (level filtering)
    selected_levels: set[str] = set()  # empty => all

    # ---------------------------------------------
    # Search Highlighting Helper (MUST BE BEFORE build_log_card)
    # ---------------------------------------------
    def _highlight_search_text(text: str, query: str, font_size: int):
        """Highlight search query in text using TextSpans."""
        if not query.strip():
            return ft.Text(text, size=font_size, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE, selectable=True)

        # Case-insensitive search
        lower_text = text.lower()
        lower_query = query.lower()

        spans: list[ft.TextSpan] = []
        last_index = 0

        # Find all occurrences
        while True:
            index = lower_text.find(lower_query, last_index)
            if index == -1:
                # Add remaining text
                if last_index < len(text):
                    spans.append(ft.TextSpan(text[last_index:]))
                break

            # Add text before match
            if index > last_index:
                spans.append(ft.TextSpan(text[last_index:index]))

            # Add highlighted match
            spans.append(ft.TextSpan(
                text[index:index + len(query)],
                style=ft.TextStyle(
                    bgcolor=ft.Colors.YELLOW_ACCENT_700,
                    color=ft.Colors.BLACK,
                    weight=ft.FontWeight.BOLD,
                )
            ))

            last_index = index + len(query)

        return ft.Text(spans=spans, size=font_size, weight=ft.FontWeight.W_600, selectable=True)

    # ---------------------------------------------
    # Statistics Card Builder
    # ---------------------------------------------
    def _build_statistics_card(logs_data: list[dict]) -> ft.Container:
        """Build visual statistics dashboard showing log level distribution."""
        if not logs_data:
            return ft.Container(height=0)  # Hidden when no data

        # Count by level
        level_counts: dict[str, int] = {}
        for log in logs_data:
            level = map_level(log.get("level"))
            level_counts[level] = level_counts.get(level, 0) + 1

        total = len(logs_data)

        # Build gauge for each level (only if count > 0)
        gauge_items: list[ft.Control] = []
        for level_name in ["INFO", "SUCCESS", "WARNING", "IMPORTANT", "ERROR", "CRITICAL"]:
            count = level_counts.get(level_name, 0)
            if count == 0:
                continue  # Skip levels with no logs

            st = level_styles(level_name)
            percentage = (count / total) if total > 0 else 0

            # Circular gauge with count overlay
            gauge = ft.Stack([
                ft.ProgressRing(
                    value=percentage,
                    width=70,
                    height=70,
                    stroke_width=8,
                    color=st["accent"],
                    bgcolor=ft.Colors.with_opacity(0.1, st["accent"]),
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Text(str(count), size=18, weight=ft.FontWeight.BOLD, color=st["accent"]),
                        ft.Text(f"{int(percentage*100)}%", size=10, color=ft.Colors.ON_SURFACE_VARIANT),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                    alignment=ft.alignment.center,
                    width=70,
                    height=70,
                ),
            ])

            # Label below gauge
            gauge_col = ft.Column([
                gauge,
                ft.Container(height=4),
                ft.Text(level_name, size=11, weight=ft.FontWeight.W_600, color=st["accent"], text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)

            gauge_items.append(gauge_col)

        # Statistics card with glassmorphic styling
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.ANALYTICS, size=20, color=ft.Colors.PRIMARY),
                    ft.Text("Log Statistics", size=16, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                    ft.Text(f"Total: {total}", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
                ], spacing=8),
                ft.Container(height=12),
                ft.Row(gauge_items, spacing=16, scroll="auto", alignment=ft.MainAxisAlignment.START),
            ], spacing=0),
            padding=16,
            border_radius=16,
            bgcolor=ft.Colors.with_opacity(GLASS_MODERATE["bg_opacity"], ft.Colors.SURFACE),
            border=ft.border.all(1, ft.Colors.with_opacity(GLASS_MODERATE["border_opacity"], ft.Colors.OUTLINE)),
            shadow=MODERATE_NEUMORPHIC_SHADOWS,
            animate=300,  # Animation duration in milliseconds
        )

    # ---------------------------------------------
    # Card builder with enhanced visual effects
    # ---------------------------------------------
    def build_log_card(log: dict, index: int = 0, apply_entrance_animation: bool = False) -> ft.Control:
        # Safe access
        time_s = str(log.get("time", ""))
        level = map_level(log.get("level"))
        comp = str(log.get("component", ""))
        msg = str(log.get("message", ""))

        st = level_styles(level)

        # Create unique ID for this card (for expansion tracking)
        card_id = f"{time_s}_{comp}_{hash(msg) % 10000}"
        is_expanded = card_id in expanded_cards

        # Check if message is long (needs expansion capability)
        is_long_message = len(msg) > 100
        display_msg = msg if (is_expanded or not is_long_message) else msg[:100] + "..."

        # Severity-based shadow selection (visual hierarchy)
        is_high_severity = level in {"ERROR", "CRITICAL"}
        default_shadow = MODERATE_NEUMORPHIC_SHADOWS if is_high_severity else SUBTLE_NEUMORPHIC_SHADOWS
        hover_shadow = PRONOUNCED_NEUMORPHIC_SHADOWS if is_high_severity else MODERATE_NEUMORPHIC_SHADOWS

        # Level dot (leading) with pulsing animation for critical
        dot = ft.Container(
            width=10,
            height=10,
            border_radius=999,
            bgcolor=st["accent"],
            animate_scale=800 if level == "CRITICAL" else None,  # Animation duration in milliseconds
            scale=1.0,
        )

        # Level pill (trailing) with enhanced styling
        level_pill = ft.Container(
            content=ft.Row([
                ft.Icon(st["icon"], size=14, color=st["accent"]),
                ft.Text(level, size=11, weight=ft.FontWeight.W_600, color=st["accent"]),
            ], spacing=4, tight=True),
            bgcolor=ft.Colors.with_opacity(0.10, st["accent"]),
            padding=ft.padding.symmetric(horizontal=8, vertical=3),
            border_radius=999,
            shadow=SUBTLE_NEUMORPHIC_SHADOWS[:1],  # Subtle depth to pill
        )

        # Title with expansion toggle handler
        def toggle_expansion(e):
            nonlocal is_expanded
            if card_id in expanded_cards:
                expanded_cards.discard(card_id)
            else:
                expanded_cards.add(card_id)
            # Refresh the list to rebuild cards with new expansion state
            _refresh_lists_by_filter()

        # Message display (with search highlighting if active)
        message_content = ft.Text(
            display_msg or "(no message)",
            size=current_density["font_size"],
            weight=ft.FontWeight.W_600,
            color=ft.Colors.ON_SURFACE,
            max_lines=None if is_expanded else 3,
            overflow=ft.TextOverflow.VISIBLE if is_expanded else ft.TextOverflow.ELLIPSIS,
            selectable=True,
        )

        # Apply search highlighting if search is active
        if search_query.strip():
            message_content = _highlight_search_text(display_msg or "(no message)", search_query, current_density["font_size"])

        # Expansion button (only for long messages)
        expansion_icon = None
        if is_long_message:
            expansion_icon = ft.IconButton(
                icon=ft.Icons.EXPAND_LESS if is_expanded else ft.Icons.EXPAND_MORE,
                icon_size=20,
                icon_color=st["accent"],
                on_click=toggle_expansion,
                tooltip="Collapse" if is_expanded else "Expand",
            )

        # Subtitle items with density-aware font size
        subtitle_size = max(10, current_density["font_size"] - 2)
        subtitle_items: list[ft.Control] = []
        if comp:
            subtitle_items.append(ft.Text(comp, size=subtitle_size, color=ft.Colors.ON_SURFACE_VARIANT))
        if time_s:
            if subtitle_items:
                subtitle_items.append(ft.Text(" • ", size=subtitle_size, color=ft.Colors.ON_SURFACE_VARIANT))
            subtitle_items.append(ft.Text(time_s, size=subtitle_size, color=ft.Colors.ON_SURFACE_VARIANT))

        subtitle = ft.Row(subtitle_items, spacing=4)

        # Expanded details section (only shown when expanded)
        expanded_details = None
        if is_expanded and is_long_message:
            expanded_details = ft.Container(
                content=ft.Column([
                    ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, st["accent"])),
                    ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                        ft.Text("Details", size=11, weight=ft.FontWeight.W_600, color=ft.Colors.ON_SURFACE_VARIANT),
                    ], spacing=6),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.LABEL, size=12, color=st["accent"]),
                                ft.Text(f"Level: {level}", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                            ], spacing=4),
                            ft.Row([
                                ft.Icon(ft.Icons.ACCESS_TIME, size=12, color=st["accent"]),
                                ft.Text(f"Time: {time_s}", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                            ], spacing=4) if time_s else None,
                            ft.Row([
                                ft.Icon(ft.Icons.WIDGETS, size=12, color=st["accent"]),
                                ft.Text(f"Component: {comp or 'N/A'}", size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                            ], spacing=4),
                        ], spacing=4),
                        padding=ft.padding.only(left=8, top=4),
                    ),
                ], spacing=8),
                padding=ft.padding.only(top=8),
                animate_size=300,  # Animation duration in milliseconds
            )

        # Build card content column
        card_content_items = [
            ft.Row([
                dot,
                ft.Container(width=current_density["spacing"]),
                ft.Column([
                    message_content,
                    subtitle,
                ], spacing=current_density["spacing"] // 2, expand=True),
                level_pill,
                expansion_icon or ft.Container(width=0),
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ]

        # Add expanded details if applicable
        if expanded_details:
            card_content_items.append(expanded_details)

        # Card surface with neumorphic depth, hover effects, and density-aware sizing
        card_surface = ft.Container(
            content=ft.Column(card_content_items, spacing=0),
            padding=current_density["padding"],
            border_radius=12,
            bgcolor=ft.Colors.with_opacity(0.02, st["tint"]),  # Subtle tint
            border=ft.border.all(1, ft.Colors.with_opacity(0.08, st["accent"])),
            shadow=default_shadow,
            animate=200,  # Animation duration in milliseconds
            animate_scale=200,  # Animation duration in milliseconds
            animate_size=300,  # Animation duration in milliseconds
            scale=1.0,
            opacity=0.0 if apply_entrance_animation else 1.0,  # Start invisible for entrance animation
            animate_opacity=400 if apply_entrance_animation else None,  # Animation duration in milliseconds
        )

        # Hover handler for interactive feedback
        def on_card_hover(e):
            is_hovered = e.data == "true"
            card_surface.shadow = hover_shadow if is_hovered else default_shadow
            card_surface.scale = 1.015 if is_hovered else 1.0
            card_surface.border = ft.border.all(
                2 if is_hovered else 1,
                ft.Colors.with_opacity(0.24 if is_hovered else 0.08, st["accent"])
            )
            card_surface.bgcolor = ft.Colors.with_opacity(0.05 if is_hovered else 0.02, st["tint"])
            card_surface.update()

            # Pulse critical dot on hover
            if level == "CRITICAL" and is_hovered:
                dot.scale = 1.3
                dot.update()
            elif level == "CRITICAL":
                dot.scale = 1.0
                dot.update()

        card_surface.on_hover = on_card_hover

        # Trigger entrance animation if requested (after a delay based on index)
        if apply_entrance_animation:
            async def animate_entrance():
                await asyncio.sleep(min(index * 0.03, 0.45))  # Max 450ms delay for smooth effect
                card_surface.opacity = 1.0
                card_surface.update()

            # Schedule animation (use page.run_task if available)
            with contextlib.suppress(Exception):
                if page and hasattr(page, 'run_task'):
                    page.run_task(animate_entrance)
        # Return the enhanced card with depth and interactivity
        return card_surface

    # Builders for list views
    def make_listview(ref: ft.Ref[ft.ListView]) -> ft.ListView:
        return ft.ListView(ref=ref, spacing=10, padding=0, auto_scroll=False, controls=[], expand=True)

    def make_loading_overlay(ref: ft.Ref[ft.Container]) -> ft.Container:
        return ft.Container(
            ref=ref,
            content=ft.Container(
                content=ft.Column([
                    ft.ProgressRing(
                        color=ft.Colors.PRIMARY,
                        stroke_width=3,
                    ),
                    ft.Text(
                        "Loading logs...",
                        size=13,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                        weight=ft.FontWeight.W_500,
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                padding=24,
                border_radius=16,
                # Glassmorphic effect for premium loading state
                bgcolor=ft.Colors.with_opacity(GLASS_MODERATE["bg_opacity"], ft.Colors.SURFACE),
                border=ft.border.all(1, ft.Colors.with_opacity(GLASS_MODERATE["border_opacity"], ft.Colors.OUTLINE)),
                shadow=MODERATE_NEUMORPHIC_SHADOWS,
            ),
            bgcolor=ft.Colors.with_opacity(0.3, ft.Colors.SURFACE),  # Backdrop (use SURFACE instead of SURFACE_VARIANT)
            alignment=ft.alignment.center,
            visible=False,
            padding=20,
        )

    # System tab content
    system_stack = ft.Stack([
        make_listview(system_list_ref),
        make_loading_overlay(system_loading_ref),
    ], expand=True)

    # Flet tab content
    flet_stack = ft.Stack([
        make_listview(flet_list_ref),
        make_loading_overlay(flet_loading_ref),
    ], expand=True)

    # Filter chip tracking
    _chip_refs: dict[str, ft.Chip] = {}

    def _style_chip(name: str):
        ch = _chip_refs.get(name)
        if not ch:
            return
        st = level_styles(name)
        sel = bool(ch.selected)
        ch.bgcolor = ft.Colors.with_opacity(0.16 if sel else 0.06, st["accent"])
        # Update leading icon color
        # Update icon color if chip has an Icon leading
        with contextlib.suppress(Exception):
            if getattr(ch, "leading", None) is not None:
                ch.leading.color = st["accent"]

    def _build_filter_chip(name: str) -> ft.Chip:
        st = level_styles(name)
        chip = ft.Chip(
            label=ft.Text(st["label"], size=12, weight=ft.FontWeight.W_600),
            selected=(name in selected_levels),
            on_select=lambda e, n=name: _on_toggle_level(n, e.control.selected),
            leading=ft.Icon(st["icon"], size=14, color=st["accent"]),
            # Enhanced styling (Chip doesn't support shadow in Flet 0.28.3)
            bgcolor=ft.Colors.with_opacity(0.16 if name in selected_levels else 0.06, st["accent"]),
        )
        _chip_refs[name] = chip
        return chip

    def _on_toggle_level(name: str, selected: bool):
        nonlocal selected_levels
        if selected:
            selected_levels.add(name)
        else:
            selected_levels.discard(name)
        # update chip visuals with animation
        ch = _chip_refs.get(name)
        if ch:
            ch.selected = selected
            st = level_styles(name)
            # Update background color when selected (Chip doesn't support shadow in Flet 0.28.3)
            ch.bgcolor = ft.Colors.with_opacity(0.16 if selected else 0.06, st["accent"])
            _style_chip(name)
            ch.update()
        _refresh_lists_by_filter()

    def _passes_filter(log: dict) -> bool:
        """Check if log passes level filter."""
        return bool(
            not selected_levels
            or map_level(log.get("level")) in selected_levels
        )

    def _passes_search(log: dict) -> bool:
        """Check if log matches search query."""
        if not search_query.strip():
            return True
        query_lower = search_query.lower()
        # Search in message, component, and level
        return (
            query_lower in str(log.get("message", "")).lower()
            or query_lower in str(log.get("component", "")).lower()
            or query_lower in str(log.get("level", "")).lower()
        )

    def _render_list(lst_ref: ft.Ref[ft.ListView], data: list[dict], show_stats: bool = False):
        """Render log list with optional statistics card and entrance animations."""
        if lst_ref.current:
            # Filter data
            filtered_data = [row for row in data if _passes_filter(row) and _passes_search(row)]

            if not filtered_data:
                # Enhanced empty state with neumorphic styling
                empty_message = "No logs match your search" if search_query.strip() else "No logs to display"
                empty_sub = "Try adjusting your filters or search" if search_query.strip() else "Logs will appear here when available"

                lst_ref.current.controls = [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(
                                ft.Icons.SEARCH_OFF if search_query.strip() else ft.Icons.INBOX,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                size=48,
                                opacity=0.6,
                            ),
                            ft.Text(
                                empty_message,
                                size=16,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                            ft.Text(
                                empty_sub,
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                opacity=0.7,
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                        padding=40,
                        border_radius=16,
                        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.SURFACE),
                        border=ft.border.all(1, ft.Colors.with_opacity(0.06, ft.Colors.OUTLINE)),
                        shadow=SUBTLE_NEUMORPHIC_SHADOWS,
                        alignment=ft.alignment.center,
                    )
                ]
            else:
                # Build cards with entrance animation for first 15 cards
                cards = []
                for idx, row in enumerate(filtered_data):
                    apply_animation = idx < 15  # Only animate first 15 cards for performance
                    cards.append(build_log_card(row, index=idx, apply_entrance_animation=apply_animation))

                # Add statistics card at top if requested
                if show_stats and data:
                    stats_card = _build_statistics_card(data)  # Use full data for stats, not filtered
                    lst_ref.current.controls = [stats_card, ft.Container(height=8)] + cards
                else:
                    lst_ref.current.controls = cards

            lst_ref.current.spacing = current_density["spacing"]
            lst_ref.current.update()

    def _refresh_lists_by_filter():
        """Refresh both lists with current filters and search."""
        _render_list(system_list_ref, system_logs_data, show_stats=True)
        _render_list(flet_list_ref, flet_logs_data, show_stats=True)

    # Custom flat tab bar (to avoid any internal background from Flet Tabs)
    active_tab_index = 0

    def _tab_button(label: str, icon: str, idx: int, current: int) -> ft.Container:
        is_active = idx == current

        # Create button with enhanced styling
        button = ft.TextButton(
            content=ft.Row([
                ft.Icon(
                    icon,
                    size=16,
                    color=ft.Colors.PRIMARY if is_active else ft.Colors.ON_SURFACE_VARIANT
                ),
                ft.Text(
                    label,
                    size=14,
                    weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.NORMAL,
                    color=ft.Colors.PRIMARY if is_active else ft.Colors.ON_SURFACE_VARIANT
                ),
            ], spacing=6),
            style=ft.ButtonStyle(
                overlay_color=ft.Colors.with_opacity(0.04, ft.Colors.PRIMARY),
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=ft.Colors.with_opacity(0.08, ft.Colors.PRIMARY) if is_active else ft.Colors.TRANSPARENT,
            ),
            on_click=lambda e, i=idx: _on_tab_click(i),
        )

        # Wrap in container for shadow effect
        return ft.Container(
            content=button,
            shadow=SUBTLE_NEUMORPHIC_SHADOWS[:1] if is_active else None,
            border_radius=10,
            animate=200,  # Animation duration in milliseconds
        )

    tabbar_row_ref: ft.Ref[ft.Row] = ft.Ref()
    content_host_ref: ft.Ref[ft.Container] = ft.Ref()

    def _render_tabbar():
        if not tabbar_row_ref.current:
            return
        tabbar_row_ref.current.controls = [
            _tab_button("System Logs", ft.Icons.ARTICLE, 0, active_tab_index),
            _tab_button("Flet Logs", ft.Icons.CODE, 1, active_tab_index),
        ]
        tabbar_row_ref.current.update()

    def _render_active_content():
        if not content_host_ref.current:
            return
        content_host_ref.current.content = (system_stack if active_tab_index == 0 else flet_stack)
        content_host_ref.current.update()

    def _on_tab_click(i: int):
        nonlocal active_tab_index
        if i == active_tab_index:
            return
        active_tab_index = i
        _render_tabbar()
        _render_active_content()

    # ---------------------------------------------
    # Search and Density Handlers
    # ---------------------------------------------
    def on_search_change(e):
        """Handle search query changes."""
        nonlocal search_query
        search_query = e.control.value if e.control.value else ""
        _refresh_lists_by_filter()

    def on_search_clear(e):
        """Clear search query."""
        nonlocal search_query
        search_query = ""
        if search_field_ref.current:
            search_field_ref.current.value = ""
            search_field_ref.current.update()
        _refresh_lists_by_filter()

    def on_density_change(e):
        """Handle density mode changes."""
        nonlocal current_density_mode, current_density
        # SegmentedButton.selected is a SET of selected segment values
        selected_set = e.control.selected
        if selected_set and len(selected_set) > 0:
            # Get the first (and only, since allow_multiple_selection=False by default) value
            selected_value = next(iter(selected_set))
            if selected_value in density_presets:
                current_density_mode = selected_value
                current_density = density_presets[current_density_mode]
                _refresh_lists_by_filter()

    # ---------------------------------------------
    # Actions
    # ---------------------------------------------
    _system_first_load = True

    async def refresh_system_logs(show_toast: bool = False, show_spinner: bool = False):
        nonlocal _system_first_load
        if system_loading_ref.current and (show_spinner or _system_first_load):
            system_loading_ref.current.visible = True
            system_loading_ref.current.update()
        logs = get_system_logs(server_bridge)
        # Normalize records
        safe_logs: list[dict] = []
        for it in logs:
            if isinstance(it, dict):
                safe_logs.append({
                    "time": it.get("time") or it.get("timestamp") or "",
                    "level": it.get("level") or it.get("severity") or "INFO",
                    "component": it.get("component") or it.get("module") or "",
                    "message": it.get("message") or it.get("msg") or "",
                })
            else:
                safe_logs.append({"time": "", "level": "INFO", "component": "", "message": str(it)})
        nonlocal system_logs_data
        system_logs_data = safe_logs
        _render_list(system_list_ref, system_logs_data, show_stats=True)
        if system_loading_ref.current and (show_spinner or _system_first_load):
            system_loading_ref.current.visible = False
            system_loading_ref.current.update()
        _system_first_load = False
        if show_toast:
            _toast(page, "System logs refreshed")

    def get_flet_logs_snapshot() -> list[dict]:
        if _flet_log_capture and _flet_log_capture.logs:
            return _flet_log_capture.logs.copy()
        return []

    _flet_first_load = True

    async def refresh_flet_logs(show_toast: bool = False, show_spinner: bool = False):
        nonlocal _flet_first_load
        if flet_loading_ref.current and (show_spinner or _flet_first_load):
            flet_loading_ref.current.visible = True
            flet_loading_ref.current.update()
        nonlocal flet_logs_data
        flet_logs_data = get_flet_logs_snapshot()
        _render_list(flet_list_ref, flet_logs_data, show_stats=True)
        if flet_loading_ref.current and (show_spinner or _flet_first_load):
            flet_loading_ref.current.visible = False
            flet_loading_ref.current.update()
        _flet_first_load = False
        if show_toast:
            _toast(page, "Flet logs refreshed")

    def on_refresh_click(_: ft.ControlEvent):
        # decide which tab
        idx = active_tab_index or 0
        if idx == 0:
            page.run_task(refresh_system_logs(True, show_spinner=True))
        else:
            page.run_task(refresh_flet_logs(True, show_spinner=True))

    def on_export_click(_: ft.ControlEvent):
        try:
            export_dir = os.path.join(_repo_root, "logs_exports")
            os.makedirs(export_dir, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            payload = {
                "exported_at": ts,
                "system": system_logs_data,
                "flet": flet_logs_data or get_flet_logs_snapshot(),
            }
            path = os.path.join(export_dir, f"logs_{ts}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            _toast(page, f"Exported to {path}")
        except Exception as e:
            _toast(page, f"Export failed: {e}", error=True)

    def on_clear_flet_click(_: ft.ControlEvent):
        try:
            _flet_log_capture.logs.clear()
            # refresh list
            page.run_task(refresh_flet_logs(False))
            _toast(page, "Cleared Flet logs")
        except Exception as e:
            _toast(page, f"Clear failed: {e}", error=True)

    # Auto-refresh switch
    auto_refresh_switch = ft.Switch(label="Auto-refresh", value=True)

    # Search bar with clear button
    search_bar = ft.Row([
        ft.TextField(
            ref=search_field_ref,
            hint_text="Search logs...",
            prefix_icon=ft.Icons.SEARCH,
            on_change=on_search_change,
            expand=True,
            border_radius=12,
            text_size=13,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=8),
            border_color=ft.Colors.OUTLINE,
            focused_border_color=ft.Colors.PRIMARY,
        ),
        ft.IconButton(
            icon=ft.Icons.CLEAR,
            tooltip="Clear search",
            on_click=on_search_clear,
            icon_size=20,
        ),
    ], spacing=8, expand=True)

    # Density controls
    density_selector = ft.SegmentedButton(
        selected={"normal"},  # Default to "normal" segment (selected is a SET of segment values)
        on_change=on_density_change,
        segments=[
            ft.Segment(
                value="compact",
                label=ft.Text("Compact", size=12),
                icon=ft.Icon(ft.Icons.DENSITY_SMALL, size=16),
            ),
            ft.Segment(
                value="normal",
                label=ft.Text("Normal", size=12),
                icon=ft.Icon(ft.Icons.DENSITY_MEDIUM, size=16),
            ),
            ft.Segment(
                value="comfortable",
                label=ft.Text("Comfortable", size=12),
                icon=ft.Icon(ft.Icons.DENSITY_LARGE, size=16),
            ),
        ],
        show_selected_icon=False,
    )

    # Filter row
    filter_row = ft.Row([
        _build_filter_chip("INFO"),
        _build_filter_chip("SUCCESS"),
        _build_filter_chip("WARNING"),
        _build_filter_chip("IMPORTANT"),
        _build_filter_chip("ERROR"),
        _build_filter_chip("CRITICAL"),
        _build_filter_chip("SPECIAL"),
    ], scroll="auto", spacing=8)

    # Tab bar + content host
    tabbar = ft.Row(ref=tabbar_row_ref, spacing=16)

    # Content host container (AnimatedSwitcher doesn't support dynamic content updates in Flet 0.28.3)
    content_host = ft.Container(
        ref=content_host_ref,
        content=system_stack,  # Default to system logs
        expand=True,
    )

    # Action buttons with enhanced neumorphic styling
    action_buttons = ft.Row([
        ft.FilledTonalButton(
            "Refresh",
            icon=ft.Icons.REFRESH,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
            ),
            on_click=on_refresh_click,
        ),
        ft.OutlinedButton(
            "Export",
            icon=ft.Icons.DOWNLOAD,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
            ),
            on_click=on_export_click,
        ),
        ft.OutlinedButton(
            "Clear Flet Logs",
            icon=ft.Icons.DELETE_SWEEP,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
            ),
            on_click=on_clear_flet_click,
        ),
    ], spacing=10)

    # Header with glassmorphic background and elevated appearance
    header = ft.Container(
        content=ft.Column([
            # Title row
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.ARTICLE, size=36, color=ft.Colors.PRIMARY),
                    ft.Text("Logs", size=28, weight=ft.FontWeight.BOLD),
                ], spacing=12),
                ft.Row([auto_refresh_switch, action_buttons], spacing=12),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=12),
            # Search and density controls row
            ft.Row([
                ft.Container(content=search_bar, expand=2),
                ft.Container(width=16),
                ft.Container(content=density_selector),
            ], spacing=0, alignment=ft.MainAxisAlignment.START),
        ], spacing=0),
        padding=16,
        border_radius=16,
        bgcolor=ft.Colors.with_opacity(GLASS_SUBTLE["bg_opacity"], ft.Colors.SURFACE),
        border=ft.border.all(1, ft.Colors.with_opacity(GLASS_SUBTLE["border_opacity"], ft.Colors.OUTLINE)),
        shadow=SUBTLE_NEUMORPHIC_SHADOWS,
    )

    content = ft.Column([
        header,
        ft.Container(filter_row, padding=ft.padding.only(bottom=8)),
        tabbar,
        content_host,
    ], spacing=18, expand=True)

    main_container = ft.Container(content=content, padding=24, expand=True)

    # ---------------------------------------------
    # Toast helper
    # ---------------------------------------------
    def _toast(pg: ft.Page, message: str, *, error: bool = False):
        try:
            pg.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=(ft.Colors.ERROR_CONTAINER if error else ft.Colors.SURFACE_CONTAINER_HIGHEST),
                show_close_icon=True,
                duration=2500,
            )
            pg.snack_bar.open = True
            pg.update()
        except Exception:
            # snack_bar can fail if page not ready; ignore
            with contextlib.suppress(Exception):
                ...

    # ---------------------------------------------
    # Lifecycle
    # ---------------------------------------------
    _live_task: asyncio.Task | None = None

    def dispose():
        nonlocal _live_task
        if _live_task and not _live_task.done():
            _live_task.cancel()
        _live_task = None

    async def _live_flet_refresh_loop():
        try:
            while True:
                # respect auto-refresh switch
                if auto_refresh_switch.value:
                    if active_tab_index == 0:
                        await refresh_system_logs(False, show_spinner=False)
                    else:
                        await refresh_flet_logs(False, show_spinner=False)
                await asyncio.sleep(1.5)
        except asyncio.CancelledError:
            return
        except Exception:
            # Don't crash the app on background errors
            return

    async def setup_subscriptions():
        nonlocal _live_task
        # Initial loads after attachment
        _render_tabbar()
        _render_active_content()
        await refresh_system_logs(False, show_spinner=True)
        await refresh_flet_logs(False, show_spinner=True)
        # Start background polling for flet logs
        try:
            _live_task = asyncio.create_task(_live_flet_refresh_loop())
        except Exception:
            _live_task = None

    return main_container, dispose, setup_subscriptions
