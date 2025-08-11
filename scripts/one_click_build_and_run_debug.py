#!/usr/bin/env python3
"""
ONE-CLICK BUILD AND RUN - DEBUG VERSION
=======================================
This version keeps console windows open so you can see any errors.
"""

import os
import sys
import subprocess
import time
import tempfile
from pathlib import Path

# Import the original functions
from .one_click_build_and_run import (
    check_api_server_status, check_backup_server_status, 
    check_python_dependencies, cleanup_existing_processes,
    print_phase
)

def create_debug_batch_file(command_list, title):
    """Create a batch file that runs a command and keeps the window open"""
    # Create a temporary batch file
    batch_content = f"""@echo off
title {title}
echo Starting {title}...
echo Command: {' '.join(command_list)}
echo.

"""
    
    # Add the actual command
    if len(command_list) == 1:
        batch_content += f"{command_list[0]}\n"
    else:
        # Handle multi-part commands
        batch_content += f'"{command_list[0]}"'
        for arg in command_list[1:]:
            batch_content += f' "{arg}"'
        batch_content += "\n"
    
    batch_content += """
echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo Server started successfully!
    echo Press any key to close this window...
) else (
    echo Server failed to start! Error code: %ERRORLEVEL%
    echo Press any key to close this window...
)
pause >nul
"""
    
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
        f.write(batch_content)
        return f.name

def main():
    print()
    print("=" * 72)
    print("   🐛 ONE-CLICK BUILD AND RUN - DEBUG VERSION")
    print("=" * 72)
    print()
    print("This version keeps console windows open so you can see errors.")
    print()
    
    # Change to project root
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # Clean up existing processes
    print_phase(1, 3, "Cleaning Up Existing Processes")
    cleanup_existing_processes()
    
    # Check dependencies
    print_phase(2, 3, "Checking Dependencies")
    missing_deps = check_python_dependencies()
    if missing_deps:
        print(f"[ERROR] Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        input("Press Enter to continue anyway...")
    
    # Start services with debug console windows
    print_phase(3, 3, "Starting Services with Debug Windows")
    
    # Create batch files for both servers
    backup_server_command = [sys.executable, "-m", "python_server.server.server"]
    api_server_command = [sys.executable, "cyberbackup_api_server.py"]
    
    backup_batch = create_debug_batch_file(backup_server_command, "Backup Server (Port 1256)")
    api_batch = create_debug_batch_file(api_server_command, "API Server (Port 9090)")
    
    print(f"Created debug batch files:")
    print(f"  Backup Server: {backup_batch}")
    print(f"  API Server: {api_batch}")
    print()
    
    # Start backup server
    print("Starting Backup Server in debug window...")
    backup_process = subprocess.Popen([backup_batch], shell=True)
    
    # Wait for backup server to start
    print("Waiting for backup server to initialize...")
    backup_ready = False
    for i in range(15):
        if check_backup_server_status():
            backup_ready = True
            print(f"[OK] Backup server ready after {i+1} seconds")
            break
        print(f"  Waiting... {i+1}/15")
        time.sleep(1)
    
    if not backup_ready:
        print("[WARNING] Backup server not responding after 15 seconds")
        print("Check the 'Backup Server (Port 1256)' window for errors")
        input("Press Enter to continue starting API server anyway...")
    
    # Start API server
    print("Starting API Server in debug window...")
    api_process = subprocess.Popen([api_batch], shell=True)
    
    # Wait for API server to start
    print("Waiting for API server to initialize...")
    api_ready = False
    for i in range(10):
        if check_api_server_status():
            api_ready = True
            print(f"[OK] API server ready after {i+1} seconds")
            break
        print(f"  Waiting... {i+1}/10")
        time.sleep(1)
    
    # Final status
    print()
    print("=" * 72)
    print("DEBUG STARTUP COMPLETE")
    print("=" * 72)
    print()
    
    backup_status = "RUNNING" if check_backup_server_status() else "NOT RESPONDING"
    api_status = "RUNNING" if check_api_server_status() else "NOT RESPONDING"
    
    print(f"Backup Server (Port 1256): {backup_status}")
    print(f"API Server (Port 9090): {api_status}")
    print()
    
    if api_ready:
        print("Opening web browser...")
        import webbrowser
        webbrowser.open("http://127.0.0.1:9090/")
        print("Web GUI: http://127.0.0.1:9090/")
    else:
        print("API Server not ready - check the 'API Server (Port 9090)' window")
    
    print()
    print("Console windows will remain open so you can see any errors.")
    print("Close the console windows when you're done testing.")
    print()
    
    # Cleanup temporary files on exit
    try:
        input("Press Enter to cleanup and exit...")
    finally:
        try:
            os.unlink(backup_batch)
            os.unlink(api_batch)
        except:
            pass

if __name__ == "__main__":
    main()