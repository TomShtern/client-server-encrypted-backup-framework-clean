#!/usr/bin/env python3
"""
Mock Server Bridge for FletV2
Provides a fake server bridge for standalone GUI development and testing.
This class mimics the real ServerBridge but returns hardcoded sample data
without any network calls.
"""

from .debug_setup import get_logger
import time
import random
from datetime import datetime, timedelta

logger = get_logger(__name__)


class MockServerBridge:
    """
    A mock implementation of the server bridge for UI development.
    """
    def __init__(self, *args, **kwargs):
        logger.info("Initialized MockServerBridge for standalone UI development.")
        self._clients = [
            {"client_id": "client_001", "address": "192.168.1.101:54321", "status": "Connected", "connected_at": "2025-09-05 10:30:15", "last_activity": "2025-09-05 14:45:30"},
            {"client_id": "client_002", "address": "192.168.1.102:54322", "status": "Registered", "connected_at": "2025-09-02 09:15:22", "last_activity": "2025-09-03 12:20:45"},
            {"client_id": "client_003", "address": "192.168.1.103:54323", "status": "Offline", "connected_at": "2025-09-01 14:22:10", "last_activity": "2025-09-02 16:33:55"},
            {"client_id": "client_004", "address": "192.168.1.104:54324", "status": "Connected", "connected_at": "2025-09-03 11:45:05", "last_activity": "2025-09-03 15:12:33"},
        ]
        self._files = [
            {"file_id": "file_001", "filename": "document1.pdf", "size": 1024000, "uploaded_at": "2025-09-03 10:30:15", "client_id": "client_001"},
            {"file_id": "file_002", "filename": "image1.jpg", "size": 2048000, "uploaded_at": "2025-09-03 11:45:30", "client_id": "client_002"}
        ]

    def _test_connection(self):
        """Mock connection test."""
        logger.info("MockServerBridge: Testing connection... Success!")
        return True

    def get_clients(self, force_refresh=False):
        """Returns a list of mock clients."""
        logger.info("MockServerBridge: get_clients() called.")
        time.sleep(0.1)  # Simulate network delay
        return self._clients

    def get_files(self):
        """Returns a list of mock files."""
        logger.info("MockServerBridge: get_files() called.")
        time.sleep(0.1)  # Simulate network delay
        return self._files

    def get_database_info(self):
        """Returns mock database information."""
        logger.info("MockServerBridge: get_database_info() called.")
        return {
            "status": "Connected",
            "tables": 5,
            "records": 1250,
            "size": "45.2 MB"
        }

    def get_logs(self):
        """Returns mock logs."""
        logger.info("MockServerBridge: get_logs() called.")
        return [
            {"id": 1, "timestamp": "2025-09-03 10:30:15", "level": "INFO", "component": "Server", "message": "Server started on port 1256"},
            {"id": 2, "timestamp": "2025-09-03 10:31:22", "level": "INFO", "component": "Client", "message": "Client client_001 connected"},
            {"id": 3, "timestamp": "2025-09-03 10:35:45", "level": "WARNING", "component": "File Transfer", "message": "File transfer completed with warnings"}
        ]

    def get_server_status(self):
        """Returns mock server status."""
        logger.info("MockServerBridge: get_server_status() called.")
        return {
            "server_running": True,
            "port": 1256,
            "uptime": "2h 34m",
            "total_transfers": 72,
            "active_clients": 3,
            "total_files": 45,
            "storage_used": "2.4 GB"
        }

    def get_recent_activity(self):
        """Returns mock recent activity."""
        logger.info("MockServerBridge: get_recent_activity() called.")
        base_time = datetime.now()
        activities = []
        for i in range(5):
            time_offset = timedelta(minutes=random.randint(1, 120))
            activity_time = base_time - time_offset
            activities.append({
                "time": activity_time.strftime("%H:%M"),
                "text": f"Activity {i+1}",
                "type": random.choice(["success", "info", "warning"])
            })
        return activities

    def get_system_status(self):
        """Returns mock system status."""
        logger.info("MockServerBridge: get_system_status() called.")
        return {
            "cpu_usage": f"{random.uniform(10, 40):.1f}%",
            "memory_usage": f"{random.uniform(30, 60):.1f}%",
            "disk_usage": "75.2%",
            "database_status": "Online",
            "server_status": "Active",
            "total_clients": len(self._clients),
            "total_files": len(self._files)
        }

    def get_dashboard_summary(self):
        """Returns a mock dashboard summary."""
        logger.info("MockServerBridge: get_dashboard_summary() called.")
        return {
            "total_clients": len(self._clients),
            "online_clients": sum(1 for c in self._clients if c['status'] == 'Connected'),
            "total_files": len(self._files),
            "total_size": "22.4 MB",
            "recent_activity": [
                "File 'document1.pdf' received from client_001.",
                "Client 'client_002' connected.",
                "Backup for 'client_003' completed successfully."
            ]
        }

    def get_client_details(self, client_id):
        """Returns mock details for a specific client."""
        logger.info(f"MockServerBridge: get_client_details({client_id}) called.")
        client = next((c for c in self._clients if c['client_id'] == client_id), None)
        if client:
            return {
                **client,
                "os_type": "Windows 10",
                "client_version": "2.1.0",
                "backup_count": len([f for f in self._files if f['client_id'] == client_id])
            }
        return None

    def get_file_details(self, file_id):
        """Returns mock details for a specific file."""
        logger.info(f"MockServerBridge: get_file_details({file_id}) called.")
        return next((f for f in self._files if f['file_id'] == file_id), None)

    def get_database_stats(self):
        """Returns mock database statistics."""
        logger.info("MockServerBridge: get_database_stats() called.")
        return {
            "total_tables": 5,
            "total_records": 150,
            "db_size_mb": 12.3,
            "last_backup": "2025-09-05 18:00:00"
        }

    def get_table_data(self, table_name):
        """Returns mock table data."""
        logger.info(f"MockServerBridge: get_table_data({table_name}) called.")
        tables_data = {
            "clients": {
                "columns": ["id", "name", "last_seen", "has_public_key", "has_aes_key"],
                "rows": [
                    {"id": "client_001", "name": "Alpha Workstation", "last_seen": "2025-09-03 10:30:15", "has_public_key": True, "has_aes_key": True},
                    {"id": "client_002", "name": "Beta Server", "last_seen": "2025-09-02 09:15:22", "has_public_key": True, "has_aes_key": True},
                    {"id": "client_003", "name": "Gamma Laptop", "last_seen": "2025-09-01 14:22:10", "has_public_key": True, "has_aes_key": False}
                ]
            },
            "files": {
                "columns": ["id", "filename", "pathname", "verified", "filesize", "modification_date", "crc", "client_id", "client_name"],
                "rows": [
                    {"id": "file_001", "filename": "document1.pdf", "pathname": "/home/user/documents/document1.pdf", "verified": True, "filesize": 1024000, "modification_date": "2025-09-03 10:30:15", "crc": 123456789, "client_id": "client_001", "client_name": "Alpha Workstation"},
                    {"id": "file_002", "filename": "image1.jpg", "pathname": "/home/user/pictures/image1.jpg", "verified": False, "filesize": 2048000, "modification_date": "2025-09-03 11:45:30", "crc": 987654321, "client_id": "client_002", "client_name": "Beta Server"}
                ]
            },
            "logs": {
                "columns": ["id", "timestamp", "level", "component", "message"],
                "rows": [
                    {"id": 1, "timestamp": "2025-09-03 10:30:15", "level": "INFO", "component": "Server", "message": "Server started on port 1256"},
                    {"id": 2, "timestamp": "2025-09-03 10:31:22", "level": "INFO", "component": "Client", "message": "Client client_001 connected"},
                    {"id": 3, "timestamp": "2025-09-03 10:35:45", "level": "WARNING", "component": "File Transfer", "message": "File transfer completed with warnings"}
                ]
            }
        }
        
        return tables_data.get(table_name, {"columns": [], "rows": []})

    def disconnect_client(self, client_id):
        """Mock disconnect client."""
        logger.info(f"MockServerBridge: disconnect_client({client_id}) called.")
        for client in self._clients:
            if client["client_id"] == client_id:
                client["status"] = "Offline"
                return True
        return False

    def delete_client(self, client_id):
        """Mock delete client."""
        logger.info(f"MockServerBridge: delete_client({client_id}) called.")
        self._clients = [c for c in self._clients if c["client_id"] != client_id]
        return True


logger.info("MockServerBridge loaded and ready for standalone UI development.")