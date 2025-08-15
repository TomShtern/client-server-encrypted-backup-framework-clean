#!/usr/bin/env python3
"""
Quick test to check if the API server is responding
"""
import requests
import json

def test_api_server():
    base_url = "http://127.0.0.1:9090"
    
    print("Testing API server connection...")
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health check: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test 2: Status endpoint
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        print(f"Status check: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Status check failed: {e}")
    
    # Test 3: Static file serving (HTML page)
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"Root page: {response.status_code} - Content length: {len(response.text)}")
    except Exception as e:
        print(f"Root page failed: {e}")
    
    # Test 4: Check what ports are listening
    import subprocess
    try:
        result = subprocess.run(["netstat", "-an"], capture_output=True, text=True, encoding='utf-8', timeout=10)
        listening_ports = [line for line in result.stdout.split('\n') if ':9090' in line or ':1256' in line]
        print("Listening ports:")
        for port in listening_ports:
            print(f"  {port.strip()}")
    except Exception as e:
        print(f"Port check failed: {e}")

if __name__ == "__main__":
    test_api_server()