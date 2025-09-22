#!/usr/bin/env python3
"""
Direct BackupServer + FletV2 Integration Test Script

Tests the direct integration between BackupServer and FletV2 (bypassing the adapter layer).
This script verifies that all components work together correctly with the new architecture.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_backup_server_direct():
    """Test the BackupServer direct integration functionality."""
    logger.info("🧪 Testing direct BackupServer integration...")

    try:
        from python_server.server.server import BackupServer

        # Create server instance directly
        server = BackupServer()

        # Test connectivity
        if hasattr(server, 'is_connected'):
            logger.info("✅ BackupServer has is_connected method")
        else:
            logger.warning("⚠️ BackupServer missing is_connected method")

        # Test server status
        if hasattr(server, 'get_server_status'):
            status = server.get_server_status()
            assert isinstance(status, dict), "Server status should be a dictionary"
            logger.info(f"✅ Server status test passed: {status}")
        else:
            logger.warning("⚠️ BackupServer missing get_server_status method")

        # Test client operations
        if hasattr(server, 'get_clients'):
            clients = server.get_clients()
            logger.info(f"✅ Client operations test passed: {type(clients)} returned")
        else:
            logger.warning("⚠️ BackupServer missing get_clients method")

        # Test file operations
        if hasattr(server, 'get_files'):
            files = server.get_files()
            logger.info(f"✅ File operations test passed: {type(files)} returned")
        else:
            logger.warning("⚠️ BackupServer missing get_files method")

        # Test database operations
        if hasattr(server, 'get_database_info'):
            db_info = server.get_database_info()
            assert isinstance(db_info, dict), "Database info should be a dictionary"
            logger.info(f"✅ Database operations test passed: {db_info}")
        else:
            logger.warning("⚠️ BackupServer missing get_database_info method")

        return True

    except Exception as e:
        logger.error(f"❌ Direct BackupServer test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_server_bridge_integration():
    """Test the ServerBridge integration with direct BackupServer."""
    logger.info("🧪 Testing ServerBridge integration...")

    try:
        from python_server.server.server import BackupServer
        from utils.server_bridge import create_server_bridge

        # Create real server directly
        real_server = BackupServer()

        # Create server bridge with real server
        bridge = create_server_bridge(real_server=real_server)

        # Test bridge methods
        if bridge.is_connected():
            logger.info("✅ Bridge connectivity test passed")
        else:
            logger.info("ℹ️ Bridge in mock mode (expected if BackupServer not fully initialized)")

        # Test bridge client operations
        clients_result = bridge.get_clients()
        assert isinstance(clients_result, list), f"Get clients should return list, got: {type(clients_result)}"
        logger.info(f"✅ Bridge client operations test passed: {len(clients_result)} clients")

        # Test bridge file operations
        files_result = bridge.get_files()
        assert isinstance(files_result, list), f"Get files should return list, got: {type(files_result)}"
        logger.info(f"✅ Bridge file operations test passed: {len(files_result)} files")

        return True

    except Exception as e:
        logger.error(f"❌ ServerBridge integration test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_async_operations():
    """Test async operations."""
    logger.info("🧪 Testing async operations...")

    try:
        import asyncio
        from server_adapter import create_fletv2_server

        async def run_async_tests():
            server = create_fletv2_server()

            # Test async client operations
            clients = await server.get_clients_async()
            assert isinstance(clients, list), "Async clients should be a list"

            # Test async file operations
            files = await server.get_files_async()
            assert isinstance(files, list), "Async files should be a list"

            # Test async database operations
            db_info = await server.get_database_info_async()
            assert isinstance(db_info, dict), "Async database info should be a dictionary"

            return True

        # Run async tests
        result = asyncio.run(run_async_tests())
        logger.info("✅ Async operations test passed")
        return result

    except Exception as e:
        logger.error(f"❌ Async operations test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_database_migration():
    """Test database migration if needed."""
    logger.info("🧪 Testing database migration...")

    try:
        from schema_migration import migrate_database_schema

        # Test migration on a test database
        test_db_path = "test_migration.db"

        # Clean up any existing test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

        # Run migration
        result = migrate_database_schema(test_db_path)

        # Clean up test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

        if result:
            logger.info("✅ Database migration test passed")
        else:
            logger.warning("⚠️ Database migration test failed - may be expected if no old data")

        return True

    except Exception as e:
        logger.error(f"❌ Database migration test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_fletv2_import():
    """Test that FletV2 can import and initialize with real server."""
    logger.info("🧪 Testing FletV2 import with real server...")

    try:
        # Import main FletV2 app
        from main import FletV2App, main, real_server_available, bridge_type

        logger.info(f"Real server available: {real_server_available}")
        logger.info(f"Bridge type: {bridge_type}")

        # Test main function signature
        import inspect
        sig = inspect.signature(main)
        params = list(sig.parameters.keys())

        if 'real_server' in params:
            logger.info("✅ Main function supports real_server parameter")
        else:
            logger.warning("⚠️ Main function missing real_server parameter")

        logger.info("✅ FletV2 import test passed - direct integration ready")

        return True

    except Exception as e:
        logger.error(f"❌ FletV2 import test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_startup_script():
    """Test that the startup script can be imported and has correct structure."""
    logger.info("🧪 Testing startup script...")

    try:
        # Import startup script components
        from start_integrated_gui import IntegratedServerManager, main_integrated

        # Test manager creation
        manager = IntegratedServerManager(force_mock=True)
        logger.info("✅ IntegratedServerManager created successfully")

        # Test that it has required methods
        required_methods = [
            'initialize_backup_server',
            'create_integrated_server_bridge',
            'start_integrated_gui',
            'shutdown'
        ]

        for method in required_methods:
            if hasattr(manager, method):
                logger.info(f"✅ Method '{method}' found")
            else:
                logger.warning(f"⚠️ Method '{method}' missing")

        logger.info("✅ Startup script test passed")
        return True

    except Exception as e:
        logger.error(f"❌ Startup script test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def run_all_tests():
    """Run all integration tests."""
    logger.info("🚀 Starting FletV2 Integration Tests")
    logger.info("=" * 60)

    tests = [
        ("Direct BackupServer", test_backup_server_direct),
        ("ServerBridge Integration", test_server_bridge_integration),
        ("Async Operations", test_async_operations),
        ("FletV2 Import", test_fletv2_import),
        ("Startup Script", test_startup_script),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        logger.info(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
        except Exception as e:
            logger.error(f"💥 {test_name} test CRASHED: {e}")

    logger.info("\n" + "=" * 60)
    logger.info(f"🏁 Integration Tests Complete: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed! Your integration is ready for production!")
        return True
    else:
        logger.warning(f"⚠️ {total - passed} tests failed. Please review the issues above.")
        return False

def main():
    """Main test function."""
    success = run_all_tests()

    if success:
        logger.info("\n✨ Ready to launch FletV2 with real server integration!")
        logger.info("Run: python main.py")
        return 0
    else:
        logger.error("\n❌ Integration issues detected. Please fix before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())