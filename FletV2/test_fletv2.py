#!/usr/bin/env python3
"""
Consolidated FletV2 Test Suite

Tests all ServerBridge functionality, mock mode, and real server integration.
Uses pytest for efficient test organization and reporting.

Usage:
    pytest test_fletv2.py -v                    # Verbose output
    pytest test_fletv2.py -v --tb=short        # Short traceback
    pytest test_fletv2.py -k "client"          # Run only client tests
    pytest test_fletv2.py --collect-only       # Show all tests without running
"""

import asyncio
import os
import sys
from pathlib import Path
import pytest

# Add parent directory to path for Shared imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Add the utils directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from utils.server_bridge import create_server_bridge


# ============================================================================
# PYTEST FIXTURES - Shared setup for all tests
# ============================================================================

@pytest.fixture
def bridge():
    """Create ServerBridge in mock mode for testing."""
    return create_server_bridge()


@pytest.fixture
def mock_real_server():
    """Create mock real server for drop-in capability testing."""
    class MockRealServer:
        def is_connected(self):
            return True

        def get_clients(self):
            return [{"id": "real_client_1", "name": "Real Client", "status": "connected"}]

        def get_server_status(self):
            return {"server_running": True, "mode": "production", "clients_connected": 1}

    return MockRealServer()


@pytest.fixture
def real_bridge(mock_real_server):
    """Create ServerBridge with mock real server."""
    return create_server_bridge(mock_real_server)


# ============================================================================
# CLIENT OPERATIONS TESTS
# ============================================================================

class TestClientOperations:
    """Test all client-related operations."""

    @pytest.mark.asyncio
    async def test_get_clients(self, bridge):
        """Test retrieving client list."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_clients)

        assert result['success'], f"get_clients failed: {result['error']}"
        clients = result['data']
        assert isinstance(clients, list), "Clients data should be a list"
        print(f"✅ get_clients: Found {len(clients)} clients")

    @pytest.mark.asyncio
    async def test_get_client_details(self, bridge):
        """Test getting client details."""
        loop = asyncio.get_running_loop()

        # First get clients to have a valid ID
        clients_result = await loop.run_in_executor(None, bridge.get_clients)
        if clients_result['data']:
            client_id = clients_result['data'][0]['id']

            result = await loop.run_in_executor(None, bridge.get_client_details, client_id)
            assert result['success'], f"get_client_details failed: {result['error']}"
            print(f"✅ get_client_details: Got details for {result['data']['name']}")

    @pytest.mark.asyncio
    async def test_add_and_delete_client(self, bridge):
        """Test adding and deleting a client."""
        loop = asyncio.get_running_loop()

        # Test add_client
        new_client_data = {
            "name": "Test-Client",
            "ip_address": "192.168.1.200",
            "version": "2.1.4",
            "platform": "Test Platform"
        }
        add_result = await loop.run_in_executor(None, bridge.add_client, new_client_data)
        assert add_result['success'], f"add_client failed: {add_result['error']}"
        new_client_id = add_result['data']
        print(f"✅ add_client: Created client {new_client_id}")

        # Test delete_client
        delete_result = await loop.run_in_executor(None, bridge.delete_client, new_client_id)
        assert delete_result['success'], f"delete_client failed: {delete_result['error']}"
        print(f"✅ delete_client: Deleted client {new_client_id}")

    @pytest.mark.asyncio
    async def test_disconnect_and_resolve_client(self, bridge):
        """Test disconnecting and resolving client."""
        loop = asyncio.get_running_loop()

        clients_result = await loop.run_in_executor(None, bridge.get_clients)
        if clients_result['data']:
            client_id = clients_result['data'][0]['id']

            # Test disconnect_client
            disconnect_result = await loop.run_in_executor(None, bridge.disconnect_client, client_id)
            assert disconnect_result['success'], f"disconnect_client failed: {disconnect_result['error']}"
            print("✅ disconnect_client: Disconnected client")

            # Test resolve_client
            resolve_result = await loop.run_in_executor(None, bridge.resolve_client, client_id)
            assert resolve_result['success'], f"resolve_client failed: {resolve_result['error']}"
            print("✅ resolve_client: Resolved client by ID")


# ============================================================================
# FILE OPERATIONS TESTS
# ============================================================================

class TestFileOperations:
    """Test all file-related operations."""

    @pytest.mark.asyncio
    async def test_get_files(self, bridge):
        """Test retrieving file list."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_files)

        assert result['success'], f"get_files failed: {result['error']}"
        files = result['data']
        assert isinstance(files, list), "Files data should be a list"
        print(f"✅ get_files: Found {len(files)} files")

    @pytest.mark.asyncio
    async def test_get_client_files(self, bridge):
        """Test retrieving files for specific client."""
        loop = asyncio.get_running_loop()

        files_result = await loop.run_in_executor(None, bridge.get_files)
        if files_result['data']:
            client_id = files_result['data'][0]['client_id']

            result = await loop.run_in_executor(None, bridge.get_client_files, client_id)
            assert result['success'], f"get_client_files failed: {result['error']}"
            client_files = result['data']
            print(f"✅ get_client_files: Found {len(client_files)} files for client")

    @pytest.mark.asyncio
    async def test_verify_and_download_file(self, bridge):
        """Test file verification and download."""
        loop = asyncio.get_running_loop()

        files_result = await loop.run_in_executor(None, bridge.get_files)
        if files_result['data']:
            file_id = files_result['data'][0]['id']

            # Test verify_file
            verify_result = await loop.run_in_executor(None, bridge.verify_file, file_id)
            assert verify_result['success'], f"verify_file failed: {verify_result['error']}"
            print(f"✅ verify_file: Verified file {file_id}")

            # Test download_file - use Downloads folder for Windows compatibility
            download_path = os.path.join(os.path.expanduser("~"), "Downloads", "test_download.txt")
            download_result = await loop.run_in_executor(None, bridge.download_file, file_id, download_path)
            assert download_result['success'], f"download_file failed: {download_result['error']}"
            print(f"✅ download_file: Downloaded file {file_id}")

    @pytest.mark.asyncio
    async def test_delete_file(self, bridge):
        """Test file deletion."""
        loop = asyncio.get_running_loop()

        files_result = await loop.run_in_executor(None, bridge.get_files)
        if len(files_result['data']) > 1:
            delete_file_id = files_result['data'][1]['id']

            result = await loop.run_in_executor(None, bridge.delete_file, delete_file_id)
            assert result['success'], f"delete_file failed: {result['error']}"
            print(f"✅ delete_file: Deleted file {delete_file_id}")


