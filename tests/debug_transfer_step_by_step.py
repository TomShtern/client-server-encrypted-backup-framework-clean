#!/usr/bin/env python3
"""
Step-by-step debug of the transfer process
"""

import os
import subprocess
import tempfile


def create_tiny_test_file():
    """Create a very small test file"""
    content = "Hello World Test File\n"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(content)
        return f.name, len(content)

def test_step_by_step():
    """Test each step of the transfer process"""
    print("=== Step-by-Step Transfer Debug ===")
    
    temp_file, file_size = create_tiny_test_file()
    print(f"Created tiny test file: {file_size} bytes")
    
    try:
        # Create transfer.info
        transfer_info_path = "build/Release/transfer.info"
        os.makedirs(os.path.dirname(transfer_info_path), exist_ok=True)
        with open(transfer_info_path, 'w') as f:
            f.write("127.0.0.1:1256\n")
            f.write("StepByStepDebug\n")
            f.write(f"{os.path.abspath(temp_file)}\n")
        
        print("Running client with tiny file...")
        print("Looking for specific debug output...")
        
        # Run client and capture output
        result = subprocess.run(
            ["build/Release/EncryptedBackupClient.exe", "--batch"],
            cwd="build/Release",
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        
        print(f"Exit code: {result.returncode}")
        
        output = result.stdout + result.stderr
        
        # Check each step
        print("\n=== Transfer Steps Analysis ===")
        
        if "File details" in output:
            print("✅ Step 1: File details displayed")
        else:
            print("❌ Step 1: File details NOT displayed")
        
        if "Buffer" in output:
            print("✅ Step 2: Buffer calculation completed")
        else:
            print("❌ Step 2: Buffer calculation FAILED")
        
        if "Memory allocation" in output:
            print("✅ Step 3: Memory allocation started")
        else:
            print("❌ Step 3: Memory allocation NOT started")
        
        if "File loaded" in output:
            print("✅ Step 4: File loaded into memory")
        else:
            print("❌ Step 4: File loading FAILED")
        
        if "TRANSFERRING" in output:
            print("✅ Step 5: Transfer phase started")
        else:
            print("❌ Step 5: Transfer phase NOT started")
        
        if "Packet" in output:
            print("✅ Step 6: Packet sending attempted")
        else:
            print("❌ Step 6: Packet sending NOT attempted")
        
        if "success" in output.lower():
            print("✅ Step 7: Transfer completed successfully")
        else:
            print("❌ Step 7: Transfer did NOT complete successfully")
        
        # Show relevant output
        print(f"\n=== Client Output (first 1500 chars) ===")
        print(output[:1500])
        
        if "error" in output.lower() or "failed" in output.lower():
            print(f"\n=== Error Analysis ===")
            lines = output.split('\n')
            for line in lines:
                if 'error' in line.lower() or 'failed' in line.lower():
                    print(f"ERROR: {line}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Client timed out - likely hanging")
        return False
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    finally:
        try:
            os.unlink(temp_file)
        except:
            pass

if __name__ == "__main__":
    print("Step-by-Step Transfer Debug")
    print("=" * 40)
    
    success = test_step_by_step()
    
    print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if not success:
        print("\nThis will help identify exactly where the transfer breaks.")
        print("Check the step analysis above to see which step failed.")
