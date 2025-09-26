#!/usr/bin/env python3
"""
GUI File Upload Test Script
Tests the file upload functionality of the backup system GUI
"""

import os
import time

import requests


def test_gui_file_upload():
    """Test file upload through the GUI API endpoint"""

    # Configuration
    api_url = "http://localhost:9090/api/start_backup"
    test_file_path = "gui_test_file.txt"
    received_files_dir = "server/received_files"

    print("=" * 60)
    print("GUI File Upload Test")
    print("=" * 60)

    # Check if test file exists
    if not os.path.exists(test_file_path):
        print(f"❌ Test file {test_file_path} not found!")
        return False

    print(f"✅ Test file found: {test_file_path}")

    # Check initial state of received_files directory
    print(f"\n📁 Checking initial state of {received_files_dir}...")
    if os.path.exists(received_files_dir):
        initial_files = os.listdir(received_files_dir)
        print(f"   Initial files: {initial_files}")
    else:
        print(f"   Directory {received_files_dir} does not exist")
        initial_files = []

    # Prepare file upload
    print("\n🚀 Uploading file via GUI API...")
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': (test_file_path, f, 'text/plain')}
            response = requests.post(api_url, files=files, timeout=10)

        print(f"   Response status: {response.status_code}")
        print(f"   Response text: {response.text}")

        if response.status_code == 200:
            print("✅ Upload request successful!")
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

    # Wait a moment for processing
    print("\n⏳ Waiting 3 seconds for file processing...")
    time.sleep(3)

    # Check if file appeared in received_files
    print(f"\n📁 Checking {received_files_dir} for uploaded file...")
    if os.path.exists(received_files_dir):
        final_files = os.listdir(received_files_dir)
        print(f"   Final files: {final_files}")

        new_files = [f for f in final_files if f not in initial_files]
        if new_files:
            print(f"✅ New files detected: {new_files}")

            # Verify content of uploaded file
            for new_file in new_files:
                file_path = os.path.join(received_files_dir, new_file)
                print(f"\n📄 Checking content of {new_file}...")
                try:
                    with open(file_path, encoding='utf-8') as f:
                        content = f.read()

                    if "UNIQUE_TEST_SIGNATURE_12345" in content:
                        print("✅ Real file content verified! GUI upload working correctly.")
                        print("   File contains expected signature.")
                        return True
                    else:
                        print("❌ File content doesn't match expected test file.")
                        print(f"   Content preview: {content[:200]}...")
                        return False

                except Exception as e:
                    print(f"❌ Error reading uploaded file: {e}")
                    return False
        else:
            print("❌ No new files found in received_files directory")
            return False
    else:
        print(f"❌ Directory {received_files_dir} still does not exist")
        return False

def main():
    """Main test function"""
    print("Starting GUI file upload test...")

    # Change to the correct directory
    base_dir = r"c:\Users\tom7s\Desktopp\Claude Folder 2\Client Server Encrypted Backup Framework"
    os.chdir(base_dir)
    print(f"Working directory: {os.getcwd()}")

    # Run the test
    success = test_gui_file_upload()

    print("\n" + "=" * 60)
    if success:
        print("🎉 GUI FILE UPLOAD TEST PASSED!")
        print("   The GUI successfully uploads real files to the server.")
    else:
        print("💥 GUI FILE UPLOAD TEST FAILED!")
        print("   The GUI is not correctly uploading real files.")
    print("=" * 60)

    return success

if __name__ == "__main__":
    main()
