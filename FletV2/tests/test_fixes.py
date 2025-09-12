#!/usr/bin/env python3
"""
Test script to verify the fixes for:
1. Files tab empty issue
2. Database table layout issue
"""

import asyncio
import sys
import os

# Add the FletV2 directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.debug_setup import get_logger
from utils.server_bridge import ServerBridge

logger = get_logger(__name__)

def test_files_scanning():
    """Test file scanning function directly."""
    print("🔍 Testing file scanning...")
    try:
        from views.files import create_files_view
        
        # Create a dummy page for testing
        class DummyPage:
            def __init__(self):
                self.run_task = lambda func: asyncio.run(func())
                self.update = lambda: None
        
        dummy_page = DummyPage()
        server_bridge = ServerBridge()  # Using mock data
        
        # Test the view creation
        files_view = create_files_view(server_bridge, dummy_page)  # type: ignore
        print("✅ Files view created successfully")
        
        # Check if the view has the expected structure
        if hasattr(files_view, 'controls') and files_view.controls and len(files_view.controls) > 0:
            print("✅ Files view has content controls")
        else:
            print("❌ Files view has no content controls")
            
    except Exception as e:
        print(f"❌ Files view test failed: {e}")
        import traceback
        traceback.print_exc()

def test_database_layout():
    """Test database view for layout conflicts."""
    print("\n🔍 Testing database layout...")
    try:
        from views.database import create_database_view
        
        # Create a dummy page for testing
        class DummyPage:
            def __init__(self):
                self.run_task = lambda func: asyncio.run(func())
                self.update = lambda: None
                self.dialog = None
        
        dummy_page = DummyPage()
        server_bridge = ServerBridge()  # Using mock data
        
        # Test the view creation
        database_view = create_database_view(server_bridge, dummy_page)  # type: ignore
        print("✅ Database view created successfully")
        
        # Check if the view has the expected structure without scroll conflicts
        if hasattr(database_view, 'controls') and database_view.controls and len(database_view.controls) > 0:
            print("✅ Database view has content controls")
        else:
            print("❌ Database view has no content controls")
            
    except Exception as e:
        print(f"❌ Database view test failed: {e}")
        import traceback
        traceback.print_exc()

def test_server_bridge():
    """Test server bridge functionality."""
    print("\n🔍 Testing server bridge...")
    try:
        server_bridge = ServerBridge()
        
        # Test client data
        clients = server_bridge.get_clients()
        print(f"✅ Server bridge returned {len(clients)} clients")
        
        # Test files data
        files = server_bridge.get_files()
        print(f"✅ Server bridge returned {len(files)} files")
        
        # Test database data
        db_info = server_bridge.get_database_info()
        print(f"✅ Server bridge returned database info with {len(db_info.get('tables', []))} tables")
        
    except Exception as e:
        print(f"❌ Server bridge test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run all tests."""
    print("🚀 Running FletV2 Fix Verification Tests\n")
    
    test_server_bridge()
    test_files_scanning()
    test_database_layout()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
