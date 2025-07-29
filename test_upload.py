#!/usr/bin/env python3
"""
Test script to isolate file upload issues
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append('.')

from src.api.real_backup_executor import RealBackupExecutor

def test_backup():
    print("=== Testing RealBackupExecutor ===")
    
    # Create test file
    test_file = "test_upload.txt"
    with open(test_file, 'w') as f:
        f.write("Test file content for backup testing")
    
    print(f"Created test file: {os.path.abspath(test_file)}")
    
    # Create executor
    print("Creating RealBackupExecutor...")
    executor = RealBackupExecutor()
    
    print(f"Client executable: {executor.client_exe}")
    print(f"Client exists: {os.path.exists(executor.client_exe)}")
    
    # Test backup
    print("Starting backup test...")
    try:
        result = executor.execute_real_backup(
            username="testuser",
            file_path=test_file,
            server_ip="127.0.0.1",
            server_port=1256,
            timeout=30
        )
        
        print(f"Backup result: {result}")
        
    except Exception as e:
        print(f"Backup failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

if __name__ == "__main__":
    test_backup()