#!/usr/bin/env python3
"""
Test script to verify FletV2 real server integration.

This script tests all aspects of the integration between FletV2 and BackupServer
to ensure real data is properly displayed instead of mock data.
"""

import os
import sys
import logging
import asyncio
from pathlib import Path

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fletv2_root = os.path.join(project_root, 'FletV2')

for path in [project_root, fletv2_root]:
    if path not in sys.path:
        sys.path.insert(0, path)

# ALWAYS import UTF-8 solution first
import Shared.utils.utf8_solution as _

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_server_import():
    """Test importing the real server."""
    try:
        from python_server.server.server import BackupServer
        logger.info("✅ Successfully imported BackupServer")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import BackupServer: {e}")
        return False

def test_server_initialization():
    """Test creating BackupServer instance."""
    try:
        from python_server.server.server import BackupServer

        # Create server instance (uses defaults)
        backup_server = BackupServer()
        logger.info("✅ Successfully created BackupServer instance")

        return backup_server
    except Exception as e:
        logger.error(f"❌ Failed to create BackupServer: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def test_server_methods(backup_server):
    """Test BackupServer methods that FletV2 will use."""
    if not backup_server:
        return False

    success = True

    # Test get_clients
    try:
        clients_result = backup_server.get_clients()
        logger.info(f"get_clients() returned: {type(clients_result)}")

        if isinstance(clients_result, dict):
            if 'success' in clients_result and 'data' in clients_result:
                client_count = len(clients_result.get('data', []))
                logger.info(f"✅ get_clients() - Found {client_count} clients")
            else:
                logger.warning(f"⚠️ get_clients() - Unexpected format: {clients_result}")
        else:
            logger.warning(f"⚠️ get_clients() - Expected dict, got {type(clients_result)}")

    except Exception as e:
        logger.error(f"❌ get_clients() failed: {e}")
        success = False

    # Test get_files
    try:
        files_result = backup_server.get_files()
        logger.info(f"get_files() returned: {type(files_result)}")

        if isinstance(files_result, dict):
            if 'success' in files_result and 'data' in files_result:
                file_count = len(files_result.get('data', []))
                logger.info(f"✅ get_files() - Found {file_count} files")
            else:
                logger.warning(f"⚠️ get_files() - Unexpected format: {files_result}")
        else:
            logger.warning(f"⚠️ get_files() - Expected dict, got {type(files_result)}")

    except Exception as e:
        logger.error(f"❌ get_files() failed: {e}")
        success = False

    # Test get_database_info
    try:
        db_info = backup_server.get_database_info()
        logger.info(f"get_database_info() returned: {type(db_info)}")

        if isinstance(db_info, dict):
            if 'success' in db_info and 'data' in db_info:
                logger.info("✅ get_database_info() - Success")
            else:
                logger.warning(f"⚠️ get_database_info() - Unexpected format: {db_info}")
        else:
            logger.warning(f"⚠️ get_database_info() - Expected dict, got {type(db_info)}")

    except Exception as e:
        logger.error(f"❌ get_database_info() failed: {e}")
        success = False

    return success

def test_server_bridge_integration(backup_server):
    """Test ServerBridge integration with real server."""
    try:
        from utils.server_bridge import ServerBridge

        # Create ServerBridge with real server
        bridge = ServerBridge(real_server=backup_server)
        logger.info("✅ Created ServerBridge with real server")

        # Test that it's not using mock data
        is_mock = getattr(bridge, '_use_mock_data', None)
        if is_mock is not None:
            logger.info(f"ServerBridge _use_mock_data: {is_mock}")
            if not is_mock:
                logger.info("✅ ServerBridge is using real server (not mock data)")
            else:
                logger.error("❌ ServerBridge is still using mock data!")
                return False

        # Test bridge methods
        try:
            clients = bridge.get_clients()
            logger.info(f"✅ ServerBridge.get_clients() returned: {type(clients)}")
        except Exception as e:
            logger.error(f"❌ ServerBridge.get_clients() failed: {e}")
            return False

        return True

    except Exception as e:
        logger.error(f"❌ ServerBridge integration test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_fletv2_import(backup_server):
    """Test that FletV2 can import and initialize with real server."""
    try:
        # Import main FletV2 components
        from main import FletV2App, main
        logger.info("✅ Successfully imported FletV2 components")

        # Test that main function accepts real_server parameter
        import inspect
        sig = inspect.signature(main)
        params = list(sig.parameters.keys())

        if 'real_server' in params:
            logger.info("✅ main() function supports real_server parameter")
        else:
            logger.error("❌ main() function missing real_server parameter")
            return False

        # Test FletV2App initialization parameters
        app_sig = inspect.signature(FletV2App.__init__)
        app_params = list(app_sig.parameters.keys())

        if 'real_server' in app_params:
            logger.info("✅ FletV2App supports real_server parameter")
        else:
            logger.error("❌ FletV2App missing real_server parameter")
            return False

        logger.info("✅ FletV2 integration test passed")
        return True

    except Exception as e:
        logger.error(f"❌ FletV2 integration test failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_integration_script():
    """Test the integration script."""
    try:
        from run_with_real_server import initialize_real_server, launch_fletv2_with_server
        logger.info("✅ Successfully imported integration script functions")

        # Test server initialization via integration script
        server = initialize_real_server()
        if server:
            logger.info("✅ Integration script can initialize real server")
            return True
        else:
            logger.warning("⚠️ Integration script failed to initialize server")
            return False

    except Exception as e:
        logger.error(f"❌ Integration script test failed: {e}")
        return False

def run_all_tests():
    """Run all integration tests."""
    logger.info("🧪 Starting FletV2 Real Server Integration Tests")
    logger.info("=" * 60)

    tests_passed = 0
    total_tests = 6

    # Test 1: Server import
    if test_server_import():
        tests_passed += 1

    # Test 2: Server initialization
    backup_server = test_server_initialization()
    if backup_server:
        tests_passed += 1

        # Test 3: Server methods
        if test_server_methods(backup_server):
            tests_passed += 1

        # Test 4: ServerBridge integration
        if test_server_bridge_integration(backup_server):
            tests_passed += 1

        # Test 5: FletV2 import/integration
        if test_fletv2_import(backup_server):
            tests_passed += 1
    else:
        logger.error("❌ Skipping dependent tests due to server initialization failure")

    # Test 6: Integration script
    if test_integration_script():
        tests_passed += 1

    logger.info("=" * 60)
    logger.info(f"🎯 Test Results: {tests_passed}/{total_tests} passed")

    if tests_passed == total_tests:
        logger.info("🎉 All tests passed! FletV2 real server integration is working correctly.")
        return True
    else:
        logger.error(f"💥 {total_tests - tests_passed} test(s) failed. Integration needs fixes.")
        return False

def main():
    """Main test function."""
    success = run_all_tests()

    if success:
        logger.info("\n🚀 Integration is ready! You can now:")
        logger.info("   1. Run FletV2 standalone: python main.py")
        logger.info("   2. Use integration script: python run_with_real_server.py")
        logger.info("   3. Import and use: from run_with_real_server import launch_fletv2_with_server")
        return 0
    else:
        logger.error("\n💥 Integration has issues. Please fix the failing tests.")
        return 1

if __name__ == "__main__":
    sys.exit(main())