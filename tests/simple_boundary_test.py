#!/usr/bin/env python3
"""
Simple boundary test without Unicode characters.
"""

import os
import subprocess
import tempfile
import time


def create_test_file(size_bytes):
    """Create a test file of exact size"""
    content = "T" * size_bytes

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(content)
        temp_path = f.name

    return temp_path

def test_transfer(file_path, size_bytes):
    """Test file transfer"""
    timestamp = int(time.time())
    username = f"btest{timestamp % 10000}"

    # Create transfer.info
    with open("transfer.info", 'w') as f:
        f.write("127.0.0.1:1256\n")
        f.write(f"{username}\n")
        f.write(f"{file_path}\n")

    print(f"Testing {size_bytes//1024}KB with username: {username}")

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
        print(f"Return code: {result.returncode}")

        if result.stdout:
            print(f"STDOUT: {result.stdout.strip()}")
        if result.stderr:
            print(f"STDERR: {result.stderr.strip()}")

        return success, result.returncode, username

    except subprocess.TimeoutExpired:
        print("TIMEOUT")
        return False, -1, username
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False, -2, username

def main():
    print("Simple Boundary Test")
    print("===================")

    # Test critical sizes
    sizes = [64*1024, 66*1024]  # 64KB and 66KB
    results = []

    for size in sizes:
        print(f"\n--- Testing {size//1024}KB ({size} bytes) ---")

        # Create test file
        test_file = create_test_file(size)
        actual_size = os.path.getsize(test_file)
        print(f"Created file: {actual_size} bytes")

        # Test transfer
        success, return_code, username = test_transfer(test_file, size)

        result = {
            'size': size,
            'success': success,
            'return_code': return_code,
            'username': username
        }
        results.append(result)

        print(f"Result: {'SUCCESS' if success else 'FAILED'}")

        # Check received files
        received_dir = "received_files"
        if os.path.exists(received_dir):
            matching_files = []
            for f in os.listdir(received_dir):
                if username in f:
                    matching_files.append(f)

            if matching_files:
                print(f"Found in received_files: {matching_files}")

        # Cleanup
        try:
            os.unlink(test_file)
        except:
            pass

        time.sleep(2)

    print("\n===================")
    print("FINAL RESULTS:")
    for result in results:
        status = "SUCCESS" if result['success'] else f"FAILED (code {result['return_code']})"
        print(f"{result['size']//1024}KB: {status}")

if __name__ == "__main__":
    main()
