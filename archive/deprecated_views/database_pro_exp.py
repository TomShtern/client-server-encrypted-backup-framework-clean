#!/usr/bin/env python3
"""Compatibility helpers for the legacy `database_pro_exp` test surface."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

# Project requirement – must be first import for reliable UTF-8 I/O on Windows.
import Shared.utils.utf8_solution as _  # noqa: F401
from FletV2.utils.async_helpers import run_sync_in_executor, safe_server_call
from FletV2.views.database_pro import (
    MAX_DISPLAY_LENGTH,
    SENSITIVE_FIELDS,
)
from FletV2.views.database_pro import (
    create_database_view as _create_database_view,
)


def create_database_view(*args: Any, **kwargs: Any):  # pragma: no cover - thin wrapper
    """Expose the modern view under the historical function name."""
    return _create_database_view(*args, **kwargs)


# ---------------------------------------------------------------------------
# Pure helpers revived for test compatibility
# ---------------------------------------------------------------------------

def _value_matches_query(value: Any, lowered_query: str) -> bool:
    if value is None:
        return False

    text = str(value)
    lowered_value = text.lower()
    if lowered_value == lowered_query:
        return True

    return lowered_query in lowered_value.split()


def filter_records_by_query(records: Iterable[dict[str, Any]], query: str | None) -> list[dict[str, Any]]:
    if not query:
        return [dict(record) for record in records]

    lowered = query.lower()
    return [
        dict(record)
        for record in records
        if any(_value_matches_query(value, lowered) for value in record.values())
    ]


def sanitize_sensitive_fields(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    sanitized: list[dict[str, Any]] = []
    for record in records:
        clone = dict(record)
        for field in SENSITIVE_FIELDS:
            if field in clone:
                clone[field] = "REDACTED"
        sanitized.append(clone)
    return sanitized


def _truncate_value(value: Any) -> Any:
    if isinstance(value, str) and len(value) > MAX_DISPLAY_LENGTH:
        return f"{value[:MAX_DISPLAY_LENGTH]}..."
    return value


def transform_for_display(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    transformed: list[dict[str, Any]] = []
    for record in records:
        clone = {key: _truncate_value(val) for key, val in record.items()}
        transformed.append(clone)
    return transformed


def prepare_records_for_export(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return transform_for_display(sanitize_sensitive_fields(records))


def get_record_id_field(_table_name: str) -> str:
    # Historical implementation always defaulted to "id" for supported tables.
    return "id"


_TABLE_REQUIRED_FIELDS = {
    "clients": {"id", "name"},
    "files": {"id", "name", "client_id"},
}


def validate_record_data(table_name: str, record: dict[str, Any]) -> tuple[bool, str]:
    required = _TABLE_REQUIRED_FIELDS.get(table_name.lower())
    if not required:
        return True, ""

    missing = [field for field in required if not record.get(field)]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, ""


def sort_records(records: Iterable[dict[str, Any]], field: str, ascending: bool = True) -> list[dict[str, Any]]:
    snapshot = [dict(record) for record in records]
    if not snapshot or field not in snapshot[0]:
        return snapshot

    def _key(item: dict[str, Any]) -> tuple[bool, Any]:
        value = item.get(field)
        return (value is None, value)

    try:
        return sorted(snapshot, key=_key, reverse=not ascending)
    except Exception:  # pragma: no cover - defensive guard
        return snapshot


# ---------------------------------------------------------------------------
# Async helpers mirroring historical behaviour
# ---------------------------------------------------------------------------

async def fetch_database_info_async(server_bridge: Any | None) -> dict[str, Any]:
    if not server_bridge:
        return {"success": False, "error": "No server bridge", "data": None}
    return await run_sync_in_executor(safe_server_call, server_bridge, "get_database_info")


async def fetch_table_data_async(server_bridge: Any | None, table_name: str) -> dict[str, Any]:
    if not server_bridge:
        return {"success": False, "error": "No server bridge", "data": None}
    return await run_sync_in_executor(safe_server_call, server_bridge, "get_table_data", table_name)


__all__ = [
    "create_database_view",
    "fetch_database_info_async",
    "fetch_table_data_async",
    "filter_records_by_query",
    "get_record_id_field",
    "prepare_records_for_export",
    "sanitize_sensitive_fields",
    "sort_records",
    "transform_for_display",
    "validate_record_data",
]
