#!/usr/bin/env python3
"""
Enhanced Mock Data Generator for FletV2 Development
Provides persistent, thread-safe, realistic test data for GUI development and testing.

Features:
- Thread-safe operations with referential integrity
- Optional disk persistence for consistent testing
- Realistic data generation with time-based changes
- Database-like operations with cascading deletes
- Change listeners for reactive UI updates
- Comprehensive mock data for all system components

TODO: DELETE THIS ENTIRE FILE when connecting to production server/database
This file is ONLY for development purposes and should not exist in production.
"""

import random
import time
import json
import threading
import logging
import asyncio
import math
import psutil
import functools
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid

# Set up logger for this module
logger = logging.getLogger(__name__)


def async_mock_data(delay: float = 0.01):
    """Decorator to convert sync mock data methods to async with simulated delay."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            await asyncio.sleep(delay)  # Simulate async operation
            return func(*args, **kwargs)
        return async_wrapper
    return decorator


@dataclass
class MockClient:
    """Client data structure matching real server schema"""
    id: str
    name: str
    ip_address: str
    status: str  # connected, disconnected, error
    last_seen: datetime
    files_count: int
    total_size: int
    connection_time: Optional[datetime] = None
    version: str = "1.0.0"
    platform: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper timestamp handling"""
        data = asdict(self)
        # Convert datetime objects to ISO strings for JSON compatibility
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


