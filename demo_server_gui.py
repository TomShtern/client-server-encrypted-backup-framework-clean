#!/usr/bin/env python3
"""
Demo script for ServerGUI - Shows the GUI in action with simulated data
"""

import sys
import os
import time
import threading
import random

# Add the server directory to the path
server_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server')
sys.path.insert(0, server_dir)

def simulate_server_activity(gui):
    """Simulate server activity to demonstrate GUI features"""
    print("Starting server activity simulation...")
    
    # Start with server offline
    gui.update_server_status(False)
    time.sleep(2)
    
    # Start server
    gui.show_info("Starting encrypted backup server...")
    time.sleep(1)
    gui.update_server_status(True, "127.0.0.1", 1256)
    gui.show_success("Server started successfully!")
    
    # Simulate client connections
    for i in range(5):
        time.sleep(2)
        connected = i + 1
        gui.update_client_stats(connected=connected, total=connected, active_transfers=0)
        gui.show_info(f"Client {connected} connected")
        
        # Simulate some file transfers
        if i > 1:
            transfers = random.randint(1, 3)
            bytes_transferred = random.randint(1024, 1024*1024*10)
            gui.update_client_stats(connected=connected, total=connected, active_transfers=transfers)
            gui.update_transfer_stats(bytes_transferred=bytes_transferred, last_activity="Just now")
    
    # Show some maintenance activity
    time.sleep(3)
    gui.update_maintenance_stats({
        'files_cleaned': 5,
        'partial_files_cleaned': 2,
        'clients_cleaned': 1,
        'last_cleanup': '2025-06-15 10:30:00'
    })
    gui.show_info("Maintenance completed - cleaned 5 files")
    
    # Show final stats    time.sleep(2)
    gui.update_transfer_stats(bytes_transferred=1024*1024*50, last_activity="30 seconds ago")
    gui.show_success("Demo completed - GUI is fully functional!")

def main():
    """Main demo function"""
    try:
        from ServerGUI import initialize_server_gui, get_server_gui, shutdown_server_gui
        
        print("=== ServerGUI Live Demo ===")
        print("Initializing enhanced GUI...")
        
        # Initialize GUI
        success = initialize_server_gui()
        if not success:
            print("❌ Failed to initialize GUI")
            return
        
        print("✓ GUI initialized successfully")
        print("🚀 Starting live demo with simulated server activity")
        print("📌 Watch the GUI for real-time updates!")
        print("⏱️  Demo will run for about 30 seconds...")
        
        # Get GUI instance
        gui = get_server_gui()
        
        # Start simulation in background
        sim_thread = threading.Thread(target=simulate_server_activity, args=(gui,), daemon=True)
        sim_thread.start()
        
        # Let demo run
        time.sleep(30)
        
        # Show final message
        gui.show_info("Demo completed! You can close the window now.")
        
        # Keep GUI open for user to explore
        print("\n✨ Demo completed!")
        print("🖱️  The GUI window will stay open for you to explore")
        print("❌ Close the window or press Ctrl+C to exit")
        
        # Wait for user to close or interrupt
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Shutting down demo...")
        
        # Shutdown
        shutdown_server_gui()
        print("✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
