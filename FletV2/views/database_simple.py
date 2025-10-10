#!/usr/bin/env python3
"""Professional database management view with DataTable, sorting, and pagination.

Replaces the ListView-based implementation with a full-featured DataTable that includes:
- Column-based sorting (click headers)
- Client-side pagination (25 rows/page for performance)
- Row selection with checkboxes
- Inline actions column (Edit/Delete)
- Full CRUD operations with dialogs
- Search/filter across all columns
- CSV/JSON export capabilities
- Material Design 3 styling

Performance optimized with targeted control updates and limited row rendering.
"""

from __future__ import annotations

import asyncio
import csv
import io
import json
import os
import sys
from collections.abc import Coroutine
from datetime import datetime
from typing import Any, Callable, cast

import aiofiles
import flet as ft

# Ensure repository and package roots are on sys.path before other imports
_views_dir = os.path.dirname(os.path.abspath(__file__))
_flet_v2_root = os.path.dirname(_views_dir)
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# UTF-8 solution for subprocess/console I/O MUST remain first real import
import Shared.utils.utf8_solution as _  # noqa: F401  pylint: disable=unused-import

try:
    from FletV2.utils.debug_setup import get_logger
except ImportError:  # pragma: no cover - fallback logging for standalone runs
    import logging

    from FletV2 import config

    def get_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name or __name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
            logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if getattr(config, "DEBUG_MODE", False) else logging.WARNING)
        return logger

from FletV2.theme import (
    create_glassmorphic_container,
    create_neumorphic_container,
    create_neumorphic_metric_card,
)
from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.state_manager import StateManager
from FletV2.utils.ui_components import themed_button
from FletV2.utils.user_feedback import show_error_message, show_success_message

logger = get_logger(__name__)

DEFAULT_TABLE = "clients"
DEFAULT_TABLE_OPTIONS: tuple[str, ...] = ("clients", "files", "logs", "settings", "backups")
ROWS_PER_PAGE = 25
MAX_EXPORT_RECORDS = 10_000
SETUP_DELAY_SECONDS = 0.5  # Delay for control attachment
SENSITIVE_FIELDS = {"aes_key", "public_key", "private_key", "password", "secret", "key_material"}