@dataclass
class MockFile:
    """File data structure matching real server schema"""
    id: str
    client_id: str
    name: str
    path: str
    size: int
    hash: str
    created: datetime
    modified: datetime
    status: str  # uploaded, verified, error
    backup_count: int = 1
    last_backup: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with proper timestamp handling"""
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


class MockDataGenerator:
    """
    Generate realistic mock data for development

    Features:
    - 30-60 client profiles with realistic data
    - Dynamic file metadata
    - Simulated server activity
    - Consistent data relationships
    - Time-based data changes for testing real-time updates
    """

    def __init__(self, num_clients: int = 45, persist_to_disk: bool = False):
        """Initialize enhanced mock data generator with persistence features"""
        self.num_clients = num_clients
        self.start_time = time.time()
        self.persist_to_disk = persist_to_disk
        self.data_file = Path("mock_data_store.json") if persist_to_disk else None

        # Thread-safe data store
        self._lock = threading.RLock()

        # Enhanced data structures using dataclasses
        self._clients: Dict[str, MockClient] = {}
        self._files: Dict[str, MockFile] = {}
        self._activity_log: List[Dict[str, Any]] = []
        self._server_status = {
            "running": True,
            "port": 8080,
            "start_time": datetime.now(),
            "connections": 0,
            "total_transfers": 0
        }

        # Referential integrity tracking
        self._client_file_index: Dict[str, Set[str]] = {}  # client_id -> {file_ids}

        # Change tracking for notifications
        self._change_listeners: List[Callable] = []

        # Legacy compatibility fields
        self.last_update = time.time()
        self.change_counter = 0

        # Initialize with realistic data
        self._generate_base_data()

        # Load persisted data if available
        if persist_to_disk and self.data_file and self.data_file.exists():
            self._load_from_disk()

        logger.debug(f"Enhanced mock data generator initialized with {len(self._clients)} clients and {len(self._files)} files")

    def _generate_base_data(self):
        """Generate base mock data that remains consistent"""

        # Client name templates for realistic variety
        client_prefixes = [
            "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
            "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi",
            "Rho", "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega",
            "Enterprise", "Production", "Development", "Testing", "Staging"
        ]

        client_suffixes = [
            "Workstation", "Server", "Laptop", "Desktop", "Node", "Instance",
            "Machine", "Host", "System", "Device", "Terminal", "Client"
        ]

        # File type distributions for realism
        file_types = {
            ".pdf": 25,
            ".docx": 20,
            ".xlsx": 15,
            ".jpg": 12,
            ".png": 10,
            ".txt": 8,
            ".mp4": 5,
            ".zip": 3,
            ".py": 2
        }

        with self._lock:
            # Generate clients using enhanced data structures
            self._clients.clear()
            self._client_file_index.clear()
        for i in range(self.num_clients):
            client_id = f"client_{i+1:03d}"

            # Generate realistic client data
            prefix = random.choice(client_prefixes)
            suffix = random.choice(client_suffixes)
            client_name = f"{prefix} {suffix}"

            # Generate IP in realistic ranges
            ip = f"192.168.{random.randint(1, 10)}.{random.randint(10, 250)}"
            port = random.randint(54321, 54400)

            # Generate connection times
            base_time = datetime.now() - timedelta(days=random.randint(0, 30))
            last_activity = base_time + timedelta(
                hours=random.randint(0, 24),
                minutes=random.randint(0, 59)
            )

            # Realistic status distribution
            status_weights = [
                ("Connected", 40),
                ("Registered", 35),
                ("Offline", 20),
                ("Error", 5)
            ]
            status = random.choices(
                [s[0] for s in status_weights],
                weights=[s[1] for s in status_weights]
            )[0]

            client = MockClient(
                id=client_id,
                name=client_name,
                ip_address=ip,
                status=status.lower(),
                last_seen=last_activity,
                files_count=0,  # Will be calculated
                total_size=0,   # Will be calculated
                connection_time=base_time,
                version=random.choice(["1.0.0", "1.1.0", "1.2.0"]),
                platform=random.choice(["Windows", "Linux", "MacOS"])
            )
            self._clients[client.id] = client
            self._client_file_index[client.id] = set()

            # Generate files for clients
            self._files.clear()
            for client in self._clients.values():
                # Each client has 0-3 files (most have 1)
                num_files = random.choices([0, 1, 2, 3], weights=[10, 70, 15, 5])[0]

                for j in range(num_files):
                    # Generate realistic filename
                    base_names = [
                        "document", "report", "image", "photo", "data", "backup",
                        "config", "log", "archive", "export", "import", "script"
                    ]
                    base_name = random.choice(base_names)
                    file_extension = random.choices(
                        list(file_types.keys()),
                        weights=list(file_types.values())
                    )[0]
                    filename = f"{base_name}_{j+1}{file_extension}"

                    # Generate consistent file_id that matches files view format
                    file_id = f"file_{hash(filename) % 10000}"

                    # Generate realistic file sizes
                    if file_extension in [".jpg", ".png"]:
                        file_size = random.randint(500_000, 5_000_000)  # 500KB - 5MB
                    elif file_extension in [".pdf", ".docx"]:
                        file_size = random.randint(100_000, 2_000_000)  # 100KB - 2MB
                    elif file_extension in [".mp4"]:
                        file_size = random.randint(10_000_000, 100_000_000)  # 10MB - 100MB
                    elif file_extension in [".zip"]:
                        file_size = random.randint(1_000_000, 50_000_000)  # 1MB - 50MB
                    else:
                        file_size = random.randint(1000, 500_000)  # 1KB - 500KB

                    # Generate upload time
                    upload_time = datetime.now() - timedelta(
                        days=random.randint(0, 7),
                        hours=random.randint(0, 23)
                    )

                    # Generate consistent file hash
                    file_hash = f"sha256:{hash(filename + str(file_size)) % 999999999:08x}"

                    file_path = f"/home/user/{random.choice(['documents', 'downloads', 'desktop'])}/{filename}"

                    file_obj = MockFile(
                        id=file_id,
                        client_id=client.id,
                        name=filename,
                        path=file_path,
                        size=file_size,
                        hash=file_hash,
                        created=upload_time,
                        modified=upload_time,
                        status=random.choice(["uploaded", "verified", "error"]),
                        backup_count=random.randint(1, 3),
                        last_backup=upload_time if random.choice([True, False]) else None
                    )

                    # Only add file if client exists (referential integrity)
                    if file_obj.client_id in self._clients:
                        self._files[file_obj.id] = file_obj
                        self._client_file_index[file_obj.client_id].add(file_obj.id)

                        # Update client totals
                        client.files_count += 1
                        client.total_size += file_size

    def get_clients(self) -> List[Dict[str, Any]]:
        """Get client data with dynamic updates and current statistics"""
        with self._lock:
            self._apply_dynamic_changes()
            clients = []
            for client in self._clients.values():
                client_dict = client.to_dict()
                # Update real-time statistics
                client_files = self._client_file_index.get(client.id, set())
                client_dict["files_count"] = len(client_files)
                client_dict["total_size"] = sum(self._files[fid].size for fid in client_files if fid in self._files)

                # Legacy compatibility fields
                client_dict["client_id"] = client.id
                client_dict["address"] = f"{client.ip_address}:54321"
                client_dict["connected_at"] = client.connection_time.strftime("%Y-%m-%d %H:%M:%S") if client.connection_time else "N/A"
                client_dict["last_activity"] = client.last_seen.strftime("%Y-%m-%d %H:%M:%S")
                client_dict["has_public_key"] = random.choice([True, False])
                client_dict["has_aes_key"] = random.choice([True, False])

                clients.append(client_dict)
            return clients

    def get_files(self, client_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get file data with dynamic updates, optionally filtered by client"""
        with self._lock:
            self._apply_dynamic_changes()
            files = []
            for file_obj in self._files.values():
                if client_id is None or file_obj.client_id == client_id:
                    file_dict = file_obj.to_dict()

                    # Legacy compatibility fields
                    file_dict["file_id"] = file_obj.id
                    file_dict["filename"] = file_obj.name
                    file_dict["pathname"] = file_obj.path
                    file_dict["type"] = file_obj.name.split('.')[-1] if '.' in file_obj.name else 'unknown'
                    file_dict["uploaded_at"] = file_obj.created.strftime("%Y-%m-%d %H:%M:%S")
                    file_dict["modification_date"] = file_obj.modified.strftime("%Y-%m-%d %H:%M:%S")
                    file_dict["owner"] = self._clients.get(file_obj.client_id, MockClient("", "", "", "", datetime.now(), 0, 0)).name.split()[0].lower()
                    file_dict["client_name"] = self._clients.get(file_obj.client_id, MockClient("", "", "", "", datetime.now(), 0, 0)).name
                    file_dict["verified"] = file_obj.status == "verified"
                    file_dict["crc"] = int(file_obj.hash.split(':')[-1], 16) if ':' in file_obj.hash else random.randint(100000000, 999999999)

                    files.append(file_dict)
            return files

    def get_server_status(self) -> Dict[str, Any]:
        """Get dynamic server status with real-time data"""
        with self._lock:
            connected_clients = len([c for c in self._clients.values() if c.status == "connected"])
            uptime_seconds = int((datetime.now() - self._server_status["start_time"]).total_seconds())
            uptime_minutes = uptime_seconds // 60
            uptime_hours = uptime_minutes // 60

            if uptime_hours > 0:
                uptime = f"{uptime_hours}h {uptime_minutes % 60}m"
            else:
                uptime = f"{uptime_minutes}m"

            total_size = sum(f.size for f in self._files.values())
            storage_gb = total_size / (1024 * 1024 * 1024)

            return {
                "server_running": self._server_status["running"],
                "port": self._server_status["port"],
                "uptime": uptime,
                "uptime_seconds": uptime_seconds,
                "total_transfers": self._server_status["total_transfers"],
                "active_clients": connected_clients,
                "clients_connected": connected_clients,
                "total_files": len(self._files),
                "storage_used": f"{storage_gb:.2f} GB",
                "storage_used_gb": storage_gb,
                "cpu_usage": random.uniform(10, 40),
                "memory_usage": random.uniform(30, 60),
                "disk_usage": random.uniform(60, 80)
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get dynamic system metrics"""
        # Simulate realistic system metrics with some variation
        base_cpu = 25 + 10 * (0.5 - random.random())  # 20-30% base
        base_memory = 45 + 10 * (0.5 - random.random())  # 40-50% base
        base_disk = 75 + 5 * (0.5 - random.random())  # 72-78% base

        return {
            'cpu_usage': max(5, min(95, base_cpu + random.uniform(-5, 15))),
            'memory_usage': max(10, min(90, base_memory + random.uniform(-5, 10))),
            'disk_usage': max(50, min(95, base_disk + random.uniform(-2, 5))),
            'cpu_cores': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'memory_used_gb': psutil.virtual_memory().used / (1024**3),
            'disk_total_gb': psutil.disk_usage('/').total / (1024**3),
            'disk_used_gb': psutil.disk_usage('/').used / (1024**3),
            'network_sent_mb': psutil.net_io_counters().bytes_sent / (1024**2),
            'network_recv_mb': psutil.net_io_counters().bytes_recv / (1024**2),
            'active_connections': len(psutil.net_connections()) if hasattr(psutil, 'net_connections') else 0
        }

    def get_analytics_data(self) -> Dict[str, Any]:
        """Get analytics data for performance dashboards."""
        system_status = self.get_system_status()
        server_status = self.get_server_status()

        return {
            'system_metrics': system_status,
            'server_metrics': server_status,
            'performance_trends': {
                'cpu_trend': [random.uniform(20, 40) for _ in range(24)],  # Last 24 hours
                'memory_trend': [random.uniform(40, 60) for _ in range(24)],
                'disk_trend': [random.uniform(70, 80) for _ in range(24)],
                'network_trend': [random.uniform(1000, 5000) for _ in range(24)]
            },
            'peak_usage': {
                'cpu_peak': random.uniform(80, 95),
                'memory_peak': random.uniform(75, 85),
                'disk_peak': random.uniform(85, 95)
            }
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics for analytics."""
        system_status = self.get_system_status()

        return {
            'cpu_metrics': {
                'usage_percent': system_status['cpu_usage'],
                'load_average': [random.uniform(0.5, 2.0) for _ in range(3)],  # 1, 5, 15 min
                'process_count': random.randint(50, 200),
                'thread_count': random.randint(200, 800)
            },
            'memory_metrics': {
                'usage_percent': system_status['memory_usage'],
                'available_mb': (system_status['memory_total_gb'] - system_status['memory_used_gb']) * 1024,
                'cached_mb': random.uniform(1000, 3000),
                'swap_used_percent': random.uniform(0, 10)
            },
            'disk_metrics': {
                'usage_percent': system_status['disk_usage'],
                'read_ops_per_sec': random.randint(100, 1000),
                'write_ops_per_sec': random.randint(50, 500),
                'io_wait_time': random.uniform(0.1, 1.0)
            },
            'network_metrics': {
                'sent_kbps': system_status['network_sent_mb'] * 8 / 60,  # Convert to kbps
                'recv_kbps': system_status['network_recv_mb'] * 8 / 60,
                'packet_loss': random.uniform(0, 0.1),
                'latency_ms': random.uniform(1, 50)
            }
        }

    def get_historical_data(self, metric: str, hours: int = 24) -> List[Dict[str, Any]]:
        """Get historical data for a specific metric."""
        now = datetime.now()
        data = []

        for i in range(hours):
            timestamp = now - timedelta(hours=i)
            value = 0

            # Generate realistic values based on metric type
            if metric == 'cpu_usage':
                value = random.uniform(20, 40) + 10 * math.sin(i * math.pi / 12)  # Daily pattern
            elif metric == 'memory_usage':
                value = random.uniform(40, 60) + 5 * math.cos(i * math.pi / 6)  # 12-hour pattern
            elif metric == 'disk_usage':
                value = random.uniform(70, 80) + random.uniform(-2, 2)
            elif metric == 'network_sent_mb':
                value = random.uniform(1000, 5000) + 2000 * math.sin(i * math.pi / 6)  # Peak during business hours
            elif metric == 'network_recv_mb':
                value = random.uniform(2000, 8000) + 3000 * math.cos(i * math.pi / 8)
            else:
                value = random.uniform(0, 100)

            data.append({
                'timestamp': timestamp.isoformat(),
                'value': max(0, value)  # Ensure non-negative values
            })

        return list(reversed(data))  # Return in chronological order

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get dashboard summary data including clients, files, transfers, and storage."""
        server_status = self.get_server_status()
        clients = self.get_clients()

        # Calculate summary statistics
        total_clients = len(clients)
        connected_clients = len([c for c in clients if c['status'] == 'connected'])
        total_files = server_status['total_files']
        total_transfers = server_status['total_transfers']
        storage_used = server_status['storage_used_gb']

        return {
            'clients': {
                'total': total_clients,
                'connected': connected_clients,
                'disconnected': total_clients - connected_clients
            },
            'files': {
                'total': total_files,
                'verified': int(total_files * 0.95),  # Assume 95% verified
                'pending': int(total_files * 0.05)   # Assume 5% pending
            },
            'transfers': {
                'completed': total_transfers,
                'failed': random.randint(0, max(1, total_transfers // 20)),  # 5% failure rate
                'in_progress': random.randint(0, 5)
            },
            'storage': {
                'used_gb': storage_used,
                'total_gb': storage_used * random.uniform(1.5, 3.0),  # Assume 33-66% utilization
                'free_gb': lambda: storage_used * random.uniform(0.5, 2.0)  # Free space
            }
        }

    def get_server_statistics(self) -> Dict[str, Any]:
        """Get detailed server statistics for dashboard display."""
        server_status = self.get_server_status()

        return {
            'uptime_days': server_status['uptime_seconds'] / (24 * 3600),
            'requests_per_second': random.uniform(10, 100),
            'average_response_time_ms': random.uniform(50, 500),
            'error_rate': random.uniform(0, 0.05),  # 0-5% error rate
            'throughput_mb_per_sec': random.uniform(1, 50),
            'active_connections': server_status['active_clients'],
            'total_connections': server_status['active_clients'] + random.randint(10, 50),
            'peak_concurrent_connections': server_status['active_clients'] + random.randint(5, 20)
        }

    def get_server_health(self) -> Dict[str, Any]:
        """Get server health metrics and status."""
        system_status = self.get_system_status()
        server_status = self.get_server_status()

        # Determine overall health status
        cpu_health = 'healthy' if system_status['cpu_usage'] < 70 else 'warning' if system_status['cpu_usage'] < 85 else 'critical'
        memory_health = 'healthy' if system_status['memory_usage'] < 75 else 'warning' if system_status['memory_usage'] < 90 else 'critical'
        disk_health = 'healthy' if system_status['disk_usage'] < 80 else 'warning' if system_status['disk_usage'] < 90 else 'critical'

        # Overall health is the worst of individual metrics
        health_levels = {'healthy': 0, 'warning': 1, 'critical': 2}
        overall_health = max([cpu_health, memory_health, disk_health], key=lambda x: health_levels[x])

        return {
            'overall_status': overall_health,
            'cpu_health': cpu_health,
            'memory_health': memory_health,
            'disk_health': disk_health,
            'last_check': datetime.now().isoformat(),
            'uptime_percentage': random.uniform(99.5, 100.0),  # 99.5-100% uptime
            'incident_count': random.randint(0, 5),
            'last_incident': (datetime.now() - timedelta(hours=random.randint(0, 100))).isoformat() if random.random() > 0.7 else None
        }

    def get_logs(self) -> List[Dict[str, Any]]:
        """Get mock log entries"""
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        components = ["Server", "Client", "Database", "File Transfer", "Authentication"]

        logs = []
        for i in range(50):  # Last 50 log entries
            timestamp = datetime.now() - timedelta(
                hours=random.randint(0, 24),
                minutes=random.randint(0, 59)
            )

            level = random.choices(log_levels, weights=[50, 25, 15, 10])[0]
            component = random.choice(components)

            # Generate realistic log messages
            messages = {
                "INFO": [
                    f"Client connected from {random.choice([c['address'] for c in self.clients[:5]])}",
                    "File transfer completed successfully",
                    "Database backup completed",
                    "Server status check passed",
                ],
                "WARNING": [
                    "Client connection unstable",
                    "High memory usage detected",
                    "File verification failed, retrying",
                    "Database query slow",
                ],
                "ERROR": [
                    "Failed to authenticate client",
                    "File transfer interrupted",
                    "Database connection lost",
                    "Disk space running low",
                ],
                "DEBUG": [
                    "Processing client request",
                    f"Cache hit ratio: {random.randint(70, 95)}%",
                    f"Memory usage: {random.randint(30, 70)}%",
                    f"Active threads: {random.randint(5, 15)}",
                ],
            }

            message = random.choice(messages[level])

            logs.append({
                "id": i + 1,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "level": level,
                "component": component,
                "message": message
            })

        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        return logs

    def clear_logs(self) -> bool:
        """Clear all logs (mock implementation)"""
        with self._lock:
            try:
                # In a real implementation, this would clear the log storage
                # For mock purposes, we just log the action
                self._add_activity("logs_clear", "All logs have been cleared")
                logger.debug("MockDataGenerator: Logs cleared (mock operation)")
                return True
            except Exception as e:
                logger.error(f"MockDataGenerator: Failed to clear logs: {e}")
                return False

    def _apply_dynamic_changes(self):
        """Apply small changes to simulate real-time activity"""
        current_time = time.time()

        # Apply changes every 30 seconds
        if current_time - self.last_update > 30:
            self.last_update = current_time
            self.change_counter += 1

            # Randomly change 1-2 client statuses
            clients_to_change = random.sample(self.clients, min(2, len(self.clients)))
            for client in clients_to_change:
                old_status = client["status"]

                # Status transition probabilities
                if old_status == "Connected":
                    new_status = random.choices(
                        ["Connected", "Offline"],
                        weights=[90, 10]
                    )[0]
                elif old_status == "Offline":
                    new_status = random.choices(
                        ["Offline", "Connected"],
                        weights=[80, 20]
                    )[0]
                else:
                    new_status = random.choices(
                        ["Connected", "Registered", "Offline"],
                        weights=[40, 50, 10]
                    )[0]

                if new_status != old_status:
                    client["status"] = new_status
                    client["last_activity"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Occasionally add a new file
            if self.change_counter % 3 == 0 and len(self.files) < 100:
                self._add_random_file()

    def _add_random_file(self):
        """Add a random new file for dynamic testing"""
        if not self.clients:
            return

        client = random.choice(self.clients)
        file_id = f"file_{len(self.files)+1:03d}"

        filename = f"new_file_{len(self.files)}.pdf"
        file_size = random.randint(100_000, 2_000_000)

        new_file = {
            "file_id": file_id,
            "filename": filename,
            "pathname": f"/home/user/documents/{filename}",
            "size": file_size,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modification_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "client_id": client["client_id"],
            "client_name": client["name"],
            "verified": False,
            "crc": random.randint(100000000, 999999999),
            "status": "Uploading"
        }

        self.files.append(new_file)
        client["files_count"] += 1
        client["total_size"] += file_size

    def get_table_data(self, table_name: str) -> Dict[str, Any]:
        """Get table data for database view"""
        if table_name == "clients":
            return {
                "columns": ["id", "name", "address", "status", "last_seen", "files_count"],
                "rows": [
                    {
                        "id": c["client_id"],
                        "name": c["name"],
                        "address": c["address"],
                        "status": c["status"],
                        "last_seen": c["last_activity"],
                        "files_count": c["files_count"]
                    }
                    for c in self.clients
                ]
            }
        elif table_name == "files":
            return {
                "columns": ["id", "filename", "client_id", "size", "uploaded_at", "verified"],
                "rows": [
                    {
                        "id": f["file_id"],
                        "filename": f["filename"],
                        "client_id": f["client_id"],
                        "size": f["size"],
                        "uploaded_at": f["uploaded_at"],
                        "verified": f["verified"]
                    }
                    for f in self.files
                ]
            }
        else:
            return {"columns": [], "rows": []}

    def delete_file(self, file_id: str) -> bool:
        """Delete file and update client statistics with thread safety"""
        with self._lock:
            if file_id not in self._files:
                logger.warning(f"MockDataGenerator: File {file_id} not found for deletion")
                return False

            file_obj = self._files[file_id]

            if self._delete_file_internal(file_id):
                self._add_activity("file_delete", f"Deleted file {file_obj.name}")
                self._save_to_disk()
                self._notify_change("files", {"action": "delete", "file_id": file_id})
                logger.debug(f"MockDataGenerator: Successfully deleted file {file_id}")
                return True
            return False

    def add_client(self, client_data: dict) -> Optional[Dict[str, Any]]:
        """Add a new client to the mock data store.

        Args:
            client_data: Dictionary containing client information (name, ip_address, etc.)

        Returns:
            Dictionary representation of the created client, or None if creation failed
        """
        with self._lock:
            try:
                return self._extracted_from_add_client_13(client_data)
            except Exception as e:
                logger.error(f"MockDataGenerator: Failed to add client: {e}")
                return None

    # TODO Rename this here and in `add_client`
    def _extracted_from_add_client_13(self, client_data):
        # Generate unique ID
        client_id = str(uuid.uuid4())

        # Create new client with provided data and defaults
        new_client = MockClient(
            id=client_id,
            name=client_data.get('name', f'Client-{client_id[:8]}'),
            ip_address=client_data.get('ip_address', f"192.168.1.{random.randint(100, 200)}"),
            status=client_data.get('status', 'connected'),
            last_seen=datetime.now(),
            files_count=0,  # New client starts with no files
            total_size=0,   # New client starts with no data
            connection_time=datetime.now(),
            version=client_data.get('version', "1.0.0"),
            platform=client_data.get('platform', random.choice(["Windows", "Linux", "MacOS"]))
        )

        # Add to internal storage
        self._clients[client_id] = new_client
        self._client_file_index[client_id] = set()

        # Update change tracking
        self._update_statistics_after_modification()
        self._add_activity("client_add", f"Added client {new_client.name}")
        self._save_to_disk()
        self._notify_change("clients", {"action": "add", "client_id": client_id})

        logger.debug(f"MockDataGenerator: Successfully added client {client_id} ({new_client.name})")
        return new_client.to_dict()

    def delete_client(self, client_id: str) -> bool:
        """Delete client with cascading file deletion and thread safety"""
        with self._lock:
            if client_id not in self._clients:
                logger.warning(f"MockDataGenerator: Client {client_id} not found for deletion")
                return False

            client = self._clients[client_id]

            # Cascading delete: remove all client files
            client_files = self._client_file_index.get(client_id, set()).copy()
            deleted_files = sum(
                self._delete_file_internal(file_id)
                for file_id in client_files
            )
            # Delete client
            del self._clients[client_id]
            del self._client_file_index[client_id]

            # Log activity
            self._add_activity(
                "client_delete",
                f"Deleted client {client.name} and {deleted_files} associated files"
            )

            self._save_to_disk()
            self._notify_change("clients", {"action": "delete", "client_id": client_id})
            logger.debug(f"MockDataGenerator: Successfully deleted client {client_id} with {deleted_files} associated files")
            return True

    def _delete_file_internal(self, file_id: str) -> bool:
        """Internal file deletion without locking (for cascading operations)"""
        if file_id not in self._files:
            return False

        file_obj = self._files[file_id]

        # Remove from client index
        if file_obj.client_id in self._client_file_index:
            self._client_file_index[file_obj.client_id].discard(file_id)

        # Delete file
        del self._files[file_id]
        return True

    def _add_activity(self, activity_type: str, message: str, timestamp: Optional[datetime] = None):
        """Add activity to log with timestamp"""
        activity = {
            "id": f"activity_{int(time.time() * 1000)}_{len(self._activity_log)}",
            "type": activity_type,
            "message": message,
            "timestamp": timestamp or datetime.now()
        }
        self._activity_log.append(activity)

        # Keep only last 100 activities for performance
        if len(self._activity_log) > 100:
            self._activity_log = self._activity_log[-100:]

        self._notify_change("activity", activity)

    def _notify_change(self, change_type: str, data: Any):
        """Notify listeners of data changes"""
        for listener in self._change_listeners:
            try:
                listener(change_type, data)
            except Exception as e:
                logger.error(f"Change listener failed: {e}")

    def _record_server_action(self, activity_type: str, message: str, action: str):
        """Record server action with activity logging, persistence, and notification."""
        self._add_activity(activity_type, message)
        self._save_to_disk()
        self._notify_change("server", {"action": action})

    def _save_to_disk(self):
        """Save current state to disk"""
        if not self.persist_to_disk or not self.data_file:
            return

        try:
            data = {
                "clients": {k: v.to_dict() for k, v in self._clients.items()},
                "files": {k: v.to_dict() for k, v in self._files.items()},
                "activity_log": [{**activity, "timestamp": activity["timestamp"].isoformat() if isinstance(activity["timestamp"], datetime) else activity["timestamp"]} for activity in self._activity_log],
                "server_status": {**self._server_status, "start_time": self._server_status["start_time"].isoformat()},
                "saved_at": datetime.now().isoformat()
            }

            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Mock data persisted to {self.data_file}")
        except Exception as e:
            logger.error(f"Failed to save mock data: {e}")

    def _load_from_disk(self):
        """Load state from disk"""
        if not self.data_file:
            return
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)

            with self._lock:
                self._extracted_from__load_from_disk_11(data)
            logger.debug(f"Mock data loaded from {self.data_file}")
        except Exception as e:
            logger.error(f"Failed to load mock data: {e}")

    # TODO Rename this here and in `_load_from_disk`
    def _extracted_from__load_from_disk_11(self, data):
        # Load clients
        for client_id, client_data in data.get("clients", {}).items():
            # Convert ISO strings back to datetime objects
            client_data["last_seen"] = datetime.fromisoformat(client_data["last_seen"])
            if client_data.get("connection_time"):
                client_data["connection_time"] = datetime.fromisoformat(client_data["connection_time"])

            self._clients[client_id] = MockClient(**client_data)
            self._client_file_index[client_id] = set()

        # Load files
        for file_id, file_data in data.get("files", {}).items():
            file_data["created"] = datetime.fromisoformat(file_data["created"])
            file_data["modified"] = datetime.fromisoformat(file_data["modified"])
            if file_data.get("last_backup"):
                file_data["last_backup"] = datetime.fromisoformat(file_data["last_backup"])

            file_obj = MockFile(**file_data)
            self._files[file_id] = file_obj
            if file_obj.client_id in self._client_file_index:
                self._client_file_index[file_obj.client_id].add(file_id)

        # Load activity log
        self._activity_log = []
        for activity in data.get("activity_log", []):
            if isinstance(activity["timestamp"], str):
                activity["timestamp"] = datetime.fromisoformat(activity["timestamp"])
            self._activity_log.append(activity)

        # Load server status
        server_status = data.get("server_status", {})
        if server_status.get("start_time"):
            server_status["start_time"] = datetime.fromisoformat(server_status["start_time"])
        self._server_status.update(server_status)

    def get_client(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get specific client by ID"""
        with self._lock:
            if client := self._clients.get(client_id):
                client_dict = client.to_dict()
                client_files = self._client_file_index.get(client_id, set())
                client_dict["files_count"] = len(client_files)
                client_dict["total_size"] = sum(self._files[fid].size for fid in client_files if fid in self._files)
                return client_dict
            return None

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get specific file by ID"""
        with self._lock:
            file_obj = self._files.get(file_id)
            return file_obj.to_dict() if file_obj else None

    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect client (change status)"""
        with self._lock:
            if client_id not in self._clients:
                return False

            client = self._clients[client_id]
            client.status = "disconnected"
            client.last_seen = datetime.now()

            self._add_activity("client_disconnect", f"Client {client.name} disconnected")
            self._save_to_disk()
            self._notify_change("clients", {"action": "disconnect", "client_id": client_id})
            return True

    def verify_file(self, file_id: str) -> Dict[str, Any]:
        """Verify file integrity"""
        with self._lock:
            if file_id not in self._files:
                return {"success": False, "message": "File not found"}

            file_obj = self._files[file_id]

            # 95% success rate for verification
            if random.random() > 0.05:
                file_obj.status = "verified"
                self._add_activity("file_verify", f"File {file_obj.name} verified successfully")
                self._save_to_disk()
                return {
                    "success": True,
                    "message": "File verified successfully",
                    "hash": file_obj.hash,
                    "status": "verified"
                }
            else:
                file_obj.status = "error"
                self._add_activity("file_error", f"File {file_obj.name} verification failed")
                return {"success": False, "message": "File verification failed"}

    def start_server(self) -> Dict[str, Any]:
        """Start server simulation"""
        with self._lock:
            if not self._server_status["running"]:
                self._server_status["running"] = True
                self._server_status["start_time"] = datetime.now()
                self._record_server_action("server_start", "Backup server started", "start")
                return {"success": True, "message": "Server started successfully"}
            return {"success": False, "message": "Server is already running"}

    def stop_server(self) -> Dict[str, Any]:
        """Stop server simulation"""
        with self._lock:
            if self._server_status["running"]:
                self._server_status["running"] = False
                # Disconnect all clients
                for client in self._clients.values():
                    if client.status == "connected":
                        client.status = "disconnected"
                        client.last_seen = datetime.now()

                self._record_server_action("server_stop", "Backup server stopped", "stop")
                return {"success": True, "message": "Server stopped successfully"}
            return {"success": False, "message": "Server is not running"}

    def add_change_listener(self, listener: Callable):
        """Add listener for data changes"""
        self._change_listeners.append(listener)

    def remove_change_listener(self, listener: Callable):
        """Remove change listener"""
        if listener in self._change_listeners:
            self._change_listeners.remove(listener)

    def cleanup(self):
        """Cleanup resources"""
        self._save_to_disk()
        self._change_listeners.clear()

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics"""
        with self._lock:
            return {
                "tables": {
                    "clients": len(self._clients),
                    "files": len(self._files),
                    "activity_log": len(self._activity_log)
                },
                "total_size": sum(f.size for f in self._files.values()),
                "indexes": len(self._client_file_index),
                "last_updated": datetime.now()
            }

    def get_recent_activity(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent server activity for dashboard timeline"""
        with self._lock:
            # Use persistent activity log if it exists and has data
            if self._activity_log:
                activities = self._activity_log[-limit:] if limit > 0 else self._activity_log
                return [
                    {
                        **activity,
                        "timestamp": activity["timestamp"] if isinstance(activity["timestamp"], datetime) else datetime.fromisoformat(activity["timestamp"])
                    }
                    for activity in reversed(activities)
                ]

            # Fallback to legacy generated activity
            activity_types = [
                ("client_connect", "Client {} connected"),
                ("client_disconnect", "Client {} disconnected"),
                ("file_transfer", "File '{}' transferred"),
                ("backup_complete", "Backup job completed ({} files)"),
                ("system_check", "System health check passed"),
                ("error", "Failed to connect to update server"),
                ("database_backup", "Database backup completed"),
                ("maintenance", "System maintenance started"),
                ("user_login", "User {} logged in"),
                ("config_change", "Configuration updated by {}"),
                ("security_alert", "Security scan completed"),
                ("performance_issue", "Performance threshold exceeded"),
            ]

            activities = []
            now = datetime.now()

            # Generate more realistic activity data
            for _ in range(limit):
                # Generate activity with realistic timestamps (within last 24 hours)
                time_offset = timedelta(minutes=random.randint(0, 1440))  # 0-1440 minutes = 24 hours
                timestamp = now - time_offset

                # Select activity type
                activity_type, message_template = random.choice(activity_types)

                # Generate appropriate message based on type
                if activity_type in ["client_connect", "client_disconnect", "user_login"]:
                    client_ip = f"192.168.1.{random.randint(1, 254)}"
                    message = message_template.format(client_ip)
                elif activity_type == "file_transfer":
                    filename = f"backup_{random.randint(1000, 9999)}.zip"
                    message = message_template.format(filename)
                elif activity_type == "backup_complete":
                    file_count = random.randint(10, 1000)
                    message = message_template.format(file_count)
                elif activity_type == "config_change":
                    user = random.choice(["admin", "operator", "manager"])
                    message = message_template.format(user)
                else:
                    message = message_template

                activities.append({
                    "timestamp": timestamp,
                    "type": activity_type,
                    "message": message,
                    "severity": "info" if activity_type not in ["error", "security_alert", "performance_issue"] else "warning" if activity_type == "performance_issue" else "error"
                })

            # Sort by timestamp (newest first)
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            return activities

    async def get_recent_activity_async(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Async version of get_recent_activity."""
        await asyncio.sleep(0.01)  # Simulate async operation
        return self.get_recent_activity(limit)

    def _update_statistics_after_deletion(self):
        """Update global statistics and relationships after deletions."""
        try:
            # Recalculate global statistics that might be cached
            self.change_counter += 1
            self.last_update = time.time()

            # Could add more sophisticated statistics updates here
            # For now, just track that changes occurred
            logger.debug("MockDataGenerator: Statistics updated after deletion operations")

        except Exception as e:
            logger.error(f"MockDataGenerator statistics update error: {e}")

    def update_table_row(self, table_name: str, row_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update a row in mock database table with validation."""
        try:
            if table_name == "clients":
                return self._update_client_row(row_id, updated_data)
            elif table_name == "files":
                return self._update_file_row(row_id, updated_data)
            else:
                logger.warning(f"MockDataGenerator: Unknown table '{table_name}' for update")
                return False

        except Exception as e:
            logger.error(f"MockDataGenerator update_table_row error: {e}")
            return False

    def _update_client_row(self, row_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update a client row with validation."""
        try:
            client_to_update = next(
                (
                    client
                    for client in self.clients
                    if client.get('client_id') == row_id
                    or client.get('id') == row_id
                ),
                None,
            )
            if not client_to_update:
                logger.warning(f"MockDataGenerator: Client {row_id} not found for update")
                return False

            # Validate the update data
            allowed_fields = {'name', 'address', 'status', 'last_activity', 'last_seen'}

            for field, value in updated_data.items():
                if field in allowed_fields:
                    # Basic validation
                    if field == 'status' and value not in ['Connected', 'Registered', 'Offline']:
                        logger.warning(f"MockDataGenerator: Invalid status '{value}' for client update")
                        continue

                    # Apply the update
                    client_to_update[field] = value
                    logger.debug(f"MockDataGenerator: Updated client {row_id} field '{field}' to '{value}'")
                else:
                    logger.warning(f"MockDataGenerator: Field '{field}' not allowed for client update")

            self._update_statistics_after_modification()
            return True

        except Exception as e:
            logger.error(f"MockDataGenerator _update_client_row error: {e}")
            return False

    def _update_file_row(self, row_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update a file row with validation."""
        try:
            file_to_update = next(
                (
                    file_obj
                    for file_obj in self.files
                    if file_obj.get('file_id') == row_id
                    or file_obj.get('id') == row_id
                ),
                None,
            )
            if not file_to_update:
                logger.warning(f"MockDataGenerator: File {row_id} not found for update")
                return False

            # Validate the update data
            allowed_fields = {'filename', 'verified', 'status'}

            original_size = file_to_update.get('size', 0)
            original_client_id = file_to_update.get('client_id')

            for field, value in updated_data.items():
                if field in allowed_fields:
                    # Basic validation
                    if field == 'verified' and not isinstance(value, bool):
                        logger.warning(f"MockDataGenerator: Invalid verified value '{value}' for file update")
                        continue

                    # Apply the update
                    file_to_update[field] = value
                    logger.debug(f"MockDataGenerator: Updated file {row_id} field '{field}' to '{value}'")
                else:
                    logger.warning(f"MockDataGenerator: Field '{field}' not allowed for file update")

            # If size changed, update client statistics
            new_size = file_to_update.get('size', 0)
            if original_size != new_size and original_client_id:
                self._update_client_statistics_for_file_change(original_client_id, new_size - original_size)

            self._update_statistics_after_modification()
            return True

        except Exception as e:
            logger.error(f"MockDataGenerator _update_file_row error: {e}")
            return False

    def _update_client_statistics_for_file_change(self, client_id: str, size_delta: int):
        """Update client statistics when file sizes change."""
        try:
            for client in self.clients:
                if client.get('client_id') == client_id or client.get('id') == client_id:
                    current_size = client.get('total_size', 0)
                    client['total_size'] = max(0, current_size + size_delta)
                    logger.debug(f"MockDataGenerator: Updated client {client_id} total size by {size_delta}")
                    break
        except Exception as e:
            logger.error(f"MockDataGenerator client statistics update error: {e}")

    def _update_statistics_after_modification(self):
        """Update statistics after any modification operation."""
        try:
            self.change_counter += 1
            self.last_update = time.time()
            logger.debug("MockDataGenerator: Statistics updated after modification")
        except Exception as e:
            logger.error(f"MockDataGenerator modification statistics error: {e}")

    def generate_clients(self) -> List[Dict[str, Any]]:
        """Legacy method name for compatibility"""
        return self.get_clients()

    def generate_files(self) -> List[Dict[str, Any]]:
        """Legacy method name for compatibility"""
        return self.get_files()

    @property
    def clients(self) -> List[Dict[str, Any]]:
        """Legacy property for backward compatibility with ServerBridge"""
        return self.get_clients()

    @property
    def files(self) -> List[Dict[str, Any]]:
        """Legacy property for backward compatibility with ServerBridge"""
        return self.get_files()

    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate referential integrity of mock data (like a real database would)."""
        try:
            issues = []

            # Check for orphaned files (files without valid client_id)
            valid_client_ids = {c.get('client_id') for c in self.clients} | {c.get('id') for c in self.clients}

            orphaned_files = []
            for file_obj in self.files:
                file_client_id = file_obj.get('client_id')
                if file_client_id and file_client_id not in valid_client_ids:
                    orphaned_files.append(file_obj.get('file_id') or file_obj.get('id'))

            if orphaned_files:
                issues.append(f"Found {len(orphaned_files)} orphaned files: {orphaned_files[:5]}...")

            # Check client statistics consistency
            stats_issues = []
            for client in self.clients:
                client_id = client.get('client_id') or client.get('id')

                # Count actual files for this client
                actual_files = [f for f in self.files if f.get('client_id') == client_id]
                actual_file_count = len(actual_files)
                actual_total_size = sum(f.get('size', 0) for f in actual_files)

                # Compare with stored statistics
                stored_file_count = client.get('files_count', 0)
                stored_total_size = client.get('total_size', 0)

                if actual_file_count != stored_file_count:
                    stats_issues.append(f"Client {client_id}: file count mismatch (stored: {stored_file_count}, actual: {actual_file_count})")

                if abs(actual_total_size - stored_total_size) > 1024:  # Allow small discrepancies
                    stats_issues.append(f"Client {client_id}: size mismatch (stored: {stored_total_size}, actual: {actual_total_size})")

            if stats_issues:
                issues.extend(stats_issues)

            return {
                'valid': not issues,
                'issues': issues,
                'total_clients': len(self.clients),
                'total_files': len(self.files),
                'orphaned_files': len(orphaned_files),
            }

        except Exception as e:
            logger.error(f"MockDataGenerator integrity validation error: {e}")
            return {'valid': False, 'issues': [f"Validation error: {str(e)}"]}


# Global singleton instances for backward compatibility
_mock_generator_instance = None
_store_lock = threading.Lock()


def get_mock_generator() -> MockDataGenerator:
    """Get singleton mock data generator instance"""
    global _mock_generator_instance
    with _store_lock:
        if _mock_generator_instance is None:
            _mock_generator_instance = MockDataGenerator()
        return _mock_generator_instance


def get_mock_store(persist_to_disk: bool = False) -> MockDataGenerator:
    """Get global mock store instance (compatibility with PersistentMockStore interface)"""
    global _mock_generator_instance
    with _store_lock:
        if _mock_generator_instance is None:
            _mock_generator_instance = MockDataGenerator(persist_to_disk=persist_to_disk)
        return _mock_generator_instance


def cleanup_mock_store():
    """Cleanup global mock store"""
    global _mock_generator_instance
    with _store_lock:
        if _mock_generator_instance:
            _mock_generator_instance.cleanup()
            _mock_generator_instance = None


# Legacy compatibility aliases
PersistentMockStore = MockDataGenerator  # For any direct class imports
MockClient = MockClient  # Re-export for compatibility
MockFile = MockFile      # Re-export for compatibility