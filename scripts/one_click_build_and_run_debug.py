#!/usr/bin/env python3
"""
ONE-CLICK BUILD AND RUN - DEBUG VERSION
=======================================
This version keeps console windows open so you can see any errors.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# Import the original functions
# Try a relative import (when executed as a package). If that fails
# (script executed directly), fall back to an absolute import so the
# module can be run with "python scripts/one_click_build_and_run_debug.py".
try:
    from .one_click_build_and_run import (
        check_api_server_status,
        check_backup_server_status,
        check_python_dependencies,
        cleanup_existing_processes,
    )
    from .one_click_build_and_run import print_phase as original_print_phase  # type: ignore
except (ImportError, SystemError):
    # Running as a plain script (no package context) - use absolute import
    from scripts.one_click_build_and_run import (
        check_api_server_status,
        check_backup_server_status,
        check_python_dependencies,
        cleanup_existing_processes,
    )
    from scripts.one_click_build_and_run import print_phase as original_print_phase

def print_phase(phase_num: int, total_phases: int, title: str) -> None:
    original_print_phase(phase_num, total_phases, title)

def create_debug_batch_file(command_list: list[str], title: str):
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
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as f:
        f.write(batch_content)
        return f.name

def main():  # sourcery skip: use-contextlib-suppress
    _extracted_from_main_2("   🐛 ONE-CLICK BUILD AND RUN - DEBUG VERSION")
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
    missing_pip_deps, missing_vcpkg_deps = check_python_dependencies()
    if missing_pip_deps or missing_vcpkg_deps:
        if missing_pip_deps:
            print(f"[ERROR] Missing Python dependencies: {', '.join([dep for dep, _ in missing_pip_deps])}")
            print("Install with: pip install " + " ".join([dep for dep, _ in missing_pip_deps]))
        if missing_vcpkg_deps:
            print(f"[ERROR] Missing VCPKG dependencies: {', '.join([dep for dep, _ in missing_vcpkg_deps])}")
            print("Install with: vcpkg install " + " ".join([dep for dep, _ in missing_vcpkg_deps]))
        input("Press Enter to continue anyway...")

    # Start services with debug console windows
    print_phase(3, 3, "Starting Services with Debug Windows")

    # Create batch files for both servers
    backup_server_command = [sys.executable, "-m", "python_server.server.server"]
    api_server_command = [sys.executable, "cyberbackup_api_server.py"]

    backup_batch = create_debug_batch_file(backup_server_command, "Backup Server (Port 1256)")
    api_batch = create_debug_batch_file(api_server_command, "API Server (Port 9090)")

    print("Created debug batch files:")
    _extracted_from_main_43(
        '  Backup Server: ', backup_batch, '  API Server: ', api_batch
    )
    backup_ready = _extracted_from_main_48(
        "Starting Backup Server in debug window...",
        backup_batch,
        "Waiting for backup server to initialize...",
    )
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

    api_ready = _extracted_from_main_48(
        "Starting API Server in debug window...",
        api_batch,
        "Waiting for API server to initialize...",
    )
    for i in range(10):
        if check_api_server_status():
            api_ready = True
            print(f"[OK] API server ready after {i+1} seconds")
            break
        print(f"  Waiting... {i+1}/10")
        time.sleep(1)

    _extracted_from_main_2("DEBUG STARTUP COMPLETE")
    backup_status = "RUNNING" if check_backup_server_status() else "NOT RESPONDING"
    api_status = "RUNNING" if check_api_server_status() else "NOT RESPONDING"

    _extracted_from_main_43(
        'Backup Server (Port 1256): ',
        backup_status,
        'API Server (Port 9090): ',
        api_status,
    )
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
            if backup_batch:
                os.unlink(backup_batch)
            if api_batch:
                os.unlink(api_batch)
        except Exception:
            pass


# TODO Rename this here and in `main`
def _extracted_from_main_43(arg0, arg1, arg2, arg3):
    print(f"{arg0}{arg1}")
    print(f"{arg2}{arg3}")
    print()


# TODO Rename this here and in `main`
def _extracted_from_main_48(arg0, arg1, arg2):
    # Start backup server
    print(arg0)
    _backup_process = subprocess.Popen([str(arg1)], shell=True)

    # Wait for backup server to start
    print(arg2)
    return False


# TODO Rename this here and in `main`
def _extracted_from_main_2(arg0):
    print()
    print("=" * 72)
    print(arg0)
    print("=" * 72)
    print()

if __name__ == "__main__":
    main()
