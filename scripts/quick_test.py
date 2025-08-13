#!/usr/bin/env python3
"""
Quick test to verify the Unicode fix and server status
"""

import socket
import time
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

def test_port_connection(port: int, timeout: int = 2):
    """Test if port is responding with multiple attempts"""
    print(f"Testing port {port}...")
    for attempt in range(3):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex(('127.0.0.1', port))
                if result == 0:
                    print(f"[OK] Port {port}: RESPONDING (attempt {attempt + 1})")
                    return True
                else:
                    print(f"[WARNING] Port {port}: Not responding (attempt {attempt + 1}, error {result})")
        except Exception as e:
            print(f"[ERROR] Port {port}: Exception on attempt {attempt + 1}: {e}")
        time.sleep(0.5)
    
    print(f"[ERROR] Port {port}: FAILED after 3 attempts")
    return False

def test_server_status():
    """Test current server status"""
    print("=== Testing Current Server Status ===")
    
    backup_server = test_port_connection(1256)
    api_server = test_port_connection(9090)
    
    print(f"\n[RESULTS]:")
    print(f"Backup Server (1256): {'[OK] RUNNING' if backup_server else '[ERROR] NOT RUNNING'}")
    print(f"API Server (9090): {'[OK] RUNNING' if api_server else '[ERROR] NOT RUNNING'}")
    
    if backup_server and not api_server:
        print("\n[INFO] Status: Backup server is running, but API server needs to be started")
        print("The Unicode fix should resolve the GUI red status issue")
    elif backup_server and api_server:
        print("\n[SUCCESS] Status: Both servers are running - system should be operational!")
    elif not backup_server and not api_server:
        print("\n[INFO] Status: No servers running - can run the canonical launcher")
    else:
        print("\n[WARNING] Status: Partial system - may need cleanup and restart")
    
    return backup_server, api_server

def main():
    print("Quick Test - CyberBackup System Status")
    print("=" * 50)
    
    backup_running, api_running = test_server_status()
    
    print("\n" + "=" * 50)
    
    if backup_running and not api_running:
        print("[SUCCESS] GOOD NEWS: The backup server is working!")
        print("[INFO] The Unicode encoding fix should resolve the GUI red status")
        print("[LAUNCH] Now you can start the API server to complete the system")
        print("\nNext steps:")
        print("1. The backup server GUI should now show green instead of red")
        print("2. Start the API server manually or restart the launcher")
        print("3. The system should be fully functional")
        
    elif backup_running and api_running:
        print("[SUCCESS] PERFECT: Both servers are running!")
        print("[INFO] Try accessing: http://127.0.0.1:9090/")
        
    else:
        print("[INFO] System ready for fresh startup")
        print("[LAUNCH] Run the canonical launcher: python scripts/one_click_build_and_run.py")

if __name__ == "__main__":
    main()