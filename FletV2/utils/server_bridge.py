#!/usr/bin/env python3
"""
Unified Server Bridge for FletV2
Simple bridge that makes direct function calls to the real server when available,
or falls back to mock data for development.

Design Principles:
- Simple and fast - no over-engineering
- Direct data access - no caching that causes stale data
- Immediate UI updates after modifications
- Clean fallback to mock data
"""

import asyncio
import time
import random
from typing import Dict, List, Tuple, Optional, Any
import aiofiles
import json
from pathlib import Path
from datetime import datetime
from utils.debug_setup import get_logger
from utils.mock_data_generator import MockDataGenerator

logger = get_logger(__name__)

# This is a placeholder for the real BackupServer class.
# In the final project, you would import the actual class:
# from python_server.server import BackupServer
class BackupServer:
    """Placeholder for the real BackupServer class"""
    pass

class ServerBridge:
    """
    A unified bridge to the backend server.
    Simple design: if a real server instance is provided, it proxies calls to it.
    Otherwise, it falls back to returning mock data for UI development.

    Key principles:
    - No caching (prevents stale data issues)
    - Direct data access for immediate UI updates
    - Simple and reliable
    """

    def __init__(self, real_server_instance: Optional[BackupServer] = None):
        """Initialize the unified server bridge."""
        self.real_server = real_server_instance

        if self.real_server:
            print("[ServerBridge] Initialized in LIVE mode, connected to the real server.")
            logger.info("ServerBridge initialized in LIVE mode with real server")
        else:
            print("[ServerBridge] Initialized in FALLBACK mode. Will use persistent mock data.")
            logger.info("ServerBridge initialized in FALLBACK mode")

        # Initialize consolidated mock data generator with persistence and realistic fallback behavior
        self.mock_generator = MockDataGenerator(num_clients=45, persist_to_disk=True)

        # Track connection status (legacy compatibility)
        self.connected = self.real_server is not None

    def _create_success_response(self, message: str, data: Any = None, mode: str = 'mock', **kwargs) -> Dict[str, Any]:
        """Create standardized success response."""
        response = {
            'success': True,
            'message': message,
            'mode': mode,
            'timestamp': time.time()
        }
        if data is not None:
            response['data'] = data
        response.update(kwargs)
        return response

    def _create_error_response(self, message: str, error_code: str = None, mode: str = 'mock', **kwargs) -> Dict[str, Any]:
        """Create standardized error response."""
        response = {
            'success': False,
            'message': message,
            'mode': mode,
            'timestamp': time.time()
        }
        if error_code:
            response['error_code'] = error_code
        response.update(kwargs)
        return response

    def _handle_server_operation(self, operation_name: str, real_method_name: str,
                                mock_fallback_func, *args, **kwargs) -> Dict[str, Any]:
        """Standardized server operation handler with consistent error handling."""
        if self.real_server and hasattr(self.real_server, real_method_name):
            try:
                real_method = getattr(self.real_server, real_method_name)
                result = real_method(*args, **kwargs)
                logger.debug(f"[ServerBridge] Real server {operation_name} successful.")

                # If result is already a dict with success/message, return as-is but add mode
                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result

                # Otherwise, wrap the result
                return self._create_success_response(
                    f"{operation_name} completed successfully",
                    data=result,
                    mode='real'
                )
            except Exception as e:
                logger.error(f"Real server {operation_name} failed: {e}")
                return self._create_error_response(
                    f"Real server {operation_name} failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback
        try:
            return mock_fallback_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Mock {operation_name} failed: {e}")
            return self._create_error_response(
                f"Mock {operation_name} failed: {str(e)}",
                error_code='MOCK_OPERATION_ERROR',
                mode='mock'
            )

    def _normalize_client_data(self, raw_clients: List[Dict]) -> List[Dict]:
        """Normalize client data format for consistent UI expectations."""
        normalized = []
        for client in raw_clients:
            # Handle both "client_id" and "id" fields for compatibility
            client_id = client.get("client_id") or client.get("id", "unknown")

            normalized_client = {
                "id": client_id,  # Always provide "id" field for UI
                "client_id": client_id,  # Keep original field for backend compatibility
                "name": client.get("name", "Unknown Client"),
                "status": client.get("status", "Unknown"),
                "last_seen": client.get("last_activity") or client.get("last_seen", "Never"),
                "files_count": str(client.get("files_count", 0)),
                "total_size": self._format_file_size(client.get("total_size", 0))
            }
            normalized.append(normalized_client)
        return normalized

    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        elif size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

    # --- Client Management ---

    def get_all_clients_from_db(self) -> List[Dict]:
        """Get all clients from database."""
        def mock_fallback():
            logger.debug("[ServerBridge] FALLBACK: Returning mock client data.")
            raw_data = self.mock_generator.get_clients()
            # Normalize data format for consistent UI expectations
            return self._normalize_client_data(raw_data)

        if self.real_server and hasattr(self.real_server, 'get_all_clients_from_db'):
            try:
                result = self.real_server.get_all_clients_from_db()
                logger.debug("[ServerBridge] Real server get_all_clients_from_db successful.")
                return self._normalize_client_data(result) if result else []
            except Exception as e:
                logger.error(f"Real server get_all_clients_from_db failed: {e}")
                # Fall through to mock fallback

        return mock_fallback()

    def get_clients(self) -> List[Dict[str, Any]]:
        """Get client data (alias for get_all_clients_from_db)."""
        return self.get_all_clients_from_db()

    async def get_clients_async(self) -> List[Dict[str, Any]]:
        """Async version of get_clients using persistent mock store."""
        if self.real_server and hasattr(self.real_server, 'get_all_clients_from_db_async'):
            try:
                raw_data = await self.real_server.get_all_clients_from_db_async()
                return self._normalize_client_data(raw_data)
            except Exception as e:
                logger.error(f"Real server async get_clients failed: {e}")
                # Fall through to persistent mock fallback

        # Persistent mock fallback with realistic async simulation
        await asyncio.sleep(0.02)  # Slightly more realistic delay
        raw_data = self.mock_generator.get_clients()
        return self._normalize_client_data(raw_data)

    def disconnect_client(self, client_id: str) -> Dict[str, Any]:
        """Disconnect a client."""
        def mock_fallback():
            logger.info(f"[ServerBridge] FALLBACK: Disconnecting client from mock data: {client_id}")
            success = self.mock_generator.disconnect_client(client_id)
            if success:
                return self._create_success_response(
                    f"Client {client_id} disconnected successfully",
                    data={"disconnected": True},
                    mode='mock'
                )
            else:
                return self._create_error_response(
                    f"Client {client_id} not found or disconnection failed",
                    error_code='CLIENT_NOT_FOUND',
                    mode='mock'
                )

        return self._handle_server_operation(
            "disconnect_client",
            "disconnect_client",
            mock_fallback,
            client_id
        )

    async def disconnect_client_async(self, client_id: str) -> Dict[str, Any]:
        """Async version of disconnect_client."""
        if self.real_server and hasattr(self.real_server, 'disconnect_client_async'):
            try:
                result = await self.real_server.disconnect_client_async(client_id)
                logger.debug("[ServerBridge] Real server disconnect_client_async successful.")

                # If result is already a dict with success/message, return as-is but add mode
                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result

                # Otherwise, wrap the result
                return self._create_success_response(
                    f"Client {client_id} disconnected successfully",
                    data={"disconnected": result},
                    mode='real'
                )
            except Exception as e:
                logger.error(f"Real server disconnect_client_async failed: {e}")
                return self._create_error_response(
                    f"Real server disconnect_client_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback
        logger.info(f"[ServerBridge] FALLBACK: Async disconnecting client from mock data: {client_id}")
        try:
            # Add brief async delay to simulate processing
            await asyncio.sleep(0.1)

            success = self.mock_generator.disconnect_client(client_id)
            if success:
                return self._create_success_response(
                    f"Client {client_id} disconnected successfully",
                    data={"disconnected": True},
                    mode='mock'
                )
            else:
                return self._create_error_response(
                    f"Client {client_id} not found or disconnection failed",
                    error_code='CLIENT_NOT_FOUND',
                    mode='mock'
                )
        except Exception as e:
            logger.error(f"Mock disconnect_client_async failed: {e}")
            return self._create_error_response(
                f"Mock disconnect_client_async failed: {str(e)}",
                error_code='MOCK_OPERATION_ERROR',
                mode='mock'
            )

    def resolve_client(self, client_id: str) -> Optional[Dict]:
        """Resolve client information by ID."""
        if self.real_server and hasattr(self.real_server, 'resolve_client'):
            try:
                return self.real_server.resolve_client(client_id)
            except Exception as e:
                logger.error(f"Real server resolve_client failed: {e}")

        # Mock fallback
        logger.debug(f"[ServerBridge] FALLBACK: Resolving client for ID: {client_id}")
        clients = self.mock_generator.get_clients()
        return next((c for c in clients if c.get('id') == client_id), None)

    def get_client_details(self, client_id: str) -> Dict[str, Any]:
        """Get detailed client information."""
        if self.real_server and hasattr(self.real_server, 'get_client_details'):
            try:
                return self.real_server.get_client_details(client_id)
            except Exception as e:
                logger.error(f"Real server get_client_details failed: {e}")

        # Mock fallback
        logger.debug(f"[ServerBridge] FALLBACK: Getting mock client details for ID: {client_id}")
        if (client := self.resolve_client(client_id)):
            # Add extra details for detailed view
            client['connection_time'] = '2025-09-07T10:00:00Z'
            client['total_files'] = 42
            client['total_size'] = '1.2 GB'
            client['last_backup'] = '2025-09-07T09:30:00Z'
            return client
        return {}

    async def add_client_async(self, client_data: dict) -> Dict[str, Any]:
        """Add a new client (async version).

        Args:
            client_data: Dictionary containing client information (name, settings, etc.)

        Returns:
            Dict with 'success', 'message', and 'data' fields
        """
        if self.real_server and hasattr(self.real_server, 'add_client_async'):
            try:
                result = await self.real_server.add_client_async(client_data)
                logger.debug("[ServerBridge] Real server add_client_async successful.")

                # If result is already a dict with success/message, return as-is but add mode
                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result

                # Otherwise, wrap the result
                return self._create_success_response(
                    f"Client '{client_data.get('name', 'Unknown')}' added successfully",
                    data=result,
                    mode='real'
                )
            except Exception as e:
                logger.error(f"Real server add_client_async failed: {e}")
                return self._create_error_response(
                    f"Real server add_client_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback
        logger.info(f"[ServerBridge] FALLBACK: Adding client to persistent mock store: {client_data}")
        try:
            # Add brief async delay to simulate processing
            await asyncio.sleep(0.1)

            # Generate new client with provided data
            new_client = self.mock_generator.add_client(client_data)
            if new_client:
                return self._create_success_response(
                    f"Client '{client_data.get('name', 'Unknown')}' added successfully",
                    data=new_client,
                    mode='mock'
                )
            else:
                return self._create_error_response(
                    "Failed to add client to mock store",
                    error_code='MOCK_ADD_FAILED',
                    mode='mock'
                )
        except Exception as e:
            logger.error(f"Mock add_client_async failed: {e}")
            return self._create_error_response(
                f"Mock add_client_async failed: {str(e)}",
                error_code='MOCK_OPERATION_ERROR',
                mode='mock'
            )

    def delete_client(self, client_id: str) -> Dict[str, Any]:
        """Delete a client with cascading file deletion."""
        def mock_fallback(client_id: str):
            logger.info(f"[ServerBridge] FALLBACK: Deleting client from persistent mock store: {client_id}")
            success = self.mock_generator.delete_client(client_id)
            if success:
                return self._create_success_response(
                    f"Client {client_id} deleted successfully",
                    data={"deleted": True, "cascading": True},
                    mode='mock'
                )
            else:
                return self._create_error_response(
                    f"Client {client_id} not found or deletion failed",
                    error_code='CLIENT_NOT_FOUND',
                    mode='mock'
                )

        return self._handle_server_operation(
            "delete_client",
            "delete_client",
            mock_fallback,
            client_id
        )

    async def delete_client_async(self, client_id: str) -> Dict[str, Any]:
        """Delete a client with cascading file deletion (async version)."""
        if self.real_server and hasattr(self.real_server, 'delete_client_async'):
            try:
                result = await self.real_server.delete_client_async(client_id)
                logger.debug("[ServerBridge] Real server delete_client_async successful.")

                # If result is already a dict with success/message, return as-is but add mode
                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result

                # Otherwise, wrap the result
                return self._create_success_response(
                    f"Client {client_id} deleted successfully",
                    data={"deleted": result, "cascading": True},
                    mode='real'
                )
            except Exception as e:
                logger.error(f"Real server delete_client_async failed: {e}")
                return self._create_error_response(
                    f"Real server delete_client_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback
        logger.info(f"[ServerBridge] FALLBACK: Async deleting client from persistent mock store: {client_id}")
        try:
            # Add brief async delay to simulate processing
            await asyncio.sleep(0.2)

            success = self.mock_generator.delete_client(client_id)
            if success:
                return self._create_success_response(
                    f"Client {client_id} deleted successfully",
                    data={"deleted": True, "cascading": True},
                    mode='mock'
                )
            else:
                return self._create_error_response(
                    f"Client {client_id} not found or deletion failed",
                    error_code='CLIENT_NOT_FOUND',
                    mode='mock'
                )
        except Exception as e:
            logger.error(f"Mock delete_client_async failed: {e}")
            return self._create_error_response(
                f"Mock delete_client_async failed: {str(e)}",
                error_code='MOCK_OPERATION_ERROR',
                mode='mock'
            )

    # --- File Management ---

    def get_client_files(self, client_id: str) -> List[Tuple]:
        """Get files for a specific client."""
        if self.real_server and hasattr(self.real_server, 'get_client_files'):
            try:
                return self.real_server.get_client_files(client_id)
            except Exception as e:
                logger.error(f"Real server get_client_files failed: {e}")

        # Mock fallback
        logger.debug(f"[ServerBridge] FALLBACK: Getting mock files for client ID: {client_id}")
        all_files = self.mock_generator.get_files()
        client_files = [f for f in all_files if f.get('client_id') == client_id]
        # Convert to tuple format if needed
        return [(f['id'], f['name'], f['path'], f['size']) for f in client_files]

    def get_files(self) -> List[Dict[str, Any]]:
        """Get all files."""
        if self.real_server and hasattr(self.real_server, 'get_files'):
            try:
                return self.real_server.get_files()
            except Exception as e:
                logger.error(f"Real server get_files failed: {e}")

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Returning mock file data.")
        return self.mock_generator.get_files()

    async def get_files_async(self) -> List[Dict[str, Any]]:
        """Async version of get_files."""
        if self.real_server and hasattr(self.real_server, 'get_files_async'):
            try:
                return await self.real_server.get_files_async()
            except Exception as e:
                logger.error(f"Real server async get_files failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        return self.mock_generator.get_files()

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete a file - Comment 11: Normalize API responses with {success, data, mode}."""
        def mock_fallback():
            logger.info(f"[ServerBridge] FALLBACK: Deleting file from mock data: {file_id}")
            success = self.mock_generator.delete_file(file_id)
            if success:
                return self._create_success_response(
                    f"File {file_id} deleted successfully",
                    data={"deleted": True, "file_id": file_id},
                    mode='mock'
                )
            else:
                return self._create_error_response(
                    f"File {file_id} not found or deletion failed",
                    error_code='FILE_NOT_FOUND',
                    mode='mock'
                )

        return self._handle_server_operation(
            "delete_file",
            "delete_file",
            mock_fallback,
            file_id
        )

    async def delete_file_async(self, file_id: str) -> Dict[str, Any]:
        """Async version of delete_file - Comment 11: Normalize API responses with {success, data, mode}."""
        if self.real_server and hasattr(self.real_server, 'delete_file_async'):
            try:
                success = await self.real_server.delete_file_async(file_id)
                if success:
                    return self._create_success_response(
                        f"File {file_id} deleted successfully",
                        data={"deleted": True, "file_id": file_id},
                        mode='real'
                    )
                else:
                    return self._create_error_response(
                        f"File {file_id} not found or deletion failed",
                        error_code='FILE_NOT_FOUND',
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server async delete_file failed: {e}")
                # Fall through to mock fallback

        # Mock fallback with async simulation
        await asyncio.sleep(0.01)
        logger.info(f"[ServerBridge] FALLBACK: Async deleting file from mock data: {file_id}")
        success = self.mock_generator.delete_file(file_id)
        if success:
            return self._create_success_response(
                f"File {file_id} deleted successfully",
                data={"deleted": True, "file_id": file_id},
                mode='mock'
            )
        else:
            return self._create_error_response(
                f"File {file_id} not found or deletion failed",
                error_code='FILE_NOT_FOUND',
                mode='mock'
            )

    def download_file(self, file_id: str, destination_path: str) -> Dict[str, Any]:
        """Download a file.

        Returns:
            Dict with 'success' bool and 'message' str indicating real vs mock operation
        """
        if self.real_server and hasattr(self.real_server, 'download_file'):
            try:
                result = self.real_server.download_file(file_id, destination_path)
                return {
                    'success': result,
                    'message': 'File downloaded successfully' if result else 'Download failed',
                    'mode': 'real'
                }
            except Exception as e:
                logger.error(f"Real server download_file failed: {e}")

        # Mock fallback - simulate download without blocking
        logger.debug(f"[ServerBridge] FALLBACK: Simulating MOCK download for file ID: {file_id}")
        try:
            # Use asyncio.create_task only if event loop exists, otherwise use synchronous fallback
            try:
                loop = asyncio.get_running_loop()
                # Schedule the async operation in the existing event loop
                loop.create_task(self._write_mock_file_async(file_id, destination_path))
            except RuntimeError:
                # No running event loop, write file synchronously to avoid threading issues
                self._write_mock_file_sync(file_id, destination_path)
            return {
                'success': True,
                'message': 'Mock download completed - sample file created',
                'mode': 'mock'
            }
        except Exception as e:
            logger.error(f"Mock download failed: {e}")
            return {
                'success': False,
                'message': f'Mock download failed: {str(e)}',
                'mode': 'mock'
            }

    async def download_file_async(self, file_id: str, destination_path: str) -> Dict[str, Any]:
        """Async version of download_file.

        Returns:
            Dict with 'success' bool and 'message' str indicating real vs mock operation
        """
        if self.real_server and hasattr(self.real_server, 'download_file_async'):
            try:
                result = await self.real_server.download_file_async(file_id, destination_path)
                return {
                    'success': result,
                    'message': f'File downloaded successfully' if result else 'Download failed',
                    'mode': 'real'
                }
            except Exception as e:
                logger.error(f"Real server async download_file failed: {e}")

        # Mock fallback
        logger.debug(f"[ServerBridge] FALLBACK: Simulating MOCK async download for file ID: {file_id}")
        await asyncio.sleep(0.001)  # Minimal delay for UI responsiveness
        await self._write_mock_file_async(file_id, destination_path)
        return {
            'success': True,
            'message': f'Mock download completed - sample file created',
            'mode': 'mock'
        }

    async def _write_mock_file_async(self, file_id: str, destination_path: str) -> None:
        """Async helper to write mock file content without blocking."""
        try:
            async with aiofiles.open(destination_path, 'w') as f:
                await f.write(f"Mock file content for file ID: {file_id}")
            logger.debug(f"Mock file written successfully to {destination_path}")
        except Exception as e:
            logger.error(f"Async mock file write failed: {e}")

    def _write_mock_file_sync(self, file_id: str, destination_path: str) -> None:
        """Synchronous helper to write mock file content - thread-safe fallback."""
        try:
            with open(destination_path, 'w', encoding='utf-8') as f:
                f.write(f"Mock file content for file ID: {file_id}")
            logger.debug(f"Mock file written successfully to {destination_path}")
        except Exception as e:
            logger.error(f"Sync mock file write failed: {e}")

    def verify_file(self, file_id: str) -> Dict[str, Any]:
        """Verify file integrity.

        Returns:
            Dict with 'success' bool and 'message' str indicating real vs mock operation
        """
        if self.real_server and hasattr(self.real_server, 'verify_file'):
            try:
                result = self.real_server.verify_file(file_id)
                return {
                    'success': result,
                    'message': 'File verification passed' if result else 'File verification failed',
                    'mode': 'real'
                }
            except Exception as e:
                logger.error(f"Real server verify_file failed: {e}")

        # Mock fallback
        logger.debug(f"[ServerBridge] FALLBACK: Simulating MOCK verify for file ID: {file_id}")
        return {
            'success': True,
            'message': 'Mock verification passed - no real verification performed',
            'mode': 'mock'
        }

    # --- Database Operations ---

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information."""
        if self.real_server and hasattr(self.real_server, 'get_database_info'):
            try:
                return self.real_server.get_database_info()
            except Exception as e:
                logger.error(f"Real server get_database_info failed: {e}")

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Returning mock database info.")
        return self.mock_generator.get_database_info()

    def get_table_data(self, table_name: str) -> Dict[str, Any]:
        """Get table data from database."""
        if self.real_server and hasattr(self.real_server, 'get_table_data'):
            try:
                return self.real_server.get_table_data(table_name)
            except Exception as e:
                logger.error(f"Real server get_table_data failed: {e}")

        # Mock fallback
        logger.debug(f"[ServerBridge] FALLBACK: Returning mock table data for: {table_name}")
        return self.mock_generator.get_table_data(table_name)

    async def get_database_info_async(self) -> Dict[str, Any]:
        """Async version of get_database_info."""
        if self.real_server and hasattr(self.real_server, 'get_database_info_async'):
            try:
                return await self.real_server.get_database_info_async()
            except Exception as e:
                logger.error(f"Real server get_database_info_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        logger.debug("[ServerBridge] FALLBACK: Returning mock database info (async).")
        return self.mock_generator.get_database_info()

    async def get_table_data_async(self, table_name: str) -> Dict[str, Any]:
        """Async version of get_table_data."""
        if self.real_server and hasattr(self.real_server, 'get_table_data_async'):
            try:
                return await self.real_server.get_table_data_async(table_name)
            except Exception as e:
                logger.error(f"Real server get_table_data_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        logger.debug(f"[ServerBridge] FALLBACK: Returning mock table data for: {table_name} (async)")
        return self.mock_generator.get_table_data(table_name)

    def update_row(self, table_name: str, row_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a row in the database.

        Returns:
            Dict with 'success' bool and 'message' str indicating real vs mock operation
        """
        if self.real_server and hasattr(self.real_server, 'update_row'):
            try:
                result = self.real_server.update_row(table_name, row_id, updated_data)
                return {
                    'success': result,
                    'message': f'Row updated successfully in {table_name}' if result else f'Failed to update row in {table_name}',
                    'mode': 'real'
                }
            except Exception as e:
                logger.error(f"Real server update_row failed: {e}")
                return {
                    'success': False,
                    'message': f'Update failed: {str(e)}',
                    'mode': 'real'
                }

        # Mock fallback - perform actual mock data update
        logger.debug(f"[ServerBridge] FALLBACK: Performing MOCK row update in {table_name} for ID: {row_id}")
        try:
            success = self.mock_generator.update_table_row(table_name, row_id, updated_data)
            return {
                'success': success,
                'message': f'Mock update completed - row {"updated" if success else "not found"} in {table_name}',
                'mode': 'mock',
                'updated_fields': list(updated_data.keys()) if success else []
            }
        except Exception as e:
            logger.error(f"Mock update failed: {e}")
            return {
                'success': False,
                'message': f'Mock update failed: {str(e)}',
                'mode': 'mock'
            }

    def delete_row(self, table_name: str, row_id: str) -> Dict[str, Any]:
        """Delete a row from the database.

        Returns:
            Dict with 'success' bool and 'message' str indicating real vs mock operation
        """
        if self.real_server and hasattr(self.real_server, 'delete_row'):
            try:
                result = self.real_server.delete_row(table_name, row_id)
                return {
                    'success': True if result else False,
                    'message': f'Row deleted successfully from {table_name}' if result else f'Failed to delete row from {table_name}',
                    'mode': 'real'
                }
            except Exception as e:
                logger.error(f"Real server delete_row failed: {e}")
                return {
                    'success': False,
                    'message': f'Delete failed: {str(e)}',
                    'mode': 'real'
                }

        # Mock fallback - perform actual mock data deletion
        logger.debug(f"[ServerBridge] FALLBACK: Performing MOCK row deletion in {table_name} for ID: {row_id}")
        try:
            if table_name == "clients":
                success = self.mock_generator.delete_client(row_id)
            elif table_name == "files":
                success = self.mock_generator.delete_file(row_id)
            else:
                logger.warning(f"Unknown table '{table_name}' for mock deletion")
                success = False

            return {
                'success': success,
                'message': f'Mock deletion completed - row {"deleted" if success else "not found"} from {table_name}',
                'mode': 'mock',
                'table': table_name,
                'cascading': table_name == "clients"  # Indicate if this was a cascading delete
            }
        except Exception as e:
            logger.error(f"Mock deletion failed: {e}")
            return {
                'success': False,
                'message': f'Mock deletion failed: {str(e)}',
                'mode': 'mock'
            }

    # Database Manager Interface - for compatibility with existing code
    class DatabaseManager:
        def __init__(self, server_bridge):
            self.bridge = server_bridge

        def update_row(self, table_name: str, row_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
            return self.bridge.update_row(table_name, row_id, updated_data)

        def delete_row(self, table_name: str, row_id: str) -> Dict[str, Any]:
            return self.bridge.delete_row(table_name, row_id)

    @property
    def db_manager(self):
        """Get database manager for compatibility with existing code."""
        if not hasattr(self, '_db_manager'):
            self._db_manager = self.DatabaseManager(self)
        return self._db_manager

    # --- Enhanced Logging Operations ---

    def get_logs(self) -> List[Dict[str, Any]]:
        """Get server logs."""
        if self.real_server and hasattr(self.real_server, 'get_logs'):
            try:
                return self.real_server.get_logs()
            except Exception as e:
                logger.error(f"Real server get_logs failed: {e}")

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Returning mock log data.")
        return self.mock_generator.get_logs()

    async def get_logs_async(self) -> List[Dict[str, Any]]:
        """Get server logs asynchronously."""
        if self.real_server and hasattr(self.real_server, 'get_logs_async'):
            try:
                return await self.real_server.get_logs_async()
            except Exception as e:
                logger.error(f"Real server get_logs_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        logger.debug("[ServerBridge] FALLBACK: Returning mock log data (async).")
        return self.mock_generator.get_logs()

    async def clear_logs_async(self) -> Dict[str, Any]:
        """Clear all server logs asynchronously."""
        if self.real_server and hasattr(self.real_server, 'clear_logs_async'):
            try:
                result = await self.real_server.clear_logs_async()
                logger.debug("[ServerBridge] Real server clear_logs_async successful.")

                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        "Logs cleared successfully",
                        data={"cleared": result},
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server clear_logs_async failed: {e}")
                return self._create_error_response(
                    f"Real server clear_logs_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Clearing mock log data (async).")
        await asyncio.sleep(0.1)  # Simulate processing time

        try:
            # Clear logs from mock generator
            self.mock_generator.clear_logs()
            return self._create_success_response(
                "Logs cleared successfully",
                data={"cleared": True, "count": 0},
                mode='mock'
            )
        except Exception as e:
            logger.error(f"Mock clear_logs_async failed: {e}")
            return self._create_error_response(
                f"Mock clear_logs_async failed: {str(e)}",
                error_code='MOCK_OPERATION_ERROR',
                mode='mock'
            )

    async def export_logs_async(self, format: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Export logs in specified format with filters."""
        if self.real_server and hasattr(self.real_server, 'export_logs_async'):
            try:
                result = await self.real_server.export_logs_async(format, filters)
                logger.debug(f"[ServerBridge] Real server export_logs_async successful for format: {format}")

                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        f"Logs exported successfully as {format}",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server export_logs_async failed: {e}")
                return self._create_error_response(
                    f"Real server export_logs_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback with file generation
        logger.debug(f"[ServerBridge] FALLBACK: Mock exporting logs as {format} with filters: {filters}")
        await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate export processing time

        try:
            import tempfile
            import json
            import csv

            # Get logs data
            logs_data = self.mock_generator.get_logs()

            # Apply filters if provided
            if filters:
                if filters.get('level') and filters['level'] != 'ALL':
                    logs_data = [log for log in logs_data if log.get('level') == filters['level']]
                if filters.get('search'):
                    search_term = filters['search'].lower()
                    logs_data = [log for log in logs_data if
                               search_term in log.get('message', '').lower() or
                               search_term in log.get('component', '').lower()]

            # Create export file
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"logs_export_{timestamp}.{format}"

            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format}', delete=False) as f:
                if format == 'json':
                    json.dump(logs_data, f, indent=2, default=str)
                elif format == 'csv':
                    if logs_data:
                        fieldnames = ['timestamp', 'level', 'component', 'message']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        for log_entry in logs_data:
                            writer.writerow({
                                'timestamp': log_entry.get('timestamp', ''),
                                'level': log_entry.get('level', ''),
                                'component': log_entry.get('component', ''),
                                'message': log_entry.get('message', '')
                            })
                elif format == 'txt':
                    for log_entry in logs_data:
                        f.write(f"[{log_entry.get('timestamp', '')}] {log_entry.get('level', '')}: "
                               f"({log_entry.get('component', '')}) {log_entry.get('message', '')}\n")

                export_path = f.name

            return self._create_success_response(
                f"Mock logs exported as {format}",
                data={
                    'export_path': export_path,
                    'format': format,
                    'count': len(logs_data),
                    'filters_applied': filters or {}
                },
                mode='mock'
            )
        except Exception as e:
            logger.error(f"Mock export_logs_async failed: {e}")
            return self._create_error_response(
                f"Mock export_logs_async failed: {str(e)}",
                error_code='MOCK_EXPORT_ERROR',
                mode='mock'
            )

    async def get_log_statistics_async(self) -> Dict[str, Any]:
        """Get log statistics and analytics."""
        if self.real_server and hasattr(self.real_server, 'get_log_statistics_async'):
            try:
                return await self.real_server.get_log_statistics_async()
            except Exception as e:
                logger.error(f"Real server get_log_statistics_async failed: {e}")

        # Mock fallback with comprehensive statistics
        await asyncio.sleep(0.02)
        logger.debug("[ServerBridge] FALLBACK: Returning mock log statistics (async).")

        logs_data = self.mock_generator.get_logs()
        stats = {
            'total_logs': len(logs_data),
            'levels': {},
            'components': {},
            'recent_errors': 0,
            'hourly_distribution': {},
            'top_components': [],
            'error_rate': 0.0
        }

        # Calculate level distribution
        for log in logs_data:
            level = log.get('level', 'UNKNOWN')
            component = log.get('component', 'Unknown')

            stats['levels'][level] = stats['levels'].get(level, 0) + 1
            stats['components'][component] = stats['components'].get(component, 0) + 1

            if level == 'ERROR':
                stats['recent_errors'] += 1

        # Calculate error rate
        if stats['total_logs'] > 0:
            stats['error_rate'] = stats['recent_errors'] / stats['total_logs']

        # Top components
        stats['top_components'] = sorted(
            stats['components'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return stats

    async def stream_logs_async(self, callback=None) -> asyncio.Task:
        """Start real-time log streaming (mock implementation)."""
        if self.real_server and hasattr(self.real_server, 'stream_logs_async'):
            try:
                return await self.real_server.stream_logs_async(callback)
            except Exception as e:
                logger.error(f"Real server stream_logs_async failed: {e}")

        # Mock fallback - simulate streaming with actual task
        logger.debug("[ServerBridge] FALLBACK: Starting mock log streaming (async).")

        async def mock_streaming():
            """Mock streaming coroutine."""
            try:
                while True:
                    await asyncio.sleep(5)  # Stream interval
                    if callback:
                        # Generate mock log entry
                        mock_log = {
                            'timestamp': datetime.now().isoformat(),
                            'level': 'INFO',
                            'component': 'Stream',
                            'message': f'Mock streaming log at {datetime.now().strftime("%H:%M:%S")}'
                        }
                        await callback(mock_log)
            except asyncio.CancelledError:
                logger.debug("Mock log streaming cancelled")
                raise

        return asyncio.create_task(mock_streaming())

    async def stop_log_stream_async(self, stream_task: Optional[asyncio.Task] = None) -> Dict[str, Any]:
        """Stop real-time log streaming."""
        if self.real_server and hasattr(self.real_server, 'stop_log_stream_async'):
            try:
                return await self.real_server.stop_log_stream_async(stream_task)
            except Exception as e:
                logger.error(f"Real server stop_log_stream_async failed: {e}")

        # Mock fallback - stop streaming task
        logger.debug("[ServerBridge] FALLBACK: Stopping mock log streaming (async).")

        if stream_task and not stream_task.done():
            stream_task.cancel()
            try:
                await stream_task
            except asyncio.CancelledError:
                pass

        return self._create_success_response(
            "Mock log streaming stopped",
            data={'streaming': False},
            mode='mock'
        )

    # --- Server Status ---

    def get_server_status(self) -> Dict[str, Any]:
        """Get server status information."""
        if self.real_server and hasattr(self.real_server, 'get_server_status'):
            try:
                return self.real_server.get_server_status()
            except Exception as e:
                logger.error(f"Real server get_server_status failed: {e}")

        # Persistent mock fallback with real-time data
        logger.debug("[ServerBridge] FALLBACK: Returning persistent mock server status.")
        return self.mock_generator.get_server_status()

    async def get_server_status_async(self) -> Dict[str, Any]:
        """Async version of get_server_status."""
        if self.real_server and hasattr(self.real_server, 'get_server_status_async'):
            try:
                return await self.real_server.get_server_status_async()
            except Exception as e:
                logger.error(f"Real server get_server_status_async failed: {e}")

        # Persistent mock fallback with realistic async simulation
        await asyncio.sleep(0.02)
        logger.debug("[ServerBridge] FALLBACK: Returning persistent mock server status (async).")
        return self.mock_generator.get_server_status()

    def get_detailed_server_status(self) -> Dict[str, Any]:
        """Get detailed server status information including extended metrics."""
        if self.real_server and hasattr(self.real_server, 'get_detailed_server_status'):
            try:
                return self.real_server.get_detailed_server_status()
            except Exception as e:
                logger.error(f"Real server get_detailed_server_status failed: {e}")

        # Mock fallback with enhanced server status data
        logger.debug("[ServerBridge] FALLBACK: Returning mock detailed server status.")
        basic_status = self.mock_generator.get_server_status()

        # Enhance with additional metrics
        detailed_status = basic_status.copy()
        detailed_status.update({
            'active_threads': random.randint(5, 20),
            'queued_requests': random.randint(0, 10),
            'average_response_time_ms': random.uniform(10, 100),
            'peak_memory_usage_mb': random.randint(100, 500),
            'network_throughput_kbps': random.randint(1000, 10000),
            'disk_io_operations': random.randint(50, 500),
            'cache_hit_rate': random.uniform(0.7, 0.99),
            'uptime_hours': random.randint(1, 1000),
            'total_requests_processed': random.randint(1000, 100000),
            'error_rate': random.uniform(0.0, 0.05)
        })

        return detailed_status

    async def get_detailed_server_status_async(self) -> Dict[str, Any]:
        """Async version of get_detailed_server_status."""
        if self.real_server and hasattr(self.real_server, 'get_detailed_server_status_async'):
            try:
                return await self.real_server.get_detailed_server_status_async()
            except Exception as e:
                logger.error(f"Real server get_detailed_server_status_async failed: {e}")

        # Mock fallback with enhanced server status data
        await asyncio.sleep(0.02)
        logger.debug("[ServerBridge] FALLBACK: Returning mock detailed server status (async).")
        basic_status = self.mock_generator.get_server_status()

        # Enhance with additional metrics
        detailed_status = basic_status.copy()
        detailed_status.update({
            'active_threads': random.randint(5, 20),
            'queued_requests': random.randint(0, 10),
            'average_response_time_ms': random.uniform(10, 100),
            'peak_memory_usage_mb': random.randint(100, 500),
            'network_throughput_kbps': random.randint(1000, 10000),
            'disk_io_operations': random.randint(50, 500),
            'cache_hit_rate': random.uniform(0.7, 0.99),
            'uptime_hours': random.randint(1, 1000),
            'total_requests_processed': random.randint(1000, 100000),
            'error_rate': random.uniform(0.0, 0.05)
        })

        return detailed_status

    def get_server_health(self) -> Dict[str, Any]:
        """Get server health metrics and status."""
        if self.real_server and hasattr(self.real_server, 'get_server_health'):
            try:
                return self.real_server.get_server_health()
            except Exception as e:
                logger.error(f"Real server get_server_health failed: {e}")

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Returning mock server health data.")
        return self.mock_generator.get_server_health()

    async def get_server_health_async(self) -> Dict[str, Any]:
        """Async version of get_server_health."""
        if self.real_server and hasattr(self.real_server, 'get_server_health_async'):
            try:
                return await self.real_server.get_server_health_async()
            except Exception as e:
                logger.error(f"Real server get_server_health_async failed: {e}")

        # Mock fallback
        await asyncio.sleep(0.02)
        logger.debug("[ServerBridge] FALLBACK: Returning mock server health data (async).")
        return self.mock_generator.get_server_health()

    async def get_system_status_async(self) -> Dict[str, Any]:
        """Async version of get_system_status."""
        if self.real_server and hasattr(self.real_server, 'get_system_status_async'):
            try:
                return await self.real_server.get_system_status_async()
            except Exception as e:
                logger.error(f"Real server get_system_status_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        logger.debug("[ServerBridge] FALLBACK: Returning mock system status (async).")
        return self.mock_generator.get_system_status()

    async def get_analytics_data_async(self) -> Dict[str, Any]:
        """Async version of get_analytics_data."""
        if self.real_server and hasattr(self.real_server, 'get_analytics_data_async'):
            try:
                return await self.real_server.get_analytics_data_async()
            except Exception as e:
                logger.error(f"Real server get_analytics_data_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        logger.debug("[ServerBridge] FALLBACK: Returning mock analytics data (async).")
        return self.mock_generator.get_analytics_data()

    async def get_performance_metrics_async(self) -> Dict[str, Any]:
        """Async version of get_performance_metrics."""
        if self.real_server and hasattr(self.real_server, 'get_performance_metrics_async'):
            try:
                return await self.real_server.get_performance_metrics_async()
            except Exception as e:
                logger.error(f"Real server get_performance_metrics_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        logger.debug("[ServerBridge] FALLBACK: Returning mock performance metrics (async).")
        return self.mock_generator.get_performance_metrics()

    async def get_historical_data_async(self, metric: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Async version of get_historical_data.

        Args:
            metric: The metric to retrieve (e.g., 'cpu_usage', 'memory_usage')
            hours: Number of hours of historical data to retrieve
        """
        if self.real_server and hasattr(self.real_server, 'get_historical_data_async'):
            try:
                return await self.real_server.get_historical_data_async(metric, hours)
            except Exception as e:
                logger.error(f"Real server get_historical_data_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        logger.debug(f"[ServerBridge] FALLBACK: Returning mock historical data for {metric} (async).")
        return self.mock_generator.get_historical_data(metric, hours)

    async def start_server_async(self) -> Dict[str, Any]:
        """Start the server (async version)."""
        async def mock_fallback():
            await asyncio.sleep(0.1)  # Simulate server startup time
            logger.debug("[ServerBridge] FALLBACK: Mock server started successfully (async).")
            return self._create_success_response(
                "Server started successfully",
                data={"server_running": True},
                mode='mock',
                server_running=True
            )

        if self.real_server and hasattr(self.real_server, 'start_server_async'):
            try:
                result = await self.real_server.start_server_async()
                logger.debug("[ServerBridge] Real server start_server_async successful.")

                # If result is already standardized, add mode and timestamp
                if isinstance(result, dict):
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        "Server started successfully",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server start_server_async failed: {e}")
                return self._create_error_response(
                    f"Failed to start server: {str(e)}",
                    error_code='SERVER_START_FAILED',
                    mode='real'
                )

        return await mock_fallback()

    async def stop_server_async(self) -> Dict[str, Any]:
        """Stop the server (async version)."""
        async def mock_fallback():
            await asyncio.sleep(0.2)  # Simulate server shutdown time
            logger.debug("[ServerBridge] FALLBACK: Mock server stopped successfully (async).")
            return self._create_success_response(
                "Server stopped successfully",
                data={"server_running": False},
                mode='mock',
                server_running=False
            )

        if self.real_server and hasattr(self.real_server, 'stop_server_async'):
            try:
                result = await self.real_server.stop_server_async()
                logger.debug("[ServerBridge] Real server stop_server_async successful.")

                # If result is already standardized, add mode and timestamp
                if isinstance(result, dict):
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        "Server stopped successfully",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server stop_server_async failed: {e}")
                return self._create_error_response(
                    f"Failed to stop server: {str(e)}",
                    error_code='SERVER_STOP_FAILED',
                    mode='real'
                )

        return await mock_fallback()

    async def get_recent_activity_async(self) -> List[Dict[str, Any]]:
        """Get recent server activity (async version)."""
        if self.real_server and hasattr(self.real_server, 'get_recent_activity_async'):
            try:
                return await self.real_server.get_recent_activity_async()
            except Exception as e:
                logger.error(f"Real server get_recent_activity_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.05)  # Simulate activity query time
        logger.debug("[ServerBridge] FALLBACK: Returning mock recent activity (async).")
        return self.mock_generator.get_recent_activity()

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary data including clients, files, transfers, and storage."""
        if self.real_server and hasattr(self.real_server, 'get_dashboard_summary'):
            try:
                return self.real_server.get_dashboard_summary()
            except Exception as e:
                logger.error(f"Real server get_dashboard_summary failed: {e}")

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Returning mock dashboard summary.")
        return self.mock_generator.get_dashboard_summary()

    async def get_dashboard_summary_async(self) -> Dict[str, Any]:
        """Async version of get_dashboard_summary."""
        if self.real_server and hasattr(self.real_server, 'get_dashboard_summary_async'):
            try:
                return await self.real_server.get_dashboard_summary_async()
            except Exception as e:
                logger.error(f"Real server get_dashboard_summary_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        logger.debug("[ServerBridge] FALLBACK: Returning mock dashboard summary (async).")
        return self.mock_generator.get_dashboard_summary()

    def get_server_statistics(self) -> Dict[str, Any]:
        """Get detailed server statistics for dashboard display."""
        if self.real_server and hasattr(self.real_server, 'get_server_statistics'):
            try:
                return self.real_server.get_server_statistics()
            except Exception as e:
                logger.error(f"Real server get_server_statistics failed: {e}")

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Returning mock server statistics.")
        return self.mock_generator.get_server_statistics()

    async def get_server_statistics_async(self) -> Dict[str, Any]:
        """Async version of get_server_statistics."""
        if self.real_server and hasattr(self.real_server, 'get_server_statistics_async'):
            try:
                return await self.real_server.get_server_statistics_async()
            except Exception as e:
                logger.error(f"Real server get_server_statistics_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        logger.debug("[ServerBridge] FALLBACK: Returning mock server statistics (async).")
        return self.mock_generator.get_server_statistics()

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status information (CPU, memory, etc.)."""
        if self.real_server and hasattr(self.real_server, 'get_system_status'):
            try:
                return self.real_server.get_system_status()
            except Exception as e:
                logger.error(f"Real server get_system_status failed: {e}")

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Returning mock system status.")
        return self.mock_generator.get_system_status()

    def get_analytics_data(self) -> Dict[str, Any]:
        """Get analytics data for performance dashboards."""
        if self.real_server and hasattr(self.real_server, 'get_analytics_data'):
            try:
                return self.real_server.get_analytics_data()
            except Exception as e:
                logger.error(f"Real server get_analytics_data failed: {e}")

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Returning mock analytics data.")
        return self.mock_generator.get_analytics_data()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics for analytics."""
        if self.real_server and hasattr(self.real_server, 'get_performance_metrics'):
            try:
                return self.real_server.get_performance_metrics()
            except Exception as e:
                logger.error(f"Real server get_performance_metrics failed: {e}")

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Returning mock performance metrics.")
        return self.mock_generator.get_performance_metrics()

    def get_historical_data(self, metric: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical data for a specific metric.

        Args:
            metric: The metric to retrieve (e.g., 'cpu_usage', 'memory_usage')
            hours: Number of hours of historical data to retrieve
        """
        if self.real_server and hasattr(self.real_server, 'get_historical_data'):
            try:
                return self.real_server.get_historical_data(metric, hours)
            except Exception as e:
                logger.error(f"Real server get_historical_data failed: {e}")

        # Mock fallback
        logger.debug(f"[ServerBridge] FALLBACK: Returning mock historical data for {metric}.")
        return self.mock_generator.get_historical_data(metric, hours)

    # --- Enhanced Settings Operations ---

    async def save_settings_async(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save settings to server storage."""
        if self.real_server and hasattr(self.real_server, 'save_settings_async'):
            try:
                result = await self.real_server.save_settings_async(settings_data)
                logger.debug("[ServerBridge] Real server save_settings_async successful.")

                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        "Settings saved successfully",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server save_settings_async failed: {e}")
                return self._create_error_response(
                    f"Real server save_settings_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback with persistent storage simulation
        logger.debug("[ServerBridge] FALLBACK: Mock saving settings (async).")
        await asyncio.sleep(0.1)  # Simulate save processing time

        try:
            # Save to mock persistent storage
            settings_file = Path("mock_server_settings.json")
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)

            return self._create_success_response(
                "Settings saved successfully",
                data={
                    'saved': True,
                    'settings_count': len(settings_data),
                    'storage': 'mock_persistent'
                },
                mode='mock'
            )
        except Exception as e:
            logger.error(f"Mock save_settings_async failed: {e}")
            return self._create_error_response(
                f"Mock save_settings_async failed: {str(e)}",
                error_code='MOCK_SAVE_ERROR',
                mode='mock'
            )

    async def load_settings_async(self) -> Dict[str, Any]:
        """Load settings from server storage."""
        if self.real_server and hasattr(self.real_server, 'load_settings_async'):
            try:
                result = await self.real_server.load_settings_async()
                logger.debug("[ServerBridge] Real server load_settings_async successful.")

                if isinstance(result, dict):
                    if 'success' in result:
                        result['mode'] = 'real'
                        result['timestamp'] = time.time()
                        return result
                    else:
                        # Direct settings data
                        return self._create_success_response(
                            "Settings loaded successfully",
                            data=result,
                            mode='real'
                        )
                else:
                    return self._create_success_response(
                        "Settings loaded successfully",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server load_settings_async failed: {e}")
                return self._create_error_response(
                    f"Real server load_settings_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback with persistent storage simulation
        logger.debug("[ServerBridge] FALLBACK: Mock loading settings (async).")
        await asyncio.sleep(0.05)  # Simulate load processing time

        try:
            # Load from mock persistent storage
            settings_file = Path("mock_server_settings.json")
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)

                return self._create_success_response(
                    "Settings loaded successfully",
                    data=settings_data,
                    mode='mock'
                )
            else:
                # Return default settings
                default_settings = {
                    'server': {
                        'port': 1256,
                        'host': '127.0.0.1',
                        'max_clients': 50,
                        'log_level': 'INFO'
                    },
                    'gui': {
                        'theme_mode': 'dark',
                        'auto_refresh': True,
                        'notifications': True
                    },
                    'monitoring': {
                        'enabled': True,
                        'interval': 2,
                        'alerts': True
                    }
                }
                return self._create_success_response(
                    "Default settings loaded",
                    data=default_settings,
                    mode='mock'
                )
        except Exception as e:
            logger.error(f"Mock load_settings_async failed: {e}")
            return self._create_error_response(
                f"Mock load_settings_async failed: {str(e)}",
                error_code='MOCK_LOAD_ERROR',
                mode='mock'
            )

    async def validate_settings_async(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate settings before saving."""
        if self.real_server and hasattr(self.real_server, 'validate_settings_async'):
            try:
                result = await self.real_server.validate_settings_async(settings_data)
                logger.debug("[ServerBridge] Real server validate_settings_async successful.")

                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        "Settings validation completed",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server validate_settings_async failed: {e}")
                return self._create_error_response(
                    f"Real server validate_settings_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback with comprehensive validation
        logger.debug("[ServerBridge] FALLBACK: Mock validating settings (async).")
        await asyncio.sleep(0.02)  # Simulate validation processing time

        try:
            validation_results = {
                'valid': True,
                'errors': [],
                'warnings': []
            }

            # Validate server settings
            if 'server' in settings_data:
                server_settings = settings_data['server']

                # Port validation
                port = server_settings.get('port')
                if port and (not isinstance(port, int) or port < 1024 or port > 65535):
                    validation_results['errors'].append("Port must be between 1024-65535")
                    validation_results['valid'] = False

                # Host validation
                host = server_settings.get('host')
                if host and not isinstance(host, str):
                    validation_results['errors'].append("Host must be a valid string")
                    validation_results['valid'] = False

                # Max clients validation
                max_clients = server_settings.get('max_clients')
                if max_clients and (not isinstance(max_clients, int) or max_clients < 1 or max_clients > 1000):
                    validation_results['errors'].append("Max clients must be between 1-1000")
                    validation_results['valid'] = False

            # Validate monitoring settings
            if 'monitoring' in settings_data:
                monitoring_settings = settings_data['monitoring']

                # Interval validation
                interval = monitoring_settings.get('interval')
                if interval and (not isinstance(interval, int) or interval < 1 or interval > 60):
                    validation_results['errors'].append("Monitoring interval must be between 1-60 seconds")
                    validation_results['valid'] = False

            # Add warnings for potential issues
            if settings_data.get('server', {}).get('port') == 80:
                validation_results['warnings'].append("Port 80 may require administrator privileges")

            return self._create_success_response(
                "Settings validation completed",
                data=validation_results,
                mode='mock'
            )
        except Exception as e:
            logger.error(f"Mock validate_settings_async failed: {e}")
            return self._create_error_response(
                f"Mock validate_settings_async failed: {str(e)}",
                error_code='MOCK_VALIDATION_ERROR',
                mode='mock'
            )

    async def backup_settings_async(self, backup_name: str, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a backup of current settings."""
        if self.real_server and hasattr(self.real_server, 'backup_settings_async'):
            try:
                result = await self.real_server.backup_settings_async(backup_name, settings_data)
                logger.debug("[ServerBridge] Real server backup_settings_async successful.")

                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        "Settings backup created successfully",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server backup_settings_async failed: {e}")
                return self._create_error_response(
                    f"Real server backup_settings_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback with file-based backup
        logger.debug(f"[ServerBridge] FALLBACK: Mock creating settings backup: {backup_name} (async).")
        await asyncio.sleep(0.1)  # Simulate backup processing time

        try:
            # Create backup file
            backup_dir = Path("settings_backups")
            backup_dir.mkdir(exist_ok=True)

            backup_file = backup_dir / f"{backup_name}.json"
            with open(backup_file, 'w', encoding='utf-8') as f:
                backup_data = {
                    'created_at': time.time(),
                    'backup_name': backup_name,
                    'settings': settings_data
                }
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            return self._create_success_response(
                "Settings backup created successfully",
                data={
                    'backup_file': str(backup_file),
                    'backup_name': backup_name,
                    'created_at': time.time()
                },
                mode='mock'
            )
        except Exception as e:
            logger.error(f"Mock backup_settings_async failed: {e}")
            return self._create_error_response(
                f"Mock backup_settings_async failed: {str(e)}",
                error_code='MOCK_BACKUP_ERROR',
                mode='mock'
            )

    async def restore_settings_async(self, backup_file: str, settings_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Restore settings from backup."""
        if self.real_server and hasattr(self.real_server, 'restore_settings_async'):
            try:
                result = await self.real_server.restore_settings_async(backup_file, settings_data)
                logger.debug("[ServerBridge] Real server restore_settings_async successful.")

                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        "Settings restored successfully",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server restore_settings_async failed: {e}")
                return self._create_error_response(
                    f"Real server restore_settings_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback with file-based restore
        logger.debug(f"[ServerBridge] FALLBACK: Mock restoring settings from: {backup_file} (async).")
        await asyncio.sleep(0.05)  # Simulate restore processing time

        try:
            if settings_data:
                # Direct settings data provided
                restored_settings = settings_data
            else:
                # Load from backup file
                backup_path = Path(backup_file)
                if backup_path.exists():
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        backup_data = json.load(f)
                    restored_settings = backup_data.get('settings', {})
                else:
                    raise FileNotFoundError(f"Backup file not found: {backup_file}")

            return self._create_success_response(
                "Settings restored successfully",
                data={
                    'restored_settings': restored_settings,
                    'backup_file': backup_file,
                    'restored_at': time.time()
                },
                mode='mock'
            )
        except Exception as e:
            logger.error(f"Mock restore_settings_async failed: {e}")
            return self._create_error_response(
                f"Mock restore_settings_async failed: {str(e)}",
                error_code='MOCK_RESTORE_ERROR',
                mode='mock'
            )

    async def get_default_settings_async(self) -> Dict[str, Any]:
        """Get default server settings."""
        if self.real_server and hasattr(self.real_server, 'get_default_settings_async'):
            try:
                result = await self.real_server.get_default_settings_async()
                logger.debug("[ServerBridge] Real server get_default_settings_async successful.")

                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        "Default settings retrieved successfully",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server get_default_settings_async failed: {e}")
                return self._create_error_response(
                    f"Real server get_default_settings_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback with comprehensive defaults
        logger.debug("[ServerBridge] FALLBACK: Mock returning default settings (async).")
        await asyncio.sleep(0.01)

        default_settings = {
            'server': {
                'port': 1256,
                'host': '127.0.0.1',
                'max_clients': 50,
                'log_level': 'INFO',
                'timeout': 30,
                'buffer_size': 4096,
                'enable_ssl': False,
                'ssl_cert_path': '',
                'ssl_key_path': ''
            },
            'gui': {
                'theme_mode': 'dark',
                'auto_refresh': True,
                'notifications': True,
                'refresh_interval': 5,
                'page_size': 50,
                'language': 'en'
            },
            'monitoring': {
                'enabled': True,
                'interval': 2,
                'alerts': True,
                'cpu_threshold': 80,
                'memory_threshold': 85,
                'disk_threshold': 90,
                'network_monitoring': True
            },
            'logging': {
                'level': 'INFO',
                'file_path': 'server.log',
                'max_file_size': 10485760,  # 10MB
                'backup_count': 5,
                'console_output': True
            },
            'security': {
                'authentication_required': False,
                'session_timeout': 3600,
                'max_login_attempts': 5,
                'lockout_duration': 900
            }
        }

        return self._create_success_response(
            "Default settings retrieved successfully",
            data=default_settings,
            mode='mock'
        )

    # --- Connection Status ---

    def is_connected(self) -> bool:
        """Check if server bridge is connected to real server."""
        return self.real_server is not None

    def test_connection(self) -> bool:
        """Test connection to real server."""
        if self.real_server and hasattr(self.real_server, 'test_connection'):
            try:
                return self.real_server.test_connection()
            except Exception as e:
                logger.error(f"Connection test failed: {e}")
                return False

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Mock connection test passed.")
        return True

    async def test_connection_async(self) -> bool:
        """Test connection to real server (async version)."""
        if self.real_server and hasattr(self.real_server, 'test_connection_async'):
            try:
                return await self.real_server.test_connection_async()
            except Exception as e:
                logger.error(f"Async connection test failed: {e}")
                return False

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.1)  # Simulate connection test time
        logger.debug("[ServerBridge] FALLBACK: Mock async connection test passed.")
        return True

    async def get_client_files_async(self, client_id: str) -> List[Tuple]:
        """Get files for a specific client (async version)."""
        if self.real_server and hasattr(self.real_server, 'get_client_files_async'):
            try:
                return await self.real_server.get_client_files_async(client_id)
            except Exception as e:
                logger.error(f"Real server async get_client_files failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.02)  # Simulate file query time
        logger.debug(f"[ServerBridge] FALLBACK: Getting mock files for client ID: {client_id} (async)")
        all_files = self.mock_generator.get_files()
        client_files = [f for f in all_files if f.get('client_id') == client_id]
        # Convert to tuple format if needed
        return [(f['id'], f['name'], f['path'], f['size']) for f in client_files]

    async def verify_file_async(self, file_id: str) -> Dict[str, Any]:
        """Verify file integrity (async version).

        Returns:
            Dict with 'success' bool and 'message' str indicating real vs mock operation
        """
        if self.real_server and hasattr(self.real_server, 'verify_file_async'):
            try:
                result = await self.real_server.verify_file_async(file_id)
                return {
                    'success': result,
                    'message': 'File verification passed' if result else 'File verification failed',
                    'mode': 'real'
                }
            except Exception as e:
                logger.error(f"Real server async verify_file failed: {e}")

        # Mock fallback with realistic verification time
        await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate file verification time
        logger.debug(f"[ServerBridge] FALLBACK: Simulating MOCK async verify for file ID: {file_id}")
        return {
            'success': True,
            'message': 'Mock verification passed - no real verification performed',
            'mode': 'mock'
        }

    async def execute_batch_operations(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple operations in parallel as a batch.

        Args:
            operations: List of operation dictionaries with 'method' and 'args' keys

        Returns:
            List of results for each operation
        """
        results = []

        if self.real_server and hasattr(self.real_server, 'execute_batch_operations'):
            try:
                return await self.real_server.execute_batch_operations(operations)
            except Exception as e:
                logger.error(f"Real server execute_batch_operations failed: {e}")
                # Fall through to mock implementation

        # Mock fallback - execute operations in parallel
        logger.debug(f"[ServerBridge] FALLBACK: Executing {len(operations)} operations in batch (mock).")

        async def execute_single_operation(op):
            method_name = op.get('method')
            args = op.get('args', [])
            kwargs = op.get('kwargs', {})

            if hasattr(self, method_name):
                method = getattr(self, method_name)
                try:
                    if asyncio.iscoroutinefunction(method):
                        return await method(*args, **kwargs)
                    else:
                        return method(*args, **kwargs)
                except Exception as e:
                    return {
                        'success': False,
                        'error': str(e),
                        'method': method_name
                    }
            else:
                return {
                    'success': False,
                    'error': f'Method {method_name} not found',
                    'method': method_name
                }

        # Execute all operations concurrently
        tasks = [execute_single_operation(op) for op in operations]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions that occurred during execution
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    'success': False,
                    'error': str(result),
                    'method': 'unknown'
                })
            else:
                processed_results.append(result)

        return processed_results

    async def batch_get_data(self, data_keys: List[str]) -> Dict[str, Any]:
        """Retrieve multiple data types in a single batch operation.

        Args:
            data_keys: List of data keys to retrieve (e.g., ['clients', 'files', 'server_status'])

        Returns:
            Dictionary with all requested data
        """
        result_data = {}

        if self.real_server and hasattr(self.real_server, 'batch_get_data'):
            try:
                return await self.real_server.batch_get_data(data_keys)
            except Exception as e:
                logger.error(f"Real server batch_get_data failed: {e}")
                # Fall through to mock implementation

        # Mock fallback - retrieve data based on keys
        logger.debug(f"[ServerBridge] FALLBACK: Retrieving batch data for keys: {data_keys}")

        # Map data keys to corresponding methods
        method_map = {
            'clients': 'get_clients_async',
            'files': 'get_files_async',
            'server_status': 'get_server_status_async',
            'system_status': 'get_system_status_async',
            'database_info': 'get_database_info_async',
            'recent_activity': 'get_recent_activity_async',
            'analytics_data': 'get_analytics_data_async',
            'performance_metrics': 'get_performance_metrics_async',
            'dashboard_summary': 'get_dashboard_summary_async',
            'server_statistics': 'get_server_statistics_async'
        }

        # Create tasks for each requested data key
        tasks = {}
        for key in data_keys:
            if key in method_map and hasattr(self, method_map[key]):
                method = getattr(self, method_map[key])
                tasks[key] = method()

        # Execute all tasks concurrently
        if tasks:
            try:
                results = await asyncio.gather(*[task for task in tasks.values()], return_exceptions=True)
                for i, (key, _) in enumerate(tasks.items()):
                    if isinstance(results[i], Exception):
                        result_data[key] = {
                            'success': False,
                            'error': str(results[i])
                        }
                    else:
                        result_data[key] = results[i]
            except Exception as e:
                logger.error(f"Batch data retrieval failed: {e}")
                return {
                    'success': False,
                    'error': str(e)
                }

        return result_data

    async def export_analytics_data_async(self, format: str = "csv", metrics: dict = None) -> Dict[str, Any]:
        """Export analytics data to file (async version).

        Args:
            format: Export format ('csv', 'json', 'xlsx')
            metrics: Analytics metrics to export

        Returns:
            Dict with success status and export path
        """
        if self.real_server and hasattr(self.real_server, 'export_analytics_data_async'):
            try:
                result = await self.real_server.export_analytics_data_async(format, metrics)
                logger.debug(f"[ServerBridge] Real server analytics export successful.")
                return self._create_success_response(
                    f"Analytics data exported to {format} format",
                    data=result,
                    mode='real'
                )
            except Exception as e:
                logger.error(f"Real server export_analytics_data_async failed: {e}")
                return self._create_error_response(
                    f"Real server analytics export failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback with realistic export simulation
        await asyncio.sleep(random.uniform(0.5, 2.0))  # Simulate export processing time
        logger.debug(f"[ServerBridge] FALLBACK: Simulating MOCK analytics export to {format} format")

        import tempfile
        import os
        import json

        # Create mock export file
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format}', delete=False) as f:
                if format == 'json':
                    json.dump(metrics or {}, f, indent=2, default=str)
                else:
                    # Simple CSV-like format for other formats
                    f.write("metric,value\n")
                    if metrics:
                        for key, value in metrics.items():
                            f.write(f"{key},{value}\n")

                export_path = f.name

            return self._create_success_response(
                f"Mock analytics data exported to {format} format",
                data={'export_path': export_path, 'format': format},
                mode='mock'
            )
        except Exception as e:
            return self._create_error_response(
                f"Mock analytics export failed: {str(e)}",
                error_code='MOCK_EXPORT_ERROR',
                mode='mock'
            )

    # --- Enhanced Batch Operations for Logs and Settings ---

    async def batch_logs_operations_async(self, operations: List[Dict[str, Any]],
                                        progress_callback=None,
                                        cancellation_token=None) -> Dict[str, Any]:
        """Execute multiple log operations efficiently in batch.

        Args:
            operations: List of log operation dictionaries
            progress_callback: Optional callback for progress updates
            cancellation_token: Optional cancellation token for long operations

        Returns:
            Dict with batch operation results and statistics
        """
        if self.real_server and hasattr(self.real_server, 'batch_logs_operations_async'):
            try:
                result = await self.real_server.batch_logs_operations_async(
                    operations, progress_callback, cancellation_token
                )
                logger.debug("[ServerBridge] Real server batch_logs_operations_async successful.")

                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        "Batch log operations completed successfully",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server batch_logs_operations_async failed: {e}")
                return self._create_error_response(
                    f"Real server batch_logs_operations_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback with comprehensive batch processing
        logger.debug(f"[ServerBridge] FALLBACK: Processing {len(operations)} log operations in batch (async).")

        try:
            results = []
            completed = 0
            total = len(operations)

            for i, operation in enumerate(operations):
                # Check for cancellation
                if cancellation_token and cancellation_token.get('cancelled', False):
                    logger.info("Batch log operations cancelled by user")
                    return self._create_error_response(
                        "Batch operations cancelled",
                        error_code='OPERATION_CANCELLED',
                        mode='mock',
                        completed=completed,
                        total=total
                    )

                # Process individual operation
                op_type = operation.get('type', 'unknown')
                op_params = operation.get('params', {})

                try:
                    if op_type == 'clear_logs':
                        result = await self.clear_logs_async()
                    elif op_type == 'export_logs':
                        format_type = op_params.get('format', 'json')
                        filters = op_params.get('filters', {})
                        result = await self.export_logs_async(format_type, filters)
                    elif op_type == 'get_log_statistics':
                        result = await self.get_log_statistics_async()
                    elif op_type == 'stream_logs':
                        callback = op_params.get('callback')
                        result = await self.stream_logs_async(callback)
                    else:
                        result = self._create_error_response(
                            f"Unknown log operation type: {op_type}",
                            error_code='UNKNOWN_OPERATION',
                            mode='mock'
                        )

                    results.append({
                        'operation': operation,
                        'result': result,
                        'index': i
                    })

                    if result.get('success', False):
                        completed += 1

                except Exception as e:
                    logger.error(f"Batch log operation {i} failed: {e}")
                    results.append({
                        'operation': operation,
                        'result': self._create_error_response(
                            f"Operation failed: {str(e)}",
                            error_code='OPERATION_ERROR',
                            mode='mock'
                        ),
                        'index': i
                    })

                # Report progress
                if progress_callback:
                    try:
                        progress_callback({
                            'completed': completed,
                            'total': total,
                            'percentage': (completed / total) * 100,
                            'current_operation': op_type
                        })
                    except Exception as e:
                        logger.warning(f"Progress callback failed: {e}")

                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.01)

            success_count = sum(1 for r in results if r['result'].get('success', False))

            return self._create_success_response(
                f"Batch log operations completed: {success_count}/{total} successful",
                data={
                    'results': results,
                    'statistics': {
                        'total_operations': total,
                        'successful': success_count,
                        'failed': total - success_count,
                        'completion_rate': (success_count / total) * 100 if total > 0 else 0
                    }
                },
                mode='mock'
            )

        except Exception as e:
            logger.error(f"Mock batch_logs_operations_async failed: {e}")
            return self._create_error_response(
                f"Mock batch_logs_operations_async failed: {str(e)}",
                error_code='MOCK_BATCH_ERROR',
                mode='mock'
            )

    async def batch_settings_operations_async(self, operations: List[Dict[str, Any]],
                                            progress_callback=None,
                                            cancellation_token=None) -> Dict[str, Any]:
        """Execute multiple settings operations efficiently in batch.

        Args:
            operations: List of settings operation dictionaries
            progress_callback: Optional callback for progress updates
            cancellation_token: Optional cancellation token for long operations

        Returns:
            Dict with batch operation results and statistics
        """
        if self.real_server and hasattr(self.real_server, 'batch_settings_operations_async'):
            try:
                result = await self.real_server.batch_settings_operations_async(
                    operations, progress_callback, cancellation_token
                )
                logger.debug("[ServerBridge] Real server batch_settings_operations_async successful.")

                if isinstance(result, dict) and 'success' in result:
                    result['mode'] = 'real'
                    result['timestamp'] = time.time()
                    return result
                else:
                    return self._create_success_response(
                        "Batch settings operations completed successfully",
                        data=result,
                        mode='real'
                    )
            except Exception as e:
                logger.error(f"Real server batch_settings_operations_async failed: {e}")
                return self._create_error_response(
                    f"Real server batch_settings_operations_async failed: {str(e)}",
                    error_code='REAL_SERVER_ERROR',
                    mode='real'
                )

        # Mock fallback with comprehensive batch processing
        logger.debug(f"[ServerBridge] FALLBACK: Processing {len(operations)} settings operations in batch (async).")

        try:
            results = []
            completed = 0
            total = len(operations)

            for i, operation in enumerate(operations):
                # Check for cancellation
                if cancellation_token and cancellation_token.get('cancelled', False):
                    logger.info("Batch settings operations cancelled by user")
                    return self._create_error_response(
                        "Batch operations cancelled",
                        error_code='OPERATION_CANCELLED',
                        mode='mock',
                        completed=completed,
                        total=total
                    )

                # Process individual operation
                op_type = operation.get('type', 'unknown')
                op_params = operation.get('params', {})

                try:
                    if op_type == 'save_settings':
                        settings_data = op_params.get('settings_data', {})
                        result = await self.save_settings_async(settings_data)
                    elif op_type == 'load_settings':
                        result = await self.load_settings_async()
                    elif op_type == 'validate_settings':
                        settings_data = op_params.get('settings_data', {})
                        result = await self.validate_settings_async(settings_data)
                    elif op_type == 'backup_settings':
                        backup_name = op_params.get('backup_name', f'backup_{int(time.time())}')
                        settings_data = op_params.get('settings_data', {})
                        result = await self.backup_settings_async(backup_name, settings_data)
                    elif op_type == 'restore_settings':
                        backup_file = op_params.get('backup_file', '')
                        settings_data = op_params.get('settings_data')
                        result = await self.restore_settings_async(backup_file, settings_data)
                    elif op_type == 'get_default_settings':
                        result = await self.get_default_settings_async()
                    else:
                        result = self._create_error_response(
                            f"Unknown settings operation type: {op_type}",
                            error_code='UNKNOWN_OPERATION',
                            mode='mock'
                        )

                    results.append({
                        'operation': operation,
                        'result': result,
                        'index': i
                    })

                    if result.get('success', False):
                        completed += 1

                except Exception as e:
                    logger.error(f"Batch settings operation {i} failed: {e}")
                    results.append({
                        'operation': operation,
                        'result': self._create_error_response(
                            f"Operation failed: {str(e)}",
                            error_code='OPERATION_ERROR',
                            mode='mock'
                        ),
                        'index': i
                    })

                # Report progress
                if progress_callback:
                    try:
                        progress_callback({
                            'completed': completed,
                            'total': total,
                            'percentage': (completed / total) * 100,
                            'current_operation': op_type
                        })
                    except Exception as e:
                        logger.warning(f"Progress callback failed: {e}")

                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.01)

            success_count = sum(1 for r in results if r['result'].get('success', False))

            return self._create_success_response(
                f"Batch settings operations completed: {success_count}/{total} successful",
                data={
                    'results': results,
                    'statistics': {
                        'total_operations': total,
                        'successful': success_count,
                        'failed': total - success_count,
                        'completion_rate': (success_count / total) * 100 if total > 0 else 0
                    }
                },
                mode='mock'
            )

        except Exception as e:
            logger.error(f"Mock batch_settings_operations_async failed: {e}")
            return self._create_error_response(
                f"Mock batch_settings_operations_async failed: {str(e)}",
                error_code='MOCK_BATCH_ERROR',
                mode='mock'
            )

    # --- Enhanced Error Handling and Retry Mechanisms ---

    async def _execute_with_retry(self, operation_func, max_retries: int = 3,
                                retry_delay: float = 1.0,
                                exponential_backoff: bool = True) -> Dict[str, Any]:
        """Execute an operation with retry logic and exponential backoff.

        Args:
            operation_func: Async function to execute
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries in seconds
            exponential_backoff: Whether to use exponential backoff

        Returns:
            Dict with operation result or error information
        """
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                result = await operation_func()

                # If we get here, operation succeeded
                if attempt > 0:
                    logger.info(f"Operation succeeded after {attempt} retries")

                return result

            except Exception as e:
                last_exception = e
                logger.warning(f"Operation attempt {attempt + 1} failed: {e}")

                # Don't retry on the last attempt
                if attempt < max_retries:
                    # Calculate delay with optional exponential backoff
                    if exponential_backoff:
                        delay = retry_delay * (2 ** attempt)
                    else:
                        delay = retry_delay

                    logger.info(f"Retrying in {delay:.2f} seconds...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Operation failed after {max_retries + 1} attempts")

        # All retries exhausted
        return self._create_error_response(
            f"Operation failed after {max_retries + 1} attempts: {str(last_exception)}",
            error_code='MAX_RETRIES_EXCEEDED',
            mode='retry_failed',
            attempts=max_retries + 1,
            last_error=str(last_exception)
        )

    async def get_logs_with_retry_async(self, max_retries: int = 3) -> List[Dict[str, Any]]:
        """Get logs with automatic retry on failure."""
        async def operation():
            return await self.get_logs_async()

        result = await self._execute_with_retry(operation, max_retries)

        # If retry mechanism returns error dict, extract the actual data or return empty list
        if isinstance(result, dict) and not result.get('success', True):
            logger.warning("Failed to get logs after retries, returning empty list")
            return []

        return result if isinstance(result, list) else []

    async def save_settings_with_retry_async(self, settings_data: Dict[str, Any],
                                           max_retries: int = 3) -> Dict[str, Any]:
        """Save settings with automatic retry on failure."""
        async def operation():
            return await self.save_settings_async(settings_data)

        return await self._execute_with_retry(operation, max_retries)

    async def export_logs_with_retry_async(self, format: str, filters: Dict[str, Any] = None,
                                         max_retries: int = 3) -> Dict[str, Any]:
        """Export logs with automatic retry on failure."""
        async def operation():
            return await self.export_logs_async(format, filters)

        return await self._execute_with_retry(operation, max_retries)

    # --- Progress Tracking for Long-Running Operations ---

    class ProgressTracker:
        """Helper class for tracking progress of long-running operations."""

        def __init__(self, total_steps: int, operation_name: str = "Operation"):
            self.total_steps = total_steps
            self.current_step = 0
            self.operation_name = operation_name
            self.start_time = time.time()
            self.callbacks = []
            self.cancelled = False

        def add_callback(self, callback):
            """Add a progress callback function."""
            self.callbacks.append(callback)

        def update(self, step: int = None, message: str = None):
            """Update progress and notify callbacks."""
            if step is not None:
                self.current_step = step
            else:
                self.current_step += 1

            percentage = (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0
            elapsed_time = time.time() - self.start_time

            progress_data = {
                'current_step': self.current_step,
                'total_steps': self.total_steps,
                'percentage': percentage,
                'operation_name': self.operation_name,
                'message': message or f"Step {self.current_step} of {self.total_steps}",
                'elapsed_time': elapsed_time,
                'estimated_remaining': (elapsed_time / self.current_step * (self.total_steps - self.current_step)) if self.current_step > 0 else 0
            }

            for callback in self.callbacks:
                try:
                    callback(progress_data)
                except Exception as e:
                    logger.warning(f"Progress callback failed: {e}")

        def cancel(self):
            """Cancel the operation."""
            self.cancelled = True

        def is_cancelled(self) -> bool:
            """Check if operation was cancelled."""
            return self.cancelled

    async def export_logs_with_progress_async(self, format: str, filters: Dict[str, Any] = None,
                                            progress_callback=None) -> Dict[str, Any]:
        """Export logs with detailed progress tracking."""
        tracker = self.ProgressTracker(5, f"Export logs as {format}")

        if progress_callback:
            tracker.add_callback(progress_callback)

        try:
            # Step 1: Validate parameters
            tracker.update(1, "Validating export parameters")
            await asyncio.sleep(0.1)

            if tracker.is_cancelled():
                return self._create_error_response("Export cancelled", error_code='CANCELLED', mode='mock')

            # Step 2: Retrieve logs
            tracker.update(2, "Retrieving log data")
            logs_data = await self.get_logs_async()
            await asyncio.sleep(0.2)

            if tracker.is_cancelled():
                return self._create_error_response("Export cancelled", error_code='CANCELLED', mode='mock')

            # Step 3: Apply filters
            tracker.update(3, "Applying filters")
            if filters:
                # Apply filtering logic here
                pass
            await asyncio.sleep(0.1)

            if tracker.is_cancelled():
                return self._create_error_response("Export cancelled", error_code='CANCELLED', mode='mock')

            # Step 4: Generate export file
            tracker.update(4, f"Generating {format} file")
            result = await self.export_logs_async(format, filters)
            await asyncio.sleep(0.3)

            if tracker.is_cancelled():
                return self._create_error_response("Export cancelled", error_code='CANCELLED', mode='mock')

            # Step 5: Finalize
            tracker.update(5, "Export completed")

            return result

        except Exception as e:
            logger.error(f"Export with progress failed: {e}")
            return self._create_error_response(
                f"Export failed: {str(e)}",
                error_code='EXPORT_ERROR',
                mode='mock'
            )

    # --- Cancellation Support for Long-Running Operations ---

    class CancellationToken:
        """Token for cancelling long-running operations."""

        def __init__(self):
            self.cancelled = False
            self.reason = None

        def cancel(self, reason: str = "User requested cancellation"):
            """Cancel the operation with optional reason."""
            self.cancelled = True
            self.reason = reason

        def is_cancelled(self) -> bool:
            """Check if cancellation was requested."""
            return self.cancelled

        def get_reason(self) -> str:
            """Get cancellation reason."""
            return self.reason or "Operation cancelled"

    def create_cancellation_token(self) -> CancellationToken:
        """Create a new cancellation token."""
        return self.CancellationToken()

    async def export_large_dataset_async(self, dataset_type: str, format: str,
                                       cancellation_token: CancellationToken = None,
                                       progress_callback=None) -> Dict[str, Any]:
        """Export large datasets with cancellation support.

        Args:
            dataset_type: Type of dataset to export ('logs', 'analytics', 'all')
            format: Export format
            cancellation_token: Token for cancelling the operation
            progress_callback: Callback for progress updates
        """
        if not cancellation_token:
            cancellation_token = self.create_cancellation_token()

        tracker = self.ProgressTracker(10, f"Export {dataset_type} dataset")
        if progress_callback:
            tracker.add_callback(progress_callback)

        try:
            # Simulate large dataset export with multiple steps
            for step in range(1, 11):
                if cancellation_token.is_cancelled():
                    logger.info(f"Export cancelled: {cancellation_token.get_reason()}")
                    return self._create_error_response(
                        cancellation_token.get_reason(),
                        error_code='OPERATION_CANCELLED',
                        mode='mock',
                        completed_steps=step - 1,
                        total_steps=10
                    )

                tracker.update(step, f"Processing chunk {step}/10")

                # Simulate processing time with cancellation checks
                for _ in range(10):  # Check cancellation frequently during long operations
                    if cancellation_token.is_cancelled():
                        break
                    await asyncio.sleep(0.05)  # 50ms chunks

            if cancellation_token.is_cancelled():
                return self._create_error_response(
                    cancellation_token.get_reason(),
                    error_code='OPERATION_CANCELLED',
                    mode='mock'
                )

            return self._create_success_response(
                f"Large {dataset_type} dataset exported successfully",
                data={
                    'dataset_type': dataset_type,
                    'format': format,
                    'export_path': f'/tmp/export_{dataset_type}_{int(time.time())}.{format}',
                    'processing_time': time.time() - tracker.start_time
                },
                mode='mock'
            )

        except Exception as e:
            logger.error(f"Large dataset export failed: {e}")
            return self._create_error_response(
                f"Export failed: {str(e)}",
                error_code='EXPORT_ERROR',
                mode='mock'
            )


# --------------------------------------------------------------------------------------
# Minimal compatibility class: ModularServerBridge
# Several legacy tests reference this name. Provide a thin wrapper to maintain compatibility
# without re-introducing the old modular complexity.
# --------------------------------------------------------------------------------------

class ModularServerBridge(ServerBridge):
    """Compatibility shim that behaves like ServerBridge.

    Historically, a more modular bridge existed. For FletV2, we unify behavior
    while keeping the class name for tests and imports that still reference it.
    """

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(real_server_instance=kwargs.get('real_server_instance'))
        logger.debug("ModularServerBridge initialized (compat shim for ServerBridge)")


# Factory function for easy instantiation
def create_server_bridge(real_server_instance: Optional[BackupServer] = None) -> ServerBridge:
    """
    Factory function to create a unified server bridge.

    Args:
        real_server_instance: Optional real server instance for live mode

    Returns:
        ServerBridge: Instance of unified server bridge
    """
    return ServerBridge(real_server_instance)


# Legacy support - alias for backward compatibility - not sure if and why this is needed, could be redunded and not wanted. be carfull.
def create_modular_server_bridge(host: str = "127.0.0.1", port: int = 1256) -> ServerBridge:
    """
    Legacy factory function for backward compatibility.
    Now creates a unified ServerBridge in fallback mode.

    Args:
        host: Ignored (kept for compatibility)
        port: Ignored (kept for compatibility)

    Returns:
        ServerBridge: Instance in fallback mode
    """
    logger.warning("create_modular_server_bridge is deprecated. Use create_server_bridge instead.")
    return ServerBridge()  # Always return fallback mode for legacy calls
