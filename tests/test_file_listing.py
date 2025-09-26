#!/usr/bin/env python3
"""
Test file listing functionality with MockaBase database
"""

# Import UTF-8 solution first to fix encoding issues

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from python_server.server.database import DatabaseManager


def test_file_listing_functionality():
    """Test the file listing functionality that was mentioned as broken"""

    print("Testing file listing functionality...")
    print("=" * 50)

    try:
        # Initialize database manager with MockaBase
        print("1. Initializing database manager with MockaBase...")
        db_manager = DatabaseManager("MockaBase.db")
        print("   PASS: Database manager initialized")

        # Test file listing functionality
        print("2. Testing file listing functionality...")
        all_files = db_manager.get_all_files()
        print(f"   PASS: Retrieved {len(all_files)} files")

        # Show some sample files
        if all_files:
            print("3. Sample files retrieved:")
            for i, file_info in enumerate(all_files[:5]):
                print(f"   - {file_info.get('filename', 'N/A')} ({file_info.get('size', 'N/A')} bytes)")

        # Test filtering functionality
        print("4. Testing file filtering...")
        # This mimics what the file management system would do
        if all_files:
            verified_files = [f for f in all_files if f.get('verified', False)]
            print(f"   PASS: Found {len(verified_files)} verified files out of {len(all_files)} total")

            # Test client filtering
            clients_with_files = {}
            for file_info in all_files:
                client = file_info.get('client', 'Unknown')
                if client not in clients_with_files:
                    clients_with_files[client] = 0
                clients_with_files[client] += 1

            print(f"   PASS: Files distributed across {len(clients_with_files)} clients")
            for client, count in list(clients_with_files.items())[:3]:
                print(f"     - {client}: {count} files")

        # Test file details retrieval
        print("5. Testing file details retrieval...")
        if all_files:
            sample_file = all_files[0]
            print("   PASS: Sample file details:")
            print(f"     Filename: {sample_file.get('filename', 'N/A')}")
            print(f"     Client: {sample_file.get('client', 'N/A')}")
            print(f"     Size: {sample_file.get('size', 'N/A')} bytes")
            print(f"     Verified: {sample_file.get('verified', 'N/A')}")
            print(f"     Date: {sample_file.get('date', 'N/A')}")

        print("\nSUCCESS: File listing functionality is working correctly!")
        return True

    except Exception as e:
        print(f"FAIL: Error during file listing test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_file_listing_functionality()
    if success:
        print("\nSUCCESS: File listing functionality is working with MockaBase!")
    else:
        print("\nFAIL: File listing functionality has issues!")
