"""
Lightweight Transfer Performance Monitor
- Tracks per-job transfer speed, moving averages, peaks, and simple stall detection
- Thread-safe in-process analytics for API and WebSocket reporting

No external deps beyond stdlib and psutil (already in requirements).
"""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from datetime import datetime


@dataclass
class Sample:
    ts: float
    bytes_transferred: Optional[int] = None
    total_bytes: Optional[int] = None
    speed_bps: Optional[float] = None  # bytes/second
    phase: Optional[str] = None


@dataclass
class JobStats:
    job_id: str
    total_bytes: Optional[int] = None
    start_ts: float = field(default_factory=time.time)
    last_ts: float = field(default_factory=time.time)
    last_progress_bytes: int = 0
    last_speed_bps: float = 0.0
    peak_speed_bps: float = 0.0
    avg_speed_bps: float = 0.0      # arithmetic mean
    ema_speed_bps: float = 0.0      # exponential moving average
    ema_alpha: float = 0.2          # smoothing factor
    samples: List[Sample] = field(default_factory=list)
    stalled_since: Optional[float] = None

    def record(self, s: Sample):
        self.samples.append(s)
        self.last_ts = s.ts
        if s.total_bytes is not None:
            self.total_bytes = s.total_bytes
        if s.speed_bps is not None:
            self.last_speed_bps = max(0.0, float(s.speed_bps))
            self.peak_speed_bps = max(self.peak_speed_bps, self.last_speed_bps)
            # arithmetic mean
            if self.avg_speed_bps == 0.0:
                self.avg_speed_bps = self.last_speed_bps
            else:
                n = len([x for x in self.samples if x.speed_bps is not None])
                self.avg_speed_bps = ((self.avg_speed_bps * (n - 1)) + self.last_speed_bps) / n
            # EMA
            if self.ema_speed_bps == 0.0:
                self.ema_speed_bps = self.last_speed_bps
            else:
                a = self.ema_alpha
                self.ema_speed_bps = a * self.last_speed_bps + (1 - a) * self.ema_speed_bps

        # Stall detection (no bytes change across samples for > 3s)
        if s.bytes_transferred is not None:
            if s.bytes_transferred == self.last_progress_bytes:
                if self.stalled_since is None:
                    self.stalled_since = s.ts
            else:
                self.stalled_since = None
                self.last_progress_bytes = s.bytes_transferred

    def summarize(self) -> Dict:
        now = time.time()
        elapsed = max(0.0, now - self.start_ts)
        last_update_age = now - self.last_ts
        total = self.total_bytes or 0
        done = min(self.last_progress_bytes, total) if total else self.last_progress_bytes
        pct = (done / total * 100.0) if total else None

        # ETA from EMA speed if possible
        if total and self.ema_speed_bps > 1:
            remaining = max(0, total - done)
            eta_sec = remaining / self.ema_speed_bps
        else:
            eta_sec = None

        # Trend heuristic over last few samples
        speeds = [x.speed_bps for x in self.samples[-5:] if x.speed_bps is not None]
        trend = "unknown"
        if len(speeds) >= 2:
            if speeds[-1] > speeds[0] * 1.2:
                trend = "increasing"
            elif speeds[-1] < speeds[0] * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"

        # Bottleneck insight heuristic (safe language)
        bottleneck = None
        if self.stalled_since and (now - self.stalled_since) > 3.0:
            bottleneck = "possible_stall"
        elif self.ema_speed_bps and self.ema_speed_bps < 256 * 1024:  # < 256 KB/s
            bottleneck = "slow_throughput"

        return {
            "job_id": self.job_id,
            "elapsed_seconds": round(elapsed, 2),
            "last_update_age": round(last_update_age, 2),
            "total_bytes": total,
            "bytes_transferred": done,
            "progress_pct": round(pct, 2) if pct is not None else None,
            "last_speed_bps": int(self.last_speed_bps),
            "avg_speed_bps": int(self.avg_speed_bps),
            "ema_speed_bps": int(self.ema_speed_bps),
            "peak_speed_bps": int(self.peak_speed_bps),
            "eta_seconds": int(eta_sec) if eta_sec is not None else None,
            "trend": trend,
            "insight": bottleneck,
        }


class PerformanceMonitor:
    def __init__(self):
        self._jobs: Dict[str, JobStats] = {}
        self._lock = threading.RLock()

    def start_job(self, job_id: str, total_bytes: Optional[int] = None):
        with self._lock:
            if job_id not in self._jobs:
                self._jobs[job_id] = JobStats(job_id=job_id, total_bytes=total_bytes)
            else:
                # reset for reuse
                js = self._jobs[job_id]
                js.total_bytes = total_bytes
                js.start_ts = time.time()
                js.last_ts = js.start_ts
                js.last_progress_bytes = 0
                js.last_speed_bps = 0.0
                js.peak_speed_bps = 0.0
                js.avg_speed_bps = 0.0
                js.ema_speed_bps = 0.0
                js.samples.clear()
                js.stalled_since = None

    def record_sample(
        self,
        job_id: str,
        bytes_transferred: Optional[int] = None,
        total_bytes: Optional[int] = None,
        speed_bps: Optional[float] = None,
        phase: Optional[str] = None,
    ):
        with self._lock:
            if job_id not in self._jobs:
                self._jobs[job_id] = JobStats(job_id=job_id, total_bytes=total_bytes)
            s = Sample(
                ts=time.time(),
                bytes_transferred=bytes_transferred,
                total_bytes=total_bytes,
                speed_bps=speed_bps,
                phase=phase,
            )
            self._jobs[job_id].record(s)

    def get_job_summary(self, job_id: str) -> Optional[Dict]:
        with self._lock:
            js = self._jobs.get(job_id)
            return js.summarize() if js else None

    def get_all_summaries(self) -> Dict[str, Dict]:
        with self._lock:
            return {jid: js.summarize() for jid, js in self._jobs.items()}


# Global singleton
_monitor_instance: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = PerformanceMonitor()
    return _monitor_instance

