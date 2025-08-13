#!/usr/bin/env python3
"""
Comprehensive boundary test to identify the exact file size boundaries
where transfers fail vs succeed.
"""

import os
import tempfile
import time
import subprocess
import random
import string
from typing import Dict, Any, List, Tuple

def generate_unique_username():
    """Generate a unique username to avoid registration conflicts"""
    timestamp = int(time.time())
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=4))
    return f"test{timestamp}{random_suffix}"

def create_test_file(size_bytes: int, name_suffix: str) -> str:
    """Create a test file of exact size"""
    content = "X" * size_bytes
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=f'_{name_suffix}.txt') as f:
        f.write(content)
        temp_path = f.name
    
    actual_size = os.path.getsize(temp_path)
    print(f"Created {name_suffix} file: {temp_path}")
    print(f"Target size: {size_bytes} bytes, Actual size: {actual_size} bytes")
    return temp_path

def test_file_transfer(file_path: str, expected_size: int, username: str) -> Tuple[bool, str | None]:
    """Test file transfer using the C++ client with unique username"""
    print(f"\n=== Testing {expected_size} byte file ===")
    print(f"File: {file_path}")
    print(f"Username: {username}")
    
    # Create transfer.info file
    transfer_info_path = "transfer.info"
    
    with open(transfer_info_path, 'w') as f:
        f.write("127.0.0.1:1256\n")
        f.write(f"{username}\n")
        f.write(f"{file_path}\n")
    
    # Run the client
    client_exe = "build/Release/EncryptedBackupClient.exe"
    if not os.path.exists(client_exe):
        print(f"ERROR: Client executable not found: {client_exe}")
        return False, "Client not found"
    
    try:
        # Run client with timeout
        result = subprocess.run(
            [client_exe, "--batch"],
            timeout=60,  # Longer timeout
            capture_output=True,
            text=True,
            encoding='utf-8',  # Explicit encoding to avoid Unicode issues
            errors='replace',  # Replace problematic characters
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        print(f"Return code: {result.returncode}")
        
        # Clean the output for display
        stdout_clean = result.stdout.replace('\x00', '') if result.stdout else "None"
        stderr_clean = result.stderr.replace('\x00', '') if result.stderr else "None"
        
        print(f"STDOUT: {stdout_clean}")
        if stderr_clean and stderr_clean != "None":
            print(f"STDERR: {stderr_clean}")
        
        success = result.returncode == 0
        error_msg = stderr_clean if not success else None
        
        # Also check if file appeared in received_files
        received_files_dir = "received_files"
        if success and os.path.exists(received_files_dir):
            # Look for file with username pattern
            found_file = None
            for f in os.listdir(received_files_dir):
                if username.lower() in f.lower() or os.path.basename(file_path) in f:
                    found_file = f
                    break
            
            if found_file:
                received_path = os.path.join(received_files_dir, found_file)
                received_size = os.path.getsize(received_path)
                print(f"File found in received_files: {found_file} ({received_size} bytes)")
                
        return success, error_msg
        
    except subprocess.TimeoutExpired:
        print("ERROR: Client timed out after 60 seconds")
        return False, "Timeout"
    except Exception as e:
        print(f"ERROR: Failed to run client: {e}")
        return False, str(e)

def main():
    """Main test function"""
    print("Comprehensive File Transfer Boundary Test")
    print("=" * 60)
    
    # Test a wide range of sizes around critical boundaries
    test_sizes: List[int] = [
        # Small files (single packet)
        1024,      # 1KB
        32768,     # 32KB
        61440,     # 60KB
        
        # Critical boundary area
        63488,     # 62KB
        64512,     # 63KB  
        65536,     # 64KB (critical boundary)
        66560,     # 65KB
        67584,     # 66KB (reported problem size)
        68608,     # 67KB
        69632,     # 68KB
        
        # Larger files (multi-packet)
        71680,     # 70KB
        81920,     # 80KB
        102400,    # 100KB
        131072,    # 128KB
    ]
    
    results: Dict[int, Dict[str, Any]] = {}
    
    print(f"Testing {len(test_sizes)} different file sizes...")
    
    for i, size in enumerate(test_sizes, 1):
        try:
            print(f"\n[{i}/{len(test_sizes)}] Testing {size} bytes ({size//1024}KB + {size%1024} bytes)")
            
            # Generate unique username for each test
            username: str = generate_unique_username()
            
            # Create test file
            test_file: str = create_test_file(size, f"{size//1024}KB_{size%1024}B")
            
            # Wait a moment to avoid overwhelming the server
            time.sleep(1)
            
            # Test transfer
            success: bool
            error_msg: str | None
            success, error_msg = test_file_transfer(test_file, size, username)
            results[size] = {
                'success': success,
                'error': error_msg,
                'username': username
            }
            
            status: str = "SUCCESS" if success else f"FAILED ({error_msg})"
            print(f"Result: {status}")
            
            # Clean up
            try:
                os.unlink(test_file)
            except:
                pass
                
        except Exception as e:
            print(f"ERROR testing {size} bytes: {e}")
            results[size] = {
                'success': False,
                'error': str(e),
                'username': 'unknown'
            }
        
        # Brief pause between tests
        time.sleep(0.5)
    
    # Summary and Analysis
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST RESULTS:")
    print("=" * 60)
    
    successful_sizes: List[int] = []
    failed_sizes: List[int] = []
    
    for size in sorted(results.keys()):
        result: Dict[str, Any] = results[size]
        status = "SUCCESS" if result['success'] else "FAILED"
        size_kb: int = size // 1024
        size_remainder: int = size % 1024
        size_desc: str = f"{size_kb}KB"
        if size_remainder > 0:
            size_desc += f"+{size_remainder}B"
        
        print(f"  {size:8d} bytes ({size_desc:>8s}): {status}")
        
        if result['success']:
            successful_sizes.append(size)
        else:
            failed_sizes.append(size)
            if result['error']:
                print(f"                                    Error: {result['error']}")
    
    # Analysis
    print("\n" + "=" * 60)
    print("BOUNDARY ANALYSIS:")
    print("=" * 60)
    
    if not failed_sizes:
        print("✅ ALL TESTS PASSED!")
        print("No file size boundary issues detected.")
    else:
        print(f"❌ FAILED SIZES: {len(failed_sizes)} out of {len(test_sizes)} tests")
        
        # Find boundary patterns
        if successful_sizes:
            max_success: int = max(successful_sizes)
            min_failure: float = min(failed_sizes) if failed_sizes else float('inf')
            
            print(f"Largest successful transfer: {max_success} bytes ({max_success//1024}KB)")
            if min_failure != float('inf'):
                print(f"Smallest failed transfer: {min_failure} bytes ({min_failure//1024}KB)")
                
                if max_success < min_failure:
                    print(f"BOUNDARY DETECTED: Failures start after {max_success} bytes")
                else:
                    print("INTERMITTENT FAILURES: No clear size boundary")
        
        # Group failures by error type
        error_groups: Dict[str, List[int]] = {}
        for size in failed_sizes:
            error: str = results[size]['error'] or 'Unknown'
            if error not in error_groups:
                error_groups[error] = []
            error_groups[error].append(size)
        
        print("\nFAILURE PATTERNS:")
        for error, sizes in error_groups.items():
            size_ranges: List[str] = [f"{s}B" for s in sizes[:3]]  # Show first 3
            if len(sizes) > 3:
                size_ranges.append(f"...+{len(sizes)-3} more")
            print(f"  {error}: {', '.join(size_ranges)}")
    
    print(f"\nTotal tests: {len(test_sizes)}")
    print(f"Successful: {len(successful_sizes)}")
    print(f"Failed: {len(failed_sizes)}")

if __name__ == "__main__":
    main()