#!/usr/bin/env python3
"""
Simple C++ Client Test - No Unicode Issues
==========================================
Test the C++ client directly with simple output
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("Simple C++ Client Test")
    print("=" * 30)
    
    # Change to project directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    
    # Create test files
    print("\nCreating test files...")
    
    # Create transfer.info with unique username
    import time
    unique_username = f"testuser_{int(time.time())}"
    with open("transfer.info", "w") as f:
        f.write(f"127.0.0.1:1256\n{unique_username}\ntest_file.txt\n")
    print(f"Created transfer.info with username: {unique_username}")
    
    # Create test file
    with open("test_file.txt", "w") as f:
        f.write("Test file for CyberBackup\n")
    print("Created test_file.txt")
    
    # Test the main C++ client
    exe_path = r"build\Release\EncryptedBackupClient.exe"
    
    if not os.path.exists(exe_path):
        print(f"ERROR: {exe_path} not found")
        return 1
    
    print(f"\nTesting: {exe_path}")
    print(f"Command: {exe_path} --batch")
    
    try:
        result = subprocess.run(
            [exe_path, "--batch"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"\nExit Code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\nSUCCESS: C++ client completed")
        else:
            print(f"\nFAILED: Exit code {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("TIMEOUT: Process hung")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Cleanup
    for file in ["transfer.info", "test_file.txt"]:
        if os.path.exists(file):
            os.remove(file)
    
    print("\nTest complete")

if __name__ == "__main__":
    main()