# ============================================================================
# DATABASE OPERATIONS TESTS
# ============================================================================

class TestDatabaseOperations:
    """Test all database-related operations."""

    @pytest.mark.asyncio
    async def test_get_database_info(self, bridge):
        """Test retrieving database information."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_database_info)

        assert result['success'], f"get_database_info failed: {result['error']}"
        db_info = result['data']
        print(f"✅ get_database_info: {db_info['total_clients']} clients, {db_info['total_files']} files")

    @pytest.mark.asyncio
    async def test_get_table_data(self, bridge):
        """Test retrieving table data."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_table_data, "clients")

        assert result['success'], f"get_table_data failed: {result['error']}"
        table_data = result['data']
        print(f"✅ get_table_data: Got {len(table_data)} rows from clients table")

    @pytest.mark.asyncio
    async def test_update_row(self, bridge):
        """Test updating database row."""
        loop = asyncio.get_running_loop()

        table_result = await loop.run_in_executor(None, bridge.get_table_data, "clients")
        if table_result['data']:
            row_id = table_result['data'][0]['id']
            update_data = {"name": "Updated-Name"}

            result = await loop.run_in_executor(None, bridge.update_row, "clients", row_id, update_data)
            assert result['success'], f"update_row failed: {result['error']}"
            print(f"✅ update_row: Updated client {row_id}")

    @pytest.mark.asyncio
    async def test_add_and_delete_table_record(self, bridge):
        """Test adding and deleting table records."""
        loop = asyncio.get_running_loop()

        # Test add_table_record
        new_record = {"name": "Test-Record", "status": "active"}
        add_result = await loop.run_in_executor(None, bridge.add_table_record, "clients", new_record)
        assert add_result['success'], f"add_table_record failed: {add_result['error']}"
        print("✅ add_table_record: Added new record")

        # Note: delete_table_record would be tested here if we had the record ID


