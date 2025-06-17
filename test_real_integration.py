#!/usr/bin/env python3
"""
Test the Real Backup Integration System
"""

import os
import sys
import tempfile
import hashlib
from pathlib import Path

def create_test_file(content="Test backup file content", filename="test_backup.txt"):
    """Create a test file for backup"""
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, filename)
    
    with open(test_file, 'w') as f:
        f.write(content)
    
    return test_file

def calculate_file_hash(file_path):
    """Calculate SHA256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def test_real_backup_executor():
    """Test the real backup executor directly"""
    print("🔒 Testing Real Backup Executor")
    print("=" * 50)
    
    # Import here to avoid issues if dependencies aren't installed
    try:
        from real_backup_executor import RealBackupExecutor
    except ImportError as e:
        print(f"❌ Failed to import RealBackupExecutor: {e}")
        return False
    
    # Create test file
    test_file = create_test_file("Hello, this is a test backup file!")
    print(f"📁 Created test file: {test_file}")
    print(f"📏 File size: {os.path.getsize(test_file)} bytes")
    print(f"🔢 File hash: {calculate_file_hash(test_file)}")
    print()
    
    # Initialize executor
    executor = RealBackupExecutor()
    
    def status_callback(phase, message):
        print(f"[{phase}] {message}")
    
    executor.set_status_callback(status_callback)
    
    # Execute backup
    print("🚀 Starting backup test...")
    result = executor.execute_real_backup(
        username="test_user",
        file_path=test_file
    )
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print("=" * 50)
    print(f"Success: {result['success']}")
    print(f"Duration: {result['duration']:.2f} seconds")
    print(f"Process Exit Code: {result['process_exit_code']}")
    print(f"Network Activity: {result['network_activity']}")
    
    if result['error']:
        print(f"Error: {result['error']}")
    
    if result['verification']:
        v = result['verification']
        print(f"\nFile Transfer Verification:")
        print(f"• File Found: {v['file_found']}")
        print(f"• Size Match: {v['size_match']} ({v['original_size']} -> {v['received_size']} bytes)")
        print(f"• Hash Match: {v['hash_match']}")
        print(f"• Transferred: {v['transferred']}")
        if v['received_file']:
            print(f"• Received File: {v['received_file']}")
    
    # Cleanup
    try:
        os.remove(test_file)
        os.rmdir(os.path.dirname(test_file))
    except:
        pass
    
    return result['success']

def check_prerequisites():
    """Check that all required components are present"""
    print("🔍 Checking Prerequisites")
    print("=" * 30)
    
    checks_passed = 0
    total_checks = 4
    
    # Check C++ client
    client_exe = "client/EncryptedBackupClient.exe"
    if os.path.exists(client_exe):
        print(f"✅ C++ Client: {client_exe}")
        checks_passed += 1
    else:
        print(f"❌ C++ Client: {client_exe} NOT FOUND")
        print("   Run 'build.bat' to compile the client")
    
    # Check server directory
    server_dir = "server"
    if os.path.exists(server_dir):
        print(f"✅ Server Directory: {server_dir}")
        checks_passed += 1
    else:
        print(f"❌ Server Directory: {server_dir} NOT FOUND")
    
    # Check received files directory
    received_files = "server/received_files"
    if os.path.exists(received_files):
        print(f"✅ Received Files: {received_files}")
        checks_passed += 1
    else:
        print(f"⚠️  Received Files: {received_files} NOT FOUND (will be created)")
        os.makedirs(received_files, exist_ok=True)
        checks_passed += 1
    
    # Check if server is running
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 1256))
        sock.close()
        
        if result == 0:
            print("✅ Backup Server: Running on port 1256")
            checks_passed += 1
        else:
            print("❌ Backup Server: NOT running on port 1256")
            print("   Start with: python server/server.py")
    except Exception:
        print("❌ Backup Server: Cannot check status")
    
    print(f"\nPrerequisite Check: {checks_passed}/{total_checks} passed")
    return checks_passed == total_checks

def main():
    """Main test function"""
    print("🔒 REAL BACKUP INTEGRATION SYSTEM TEST")
    print("=" * 60)
    print()
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return False
    
    print("\n" + "=" * 60)
    
    # Test the backup executor
    success = test_real_backup_executor()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Real backup integration is working correctly")
        print("✅ Files are actually being transferred")
        print("✅ System is ready for use")
        print()
        print("Next steps:")
        print("1. Start the integration server: python integration_web_server.py")
        print("2. Open browser to: http://localhost:5000")
        print("3. Upload files and verify real backups!")
    else:
        print("❌ TESTS FAILED!")
        print("The real backup integration is not working properly.")
        print("Check the error messages above for details.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