def create_database_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    state_manager: StateManager | None = None,  # noqa: ARG001 - reserved for future use
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    """Create professional database management view with DataTable."""

    logger.info("Initializing database view with DataTable and pagination")

    current_table = DEFAULT_TABLE
    available_tables: list[str] = list(DEFAULT_TABLE_OPTIONS)
    all_records: list[dict[str, Any]] = []
    filtered_records: list[dict[str, Any]] = []
    table_columns: list[str] = []
    search_query = ""
    current_page = 0
    sort_column_index: int | None = None
    sort_ascending = True
    db_info: dict[str, Any] = {
        "status": "Disconnected",
        "tables": 0,
        "total_records": 0,
        "size": "0 MB",
        "integrity_check": False,
        "connection_pool_healthy": False,
    }

    def get_active_bridge() -> ServerBridge | None:
        bridge = server_bridge
        if bridge is None:
            return None
        return bridge if getattr(bridge, "real_server", None) else None

    def server_available() -> bool:
        return get_active_bridge() is not None

    # ------------------------------------------------------------------
    # UI CONTROLS
    # ------------------------------------------------------------------
    status_text = ft.Text("Ready", size=14, color=ft.Colors.GREY_400)
    loading_indicator = ft.ProgressRing(width=20, height=20, visible=False)

    db_status_value = ft.Text("Disconnected", size=20, weight=ft.FontWeight.BOLD)
    db_tables_value = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
    db_records_value = ft.Text("0", size=20, weight=ft.FontWeight.BOLD)
    db_size_value = ft.Text("0 MB", size=20, weight=ft.FontWeight.BOLD)

    table_dropdown = ft.Dropdown(
        label="Select table",
        value=current_table,
        width=220,
    )

    search_field = ft.TextField(
        label="Search records",
        prefix_icon=ft.Icons.SEARCH,
        hint_text="Type to filter across all columns…",
        width=320,
    )

    # DataTable will be created dynamically
    data_table = ft.DataTable(
        columns=[],
        rows=[],
        column_spacing=20,
        data_row_min_height=40,
        data_row_max_height=60,
        heading_row_height=50,
        show_checkbox_column=True,
        horizontal_lines=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT),
        divider_thickness=1,
    )

    # Pagination controls
    page_info_text = ft.Text("No records", size=13, color=ft.Colors.ON_SURFACE_VARIANT)
    prev_page_button = ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        tooltip="Previous page",
        disabled=True,
    )
    next_page_button = ft.IconButton(
        icon=ft.Icons.ARROW_FORWARD,
        tooltip="Next page",
        disabled=True,
    )

    add_button = cast(
        ft.FilledButton, themed_button("Add Record", lambda _e: None, "filled", ft.Icons.ADD)
    )
    refresh_button = cast(
        ft.OutlinedButton, themed_button("Refresh", lambda _e: None, "outlined", ft.Icons.REFRESH)
    )
    export_csv_button = cast(
        ft.OutlinedButton, themed_button("Export CSV", lambda _e: None, "outlined", ft.Icons.DOWNLOAD)
    )
    export_json_button = cast(
        ft.OutlinedButton, themed_button("Export JSON", lambda _e: None, "outlined", ft.Icons.DOWNLOAD)
    )

    add_button.disabled = not server_available()

    # ------------------------------------------------------------------
    # HELPER FUNCTIONS
    # ------------------------------------------------------------------
    def _control_attached(control: ft.Control) -> bool:
        return getattr(control, "page", None) is not None

    def _stringify(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, (bytes, bytearray)):
            # Show first 8 chars of hex for readability
            hex_str = value.hex()
            return f"{hex_str[:8]}..." if len(hex_str) > 8 else hex_str
        if isinstance(value, datetime):
            return value.isoformat(sep=" ", timespec="seconds")
        return str(value)

    def set_status(message: str, color: str | None = None, loading: bool | None = None) -> None:
        status_text.value = message
        if color:
            status_text.color = color
        if _control_attached(status_text):
            status_text.update()

        if loading is not None:
            loading_indicator.visible = loading
            if _control_attached(loading_indicator):
                loading_indicator.update()

    def update_database_info_ui() -> None:
        # Only modify controls if ALL are attached to page
        attached = all(_control_attached(c) for c in (db_status_value, db_tables_value, db_records_value, db_size_value, add_button))
        if not attached:
            logger.debug("Database info controls not yet attached, skipping update")
            return

        db_status_value.value = db_info.get("status", "Unknown")
        status_lower = db_info.get("status", "").lower()
        if "connected" in status_lower:
            db_status_value.color = ft.Colors.GREEN
        elif "error" in status_lower:
            db_status_value.color = ft.Colors.ERROR
        else:
            db_status_value.color = ft.Colors.GREY

        db_tables_value.value = str(db_info.get("tables", 0))
        db_records_value.value = str(db_info.get("total_records", 0))
        db_size_value.value = db_info.get("size", "0 MB")

        for control in (db_status_value, db_tables_value, db_records_value, db_size_value):
            control.update()

        add_button.disabled = not server_available()
        add_button.update()

    def update_table_dropdown() -> None:
        attached = _control_attached(table_dropdown)
        if not attached:
            logger.debug("Table dropdown not yet attached, skipping update")
            return

        options = available_tables or list(DEFAULT_TABLE_OPTIONS)
        table_dropdown.options = [
            ft.dropdown.Option(
                text=table.replace("_", " ").title(),
                key=table,
            )
            for table in options
        ]
        if current_table not in options:
            table_dropdown.value = options[0]
        else:
            table_dropdown.value = current_table

        table_dropdown.disabled = not server_available()
        if server_available():
            table_dropdown.helper_text = None
        else:
            table_dropdown.helper_text = "Server disconnected"

        table_dropdown.update()

    def get_total_pages() -> int:
        if not filtered_records:
            return 0
        return max(1, (len(filtered_records) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE)

    def get_page_records() -> list[dict[str, Any]]:
        """Get records for current page."""
        start_idx = current_page * ROWS_PER_PAGE
        end_idx = start_idx + ROWS_PER_PAGE
        return filtered_records[start_idx:end_idx]

    def update_pagination_controls() -> None:
        """Update pagination button states and page info."""
        total_pages = get_total_pages()
        total_records = len(filtered_records)

        if total_records == 0:
            page_info_text.value = "No records"
            prev_page_button.disabled = True
            next_page_button.disabled = True
        else:
            start_idx = current_page * ROWS_PER_PAGE + 1
            end_idx = min((current_page + 1) * ROWS_PER_PAGE, total_records)
            page_info_text.value = f"Showing {start_idx}-{end_idx} of {total_records} records • Page {current_page + 1} of {total_pages}"

            prev_page_button.disabled = current_page <= 0
            next_page_button.disabled = current_page >= total_pages - 1

        for control in (page_info_text, prev_page_button, next_page_button):
            if _control_attached(control):
                control.update()

    def build_table_columns() -> list[ft.DataColumn]:
        """Build DataTable columns from table schema."""
        if not table_columns:
            return [ft.DataColumn(ft.Text("No Data", weight=ft.FontWeight.BOLD))]

        columns = []
        for idx, col_name in enumerate(table_columns):
            # Skip sensitive fields
            if col_name.lower() in SENSITIVE_FIELDS:
                continue

            # Format column header
            header_text = col_name.replace("_", " ").title()

            # Create sortable column
            column = ft.DataColumn(
                label=ft.Text(header_text, weight=ft.FontWeight.BOLD),
                on_sort=lambda e, col_idx=idx: on_column_sort(col_idx),
            )
            columns.append(column)

        # Add Actions column
        columns.append(
            ft.DataColumn(
                label=ft.Text("Actions", weight=ft.FontWeight.BOLD),
            )
        )

        return columns

    def build_table_rows() -> list[ft.DataRow]:
        """Build DataTable rows for current page."""
        if not filtered_records or not table_columns:
            return []

        page_records = get_page_records()
        rows = []

        for record in page_records:
            cells = []

            # Add data cells
            for col_name in table_columns:
                if col_name.lower() in SENSITIVE_FIELDS:
                    continue

                value = _stringify(record.get(col_name, ""))
                cells.append(ft.DataCell(ft.Text(value, selectable=True)))

            # Add actions cell
            if server_available():
                actions_cell = ft.DataCell(
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=18,
                                tooltip="Edit",
                                on_click=lambda e, r=record: edit_record(r),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=18,
                                icon_color=ft.Colors.ERROR,
                                tooltip="Delete",
                                on_click=lambda e, r=record: delete_record(r),
                            ),
                        ],
                        spacing=0,
                    )
                )
            else:
                actions_cell = ft.DataCell(ft.Text(""))

            cells.append(actions_cell)

            row = ft.DataRow(
                cells=cells,
                on_select_changed=lambda e: None,  # Placeholder for selection
            )
            rows.append(row)

        return rows

    def refresh_data_table() -> None:
        """Rebuild and update DataTable."""
        if not _control_attached(data_table):
            logger.debug("DataTable not yet attached, skipping update")
            return

        data_table.columns = build_table_columns()
        data_table.rows = build_table_rows()
        data_table.sort_column_index = sort_column_index
        data_table.sort_ascending = sort_ascending

        data_table.update()
        update_pagination_controls()

    def apply_search_filter() -> None:
        nonlocal filtered_records, current_page

        if not search_query.strip():
            filtered_records = list(all_records)
        else:
            query = search_query.lower()
            filtered_records = [
                record
                for record in all_records
                if any(query in _stringify(value).lower() for value in record.values())
            ]

        # Reset to first page after filtering
        current_page = 0
        refresh_data_table()

        if search_query.strip():
            set_status(
                f"Found {len(filtered_records)} matches",
                ft.Colors.BLUE if filtered_records else ft.Colors.GREY,
                loading=None,
            )
        else:
            set_status(
                f"Loaded {len(filtered_records)} records",
                ft.Colors.GREEN if filtered_records else ft.Colors.GREY,
                loading=None,
            )

    def apply_sort() -> None:
        """Sort filtered records by current sort column."""
        nonlocal filtered_records

        if sort_column_index is None or not table_columns:
            return

        # Get visible columns (excluding sensitive fields)
        visible_columns = [col for col in table_columns if col.lower() not in SENSITIVE_FIELDS]

        if sort_column_index >= len(visible_columns):
            return

        sort_column_name = visible_columns[sort_column_index]

        def sort_key(record: dict[str, Any]) -> Any:
            value = record.get(sort_column_name)
            if value is None:
                return ""
            if isinstance(value, (bytes, bytearray)):
                return value.hex()
            return value

        try:
            filtered_records.sort(key=sort_key, reverse=not sort_ascending)
        except Exception as e:
            logger.warning(f"Sort failed: {e}")

    def get_export_payload() -> tuple[list[str], list[dict[str, Any]]]:
        if table_columns:
            columns = table_columns[:]
        else:
            columns = sorted({key for record in filtered_records for key in record.keys() if isinstance(key, str)})
        rows_to_export = filtered_records[:MAX_EXPORT_RECORDS]
        return columns, rows_to_export

    # ------------------------------------------------------------------
    # EVENT HANDLERS
    # ------------------------------------------------------------------
    def on_table_change(event: ft.ControlEvent) -> None:
        nonlocal current_table, search_query, current_page

        current_table = event.control.value or DEFAULT_TABLE
        search_query = ""
        current_page = 0
        search_field.value = ""
        if _control_attached(search_field):
            search_field.update()

        if hasattr(page, "run_task"):
            page.run_task(load_table_data_async)

    def on_search_change(event: ft.ControlEvent) -> None:
        nonlocal search_query
        search_query = event.control.value or ""
        apply_search_filter()

    def on_column_sort(col_idx: int) -> None:
        """Handle column header click for sorting."""
        nonlocal sort_column_index, sort_ascending

        if sort_column_index == col_idx:
            # Toggle sort direction
            sort_ascending = not sort_ascending
        else:
            # New column, default to ascending
            sort_column_index = col_idx
            sort_ascending = True

        apply_sort()
        refresh_data_table()

    def on_previous_page(e: ft.ControlEvent) -> None:
        nonlocal current_page
        if current_page > 0:
            current_page -= 1
            refresh_data_table()

    def on_next_page(e: ft.ControlEvent) -> None:
        nonlocal current_page
        total_pages = get_total_pages()
        if current_page < total_pages - 1:
            current_page += 1
            refresh_data_table()

    def on_refresh(_event: ft.ControlEvent) -> None:
        if hasattr(page, "run_task"):
            page.run_task(load_database_info_async)
            page.run_task(load_table_names_async)
            page.run_task(load_table_data_async)

    # ------------------------------------------------------------------
    # CRUD OPERATIONS
    # ------------------------------------------------------------------
    def add_record(_event: ft.ControlEvent) -> None:
        bridge = get_active_bridge()
        if bridge is None:
            show_error_message(page, "Connect the backup server to add records.")
            return

        editable_columns = [col for col in table_columns if col.lower() not in {"id", "uuid"}]
        if not editable_columns:
            show_error_message(page, "No editable columns available for this table.")
            return

        input_fields: dict[str, ft.TextField] = {}
        for column in editable_columns:
            field = ft.TextField(label=column.replace("_", " ").title())
            input_fields[column] = field

        add_dialog = ft.AlertDialog(
            title=ft.Text(f"Add record to {current_table.title()}"),
            content=ft.Column(list(input_fields.values()), height=360, scroll="auto"),
        )

        async def save_async() -> None:
            try:
                set_status("Saving record…", ft.Colors.BLUE, True)
                payload = {column: field.value or None for column, field in input_fields.items()}
                # CRITICAL: Use run_in_executor for sync bridge method
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, bridge.add_table_record, current_table, payload)
                if result.get("success"):
                    show_success_message(page, "Record added successfully")
                    await load_table_data_async()
                    page.close(add_dialog)
                else:
                    show_error_message(
                        page,
                        f"Failed to add record: {result.get('error', 'Unknown error')}",
                    )
            except Exception as exc:
                logger.exception("Error adding record: %s", exc)
                show_error_message(page, f"Error adding record: {exc}")
            finally:
                set_status("Ready", ft.Colors.GREY_400, False)

        add_dialog.actions = [
            ft.TextButton("Cancel", on_click=lambda _: page.close(add_dialog)),
            ft.FilledButton("Add", on_click=lambda _: page.run_task(save_async)),
        ]

        page.open(add_dialog)

    def edit_record(record: dict[str, Any]) -> None:
        bridge = get_active_bridge()
        if bridge is None:
            show_error_message(page, "Connect the backup server to edit records.")
            return

        editable_columns = [col for col in table_columns if col.lower() not in {"id", "uuid"}]
        if not editable_columns:
            show_error_message(page, "No editable columns available for this table.")
            return

        input_fields: dict[str, ft.TextField] = {}
        for column in editable_columns:
            input_fields[column] = ft.TextField(
                label=column.replace("_", " ").title(),
                value=_stringify(record.get(column, "")),
            )

        edit_dialog = ft.AlertDialog(
            title=ft.Text(f"Edit record #{record.get('id', 'unknown')}"),
            content=ft.Column(list(input_fields.values()), height=360, scroll="auto"),
        )

        async def save_changes() -> None:
            try:
                payload = dict(record)
                for column, field in input_fields.items():
                    payload[column] = field.value or None

                set_status("Updating record…", ft.Colors.BLUE, True)
                # CRITICAL: Use run_in_executor for sync bridge method
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, bridge.update_table_record, current_table, payload)
                if result.get("success"):
                    show_success_message(page, "Record updated successfully")
                    await load_table_data_async()
                    page.close(edit_dialog)
                else:
                    show_error_message(
                        page,
                        f"Failed to update record: {result.get('error', 'Unknown error')}",
                    )
            except Exception as exc:
                logger.exception("Error updating record: %s", exc)
                show_error_message(page, f"Error updating record: {exc}")
            finally:
                set_status("Ready", ft.Colors.GREY_400, False)

        edit_dialog.actions = [
            ft.TextButton("Cancel", on_click=lambda _: page.close(edit_dialog)),
            ft.FilledButton("Save", on_click=lambda _: page.run_task(save_changes)),
        ]

        page.open(edit_dialog)

    def delete_record(record: dict[str, Any]) -> None:
        bridge = get_active_bridge()
        if bridge is None:
            show_error_message(page, "Connect the backup server to delete records.")
            return

        record_id = record.get("id") or record.get("ID")
        if record_id is None:
            show_error_message(page, "Record is missing an identifier; cannot delete.")
            return

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirm delete"),
            content=ft.Text(
                f"Are you sure you want to delete record {record_id}? This action cannot be undone.",
                selectable=True,
            ),
        )

        async def confirm_async() -> None:
            try:
                set_status("Deleting record…", ft.Colors.BLUE, True)
                # CRITICAL: Use run_in_executor for sync bridge method
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, bridge.delete_table_record, current_table, record_id)
                if result.get("success"):
                    show_success_message(page, "Record deleted successfully")
                    await load_table_data_async()
                    page.close(confirm_dialog)
                else:
                    show_error_message(
                        page,
                        f"Failed to delete record: {result.get('error', 'Unknown error')}",
                    )
            except Exception as exc:
                logger.exception("Error deleting record: %s", exc)
                show_error_message(page, f"Error deleting record: {exc}")
            finally:
                set_status("Ready", ft.Colors.GREY_400, False)

        confirm_dialog.actions = [
            ft.TextButton("Cancel", on_click=lambda _: page.close(confirm_dialog)),
            ft.FilledButton(
                "Delete",
                on_click=lambda _: page.run_task(confirm_async),
                style=ft.ButtonStyle(bgcolor=ft.Colors.ERROR),
            ),
        ]

        page.open(confirm_dialog)

    # ------------------------------------------------------------------
    # EXPORT FUNCTIONALITY
    # ------------------------------------------------------------------
    def export_data(fmt: str) -> None:
        if not filtered_records:
            show_error_message(page, "Nothing to export")
            return

        async def export_async() -> None:
            columns, rows_to_export = get_export_payload()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{current_table}_{timestamp}.{fmt}"
            filepath = os.path.join(_repo_root, filename)

            try:
                if fmt == "csv":
                    buffer = io.StringIO()
                    writer = csv.writer(buffer)
                    writer.writerow(columns)
                    for row in rows_to_export:
                        writer.writerow([_stringify(row.get(column, "")) for column in columns])
                    async with aiofiles.open(filepath, "w", encoding="utf-8", newline="") as handle:
                        await handle.write(buffer.getvalue())
                else:
                    payload = [
                        {column: _stringify(row.get(column, "")) for column in columns}
                        for row in rows_to_export
                    ]
                    async with aiofiles.open(filepath, "w", encoding="utf-8") as handle:
                        await handle.write(json.dumps(payload, indent=2, ensure_ascii=False))

                show_success_message(
                    page,
                    f"Exported {len(rows_to_export)} records to {filename}",
                )
            except Exception as exc:
                logger.exception("Error exporting data: %s", exc)
                show_error_message(page, f"Export failed: {exc}")

        if hasattr(page, "run_task"):
            page.run_task(export_async)

    # ------------------------------------------------------------------
    # DATA LOADING HELPERS
    # ------------------------------------------------------------------
    async def load_database_info_async() -> None:
        nonlocal db_info

        if not server_available():
            db_info = {
                "status": "Disconnected",
                "tables": 0,
                "total_records": 0,
                "size": "0 MB",
                "integrity_check": False,
                "connection_pool_healthy": False,
            }
            update_database_info_ui()
            return

        try:
            set_status("Loading database info…", ft.Colors.BLUE, True)
            bridge = get_active_bridge()
            if bridge is None:
                db_info = {
                    "status": "Disconnected",
                    "tables": 0,
                    "total_records": 0,
                    "size": "0 MB",
                    "integrity_check": False,
                    "connection_pool_healthy": False,
                }
                update_database_info_ui()
                return

            # CRITICAL: Use run_in_executor for sync bridge method
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, bridge.get_database_info)

            if result.get("success") and result.get("data"):
                db_info = result["data"]
            else:
                error_msg = result.get("error", "Unknown error")
                logger.warning("Failed to load database info: %s", error_msg)
                db_info["status"] = f"Error: {error_msg}"
        except Exception as exc:
            logger.exception("Database info load failed: %s", exc)
            db_info["status"] = f"Error: {exc}"
        finally:
            set_status("Ready", ft.Colors.GREY_400, False)
            update_database_info_ui()

    async def load_table_names_async() -> None:
        nonlocal available_tables

        if not server_available():
            available_tables = list(DEFAULT_TABLE_OPTIONS)
            update_table_dropdown()
            return

        try:
            set_status("Fetching table list…", ft.Colors.BLUE, True)
            bridge = get_active_bridge()
            if bridge is None:
                available_tables = list(DEFAULT_TABLE_OPTIONS)
                return

            # CRITICAL: Use run_in_executor for sync method
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, bridge.get_table_names)
            if result.get("success"):
                data = result.get("data") or []
                available_tables = data or list(DEFAULT_TABLE_OPTIONS)
            else:
                error_msg = result.get("error", "Unknown error")
                logger.warning("Failed to load table names: %s", error_msg)
                available_tables = list(DEFAULT_TABLE_OPTIONS)
        except Exception as exc:
            logger.exception("Table name load failed: %s", exc)
            available_tables = list(DEFAULT_TABLE_OPTIONS)
        finally:
            set_status("Ready", ft.Colors.GREY_400, False)
            update_table_dropdown()

    async def load_table_data_async() -> None:
        nonlocal all_records, filtered_records, table_columns, current_page

        if not server_available():
            all_records = []
            filtered_records = []
            table_columns = []
            refresh_data_table()
            return

        try:
            set_status(f"Loading {current_table}…", ft.Colors.BLUE, True)
            bridge = get_active_bridge()
            if bridge is None:
                all_records = []
                filtered_records = []
                table_columns = []
                return

            # CRITICAL: Use run_in_executor for sync bridge method
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, bridge.get_table_data, current_table)
            if result.get("success"):
                data = result.get("data", {})
                table_columns = list(data.get("columns", []))
                all_records = list(data.get("rows", []))
                filtered_records = list(all_records)
                current_page = 0
            else:
                error_msg = result.get("error", "Unknown error")
                logger.warning("Failed to load table data: %s", error_msg)
                all_records = []
                filtered_records = []
                table_columns = []
        except Exception as exc:
            logger.exception("Table data load failed: %s", exc)
            all_records = []
            filtered_records = []
            table_columns = []
        finally:
            apply_search_filter()
            set_status("Ready", ft.Colors.GREY_400, False)

    # ------------------------------------------------------------------
    # LAYOUT COMPOSITION
    # ------------------------------------------------------------------
    info_cards = ft.ResponsiveRow(
        [
            ft.Container(
                content=create_neumorphic_metric_card(
                    ft.Column(
                        [
                            ft.Row([ft.Icon(ft.Icons.DATASET, size=24), ft.Text("Status", size=14)]),
                            db_status_value,
                        ],
                        spacing=8,
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
                            db_tables_value,
                        ],
                        spacing=8,
                    ),
                    intensity="pronounced",
                ),
                col={"sm": 12, "md": 6, "lg": 3},
            ),
            ft.Container(
                content=create_neumorphic_metric_card(
                    ft.Column(
                        [
                            ft.Row([ft.Icon(ft.Icons.STORAGE, size=24), ft.Text("Records", size=14)]),
                            db_records_value,
                        ],
                        spacing=8,
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
                            db_size_value,
                        ],
                        spacing=8,
                    ),
                    intensity="pronounced",
                ),
                col={"sm": 12, "md": 6, "lg": 3},
            ),
        ]
    )

    controls_row = create_glassmorphic_container(
        ft.Row(
            [
                table_dropdown,
                search_field,
                ft.Container(expand=True),
                loading_indicator,
                status_text,
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.START,
        ),
        intensity="moderate",
    )

    actions_row = ft.Row(
        [
            add_button,
            refresh_button,
            export_csv_button,
            export_json_button,
        ],
        spacing=12,
    )

    # DataTable container with scroll
    table_container = ft.Container(
        content=ft.Column(
            [
                ft.Container(
                    content=data_table,
                    border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
                    border_radius=8,
                    padding=10,
                ),
            ],
            scroll="auto",
            expand=True,
        ),
        expand=True,
    )

    # Pagination row
    pagination_row = ft.Row(
        [
            page_info_text,
            ft.Container(expand=True),
            prev_page_button,
            next_page_button,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    records_section = create_neumorphic_container(
        ft.Column(
            [
                ft.Text("Database Records", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Interactive table with sorting, pagination, and full CRUD operations",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                table_container,
                pagination_row,
            ],
            spacing=16,
            expand=True,
        ),
        effect_type="raised",
        intensity="pronounced",
    )

    main_content = ft.Column(
        [
            ft.Text("Database Management", size=32, weight=ft.FontWeight.BOLD),
            info_cards,
            controls_row,
            actions_row,
            records_section,
        ],
        expand=True,
        spacing=24,
        scroll="auto",
    )

    main_container = ft.Container(content=main_content, expand=True)

    # Wire up event handlers
    table_dropdown.on_change = on_table_change
    search_field.on_change = on_search_change
    add_button.on_click = add_record
    refresh_button.on_click = on_refresh
    export_csv_button.on_click = lambda _e: export_data("csv")
    export_json_button.on_click = lambda _e: export_data("json")
    prev_page_button.on_click = on_previous_page
    next_page_button.on_click = on_next_page

    # ------------------------------------------------------------------
    # LIFECYCLE HOOKS
    # ------------------------------------------------------------------
    background_tasks: list[asyncio.Task] = []
    _setup_cancelled = False

    async def setup() -> None:
        """Setup function - load initial data."""
        nonlocal _setup_cancelled

        logger.info("Setting up database view (async)")
        try:
            if _setup_cancelled:
                return

            # Allow AnimatedSwitcher transition to finish
            await asyncio.sleep(SETUP_DELAY_SECONDS)

            if _setup_cancelled:
                return

            # Initialize UI state
            update_table_dropdown()
            update_database_info_ui()
            refresh_data_table()

            # Load data
            await load_database_info_async()
            await load_table_names_async()
            await load_table_data_async()
        except asyncio.CancelledError:
            logger.info("Database view setup cancelled")
            raise
        except Exception as exc:
            logger.exception("Database view setup failed: %s", exc)

    def dispose() -> None:
        """Dispose hook - cancel background tasks."""
        nonlocal _setup_cancelled

        logger.info("Disposing database view - cancelling background tasks")
        _setup_cancelled = True

        for task in background_tasks:
            if not task.done():
                task.cancel()

        background_tasks.clear()
        logger.debug("Database view disposed")

    return (main_container, dispose, setup)
