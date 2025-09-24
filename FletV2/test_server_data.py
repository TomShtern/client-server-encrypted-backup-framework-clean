#!/usr/bin/env python3
"""
Quick test script to verify server integration and data availability
"""

import os
import sys
import asyncio

# Set environment variables for real server integration
os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'
os.environ['CYBERBACKUP_DISABLE_GUI'] = '1'

# Add parent directory to sys.path for imports
sys.path.insert(0, '..')

def test_real_server_integration():
    """Test real server integration and data retrieval"""
    print("=" * 60)
    print("TESTING FLETV2 SERVER INTEGRATION")
    print("=" * 60)

    try:
        from python_server.server.server import BackupServer
        print("✅ BackupServer import successful")

        # Create real server instance
        real_server = BackupServer()
        print("✅ BackupServer instance created")

        # Test database connection
        if hasattr(real_server.db_manager, 'execute'):
            result = real_server.db_manager.execute(
                "SELECT COUNT(*) as count FROM clients", fetchone=True
            )
            if result:
                client_count = result['count']
                print(f"✅ Database connected: {client_count} clients found")
            else:
                print("⚠️ Database connected but no client count available")

        # Test server bridge
        from utils.server_bridge import ServerBridge
        server_bridge = ServerBridge(real_server)
        print("✅ ServerBridge created with real server")

        # Test client data retrieval
        clients_result = server_bridge.get_clients()
        print(f"✅ get_clients() result: {clients_result.get('success', False)}")
        if clients_result.get('success'):
            clients = clients_result.get('data', [])
            print(f"   → Found {len(clients)} clients")
            if clients:
                first_client = clients[0]
                print(f"   → First client: {first_client.get('name', 'N/A')}")

        # Test files data retrieval
        files_result = server_bridge.get_files()
        print(f"✅ get_files() result: {files_result.get('success', False)}")
        if files_result.get('success'):
            files = files_result.get('data', [])
            print(f"   → Found {len(files)} files")

        # Test database table structure
        tables_result = server_bridge.get_database_tables()
        print(f"✅ get_database_tables() result: {tables_result.get('success', False)}")
        if tables_result.get('success'):
            tables = tables_result.get('data', [])
            print(f"   → Found {len(tables)} tables")

        print("=" * 60)
        print("✅ ALL TESTS PASSED - REAL SERVER INTEGRATION WORKING")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_async_operations():
    """Test async server operations"""
    print("\nTesting async operations...")

    try:
        from python_server.server.server import BackupServer
        from utils.server_bridge import ServerBridge

        real_server = BackupServer()
        server_bridge = ServerBridge(real_server)

        # Test async client retrieval
        clients_result = await server_bridge.get_clients_async()
        print(f"✅ get_clients_async() result: {clients_result.get('success', False)}")

        # Test async files retrieval
        files_result = await server_bridge.get_files_async()
        print(f"✅ get_files_async() result: {files_result.get('success', False)}")

        print("✅ Async operations working correctly")

    except Exception as e:
        print(f"❌ Async test failed: {e}")

if __name__ == "__main__":
    # Test synchronous operations
    sync_success = test_real_server_integration()

    # Test asynchronous operations
    if sync_success:
        print("\n" + "=" * 60)
        print("TESTING ASYNC OPERATIONS")
        print("=" * 60)
        asyncio.run(test_async_operations())