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
from typing import Dict, Optional, Tuple


@dataclass
class ConnStats:
    client_addr: Tuple[str, int]
    client_id_hex: str = ""
    opened_ts: float = field(default_factory=time.time)
    last_read_ts: float = field(default_factory=time.time)
    last_write_ts: float = field(default_factory=time.time)
    bytes_in: int = 0
    bytes_out: int = 0
    read_errors: int = 0
    write_errors: int = 0
    partial_clears: int = 0
    closed_ts: Optional[float] = None
    last_error: Optional[str] = None

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

    def summary(self) -> Dict:
        now = time.time()
        return {
            "client": f"{self.client_addr[0]}:{self.client_addr[1]}",
            "client_id": self.client_id_hex,
            "uptime_sec": int((self.closed_ts or now) - self.opened_ts),
            "idle_read_sec": int(now - self.last_read_ts),
            "idle_write_sec": int(now - self.last_write_ts),
            "bytes_in": self.bytes_in,
            "bytes_out": self.bytes_out,
            "read_errors": self.read_errors,
            "write_errors": self.write_errors,
            "partial_clears": self.partial_clears,
            "last_error": self.last_error,
            "closed": self.closed_ts is not None,
        }


class ConnectionHealthMonitor:
    def __init__(self):
        self._lock = threading.RLock()
        self._stats: Dict[int, ConnStats] = {}

    def open_conn(self, fd: int, client_addr: Tuple[str, int]):
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

    def get_summary(self) -> Dict[int, Dict]:
        with self._lock:
            return {fd: cs.summary() for fd, cs in self._stats.items()}

    def get_conn(self, fd: int) -> Optional[Dict]:
        with self._lock:
            cs = self._stats.get(fd)
            return cs.summary() if cs else None


# Global singleton used by server
_monitor_instance: Optional[ConnectionHealthMonitor] = None


def get_connection_health_monitor() -> ConnectionHealthMonitor:
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = ConnectionHealthMonitor()
    return _monitor_instance

