"""
Production ServerBridge - Direct delegation to real BackupServer instance.

Provides clean API surface for the FletV2 GUI:
- Direct delegation pattern to real server
- Consistent structured returns: {'success': bool, 'data': Any, 'error': str}
- Data format conversion between BackupServer and FletV2 formats
- Error handling with structured responses
"""

import logging
import uuid
from collections.abc import Callable
from typing import Any

# NOTE: Mock data has been fully removed per project policy:
#  - If a real server instance isn't supplied, methods now return empty data structures
#    or {'success': False, 'error': 'No real server configured'} without fabricating values.
#  - This preserves ability for views/tests to instantiate a bridge in a "disconnected" state
#    while guaranteeing NO synthetic metrics or entities leak into the UI.

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

def _case_insensitive_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Fetch the first matching key from a dictionary using case-insensitive lookup."""
    if not data:
        return default

    for key in keys:
        if key in data:
            return data[key]
        if isinstance(key, str):
            lowered = key.lower()
            for actual_key, value in data.items():
                if isinstance(actual_key, str) and actual_key.lower() == lowered:
                    return value
    return default


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {'1', 'true', 'yes', 'on'}:
            return True
        if lowered in {'0', 'false', 'no', 'off'}:
            return False
    return False


def convert_backupserver_client_to_fletv2(client_data: dict[str, Any]) -> dict[str, Any]:
    """Convert BackupServer client format to FletV2 expected format."""
    if not client_data:
        return {}

    raw_id = _case_insensitive_get(client_data, 'id', 'ID', 'client_id', 'ClientID', default=b'')
    if isinstance(raw_id, bytes):
        client_id = raw_id.hex()
    else:
        client_id = str(raw_id) if raw_id is not None else ''

    raw_name = _case_insensitive_get(client_data, 'name', 'Name', default='')
    last_seen = _case_insensitive_get(client_data, 'last_seen', 'LastSeen', default='')
    files_count = _case_insensitive_get(client_data, 'files_count', 'FilesCount', default=0)
    try:
        files_count_int = int(files_count)
    except (TypeError, ValueError):
        files_count_int = 0

    return {
        'id': client_id,
        'name': str(raw_name) if raw_name is not None else '',
        'last_seen': str(last_seen) if last_seen is not None else '',
        'status': 'Active' if last_seen else 'Inactive',
        'files_count': files_count_int,
        'ip_address': _case_insensitive_get(client_data, 'ip_address', 'IPAddress', default='Unknown'),
        'platform': _case_insensitive_get(client_data, 'platform', default='Unknown'),
        'version': _case_insensitive_get(client_data, 'version', default='1.0')
    }


def convert_backupserver_file_to_fletv2(file_data: dict[str, Any]) -> dict[str, Any]:
    """Convert BackupServer file format to FletV2 expected format."""
    if not file_data:
        return {}

    raw_id = _case_insensitive_get(file_data, 'id', 'ID', default=None)
    if isinstance(raw_id, bytes):
        file_id = raw_id.hex()
    elif raw_id is not None:
        file_id = str(raw_id)
    else:
        file_id = str(uuid.uuid4())

    raw_client_id = _case_insensitive_get(file_data, 'client_id', 'ClientID', default='')
    if isinstance(raw_client_id, bytes):
        client_id = raw_client_id.hex()
    else:
        client_id = str(raw_client_id) if raw_client_id is not None else ''

    filename = _case_insensitive_get(file_data, 'filename', 'FileName', 'name', default='')
    file_size = _case_insensitive_get(file_data, 'size', 'FileSize', default=0)
    try:
        file_size_int = int(file_size)
    except (TypeError, ValueError):
        file_size_int = 0

    verified_value = _case_insensitive_get(file_data, 'verified', 'Verified', default=False)
    verified = _coerce_bool(verified_value)

    return {
        'id': file_id,
        'name': str(filename) if filename is not None else '',
        'client_id': client_id,
        'size': file_size_int,
        'status': 'Verified' if verified else 'Pending',
        'verified': verified,
        'path': _case_insensitive_get(file_data, 'path', 'PathName', default=''),
        'hash': _case_insensitive_get(file_data, 'hash', 'CRC', default=''),
        'created': _case_insensitive_get(
            file_data, 'created', 'Created', 'CreationDate', 'ModificationDate', default=''
        ),
        'modified': _case_insensitive_get(file_data, 'modified', 'ModificationDate', default=''),
        'type': _case_insensitive_get(file_data, 'type', default='file'),
        'backup_count': _case_insensitive_get(file_data, 'backup_count', 'BackupCount', default=1),
        'last_backup': _case_insensitive_get(
            file_data, 'last_backup', 'LastBackup', 'ModificationDate', default=''
        )
    }

def convert_fletv2_client_to_backupserver(client_data: dict[str, Any]) -> dict[str, Any]:
    """Convert FletV2 client format to BackupServer expected format."""
    if not client_data:
        return {}

    # Convert string ID back to bytes if needed
    client_id = client_data.get('id', '')
    if isinstance(client_id, str):
        client_id = uuid_string_to_blob(client_id)

    return {
        'id': client_id,
        'name': client_data.get('name', ''),
        'public_key': None,  # Will be set by BackupServer
        'aes_key': None      # Will be set by BackupServer
    }

class ServerBridge:
    """ServerBridge delegating to a real server instance.

    When instantiated without a real server, the instance enters a disconnected
    state and returns empty collections or explicit failure responses WITHOUT
    generating any fabricated/mock data. This satisfies the "no mock data"
    project directive while allowing UI components to render graceful
    "No data" placeholders.
    """

    def __init__(self, real_server: Any | None = None):
        self.real_server = real_server
        self._connection_status = "connected" if real_server else "disconnected"
        if self.real_server:
            logger.info("ServerBridge initialized (real server connected)")
        else:
            logger.warning("ServerBridge initialized with NO real server (disconnected mode, no data)")

    def is_connected(self) -> bool:
        """Return connection status based on real server availability."""
        return bool(
            self.real_server
            and hasattr(self.real_server, 'is_connected')
            and self.real_server.is_connected()
        )

    def _call_real_server_method(self, method_name: str, *args, **kwargs) -> dict[str, Any]:
        """Helper to call real server method with data conversion."""
        if not self.real_server:
            return {'success': False, 'data': None, 'error': 'No real server configured'}
        try:
            if not hasattr(self.real_server, method_name):
                return {
                    'success': False,
                    'data': None,
                    'error': f'Method {method_name} not available on server',
                }

            result = getattr(self.real_server, method_name)(*args, **kwargs)

            # Apply data format conversion for BackupServer results
            converted_result = self._convert_backupserver_result(method_name, result)

            # Normalize result format
            if isinstance(converted_result, dict) and 'success' in converted_result:
                return converted_result
            return {'success': True, 'data': converted_result, 'error': None}

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

    async def _call_real_server_method_async(self, method_name: str, *args, **kwargs) -> dict[str, Any]:
        """Async version of _call_real_server_method with data conversion."""
        if not self.real_server:
            return {'success': False, 'data': None, 'error': 'No real server configured'}
        try:
            if not hasattr(self.real_server, method_name):
                return {
                    'success': False,
                    'data': None,
                    'error': f'Method {method_name} not available on server',
                }

            result = await getattr(self.real_server, method_name)(*args, **kwargs)

            # Apply data format conversion for BackupServer results
            converted_result = self._convert_backupserver_result(method_name, result)

            # Normalize result format
            if isinstance(converted_result, dict) and 'success' in converted_result:
                return converted_result
            return {'success': True, 'data': converted_result, 'error': None}

        except Exception as e:
            logger.error(f"Error in {method_name}: {e}")
            return {'success': False, 'data': None, 'error': str(e)}

    # ============================================================================
    # CLIENT OPERATIONS
    # ============================================================================

    def get_all_clients_from_db(self) -> dict[str, Any]:
        """Get all clients from database."""
        return self._call_real_server_method('get_clients')

    def get_clients(self) -> list[dict[str, Any]]:
        """Get all clients (sync version)."""
        if not self.real_server:
            return []
        result = self._call_real_server_method('get_clients')
        if isinstance(result, dict) and 'data' in result:
            return result['data'] if result['data'] is not None else []
        return result if isinstance(result, list) else []

    async def get_clients_async(self) -> list[dict[str, Any]]:
        """Get all clients (async version)."""
        if not self.real_server:
            return []
        result = await self._call_real_server_method_async('get_clients_async')
        if isinstance(result, dict) and 'data' in result:
            return result['data'] if result['data'] is not None else []
        return result if isinstance(result, list) else []

    def get_client_details(self, client_id: str) -> dict[str, Any]:
        """Get details for a specific client."""
        return self._call_real_server_method('get_client_details', client_id)

    async def add_client_async(self, client_data: dict[str, Any]) -> dict[str, Any]:
        """Add a new client."""
        return await self._call_real_server_method_async('add_client_async', client_data)

    def add_client(self, client_data: dict[str, Any]) -> dict[str, Any]:
        """Add a new client (sync version)."""
        return self._call_real_server_method('add_client', client_data)

    def update_client(self, client_id: str, updated_data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing client (sync version)."""
        return self._call_real_server_method('update_client', client_id, updated_data)

    async def update_client_async(self, client_id: str, updated_data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing client (async version)."""
        return await self._call_real_server_method_async('update_client_async', client_id, updated_data)

    def delete_client(self, client_id: str) -> dict[str, Any]:
        """Delete a client (sync version)."""
        return self._call_real_server_method('delete_client', client_id)

    async def delete_client_async(self, client_id: str) -> dict[str, Any]:
        """Delete a client (async version)."""
        return await self._call_real_server_method_async('delete_client_async', client_id)

    def disconnect_client(self, client_id: str) -> dict[str, Any]:
        """Disconnect a specific client."""
        return self._call_real_server_method('disconnect_client', client_id)

    async def disconnect_client_async(self, client_id: str) -> dict[str, Any]:
        """Disconnect a specific client (async)."""
        return await self._call_real_server_method_async('disconnect_client_async', client_id)

    def resolve_client(self, client_identifier: str) -> dict[str, Any]:
        """Resolve client by ID or name."""
        return self._call_real_server_method('resolve_client', client_identifier)

    # ============================================================================
    # FILE OPERATIONS
    # ============================================================================

    def get_client_files(self, client_id: str) -> dict[str, Any]:
        """Get files for a specific client."""
        return self._call_real_server_method('get_client_files', client_id)

    async def get_client_files_async(self, client_id: str) -> dict[str, Any]:
        """Get files for a specific client (async)."""
        return await self._call_real_server_method_async('get_client_files_async', client_id)

    def get_files(self) -> list[dict[str, Any]]:
        """Get all files."""
        if not self.real_server:
            return []
        result = self._call_real_server_method('get_files')
        if isinstance(result, dict) and 'data' in result:
            return result['data'] if result['data'] is not None else []
        return result if isinstance(result, list) else []

    async def get_files_async(self) -> list[dict[str, Any]]:
        """Get all files (async)."""
        if not self.real_server:
            return []
        result = await self._call_real_server_method_async('get_files_async')
        if isinstance(result, dict) and 'data' in result:
            return result['data'] if result['data'] is not None else []
        return result if isinstance(result, list) else []

    def delete_file(self, file_id: str) -> dict[str, Any]:
        """Delete a file."""
        return self._call_real_server_method('delete_file', file_id)

    async def delete_file_async(self, file_id: str) -> dict[str, Any]:
        """Delete a file (async)."""
        return await self._call_real_server_method_async('delete_file_async', file_id)

    def delete_file_by_client_and_name(self, client_id: str, filename: str) -> dict[str, Any]:
        """Delete a file by client ID and filename."""
        return self._call_real_server_method('delete_file_by_client_and_name', client_id, filename)

    async def delete_file_by_client_and_name_async(self, client_id: str, filename: str) -> dict[str, Any]:
        """Delete a file by client ID and filename (async)."""
        return await self._call_real_server_method_async(
            'delete_file_by_client_and_name_async', client_id, filename
        )

    def download_file(self, file_id: str, destination_path: str) -> dict[str, Any]:
        """Download a file to destination."""
        return self._call_real_server_method('download_file', file_id, destination_path)

    async def download_file_async(self, file_id: str, destination_path: str):
        """Download a file to destination (async)."""
        return await self._call_real_server_method_async('download_file_async', file_id, destination_path)

    def verify_file(self, file_id: str):
        """Verify file integrity."""
        return self._call_real_server_method('verify_file', file_id)

    async def verify_file_async(self, file_id: str):
        """Verify file integrity (async)."""
        return await self._call_real_server_method_async('verify_file_async', file_id)

    # ============================================================================
    # LOG OPERATIONS
    # ============================================================================

    def get_logs(self):
        """Get system logs."""
        return self._call_real_server_method('get_logs')

    async def get_logs_async(self):
        """Get system logs (async)."""
        return await self._call_real_server_method_async('get_logs_async')

    async def clear_logs_async(self):
        """Clear all logs."""
        return await self._call_real_server_method_async('clear_logs_async')

    async def export_logs_async(self, export_format: str, filters: dict[str, Any] | None = None):
        """Export logs in specified format."""
        return await self._call_real_server_method_async('export_logs_async', export_format, filters or {})

    async def get_log_statistics_async(self):
        """Get log statistics."""
        return await self._call_real_server_method_async('get_log_statistics_async')

    async def stream_logs_async(self, callback: Callable[[dict[str, Any]], None]):
        """Stream logs in real-time."""
        return await self._call_real_server_method_async('stream_logs_async', callback)

    async def stop_log_stream_async(self, streaming_task: Any):
        """Stop log streaming."""
        return await self._call_real_server_method_async('stop_log_stream_async', streaming_task)

    # ============================================================================
    # SERVER STATUS & MONITORING
    # ============================================================================

    def get_server_status(self):
        """Get basic server status."""
        return self._call_real_server_method('get_server_status')

    async def get_server_status_async(self):
        """Get basic server status (async)."""
        return await self._call_real_server_method_async('get_server_status_async')

    def get_detailed_server_status(self):
        """Get comprehensive server status."""
        return self._call_real_server_method('get_detailed_server_status')

    async def get_detailed_server_status_async(self):
        """Get comprehensive server status (async)."""
        return await self._call_real_server_method_async('get_detailed_server_status_async')

    def get_server_health(self):
        """Get server health metrics."""
        return self._call_real_server_method('get_server_health')

    async def get_server_health_async(self):
        """Get server health metrics (async)."""
        return await self._call_real_server_method_async('get_server_health_async')

    async def start_server_async(self):
        """Start the server."""
        return await self._call_real_server_method_async('start_server_async')

    def start_server(self):
        """Start the server (synchronous wrapper)."""
        try:
            # For placeholder mode, just return success
            if not self.real_server:
                return {"success": False, "error": "No real server configured"}
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
        return await self._call_real_server_method_async('stop_server_async')

    def stop_server(self):
        """Stop the server (synchronous wrapper)."""
        try:
            # For placeholder mode, just return success
            if not self.real_server:
                return {"success": False, "error": "No real server configured"}
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
        return self._call_real_server_method('test_connection')

    async def test_connection_async(self):
        """Test server connection (async)."""
        return await self._call_real_server_method_async('test_connection_async')

    # ============================================================================
    # ANALYTICS & SYSTEM
    # ============================================================================

    def get_system_status(self):
        """Get system status."""
        return self._call_real_server_method('get_system_status')

    async def get_system_status_async(self):
        """Get system status (async)."""
        return await self._call_real_server_method_async('get_system_status_async')

    def get_analytics_data(self):
        """Get analytics data."""
        return self._call_real_server_method('get_analytics_data')

    async def get_analytics_data_async(self):
        """Get analytics data (async)."""
        return await self._call_real_server_method_async('get_analytics_data_async')

    def get_performance_metrics(self):
        """Get performance metrics."""
        return self._call_real_server_method('get_performance_metrics')

    async def get_performance_metrics_async(self):
        """Get performance metrics (async)."""
        return await self._call_real_server_method_async('get_performance_metrics_async')

    def get_historical_data(self, metric: str, hours: int = 24):
        """Get historical performance data."""
        return self._call_real_server_method('get_historical_data', metric, hours)

    async def get_historical_data_async(self, metric: str, hours: int = 24):
        """Get historical performance data (async)."""
        return await self._call_real_server_method_async('get_historical_data_async', metric, hours)

    def get_dashboard_summary(self):
        """Get dashboard summary data."""
        return self._call_real_server_method('get_dashboard_summary')

    async def get_dashboard_summary_async(self):
        """Get dashboard summary data (async)."""
        return await self._call_real_server_method_async('get_dashboard_summary_async')

    def get_server_statistics(self):
        """Get detailed server statistics."""
        return self._call_real_server_method('get_server_statistics')

    async def get_server_statistics_async(self):
        """Get detailed server statistics (async)."""
        return await self._call_real_server_method_async('get_server_statistics_async')

    async def get_recent_activity_async(self, limit: int = 50):
        """Get recent system activity."""
        return await self._call_real_server_method_async('get_recent_activity_async', limit)

    # ============================================================================
    # SETTINGS MANAGEMENT
    # ============================================================================

    async def save_settings_async(self, settings_data: dict[str, Any]):
        """Save application settings."""
        return await self._call_real_server_method_async('save_settings_async', settings_data)

    def save_settings(self, settings_data: dict[str, Any]):
        """Save application settings (sync version)."""
        return self._call_real_server_method('save_settings', settings_data)

    async def load_settings_async(self):
        """Load current settings."""
        return await self._call_real_server_method_async('load_settings_async')

    def load_settings(self):
        """Load current settings (sync version)."""
        return self._call_real_server_method('load_settings')

    async def validate_settings_async(self, settings_data: dict[str, Any]):
        """Validate settings data."""
        return await self._call_real_server_method_async('validate_settings_async', settings_data)

    async def backup_settings_async(self, backup_name: str, settings_data: dict[str, Any]):
        """Create settings backup."""
        return await self._call_real_server_method_async('backup_settings_async', backup_name, settings_data)

    async def restore_settings_async(self, backup_file: str):
        """Restore settings from backup."""
        return await self._call_real_server_method_async('restore_settings_async', backup_file)

    async def get_default_settings_async(self):
        """Get default settings."""
        return await self._call_real_server_method_async('get_default_settings_async')

    # ============================================================================
    # DATABASE OPERATIONS (for database view)
    # ============================================================================

    def _normalize_table_row(self, table_name: str, row: dict[str, Any]) -> dict[str, Any]:
        """Normalize table rows using known converters while preserving original data."""
        if not isinstance(row, dict):
            return row

        normalized_row = dict(row)
        table_name_lower = table_name.lower()

        if table_name_lower == 'clients':
            normalized_row.update(convert_backupserver_client_to_fletv2(row))
        elif table_name_lower == 'files':
            normalized_row.update(convert_backupserver_file_to_fletv2(row))
        else:
            for key, value in list(row.items()):
                if isinstance(key, str):
                    lowered = key.lower()
                    if lowered not in normalized_row:
                        normalized_row[lowered] = value

        if 'id' not in normalized_row:
            raw_id = row.get('id') or row.get('ID')
            if isinstance(raw_id, bytes):
                normalized_row['id'] = raw_id.hex()
            elif raw_id is not None:
                normalized_row['id'] = str(raw_id)

        return normalized_row

    def add_table_record(self, table_name: str, record_data: dict[str, Any]) -> dict[str, Any]:
        """Insert a new database record via the real server."""
        if not record_data:
            return {'success': False, 'data': None, 'error': 'No data provided'}

        result = self._call_real_server_method('add_row', table_name, record_data)
        if result.get('success') and isinstance(result.get('data'), dict):
            result['data'] = self._normalize_table_row(table_name, result['data'])
        return result

    async def add_table_record_async(self, table_name: str, record_data: dict[str, Any]) -> dict[str, Any]:
        result = await self._call_real_server_method_async('add_row_async', table_name, record_data)
        if result.get('success') and isinstance(result.get('data'), dict):
            result['data'] = self._normalize_table_row(table_name, result['data'])
        return result

    def update_table_record(self, table_name: str, record_data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing database record via the real server."""
        if not record_data:
            return {'success': False, 'data': None, 'error': 'No data provided'}

        record_identifier = record_data.get('id') or record_data.get('ID')
        if record_identifier is None:
            return {'success': False, 'data': None, 'error': 'Record identifier missing'}

        sanitized_data = dict(record_data)
        sanitized_data.pop('id', None)
        sanitized_data.pop('ID', None)

        result = self._call_real_server_method('update_row', table_name, record_identifier, sanitized_data)
        if result.get('success') and isinstance(result.get('data'), dict):
            result['data'] = self._normalize_table_row(table_name, result['data'])
        return result

    async def update_table_record_async(self, table_name: str, record_data: dict[str, Any]) -> dict[str, Any]:
        if not record_data:
            return {'success': False, 'data': None, 'error': 'No data provided'}

        record_identifier = record_data.get('id') or record_data.get('ID')
        if record_identifier is None:
            return {'success': False, 'data': None, 'error': 'Record identifier missing'}

        sanitized_data = dict(record_data)
        sanitized_data.pop('id', None)
        sanitized_data.pop('ID', None)

        result = await self._call_real_server_method_async(
            'update_row_async', table_name, record_identifier, sanitized_data
        )
        if result.get('success') and isinstance(result.get('data'), dict):
            result['data'] = self._normalize_table_row(table_name, result['data'])
        return result

    def delete_table_record(self, table_name: str, record_identifier: Any) -> dict[str, Any]:
        """Delete a database record via the real server."""
        if record_identifier is None:
            return {'success': False, 'data': None, 'error': 'Record identifier missing'}

        if isinstance(record_identifier, dict):
            record_identifier = record_identifier.get('id') or record_identifier.get('ID')

        if record_identifier is None:
            return {'success': False, 'data': None, 'error': 'Record identifier missing'}

        return self._call_real_server_method('delete_row', table_name, record_identifier)

    async def delete_table_record_async(self, table_name: str, record_identifier: Any) -> dict[str, Any]:
        if isinstance(record_identifier, dict):
            record_identifier = record_identifier.get('id') or record_identifier.get('ID')

        if record_identifier is None:
            return {'success': False, 'data': None, 'error': 'Record identifier missing'}

        return await self._call_real_server_method_async('delete_row_async', table_name, record_identifier)

    def get_database_info(self) -> dict[str, Any]:
        """Get database information and statistics."""
        if not self.real_server or not hasattr(self.real_server, 'db_manager'):
            return {'success': False, 'data': None, 'error': 'Database manager not available on server'}

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

    async def get_database_info_async(self) -> dict[str, Any]:
        """Get database information and statistics (async version)."""
        if not self.real_server or not hasattr(self.real_server, 'db_manager'):
            return {'success': False, 'data': None, 'error': 'Database manager not available on server'}

        try:
            # Call BackupServer's async method
            result = await self._call_real_server_method_async('get_database_info_async')

            if not result.get('success'):
                return result

            # Transform BackupServer format to DatabaseView format
            server_data = result.get('data', {})
            db_manager = self.real_server.db_manager
            health = db_manager.get_database_health()

            return {
                'success': True,
                'data': {
                    'status': 'Connected' if health.get('integrity_check') else 'Error',
                    'tables': health.get('table_count', 0),
                    'total_records': server_data.get('total_clients', 0) + server_data.get('total_files', 0),
                    'size': f"{server_data.get('database_size_bytes', 0) / (1024*1024):.1f} MB",
                    'integrity_check': health.get('integrity_check', False),
                    'foreign_key_check': health.get('foreign_key_check', False),
                    'connection_pool_healthy': health.get('connection_pool_healthy', True)
                },
                'error': None
            }
        except Exception as e:
            logger.error(f"Error getting database info async: {e}")
            return {'success': False, 'data': None, 'error': str(e)}

    def get_table_names(self) -> dict[str, Any]:
        """Get list of database table names."""
        if not self.real_server or not hasattr(self.real_server, 'db_manager'):
            return {'success': False, 'data': [], 'error': 'Database manager not available on server'}

        try:
            db_manager = self.real_server.db_manager
            table_names = db_manager.get_table_names()
            return {'success': True, 'data': table_names, 'error': None}
        except Exception as e:
            logger.error(f"Error getting table names: {e}")
            return {'success': False, 'data': [], 'error': str(e)}

    def get_table_data(self, table_name: str) -> dict[str, Any]:
        """Get data from a specific database table."""
        if not self.real_server or not hasattr(self.real_server, 'db_manager'):
            return {
                'success': False,
                'data': {'columns': [], 'rows': []},
                'error': 'Database manager not available on server',
            }

        try:
            db_manager = self.real_server.db_manager
            columns, rows = db_manager.get_table_content(table_name)

            # Convert to format expected by FletV2
            table_data = [self._normalize_table_row(table_name, row) for row in rows]

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

    async def get_table_data_async(self, table_name: str) -> dict[str, Any]:
        """Get data from a specific database table (async version)."""
        # Call BackupServer's async method directly to avoid connection pool issues
        return await self._call_real_server_method_async('get_table_data_async', table_name)


# ============================================================================
# FACTORY FUNCTIONS (for compatibility with existing code)
# ============================================================================

def create_server_bridge(real_server: Any | None = None):
    """Factory creating a ServerBridge.

    Supplying no real_server returns a disconnected bridge (no data, no mock).
    This is useful for UI initialization pathways where a server may connect later.
    """
    return ServerBridge(real_server=real_server)

# Module-level singleton to avoid function attribute access diagnostics
_SERVER_BRIDGE_INSTANCE: ServerBridge | None = None

def get_server_bridge() -> ServerBridge:
    """Deprecated singleton accessor retained for backward compatibility.

    Returns a disconnected bridge (no data). Prefer explicit create_server_bridge().
    """
    global _SERVER_BRIDGE_INSTANCE
    if _SERVER_BRIDGE_INSTANCE is None:
        _SERVER_BRIDGE_INSTANCE = ServerBridge()
    return _SERVER_BRIDGE_INSTANCE
