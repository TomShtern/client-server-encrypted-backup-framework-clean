"""
Purpose: Log monitoring & system tracking
Logic: Log parsing, monitoring, and system tracking
No UI: Pure business logic for monitoring operations
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
import threading

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[WARNING] psutil not available - system monitoring will use basic fallback")


@dataclass
class SystemMetrics:
    """System performance metrics data structure"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    process_count: int = 0
    uptime_seconds: float = 0


@dataclass
class LogEntry:
    """Log entry data structure for monitoring"""
    timestamp: datetime
    level: str
    message: str
    component: str
    metadata: Optional[Dict[str, Any]] = None


class BasicSystemMonitor:
    """Basic system monitoring service for backup server operations"""
    
    def __init__(self, log_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize system monitoring service
        
        Args:
            log_callback: Optional callback for logging messages
        """
        self.log_callback = log_callback or print
        self._monitoring_active = False
        self._monitoring_task = None
        self._start_time = time.time()
        self._last_network_stats = None
        self._metrics_history: List[SystemMetrics] = []
        self._max_history = 100  # Keep last 100 metrics entries
        
        # Initialize network baseline if psutil available
        if PSUTIL_AVAILABLE:
            try:
                self._last_network_stats = psutil.net_io_counters()
            except Exception as e:
                self.log_callback(f"[MONITOR] Could not initialize network stats: {e}")
    
    async def start_monitoring(self, interval_seconds: int = 30) -> bool:
        """
        Start continuous system monitoring
        
        Args:
            interval_seconds: Monitoring check interval in seconds
            
        Returns:
            bool: True if monitoring started successfully
        """
        if self._monitoring_active:
            self.log_callback("[MONITOR] Monitoring already active")
            return True
            
        try:
            self._monitoring_active = True
            self._monitoring_task = asyncio.create_task(self._monitoring_loop(interval_seconds))
            self.log_callback(f"[MONITOR] System monitoring started (interval: {interval_seconds}s)")
            return True
        except Exception as e:
            self.log_callback(f"[MONITOR] Failed to start monitoring: {e}")
            self._monitoring_active = False
            return False
    
    async def stop_monitoring(self) -> bool:
        """
        Stop the monitoring process
        
        Returns:
            bool: True if stopped successfully
        """
        if not self._monitoring_active:
            return True
            
        try:
            self._monitoring_active = False
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
            self.log_callback("[MONITOR] System monitoring stopped")
            return True
        except Exception as e:
            self.log_callback(f"[MONITOR] Error stopping monitoring: {e}")
            return False
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is currently active"""
        return self._monitoring_active
    
    async def _monitoring_loop(self, interval_seconds: int) -> None:
        """Main monitoring loop"""
        while self._monitoring_active:
            try:
                metrics = self._collect_system_metrics()
                self._add_metrics_to_history(metrics)
                self._log_metrics(metrics)
                
                # Check for alerts
                self._check_resource_alerts(metrics)
                
                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log_callback(f"[MONITOR] Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """
        Collect current system metrics
        
        Returns:
            SystemMetrics: Current system performance data
        """
        timestamp = datetime.now()
        uptime = time.time() - self._start_time
        
        if PSUTIL_AVAILABLE:
            try:
                cpu_percent = psutil.cpu_percent(interval=1.0)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Get disk usage for root/main drive
                try:
                    disk_usage = psutil.disk_usage('/')
                    disk_percent = disk_usage.percent
                except:
                    # Fallback for Windows
                    try:
                        disk_usage = psutil.disk_usage('C:\\')
                        disk_percent = disk_usage.percent
                    except:
                        disk_percent = 0.0
                
                # Network stats
                network_io = psutil.net_io_counters()
                network_sent = network_io.bytes_sent
                network_recv = network_io.bytes_recv
                
                # Process count
                process_count = len(psutil.pids())
                
            except Exception as e:
                self.log_callback(f"[MONITOR] Error collecting psutil metrics: {e}")
                # Fallback to basic metrics
                cpu_percent = 0.0
                memory_percent = 0.0 
                disk_percent = 0.0
                network_sent = 0
                network_recv = 0
                process_count = 0
        else:
            # Basic fallback when psutil not available
            cpu_percent = 0.0
            memory_percent = 0.0
            disk_percent = 0.0
            network_sent = 0
            network_recv = 0
            process_count = 0
        
        return SystemMetrics(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent, 
            disk_percent=disk_percent,
            network_bytes_sent=network_sent,
            network_bytes_recv=network_recv,
            process_count=process_count,
            uptime_seconds=uptime
        )
    
    def _add_metrics_to_history(self, metrics: SystemMetrics) -> None:
        """Add metrics to history and maintain size limit"""
        self._metrics_history.append(metrics)
        if len(self._metrics_history) > self._max_history:
            self._metrics_history.pop(0)  # Remove oldest entry
    
    def _log_metrics(self, metrics: SystemMetrics) -> None:
        """Log system metrics"""
        if PSUTIL_AVAILABLE:
            message = (
                f"System Stats: CPU {metrics.cpu_percent:.1f}%, "
                f"Memory {metrics.memory_percent:.1f}%, "
                f"Disk {metrics.disk_percent:.1f}%, "
                f"Processes {metrics.process_count}, "
                f"Uptime {metrics.uptime_seconds/3600:.1f}h"
            )
        else:
            message = f"System monitoring active - Uptime {metrics.uptime_seconds/3600:.1f}h (basic mode)"
        
        self.log_callback(f"[MONITOR] {message}")
    
    def _check_resource_alerts(self, metrics: SystemMetrics) -> None:
        """Check for resource usage alerts"""
        if not PSUTIL_AVAILABLE:
            return
            
        # Alert thresholds
        if metrics.cpu_percent > 90:
            self.log_callback(f"[MONITOR] HIGH CPU USAGE: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > 90:
            self.log_callback(f"[MONITOR] HIGH MEMORY USAGE: {metrics.memory_percent:.1f}%")
        
        if metrics.disk_percent > 95:
            self.log_callback(f"[MONITOR] HIGH DISK USAGE: {metrics.disk_percent:.1f}%")
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics"""
        if self._metrics_history:
            return self._metrics_history[-1]
        return None
    
    def get_metrics_history(self, count: int = 10) -> List[SystemMetrics]:
        """
        Get recent metrics history
        
        Args:
            count: Number of recent entries to return
            
        Returns:
            List of recent SystemMetrics
        """
        return self._metrics_history[-count:] if self._metrics_history else []
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for the monitoring session
        
        Returns:
            Dictionary with summary statistics
        """
        if not self._metrics_history:
            return {"status": "no_data", "message": "No metrics collected yet"}
        
        recent_metrics = self._metrics_history[-10:]  # Last 10 entries
        
        if PSUTIL_AVAILABLE and recent_metrics:
            avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
            avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
            avg_disk = sum(m.disk_percent for m in recent_metrics) / len(recent_metrics)
            
            return {
                "status": "active" if self._monitoring_active else "stopped",
                "total_entries": len(self._metrics_history),
                "uptime_hours": (time.time() - self._start_time) / 3600,
                "average_cpu": round(avg_cpu, 1),
                "average_memory": round(avg_memory, 1), 
                "average_disk": round(avg_disk, 1),
                "psutil_available": True
            }
        else:
            return {
                "status": "active" if self._monitoring_active else "stopped",
                "total_entries": len(self._metrics_history),
                "uptime_hours": (time.time() - self._start_time) / 3600,
                "psutil_available": False,
                "message": "Running in basic mode without detailed system metrics"
            }