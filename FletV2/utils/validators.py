#!/usr/bin/env python3
"""
Common validator functions for Settings forms and other inputs.
Extracted from views/settings.py for reuse and maintainability.
"""

from __future__ import annotations

from collections.abc import Callable

from config import MAX_PORT, MIN_PORT


def validate_port(value: str) -> tuple[bool, str]:
    try:
        port = int(value)
        if port < MIN_PORT:
            return False, f"Port must be at least {MIN_PORT} (system reserved)"
        elif port > MAX_PORT:
            return False, f"Port cannot exceed {MAX_PORT}"
        if port in {80, 443}:
            return True, f"⚠️ Port {port} may require administrator privileges"
        return True, ""
    except ValueError:
        return False, "Please enter a valid number"


def validate_max_clients(value: str) -> tuple[bool, str]:
    try:
        clients = int(value)
        if clients < 1:
            return False, "Must be at least 1"
        elif clients > 1000:
            return False, "Cannot exceed 1000 clients"
        elif clients > 100:
            return True, "⚠️ High client count may impact performance"
        return True, ""
    except ValueError:
        return False, "Please enter a valid number"


def validate_monitoring_interval(value: str) -> tuple[bool, str]:
    try:
        interval = int(value)
        if interval < 1 or interval > 60:
            return False, "Interval must be between 1 and 60 seconds"
        elif interval < 2:
            return True, "⚠️ Very frequent monitoring may impact performance"
        return True, ""
    except ValueError:
        return False, "Please enter a valid number"


def validate_file_size(value: str) -> tuple[bool, str]:
    try:
        size = int(value)
        if size < 1024:
            return False, "File size must be at least 1KB (1024 bytes)"
        elif size > 1073741824:
            return False, "File size cannot exceed 1GB"
        return True, ""
    except ValueError:
        return False, "Please enter a valid number"


def validate_timeout(value: str) -> tuple[bool, str]:
    try:
        timeout = int(value)
        if timeout < 1:
            return False, "Timeout must be at least 1 second"
        elif timeout > 3600:
            return False, "Timeout cannot exceed 1 hour (3600 seconds)"
        return True, ""
    except ValueError:
        return False, "Please enter a valid number"

# Registry for validator lookup by name
VALIDATORS: dict[str, Callable[[str], tuple[bool, str]]] = {
    "validate_port": validate_port,
    "validate_max_clients": validate_max_clients,
    "validate_monitoring_interval": validate_monitoring_interval,
    "validate_file_size": validate_file_size,
    "validate_timeout": validate_timeout,
}
