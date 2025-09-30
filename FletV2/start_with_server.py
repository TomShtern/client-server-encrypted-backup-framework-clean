#!/usr/bin/env python3
"""
Start FletV2 GUI with Real BackupServer Integration

This launcher creates a BackupServer instance and integrates it directly with
the Flet GUI, enabling full CRUD operations and real-time server monitoring.

Usage:
    cd FletV2 && python start_with_server.py

Features:
    - Real server instance (not mock data)
    - Direct method calls (not API calls)
    - Full CRUD operations on clients/files
    - Real-time logs and metrics
    - Database integration
"""

import os
import sys
import asyncio
import threading
import time

# Add repository root to path for imports
_flet_v2_root = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Configure environment for GUI integration
os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'  # Disable server's embedded GUI
os.environ['CYBERBACKUP_DISABLE_GUI'] = '1'  # Use standalone FletV2 GUI instead

# Enable debugging
os.environ['FLET_DASHBOARD_DEBUG'] = '1'
os.environ['FLET_DASHBOARD_CONTENT_DEBUG'] = '1'

print("=" * 70)
print(">> Starting Flet GUI with Real BackupServer Integration")
print("=" * 70)

# Import the real server
print("\n[1/4] Importing BackupServer...")
try:
    from python_server.server.server import BackupServer
    print("[OK] BackupServer imported successfully")
except ImportError as e:
    print(f"[ERROR] Failed to import BackupServer: {e}")
    print("\nMake sure python_server/ is in the correct location.")
    sys.exit(1)

# Import Flet
print("\n[2/4] Importing Flet...")
import flet as ft
import main

# Initialize BackupServer in a separate thread
print("\n[3/4] Initializing BackupServer...")
server_instance = None
server_thread = None
server_ready = threading.Event()

def run_server():
    """Run BackupServer in background thread."""
    global server_instance
    try:
        server_instance = BackupServer()
        print("[OK] BackupServer instance created")

        # Server is ready for GUI integration
        server_ready.set()

        # Start the server (this will block in this thread)
        print("[NET] Starting BackupServer network listener...")
        server_instance.start()

    except Exception as e:
        print(f"[ERROR] Server initialization failed: {e}")
        import traceback
        traceback.print_exc()
        server_ready.set()  # Unblock even on failure

# Start server in background thread
server_thread = threading.Thread(target=run_server, daemon=True, name="BackupServer")
server_thread.start()

# Wait for server to be ready
print("[WAIT] Waiting for server initialization...")
server_ready.wait(timeout=10)

if not server_instance:
    print("\n[ERROR] Server failed to initialize. Starting GUI in mock-only mode...")
    server_instance = None
else:
    print("[OK] Server initialized and ready")

# Launch Flet GUI with server instance
print("\n[4/4] Launching Flet GUI...")
print("=" * 70)

async def gui_with_server_main(page: ft.Page):
    """
    Initialize FletV2App with real server instance.

    The server object will be passed to server_bridge, which will call
    its methods directly (no API calls needed).
    """
    print(f"\n[START] GUI Starting...")
    print(f"   Server Instance: {'[OK] Connected' if server_instance else '[WARN]  Mock Mode'}")

    # Create FletV2App with real server
    app = main.FletV2App(page, real_server=server_instance)
    await app.initialize()

    print(f"\n{'=' * 70}")
    print(f"{'[READY] FletV2 GUI is Running':^70}")
    if server_instance:
        print(f"{'[OK] Real server connected - Full CRUD operational':^70}")
    else:
        print(f"{'[WARN]  Mock mode - Server connection failed':^70}")
    print(f"{'=' * 70}\n")

if __name__ == "__main__":
    # Run Flet app
    ft.app(target=gui_with_server_main, view=ft.AppView.FLET_APP)

    # Cleanup on exit
    if server_instance:
        print("\n[STOP] Shutting down BackupServer...")
        try:
            server_instance.stop()
            print("[OK] Server stopped cleanly")
        except Exception as e:
            print(f"[WARN]  Server shutdown error: {e}")
