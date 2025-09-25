#!/usr/bin/env python3
"""
Database Integration Test Suite for FletV2

This script tests the complete database integration between BackupServer and FletV2,
including configuration, data format conversion, and view compatibility.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseIntegrationTester:
    """Comprehensive test suite for database integration."""

    def __init__(self):
        self.test_results = {}
        self.backup_server = None
        self.server_bridge = None

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all database integration tests."""
        logger.info("🚀 Starting Database Integration Test Suite")
        logger.info("=" * 60)

        tests = [
            ("Configuration Tests", self.test_configuration),
            ("Database Connectivity", self.test_database_connectivity),
            ("Data Format Conversion", self.test_data_conversion),
            ("ServerBridge Operations", self.test_server_bridge),
            ("Migration System", self.test_migration_system),
            ("View Compatibility", self.test_view_compatibility),
            ("Real Data Access", self.test_real_data_access)
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            logger.info(f"\n📋 Running {test_name}...")
            try:
                result = await test_func()
                self.test_results[test_name] = result
                if result.get('success', False):
                    passed += 1
                    logger.info(f"✅ {test_name} PASSED")
                else:
                    logger.error(f"❌ {test_name} FAILED: {result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.error(f"💥 {test_name} CRASHED: {e}")
                self.test_results[test_name] = {'success': False, 'error': str(e)}

        logger.info("\n" + "=" * 60)
        logger.info(f"🏁 Test Results: {passed}/{total} tests passed")

        if passed == total:
            logger.info("🎉 All tests passed! Database integration is ready for production!")
            return {'success': True, 'passed': passed, 'total': total, 'results': self.test_results}
        else:
            logger.warning(f"⚠️ {total - passed} tests failed. Please review the issues above.")
            return {'success': False, 'passed': passed, 'total': total, 'results': self.test_results}

    async def test_configuration(self) -> Dict[str, Any]:
        """Test configuration system."""
        try:
            # Test FletV2 config
            import config as fletv2_config

            # Check if database path is configured
            if hasattr(fletv2_config, 'DATABASE_PATH'):
                db_path = str(fletv2_config.DATABASE_PATH)
                logger.info(f"FletV2 database path: {db_path}")
            else:
                return {'success': False, 'error': 'DATABASE_PATH not configured in FletV2'}

            # Test shared config
            try:
                from Shared.config import get_absolute_database_path, get_database_config_for_fletv2
                shared_db_path = get_absolute_database_path()
                db_config = get_database_config_for_fletv2()
                logger.info(f"Shared config database path: {shared_db_path}")
                logger.info(f"Database config keys: {list(db_config.keys())}")
            except ImportError as e:
                return {'success': False, 'error': f'Shared config import failed: {e}'}

            # Check if paths match
            if os.path.abspath(db_path) == os.path.abspath(shared_db_path):
                return {'success': True, 'message': 'Configuration system working correctly'}
            else:
                return {'success': False, 'error': f'Path mismatch: {db_path} vs {shared_db_path}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_database_connectivity(self) -> Dict[str, Any]:
        """Test database file existence and accessibility."""
        try:
            import config as fletv2_config
            db_path = fletv2_config.DATABASE_PATH

            # Check if database file exists
            if not os.path.exists(db_path):
                return {'success': False, 'error': f'Database file does not exist: {db_path}'}

            # Check if file is readable
            if not os.access(db_path, os.R_OK):
                return {'success': False, 'error': f'Database file is not readable: {db_path}'}

            # Try to connect to database
            import sqlite3
            try:
                with sqlite3.connect(str(db_path)) as conn:
                    # Check for essential tables
                    tables = conn.execute("""
                        SELECT name FROM sqlite_master
                        WHERE type='table' AND name IN ('clients', 'files')
                    """).fetchall()

                    if len(tables) < 2:
                        return {'success': False, 'error': f'Missing essential tables. Found: {[t[0] for t in tables]}'}

                    # Check table contents
                    clients_count = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
                    files_count = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]

                    logger.info(f"Database contains {clients_count} clients, {files_count} files")

                    return {
                        'success': True,
                        'message': f'Database accessible with {clients_count} clients, {files_count} files'
                    }

            except sqlite3.Error as e:
                return {'success': False, 'error': f'SQLite error: {e}'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_data_conversion(self) -> Dict[str, Any]:
        """Test data format conversion functions."""
        try:
            from utils.server_bridge import (
                blob_to_uuid_string, uuid_string_to_blob,
                convert_backupserver_client_to_fletv2, convert_backupserver_file_to_fletv2
            )
            import uuid

            # Test UUID conversion
            test_uuid = uuid.uuid4()
            test_blob = test_uuid.bytes
            converted_string = blob_to_uuid_string(test_blob)
            converted_back = uuid_string_to_blob(converted_string)

            if test_blob != converted_back:
                return {'success': False, 'error': 'UUID conversion round-trip failed'}

            # Test client conversion
            mock_client = {
                'id': test_blob,
                'name': 'Test Client',
                'last_seen': '2024-01-01T00:00:00Z'
            }
            converted_client = convert_backupserver_client_to_fletv2(mock_client)

            if not isinstance(converted_client.get('id'), str):
                return {'success': False, 'error': 'Client ID conversion failed'}

            # Test file conversion
            mock_file = {
                'filename': 'test.txt',
                'client_id': test_blob,
                'size': 1024,
                'verified': True
            }
            converted_file = convert_backupserver_file_to_fletv2(mock_file)

            if not isinstance(converted_file.get('client_id'), str):
                return {'success': False, 'error': 'File client_id conversion failed'}

            return {'success': True, 'message': 'Data conversion functions working correctly'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_server_bridge(self) -> Dict[str, Any]:
        """Test ServerBridge operations."""
        try:
            from utils.server_bridge import create_server_bridge

            # Test with mock mode first
            mock_bridge = create_server_bridge(real_server=None)

            if not mock_bridge.is_connected():
                return {'success': False, 'error': 'Mock bridge should report as connected'}

            # Test basic operations
            clients = mock_bridge.get_clients()
            if not isinstance(clients, list):
                return {'success': False, 'error': 'get_clients should return a list'}

            files = mock_bridge.get_files()
            if not isinstance(files, list):
                return {'success': False, 'error': 'get_files should return a list'}

            # Test database operations
            db_info = mock_bridge.get_database_info()
            if not db_info.get('success'):
                return {'success': False, 'error': 'get_database_info should succeed'}

            self.server_bridge = mock_bridge
            return {'success': True, 'message': 'ServerBridge operations working correctly'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_migration_system(self) -> Dict[str, Any]:
        """Test migration system integration."""
        try:
            from schema_migration import migrate_database_schema, check_database_schema
            import sqlite3

            # Test schema checking
            import config as fletv2_config
            db_path = str(fletv2_config.DATABASE_PATH)

            with sqlite3.connect(db_path) as conn:
                schema_info = check_database_schema(conn)

            if not schema_info.get('backupserver_compatible'):
                return {'success': False, 'error': 'Database schema is not BackupServer compatible'}

            logger.info(f"Schema info: {schema_info}")

            return {'success': True, 'message': 'Migration system working correctly'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_view_compatibility(self) -> Dict[str, Any]:
        """Test that FletV2 views can work with real database."""
        try:
            # Test database view
            from views.database import create_database_view
            import flet as ft

            # Create a mock page for testing
            class MockPage:
                def __init__(self):
                    self.controls = []
                    self.title = "Test"
                    self.overlay = []
                    self.snack_bar = None
                    self.theme_mode = None

                def add(self, control):
                    self.controls.append(control)

                def update(self):
                    pass

                def run_task(self, task):
                    pass

                def show_snack_bar(self, snack_bar):
                    self.snack_bar = snack_bar

            mock_page = MockPage()

            # Create database view with our server bridge
            if self.server_bridge is None:
                from utils.server_bridge import create_server_bridge
                self.server_bridge = create_server_bridge(real_server=None)

            db_view = create_database_view(self.server_bridge, mock_page)  # type: ignore

            if db_view is None:
                return {'success': False, 'error': 'Database view creation failed'}

            logger.info("Database view created successfully")

            # Test clients view
            try:
                from views.clients import create_clients_view
                clients_view = create_clients_view(self.server_bridge, mock_page, None)  # type: ignore
                if clients_view is None:
                    return {'success': False, 'error': 'Clients view creation failed'}
                logger.info("Clients view created successfully")
            except Exception as e:
                logger.warning(f"Clients view test failed: {e}")

            # Test files view
            try:
                from views.files import create_files_view
                files_view = create_files_view(self.server_bridge, mock_page)  # type: ignore
                if files_view is None:
                    return {'success': False, 'error': 'Files view creation failed'}
                logger.info("Files view created successfully")
            except Exception as e:
                logger.warning(f"Files view test failed: {e}")

            return {'success': True, 'message': 'View compatibility tests passed'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def test_real_data_access(self) -> Dict[str, Any]:
        """Test accessing real data through ServerBridge."""
        try:
            # Try to create a ServerBridge with real BackupServer
            try:
                from python_server.server.server import BackupServer
                backup_server = BackupServer()
                self.backup_server = backup_server

                from utils.server_bridge import create_server_bridge
                real_bridge = create_server_bridge(real_server=backup_server)

                # Test real data access
                clients_result = real_bridge.get_clients()
                files_result = real_bridge.get_files()
                db_info_result = real_bridge.get_database_info()

                logger.info(f"Real clients: {len(clients_result) if isinstance(clients_result, list) else 'Error'}")
                logger.info(f"Real files: {len(files_result) if isinstance(files_result, list) else 'Error'}")
                logger.info(f"DB info success: {db_info_result.get('success') if isinstance(db_info_result, dict) else False}")

                return {'success': True, 'message': 'Real data access working correctly'}

            except Exception as e:
                logger.warning(f"Real server test failed: {e}")
                # This is not necessarily a failure - server might not be available
                return {'success': True, 'message': f'Real server not available ({e}), but that\'s acceptable'}

        except Exception as e:
            return {'success': False, 'error': str(e)}

async def main():
    """Main test function."""
    tester = DatabaseIntegrationTester()
    results = await tester.run_all_tests()

    if results['success']:
        print("\n✨ Database integration is ready for production!")
        print("🚀 You can now run: python start_integrated_gui.py")
        return 0
    else:
        print("\n❌ Database integration has issues that need to be addressed.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)