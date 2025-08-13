#!/usr/bin/env python3
"""
Simple Server Launcher
Starts the backup server and API server in separate console windows
"""

import sys
import os
import subprocess
import time
import webbrowser

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

def check_port_available(port):
    """Check if a port is available"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', port))
            return True
    except OSError:
        return False

def wait_for_server(port, timeout=30):
    """Wait for server to be ready"""
    import socket
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('127.0.0.1', port))
                if result == 0:
                    return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    print("=" * 50)
    print("    CyberBackup Server Launcher")
    print("=" * 50)
    
    # Check if ports are available
    if not check_port_available(1256):
        print("ERROR: Port 1256 is in use. Please close other applications using this port.")
        return 1
    
    if not check_port_available(9090):
        print("ERROR: Port 9090 is in use. Please close other applications using this port.")
        return 1
    
    print("✓ Ports 1256 and 9090 are available")
    
    # Set up environment with Python path
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    try:
        # Start backup server
        print("\n1. Starting Python Backup Server...")
        backup_server = subprocess.Popen(
            [sys.executable, '-m', 'python_server.server.server'],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
            env=env
        )
        print(f"   Backup server started with PID: {backup_server.pid}")
        
        # Wait for backup server to start
        print("   Waiting for backup server to be ready...")
        if wait_for_server(1256, timeout=30):
            print("   ✓ Backup server is ready on port 1256")
        else:
            print("   ✗ Backup server failed to start on port 1256")
            return 1
        
        # Start API server
        print("\n2. Starting API Bridge Server...")
        api_server = subprocess.Popen(
            [sys.executable, '-m', 'api_server.cyberbackup_api_server'],
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
            env=env
        )
        print(f"   API server started with PID: {api_server.pid}")
        
        # Wait for API server to start
        print("   Waiting for API server to be ready...")
        if wait_for_server(9090, timeout=30):
            print("   ✓ API server is ready on port 9090")
        else:
            print("   ✗ API server failed to start on port 9090")
            return 1
        
        # Open web browser
        gui_url = "http://127.0.0.1:9090/"
        print(f"\n3. Opening Web GUI: {gui_url}")
        webbrowser.open(gui_url)
        
        print("\n" + "=" * 50)
        print("🎉 SUCCESS! All servers are running:")
        print(f"   • Backup Server: Port 1256 (PID: {backup_server.pid})")
        print(f"   • API Server: Port 9090 (PID: {api_server.pid})")
        print(f"   • Web GUI: {gui_url}")
        print("=" * 50)
        
        print("\nServers are running in separate console windows.")
        print("Close the console windows to stop the servers.")
        print("Press Enter to exit this launcher...")
        input()
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: Failed to start servers: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())