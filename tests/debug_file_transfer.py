#!/usr/bin/env python3
"""
Debug file transfer process step by step
"""
import httpx
import os
import tempfile
import time
import asyncio


async def debug_file_transfer():
    print("=== FILE TRANSFER DEBUGGING ===")
    
    # Step 1: Create a small test file
    test_content = "Test file for debugging transfer process"
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
    temp_file.write(test_content)
    temp_file.close()
    
    print(f"1. Created test file: {temp_file.name}")
    print(f"   Content: {test_content}")
    print(f"   Size: {os.path.getsize(temp_file.name)} bytes")
    
    # Step 2: Check API server status
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get("http://127.0.0.1:9090/api/status")
            print(f"2. API Server status: {response.status_code}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"   Connected: {status_data.get('connected', 'unknown')}")
            print(f"   Status: {status_data.get('status', 'unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"2. API Server ERROR: {e}")
        return
    
    # Step 3: Check what files are currently in received_files
    print("3. Current files in received_files:")
    received_dirs = ["received_files", "python_server/server/received_files"]
    for dir_path in received_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"   {dir_path}: {files}")
            break
    else:
        print("   No received_files directory found!")
    
    # Step 4: Attempt file upload
    print("4. Attempting file upload...")
    try:
        with open(temp_file.name, 'rb') as f:
            files = {'file': (os.path.basename(temp_file.name), f, 'text/plain')}
            data = {
                'username': 'debug_test_user',
                'server': '127.0.0.1',
                'port': '1256'
            }
            
            print(f"   Uploading: {os.path.basename(temp_file.name)}")
            print(f"   Username: {data['username']}")
            print(f"   Server: {data['server']}:{data['port']}")
            
            response = await client.post("http://127.0.0.1:9090/api/start_backup", 
                                       files=files, data=data, timeout=30)
            print(f"   Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   Success: {result.get('success', 'unknown')}")
                if result.get('job_id'):
                    print(f"   Job ID: {result['job_id']}")
                    
                    # Step 5: Monitor progress
                    print("5. Monitoring progress...")
                    for _ in range(10):  # Check for 10 seconds
                        try:
                            progress_response = await client.get(f"http://127.0.0.1:9090/api/status?job_id={result['job_id']}", timeout=5)
                            if progress_response.status_code == 200:
                                progress_data = progress_response.json()
                                print(f"   Progress: {progress_data.get('progress', {}).get('percentage', 0)}% - {progress_data.get('message', 'No message')}")
                                if progress_data.get('progress', {}).get('percentage', 0) >= 100:
                                    break
                        except Exception as e:
                            print(f"   Progress check error: {e}")
                        
                        time.sleep(1)
                        
            else:
                print(f"   Upload failed: {response.text}")
                
    except Exception as e:
        print(f"4. Upload ERROR: {e}")
    
    # Step 6: Check if file appeared in received_files
    print("6. Checking if file was received...")
    import time
    time.sleep(2)  # Wait a bit for file to be processed
    
    for dir_path in received_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"   {dir_path}: {files}")
            
            # Look for our test file
            test_filename = os.path.basename(temp_file.name)
            if test_filename in files:
                received_path = os.path.join(dir_path, test_filename)
                received_size = os.path.getsize(received_path)
                print(f"   ✅ File found! Size: {received_size} bytes")
                
                # Compare content
                with open(received_path, 'r') as f:
                    received_content = f.read()
                if received_content == test_content:
                    print(f"   ✅ Content matches!")
                else:
                    print(f"   ❌ Content mismatch!")
                    print(f"   Expected: {test_content}")
                    print(f"   Received: {received_content}")
            else:
                print(f"   ❌ Test file not found in {dir_path}")
            break
    
    # Cleanup
    try:
        os.unlink(temp_file.name)
        print(f"7. Cleaned up temp file: {temp_file.name}")
    except:
        pass

if __name__ == "__main__":
    import time
    asyncio.run(debug_file_transfer())