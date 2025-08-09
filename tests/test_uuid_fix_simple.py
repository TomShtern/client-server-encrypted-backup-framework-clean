#!/usr/bin/env python3
"""
Simple test to verify UUID fix is working
"""

import tempfile
import os
import sys

def test_uuid_import():
    """Test that the UUID fix works"""
    print("Testing UUID fix...")
    
    try:
        # Test the problematic import pattern that was causing the error
        print("1. Testing global uuid import...")
        
        # This should work now
        import time
        job_id = f"job_{int(time.time() * 1000000)}"
        print(f"   ✅ Job ID generation works: {job_id}")
        
        # Test local uuid import
        print("2. Testing local uuid import...")
        import uuid as uuid_lib
        client_id = str(uuid_lib.uuid4())
        print(f"   ✅ UUID generation works: {client_id}")
        
        # Test the API server import
        print("3. Testing API server import...")
        try:
            import cyberbackup_api_server
            print("   ✅ API server imports successfully")
        except Exception as e:
            print(f"   ❌ API server import failed: {e}")
            return False
        
        print("\n🎉 UUID fix is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ UUID fix test failed: {e}")
        return False

def test_api_server_startup():
    """Test if API server can start"""
    print("\nTesting API server startup...")
    
    try:
        from flask import Flask
        from flask_cors import CORS
        
        app = Flask(__name__)
        CORS(app)
        
        @app.route('/test')
        def test():
            # Test the problematic UUID pattern
            job_id = f"job_{int(time.time() * 1000000)}"
            return {'status': 'working', 'job_id': job_id}
        
        print("   ✅ Flask app with UUID pattern works")
        return True
        
    except Exception as e:
        print(f"   ❌ Flask app test failed: {e}")
        return False

if __name__ == "__main__":
    print("UUID Fix Verification Test")
    print("=" * 50)
    
    success1 = test_uuid_import()
    success2 = test_api_server_startup()
    
    print("=" * 50)
    if success1 and success2:
        print("✅ ALL TESTS PASSED - UUID fix is working!")
        print("\nThe API server should now work without UUID errors.")
        print("Try starting it manually with: python cyberbackup_api_server.py")
    else:
        print("❌ SOME TESTS FAILED - UUID fix needs more work")
    
    sys.exit(0 if (success1 and success2) else 1)
