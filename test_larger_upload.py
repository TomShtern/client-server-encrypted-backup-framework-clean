#!/usr/bin/env python3
"""
Test larger file upload
"""
import requests
import os

def test_larger_file_upload():
    api_url = "http://localhost:9090/api/start_backup"
    test_file_path = "test_larger_file.txt"
    
    print("🔍 Testing larger file upload...")
    print(f"📁 Uploading file: {test_file_path}")
    
    # Check file size
    file_size = os.path.getsize(test_file_path)
    print(f"📊 File size: {file_size} bytes")
    
    # Prepare the file for upload
    with open(test_file_path, 'rb') as file:
        files = {'file': ('test_larger_file.txt', file, 'text/plain')}
        data = {
            'serverAddress': 'localhost:1256',
            'password': 'test123',
            'targetPath': '/backups/large_test'
        }
        
        try:
            print("🚀 Sending upload request...")
            response = requests.post(api_url, files=files, data=data, timeout=10)
            
            print(f"📡 Response status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            
            return response.status_code == 200
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 CyberBackup 3.0 Larger File Test")
    print("=" * 60)
    
    success = test_larger_file_upload()
    
    print("\n📁 Listing received files:")
    received_dir = "server/received_files"
    if os.path.exists(received_dir):
        files = os.listdir(received_dir)
        for file in files:
            size = os.path.getsize(os.path.join(received_dir, file))
            print(f"   📄 {file} ({size} bytes)")
    
    print("=" * 60)
