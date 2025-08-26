#!/usr/bin/env python3
"""
Simple Server Bridge - Fallback implementation for development/testing
Provides mock data and basic functionality when full server bridge isn't available
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional

class SimpleServerInfo:
    """Simple server info data structure"""
    def __init__(self):
        self.running = False
        self.host = "localhost"
        self.port = 1256
        self.connected_clients = 0
        self.total_clients = 5
        self.active_transfers = 0
        self.uptime_start = None

class SimpleServerBridge:
    """Simple server bridge for testing and development"""
    
    def __init__(self):
        self.mock_mode = True
        self.server_info = SimpleServerInfo()
        self.mock_clients = [
            {"id": 1, "name": "TestClient1", "status": "connected"},
            {"id": 2, "name": "TestClient2", "status": "idle"},
            {"id": 3, "name": "TestClient3", "status": "idle"},
            {"id": 4, "name": "TestClient4", "status": "disconnected"},
            {"id": 5, "name": "TestClient5", "status": "idle"}
        ]
        self.mock_files = [
            {"name": "document1.txt", "size": 1024, "date": "2025-08-26"},
            {"name": "image.jpg", "size": 2048000, "date": "2025-08-25"},
            {"name": "config.json", "size": 512, "date": "2025-08-24"}
        ]
        
    async def get_server_status(self) -> SimpleServerInfo:
        """Get current server status"""
        return self.server_info
    
    async def start_server(self) -> bool:
        """Start the server"""
        await asyncio.sleep(0.5)  # Simulate startup time
        self.server_info.running = True
        self.server_info.uptime_start = datetime.now()
        self.server_info.connected_clients = 2
        return True
    
    async def stop_server(self) -> bool:
        """Stop the server"""
        await asyncio.sleep(0.3)  # Simulate shutdown time
        self.server_info.running = False
        self.server_info.uptime_start = None
        self.server_info.connected_clients = 0
        return True
    
    async def restart_server(self) -> bool:
        """Restart the server"""
        await self.stop_server()
        await asyncio.sleep(0.5)
        return await self.start_server()
    
    def get_client_list(self) -> List[Dict[str, Any]]:
        """Get list of registered clients"""
        return self.mock_clients.copy()
    
    def get_file_list(self) -> List[Dict[str, Any]]:
        """Get list of transferred files"""
        return self.mock_files.copy()
    
    async def backup_database(self) -> bool:
        """Backup the database"""
        await asyncio.sleep(1.0)  # Simulate backup time
        return True
    
    async def cleanup_old_files(self, days: int = 30) -> Dict[str, Any]:
        """Clean up old files"""
        await asyncio.sleep(0.8)  # Simulate cleanup time
        return {"cleaned_files": 3, "freed_space": "15.2 MB"}