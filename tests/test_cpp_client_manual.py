#!/usr/bin/env python3
"""
Manual C++ Client Test Script
=============================

This script tests the EncryptedBackupClient.exe directly to diagnose 
why it might be crashing when called from the Python framework.

Run this script to test the C++ client outside of the web interface.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def create_test_transfer_info():
    """Create a test transfer.info file"""
    content = "127.0.0.1:1256\ntestuser\ntest_file.txt\n"
    with open("transfer.info", "w") as f:
        f.write(content)
    print(f"Created transfer.info with content:\n{content}")

def create_test_file():
    """Create a small test file to upload"""
    test_content = "This is a test file for the CyberBackup system.\nCreated by test_cpp_client_manual.py\n"
    with open("test_file.txt", "w") as f:
        f.write(test_content)
    print(f"Created test_file.txt ({len(test_content)} bytes)")

def test_executable_exists():
    """Check which C++ client executables exist"""
    possible_paths = [
        r"build\Release\EncryptedBackupClient.exe",
        r"client\EncryptedBackupClient.exe",
        r"EncryptedBackupClient.exe"
    ]
    
    existing_exes = []
    for path in possible_paths:
        if os.path.exists(path):
            existing_exes.append(os.path.abspath(path))
            print(f"[OK] Found: {os.path.abspath(path)}")
        else:
            print(f"[MISSING] {path}")
    
    return existing_exes

def run_cpp_client_test(exe_path):
    """Run the C++ client and capture its output"""
    print(f"\n{'='*60}")
    print(f"Testing: {exe_path}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"{'='*60}")
    
    # Test 1: Run with --batch flag (as used by Python code)
    print("\nTEST 1: Running with --batch flag")
    print(f"Command: {exe_path} --batch")
    try:
        result = subprocess.run(
            [exe_path, "--batch"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=30
        )
        
        print(f"Exit Code: {result.returncode}")
        if result.stdout:
            print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
            
        if result.returncode == 0:
            print("[SUCCESS] C++ client completed without errors")
        else:
            print(f"[FAILED] C++ client failed with exit code {result.returncode}")
            
    except subprocess.TimeoutExpired:
        print("[TIMEOUT] C++ client hung for more than 30 seconds")
    except FileNotFoundError:
        print(f"[FILE NOT FOUND] Could not execute {exe_path}")
    except Exception as e:
        print(f"[EXCEPTION] {e}")

def main():
    print("C++ Client Manual Test Script")
    print("=" * 40)
    print()
    
    # Change to the project root directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"Working directory: {os.getcwd()}")
    print()
    
    # Check which executables exist
    print("Checking for C++ client executables...")
    existing_exes = test_executable_exists()
    
    if not existing_exes:
        print("\n[ERROR] No C++ client executables found!")
        print("You may need to build the project first.")
        print("Try running: python one_click_build_and_run.py")
        return 1
    
    # Create test files
    print(f"\nCreating test files...")
    create_test_transfer_info()
    create_test_file()
    
    # Test each executable
    for exe_path in existing_exes:
        run_cpp_client_test(exe_path)
    
    # Cleanup
    print(f"\nCleaning up test files...")
    for file in ["transfer.info", "test_file.txt"]:
        if os.path.exists(file):
            os.remove(file)
            print(f"Removed: {file}")
    
    print(f"\n{'='*60}")
    print("Manual test completed!")
    print("If the C++ client failed, the error messages above")
    print("should help identify why it's crashing in the web interface.")
    print(f"{'='*60}")

if __name__ == "__main__":  # pragma: no cover - manual execution helper
    try:
        ret = main()
        print(f"Exited with code {ret}")
    except KeyboardInterrupt:  # noqa: PIE786
        print("\n\nTest interrupted by user")
    except Exception as e:  # noqa: BLE001
        print(f"\n\nUnexpected error: {e}")