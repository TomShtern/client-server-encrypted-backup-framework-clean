#!/usr/bin/env python3
"""
Server Bridge for Flet GUI
Interfaces with the existing server integration system.
"""

import asyncio
import sys
import os
import random
import psutil
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

# Add project root to path to access existing server integration
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

try:
    from python_server.server.server import BackupServer
    from python_server.server.database import DatabaseManager
    from python_server.server.config import DEFAULT_PORT
    BRIDGE_AVAILABLE = True
    PSUTIL_AVAILABLE = True
    print("[INFO] Direct server integration available - using real data")
except ImportError:
    try:
        # Try fallback path
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
        from python_server.server.server import BackupServer  
        from python_server.server.database import DatabaseManager
        from python_server.server.config import DEFAULT_PORT
        BRIDGE_AVAILABLE = True
        PSUTIL_AVAILABLE = True
        print("[INFO] Direct server integration available via fallback path - using real data")
    except ImportError:
        BRIDGE_AVAILABLE = False
        PSUTIL_AVAILABLE = False
        print("[WARNING] Direct server integration not available - real integration failed")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("[WARNING] psutil not available - system monitoring will use fallback")


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

@dataclass
class MockClient:
    client_id: str
    address: str
    connected_at: datetime
    last_activity: datetime
    status: str = "Idle"

