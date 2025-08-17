#!/usr/bin/env python3
"""
Test script to verify GUI integration fixes
"""

import sys
import os
import time

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from python_server.server_gui.ServerGUI import ServerGUI
    
    print("Testing ServerGUI integration methods...")
    
    # Create a minimal server-like object for testing
    class MockServer:
        def __init__(self):
            self.running = True
            self.host = "127.0.0.1"
            self.port = 1256
            # Add required attributes for BackupServerLike protocol
            self.clients = {}  # Dict[bytes, Any]
            self.clients_by_name = {}  # Dict[str, bytes]
            self.network_server = None
            self.file_transfer_manager = None
            self.db_manager = self.MockDBManager()
            
        class MockDBManager:
            def get_all_clients(self):
                return [f"client_{i}" for i in range(5)]  # Mock 5 clients
        
        def start(self) -> None:
            """Mock start method"""
            self.running = True
            
        def stop(self) -> None:
            """Mock stop method"""
            self.running = False
            
        def apply_settings(self, settings) -> None:
            """Mock apply_settings method"""
            pass
    
    # Create GUI instance with mock server
    mock_server = MockServer()
    gui = ServerGUI(mock_server)
    
    print("✅ ServerGUI imported and instantiated successfully")
    
    # Test the update methods directly
    print("\n🔍 Testing update_server_status...")
    gui.update_server_status(True, "127.0.0.1", 1256)
    
    print("🔍 Testing update_client_stats...")
    gui.update_client_stats({
        'connected': 3,
        'total': 5,
        'active_transfers': 1
    })
    
    print("🔍 Testing update_transfer_stats...")
    gui.update_transfer_stats({
        'bytes_transferred': 1024000,
        'rate_kbps': 150.5,
        'last_activity': 'test_file.txt'
    })
    
    print("🔍 Testing sync_current_server_state...")
    gui.sync_current_server_state()
    
    print("\n✅ All integration methods executed without errors!")
    print("✅ GUI integration fixes are working correctly")
    
except Exception as e:
    print(f"❌ Error testing GUI integration: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 GUI integration test completed successfully!")
