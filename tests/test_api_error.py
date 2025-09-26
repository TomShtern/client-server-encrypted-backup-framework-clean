#!/usr/bin/env python3
import os
import tempfile

import requests

# Create a small test file
with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_test.txt') as f:
    f.write('Test content for API error debugging')
    test_file = f.name

print(f"Created test file: {test_file}")

try:
    # Test the API endpoint that's causing the 500 error
    with open(test_file, 'rb') as f:
        files = {'file': f}
        data = {
            'username': 'TestAPIError',
            'server': '127.0.0.1',
            'port': '1256'
        }

        print("Sending request to API server...")
        response = requests.post('http://127.0.0.1:9090/api/start_backup',
                               files=files,
                               data=data,
                               timeout=30)

        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code == 500:
            print("500 error confirmed - checking API server logs...")

except Exception as e:
    print(f"Request failed: {e}")

finally:
    # Cleanup
    try:
        os.unlink(test_file)
    except:
        pass