# ============================================================================
# LOG OPERATIONS TESTS
# ============================================================================

class TestLogOperations:
    """Test all log-related operations."""

    @pytest.mark.asyncio
    async def test_get_logs(self, bridge):
        """Test retrieving logs."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_logs)

        assert result['success'], f"get_logs failed: {result['error']}"
        logs = result['data']
        print(f"✅ get_logs: Found {len(logs)} log entries")

    @pytest.mark.asyncio
    async def test_get_log_statistics(self, bridge):
        """Test retrieving log statistics."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_log_statistics)

        assert result['success'], f"get_log_statistics failed: {result['error']}"
        stats = result['data']
        print(f"✅ get_log_statistics: {stats['total_logs']} logs, levels: {list(stats['levels'].keys())}")

    @pytest.mark.asyncio
    async def test_export_logs(self, bridge):
        """Test exporting logs."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.export_logs, "json", {"level": "INFO"})

        assert result['success'], f"export_logs failed: {result['error']}"
        export_data = result['data']
        print(f"✅ export_logs: Exported {export_data['count']} logs in {export_data['format']} format")

    @pytest.mark.asyncio
    async def test_clear_logs(self, bridge):
        """Test clearing logs."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.clear_logs)

        assert result['success'], f"clear_logs failed: {result['error']}"
        print("✅ clear_logs: Successfully cleared logs")


# ============================================================================
# SERVER STATUS TESTS
# ============================================================================

