#!/usr/bin/env python3
"""
Test script to debug the API endpoints directly
"""

import os
import sys

import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Shared.utils.unified_config import get_config

base_url = f"http://{get_config('api.host', '127.0.0.1')}:{get_config('api.port', 9090)}"

def test_api_status():
    """Test the /api/status endpoint"""
    try:
        response = requests.get(f'{base_url}/api/status')
        print(f"Status endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"Status endpoint failed: {e}")
        return False

def test_api_connect():
    """Test the /api/connect endpoint"""
    try:
        data = {
            "host": get_config('server.host', '127.0.0.1'),
            "port": get_config('server.port', 1256),
            "username": "testuser"
        }
        response = requests.post(f'{base_url}/api/connect',
                               json=data,
                               headers={'Content-Type': 'application/json'})
        print(f"Connect endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Connect endpoint failed: {e}")
        return False

def test_api_upload():
    """Test the /api/start_backup endpoint"""
    try:
        # Create a test file
        with open('test_upload_file.txt', 'w') as f:
            f.write('This is a test file for upload')

        files = {'file': open('test_upload_file.txt', 'rb')}
        data = {
            'username': 'testuser',
            'server': get_config('server.host', '127.0.0.1'),
            'port': get_config('server.port', 1256)
        }

        response = requests.post(f'{base_url}/api/start_backup',
                               files=files,
                               data=data)
        print(f"Upload endpoint: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Upload endpoint failed: {e}")
        return False
    finally:
        try:
            import os
            os.remove('test_upload_file.txt')
        except:
            pass

if __name__ == "__main__":
    print("=== Testing API Endpoints ===")

    print("\n1. Testing /api/status...")
    test_api_status()

    print("\n2. Testing /api/connect...")
    test_api_connect()

    print("\n3. Testing /api/start_backup...")
    test_api_upload()

    print("\n=== Test Complete ===")
