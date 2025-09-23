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
import uuid
from typing import Any, Dict, Optional, List, Callable

from .mock_database_simulator import MockDatabase, get_mock_database
from .real_server_client import RealServerClient

# Import config locally when needed to avoid global import conflicts

logger = logging.getLogger(__name__)

# Data Format Conversion Utilities for BackupServer Compatibility

def blob_to_uuid_string(blob_data: bytes) -> str:
    """Convert BLOB UUID to string representation."""
    if not blob_data or len(blob_data) != 16:
        return str(uuid.uuid4())
    try:
        return str(uuid.UUID(bytes=blob_data))
    except (ValueError, TypeError):
        return str(uuid.uuid4())

def uuid_string_to_blob(uuid_str: str) -> bytes:
    """Convert UUID string to BLOB format."""
    try:
        return uuid.UUID(uuid_str).bytes
    except (ValueError, TypeError):
        return uuid.uuid4().bytes

def convert_backupserver_client_to_fletv2(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert BackupServer client format to FletV2 expected format."""
    if not client_data:
        return {}

    # BackupServer format: {'id': bytes, 'name': str, 'last_seen': str}
    # FletV2 format: {'id': str, 'name': str, 'last_seen': str, 'status': str, 'files_count': int}
    converted = {
        'id': blob_to_uuid_string(client_data.get('id', b'')) if isinstance(client_data.get('id'), bytes) else str(client_data.get('id', '')),
        'name': client_data.get('name', ''),
        'last_seen': client_data.get('last_seen', ''),
        'status': 'Active' if client_data.get('last_seen') else 'Inactive',
        'files_count': client_data.get('files_count', 0),
        'ip_address': client_data.get('ip_address', 'Unknown'),
        'platform': client_data.get('platform', 'Unknown'),
        'version': client_data.get('version', '1.0')
    }
    return converted

def convert_backupserver_file_to_fletv2(file_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert BackupServer file format to FletV2 expected format."""
    if not file_data:
        return {}

    # BackupServer format: {'filename': str, 'client_id': bytes, 'size': int, 'verified': bool}
    # FletV2 format: {'id': str, 'name': str, 'client_id': str, 'size': int, 'status': str}
    converted = {
        'id': str(uuid.uuid4()),  # Generate ID if not provided
        'name': file_data.get('filename', file_data.get('name', '')),
        'client_id': blob_to_uuid_string(file_data.get('client_id', b'')) if isinstance(file_data.get('client_id'), bytes) else str(file_data.get('client_id', '')),
        'size': file_data.get('size', file_data.get('FileSize', 0)),
        'status': 'Verified' if file_data.get('verified', False) else 'Pending',
        'path': file_data.get('path', file_data.get('PathName', '')),
        'hash': file_data.get('hash', ''),
        'created': file_data.get('created', file_data.get('ModificationDate', '')),
        'modified': file_data.get('modified', file_data.get('ModificationDate', '')),
        'type': file_data.get('type', 'file'),
        'backup_count': file_data.get('backup_count', 1),
        'last_backup': file_data.get('last_backup', file_data.get('ModificationDate', ''))
    }
    return converted

def convert_fletv2_client_to_backupserver(client_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert FletV2 client format to BackupServer expected format."""
    if not client_data:
        return {}

    # Convert string ID back to bytes if needed
    client_id = client_data.get('id', '')
    if isinstance(client_id, str):
        client_id = uuid_string_to_blob(client_id)

    converted = {
        'id': client_id,
        'name': client_data.get('name', ''),
        'public_key': None,  # Will be set by BackupServer
        'aes_key': None      # Will be set by BackupServer
    }
    return converted

class ServerBridge:
    """
    Simplified ServerBridge that provides clean drop-in replacement capability.

    If real_server is provided, delegates to it. Otherwise uses MockDatabase for development.
    Maintains 100% compatibility with existing views while being dramatically simpler.
    """

    def __init__(self, real_server: Any | None = None):
        """
        Initialize ServerBridge with optional real server instance.

        Args:
            real_server: Real server instance with methods like get_clients(), delete_file(), etc.
                        If None, uses MockDatabase for development/testing.
        """
        # Instance attributes
        self.real_server = real_server
        # CRITICAL CHANGE: When real server is provided, NEVER use mock data
        self._use_mock_data = not bool(real_server)
        self._mock_db = get_mock_database() if self._use_mock_data else None
        self._connection_status = "connected" if real_server else "mock_mode"

        logger.info(f"ServerBridge initialized in {'PRODUCTION' if real_server else 'MOCK'} mode")

    def is_connected(self) -> bool:
        """Check if server is connected."""
        if self.real_server:
            return hasattr(self.real_server, 'is_connected') and self.real_server.is_connected()
        return True  # Mock is always "connected"

    def _call_real_or_mock(self, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Helper to call real server method or fall back to mock with data conversion."""
        try:
            if self.real_server is not None and hasattr(self.real_server, method_name):
                result = getattr(self.real_server, method_name)(*args, **kwargs)

                # Apply data format conversion for BackupServer results
                converted_result = self._convert_backupserver_result(method_name, result)

                # Normalize result format
                if isinstance(converted_result, dict) and 'success' in converted_result:
                    return converted_result
                return {'success': True, 'data': converted_result, 'error': None}
            else:
                # Use mock database only if mock data is enabled
                if self._use_mock_data and self._mock_db is not None:
                    mock_method = getattr(self._mock_db, method_name, None)
                    if mock_method:
                        result = mock_method(*args, **kwargs)
                        return {'success': True, 'data': result, 'error': None}

                # Return empty data when mock is disabled or not available
                return {'success': True, 'data': [], 'error': None}

        except Exception as e:
            logger.error(f"Error in {method_name}: {e}")
            return {'success': False, 'data': None, 'error': str(e)}

    def _convert_backupserver_result(self, method_name: str, result: Any) -> Any:
        """Convert BackupServer results to FletV2 compatible format."""
        try:
            # If result is a BackupServer response dict with 'success' and 'data' fields
            if isinstance(result, dict) and 'success' in result and 'data' in result:
                if not result.get('success', False):
                    # Return error as-is
                    return result

                # Extract the actual data from BackupServer response
                data = result['data']

                # Convert the data based on method type
                if 'client' in method_name.lower():
                    if isinstance(data, list):
                        converted_data = [convert_backupserver_client_to_fletv2(item) for item in data]
                    elif isinstance(data, dict):
                        converted_data = convert_backupserver_client_to_fletv2(data)
                    else:
                        converted_data = data
                elif 'file' in method_name.lower():
                    if isinstance(data, list):
                        converted_data = [convert_backupserver_file_to_fletv2(item) for item in data]
                    elif isinstance(data, dict):
                        converted_data = convert_backupserver_file_to_fletv2(data)
                    else:
                        converted_data = data
                else:
                    # For other methods, keep data as-is
                    converted_data = data

                # Return in same format as BackupServer response
                return {
                    'success': result['success'],
                    'data': converted_data,
                    'error': result.get('error', '')
                }

            # Handle legacy direct data (not wrapped in success/data format)
            else:
                if 'client' in method_name.lower():
                    if isinstance(result, list):
                        return [convert_backupserver_client_to_fletv2(item) for item in result]
                    elif isinstance(result, dict):
                        return convert_backupserver_client_to_fletv2(result)
                elif 'file' in method_name.lower():
                    if isinstance(result, list):
                        return [convert_backupserver_file_to_fletv2(item) for item in result]
                    elif isinstance(result, dict):
                        return convert_backupserver_file_to_fletv2(result)

                # For other methods, return as-is
                return result

        except Exception as e:
            logger.warning(f"Data conversion error for {method_name}: {e}")
            return result

    async def _call_real_or_mock_async(self, method_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Async version of _call_real_or_mock with data conversion."""
        try:
            if self.real_server is not None and hasattr(self.real_server, method_name):
                result = await getattr(self.real_server, method_name)(*args, **kwargs)

                # Apply data format conversion for BackupServer results
                converted_result = self._convert_backupserver_result(method_name, result)

                # Normalize result format
                if isinstance(converted_result, dict) and 'success' in converted_result:
                    return converted_result
                return {'success': True, 'data': converted_result, 'error': None}
            else:
                # Use mock database only if mock data is enabled
                if self._use_mock_data and self._mock_db is not None:
                    async_method_name = method_name if method_name.endswith('_async') else f"{method_name}_async"
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

                # Return empty data when mock is disabled or not available
                return {'success': True, 'data': [], 'error': None}

        except Exception as e:
            logger.error(f"Error in {method_name}: {e}")
            return {'success': False, 'data': None, 'error': str(e)}

    # ============================================================================
    # CLIENT OPERATIONS
    # ============================================================================

    def get_all_clients_from_db(self) -> Dict[str, Any]:
        """Get all clients from database."""
        return self._call_real_or_mock('get_clients')

    def get_clients(self) -> List[Dict[str, Any]]:
        """Get all clients (sync version)."""
        result = self._call_real_or_mock('get_clients')
        if isinstance(result, dict) and 'data' in result:
            return result['data'] if result['data'] is not None else []
        return result if isinstance(result, list) else []

    async def get_clients_async(self) -> List[Dict[str, Any]]:
        """Get all clients (async version)."""
        result = await self._call_real_or_mock_async('get_clients_async')
        if isinstance(result, dict) and 'data' in result:
            return result['data'] if result['data'] is not None else []
        return result if isinstance(result, list) else []

    def get_client_details(self, client_id: str) -> Dict[str, Any]:
        """Get details for a specific client."""
        return self._call_real_or_mock('get_client_details', client_id)

    async def add_client_async(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new client."""
        return await self._call_real_or_mock_async('add_client_async', client_data)

    def add_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new client (sync version)."""
        return self._call_real_or_mock('add_client', client_data)

    def delete_client(self, client_id: str) -> Dict[str, Any]:
        """Delete a client (sync version)."""
        return self._call_real_or_mock('delete_client', client_id)

    async def delete_client_async(self, client_id: str) -> Dict[str, Any]:
        """Delete a client (async version)."""
        return await self._call_real_or_mock_async('delete_client_async', client_id)

    def disconnect_client(self, client_id: str) -> Dict[str, Any]:
        """Disconnect a specific client."""
        return self._call_real_or_mock('disconnect_client', client_id)

    async def disconnect_client_async(self, client_id: str) -> Dict[str, Any]:
        """Disconnect a specific client (async)."""
        return await self._call_real_or_mock_async('disconnect_client_async', client_id)

    def resolve_client(self, client_identifier: str) -> Dict[str, Any]:
        """Resolve client by ID or name."""
        return self._call_real_or_mock('resolve_client', client_identifier)

    # ============================================================================
    # FILE OPERATIONS
    # ============================================================================

    def get_client_files(self, client_id: str) -> Dict[str, Any]:
        """Get files for a specific client."""
        return self._call_real_or_mock('get_client_files', client_id)

    async def get_client_files_async(self, client_id: str) -> Dict[str, Any]:
        """Get files for a specific client (async)."""
        return await self._call_real_or_mock_async('get_client_files_async', client_id)

    def get_files(self) -> List[Dict[str, Any]]:
        """Get all files."""
        result = self._call_real_or_mock('get_files')
        if isinstance(result, dict) and 'data' in result:
            return result['data'] if result['data'] is not None else []
        return result if isinstance(result, list) else []

    async def get_files_async(self) -> List[Dict[str, Any]]:
        """Get all files (async)."""
        result = await self._call_real_or_mock_async('get_files_async')
        if isinstance(result, dict) and 'data' in result:
            return result['data'] if result['data'] is not None else []
        return result if isinstance(result, list) else []

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a file."""
        return self._call_real_or_mock('delete_file', file_id)

    async def delete_file_async(self, file_id: str) -> Dict[str, Any]:
        """Delete a file (async)."""
        return await self._call_real_or_mock_async('delete_file_async', file_id)

    def delete_file_by_client_and_name(self, client_id: str, filename: str) -> Dict[str, Any]:
        """Delete a file by client ID and filename."""
        return self._call_real_or_mock('delete_file_by_client_and_name', client_id, filename)

    async def delete_file_by_client_and_name_async(self, client_id: str, filename: str) -> Dict[str, Any]:
        """Delete a file by client ID and filename (async)."""
        return await self._call_real_or_mock_async('delete_file_by_client_and_name_async', client_id, filename)

    def download_file(self, file_id: str, destination_path: str) -> Dict[str, Any]:
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

    async def stream_logs_async(self, callback: Callable[[Dict[str, Any]], None]):
        """Stream logs in real-time."""
        return await self._call_real_or_mock_async('stream_logs_async', callback)

    async def stop_log_stream_async(self, streaming_task: Any):
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

    def start_server(self):
        """Start the server (synchronous wrapper)."""
        try:
            # For mock mode, just return success
            if not self.real_server:
                return {"success": True, "message": "Server started (mock mode)"}
            # For real server, delegate to the async method
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.start_server_async())
            loop.close()
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def stop_server_async(self):
        """Stop the server."""
        return await self._call_real_or_mock_async('stop_server_async')

    def stop_server(self):
        """Stop the server (synchronous wrapper)."""
        try:
            # For mock mode, just return success
            if not self.real_server:
                return {"success": True, "message": "Server stopped (mock mode)"}
            # For real server, delegate to the async method
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.stop_server_async())
            loop.close()
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

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

    def save_settings(self, settings_data: Dict[str, Any]):
        """Save application settings (sync version)."""
        return self._call_real_or_mock('save_settings', settings_data)

    async def load_settings_async(self):
        """Load current settings."""
        return await self._call_real_or_mock_async('load_settings_async')

    def load_settings(self):
        """Load current settings (sync version)."""
        return self._call_real_or_mock('load_settings')

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
    # DATABASE OPERATIONS (for database view)
    # ============================================================================

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        if self.real_server and hasattr(self.real_server, 'db_manager'):
            try:
                db_manager = self.real_server.db_manager
                stats = db_manager.get_database_stats()
                health = db_manager.get_database_health()

                return {
                    'success': True,
                    'data': {
                        'status': 'Connected' if health.get('integrity_check') else 'Error',
                        'tables': health.get('table_count', 0),
                        'total_records': stats.get('total_clients', 0) + stats.get('total_files', 0),
                        'size': f"{stats.get('database_size_bytes', 0) / (1024*1024):.1f} MB",
                        'integrity_check': health.get('integrity_check', False),
                        'foreign_key_check': health.get('foreign_key_check', False),
                        'connection_pool_healthy': health.get('connection_pool_healthy', True)
                    },
                    'error': None
                }
            except Exception as e:
                logger.error(f"Error getting database info: {e}")
                return {'success': False, 'data': None, 'error': str(e)}
        else:
            # Use mock database only if mock data is enabled
            if self._use_mock_data:
                # Mock database info
                return {
                    'success': True,
                    'data': {
                        'status': 'Connected (Mock)',
                        'tables': 5,
                        'total_records': 1247,
                        'size': '15.3 MB',
                        'integrity_check': True,
                        'foreign_key_check': True,
                        'connection_pool_healthy': True
                    },
                    'error': None
                }
            else:
                # Return empty data when mock is disabled
                return {
                    'success': True,
                    'data': {
                        'status': 'Connected',
                        'tables': 0,
                        'total_records': 0,
                        'size': '0 MB',
                        'integrity_check': True,
                        'foreign_key_check': True,
                        'connection_pool_healthy': True
                    },
                    'error': None
                }

    def get_table_names(self) -> Dict[str, Any]:
        """Get list of database table names."""
        if self.real_server and hasattr(self.real_server, 'db_manager'):
            try:
                db_manager = self.real_server.db_manager
                table_names = db_manager.get_table_names()
                return {'success': True, 'data': table_names, 'error': None}
            except Exception as e:
                logger.error(f"Error getting table names: {e}")
                return {'success': False, 'data': [], 'error': str(e)}
        else:
            # Use mock database only if mock data is enabled
            if self._use_mock_data:
                # Mock table names
                return {'success': True, 'data': ['clients', 'files'], 'error': None}
            else:
                # Return empty data when mock is disabled
                return {'success': True, 'data': [], 'error': None}

    def get_table_data(self, table_name: str) -> Dict[str, Any]:
        """Get data from a specific database table."""
        if self.real_server and hasattr(self.real_server, 'db_manager'):
            try:
                db_manager = self.real_server.db_manager
                columns, rows = db_manager.get_table_content(table_name)

                # Convert to format expected by FletV2
                table_data = []
                for row in rows:
                    # Apply data conversion based on table type
                    if table_name == 'clients':
                        converted_row = convert_backupserver_client_to_fletv2(row)
                    elif table_name == 'files':
                        converted_row = convert_backupserver_file_to_fletv2(row)
                    else:
                        converted_row = row
                    table_data.append(converted_row)

                return {
                    'success': True,
                    'data': {
                        'columns': columns,
                        'rows': table_data
                    },
                    'error': None
                }
            except Exception as e:
                logger.error(f"Error getting table data for {table_name}: {e}")
                return {'success': False, 'data': {'columns': [], 'rows': []}, 'error': str(e)}
        else:
            # Use mock database only if mock data is enabled
            if self._use_mock_data and self._mock_db is not None:
                # Use mock database
                return self._call_real_or_mock('get_table_data', table_name)
            else:
                # Return empty data when mock is disabled
                return {
                    'success': True,
                    'data': {
                        'columns': [],
                        'rows': []
                    },
                    'error': None
                }


# ============================================================================
# FACTORY FUNCTIONS (for compatibility with existing code)
# ============================================================================

def create_server_bridge(real_server: Any | None = None):
    """
    Factory function to create ServerBridge instance.

    Args:
        real_server: Optional real server instance for production use

    Returns:
        ServerBridge instance configured for production or development
    """
    # Local config import to avoid global module conflicts
    try:
        from .. import config
    except ImportError:
        try:
            import config
        except ImportError:
            config = None

    # If real_server is provided directly, use it immediately
    if real_server is not None:
        logger.info("Using directly provided real server instance")
        return ServerBridge(real_server=real_server)

    # Auto-detect real server from environment if not explicitly provided
    try:
        if config and config.REAL_SERVER_URL:
            try:
                client: RealServerClient = RealServerClient(
                    base_url=config.REAL_SERVER_URL,
                    token=config.BACKUP_SERVER_TOKEN,
                    verify_tls=config.VERIFY_TLS,
                    timeout=config.REQUEST_TIMEOUT,
                )
                # Lightweight async health check
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                health: Dict[str, Any] = loop.run_until_complete(client.test_connection_async())
                loop.close()
                if health.get("success"):
                    logger.debug("Using RealServerClient based on REAL_SERVER_URL")
                    return ServerBridge(real_server=client)
                else:
                    logger.warning("Real server health check failed; falling back to mock mode: %s", health.get("error"))
            except Exception as e:
                logger.warning("Failed to initialize RealServerClient; falling back to mock mode: %s", e)
    except (ImportError, AttributeError) as e:
        logger.warning("Config import failed, using mock mode: %s", e)

    return ServerBridge(real_server)

# Module-level singleton to avoid function attribute access diagnostics
_SERVER_BRIDGE_INSTANCE: Optional[ServerBridge] = None

def get_server_bridge() -> ServerBridge:
    """Get or create a singleton ServerBridge instance for development."""
    global _SERVER_BRIDGE_INSTANCE
    if _SERVER_BRIDGE_INSTANCE is None:
        _SERVER_BRIDGE_INSTANCE = ServerBridge()
    return _SERVER_BRIDGE_INSTANCE