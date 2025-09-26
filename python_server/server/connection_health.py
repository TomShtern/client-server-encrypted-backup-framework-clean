"""
Connection Health Monitoring for the NetworkServer
- Tracks per-connection last activity, bytes in/out, errors, and lifetimes
- Provides lightweight stall detection and summary stats
- Pure server-side; no protocol changes required
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConnStats:
    client_addr: tuple[str, int]
    client_id_hex: str = ""
    opened_ts: float = field(default_factory=time.time)
    last_read_ts: float = field(default_factory=time.time)
    last_write_ts: float = field(default_factory=time.time)
    bytes_in: int = 0
    bytes_out: int = 0
    read_errors: int = 0
    write_errors: int = 0
    partial_clears: int = 0
    closed_ts: float | None = None
    last_error: str | None = None

    def heartbeat_read(self, n: int):
        now = time.time()
        self.last_read_ts = now
        if n > 0:
            self.bytes_in += n

    def heartbeat_write(self, n: int):
        now = time.time()
        self.last_write_ts = now
        if n > 0:
            self.bytes_out += n

    def mark_error(self, where: str, err: Exception):
        self.last_error = f"{where}: {err}"
        if where == "read":
            self.read_errors += 1
        elif where == "write":
            self.write_errors += 1

    def close(self):
        self.closed_ts = time.time()

    def summary(self) -> dict[str, Any]:
        """Return a summary dict of this connection's stats."""
        now = time.time()
        lifetime = (self.closed_ts or now) - self.opened_ts
        return {
            'client_addr': f"{self.client_addr[0]}:{self.client_addr[1]}",
            'client_id': self.client_id_hex,
            'lifetime': round(lifetime, 2),
            'bytes_in': self.bytes_in,
            'bytes_out': self.bytes_out,
            'errors': self.read_errors + self.write_errors,
            'last_error': self.last_error,
            'closed': self.closed_ts is not None
        }


class ConnectionHealthMonitor:
    def __init__(self):
        self._lock = threading.RLock()
        self._stats: dict[int, ConnStats] = {}

    def open_conn(self, fd: int, client_addr: tuple[str, int]):
        with self._lock:
            self._stats[fd] = ConnStats(client_addr=client_addr)

    def set_client_id(self, fd: int, client_id_hex: str):
        with self._lock:
            cs = self._stats.get(fd)
            if cs:
                cs.client_id_hex = client_id_hex

    def heartbeat_read(self, fd: int, n: int):
        with self._lock:
            cs = self._stats.get(fd)
            if cs:
                cs.heartbeat_read(n)

    def heartbeat_write(self, fd: int, n: int):
        with self._lock:
            cs = self._stats.get(fd)
            if cs:
                cs.heartbeat_write(n)

    def record_partial_clears(self, fd: int, count: int):
        with self._lock:
            cs = self._stats.get(fd)
            if cs and count > 0:
                cs.partial_clears += count

    def mark_error(self, fd: int, where: str, err: Exception):
        with self._lock:
            cs = self._stats.get(fd)
            if cs:
                cs.mark_error(where, err)

    def close_conn(self, fd: int):
        with self._lock:
            cs = self._stats.pop(fd, None)
            if cs:
                cs.close()
                # store closed stats under negative key to retain briefly? For now, drop.

    def get_summary(self) -> dict[int, dict]:
        with self._lock:
            return {fd: cs.summary() for fd, cs in self._stats.items()}

    def get_conn(self, fd: int) -> dict | None:
        with self._lock:
            cs = self._stats.get(fd)
            return cs.summary() if cs else None


# Global singleton used by server
_monitor_instance: ConnectionHealthMonitor | None = None


def get_connection_health_monitor() -> ConnectionHealthMonitor:
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = ConnectionHealthMonitor()
    return _monitor_instance

