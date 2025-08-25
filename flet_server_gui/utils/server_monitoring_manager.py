#!/usr/bin/env python3
"""
Server Monitoring Manager
Handles system metrics, performance monitoring, and health checks.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[WARNING] psutil not available - system monitoring disabled")

try:
    from python_server.server.server import BackupServer
    SERVER_AVAILABLE = True
except ImportError:
    SERVER_AVAILABLE = False
    print("[WARNING] Server integration not available")


class ServerMonitoringManager:
    """Manages system monitoring and performance metrics"""
    
    def __init__(self, server_instance: Optional[BackupServer] = None):
        self.server_instance = server_instance
        self.monitoring_enabled = PSUTIL_AVAILABLE
        
        if not self.monitoring_enabled:
            print("[WARNING] System monitoring will use fallback values")
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        try:
            if not self.monitoring_enabled:
                return self._get_fallback_system_metrics()
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_total = memory.total / (1024**3)  # GB
            memory_used = memory.used / (1024**3)  # GB
            memory_percent = memory.percent
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_total = disk.total / (1024**3)  # GB
            disk_used = disk.used / (1024**3)  # GB
            disk_percent = (disk.used / disk.total) * 100
            
            # Network metrics
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent / (1024**2)  # MB
            network_recv = network.bytes_recv / (1024**2)  # MB
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': round(cpu_percent, 1),
                    'count': cpu_count
                },
                'memory': {
                    'total_gb': round(memory_total, 2),
                    'used_gb': round(memory_used, 2),
                    'percent': round(memory_percent, 1),
                    'available_gb': round((memory.total - memory.used) / (1024**3), 2)
                },
                'disk': {
                    'total_gb': round(disk_total, 2),
                    'used_gb': round(disk_used, 2),
                    'percent': round(disk_percent, 1),
                    'free_gb': round((disk.total - disk.used) / (1024**3), 2)
                },
                'network': {
                    'sent_mb': round(network_sent, 2),
                    'recv_mb': round(network_recv, 2)
                }
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get system metrics: {e}")
            return self._get_fallback_system_metrics()
    
    def get_server_performance_metrics(self) -> Dict[str, Any]:
        """Get server-specific performance metrics"""
        try:
            base_metrics = self.get_system_metrics()
            
            # Add server-specific metrics
            server_metrics = {
                'server_status': 'running' if (self.server_instance and self.server_instance.running) else 'stopped',
                'active_connections': len(self.server_instance.clients) if self.server_instance else 0,
                'total_threads': 0,
                'memory_usage_mb': 0
            }
            
            if self.monitoring_enabled:
                try:
                    # Get current process info
                    process = psutil.Process()
                    server_metrics.update({
                        'total_threads': process.num_threads(),
                        'memory_usage_mb': round(process.memory_info().rss / (1024**2), 2)
                    })
                except Exception as e:
                    print(f"[WARNING] Could not get process metrics: {e}")
            
            # Combine system and server metrics
            return {
                **base_metrics,
                'server': server_metrics
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get server performance metrics: {e}")
            return self._get_fallback_server_metrics()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            metrics = self.get_system_metrics()
            
            # Determine health based on thresholds
            health_issues = []
            overall_status = 'healthy'
            
            # Check CPU
            if metrics['cpu']['percent'] > 80:
                health_issues.append('High CPU usage')
                overall_status = 'warning'
            
            # Check Memory
            if metrics['memory']['percent'] > 85:
                health_issues.append('High memory usage')
                overall_status = 'warning'
            
            # Check Disk
            if metrics['disk']['percent'] > 90:
                health_issues.append('Low disk space')
                if overall_status == 'healthy':
                    overall_status = 'warning'
            
            # Check server status
            if not (self.server_instance and self.server_instance.running):
                health_issues.append('Server not running')
                overall_status = 'critical'
            
            return {
                'status': overall_status,
                'issues': health_issues,
                'last_check': datetime.now().isoformat(),
                'monitoring_available': self.monitoring_enabled
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get health status: {e}")
            return {
                'status': 'unknown',
                'issues': ['Monitoring system error'],
                'last_check': datetime.now().isoformat(),
                'monitoring_available': False
            }
    
    def _get_fallback_system_metrics(self) -> Dict[str, Any]:
        """Get fallback metrics when psutil is unavailable"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {'percent': 0.0, 'count': 1},
            'memory': {'total_gb': 8.0, 'used_gb': 4.0, 'percent': 50.0, 'available_gb': 4.0},
            'disk': {'total_gb': 100.0, 'used_gb': 50.0, 'percent': 50.0, 'free_gb': 50.0},
            'network': {'sent_mb': 0.0, 'recv_mb': 0.0},
            'monitoring_note': 'Fallback values - psutil not available'
        }
    
    def _get_fallback_server_metrics(self) -> Dict[str, Any]:
        """Get fallback server metrics when monitoring fails"""
        base = self._get_fallback_system_metrics()
        base['server'] = {
            'server_status': 'unknown',
            'active_connections': 0,
            'total_threads': 0,
            'memory_usage_mb': 0
        }
        return base
    
    def is_monitoring_available(self) -> bool:
        """Check if system monitoring is available"""
        return self.monitoring_enabled
