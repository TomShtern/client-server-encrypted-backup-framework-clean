#!/usr/bin/env python3
"""Test multiple transfers to reproduce socket connection issue"""

import os
import time

import requests


def test_multiple_transfers():
    for i in range(3):
        test_file = f"socket_test_{i}.txt"
        username = f"SocketTest{i}"

        # Create test file
        with open(test_file, "w") as f:
            f.write(f"Socket test {i} - testing connection stability")

        print(f"Testing transfer {i}: {test_file} -> {username}")

        try:
            with open(test_file, "rb") as f:
                response = requests.post('http://127.0.0.1:9090/api/start_backup',
                                       files={'file': f},
                                       data={'username': username},
                                       timeout=30)

            print(f"  Status: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text}")
            else:
                result = response.json()
                print(f"  Job ID: {result.get('job_id', 'N/A')}")

        except Exception as e:
            print(f"  Exception: {e}")

        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)

        time.sleep(2)  # Wait between transfers

if __name__ == "__main__":
    test_multiple_transfers()
