#!/usr/bin/env python3
"""
Server Connection Manager
Handles server lifecycle operations (start, stop, restart) and basic status.
"""

# Enable UTF-8 support
import Shared.utils.utf8_solution

import asyncio
import threading
import sys
import os
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, project_root)

try:
    from python_server.server.server import BackupServer
    from python_server.server.config import DEFAULT_PORT
    SERVER_AVAILABLE = True
except ImportError:
    SERVER_AVAILABLE = False
    print("[WARNING] Server integration not available")


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


class ServerConnectionManager:
    """Manages server lifecycle operations and basic status"""
    
    def __init__(self, server_instance: Optional[BackupServer] = None):
        self.server_instance = server_instance
        self._server_start_time = None
        
        if not SERVER_AVAILABLE:
            raise RuntimeError("Server integration required but not available")
    
    async def get_server_status(self) -> ServerInfo:
        """Get current server status"""
        try:
            server_info = ServerInfo()
            
            if self.server_instance:
                server_info.running = self.server_instance.running
                server_info.host = "127.0.0.1"
                server_info.port = getattr(self.server_instance, 'port', 1256)
                
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
                return True
            else:
                print("[ERROR] Server failed to start")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to start server: {e}")
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
                return True
            else:
                print("[ERROR] Server failed to stop cleanly")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to stop server: {e}")
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
