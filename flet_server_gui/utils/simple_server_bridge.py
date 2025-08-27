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
    
    def is_server_running(self) -> bool:
        """Check if backup server is running"""
        return self.server_info.running
    
    def get_clients(self) -> List[Dict[str, Any]]:
        """Get list of connected clients (standardized API)"""
        return self.get_client_list()
    
    def get_files(self) -> List[Dict[str, Any]]:
        """Get list of managed files (standardized API)"""
        return self.get_file_list()
    
    def get_notifications(self) -> List[Dict[str, Any]]:
        """Get pending notifications"""
        mock_notifications = []
        
        # Add server status notification
        if self.server_info.running:
            mock_notifications.append({
                "id": 1,
                "type": "system",
                "message": f"Server running on {self.server_info.host}:{self.server_info.port}",
                "timestamp": datetime.now().isoformat(),
                "severity": "info"
            })
        else:
            mock_notifications.append({
                "id": 2,
                "type": "system", 
                "message": "Server is currently stopped",
                "timestamp": datetime.now().isoformat(),
                "severity": "warning"
            })
        
        # Add client activity notifications
        connected_count = len([c for c in self.mock_clients if c["status"] == "connected"])
        if connected_count > 0:
            mock_notifications.append({
                "id": 3,
                "type": "client",
                "message": f"{connected_count} client(s) currently connected",
                "timestamp": datetime.now().isoformat(),
                "severity": "info"
            })
        
        # Add file activity notification
        mock_notifications.append({
            "id": 4,
            "type": "file",
            "message": f"{len(self.mock_files)} files in backup storage",
            "timestamp": datetime.now().isoformat(),
            "severity": "info"
        })
        
        return mock_notifications

    # ============================================================================
    # MISSING METHODS FOR COMPLETE MODULARSERVERBRIDGE COMPATIBILITY
    # ============================================================================

    async def cleanup_old_files_by_age(self, days_threshold: int) -> Dict[str, Any]:
        """Clean up old files by age threshold (async version for button compatibility)"""
        await asyncio.sleep(0.8)  # Simulate cleanup time
        cleaned_count = max(0, min(len(self.mock_files), days_threshold // 10))  # Mock calculation
        freed_space_mb = cleaned_count * 2.5  # Mock space calculation
        
        return {
            "cleaned_files": cleaned_count,
            "freed_space": f"{freed_space_mb:.1f} MB",
            "days_threshold": days_threshold,
            "status": "success"
        }

    def get_all_clients(self) -> List[Dict[str, Any]]:
        """Get all clients (standardized method name for compatibility)"""
        return self.mock_clients.copy()

    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get all files (standardized method name for compatibility)"""
        return self.mock_files.copy()

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        current_time = datetime.now().isoformat()
        connected_clients = len([c for c in self.mock_clients if c["status"] == "connected"])
        idle_clients = len([c for c in self.mock_clients if c["status"] == "idle"]) 
        disconnected_clients = len([c for c in self.mock_clients if c["status"] == "disconnected"])
        
        return {
            "total_clients": len(self.mock_clients),
            "connected_clients": connected_clients,
            "idle_clients": idle_clients,
            "disconnected_clients": disconnected_clients,
            "total_files": len(self.mock_files),
            "total_storage_mb": sum(file.get("size", 0) for file in self.mock_files) / (1024 * 1024),
            "database_size_mb": 15.7,  # Mock database size
            "last_backup": "2025-08-26T10:30:00",
            "uptime_seconds": (datetime.now() - self.server_info.uptime_start).total_seconds() if self.server_info.uptime_start else 0,
            "timestamp": current_time
        }

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            import psutil
            # Try to get real system metrics, fall back to mock data
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            # Use system root drive (Windows: C:\, Unix: /)
            import os
            if os.name == 'nt':  # Windows
                disk_path = 'C:\\'
            else:  # Unix-like systems
                disk_path = '/'
            
            disk = psutil.disk_usage(disk_path)
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "memory_total_gb": memory.total / (1024**3),
                "disk_usage": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "disk_total_gb": disk.total / (1024**3),
                "network_connections": len(psutil.net_connections()),
                "boot_time": psutil.boot_time(),
                "timestamp": datetime.now().isoformat()
            }
        except (ImportError, Exception):
            # Fallback mock data if psutil not available or any error occurs
            return {
                "cpu_usage": 25.3,
                "memory_usage": 42.1,
                "memory_available_gb": 8.7,
                "memory_total_gb": 16.0,
                "disk_usage": 68.4,
                "disk_free_gb": 145.2,
                "disk_total_gb": 512.0,
                "network_connections": 15,
                "boot_time": datetime.now().timestamp() - 3600 * 24,  # 1 day ago
                "timestamp": datetime.now().isoformat()
            }

    # ============================================================================
    # ADDITIONAL COMPATIBILITY METHODS
    # ============================================================================

    def get_recent_activity(self, count: int = 50) -> List[Dict[str, Any]]:
        """Get recent activity (mock implementation)"""
        mock_activities = []
        base_time = datetime.now()
        
        # Generate some mock activities
        activities = [
            {"action": "client_connected", "details": "TestClient1 connected", "type": "connection"},
            {"action": "file_uploaded", "details": "document1.txt uploaded", "type": "file"},
            {"action": "backup_completed", "details": "Database backup completed", "type": "system"},
            {"action": "client_disconnected", "details": "TestClient4 disconnected", "type": "connection"},
            {"action": "cleanup_executed", "details": "Old files cleaned up", "type": "maintenance"},
            {"action": "server_started", "details": "Backup server started", "type": "system"},
        ]
        
        for i, activity in enumerate(activities[:count]):
            activity_time = base_time.replace(minute=base_time.minute - i * 5)
            mock_activities.append({
                "id": i + 1,
                "timestamp": activity_time.isoformat(),
                "action": activity["action"],
                "details": activity["details"],
                "type": activity["type"]
            })
        
        return mock_activities

    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        current_time = datetime.now().isoformat()
        
        # Mock health checks
        health_checks = {
            "server_process": {"status": "healthy" if self.server_info.running else "unhealthy", "message": "Server process status"},
            "database_connection": {"status": "healthy", "message": "Database connection active"},
            "disk_space": {"status": "healthy", "message": "Sufficient disk space available"},
            "memory_usage": {"status": "healthy", "message": "Memory usage within normal limits"},
            "network_connectivity": {"status": "healthy", "message": "Network connectivity OK"}
        }
        
        # Overall status
        unhealthy_checks = [check for check in health_checks.values() if check["status"] != "healthy"]
        overall_status = "healthy" if not unhealthy_checks else "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": current_time,
            "checks": health_checks,
            "unhealthy_count": len(unhealthy_checks),
            "total_checks": len(health_checks)
        }

    def get_server_performance_metrics(self) -> Dict[str, Any]:
        """Get server-specific performance metrics"""
        return {
            "active_connections": self.server_info.connected_clients,
            "total_requests_handled": 247,  # Mock value
            "average_response_time_ms": 125.3,  # Mock value
            "requests_per_minute": 12.5,  # Mock value
            "error_rate_percent": 0.8,  # Mock value
            "uptime_seconds": (datetime.now() - self.server_info.uptime_start).total_seconds() if self.server_info.uptime_start else 0,
            "peak_memory_usage_mb": 84.2,  # Mock value
            "timestamp": datetime.now().isoformat()
        }

    def is_real_integration(self) -> bool:
        """Check if using real integration (always False for simple bridge)"""
        return False

    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect a client (mock implementation)"""
        # Find and update client status
        for client in self.mock_clients:
            if str(client.get("id")) == str(client_id):
                client["status"] = "disconnected"
                return True
        return False

    def delete_client(self, client_id: str) -> bool:
        """Delete a client (mock implementation)"""
        # Remove client from mock list
        initial_count = len(self.mock_clients)
        self.mock_clients = [c for c in self.mock_clients if str(c.get("id")) != str(client_id)]
        return len(self.mock_clients) < initial_count

    def disconnect_multiple_clients(self, client_ids: List[str]) -> int:
        """Disconnect multiple clients (mock implementation)"""
        disconnected_count = 0
        for client_id in client_ids:
            if self.disconnect_client(client_id):
                disconnected_count += 1
        return disconnected_count

    def delete_multiple_clients(self, client_ids: List[str]) -> int:
        """Delete multiple clients (mock implementation)"""
        deleted_count = 0
        for client_id in client_ids:
            if self.delete_client(client_id):
                deleted_count += 1
        return deleted_count

    async def backup_database(self, destination_path: str = None) -> bool:
        """Backup database (async version with optional destination)"""
        await asyncio.sleep(1.0)  # Simulate backup time
        return True

    def export_database_to_csv(self, table_name: str, destination_path: str) -> bool:
        """Export database table to CSV (mock implementation)"""
        # Mock successful export
        return True

    def get_database_tables(self) -> List[str]:
        """Get list of database tables (mock implementation)"""
        return ["clients", "files", "transfers", "logs", "settings"]

    def import_clients_from_data(self, client_data_list: List[Dict[str, Any]]) -> int:
        """Import clients from data (mock implementation)"""
        # Add mock clients to the list
        imported_count = 0
        for client_data in client_data_list:
            if "name" in client_data:
                new_id = max([c.get("id", 0) for c in self.mock_clients], default=0) + 1
                self.mock_clients.append({
                    "id": new_id,
                    "name": client_data["name"],
                    "status": client_data.get("status", "idle")
                })
                imported_count += 1
        return imported_count

    def delete_file(self, file_info: Dict[str, Any]) -> bool:
        """Delete a file (mock implementation)"""
        initial_count = len(self.mock_files)
        filename = file_info.get("name")
        self.mock_files = [f for f in self.mock_files if f.get("name") != filename]
        return len(self.mock_files) < initial_count

    def delete_multiple_files(self, file_infos: List[Dict[str, Any]]) -> int:
        """Delete multiple files (mock implementation)"""
        deleted_count = 0
        for file_info in file_infos:
            if self.delete_file(file_info):
                deleted_count += 1
        return deleted_count

    def download_file(self, file_info: Dict[str, Any], destination_path: str) -> bool:
        """Download a file (mock implementation)"""
        # Mock successful download
        return True

    def verify_file(self, file_info: Dict[str, Any]) -> bool:
        """Verify a file (mock implementation)"""
        # Mock successful verification
        return True

    def upload_file_to_storage(self, file_path: str, client_name: str = "system") -> bool:
        """Upload file to storage (mock implementation)"""
        # Mock successful upload
        import os
        if os.path.exists(file_path):
            filename = os.path.basename(file_path)
            self.mock_files.append({
                "name": filename,
                "size": 1024,  # Mock size
                "date": datetime.now().strftime("%Y-%m-%d"),
                "client": client_name
            })
            return True
        return False

    def get_file_content(self, filename: str) -> bytes:
        """Get file content for preview (mock implementation)"""
        # Return mock content
        return f"Mock content for file: {filename}".encode('utf-8')

    def is_monitoring_available(self) -> bool:
        """Check if monitoring is available"""
        return True  # Always available in mock mode

    def get_component_stats(self) -> Dict[str, Any]:
        """Get statistics about all components"""
        return {
            'connection_manager': {
                'server_running': self.server_info.running,
                'uptime_start': self.server_info.uptime_start.isoformat() if self.server_info.uptime_start else None
            },
            'data_manager': self.get_database_stats(),
            'monitoring_manager': {
                'available': self.is_monitoring_available(),
                'health': self.get_health_status()
            },
            'file_manager': {
                'total_files': len(self.mock_files),
                'total_size_bytes': sum(f.get("size", 0) for f in self.mock_files)
            }
        }

    def register_connection_callback(self, callback):
        """Register callback for connection status changes (mock implementation)"""
        # Mock implementation - store callback but don't actually use it
        self._connection_callback = callback