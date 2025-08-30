#!/usr/bin/env python3
"""
Direct test of RealBackupExecutor to isolate the transfer failure issue
Bypasses web interface and API to test C++ client execution directly
"""

import os
import sys
import tempfile
from pathlib import Path

# Add api_server to path for imports
from Shared.path_utils import setup_imports
setup_imports()

from api.real_backup_executor import RealBackupExecutor

def create_test_file():
    """Create a simple test file for transfer"""
    test_content = f"Direct executor test - {os.urandom(8).hex()}\nThis file tests the RealBackupExecutor directly.\nTime: {__import__('datetime').datetime.now()}"
    test_file = "test_direct_executor.txt"
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    return os.path.abspath(test_file)

def test_direct_executor():
    """Test RealBackupExecutor directly to isolate the issue"""
    print("=" * 60)
    print("DIRECT REAL BACKUP EXECUTOR TEST")
    print("=" * 60)
    
    # Create test file
    test_file = create_test_file()
    print(f"Created test file: {test_file}")
    print(f"File size: {os.path.getsize(test_file)} bytes")
    
    # Test parameters
    username = "DirectExecutorTest"
    server_ip = "127.0.0.1"
    server_port = 1256
    
    print(f"Username: {username}")
    print(f"Server: {server_ip}:{server_port}")
    print()
    
    # Create executor instance
    print("Creating RealBackupExecutor instance...")
    try:
        executor = RealBackupExecutor()
        print("[OK] RealBackupExecutor created successfully")
    except Exception as e:
        print(f"[ERROR] Failed to create RealBackupExecutor: {e}")
        return False
    
    # Set up status callback
    def status_callback(phase, data):
        if isinstance(data, dict):
            message = data.get('message', phase)
            progress = data.get('progress', 'N/A')
            print(f"[{phase}] {message} (Progress: {progress})")
        else:
            print(f"[{phase}] {data}")
    
    executor.set_status_callback(status_callback)
    
    # Execute backup
    print("\nExecuting real backup...")
    print("-" * 40)
    
    try:
        result = executor.execute_real_backup(
            username=username,
            file_path=test_file,
            server_ip=server_ip,
            server_port=server_port,
            timeout=60  # 1 minute timeout
        )
        
        print("-" * 40)
        print("BACKUP EXECUTION RESULTS:")
        print(f"Success: {result.get('success', False)}")
        print(f"Duration: {result.get('duration', 0):.2f} seconds")
        print(f"Exit Code: {result.get('process_exit_code', 'N/A')}")
        print(f"Network Activity: {result.get('network_activity', False)}")
        
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        if result.get('success'):
            print("\n[SUCCESS] BACKUP COMPLETED SUCCESSFULLY")
        else:
            print("\n[FAILED] BACKUP FAILED")
            
    except Exception as e:
        print(f"\n[EXCEPTION] BACKUP EXECUTION EXCEPTION: {e}")
        result = {'success': False, 'error': str(e)}
    
    # Cleanup
    try:
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"[OK] Cleaned up test file: {test_file}")
    except Exception as e:
        print(f"Warning: Could not cleanup test file: {e}")
    
    print("\n" + "=" * 60)
    return result.get('success', False)

if __name__ == "__main__":  # pragma: no cover - manual execution path
    success = test_direct_executor()
    print("SUCCESS" if success else "FAILURE")