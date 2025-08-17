# In file: __main__.py
# Place this file in the root of your project directory, alongside EnhancedServerGUI.py

import sys
import os

# Ensure the project root is on the Python path to resolve imports correctly
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now, we can import the main GUI class and its dependencies
from EnhancedServerGUI import EnhancedServerGUI
# If you have a separate server class, you would import and instantiate it here
# from python_server.server.main import BackupServer

def main():
    """The main entry point for the application."""
    print("[INFO] Launching Server GUI Application...")

    # In a real application, you would instantiate your actual server here
    # server_instance = BackupServer() 
    server_instance = None # For standalone GUI testing

    gui = EnhancedServerGUI(server_instance=server_instance)

    if gui.initialize():
        try:
            # If using tkthread, the main thread can do other work or just wait.
            # If not, the gui_thread must be joined.
            if gui.gui_thread and hasattr(gui.gui_thread, 'join'):
                gui.gui_thread.join()
        except KeyboardInterrupt:
            print("\n[INFO] Shutdown signal received.")
            if gui.is_running:
                gui.shutdown()
    else:
        print("[FATAL] GUI could not be initialized.")
    
    print("[INFO] Application has exited.")

if __name__ == "__main__":
    main()