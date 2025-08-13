#!/usr/bin/env python3
"""
Focused test to quickly identify the 64KB vs 66KB boundary issue.
"""

import os
import tempfile
import time
import subprocess
import random
import string
from typing import Tuple, Dict, Any, List

def generate_unique_username():
    """Generate a unique username"""
    timestamp = int(time.time())
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=3))
    return f"btest{timestamp % 10000}{random_suffix}"

def create_test_file(size_bytes: int, name_suffix: str) -> str:
    """Create a test file of exact size"""
    content = "T" * size_bytes
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_{name_suffix}.txt') as f:
        f.write(content)
        temp_path = f.name
    
    return temp_path

def test_transfer(file_path: str, size_bytes: int) -> Tuple[bool, str, str]:
    """Quick transfer test"""
    username = generate_unique_username()
    
    # Create transfer.info
    with open("transfer.info", 'w') as f:
        f.write("127.0.0.1:1256\n")
        f.write(f"{username}\n")
        f.write(f"{file_path}\n")
    
    # Test transfer
    client_exe = "build/Release/EncryptedBackupClient.exe"
    
    try:
        result = subprocess.run(
            [client_exe, "--batch"],
            timeout=30,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        success = result.returncode == 0
        error_msg = result.stderr if result.stderr else "Unknown"
        
        return success, error_msg, username
        
    except subprocess.TimeoutExpired:
        return False, "Timeout", username
    except Exception as e:
        return False, str(e), username

def main():
    """Main test function"""
    print("Focused 64KB vs 66KB Boundary Test")
    print("=" * 40)
    
    # Focus on the critical boundary area
    test_sizes: List[int] = [
        63 * 1024,    # 64512 bytes - 63KB
        64 * 1024,    # 65536 bytes - 64KB (should work)
        65 * 1024,    # 66560 bytes - 65KB
        66 * 1024,    # 67584 bytes - 66KB (reported issue)
        67 * 1024,    # 68608 bytes - 67KB
    ]
    
    results: Dict[int, Dict[str, Any]] = {}
    
    for size in test_sizes:
        size_kb = size // 1024
        print(f"\nTesting {size_kb}KB ({size} bytes)...")
        
        try:
            # Create test file
            test_file = create_test_file(size, f"{size_kb}KB")
            actual_size = os.path.getsize(test_file)
            print(f"File created: {actual_size} bytes")
            
            # Test transfer
            success, error_msg, username = test_transfer(test_file, size)
            
            results[size] = {
                'success': success,
                'error': error_msg,
                'username': username,
                'actual_size': actual_size
            }
            
            status = "✅ SUCCESS" if success else f"❌ FAILED"
            print(f"Result: {status}")
            if not success:
                print(f"Error: {error_msg}")
            
            # Check if file appeared in received_files
            if success:
                received_dir = "received_files"
                if os.path.exists(received_dir):
                    files = [f for f in os.listdir(received_dir) if username in f]
                    if files:
                        received_file = files[0]
                        received_size = os.path.getsize(os.path.join(received_dir, received_file))
                        print(f"Received file: {received_file} ({received_size} bytes)")
            
            # Cleanup
            try:
                os.unlink(test_file)
            except:
                pass
                
            time.sleep(1)  # Brief pause
            
        except Exception as e:
            print(f"ERROR: {e}")
            results[size] = {
                'success': False,
                'error': str(e),
                'username': 'unknown',
                'actual_size': 0
            }
    
    # Summary
    print("\n" + "=" * 40)
    print("SUMMARY:")
    print("=" * 40)
    
    successful = []
    failed = []
    
    for size in sorted(results.keys()):
        result = results[size]
        size_kb = size // 1024
        status = "SUCCESS" if result['success'] else "FAILED"
        
        print(f"{size_kb:2d}KB ({size:5d} bytes): {status}")
        
        if result['success']:
            successful.append(size)
        else:
            failed.append(size)
            print(f"                          Error: {result['error']}")
    
    print(f"\nSuccessful transfers: {len(successful)}")
    print(f"Failed transfers: {len(failed)}")
    
    if failed:
        print(f"\nFailed sizes: {[s//1024 for s in failed]}KB")
        
        # Check for specific error patterns
        error_counts = {}
        for size in failed:
            error = results[size]['error']
            error_counts[error] = error_counts.get(error, 0) + 1
        
        print("\nError patterns:")
        for error, count in error_counts.items():
            print(f"  {error}: {count} occurrences")
    else:
        print("\nAll tests passed - no boundary issue detected!")

if __name__ == "__main__":
    main()