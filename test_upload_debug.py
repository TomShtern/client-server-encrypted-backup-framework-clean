#!/usr/bin/env python3
"""
Test file upload to debug the upload issue
"""

import requests
import tempfile
import os

def test_upload():
    """Test file upload through the API"""
    
    # Create a test file
    test_content = "This is a test file for debugging upload issues.\nTimestamp: " + str(time.time())
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    try:
        print(f"🧪 Testing file upload...")
        print(f"   Test file: {test_file_path}")
        print(f"   File size: {os.path.getsize(test_file_path)} bytes")
        
        # Test API status first
        print(f"\n📡 Testing API status...")
        status_response = requests.get("http://127.0.0.1:9090/api/status", timeout=5)
        print(f"   Status response: {status_response.status_code}")
        print(f"   Status data: {status_response.json()}")
        
        # Test connection
        print(f"\n🔗 Testing connection...")
        connect_data = {
            'server': '127.0.0.1:1256',
            'username': 'testuser'
        }
        connect_response = requests.post("http://127.0.0.1:9090/api/connect", 
                                       json=connect_data, timeout=10)
        print(f"   Connect response: {connect_response.status_code}")
        print(f"   Connect data: {connect_response.json()}")
        
        # Test file upload
        print(f"\n📤 Testing file upload...")
        with open(test_file_path, 'rb') as file:
            files = {'file': ('test_debug.txt', file, 'text/plain')}
            data = {
                'username': 'testuser',
                'server': '127.0.0.1',
                'port': '1256'
            }
            
            upload_response = requests.post("http://127.0.0.1:9090/api/start_backup", 
                                          files=files, data=data, timeout=30)
            print(f"   Upload response: {upload_response.status_code}")
            print(f"   Upload data: {upload_response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            os.unlink(test_file_path)
        except:
            pass

if __name__ == "__main__":
    import time
    test_upload()
