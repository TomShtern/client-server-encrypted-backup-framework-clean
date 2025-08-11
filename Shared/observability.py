#!/usr/bin/env python3
"""
Enhanced Observability Framework for CyberBackup 3.0
Provides structured logging, metrics collection, and comprehensive monitoring
"""

import json
import time
import threading
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from enum import Enum
import psutil
import os
from contextlib import suppress


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


class LogLevel(Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


@dataclass
class StructuredLogEntry:
    """Structured log entry with consistent fields"""
    timestamp: str
    level: str
    component: str
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    operation: Optional[str] = None
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class Metric:
    """Metric data point"""
    name: str
    type: MetricType
    value: float
    timestamp: float
    tags: Dict[str, str] = field(default_factory=dict)
    unit: Optional[str] = None


@dataclass
class SystemMetrics:
    """System-level metrics snapshot"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    disk_free_gb: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    open_files: int


class StructuredLogger:
    """Enhanced structured logger with context management"""
    
    def __init__(self, component: str, base_logger: logging.Logger):
        self.component = component
        self.base_logger = base_logger
        self.context: Dict[str, Any] = {}
        self.trace_id: Optional[str] = None
        self.span_id: Optional[str] = None
        
    def with_context(self, **kwargs) -> 'StructuredLogger':
        """Create a new logger with additional context"""
        new_logger = StructuredLogger(self.component, self.base_logger)
        new_logger.context = {**self.context, **kwargs}
        new_logger.trace_id = self.trace_id
        new_logger.span_id = self.span_id
        return new_logger
        
    def with_trace(self, trace_id: str, span_id: Optional[str] = None) -> 'StructuredLogger':
        """Create a new logger with tracing information"""
        new_logger = StructuredLogger(self.component, self.base_logger)
        new_logger.context = self.context.copy()
        new_logger.trace_id = trace_id
        new_logger.span_id = span_id or trace_id
        return new_logger
        
    def _log(self, level: LogLevel, message: str, **kwargs):
        """Internal logging method"""
        entry = StructuredLogEntry(
            timestamp=f"{datetime.now(timezone.utc).isoformat()}Z",
            level=level.value,
            component=self.component,
            message=message,
            context={**self.context, **kwargs.get('context', {})},
            trace_id=self.trace_id,
            span_id=self.span_id,
            user_id=kwargs.get('user_id'),
            session_id=kwargs.get('session_id'),
            operation=kwargs.get('operation'),
            duration_ms=kwargs.get('duration_ms'),
            error_code=kwargs.get('error_code'),
            tags=kwargs.get('tags', {})
        )
        
        # Log as JSON for structured parsing
        json_log = json.dumps(asdict(entry), default=str)
        
        # Also log human-readable format
        human_msg = f"[{self.component}] {message}"
        if self.trace_id:
            human_msg += f" [trace:{self.trace_id}]"
        if entry.context:
            human_msg += f" {entry.context}"
            
        # Send to appropriate log level
        if level in (LogLevel.TRACE, LogLevel.DEBUG):
            self.base_logger.debug(f"STRUCTURED: {json_log}")
            self.base_logger.debug(human_msg)
        elif level == LogLevel.INFO:
            self.base_logger.info(f"STRUCTURED: {json_log}")
            self.base_logger.info(human_msg)
        elif level == LogLevel.WARN:
            self.base_logger.warning(f"STRUCTURED: {json_log}")
            self.base_logger.warning(human_msg)
        elif level == LogLevel.ERROR:
            self.base_logger.error(f"STRUCTURED: {json_log}")
            self.base_logger.error(human_msg)
        elif level == LogLevel.FATAL:
            self.base_logger.critical(f"STRUCTURED: {json_log}")
            self.base_logger.critical(human_msg)
    
    def trace(self, message: str, **kwargs):
        self._log(LogLevel.TRACE, message, **kwargs)
        
    def debug(self, message: str, **kwargs):
        self._log(LogLevel.DEBUG, message, **kwargs)
        
    def info(self, message: str, **kwargs):
        self._log(LogLevel.INFO, message, **kwargs)
        
    def warn(self, message: str, **kwargs):
        self._log(LogLevel.WARN, message, **kwargs)
        
    def error(self, message: str, **kwargs):
        self._log(LogLevel.ERROR, message, **kwargs)
        
    def fatal(self, message: str, **kwargs):
        self._log(LogLevel.FATAL, message, **kwargs)


class MetricsCollector:
    """Thread-safe metrics collection and aggregation"""
    
    def __init__(self, max_history: int = 1000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.lock = threading.RLock()
        self.start_time = time.time()
        
    def record_counter(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """Record a counter metric (cumulative)"""
        metric = Metric(
            name=name,
            type=MetricType.COUNTER,
            value=value,
            timestamp=time.time(),
            tags=tags or {}
        )
        with self.lock:
            self.metrics[name].append(metric)
            
    def record_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Record a gauge metric (current value)"""
        metric = Metric(
            name=name,
            type=MetricType.GAUGE,
            value=value,
            timestamp=time.time(),
            tags=tags or {}
        )
        with self.lock:
            self.metrics[name].append(metric)
            
    def record_timer(self, name: str, duration_ms: float, tags: Optional[Dict[str, str]] = None):
        """Record a timer metric"""
        metric = Metric(
            name=name,
            type=MetricType.TIMER,
            value=duration_ms,
            timestamp=time.time(),
            tags=tags or {},
            unit="ms"
        )
        with self.lock:
            self.metrics[name].append(metric)
            
    def get_metric_summary(self, name: str, window_seconds: int = 300) -> Dict[str, Any]:
        """Get summary statistics for a metric within time window"""
        with self.lock:
            if name not in self.metrics:
                return {}
                
            now = time.time()
            cutoff = now - window_seconds
            recent_metrics = [m for m in self.metrics[name] if m.timestamp >= cutoff]
            
            if not recent_metrics:
                return {}
                
            values = [m.value for m in recent_metrics]
            return {
                "name": name,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "sum": sum(values),
                "latest": values[-1] if values else 0,
                "window_seconds": window_seconds,
                "timestamp": now
            }
            
    def get_all_summaries(self, window_seconds: int = 300) -> Dict[str, Dict[str, Any]]:
        """Get summaries for all metrics"""
        with self.lock:
            return {name: self.get_metric_summary(name, window_seconds) 
                   for name in self.metrics.keys()}


class SystemMonitor:
    """System-level metrics monitoring"""
    
    def __init__(self, collection_interval: float = 30.0):
        self.collection_interval = collection_interval
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.metrics_history: deque = deque(maxlen=1000)
        self.lock = threading.RLock()
        
    def start(self):
        """Start system monitoring"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop system monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            with suppress(Exception):
                metrics = self._collect_system_metrics()
                with self.lock:
                    self.metrics_history.append(metrics)
                
            time.sleep(self.collection_interval)
            
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1.0)
        memory = psutil.virtual_memory()
        
        # Disk usage for current directory
        disk = psutil.disk_usage('.')
        
        # Network stats
        net_io = psutil.net_io_counters()
        
        # Process stats
        current_process = psutil.Process()
        connections = len(current_process.connections())
        open_files = len(current_process.open_files())
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=memory.used / 1024 / 1024,
            disk_usage_percent=(disk.used / disk.total) * 100,
            disk_free_gb=disk.free / 1024 / 1024 / 1024,
            network_bytes_sent=net_io.bytes_sent,
            network_bytes_recv=net_io.bytes_recv,
            active_connections=connections,
            open_files=open_files
        )
        
    def get_latest_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics"""
        with self.lock:
            return self.metrics_history[-1] if self.metrics_history else None
            
    def get_metrics_history(self, window_seconds: int = 300) -> List[SystemMetrics]:
        """Get system metrics within time window"""
        cutoff = time.time() - window_seconds
        with self.lock:
            return [m for m in self.metrics_history if m.timestamp >= cutoff]


# Global instances
_metrics_collector: Optional[MetricsCollector] = None
_system_monitor: Optional[SystemMonitor] = None


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def get_system_monitor() -> SystemMonitor:
    """Get global system monitor instance"""
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    return _system_monitor


def create_structured_logger(component: str, base_logger: logging.Logger) -> StructuredLogger:
    """Create a structured logger for a component"""
    return StructuredLogger(component, base_logger)


# Context manager for operation timing
class TimedOperation:
    """Context manager for timing operations and recording metrics"""
    
    def __init__(self, operation_name: str, logger: StructuredLogger, 
                 tags: Optional[Dict[str, str]] = None):
        self.operation_name = operation_name
        self.logger = logger
        self.tags = tags or {}
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(f"Starting {self.operation_name}", 
                        operation=self.operation_name, tags=self.tags)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is None:
            # Should not happen in normal flow, but handle gracefully
            self.logger.error(f"Timer not properly initialized for {self.operation_name}")
            return
            
        duration_ms = (time.time() - self.start_time) * 1000
        
        # Record timing metric
        get_metrics_collector().record_timer(
            f"operation.{self.operation_name}.duration",
            duration_ms,
            self.tags
        )
        
        # Log completion
        if exc_type is None:
            self.logger.info(f"Completed {self.operation_name}", 
                           operation=self.operation_name,
                           duration_ms=duration_ms,
                           tags=self.tags)
        else:
            self.logger.error(f"Failed {self.operation_name}: {exc_val}",
                            operation=self.operation_name,
                            duration_ms=duration_ms,
                            error_code=exc_type.__name__,
                            tags=self.tags)
                          
