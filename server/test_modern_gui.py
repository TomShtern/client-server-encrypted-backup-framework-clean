#!/usr/bin/env python3
"""
Test script for the ULTRA MODERN ServerGUI
Tests the new modern interface with dark theme and animations
"""

import time
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_modern_gui():
    """Test the ultra modern GUI functionality"""
    print("🚀 Testing ULTRA MODERN Server GUI...")
    
    try:
        # Import the modern GUI
        from ServerGUI import (
            initialize_server_gui, shutdown_server_gui, update_server_status,
            update_client_stats, update_transfer_stats, update_maintenance_stats,
            show_server_error, show_server_success, show_server_notification
        )
        
        # Test 1: Initialize modern GUI
        print("1. 🎨 Testing modern GUI initialization...")
        if not initialize_server_gui():
            print("❌ Modern GUI initialization failed!")
            return False
        print("✅ Ultra modern GUI initialized successfully!")
        
        # Wait for GUI to fully load
        time.sleep(2)
        
        # Test 2: Server status updates with modern styling
        print("2. 🖥️ Testing modern server status updates...")
        update_server_status(True, "127.0.0.1", 8080)
        time.sleep(1)
        print("✅ Modern server status updated")
        
        # Test 3: Client statistics with progress bars
        print("3. 👥 Testing modern client statistics...")
        update_client_stats(connected=5, total=15, active_transfers=3)
        time.sleep(1)
        print("✅ Modern client stats updated")
        
        # Test 4: Transfer statistics with animations
        print("4. 📊 Testing modern transfer statistics...")
        update_transfer_stats(bytes_transferred=1024*1024*250, last_activity="2025-06-04 22:30:00")
        time.sleep(1)
        print("✅ Modern transfer stats updated")
        
        # Test 5: Maintenance statistics
        print("5. ⚙️ Testing modern maintenance statistics...")
        update_maintenance_stats({
            'files_cleaned': 12,
            'partial_files_cleaned': 5,
            'clients_cleaned': 2,
            'last_cleanup': "2025-06-04 22:25:00"
        })
        time.sleep(1)
        print("✅ Modern maintenance stats updated")
        
        # Test 6: Modern error messages
        print("6. ❌ Testing modern error display...")
        show_server_error("Test error message with modern styling")
        time.sleep(2)
        print("✅ Modern error displayed")
        
        # Test 7: Modern success messages
        print("7. ✅ Testing modern success display...")
        show_server_success("Test success message with modern styling")
        time.sleep(2)
        print("✅ Modern success displayed")
        
        # Test 8: Modern notifications
        print("8. 🔔 Testing modern notifications...")
        show_server_notification("Modern Test", "This is a modern notification with sophisticated styling!")
        time.sleep(2)
        print("✅ Modern notification displayed")
        
        # Test 9: Rapid updates with animations
        print("9. ⚡ Testing rapid modern updates...")
        for i in range(8):
            update_client_stats(connected=i+1)
            update_transfer_stats(bytes_transferred=(i+1)*1024*1024*10)
            time.sleep(0.3)
        print("✅ Rapid modern updates handled")
        
        # Test 10: Server stop with modern styling
        print("10. 🛑 Testing modern server stop status...")
        update_server_status(False)
        time.sleep(1)
        print("✅ Modern server stop status updated")
        
        print("\n🎉 ALL ULTRA MODERN GUI TESTS COMPLETED SUCCESSFULLY!")
        print("🎨 The modern GUI should be visible with:")
        print("   • Dark theme with sophisticated colors")
        print("   • Card-based layout with modern styling")
        print("   • Animated progress bars and status indicators")
        print("   • Modern typography and spacing")
        print("   • Interactive hover effects on buttons")
        print("   • Real-time status updates with smooth animations")
        print("\n💡 You can interact with the modern GUI window to test all features.")
        print("🔧 Use the modern control buttons to test advanced functionality.")
        print("⌨️ Press Ctrl+C to exit the modern GUI test...")
        
        return True
        
    except Exception as e:
        print(f"❌ Modern GUI test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function for ultra modern GUI"""
    try:
        if test_modern_gui():
            # Keep the modern GUI running for manual testing
            try:
                print("\n🎨 Modern GUI is now running...")
                print("🖱️ Try clicking the modern buttons and interacting with the interface!")
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Shutting down ultra modern GUI test...")
        
    except Exception as e:
        print(f"❌ Modern GUI test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("🧹 Cleaning up modern GUI...")
        try:
            from ServerGUI import shutdown_server_gui
            shutdown_server_gui()
        except:
            pass
        print("✅ Modern GUI test completed.")

if __name__ == "__main__":
    main()
