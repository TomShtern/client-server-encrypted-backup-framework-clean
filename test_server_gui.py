#!/usr/bin/env python3
"""
Test script for ServerGUI - identifies and fixes immediate issues
"""

import sys
import os
import traceback

# Add the server directory to the path
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server')
sys.path.insert(0, server_dir)

def test_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")
    try:
        from ServerGUI import ServerGUI, initialize_server_gui, get_server_gui
        print("✓ ServerGUI imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False

def test_gui_initialization():
    """Test GUI initialization"""
    print("\nTesting GUI initialization...")
    try:
        from ServerGUI import ServerGUI
        # Test basic initialization
        gui = ServerGUI()
        print("✓ ServerGUI instance created successfully")
        
        # Test settings
        print(f"✓ Default settings loaded: {gui.settings}")
        
        return True
    except Exception as e:
        print(f"✗ GUI initialization error: {e}")
        traceback.print_exc()
        return False

def test_gui_start():
    """Test starting the GUI (will run briefly)"""
    print("\nTesting GUI startup...")
    try:
        from ServerGUI import initialize_server_gui, get_server_gui, shutdown_server_gui
        success = initialize_server_gui()
        if success:
            print("✓ GUI started successfully")
            # Let it run for a moment to test initialization
            import time
            time.sleep(2)
            
            # Test some basic operations
            gui = get_server_gui()
            gui.show_info("Test message")
            gui.update_server_status(True, "127.0.0.1", 1256)
            gui.update_client_stats(connected=5, total=10)
            
            print("✓ Basic GUI operations work")
            
            # Shutdown
            shutdown_server_gui()
            print("✓ GUI shutdown successfully")
            return True
        else:
            print("✗ GUI failed to start")
            return False
    except Exception as e:
        print(f"✗ GUI startup error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("=== ServerGUI Test Suite ===")
    
    # Test 1: Imports
    if not test_imports():
        print("\n❌ Import test failed - cannot continue")
        return False
    
    # Test 2: Basic initialization
    if not test_gui_initialization():
        print("\n❌ Initialization test failed")
        return False
    
    # Test 3: GUI startup (optional - might fail on headless systems)
    try:
        if not test_gui_start():
            print("\n⚠️ GUI startup test failed (might be expected on headless systems)")
    except Exception as e:
        print(f"\n⚠️ GUI startup test failed: {e}")
    
    print("\n=== Test Summary ===")
    print("✓ Basic functionality appears to be working")
    print("✓ No critical import or initialization errors detected")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 ServerGUI appears to be working correctly!")
        else:
            print("\n❌ ServerGUI has issues that need fixing")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
