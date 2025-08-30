"""
Server Control Actions

Pure business logic for server operations, independent of UI concerns.
"""

from typing import Dict, Any, Optional
from .base_action import BaseAction, ActionResult
import asyncio
import time


class ServerActions(BaseAction):
    """
    Handles all server control and monitoring operations.
    
    This class encapsulates server management logic without UI dependencies,
    making it easily testable and reusable.
    """
    
    async def start_server(self) -> ActionResult:
        """
        Start the backup server with comprehensive error handling.
        
        Returns:
            ActionResult with server start outcome
        """
        try:
            # Check if server is already running
            status = await self.server_bridge.get_server_status()
            if status and getattr(status, 'running', False):
                return ActionResult.make_error(
                    error_message="Server is already running",
                    error_code="SERVER_ALREADY_RUNNING"
                )

            # Attempt to start server
            success = await self.server_bridge.start_server()

            if not success:
                return ActionResult.error_result(
                    error_message="Failed to start server",
                    error_code="START_COMMAND_FAILED"
                )

            # Wait a moment and verify server actually started
            await asyncio.sleep(1)
            status = await self.server_bridge.get_server_status()

            return (
                ActionResult.make_success(
                    data={
                        'action': 'start_server',
                        'server_status': 'running',
                        'host': getattr(status, 'host', 'unknown'),
                        'port': getattr(status, 'port', 'unknown'),
                    },
                    metadata={
                        'operation_type': 'server_control',
                        'timestamp': time.time(),
                    },
                )
                if status and getattr(status, 'running', False)
                else ActionResult.error_result(
                    error_message="Server start command succeeded but server is not running",
                    error_code="START_VERIFICATION_FAILED",
                )
            )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error starting server: {str(e)}",
                error_code="START_EXCEPTION"
            )
    
    async def stop_server(self) -> ActionResult:
        """
        Stop the backup server gracefully.
        
        Returns:
            ActionResult with server stop outcome
        """
        try:
            # Check if server is actually running
            status = await self.server_bridge.get_server_status()
            if not status or not getattr(status, 'running', False):
                return ActionResult.error_result(
                    error_message="Server is not currently running",
                    error_code="SERVER_NOT_RUNNING"
                )

            # Attempt to stop server
            success = await self.server_bridge.stop_server()

            if not success:
                return ActionResult.error_result(
                    error_message="Failed to stop server",
                    error_code="STOP_COMMAND_FAILED"
                )

            # Wait a moment and verify server actually stopped
            await asyncio.sleep(1)
            status = await self.server_bridge.get_server_status()

            return (
                ActionResult.make_success(
                    data={'action': 'stop_server', 'server_status': 'stopped'},
                    metadata={
                        'operation_type': 'server_control',
                        'timestamp': time.time(),
                    },
                )
                if not status or not getattr(status, 'running', False)
                else ActionResult.error_result(
                    error_message="Server stop command succeeded but server is still running",
                    error_code="STOP_VERIFICATION_FAILED",
                )
            )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error stopping server: {str(e)}",
                error_code="STOP_EXCEPTION"
            )
    
    async def restart_server(self) -> ActionResult:
        """
        Restart the backup server (stop then start).
        
        Returns:
            ActionResult with server restart outcome
        """
        try:
            # Stop server first
            stop_result = await self.stop_server()
            
            # If stop failed and it's not because server wasn't running, abort
            if not stop_result.success and stop_result.error_code != "SERVER_NOT_RUNNING":
                return ActionResult.error_result(
                    error_message=f"Restart failed during stop: {stop_result.error_message}",
                    error_code="RESTART_STOP_FAILED"
                )
            
            # Wait a moment between stop and start
            await asyncio.sleep(2)
            
            # Start server
            start_result = await self.start_server()
            
            if start_result.success:
                return ActionResult.make_success(
                    data={
                        'action': 'restart_server',
                        'server_status': 'running',
                        'stop_result': stop_result.success,
                        'start_result': start_result.success
                    },
                    metadata={
                        'operation_type': 'server_control',
                        'timestamp': time.time()
                    }
                )
            else:
                return ActionResult.error_result(
                    error_message=f"Restart failed during start: {start_result.error_message}",
                    error_code="RESTART_START_FAILED"
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error restarting server: {str(e)}",
                error_code="RESTART_EXCEPTION"
            )
    
    async def get_server_status(self) -> ActionResult:
        """
        Get comprehensive server status information.
        
        Returns:
            ActionResult with detailed server status
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
                
                return ActionResult.make_success(
                    data=status_data,
                    metadata={
                        'operation_type': 'server_status',
                        'timestamp': time.time()
                    }
                )
            else:
                return ActionResult.error_result(
                    error_message="Unable to retrieve server status",
                    error_code="STATUS_UNAVAILABLE"
                )
                
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting server status: {str(e)}",
                error_code="STATUS_EXCEPTION"
            )
    
    async def get_server_health(self) -> ActionResult:
        """
        Perform comprehensive server health check.
        
        Returns:
            ActionResult with health check results
        """
        try:
            health_data = {
                'overall_status': 'healthy',
                'checks': {}
            }

            # Check server status
            status_result = await self.get_server_status()
            if status_result.success:
                health_data['checks']['server_running'] = {
                    'status': 'pass' if status_result.data.get('running') else 'fail',
                    'message': 'Server is running' if status_result.data.get('running') else 'Server is not running'
                }
            else:
                health_data['checks']['server_running'] = {
                    'status': 'fail',
                    'message': f"Could not check server status: {status_result.error_message}"
                }

            # Check database connectivity (if available)
            try:
                db_check = await self.server_bridge.check_database_connection()
                health_data['checks']['database'] = {
                    'status': 'pass' if db_check else 'fail',
                    'message': 'Database accessible' if db_check else 'Database connection failed'
                }
            except Exception:
                health_data['checks']['database'] = {
                    'status': 'unknown',
                    'message': 'Database check not available'
                }

            # Check disk space (if available)
            try:
                disk_usage = await self.server_bridge.get_disk_usage()
                if disk_usage and disk_usage.get('percent_used', 0) < 90:
                    health_data['checks']['disk_space'] = {
                        'status': 'pass',
                        'message': f"Disk usage: {disk_usage.get('percent_used', 0)}%"
                    }
                else:
                    health_data['checks']['disk_space'] = {
                        'status': 'warning',
                        'message': f"High disk usage: {disk_usage.get('percent_used', 0) if disk_usage else 'unknown'}%"
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

            return ActionResult.make_success(
                data=health_data,
                metadata={
                    'operation_type': 'health_check',
                    'timestamp': time.time(),
                    'total_checks': len(health_data['checks']),
                    'failed_checks': len(failed_checks),
                    'warning_checks': len(warning_checks)
                }
            )

        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Health check failed: {str(e)}",
                error_code="HEALTH_CHECK_EXCEPTION"
            )

    async def get_client_details(self, client_id: str) -> ActionResult:
        """
        Get detailed information about a specific client through server bridge.
        
        Args:
            client_id: Unique identifier for the client
            
        Returns:
            ActionResult with client details
        """
        try:
            client_data = await self.server_bridge.get_client_details(client_id)
            if client_data:
                return ActionResult.make_success(
                    data=client_data,
                    metadata={'client_id': client_id, 'operation_type': 'client_details'}
                )
            else:
                return ActionResult.error_result(
                    error_message=f"Client {client_id} not found",
                    error_code="CLIENT_NOT_FOUND"
                )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting client details for {client_id}: {str(e)}",
                error_code="CLIENT_DETAILS_EXCEPTION"
            )

    async def get_file_list(self) -> ActionResult:
        """
        Get list of all files from the server.
        
        Returns:
            ActionResult with file list
        """
        try:
            files = await self.server_bridge.get_file_list()
            return ActionResult.make_success(
                data=files,
                metadata={
                    'file_count': len(files),
                    'operation_type': 'file_list'
                }
            )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting file list: {str(e)}",
                error_code="FILE_LIST_EXCEPTION"
            )

    async def get_client_list(self) -> ActionResult:
        """
        Get list of all clients from the server.
        
        Returns:
            ActionResult with client list
        """
        try:
            clients = await self.server_bridge.get_client_list()
            return ActionResult.make_success(
                data=clients,
                metadata={
                    'client_count': len(clients),
                    'operation_type': 'client_list'
                }
            )
        except Exception as e:
            return ActionResult.error_result(
                error_message=f"Error getting client list: {str(e)}",
                error_code="CLIENT_LIST_EXCEPTION"
            )