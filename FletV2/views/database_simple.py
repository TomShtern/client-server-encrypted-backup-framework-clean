#!/usr/bin/env python3
"""Lightweight database management view tuned for Flet 0.28.3 web hot-reload.

The previous implementation relied on ``ft.DataTable`` which caused heavy widget
rebuilds on every update. In web mode that triggered long blocking layouts and
made the entire GUI appear frozen even when no server was connected. This
rewrite switches to a ``ListView`` based layout per the official Flet guidance
(https://flet.dev/docs/controls/listview/) to use ListView/GridView for large or
frequently refreshed collections. All updates now target individual controls,
eliminating the freeze while retaining CRUD, search, and export capabilities.
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
MAX_VISIBLE_RECORDS = 50
MAX_EXPORT_RECORDS = 10_000
SETUP_DELAY_SECONDS = 0.5  # Increased from 0.2 to ensure controls fully attached
SENSITIVE_FIELDS = {"aes_key", "public_key", "private_key", "password", "secret", "key_material"}


def create_database_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    state_manager: StateManager | None = None,  # noqa: ARG001 - reserved for future use
) -> tuple[ft.Control, Callable[[], None], Callable[[], Coroutine[Any, Any, None]]]:
    """Create lightweight database management view."""

    print("🔴 [DATABASE_VIEW] Function ENTERED")
    logger.info("🔴 [DATABASE_VIEW] Initializing lightweight database view (ListView-based)")
    print("🔴 [DATABASE_VIEW] Logger.info completed")

    current_table = DEFAULT_TABLE
    available_tables: list[str] = list(DEFAULT_TABLE_OPTIONS)
    all_records: list[dict[str, Any]] = []
    filtered_records: list[dict[str, Any]] = []
    table_columns: list[str] = []
    search_query = ""
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

    records_list = ft.ListView(expand=True, spacing=12, padding=ft.Padding(0, 4, 0, 24))
    records_list.controls.append(
        ft.Container(
            content=ft.Column(
                [
                    ft.Icon(ft.Icons.DATASET, size=48, color=ft.Colors.GREY_500),
                    ft.Text("Database view is ready", size=16, color=ft.Colors.GREY_500),
                    ft.Text(
                        "Connect the backup server and choose a table to load records.",
                        size=12,
                        color=ft.Colors.GREY_400,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
                spacing=8,
            ),
            padding=ft.Padding(0, 36, 0, 36),
        )
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
            return value.hex()
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
        print("🔵 [UPDATE_DB_INFO] Function called")
        # CRITICAL: Only modify controls if ALL are attached to page
        attached = all(_control_attached(c) for c in (db_status_value, db_tables_value, db_records_value, db_size_value, add_button))
        print(f"🔵 [UPDATE_DB_INFO] All controls attached: {attached}")
        if not attached:
            logger.debug("Database info controls not yet attached, skipping update")
            print("🔵 [UPDATE_DB_INFO] Returning early - controls not attached")
            return
        print("🔵 [UPDATE_DB_INFO] Controls attached, proceeding with update")

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
        print("🔵 [UPDATE_DROPDOWN] Function called")
        # CRITICAL: Only modify dropdown if attached to page
        attached = _control_attached(table_dropdown)
        print(f"🔵 [UPDATE_DROPDOWN] Dropdown attached: {attached}")
        if not attached:
            logger.debug("Table dropdown not yet attached, skipping update")
            print("🔵 [UPDATE_DROPDOWN] Returning early - dropdown not attached")
            return
        print("🔵 [UPDATE_DROPDOWN] Dropdown attached, proceeding with update")

        options = available_tables or list(DEFAULT_TABLE_OPTIONS)
        # Use explicit text/key to avoid value mismatches across Flet versions
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

    def build_record_tile(record: dict[str, Any], index: int) -> ft.Container:
        display_keys: list[str] = table_columns or list(record.keys())
        rows: list[ft.Control] = []
        shown = 0
        for key in display_keys:
            if not isinstance(key, str):
                continue
            if key.lower() in SENSITIVE_FIELDS:
                continue
            value = _stringify(record.get(key))
            if not value and value != "0":
                continue
            rows.append(
                ft.Row(
                    [
                        ft.Text(
                            key.replace("_", " ").title(),
                            size=12,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            width=150,
                        ),
                        ft.Text(value, size=12, selectable=True, expand=True),
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                )
            )
            shown += 1
            if shown >= 8:
                break

        if not rows:
            rows.append(ft.Text("No displayable fields", size=12, color=ft.Colors.GREY_500))

        footer: ft.Control | None = None
        if server_available():
            footer = ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        tooltip="Edit record",
                        icon_size=18,
                        on_click=lambda _e, r=record: edit_record(r),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE,
                        tooltip="Delete record",
                        icon_size=18,
                        icon_color=ft.Colors.ERROR,
                        on_click=lambda _e, r=record: delete_record(r),
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            )

        tile_children: list[ft.Control] = [
            ft.Text(f"{current_table.title()} #{index + 1}", size=14, weight=ft.FontWeight.BOLD),
            ft.Column(rows, spacing=6, tight=True),
        ]

        if footer:
            tile_children.append(footer)

        return ft.Container(
            content=ft.Column(tile_children, spacing=10, tight=True),
            padding=ft.Padding(16, 12, 16, 12),
            border_radius=14,
            # SURFACE_VARIANT not available in current Flet; approximate with SURFACE tint
            bgcolor=ft.Colors.with_opacity(0.06, ft.Colors.SURFACE),
        )

    def refresh_records_list() -> None:
        print("🔵 [REFRESH_RECORDS] Function called")
        # CRITICAL: Only modify ListView controls if attached to page
        attached = _control_attached(records_list)
        print(f"🔵 [REFRESH_RECORDS] Records list attached: {attached}")
        if not attached:
            logger.debug("Records list not yet attached, skipping update")
            print("🔵 [REFRESH_RECORDS] Returning early - list not attached")
            return
        print("🔵 [REFRESH_RECORDS] List attached, proceeding with update")

        records_list.controls.clear()

        if not filtered_records:
            if server_available():
                message = f"No records found in '{current_table}'."
            else:
                message = "Connect the backup server to load data."
            records_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.INBOX_OUTLINED, size=40, color=ft.Colors.GREY_500),
                            ft.Text(message, size=14, color=ft.Colors.GREY_500),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,
                    ),
                    padding=ft.Padding(0, 28, 0, 28),
                )
            )
        else:
            summary = ft.Text(
                f"Showing {min(len(filtered_records), MAX_VISIBLE_RECORDS)} of {len(filtered_records)} records",
                size=13,
                color=ft.Colors.ON_SURFACE_VARIANT,
            )
            records_list.controls.append(summary)

            for index, record in enumerate(filtered_records[:MAX_VISIBLE_RECORDS]):
                records_list.controls.append(build_record_tile(record, index))

            if len(filtered_records) > MAX_VISIBLE_RECORDS:
                records_list.controls.append(
                    ft.Text(
                        f"…and {len(filtered_records) - MAX_VISIBLE_RECORDS} more records",
                        size=12,
                        color=ft.Colors.GREY_500,
                        italic=True,
                    )
                )

        records_list.update()

    def apply_search_filter() -> None:
        nonlocal filtered_records

        if not search_query.strip():
            filtered_records = list(all_records)
        else:
            query = search_query.lower()
            filtered_records = [
                record
                for record in all_records
                if any(query in _stringify(value).lower() for value in record.values())
            ]

        refresh_records_list()
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
        nonlocal current_table, search_query

        current_table = event.control.value or DEFAULT_TABLE
        search_query = ""
        search_field.value = ""
        if _control_attached(search_field):
            search_field.update()

        if hasattr(page, "run_task"):
            # Pass function reference, not coroutine object
            page.run_task(load_table_data_async)

    def on_search_change(event: ft.ControlEvent) -> None:
        nonlocal search_query
        search_query = event.control.value or ""
        apply_search_filter()

    def on_refresh(_event: ft.ControlEvent) -> None:
        if hasattr(page, "run_task"):
            # FIXED: Pass function, not coroutine object
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
                # CRITICAL FIX: Use run_in_executor for sync bridge method (January 2025)
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
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Error adding record: %s", exc)
                show_error_message(page, f"Error adding record: {exc}")
            finally:
                set_status("Ready", ft.Colors.GREY_400, False)

        add_dialog.actions = [
            ft.TextButton("Cancel", on_click=lambda _: page.close(add_dialog)),
            # Pass function reference to run_task
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
                # CRITICAL FIX: Use run_in_executor for sync bridge method (January 2025)
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
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Error updating record: %s", exc)
                show_error_message(page, f"Error updating record: {exc}")
            finally:
                set_status("Ready", ft.Colors.GREY_400, False)

        edit_dialog.actions = [
            ft.TextButton("Cancel", on_click=lambda _: page.close(edit_dialog)),
            # Pass function reference to run_task
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
                # CRITICAL FIX: Use run_in_executor for sync bridge method (January 2025)
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
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Error deleting record: %s", exc)
                show_error_message(page, f"Error deleting record: {exc}")
            finally:
                set_status("Ready", ft.Colors.GREY_400, False)

        confirm_dialog.actions = [
            ft.TextButton("Cancel", on_click=lambda _: page.close(confirm_dialog)),
            ft.FilledButton(
                "Delete",
                # Pass function reference to run_task
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
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Error exporting data: %s", exc)
                show_error_message(page, f"Export failed: {exc}")

        if hasattr(page, "run_task"):
            # Pass function reference, not coroutine object
            page.run_task(export_async)

    # ------------------------------------------------------------------
    # DATA LOADING HELPERS
    # ------------------------------------------------------------------
    async def load_database_info_async() -> None:
        nonlocal db_info
        print("🟠 [LOAD_DB_INFO] Function ENTERED")

        if not server_available():
            print("🟠 [LOAD_DB_INFO] Server not available")
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
            print("🟠 [LOAD_DB_INFO] Setting status to 'Loading database info…'")
            set_status("Loading database info…", ft.Colors.BLUE, True)
            print("🟠 [LOAD_DB_INFO] Getting active bridge")
            bridge = get_active_bridge()
            if bridge is None:
                print("🟠 [LOAD_DB_INFO] Bridge is None")
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

            # CRITICAL FIX: Use run_in_executor for sync bridge method (January 2025)
            print("🟠 [LOAD_DB_INFO] About to call bridge.get_database_info() with run_in_executor")
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, bridge.get_database_info)
            print(f"🟠 [LOAD_DB_INFO] Method returned: success={result.get('success')}, error={result.get('error')}")

            if result.get("success") and result.get("data"):
                db_info = result["data"]
                print(f"🟠 [LOAD_DB_INFO] SUCCESS - Updated db_info: {db_info}")
            else:
                error_msg = result.get("error", "Unknown error")
                print(f"🟠 [LOAD_DB_INFO] FAILED - Error: {error_msg}")
                logger.warning("Failed to load database info: %s", error_msg)
                db_info["status"] = f"Error: {error_msg}"
        except Exception as exc:  # pragma: no cover - defensive
            print(f"🟠 [LOAD_DB_INFO] EXCEPTION: {type(exc).__name__}: {exc}")
            logger.exception("Database info load failed: %s", exc)
            db_info["status"] = f"Error: {exc}"
        finally:
            print("🟠 [LOAD_DB_INFO] Finally block - setting status to Ready")
            set_status("Ready", ft.Colors.GREY_400, False)
            update_database_info_ui()
            print("🟠 [LOAD_DB_INFO] Function EXITING")

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

            # CRITICAL FIX: Use run_in_executor for sync method (no async version exists)
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, bridge.get_table_names)
            if result.get("success"):
                data = result.get("data") or []
                available_tables = data or list(DEFAULT_TABLE_OPTIONS)
            else:
                error_msg = result.get("error", "Unknown error")
                logger.warning("Failed to load table names: %s", error_msg)
                available_tables = list(DEFAULT_TABLE_OPTIONS)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Table name load failed: %s", exc)
            available_tables = list(DEFAULT_TABLE_OPTIONS)
        finally:
            set_status("Ready", ft.Colors.GREY_400, False)
            update_table_dropdown()

    async def load_table_data_async() -> None:
        nonlocal all_records, filtered_records, table_columns

        if not server_available():
            all_records = []
            filtered_records = []
            table_columns = []
            refresh_records_list()
            return

        try:
            set_status(f"Loading {current_table}…", ft.Colors.BLUE, True)
            bridge = get_active_bridge()
            if bridge is None:
                all_records = []
                filtered_records = []
                table_columns = []
                return

            # CRITICAL FIX: Use run_in_executor for sync bridge method (January 2025)
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, bridge.get_table_data, current_table)
            if result.get("success"):
                data = result.get("data", {})
                table_columns = list(data.get("columns", []))
                all_records = list(data.get("rows", []))
                filtered_records = list(all_records)
            else:
                error_msg = result.get("error", "Unknown error")
                logger.warning("Failed to load table data: %s", error_msg)
                all_records = []
                filtered_records = []
                table_columns = []
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Table data load failed: %s", exc)
            all_records = []
            filtered_records = []
            table_columns = []
        finally:
            apply_search_filter()
            set_status("Ready", ft.Colors.GREY_400, False)

    # ------------------------------------------------------------------
    # INITIAL LAYOUT COMPOSITION
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

    add_button.on_click = add_record
    refresh_button.on_click = on_refresh
    export_csv_button.on_click = lambda _e: export_data("csv")
    export_json_button.on_click = lambda _e: export_data("json")

    records_section = create_neumorphic_container(
        ft.Column(
            [
                ft.Text("Database Records", size=28, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Rendered with ListView to avoid DataTable freezes per Flet documentation.",
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT,
                ),
                ft.Divider(height=1, color=ft.Colors.OUTLINE_VARIANT),
                ft.Container(content=records_list, expand=True),
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

    table_dropdown.on_change = on_table_change
    search_field.on_change = on_search_change

    # CRITICAL FIX: Do NOT update controls during view creation!
    # These updates will freeze the UI if called before the view is attached to the page.
    # All UI updates are now deferred to the setup() function.
    # update_table_dropdown()     # ❌ REMOVED - causes freeze
    # update_database_info_ui()   # ❌ REMOVED - causes freeze
    # refresh_records_list()      # ❌ REMOVED - causes freeze

    # ------------------------------------------------------------------
    # LIFECYCLE HOOKS
    # ------------------------------------------------------------------
    # Track background tasks for proper cancellation
    background_tasks: list[asyncio.Task] = []
    _setup_cancelled = False

    async def setup() -> None:
        """Setup function - load initial data."""
        nonlocal _setup_cancelled

        print("🔴 [DATABASE_SETUP] Setup function CALLED")
        logger.info("🔴 [DATABASE_SETUP] Setting up database view (async)")
        print("🔴 [DATABASE_SETUP] About to call update functions")
        try:
            # Check if disposed before proceeding
            if _setup_cancelled:
                print("🔴 [DATABASE_SETUP] Setup cancelled - exiting early")
                return

            # Allow AnimatedSwitcher transition to finish BEFORE any updates to avoid
            # potential deadlocks/disconnects when controls aren't fully attached yet.
            print(f"🔴 [DATABASE_SETUP] Waiting {SETUP_DELAY_SECONDS}s for attachment")
            await asyncio.sleep(SETUP_DELAY_SECONDS)

            if _setup_cancelled:
                print("🔴 [DATABASE_SETUP] Setup cancelled after sleep - exiting")
                return

            # CRITICAL: Initialize UI state AFTER guaranteed attachment delay
            print("🔴 [DATABASE_SETUP] Calling update_table_dropdown()")
            update_table_dropdown()
            print("🔴 [DATABASE_SETUP] Calling update_database_info_ui()")
            update_database_info_ui()
            print("🔴 [DATABASE_SETUP] Calling refresh_records_list()")
            refresh_records_list()
            print("🔴 [DATABASE_SETUP] Initial UI updates completed, loading data…")

            print("🔴 [DATABASE_SETUP] Sleep completed, loading database info")
            await load_database_info_async()
            print("🔴 [DATABASE_SETUP] Database info loaded, loading table names")
            await load_table_names_async()
            print("🔴 [DATABASE_SETUP] Table names loaded, loading table data")
            await load_table_data_async()
            print("🔴 [DATABASE_SETUP] All async loading completed successfully!")
        except asyncio.CancelledError:
            print("🔴 [DATABASE_SETUP] Setup task was cancelled")
            logger.info("Database view setup cancelled")
            raise  # Re-raise to properly cancel the task
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Database view setup failed: %s", exc)

    def dispose() -> None:
        """Dispose hook - cancel background tasks."""
        nonlocal _setup_cancelled

        print("🟥 [DATABASE_DISPOSE] Dispose function CALLED")
        logger.info("🟥 [DATABASE_DISPOSE] Disposing database view - cancelling background tasks")

        # Signal setup to stop if it's running
        _setup_cancelled = True

        # Cancel all tracked background tasks
        for task in background_tasks:
            if not task.done():
                print(f"🟥 [DATABASE_DISPOSE] Cancelling task: {task}")
                task.cancel()

        background_tasks.clear()
        print("🟥 [DATABASE_DISPOSE] All background tasks cancelled")
        logger.debug("Database view disposed")

    print(f"🔴 [DATABASE_VIEW] About to return tuple: (main_container={type(main_container)}, dispose={type(dispose)}, setup={type(setup)})")
    logger.info(f"🔴 [DATABASE_VIEW] Returning view tuple with setup function: {setup}")
    result = (main_container, dispose, setup)
    print(f"🔴 [DATABASE_VIEW] Result tuple created, len={len(result)}, types={[type(x) for x in result]}")
    return result
