#!/usr/bin/env python3
"""
Simple Lorem Ipsum Placeholder Data Generator
Replaces complex mock data systems with lightweight Lorem ipsum style content.

This module provides clearly recognizable placeholder data that:
- Uses Lorem ipsum style text for names, descriptions, paths
- Has realistic structure for GUI components
- Returns structured format: {'success': bool, 'data': Any, 'error': str}
- Makes the GUI look populated while being obviously placeholder content
"""

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
import uuid
import random


class PlaceholderDataGenerator:
    """Simple Lorem ipsum style data generator for GUI testing."""

    def __init__(self):
        """Initialize with Lorem ipsum style base data."""
        # Lorem ipsum style client names
        self._client_names = [
            "Lorem-Ipsum-01", "Dolor-Sit-Amet-02", "Consectetur-03",
            "Adipiscing-Elit-04", "Sed-Do-Eiusmod-05", "Tempor-Incididunt-06",
            "Ut-Labore-Dolore-07", "Magna-Aliqua-08", "Enim-Ad-Minim-09",
            "Veniam-Quis-10", "Nostrud-Exercitation-11", "Ullamco-Laboris-12"
        ]

        # Lorem ipsum style file names
        self._file_names = [
            "lorem-ipsum.pdf", "dolor-sit-amet.docx", "consectetur.txt",
            "adipiscing-elit.jpg", "sed-do-eiusmod.mp4", "tempor-incididunt.zip",
            "ut-labore.xlsx", "dolore-magna.png", "aliqua-enim.py",
            "ad-minim-veniam.sql", "quis-nostrud.json", "exercitation.csv"
        ]

        # Lorem ipsum style paths
        self._paths = [
            "/Lorem/Ipsum/dolor", "/Sit/Amet/consectetur", "/Adipiscing/elit/sed",
            "/Do/Eiusmod/tempor", "/Incididunt/ut/labore", "/Et/Dolore/magna"
        ]

        # Lorem ipsum style log messages
        self._log_messages = [
            "Lorem ipsum dolor sit amet operation completed",
            "Consectetur adipiscing elit processing finished",
            "Sed do eiusmod tempor task executed successfully",
            "Ut labore et dolore magna connection established",
            "Aliqua enim ad minim veniam backup completed",
            "Quis nostrud exercitation service started",
            "Ullamco laboris nisi ut file transferred",
            "Aliquip ex ea commodo system initialized"
        ]

        # Lorem ipsum style component names
        self._components = ["Lorem", "Ipsum", "Dolor", "Sit", "Consectetur", "Adipiscing"]

        # Lorem ipsum style server status messages
        self._status_messages = [
            "Lorem ipsum server running normally",
            "Dolor sit amet backup service active",
            "Consectetur adipiscing connections healthy",
            "Sed do eiusmod system operational"
        ]

    # ============================================================================
    # CLIENT DATA
    # ============================================================================

    def get_clients(self) -> List[Dict[str, Any]]:
        """Generate Lorem ipsum style client data."""
        clients = []
        statuses = ["Connected", "Disconnected", "Connecting", "Registered", "Offline"]

        for i, name in enumerate(self._client_names):
            clients.append({
                'id': f"lorem-{i+1:03d}",
                'name': name,
                'status': random.choice(statuses),
                'last_seen': self._random_recent_time(),
                'files_count': random.randint(5, 100),
                'ip_address': f"192.168.{random.randint(1,10)}.{random.randint(100,199)}",
                'platform': random.choice(["Lorem-OS", "Ipsum-System", "Dolor-Platform"]),
                'version': f"{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,9)}"
            })

        return clients

    async def get_clients_async(self) -> List[Dict[str, Any]]:
        """Async version of get_clients."""
        return self.get_clients()

    def get_client_details(self, client_id: str) -> Dict[str, Any]:
        """Get Lorem ipsum style details for a specific client."""
        clients = self.get_clients()
        client = next((c for c in clients if c['id'] == client_id), None)

        if client:
            return {
                **client,
                'description': f"Lorem ipsum client {client_id} details",
                'location': f"/Lorem/Clients/{client['name']}/config",
                'last_backup': self._random_recent_time(),
                'total_data': f"{random.randint(1, 50)} GB"
            }

        return {}

    def add_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate adding a Lorem ipsum client."""
        return {
            'success': True,
            'data': {
                'id': f"lorem-new-{int(time.time())}",
                'name': client_data.get('name', 'Lorem-Ipsum-New'),
                'message': 'Lorem ipsum client added successfully'
            },
            'error': None
        }

    async def add_client_async(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        """Async version of add_client."""
        return self.add_client(client_data)

    def delete_client(self, client_id: str) -> Dict[str, Any]:
        """Simulate deleting a Lorem ipsum client."""
        return {
            'success': True,
            'data': {'message': f'Lorem ipsum client {client_id} deleted'},
            'error': None
        }

    async def delete_client_async(self, client_id: str) -> Dict[str, Any]:
        """Async version of delete_client."""
        return self.delete_client(client_id)

    def disconnect_client(self, client_id: str) -> Dict[str, Any]:
        """Simulate disconnecting a Lorem ipsum client."""
        return {
            'success': True,
            'data': {'message': f'Lorem ipsum client {client_id} disconnected'},
            'error': None
        }

    async def disconnect_client_async(self, client_id: str) -> Dict[str, Any]:
        """Async version of disconnect_client."""
        return self.disconnect_client(client_id)

    def resolve_client(self, client_identifier: str) -> Dict[str, Any]:
        """Resolve Lorem ipsum client by ID or name."""
        clients = self.get_clients()
        client = next((c for c in clients if
                      c['id'] == client_identifier or
                      c['name'] == client_identifier), None)

        return {
            'success': bool(client),
            'data': client,
            'error': None if client else f'Lorem ipsum client {client_identifier} not found'
        }

    # ============================================================================
    # FILE DATA
    # ============================================================================

    def get_files(self) -> List[Dict[str, Any]]:
        """Generate Lorem ipsum style file data."""
        files = []
        types = ["document", "image", "video", "code", "archive"]
        statuses = ["complete", "verified", "uploading", "failed", "queued"]

        for i, name in enumerate(self._file_names):
            size = random.randint(1024, 1024*1024*100)  # 1KB to 100MB
            files.append({
                'id': f"file-lorem-{i+1:03d}",
                'name': name,
                'size': size,
                'type': random.choice(types),
                'status': random.choice(statuses),
                'modified': self._random_recent_time(),
                'path': f"{random.choice(self._paths)}/{name}",
                'client_id': f"lorem-{random.randint(1,12):03d}",
                'hash': f"lorem{random.randint(100000,999999)}",
                'created': self._random_recent_time(),
                'backup_count': random.randint(1, 5),
                'last_backup': self._random_recent_time()
            })

        return files

    async def get_files_async(self) -> List[Dict[str, Any]]:
        """Async version of get_files."""
        return self.get_files()

    def get_client_files(self, client_id: str) -> Dict[str, Any]:
        """Get Lorem ipsum files for a specific client."""
        all_files = self.get_files()
        client_files = [f for f in all_files if f['client_id'] == client_id]

        return {
            'success': True,
            'data': client_files,
            'error': None
        }

    async def get_client_files_async(self, client_id: str) -> Dict[str, Any]:
        """Async version of get_client_files."""
        return self.get_client_files(client_id)

    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Simulate deleting a Lorem ipsum file."""
        return {
            'success': True,
            'data': {'message': f'Lorem ipsum file {file_id} deleted'},
            'error': None
        }

    async def delete_file_async(self, file_id: str) -> Dict[str, Any]:
        """Async version of delete_file."""
        return self.delete_file(file_id)

    def delete_file_by_client_and_name(self, client_id: str, filename: str) -> Dict[str, Any]:
        """Simulate deleting a Lorem ipsum file by client and name."""
        return {
            'success': True,
            'data': {'message': f'Lorem ipsum file {filename} deleted from client {client_id}'},
            'error': None
        }

    async def delete_file_by_client_and_name_async(self, client_id: str, filename: str) -> Dict[str, Any]:
        """Async version of delete_file_by_client_and_name."""
        return self.delete_file_by_client_and_name(client_id, filename)

    def download_file(self, file_id: str, destination_path: str) -> Dict[str, Any]:
        """Simulate downloading a Lorem ipsum file."""
        return {
            'success': True,
            'data': {'message': f'Lorem ipsum file {file_id} downloaded to {destination_path}'},
            'error': None
        }

    async def download_file_async(self, file_id: str, destination_path: str) -> Dict[str, Any]:
        """Async version of download_file."""
        return self.download_file(file_id, destination_path)

    def verify_file(self, file_id: str) -> Dict[str, Any]:
        """Simulate verifying a Lorem ipsum file."""
        return {
            'success': True,
            'data': {'message': f'Lorem ipsum file {file_id} verified successfully'},
            'error': None
        }

    async def verify_file_async(self, file_id: str) -> Dict[str, Any]:
        """Async version of verify_file."""
        return self.verify_file(file_id)

    # ============================================================================
    # LOG DATA
    # ============================================================================

    def get_logs(self) -> List[Dict[str, Any]]:
        """Generate Lorem ipsum style log data."""
        logs = []
        levels = ["INFO", "ERROR", "WARNING", "DEBUG"]

        for i in range(50):  # Generate 50 log entries
            time_offset = timedelta(hours=random.randint(0, 24))
            log_time = datetime.now() - time_offset

            logs.append({
                'id': i + 1,
                'timestamp': log_time.strftime("%H:%M:%S"),
                'date': log_time.strftime("%Y-%m-%d"),
                'level': random.choice(levels),
                'component': random.choice(self._components),
                'message': random.choice(self._log_messages)
            })

        return sorted(logs, key=lambda x: x['id'], reverse=True)

    async def get_logs_async(self) -> List[Dict[str, Any]]:
        """Async version of get_logs."""
        return self.get_logs()

    async def clear_logs_async(self) -> Dict[str, Any]:
        """Simulate clearing Lorem ipsum logs."""
        return {
            'success': True,
            'data': {'message': 'Lorem ipsum logs cleared successfully'},
            'error': None
        }

    async def export_logs_async(self, export_format: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simulate exporting Lorem ipsum logs."""
        return {
            'success': True,
            'data': {
                'message': f'Lorem ipsum logs exported as {export_format}',
                'file_path': f'/Lorem/Exports/logs.{export_format}',
                'entries_exported': random.randint(10, 100)
            },
            'error': None
        }

    async def get_log_statistics_async(self) -> Dict[str, Any]:
        """Get Lorem ipsum style log statistics."""
        return {
            'success': True,
            'data': {
                'total_logs': random.randint(1000, 5000),
                'errors': random.randint(10, 50),
                'warnings': random.randint(50, 200),
                'info': random.randint(500, 2000),
                'debug': random.randint(100, 1000)
            },
            'error': None
        }

    async def stream_logs_async(self, callback: Callable[[Dict[str, Any]], None]) -> Dict[str, Any]:
        """Simulate streaming Lorem ipsum logs."""
        return {
            'success': True,
            'data': {'message': 'Lorem ipsum log streaming started'},
            'error': None
        }

    async def stop_log_stream_async(self, streaming_task: Any) -> Dict[str, Any]:
        """Simulate stopping Lorem ipsum log stream."""
        return {
            'success': True,
            'data': {'message': 'Lorem ipsum log streaming stopped'},
            'error': None
        }

    # ============================================================================
    # SERVER STATUS & ANALYTICS
    # ============================================================================

    def get_server_status(self) -> Dict[str, Any]:
        """Get Lorem ipsum style server status."""
        return {
            'success': True,
            'data': {
                'status': 'Running',
                'uptime': f"{random.randint(1, 72)} hours",
                'message': random.choice(self._status_messages),
                'version': '1.0.0-lorem',
                'environment': 'Lorem-Ipsum-Environment'
            },
            'error': None
        }

    async def get_server_status_async(self) -> Dict[str, Any]:
        """Async version of get_server_status."""
        return self.get_server_status()

    def get_detailed_server_status(self) -> Dict[str, Any]:
        """Get Lorem ipsum style detailed server status."""
        return {
            'success': True,
            'data': {
                **self.get_server_status()['data'],
                'connections': random.randint(5, 50),
                'memory_usage': f"{random.randint(30, 80)}%",
                'cpu_usage': f"{random.randint(10, 60)}%",
                'disk_space': f"{random.randint(40, 90)}% used"
            },
            'error': None
        }

    async def get_detailed_server_status_async(self) -> Dict[str, Any]:
        """Async version of get_detailed_server_status."""
        return self.get_detailed_server_status()

    def get_server_health(self) -> Dict[str, Any]:
        """Get Lorem ipsum style server health."""
        return {
            'success': True,
            'data': {
                'overall_health': 'Good',
                'services_running': random.randint(8, 12),
                'last_check': self._random_recent_time(),
                'alerts': random.randint(0, 3)
            },
            'error': None
        }

    async def get_server_health_async(self) -> Dict[str, Any]:
        """Async version of get_server_health."""
        return self.get_server_health()

    async def start_server_async(self) -> Dict[str, Any]:
        """Simulate starting Lorem ipsum server."""
        return {
            'success': True,
            'data': {'message': 'Lorem ipsum server started successfully'},
            'error': None
        }

    async def stop_server_async(self) -> Dict[str, Any]:
        """Simulate stopping Lorem ipsum server."""
        return {
            'success': True,
            'data': {'message': 'Lorem ipsum server stopped successfully'},
            'error': None
        }

    def test_connection(self) -> Dict[str, Any]:
        """Test Lorem ipsum connection."""
        return {
            'success': True,
            'data': {'message': 'Lorem ipsum connection test passed'},
            'error': None
        }

    async def test_connection_async(self) -> Dict[str, Any]:
        """Async version of test_connection."""
        return self.test_connection()

    # ============================================================================
    # ANALYTICS DATA
    # ============================================================================

    def get_analytics_data(self) -> Dict[str, Any]:
        """Get Lorem ipsum style analytics data."""
        return {
            'success': True,
            'data': {
                'total_clients': random.randint(10, 100),
                'active_connections': random.randint(5, 50),
                'total_files': random.randint(100, 1000),
                'total_storage': f"{random.randint(10, 500)} GB",
                'backup_success_rate': f"{random.randint(85, 99)}%",
                'average_backup_time': f"{random.randint(5, 30)} minutes"
            },
            'error': None
        }

    async def get_analytics_data_async(self) -> Dict[str, Any]:
        """Async version of get_analytics_data."""
        return self.get_analytics_data()

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get Lorem ipsum style performance metrics."""
        return {
            'success': True,
            'data': {
                'cpu_usage': random.randint(10, 80),
                'memory_usage': random.randint(30, 90),
                'disk_usage': random.randint(40, 85),
                'network_in': random.randint(100, 1000),
                'network_out': random.randint(50, 500),
                'response_time': random.randint(50, 200)
            },
            'error': None
        }

    async def get_performance_metrics_async(self) -> Dict[str, Any]:
        """Async version of get_performance_metrics."""
        return self.get_performance_metrics()

    def get_historical_data(self, metric: str, hours: int = 24) -> Dict[str, Any]:
        """Get Lorem ipsum style historical data."""
        data_points = []
        for i in range(hours):
            time_point = datetime.now() - timedelta(hours=i)
            data_points.append({
                'timestamp': time_point.strftime("%H:%M"),
                'value': random.randint(10, 100),
                'label': f"Lorem-{i}"
            })

        return {
            'success': True,
            'data': {
                'metric': f"lorem-{metric}",
                'data_points': data_points,
                'unit': 'Lorem Units'
            },
            'error': None
        }

    async def get_historical_data_async(self, metric: str, hours: int = 24) -> Dict[str, Any]:
        """Async version of get_historical_data."""
        return self.get_historical_data(metric, hours)

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get Lorem ipsum style dashboard summary."""
        return {
            'success': True,
            'data': {
                'status': 'Lorem Ipsum Active',
                'clients_online': random.randint(5, 20),
                'recent_backups': random.randint(10, 50),
                'system_health': random.choice(['Excellent', 'Good', 'Fair']),
                'alerts': random.randint(0, 3),
                'storage_used': f"{random.randint(40, 85)}%"
            },
            'error': None
        }

    async def get_dashboard_summary_async(self) -> Dict[str, Any]:
        """Async version of get_dashboard_summary."""
        return self.get_dashboard_summary()

    def get_server_statistics(self) -> Dict[str, Any]:
        """Get Lorem ipsum style server statistics."""
        return {
            'success': True,
            'data': {
                'uptime_days': random.randint(1, 30),
                'total_requests': random.randint(1000, 10000),
                'error_rate': f"{random.randint(0, 5)}%",
                'average_response_time': f"{random.randint(50, 200)}ms",
                'peak_concurrent_users': random.randint(10, 100)
            },
            'error': None
        }

    async def get_server_statistics_async(self) -> Dict[str, Any]:
        """Async version of get_server_statistics."""
        return self.get_server_statistics()

    async def get_recent_activity_async(self, limit: int = 50) -> Dict[str, Any]:
        """Get Lorem ipsum style recent activity."""
        activities = []
        for i in range(min(limit, 20)):  # Limit to 20 for simplicity
            activities.append({
                'id': i + 1,
                'timestamp': self._random_recent_time(),
                'action': random.choice(['Lorem Action', 'Ipsum Task', 'Dolor Process']),
                'description': f"Lorem ipsum activity {i + 1} completed",
                'user': f"Lorem-User-{random.randint(1, 5)}"
            })

        return {
            'success': True,
            'data': activities,
            'error': None
        }

    # ============================================================================
    # SYSTEM STATUS
    # ============================================================================

    def get_system_status(self) -> Dict[str, Any]:
        """Get Lorem ipsum style system status."""
        return {
            'success': True,
            'data': {
                'overall_status': 'Lorem Ipsum Operational',
                'services': {
                    'Lorem Service': 'Running',
                    'Ipsum Module': 'Running',
                    'Dolor Component': 'Running'
                },
                'last_update': self._random_recent_time()
            },
            'error': None
        }

    async def get_system_status_async(self) -> Dict[str, Any]:
        """Async version of get_system_status."""
        return self.get_system_status()

    # ============================================================================
    # SETTINGS MANAGEMENT
    # ============================================================================

    async def save_settings_async(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate saving Lorem ipsum settings."""
        return {
            'success': True,
            'data': {'message': 'Lorem ipsum settings saved successfully'},
            'error': None
        }

    def save_settings(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate saving Lorem ipsum settings (sync)."""
        return {
            'success': True,
            'data': {'message': 'Lorem ipsum settings saved successfully'},
            'error': None
        }

    async def load_settings_async(self) -> Dict[str, Any]:
        """Load Lorem ipsum style settings."""
        return {
            'success': True,
            'data': {
                'server_name': 'Lorem Ipsum Server',
                'backup_interval': '24 hours',
                'max_connections': random.randint(50, 200),
                'theme': 'Lorem Theme',
                'notifications': True
            },
            'error': None
        }

    def load_settings(self) -> Dict[str, Any]:
        """Load Lorem ipsum style settings (sync)."""
        return {
            'success': True,
            'data': {
                'server_name': 'Lorem Ipsum Server',
                'backup_interval': '24 hours',
                'max_connections': random.randint(50, 200),
                'theme': 'Lorem Theme',
                'notifications': True
            },
            'error': None
        }

    async def validate_settings_async(self, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Lorem ipsum settings."""
        return {
            'success': True,
            'data': {'message': 'Lorem ipsum settings validation passed'},
            'error': None
        }

    async def backup_settings_async(self, backup_name: str, settings_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Lorem ipsum settings backup."""
        return {
            'success': True,
            'data': {
                'message': f'Lorem ipsum settings backup "{backup_name}" created',
                'backup_path': f'/Lorem/Backups/{backup_name}.json'
            },
            'error': None
        }

    async def restore_settings_async(self, backup_file: str) -> Dict[str, Any]:
        """Restore Lorem ipsum settings from backup."""
        return {
            'success': True,
            'data': {'message': f'Lorem ipsum settings restored from {backup_file}'},
            'error': None
        }

    async def get_default_settings_async(self) -> Dict[str, Any]:
        """Get Lorem ipsum default settings."""
        return {
            'success': True,
            'data': {
                'server_name': 'Default Lorem Server',
                'backup_interval': '24 hours',
                'max_connections': 100,
                'theme': 'Default Lorem Theme',
                'notifications': True,
                'encryption': True
            },
            'error': None
        }

    # ============================================================================
    # DATABASE OPERATIONS
    # ============================================================================

    def get_database_info(self) -> Dict[str, Any]:
        """Get Lorem ipsum style database info."""
        return {
            'success': True,
            'data': {
                'status': 'Connected (Lorem Ipsum)',
                'tables': random.randint(5, 15),
                'total_records': random.randint(500, 2000),
                'size': f"{random.randint(10, 100)} MB",
                'integrity_check': True,
                'foreign_key_check': True,
                'connection_pool_healthy': True
            },
            'error': None
        }

    def get_table_names(self) -> Dict[str, Any]:
        """Get Lorem ipsum style table names."""
        return {
            'success': True,
            'data': ['lorem_clients', 'ipsum_files', 'dolor_logs', 'sit_settings'],
            'error': None
        }

    def get_table_data(self, table_name: str) -> Dict[str, Any]:
        """Get Lorem ipsum style table data."""
        if table_name == 'lorem_clients':
            return {
                'success': True,
                'data': {
                    'columns': ['id', 'name', 'status', 'created'],
                    'rows': self.get_clients()
                },
                'error': None
            }
        elif table_name == 'ipsum_files':
            return {
                'success': True,
                'data': {
                    'columns': ['id', 'name', 'size', 'type', 'status'],
                    'rows': self.get_files()
                },
                'error': None
            }
        else:
            return {
                'success': True,
                'data': {
                    'columns': ['lorem', 'ipsum', 'dolor'],
                    'rows': [
                        {'lorem': 'Lorem', 'ipsum': 'Ipsum', 'dolor': 'Dolor'},
                        {'lorem': 'Sit', 'ipsum': 'Amet', 'dolor': 'Consectetur'}
                    ]
                },
                'error': None
            }

    # ============================================================================
    # HELPER METHODS
    # ============================================================================

    def _random_recent_time(self) -> str:
        """Generate a random recent timestamp."""
        time_offset = timedelta(hours=random.randint(0, 24))
        recent_time = datetime.now() - time_offset
        return recent_time.strftime("%Y-%m-%d %H:%M:%S")


# ============================================================================
# SINGLETON INSTANCE AND FACTORY FUNCTIONS
# ============================================================================

# Global singleton instance for consistent Lorem ipsum data
_placeholder_generator: Optional[PlaceholderDataGenerator] = None

def get_placeholder_generator() -> PlaceholderDataGenerator:
    """Get or create the global placeholder data generator."""
    global _placeholder_generator
    if _placeholder_generator is None:
        _placeholder_generator = PlaceholderDataGenerator()
    return _placeholder_generator

def create_placeholder_generator() -> PlaceholderDataGenerator:
    """Factory function to create a new placeholder data generator."""
    return PlaceholderDataGenerator()

# Convenience function for direct usage
def get_lorem_clients() -> List[Dict[str, Any]]:
    """Get Lorem ipsum style client data directly."""
    return get_placeholder_generator().get_clients()

def get_lorem_files() -> List[Dict[str, Any]]:
    """Get Lorem ipsum style file data directly."""
    return get_placeholder_generator().get_files()

def get_lorem_logs() -> List[Dict[str, Any]]:
    """Get Lorem ipsum style log data directly."""
    return get_placeholder_generator().get_logs()


# Module exports
__all__ = [
    'PlaceholderDataGenerator',
    'get_placeholder_generator',
    'create_placeholder_generator',
    'get_lorem_clients',
    'get_lorem_files',
    'get_lorem_logs'
]