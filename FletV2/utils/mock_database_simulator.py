"""
MockDatabase - Clean, efficient database simulator for development/testing.

Provides realistic database behavior without disk I/O or artificial complexity.
Thread-safe, maintains referential integrity, and returns data in expected formats.
"""

import asyncio
import logging
import threading
import time
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import random

logger = logging.getLogger(__name__)

@dataclass
class MockClient:
    """Mock client entity matching expected data structure."""
    id: str
    name: str
    ip_address: str
    status: str
    last_seen: str
    files_count: int
    total_size: int
    connection_time: str
    version: str
    platform: str
    sync_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return asdict(self)

@dataclass
class MockFile:
    """Mock file entity with proper relationships."""
    id: str
    client_id: str
    name: str
    path: str
    size: int
    hash: str
    created: str
    modified: str
    status: str
    backup_count: int
    last_backup: str
    type: str = "file"
    owner: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        data = asdict(self)
        data['owner'] = self.owner or self.client_id
        return data

@dataclass
class MockLogEntry:
    """Mock log entry for system logs."""
    id: int
    timestamp: str
    level: str
    component: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return asdict(self)


class MockDatabase:
    """
    Thread-safe mock database that simulates real database behavior.

    Provides CRUD operations, referential integrity, and realistic data
    without disk I/O or artificial delays.
    """

    def __init__(self):
        """Initialize mock database with seed data."""
        self._lock = threading.RLock()
        self._clients: Dict[str, MockClient] = {}
        self._files: Dict[str, MockFile] = {}
        self._logs: List[MockLogEntry] = []
        self._settings: Dict[str, Any] = {}
        self._client_files: Dict[str, List[str]] = {}  # client_id -> [file_ids]

        # Generate realistic seed data
        self._generate_seed_data()

        logger.info(f"MockDatabase initialized with {len(self._clients)} clients and {len(self._files)} files")

    def _generate_seed_data(self):
        """Generate realistic seed data for development."""

        # Generate clients
        client_names = ["Production-Server", "Dev-Workstation", "Backup-Node", "Web-Server",
                       "Database-Server", "File-Server", "Mail-Server", "Test-Environment"]

        platforms = ["Windows Server 2019", "Ubuntu 20.04", "CentOS 8", "macOS Big Sur", "Windows 10"]
        versions = ["2.1.4", "2.1.3", "2.0.8", "1.9.12"]
        statuses = ["connected", "connected", "connected", "disconnected", "offline"]

        for i in range(len(client_names)):
            client_id = str(uuid.uuid4())
            client = MockClient(
                id=client_id,
                name=client_names[i],
                ip_address=f"192.168.1.{10 + i}",
                status=random.choice(statuses[:3] if i < 6 else statuses),  # Most online
                last_seen=(datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat(),
                files_count=0,  # Will be calculated
                total_size=0,   # Will be calculated
                connection_time=(datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                version=random.choice(versions),
                platform=random.choice(platforms),
                sync_enabled=True
            )
            self._clients[client_id] = client
            self._client_files[client_id] = []

        # Generate files for each client
        file_types = [".txt", ".docx", ".pdf", ".jpg", ".png", ".mp4", ".zip", ".sql"]
        file_names = ["report", "backup", "config", "data", "image", "video", "archive", "database"]

        file_id_counter = 1
        for client_id in self._clients.keys():
            # Each client has 3-8 files
            num_files = random.randint(3, 8)
            client_total_size = 0

            for _ in range(num_files):
                file_id = f"file_{file_id_counter:04d}"
                file_id_counter += 1

                name = random.choice(file_names) + random.choice(file_types)
                size = random.randint(1024, 50 * 1024 * 1024)  # 1KB to 50MB
                client_total_size += size

                file_obj = MockFile(
                    id=file_id,
                    client_id=client_id,
                    name=name,
                    path=f"/backups/{self._clients[client_id].name}/{name}",
                    size=size,
                    hash=f"sha256_{uuid.uuid4().hex[:16]}",
                    created=(datetime.now() - timedelta(days=random.randint(1, 10))).isoformat(),
                    modified=(datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                    status=random.choice(["uploaded", "verified", "verified", "error"]),  # Mostly good
                    backup_count=random.randint(1, 5),
                    last_backup=(datetime.now() - timedelta(hours=random.randint(1, 24))).isoformat(),
                    owner=client_id
                )

                self._files[file_id] = file_obj
                self._client_files[client_id].append(file_id)

            # Update client file count and size
            self._clients[client_id].files_count = num_files
            self._clients[client_id].total_size = client_total_size

        # Generate sample logs
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        log_components = ["BackupService", "FileManager", "NetworkManager", "DatabaseManager", "AuthService"]
        log_messages = [
            "Backup completed successfully", "Connection established", "File verification failed",
            "Client disconnected", "Database updated", "Authentication successful",
            "Network timeout occurred", "Backup started", "File uploaded"
        ]

        for i in range(50):
            log_entry = MockLogEntry(
                id=i + 1,
                timestamp=(datetime.now() - timedelta(minutes=random.randint(0, 1440))).isoformat(),
                level=random.choice(log_levels),
                component=random.choice(log_components),
                message=random.choice(log_messages)
            )
            self._logs.append(log_entry)

        # Sort logs by timestamp (newest first)
        self._logs.sort(key=lambda x: x.timestamp, reverse=True)

        # Default settings
        self._settings = {
            "backup_retention_days": 30,
            "max_concurrent_backups": 5,
            "compression_enabled": True,
            "notification_email": "admin@example.com",
            "debug_logging": False
        }

    # ============================================================================
    # CLIENT OPERATIONS
    # ============================================================================

    def get_clients(self) -> List[Dict[str, Any]]:
        """Get all clients."""
        with self._lock:
            return [client.to_dict() for client in self._clients.values()]

    async def get_clients_async(self) -> List[Dict[str, Any]]:
        """Get all clients (async)."""
        await asyncio.sleep(0.001)  # Minimal realistic delay
        return self.get_clients()

    def get_client_details(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get details for specific client."""
        with self._lock:
            client = self._clients.get(client_id)
            return client.to_dict() if client else None

    def add_client(self, client_data: Dict[str, Any]) -> str:
        """Add new client."""
        with self._lock:
            client_id = str(uuid.uuid4())
            client = MockClient(
                id=client_id,
                name=client_data.get("name", f"Client-{len(self._clients) + 1}"),
                ip_address=client_data.get("ip_address", f"192.168.1.{100 + len(self._clients)}"),
                status="connected",
                last_seen=datetime.now().isoformat(),
                files_count=0,
                total_size=0,
                connection_time=datetime.now().isoformat(),
                version=client_data.get("version", "2.1.4"),
                platform=client_data.get("platform", "Unknown"),
                sync_enabled=client_data.get("sync_enabled", True)
            )
            self._clients[client_id] = client
            self._client_files[client_id] = []
            return client_id

    async def add_client_async(self, client_data: Dict[str, Any]) -> str:
        """Add new client (async)."""
        await asyncio.sleep(0.001)
        return self.add_client(client_data)

    def delete_client(self, client_id: str) -> bool:
        """Delete client and all associated files (cascading)."""
        with self._lock:
            if client_id not in self._clients:
                return False

            # Delete associated files
            file_ids = self._client_files.get(client_id, [])
            for file_id in file_ids:
                self._files.pop(file_id, None)

            # Delete client
            del self._clients[client_id]
            del self._client_files[client_id]
            return True

    async def delete_client_async(self, client_id: str) -> bool:
        """Delete client (async)."""
        await asyncio.sleep(0.001)
        return self.delete_client(client_id)

    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect a client."""
        with self._lock:
            if client_id in self._clients:
                self._clients[client_id].status = "disconnected"
                self._clients[client_id].last_seen = datetime.now().isoformat()
                return True
            return False

    async def disconnect_client_async(self, client_id: str) -> bool:
        """Disconnect a client (async)."""
        await asyncio.sleep(0.001)
        return self.disconnect_client(client_id)

    def resolve_client(self, client_identifier: str) -> Optional[Dict[str, Any]]:
        """Resolve client by ID or name."""
        with self._lock:
            # Try by ID first
            if client_identifier in self._clients:
                return self._clients[client_identifier].to_dict()

            # Try by name
            for client in self._clients.values():
                if client.name == client_identifier:
                    return client.to_dict()
            return None

    # ============================================================================
    # FILE OPERATIONS
    # ============================================================================

    def get_files(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get files, optionally filtered by client."""
        with self._lock:
            if client_id:
                file_ids = self._client_files.get(client_id, [])
                return [self._files[fid].to_dict() for fid in file_ids if fid in self._files]
            return [file_obj.to_dict() for file_obj in self._files.values()]

    async def get_files_async(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get files (async)."""
        await asyncio.sleep(0.001)
        return self.get_files(client_id)

    def get_client_files(self, client_id: str) -> List[Dict[str, Any]]:
        """Get files for specific client."""
        return self.get_files(client_id)

    async def get_client_files_async(self, client_id: str) -> List[Dict[str, Any]]:
        """Get files for specific client (async)."""
        return await self.get_files_async(client_id)

    def delete_file(self, file_id: str) -> bool:
        """Delete a file and update relationships."""
        with self._lock:
            if file_id not in self._files:
                return False

            file_obj = self._files[file_id]
            client_id = file_obj.client_id

            # Remove file
            del self._files[file_id]

            # Update client relationships
            if client_id in self._client_files:
                self._client_files[client_id] = [fid for fid in self._client_files[client_id] if fid != file_id]

                # Update client statistics
                if client_id in self._clients:
                    self._clients[client_id].files_count -= 1
                    self._clients[client_id].total_size -= file_obj.size

            return True

    async def delete_file_async(self, file_id: str) -> bool:
        """Delete a file (async)."""
        await asyncio.sleep(0.001)
        return self.delete_file(file_id)

    def verify_file(self, file_id: str) -> bool:
        """Verify file integrity."""
        with self._lock:
            if file_id in self._files:
                self._files[file_id].status = "verified"
                return True
            return False

    async def verify_file_async(self, file_id: str) -> bool:
        """Verify file integrity (async)."""
        await asyncio.sleep(0.001)
        return self.verify_file(file_id)

    def download_file(self, file_id: str, destination_path: str) -> bool:
        """Simulate file download."""
        with self._lock:
            if file_id in self._files:
                # In real implementation, would copy file to destination_path
                # For mock, just return success
                return True
            return False

    async def download_file_async(self, file_id: str, destination_path: str) -> bool:
        """Simulate file download (async)."""
        await asyncio.sleep(0.001)
        return self.download_file(file_id, destination_path)

    # ============================================================================
    # DATABASE OPERATIONS
    # ============================================================================

    def get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Get data from table (for database view)."""
        with self._lock:
            if table_name.lower() == "clients":
                return self.get_clients()
            elif table_name.lower() == "files":
                return self.get_files()
            elif table_name.lower() == "logs":
                return [log.to_dict() for log in self._logs]
            return []

    async def get_table_data_async(self, table_name: str) -> List[Dict[str, Any]]:
        """Get table data (async)."""
        await asyncio.sleep(0.001)
        return self.get_table_data(table_name)

    def update_row(self, table_name: str, row_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update a row in table."""
        with self._lock:
            if table_name.lower() == "clients" and row_id in self._clients:
                client = self._clients[row_id]
                for key, value in updated_data.items():
                    if hasattr(client, key):
                        setattr(client, key, value)
                return True
            elif table_name.lower() == "files" and row_id in self._files:
                file_obj = self._files[row_id]
                for key, value in updated_data.items():
                    if hasattr(file_obj, key):
                        setattr(file_obj, key, value)
                return True
            return False

    def delete_row(self, table_name: str, row_id: str) -> bool:
        """Delete a row from table."""
        with self._lock:
            if table_name.lower() == "clients":
                return self.delete_client(row_id)
            elif table_name.lower() == "files":
                return self.delete_file(row_id)
            return False

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information."""
        with self._lock:
            return {
                "tables": ["clients", "files", "logs"],
                "total_clients": len(self._clients),
                "total_files": len(self._files),
                "total_logs": len(self._logs),
                "database_size": f"{sum(f.size for f in self._files.values()) / (1024*1024):.1f} MB"
            }

    async def get_database_info_async(self) -> Dict[str, Any]:
        """Get database info (async)."""
        await asyncio.sleep(0.001)
        return self.get_database_info()

    # ============================================================================
    # LOG OPERATIONS
    # ============================================================================

    def get_logs(self) -> List[Dict[str, Any]]:
        """Get system logs."""
        with self._lock:
            return [log.to_dict() for log in self._logs]

    async def get_logs_async(self) -> List[Dict[str, Any]]:
        """Get system logs (async)."""
        await asyncio.sleep(0.001)
        return self.get_logs()

    def clear_logs(self) -> bool:
        """Clear all logs."""
        with self._lock:
            self._logs.clear()
            return True

    async def clear_logs_async(self) -> bool:
        """Clear all logs (async)."""
        await asyncio.sleep(0.001)
        return self.clear_logs()

    async def export_logs_async(self, export_format: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export logs in specified format."""
        await asyncio.sleep(0.001)
        logs = self.get_logs()

        # Apply filters if provided
        if filters:
            # Simple filtering implementation
            if "level" in filters:
                logs = [log for log in logs if log["level"] == filters["level"]]

        return {
            "format": export_format,
            "count": len(logs),
            "data": logs
        }

    async def get_log_statistics_async(self) -> Dict[str, Any]:
        """Get log statistics."""
        await asyncio.sleep(0.001)
        with self._lock:
            levels = {}
            components = {}

            for log in self._logs:
                levels[log.level] = levels.get(log.level, 0) + 1
                components[log.component] = components.get(log.component, 0) + 1

            return {
                "total_logs": len(self._logs),
                "levels": levels,
                "components": components,
                "oldest_log": self._logs[-1].timestamp if self._logs else None,
                "newest_log": self._logs[0].timestamp if self._logs else None
            }

    # ============================================================================
    # SERVER STATUS & ANALYTICS
    # ============================================================================

    def get_server_status(self) -> Dict[str, Any]:
        """Get server status."""
        with self._lock:
            connected_clients = sum(1 for c in self._clients.values() if c.status == "connected")
            return {
                "server_running": True,
                "uptime": "72:15:33",
                "clients_connected": connected_clients,
                "total_clients": len(self._clients),
                "total_files": len(self._files),
                "total_storage": sum(f.size for f in self._files.values()),
                "last_backup": datetime.now().isoformat()
            }

    async def get_server_status_async(self) -> Dict[str, Any]:
        """Get server status (async)."""
        await asyncio.sleep(0.001)
        return self.get_server_status()

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            **self.get_server_status(),
            "cpu_usage": random.uniform(10, 80),
            "memory_usage": random.uniform(40, 85),
            "disk_usage": random.uniform(20, 70),
            "network_sent_mb": random.randint(100, 1000),
            "network_recv_mb": random.randint(200, 1500)
        }

    async def get_system_status_async(self) -> Dict[str, Any]:
        """Get system status (async)."""
        await asyncio.sleep(0.001)
        return self.get_system_status()

    def get_analytics_data(self) -> Dict[str, Any]:
        """Get analytics data."""
        return self.get_system_status()

    async def get_analytics_data_async(self) -> Dict[str, Any]:
        """Get analytics data (async)."""
        return await self.get_system_status_async()

    def test_connection(self) -> bool:
        """Test connection (always succeeds for mock)."""
        return True

    async def test_connection_async(self) -> bool:
        """Test connection (async)."""
        await asyncio.sleep(0.001)
        return True

    # Additional missing methods for compatibility
    def get_detailed_server_status(self) -> Dict[str, Any]:
        """Get detailed server status."""
        return {**self.get_server_status(), "detailed": True, "subsystems": ["backup", "network", "storage"]}

    async def get_detailed_server_status_async(self) -> Dict[str, Any]:
        """Get detailed server status (async)."""
        await asyncio.sleep(0.001)
        return self.get_detailed_server_status()

    def get_server_health(self) -> Dict[str, Any]:
        """Get server health."""
        return {"status": "healthy", "uptime": "72:15:33", "checks_passed": 8, "checks_failed": 0}

    async def get_server_health_async(self) -> Dict[str, Any]:
        """Get server health (async)."""
        await asyncio.sleep(0.001)
        return self.get_server_health()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.get_system_status()

    async def get_performance_metrics_async(self) -> Dict[str, Any]:
        """Get performance metrics (async)."""
        return await self.get_system_status_async()

    def get_historical_data(self, metric: str, hours: int = 24) -> Dict[str, Any]:
        """Get historical data."""
        return {"metric": metric, "hours": hours, "data": [random.uniform(10, 90) for _ in range(hours)]}

    async def get_historical_data_async(self, metric: str, hours: int = 24) -> Dict[str, Any]:
        """Get historical data (async)."""
        await asyncio.sleep(0.001)
        return self.get_historical_data(metric, hours)

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary."""
        return self.get_server_status()

    async def get_dashboard_summary_async(self) -> Dict[str, Any]:
        """Get dashboard summary (async)."""
        return await self.get_server_status_async()

    def get_server_statistics(self) -> Dict[str, Any]:
        """Get detailed server statistics."""
        return self.get_system_status()

    async def get_server_statistics_async(self) -> Dict[str, Any]:
        """Get server statistics (async)."""
        return await self.get_system_status_async()

    async def get_recent_activity_async(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent activity."""
        await asyncio.sleep(0.001)
        activities = []
        for i in range(min(limit, 20)):
            activities.append({
                "id": i,
                "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                "type": random.choice(["backup", "restore", "connect", "disconnect"]),
                "description": f"Activity {i}"
            })
        return activities

    async def start_server_async(self) -> bool:
        """Start server (mock always succeeds)."""
        await asyncio.sleep(0.001)
        return True

    async def stop_server_async(self) -> bool:
        """Stop server (mock always succeeds)."""
        await asyncio.sleep(0.001)
        return True

    async def validate_settings_async(self, settings_data: Dict[str, Any]) -> bool:
        """Validate settings (mock always validates)."""
        await asyncio.sleep(0.001)
        return True

    async def backup_settings_async(self, backup_name: str, settings_data: Dict[str, Any]) -> bool:
        """Backup settings (mock always succeeds)."""
        await asyncio.sleep(0.001)
        return True

    async def restore_settings_async(self, backup_file: str) -> Dict[str, Any]:
        """Restore settings (mock returns default settings)."""
        await asyncio.sleep(0.001)
        return self.load_settings()

    async def get_default_settings_async(self) -> Dict[str, Any]:
        """Get default settings."""
        await asyncio.sleep(0.001)
        return {
            "backup_retention_days": 30,
            "max_concurrent_backups": 5,
            "compression_enabled": True,
            "notification_email": "admin@example.com",
            "debug_logging": False
        }

    # Stream operations (mock implementations)
    async def stream_logs_async(self, callback) -> bool:
        """Stream logs (mock implementation)."""
        await asyncio.sleep(0.001)
        return True

    async def stop_log_stream_async(self, streaming_task) -> bool:
        """Stop log stream (mock implementation)."""
        await asyncio.sleep(0.001)
        return True

    # ============================================================================
    # SETTINGS OPERATIONS
    # ============================================================================

    def save_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Save settings."""
        with self._lock:
            self._settings.update(settings_data)
            return True

    async def save_settings_async(self, settings_data: Dict[str, Any]) -> bool:
        """Save settings (async)."""
        await asyncio.sleep(0.001)
        return self.save_settings(settings_data)

    def load_settings(self) -> Dict[str, Any]:
        """Load current settings."""
        with self._lock:
            return self._settings.copy()

    async def load_settings_async(self) -> Dict[str, Any]:
        """Load settings (async)."""
        await asyncio.sleep(0.001)
        return self.load_settings()


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_mock_database_instance = None
_mock_database_lock = threading.Lock()

def get_mock_database() -> MockDatabase:
    """Get or create singleton MockDatabase instance."""
    global _mock_database_instance

    if _mock_database_instance is None:
        with _mock_database_lock:
            if _mock_database_instance is None:
                _mock_database_instance = MockDatabase()

    return _mock_database_instance