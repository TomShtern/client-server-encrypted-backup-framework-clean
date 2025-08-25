"""
Purpose: Core server operations and lifecycle management
Logic: Handles all server control, monitoring, and status operations including start/stop/restart, health checks, and performance metrics
UI: None - pure business logic
Dependencies: ServerBridge for server integration, typing for type hints, asyncio for async operations, time for timestamps
"""

import asyncio
import time
import sys
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

# Add project root to path for imports
project_root = os.path.join(os.path.dirname(__file__), "..", "..", "..")
sys.path.insert(0, project_root)

try:
    from python_server.server.server import BackupServer
    SERVER_AVAILABLE = True
except ImportError:
    SERVER_AVAILABLE = False


@dataclass
class ServerStatus:
    """Server status information"""
    running: bool = False
    host: str = "unknown"
    port: str = "unknown"
    connected_clients: int = 0
    uptime_start: Optional[str] = None
    version: str = "unknown"
    
    
@dataclass 
class HealthCheckResult:
    """Health check result information"""
    overall_status: str
    checks: Dict[str, Dict[str, str]]
    total_checks: int = 0
    failed_checks: int = 0
    warning_checks: int = 0


class ServerOperations:
    """
    Core server operations class handling all server lifecycle and monitoring.
    
    This class provides a clean interface for server management operations
    without UI dependencies, making it suitable for various client interfaces.
    """
    
    def __init__(self, server_bridge):
        """
        Initialize server operations with server bridge dependency.
        
        Args:
            server_bridge: Server integration interface
        """
        self.server_bridge = server_bridge
        
    async def start_server(self) -> Dict[str, Any]:
        """
        Start the backup server with comprehensive error handling.
        
        Returns:
            Dictionary containing operation result and server status
        """
        try:
            # Check if server is already running
            status = await self.get_server_status()
            if status.get('success') and status.get('data', {}).get('running'):
                return {
                    'success': False,
                    'error': 'Server is already running',
                    'error_code': 'SERVER_ALREADY_RUNNING'
                }
            
            # Attempt to start server
            success = await self.server_bridge.start_server()
            
            if success:
                # Wait a moment and verify server actually started
                await asyncio.sleep(1)
                status_check = await self.get_server_status()
                
                if status_check.get('success') and status_check.get('data', {}).get('running'):
                    return {
                        'success': True,
                        'data': {
                            'action': 'start_server',
                            'server_status': 'running',
                            'host': status_check.get('data', {}).get('host', 'unknown'),
                            'port': status_check.get('data', {}).get('port', 'unknown')
                        },
                        'metadata': {
                            'operation_type': 'server_control',
                            'timestamp': time.time()
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Server start command succeeded but server is not running',
                        'error_code': 'START_VERIFICATION_FAILED'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Failed to start server',
                    'error_code': 'START_COMMAND_FAILED'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error starting server: {str(e)}',
                'error_code': 'START_EXCEPTION'
            }
    
    async def stop_server(self) -> Dict[str, Any]:
        """
        Stop the backup server gracefully.
        
        Returns:
            Dictionary containing operation result
        """
        try:
            # Check if server is actually running
            status = await self.get_server_status()
            if not status.get('success') or not status.get('data', {}).get('running'):
                return {
                    'success': False,
                    'error': 'Server is not currently running',
                    'error_code': 'SERVER_NOT_RUNNING'
                }
            
            # Attempt to stop server
            success = await self.server_bridge.stop_server()
            
            if success:
                # Wait a moment and verify server actually stopped
                await asyncio.sleep(1)
                status_check = await self.get_server_status()
                
                if not status_check.get('success') or not status_check.get('data', {}).get('running'):
                    return {
                        'success': True,
                        'data': {
                            'action': 'stop_server',
                            'server_status': 'stopped'
                        },
                        'metadata': {
                            'operation_type': 'server_control',
                            'timestamp': time.time()
                        }
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Server stop command succeeded but server is still running',
                        'error_code': 'STOP_VERIFICATION_FAILED'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Failed to stop server',
                    'error_code': 'STOP_COMMAND_FAILED'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error stopping server: {str(e)}',
                'error_code': 'STOP_EXCEPTION'
            }
    
    async def restart_server(self) -> Dict[str, Any]:
        """
        Restart the backup server (stop then start).
        
        Returns:
            Dictionary containing operation result
        """
        try:
            # Stop server first
            stop_result = await self.stop_server()
            
            # If stop failed and it's not because server wasn't running, abort
            if not stop_result.get('success') and stop_result.get('error_code') != 'SERVER_NOT_RUNNING':
                return {
                    'success': False,
                    'error': f'Restart failed during stop: {stop_result.get("error")}',
                    'error_code': 'RESTART_STOP_FAILED'
                }
            
            # Wait a moment between stop and start
            await asyncio.sleep(2)
            
            # Start server
            start_result = await self.start_server()
            
            if start_result.get('success'):
                return {
                    'success': True,
                    'data': {
                        'action': 'restart_server',
                        'server_status': 'running',
                        'stop_result': stop_result.get('success'),
                        'start_result': start_result.get('success')
                    },
                    'metadata': {
                        'operation_type': 'server_control',
                        'timestamp': time.time()
                    }
                }
            else:
                return {
                    'success': False,
                    'error': f'Restart failed during start: {start_result.get("error")}',
                    'error_code': 'RESTART_START_FAILED'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error restarting server: {str(e)}',
                'error_code': 'RESTART_EXCEPTION'
            }
    
    async def get_server_status(self) -> Dict[str, Any]:
        """
        Get comprehensive server status information.
        
        Returns:
            Dictionary containing server status details
        """
        try:
            status = await self.server_bridge.get_server_status()
            
            if status:
                status_data = {
                    'running': getattr(status, 'running', False),
                    'host': getattr(status, 'host', 'unknown'),
                    'port': getattr(status, 'port', 'unknown'),
                    'connected_clients': getattr(status, 'connected_clients', 0),
                    'uptime_start': str(getattr(status, 'uptime_start', 'unknown')),
                    'version': getattr(status, 'version', 'unknown')
                }
                
                return {
                    'success': True,
                    'data': status_data,
                    'metadata': {
                        'operation_type': 'server_status',
                        'timestamp': time.time()
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Unable to retrieve server status',
                    'error_code': 'STATUS_UNAVAILABLE'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting server status: {str(e)}',
                'error_code': 'STATUS_EXCEPTION'
            }
    
    async def get_server_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive server health check.
        
        Returns:
            Dictionary containing health check results
        """
        try:
            health_data = {
                'overall_status': 'healthy',
                'checks': {}
            }
            
            # Check server status
            status_result = await self.get_server_status()
            if status_result.get('success'):
                health_data['checks']['server_running'] = {
                    'status': 'pass' if status_result.get('data', {}).get('running') else 'fail',
                    'message': 'Server is running' if status_result.get('data', {}).get('running') else 'Server is not running'
                }
            else:
                health_data['checks']['server_running'] = {
                    'status': 'fail',
                    'message': f'Could not check server status: {status_result.get("error")}'
                }
            
            # Check database connectivity (if available)
            try:
                if hasattr(self.server_bridge, 'check_database_connection'):
                    db_check = await self.server_bridge.check_database_connection()
                    health_data['checks']['database'] = {
                        'status': 'pass' if db_check else 'fail',
                        'message': 'Database accessible' if db_check else 'Database connection failed'
                    }
                else:
                    # Try to get database stats as a proxy for connectivity
                    db_stats = self.server_bridge.get_database_stats()
                    health_data['checks']['database'] = {
                        'status': 'pass' if db_stats else 'fail',
                        'message': 'Database accessible' if db_stats else 'Database connection failed'
                    }
            except Exception:
                health_data['checks']['database'] = {
                    'status': 'unknown',
                    'message': 'Database check not available'
                }
            
            # Check disk space (if available)
            try:
                if hasattr(self.server_bridge, 'get_disk_usage'):
                    disk_usage = await self.server_bridge.get_disk_usage()
                    if disk_usage and disk_usage.get('percent_used', 0) < 90:
                        health_data['checks']['disk_space'] = {
                            'status': 'pass',
                            'message': f'Disk usage: {disk_usage.get("percent_used", 0)}%'
                        }
                    else:
                        health_data['checks']['disk_space'] = {
                            'status': 'warning',
                            'message': f'High disk usage: {disk_usage.get("percent_used", 0) if disk_usage else "unknown"}%'
                        }
                else:
                    health_data['checks']['disk_space'] = {
                        'status': 'unknown',
                        'message': 'Disk space check not available'
                    }
            except Exception:
                health_data['checks']['disk_space'] = {
                    'status': 'unknown',
                    'message': 'Disk space check not available'
                }
            
            # Determine overall health
            failed_checks = [check for check in health_data['checks'].values() if check['status'] == 'fail']
            warning_checks = [check for check in health_data['checks'].values() if check['status'] == 'warning']
            
            if failed_checks:
                health_data['overall_status'] = 'unhealthy'
            elif warning_checks:
                health_data['overall_status'] = 'warning'
            else:
                health_data['overall_status'] = 'healthy'
            
            return {
                'success': True,
                'data': health_data,
                'metadata': {
                    'operation_type': 'health_check',
                    'timestamp': time.time(),
                    'total_checks': len(health_data['checks']),
                    'failed_checks': len(failed_checks),
                    'warning_checks': len(warning_checks)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Health check failed: {str(e)}',
                'error_code': 'HEALTH_CHECK_EXCEPTION'
            }

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system performance metrics.
        
        Returns:
            Dictionary containing system metrics
        """
        try:
            if hasattr(self.server_bridge, 'monitoring_manager'):
                return self.server_bridge.monitoring_manager.get_system_metrics()
            else:
                return {
                    'cpu_percent': 0,
                    'memory_percent': 0,
                    'disk_usage': 0,
                    'network_io': {'bytes_sent': 0, 'bytes_recv': 0},
                    'available': False
                }
        except Exception as e:
            return {
                'error': str(e),
                'available': False
            }
    
    def get_server_performance_metrics(self) -> Dict[str, Any]:
        """
        Get server-specific performance metrics.
        
        Returns:
            Dictionary containing server performance metrics
        """
        try:
            if hasattr(self.server_bridge, 'monitoring_manager'):
                return self.server_bridge.monitoring_manager.get_server_performance_metrics()
            else:
                return {
                    'active_connections': 0,
                    'requests_per_minute': 0,
                    'average_response_time': 0,
                    'error_rate': 0,
                    'available': False
                }
        except Exception as e:
            return {
                'error': str(e),
                'available': False
            }
    
    async def get_client_details(self, client_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific client through server operations.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            Dictionary containing client details
        """
        try:
            if hasattr(self.server_bridge, 'get_client_details'):
                client_data = await self.server_bridge.get_client_details(client_id)
            else:
                # Fallback to getting all clients and filtering
                all_clients = self.server_bridge.get_all_clients()
                client_data = next((c for c in all_clients if getattr(c, 'client_id', None) == client_id), None)
            
            if client_data:
                return {
                    'success': True,
                    'data': client_data if isinstance(client_data, dict) else client_data.__dict__,
                    'metadata': {'client_id': client_id, 'operation_type': 'client_details'}
                }
            else:
                return {
                    'success': False,
                    'error': f'Client {client_id} not found',
                    'error_code': 'CLIENT_NOT_FOUND'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting client details for {client_id}: {str(e)}',
                'error_code': 'CLIENT_DETAILS_EXCEPTION'
            }

    async def get_file_list(self) -> Dict[str, Any]:
        """
        Get list of all files from the server.
        
        Returns:
            Dictionary containing file list
        """
        try:
            files = self.server_bridge.get_all_files()
            return {
                'success': True,
                'data': files,
                'metadata': {
                    'file_count': len(files) if files else 0,
                    'operation_type': 'file_list'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting file list: {str(e)}',
                'error_code': 'FILE_LIST_EXCEPTION'
            }

    async def get_client_list(self) -> Dict[str, Any]:
        """
        Get list of all clients from the server.
        
        Returns:
            Dictionary containing client list
        """
        try:
            clients = self.server_bridge.get_all_clients()
            return {
                'success': True,
                'data': clients,
                'metadata': {
                    'client_count': len(clients) if clients else 0,
                    'operation_type': 'client_list'
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error getting client list: {str(e)}',
                'error_code': 'CLIENT_LIST_EXCEPTION'
            }

    def is_monitoring_available(self) -> bool:
        """Check if server monitoring is available."""
        return hasattr(self.server_bridge, 'monitoring_manager') and \
               hasattr(self.server_bridge.monitoring_manager, 'is_monitoring_available') and \
               self.server_bridge.monitoring_manager.is_monitoring_available()
    
    def is_real_integration(self) -> bool:
        """Check if using real server integration."""
        return hasattr(self.server_bridge, 'is_real_integration') and \
               self.server_bridge.is_real_integration()