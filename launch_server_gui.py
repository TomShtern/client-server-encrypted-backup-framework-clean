#!/usr/bin/env python3
"""
Quick launcher for Server GUI with proper path setup
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Set up the environment
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Add project root to Python path
    env = os.environ.copy()
    existing_pp = env.get('PYTHONPATH', '')
    if existing_pp:
        # Prepend project root if not already present
        paths = existing_pp.split(os.pathsep)
        if str(project_root) not in paths:
            env['PYTHONPATH'] = str(project_root) + os.pathsep + existing_pp
    else:
        env['PYTHONPATH'] = str(project_root)
    
    # Path to Server GUI
    server_gui_path = project_root / "python_server" / "server_gui" / "ServerGUI.py"
    
    if not server_gui_path.exists():
        print(f"ERROR: Server GUI not found at {server_gui_path}")
        return 1
    
    print("🖥️  Starting Server GUI...")
    print(f"   Path: {server_gui_path}")
    print(f"   Working Directory: {project_root}")
    
    # Use the virtual environment Python
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
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
        return 1

if __name__ == "__main__":
    sys.exit(main())
