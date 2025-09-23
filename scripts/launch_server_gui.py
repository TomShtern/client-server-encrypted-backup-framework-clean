#!/usr/bin/env python3
"""
Quick launcher for Server GUI with proper path setup and Sentry error tracking
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get project root before any other operations
    project_root = Path(__file__).parent.resolve()
    
    # Setup standardized import paths
    from Shared.path_utils import setup_imports
    setup_imports()
    
    try:
        from Shared.sentry_config import init_sentry, capture_error
        sentry_initialized = init_sentry("launcher-gui")
    except ImportError:
        sentry_initialized = False
        capture_error = None
        print("[WARNING] Sentry not available for launcher")
    
    try:
        # Set up the environment
        os.chdir(project_root)
    
        # Add project root to Python path
        env = os.environ.copy()
        if existing_pp := env.get('PYTHONPATH', ''):
            # Prepend project root if not already present
            paths = existing_pp.split(os.pathsep)
            if str(project_root) not in paths:
                env['PYTHONPATH'] = str(project_root) + os.pathsep + existing_pp
        else:
            env['PYTHONPATH'] = str(project_root)
    
    except Exception as e:
        print(f"❌ Failed to set up environment: {e}")
        if sentry_initialized and capture_error:
            capture_error(e, "launcher-gui", {"operation": "environment_setup"})
        return 1
    
    # Path to Server GUI
    server_gui_path = project_root / "python_server" / "server_gui" / "ServerGUI.py"
    
    if not server_gui_path.exists():
        print(f"ERROR: Server GUI not found at {server_gui_path}")
        return 1
    
    print("🖥️  Starting Server GUI...")
    print(f"   Path: {server_gui_path}")
    print(f"   Working Directory: {project_root}")
    
    # Use the virtual environment Python
    venv_python = project_root / "flet_venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = sys.executable  # Fallback to current Python
    
    try:
        # Launch Server GUI in new console window (Windows)
        if os.name == 'nt':
            env['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'
            process = subprocess.Popen(
                [str(venv_python), str(server_gui_path)],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                env=env,
                cwd=str(project_root)
            )
        else:
            # For non-Windows systems
            env['CYBERBACKUP_DISABLE_INTEGRATED_GUI'] = '1'
            process = subprocess.Popen(
                [str(venv_python), str(server_gui_path)],
                env=env,
                cwd=str(project_root)
            )
        
        print(f"✅ Server GUI started with PID: {process.pid}")
        print("   A new console window should have opened with the Server GUI")
        return 0
        
    except Exception as e:
        print(f"❌ Failed to start Server GUI: {e}")
        if sentry_initialized and capture_error:
            capture_error(e, "launcher-gui", {"operation": "launch_server_gui"})
        return 1

if __name__ == "__main__":
    sys.exit(main())
