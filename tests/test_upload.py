#!/usr/bin/env python3
"""
Test script to verify file upload functionality
"""
import os

import requests


def test_file_upload():
    api_url = "http://localhost:9090/api/start_backup"
    test_file_path = "test_upload_file.txt"

    print("🔍 Testing file upload functionality...")
    print(f"📁 Uploading file: {test_file_path}")

    # Check if test file exists
    if not os.path.exists(test_file_path):
        print("❌ Test file not found!")
        return False

    # Prepare the file for upload
    with open(test_file_path, 'rb') as file:
        files = {'file': ('test_upload_file.txt', file, 'text/plain')}
        data = {
            'serverAddress': 'localhost:1256',
            'password': 'test123',
            'targetPath': '/backups/test'
        }

        try:
            print("🚀 Sending upload request...")
            response = requests.post(api_url, files=files, data=data, timeout=10)

            print(f"📡 Response status: {response.status_code}")
            print(f"📄 Response content: {response.text}")

            if response.status_code == 200:
                print("✅ Upload request successful!")
                return True
            else:
                print(f"❌ Upload failed with status {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

def check_received_files():
    """Check if files appeared in the received_files directory"""
    received_dir = "server/received_files"
    print(f"\n🔍 Checking received files in: {received_dir}")

    if os.path.exists(received_dir):
        files = os.listdir(received_dir)
        if files:
            print(f"✅ Found {len(files)} file(s):")
            for file in files:
                print(f"   📄 {file}")
            return True
        else:
            print("📭 No files found in received_files directory")
            return False
    else:
        print("❌ Received files directory not found!")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 CyberBackup 3.0 Upload Test")
    print("=" * 60)

    # Test the upload
    upload_success = test_file_upload()

    # Wait a moment for processing
    import time
    print("\n⏳ Waiting for file processing...")
    time.sleep(2)

    # Check if file was received
    files_received = check_received_files()

    print("\n" + "=" * 60)
    if upload_success and files_received:
        print("🎉 SUCCESS: End-to-end file upload working!")
    elif upload_success:
        print("⚠️  PARTIAL: Upload succeeded but file not found in received_files")
    else:
        print("❌ FAILED: Upload test failed")
    print("=" * 60)
