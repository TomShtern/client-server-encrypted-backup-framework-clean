#!/usr/bin/env python3
"""
MockDatabase - Thread-Safe In-Memory Database Simulation for FletV2

Provides realistic database behavior for development/testing with:
- Entity relationships with referential integrity
- Thread-safe CRUD operations
- Realistic data generation
- No disk I/O (pure in-memory)
- Support for sync and async operations

Design Philosophy:
- Simulate real database behavior without the overhead
- Maintain consistency and referential integrity
- Fast, thread-safe operations for responsive UI
- Clean data formats matching server expectations
"""

import asyncio
import threading
import time
import random
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class MockEntity:
    """Base class for mock database entities"""
    id: str
    created_at: datetime
    updated_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


@dataclass
class MockClient(MockEntity):
    """Mock client entity matching server expectations"""
    name: str
    ip_address: str
    status: str
    last_seen: datetime
    version: str = "1.0.0"
    platform: str = "Windows"


@dataclass
class MockFile(MockEntity):
    """Mock file entity with client relationship"""
    client_id: str
    name: str
    path: str
    size: int
    hash: str
    status: str = "uploaded"
    verified: bool = False


@dataclass
class MockLogEntry(MockEntity):
    """Mock log entry for system logging"""
    level: str
    component: str
    message: str
    timestamp: datetime


