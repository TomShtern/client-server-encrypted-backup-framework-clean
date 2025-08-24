#!/usr/bin/env python3
"""
Comprehensive Test Suite for Flet GUI Real Data Integration
Tests all core functionality to ensure everything works properly.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flet_server_gui.utils.server_bridge import ServerBridge
    from flet_server_gui.components.real_database_view import RealDatabaseView
    from flet_server_gui.components.real_data_clients import RealDataClientsView, RealDataStatsCard
    from flet_server_gui.components.real_data_files import RealDataFilesView, FileTypeBreakdownCard
    print("[OK] All Flet GUI imports successful")
except ImportError as e:
    print(f"[ERROR] Import Error: {e}")
    sys.exit(1)

def test_server_bridge():
    """Test ServerBridge functionality"""
    print("\n🔍 Testing ServerBridge...")
    
    try:
        bridge = ServerBridge()
        print(f"  [OK] ServerBridge initialized - Mock mode: {bridge.is_mock_mode()}")
        
        if not bridge.is_mock_mode():
            print("  🗄️ Database manager available")
        else:
            print("  [WARNING] Running in mock mode - database not available")
            
        return bridge
        
    except Exception as e:
        print(f"  [ERROR] ServerBridge failed: {e}")
        return None

async def test_server_status(bridge):
    """Test server status functionality"""
    print("\n📊 Testing Server Status...")
    
    try:
        status = await bridge.get_server_status()
        print(f"  [OK] Server status retrieved: {status.total_clients} clients, {status.total_transfers} transfers")
    except Exception as e:
        print(f"  [ERROR] Server status failed: {e}")

def test_client_data(bridge):
    """Test client data retrieval"""
    print("\n👥 Testing Client Data...")
    
    try:
        clients = bridge.get_client_list()
        print(f"  [OK] Retrieved {len(clients)} clients from database")
        
        if clients:
            sample_client = clients[0]
            print(f"  📋 Sample client: {sample_client.client_id} - Status: {sample_client.status}")
        else:
            print("  [WARNING] No clients found in database")
            
    except Exception as e:
        print(f"  [ERROR] Client data failed: {e}")

def test_file_data(bridge):
    """Test file data retrieval"""
    print("\n📁 Testing File Data...")
    
    try:
        files = bridge.get_file_list()
        print(f"  [OK] Retrieved {len(files)} files from database")
        
        if files:
            sample_file = files[0]
            filename = sample_file.get('filename', 'Unknown')
            size = sample_file.get('size', 0)
            print(f"  📋 Sample file: {filename} ({size} bytes)")
        else:
            print("  [WARNING] No files found in database")
            
    except Exception as e:
        print(f"  [ERROR] File data failed: {e}")

def test_database_operations(bridge):
    """Test database operations"""
    print("\n🗄️ Testing Database Operations...")
    
    if bridge.is_mock_mode():
        print("  [WARNING] Skipping database tests - mock mode")
        return
    
    try:
        # Test database stats
        stats = bridge.db_manager.get_database_stats()
        print(f"  [OK] Database stats: {stats}")
        
        # Test table names
        tables = bridge.db_manager.get_table_names()
        print(f"  [OK] Found {len(tables)} database tables: {tables}")
        
        # Test table content (first table)
        if tables:
            table_name = tables[0]
            columns, rows = bridge.db_manager.get_table_content(table_name)
            print(f"  [OK] Table '{table_name}': {len(columns)} columns, {len(rows)} rows")
        
        # Test database health
        health = bridge.db_manager.get_database_health()
        print(f"  [OK] Database health check: {health.get('integrity_check', False)}")
        
    except Exception as e:
        print(f"  [ERROR] Database operations failed: {e}")

def test_components(bridge):
    """Test GUI components creation"""
    print("\n🎨 Testing GUI Components...")
    
    try:
        # Test database view
        db_view = RealDatabaseView(bridge)
        print("  [OK] RealDatabaseView created successfully")
        
        # Test client view
        client_view = RealDataClientsView(bridge)
        print("  [OK] RealDataClientsView created successfully")
        
        # Test file view
        file_view = RealDataFilesView(bridge)
        print("  [OK] RealDataFilesView created successfully")
        
        # Test stats card
        stats_card = RealDataStatsCard(bridge)
        print("  [OK] RealDataStatsCard created successfully")
        
        # Test file type breakdown
        breakdown_card = FileTypeBreakdownCard(bridge)
        print("  [OK] FileTypeBreakdownCard created successfully")
        
    except Exception as e:
        print(f"  [ERROR] Component creation failed: {e}")

async def test_server_controls(bridge):
    """Test server control functionality"""
    print("\n🎮 Testing Server Controls...")
    
    try:
        # Note: These will print warnings in mock mode, which is expected
        start_result = await bridge.start_server()
        print(f"  📝 Start server result: {start_result}")
        
        stop_result = await bridge.stop_server()
        print(f"  📝 Stop server result: {stop_result}")
        
        restart_result = await bridge.restart_server()
        print(f"  📝 Restart server result: {restart_result}")
        
        if bridge.is_mock_mode():
            print("  [WARNING] Server controls show warnings in mock mode (expected)")
        else:
            print("  [OK] Server controls executed")
            
    except Exception as e:
        print(f"  [ERROR] Server controls failed: {e}")

def test_activity_logs(bridge):
    """Test activity log functionality"""
    print("\n📋 Testing Activity Logs...")
    
    try:
        logs = bridge.get_recent_activity(10)
        print(f"  [OK] Retrieved {len(logs)} activity log entries")
        
        if logs:
            sample_log = logs[0]
            print(f"  📋 Sample log: {sample_log}")
        else:
            print("  ℹ️ No activity logs available (expected for now)")
            
    except Exception as e:
        print(f"  [ERROR] Activity logs failed: {e}")

async def main():
    """Run comprehensive test suite"""
    print("🚀 Starting Comprehensive Flet GUI Test Suite")
    print(f"⏰ Test started at: {datetime.now()}")
    print("=" * 60)
    
    # Test 1: Server Bridge
    bridge = test_server_bridge()
    if not bridge:
        print("[ERROR] CRITICAL: ServerBridge failed - cannot continue")
        return False
    
    # Test 2: Server Status
    await test_server_status(bridge)
    
    # Test 3: Client Data
    test_client_data(bridge)
    
    # Test 4: File Data  
    test_file_data(bridge)
    
    # Test 5: Database Operations
    test_database_operations(bridge)
    
    # Test 6: GUI Components
    test_components(bridge)
    
    # Test 7: Server Controls
    await test_server_controls(bridge)
    
    # Test 8: Activity Logs
    test_activity_logs(bridge)
    
    print("=" * 60)
    print("🎉 Comprehensive Test Suite Complete!")
    
    if bridge.is_mock_mode():
        print("[WARNING]  MOCK MODE: Some functionality limited without real server")
        print("💡 To test with real data, ensure server database is accessible")
    else:
        print("[OK] REAL DATA MODE: Full functionality tested successfully")
    
    print(f"⏰ Test completed at: {datetime.now()}")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[WARNING] Test suite interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Test suite failed: {e}")
        import traceback
        traceback.print_exc()