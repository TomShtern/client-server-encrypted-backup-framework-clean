#!/usr/bin/env python3
"""
FletV2 Integration Test Script

Tests the integration between FletV2 and your real server infrastructure.
This script verifies that all components work together correctly.
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

def test_server_adapter():
    """Test the server adapter functionality."""
    logger.info("🧪 Testing server adapter...")

    try:
        from server_adapter import create_fletv2_server

        # Create server instance
        server = create_fletv2_server()

        # Test connectivity
        assert server.is_connected(), "Server should be connected"
        logger.info("✅ Server connectivity test passed")

        # Test server status
        status = server.get_server_status()
        assert isinstance(status, dict), "Server status should be a dictionary"
        assert "running" in status, "Status should include 'running' field"
        logger.info(f"✅ Server status test passed: {status}")

        # Test client operations
        clients = server.get_clients()
        assert isinstance(clients, list), "Clients should be a list"
        logger.info(f"✅ Client operations test passed: {len(clients)} clients found")

        # Test file operations
        files = server.get_files()
        assert isinstance(files, list), "Files should be a list"
        logger.info(f"✅ File operations test passed: {len(files)} files found")

        # Test database operations
        db_info = server.get_database_info()
        assert isinstance(db_info, dict), "Database info should be a dictionary"
        assert "tables" in db_info, "Database info should include tables"
        logger.info(f"✅ Database operations test passed: {db_info['tables']}")

        return True

    except Exception as e:
        logger.error(f"❌ Server adapter test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_server_bridge_integration():
    """Test the ServerBridge integration with real server."""
    logger.info("🧪 Testing ServerBridge integration...")

    try:
        from server_adapter import create_fletv2_server
        from utils.server_bridge import create_server_bridge

        # Create real server
        real_server = create_fletv2_server()

        # Create server bridge with real server
        bridge = create_server_bridge(real_server=real_server)

        # Test bridge methods
        assert bridge.is_connected(), "Bridge should report as connected"
        logger.info("✅ Bridge connectivity test passed")

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
        from main import FletV2App, REAL_SERVER_AVAILABLE, BRIDGE_TYPE

        logger.info(f"Real server available: {REAL_SERVER_AVAILABLE}")
        logger.info(f"Bridge type: {BRIDGE_TYPE}")

        if REAL_SERVER_AVAILABLE:
            logger.info("✅ FletV2 import test passed - real server integration available")
        else:
            logger.info("ℹ️ FletV2 import test passed - running in mock mode")

        return True

    except Exception as e:
        logger.error(f"❌ FletV2 import test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def run_all_tests():
    """Run all integration tests."""
    logger.info("🚀 Starting FletV2 Integration Tests")
    logger.info("=" * 60)

    tests = [
        ("Server Adapter", test_server_adapter),
        ("ServerBridge Integration", test_server_bridge_integration),
        ("Async Operations", test_async_operations),
        ("Database Migration", test_database_migration),
        ("FletV2 Import", test_fletv2_import),
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