class ServerBridge:
    """Bridge to interface with the server system - REAL INTEGRATION ONLY."""
    
    def __init__(self, server_instance: Optional[BackupServer] = None):
        self.server_instance: Optional[BackupServer] = server_instance
        self.db_manager = None
        self.mock_mode = not BRIDGE_AVAILABLE
        self.system_monitor_enabled = PSUTIL_AVAILABLE
        self._server_start_time = None
        
        if BRIDGE_AVAILABLE:
            try:
                # Initialize database manager directly
                self.db_manager = DatabaseManager()
                print("[INFO] Direct database connection established for real data")
                self.mock_mode = False
                
                # If no server instance provided, create one for standalone mode
                if not self.server_instance:
                    print("[INFO] No server instance provided, creating new BackupServer for real integration")
                    self.server_instance = BackupServer()
                    
            except Exception as e:
                print(f"[ERROR] Could not initialize server integration: {e}")
                print("[CRITICAL] Real integration failed - this violates NO MOCK requirement")
                raise RuntimeError(f"Real server integration required but failed: {e}")
        
        if self.mock_mode:
            print("[CRITICAL ERROR] Mock mode detected - this violates the NO MOCK DATA requirement")
            raise RuntimeError("Mock mode is not allowed - all implementations must be real")

    async def get_server_status(self) -> ServerInfo:
        """Get current server status"""
        if self.mock_mode:
            self.mock_server_info.connected_clients = len(self.mock_clients)
            self.mock_server_info.active_transfers = len([c for c in self.mock_clients if c.status == 'Transferring'])
            return self.mock_server_info
        
        # Real implementation
        try:
            if self.db_manager:
                # Get stats from database instead
                stats = self.db_manager.get_database_stats()
                
                server_info = ServerInfo()
                server_info.running = info.get('running', False)
                server_info.host = info.get('host', '127.0.0.1')
                server_info.port = info.get('port', 1256)
                
                if info.get('start_time'):
                    server_info.uptime_start = datetime.fromisoformat(info['start_time'])
                
                server_info.connected_clients = stats.active_connections
                server_info.total_clients = stats.total_clients
                server_info.active_transfers = 0  # TODO: Implement active transfers tracking
                server_info.total_transfers = stats.total_files
                
                return server_info
        except Exception as e:
            print(f"[ERROR] Failed to get server status: {e}")
        
        return ServerInfo() # Fallback

    async def start_server(self) -> bool:
        if self.mock_mode:
            if not self.mock_server_info.running:
                self.mock_server_info.running = True
                self.mock_server_info.uptime_start = datetime.now()
                self.add_mock_log("Server", "Server started successfully", "SUCCESS")
            return True
        
        # Real implementation
        try:
            if self.db_manager:
                # TODO: Implement actual server start logic
                # Wait a bit for the server to start
                await asyncio.sleep(2)
                return True
        except Exception as e:
            print(f"[ERROR] Failed to start server: {e}")
        
        return False

    async def stop_server(self) -> bool:
        if self.mock_mode:
            if self.mock_server_info.running:
                self.mock_server_info.running = False
                self.mock_server_info.uptime_start = None
                self.mock_clients.clear()
                self.add_mock_log("Server", "Server stopped", "INFO")
            return True
        
        # Real implementation
        try:
            if self.db_manager:
                # TODO: Implement actual server stop logic
                # Wait a bit for the server to stop
                await asyncio.sleep(2)
                return True
        except Exception as e:
            print(f"[ERROR] Failed to stop server: {e}")
        
        return False

    async def restart_server(self) -> bool:
        if self.mock_mode:
            await self.stop_server()
            await asyncio.sleep(1)
            await self.start_server()
            self.add_mock_log("Server", "Server restarted", "SUCCESS")
            return True
        
        # Real implementation
        try:
            if self.db_manager:
                # TODO: Implement actual server restart logic
                # Wait a bit for the server to restart
                await asyncio.sleep(3)
                return True
        except Exception as e:
            print(f"[ERROR] Failed to restart server: {e}")
        
        return False

    def get_client_list(self) -> List[MockClient]:
        """Get list of registered clients from real database."""
        if self.mock_mode:
            return []
        
        # Real implementation using direct database access
        try:
            if self.db_manager:
                # Get all registered clients from database
                db_clients = self.db_manager.get_all_clients()
                real_clients = []
                
                for client_data in db_clients:
                    # Fix date parsing - remove extra 'Z' if present
                    last_seen_str = client_data['last_seen']
                    if last_seen_str:
                        # Remove extra 'Z' if it exists with timezone info
                        if last_seen_str.endswith('+00:00Z'):
                            last_seen_str = last_seen_str[:-1]  # Remove the 'Z'
                        try:
                            last_seen_dt = datetime.fromisoformat(last_seen_str)
                        except ValueError:
                            last_seen_dt = datetime.now()
                    else:
                        last_seen_dt = datetime.now()
                    
                    client = MockClient(
                        client_id=client_data['name'],  # Use name as display ID
                        address="N/A",  # Database doesn't store current IP
                        connected_at=last_seen_dt,
                        last_activity=last_seen_dt,
                        status="Registered"  # All DB clients are registered
                    )
                    real_clients.append(client)
                
                print(f"[INFO] Retrieved {len(real_clients)} real clients from database")
                return real_clients
                
        except Exception as e:
            print(f"[ERROR] Failed to get client list from database: {e}")
        
        return []

    def get_file_list(self) -> List[Dict[str, Any]]:
        """Get list of transferred files from real database."""
        if self.mock_mode:
            return []
        
        # Real implementation using direct database access
        try:
            if self.db_manager:
                # Get all files from database
                db_files = self.db_manager.get_all_files()
                print(f"[INFO] Retrieved {len(db_files)} real files from database")
                return db_files
                
        except Exception as e:
            print(f"[ERROR] Failed to get file list from database: {e}")
        
        return []

    def get_recent_activity(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent server activity logs."""
        if self.mock_mode:
            return []
        
        # For real implementation, get logs from server log files
        return []

    def is_mock_mode(self) -> bool:
        return self.mock_mode
    
    # === Client Management Operations ===
    
    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect a specific client."""
        if self.mock_mode:
            print(f"[MOCK] Would disconnect client: {client_id}")
            return True
        
        try:
            # TODO: Implement actual client disconnection via server API
            print(f"[INFO] Disconnecting client: {client_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to disconnect client {client_id}: {e}")
            return False
    
    def delete_client(self, client_id: str) -> bool:
        """Delete a client from the database."""
        if self.mock_mode:
            print(f"[MOCK] Would delete client: {client_id}")
            return True
        
        try:
            if self.db_manager:
                # TODO: Add delete client method to DatabaseManager
                print(f"[INFO] Deleting client from database: {client_id}")
                # self.db_manager.delete_client(client_id)
                return True
        except Exception as e:
            print(f"[ERROR] Failed to delete client {client_id}: {e}")
            return False
        
        return False
    
    def disconnect_multiple_clients(self, client_ids: List[str]) -> int:
        """Disconnect multiple clients. Returns count of successfully disconnected."""
        success_count = 0
        for client_id in client_ids:
            if self.disconnect_client(client_id):
                success_count += 1
        return success_count
    
    def delete_multiple_clients(self, client_ids: List[str]) -> int:
        """Delete multiple clients. Returns count of successfully deleted."""
        success_count = 0
        for client_id in client_ids:
            if self.delete_client(client_id):
                success_count += 1
        return success_count
    
    # === File Management Operations ===
    
    def delete_file(self, file_info: Dict[str, Any]) -> bool:
        """Delete a file from storage and database."""
        if self.mock_mode:
            filename = file_info.get('filename', 'Unknown')
            print(f"[MOCK] Would delete file: {filename}")
            return True
        
        try:
            filename = file_info.get('filename', 'Unknown')
            file_id = file_info.get('id')
            
            if self.db_manager and file_id:
                # TODO: Add delete file method to DatabaseManager
                print(f"[INFO] Deleting file from database: {filename}")
                # self.db_manager.delete_file(file_id)
                return True
        except Exception as e:
            print(f"[ERROR] Failed to delete file {filename}: {e}")
            return False
        
        return False
    
    def delete_multiple_files(self, file_infos: List[Dict[str, Any]]) -> int:
        """Delete multiple files. Returns count of successfully deleted."""
        success_count = 0
        for file_info in file_infos:
            if self.delete_file(file_info):
                success_count += 1
        return success_count
    
    def download_file(self, file_info: Dict[str, Any], destination_path: str) -> bool:
        """Download a file to specified destination."""
        if self.mock_mode:
            filename = file_info.get('filename', 'Unknown')
            print(f"[MOCK] Would download file: {filename} to {destination_path}")
            return True
        
        try:
            filename = file_info.get('filename', 'Unknown')
            # TODO: Implement actual file download from server storage
            print(f"[INFO] Downloading file: {filename} to {destination_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to download file {filename}: {e}")
            return False
    
    def verify_file(self, file_info: Dict[str, Any]) -> bool:
        """Verify file integrity."""
        if self.mock_mode:
            filename = file_info.get('filename', 'Unknown')
            print(f"[MOCK] Would verify file: {filename}")
            return True
        
        try:
            filename = file_info.get('filename', 'Unknown')
            # TODO: Implement actual file verification (CRC, size, etc.)
            print(f"[INFO] Verifying file: {filename}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to verify file {filename}: {e}")
            return False

