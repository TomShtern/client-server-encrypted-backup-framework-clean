#!/usr/bin/env python3
"""
Simplified Clients View - The Flet Way
~350 lines instead of 956 lines of framework fighting!

Core Principle: Use Flet's built-in DataTable, AlertDialog, and TextField.
Clean client management with server integration and graceful fallbacks.
"""

import asyncio
import concurrent.futures
import contextlib
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime
from typing import Any

import flet as ft

# ALWAYS import this in any Python file that deals with subprocess or console I/O

try:
    from FletV2.utils.debug_setup import get_logger
except ImportError:  # pragma: no cover - fallback logging
    import logging

    from FletV2 import config

    def get_logger(name: str) -> logging.Logger:
        logger = logging.getLogger(name or __name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
            logger.addHandler(handler)
        logger.setLevel(logging.DEBUG if getattr(config, "DEBUG_MODE", False) else logging.WARNING)
        return logger


from FletV2.utils.async_helpers import create_async_fetch_function, run_sync_in_executor, safe_server_call
from FletV2.utils.server_bridge import ServerBridge
from FletV2.utils.simple_state import SimpleState
from FletV2.utils.ui_builders import (
    create_action_button,
    create_filter_dropdown,
    create_metric_card,
    create_search_bar,
    create_view_header,
)
from FletV2.utils.ui_components import AppCard, create_status_pill
from FletV2.utils.user_feedback import show_error_message, show_success_message

logger = get_logger(__name__)

SERVER_NOT_CONNECTED_MESSAGE = "Server not connected. Please start the backup server."


class _ClientsViewController:
    def __init__(
        self,
        server_bridge: ServerBridge | None,
        page: ft.Page,
        state_manager: SimpleState | None,
        global_search: ft.Control | None,
    ) -> None:
        self.server_bridge = server_bridge
        self.page = page
        self.state_manager = state_manager
        self.state_subscription_callback: Callable[[Any, Any], None] | None = None
        self.global_search = global_search

        self.search_query = ""
        self.status_filter = "all"
        self.clients_data: list[dict[str, Any]] = []

        self._fetch_clients_async = create_async_fetch_function("get_clients", empty_default=[])

        self.clients_table = self._create_clients_table()
        (
            self.total_clients_value,
            self.connected_clients_value,
            self.disconnected_clients_value,
            self.total_files_value,
        ) = self._create_stat_controls()

        self.loading_ring = ft.ProgressRing(width=20, height=20, visible=False)

        self.search_field = create_search_bar(
            self.on_search_change,
            placeholder="Search clients…",
        )

        self.status_filter_dropdown = create_filter_dropdown(
            "Status",
            [
                ("all", "All"),
                ("connected", "Connected"),
                ("disconnected", "Disconnected"),
                ("connecting", "Connecting"),
            ],
            self.on_status_filter_change,
            value=self.status_filter,
            width=200,
        )

        self.refresh_button = create_action_button(
            "Refresh",
            self.refresh_clients,
            icon=ft.Icons.REFRESH,
            primary=False,
        )

    def build(self) -> tuple[ft.Control, Callable[[], None], Callable[[], Awaitable[None]]]:
        filters_row = self._create_filters_row()
        stats_section = AppCard(self._create_stats_row(), title="At a glance")
        filters_section = AppCard(filters_row, title="Filters")
        table_section = AppCard(self.clients_table, title="Clients")
        table_section.expand = True

        # Note: Global search is in the app-level header (main.py), not view-level
        header_actions = [
            create_action_button("Add client", lambda _: self.add_client(), icon=ft.Icons.PERSON_ADD),
            self.refresh_button,
        ]

        header = create_view_header(
            "Client management",
            icon=ft.Icons.PEOPLE_ALT_OUTLINED,
            description="Manage registered backup clients and their connection status.",
            actions=header_actions,
        )

        main_column = ft.Column(
            [
                header,
                stats_section,
                filters_section,
                table_section,
            ],
            spacing=16,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

        main_layout = ft.Container(
            content=main_column,
            padding=ft.padding.symmetric(horizontal=20, vertical=16),
            expand=True,
        )

        return main_layout, self.dispose, self.setup_subscriptions

    async def setup_subscriptions(self) -> None:
        existing_clients: list[dict[str, Any]] = []
        if self.state_manager is not None:
            with contextlib.suppress(Exception):
                state_value = self.state_manager.get("clients", [])
                if isinstance(state_value, list):
                    existing_clients = state_value

        if existing_clients:
            self.apply_clients_data(existing_clients, broadcast=False, source="state_manager_init")
        else:
            await self.load_clients_data()

    def dispose(self) -> None:
        logger.debug("Disposing clients view")
        if self.state_manager is not None and self.state_subscription_callback is not None:
            with contextlib.suppress(Exception):
                self.state_manager.unsubscribe("clients", self.state_subscription_callback)
            self.state_subscription_callback = None

    # ------------------------------------------------------------------
    # Control builders
    # ------------------------------------------------------------------

    def _create_clients_table(self) -> ft.DataTable:
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Status")),
                ft.DataColumn(ft.Text("Last Seen")),
                ft.DataColumn(ft.Text("Files")),
                ft.DataColumn(ft.Text("Actions")),
            ],
            rows=[],
            heading_row_color="#212121",
            border_radius=12,
            expand=True,
        )

    def _create_stat_controls(self) -> tuple[ft.Control, ft.Control, ft.Control, ft.Control]:
        total_clients_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
        total_clients_value.semantics_label = "Total clients count"
        connected_clients_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
        connected_clients_value.semantics_label = "Connected clients count"
        disconnected_clients_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
        disconnected_clients_value.semantics_label = "Disconnected clients count"
        total_files_value = ft.Text("0", size=24, weight=ft.FontWeight.BOLD)
        total_files_value.semantics_label = "Total files across clients"

        return (
            total_clients_value,
            connected_clients_value,
            disconnected_clients_value,
            total_files_value,
        )

    def _create_stats_row(self) -> ft.ResponsiveRow:
        return ft.ResponsiveRow(
            [
                ft.Column(
                    [
                        create_metric_card(
                            "Total Clients", self.total_clients_value, ft.Icons.PEOPLE, "Total clients metric"
                        )
                    ],
                    col={"sm": 12, "md": 6, "lg": 3},
                ),
                ft.Column(
                    [
                        create_metric_card(
                            "Connected",
                            self.connected_clients_value,
                            ft.Icons.WIFI,
                            "Connected clients metric",
                        )
                    ],
                    col={"sm": 12, "md": 6, "lg": 3},
                ),
                ft.Column(
                    [
                        create_metric_card(
                            "Disconnected",
                            self.disconnected_clients_value,
                            ft.Icons.WIFI_OFF,
                            "Disconnected clients metric",
                        )
                    ],
                    col={"sm": 12, "md": 6, "lg": 3},
                ),
                ft.Column(
                    [
                        create_metric_card(
                            "Total Files",
                            self.total_files_value,
                            ft.Icons.FOLDER,
                            "Total client files metric",
                        )
                    ],
                    col={"sm": 12, "md": 6, "lg": 3},
                ),
            ]
        )

    def _create_filters_row(self) -> ft.ResponsiveRow:
        return ft.ResponsiveRow(
            controls=[
                ft.Container(content=self.search_field, col={"xs": 12, "sm": 8, "md": 6, "lg": 5}),
                ft.Container(content=self.status_filter_dropdown, col={"xs": 12, "sm": 4, "md": 3, "lg": 2}),
                ft.Container(
                    content=ft.Row(
                        [
                            self.refresh_button,
                            self.loading_ring,
                        ],
                        spacing=8,
                    ),
                    col={"xs": 12, "sm": 12, "md": 3, "lg": 2},
                    alignment=ft.alignment.center_left,
                ),
            ],
            spacing=12,
            run_spacing=12,
            alignment=ft.MainAxisAlignment.START,
        )

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    async def load_clients_data(self, *, broadcast: bool | None = None) -> None:
        try:
            self._show_loading()
            should_broadcast = self.state_manager is not None if broadcast is None else broadcast
            new_clients = await self._fetch_clients_async(self.server_bridge)
            self.apply_clients_data(new_clients, broadcast=should_broadcast)
        except Exception as exc:
            logger.error(f"Error loading clients: {exc}")
            show_error_message(self.page, f"Failed to load clients: {exc}")
        finally:
            self._hide_loading()

    def apply_clients_data(
        self,
        new_clients: list[dict[str, Any]] | None,
        *,
        broadcast: bool = False,
        source: str = "clients_view",
    ) -> None:
        normalized: list[dict[str, Any]] = []
        if new_clients:
            normalized = [dict(item) if isinstance(item, dict) else item for item in new_clients]

        self.clients_data = normalized
        self.update_stats()
        self.update_table()

        if broadcast and self.state_manager is not None:
            with contextlib.suppress(Exception):
                self.state_manager.update(
                    "clients",
                    [dict(item) if isinstance(item, dict) else item for item in normalized],
                    source=source,
                )

    def update_stats(self) -> None:
        totals = len(self.clients_data)
        connected = len(
            [client for client in self.clients_data if str(client.get("status", "")).lower() == "connected"]
        )
        disconnected = len(
            [
                client
                for client in self.clients_data
                if str(client.get("status", "")).lower() == "disconnected"
            ]
        )
        files_total = sum(int(client.get("files_count", 0) or 0) for client in self.clients_data)

        self.total_clients_value.value = str(totals)
        self.connected_clients_value.value = str(connected)
        self.disconnected_clients_value.value = str(disconnected)
        self.total_files_value.value = str(files_total)

        for control in (
            self.total_clients_value,
            self.connected_clients_value,
            self.disconnected_clients_value,
            self.total_files_value,
        ):
            with contextlib.suppress(Exception):
                control.update()

    def update_table(self) -> None:
        filtered_clients = self.filter_clients()

        if self.clients_table.rows:
            self.clients_table.rows.clear()

        for client in filtered_clients:
            self.clients_table.rows.append(self._build_client_row(client))

        if getattr(self.clients_table, "page", None):
            self.clients_table.update()

    def filter_clients(self) -> list[dict[str, Any]]:
        filtered = self.clients_data.copy()

        if self.search_query.strip():
            query = self.search_query.lower()
            filtered = [
                client
                for client in filtered
                if (
                    query in str(client.get("id", "")).lower()
                    or query in str(client.get("name", "")).lower()
                    or query in str(client.get("status", "")).lower()
                )
            ]

        if self.status_filter != "all":
            filtered = [
                client
                for client in filtered
                if str(client.get("status", "")).lower() == self.status_filter.lower()
            ]

        return filtered

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def on_search_change(self, event: ft.ControlEvent | str) -> None:
        value = event if isinstance(event, str) else getattr(getattr(event, "control", None), "value", "")
        self.search_query = value or ""
        self.update_table()

    def on_status_filter_change(self, event: ft.ControlEvent) -> None:
        self.status_filter = event.control.value
        self.update_table()

    async def refresh_clients(self, _event: ft.ControlEvent) -> None:
        try:
            self._show_loading()
            await self.load_clients_data()
            show_success_message(self.page, "Clients refreshed")
        finally:
            self._hide_loading()

    def view_client_details(self, client: dict[str, Any]) -> None:
        details_dialog = ft.AlertDialog(
            title=ft.Text("Client Details"),
            content=ft.Column(
                [
                    ft.Text(f"ID: {client.get('id', 'N/A')}"),
                    ft.Text(f"Name: {client.get('name', 'N/A')}"),
                    ft.Row(
                        [
                            ft.Text("Status: "),
                            create_status_pill(
                                client.get("status", "Unknown"),
                                self.get_status_type(client.get("status", "Unknown")),
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Text(f"Last Seen: {client.get('last_seen', 'N/A')}"),
                    ft.Text(f"Files: {client.get('files_count', 'N/A')}"),
                    ft.Text(f"IP Address: {client.get('ip_address', 'N/A')}"),
                ],
                height=200,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[ft.TextButton("Close", on_click=lambda _e: self.page.close(details_dialog))],
        )
        self.page.open(details_dialog)

    def disconnect_client(self, client: dict[str, Any]) -> None:
        async def confirm_disconnect_async(_e: ft.ControlEvent) -> None:
            if not self.server_bridge:
                show_error_message(self.page, SERVER_NOT_CONNECTED_MESSAGE)
                self.page.close(confirm_dialog)
                return

            client_id = client.get("id")
            if not client_id or not isinstance(client_id, str):
                show_error_message(self.page, "Invalid client ID")
                self.page.close(confirm_dialog)
                return

            result = await run_sync_in_executor(
                safe_server_call, self.server_bridge, "disconnect_client", client_id
            )

            if result.get("success"):
                show_success_message(self.page, f"Client {client.get('name')} disconnected")
                await self.load_clients_data()
            else:
                show_error_message(self.page, f"Failed to disconnect: {result.get('error', 'Unknown error')}")

            self.page.close(confirm_dialog)

        async def confirm_disconnect(event: ft.ControlEvent) -> None:
            await self._run_with_loading(confirm_disconnect_async, event)

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Disconnect"),
            content=ft.Text(f"Are you sure you want to disconnect {client.get('name', 'this client')}?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: self.page.close(confirm_dialog)),
                ft.FilledButton("Disconnect", on_click=confirm_disconnect),
            ],
        )
        self.page.open(confirm_dialog)

    def delete_client(self, client: dict[str, Any]) -> None:
        async def confirm_delete_async(_e: ft.ControlEvent) -> None:
            if not self.server_bridge:
                show_error_message(self.page, SERVER_NOT_CONNECTED_MESSAGE)
                self.page.close(delete_dialog)
                return

            client_id = client.get("id")
            if not client_id or not isinstance(client_id, str):
                show_error_message(self.page, "Invalid client ID")
                self.page.close(delete_dialog)
                return

            result = await run_sync_in_executor(
                safe_server_call, self.server_bridge, "delete_client", client_id
            )

            if result.get("success"):
                show_success_message(self.page, f"Client {client.get('name')} deleted")
                await self.load_clients_data()
            else:
                show_error_message(self.page, f"Failed to delete: {result.get('error', 'Unknown error')}")

            self.page.close(delete_dialog)

        async def confirm_delete(event: ft.ControlEvent) -> None:
            await self._run_with_loading(confirm_delete_async, event)

        delete_dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text(
                f"Are you sure you want to delete {client.get('name', 'this client')}?\n\nThis action cannot be undone."
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: self.page.close(delete_dialog)),
                ft.FilledButton(
                    "Delete", on_click=confirm_delete, style=ft.ButtonStyle(bgcolor=ft.Colors.RED)
                ),
            ],
        )
        self.page.open(delete_dialog)

    def add_client(self) -> None:
        name_field = ft.TextField(label="Client Name", hint_text="Enter client name")
        ip_field = ft.TextField(label="IP Address", hint_text="Enter IP address")
        status_dropdown = ft.Dropdown(
            label="Status",
            value="Disconnected",
            options=[
                ft.dropdown.Option("Connected"),
                ft.dropdown.Option("Disconnected"),
                ft.dropdown.Option("Connecting"),
            ],
        )

        async def save_client_async(_e: ft.ControlEvent) -> None:
            if not name_field.value or not name_field.value.strip():
                show_error_message(self.page, "Client name is required")
                return

            new_client = {
                "id": f"client-{str(uuid.uuid4())[:8]}",
                "name": name_field.value.strip(),
                "ip_address": ip_field.value.strip() if ip_field.value else "Unknown",
                "status": status_dropdown.value,
                "files_count": 0,
                "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            if not self.server_bridge:
                show_error_message(self.page, SERVER_NOT_CONNECTED_MESSAGE)
                return

            result = await run_sync_in_executor(
                safe_server_call, self.server_bridge, "add_client", new_client
            )

            if result.get("success"):
                show_success_message(self.page, f"Client {new_client['name']} added")
                await self.load_clients_data()
                self.page.close(add_dialog)
            else:
                show_error_message(self.page, f"Failed to add client: {result.get('error', 'Unknown error')}")

        async def save_client(event: ft.ControlEvent) -> None:
            await self._run_with_loading(save_client_async, event)

        add_dialog = ft.AlertDialog(
            title=ft.Text("Add New Client"),
            content=ft.Column([name_field, ip_field, status_dropdown], height=200, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: self.page.close(add_dialog)),
                ft.FilledButton("Add", on_click=save_client),
            ],
        )
        self.page.open(add_dialog)

    def edit_client(self, client: dict[str, Any]) -> None:
        name_field = ft.TextField(
            label="Client Name", value=client.get("name", ""), hint_text="Enter client name"
        )
        ip_field = ft.TextField(
            label="IP Address", value=client.get("ip_address", ""), hint_text="Enter IP address"
        )
        status_dropdown = ft.Dropdown(
            label="Status",
            value=client.get("status", "Disconnected"),
            options=[
                ft.dropdown.Option("Connected"),
                ft.dropdown.Option("Disconnected"),
                ft.dropdown.Option("Connecting"),
            ],
        )

        async def save_changes_async(_e: ft.ControlEvent) -> None:
            if not name_field.value or not name_field.value.strip():
                show_error_message(self.page, "Client name is required")
                return

            updated_client = {
                **client,
                "name": name_field.value.strip(),
                "ip_address": ip_field.value.strip()
                if ip_field.value
                else client.get("ip_address", "Unknown"),
                "status": status_dropdown.value,
                "last_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            if not self.server_bridge:
                show_error_message(self.page, SERVER_NOT_CONNECTED_MESSAGE)
                return

            client_id = updated_client.get("id") or client.get("id")
            if client_id is None:
                show_error_message(self.page, "Selected client has no ID; cannot update.")
                return

            result = await run_sync_in_executor(
                safe_server_call,
                self.server_bridge,
                "update_client",
                str(client_id),
                {"name": updated_client["name"]},
            )

            if result.get("success"):
                show_success_message(self.page, f"Client {updated_client['name']} updated")
                await self.load_clients_data()
                self.page.close(edit_dialog)
            else:
                show_error_message(
                    self.page, f"Failed to update client: {result.get('error', 'Unknown error')}"
                )

        async def save_changes(event: ft.ControlEvent) -> None:
            await self._run_with_loading(save_changes_async, event)

        edit_dialog = ft.AlertDialog(
            title=ft.Text(f"Edit Client: {client.get('name', 'Unknown')}"),
            content=ft.Column([name_field, ip_field, status_dropdown], height=200, scroll=ft.ScrollMode.AUTO),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _e: self.page.close(edit_dialog)),
                ft.FilledButton("Save", on_click=save_changes),
            ],
        )
        self.page.open(edit_dialog)

    def get_status_type(self, status: str) -> str:
        status_mapping = {
            "connected": "success",
            "disconnected": "error",
            "connecting": "warning",
            "registered": "registered",
            "offline": "offline",
            "error": "error",
            "unknown": "unknown",
        }
        return status_mapping.get(status.lower(), "default")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_client_row(self, client: dict[str, Any]) -> ft.DataRow:
        status = client.get("status", "Unknown")
        return ft.DataRow(
            cells=[
                ft.DataCell(ft.Text(str(client.get("id", "")))),
                ft.DataCell(ft.Text(str(client.get("name", "")))),
                ft.DataCell(create_status_pill(status, self.get_status_type(status))),
                ft.DataCell(ft.Text(str(client.get("last_seen", "")))),
                ft.DataCell(ft.Text(str(client.get("files_count", 0)))),
                ft.DataCell(
                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_VERT,
                        items=[
                            ft.PopupMenuItem(
                                text="View Details",
                                icon=ft.Icons.INFO,
                                on_click=lambda _e, c=client: self.view_client_details(c),
                            ),
                            ft.PopupMenuItem(
                                text="Edit",
                                icon=ft.Icons.EDIT,
                                on_click=lambda _e, c=client: self.edit_client(c),
                            ),
                            ft.PopupMenuItem(
                                text="Disconnect",
                                icon=ft.Icons.LOGOUT,
                                on_click=lambda _e, c=client: self.disconnect_client(c),
                            ),
                            ft.PopupMenuItem(
                                text="Delete",
                                icon=ft.Icons.DELETE,
                                on_click=lambda _e, c=client: self.delete_client(c),
                            ),
                        ],
                    )
                ),
            ]
        )

    def _show_loading(self) -> None:
        self.loading_ring.visible = True
        self.loading_ring.update()

    def _hide_loading(self) -> None:
        self.loading_ring.visible = False
        self.loading_ring.update()

    async def _run_with_loading(
        self,
        handler: Callable[[ft.ControlEvent], Awaitable[None]],
        event: ft.ControlEvent,
    ) -> None:
        try:
            self._show_loading()
            if hasattr(self.page, "run_task"):
                await self._await_if_needed(self.page.run_task(handler, event))
            else:
                await handler(event)
        finally:
            self._hide_loading()

    async def _await_if_needed(self, maybe_awaitable: Any) -> None:
        if maybe_awaitable is None:
            return

        if asyncio.iscoroutine(maybe_awaitable):
            await maybe_awaitable
            return

        if isinstance(maybe_awaitable, (asyncio.Task, asyncio.Future)):
            await maybe_awaitable
            return

        if isinstance(maybe_awaitable, concurrent.futures.Future):
            loop = asyncio.get_running_loop()
            await asyncio.wrap_future(maybe_awaitable, loop=loop)
            return

        awaitable = getattr(maybe_awaitable, "__await__", None)
        if callable(awaitable):
            await maybe_awaitable


# ==============================================================================
# MAIN VIEW
# All logic is organized within create_clients_view as nested functions
# ==============================================================================

# Note: Helper builders moved to FletV2.utils.ui_builders module


def create_clients_view(
    server_bridge: ServerBridge | None,
    page: ft.Page,
    _state_manager: SimpleState | None,
    global_search: ft.Control | None = None,
) -> Any:
    """Assemble the clients view using the controller abstraction."""
    logger.info("Creating simplified clients view")

    controller = _ClientsViewController(server_bridge, page, _state_manager, global_search)

    if _state_manager is not None:

        def _handle_state_clients(new_value: Any, _old_value: Any) -> None:
            if isinstance(new_value, list):
                controller.apply_clients_data(new_value, broadcast=False, source="state_manager")

        controller.state_subscription_callback = _handle_state_clients
        with contextlib.suppress(Exception):
            _state_manager.subscribe("clients", controller.state_subscription_callback)

    return controller.build()
