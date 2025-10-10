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

# Add repository root to path for imports
_flet_v2_root = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_flet_v2_root)
for _path in (_flet_v2_root, _repo_root):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Configure environment for GUI integration
os.environ['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'  # Disable server's embedded GUI
os.environ['CYBERBACKUP_DISABLE_GUI'] = '1'  # Use standalone FletV2 GUI instead
os.environ['PYTHONNOUSERSITE'] = '1'  # Prevent package conflicts from user site-packages

# Enable debugging
os.environ['FLET_DASHBOARD_DEBUG'] = '1'
os.environ['FLET_DASHBOARD_CONTENT_DEBUG'] = '1'

print("=" * 70)
print(">> Starting Flet GUI with Real BackupServer Integration")
print("=" * 70)

# Initialize log capture VERY EARLY (before any other imports)
# This ensures all Flet framework and application logs are captured
print("\n[0/4] Initializing log capture system...")
try:
    from Shared.logging.flet_log_capture import get_flet_log_capture
    _log_capture = get_flet_log_capture()
    print(f"[OK] Log capture initialized - ready to capture framework and app logs")
except Exception as e:
    print(f"[WARNING] Failed to initialize log capture: {e}")
    print("Logs view may not display Flet framework logs correctly.")

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
import flet as ft  # noqa: E402 - Import after environment setup
import main  # noqa: E402 - Import after environment setup

# Initialize BackupServer in MAIN thread (signal handlers require main thread)
print("\n[3/4] Initializing BackupServer (main thread)...")
server_instance = None
try:
    print("[INIT] Creating BackupServer instance in main thread (signals enabled)...")
    server_instance = BackupServer()
    print("[OK] BackupServer instance created successfully")
    print("[INFO] Network server NOT started (integration mode) - call start() separately if needed")
except Exception as init_err:
    print(f"[ERROR] BackupServer initialization failed: {init_err}")
    import traceback as _tb
    _tb.print_exc()
    print("[WARN] Proceeding without real server (GUI-only mode)")
    server_instance = None

# Launch Flet GUI with server instance
print("\n[4/4] Launching Flet GUI...")
print("=" * 70)

# Store app instance to prevent multiple creations
_app_instance = None

def gui_with_server_main(page: ft.Page):
    """
    Initialize FletV2App with real server instance.

    The server object will be passed to server_bridge, which will call
    its methods directly (no API calls needed).

    Note: This function may be called multiple times in WEB_BROWSER mode
    (once per page connection/tab). We create a fresh app for each page.
    """
    global _app_instance

    print("🟢 [START] gui_with_server_main function ENTERED")
    print(f"🟢 [START] Page object: {page}")
    print(f"🟢 [START] Server instance available: {server_instance is not None}")

    print("\n[PAGE CONNECT] New page connection established")

    # Server already initialized (or failed) before ft.app launch
    print(f"   Server Instance: {'[OK] Connected' if server_instance else '[WARN]  Mock Mode'}")

    # Create FletV2App with real server
    app = main.FletV2App(page, real_server=server_instance)

    # Set up cleanup handler for when page disconnects
    def cleanup_on_disconnect(e):
        print("\n[PAGE DISCONNECT] Cleaning up resources...")
        try:
            # Call dispose function if it exists
            if hasattr(app, 'dispose') and callable(app.dispose):
                app.dispose()
            # Clean up current view
            if hasattr(app, '_current_view_dispose') and app._current_view_dispose:
                app._current_view_dispose()
            print("[OK] Resources cleaned up")
        except Exception as cleanup_err:
            print(f"[WARN] Cleanup error: {cleanup_err}")

    page.on_disconnect = cleanup_on_disconnect

    # Initialize the app using Flet's task runner
    async def async_init():
        try:
            print("[INIT] Starting async initialization...")
            print(f"[DEBUG] App object: {app}")
            print(f"[DEBUG] App.initialize callable? {callable(getattr(app, 'initialize', None))}")
            print(f"[DEBUG] About to await app.initialize()...")
            await app.initialize()
            print(f"[DEBUG] app.initialize() returned successfully")
            print(f"\n{'=' * 70}")
            print(f"{'[READY] FletV2 GUI is Running':^70}")
            if server_instance:
                print(f"{'[OK] Real server connected - Full CRUD operational':^70}")
            else:
                print(f"{'[WARN]  Mock mode - Server connection failed':^70}")
            print(f"{'=' * 70}\n")
        except Exception as init_err:
            print(f"[ERROR] App initialization failed: {init_err}")
            import traceback
            traceback.print_exc()

    #  Schedule initialization
    print("[DEBUG] Scheduling async initialization task...")
    page.run_task(async_init)
    print("[DEBUG] Task scheduled")

if __name__ == "__main__":
    preferred_ports = [8570, 8571, 8572]
    launched = False
    for cand in preferred_ports:
        try:
            print(f"[PORT] Attempting Flet launch on {cand}...")
            ft.app(target=gui_with_server_main, view=ft.AppView.WEB_BROWSER, port=cand)
            launched = True
            print(f"[BOOT] Flet launched successfully on port {cand}")
            break
        except OSError as ose:
            print(f"[WARN] Port {cand} failed: {ose}")
        except Exception as ex:
            print(f"[ERROR] Unexpected launch error on {cand}: {ex}")
    if not launched:
        # Fallback to ephemeral port
        print("[FALLBACK] All preferred ports busy; launching on ephemeral port (0)...")
        try:
            ft.app(target=gui_with_server_main, view=ft.AppView.WEB_BROWSER, port=0)
            launched = True
            print("[BOOT] Flet launched on ephemeral port (check console for actual port)")
        except Exception as final_err:
            print(f"[FATAL] Flet application failed to launch on any port: {final_err}")
            raise SystemExit(1) from final_err

    # Cleanup on exit
    if server_instance:
        print("\n[STOP] Shutting down BackupServer...")
        try:
            server_instance.stop()
            print("[OK] Server stopped cleanly")
        except Exception as e:
            print(f"[WARN]  Server shutdown error: {e}")
