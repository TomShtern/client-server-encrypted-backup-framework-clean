#!/usr/bin/env python3
"""
Test the UUID fix in isolation
"""

import tempfile
import requests
import os

def test_api_server():
    """Test if the API server is working without UUID errors"""
    
    # Create a small test file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_uuid_test.txt') as f:
        f.write('UUID fix test content')
        test_file = f.name
    
    try:
        print(f"Testing API server with file: {test_file}")
        
        # Test the API endpoint
        with open(test_file, 'rb') as f:
            files = {'file': f}
            data = {
                'username': 'UUIDTestUser',
                'server': '127.0.0.1',
                'port': '1256'
            }
            
            print("Sending request to API server...")
            response = requests.post('http://127.0.0.1:9090/api/start_backup',
                                   files=files,
                                   data=data,
                                   timeout=10)
            
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS: API server is working!")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"Response text: {response.text[:500]}...")
                return False
                
    except requests.exceptions.ConnectionError:
        print("❌ FAILED: Could not connect to API server on port 9090")
        print("Make sure the API server is running")
        return False
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False
    finally:
        # Cleanup
        try:
            os.unlink(test_file)
        except:
            pass

if __name__ == "__main__":
    print("Testing UUID fix...")
    print("=" * 50)
    success = test_api_server()
    print("=" * 50)
    if success:
        print("🎉 UUID fix is working! You can now upload files through the web GUI.")
    else:
        print("💥 UUID fix failed. Need to investigate further.")
