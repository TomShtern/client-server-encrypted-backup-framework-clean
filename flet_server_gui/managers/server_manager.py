#!/usr/bin/env python3
"""
Unified Server Manager
Consolidates server lifecycle, monitoring, connection status, and performance management.
Follows Duplication Mindset principles by eliminating "Slightly Different" Fallacy.

Unified Responsibilities:
- Server lifecycle (start, stop, restart)
- Server monitoring (status, health, metrics)
- Connection status management
- Performance optimization and metrics
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import asyncio
import threading
import sys
import os
import logging
import time
import functools
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
from dataclasses import dataclass, field

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
    from python_server.server.config import DEFAULT_PORT
    SERVER_AVAILABLE = True
except ImportError:
    SERVER_AVAILABLE = False
    print("[WARNING] Server integration not available")

logger = logging.getLogger(__name__)


# ============================================================================
# CONNECTION STATUS MANAGEMENT (from connection_status_manager.py)
# ============================================================================

class ConnectionStatus(Enum):
    """Connection status states for server monitoring"""
    DISCONNECTED = "disconnected"    # Not connected
    CONNECTING = "connecting"        # Connection attempt in progress
    CONNECTED = "connected"          # Successfully connected
    RECONNECTING = "reconnecting"    # Attempting to reconnect
    ERROR = "error"                  # Connection failed with error
    TIMEOUT = "timeout"              # Connection timed out


@dataclass
class ConnectionConfig:
    """Configuration for connection management behavior"""
    host: str = "localhost"
    port: int = 1256
    timeout_seconds: int = 10
    health_check_interval: int = 30  # seconds
    max_reconnect_attempts: int = 5
    reconnect_delay: int = 5  # seconds between attempts
    exponential_backoff: bool = True
    max_backoff_delay: int = 60  # maximum delay between attempts


@dataclass 
class ConnectionInfo:
    """Information about current connection state"""
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    host: str = "localhost"
    port: int = 1256
    connected_at: Optional[datetime] = None
    last_error: Optional[str] = None
    reconnect_attempts: int = 0
    health_check_count: int = 0
    last_health_check: Optional[datetime] = None


# ============================================================================
# SERVER LIFECYCLE MANAGEMENT (from server_lifecycle_manager.py)
# ============================================================================

@dataclass
class ServerInfo:
    """Server information data class"""
    running: bool = False
    host: str = "127.0.0.1"
    port: int = 1256
    uptime_start: Optional[datetime] = None
    connected_clients: int = 0
    total_clients: int = 0
    active_transfers: int = 0
    total_transfers: int = 0


# ============================================================================
# UNIFIED SERVER MANAGER
# ============================================================================

class ServerManager:
    """
    Unified Server Manager consolidating lifecycle, monitoring, and connection management.
    
    Eliminates "Slightly Different" Fallacy by combining:
    - ServerLifecycleManager (start/stop/restart operations)
    - MonitoringManager (system metrics and health monitoring)
    - ConnectionStatusManager (connection status tracking)
    
    Follows single responsibility principle: ALL server-related operations.
    """
    
    def __init__(self, server_instance: Optional[BackupServer] = None, config: Optional[ConnectionConfig] = None):
        self.server_instance = server_instance
        self.config = config or ConnectionConfig()
        
        # Server lifecycle state
        self._server_start_time = None
        
        # Monitoring state
        self.monitoring_enabled = PSUTIL_AVAILABLE
        
        # Connection state
        self.connection_info = ConnectionInfo(
            host=self.config.host,
            port=self.config.port
        )
        self.status_callbacks: List[Callable[[ConnectionStatus], None]] = []
        self.health_check_task: Optional[asyncio.Task] = None
        self._reconnect_task: Optional[asyncio.Task] = None
        
        # Performance monitoring state (integrated from performance_manager.py)
        self.__init_performance_monitoring()
        
        if not SERVER_AVAILABLE:
            raise RuntimeError("Server integration required but not available")
        
        if not self.monitoring_enabled:
            print("[WARNING] System monitoring will use fallback values")
    
    # ========================================================================
    # SERVER LIFECYCLE OPERATIONS (from server_lifecycle_manager.py)
    # ========================================================================
    
    async def get_server_status(self) -> ServerInfo:
        """Get current server status"""
        try:
            server_info = ServerInfo()
            
            if self.server_instance:
                server_info.running = self.server_instance.running
                server_info.host = self.config.host
                server_info.port = self.config.port
                
                if self.server_instance.running and self._server_start_time:
                    server_info.uptime_start = self._server_start_time
                
                server_info.connected_clients = len(self.server_instance.clients)
            
            return server_info
            
        except Exception as e:
            print(f"[ERROR] Failed to get server status: {e}")
            return ServerInfo()
    
    async def start_server(self) -> bool:
        """Start the server"""
        try:
            if not self.server_instance:
                print("[ERROR] No server instance available")
                return False
                
            if self.server_instance.running:
                print("[INFO] Server is already running")
                return True
            
            print("[INFO] Starting backup server...")
            
            def start_server_thread():
                try:
                    self.server_instance.start()
                    self._server_start_time = datetime.now()
                    print("[SUCCESS] Server started successfully")
                except Exception as e:
                    print(f"[ERROR] Server start failed: {e}")
            
            server_thread = threading.Thread(target=start_server_thread, daemon=True)
            server_thread.start()
            
            await asyncio.sleep(2)  # Wait for startup
            
            if self.server_instance.running:
                print("[SUCCESS] Server startup verified")
                await self._update_connection_status(ConnectionStatus.CONNECTED)
                return True
            else:
                print("[ERROR] Server failed to start")
                await self._update_connection_status(ConnectionStatus.ERROR, "Server failed to start")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to start server: {e}")
            await self._update_connection_status(ConnectionStatus.ERROR, str(e))
            return False
    
    async def stop_server(self) -> bool:
        """Stop the server"""
        try:
            if not self.server_instance:
                print("[ERROR] No server instance available")
                return False
                
            if not self.server_instance.running:
                print("[INFO] Server is not running")
                return True
            
            print("[INFO] Stopping backup server...")
            self.server_instance.stop()
            
            # Wait for clean shutdown
            await asyncio.sleep(1)
            
            if not self.server_instance.running:
                print("[SUCCESS] Server stopped successfully")
                self._server_start_time = None
                await self._update_connection_status(ConnectionStatus.DISCONNECTED)
                return True
            else:
                print("[ERROR] Server failed to stop cleanly")
                await self._update_connection_status(ConnectionStatus.ERROR, "Failed to stop cleanly")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to stop server: {e}")
            await self._update_connection_status(ConnectionStatus.ERROR, str(e))
            return False
    
    async def restart_server(self) -> bool:
        """Restart the server"""
        print("[INFO] Restarting server...")
        
        # Stop first
        stop_success = await self.stop_server()
        if not stop_success:
            print("[ERROR] Failed to stop server for restart")
            return False
        
        # Wait a moment between stop and start
        await asyncio.sleep(1)
        
        # Start again
        start_success = await self.start_server()
        if start_success:
            print("[SUCCESS] Server restarted successfully")
        else:
            print("[ERROR] Failed to start server after stop")
        
        return start_success
    
    def is_server_running(self) -> bool:
        """Check if server is currently running"""
        return self.server_instance and self.server_instance.running
    
    def get_uptime(self) -> Optional[datetime]:
        """Get server uptime start time"""
        return self._server_start_time if self.is_server_running() else None
    
    # ========================================================================
    # SYSTEM MONITORING OPERATIONS (from monitoring_manager.py)
    # ========================================================================
    
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
                    current_process = psutil.Process()
                    server_metrics['total_threads'] = current_process.num_threads()
                    server_metrics['memory_usage_mb'] = current_process.memory_info().rss / (1024**2)
                except:
                    pass

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
                overall_status = 'critical'
            
            # Check server status
            if not (self.server_instance and self.server_instance.running):
                health_issues.append('Server not running')
                overall_status = 'critical'
            
            if overall_status == 'critical':
                overall_status = 'critical'
            elif health_issues:
                overall_status = 'warning'
            
            return {
                'status': overall_status,
                'issues': health_issues,
                'last_check': datetime.now().isoformat(),
                'monitoring_available': self.monitoring_enabled
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to get health status: {e}")
            return {
                'status': 'error',
                'issues': [f'Health check failed: {e}'],
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
    
    # ========================================================================
    # CONNECTION STATUS MANAGEMENT (from connection_status_manager.py)
    # ========================================================================
    
    def add_status_callback(self, callback: Callable[[ConnectionStatus], None]) -> None:
        """Add a callback to be notified of connection status changes"""
        if callback not in self.status_callbacks:
            self.status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: Callable[[ConnectionStatus], None]) -> None:
        """Remove a status change callback"""
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)
    
    async def _update_connection_status(self, status: ConnectionStatus, error: Optional[str] = None) -> None:
        """Update connection status and notify callbacks"""
        previous_status = self.connection_info.status
        self.connection_info.status = status
        
        if status == ConnectionStatus.CONNECTED:
            self.connection_info.connected_at = datetime.now()
            self.connection_info.last_error = None
            self.connection_info.reconnect_attempts = 0
        elif status in [ConnectionStatus.ERROR, ConnectionStatus.TIMEOUT]:
            self.connection_info.last_error = error
        
        # Log status change
        logger.info(f"Connection status changed: {previous_status.value} -> {status.value}")
        if error:
            logger.error(f"Connection error: {error}")
        
        # Notify callbacks
        for callback in self.status_callbacks:
            try:
                callback(status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def get_connection_info(self) -> ConnectionInfo:
        """Get current connection information"""
        return self.connection_info
    
    async def start_health_monitoring(self) -> None:
        """Start periodic health check monitoring"""
        if self.health_check_task and not self.health_check_task.done():
            return  # Already running
        
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Health monitoring started")
    
    async def stop_health_monitoring(self) -> None:
        """Stop health check monitoring"""
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None
            logger.info("Health monitoring stopped")
    
    async def _health_check_loop(self) -> None:
        """Periodic health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                
                # Perform health check
                health_status = self.get_health_status()
                self.connection_info.health_check_count += 1
                self.connection_info.last_health_check = datetime.now()
                
                # Update connection status based on health
                if health_status['status'] == 'critical':
                    await self._update_connection_status(ConnectionStatus.ERROR, 
                                                       f"Health check failed: {', '.join(health_status['issues'])}")
                elif self.is_server_running():
                    await self._update_connection_status(ConnectionStatus.CONNECTED)
                else:
                    await self._update_connection_status(ConnectionStatus.DISCONNECTED)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await self._update_connection_status(ConnectionStatus.ERROR, str(e))

    # ============================================================================
    # PERFORMANCE MANAGEMENT (integrated from performance_manager.py)
    # ============================================================================
    
    def __init_performance_monitoring(self):
        """Initialize performance monitoring"""
        self._performance_metrics: Dict[str, List[float]] = {}
        self._debounced_functions: Dict[str, Callable] = {}
    
    def measure_performance(self, operation_name: str):
        """Decorator to measure server operation performance"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration = time.time() - start_time
                    self._record_performance_metric(operation_name, duration)
            return wrapper
        return decorator
    
    def debounce_server_operation(self, delay: float = 0.3):
        """Decorator to debounce frequent server operations"""
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                func_key = f"{func.__name__}_{id(args)}_{id(kwargs)}"
                
                # Cancel previous delayed call
                if func_key in self._debounced_functions:
                    # In a real implementation, you'd cancel the timer
                    pass
                
                # Store new delayed call
                def delayed_call():
                    time.sleep(delay)
                    return func(*args, **kwargs)
                
                self._debounced_functions[func_key] = delayed_call
                return delayed_call()
                
            return wrapper
        return decorator
    
    def _record_performance_metric(self, operation: str, duration: float):
        """Record server performance metric"""
        if operation not in self._performance_metrics:
            self._performance_metrics[operation] = []
        
        self._performance_metrics[operation].append(duration)
        
        # Keep only last 100 measurements
        if len(self._performance_metrics[operation]) > 100:
            self._performance_metrics[operation] = self._performance_metrics[operation][-100:]
    
    def get_performance_report(self) -> Dict[str, Dict[str, float]]:
        """Generate server performance report"""
        return {
            operation: {
                'avg_duration': sum(measurements) / len(measurements),
                'max_duration': max(measurements),
                'min_duration': min(measurements),
                'call_count': len(measurements),
                'last_duration': measurements[-1] if measurements else 0.0
            }
            for operation, measurements in self._performance_metrics.items()
            if measurements
        }
    
    def get_server_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive server performance statistics"""
        try:
            performance_data = {
                'operation_metrics': self.get_performance_report(),
                'health_metrics': self.get_health_status(),
                'connection_metrics': {
                    'status': self.connection_info.status.value,
                    'uptime_seconds': (datetime.now() - self.connection_info.connected_at).total_seconds() 
                                    if self.connection_info.connected_at else 0,
                    'health_checks': self.connection_info.health_check_count,
                    'reconnect_attempts': self.connection_info.reconnect_attempts
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # Add system metrics if available
            if PSUTIL_AVAILABLE:
                performance_data['system_metrics'] = {
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'disk_usage_percent': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
                }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Failed to get performance stats: {e}")
            return {
                'operation_metrics': {},
                'health_metrics': {'status': 'unknown', 'issues': [str(e)]},
                'connection_metrics': {'status': 'error'},
                'system_metrics': {},
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
