#!/usr/bin/env python3
"""
Test script to run the Flet GUI for 40 seconds
"""

import subprocess
import time
import sys
import os

def run_gui_for_duration(duration_seconds=40):
    """Run the Flet GUI for a specified duration"""
    print(f"Starting Flet GUI for {duration_seconds} seconds...")
    
    # Change to the project directory
    project_dir = os.path.join(os.path.dirname(__file__))
    os.chdir(project_dir)
    
    # Start the GUI process
    gui_process = subprocess.Popen([
        '.\\flet_venv\\Scripts\\python.exe', 
        'flet_server_gui/main.py'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    print(f"GUI process started with PID: {gui_process.pid}")
    print("GUI should now be visible. Waiting for timeout...")
    
    # Wait for the specified duration
    try:
        time.sleep(duration_seconds)
        print(f"\n{duration_seconds} seconds elapsed. Terminating GUI process...")
        gui_process.terminate()
        gui_process.wait(timeout=5)  # Wait up to 5 seconds for graceful termination
        print("GUI process terminated successfully.")
    except KeyboardInterrupt:
        print("\nInterrupted by user. Terminating GUI process...")
        gui_process.terminate()
        gui_process.wait(timeout=5)
        print("GUI process terminated.")
    except subprocess.TimeoutExpired:
        print("GUI process didn't terminate gracefully. Killing it...")
        gui_process.kill()
        gui_process.wait()
        print("GUI process killed.")

if __name__ == "__main__":
    duration = 40  # Default 40 seconds
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print("Invalid duration. Using default 40 seconds.")
    
    run_gui_for_duration(duration)