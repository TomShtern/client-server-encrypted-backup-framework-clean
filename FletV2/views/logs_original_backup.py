#!/usr/bin/env python3
"""Enhanced Logs View with Material Design 3 and Advanced Server Integration

Features:
 - Enhanced server bridge integration with async operations
 - Material Design 3 styling with sophisticated progress indicators
 - Advanced filtering (date range, component, regex search)
 - Multiple export formats (CSV, JSON, TXT) with progress tracking
 - Real-time log streaming support
 - State manager integration for reactive updates
 - Log level statistics and visual indicators
 - Smooth animations and transitions
 - Zero-based internal pagination (user display +1)

All internal page math uses zero-based indexing. User-facing labels add +1.
"""

import flet as ft
from typing import List, Dict, Any, Optional, Callable
import asyncio
from datetime import datetime, timedelta
import random
import re
import json
import csv
import tempfile
import os

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge
from utils.state_manager import StateManager
from utils.ui_helpers import level_colors, striped_row_color, build_level_badge
from utils.performance import PerfTimer
from utils.user_feedback import show_success_message
from config import ASYNC_DELAY
from utils.performance import (
    PaginationConfig,
    global_memory_manager, paginate_data
)
from theme import get_brand_color, create_modern_button_style, get_shadow_style
from utils.ui_components import create_modern_card

logger = get_logger(__name__)