class TestServerStatus:
    """Test server status and monitoring operations."""

    @pytest.mark.asyncio
    async def test_get_server_status(self, bridge):
        """Test retrieving server status."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_server_status)

        assert result['success'], f"get_server_status failed: {result['error']}"
        status = result['data']
        print(f"✅ get_server_status: Server running: {status['server_running']}, {status['clients_connected']} clients connected")

    @pytest.mark.asyncio
    async def test_get_system_status(self, bridge):
        """Test retrieving system status."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_system_status)

        assert result['success'], f"get_system_status failed: {result['error']}"
        sys_status = result['data']
        print(f"✅ get_system_status: CPU: {sys_status['cpu_usage']:.1f}%, Memory: {sys_status['memory_usage']:.1f}%")

    def test_is_connected(self, bridge):
        """Test connection status check."""
        is_connected = bridge.is_connected()
        print(f"✅ is_connected: {is_connected}")

    @pytest.mark.asyncio
    async def test_connection(self, bridge):
        """Test connection testing."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.test_connection)

        assert result['success'], f"test_connection failed: {result['error']}"
        print("✅ test_connection: Connection test successful")


# ============================================================================
# ANALYTICS TESTS
# ============================================================================

class TestAnalytics:
    """Test analytics and performance operations."""

    @pytest.mark.asyncio
    async def test_get_analytics_data(self, bridge):
        """Test retrieving analytics data."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_analytics_data)

        assert result['success'], f"get_analytics_data failed: {result['error']}"
        analytics = result['data']
        print(f"✅ get_analytics_data: Got analytics data with {len(analytics)} metrics")

    @pytest.mark.asyncio
    async def test_get_dashboard_summary(self, bridge):
        """Test retrieving dashboard summary."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, bridge.get_dashboard_summary)

        assert result['success'], f"get_dashboard_summary failed: {result['error']}"
        summary = result['data']
        print(f"✅ get_dashboard_summary: Dashboard shows {summary.get('total_clients', 0)} clients")


# ============================================================================
# SETTINGS TESTS
# ============================================================================

class TestSettings:
    """Test settings management operations."""

    @pytest.mark.asyncio
    async def test_save_and_load_settings(self, bridge):
        """Test saving and loading settings."""
        loop = asyncio.get_running_loop()

        # Test save_settings
        test_settings = {
            "test_setting": "test_value",
            "backup_retention": 30,
            "compression": True
        }
        save_result = await loop.run_in_executor(None, bridge.save_settings, test_settings)
        assert save_result['success'], f"save_settings failed: {save_result['error']}"
        print(f"✅ save_settings: Saved {len(test_settings)} settings")

        # Test load_settings
        load_result = await loop.run_in_executor(None, bridge.load_settings)
        assert load_result['success'], f"load_settings failed: {load_result['error']}"
        loaded_settings = load_result['data']
        print(f"✅ load_settings: Loaded {len(loaded_settings)} settings")

        # Verify settings were saved correctly
        assert loaded_settings.get('test_setting') == 'test_value', "Settings not saved correctly"
        print("✅ Settings persistence: Verified settings were saved and loaded correctly")

    @pytest.mark.asyncio
    async def test_validate_settings(self, bridge):
        """Test settings validation."""
        loop = asyncio.get_running_loop()

        test_settings = {"backup_retention": 30}
        result = await loop.run_in_executor(None, bridge.validate_settings, test_settings)

        assert result['success'], f"validate_settings failed: {result['error']}"
        print("✅ validate_settings: Settings validated successfully")


# ============================================================================
# MOCK MODE TESTS
# ============================================================================

class TestMockMode:
    """Test mock mode functionality."""

    @pytest.mark.asyncio
    async def test_mock_mode_indicators(self, bridge):
        """Test that mock mode returns proper indicators."""
        loop = asyncio.get_running_loop()

        # Test download with mock indicator
        download_path = os.path.join(os.path.expanduser("~"), "Downloads", "test.txt")
        download_result = await loop.run_in_executor(None, bridge.download_file, "test_file", download_path)
        assert download_result['success'], "Mock download should succeed"
        assert 'mode' in download_result, "Mock download should include mode indicator"
        print(f"✅ Mock download: {download_result}")

        # Test verify with mock indicator
        verify_result = await loop.run_in_executor(None, bridge.verify_file, "test_file")
        assert verify_result['success'], "Mock verify should succeed"
        assert 'mode' in verify_result, "Mock verify should include mode indicator"
        print(f"✅ Mock verify: {verify_result}")

        # Test database operations with mock indicator
        update_result = await loop.run_in_executor(None, bridge.update_row, "test_table", "test_id", {"name": "test"})
        assert update_result['success'], "Mock update should succeed"
        assert 'mode' in update_result, "Mock update should include mode indicator"
        print(f"✅ Mock update: {update_result}")

    def test_mock_mode_not_connected(self, bridge):
        """Test that mock mode reports not connected."""
        is_connected = bridge.is_connected()
        assert not is_connected, "Mock mode should report not connected"
        print(f"✅ Mock mode connection status: {is_connected}")


# ============================================================================
# REAL SERVER INTEGRATION TESTS
# ============================================================================

class TestRealServerIntegration:
    """Test drop-in capability with real server."""

    @pytest.mark.asyncio
    async def test_real_server_get_clients(self, real_bridge):
        """Test getting clients from real server."""
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, real_bridge.get_clients)

        # Real server returns raw list, not structured response
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert result[0]['name'] == "Real Client", "Not using real server data"
        print("✅ Real server get_clients: Successfully used real server methods")

    def test_real_server_status(self, real_bridge):
        """Test getting server status from real server."""
        result = real_bridge.get_server_status()

        assert result['success'], f"Real server get_server_status failed: {result['error']}"
        status = result['data']
        assert status['mode'] == "production", "Not using real server status"
        print("✅ Real server status: Real server status indicates production mode")

    def test_real_server_is_connected(self, real_bridge):
        """Test that real server reports connected."""
        is_connected = real_bridge.is_connected()
        assert is_connected, "Real server should report connected"
        print(f"✅ Real server is_connected: {is_connected}")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    """Run tests with pytest."""
    import subprocess

    print("🚀 Running Consolidated FletV2 Test Suite")
    print("=" * 80)

    # Run pytest with verbose output
    result = subprocess.run(
        ["pytest", __file__, "-v", "--tb=short", "--color=yes"],
        capture_output=False
    )

    sys.exit(result.returncode)
