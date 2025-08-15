#!/usr/bin/env python3
"""
Debug script to test 66KB file transfer issue
Creates test files and monitors the transfer process
"""

import os
import tempfile
import time
import subprocess
import sys

def create_test_file(size_bytes, content_pattern="A"):
    """Create a test file of specific size"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_{size_bytes//1024}KB.txt') as f:
        # Fill with pattern to reach desired size
        pattern_size = len(content_pattern.encode('utf-8'))
        full_patterns = size_bytes // pattern_size
        remainder = size_bytes % pattern_size
        
        # Write full patterns
        for _ in range(full_patterns):
            f.write(content_pattern)
        
        # Write remainder
        if remainder > 0:
            f.write(content_pattern[:remainder])
        
        return f.name

def test_file_transfer(file_path, expected_size):
    """Test file transfer using the C++ client"""
    print(f"\n=== Testing {expected_size//1024}KB file ===")
    print(f"File: {file_path}")
    print(f"Size: {os.path.getsize(file_path)} bytes")
    
    # Create transfer.info file in the current working directory (where client expects it)
    transfer_info_path = "transfer.info"
    
    with open(transfer_info_path, 'w') as f:
        f.write("127.0.0.1:1256\n")
        f.write(f"TestDebug{expected_size//1024}KB\n")
        f.write(f"{file_path}\n")
    
    print(f"Created transfer.info: {transfer_info_path}")
    
    # Run the client
    client_exe = "build/Release/EncryptedBackupClient.exe"
    if not os.path.exists(client_exe):
        print(f"ERROR: Client executable not found: {client_exe}")
        return False
    
    print(f"Running client: {client_exe}")
    
    try:
        # Run client with timeout
        result = subprocess.run(
            [client_exe, "--batch"],
            timeout=30,
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("ERROR: Client timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"ERROR: Failed to run client: {e}")
        return False

def main():
    """Main test function"""
    print("66KB File Transfer Debug Test")
    print("=" * 50)
    
    # Test sizes
    test_sizes = [
        60 * 1024,   # 60KB - should work (single packet)
        64 * 1024,   # 64KB - should work (single packet)
        66 * 1024,   # 66KB - currently failing (multi-packet)
        70 * 1024,   # 70KB - multi-packet
    ]
    
    results = {}
    
    for size in test_sizes:
        try:
            # Create test file
            test_file = create_test_file(size, "X")
            print(f"\nCreated test file: {test_file}")
            
            # Test transfer
            success = test_file_transfer(test_file, size)
            results[size] = success
            
            print(f"Result: {'SUCCESS' if success else 'FAILED'}")
            
            # Clean up
            try:
                os.unlink(test_file)
            except:
                pass
                
        except Exception as e:
            print(f"ERROR testing {size//1024}KB file: {e}")
            results[size] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    for size, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"  {size//1024}KB: {status}")
    
    # Analysis
    failed_sizes = [size for size, success in results.items() if not success]
    if failed_sizes:
        print(f"\nFailed sizes: {[s//1024 for s in failed_sizes]}KB")
        print("This confirms the multi-packet transfer issue.")
    else:
        print("\nAll tests passed! The issue may be resolved.")

if __name__ == "__main__":
    main()