def create_logs_view(
    server_bridge: Optional[ServerBridge],
    page: ft.Page,
    state_manager: StateManager
) -> ft.Control:
    """Return the enhanced logs view control with Material Design 3 and server integration."""
    logger.info("Creating enhanced logs view with Material Design 3 and server integration")

    # Enhanced State Management
    logs_data: List[Dict[str, Any]] = []
    filtered_logs_data: List[Dict[str, Any]] = []
    current_filter = "ALL"
    search_query = ""
    is_loading = False
    last_updated = None
    logs_statistics: Dict[str, Any] = {}
    streaming_enabled = False
    streaming_task: Optional[asyncio.Task] = None

    # Advanced filtering state
    date_filter_enabled = False
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    component_filter = "ALL"
    regex_search_enabled = False
    search_highlights: List[str] = []

    # Performance helpers - Flet-compatible debouncing
    search_debounce_timer = None
    cancelled_tasks = []  # Track cancelled tasks for cleanup
    pagination_config = PaginationConfig(page_size=50, current_page=0)  # zero-based
    global_memory_manager.register_component("logs_view")

    # Theme detection for Material Design 3 styling
    is_dark_theme = page.theme_mode == ft.ThemeMode.DARK

    # ---------------------- Enhanced Data Generation / Helpers ---------------------- #
    def generate_mock_logs(count: int = 200) -> List[Dict[str, Any]]:
        """Generate enhanced mock logs with more realistic data patterns."""
        base_time = datetime.now()
        log_types = ["INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG"]
        components = ["Server", "Client", "Database", "File Transfer", "Auth", "System", "Network", "Storage", "Backup", "Security"]
        messages = [
            "Connection established from 192.168.1.{ip}",
            "File transfer completed: {filename}",
            "Authentication successful for user_{id}",
            "Database query executed in {time}ms",
            "Error processing request: timeout",
            "Server started on port 1256",
            "Client disconnected unexpectedly",
            "Backup operation completed successfully",
            "Memory usage: {usage}%",
            "SSL certificate renewed",
            "Configuration reloaded",
            "Cache cleared successfully",
            "Network connection restored",
            "Failed to connect to database",
            "File verification completed",
            "Encryption key rotated successfully",
            "Log rotation completed",
            "Performance metrics collected",
            "Health check passed",
            "Scheduled maintenance started"
        ]
        data: List[Dict[str, Any]] = []
        for i in range(count):
            time_offset = timedelta(
                hours=random.randint(0, 72),  # Extended time range
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59)
            )
            log_time = base_time - time_offset
            level = random.choice(log_types)
            component = random.choice(components)
            template = random.choice(messages)
            msg = template.format(
                ip=random.randint(100, 199),
                filename=f"document_{random.randint(1,999)}.{random.choice(['pdf','txt','jpg','log','zip','bak'])}",
                id=random.randint(1, 500),
                time=random.randint(20, 900),
                usage=random.randint(30, 97)
            )
            data.append({
                "id": i + 1,
                "timestamp": log_time.isoformat(),
                "level": level,
                "component": component,
                "message": msg
            })
        data.sort(key=lambda x: x["timestamp"], reverse=True)
        return data

    def calculate_logs_statistics(logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate comprehensive log statistics."""
        if not logs:
            return {}

        stats = {
            "total_logs": len(logs),
            "levels": {},
            "components": {},
            "recent_errors": 0,
            "hourly_distribution": {},
            "error_rate": 0.0,
            "last_24h": 0
        }

        now = datetime.now()
        last_24h = now - timedelta(hours=24)

        for log in logs:
            level = log.get("level", "UNKNOWN")
            component = log.get("component", "Unknown")

            # Level distribution
            stats["levels"][level] = stats["levels"].get(level, 0) + 1

            # Component distribution
            stats["components"][component] = stats["components"].get(component, 0) + 1

            # Time-based analysis
            try:
                log_time = datetime.fromisoformat(log["timestamp"])
                if log_time >= last_24h:
                    stats["last_24h"] += 1
                    if level == "ERROR":
                        stats["recent_errors"] += 1

                # Hourly distribution
                hour = log_time.hour
                stats["hourly_distribution"][hour] = stats["hourly_distribution"].get(hour, 0) + 1
            except (ValueError, KeyError):
                pass

        # Calculate error rate
        if stats["last_24h"] > 0:
            stats["error_rate"] = stats["recent_errors"] / stats["last_24h"]

        return stats

    def level_fg(level: str):
        fg, _ = level_colors(level)
        return fg

    def level_bg(level: str):
        _, bg = level_colors(level)
        return bg

    def apply_filters():
        """Enhanced filtering with date range, component, and regex support."""
        nonlocal filtered_logs_data, search_highlights
        data = logs_data.copy()
        search_highlights = []

        # Level filtering
        if current_filter != "ALL":
            data = [d for d in data if d["level"] == current_filter]

        # Component filtering
        if component_filter != "ALL":
            data = [d for d in data if d.get("component") == component_filter]

        # Date range filtering
        if date_filter_enabled and (date_from or date_to):
            filtered_by_date = []
            for d in data:
                try:
                    log_time = datetime.fromisoformat(d["timestamp"])
                    if date_from and log_time < date_from:
                        continue
                    if date_to and log_time > date_to:
                        continue
                    filtered_by_date.append(d)
                except (ValueError, KeyError):
                    # Include logs with invalid timestamps
                    filtered_by_date.append(d)
            data = filtered_by_date

        # Search filtering with regex support
        if search_query.strip():
            q = search_query.strip()
            filtered_by_search = []

            if regex_search_enabled:
                try:
                    pattern = re.compile(q, re.IGNORECASE)
                    for d in data:
                        message = d.get("message", "")
                        component = d.get("component", "")
                        level = d.get("level", "")

                        if (pattern.search(message) or
                            pattern.search(component) or
                            pattern.search(level)):
                            filtered_by_search.append(d)
                            # Extract highlights for regex matches
                            for match in pattern.finditer(message):
                                if match.group() not in search_highlights:
                                    search_highlights.append(match.group())
                except re.error:
                    # Fallback to simple search if regex is invalid
                    q_lower = q.lower()
                    filtered_by_search = [d for d in data if (
                        q_lower in d.get("message", "").lower() or
                        q_lower in d.get("component", "").lower() or
                        q_lower in d.get("level", "").lower()
                    )]
                    search_highlights = [q] if filtered_by_search else []
            else:
                # Simple text search
                q_lower = q.lower()
                filtered_by_search = [d for d in data if (
                    q_lower in d.get("message", "").lower() or
                    q_lower in d.get("component", "").lower() or
                    q_lower in d.get("level", "").lower()
                )]
                search_highlights = [q] if filtered_by_search else []

            data = filtered_by_search

        filtered_logs_data = data

    # ---------------------- Enhanced UI Update Functions --------------------------- #
    def create_log_data_row(entry: Dict[str, Any], index: int) -> ft.DataRow:
        """Create a DataRow for a log entry with enhanced styling and highlighting."""
        try:
            # Format timestamp to show date and time
            dt = datetime.fromisoformat(entry["timestamp"])
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, KeyError):
            time_str = str(entry.get("timestamp", "Unknown"))

        # Create enhanced level badge with Material Design 3 styling
        level_badge = build_level_badge(entry["level"])

        # Handle long messages with smart truncation and highlighting
        message = entry.get("message", "")
        display_message = message

        # Apply search highlighting if enabled
        if search_highlights and search_query.strip():
            for highlight in search_highlights:
                if highlight.lower() in message.lower():
                    # Simple highlighting - in a real implementation, you'd use RichText
                    display_message = message.replace(
                        highlight,
                        f"🔍{highlight}🔍"  # Simple highlight marker
                    )
                    break

        if len(display_message) > 80:
            display_message = display_message[:77] + "..."

        # Get row background color with enhanced Material Design 3 styling
        row_bg = striped_row_color(index)

        return ft.DataRow(
            cells=[
                ft.DataCell(
                    ft.Text(
                        time_str,
                        size=12,
                        weight=ft.FontWeight.W_500,
                        color=ft.Colors.BLUE_GREY_300 if is_dark_theme else ft.Colors.BLUE_GREY_700,
                        font_family="monospace"
                    )
                ),
                ft.DataCell(level_badge),
                ft.DataCell(
                    ft.Text(
                        entry.get("component", "Unknown"),
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.INDIGO_300 if is_dark_theme else ft.Colors.INDIGO_700
                    )
                ),
                ft.DataCell(
                    ft.Container(
                        content=ft.Text(
                            display_message,
                            size=12,
                            color=ft.Colors.GREY_200 if is_dark_theme else ft.Colors.GREY_800,
                            overflow=ft.TextOverflow.ELLIPSIS
                        ),
                        tooltip=message if len(message) > 80 else None,
                        expand=True
                    )
                )
            ],
            color=row_bg
        )

    def create_statistics_panel() -> ft.Container:
        """Create a responsive statistics panel with Material Design 3 styling."""
        if not logs_statistics:
            return ft.Container()

        # Total logs card with modern styling
        total_logs_card = create_modern_card(
            content=ft.Column([
                ft.Text("Total Logs", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(str(logs_statistics.get("total_logs", 0)), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY)
            ], spacing=6),
            elevation="soft",
            is_dark=is_dark_theme,
            padding=16,
            hover_effect=True
        )

        # Error rate card with enhanced color coding
        error_rate = logs_statistics.get("error_rate", 0)
        error_color = ft.Colors.ERROR if error_rate > 0.1 else ft.Colors.GREEN_500 if error_rate < 0.05 else ft.Colors.YELLOW_500
        error_rate_card = create_modern_card(
            content=ft.Column([
                ft.Text("Error Rate", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(f"{error_rate:.1%}", size=24, weight=ft.FontWeight.BOLD, color=error_color)
            ], spacing=6),
            elevation="soft",
            is_dark=is_dark_theme,
            padding=16,
            hover_effect=True,
            color_accent="error" if error_rate > 0.1 else "success" if error_rate < 0.05 else "warning"
        )

        # Last 24h card with secondary accent
        last_24h_card = create_modern_card(
            content=ft.Column([
                ft.Text("Last 24h", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(str(logs_statistics.get("last_24h", 0)), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.SECONDARY)
            ], spacing=6),
            elevation="soft",
            is_dark=is_dark_theme,
            padding=16,
            hover_effect=True
        )

        # Recent errors card with tertiary accent
        recent_errors_card = create_modern_card(
            content=ft.Column([
                ft.Text("Recent Errors", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(str(logs_statistics.get("recent_errors", 0)), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.TERTIARY)
            ], spacing=6),
            elevation="soft",
            is_dark=is_dark_theme,
            padding=16,
            hover_effect=True
        )

        # Use ResponsiveRow for adaptive layout
        return ft.Container(
            content=ft.ResponsiveRow([
                ft.Column([total_logs_card], col={"sm": 12, "md": 6, "lg": 3}),
                ft.Column([error_rate_card], col={"sm": 12, "md": 6, "lg": 3}),
                ft.Column([last_24h_card], col={"sm": 12, "md": 6, "lg": 3}),
                ft.Column([recent_errors_card], col={"sm": 12, "md": 6, "lg": 3})
            ]),
            padding=ft.Padding(0, 12, 0, 16)
        )

    def update_list():
        """Enhanced list update with Material Design 3 animations and statistics."""
        # Update statistics
        nonlocal logs_statistics
        logs_statistics = calculate_logs_statistics(filtered_logs_data)

        if not filtered_logs_data:
            empty_state = create_modern_card(
                content=ft.Column([
                    ft.Icon(ft.Icons.ARTICLE_OUTLINED, size=64, color=ft.Colors.PRIMARY),
                    ft.Container(height=16),
                    ft.Text("No logs found", weight=ft.FontWeight.BOLD, size=18, color=ft.Colors.ON_SURFACE),
                    ft.Text("Adjust filters or search query to view logs.", size=14, color=ft.Colors.ON_SURFACE_VARIANT),
                    ft.Container(height=24),
                    ft.Row([
                        ft.FilledButton("Show All", icon=ft.Icons.CLEAR_ALL, on_click=create_filter_handler("ALL")),
                        ft.OutlinedButton("Refresh", icon=ft.Icons.REFRESH, on_click=on_refresh_logs)
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=16)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                elevation="medium",
                is_dark=is_dark_theme,
                padding=32,
                hover_effect=True
            )
            empty_state.height = 320
            empty_state.alignment = ft.alignment.center
            logs_container.controls = [empty_state]
        else:
            # Ensure current page valid after any filter change
            total_pages = max(1, (len(filtered_logs_data) + pagination_config.page_size - 1) // pagination_config.page_size)
            if pagination_config.current_page >= total_pages:
                pagination_config.current_page = max(0, total_pages - 1)

            slice_data, _ = paginate_data(
                filtered_logs_data,
                pagination_config.current_page,
                pagination_config.page_size
            )

            # Create enhanced DataTable with Material Design 3 styling
            data_table = ft.DataTable(
                columns=[
                    ft.DataColumn(
                        ft.Text("Time", weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.PRIMARY),
                        numeric=False
                    ),
                    ft.DataColumn(
                        ft.Text("Level", weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.PRIMARY),
                        numeric=False
                    ),
                    ft.DataColumn(
                        ft.Text("Component", weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.PRIMARY),
                        numeric=False
                    ),
                    ft.DataColumn(
                        ft.Text("Message", weight=ft.FontWeight.BOLD, size=12, color=ft.Colors.PRIMARY),
                        numeric=False
                    ),
                ],
                rows=[create_log_data_row(entry, i) for i, entry in enumerate(slice_data)],
                border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                border_radius=12,
                vertical_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                horizontal_lines=ft.border.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
                column_spacing=20,
                data_row_min_height=48,
                data_row_max_height=80,
            )

            # Wrap in enhanced scrollable container
            table_container = ft.Container(
                content=ft.Column([
                    create_statistics_panel(),
                    ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                    data_table
                ], spacing=0),
                bgcolor=ft.Colors.SURFACE,
                border_radius=12,
                padding=ft.Padding(12, 12, 12, 12),
                shadow=get_shadow_style("soft", is_dark_theme)
            )

            scrollable_table = ft.Column([
                table_container
            ], expand=True, scroll=ft.ScrollMode.AUTO)

            logs_container.controls = [
                ft.AnimatedSwitcher(
                    content=scrollable_table,
                    transition=ft.AnimatedSwitcherTransition.FADE,
                    duration=300,  # Slightly longer for smoother animation
                )
            ]

        # Update statistics panel
        if hasattr(logs_container, 'parent') and logs_container.parent:
            logs_container.update()
        else:
            # Fallback for initial render
            try:
                logs_container.update()
            except:
                pass

    def update_status():
        """Enhanced status update with streaming indicator and statistics."""
        total = len(logs_data)
        filt = len(filtered_logs_data)
        total_pages = max(1, (filt + pagination_config.page_size - 1) // pagination_config.page_size)

        # Build status message with enhanced information
        status_parts = []

        if filt:
            start = pagination_config.current_page * pagination_config.page_size + 1
            end = min(start + pagination_config.page_size - 1, filt)
            status_parts.append(f"Showing {start}-{end} of {filt} logs")
            if filt != total:
                status_parts.append(f"(Filtered from {total})")
            status_parts.append(f"Page {pagination_config.current_page + 1} of {total_pages}")
        else:
            status_parts.append(f"No logs found (Total: {total})")

        # Add streaming indicator
        if streaming_enabled:
            status_parts.append("🔴 Live")

        # Add search highlights info
        if search_highlights:
            status_parts.append(f"Highlights: {len(search_highlights)}")

        status_text.value = " | ".join(status_parts)
        # Safe update - only if control is attached to page
        if hasattr(status_text, 'page') and status_text.page:
            status_text.update()

    def update_pagination_controls():
        total_pages = max(1, (len(filtered_logs_data) + pagination_config.page_size - 1) // pagination_config.page_size)
        first_btn.disabled = pagination_config.current_page <= 0
        prev_btn.disabled = pagination_config.current_page <= 0
        next_btn.disabled = (pagination_config.current_page + 1) >= total_pages
        last_btn.disabled = (pagination_config.current_page + 1) >= total_pages
        page_info_text.value = f"Page {pagination_config.current_page + 1} of {total_pages}"
        for c in [first_btn, prev_btn, next_btn, last_btn, page_info_text]:
            c.update()

    # ---------------------- Enhanced Event Handlers -------------------------------- #
    async def perform_search():
        """Enhanced search with comprehensive error handling and user feedback."""
        nonlocal search_query
        pagination_config.current_page = 0

        # Set loading state with enhanced UI feedback
        state_manager.set_loading("logs_search", True)
        if loading_indicator_ref.current:
            loading_indicator_ref.current.visible = True
            loading_indicator_ref.current.update()

        try:
            # Validate search query for regex mode
            if regex_search_enabled and search_query.strip():
                try:
                    re.compile(search_query.strip())
                except re.error as e:
                    state_manager.add_notification(
                        f"Invalid regex pattern: {str(e)}",
                        "error", auto_dismiss=5
                    )
                    return

            with PerfTimer("logs.search.perform"):
                apply_filters()
                update_list()
                update_status()
                update_pagination_controls()

            # Update state manager with search results
            await state_manager.update_async("logs_filtered", filtered_logs_data, source="search")

            logger.info(f"Search query='{search_query}' results={len(filtered_logs_data)} regex={regex_search_enabled}")

            # Enhanced notification for search results
            if search_query.strip():
                search_type = "regex" if regex_search_enabled else "text"
                highlight_info = f" ({len(search_highlights)} highlights)" if search_highlights else ""

                if filtered_logs_data:
                    state_manager.add_notification(
                        f"{search_type.title()} search found {len(filtered_logs_data)} results{highlight_info}",
                        "success", auto_dismiss=3
                    )
                else:
                    state_manager.add_notification(
                        f"No results found for {search_type} search '{search_query}'",
                        "warning", auto_dismiss=4
                    )

        except Exception as e:
            logger.error(f"Search operation failed: {e}", exc_info=True)
            state_manager.add_notification(
                f"Search failed: {str(e)}",
                "error", auto_dismiss=5
            )
        finally:
            state_manager.set_loading("logs_search", False)
            if loading_indicator_ref.current:
                loading_indicator_ref.current.visible = False
                loading_indicator_ref.current.update()

    def on_search_change(e):
        nonlocal search_query, search_debounce_timer, cancelled_tasks
        search_query = e.control.value

        # Cancel previous debounce timer if it exists
        if search_debounce_timer:
            search_debounce_timer.cancel()
            cancelled_tasks.append(search_debounce_timer)  # Track for cleanup

        # Create debounced search using page.run_task with delay
        async def debounced_search():
            try:
                await asyncio.sleep(0.3)  # 300ms debounce delay
                await perform_search()
            except asyncio.CancelledError:
                # Silently handle cancellation
                pass
            except Exception as e:
                logger.error(f"Search debounce error: {e}")

        # Use page.run_task for proper Flet async handling
        search_debounce_timer = page.run_task(debounced_search)

    def on_search_clear(e):
        nonlocal search_query, search_debounce_timer, cancelled_tasks
        search_query = ""
        search_field.value = ""

        # Cancel any pending search
        if search_debounce_timer:
            search_debounce_timer.cancel()
            cancelled_tasks.append(search_debounce_timer)
            search_debounce_timer = None

        pagination_config.current_page = 0
        apply_filters()
        update_list()
        update_status()
        update_pagination_controls()

    async def cleanup_cancelled_tasks():
        """Clean up cancelled tasks to prevent CancelledError logs."""
        nonlocal cancelled_tasks
        if not cancelled_tasks:
            return

        cleanup_list = cancelled_tasks[:]
        cancelled_tasks = []

        for task in cleanup_list:
            if not task.done():
                try:
                    await task
                except asyncio.CancelledError:
                    pass  # Expected cancellation
                except Exception:
                    pass  # Ignore other errors during cleanup

    # Run cleanup periodically
    async def periodic_cleanup():
        """Periodic cleanup of cancelled tasks."""
        while True:
            await asyncio.sleep(10)  # Every 10 seconds
            await cleanup_cancelled_tasks()

    # Start cleanup task
    page.run_task(periodic_cleanup)

    def create_filter_handler(level: str):
        def handler(_):
            nonlocal current_filter
            current_filter = level
            pagination_config.current_page = 0
            apply_filters()
            update_list()
            update_status()
            update_pagination_controls()
            # Update ALL button style
            for i, b in enumerate(filter_buttons):
                if i == 0:
                    b.style = ft.ButtonStyle(bgcolor=ft.Colors.PRIMARY if current_filter == "ALL" else None)
                b.update()
        return handler

    def close_dialog(_):
        """Enhanced dialog close with animation."""
        if page.dialog:
            page.dialog.open = False
            page.dialog.update()

    async def confirm_clear(_):
        """Enhanced clear operation with comprehensive error handling and progress tracking."""
        nonlocal logs_data, filtered_logs_data

        # Set loading state with enhanced UI feedback
        state_manager.set_loading("logs_clear", True)
        if loading_indicator_ref.current:
            loading_indicator_ref.current.visible = True
            loading_indicator_ref.current.update()

        try:
            # Show progress notification
            state_manager.add_notification(
                "Clearing logs...", "info", auto_dismiss=False
            )

            original_count = len(logs_data)

            # Use server bridge if available
            if server_bridge and hasattr(server_bridge, 'clear_logs_async'):
                try:
                    result = await server_bridge.clear_logs_async()
                    if result.get('success', True):
                        logs_data = []
                        filtered_logs_data = []

                        # Update state manager
                        if hasattr(state_manager, 'clear_logs_state'):
                            await state_manager.clear_logs_state()
                        else:
                            await state_manager.update_async("logs_data", [], source="clear")

                        # Broadcast clear event to other views (if method exists)
                        if hasattr(state_manager, 'broadcast_logs_event'):
                            state_manager.broadcast_logs_event({
                                "type": "logs_cleared",
                                "count": original_count,
                                "mode": result.get('mode', 'server')
                            })
                        else:
                            # Fallback: update logs_events state
                            await state_manager.update_async("logs_events", {
                                "type": "logs_cleared",
                                "count": original_count,
                                "mode": result.get('mode', 'server')
                            }, source="clear_operation")

                        state_manager.add_notification(
                            f"Successfully cleared {original_count} logs ({result.get('mode', 'server')} mode)",
                            "success", auto_dismiss=4
                        )
                    else:
                        error_msg = result.get('error', 'Unknown server error')
                        logger.error(f"Server clear failed: {error_msg}")
                        state_manager.add_notification(
                            f"Failed to clear logs: {error_msg}",
                            "error", auto_dismiss=6
                        )
                        return  # Don't proceed with local clear if server explicitly failed

                except Exception as e:
                    logger.warning(f"Server clear failed, attempting local clear: {e}")
                    # Fall through to local clear
                    logs_data = []
                    filtered_logs_data = []
                    await state_manager.update_async("logs_data", [], source="local_clear")
                    state_manager.add_notification(
                        f"Logs cleared locally ({original_count} entries) - server unavailable",
                        "warning", auto_dismiss=5
                    )
            else:
                # Local clear with enhanced feedback
                logs_data = []
                filtered_logs_data = []
                await state_manager.update_async("logs_data", [], source="local_clear")
                state_manager.add_notification(
                    f"Logs cleared locally ({original_count} entries)",
                    "success", auto_dismiss=4
                )

            # Update UI with smooth transition
            populate_component_filter()  # Clear component options
            apply_filters()
            update_list()
            update_status()
            update_pagination_controls()

        except Exception as e:
            logger.error(f"Clear operation failed: {e}", exc_info=True)
            state_manager.add_notification(
                f"Clear operation failed: {str(e)}",
                "error", auto_dismiss=6
            )
        finally:
            state_manager.set_loading("logs_clear", False)
            if loading_indicator_ref.current:
                loading_indicator_ref.current.visible = False
                loading_indicator_ref.current.update()
            close_dialog(None)

    def on_clear_logs(_):
        """Enhanced clear logs dialog with Material Design 3 styling."""
        page.dialog = ft.AlertDialog(
            title=ft.Text("Clear Logs", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Are you sure you want to clear all logs?"),
                ft.Text("This action cannot be undone.", size=12, color=ft.Colors.ERROR, italic=True)
            ], tight=True, spacing=8),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton(
                    "Clear All Logs",
                    icon=ft.Icons.CLEAR_ALL,
                    on_click=lambda e: page.run_task(confirm_clear, e),
                    style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR)
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.dialog.update()

    def on_refresh_logs(_):
        """Enhanced refresh with comprehensive error handling and progress tracking."""
        async def refresh_with_feedback():
            try:
                # Show immediate feedback
                state_manager.add_notification("Refreshing logs...", "info", auto_dismiss=3)

                # Set loading state
                state_manager.set_loading("logs_load", True)
                if loading_indicator_ref.current:
                    loading_indicator_ref.current.visible = True
                    loading_indicator_ref.current.update()

                # Store previous count for comparison
                previous_count = len(logs_data)

                # Perform the refresh
                await load_logs_data_async()

                # Show completion feedback with change information
                new_count = len(logs_data)
                change = new_count - previous_count

                if change > 0:
                    state_manager.add_notification(
                        f"Refresh complete: {new_count} logs ({change} new entries)",
                        "success", auto_dismiss=4
                    )
                elif change < 0:
                    state_manager.add_notification(
                        f"Refresh complete: {new_count} logs ({abs(change)} removed)",
                        "info", auto_dismiss=4
                    )
                else:
                    state_manager.add_notification(
                        f"Refresh complete: {new_count} logs (no changes)",
                        "info", auto_dismiss=3
                    )

            except Exception as e:
                logger.error(f"Refresh operation failed: {e}", exc_info=True)
                state_manager.add_notification(
                    f"Refresh failed: {str(e)}",
                    "error", auto_dismiss=5
                )
            finally:
                state_manager.set_loading("logs_load", False)
                if loading_indicator_ref.current:
                    loading_indicator_ref.current.visible = False
                    loading_indicator_ref.current.update()

        page.run_task(refresh_with_feedback)

    # Helper function for file save dialog
    async def choose_save_location(temp_path: str, export_format: str) -> Optional[str]:
        """Use FilePicker to let user choose save location and move the temp file."""
        try:
            # Create FilePicker for save dialog
            file_picker = ft.FilePicker(
                on_result=lambda e: None  # Will be handled below
            )
            page.overlay.append(file_picker)
            page.update()

            # Create a future to wait for user selection
            save_future = asyncio.Future()

            def on_save_result(e: ft.FilePickerResultEvent):
                if e.path:
                    save_future.set_result(e.path)
                else:
                    save_future.set_result(None)

            file_picker.on_result = on_save_result

            # Generate default filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"logs_export_{timestamp}.{export_format}"

            # Open save dialog
            file_picker.save_file(
                dialog_title="Save logs export as...",
                file_name=default_filename,
                allowed_extensions=[export_format],
            )

            # Wait for user selection (with timeout)
            try:
                selected_path = await asyncio.wait_for(save_future, timeout=60.0)
                if selected_path:
                    # Move temp file to selected location
                    import shutil
                    shutil.move(temp_path, selected_path)

                    # Show "Open Folder" option
                    await show_export_complete_dialog(selected_path)

                    return selected_path
                else:
                    # User cancelled - clean up temp file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    return None

            except asyncio.TimeoutError:
                # Timeout - clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                return None

        except Exception as e:
            logger.error(f"File save dialog error: {e}")
            # Fallback - just notify about temp location
            state_manager.add_notification(f"Export saved to: {temp_path}", "info")
            return temp_path
        finally:
            # Clean up FilePicker
            if file_picker in page.overlay:
                page.overlay.remove(file_picker)
                page.update()

    async def show_export_complete_dialog(file_path: str):
        """Show dialog with option to open folder containing exported file."""
        async def open_folder_async():
            try:
                import platform
                folder_path = os.path.dirname(file_path)

                if platform.system() == "Windows":
                    await asyncio.create_subprocess_exec("explorer", folder_path)
                elif platform.system() == "Darwin":  # macOS
                    await asyncio.create_subprocess_exec("open", folder_path)
                else:  # Linux
                    await asyncio.create_subprocess_exec("xdg-open", folder_path)

                complete_dialog.open = False
                complete_dialog.update()
            except Exception as e:
                logger.error(f"Failed to open folder: {e}")

        def open_folder(_):
            """Sync wrapper for async folder opening."""
            page.run_task(open_folder_async)

        complete_dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text("Export Complete"),
            content=ft.Text(f"File saved: {os.path.basename(file_path)}"),
            actions=[
                ft.TextButton("Open Folder", on_click=open_folder),
                ft.TextButton("Close", on_click=lambda _: setattr(complete_dialog, 'open', False) or complete_dialog.update())
            ]
        )

        page.dialog = complete_dialog
        complete_dialog.open = True
        complete_dialog.update()

        # Auto-close after 5 seconds
        await asyncio.sleep(5)
        if complete_dialog.open:
            complete_dialog.open = False
            complete_dialog.update()

    async def export_logs_async(export_format: str = "json", include_filters: bool = True):
        """Enhanced export with multiple formats and server bridge integration."""
        try:
            # Progress tracking
            state_manager.start_progress("logs_export", total_steps=3, message="Preparing export")
            state_manager.set_loading("logs_export", True)

            # Create enhanced progress dialog
            progress_ring = ft.ProgressRing(
                width=40,
                height=40,
                color=ft.Colors.PRIMARY,
                stroke_width=4
            )
            progress_text = ft.Text("Preparing export...", size=14, weight=ft.FontWeight.W_500)

            dlg = ft.AlertDialog(
                modal=True,
                title=ft.Row([
                    ft.Icon(ft.Icons.DOWNLOAD, color=ft.Colors.PRIMARY),
                    ft.Text("Export Logs", weight=ft.FontWeight.BOLD)
                ], spacing=8),
                content=ft.Container(
                    content=ft.Column([
                        progress_ring,
                        progress_text,
                        ft.Text(f"Format: {export_format.upper()}", size=12, color=ft.Colors.ON_SURFACE_VARIANT)
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=16),
                    width=300,
                    height=120,
                    padding=ft.Padding(20, 20, 20, 20)
                ),
                bgcolor=ft.Colors.SURFACE,
                shape=ft.RoundedRectangleBorder(radius=16)
            )
            page.dialog = dlg
            dlg.open = True
            dlg.update()

            # Prepare export data
            export_data = filtered_logs_data if include_filters else logs_data
            state_manager.update_progress("logs_export", step=1, message="Exporting via server" if server_bridge and hasattr(server_bridge, 'export_logs_async') else "Generating local export")

            # Use server bridge if available
            if server_bridge and hasattr(server_bridge, 'export_logs_async'):
                try:
                    progress_text.value = "Exporting via server..."
                    progress_text.update()

                    filters = {
                        "level": current_filter if current_filter != "ALL" else None,
                        "component": component_filter if component_filter != "ALL" else None,
                        "search": search_query if search_query.strip() else None,
                        "date_from": date_from.isoformat() if date_from else None,
                        "date_to": date_to.isoformat() if date_to else None
                    } if include_filters else {}

                    result = await server_bridge.export_logs_async(export_format, filters)

                    if result.get('success', True):
                        export_path = result.get('data', {}).get('export_path', 'Unknown')
                        progress_text.value = f"Export completed. Choose save location..."
                        progress_text.update()
                        state_manager.update_progress("logs_export", step=2, message="Awaiting save location...")

                        # Allow user to choose save location
                        final_path = await choose_save_location(export_path, export_format)
                        if final_path:
                            progress_text.value = f"Export saved: {os.path.basename(final_path)}"
                            progress_text.update()
                            await asyncio.sleep(1)

                            state_manager.add_notification(
                                f"Logs exported successfully to {os.path.basename(final_path)} ({result.get('mode', 'server')})",
                                "success"
                            )
                        else:
                            state_manager.add_notification("Export cancelled by user", "info")
                        state_manager.update_progress("logs_export", step=3, message="Completed")
                        return True
                    else:
                        raise Exception(result.get('error', 'Export failed'))

                except Exception as e:
                    logger.warning(f"Server export failed, using local export: {e}")
                    # Fall through to local export

            # Local export fallback
            progress_text.value = "Generating local export..."
            progress_text.update()
            await asyncio.sleep(0.5)

            # Create temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logs_export_{timestamp}.{export_format}"

            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{export_format}', delete=False) as f:
                if export_format == 'json':
                    json.dump(export_data, f, indent=2, default=str)
                elif export_format == 'csv':
                    if export_data:
                        fieldnames = ['timestamp', 'level', 'component', 'message']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for entry in export_data:
                            writer.writerow({
                                'timestamp': entry.get('timestamp', ''),
                                'level': entry.get('level', ''),
                                'component': entry.get('component', ''),
                                'message': entry.get('message', '')
                            })
                elif export_format == 'txt':
                    for entry in export_data:
                        f.write(f"[{entry.get('timestamp', '')}] {entry.get('level', '')}: "
                               f"({entry.get('component', '')}) {entry.get('message', '')}\n")

                export_path = f.name

            progress_text.value = f"Export completed. Choose save location..."
            progress_text.update()
            state_manager.update_progress("logs_export", step=2, message="Awaiting save location...")

            # Allow user to choose save location
            final_path = await choose_save_location(export_path, export_format)
            if final_path:
                state_manager.add_notification(
                    f"Logs exported to {os.path.basename(final_path)} ({len(export_data)} entries)",
                    "success"
                )
            else:
                state_manager.add_notification("Export cancelled by user", "info")
            state_manager.update_progress("logs_export", step=3, message="Completed")
            return final_path is not None

        except Exception as e:
            logger.error(f"Export operation failed: {e}", exc_info=True)
            state_manager.add_notification(
                f"Export failed: {str(e)}",
                "error", auto_dismiss=6
            )
            return False
        finally:
            state_manager.set_loading("logs_export", False)
            state_manager.clear_progress("logs_export")
            if loading_indicator_ref.current:
                loading_indicator_ref.current.visible = False
                loading_indicator_ref.current.update()
            if page.dialog:
                page.dialog.open = False
                page.dialog.update()

    def show_export_dialog(_):
        """Show enhanced export dialog with format selection."""
        format_dropdown = ft.Dropdown(
            label="Export Format",
            value="json",
            options=[
                ft.dropdown.Option("json", "JSON"),
                ft.dropdown.Option("csv", "CSV"),
                ft.dropdown.Option("txt", "Text")
            ],
            width=200
        )

        include_filters_checkbox = ft.Checkbox(
            label="Apply current filters",
            value=True
        )

        def on_export_confirm(_):
            export_format = format_dropdown.value
            include_filters = include_filters_checkbox.value
            close_dialog(None)
            page.run_task(export_logs_async, export_format, include_filters)

        page.dialog = ft.AlertDialog(
            title=ft.Text("Export Logs", weight=ft.FontWeight.BOLD),
            content=ft.Column([
                ft.Text("Choose export format and options:"),
                ft.Container(height=8),
                format_dropdown,
                include_filters_checkbox,
                ft.Container(height=8),
                ft.Text(
                    f"Will export {len(filtered_logs_data)} filtered logs" if filtered_logs_data != logs_data
                    else f"Will export {len(logs_data)} logs",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ], tight=True, spacing=8),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Export", icon=ft.Icons.DOWNLOAD, on_click=on_export_confirm)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog.open = True
        page.dialog.update()

    # ---------------------- Enhanced Async Data Load -------------------------------- #
    async def load_logs_data_async():
        """Enhanced data loading with state manager integration and streaming support."""
        nonlocal logs_data, last_updated, is_loading
        if is_loading:
            return
        is_loading = True

        # Set loading state in state manager
        state_manager.set_loading("logs_load", True)

        try:
            status_text.value = "Loading logs..."
            # Safe update - only if control is attached to page
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()

            with PerfTimer("logs.load.fetch"):
                if server_bridge:
                    try:
                        # Try async method first
                        if hasattr(server_bridge, 'get_logs_async'):
                            logs_data = await server_bridge.get_logs_async()
                        else:
                            # Fallback to sync method
                            logs_data = server_bridge.get_logs()

                        if not isinstance(logs_data, list):
                            logs_data = []

                        # Update state manager with logs data
                        await state_manager.update_logs_async(logs_data, source="server")

                    except Exception as e:
                        logger.warning(f"Server bridge failure: {e}")
                        logs_data = generate_mock_logs()
                        await state_manager.update_logs_async(logs_data, source="mock_fallback")
                        state_manager.add_notification(
                            "Using mock data (server unavailable)",
                            "warning",
                            auto_dismiss=5
                        )
                else:
                    logs_data = generate_mock_logs()
                    await state_manager.update_logs_async(logs_data, source="mock")

            last_updated = datetime.now()
            last_updated_text.value = f"Last updated: {last_updated.strftime('%H:%M:%S')}"
            # Safe update - only if control is attached to page
            if hasattr(last_updated_text, 'page') and last_updated_text.page:
                last_updated_text.update()

            with PerfTimer("logs.load.render"):
                apply_filters()
                update_list()
                update_status()
                update_pagination_controls()

            # Load statistics if server bridge supports it
            if server_bridge and hasattr(server_bridge, 'get_log_statistics_async'):
                try:
                    stats = await server_bridge.get_log_statistics_async()
                    if isinstance(stats, dict):
                        nonlocal logs_statistics
                        logs_statistics = stats
                        update_list()  # Refresh to show statistics
                except Exception as e:
                    logger.debug(f"Failed to load log statistics: {e}")

        except Exception as e:
            logger.error(f"Loading error: {e}")
            status_text.value = "Error loading logs"
            # Safe update - only if control is attached to page
            if hasattr(status_text, 'page') and status_text.page:
                status_text.update()
            state_manager.add_notification(f"Failed to load logs: {str(e)}", "error")
        finally:
            is_loading = False
            state_manager.set_loading("logs_load", False)

    async def start_log_streaming():
        """Start real-time log streaming if supported by server bridge."""
        nonlocal streaming_enabled, streaming_task

        if not server_bridge or not hasattr(server_bridge, 'stream_logs_async'):
            state_manager.add_notification("Log streaming not supported", "warning")
            return

        if streaming_enabled:
            return  # Already streaming

        try:
            streaming_enabled = True

            async def on_new_log(log_entry):
                """Callback for new log entries."""
                nonlocal logs_data
                if not streaming_enabled:  # Guard against updates after stop
                    return

                logs_data.insert(0, log_entry)  # Add to beginning
                # Keep only recent logs to prevent memory issues
                if len(logs_data) > 1000:
                    logs_data = logs_data[:1000]

                # Update UI if current view matches
                apply_filters()
                update_list()
                update_status()

            # Get the streaming task from server bridge
            streaming_task = await server_bridge.stream_logs_async(callback=on_new_log)

            state_manager.add_notification("Live log streaming started", "success")
            update_status()  # Update to show streaming indicator

        except Exception as e:
            logger.error(f"Failed to start log streaming: {e}")
            streaming_enabled = False
            streaming_task = None
            state_manager.add_notification(f"Streaming error: {str(e)}", "error")

    async def stop_log_streaming():
        """Stop real-time log streaming."""
        nonlocal streaming_enabled, streaming_task

        streaming_enabled = False

        if streaming_task and not streaming_task.done():
            # Use server bridge's stop method
            if server_bridge and hasattr(server_bridge, 'stop_log_stream_async'):
                try:
                    await server_bridge.stop_log_stream_async(streaming_task)
                except Exception as e:
                    logger.error(f"Error stopping log stream: {e}")
            else:
                # Direct cancellation fallback
                streaming_task.cancel()
                try:
                    await streaming_task
                except asyncio.CancelledError:
                    pass

        streaming_task = None
        state_manager.add_notification("Log streaming stopped", "info")
        update_status()  # Update to remove streaming indicator

    def toggle_streaming(_):
        """Toggle log streaming on/off."""
        if streaming_enabled:
            page.run_task(stop_log_streaming)
        else:
            page.run_task(start_log_streaming)

    # ---------------------- Enhanced UI Controls ------------------------------------ #
    status_text = ft.Text("Loading logs...", color=ft.Colors.OUTLINE, size=12)
    last_updated_text = ft.Text("Last updated: Never", size=12, color=ft.Colors.ON_SURFACE_VARIANT)

    # Enhanced search field with regex toggle
    def on_regex_toggle(e):
        nonlocal regex_search_enabled
        e.control.selected = not e.control.selected
        regex_search_enabled = e.control.selected
        e.control.update()
        apply_filters()
        update_list()
        update_status()
        update_pagination_controls()

    regex_toggle = ft.IconButton(
        icon=ft.Icons.SEARCH,
        tooltip="Toggle regex search",
        selected=False,
        on_click=on_regex_toggle,
    )

    search_field = ft.TextField(
        label="Search logs...",
        hint_text="Search by message, component, or level (supports regex)",
        prefix_icon=ft.Icons.SEARCH,
        suffix=ft.Row([
            regex_toggle,
            ft.IconButton(icon=ft.Icons.CLEAR, tooltip="Clear search", on_click=on_search_clear)
        ], tight=True, spacing=0),
        on_change=on_search_change,
        expand=True,
        filled=True,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        border_radius=12,
        content_padding=ft.Padding(16, 12, 16, 12),
        border_color=ft.Colors.OUTLINE_VARIANT,
        focused_border_color=ft.Colors.PRIMARY
    )

    # Enhanced filter buttons with Material Design 3 styling
    filter_buttons = [
        ft.FilledButton(
            "ALL",
            icon=ft.Icons.FILTER_LIST,
            on_click=create_filter_handler("ALL"),
            style=create_modern_button_style("primary", is_dark_theme, "filled"),
            tooltip="Show all logs"
        ),
        ft.OutlinedButton(
            "INFO",
            icon=ft.Icons.INFO,
            on_click=create_filter_handler("INFO"),
            style=create_modern_button_style("primary", is_dark_theme, "outlined")
        ),
        ft.OutlinedButton(
            "SUCCESS",
            icon=ft.Icons.CHECK_CIRCLE,
            on_click=create_filter_handler("SUCCESS"),
            style=create_modern_button_style("primary", is_dark_theme, "outlined")
        ),
        ft.OutlinedButton(
            "WARNING",
            icon=ft.Icons.WARNING,
            on_click=create_filter_handler("WARNING"),
            style=create_modern_button_style("primary", is_dark_theme, "outlined")
        ),
        ft.OutlinedButton(
            "ERROR",
            icon=ft.Icons.ERROR,
            on_click=create_filter_handler("ERROR"),
            style=create_modern_button_style("primary", is_dark_theme, "outlined")
        ),
        ft.OutlinedButton(
            "DEBUG",
            icon=ft.Icons.BUG_REPORT,
            on_click=create_filter_handler("DEBUG"),
            style=create_modern_button_style("primary", is_dark_theme, "outlined")
        ),
    ]

    # Component filter dropdown
    component_dropdown = ft.Dropdown(
        label="Component",
        value="ALL",
        options=[ft.dropdown.Option("ALL", "All Components")],
        width=150,
        on_change=lambda e: setattr(globals(), 'component_filter', e.control.value) or
                           setattr(pagination_config, 'current_page', 0) or
                           apply_filters() or update_list() or update_status() or update_pagination_controls()
    )

    # Date range controls
    date_from_field = ft.TextField(
        label="From Date",
        hint_text="YYYY-MM-DD",
        width=120,
        disabled=True
    )

    date_to_field = ft.TextField(
        label="To Date",
        hint_text="YYYY-MM-DD",
        width=120,
        disabled=True
    )

    date_filter_toggle = ft.Switch(
        label="Date Filter",
        value=False,
        on_change=lambda e: setattr(globals(), 'date_filter_enabled', e.control.value) or
                           setattr(date_from_field, 'disabled', not e.control.value) or
                           setattr(date_to_field, 'disabled', not e.control.value) or
                           date_from_field.update() or date_to_field.update()
    )

    logs_container = ft.Column(controls=[], expand=True, spacing=0, scroll=ft.ScrollMode.AUTO)

    # Pagination controls
    def on_first(_):
        pagination_config.current_page = 0; update_list(); update_status(); update_pagination_controls()
    def on_prev(_):
        if pagination_config.current_page > 0:
            pagination_config.current_page -= 1; update_list(); update_status(); update_pagination_controls()
    def on_next(_):
        total_pages = max(1, (len(filtered_logs_data) + pagination_config.page_size - 1) // pagination_config.page_size)
        if (pagination_config.current_page + 1) < total_pages:
            pagination_config.current_page += 1; update_list(); update_status(); update_pagination_controls()
    def on_last(_):
        total_pages = max(1, (len(filtered_logs_data) + pagination_config.page_size - 1) // pagination_config.page_size)
        pagination_config.current_page = max(0, total_pages - 1); update_list(); update_status(); update_pagination_controls()

    first_btn = ft.IconButton(icon=ft.Icons.FIRST_PAGE, tooltip="First Page", on_click=on_first, disabled=True)
    prev_btn = ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, tooltip="Previous Page", on_click=on_prev, disabled=True)
    next_btn = ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, tooltip="Next Page", on_click=on_next, disabled=True)
    last_btn = ft.IconButton(icon=ft.Icons.LAST_PAGE, tooltip="Last Page", on_click=on_last, disabled=True)
    page_info_text = ft.Text("Page 1 of 1", size=12, weight=ft.FontWeight.W_500)
    pagination_row = ft.Row([first_btn, prev_btn, page_info_text, next_btn, last_btn], spacing=5)

    # Enhanced action buttons with Material Design 3 styling
    # Enhanced loading indicator with Material Design 3 styling
    loading_indicator_ref = ft.Ref[ft.ProgressRing]()
    loading_indicator = ft.ProgressRing(
        ref=loading_indicator_ref,
        width=24,
        height=24,
        stroke_width=3,
        color=ft.Colors.PRIMARY,
        visible=False
    )

    action_buttons = ft.Row([
        ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Refresh Logs",
            on_click=on_refresh_logs,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.HOVERED: ft.Colors.PRIMARY_CONTAINER},
                color=ft.Colors.PRIMARY
            )
        ),
        ft.IconButton(
            icon=ft.Icons.DOWNLOAD,
            tooltip="Export Logs",
            on_click=show_export_dialog,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.HOVERED: ft.Colors.SECONDARY_CONTAINER},
                color=ft.Colors.SECONDARY
            )
        ),
        ft.IconButton(
            icon=ft.Icons.STOP_CIRCLE if streaming_enabled else ft.Icons.STREAM,
            tooltip="Stop Streaming" if streaming_enabled else "Toggle Live Streaming",
            on_click=toggle_streaming,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.HOVERED: ft.Colors.TERTIARY_CONTAINER},
                color=ft.Colors.ERROR if streaming_enabled else ft.Colors.TERTIARY
            )
        ),
        ft.IconButton(
            icon=ft.Icons.CLEAR_ALL,
            tooltip="Clear All Logs",
            on_click=on_clear_logs,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.HOVERED: ft.Colors.ERROR_CONTAINER},
                color=ft.Colors.ERROR
            )
        ),
        ft.Container(width=8),  # Spacer
        loading_indicator  # Add loading indicator to action row
    ], spacing=8)

    # Enhanced layout with Material Design 3 structure
    view = ft.Column([
        # Header section with enhanced styling
        ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.ARTICLE, size=28, color=ft.Colors.PRIMARY),
                    ft.Text("System Logs", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SURFACE)
                ], spacing=12),
                ft.Container(expand=True),
                action_buttons
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding(24, 20, 24, 16),
            bgcolor=ft.Colors.SURFACE,
            border_radius=ft.BorderRadius(16, 16, 0, 0)
        ),

        # Filter section with responsive design
        ft.Container(
            content=ft.ResponsiveRow([
                # Filter buttons - responsive layout
                ft.Column([
                    ft.Row(filter_buttons[:3], spacing=12, wrap=True),  # First row: ALL, INFO, SUCCESS
                    ft.Container(height=8),
                    ft.Row(filter_buttons[3:], spacing=12, wrap=True)   # Second row: WARNING, ERROR, DEBUG
                ], col={"sm": 12, "md": 8, "lg": 9}),

                # Additional controls - stacked on mobile, inline on desktop
                ft.Column([
                    ft.Row([
                        component_dropdown,
                        date_filter_toggle
                    ], spacing=12, wrap=True),
                    ft.Container(height=8),
                    ft.Row([
                        date_from_field,
                        date_to_field
                    ], spacing=8, wrap=True)
                ], col={"sm": 12, "md": 4, "lg": 3})
            ]),
            padding=ft.Padding(24, 0, 24, 16),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=0
        ),

        # Search section with responsive design
        ft.Container(
            content=ft.ResponsiveRow([
                # Search field - takes most space
                ft.Column([
                    search_field
                ], col={"sm": 12, "md": 9, "lg": 10}),

                # Search info - hidden on small screens
                ft.Column([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("🔍 Smart Search", size=11, color=ft.Colors.ON_SURFACE_VARIANT, italic=True),
                            ft.Text("300ms debounced", size=10, color=ft.Colors.OUTLINE, italic=True)
                        ], spacing=2),
                        visible=True  # Always visible but responsive
                    )
                ], col={"sm": 0, "md": 3, "lg": 2})
            ]),
            padding=ft.Padding(24, 0, 24, 16),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
        ),

        # Status and pagination section
        ft.Container(
            content=ft.Row([
                status_text,
                ft.Container(expand=True),
                last_updated_text
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding(24, 8, 24, 8),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST
        ),

        ft.Container(
            content=ft.Row([
                ft.Container(expand=True),
                pagination_row,
                ft.Container(expand=True)
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=ft.Padding(24, 8, 24, 16),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=ft.BorderRadius(0, 0, 16, 16)
        ),

        # Main content area with enhanced styling
        ft.Container(
            content=logs_container,
            expand=True,
            padding=ft.Padding(24, 16, 24, 24),
            bgcolor=ft.Colors.SURFACE,
            border_radius=0
        )
    ], expand=True, spacing=0)

    # State manager integration for reactive updates
    def setup_state_subscriptions():
        """Set up state manager subscriptions for reactive updates with dispose tracking (Comment 12)."""
        # Store subscription callbacks for later cleanup
        subscriptions = []

        # Subscribe to logs data changes from other views
        async def on_logs_updated(new_logs, old_logs):
            nonlocal logs_data
            if new_logs != logs_data:
                logs_data = new_logs
                # Update component filter dropdown with new data
                populate_component_filter()
                apply_filters()
                update_list()
                update_status()
                update_pagination_controls()

                # Show notification if logs were updated from external source
                if old_logs and len(new_logs) != len(old_logs):
                    state_manager.add_notification(
                        f"Logs updated: {len(new_logs)} entries ({abs(len(new_logs) - len(old_logs))} change)",
                        "info", auto_dismiss=3
                    )

        def on_loading_states(loading_states, _):
            """Handle loading state updates with enhanced UI feedback."""
            update_loading_indicators(loading_states)

            # Update search field state during search operations
            if search_field and hasattr(search_field, 'disabled'):
                search_field.disabled = loading_states.get("logs_search", False)
                # Safe update - only if control is attached to page
                if hasattr(search_field, 'page') and search_field.page:
                    search_field.update()

            # Update status text during loading operations (safe updates)
            if loading_states.get("logs_load", False):
                status_text.value = "Loading logs..."
                if hasattr(status_text, 'page') and status_text.page:
                    status_text.update()
            elif loading_states.get("logs_search", False):
                status_text.value = "Searching logs..."
                if hasattr(status_text, 'page') and status_text.page:
                    status_text.update()
            elif loading_states.get("logs_export", False):
                status_text.value = "Exporting logs..."
                if hasattr(status_text, 'page') and status_text.page:
                    status_text.update()
            elif loading_states.get("logs_clear", False):
                status_text.value = "Clearing logs..."
                if hasattr(status_text, 'page') and status_text.page:
                    status_text.update()

        def on_logs_events(event, _):
            """Handle logs event notifications."""
            if event:
                handle_logs_event(event)

        state_manager.subscribe_to_logs_async(on_logs_updated)
        subscriptions.append(('logs_async', on_logs_updated))

        # Subscribe to loading states
        state_manager.subscribe("loading_states", on_loading_states)
        subscriptions.append(('loading_states', on_loading_states))

        # Subscribe to notifications for logs events
        state_manager.subscribe("logs_events", on_logs_events)
        subscriptions.append(('logs_events', on_logs_events))

        return subscriptions

    def update_loading_indicators(loading_states: Dict[str, bool]):
        """Update UI loading indicators based on state manager."""
        # Update action buttons based on loading states
        if action_buttons.controls:
            for i, button in enumerate(action_buttons.controls):
                if isinstance(button, ft.IconButton):
                    if i == 0 and loading_states.get("logs_load", False):  # Refresh button
                        button.icon = ft.Icons.HOURGLASS_EMPTY
                    elif i == 1 and loading_states.get("logs_export", False):  # Export button
                        button.icon = ft.Icons.HOURGLASS_EMPTY
                    elif i == 3 and loading_states.get("logs_clear", False):  # Clear button
                        button.icon = ft.Icons.HOURGLASS_EMPTY
                    else:
                        # Reset to original icons
                        if i == 0:
                            button.icon = ft.Icons.REFRESH
                        elif i == 1:
                            button.icon = ft.Icons.DOWNLOAD
                        elif i == 2:
                            button.icon = ft.Icons.STOP_CIRCLE if streaming_enabled else ft.Icons.STREAM
                        elif i == 3:
                            button.icon = ft.Icons.CLEAR_ALL
                    button.update()

    def handle_logs_event(event: Dict[str, Any]):
        """Handle logs events from state manager."""
        if not event:
            return

        event_type = event.get('type')
        if event_type == 'logs_cleared':
            # Refresh the view when logs are cleared from another view
            page.run_task(load_logs_data_async)
        elif event_type == 'logs_updated':
            # Refresh when logs are updated from another source
            page.run_task(load_logs_data_async)

    def populate_component_filter():
        """Populate component filter dropdown with available components."""
        if logs_data:
            components = set()
            for log in logs_data:
                component = log.get('component', 'Unknown')
                if component:
                    components.add(component)

            options = [ft.dropdown.Option("ALL", "All Components")]
            for component in sorted(components):
                options.append(ft.dropdown.Option(component, component))

            component_dropdown.options = options
            # Safe update - only if control is attached to page
            if hasattr(component_dropdown, 'page') and component_dropdown.page:
                component_dropdown.update()

    # Expose manual trigger and setup
    def trigger_initial_load():
        page.run_task(load_logs_data_async)
    view.trigger_initial_load = trigger_initial_load

    # Set up state manager subscriptions with dispose tracking (Comment 12)
    subscriptions = setup_state_subscriptions()

    # Create dispose function for StateManager cleanup (Comment 12)
    def dispose():
        """Clean up StateManager subscriptions when view is disposed."""
        try:
            # Stop streaming if active
            if streaming_task and not streaming_task.done():
                streaming_task.cancel()

            # Unsubscribe from all tracked subscriptions
            for key, callback in subscriptions:
                if key == 'logs_async':
                    # For async subscriptions, use unsubscribe_async if it exists
                    if hasattr(state_manager, 'unsubscribe_logs_async'):
                        state_manager.unsubscribe_logs_async(callback)
                    else:
                        logger.debug("logs_async unsubscribe not available")
                else:
                    state_manager.unsubscribe(key, callback)

            logger.debug(f"Logs view disposed: cleaned up {len(subscriptions)} subscriptions")
        except Exception as e:
            logger.warning(f"Error during logs view disposal: {e}")

    # Kick off initial load (delayed to ensure page attachment)
    async def delayed_initial():
        await asyncio.sleep(0.05)
        await load_logs_data_async()
        # Populate component filter after initial load
        populate_component_filter()
    page.run_task(delayed_initial)

    return view, dispose

