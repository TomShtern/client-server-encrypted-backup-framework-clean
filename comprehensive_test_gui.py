#!/usr/bin/env python3
"""
Comprehensive test script for ServerGUI - tests all functionality
"""

import sys
import os
import time
import threading
import traceback

# Add the server directory to the path
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server')
sys.path.insert(0, server_dir)

def test_widget_creation():
    """Test custom widget creation"""
    print("Testing custom widget creation...")
    try:
        from server.ServerGUI import ModernCard, ModernProgressBar, ModernStatusIndicator
        import tkinter as tk
        
        # Create a test root
        root = tk.Tk()
        root.withdraw()  # Hide the test window
        
        # Test ModernCard
        card = ModernCard(root, title="Test Card")
        print("✓ ModernCard created successfully")
        
        # Test ModernProgressBar
        progress = ModernProgressBar(root)
        progress.set_progress(50)
        print("✓ ModernProgressBar created and set to 50%")
        
        # Test ModernStatusIndicator
        status = ModernStatusIndicator(root)
        status.set_status("online")
        print("✓ ModernStatusIndicator created and set to online")
        
        root.destroy()
        return True
        
    except Exception as e:
        print(f"✗ Widget creation error: {e}")
        traceback.print_exc()
        return False

def test_gui_operations():
    """Test GUI operations without displaying window"""
    print("\nTesting GUI operations...")
    try:
        from server.ServerGUI import ServerGUI
        
        gui = ServerGUI()
        
        # Test status updates
        gui.update_server_status(True, "127.0.0.1", 1256)
        gui.update_client_stats(connected=5, total=10, active_transfers=2)
        gui.update_transfer_stats(bytes_transferred=1024*1024, last_activity="2025-06-15 10:30:00")
        
        # Test maintenance stats
        gui.update_maintenance_stats({
            'files_cleaned': 5,
            'partial_files_cleaned': 2,
            'clients_cleaned': 1,
            'last_cleanup': '2025-06-15 10:00:00'
        })
        
        # Test messages
        gui.show_error("Test error message")
        gui.show_success("Test success message")
        gui.show_info("Test info message")
        
        print("✓ All GUI operations completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ GUI operations error: {e}")
        traceback.print_exc()
        return False

def test_gui_with_display():
    """Test GUI with actual display (brief)"""
    print("\nTesting GUI with display...")
    try:
        from server.ServerGUI import initialize_server_gui, get_server_gui, shutdown_server_gui
        
        # Initialize GUI
        success = initialize_server_gui()
        if not success:
            print("✗ GUI initialization failed")
            return False
        
        print("✓ GUI initialized successfully")
        
        # Get GUI instance
        gui = get_server_gui()
        
        # Test updates
        gui.update_server_status(True, "127.0.0.1", 1256)
        print("✓ Server status updated")
        
        gui.update_client_stats(connected=3, total=5, active_transfers=1)
        print("✓ Client stats updated")
        
        gui.update_transfer_stats(bytes_transferred=2048, last_activity="Just now")
        print("✓ Transfer stats updated")
        
        # Test notifications
        gui.show_info("Test notification - GUI is working!")
        print("✓ Notification shown")
        
        # Let it run briefly
        time.sleep(2)
        
        # Test shutdown
        shutdown_server_gui()
        print("✓ GUI shutdown successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ GUI display test error: {e}")
        traceback.print_exc()
        return False

def test_database_operations():
    """Test database-related operations"""
    print("\nTesting database operations...")
    try:
        from server.ServerGUI import ServerGUI
        
        gui = ServerGUI()
        
        # Test database path
        print(f"✓ Database path: {gui.db_path}")
        
        # Test settings
        print(f"✓ Settings loaded: {len(gui.settings)} settings")
        
        # Test data structures
        print(f"✓ Performance data structure: {len(gui.performance_data)} metrics")
        print(f"✓ Activity log: {len(gui.activity_log)} entries")
        
        return True
        
    except Exception as e:
        print(f"✗ Database operations error: {e}")
        traceback.print_exc()
        return False

def test_theme_and_styling():
    """Test theme and styling constants"""
    print("\nTesting theme and styling...")
    try:
        from server.ServerGUI import ModernTheme
        
        # Test theme constants
        print(f"✓ Primary background: {ModernTheme.PRIMARY_BG}")
        print(f"✓ Secondary background: {ModernTheme.SECONDARY_BG}")
        print(f"✓ Text primary: {ModernTheme.TEXT_PRIMARY}")
        print(f"✓ Success color: {ModernTheme.SUCCESS}")
        print(f"✓ Error color: {ModernTheme.ERROR}")
        
        # Test all color constants exist
        required_colors = [
            'PRIMARY_BG', 'SECONDARY_BG', 'CARD_BG', 'ACCENT_BG',
            'TEXT_PRIMARY', 'TEXT_SECONDARY', 'TEXT_ACCENT',
            'SUCCESS', 'WARNING', 'ERROR', 'INFO',
            'ACCENT_BLUE', 'ACCENT_PURPLE', 'ACCENT_GREEN', 'ACCENT_ORANGE'
        ]
        
        for color in required_colors:
            if hasattr(ModernTheme, color):
                print(f"✓ {color}: {getattr(ModernTheme, color)}")
            else:
                print(f"✗ Missing color: {color}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Theme testing error: {e}")
        traceback.print_exc()
        return False

def test_advanced_features():
    """Test advanced features availability"""
    print("\nTesting advanced features...")
    try:
        from server.ServerGUI import CHARTS_AVAILABLE, SYSTEM_MONITOR_AVAILABLE, TRAY_AVAILABLE
        
        print(f"✓ Charts available: {CHARTS_AVAILABLE}")
        print(f"✓ System monitoring available: {SYSTEM_MONITOR_AVAILABLE}")
        print(f"✓ System tray available: {TRAY_AVAILABLE}")
        
        # Test optional imports
        if CHARTS_AVAILABLE:
            print("✓ Matplotlib functionality enabled")
        else:
            print("⚠️ Matplotlib not available - charts disabled")
        
        if SYSTEM_MONITOR_AVAILABLE:
            print("✓ System monitoring functionality enabled")
        else:
            print("⚠️ psutil not available - using simulated data")
        
        if TRAY_AVAILABLE:
            print("✓ System tray functionality enabled")
        else:
            print("⚠️ pystray not available - system tray disabled")
        
        return True
        
    except Exception as e:
        print(f"✗ Advanced features error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main comprehensive test function"""
    print("=== ServerGUI Comprehensive Test Suite ===")
    
    test_results = []
    
    # Test 1: Widget Creation
    result = test_widget_creation()
    test_results.append(("Widget Creation", result))
    
    # Test 2: GUI Operations
    result = test_gui_operations()
    test_results.append(("GUI Operations", result))
    
    # Test 3: Database Operations
    result = test_database_operations()
    test_results.append(("Database Operations", result))
    
    # Test 4: Theme and Styling
    result = test_theme_and_styling()
    test_results.append(("Theme and Styling", result))
    
    # Test 5: Advanced Features
    result = test_advanced_features()
    test_results.append(("Advanced Features", result))
    
    # Test 6: GUI with Display (optional)
    try:
        result = test_gui_with_display()
        test_results.append(("GUI Display", result))
    except Exception as e:
        print(f"⚠️ GUI display test skipped: {e}")
        test_results.append(("GUI Display", False))
    
    # Summary
    print("\n=== Test Summary ===")
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ServerGUI is working correctly.")
        return True
    else:
        print(f"❌ {total - passed} tests failed. ServerGUI needs fixes.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        traceback.print_exc()
        sys.exit(1)
