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
import re
import csv
from typing import Any, Callable, Optional
try:
    import websockets
except ImportError:
    websockets = None

import flet as ft

# Path setup
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import Shared.utils.utf8_solution as _  # noqa: F401

# Import modularized components
from FletV2.utils.ui.neomorphism import NeomorphicShadows
from FletV2.utils.logging.color_system import LogColorSystem
from FletV2.components.log_card import LogCard  # Moved from inside function

# Define batch size for pagination
BATCH_SIZE = 50  # Process logs in batches of 50

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
# FLET LOG CAPTURE SYSTEM
# Uses singleton from Shared module - initialized early in application lifecycle
# --------------------------------------------------------------------------------------

# Import singleton log capture (initialized in start_with_server.py)
try:
    from Shared.logging.flet_log_capture import get_flet_log_capture
    _flet_log_capture = get_flet_log_capture()
except ImportError:
    # Fallback if Shared module not available (shouldn't happen in production)
    print("[WARNING] Could not import FletLogCapture singleton - Flet logs may not display")
    _flet_log_capture = None

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
            data = result.get('data', {})
            # Server returns {'logs': [...], 'note': '...'}, extract the logs list
            if isinstance(data, dict):
                raw_logs = data.get('logs', [])
                # Convert raw log strings to dict format
                parsed_logs = []
                for line in raw_logs:
                    if isinstance(line, str):
                        # Parse log line format: "TIMESTAMP - LEVEL - MESSAGE"
                        # Example: "2025-10-10 20:18:34,099 - INFO - Server started"
                        parts = line.split(' - ', 2)
                        if len(parts) >= 3:
                            parsed_logs.append({
                                'time': parts[0].strip(),
                                'level': parts[1].strip(),
                                'message': parts[2].strip(),
                                'component': 'Server',
                            })
                        else:
                            # Fallback for unparseable lines
                            parsed_logs.append({
                                'time': '',
                                'level': 'INFO',
                                'message': line,
                                'component': 'Server',
                            })
                    elif isinstance(line, dict):
                        # Already in dict format
                        parsed_logs.append(line)
                return parsed_logs
            return []
        return []
    except Exception as e:
        print(f"[ERROR] get_system_logs failed: {e}")
        import traceback
        traceback.print_exc()
        return []

