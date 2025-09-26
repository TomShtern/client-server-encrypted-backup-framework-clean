#!/usr/bin/env python3
"""
Debug script to test the process registry system directly
"""
import json

import requests


def test_process_registry():
    print("=== DEBUGGING PROCESS REGISTRY SYSTEM ===")

    # Test file
    test_file = "test_process_registry.txt"
    username = "ProcessRegistryDebug"

    print(f"Testing file: {test_file}")
    print(f"Username: {username}")

    try:
        # Call the API backup endpoint
        print("\n1. Calling /api/start_backup...")

        response = requests.post('http://127.0.0.1:9090/api/start_backup',
                               json={
                                   'username': username,
                                   'file_path': test_file
                               },
                               timeout=60)

        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")

            if data.get('success'):
                print("[SUCCESS] API call succeeded")
            else:
                print(f"[FAILED] API call failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"[ERROR] HTTP error: {response.status_code}")
            print(f"Response text: {response.text}")

    except requests.exceptions.Timeout:
        print("[ERROR] Request timeout - process may have hung")
    except requests.exceptions.ConnectionError:
        print("[ERROR] Connection error - API server may not be running")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")

    print("\n=== DONE ===")

if __name__ == "__main__":
    test_process_registry()
