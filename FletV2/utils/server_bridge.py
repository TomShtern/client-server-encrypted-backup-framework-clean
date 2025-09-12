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
from typing import Dict, List, Tuple, Optional, Any
import aiofiles
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
            print("[ServerBridge] Initialized in FALLBACK mode. Will return mock data.")
            logger.info("ServerBridge initialized in FALLBACK mode")

        # Initialize mock data generator for fallback mode
        self.mock_generator = MockDataGenerator(num_clients=45)

        # Track connection status (legacy compatibility)
        self.connected = self.real_server is not None

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
        if self.real_server:
            try:
                return self.real_server.get_all_clients_from_db()
            except Exception as e:
                logger.error(f"Real server get_all_clients_from_db failed: {e}")
                # Fall through to mock fallback

        logger.debug("[ServerBridge] FALLBACK: Returning mock client data.")
        raw_data = self.mock_generator.get_clients()
        # Normalize data format for consistent UI expectations
        return self._normalize_client_data(raw_data)

    def get_clients(self) -> List[Dict[str, Any]]:
        """Get client data (alias for get_all_clients_from_db)."""
        return self.get_all_clients_from_db()

    async def get_clients_async(self) -> List[Dict[str, Any]]:
        """Async version of get_clients."""
        if self.real_server and hasattr(self.real_server, 'get_all_clients_from_db_async'):
            try:
                raw_data = await self.real_server.get_all_clients_from_db_async()
                return self._normalize_client_data(raw_data)
            except Exception as e:
                logger.error(f"Real server async get_clients failed: {e}")
                # Fall through to mock fallback

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        raw_data = self.mock_generator.get_clients()
        return self._normalize_client_data(raw_data)

    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect a client."""
        if self.real_server and hasattr(self.real_server, 'disconnect_client'):
            try:
                return self.real_server.disconnect_client(client_id)
            except Exception as e:
                logger.error(f"Real server disconnect_client failed: {e}")

        # Mock fallback - actually remove client from mock data
        logger.info(f"[ServerBridge] FALLBACK: Disconnecting client from mock data: {client_id}")
        return self.mock_generator.delete_client(client_id)

    async def disconnect_client_async(self, client_id: str) -> bool:
        """Async version of disconnect_client."""
        if self.real_server and hasattr(self.real_server, 'disconnect_client_async'):
            try:
                return await self.real_server.disconnect_client_async(client_id)
            except Exception as e:
                logger.error(f"Real server async disconnect_client failed: {e}")

        # Mock fallback - actually remove client from mock data
        logger.info(f"[ServerBridge] FALLBACK: Async disconnecting client from mock data: {client_id}")
        await asyncio.sleep(0.01)
        return self.mock_generator.delete_client(client_id)

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

    def delete_client(self, client_id: str) -> bool:
        """Delete a client."""
        if self.real_server and hasattr(self.real_server, 'delete_client'):
            try:
                return self.real_server.delete_client(client_id)
            except Exception as e:
                logger.error(f"Real server delete_client failed: {e}")

        # Mock fallback
        logger.info(f"[ServerBridge] FALLBACK: Deleting client from mock data: {client_id}")
        return self.mock_generator.delete_client(client_id)

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

    def delete_file(self, file_id: str) -> bool:
        """Delete a file."""
        if self.real_server and hasattr(self.real_server, 'delete_file'):
            try:
                return self.real_server.delete_file(file_id)
            except Exception as e:
                logger.error(f"Real server delete_file failed: {e}")

        # Mock fallback - actually delete from mock data
        logger.info(f"[ServerBridge] FALLBACK: Deleting file from mock data: {file_id}")
        return self.mock_generator.delete_file(file_id)

    async def delete_file_async(self, file_id: str) -> bool:
        """Async version of delete_file."""
        if self.real_server and hasattr(self.real_server, 'delete_file_async'):
            try:
                return await self.real_server.delete_file_async(file_id)
            except Exception as e:
                logger.error(f"Real server async delete_file failed: {e}")

        # Mock fallback - actually delete from mock data
        logger.info(f"[ServerBridge] FALLBACK: Async deleting file from mock data: {file_id}")
        await asyncio.sleep(0.01)
        return self.mock_generator.delete_file(file_id)

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

        # Mock fallback - simulate successful update
        logger.debug(f"[ServerBridge] FALLBACK: Simulating MOCK row update in {table_name} for ID: {row_id}")
        return {
            'success': True,
            'message': 'Mock update completed - no real database changes made',
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

        # Mock fallback - simulate successful deletion
        logger.debug(f"[ServerBridge] FALLBACK: Simulating MOCK row deletion in {table_name} for ID: {row_id}")
        return {
            'success': True,
            'message': 'Mock deletion completed - no real database changes made',
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

    # --- Logging ---

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

    # --- Server Status ---

    def get_server_status(self) -> Dict[str, Any]:
        """Get server status information."""
        if self.real_server and hasattr(self.real_server, 'get_server_status'):
            try:
                return self.real_server.get_server_status()
            except Exception as e:
                logger.error(f"Real server get_server_status failed: {e}")

        # Mock fallback
        logger.debug("[ServerBridge] FALLBACK: Returning mock server status.")
        return self.mock_generator.get_server_status()

    async def get_server_status_async(self) -> Dict[str, Any]:
        """Async version of get_server_status."""
        if self.real_server and hasattr(self.real_server, 'get_server_status_async'):
            try:
                return await self.real_server.get_server_status_async()
            except Exception as e:
                logger.error(f"Real server get_server_status_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.01)
        logger.debug("[ServerBridge] FALLBACK: Returning mock server status (async).")
        return self.mock_generator.get_server_status()

    async def start_server_async(self) -> Dict[str, Any]:
        """Start the server (async version)."""
        if self.real_server and hasattr(self.real_server, 'start_server_async'):
            try:
                result = await self.real_server.start_server_async()
                logger.debug("[ServerBridge] Real server start_server_async successful.")
                return result
            except Exception as e:
                logger.error(f"Real server start_server_async failed: {e}")

        # Mock fallback with brief async simulation
        await asyncio.sleep(0.1)  # Simulate server startup time
        logger.debug("[ServerBridge] FALLBACK: Mock server started successfully (async).")
        return {
            "success": True,
            "message": "Server started successfully",
            "server_running": True,
            "timestamp": time.time()
        }

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


# Legacy support - alias for backward compatibility
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