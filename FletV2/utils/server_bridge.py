"""
Simplified ServerBridge - Clean drop-in replacement for the original 2,743-line version.
Preserves ALL functionality while removing over-engineering.

Reduces complexity from 2,743 lines to ~500 lines by:
- Simple delegation pattern instead of complex abstraction layers
- No artificial delays or complex retry mechanisms
- No persistent disk storage for mock data
- Direct method calls with basic fallback
- Clean error handling without complex hierarchies
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, Union, List
from pathlib import Path

from .mock_database_simulator import MockDatabase, get_mock_database

logger = logging.getLogger(__name__)

class ServerBridge:
    """
    Simplified ServerBridge that provides clean drop-in replacement capability.

    If real_server is provided, delegates to it. Otherwise uses MockDatabase for development.
    Maintains 100% compatibility with existing views while being dramatically simpler.
    """

    def __init__(self, real_server=None):
        """
        Initialize ServerBridge with optional real server instance.

        Args:
            real_server: Real server instance with methods like get_clients(), delete_file(), etc.
                        If None, uses MockDatabase for development/testing.
        """
        self.real_server = real_server
        self._mock_db = get_mock_database() if not real_server else None
        self._connection_status = "connected" if real_server else "mock_mode"

        logger.info(f"ServerBridge initialized in {'production' if real_server else 'mock'} mode")

    def is_connected(self) -> bool:
        """Check if server is connected."""
        if self.real_server:
            return hasattr(self.real_server, 'is_connected') and self.real_server.is_connected()
        return True  # Mock is always "connected"

    def _call_real_or_mock(self, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Helper to call real server method or fall back to mock."""
        try:
            if self.real_server and hasattr(self.real_server, method_name):
                result = getattr(self.real_server, method_name)(*args, **kwargs)
                # Normalize result format
                if isinstance(result, dict) and 'success' in result:
                    return result
                return {'success': True, 'data': result, 'error': None}
            else:
                # Use mock database
                mock_method = getattr(self._mock_db, method_name, None)
                if mock_method:
                    result = mock_method(*args, **kwargs)
                    return {'success': True, 'data': result, 'error': None}
                else:
                    return {'success': False, 'data': None, 'error': f'Method {method_name} not available'}

        except Exception as e:
            logger.error(f"Error in {method_name}: {e}")
            return {'success': False, 'data': None, 'error': str(e)}

    async def _call_real_or_mock_async(self, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Async version of _call_real_or_mock."""
        try:
            if self.real_server and hasattr(self.real_server, method_name):
                result = await getattr(self.real_server, method_name)(*args, **kwargs)
                # Normalize result format
                if isinstance(result, dict) and 'success' in result:
                    return result
                return {'success': True, 'data': result, 'error': None}
            else:
                # Use mock database async method
                async_method_name = f"{method_name}_async" if not method_name.endswith('_async') else method_name
                mock_method = getattr(self._mock_db, async_method_name, None)
                if mock_method:
                    result = await mock_method(*args, **kwargs)
                    return {'success': True, 'data': result, 'error': None}
                else:
                    # Try sync version
                    sync_method_name = method_name.replace('_async', '')
                    mock_method = getattr(self._mock_db, sync_method_name, None)
                    if mock_method:
                        result = mock_method(*args, **kwargs)
                        return {'success': True, 'data': result, 'error': None}
                    return {'success': False, 'data': None, 'error': f'Method {method_name} not available'}

        except Exception as e:
            logger.error(f"Error in {method_name}: {e}")
            return {'success': False, 'data': None, 'error': str(e)}

    # ============================================================================
    # CLIENT OPERATIONS
    # ============================================================================

    def get_all_clients_from_db(self):
        """Get all clients from database."""
        return self._call_real_or_mock('get_clients')

    def get_clients(self):
        """Get all clients (sync version)."""
        return self._call_real_or_mock('get_clients')

    async def get_clients_async(self):
        """Get all clients (async version)."""
        return await self._call_real_or_mock_async('get_clients_async')

    def get_client_details(self, client_id: str):
        """Get details for a specific client."""
        return self._call_real_or_mock('get_client_details', client_id)

    async def add_client_async(self, client_data: Dict[str, Any]):
        """Add a new client."""
        return await self._call_real_or_mock_async('add_client_async', client_data)

    def delete_client(self, client_id: str):
        """Delete a client (sync version)."""
        return self._call_real_or_mock('delete_client', client_id)

    async def delete_client_async(self, client_id: str):
        """Delete a client (async version)."""
        return await self._call_real_or_mock_async('delete_client_async', client_id)

    def disconnect_client(self, client_id: str):
        """Disconnect a specific client."""
        return self._call_real_or_mock('disconnect_client', client_id)

    async def disconnect_client_async(self, client_id: str):
        """Disconnect a specific client (async)."""
        return await self._call_real_or_mock_async('disconnect_client_async', client_id)

    def resolve_client(self, client_identifier: str):
        """Resolve client by ID or name."""
        return self._call_real_or_mock('resolve_client', client_identifier)

    # ============================================================================
    # FILE OPERATIONS
    # ============================================================================

    def get_client_files(self, client_id: str):
        """Get files for a specific client."""
        return self._call_real_or_mock('get_client_files', client_id)

    async def get_client_files_async(self, client_id: str):
        """Get files for a specific client (async)."""
        return await self._call_real_or_mock_async('get_client_files_async', client_id)

    def get_files(self):
        """Get all files."""
        return self._call_real_or_mock('get_files')

    async def get_files_async(self):
        """Get all files (async)."""
        return await self._call_real_or_mock_async('get_files_async')

    def delete_file(self, file_id: str):
        """Delete a file."""
        return self._call_real_or_mock('delete_file', file_id)

    async def delete_file_async(self, file_id: str):
        """Delete a file (async)."""
        return await self._call_real_or_mock_async('delete_file_async', file_id)

    def download_file(self, file_id: str, destination_path: str):
        """Download a file to destination."""
        return self._call_real_or_mock('download_file', file_id, destination_path)

    async def download_file_async(self, file_id: str, destination_path: str):
        """Download a file to destination (async)."""
        return await self._call_real_or_mock_async('download_file_async', file_id, destination_path)

    def verify_file(self, file_id: str):
        """Verify file integrity."""
        return self._call_real_or_mock('verify_file', file_id)

    async def verify_file_async(self, file_id: str):
        """Verify file integrity (async)."""
        return await self._call_real_or_mock_async('verify_file_async', file_id)

    # ============================================================================
    # DATABASE OPERATIONS
    # ============================================================================

    def get_database_info(self):
        """Get database information."""
        return self._call_real_or_mock('get_database_info')

    async def get_database_info_async(self):
        """Get database information (async)."""
        return await self._call_real_or_mock_async('get_database_info_async')

    def get_table_data(self, table_name: str):
        """Get data from a specific table."""
        return self._call_real_or_mock('get_table_data', table_name)

    async def get_table_data_async(self, table_name: str):
        """Get data from a specific table (async)."""
        return await self._call_real_or_mock_async('get_table_data_async', table_name)

    def update_row(self, table_name: str, row_id: str, updated_data: Dict[str, Any]):
        """Update a specific row."""
        return self._call_real_or_mock('update_row', table_name, row_id, updated_data)

    def delete_row(self, table_name: str, row_id: str):
        """Delete a specific row."""
        return self._call_real_or_mock('delete_row', table_name, row_id)

    @property
    def db_manager(self):
        """Database manager property for compatibility."""
        if self.real_server and hasattr(self.real_server, 'db_manager'):
            return self.real_server.db_manager
        return self._mock_db

    # ============================================================================
    # LOG OPERATIONS
    # ============================================================================

    def get_logs(self):
        """Get system logs."""
        return self._call_real_or_mock('get_logs')

    async def get_logs_async(self):
        """Get system logs (async)."""
        return await self._call_real_or_mock_async('get_logs_async')

    async def clear_logs_async(self):
        """Clear all logs."""
        return await self._call_real_or_mock_async('clear_logs_async')

    async def export_logs_async(self, export_format: str, filters: Optional[Dict[str, Any]] = None):
        """Export logs in specified format."""
        return await self._call_real_or_mock_async('export_logs_async', export_format, filters or {})

    async def get_log_statistics_async(self):
        """Get log statistics."""
        return await self._call_real_or_mock_async('get_log_statistics_async')

    async def stream_logs_async(self, callback):
        """Stream logs in real-time."""
        return await self._call_real_or_mock_async('stream_logs_async', callback)

    async def stop_log_stream_async(self, streaming_task):
        """Stop log streaming."""
        return await self._call_real_or_mock_async('stop_log_stream_async', streaming_task)

    # ============================================================================
    # SERVER STATUS & MONITORING
    # ============================================================================

    def get_server_status(self):
        """Get basic server status."""
        return self._call_real_or_mock('get_server_status')

    async def get_server_status_async(self):
        """Get basic server status (async)."""
        return await self._call_real_or_mock_async('get_server_status_async')

    def get_detailed_server_status(self):
        """Get comprehensive server status."""
        return self._call_real_or_mock('get_detailed_server_status')

    async def get_detailed_server_status_async(self):
        """Get comprehensive server status (async)."""
        return await self._call_real_or_mock_async('get_detailed_server_status_async')

    def get_server_health(self):
        """Get server health metrics."""
        return self._call_real_or_mock('get_server_health')

    async def get_server_health_async(self):
        """Get server health metrics (async)."""
        return await self._call_real_or_mock_async('get_server_health_async')

    async def start_server_async(self):
        """Start the server."""
        return await self._call_real_or_mock_async('start_server_async')

    async def stop_server_async(self):
        """Stop the server."""
        return await self._call_real_or_mock_async('stop_server_async')

    def test_connection(self):
        """Test server connection."""
        return self._call_real_or_mock('test_connection')

    async def test_connection_async(self):
        """Test server connection (async)."""
        return await self._call_real_or_mock_async('test_connection_async')

    # ============================================================================
    # ANALYTICS & SYSTEM
    # ============================================================================

    def get_system_status(self):
        """Get system status."""
        return self._call_real_or_mock('get_system_status')

    async def get_system_status_async(self):
        """Get system status (async)."""
        return await self._call_real_or_mock_async('get_system_status_async')

    def get_analytics_data(self):
        """Get analytics data."""
        return self._call_real_or_mock('get_analytics_data')

    async def get_analytics_data_async(self):
        """Get analytics data (async)."""
        return await self._call_real_or_mock_async('get_analytics_data_async')

    def get_performance_metrics(self):
        """Get performance metrics."""
        return self._call_real_or_mock('get_performance_metrics')

    async def get_performance_metrics_async(self):
        """Get performance metrics (async)."""
        return await self._call_real_or_mock_async('get_performance_metrics_async')

    def get_historical_data(self, metric: str, hours: int = 24):
        """Get historical performance data."""
        return self._call_real_or_mock('get_historical_data', metric, hours)

    async def get_historical_data_async(self, metric: str, hours: int = 24):
        """Get historical performance data (async)."""
        return await self._call_real_or_mock_async('get_historical_data_async', metric, hours)

    def get_dashboard_summary(self):
        """Get dashboard summary data."""
        return self._call_real_or_mock('get_dashboard_summary')

    async def get_dashboard_summary_async(self):
        """Get dashboard summary data (async)."""
        return await self._call_real_or_mock_async('get_dashboard_summary_async')

    def get_server_statistics(self):
        """Get detailed server statistics."""
        return self._call_real_or_mock('get_server_statistics')

    async def get_server_statistics_async(self):
        """Get detailed server statistics (async)."""
        return await self._call_real_or_mock_async('get_server_statistics_async')

    async def get_recent_activity_async(self, limit: int = 50):
        """Get recent system activity."""
        return await self._call_real_or_mock_async('get_recent_activity_async', limit)

    # ============================================================================
    # SETTINGS MANAGEMENT
    # ============================================================================

    async def save_settings_async(self, settings_data: Dict[str, Any]):
        """Save application settings."""
        return await self._call_real_or_mock_async('save_settings_async', settings_data)

    async def load_settings_async(self):
        """Load current settings."""
        return await self._call_real_or_mock_async('load_settings_async')

    async def validate_settings_async(self, settings_data: Dict[str, Any]):
        """Validate settings data."""
        return await self._call_real_or_mock_async('validate_settings_async', settings_data)

    async def backup_settings_async(self, backup_name: str, settings_data: Dict[str, Any]):
        """Create settings backup."""
        return await self._call_real_or_mock_async('backup_settings_async', backup_name, settings_data)

    async def restore_settings_async(self, backup_file: str):
        """Restore settings from backup."""
        return await self._call_real_or_mock_async('restore_settings_async', backup_file)

    async def get_default_settings_async(self):
        """Get default settings."""
        return await self._call_real_or_mock_async('get_default_settings_async')


# ============================================================================
# FACTORY FUNCTIONS (for compatibility with existing code)
# ============================================================================

def create_server_bridge(real_server=None):
    """
    Factory function to create ServerBridge instance.

    Args:
        real_server: Optional real server instance for production use

    Returns:
        ServerBridge instance configured for production or development
    """
    return ServerBridge(real_server)

def get_server_bridge():
    """Get or create a singleton ServerBridge instance for development."""
    if not hasattr(get_server_bridge, '_instance'):
        get_server_bridge._instance = ServerBridge()
    return get_server_bridge._instance