class MockDatabase:
    """
    Thread-safe in-memory database simulation

    Provides realistic database behavior with:
    - CRUD operations maintaining referential integrity
    - Thread-safe concurrent access
    - Realistic data generation
    - Server-compatible return formats
    """

    def __init__(self, seed_data: bool = True):
        """Initialize mock database with optional seed data"""
        self._lock = threading.RLock()

        # Entity storage
        self._clients: Dict[str, MockClient] = {}
        self._files: Dict[str, MockFile] = {}
        self._logs: List[MockLogEntry] = []

        # Relationship indexes for performance
        self._client_files: Dict[str, Set[str]] = {}  # client_id -> {file_ids}

        # Settings and configuration
        self._settings: Dict[str, Any] = {}
        self._server_metrics: Dict[str, Any] = {}

        if seed_data:
            self._generate_seed_data()

        logger.info(f"MockDatabase initialized with {len(self._clients)} clients, {len(self._files)} files")

    def _generate_seed_data(self):
        """Generate realistic seed data for development"""
        with self._lock:
            # Generate 20-30 clients
            num_clients = random.randint(20, 30)

            for i in range(num_clients):
                client_id = str(uuid.uuid4())
                now = datetime.now()

                client = MockClient(
                    id=client_id,
                    created_at=now - timedelta(days=random.randint(1, 90)),
                    updated_at=now,
                    name=f"Client-{random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'])}-{i+1:02d}",
                    ip_address=f"192.168.{random.randint(1, 10)}.{random.randint(10, 250)}",
                    status=random.choice(["connected", "disconnected", "offline"]),
                    last_seen=now - timedelta(hours=random.randint(0, 48)),
                    version=random.choice(["1.0.0", "1.1.0", "1.2.0"]),
                    platform=random.choice(["Windows", "Linux", "MacOS"])
                )

                self._clients[client_id] = client
                self._client_files[client_id] = set()

                # Generate 0-3 files per client
                num_files = random.choices([0, 1, 2, 3], weights=[20, 50, 20, 10])[0]

                for j in range(num_files):
                    file_id = str(uuid.uuid4())
                    file_ext = random.choice([".pdf", ".docx", ".jpg", ".png", ".txt", ".zip"])

                    file_obj = MockFile(
                        id=file_id,
                        created_at=now - timedelta(days=random.randint(0, 30)),
                        updated_at=now,
                        client_id=client_id,
                        name=f"file_{j+1}{file_ext}",
                        path=f"/home/user/{random.choice(['documents', 'downloads'])}/file_{j+1}{file_ext}",
                        size=random.randint(1024, 10_000_000),
                        hash=f"sha256:{random.randbytes(32).hex()}",
                        status=random.choice(["uploaded", "verified", "error"]),
                        verified=random.choice([True, False])
                    )

                    self._files[file_id] = file_obj
                    self._client_files[client_id].add(file_id)

            # Generate some log entries
            self._generate_log_entries()

            # Initialize default settings
            self._settings = {
                "server_port": 8080,
                "max_clients": 100,
                "backup_enabled": True,
                "log_level": "INFO",
                "retention_days": 30
            }

    def _generate_log_entries(self, count: int = 50):
        """Generate realistic log entries"""
        levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        components = ["Server", "Client", "Database", "FileTransfer", "Auth"]

        messages = {
            "INFO": ["Client connected", "File transfer completed", "Database backup success"],
            "WARNING": ["High memory usage", "Client connection unstable", "File verification failed"],
            "ERROR": ["Client authentication failed", "Database connection lost", "File transfer error"],
            "DEBUG": ["Processing request", "Cache hit", "Memory usage check"]
        }

        base_time = datetime.now()

        for i in range(count):
            level = random.choices(levels, weights=[50, 25, 15, 10])[0]
            component = random.choice(components)
            message = random.choice(messages[level])

            log_entry = MockLogEntry(
                id=str(uuid.uuid4()),
                created_at=base_time - timedelta(hours=random.randint(0, 72)),
                updated_at=base_time,
                level=level,
                component=component,
                message=message,
                timestamp=base_time - timedelta(minutes=random.randint(0, 4320))  # Last 3 days
            )

            self._logs.append(log_entry)

    # Client Operations
    def get_clients(self) -> List[Dict[str, Any]]:
        """Get all clients with computed statistics"""
        with self._lock:
            clients = []
            for client in self._clients.values():
                client_dict = client.to_dict()

                # Add computed fields expected by views
                client_files = self._client_files.get(client.id, set())
                client_dict.update({
                    "client_id": client.id,  # Legacy compatibility
                    "address": f"{client.ip_address}:54321",
                    "files_count": len(client_files),
                    "total_size": sum(self._files[fid].size for fid in client_files if fid in self._files),
                    "connected_at": client.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "last_activity": client.last_seen.strftime("%Y-%m-%d %H:%M:%S")
                })

                clients.append(client_dict)
            return clients

    def add_client(self, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add new client with validation"""
        with self._lock:
            try:
                client_id = str(uuid.uuid4())
                now = datetime.now()

                client = MockClient(
                    id=client_id,
                    created_at=now,
                    updated_at=now,
                    name=client_data.get("name", f"Client-{client_id[:8]}"),
                    ip_address=client_data.get("ip_address", f"192.168.1.{random.randint(100, 200)}"),
                    status=client_data.get("status", "connected"),
                    last_seen=now,
                    version=client_data.get("version", "1.0.0"),
                    platform=client_data.get("platform", "Windows")
                )

                self._clients[client_id] = client
                self._client_files[client_id] = set()

                return client.to_dict()

            except Exception as e:
                logger.error(f"Failed to add client: {e}")
                return None

    def delete_client(self, client_id: str) -> bool:
        """Delete client with cascading file deletion"""
        with self._lock:
            if client_id not in self._clients:
                return False

            # Cascading delete: remove all client files
            client_files = self._client_files.get(client_id, set()).copy()
            for file_id in client_files:
                if file_id in self._files:
                    del self._files[file_id]

            # Remove client
            del self._clients[client_id]
            del self._client_files[client_id]

            logger.info(f"Deleted client {client_id} and {len(client_files)} files")
            return True

    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect client (change status)"""
        with self._lock:
            if client_id not in self._clients:
                return False

            client = self._clients[client_id]
            client.status = "disconnected"
            client.last_seen = datetime.now()
            client.updated_at = datetime.now()
            return True

    # File Operations
    def get_files(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get files, optionally filtered by client"""
        with self._lock:
            files = []
            for file_obj in self._files.values():
                if client_id is None or file_obj.client_id == client_id:
                    file_dict = file_obj.to_dict()

                    # Add legacy compatibility fields
                    client = self._clients.get(file_obj.client_id)
                    file_dict.update({
                        "file_id": file_obj.id,
                        "filename": file_obj.name,
                        "pathname": file_obj.path,
                        "client_name": client.name if client else "Unknown",
                        "uploaded_at": file_obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "modification_date": file_obj.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                    })

                    files.append(file_dict)
            return files

    def delete_file(self, file_id: str) -> bool:
        """Delete file and update client relationships"""
        with self._lock:
            if file_id not in self._files:
                return False

            file_obj = self._files[file_id]

            # Remove from client index
            if file_obj.client_id in self._client_files:
                self._client_files[file_obj.client_id].discard(file_id)

            del self._files[file_id]
            return True

    def verify_file(self, file_id: str) -> Dict[str, Any]:
        """Verify file integrity"""
        with self._lock:
            if file_id not in self._files:
                return {"success": False, "message": "File not found"}

            file_obj = self._files[file_id]

            # 95% success rate for verification
            if random.random() < 0.95:
                file_obj.status = "verified"
                file_obj.verified = True
                file_obj.updated_at = datetime.now()
                return {"success": True, "message": "File verified"}
            else:
                file_obj.status = "error"
                file_obj.verified = False
                return {"success": False, "message": "Verification failed"}

    # Database Operations
    def get_table_data(self, table_name: str) -> Dict[str, Any]:
        """Get table data for database view"""
        with self._lock:
            if table_name == "clients":
                return {
                    "columns": ["id", "name", "ip_address", "status", "last_seen", "files_count"],
                    "rows": [
                        {
                            "id": c.id,
                            "name": c.name,
                            "ip_address": c.ip_address,
                            "status": c.status,
                            "last_seen": c.last_seen.strftime("%Y-%m-%d %H:%M:%S"),
                            "files_count": len(self._client_files.get(c.id, set()))
                        }
                        for c in self._clients.values()
                    ]
                }
            elif table_name == "files":
                return {
                    "columns": ["id", "name", "client_id", "size", "status", "verified"],
                    "rows": [
                        {
                            "id": f.id,
                            "name": f.name,
                            "client_id": f.client_id,
                            "size": f.size,
                            "status": f.status,
                            "verified": f.verified
                        }
                        for f in self._files.values()
                    ]
                }
            else:
                return {"columns": [], "rows": []}

    def update_row(self, table_name: str, row_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update table row with validation"""
        with self._lock:
            try:
                if table_name == "clients" and row_id in self._clients:
                    client = self._clients[row_id]
                    for key, value in updated_data.items():
                        if hasattr(client, key):
                            setattr(client, key, value)
                    client.updated_at = datetime.now()
                    return True
                elif table_name == "files" and row_id in self._files:
                    file_obj = self._files[row_id]
                    for key, value in updated_data.items():
                        if hasattr(file_obj, key):
                            setattr(file_obj, key, value)
                    file_obj.updated_at = datetime.now()
                    return True
                return False
            except Exception as e:
                logger.error(f"Update row error: {e}")
                return False

    def delete_row(self, table_name: str, row_id: str) -> bool:
        """Delete table row with cascading"""
        if table_name == "clients":
            return self.delete_client(row_id)
        elif table_name == "files":
            return self.delete_file(row_id)
        return False

    # Log Operations
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get log entries sorted by timestamp"""
        with self._lock:
            return [
                {
                    "id": log.id,
                    "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "level": log.level,
                    "component": log.component,
                    "message": log.message
                }
                for log in sorted(self._logs, key=lambda x: x.timestamp, reverse=True)
            ]

    def clear_logs(self) -> bool:
        """Clear all log entries"""
        with self._lock:
            self._logs.clear()
            return True

    # Analytics and Status
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status metrics"""
        with self._lock:
            connected_clients = len([c for c in self._clients.values() if c.status == "connected"])
            total_files = len(self._files)
            total_size = sum(f.size for f in self._files.values())

            return {
                "server_running": True,
                "port": 8080,
                "clients": len(self._clients),
                "active_clients": connected_clients,
                "files": total_files,
                "total_files": total_files,
                "storage_used_gb": total_size / (1024**3),
                "cpu_usage": random.uniform(15, 45),
                "memory_usage": random.uniform(30, 70),
                "uptime": "24h 15m"
            }

    # Settings Operations
    def save_settings(self, settings_data: Dict[str, Any]) -> bool:
        """Save settings to mock storage"""
        with self._lock:
            try:
                self._settings.update(settings_data)
                return True
            except Exception as e:
                logger.error(f"Save settings error: {e}")
                return False

    def load_settings(self) -> Dict[str, Any]:
        """Load settings from mock storage"""
        with self._lock:
            return self._settings.copy()

    # Async wrappers for compatibility
    async def get_clients_async(self) -> List[Dict[str, Any]]:
        """Async wrapper for get_clients"""
        await asyncio.sleep(0.001)  # Minimal delay
        return self.get_clients()

    async def add_client_async(self, client_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Async wrapper for add_client"""
        await asyncio.sleep(0.001)
        return self.add_client(client_data)

    async def delete_client_async(self, client_id: str) -> bool:
        """Async wrapper for delete_client"""
        await asyncio.sleep(0.001)
        return self.delete_client(client_id)

    async def get_files_async(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Async wrapper for get_files"""
        await asyncio.sleep(0.001)
        return self.get_files(client_id)

    async def delete_file_async(self, file_id: str) -> bool:
        """Async wrapper for delete_file"""
        await asyncio.sleep(0.001)
        return self.delete_file(file_id)

    async def get_logs_async(self) -> List[Dict[str, Any]]:
        """Async wrapper for get_logs"""
        await asyncio.sleep(0.001)
        return self.get_logs()

    async def clear_logs_async(self) -> bool:
        """Async wrapper for clear_logs"""
        await asyncio.sleep(0.001)
        return self.clear_logs()

    # Utility methods
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self._lock:
            return {
                "clients_count": len(self._clients),
                "files_count": len(self._files),
                "logs_count": len(self._logs),
                "total_storage_mb": sum(f.size for f in self._files.values()) / (1024**2),
                "connected_clients": len([c for c in self._clients.values() if c.status == "connected"])
            }

    def cleanup(self):
        """Cleanup resources (no-op for in-memory)"""
        pass


# Singleton instance for backward compatibility
_mock_database_instance = None
_instance_lock = threading.Lock()


def get_mock_database(seed_data: bool = True) -> MockDatabase:
    """Get singleton mock database instance"""
    global _mock_database_instance
    with _instance_lock:
        if _mock_database_instance is None:
            _mock_database_instance = MockDatabase(seed_data=seed_data)
        return _mock_database_instance


def reset_mock_database():
    """Reset singleton instance (useful for testing)"""
    global _mock_database_instance
    with _instance_lock:
        if _mock_database_instance:
            _mock_database_instance.cleanup()
        _mock_database_instance = None