# Define the highlight_text function for search text highlighting
def highlight_text(text: str, search_query: str) -> ft.Control:
    """
    Creates a text control with highlighted search terms.
    If search_query is provided, matches are highlighted with a background color.
    """
    if not search_query:
        return ft.Text(text, selectable=True)

    # Case insensitive search
    search_lower = search_query.lower()
    text_lower = text.lower()

    # Find all occurrences of the search query
    parts = []
    start = 0
    pos = text_lower.find(search_lower)

    while pos != -1:
        # Add text before match
        if pos > start:
            parts.append(ft.TextSpan(text[start:pos]))

        # Add highlighted match
        parts.append(ft.TextSpan(
            text=text[pos:pos+len(search_query)],
            style=ft.TextStyle(
                bgcolor=ft.Colors.YELLOW_300,
                color=ft.Colors.BLACK
            )
        ))

        start = pos + len(search_query)
        pos = text_lower.find(search_lower, start)

    # Add remaining text
    if start < len(text):
        parts.append(ft.TextSpan(text[start:]))

    # If no matches found, return regular text
    if not parts:
        return ft.Text(text, selectable=True, size=12)

    return ft.Text(
        spans=parts,
        selectable=True,
        size=12,
    )

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
    # STRUCTURED STATE MANAGEMENT
    # ---------------------------------------------
    from dataclasses import dataclass, field

    @dataclass
    class LogsViewState:
        selected_levels: set[str] = field(default_factory=set)
        search_query: str = ""
        is_compact_mode: bool = False
        is_auto_scroll_locked: bool = True
        system_logs_data: list[dict] = field(default_factory=list)
        flet_logs_data: list[dict] = field(default_factory=list)
        current_system_batch: int = 0
        current_flet_batch: int = 0
        system_log_controls: list[ft.Control] = field(default_factory=list)
        flet_log_controls: list[ft.Control] = field(default_factory=list)

    # Initialize state
    view_state = LogsViewState()

    # WebSocket connection for live logs
    websocket_connection = None
    is_live_mode = False

    # ---------------------------------------------
    # Toast Notifications
    # ---------------------------------------------

    def _show_toast(pg: ft.Page, message: str, toast_type: str = "info"):
        """Show toast notification with appropriate styling"""
        with contextlib.suppress(Exception):
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

        # Determine if compact mode is active
        is_compact = compact_mode_switch.value
        # Update state
        view_state.is_compact_mode = is_compact

        return LogCard(
            log=log,
            index=index,
            is_compact=is_compact,
            search_query=view_state.search_query,
            on_click=lambda _: show_log_details(log),
            page=page,  # Pass page reference for theme-aware shadows
        )

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
            "App Logs": ft.Icons.APPS_ROUNDED,  # Changed from "Flet Logs"
            "Application Logs": ft.Icons.APPS_ROUNDED,  # Also support full name
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

    # Create list views
    def make_listview(ref: ft.Ref[ft.ListView]) -> ft.ListView:
        return ft.ListView(
            ref=ref,
            spacing=12,  # Increased spacing for neomorphic effect
            padding=ft.padding.all(4),
            auto_scroll=False,
            controls=[],
            expand=True,
            on_scroll=lambda e: on_list_scroll(e),
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
            selected=(level_name in view_state.selected_levels),  # Use view state instead of undefined variable
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
        if is_selected:
            view_state.selected_levels.add(level_name)
        else:
            view_state.selected_levels.discard(level_name)

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

    # Debounce timer for search
    search_debounce_timer = None

    def on_search_change(e: ft.ControlEvent):
        """Handle search query changes with debounce"""
        nonlocal search_debounce_timer

        # Cancel previous timer
        if search_debounce_timer and not search_debounce_timer.done():
            search_debounce_timer.cancel()

        # Update search query
        view_state.search_query = e.data or ""

        # Set new timer - use page.run_task instead of asyncio.create_task
        async def delayed_refresh():
            await asyncio.sleep(0.3)  # 300ms delay
            _refresh_lists_by_filter()

        search_debounce_timer = page.run_task(delayed_refresh)

    # ---------------------------------------------
    # LOG DETAILS DIALOG
    # ---------------------------------------------

    def show_log_details(log_data: dict):
        """Show detailed log information in a modal dialog"""
        # Create the content for the dialog
        full_message = log_data.get("message", "") or "(empty message)"

        # Format the raw log data as JSON
        try:
            formatted_json = json.dumps(log_data, indent=2, ensure_ascii=False)
        except Exception:
            formatted_json = str(log_data)

        # Create message container with full text
        message_container = ft.Container(
            content=ft.Column([
                ft.Text("Full Log Message", weight=ft.FontWeight.BOLD, size=16),
                ft.Divider(),
                ft.Text(
                    full_message,
                    selectable=True,
                    size=14,
                    expand=True,
                ),
            ], scroll=ft.ScrollMode.AUTO),
            padding=10,
            height=150,
        )

        # Create JSON container with raw data
        json_container = ft.Container(
            content=ft.Column([
                ft.Text("Raw Log Data (JSON)", weight=ft.FontWeight.BOLD, size=16),
                ft.Divider(),
                ft.Text(
                    formatted_json,
                    selectable=True,
                    size=12,
                    expand=True,
                ),
            ], scroll=ft.ScrollMode.AUTO),
            padding=10,
            height=200,
        )

        # Create copy button
        def copy_message_to_clipboard(e):
            page.set_clipboard(full_message)
            _show_toast(page, "Log message copied to clipboard", "success")

        copy_button = ft.TextButton(
            "Copy Full Message",
            icon=ft.Icons.COPY_ROUNDED,
            on_click=copy_message_to_clipboard
        )

        # Create the dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Log Entry Details"),
            content=ft.Column([
                message_container,
                json_container,
                copy_button
            ], spacing=10, height=450, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Close", on_click=lambda _: close_dialog(dialog))
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            modal=True,
        )

        # Function to close the dialog
        def close_dialog(dlg):
            try:
                dlg.open = False
                page.update()
                page.dialog = None
            except Exception as e:
                print(f"[ERROR] Failed to close dialog: {e}")

        # Open the dialog
        try:
            page.dialog = dialog
            dialog.open = True  # CRITICAL: Must set open=True to display dialog!
            page.update()
        except Exception as e:
            print(f"[ERROR] Failed to open dialog: {e}")
            _show_toast(page, f"Error opening dialog: {e}", "error")

    def on_list_scroll(e: ft.ScrollEvent):
        """Handle scroll events to disable auto-scroll when user scrolls up"""
        # Disable auto-scroll when user scrolls manually
        if auto_scroll_switch.value:
            auto_scroll_switch.value = False
            # Update the switch visual state
            with contextlib.suppress(Exception):
                auto_scroll_switch.update()

    # Time range for filtering (if needed)
    start_time_filter = None  # Would come from UI controls
    end_time_filter = None    # Would come from UI controls
    selected_component_filter = "All"  # Component filter

    def _passes_filter(log: dict) -> bool:
        """Check if log passes current filter"""
        # Check level filter
        if view_state.selected_levels and map_level(log.get("level")) not in view_state.selected_levels:
            return False

        # Check component filter
        if selected_component_filter != "All":
            log_component = log.get("component", "").lower()
            if log_component and selected_component_filter.lower() not in log_component:
                return False

        # Check search query (with optional regex support)
        if view_state.search_query:
            is_regex_search = view_state.search_query.startswith('/') and view_state.search_query.endswith('/')
            search_text = view_state.search_query[1:-1] if is_regex_search else view_state.search_query
            message = log.get("message", "")
            component = log.get("component", "")
            time_str = log.get("time", "")

            found_match = False

            if is_regex_search:
                # Try to use regex to match
                try:
                    import re
                    pattern = re.compile(search_text, re.IGNORECASE)
                    if (pattern.search(message) or
                        pattern.search(component) or
                        pattern.search(time_str)):
                        found_match = True
                except re.error:
                    # If regex is invalid, fall back to simple text matching
                    search_lower = search_text.lower()
                    message_lower = message.lower()
                    component_lower = component.lower()
                    time_lower = time_str.lower()
                    if (search_lower in message_lower or
                        search_lower in component_lower or
                        search_lower in time_lower):
                        found_match = True
            else:
                # Simple text search
                search_lower = search_text.lower()
                message_lower = message.lower()
                component_lower = component.lower()
                time_lower = time_str.lower()
                if (search_lower in message_lower or
                    search_lower in component_lower or
                    search_lower in time_lower):
                    found_match = True

            if not found_match:
                return False

        # Check time range filter (simplified implementation)
        if start_time_filter or end_time_filter:
            log_time_str = log.get("time", "")
            if log_time_str:
                # Parse time string - expecting format like "HH:MM:SS.mmm"
                with contextlib.suppress(Exception):
                    # For now, just check if the time is within our range
                    # This is a simplified check - a full implementation would parse time properly
                    if start_time_filter and log_time_str < start_time_filter:
                        return False
                    if end_time_filter and log_time_str > end_time_filter:
                        return False

        return True

    def _render_list(lst_ref: ft.Ref[ft.ListView], data: list[dict], tab_name: str, is_system: bool = True):
        """Render log list with filtering and pagination"""
        # Reduced debug output - only log when ref is None
        if not lst_ref.current:
            print(f"[DEBUG] _render_list: lst_ref.current is None for {tab_name}")
            return

        # Note: Removed page attachment check - Flet handles this automatically
        # The control might temporarily not have .page during transitions but updates still work

        # Check current scroll offset to determine if user has scrolled up
        try:
            # We need to check if the list view has scrolled up
            # Note: This might be different depending on Flet's implementation
            # We'll determine scroll state based on user preference and auto-scroll setting
            should_scroll_to_bottom = auto_scroll_switch.value
        except Exception:
            should_scroll_to_bottom = True

        if not data:
            # Show empty state (debug removed - normal behavior)
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
                        ], horizontal_alignment=ft.alignment.center, spacing=0),
                        padding=60,
                        alignment=ft.alignment.center,
                    )
                ]
            else:
                # Determine which batch to show based on the tab
                current_batch = view_state.current_system_batch if is_system else view_state.current_flet_batch
                start_idx = current_batch * BATCH_SIZE
                end_idx = start_idx + BATCH_SIZE

                # Get the batch of logs to render
                batch_data = filtered_data[start_idx:end_idx]

                # Create log cards for the current batch
                log_cards = [build_log_card(row, idx) for idx, row in enumerate(batch_data)]

                # Add "Load More" button if there are more logs
                if end_idx < len(filtered_data):
                    load_more_button = ft.Container(
                        content=ft.ElevatedButton(
                            "Load More",
                            icon=ft.Icons.ADD_ROUNDED,
                            on_click=lambda _: load_more_logs(is_system_tab=is_system),
                            style=ft.ButtonStyle(
                                padding=ft.padding.symmetric(horizontal=24, vertical=12),
                                shape=ft.RoundedRectangleBorder(radius=24),
                            )
                        ),
                        padding=ft.padding.symmetric(vertical=10),
                        alignment=ft.alignment.center,
                    )

                    lst_ref.current.controls = log_cards + [load_more_button]
                else:
                    lst_ref.current.controls = log_cards

        # Safe update - control might not be attached to page during setup
        try:
            lst_ref.current.update()
        except AssertionError as e:
            if "must be added to the page first" not in str(e):
                raise

        # Auto-scroll to bottom if enabled
        if should_scroll_to_bottom:
            with contextlib.suppress(Exception):
                lst_ref.current.scroll_to(offset=-1, duration=300)

        # Update statistics panel
        update_statistics()

        # Check for critical logs and show alerts if needed
        check_for_critical_logs(data)

    def load_more_logs(is_system_tab: bool):
        """Load the next batch of logs"""
        if is_system_tab:
            view_state.current_system_batch += 1
            # Re-render with the new batch
            _render_list(system_list_ref, view_state.system_logs_data, "System Logs", is_system=True)
        else:
            view_state.current_flet_batch += 1
            # Re-render with the new batch
            _render_list(flet_list_ref, view_state.flet_logs_data, "Flet Logs", is_system=False)

    def _refresh_lists_by_filter():
        """Refresh both lists with current filter settings"""
        # Reset batch counters when refreshing
        view_state.current_system_batch = 0
        view_state.current_flet_batch = 0
        _render_list(system_list_ref, view_state.system_logs_data, "System Logs", is_system=True)
        _render_list(flet_list_ref, view_state.flet_logs_data, "Flet Logs", is_system=False)

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
            _create_tab_button("App Logs", ft.Icons.APPS_ROUNDED, 1, active_tab_index == 1),  # Changed from "Flet Logs"
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

        # Reset batch counter for the previous tab
        if active_tab_index == 0:  # Was on System logs tab
            view_state.current_system_batch = 0
        else:  # Was on Flet logs tab
            view_state.current_flet_batch = 0

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

        if (system_loading_ref.current and (show_spinner or _system_first_load) and
            hasattr(system_loading_ref.current, 'page') and system_loading_ref.current.page):
            system_loading_ref.current.visible = True
            system_loading_ref.current.update()

        # Fetch logs
        logs = get_system_logs(server_bridge)
        # Reduced spam: Only log on first load
        if _system_first_load:
            print(f"[DEBUG] refresh_system_logs: Fetched {len(logs)} logs from server")

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

        # Reduced spam: Only log normalization count on first load
        if _system_first_load:
            print(f"[DEBUG] refresh_system_logs: Normalized to {len(safe_logs)} safe logs")
        view_state.system_logs_data = safe_logs
        _render_list(system_list_ref, view_state.system_logs_data, "System Logs")

        # Update statistics panel
        update_statistics()

        if (system_loading_ref.current and (show_spinner or _system_first_load) and
            hasattr(system_loading_ref.current, 'page') and system_loading_ref.current.page):
            system_loading_ref.current.visible = False
            system_loading_ref.current.update()

        _system_first_load = False

        if show_toast:
            _show_toast(page, "System logs refreshed", "success")

    async def refresh_flet_logs(show_toast: bool = False, show_spinner: bool = False):
        """Refresh Flet logs from singleton capture handler - shows APPLICATION logs"""
        nonlocal _flet_first_load

        if (flet_loading_ref.current and (show_spinner or _flet_first_load) and
            hasattr(flet_loading_ref.current, 'page') and flet_loading_ref.current.page):
            flet_loading_ref.current.visible = True
            flet_loading_ref.current.update()

        # Get APPLICATION logs from singleton capture (changed from get_flet_logs to get_app_logs)
        if _flet_log_capture:
            view_state.flet_logs_data = _flet_log_capture.get_app_logs()  # CHANGED: Show app logs instead
        else:
            view_state.flet_logs_data = []

        # Reduced spam: Only log on first load
        if _flet_first_load:
            if _flet_log_capture:
                stats = _flet_log_capture.get_stats()
                print(f"[DEBUG] refresh_flet_logs: Fetched {len(view_state.flet_logs_data)} Application logs (GUI)")
                print(f"[DEBUG] Capture stats: {stats}")
            else:
                print("[DEBUG] refresh_flet_logs: FletLogCapture singleton not available")

        _render_list(flet_list_ref, view_state.flet_logs_data, "Application Logs")  # CHANGED: Updated tab name

        # Update statistics panel
        update_statistics()

        if (flet_loading_ref.current and (show_spinner or _flet_first_load) and
            hasattr(flet_loading_ref.current, 'page') and flet_loading_ref.current.page):
            flet_loading_ref.current.visible = False
            flet_loading_ref.current.update()

        _flet_first_load = False

        if show_toast:
            _show_toast(page, "Application logs refreshed", "success")

    def on_refresh_click(_: ft.ControlEvent):
        """Handle refresh button click"""
        # Create async wrapper functions for page.run_task
        async def refresh_system_task():
            await refresh_system_logs(show_toast=True, show_spinner=True)

        async def refresh_flet_task():
            await refresh_flet_logs(show_toast=True, show_spinner=True)

        if active_tab_index == 0:
            page.run_task(refresh_system_task)
        else:
            page.run_task(refresh_flet_task)

    def on_export_click(_: ft.ControlEvent):
        """Show export options dialog"""
        # Create dropdown for export format
        format_dropdown = ft.Dropdown(
            label="Export Format",
            width=200,
            options=[
                ft.dropdown.Option("json", "JSON"),
                ft.dropdown.Option("csv", "CSV"),
                ft.dropdown.Option("txt", "Plain Text"),
            ],
            value="json"  # Default to JSON
        )

        # Create checkbox for filtered vs all logs
        filtered_only_checkbox = ft.Checkbox(label="Export only currently filtered logs", value=True)

        def perform_export(e):
            """Perform the actual export based on selected options"""
            try:
                export_dir = os.path.join(_repo_root, "logs_exports")
                os.makedirs(export_dir, exist_ok=True)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_format = format_dropdown.value
                filtered_only = filtered_only_checkbox.value

                # Determine which logs to export
                if active_tab_index == 0:  # System logs
                    export_logs = [log for log in view_state.system_logs_data if _passes_filter(log)] if filtered_only else view_state.system_logs_data
                else:  # Flet logs
                    export_logs = [log for log in view_state.flet_logs_data if _passes_filter(log)] if filtered_only else view_state.flet_logs_data

                if export_format == "json":
                    # Export as JSON
                    payload = {
                        "exported_at": timestamp,
                        "export_datetime": datetime.now().isoformat(),
                        "filtered_only": filtered_only,
                        "active_tab": "System Logs" if active_tab_index == 0 else "Flet Logs",
                        "logs": export_logs,
                    }

                    filepath = os.path.join(export_dir, f"logs_{timestamp}.json")

                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(payload, f, indent=2, ensure_ascii=False)

                elif export_format == "csv":
                    # Export as CSV
                    import csv
                    filepath = os.path.join(export_dir, f"logs_{timestamp}.csv")

                    with open(filepath, "w", newline='', encoding="utf-8") as csvfile:
                        fieldnames = ["time", "level", "component", "message"]
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                        writer.writeheader()
                        for log in export_logs:
                            writer.writerow({
                                "time": log.get("time", ""),
                                "level": log.get("level", ""),
                                "component": log.get("component", ""),
                                "message": log.get("message", ""),
                            })

                elif export_format == "txt":
                    # Export as plain text
                    filepath = os.path.join(export_dir, f"logs_{timestamp}.txt")

                    with open(filepath, "w", encoding="utf-8") as txtfile:
                        txtfile.write(f"Log Export - {datetime.now().isoformat()}\n")
                        txtfile.write(f"Filtered Only: {filtered_only}\n")
                        txtfile.write(f"Active Tab: {'System Logs' if active_tab_index == 0 else 'Flet Logs'}\n")
                        txtfile.write("="*50 + "\n\n")

                        for log in export_logs:
                            txtfile.write(f"[{log.get('time', '')}] [{log.get('level', '')}] ")
                            txtfile.write(f"[{log.get('component', '')}] {log.get('message', '')}\n")

                _show_toast(page, f"Exported to {filepath}", "success")
                # Close dialog
                with contextlib.suppress(Exception):
                    page.dialog = None
                    page.update()
            except Exception as e:
                _show_toast(page, f"Export failed: {str(e)}", "error")

        # Create export button
        export_button = ft.ElevatedButton("Export", on_click=perform_export)

        # Create dialog
        export_dialog = ft.AlertDialog(
            title=ft.Text("Export Logs"),
            content=ft.Column([
                format_dropdown,
                filtered_only_checkbox,
            ], spacing=10, height=150),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: close_export_dialog()),
                export_button,
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        def close_export_dialog():
            with contextlib.suppress(Exception):
                page.dialog = None
                page.update()

        # Show dialog
        with contextlib.suppress(Exception):
            page.dialog = export_dialog
            page.update()

    async def on_clear_flet_click(_: ft.ControlEvent):
        """Clear Flet logs from singleton capture"""
        try:
            if _flet_log_capture:
                _flet_log_capture.clear_flet_logs()
                await refresh_flet_logs(show_toast=False)
                _show_toast(page, "Cleared Flet logs", "success")
            else:
                _show_toast(page, "Log capture not available", "error")
        except Exception as e:
            _show_toast(page, f"Clear failed: {str(e)}", "error")

    def check_for_critical_logs(logs):
        """Check logs for ERROR and CRITICAL messages and show alerts"""
        # Look for ERROR and CRITICAL logs
        critical_logs = []
        for log in logs:
            level = map_level(log.get("level", ""))
            if level in ["ERROR", "CRITICAL"]:
                critical_logs.append(log)

        # If we found critical logs, show an alert
        if critical_logs:
            # Count the number of critical logs
            error_count = len([log for log in critical_logs if map_level(log.get("level", "")) == "ERROR"])
            critical_count = len([log for log in critical_logs if map_level(log.get("level", "")) == "CRITICAL"])

            # Show an appropriate alert
            if critical_count > 0:
                alert_message = f"{critical_count} CRITICAL and {error_count} ERROR logs detected!"
                _show_toast(page, alert_message, "error")
            elif error_count > 0:
                alert_message = f"{error_count} ERROR logs detected!"
                _show_toast(page, alert_message, "error")

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

    # Auto-refresh switch (compact)
    auto_refresh_switch = ft.Switch(
        label="Auto-refresh",
        value=True,
        label_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_400),
    )

    # Auto-scroll to bottom switch (compact)
    auto_scroll_switch = ft.Switch(
        label="Lock to Bottom",
        value=True,
        label_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_400),
    )

    # Compact mode switch
    compact_mode_switch = ft.Switch(
        label="Compact Mode",
        value=False,
        label_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_400),
    )

    # Load saved settings
    def load_saved_settings():
        """Load user preferences from client storage"""
        # Wrap in try/except to handle timeout errors gracefully
        with contextlib.suppress(Exception):
            # Load filters
            saved_filters = page.client_storage.get("logs.filters")
            if saved_filters and isinstance(saved_filters, list):
                view_state.selected_levels = set(saved_filters)
                # Update UI to reflect saved filters
                for level_name, chip in _chip_refs.items():
                    chip.selected = level_name in view_state.selected_levels
                    config = LogColorSystem.get_level_config(level_name)
                    chip.bgcolor = LogColorSystem.get_surface_tint(
                        config["primary"],
                        0.20 if level_name in view_state.selected_levels else 0.08
                    )
                    if chip.leading:
                        chip.leading.color = config["primary"]

            # Load compact mode setting
            saved_compact_mode = page.client_storage.get("logs.compact_mode")
            if saved_compact_mode is not None:
                compact_mode_switch.value = saved_compact_mode

            # Load auto-scroll setting
            saved_auto_scroll = page.client_storage.get("logs.auto_scroll")
            if saved_auto_scroll is not None:
                auto_scroll_switch.value = saved_auto_scroll

    # Function to save settings
    def save_current_settings():
        """Save user preferences to client storage"""
        with contextlib.suppress(Exception):
            # Save filters
            page.client_storage.set("logs.filters", list(view_state.selected_levels))
            # Save compact mode
            page.client_storage.set("logs.compact_mode", compact_mode_switch.value)
            # Save auto-scroll
            page.client_storage.set("logs.auto_scroll", auto_scroll_switch.value)

    # Update settings when they change
    def update_settings(e):
        save_current_settings()

    # Set up change event handlers
    compact_mode_switch.on_change = update_settings
    auto_scroll_switch.on_change = update_settings

    # Create save filter button
    save_filter_button = ft.IconButton(
        icon=ft.Icons.SAVE_OUTLINED,
        tooltip="Save current filters",
        on_click=lambda e: save_current_filter()
    )

    # Live mode toggle switch (compact)
    live_mode_switch = ft.Switch(
        label="Live Mode",
        value=False,
        label_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_400),
    )

    # Component filter dropdown (compact)
    component_options = ft.Dropdown(
        label="Component",
        width=150,
        options=[ft.dropdown.Option("All"), ft.dropdown.Option("Server"), ft.dropdown.Option("Client")],  # Placeholder options
        on_change=lambda e: update_component_filter(e),
    )

    def update_component_filter(e):
        """Update the component filter from UI control"""
        nonlocal selected_component_filter
        selected_component_filter = e.control.value
        # Refresh the logs to apply the new filter
        _refresh_lists_by_filter()

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
    # Header Section - Ultra Compact Single Row
    # ---------------------------------------------

    # Compact search field
    search_field = ft.TextField(
        hint_text="Search...",
        icon=ft.Icons.SEARCH_ROUNDED,
        width=200,
        dense=True,
        on_change=lambda e: on_search_change(e),
    )

    # Ultra-compact switches (icon-only or very small labels)
    auto_refresh_switch = ft.Switch(
        label="Auto",
        value=True,
        label_style=ft.TextStyle(size=10),
    )

    auto_scroll_switch = ft.Switch(
        label="Lock",
        value=True,
        label_style=ft.TextStyle(size=10),
    )

    compact_mode_switch = ft.Switch(
        label="Compact",
        value=False,
        label_style=ft.TextStyle(size=10),
    )

    live_mode_switch = ft.Switch(
        label="Live",
        value=False,
        label_style=ft.TextStyle(size=10),
    )

    # Compact component dropdown
    component_options = ft.Dropdown(
        label="Component",
        width=120,
        dense=True,
        options=[ft.dropdown.Option("All"), ft.dropdown.Option("Server"), ft.dropdown.Option("Client")],
        on_change=lambda e: update_component_filter(e),
    )

    # Icon-only action buttons for maximum compactness
    refresh_btn = ft.IconButton(
        icon=ft.Icons.REFRESH_ROUNDED,
        tooltip="Refresh logs",
        on_click=on_refresh_click,
    )

    export_btn = ft.IconButton(
        icon=ft.Icons.DOWNLOAD_ROUNDED,
        tooltip="Export logs",
        on_click=on_export_click,
    )

    clear_btn = ft.IconButton(
        icon=ft.Icons.DELETE_SWEEP_ROUNDED,
        tooltip="Clear Flet logs",
        on_click=on_clear_flet_click,
    )

    save_filter_button = ft.IconButton(
        icon=ft.Icons.SAVE_OUTLINED,
        tooltip="Save current filters",
        on_click=lambda e: save_current_filter()
    )

    # Single row header - everything in one line
    header_row = ft.Row([
        ft.Text("Logs", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE),
        ft.VerticalDivider(width=1),
        search_field,
        ft.VerticalDivider(width=1),
        auto_refresh_switch,
        auto_scroll_switch,
        compact_mode_switch,
        live_mode_switch,
        ft.VerticalDivider(width=1),
        component_options,
        ft.VerticalDivider(width=1),
        refresh_btn,
        export_btn,
        clear_btn,
        save_filter_button,
    ], spacing=6, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    # Simplified statistics - just a placeholder since update_statistics was removed
    def update_statistics():
        """Placeholder for statistics update - simplified version"""
        pass

    def update_time_filter():
        """Placeholder for time filter update"""
        # Time filters removed for compactness
        _refresh_lists_by_filter()

    # Saved filters functionality
    def save_current_filter():
        """Save the current filter configuration as a preset"""
        # Get current filter values
        current_filters = {
            'selected_levels': list(view_state.selected_levels),
            'search_query': view_state.search_query,
            'start_time': start_time_filter,
            'end_time': end_time_filter,
            'component_filter': selected_component_filter,
        }

        # Create a name for the filter preset (could also prompt user for name)
        import time
        filter_name = f"Filter_{int(time.time())}"

        # Save to client storage
        with contextlib.suppress(Exception):
            saved_filters = page.client_storage.get("logs.saved_filters") or {}
            saved_filters[filter_name] = current_filters
            page.client_storage.set("logs.saved_filters", saved_filters)

            # Update the saved filters dropdown
            update_saved_filters_dropdown()
        _show_toast(page, f"Filter saved as {filter_name}", "success")

    def load_filter_preset(filter_name):
        """Load a saved filter preset"""
        saved_filters = page.client_storage.get("logs.saved_filters") or {}
        filter_data = saved_filters.get(filter_name, {})

        if filter_data:
            # Apply the saved filter settings
            view_state.selected_levels = set(filter_data.get('selected_levels', []))

            # Update the search field
            search_field.value = filter_data.get('search_query', '')
            view_state.search_query = filter_data.get('search_query', '')

            # Update time filters
            nonlocal start_time_filter, end_time_filter, selected_component_filter
            start_time_filter = filter_data.get('start_time', None)
            end_time_filter = filter_data.get('end_time', None)

            selected_component_filter = filter_data.get('component_filter', 'All')

            # Update UI elements to reflect saved values
            # Time filter fields removed for compactness
            if component_options:
                component_options.value = selected_component_filter

            # Update chip selections
            for level_name, chip in _chip_refs.items():
                chip.selected = level_name in view_state.selected_levels
                config = LogColorSystem.get_level_config(level_name)
                chip.bgcolor = LogColorSystem.get_surface_tint(
                    config["primary"],
                    0.20 if level_name in view_state.selected_levels else 0.08
                )
                if chip.leading:
                    chip.leading.color = config["primary"]
                with contextlib.suppress(Exception):
                    chip.update()

            # Refresh the logs to apply the new filters
            _refresh_lists_by_filter()
            _show_toast(page, f"Loaded filter: {filter_name}", "success")

    def update_saved_filters_dropdown():
        """Update the saved filters dropdown with available presets"""
        saved_filters = page.client_storage.get("logs.saved_filters") or {}
        filter_names = list(saved_filters.keys())

        # Clear existing options and add new ones
        # Note: We can't update dropdown options dynamically in Flet,
        # so this would require recreating the control or using a different approach
        pass

    def toggle_live_mode(e):
        """Toggle live mode on/off"""
        nonlocal is_live_mode, websocket_connection
        is_live_mode = live_mode_switch.value

        if is_live_mode and websockets:
            # Start WebSocket connection for live logs
            page.run_task(start_websocket_connection)
            # Store the task reference if needed for cancellation
            # task reference is stored in _live_task in the setup_subscriptions function
        elif not is_live_mode and websocket_connection:
            # Close WebSocket connection
            async def close_websocket():
                nonlocal websocket_connection
                with contextlib.suppress(Exception):
                    if websocket_connection:
                        await websocket_connection.close()
                # Update the connection variable after closing
                websocket_connection = None

            page.run_task(close_websocket)

    # Set up change event for live mode switch
    live_mode_switch.on_change = toggle_live_mode

    async def start_websocket_connection():
        """Start WebSocket connection to receive live logs"""
        nonlocal websocket_connection
        try:
            # Check if websockets module is available
            if not websockets:
                _show_toast(page, "WebSockets not available", "error")
                live_mode_switch.value = False
                with contextlib.suppress(Exception):
                    live_mode_switch.update()
                return

            # This would connect to your server's WebSocket endpoint
            # Replace with actual WebSocket endpoint
            ws_url = "ws://localhost:8080/logs"  # Placeholder - replace with actual endpoint
            websocket_connection = await websockets.connect(ws_url)

            # Start listening for messages
            await listen_for_logs(websocket_connection)
        except Exception as ex:
            # Handle connection errors
            _show_toast(page, f"WebSocket connection failed: {str(ex)}", "error")
            is_live_mode = False
            live_mode_switch.value = False
            with contextlib.suppress(Exception):
                live_mode_switch.update()

    async def listen_for_logs(ws_connection):
        """Listen for incoming log messages from WebSocket"""
        try:
            async for message in ws_connection:
                try:
                    # Parse the incoming log message
                    log_data = json.loads(message)

                    # Add to the appropriate log list based on the source
                    if active_tab_index == 0:  # System logs tab
                        # Prepend new log to the existing list
                        view_state.system_logs_data.insert(0, log_data)
                    else:  # Flet logs tab
                        view_state.flet_logs_data.insert(0, log_data)

                    # Update statistics
                    update_statistics()

                    # If auto-scroll is enabled, scroll to the new log
                    if auto_scroll_switch.value:
                        # Refresh the view to show the new log
                        if active_tab_index == 0:
                            _render_list(system_list_ref, view_state.system_logs_data, "System Logs", is_system=True)
                        else:
                            _render_list(flet_list_ref, view_state.flet_logs_data, "Flet Logs", is_system=False)

                        # Scroll to the top item to see the latest log
                        list_ref = system_list_ref if active_tab_index == 0 else flet_list_ref
                        if list_ref.current:
                            with contextlib.suppress(Exception):
                                list_ref.current.scroll_to(offset=0, duration=300)
                except json.JSONDecodeError:
                    # Skip invalid JSON messages
                    continue
                except Exception:
                    # Handle other parsing errors
                    continue
        except Exception as ws_ex:
            # Check if it's a websocket connection closed error
            if websockets and 'ConnectionClosed' in str(type(ws_ex)):
                # Connection was closed, stop live mode
                is_live_mode = False
                live_mode_switch.value = False
                with contextlib.suppress(Exception):
                    live_mode_switch.update()
                _show_toast(page, "WebSocket connection closed", "info")
            else:
                # Handle other connection errors
                is_live_mode = False
                live_mode_switch.value = False
                with contextlib.suppress(Exception):
                    live_mode_switch.update()
                _show_toast(page, "Live log connection error", "error")

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
        ft.Container(content=header_row, padding=ft.padding.only(bottom=8)),
        filter_container,
        # Stats row removed for compactness
        ft.Container(content=tabbar, padding=ft.padding.symmetric(vertical=8)),
        content_host,
    ], spacing=0, expand=True)

    # Main container with reduced padding
    main_container = ft.Container(
        content=main_content,
        padding=16,
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

                await asyncio.sleep(5.0)  # Refresh every 5 seconds (reduced spam)
        except asyncio.CancelledError:
            return
        except Exception:
            # Don't crash on background errors
            return

    async def setup_subscriptions():
        """Initialize view with fast initial load"""
        nonlocal _live_task

        # Load saved settings
        load_saved_settings()

        # CRITICAL FIX: Wait for refs to be fully initialized
        # Flet needs time to attach controls to page tree and populate refs
        # Without this delay, ListView.update() fails with "Control must be added to the page first"
        await asyncio.sleep(0.3)

        # Additional safety: Wait for refs to be populated
        max_wait = 20  # 2 seconds max wait
        wait_count = 0
        while (wait_count < max_wait and
               not all([tabbar_row_ref.current, content_host_ref.current,
                       system_list_ref.current, flet_list_ref.current])):
            await asyncio.sleep(0.1)
            wait_count += 1

        # Render initial UI
        _render_tabbar()
        _render_active_content()

        # Load initial data - must wait for completion to ensure UI updates
        try:
            await refresh_system_logs(show_toast=False, show_spinner=True)
            await refresh_flet_logs(show_toast=False, show_spinner=True)
        except Exception as e:
            # Log any errors during initial load
            print(f"Error loading initial logs: {e}")
            import traceback
            traceback.print_exc()

        # Start auto-refresh loop
        try:
            _live_task = asyncio.create_task(_auto_refresh_loop())
        except Exception:
            _live_task = None

    return main_container, dispose, setup_subscriptions