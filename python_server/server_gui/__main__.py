# -*- coding: utf-8 -*-
"""
__main__.py - Standalone Executable Entry Point for the Server GUI.

This script makes the `server_gui` package directly runnable. It is designed
for development, testing, and demonstration purposes, launching the GUI
without needing to run the full server backend.

This approach is the modern Python standard for creating executable packages.

To run, execute the package from the project's root directory:
    python -m python_server.server_gui
"""

import sys
import os
import traceback

# Import UTF-8 solution FIRST for proper Unicode handling
try:
    # Add project root to path temporarily for import
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    import Shared.utils.utf8_solution
except ImportError:
    pass  # Will be handled later in main()

def main() -> int:
    """
    Initializes and runs the Server GUI application in standalone mode.
    
    This function performs critical path correction to ensure that all project
    modules, especially the 'Shared' and 'server' packages, are discoverable.
    It then instantiates and runs the main ServerGUI application.

    Returns:
        int: An exit code (0 for success, 1 for failure).
    """
    print("[INFO] Launching Encrypted Backup Server GUI in Standalone Mode...")
    
    # --- Definitive Path Correction ---
    # Based on the confirmed project structure, we ensure the project root
    # is in the Python path. This is non-negotiable for robust execution.
    # __main__.py -> server_gui -> python_server -> Client_Server_Encrypted_Backup_Framework
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            print(f"[OK]   Project root added to system path: {project_root}")
        
        # Import the ServerGUI class *after* path correction has been applied.
        from python_server.server_gui.ServerGUI import ServerGUI
    except ImportError as e:
        print(f"\n{'='*80}\n[FATAL] A critical import failed. This often means the script is not being run\n"
              f"        from the project's root directory ('Client_Server_Encrypted_Backup_Framework').\n"
              f"        Error: {e}\n{'='*80}\n")
        return 1

    # --- Application Launch ---
    try:
        # We pass `server_instance=None` to engage the standalone logic within
        # ServerGUI, such as the fallback database manager.
        gui: ServerGUI = ServerGUI(server_instance=None)
        gui.run()
        
    except Exception:
        print(f"\n{'='*80}\n[FATAL] A critical, unhandled exception occurred during GUI execution.\n{'='*80}\n")
        traceback.print_exc()
        # In a production build, this would pop a user-friendly error dialog.
        return 1
        
    print("[INFO] Application has exited gracefully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())