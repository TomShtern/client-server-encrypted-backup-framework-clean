#!/usr/bin/env python3
"""
Standalone Backup Server Launcher
Fixes import issues and starts the backup server properly
"""

import sys
import os

# Add the project root to Python path to fix import issues
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """Start the backup server with proper imports"""
    try:
        # Import and start the server
        from src.server.network_server import NetworkServer
        from src.server.database import DatabaseManager
        from src.server.request_handlers import RequestHandler
        from src.server.gui_integration import GUIManager
        
        print("Starting CyberBackup 3.0 Server...")
        print("Port: 1256")
        print("=" * 50)
        
        # Initialize components
        db_manager = DatabaseManager()
        request_handler = RequestHandler(db_manager)
        gui_manager = GUIManager()
        
        # Create and start network server
        network_server = NetworkServer(
            port=1256,
            request_handler=request_handler.process_request,
            client_resolver=db_manager.get_client_by_id
        )
        
        # Start the server
        success = network_server.start()
        if not success:
            print("Failed to start backup server!")
            return 1
            
        print("Backup server started successfully!")
        print("Press Ctrl+C to stop the server")
        
        # Keep the server running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            network_server.stop()
            print("Server stopped.")
            
        return 0
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure all dependencies are installed")
        return 1
    except Exception as e:
        print(f"Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
