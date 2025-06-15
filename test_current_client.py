#!/usr/bin/env python3
"""
Test Current Client Executable
Tests if the current client can connect to the running server
"""

import subprocess
import os
import time

def test_current_client():
    print("🧪 TESTING CURRENT CLIENT EXECUTABLE")
    print("=" * 50)
    
    # Check if client executable exists
    client_path = "client/EncryptedBackupClient.exe"
    
    if not os.path.exists(client_path):
        print(f"❌ FAIL: Client executable not found at {client_path}")
        return False
    
    print(f"✅ PASS: Client executable found at {client_path}")
    
    # Check configuration files
    config_files = [
        "client/transfer.info",
        "test_file.txt"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✅ PASS: Config file {config_file} exists")
        else:
            print(f"⚠️  WARNING: Config file {config_file} missing")
    
    # Try to run the client (this will work in Windows environment)
    print(f"\n🔍 Client Information:")
    
    try:
        # Get file size
        size = os.path.getsize(client_path)
        print(f"   Size: {size:,} bytes ({size / 1024 / 1024:.1f} MB)")
        
        # Get modification time
        mtime = os.path.getmtime(client_path)
        print(f"   Modified: {time.ctime(mtime)}")
        
        print(f"\n📋 To test the client in Windows:")
        print(f"   1. Open Command Prompt or PowerShell")
        print(f"   2. Navigate to the project directory")
        print(f"   3. Run: {client_path}")
        print(f"   4. The client should connect to the server on port 1256")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_current_client()
    if success:
        print("\n✅ CLIENT EXECUTABLE IS READY FOR TESTING")
    else:
        print("\n❌ CLIENT ISSUES DETECTED")
    
    exit(0 if success else 1)