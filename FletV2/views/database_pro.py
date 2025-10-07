#!/usr/bin/env python3
"""Professional Database Management View for Flet 0.28.3

This module provides a complete, production-ready database management interface
with full CRUD operations, search/filter, and export capabilities. Built following
Flet 0.28.3 best practices and async/sync integration patterns.

Key Features:
- ListView-based display for optimal performance
- Full CRUD operations (Create, Read, Update, Delete)
- Real-time search and filtering
- Export to CSV and JSON
- Neumorphic and glassmorphic styling
- Proper async/sync integration with run_in_executor

Architecture:
- All ServerBridge calls use asyncio.run_in_executor (methods are synchronous)
- Setup function waits for control attachment before updates
- Dispose function properly cancels background tasks
- No blocking operations in async context
"""

from __future__ import annotations

import asyncio
import csv
import io
import json
import os
import sys
from datetime import datetime
from typing import Any, Callable, Coroutine

import flet as ft

# Ensure proper path setup
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# UTF-8 solution for subprocess/console I/O
import Shared.utils.utf8_solution as _  # noqa: F401

from FletV2.theme import (
    create_glassmorphic_container,
    create_neumorphic_container,
    create_neumorphic_metric_card,
    themed_button,
)
from FletV2.utils.debug_setup import get_logger
from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.state_manager import StateManager
from FletV2.utils.user_feedback import show_error_message, show_success_message

logger = get_logger(__name__)

# Configuration Constants
DEFAULT_TABLE = "clients"
DEFAULT_TABLES = ["clients", "files", "logs", "backups", "settings"]
MAX_VISIBLE_RECORDS = 100
MAX_EXPORT_RECORDS = 10000
MAX_DISPLAY_LENGTH = 100  # Maximum characters to display for string values
SETUP_DELAY = 0.5  # Seconds to wait for control attachment
SENSITIVE_FIELDS = {"aes_key", "public_key", "private_key", "password", "secret", "token"}


