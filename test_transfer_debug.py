#!/usr/bin/env python3
"""
Debug script to test file transfer and identify where it's failing
"""

import requests
import tempfile
import os
import time
import json

def test_file_transfer():
    """Test file transfer and identify failure point"""
    
    print("=== File Transfer Debug Test ===")
    
    # Create a small test file
    test_content = "This is a test file for debugging transfer issues.\nTimestamp: " + str(time.time())
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file_path = f.name
    
    try:
        print(f"1. Created test file: {temp_file_path}")
        print(f"   Content size: {len(test_content)} bytes")
        
        # Test API server connectivity
        print("\n2. Testing API server connectivity...")
        try:
            response = requests.get("http://127.0.0.1:9090/api/status", timeout=5)
            print(f"   API server status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.text}")
        except Exception as e:
            print(f"   ERROR: Cannot connect to API server: {e}")
            return False
        
        # Test file upload
        print("\n3. Testing file upload...")
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': (os.path.basename(temp_file_path), f, 'text/plain')}
                data = {
                    'username': 'DebugTest',
                    'server': '127.0.0.1',
                    'port': '1256'
                }
                
                print(f"   Uploading: {os.path.basename(temp_file_path)}")
                print(f"   Username: {data['username']}")
                print(f"   Server: {data['server']}:{data['port']}")
                
                response = requests.post("http://127.0.0.1:9090/api/start_backup", 
                                       files=files, data=data, timeout=30)
                
                print(f"   Upload response: {response.status_code}")
                print(f"   Response body: {response.text}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('success'):
                        print("   ✅ Upload request successful!")
                        
                        # Wait and check if file appears in received_files
                        print("\n4. Checking if file was received...")
                        filename = response_data.get('filename', os.path.basename(temp_file_path))
                        
                        for i in range(10):  # Check for 10 seconds
                            received_file_path = os.path.join("received_files", filename)
                            if os.path.exists(received_file_path):
                                print(f"   ✅ File found in received_files: {received_file_path}")
                                
                                # Verify content
                                with open(received_file_path, 'r') as rf:
                                    received_content = rf.read()
                                    if received_content == test_content:
                                        print("   ✅ File content matches!")
                                        return True
                                    else:
                                        print("   ❌ File content mismatch!")
                                        print(f"   Expected: {test_content}")
                                        print(f"   Received: {received_content}")
                                        return False
                            else:
                                print(f"   Waiting for file... ({i+1}/10)")
                                time.sleep(1)
                        
                        print("   ❌ File not found in received_files after 10 seconds")
                        return False
                    else:
                        print(f"   ❌ Upload failed: {response_data.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"   ❌ Upload failed with status {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"   ERROR: Upload failed: {e}")
            return False
            
    finally:
        # Cleanup
        try:
            os.unlink(temp_file_path)
        except:
            pass
    
    return False

if __name__ == "__main__":
    success = test_file_transfer()
    if success:
        print("\n🎉 Transfer test PASSED!")
    else:
        print("\n💥 Transfer test FAILED!")
        print("\nNext steps:")
        print("1. Check API server logs: logs/api-server-*.log")
        print("2. Check backup server logs: logs/backup-server-*.log") 
        print("3. Check if C++ client is being executed")
        print("4. Check transfer.info file in build/Release/")
