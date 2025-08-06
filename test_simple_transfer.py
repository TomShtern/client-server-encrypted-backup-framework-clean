#!/usr/bin/env python3
"""
Simple test to isolate the transfer issue
"""

import os
import subprocess
import tempfile
import time

def create_simple_test_file():
    """Create a simple test file"""
    content = "This is a simple test file for debugging the transfer issue.\n" * 100
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        return f.name, len(content)

def test_simple_transfer():
    """Test with a simple small file"""
    print("=== Simple Transfer Test ===")
    
    temp_file, file_size = create_simple_test_file()
    print(f"Created test file: {file_size} bytes")
    
    try:
        # Create transfer.info
        transfer_info_path = "build/Release/transfer.info"
        os.makedirs(os.path.dirname(transfer_info_path), exist_ok=True)
        with open(transfer_info_path, 'w') as f:
            f.write("127.0.0.1:1256\n")
            f.write("SimpleDebugTest\n")
            f.write(f"{os.path.abspath(temp_file)}\n")
        
        print("Running client with simple file...")
        
        # Run client and capture output to a file to avoid Unicode issues
        with open("debug_output.txt", "w", encoding="utf-8", errors="replace") as output_file:
            result = subprocess.run(
                ["build/Release/EncryptedBackupClient.exe", "--batch"],
                cwd="build/Release",
                stdout=output_file,
                stderr=subprocess.STDOUT,
                timeout=30
            )
        
        print(f"Exit code: {result.returncode}")
        
        # Read the output file
        try:
            with open("debug_output.txt", "r", encoding="utf-8", errors="replace") as f:
                output = f.read()
                
            print("=== Client Output ===")
            print(output[:2000])  # First 2000 chars
            
            # Check for key indicators
            if "Enhanced Buffer Transfer" in output:
                print("✅ Enhanced buffer system activated")
            if "Memory mode" in output:
                print("✅ Memory mode selected (correct for small file)")
            if "File loaded" in output:
                print("✅ File loaded successfully")
            if "Transfer Plan" in output:
                print("✅ Transfer plan created")
            if "TRANSFERRING" in output:
                print("✅ Transfer phase started")
            if "retry" in output.lower():
                print("⚠️ Retry mechanism activated")
            if "failed" in output.lower():
                print("❌ Transfer failed")
            if "success" in output.lower():
                print("✅ Transfer success detected")
                
        except Exception as e:
            print(f"Could not read output file: {e}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("⚠️ Test timed out")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    finally:
        try:
            os.unlink(temp_file)
            os.unlink("debug_output.txt")
        except:
            pass

if __name__ == "__main__":
    print("Simple Transfer Debug Test")
    print("=" * 30)
    
    success = test_simple_transfer()
    
    print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if not success:
        print("\nThis confirms the transfer is broken.")
        print("The issue is likely in our new code changes.")