def create_database_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    state_manager: StateManager | None = None,
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    """Create professional database management view.

    Args:
        server_bridge: Bridge to backend server (may be None if disconnected)
        page: Flet page instance
        state_manager: State manager instance (reserved for future use)

    Returns:
        Tuple of (main_container, dispose_func, setup_func)
    """
    logger.info("Initializing professional database view")
    print(f"🟧 [DATABASE_PRO] create_database_view CALLED")
    print(f"🟧 [DATABASE_PRO] server_bridge: {server_bridge is not None}")
    print(f"🟧 [DATABASE_PRO] page: {page is not None}")

    # ========================================================================
    # STATE VARIABLES
    # ========================================================================
    current_table = DEFAULT_TABLE
    available_tables: list[str] = DEFAULT_TABLES.copy()
    all_records: list[dict[str, Any]] = []
    filtered_records: list[dict[str, Any]] = []
    table_columns: list[str] = []
    search_query = ""

    db_stats = {
        "status": "Disconnected",
        "tables": 0,
        "total_records": 0,
        "size": "0 MB",
    }

    _setup_cancelled = False
    background_tasks: list[asyncio.Task] = []

    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================

    def get_active_bridge() -> ServerBridge | None:
        """Get active server bridge if available."""
        if server_bridge is None:
            return None
        return server_bridge if getattr(server_bridge, "real_server", None) else None

    def is_server_connected() -> bool:
        """Check if server is connected."""
        return get_active_bridge() is not None

    def is_control_attached(control: ft.Control) -> bool:
        """Check if control is attached to page."""
        return getattr(control, "page", None) is not None

    def stringify_value(value: Any) -> str:
        """Convert any value to display string with truncation for readability."""
        if value is None:
            return ""
        if isinstance(value, (bytes, bytearray)):
            hex_str = value.hex()
            return hex_str[:32] + "..." if len(hex_str) > 32 else hex_str
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")

        # Convert to string
        str_value = str(value)

        # Truncate long strings for display
        if len(str_value) > MAX_DISPLAY_LENGTH:
            return f"{str_value[:MAX_DISPLAY_LENGTH]}..."

        return str_value

    # ========================================================================
    # UI CONTROLS
    # ========================================================================

    # Status indicators
    status_text = ft.Text("Ready", size=14, color=ft.Colors.GREY_400)
    loading_ring = ft.ProgressRing(width=20, height=20, visible=False)

    # Database stats
    stat_status = ft.Text("Disconnected", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY)
    stat_tables = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
    stat_records = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
    stat_size = ft.Text("0 MB", size=20, weight=ft.FontWeight.BOLD)

    # Controls
    table_dropdown = ft.Dropdown(
        label="Select Table",
        value=current_table,
        width=200,
        options=[ft.dropdown.Option(text=t.title(), key=t) for t in DEFAULT_TABLES],
    )

    search_field = ft.TextField(
        label="Search records",
        hint_text="Type to filter...",
        prefix_icon=ft.Icons.SEARCH,
        width=300,
        on_change=lambda e: None,  # Will be set later
    )

    # Records display - two view modes: cards (ListView) and table (DataTable)
    view_mode = "cards"  # "cards" or "table"

    # Provide a fallback height to ensure visibility even if parent doesn't expand fully
    # Use a Column instead of ListView to avoid attachment/height quirks
    # NO scroll here - parent main_layout handles scrolling to avoid nested scroll conflicts
    records_listview = ft.Column(
        spacing=10,
        tight=False,
    )
    # Provide an initial placeholder so the section is never visually empty
    records_listview.controls.append(
        ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.DATASET, size=40, color=ft.Colors.GREY_500),
                    ft.Text("Loading database records...", size=14, color=ft.Colors.GREY_500),
                    ft.Text("Select a table to view data", size=12, color=ft.Colors.GREY_400),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(0, 28, 0, 28),
        )
    )

    # Container for cards view
    cards_view_container = ft.Container(
        content=records_listview,
        padding=ft.Padding(8, 8, 8, 24),
        visible=True,
    )

    # DataTable for table view mode
    # CRITICAL: DataTable requires at least one column - initialize with placeholder
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Loading...", weight=ft.FontWeight.BOLD, size=13))
        ],
        rows=[
            ft.DataRow(cells=[ft.DataCell(ft.Text("Initializing database view...", color=ft.Colors.GREY_500))])
        ],
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE)),
        border_radius=8,
        horizontal_lines=ft.BorderSide(1, ft.Colors.with_opacity(0.05, ft.Colors.OUTLINE)),
        heading_row_height=48,
        data_row_min_height=40,
        data_row_max_height=60,
        column_spacing=20,
        show_checkbox_column=False,
    )

    # Container to hold current view mode
    # NO scroll here - parent main_layout handles scrolling to avoid nested scroll conflicts
    table_view_container = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=data_table,
                    border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE)),
                    border_radius=8,
                    padding=10,
                ),
            ],
            spacing=10,
        ),
        visible=False,
    )

    # Single switcher container to avoid Stack overlay quirks
    # NOTE: ft.Container does NOT support min_height in Flet 0.28.3 (only height/width)
    views_switcher = ft.Container(content=cards_view_container)

    # Action buttons
    btn_add = themed_button("Add Record", None, "filled", ft.Icons.ADD)
    btn_refresh = themed_button("Refresh", None, "outlined", ft.Icons.REFRESH)
    btn_export_csv = themed_button("Export CSV", None, "outlined", ft.Icons.FILE_DOWNLOAD)
    btn_export_json = themed_button("Export JSON", None, "outlined", ft.Icons.CODE)

    # View mode toggle
    btn_view_cards = ft.IconButton(
        icon=ft.Icons.VIEW_MODULE,
        tooltip="Card View",
        selected=True,
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.ON_SURFACE_VARIANT, ft.ControlState.SELECTED: ft.Colors.PRIMARY}
        ),
    )
    btn_view_table = ft.IconButton(
        icon=ft.Icons.TABLE_CHART,
        tooltip="Table View",
        selected=False,
        style=ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: ft.Colors.ON_SURFACE_VARIANT, ft.ControlState.SELECTED: ft.Colors.PRIMARY}
        ),
    )

    # Initialize button states
    btn_add.disabled = not is_server_connected()

    # ========================================================================
    # UI UPDATE FUNCTIONS
    # ========================================================================

    def _force_records_area_update() -> None:
        """Aggressively update nested controls to ensure rendering (DB_FIX)."""
        try:
            print("🟪 [DB_FIX] Forcing nested updates for records area")
            # Update only the active view's controls (content swapping handles visibility)
            if view_mode == "cards" and is_control_attached(records_listview):
                records_listview.update()
                if is_control_attached(cards_view_container):
                    cards_view_container.update()
            elif view_mode == "table" and is_control_attached(data_table):
                data_table.update()
                if is_control_attached(table_view_container):
                    table_view_container.update()

            # Update parent containers
            if is_control_attached(views_switcher):
                views_switcher.update()
            if is_control_attached(records_section):
                records_section.update()
            if hasattr(page, "update"):
                page.update()
        except Exception as _e:  # noqa: F841 - best-effort fix
            # Avoid breaking the flow if an update fails mid-tree
            pass

    def update_status(message: str, color: str | None = None, loading: bool = False) -> None:
        """Update status text and loading indicator."""
        status_text.value = message
        if color:
            status_text.color = color
        loading_ring.visible = loading

        if is_control_attached(status_text):
            status_text.update()
        if is_control_attached(loading_ring):
            loading_ring.update()

    def update_db_stats_ui() -> None:
        """Update database statistics display."""
        if not all(is_control_attached(c) for c in [stat_status, stat_tables, stat_records, stat_size]):
            logger.debug("Database stats controls not attached, skipping update")
            return

        stat_status.value = db_stats["status"]
        stat_tables.value = str(db_stats["tables"])
        stat_records.value = str(db_stats["total_records"])
        stat_size.value = db_stats["size"]

        # Color code status
        status_lower = db_stats["status"].lower()
        if "connected" in status_lower:
            stat_status.color = ft.Colors.GREEN
        elif "error" in status_lower:
            stat_status.color = ft.Colors.ERROR
        else:
            stat_status.color = ft.Colors.GREY

        for ctrl in [stat_status, stat_tables, stat_records, stat_size]:
            ctrl.update()

        # Update button states
        btn_add.disabled = not is_server_connected()
        if is_control_attached(btn_add):
            btn_add.update()

    def update_table_dropdown_ui() -> None:
        """Update table dropdown options and state."""
        if not is_control_attached(table_dropdown):
            logger.debug("Table dropdown not attached, skipping update")
            return

        table_dropdown.options = [
            ft.dropdown.Option(text=t.title(), key=t) for t in available_tables
        ]
        table_dropdown.value = current_table if current_table in available_tables else available_tables[0]
        table_dropdown.disabled = not is_server_connected()
        table_dropdown.update()

    def build_record_card(record: dict[str, Any], index: int) -> ft.Container:
        """Build a card UI for a single record."""
        display_keys = table_columns or list(record.keys())
        rows: list[ft.Control] = []

        # Build field rows (limit to 10 fields for readability)
        shown = 0
        for key in display_keys:
            if not isinstance(key, str) or key.lower() in SENSITIVE_FIELDS:
                continue

            value = stringify_value(record.get(key))
            if not value and value != "0":
                continue

            rows.append(
                ft.Row(
                    [
                        ft.Text(
                            key.replace("_", " ").title() + ":",
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            width=140,
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Text(value, size=12, selectable=True, expand=True),
                    ],
                    spacing=8,
                )
            )
            shown += 1
            if shown >= 10:
                break

        if not rows:
            rows.append(ft.Text("No displayable fields", size=12, color=ft.Colors.GREY_500, italic=True))

        # Action buttons
        actions_row = None
        if is_server_connected():
            actions_row = ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.EDIT_OUTLINED,
                        tooltip="Edit record",
                        icon_size=18,
                        on_click=lambda _e, r=record: edit_record_dialog(r),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        tooltip="Delete record",
                        icon_size=18,
                        icon_color=ft.Colors.ERROR,
                        on_click=lambda _e, r=record: delete_record_dialog(r),
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            )

        # Card header
        header = ft.Row(
            [
                ft.Icon(ft.Icons.ARTICLE_OUTLINED, size=16, color=ft.Colors.PRIMARY),
                ft.Text(
                    f"{current_table.title()} #{index + 1}",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            spacing=8,
        )

        card_content = [header, ft.Divider(height=1, thickness=0.5), ft.Column(rows, spacing=4, tight=True)]
        if actions_row:
            card_content.append(actions_row)

        return ft.Container(
            content=ft.Column(card_content, spacing=10, tight=True),
            padding=ft.Padding(14, 12, 14, 12),
            border_radius=12,
            # SURFACE_VARIANT is not available in current Flet version; use SURFACE as base
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.SURFACE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.OUTLINE)),
        )

    def refresh_records_display() -> None:
        """Refresh the records list (Column with cards)."""
        print(f"🟩 [REFRESH_DISPLAY] ENTERED - filtered_records: {len(filtered_records)}")

        if not is_control_attached(records_listview):
            print(f"🟩 [REFRESH_DISPLAY] records_listview NOT ATTACHED - skipping")
            logger.debug("Records list not attached, skipping refresh")
            return

        print(f"🟩 [REFRESH_DISPLAY] records_listview IS ATTACHED - clearing controls")
        records_listview.controls.clear()

        # CRITICAL: Always ensure non-empty controls to prevent gray screen
        if not filtered_records:
            # Empty state
            print(f"🟩 [REFRESH_DISPLAY] NO RECORDS - showing empty state")
            message = "No records found" if is_server_connected() else "Server not connected"
            records_listview.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.INBOX_OUTLINED, size=48, color=ft.Colors.GREY_400),
                            ft.Text(message, size=16, color=ft.Colors.GREY_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    padding=ft.Padding(0, 40, 0, 40),
                    alignment=ft.alignment.center,
                )
            )
        else:
            # Summary text
            print(f"🟩 [REFRESH_DISPLAY] HAS RECORDS - building {len(filtered_records)} cards")
            count_text = f"Showing {min(len(filtered_records), MAX_VISIBLE_RECORDS)} of {len(filtered_records)} records"
            records_listview.controls.append(
                ft.Text(count_text, size=13, color=ft.Colors.ON_SURFACE_VARIANT, weight=ft.FontWeight.W_500)
            )

            # Record cards
            for idx, record in enumerate(filtered_records[:MAX_VISIBLE_RECORDS]):
                records_listview.controls.append(build_record_card(record, idx))

            # Overflow indicator
            if len(filtered_records) > MAX_VISIBLE_RECORDS:
                records_listview.controls.append(
                    ft.Text(
                        f"...and {len(filtered_records) - MAX_VISIBLE_RECORDS} more records",
                        size=12,
                        color=ft.Colors.GREY_500,
                        italic=True,
                    )
                )

        # CRITICAL: Final validation - NEVER render empty controls (prevents gray screen)
        if not records_listview.controls:
            print(f"🟥 [REFRESH_DISPLAY] CRITICAL: Empty controls detected, adding fallback content!")
            records_listview.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.ERROR_OUTLINE, size=48, color=ft.Colors.ERROR),
                            ft.Text("Error: No content to display", size=16, color=ft.Colors.ERROR),
                            ft.Text("Please refresh or contact support", size=12, color=ft.Colors.GREY_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    padding=ft.Padding(0, 40, 0, 40),
                    alignment=ft.alignment.center,
                )
            )

        print(f"🟩 [REFRESH_DISPLAY] About to call records_listview.update() - controls count: {len(records_listview.controls)}")
        records_listview.update()
        print(f"🟩 [REFRESH_DISPLAY] records_listview.update() COMPLETED")
        _force_records_area_update()

    def refresh_data_table() -> None:
        """Refresh the DataTable display."""
        if not is_control_attached(data_table):
            logger.debug("DataTable not attached, skipping refresh")
            return

        # Clear existing table
        data_table.columns.clear()
        data_table.rows.clear()

        # CRITICAL: Always ensure non-empty columns/rows to prevent gray screen
        if not filtered_records or not table_columns:
            # Empty state - show message in table
            data_table.columns.append(ft.DataColumn(ft.Text("No Data", weight=ft.FontWeight.BOLD)))
            data_table.rows.append(
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text("No records to display", color=ft.Colors.GREY_500))]
                )
            )
        else:
            # Build columns (limit to avoid overflow)
            display_columns = [col for col in table_columns if col.lower() not in SENSITIVE_FIELDS][:8]

            for col_name in display_columns:
                data_table.columns.append(
                    ft.DataColumn(
                        ft.Text(col_name.replace("_", " ").title(), weight=ft.FontWeight.BOLD, size=13)
                    )
                )

            # Add action column
            if is_server_connected():
                data_table.columns.append(ft.DataColumn(ft.Text("Actions", weight=ft.FontWeight.BOLD, size=13)))

            # Build rows (limit to prevent performance issues)
            for record in filtered_records[:MAX_VISIBLE_RECORDS]:
                cells = []

                for col_name in display_columns:
                    value = stringify_value(record.get(col_name))
                    # Truncate long values
                    if len(value) > 50:
                        value = value[:47] + "..."
                    cells.append(ft.DataCell(ft.Text(value, size=12, selectable=True)))

                # Add action buttons
                if is_server_connected():
                    action_cell = ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=16,
                                    tooltip="Edit",
                                    on_click=lambda _e, r=record: edit_record_dialog(r),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=16,
                                    icon_color=ft.Colors.ERROR,
                                    tooltip="Delete",
                                    on_click=lambda _e, r=record: delete_record_dialog(r),
                                ),
                            ],
                            spacing=4,
                        )
                    )
                    cells.append(action_cell)

                data_table.rows.append(ft.DataRow(cells=cells))

        # CRITICAL: Final validation - DataTable MUST have columns and rows (prevents gray screen)
        if not data_table.columns:
            print(f"🟥 [REFRESH_TABLE] CRITICAL: Empty columns detected, adding fallback!")
            data_table.columns.append(ft.DataColumn(ft.Text("Error", weight=ft.FontWeight.BOLD, color=ft.Colors.ERROR)))
        if not data_table.rows:
            print(f"🟥 [REFRESH_TABLE] CRITICAL: Empty rows detected, adding fallback!")
            data_table.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("No data available", color=ft.Colors.GREY_500))])
            )

        data_table.update()

    def toggle_view_mode(new_mode: str) -> None:
        """Toggle between cards and table view modes."""
        nonlocal view_mode

        if view_mode == new_mode:
            return

        view_mode = new_mode

        # Update button states
        btn_view_cards.selected = (new_mode == "cards")
        btn_view_table.selected = (new_mode == "table")

        # Swap content in switcher to avoid overlay issues
        is_cards = (new_mode == "cards")
        views_switcher.content = cards_view_container if is_cards else table_view_container
        if is_control_attached(views_switcher):
            views_switcher.update()

        # Refresh appropriate view
        if is_cards:
            refresh_records_display()
            if is_control_attached(cards_view_container):
                cards_view_container.update()
        else:
            refresh_data_table()
            if is_control_attached(table_view_container):
                table_view_container.update()

        # Update view mode buttons
        if is_control_attached(btn_view_cards):
            btn_view_cards.update()
        if is_control_attached(btn_view_table):
            btn_view_table.update()

        logger.info(f"View mode changed to: {new_mode}")

    def apply_search_filter() -> None:
        """Apply search filter to records."""
        nonlocal filtered_records

        print(f"🟨 [SEARCH_FILTER] ENTERED - all_records: {len(all_records)}, search_query: '{search_query}'")

        if not search_query.strip():
            filtered_records = all_records.copy()
        else:
            query_lower = search_query.lower()
            filtered_records = [
                record
                for record in all_records
                if any(query_lower in stringify_value(v).lower() for v in record.values())
            ]

        print(f"🟨 [SEARCH_FILTER] filtered_records: {len(filtered_records)}, view_mode: {view_mode}")

        # Refresh the active view
        if view_mode == "cards":
            print(f"🟨 [SEARCH_FILTER] Calling refresh_records_display()")
            refresh_records_display()
        else:
            print(f"🟨 [SEARCH_FILTER] Calling refresh_data_table()")
            refresh_data_table()

        # Update status
        if search_query.strip():
            msg = f"Found {len(filtered_records)} matching records"
            color = ft.Colors.BLUE if filtered_records else ft.Colors.ORANGE
        else:
            msg = f"Loaded {len(filtered_records)} records"
            color = ft.Colors.GREEN if filtered_records else ft.Colors.GREY

        print(f"🟨 [SEARCH_FILTER] Updating status: '{msg}'")
        update_status(msg, color, False)

    # ========================================================================
    # DATA LOADING (ASYNC WITH run_in_executor)
    # ========================================================================

    async def load_database_stats() -> None:
        """Load database statistics from server."""
        nonlocal db_stats

        if not is_server_connected():
            db_stats = {"status": "Disconnected", "tables": 0, "total_records": 0, "size": "0 MB"}
            update_db_stats_ui()
            return

        try:
            update_status("Loading database info...", ft.Colors.BLUE, True)
            bridge = get_active_bridge()
            if bridge is None:
                db_stats = {"status": "Disconnected", "tables": 0, "total_records": 0, "size": "0 MB"}
                return

            # SIMPLIFIED: Use basic client/file counts instead of complex database health checks
            loop = asyncio.get_running_loop()

            # Get simple counts without database health checks (which cause freezing)
            # Note: get_clients() and get_files() return lists directly, not wrapped in dicts
            clients_result: list[dict[str, Any]] = await loop.run_in_executor(None, bridge.get_clients)
            files_result: list[dict[str, Any]] = await loop.run_in_executor(None, bridge.get_files)

            client_count = len(clients_result) if clients_result else 0
            file_count = len(files_result) if files_result else 0

            db_stats = {
                "status": "Connected",
                "tables": 2,  # clients and files
                "total_records": client_count + file_count,
                "size": "N/A"  # Skip size calculation to avoid database locks
            }
            logger.info(f"Database stats loaded: {db_stats}")

        except Exception as e:
            logger.exception(f"Error loading database stats: {e}")
            db_stats["status"] = f"Error: {e}"
            db_stats["tables"] = 0
            db_stats["total_records"] = 0
            db_stats["size"] = "0 MB"

        finally:
            update_status("Ready", ft.Colors.GREY_400, False)
            update_db_stats_ui()

    async def load_table_names() -> None:
        """Load available table names from server."""
        nonlocal available_tables

        if not is_server_connected():
            available_tables = DEFAULT_TABLES.copy()
            update_table_dropdown_ui()
            return

        try:
            update_status("Loading tables...", ft.Colors.BLUE, True)

            # SIMPLIFIED: Use fixed table list instead of querying database schema
            # Querying schema can cause database locks in multi-threaded environment
            available_tables = DEFAULT_TABLES.copy()
            logger.info(f"Using default tables: {available_tables}")

        except Exception as e:
            logger.exception(f"Error loading table names: {e}")
            available_tables = DEFAULT_TABLES.copy()

        finally:
            update_status("Ready", ft.Colors.GREY_400, False)
            update_table_dropdown_ui()

    async def load_table_data() -> None:
        """Load data for currently selected table."""
        nonlocal all_records, filtered_records, table_columns

        if not is_server_connected():
            all_records = []
            filtered_records = []
            table_columns = []
            refresh_records_display()
            return

        try:
            update_status(f"Loading {current_table}...", ft.Colors.BLUE, True)
            bridge = get_active_bridge()
            if bridge is None:
                all_records = []
                table_columns = []
                return

            # CRITICAL: Use run_in_executor for sync ServerBridge method
            loop = asyncio.get_running_loop()
            print(f"🟧 [LOAD_TABLE] About to call get_table_data for '{current_table}'")
            result = await loop.run_in_executor(None, bridge.get_table_data, current_table)
            print(f"🟧 [LOAD_TABLE] get_table_data returned: {result.get('success')}")

            if result.get("success") and result.get("data"):
                data = result["data"]
                table_columns = data.get("columns", [])
                all_records = data.get("rows", [])
                print(f"🟧 [LOAD_TABLE] SUCCESS! Loaded {len(all_records)} records, {len(table_columns)} columns")
                logger.info(f"Loaded {len(all_records)} records from {current_table}")
            else:
                error = result.get("error", "Unknown error")
                print(f"🟧 [LOAD_TABLE] FAILED: {error}")
                logger.warning(f"Failed to load table data: {error}")
                all_records = []
                table_columns = []

        except Exception as e:
            print(f"🟧 [LOAD_TABLE] EXCEPTION: {e}")
            logger.exception(f"Error loading table data: {e}")
            all_records = []
            table_columns = []

        finally:
            print(f"🟧 [LOAD_TABLE] Finally block - applying search filter")
            print(f"🟧 [LOAD_TABLE] all_records count: {len(all_records)}, filtered_records count: {len(filtered_records)}")
            apply_search_filter()
            print(f"🟧 [LOAD_TABLE] After apply_search_filter - filtered_records count: {len(filtered_records)}")
            update_status("Ready", ft.Colors.GREY_400, False)
            _force_records_area_update()

    # ========================================================================
    # EVENT HANDLERS
    # ========================================================================

    def on_table_change(e: ft.ControlEvent) -> None:
        """Handle table selection change."""
        nonlocal current_table, search_query

        current_table = e.control.value or DEFAULT_TABLE
        search_query = ""
        search_field.value = ""

        if is_control_attached(search_field):
            search_field.update()

        # Reload data for new table
        page.run_task(load_table_data)

    def on_search_change(e: ft.ControlEvent) -> None:
        """Handle search field change."""
        nonlocal search_query
        search_query = e.control.value or ""
        apply_search_filter()

    def on_refresh_click(e: ft.ControlEvent) -> None:
        """Handle refresh button click."""
        page.run_task(load_database_stats)
        page.run_task(load_table_names)
        page.run_task(load_table_data)

    # ========================================================================
    # CRUD OPERATIONS
    # ========================================================================

    def add_record_dialog(e: ft.ControlEvent) -> None:
        """Show dialog to add new record."""
        if not is_server_connected():
            show_error_message(page, "Server not connected")
            return

        # Get editable columns (exclude ID, auto-generated fields)
        editable_cols = [col for col in table_columns if col.lower() not in {"id", "uuid", "created_at"}]

        if not editable_cols:
            show_error_message(page, "No editable columns in this table")
            return

        # Create input fields
        input_fields: dict[str, ft.TextField] = {}
        for col in editable_cols:
            input_fields[col] = ft.TextField(
                label=col.replace("_", " ").title(),
                hint_text=f"Enter {col}",
            )

        dialog = ft.AlertDialog(
            title=ft.Text(f"Add Record to {current_table.title()}"),
            content=ft.Container(
                content=ft.Column(
                    list(input_fields.values()),
                    scroll="auto",
                    tight=True,
                ),
                width=400,
                height=min(400, len(editable_cols) * 80),
            ),
        )

        async def save_record() -> None:
            """Save new record to database."""
            try:
                update_status("Saving record...", ft.Colors.BLUE, True)

                # Build record data
                record_data = {col: field.value or None for col, field in input_fields.items()}

                bridge = get_active_bridge()
                if bridge is None:
                    show_error_message(page, "Server disconnected")
                    return

                # CRITICAL: Use run_in_executor for sync ServerBridge method
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, bridge.add_table_record, current_table, record_data)

                if result.get("success"):
                    show_success_message(page, "Record added successfully")
                    page.close(dialog)
                    await load_table_data()
                else:
                    error = result.get("error", "Unknown error")
                    show_error_message(page, f"Failed to add record: {error}")

            except Exception as ex:
                logger.exception(f"Error adding record: {ex}")
                show_error_message(page, f"Error: {ex}")

            finally:
                update_status("Ready", ft.Colors.GREY_400, False)

        dialog.actions = [
            ft.TextButton("Cancel", on_click=lambda _: page.close(dialog)),
            ft.FilledButton("Add", on_click=lambda _: page.run_task(save_record)),
        ]

        page.open(dialog)

    def edit_record_dialog(record: dict[str, Any]) -> None:
        """Show dialog to edit existing record."""
        if not is_server_connected():
            show_error_message(page, "Server not connected")
            return

        # Get editable columns
        editable_cols = [col for col in table_columns if col.lower() not in {"id", "uuid"}]

        if not editable_cols:
            show_error_message(page, "No editable columns in this table")
            return

        # Create input fields with current values
        input_fields: dict[str, ft.TextField] = {}
        for col in editable_cols:
            input_fields[col] = ft.TextField(
                label=col.replace("_", " ").title(),
                value=stringify_value(record.get(col, "")),
            )

        record_id = record.get("id") or record.get("ID") or "unknown"

        dialog = ft.AlertDialog(
            title=ft.Text(f"Edit Record #{record_id}"),
            content=ft.Container(
                content=ft.Column(
                    list(input_fields.values()),
                    scroll="auto",
                    tight=True,
                ),
                width=400,
                height=min(400, len(editable_cols) * 80),
            ),
        )

        async def save_changes() -> None:
            """Save changes to record."""
            try:
                update_status("Updating record...", ft.Colors.BLUE, True)

                # Build updated record (preserve all original fields, update edited ones)
                updated_record = dict(record)
                for col, field in input_fields.items():
                    updated_record[col] = field.value or None

                bridge = get_active_bridge()
                if bridge is None:
                    show_error_message(page, "Server disconnected")
                    return

                # CRITICAL: Use run_in_executor for sync ServerBridge method
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, bridge.update_table_record, current_table, updated_record)

                if result.get("success"):
                    show_success_message(page, "Record updated successfully")
                    page.close(dialog)
                    await load_table_data()
                else:
                    error = result.get("error", "Unknown error")
                    show_error_message(page, f"Failed to update record: {error}")

            except Exception as ex:
                logger.exception(f"Error updating record: {ex}")
                show_error_message(page, f"Error: {ex}")

            finally:
                update_status("Ready", ft.Colors.GREY_400, False)

        dialog.actions = [
            ft.TextButton("Cancel", on_click=lambda _: page.close(dialog)),
            ft.FilledButton("Save", on_click=lambda _: page.run_task(save_changes)),
        ]

        page.open(dialog)

    def delete_record_dialog(record: dict[str, Any]) -> None:
        """Show confirmation dialog to delete record."""
        if not is_server_connected():
            show_error_message(page, "Server not connected")
            return

        record_id = record.get("id") or record.get("ID")
        if record_id is None:
            show_error_message(page, "Record has no ID, cannot delete")
            return

        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Deletion"),
            content=ft.Text(
                f"Are you sure you want to delete record #{record_id}?\n\nThis action cannot be undone.",
                selectable=True,
            ),
        )

        async def confirm_delete() -> None:
            """Delete the record."""
            try:
                update_status("Deleting record...", ft.Colors.BLUE, True)

                bridge = get_active_bridge()
                if bridge is None:
                    show_error_message(page, "Server disconnected")
                    return

                # CRITICAL: Use run_in_executor for sync ServerBridge method
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, bridge.delete_table_record, current_table, record_id)

                if result.get("success"):
                    show_success_message(page, "Record deleted successfully")
                    page.close(dialog)
                    await load_table_data()
                else:
                    error = result.get("error", "Unknown error")
                    show_error_message(page, f"Failed to delete record: {error}")

            except Exception as ex:
                logger.exception(f"Error deleting record: {ex}")
                show_error_message(page, f"Error: {ex}")

            finally:
                update_status("Ready", ft.Colors.GREY_400, False)

        dialog.actions = [
            ft.TextButton("Cancel", on_click=lambda _: page.close(dialog)),
            ft.FilledButton(
                "Delete",
                on_click=lambda _: page.run_task(confirm_delete),
                style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR),
            ),
        ]

        page.open(dialog)

    # ========================================================================
    # EXPORT FUNCTIONALITY
    # ========================================================================

    def export_data(format_type: str) -> None:
        """Export filtered records to file."""
        if not filtered_records:
            show_error_message(page, "No data to export")
            return

        async def do_export() -> None:
            """Perform the export operation."""
            try:
                update_status(f"Exporting to {format_type.upper()}...", ft.Colors.BLUE, True)

                # Prepare data
                columns = table_columns or list(filtered_records[0].keys())
                records_to_export = filtered_records[:MAX_EXPORT_RECORDS]

                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{current_table}_{timestamp}.{format_type}"
                filepath = os.path.join(_repo_root, filename)

                # Export based on format
                if format_type == "csv":
                    with open(filepath, "w", encoding="utf-8", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(columns)
                        for record in records_to_export:
                            writer.writerow([stringify_value(record.get(col, "")) for col in columns])
                else:  # json
                    export_data = [
                        {col: stringify_value(record.get(col, "")) for col in columns}
                        for record in records_to_export
                    ]
                    with open(filepath, "w", encoding="utf-8") as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)

                show_success_message(page, f"Exported {len(records_to_export)} records to {filename}")
                logger.info(f"Exported {len(records_to_export)} records to {filepath}")

            except Exception as ex:
                logger.exception(f"Export error: {ex}")
                show_error_message(page, f"Export failed: {ex}")

            finally:
                update_status("Ready", ft.Colors.GREY_400, False)

        page.run_task(do_export)

    # ========================================================================
    # UI LAYOUT ASSEMBLY
    # ========================================================================

    # Stats cards
    stats_row = ft.ResponsiveRow(
        [
            ft.Container(
                content=create_neumorphic_metric_card(
                    ft.Column(
                        [
                            ft.Row([ft.Icon(ft.Icons.STORAGE, size=24), ft.Text("Status", size=14)]),
                            stat_status,
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    intensity="pronounced",
                ),
                col={"sm": 12, "md": 6, "lg": 3},
            ),
            ft.Container(
                content=create_neumorphic_metric_card(
                    ft.Column(
                        [
                            ft.Row([ft.Icon(ft.Icons.TABLE_CHART, size=24), ft.Text("Tables", size=14)]),
                            stat_tables,
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    intensity="pronounced",
                ),
                col={"sm": 12, "md": 6, "lg": 3},
            ),
            ft.Container(
                content=create_neumorphic_metric_card(
                    ft.Column(
                        [
                            ft.Row([ft.Icon(ft.Icons.DATASET, size=24), ft.Text("Records", size=14)]),
                            stat_records,
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    intensity="pronounced",
                ),
                col={"sm": 12, "md": 6, "lg": 3},
            ),
            ft.Container(
                content=create_neumorphic_metric_card(
                    ft.Column(
                        [
                            ft.Row([ft.Icon(ft.Icons.FOLDER, size=24), ft.Text("Size", size=14)]),
                            stat_size,
                        ],
                        spacing=8,
                        tight=True,
                    ),
                    intensity="pronounced",
                ),
                col={"sm": 12, "md": 6, "lg": 3},
            ),
        ]
    )

    # Controls bar - SIMPLIFIED (no glassmorphic wrapper for debugging)
    controls_bar = ft.Container(
        content=ft.Row(
            [
                table_dropdown,
                search_field,
                ft.Container(expand=True),
                loading_ring,
                status_text,
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor=ft.Colors.SURFACE,  # SURFACE_VARIANT doesn't exist in Flet 0.28.3
        border_radius=8,
        padding=12,
    )

    # Actions bar
    actions_bar = ft.Row(
        [
            btn_add,
            btn_refresh,
            btn_export_csv,
            btn_export_json,
            ft.Container(expand=True),  # Spacer
            ft.VerticalDivider(width=1, thickness=1, color=ft.Colors.OUTLINE_VARIANT),
            ft.Text("View:", size=13, color=ft.Colors.ON_SURFACE_VARIANT),
            btn_view_cards,
            btn_view_table,
        ],
        spacing=12,
        alignment=ft.MainAxisAlignment.START,
    )

    # Records section - SIMPLIFIED (no neumorphic wrapper for debugging)
    records_section = ft.Container(
        content=ft.Column(
            [
                ft.Text("Database Records", size=24, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Full CRUD operations with search and export capabilities",
                    size=13,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Divider(height=1, thickness=0.5, color=ft.Colors.OUTLINE_VARIANT),
                # Single container switches between cards/table views
                views_switcher,
            ],
            spacing=14,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        ),
        bgcolor=ft.Colors.SURFACE,  # SURFACE_VARIANT doesn't exist in Flet 0.28.3
        border_radius=8,
        padding=16,
    )

    # Main layout - using ListView for automatic scrolling
    main_layout = ft.ListView(
        controls=[
            ft.Text("Database Management", size=32, weight=ft.FontWeight.BOLD),
            stats_row,
            controls_bar,
            actions_bar,
            records_section,
        ],
        spacing=20,
        padding=ft.Padding(20, 20, 20, 20),
        expand=1,  # Fills available space
    )

    # Main container wraps ListView - NO styling to isolate layout issues
    main_container = ft.Container(
        content=main_layout,
    )

    # ========================================================================
    # WIRE UP EVENT HANDLERS
    # ========================================================================

    table_dropdown.on_change = on_table_change
    search_field.on_change = on_search_change
    btn_add.on_click = add_record_dialog
    btn_refresh.on_click = on_refresh_click
    btn_export_csv.on_click = lambda _: export_data("csv")
    btn_export_json.on_click = lambda _: export_data("json")
    btn_view_cards.on_click = lambda _: toggle_view_mode("cards")
    btn_view_table.on_click = lambda _: toggle_view_mode("table")

    # ========================================================================
    # LIFECYCLE FUNCTIONS
    # ========================================================================

    async def setup() -> None:
        """Setup function - load initial data after attachment."""
        nonlocal _setup_cancelled

        print(f"🟧 [DATABASE_PRO] setup() ENTERED")
        print(f"🟧 [DATABASE_PRO] _setup_cancelled = {_setup_cancelled}")
        logger.info("Starting database view setup")

        try:
            # Check cancellation before proceeding
            if _setup_cancelled:
                print(f"🟧 [DATABASE_PRO] Setup cancelled before start, exiting")
                logger.info("Setup cancelled before start")
                return

            print(f"🟧 [DATABASE_PRO] About to sleep for {SETUP_DELAY}s")
            # CRITICAL: Wait for control attachment to page
            logger.debug(f"Waiting {SETUP_DELAY}s for control attachment...")
            await asyncio.sleep(SETUP_DELAY)

            print(f"🟧 [DATABASE_PRO] Sleep completed, checking cancellation again")
            if _setup_cancelled:
                print(f"🟧 [DATABASE_PRO] Setup cancelled after delay, exiting")
                logger.info("Setup cancelled after delay")
                return

            # Load data from server FIRST (before UI updates)
            print(f"🟧 [DATABASE_PRO] About to load database stats")
            logger.debug("Loading database stats...")
            await load_database_stats()

            print(f"🟧 [DATABASE_PRO] About to load table names")
            logger.debug("Loading table names...")
            await load_table_names()

            print(f"🟧 [DATABASE_PRO] About to load table data")
            logger.debug("Loading table data...")
            await load_table_data()

            # THEN update UI with loaded data
            print(f"🟧 [DATABASE_PRO] Data loaded, now updating UI")
            logger.debug("Updating UI with loaded data...")
            update_table_dropdown_ui()
            update_db_stats_ui()

            # Force final refresh to ensure display is updated
            print(f"🟧 [DATABASE_PRO] Forcing final refresh (view_mode={view_mode})")
            if view_mode == "cards":
                views_switcher.content = cards_view_container
                refresh_records_display()
            else:
                views_switcher.content = table_view_container
                refresh_data_table()
            if is_control_attached(views_switcher):
                views_switcher.update()

            print(f"🟧 [DATABASE_PRO] All data loaded and UI updated successfully!")
            logger.info("Database view setup completed successfully")
            _force_records_area_update()

        except asyncio.CancelledError:
            print(f"🟧 [DATABASE_PRO] Setup was CANCELLED (CancelledError)")
            logger.info("Setup cancelled via CancelledError")
            raise

        except Exception as e:
            print(f"🟧 [DATABASE_PRO] Setup FAILED with exception: {e}")
            logger.exception(f"Setup failed: {e}")

    def dispose() -> None:
        """Dispose function - cleanup resources."""
        nonlocal _setup_cancelled

        logger.info("🟥 [DATABASE_PRO] Disposing view")

        # Signal setup to stop
        _setup_cancelled = True

        # Cancel background tasks
        for task in background_tasks:
            if not task.done():
                logger.debug(f"Cancelling task: {task}")
                task.cancel()

        background_tasks.clear()
        logger.info("Database view disposed")

    # ========================================================================
    # RETURN VIEW TUPLE
    # ========================================================================

    logger.info("Database view creation completed")
    print(f"🟧 [DATABASE_PRO] About to return tuple")
    print(f"🟧 [DATABASE_PRO] main_container type: {type(main_container)}")
    print(f"🟧 [DATABASE_PRO] dispose callable: {callable(dispose)}")
    print(f"🟧 [DATABASE_PRO] setup callable: {callable(setup)}")
    return (main_container, dispose, setup)
