#!/usr/bin/env python3
"""
Server Bridge for Flet GUI
Interfaces with the existing server integration system.
"""

import asyncio
import sys
import os
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

# Add project root to path to access existing server integration
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

try:
    from kivymd_gui.utils.server_integration import ServerIntegrationBridge, ServerStatus
    from kivymd_gui.models.data_models import ClientInfo
    BRIDGE_AVAILABLE = True
except ImportError:
    BRIDGE_AVAILABLE = False
    print("[INFO] Server integration bridge not available - using mock data")


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
    """Bridge to interface with the server system, with enhanced mock mode."""
    
    def __init__(self):
        self.server_integration = None
        self.mock_mode = not BRIDGE_AVAILABLE
        
        # Enhanced mock data for development
        self.mock_server_info = ServerInfo(total_clients=15, total_transfers=128)
        self.mock_clients: List[MockClient] = []
        self.mock_logs: List[Dict[str, Any]] = []
        
        if self.mock_mode:
            print("[INFO] Running in Mock Mode with simulated activity.")
            asyncio.create_task(self.simulate_activity())

        if BRIDGE_AVAILABLE:
            try:
                self.server_integration = ServerIntegrationBridge()
                self.server_integration.start_bridge()
            except Exception as e:
                print(f"[WARNING] Could not initialize server bridge: {e}")
                self.mock_mode = True

    async def get_server_status(self) -> ServerInfo:
        """Get current server status"""
        if self.mock_mode:
            self.mock_server_info.connected_clients = len(self.mock_clients)
            self.mock_server_info.active_transfers = len([c for c in self.mock_clients if c.status == 'Transferring'])
            return self.mock_server_info
        
        # Real implementation
        try:
            if self.server_integration:
                stats = self.server_integration.get_server_stats()
                info = self.server_integration.get_server_info()
                
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
            if self.server_integration:
                self.server_integration.start_server_async(standalone=False)
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
            if self.server_integration:
                self.server_integration.stop_server_async()
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
            if self.server_integration:
                self.server_integration.restart_server_async(standalone=False)
                # Wait a bit for the server to restart
                await asyncio.sleep(3)
                return True
        except Exception as e:
            print(f"[ERROR] Failed to restart server: {e}")
        
        return False

    def get_client_list(self) -> List[MockClient]:
        """Get list of connected clients."""
        if self.mock_mode:
            return self.mock_clients
        
        # Real implementation
        try:
            if self.server_integration:
                client_infos = self.server_integration.get_client_list()
                mock_clients = []
                for client_info in client_infos:
                    mock_client = MockClient(
                        client_id=client_info.client_id,
                        address=client_info.ip_address,
                        connected_at=client_info.connection_time or datetime.now(),
                        last_activity=client_info.last_seen,
                        status=client_info.status
                    )
                    mock_clients.append(mock_client)
                return mock_clients
        except Exception as e:
            print(f"[ERROR] Failed to get client list: {e}")
        
        return []

    def get_recent_activity(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent server activity logs."""
        if self.mock_mode:
            return self.mock_logs[:count]
        
        # For real implementation, we would get logs from the server
        # For now, return empty list
        return []

    def is_mock_mode(self) -> bool:
        return self.mock_mode

    # --- Mock Mode Simulation --- #

    def add_mock_log(self, source: str, message: str, level: str):
        self.mock_logs.insert(0, {
            "timestamp": datetime.now(),
            "source": source,
            "message": message,
            "level": level
        })
        if len(self.mock_logs) > 100: # Keep a history of 100 logs
            self.mock_logs.pop()

    async def simulate_activity(self):
        """A background task to simulate server activity in mock mode."""
        client_id_counter = 0
        while True:
            await asyncio.sleep(random.uniform(3, 10))
            if not self.mock_server_info.running:
                continue

            action = random.choice(["connect", "disconnect", "transfer_start", "transfer_end", "error"])

            if action == "connect" and len(self.mock_clients) < 10:
                client_id_counter += 1
                new_client = MockClient(
                    client_id=f"client_{client_id_counter}",
                    address=f"192.168.1.{random.randint(100, 200)}",
                    connected_at=datetime.now(),
                    last_activity=datetime.now()
                )
                self.mock_clients.append(new_client)
                self.add_mock_log(new_client.client_id, "Connected to server", "INFO")

            elif action == "disconnect" and self.mock_clients:
                client_to_disconnect = random.choice(self.mock_clients)
                self.mock_clients.remove(client_to_disconnect)
                self.add_mock_log(client_to_disconnect.client_id, "Disconnected from server", "INFO")

            elif action == "transfer_start" and any(c.status == "Idle" for c in self.mock_clients):
                client = random.choice([c for c in self.mock_clients if c.status == "Idle"])
                client.status = "Transferring"
                self.add_mock_log(client.client_id, f"Started file transfer: backup_{random.randint(1,100)}.dat", "SUCCESS")

            elif action == "transfer_end" and any(c.status == "Transferring" for c in self.mock_clients):
                client = random.choice([c for c in self.mock_clients if c.status == "Transferring"])
                client.status = "Idle"
                self.add_mock_log(client.client_id, "File transfer completed successfully", "SUCCESS")

            elif action == "error" and self.mock_clients:
                client = random.choice(self.mock_clients)
                self.add_mock_log(client.client_id, "CRC check failed for a file chunk", "ERROR")